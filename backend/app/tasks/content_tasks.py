"""Content quality monitoring tasks."""
import logging

from sqlalchemy import func, select

from app.db.session import AsyncSessionLocal
from app.models.content import ContentStatus, Question
from app.models.notification import NotificationType
from app.models.session import Attempt
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)

# Thresholds
LOW_SUCCESS_RATE = 0.20   # < 20% success → question too hard
HIGH_SUCCESS_RATE = 0.95  # > 95% success → question too easy
MIN_ATTEMPTS = 20         # Need at least 20 attempts for reliable stats


async def _check_question_success_rates() -> None:
    """CRON: flag questions with abnormal success rates and notify admins."""
    async with AsyncSessionLocal() as db:
        try:
            # Aggregate success rates for published questions with enough attempts
            from sqlalchemy import case

            correct_expr = func.sum(case((Attempt.is_correct.is_(True), 1), else_=0))
            stats = await db.execute(
                select(
                    Attempt.question_id,
                    func.count(Attempt.id).label("total"),
                    correct_expr.label("correct"),
                )
                .join(Question, Attempt.question_id == Question.id)
                .where(Question.status == ContentStatus.PUBLISHED)
                .group_by(Attempt.question_id)
                .having(func.count(Attempt.id) >= MIN_ATTEMPTS)
            )

            flagged = []
            for row in stats.all():
                question_id = row[0]
                total = row[1]
                correct = row[2] or 0
                rate = correct / total if total > 0 else 0

                if rate < LOW_SUCCESS_RATE:
                    flagged.append({"id": str(question_id), "rate": round(rate * 100, 1), "type": "too_hard", "total": total})
                elif rate > HIGH_SUCCESS_RATE:
                    flagged.append({"id": str(question_id), "rate": round(rate * 100, 1), "type": "too_easy", "total": total})

            if flagged:
                # Notify all admins
                from app.services.notification_service import notification_service

                admin_result = await db.execute(
                    select(User).where(User.role == UserRole.ADMIN, User.is_active.is_(True))
                )
                admins = admin_result.scalars().all()

                too_hard = [f for f in flagged if f["type"] == "too_hard"]
                too_easy = [f for f in flagged if f["type"] == "too_easy"]

                body_parts = []
                if too_hard:
                    body_parts.append(f"{len(too_hard)} question(s) trop difficile(s) (<{LOW_SUCCESS_RATE*100:.0f}%)")
                if too_easy:
                    body_parts.append(f"{len(too_easy)} question(s) trop facile(s) (>{HIGH_SUCCESS_RATE*100:.0f}%)")

                body = "Alerte qualité contenu :\n" + "\n".join(body_parts)

                for admin in admins:
                    await notification_service.create(
                        db=db,
                        user_id=admin.id,
                        type=NotificationType.SYSTEM,
                        title="Alerte qualité questions",
                        body=body,
                        data={"flagged_questions": flagged[:10]},
                    )

                await db.commit()
                logger.info("[ContentQuality] Flagged %d questions, notified %d admins", len(flagged), len(admins))
            else:
                logger.info("[ContentQuality] All questions within normal success rate range")

        except Exception:
            logger.exception("[ContentQuality] Failed to check question success rates")
