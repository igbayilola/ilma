"""Badge engine: rules, awarding, idempotent offline sync."""
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.badge import Badge, StudentBadge
from app.models.progress import Progress
from app.models.session import ExerciseSession, SessionStatus

# ── Badge rule definitions ─────────────────────────────────
BADGE_RULES = {
    "first_exercise": {
        "description": "First completed session",
        "check": "_check_first_exercise",
    },
    "streak_3": {
        "description": "3 consecutive correct",
        "check": "_check_streak",
        "threshold": 3,
    },
    "streak_10": {
        "description": "10 consecutive correct",
        "check": "_check_streak",
        "threshold": 10,
    },
    "mastery_skill": {
        "description": "90%+ on a skill",
        "check": "_check_mastery",
    },
    "all_subjects": {
        "description": "Exercise in every subject",
        "check": "_check_all_subjects",
    },
}


class BadgeService:
    async def award_badges(
        self, db: AsyncSession, profile_id: UUID, context: dict | None = None
    ) -> list[str]:
        """Evaluate all rules and award new badges. Returns list of newly awarded badge codes."""
        awarded = []

        # Get already-earned badge codes
        result = await db.execute(
            select(Badge.code)
            .join(StudentBadge, StudentBadge.badge_id == Badge.id)
            .where(StudentBadge.profile_id == profile_id)
        )
        existing_codes = {row[0] for row in result.all()}

        for code, rule in BADGE_RULES.items():
            if code in existing_codes:
                continue

            checker = getattr(self, rule["check"])
            earned = await checker(db, profile_id, rule)
            if earned:
                badge_result = await db.execute(select(Badge).where(Badge.code == code))
                badge = badge_result.scalar_one_or_none()
                if badge:
                    sb = StudentBadge(
                        profile_id=profile_id,
                        badge_id=badge.id,
                        awarded_at=datetime.now(timezone.utc),
                    )
                    db.add(sb)
                    awarded.append(code)

        if awarded:
            await db.flush()
        return awarded

    async def sync_badge_event(
        self,
        db: AsyncSession,
        profile_id: UUID,
        badge_code: str,
        client_event_id: str,
        awarded_at: datetime,
    ) -> bool:
        """Process offline badge_gained event. Idempotent via client_event_id."""
        # Check duplicate
        existing = await db.execute(
            select(StudentBadge).where(StudentBadge.client_event_id == client_event_id)
        )
        if existing.scalar_one_or_none():
            return False  # Already recorded

        badge_result = await db.execute(select(Badge).where(Badge.code == badge_code))
        badge = badge_result.scalar_one_or_none()
        if not badge:
            return False

        # Check not already earned (different event)
        dup = await db.execute(
            select(StudentBadge).where(
                StudentBadge.profile_id == profile_id,
                StudentBadge.badge_id == badge.id,
            )
        )
        if dup.scalar_one_or_none():
            return False

        sb = StudentBadge(
            profile_id=profile_id,
            badge_id=badge.id,
            client_event_id=client_event_id,
            awarded_at=awarded_at,
            synced_at=datetime.now(timezone.utc),
        )
        db.add(sb)
        await db.flush()
        return True

    async def get_student_badges(self, db: AsyncSession, profile_id: UUID) -> list[dict]:
        result = await db.execute(
            select(StudentBadge, Badge)
            .join(Badge, StudentBadge.badge_id == Badge.id)
            .where(StudentBadge.profile_id == profile_id)
            .order_by(StudentBadge.awarded_at.desc())
        )
        return [
            {
                "badge_code": b.code,
                "badge_name": b.name,
                "description": b.description,
                "icon": b.icon,
                "category": b.category.value,
                "awarded_at": sb.awarded_at.isoformat() if sb.awarded_at else None,
            }
            for sb, b in result.all()
        ]

    # ── Rule checkers ──────────────────────────────────────
    async def _check_first_exercise(self, db: AsyncSession, profile_id: UUID, rule: dict) -> bool:
        result = await db.execute(
            select(func.count(ExerciseSession.id)).where(
                ExerciseSession.profile_id == profile_id,
                ExerciseSession.status == SessionStatus.COMPLETED,
            )
        )
        return (result.scalar() or 0) >= 1

    async def _check_streak(self, db: AsyncSession, profile_id: UUID, rule: dict) -> bool:
        threshold = rule.get("threshold", 3)
        result = await db.execute(
            select(func.max(Progress.best_streak)).where(Progress.profile_id == profile_id)
        )
        best = result.scalar() or 0
        return best >= threshold

    async def _check_mastery(self, db: AsyncSession, profile_id: UUID, rule: dict) -> bool:
        result = await db.execute(
            select(func.count(Progress.id)).where(
                Progress.profile_id == profile_id,
                Progress.smart_score >= 90,
            )
        )
        return (result.scalar() or 0) >= 1

    async def _check_all_subjects(self, db: AsyncSession, profile_id: UUID, rule: dict) -> bool:
        from app.models.content import Skill, Subject

        # Count active subjects
        subj_count = await db.execute(select(func.count(Subject.id)).where(Subject.is_active.is_(True)))
        total_subjects = subj_count.scalar() or 0
        if total_subjects == 0:
            return False

        # Count distinct subjects the profile has practiced
        practiced = await db.execute(
            select(func.count(func.distinct(Subject.id)))
            .select_from(ExerciseSession)
            .join(Skill, ExerciseSession.skill_id == Skill.id)
            .join(Subject, Skill.domain_id == Subject.id)  # Simplified; proper join through Domain
            .where(
                ExerciseSession.profile_id == profile_id,
                ExerciseSession.status == SessionStatus.COMPLETED,
            )
        )
        return (practiced.scalar() or 0) >= total_subjects


badge_service = BadgeService()
