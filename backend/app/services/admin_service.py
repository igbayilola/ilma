"""Admin service: user management, analytics, exports."""
import csv
import io
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import Integer, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.core.security import get_password_hash
from app.models.session import Attempt, ExerciseSession, SessionStatus
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
