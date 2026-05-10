"""Admin service: user management, analytics, exports."""
import csv
import io
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import Integer, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.core.security import get_password_hash
from app.models.notification import Notification, NotificationChannel, NotificationType
from app.models.parent_student import ParentStudent
from app.models.profile import Profile
from app.models.session import Attempt, ExerciseSession, SessionStatus
from app.models.social import Challenge
from app.models.subscription import Payment, PaymentStatus, Subscription, SubscriptionStatus
from app.models.user import User, UserRole


class AdminService:
    # ── User management ────────────────────────────────────
    async def list_users(
        self, db: AsyncSession, role: UserRole | None = None, search: str | None = None,
        skip: int = 0, limit: int = 50,
    ) -> tuple[list[User], int]:
        query = select(User)
        count_query = select(func.count(User.id))

        if role:
            query = query.where(User.role == role)
            count_query = count_query.where(User.role == role)
        if search:
            pattern = f"%{search}%"
            query = query.where(User.full_name.ilike(pattern) | User.email.ilike(pattern))
            count_query = count_query.where(User.full_name.ilike(pattern) | User.email.ilike(pattern))

        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        result = await db.execute(query.order_by(User.created_at.desc()).offset(skip).limit(limit))
        return list(result.scalars().all()), total

    async def suspend_user(self, db: AsyncSession, user_id: UUID) -> User:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundException("Utilisateur", str(user_id))
        user.is_active = False
        await db.flush()
        return user

    async def reactivate_user(self, db: AsyncSession, user_id: UUID) -> User:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundException("Utilisateur", str(user_id))
        user.is_active = True
        await db.flush()
        return user

    async def reset_user_password(self, db: AsyncSession, user_id: UUID, new_password: str) -> None:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundException("Utilisateur", str(user_id))
        user.hashed_password = get_password_hash(new_password)
        await db.flush()

    # ── Analytics ──────────────────────────────────────────
    async def get_kpis(self, db: AsyncSession) -> dict:
        now = datetime.now(timezone.utc)
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_ago = now - timedelta(days=30)

        # DAU / MAU (profile-based)
        dau_result = await db.execute(
            select(func.count(func.distinct(ExerciseSession.profile_id))).where(
                ExerciseSession.created_at >= today
            )
        )
        dau = dau_result.scalar() or 0

        mau_result = await db.execute(
            select(func.count(func.distinct(ExerciseSession.profile_id))).where(
                ExerciseSession.created_at >= month_ago
            )
        )
        mau = mau_result.scalar() or 0

        # Total users
        total_users = await db.execute(select(func.count(User.id)))
        total_students = await db.execute(
            select(func.count(User.id)).where(User.role == UserRole.STUDENT)
        )

        # Sessions today
        sessions_today = await db.execute(
            select(func.count(ExerciseSession.id)).where(ExerciseSession.created_at >= today)
        )

        # Revenue (completed payments this month)
        mrr_result = await db.execute(
            select(func.sum(Payment.amount_xof)).where(
                Payment.status == PaymentStatus.COMPLETED,
                Payment.created_at >= month_ago,
            )
        )
        mrr = mrr_result.scalar() or 0

        # Active subscriptions
        active_subs = await db.execute(
            select(func.count(Subscription.id)).where(
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.expires_at > now,
            )
        )

        # Average score
        avg_score = await db.execute(
            select(func.avg(ExerciseSession.score)).where(
                ExerciseSession.status == SessionStatus.COMPLETED
            )
        )

        return {
            "dau": dau,
            "mau": mau,
            "total_users": total_users.scalar() or 0,
            "total_students": total_students.scalar() or 0,
            "sessions_today": sessions_today.scalar() or 0,
            "mrr_xof": mrr,
            "active_subscriptions": active_subs.scalar() or 0,
            "avg_session_score": round(avg_score.scalar() or 0, 1),
        }

    # ── Payments (Admin) ──────────────────────────────────
    async def list_payments(
        self, db: AsyncSession, status: PaymentStatus | None = None,
        skip: int = 0, limit: int = 50,
    ) -> tuple[list[dict], int]:
        query = select(Payment).join(User, Payment.user_id == User.id)
        count_query = select(func.count(Payment.id))

        if status:
            query = query.where(Payment.status == status)
            count_query = count_query.where(Payment.status == status)

        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        result = await db.execute(
            query.order_by(Payment.created_at.desc()).offset(skip).limit(limit)
        )
        payments = result.scalars().all()

        items = []
        for p in payments:
            # Fetch user name
            user_result = await db.execute(select(User.full_name, User.email).where(User.id == p.user_id))
            user_row = user_result.one_or_none()
            items.append({
                "id": str(p.id),
                "user_name": user_row[0] if user_row else "—",
                "user_email": user_row[1] if user_row else "",
                "provider": p.provider.value if p.provider else "mock",
                "provider_tx_id": p.provider_tx_id,
                "amount_xof": p.amount_xof,
                "status": p.status.value if p.status else "pending",
                "created_at": p.created_at.isoformat() if p.created_at else None,
            })
        return items, total

    # ── Question Analytics ─────────────────────────────────
    async def get_question_stats(self, db: AsyncSession, limit: int = 50) -> list[dict]:
        """Return per-question stats: success rate, avg time, attempt count."""
        from app.models.content import Question as QuestionModel
        from app.models.content import Skill

        stmt = (
            select(
                Attempt.question_id,
                func.count(Attempt.id).label("total_attempts"),
                func.sum(func.cast(Attempt.is_correct, Integer)).label("correct_count"),
                func.avg(Attempt.time_spent_seconds).label("avg_time"),
            )
            .where(Attempt.question_id.isnot(None))
            .group_by(Attempt.question_id)
            .order_by(func.count(Attempt.id).desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        rows = result.all()

        items = []
        for row in rows:
            q_result = await db.execute(
                select(QuestionModel.prompt, QuestionModel.skill_id).where(QuestionModel.id == row.question_id)
            )
            q_data = q_result.one_or_none()
            skill_name = ""
            if q_data and q_data[1]:
                s_result = await db.execute(select(Skill.name).where(Skill.id == q_data[1]))
                skill_name = s_result.scalar() or ""

            total = row.total_attempts or 0
            correct = row.correct_count or 0
            success_rate = round((correct / total) * 100, 1) if total > 0 else 0

            items.append({
                "question_id": str(row.question_id),
                "prompt": q_data[0] if q_data else "—",
                "skill_name": skill_name,
                "success_rate": success_rate,
                "avg_time_seconds": round(row.avg_time or 0, 1),
                "total_attempts": total,
            })
        return items

    # ── Digest Stats ──────────────────────────────────────
    async def get_digest_stats(self, db: AsyncSession) -> dict:
        """Return SMS digest tracking stats based on WEEKLY_REPORT notifications."""
        now = datetime.now(timezone.utc)
        # Start of current ISO week (Monday)
        week_start = (now - timedelta(days=now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        last_week_start = week_start - timedelta(days=7)

        # Total digests sent (all time) — count SMS channel WEEKLY_REPORT notifications
        total_result = await db.execute(
            select(func.count(Notification.id)).where(
                Notification.type == NotificationType.WEEKLY_REPORT,
                Notification.channel == NotificationChannel.SMS,
            )
        )
        total_all_time = total_result.scalar() or 0

        # Digests sent this week
        this_week_result = await db.execute(
            select(func.count(Notification.id)).where(
                Notification.type == NotificationType.WEEKLY_REPORT,
                Notification.channel == NotificationChannel.SMS,
                Notification.created_at >= week_start,
            )
        )
        digests_this_week = this_week_result.scalar() or 0

        # Digests sent last week
        last_week_result = await db.execute(
            select(func.count(Notification.id)).where(
                Notification.type == NotificationType.WEEKLY_REPORT,
                Notification.channel == NotificationChannel.SMS,
                Notification.created_at >= last_week_start,
                Notification.created_at < week_start,
            )
        )
        digests_last_week = last_week_result.scalar() or 0

        # Unique parents reached (all time) — distinct user_ids with WEEKLY_REPORT SMS
        unique_parents_result = await db.execute(
            select(func.count(func.distinct(Notification.user_id))).where(
                Notification.type == NotificationType.WEEKLY_REPORT,
                Notification.channel == NotificationChannel.SMS,
            )
        )
        unique_parents = unique_parents_result.scalar() or 0

        # Average children per digest parent
        # = total parent-student links for parents who received at least one digest
        if unique_parents > 0:
            digest_parent_subq = (
                select(Notification.user_id).where(
                    Notification.type == NotificationType.WEEKLY_REPORT,
                    Notification.channel == NotificationChannel.SMS,
                ).distinct()
            )
            children_count_result = await db.execute(
                select(func.count(ParentStudent.id)).where(
                    ParentStudent.parent_id.in_(digest_parent_subq)
                )
            )
            total_children_links = children_count_result.scalar() or 0
            avg_children = round(total_children_links / unique_parents, 1)
        else:
            avg_children = 0.0

        return {
            "total_all_time": total_all_time,
            "digests_this_week": digests_this_week,
            "digests_last_week": digests_last_week,
            "unique_parents_reached": unique_parents,
            "avg_children_per_digest": avg_children,
        }

    # ── Engagement Analytics (ANALYTICS.1) ──────────────────
    async def get_engagement(self, db: AsyncSession) -> dict:
        """DAU, WAU, MAU, stickiness ratio, and 30-day time series."""
        now = datetime.now(timezone.utc)
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        # Current DAU / WAU / MAU
        dau_r = await db.execute(
            select(func.count(func.distinct(ExerciseSession.profile_id)))
            .where(ExerciseSession.created_at >= today)
        )
        dau = dau_r.scalar() or 0

        wau_r = await db.execute(
            select(func.count(func.distinct(ExerciseSession.profile_id)))
            .where(ExerciseSession.created_at >= week_ago)
        )
        wau = wau_r.scalar() or 0

        mau_r = await db.execute(
            select(func.count(func.distinct(ExerciseSession.profile_id)))
            .where(ExerciseSession.created_at >= month_ago)
        )
        mau = mau_r.scalar() or 0

        stickiness = round(dau / mau, 3) if mau > 0 else 0.0

        # 30-day time series: DAU per day
        time_series = []
        for i in range(29, -1, -1):
            day_start = today - timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            day_r = await db.execute(
                select(func.count(func.distinct(ExerciseSession.profile_id)))
                .where(
                    ExerciseSession.created_at >= day_start,
                    ExerciseSession.created_at < day_end,
                )
            )
            time_series.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "dau": day_r.scalar() or 0,
            })

        return {
            "dau": dau,
            "wau": wau,
            "mau": mau,
            "stickiness": stickiness,
            "time_series": time_series,
        }

    # ── Retention Analytics (ANALYTICS.2) ─────────────────
    async def get_retention(self, db: AsyncSession) -> list[dict]:
        """D1, D7, D14, D30 retention for last 8 weekly cohorts."""
        now = datetime.now(timezone.utc)
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        # Start of current ISO week (Monday)
        current_week_start = today - timedelta(days=today.weekday())

        cohorts = []
        for i in range(8, 0, -1):
            cohort_start = current_week_start - timedelta(weeks=i)
            cohort_end = cohort_start + timedelta(days=7)

            # Profiles created in this cohort week
            cohort_profiles_r = await db.execute(
                select(Profile.id).where(
                    Profile.created_at >= cohort_start,
                    Profile.created_at < cohort_end,
                )
            )
            cohort_profile_ids = [row[0] for row in cohort_profiles_r.all()]
            cohort_size = len(cohort_profile_ids)

            if cohort_size == 0:
                cohorts.append({
                    "cohort_week": cohort_start.strftime("%Y-%m-%d"),
                    "cohort_size": 0,
                    "d1": 0.0, "d7": 0.0, "d14": 0.0, "d30": 0.0,
                })
                continue

            retention = {}
            for label, days in [("d1", 1), ("d7", 7), ("d14", 14), ("d30", 30)]:
                check_start = cohort_start + timedelta(days=days)
                check_end = check_start + timedelta(days=1)
                # Only calculate if the check date is in the past
                if check_start > today:
                    retention[label] = None
                    continue
                ret_r = await db.execute(
                    select(func.count(func.distinct(ExerciseSession.profile_id)))
                    .where(
                        ExerciseSession.profile_id.in_(cohort_profile_ids),
                        ExerciseSession.created_at >= check_start,
                        ExerciseSession.created_at < check_end,
                    )
                )
                retained = ret_r.scalar() or 0
                retention[label] = round((retained / cohort_size) * 100, 1)

            cohorts.append({
                "cohort_week": cohort_start.strftime("%Y-%m-%d"),
                "cohort_size": cohort_size,
                **retention,
            })

        return cohorts

    # ── Conversion Funnel (ANALYTICS.3) ───────────────────
    async def get_conversion(self, db: AsyncSession) -> dict:
        """Conversion funnel: users → profile → first session → payment → subscriber."""
        now = datetime.now(timezone.utc)

        # Stage 1: Total registered users
        total_users_r = await db.execute(select(func.count(User.id)))
        total_users = total_users_r.scalar() or 0

        # Stage 2: Users who created at least one profile
        users_with_profile_r = await db.execute(
            select(func.count(func.distinct(Profile.user_id)))
        )
        users_with_profile = users_with_profile_r.scalar() or 0

        # Stage 3: Profiles that completed at least one session
        profiles_with_session_r = await db.execute(
            select(func.count(func.distinct(ExerciseSession.profile_id)))
        )
        profiles_with_session = profiles_with_session_r.scalar() or 0

        # Stage 4: Users who started a payment (any payment record)
        users_started_payment_r = await db.execute(
            select(func.count(func.distinct(Payment.user_id)))
        )
        users_started_payment = users_started_payment_r.scalar() or 0

        # Stage 5: Users who completed a payment
        users_completed_payment_r = await db.execute(
            select(func.count(func.distinct(Payment.user_id)))
            .where(Payment.status == PaymentStatus.COMPLETED)
        )
        users_completed_payment = users_completed_payment_r.scalar() or 0

        # Stage 6: Users with active subscription
        active_subscribers_r = await db.execute(
            select(func.count(func.distinct(Subscription.user_id)))
            .where(
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.expires_at > now,
            )
        )
        active_subscribers = active_subscribers_r.scalar() or 0

        stages = [
            {"stage": "Utilisateurs inscrits", "count": total_users},
            {"stage": "Profil créé", "count": users_with_profile},
            {"stage": "Première session", "count": profiles_with_session},
            {"stage": "Paiement initié", "count": users_started_payment},
            {"stage": "Paiement complété", "count": users_completed_payment},
            {"stage": "Abonné actif", "count": active_subscribers},
        ]

        # Calculate conversion rates between stages
        for i in range(1, len(stages)):
            prev = stages[i - 1]["count"]
            curr = stages[i]["count"]
            stages[i]["conversion_rate"] = round((curr / prev) * 100, 1) if prev > 0 else 0.0
        stages[0]["conversion_rate"] = 100.0

        return {"stages": stages}

    # ── Virality / K-factor (ANALYTICS.4) ─────────────────
    async def get_virality(self, db: AsyncSession) -> dict:
        """K-factor based on challenges (invitations) sent and user growth."""
        now = datetime.now(timezone.utc)
        month_ago = now - timedelta(days=30)

        # Total challenges created (as proxy for invitations/shares)
        total_challenges_r = await db.execute(select(func.count(Challenge.id)))
        total_challenges = total_challenges_r.scalar() or 0

        # Challenges this month
        challenges_month_r = await db.execute(
            select(func.count(Challenge.id))
            .where(Challenge.created_at >= month_ago)
        )
        challenges_month = challenges_month_r.scalar() or 0

        # Active profiles this month (sent or received challenges)
        active_challengers_r = await db.execute(
            select(func.count(func.distinct(Challenge.challenger_id)))
            .where(Challenge.created_at >= month_ago)
        )
        active_challengers = active_challengers_r.scalar() or 0

        # Total active profiles this month
        mau_r = await db.execute(
            select(func.count(func.distinct(ExerciseSession.profile_id)))
            .where(ExerciseSession.created_at >= month_ago)
        )
        mau = mau_r.scalar() or 0

        # New users this month
        new_users_r = await db.execute(
            select(func.count(User.id)).where(User.created_at >= month_ago)
        )
        new_users = new_users_r.scalar() or 0

        # K-factor = invitations_per_user * conversion_rate
        invitations_per_user = round(challenges_month / mau, 2) if mau > 0 else 0.0
        # Approximate conversion: new users / challenges sent
        invite_conversion = round(new_users / challenges_month, 2) if challenges_month > 0 else 0.0
        k_factor = round(invitations_per_user * invite_conversion, 3)

        return {
            "total_challenges": total_challenges,
            "challenges_this_month": challenges_month,
            "active_challengers": active_challengers,
            "mau": mau,
            "new_users_this_month": new_users,
            "invitations_per_user": invitations_per_user,
            "invite_conversion_rate": invite_conversion,
            "k_factor": k_factor,
        }

    # ── Notification Monitoring (P0-1.17 / QUAL.3) ─────────
    async def get_notification_stats(self, db: AsyncSession) -> dict:
        """Return notification delivery monitoring stats."""
        now = datetime.now(timezone.utc)
        day_ago = now - timedelta(hours=24)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        # Total sent by time window
        async def _count_since(since: datetime) -> int:
            r = await db.execute(
                select(func.count(Notification.id)).where(Notification.created_at >= since)
            )
            return r.scalar() or 0

        total_24h = await _count_since(day_ago)
        total_7d = await _count_since(week_ago)
        total_30d = await _count_since(month_ago)

        # By channel: sent count, failed count, delivered count, failure rate
        channel_stats = []
        for ch in NotificationChannel:
            sent_r = await db.execute(
                select(func.count(Notification.id)).where(
                    Notification.channel == ch,
                    Notification.created_at >= month_ago,
                )
            )
            sent_count = sent_r.scalar() or 0

            failed_r = await db.execute(
                select(func.count(Notification.id)).where(
                    Notification.channel == ch,
                    Notification.status == "failed",
                    Notification.created_at >= month_ago,
                )
            )
            failed_count = failed_r.scalar() or 0

            delivered_r = await db.execute(
                select(func.count(Notification.id)).where(
                    Notification.channel == ch,
                    Notification.status.in_(["delivered", "sent", "opened"]),
                    Notification.created_at >= month_ago,
                )
            )
            delivered_count = delivered_r.scalar() or 0

            failure_rate = round((failed_count / sent_count) * 100, 1) if sent_count > 0 else 0.0

            channel_stats.append({
                "channel": ch.value,
                "sent_count": sent_count,
                "delivered_count": delivered_count,
                "failed_count": failed_count,
                "failure_rate": failure_rate,
            })

        # Top 5 failure reasons
        from sqlalchemy import desc as sa_desc
        error_r = await db.execute(
            select(
                Notification.error_message,
                func.count(Notification.id).label("count"),
            )
            .where(
                Notification.status == "failed",
                Notification.error_message.isnot(None),
                Notification.created_at >= month_ago,
            )
            .group_by(Notification.error_message)
            .order_by(sa_desc("count"))
            .limit(5)
        )
        top_errors = [
            {"error": row[0], "count": row[1]}
            for row in error_r.all()
        ]

        # Delivery rate by day (last 14 days)
        daily_series = []
        for i in range(13, -1, -1):
            day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)

            day_total_r = await db.execute(
                select(func.count(Notification.id)).where(
                    Notification.created_at >= day_start,
                    Notification.created_at < day_end,
                )
            )
            day_total = day_total_r.scalar() or 0

            day_delivered_r = await db.execute(
                select(func.count(Notification.id)).where(
                    Notification.created_at >= day_start,
                    Notification.created_at < day_end,
                    Notification.status.in_(["delivered", "sent", "opened"]),
                )
            )
            day_delivered = day_delivered_r.scalar() or 0

            daily_series.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "total": day_total,
                "delivered": day_delivered,
                "delivery_rate": round((day_delivered / day_total) * 100, 1) if day_total > 0 else 0.0,
            })

        return {
            "total_24h": total_24h,
            "total_7d": total_7d,
            "total_30d": total_30d,
            "by_channel": channel_stats,
            "top_errors": top_errors,
            "daily_series": daily_series,
        }

    # ── CSV Export ─────────────────────────────────────────
    async def export_users_csv(self, db: AsyncSession) -> str:
        result = await db.execute(select(User).order_by(User.created_at))
        users = result.scalars().all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "email", "full_name", "role", "is_active", "created_at"])
        for u in users:
            writer.writerow([str(u.id), u.email, u.full_name, u.role.value, u.is_active, u.created_at])
        return output.getvalue()


admin_service = AdminService()
