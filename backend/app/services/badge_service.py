"""Badge engine: extensible rule-based system with 30+ badges.

Rules are defined as dicts with a `condition_type` and `params`.
The engine evaluates each unearned badge's condition at session.complete.
"""
import logging
from datetime import datetime, time, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.badge import Badge, StudentBadge
from app.models.content import Domain, Skill, Subject
from app.models.notification import NotificationType
from app.models.progress import Progress
from app.models.session import ExerciseSession, SessionStatus

logger = logging.getLogger(__name__)


# ── Badge definitions (30+ badges) ──────────────────────────
# Each badge is identified by `code` and evaluated by `condition_type` + `params`.
# These are seeded into the `badges` table on first run.

BADGE_DEFINITIONS = [
    # ── Régularité (streak) ──
    {"code": "first_exercise", "name": "Première séance", "description": "Complète ton premier exercice", "icon": "🎯", "category": "streak", "condition_type": "min_sessions", "params": {"min": 1}},
    {"code": "streak_3", "name": "Série 3 jours", "description": "3 jours de suite", "icon": "🔥", "category": "streak", "condition_type": "min_best_streak", "params": {"min": 3}},
    {"code": "streak_7", "name": "Série 7 jours", "description": "Une semaine complète", "icon": "🔥", "category": "streak", "condition_type": "min_best_streak", "params": {"min": 7}},
    {"code": "streak_30", "name": "Série 30 jours", "description": "Un mois sans interruption !", "icon": "💎", "category": "streak", "condition_type": "min_best_streak", "params": {"min": 30}},
    {"code": "streak_100", "name": "Série 100 jours", "description": "Cent jours de persévérance", "icon": "👑", "category": "streak", "condition_type": "min_best_streak", "params": {"min": 100}},
    {"code": "early_bird", "name": "Lève-tôt", "description": "Joue avant 8h du matin", "icon": "🌅", "category": "streak", "condition_type": "session_before_hour", "params": {"hour": 8}},

    # ── Maîtrise (mastery) ──
    {"code": "perfect_score", "name": "Score parfait", "description": "100% sur un exercice", "icon": "💯", "category": "mastery", "condition_type": "perfect_session", "params": {}},
    {"code": "mastery_skill", "name": "Compétence maîtrisée", "description": "Score ≥ 90% sur une compétence", "icon": "⭐", "category": "mastery", "condition_type": "min_skill_score", "params": {"min_score": 90, "min_count": 1}},
    {"code": "mastery_5_skills", "name": "5 compétences maîtrisées", "description": "Score ≥ 90% sur 5 compétences", "icon": "🌟", "category": "mastery", "condition_type": "min_skill_score", "params": {"min_score": 90, "min_count": 5}},
    {"code": "mastery_10_skills", "name": "10 compétences maîtrisées", "description": "Score ≥ 90% sur 10 compétences", "icon": "🏆", "category": "mastery", "condition_type": "min_skill_score", "params": {"min_score": 90, "min_count": 10}},
    {"code": "domain_complete", "name": "Domaine complet", "description": "Maîtrise toutes les compétences d'un domaine", "icon": "🗂️", "category": "mastery", "condition_type": "domain_mastered", "params": {"min_score": 80}},
    {"code": "zero_errors_10", "name": "Zéro erreur", "description": "10 questions sans aucune erreur", "icon": "🎯", "category": "mastery", "condition_type": "min_correct_streak", "params": {"min": 10}},

    # ── Exploration ──
    {"code": "all_subjects", "name": "Toutes les matières", "description": "Exercice dans chaque matière", "icon": "🌍", "category": "exploration", "condition_type": "all_subjects_practiced", "params": {}},
    {"code": "questions_100", "name": "100 questions", "description": "Répondre à 100 questions", "icon": "📝", "category": "exploration", "condition_type": "min_total_attempts", "params": {"min": 100}},
    {"code": "questions_500", "name": "500 questions", "description": "Répondre à 500 questions", "icon": "📚", "category": "exploration", "condition_type": "min_total_attempts", "params": {"min": 500}},
    {"code": "questions_1000", "name": "1000 questions", "description": "Répondre à 1000 questions", "icon": "🎓", "category": "exploration", "condition_type": "min_total_attempts", "params": {"min": 1000}},
    {"code": "sessions_10", "name": "10 exercices", "description": "Complète 10 exercices", "icon": "📖", "category": "exploration", "condition_type": "min_sessions", "params": {"min": 10}},
    {"code": "sessions_50", "name": "50 exercices", "description": "Complète 50 exercices", "icon": "📘", "category": "exploration", "condition_type": "min_sessions", "params": {"min": 50}},
    {"code": "sessions_100", "name": "100 exercices", "description": "Complète 100 exercices", "icon": "📗", "category": "exploration", "condition_type": "min_sessions", "params": {"min": 100}},

    # ── CEP ──
    {"code": "cep_exam_80", "name": "Examen blanc 80%+", "description": "Obtenir 80%+ à un examen blanc", "icon": "📋", "category": "cep", "condition_type": "exam_score", "params": {"min_pct": 80}},
    {"code": "cep_exam_90", "name": "Examen blanc 90%+", "description": "Obtenir 90%+ à un examen blanc", "icon": "🏅", "category": "cep", "condition_type": "exam_score", "params": {"min_pct": 90}},
    {"code": "cep_all_subjects", "name": "Toutes matières CEP", "description": "Maîtrise toutes les matières du CEP", "icon": "🎓", "category": "cep", "condition_type": "all_subjects_mastered", "params": {"min_score": 70}},
    {"code": "cep_ready", "name": "Prêt pour le CEP", "description": "Score moyen ≥ 80% dans toutes les matières", "icon": "🇧🇯", "category": "cep", "condition_type": "all_subjects_mastered", "params": {"min_score": 80}},

    # ── Social ──
    {"code": "first_challenge", "name": "Premier défi", "description": "Envoie ton premier défi", "icon": "⚔️", "category": "social", "condition_type": "manual", "params": {}},
    {"code": "challenges_5_won", "name": "5 défis gagnés", "description": "Gagne 5 défis contre des amis", "icon": "🏆", "category": "social", "condition_type": "manual", "params": {}},
    {"code": "top_3_leaderboard", "name": "Top 3 classement", "description": "Atteindre le top 3 hebdomadaire", "icon": "🥇", "category": "social", "condition_type": "manual", "params": {}},

    # ── Spécial ──
    {"code": "subject_complete", "name": "Matière complète", "description": "Maîtrise toutes les compétences d'une matière", "icon": "🎖️", "category": "special", "condition_type": "subject_mastered", "params": {"min_score": 80}},
    {"code": "comeback", "name": "Retour en force", "description": "Reviens après 7+ jours d'absence", "icon": "💪", "category": "special", "condition_type": "comeback", "params": {"min_days": 7}},
]


class BadgeService:
    async def seed_badges(self, db: AsyncSession) -> int:
        """Seed badge definitions into the badges table. Idempotent."""
        existing = await db.execute(select(Badge.code))
        existing_codes = {row[0] for row in existing.all()}
        created = 0

        for defn in BADGE_DEFINITIONS:
            if defn["code"] in existing_codes:
                continue
            badge = Badge(
                code=defn["code"],
                name=defn["name"],
                description=defn["description"],
                icon=defn["icon"],
                category=defn["category"],
                criteria={"condition_type": defn["condition_type"], "params": defn["params"]},
            )
            db.add(badge)
            created += 1

        if created:
            await db.flush()
            logger.info("Seeded %d new badges", created)
        return created

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

        # Get all badges from DB
        all_badges_result = await db.execute(select(Badge))
        all_badges = list(all_badges_result.scalars().all())

        for badge in all_badges:
            if badge.code in existing_codes:
                continue

            criteria = badge.criteria or {}
            condition_type = criteria.get("condition_type", "")
            params = criteria.get("params", {})

            if condition_type == "manual":
                continue  # Social badges are awarded manually

            earned = await self._evaluate_condition(db, profile_id, condition_type, params, context)
            if earned:
                sb = StudentBadge(
                    profile_id=profile_id,
                    badge_id=badge.id,
                    awarded_at=datetime.now(timezone.utc),
                )
                db.add(sb)
                awarded.append(badge.code)

        if awarded:
            await db.flush()
            await self._notify_badges(db, profile_id, awarded)
        return awarded

    async def _evaluate_condition(
        self, db: AsyncSession, profile_id: UUID,
        condition_type: str, params: dict, context: dict | None = None,
    ) -> bool:
        """Evaluate a single badge condition."""
        if condition_type == "min_sessions":
            count = await db.execute(
                select(func.count(ExerciseSession.id)).where(
                    ExerciseSession.profile_id == profile_id,
                    ExerciseSession.status == SessionStatus.COMPLETED,
                )
            )
            return (count.scalar() or 0) >= params.get("min", 1)

        if condition_type == "min_best_streak":
            result = await db.execute(
                select(func.max(Progress.best_streak)).where(Progress.profile_id == profile_id)
            )
            return (result.scalar() or 0) >= params.get("min", 3)

        if condition_type == "min_skill_score":
            result = await db.execute(
                select(func.count(Progress.id)).where(
                    Progress.profile_id == profile_id,
                    Progress.smart_score >= params.get("min_score", 90),
                )
            )
            return (result.scalar() or 0) >= params.get("min_count", 1)

        if condition_type == "min_total_attempts":
            result = await db.execute(
                select(func.sum(Progress.total_attempts)).where(Progress.profile_id == profile_id)
            )
            return (result.scalar() or 0) >= params.get("min", 100)

        if condition_type == "min_correct_streak":
            result = await db.execute(
                select(func.max(Progress.best_streak)).where(Progress.profile_id == profile_id)
            )
            return (result.scalar() or 0) >= params.get("min", 10)

        if condition_type == "perfect_session":
            result = await db.execute(
                select(func.count(ExerciseSession.id)).where(
                    ExerciseSession.profile_id == profile_id,
                    ExerciseSession.status == SessionStatus.COMPLETED,
                    ExerciseSession.total_questions > 0,
                    ExerciseSession.correct_answers == ExerciseSession.total_questions,
                )
            )
            return (result.scalar() or 0) >= 1

        if condition_type == "all_subjects_practiced":
            subj_count = await db.execute(
                select(func.count(Subject.id)).where(Subject.is_active.is_(True))
            )
            total = subj_count.scalar() or 0
            if total == 0:
                return False
            practiced = await db.execute(
                select(func.count(func.distinct(Domain.subject_id)))
                .select_from(ExerciseSession)
                .join(Skill, ExerciseSession.skill_id == Skill.id)
                .join(Domain, Skill.domain_id == Domain.id)
                .where(
                    ExerciseSession.profile_id == profile_id,
                    ExerciseSession.status == SessionStatus.COMPLETED,
                )
            )
            return (practiced.scalar() or 0) >= total

        if condition_type == "session_before_hour":
            hour = params.get("hour", 8)
            result = await db.execute(
                select(func.count(ExerciseSession.id)).where(
                    ExerciseSession.profile_id == profile_id,
                    ExerciseSession.status == SessionStatus.COMPLETED,
                    func.extract("hour", ExerciseSession.started_at) < hour,
                )
            )
            return (result.scalar() or 0) >= 1

        if condition_type == "comeback":
            # Check if last session was 7+ days ago AND current session is today
            result = await db.execute(
                select(ExerciseSession.completed_at)
                .where(
                    ExerciseSession.profile_id == profile_id,
                    ExerciseSession.status == SessionStatus.COMPLETED,
                )
                .order_by(ExerciseSession.completed_at.desc())
                .limit(2)
            )
            rows = result.all()
            if len(rows) < 2:
                return False
            latest, prev = rows[0][0], rows[1][0]
            if latest and prev:
                gap = (latest - prev).days
                return gap >= params.get("min_days", 7)
            return False

        if condition_type == "domain_mastered":
            # Check if all skills in any domain have score >= min_score
            min_score = params.get("min_score", 80)
            domains = await db.execute(select(Domain.id))
            for (domain_id,) in domains.all():
                skill_ids_result = await db.execute(
                    select(Skill.id).where(Skill.domain_id == domain_id)
                )
                skill_ids = [r[0] for r in skill_ids_result.all()]
                if not skill_ids:
                    continue
                mastered = await db.execute(
                    select(func.count(Progress.id)).where(
                        Progress.profile_id == profile_id,
                        Progress.skill_id.in_(skill_ids),
                        Progress.smart_score >= min_score,
                    )
                )
                if (mastered.scalar() or 0) >= len(skill_ids):
                    return True
            return False

        if condition_type == "subject_mastered":
            min_score = params.get("min_score", 80)
            subjects = await db.execute(
                select(Subject.id).where(Subject.is_active.is_(True))
            )
            for (subject_id,) in subjects.all():
                skill_ids_result = await db.execute(
                    select(Skill.id)
                    .join(Domain, Skill.domain_id == Domain.id)
                    .where(Domain.subject_id == subject_id)
                )
                skill_ids = [r[0] for r in skill_ids_result.all()]
                if not skill_ids:
                    continue
                mastered = await db.execute(
                    select(func.count(Progress.id)).where(
                        Progress.profile_id == profile_id,
                        Progress.skill_id.in_(skill_ids),
                        Progress.smart_score >= min_score,
                    )
                )
                if (mastered.scalar() or 0) >= len(skill_ids):
                    return True
            return False

        if condition_type == "all_subjects_mastered":
            min_score = params.get("min_score", 70)
            subjects = await db.execute(
                select(Subject.id).where(Subject.is_active.is_(True))
            )
            subject_ids = [r[0] for r in subjects.all()]
            if not subject_ids:
                return False
            for subject_id in subject_ids:
                skill_ids_result = await db.execute(
                    select(Skill.id)
                    .join(Domain, Skill.domain_id == Domain.id)
                    .where(Domain.subject_id == subject_id)
                )
                skill_ids = [r[0] for r in skill_ids_result.all()]
                if not skill_ids:
                    return False
                mastered = await db.execute(
                    select(func.count(Progress.id)).where(
                        Progress.profile_id == profile_id,
                        Progress.skill_id.in_(skill_ids),
                        Progress.smart_score >= min_score,
                    )
                )
                if (mastered.scalar() or 0) < len(skill_ids):
                    return False
            return True

        if condition_type == "exam_score":
            from app.models.mock_exam import ExamSession
            min_score = params.get("min_score", 80)
            min_count = params.get("min_count", 1)
            result = await db.execute(
                select(func.count(ExamSession.id)).where(
                    ExamSession.profile_id == profile_id,
                    ExamSession.status == "completed",
                    ExamSession.score >= min_score,
                )
            )
            return (result.scalar() or 0) >= min_count

        return False

    async def _notify_badges(self, db: AsyncSession, profile_id: UUID, badge_codes: list[str]) -> None:
        """Send in-app notification for newly earned badges."""
        try:
            from app.models.profile import Profile
            from app.services.notification_service import notification_service

            profile_result = await db.execute(select(Profile).where(Profile.id == profile_id))
            profile = profile_result.scalar_one_or_none()
            if not profile:
                return

            for code in badge_codes:
                badge_result = await db.execute(select(Badge).where(Badge.code == code))
                badge = badge_result.scalar_one_or_none()
                badge_name = badge.name if badge else code
                badge_icon = badge.icon if badge else "🏅"

                await notification_service.create(
                    db=db,
                    user_id=profile.user_id,
                    type=NotificationType.BADGE_EARNED,
                    title=f"{badge_icon} Badge débloqué : {badge_name} !",
                    body=f"Félicitations ! Tu as gagné le badge « {badge_name} ». Continue comme ça !",
                    data={"badge_code": code},
                )
        except Exception:
            logger.warning("Failed to send badge notification for profile %s", profile_id, exc_info=True)

    async def sync_badge_event(
        self,
        db: AsyncSession,
        profile_id: UUID,
        badge_code: str,
        client_event_id: str,
        awarded_at: datetime,
    ) -> bool:
        """Process offline badge_gained event. Idempotent via client_event_id."""
        existing = await db.execute(
            select(StudentBadge).where(StudentBadge.client_event_id == client_event_id)
        )
        if existing.scalar_one_or_none():
            return False

        badge_result = await db.execute(select(Badge).where(Badge.code == badge_code))
        badge = badge_result.scalar_one_or_none()
        if not badge:
            return False

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

    async def _compute_progress(self, db: AsyncSession, profile_id: UUID, criteria: dict) -> dict:
        """Compute current/target progress for an unearned badge."""
        ct = criteria.get("condition_type", "")
        params = criteria.get("params", {})

        if ct == "min_sessions":
            target = params.get("min", 1)
            result = await db.execute(
                select(func.count(ExerciseSession.id)).where(
                    ExerciseSession.profile_id == profile_id,
                    ExerciseSession.status == SessionStatus.COMPLETED,
                )
            )
            return {"current": result.scalar() or 0, "target": target}

        if ct == "min_best_streak":
            target = params.get("min", 3)
            result = await db.execute(
                select(func.max(Progress.best_streak)).where(Progress.profile_id == profile_id)
            )
            return {"current": result.scalar() or 0, "target": target}

        if ct == "min_skill_score":
            target = params.get("min_count", 1)
            result = await db.execute(
                select(func.count(Progress.id)).where(
                    Progress.profile_id == profile_id,
                    Progress.smart_score >= params.get("min_score", 90),
                )
            )
            return {"current": result.scalar() or 0, "target": target}

        if ct == "min_total_attempts":
            target = params.get("min", 100)
            result = await db.execute(
                select(func.sum(Progress.total_attempts)).where(Progress.profile_id == profile_id)
            )
            return {"current": result.scalar() or 0, "target": target}

        # For other types, no progress tracking
        return {"current": 0, "target": 1}

    async def get_all_badges_with_status(self, db: AsyncSession, profile_id: UUID) -> list[dict]:
        """Get all badges with earned/locked status + progress for the collection page."""
        earned_result = await db.execute(
            select(StudentBadge.badge_id, StudentBadge.awarded_at)
            .where(StudentBadge.profile_id == profile_id)
        )
        earned_map = {row[0]: row[1] for row in earned_result.all()}

        all_badges_result = await db.execute(
            select(Badge).order_by(Badge.category, Badge.code)
        )
        badges = []
        for b in all_badges_result.scalars().all():
            earned = b.id in earned_map
            progress = None
            if not earned and b.criteria:
                try:
                    progress = await self._compute_progress(db, profile_id, b.criteria)
                except Exception:
                    progress = {"current": 0, "target": 1}

            badges.append({
                "badge_code": b.code,
                "badge_name": b.name,
                "description": b.description,
                "icon": b.icon,
                "category": b.category.value,
                "earned": earned,
                "awarded_at": earned_map[b.id].isoformat() if earned else None,
                "progress": progress,
            })
        return badges


badge_service = BadgeService()
