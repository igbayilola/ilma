"""Exercise session engine: start, next question (adaptive), attempt (idempotent), complete."""
import logging
import random
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException, NotFoundException
from app.models.content import Question
from app.models.profile import Profile
from app.models.progress import MicroSkillProgress
from app.models.session import Attempt, ExerciseSession, SessionMode, SessionStatus
from app.services.config_service import config_service

logger = logging.getLogger(__name__)


class SessionService:
    async def start_session(
        self,
        db: AsyncSession,
        profile: Profile,
        skill_id: UUID,
        mode: SessionMode,
        micro_skill_id: UUID | None = None,
    ) -> ExerciseSession:
        # Build question filter
        filters = [Question.is_active.is_(True)]
        if micro_skill_id:
            filters.append(Question.micro_skill_id == micro_skill_id)
        else:
            filters.append(Question.skill_id == skill_id)

        count_result = await db.execute(
            select(func.count(Question.id)).where(*filters)
        )
        total = count_result.scalar() or 0
        if total == 0:
            raise AppException(
                status_code=400,
                code="NO_QUESTIONS",
                message="Aucune question disponible pour cette compétence.",
            )

        session = ExerciseSession(
            profile_id=profile.id,
            skill_id=skill_id,
            micro_skill_id=micro_skill_id,
            mode=mode,
            status=SessionStatus.IN_PROGRESS,
            total_questions=min(total, 10),  # Cap at 10 per session
            started_at=datetime.now(timezone.utc),
        )
        db.add(session)
        await db.flush()
        return session

    async def get_next_question(
        self, db: AsyncSession, session_id: UUID, profile: Profile
    ) -> Question | None:
        session = await self._get_session(db, session_id, profile.id)
        if session.status != SessionStatus.IN_PROGRESS:
            raise AppException(status_code=400, code="SESSION_ENDED", message="Cette session est terminée.")

        # Get IDs of already-answered questions
        answered = await db.execute(
            select(Attempt.question_id).where(Attempt.session_id == session_id)
        )
        answered_ids = {row[0] for row in answered.all()}

        # Build question filter based on session scope
        if session.micro_skill_id:
            query = select(Question).where(
                Question.micro_skill_id == session.micro_skill_id,
                Question.is_active.is_(True),
            )
        else:
            query = select(Question).where(
                Question.skill_id == session.skill_id,
                Question.is_active.is_(True),
            )

        if answered_ids:
            query = query.where(Question.id.notin_(answered_ids))

        result = await db.execute(query)
        candidates = list(result.scalars().all())
        if not candidates:
            return None

        # Adaptive selection
        return await self._select_adaptive(db, candidates, profile.id)

    async def _select_adaptive(
        self, db: AsyncSession, candidates: list[Question], profile_id: UUID
    ) -> Question:
        """Weighted random selection: lower micro-skill scores → higher weight."""
        max_score = await config_service.get(db, "smart_score_max")

        # Collect micro_skill_ids from candidates
        ms_ids = {q.micro_skill_id for q in candidates if q.micro_skill_id}

        if not ms_ids:
            # No micro-skill data — fall back to random
            return random.choice(candidates)

        # Fetch micro-skill progress for this profile
        msp_result = await db.execute(
            select(
                MicroSkillProgress.micro_skill_id,
                MicroSkillProgress.smart_score,
            ).where(
                MicroSkillProgress.profile_id == profile_id,
                MicroSkillProgress.micro_skill_id.in_(ms_ids),
            )
        )
        score_map: dict[UUID, float] = {
            row[0]: row[1] for row in msp_result.all()
        }

        # Assign weights: inverse of score (low score → high weight)
        NEUTRAL_WEIGHT = 50.0
        weights = []
        for q in candidates:
            if q.micro_skill_id and q.micro_skill_id in score_map:
                score = score_map[q.micro_skill_id]
                weights.append(max_score - score + 1)
            elif q.micro_skill_id:
                # Micro-skill exists but no progress yet → treat as 0 score (high weight)
                weights.append(max_score + 1)
            else:
                weights.append(NEUTRAL_WEIGHT)

        return random.choices(candidates, weights=weights, k=1)[0]

    async def record_attempt(
        self,
        db: AsyncSession,
        session_id: UUID,
        profile: Profile,
        question_id: UUID,
        client_event_id: str,
        answer: object,
        time_spent_seconds: int | None,
    ) -> Attempt:
        session = await self._get_session(db, session_id, profile.id)
        if session.status != SessionStatus.IN_PROGRESS:
            raise AppException(status_code=400, code="SESSION_ENDED", message="Cette session est terminée.")

        # Idempotence: return existing attempt if client_event_id already recorded
        existing = await db.execute(
            select(Attempt).where(Attempt.client_event_id == client_event_id)
        )
        dup = existing.scalar_one_or_none()
        if dup:
            return dup

        # Anti-cheat: minimum time check
        min_time = await config_service.get(db, "min_attempt_time_seconds")
        if time_spent_seconds is not None and time_spent_seconds < min_time:
            raise AppException(
                status_code=400,
                code="TOO_FAST",
                message="Temps de réponse trop court.",
            )

        # Get correct answer
        q_result = await db.execute(select(Question).where(Question.id == question_id))
        question = q_result.scalar_one_or_none()
        if not question:
            raise NotFoundException("Question", str(question_id))

        is_correct = self._check_answer(question, answer)
        points = question.points if is_correct else 0

        attempt = Attempt(
            session_id=session_id,
            question_id=question_id,
            profile_id=profile.id,
            client_event_id=client_event_id,
            answer=answer,
            is_correct=is_correct,
            points_earned=points,
            time_spent_seconds=time_spent_seconds,
            synced_at=datetime.now(timezone.utc),
        )
        db.add(attempt)

        # Update session counters
        session.total_questions = max(session.total_questions, session.correct_answers + 1)
        if is_correct:
            session.correct_answers += 1
        await db.flush()

        return attempt

    async def complete_session(
        self, db: AsyncSession, session_id: UUID, profile: Profile
    ) -> ExerciseSession:
        session = await self._get_session(db, session_id, profile.id)
        if session.status == SessionStatus.COMPLETED:
            return session  # Idempotent

        now = datetime.now(timezone.utc)
        session.status = SessionStatus.COMPLETED
        session.completed_at = now
        if session.started_at:
            started = session.started_at.replace(tzinfo=timezone.utc) if session.started_at.tzinfo is None else session.started_at
            session.duration_seconds = int((now - started).total_seconds())

        # Calculate final score
        if session.total_questions > 0:
            session.score = round(session.correct_answers / session.total_questions * 100, 1)

        db.add(session)
        await db.flush()

        # Award XP to weekly leaderboard
        try:
            from app.services.social_service import social_service
            xp = max(1, session.correct_answers)  # 1 XP per correct answer, min 1 for participation
            await social_service.increment_xp(db, profile.id, xp)
        except Exception:
            logger.warning("Failed to increment XP for profile %s", profile.id, exc_info=True)

        # Award badges
        try:
            from app.services.badge_service import badge_service
            await badge_service.award_badges(db, profile.id)
        except Exception:
            logger.warning("Failed to award badges for profile %s", profile.id, exc_info=True)

        return session

    # ── Helpers ─────────────────────────────────────────────
    async def _get_session(
        self, db: AsyncSession, session_id: UUID, profile_id: UUID
    ) -> ExerciseSession:
        result = await db.execute(
            select(ExerciseSession).where(ExerciseSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            raise NotFoundException("Session", str(session_id))
        if session.profile_id != profile_id:
            raise AppException(status_code=403, code="FORBIDDEN", message="Accès refusé à cette session.")
        return session

    def _check_answer(self, question: Question, answer: object) -> bool:
        correct = question.correct_answer
        if isinstance(correct, str) and isinstance(answer, str):
            return correct.strip().lower() == answer.strip().lower()
        return correct == answer


session_service = SessionService()
