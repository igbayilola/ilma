"""Scheduled notification tasks — CRON jobs for automatic notifications.

Triggers:
- Daily reminder (16h-18h): "Ton défi du jour t'attend !" if not played today
- Streak danger (J+2 inactivity): "Tu vas perdre ta série de X jours !"
- Weekly parent digest (Sunday evening): summary per child
"""
import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.notification import NotificationType
from app.models.profile import Profile
from app.models.progress import Progress
from app.models.session import ExerciseSession, SessionStatus
from app.models.user import User, UserRole
from app.models.parent_student import ParentStudent
from app.services.notification_service import notification_service

logger = logging.getLogger(__name__)


async def _get_db() -> AsyncSession:
    return AsyncSessionLocal()


# ── Daily Reminder ────────────────────────────────────────────


async def _send_daily_reminders() -> int:
    """Send 'Ton défi du jour t'attend !' to students who haven't played today."""
    db = await _get_db()
    sent = 0
    try:
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        # Find active student users
        result = await db.execute(
            select(User).where(
                User.role == UserRole.STUDENT,
                User.is_active.is_(True),
            )
        )
        students = list(result.scalars().all())

        for student in students:
            # Check if they have any session completed today
            session_today = await db.execute(
                select(func.count(ExerciseSession.id)).where(
                    ExerciseSession.student_id == student.id,
                    ExerciseSession.status == SessionStatus.COMPLETED,
                    ExerciseSession.completed_at >= today_start,
                )
            )
            if (session_today.scalar() or 0) > 0:
                continue  # Already played today

            # Throttle: max N notifications per day
            today_count = await notification_service.count_today(db, student.id)
            if today_count >= settings.NOTIFICATION_MAX_PER_DAY:
                continue

            await notification_service.create_multi_channel(
                db=db,
                user_id=student.id,
                type=NotificationType.INACTIVITY,
                title="Ton défi du jour t'attend !",
                body="Joue maintenant pour garder ta série et gagner des XP !",
                phone=student.phone,
            )
            sent += 1

        await db.commit()
        logger.info("[CRON] Daily reminders sent: %d", sent)
    except Exception:
        await db.rollback()
        logger.exception("[CRON] Daily reminder task failed")
    finally:
        await db.close()
    return sent


# ── Streak Danger ─────────────────────────────────────────────


async def _send_streak_danger_alerts() -> int:
    """Send 'Tu vas perdre ta série !' to students inactive for 2 days with an active streak."""
    db = await _get_db()
    sent = 0
    try:
        two_days_ago = datetime.now(timezone.utc) - timedelta(days=2)

        # Find profiles with streak > 0 and no session in 2 days
        result = await db.execute(
            select(Progress.profile_id, func.max(Progress.streak).label("max_streak"))
            .where(Progress.streak > 0)
            .group_by(Progress.profile_id)
        )
        streak_profiles = result.all()

        for profile_id, max_streak in streak_profiles:
            # Check last activity
            last_session = await db.execute(
                select(func.max(ExerciseSession.completed_at)).where(
                    ExerciseSession.profile_id == profile_id,
                    ExerciseSession.status == SessionStatus.COMPLETED,
                )
            )
            last_completed = last_session.scalar()
            if last_completed is None or last_completed > two_days_ago:
                continue  # Active recently

            # Find the user for this profile
            profile_result = await db.execute(
                select(Profile).where(Profile.id == profile_id)
            )
            profile = profile_result.scalar_one_or_none()
            if not profile:
                continue

            # Throttle
            today_count = await notification_service.count_today(db, profile.user_id)
            if today_count >= settings.NOTIFICATION_MAX_PER_DAY:
                continue

            await notification_service.create_multi_channel(
                db=db,
                user_id=profile.user_id,
                type=NotificationType.INACTIVITY,
                title=f"Tu vas perdre ta série de {max_streak} jours !",
                body="Reviens vite faire un exercice pour garder ta série !",
            )
            sent += 1

        await db.commit()
        logger.info("[CRON] Streak danger alerts sent: %d", sent)
    except Exception:
        await db.rollback()
        logger.exception("[CRON] Streak danger task failed")
    finally:
        await db.close()
    return sent


# ── Weekly Parent Digest ──────────────────────────────────────


async def _send_parent_weekly_digest() -> int:
    """Send weekly progress digest to parents (Sunday evening)."""
    db = await _get_db()
    sent = 0
    try:
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)

        # Find all parents
        result = await db.execute(
            select(User).where(
                User.role == UserRole.PARENT,
                User.is_active.is_(True),
            )
        )
        parents = list(result.scalars().all())

        for parent in parents:
            # Find linked children
            children_result = await db.execute(
                select(ParentStudent).where(ParentStudent.parent_id == parent.id)
            )
            links = list(children_result.scalars().all())
            if not links:
                continue

            # Build summary per child
            summaries = []
            for link in links:
                # Get child user info
                child_result = await db.execute(
                    select(User).where(User.id == link.student_id)
                )
                child = child_result.scalar_one_or_none()
                if not child:
                    continue

                # Count sessions this week
                sessions_count = await db.execute(
                    select(func.count(ExerciseSession.id)).where(
                        ExerciseSession.student_id == child.id,
                        ExerciseSession.status == SessionStatus.COMPLETED,
                        ExerciseSession.completed_at >= week_ago,
                    )
                )
                count = sessions_count.scalar() or 0

                # Total time this week
                time_result = await db.execute(
                    select(func.coalesce(func.sum(ExerciseSession.duration_seconds), 0)).where(
                        ExerciseSession.student_id == child.id,
                        ExerciseSession.status == SessionStatus.COMPLETED,
                        ExerciseSession.completed_at >= week_ago,
                    )
                )
                total_seconds = time_result.scalar() or 0
                total_minutes = total_seconds // 60

                name = child.full_name or "Votre enfant"
                if count == 0:
                    summaries.append(f"- {name} : inactif cette semaine")
                else:
                    summaries.append(f"- {name} : {count} exercice(s), {total_minutes} min")

            if not summaries:
                continue

            body = "Résumé de la semaine :\n" + "\n".join(summaries)

            await notification_service.create_multi_channel(
                db=db,
                user_id=parent.id,
                type=NotificationType.WEEKLY_REPORT,
                title="Résumé hebdomadaire Sitou",
                body=body,
                phone=parent.phone,
            )
            sent += 1

        await db.commit()
        logger.info("[CRON] Parent digest sent: %d", sent)
    except Exception:
        await db.rollback()
        logger.exception("[CRON] Parent digest task failed")
    finally:
        await db.close()
    return sent


# ── At-Risk Detection + Parent Alert ──────────────────────────


async def _send_parent_inactivity_alerts() -> int:
    """Alert parents when their child has been inactive for 3+ days.
    Combines multiple risk signals into a unified score."""
    db = await _get_db()
    sent = 0
    try:
        three_days_ago = datetime.now(timezone.utc) - timedelta(days=3)

        # Find all profiles with parent links
        result = await db.execute(
            select(Profile).where(Profile.is_active.is_(True))
        )
        profiles = list(result.scalars().all())

        for profile in profiles:
            # Signal 1: Days inactive
            last_session = await db.execute(
                select(func.max(ExerciseSession.completed_at)).where(
                    ExerciseSession.profile_id == profile.id,
                    ExerciseSession.status == SessionStatus.COMPLETED,
                )
            )
            last_completed = last_session.scalar()
            if last_completed is not None and last_completed > three_days_ago:
                continue  # Active recently

            days_inactive = 0
            if last_completed:
                days_inactive = (datetime.now(timezone.utc) - last_completed).days
            else:
                days_inactive = (datetime.now(timezone.utc) - profile.created_at).days
                if days_inactive < 3:
                    continue  # New profile, not yet inactive

            # Signal 2: Average score < 40%
            avg_result = await db.execute(
                select(func.avg(Progress.smart_score)).where(
                    Progress.profile_id == profile.id,
                    Progress.attempts > 0,
                )
            )
            avg_score = avg_result.scalar() or 50  # default if no data

            # Compute risk level
            risk_level = "low"
            if days_inactive >= 7 or avg_score < 30:
                risk_level = "high"
            elif days_inactive >= 3 or avg_score < 40:
                risk_level = "medium"

            if risk_level == "low":
                continue

            # Find parent to notify
            parent_result = await db.execute(
                select(User).where(User.id == profile.user_id, User.role == UserRole.PARENT)
            )
            parent = parent_result.scalar_one_or_none()
            if not parent:
                continue

            # Throttle
            today_count = await notification_service.count_today(db, parent.id)
            if today_count >= settings.NOTIFICATION_MAX_PER_DAY:
                continue

            # Build contextual message
            child_name = profile.display_name or "Votre enfant"
            if risk_level == "high":
                title = f"Alerte : {child_name} risque de décrocher"
                body = f"{child_name} n'a pas étudié depuis {days_inactive} jours"
                if avg_score < 40:
                    body += f" et son score moyen est de {avg_score:.0f}%"
                body += ". Encouragez-le à reprendre avec un exercice de 10 minutes."
            else:
                title = f"{child_name} n'a pas étudié depuis {days_inactive} jours"
                body = f"Un petit rappel pourrait aider {child_name} à reprendre le rythme."

            await notification_service.create_multi_channel(
                db=db,
                user_id=parent.id,
                type=NotificationType.INACTIVITY,
                title=title,
                body=body,
                phone=parent.phone,
            )
            sent += 1

        await db.commit()
        logger.info("[CRON] Parent inactivity alerts sent: %d", sent)
    except Exception:
        await db.rollback()
        logger.exception("[CRON] Parent inactivity alert task failed")
    finally:
        await db.close()
    return sent


# ── Sync wrappers (APScheduler calls sync functions) ──────────


def run_daily_reminders() -> None:
    """Sync wrapper for APScheduler."""
    asyncio.get_event_loop().create_task(_send_daily_reminders())


def run_streak_danger_alerts() -> None:
    """Sync wrapper for APScheduler."""
    asyncio.get_event_loop().create_task(_send_streak_danger_alerts())


def run_parent_weekly_digest() -> None:
    """Sync wrapper for APScheduler."""
    asyncio.get_event_loop().create_task(_send_parent_weekly_digest())
