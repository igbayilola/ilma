"""SmartScore calculation, progress tracking, and statistics."""
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, literal_column, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import MicroSkill
from app.models.progress import MicroSkillProgress, Progress
from app.models.session import Attempt, ExerciseSession, SessionStatus
from app.services.config_service import config_service
from app.services.risk_service import classify_risk, suggested_action


class ProgressService:
    async def update_progress_after_attempt(
        self,
        db: AsyncSession,
        profile_id: UUID,
        skill_id: UUID,
        is_correct: bool,
        micro_skill_id: UUID | None = None,
    ) -> Progress:
        """Recalculate SmartScore after an attempt."""
        streak_bonus_rate = await config_service.get(db, "smart_score_streak_bonus")
        max_score = await config_service.get(db, "smart_score_max")

        # Update micro-skill progress first if applicable
        if micro_skill_id:
            await self.update_micro_skill_progress_after_attempt(
                db, profile_id, micro_skill_id, is_correct
            )

        result = await db.execute(
            select(Progress).where(
                Progress.profile_id == profile_id,
                Progress.skill_id == skill_id,
            )
        )
        progress = result.scalar_one_or_none()

        if not progress:
            progress = Progress(
                profile_id=profile_id,
                skill_id=skill_id,
                smart_score=0.0,
                total_attempts=0,
                correct_attempts=0,
                streak=0,
                best_streak=0,
            )
            db.add(progress)

        progress.total_attempts += 1
        now = datetime.now(timezone.utc)

        if is_correct:
            progress.correct_attempts += 1
            progress.streak += 1
            if progress.streak > progress.best_streak:
                progress.best_streak = progress.streak
        else:
            progress.streak = 0

        # SmartScore = weighted accuracy + streak bonus
        if progress.total_attempts > 0:
            accuracy = progress.correct_attempts / progress.total_attempts * 100
            streak_bonus = min(progress.streak * streak_bonus_rate * 100, 20)  # Cap at 20
            progress.smart_score = min(accuracy + streak_bonus, max_score)

        progress.last_attempt_at = now
        await db.flush()

        # If micro-skills exist for this skill, aggregate from them
        await self._maybe_aggregate_from_micro_skills(db, profile_id, skill_id, progress)
        await db.flush()

        return progress

    async def update_micro_skill_progress_after_attempt(
        self,
        db: AsyncSession,
        profile_id: UUID,
        micro_skill_id: UUID,
        is_correct: bool,
    ) -> MicroSkillProgress:
        """Recalculate SmartScore for a micro-skill after an attempt."""
        streak_bonus_rate = await config_service.get(db, "smart_score_streak_bonus")
        max_score = await config_service.get(db, "smart_score_max")

        result = await db.execute(
            select(MicroSkillProgress).where(
                MicroSkillProgress.profile_id == profile_id,
                MicroSkillProgress.micro_skill_id == micro_skill_id,
            )
        )
        msp = result.scalar_one_or_none()

        if not msp:
            msp = MicroSkillProgress(
                profile_id=profile_id,
                micro_skill_id=micro_skill_id,
                smart_score=0.0,
                total_attempts=0,
                correct_attempts=0,
                streak=0,
                best_streak=0,
            )
            db.add(msp)

        msp.total_attempts += 1
        now = datetime.now(timezone.utc)

        if is_correct:
            msp.correct_attempts += 1
            msp.streak += 1
            if msp.streak > msp.best_streak:
                msp.best_streak = msp.streak
        else:
            msp.streak = 0

        if msp.total_attempts > 0:
            accuracy = msp.correct_attempts / msp.total_attempts * 100
            streak_bonus = min(msp.streak * streak_bonus_rate * 100, 20)
            msp.smart_score = min(accuracy + streak_bonus, max_score)

        msp.last_attempt_at = now
        await db.flush()
        return msp

    async def _maybe_aggregate_from_micro_skills(
        self,
        db: AsyncSession,
        profile_id: UUID,
        skill_id: UUID,
        progress: Progress,
    ) -> None:
        """Override skill score with average of micro-skill scores (non-practiced = 0)."""
        # Get all micro_skill IDs for this skill
        ms_result = await db.execute(
            select(MicroSkill.id).where(MicroSkill.skill_id == skill_id)
        )
        all_micro_skill_ids = [row[0] for row in ms_result.all()]

        if not all_micro_skill_ids:
            return  # No micro-skills → keep standard score

        # Get existing micro-skill progress
        msp_result = await db.execute(
            select(MicroSkillProgress.smart_score).where(
                MicroSkillProgress.profile_id == profile_id,
                MicroSkillProgress.micro_skill_id.in_(all_micro_skill_ids),
            )
        )
        scores = [row[0] for row in msp_result.all()]

        # Average over ALL micro-skills (non-practiced count as 0)
        total_score = sum(scores)
        progress.smart_score = total_score / len(all_micro_skill_ids)

    async def apply_weekly_decay(self, db: AsyncSession) -> int:
        """Decay all SmartScores that haven't been updated in 7+ days."""
        decay_rate = await config_service.get(db, "smart_score_decay_rate")
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)

        # Decay skill-level progress
        result = await db.execute(
            select(Progress).where(
                Progress.last_attempt_at < cutoff,
                Progress.smart_score > 0,
            )
        )
        stale = list(result.scalars().all())
        for p in stale:
            p.smart_score = max(0, p.smart_score * (1 - decay_rate))
            p.last_decay_at = datetime.now(timezone.utc)

        # Decay micro-skill progress
        msp_result = await db.execute(
            select(MicroSkillProgress).where(
                MicroSkillProgress.last_attempt_at < cutoff,
                MicroSkillProgress.smart_score > 0,
            )
        )
        stale_msp = list(msp_result.scalars().all())
        for msp in stale_msp:
            msp.smart_score = max(0, msp.smart_score * (1 - decay_rate))
            msp.last_decay_at = datetime.now(timezone.utc)

        await db.flush()
        return len(stale) + len(stale_msp)

    # ── Read endpoints ─────────────────────────────────────
    async def get_summary(self, db: AsyncSession, profile_id: UUID) -> dict:
        """Overall progress summary for a profile."""
        result = await db.execute(
            select(
                func.count(Progress.id),
                func.avg(Progress.smart_score),
                func.sum(Progress.total_attempts),
                func.sum(Progress.correct_attempts),
                func.max(Progress.best_streak),
            ).where(Progress.profile_id == profile_id)
        )
        row = result.one()
        skills_count, avg_score, total_attempts, correct_attempts, best_streak = row

        # Total sessions & time
        sess_result = await db.execute(
            select(
                func.count(ExerciseSession.id),
                func.sum(ExerciseSession.duration_seconds),
            ).where(
                ExerciseSession.profile_id == profile_id,
                ExerciseSession.status == SessionStatus.COMPLETED,
            )
        )
        sess_row = sess_result.one()
        total_sessions, total_time = sess_row

        return {
            "skills_practiced": skills_count or 0,
            "average_smart_score": round(avg_score or 0, 1),
            "total_attempts": total_attempts or 0,
            "correct_attempts": correct_attempts or 0,
            "accuracy_pct": round((correct_attempts or 0) / max(total_attempts or 1, 1) * 100, 1),
            "best_streak": best_streak or 0,
            "total_sessions": total_sessions or 0,
            "total_time_minutes": round((total_time or 0) / 60, 1),
        }

    async def get_skills_progress(self, db: AsyncSession, profile_id: UUID) -> list[dict]:
        """Per-skill progress list."""
        result = await db.execute(
            select(Progress).where(Progress.profile_id == profile_id).order_by(Progress.smart_score.desc())
        )
        return [
            {
                "skill_id": str(p.skill_id),
                "smart_score": round(p.smart_score, 1),
                "total_attempts": p.total_attempts,
                "correct_attempts": p.correct_attempts,
                "streak": p.streak,
                "best_streak": p.best_streak,
                "last_attempt_at": p.last_attempt_at.isoformat() if p.last_attempt_at else None,
            }
            for p in result.scalars().all()
        ]

    async def get_micro_skills_progress(
        self, db: AsyncSession, profile_id: UUID, skill_id: UUID
    ) -> list[dict]:
        """Per-micro-skill progress for a given skill (LEFT JOIN so unpracticed micro-skills appear)."""
        from sqlalchemy.orm import aliased

        msp_alias = aliased(MicroSkillProgress)

        stmt = (
            select(
                MicroSkill.id,
                MicroSkill.name,
                MicroSkill.external_id,
                MicroSkill.difficulty_index,
                msp_alias.smart_score,
                msp_alias.total_attempts,
                msp_alias.correct_attempts,
                msp_alias.streak,
                msp_alias.best_streak,
                msp_alias.last_attempt_at,
            )
            .outerjoin(
                msp_alias,
                (msp_alias.micro_skill_id == MicroSkill.id)
                & (msp_alias.profile_id == profile_id),
            )
            .where(MicroSkill.skill_id == skill_id)
            .order_by(MicroSkill.order)
        )
        rows = await db.execute(stmt)
        return [
            {
                "micro_skill_id": str(row[0]),
                "micro_skill_name": row[1],
                "external_id": row[2],
                "difficulty_index": row[3],
                "smart_score": round(row[4] or 0, 1),
                "total_attempts": row[5] or 0,
                "correct_attempts": row[6] or 0,
                "streak": row[7] or 0,
                "best_streak": row[8] or 0,
                "last_attempt_at": row[9].isoformat() if row[9] else None,
            }
            for row in rows.all()
        ]

    async def get_daily_stats(
        self, db: AsyncSession, profile_id: UUID, days: int = 7
    ) -> list[dict]:
        """Daily attempt counts for the last N days."""
        since = datetime.now(timezone.utc) - timedelta(days=days)
        day_col = func.date_trunc(literal_column("'day'"), Attempt.created_at).label("day")
        raw = await db.execute(
            select(
                day_col,
                func.count(Attempt.id),
            )
            .where(Attempt.profile_id == profile_id, Attempt.created_at >= since)
            .group_by(day_col)
            .order_by(day_col)
        )
        return [
            {"date": row[0].isoformat() if row[0] else None, "attempts": row[1]}
            for row in raw.all()
        ]


    async def get_child_health(self, db: AsyncSession, profile_id: UUID) -> dict:
        """Health-at-a-glance for a child profile (used by parent dashboard).

        Returns:
            average_score, streak, status (green/orange/red),
            time_this_week, time_delta_vs_last_week,
            weakest_skill_name, advice
        """
        from app.models.content import Skill

        now = datetime.now(timezone.utc)
        week_start = now - timedelta(days=7)
        prev_week_start = now - timedelta(days=14)

        # Average SmartScore
        score_result = await db.execute(
            select(func.avg(Progress.smart_score)).where(Progress.profile_id == profile_id)
        )
        avg_score = round(score_result.scalar() or 0, 1)

        # Current streak (max across skills)
        streak_result = await db.execute(
            select(func.max(Progress.streak)).where(Progress.profile_id == profile_id)
        )
        streak = streak_result.scalar() or 0

        # Time this week
        time_result = await db.execute(
            select(func.coalesce(func.sum(ExerciseSession.duration_seconds), 0)).where(
                ExerciseSession.profile_id == profile_id,
                ExerciseSession.status == SessionStatus.COMPLETED,
                ExerciseSession.completed_at >= week_start,
            )
        )
        time_this_week_seconds = time_result.scalar() or 0

        # Time previous week
        prev_time_result = await db.execute(
            select(func.coalesce(func.sum(ExerciseSession.duration_seconds), 0)).where(
                ExerciseSession.profile_id == profile_id,
                ExerciseSession.status == SessionStatus.COMPLETED,
                ExerciseSession.completed_at >= prev_week_start,
                ExerciseSession.completed_at < week_start,
            )
        )
        time_prev_week_seconds = prev_time_result.scalar() or 0

        time_this_week_min = round(time_this_week_seconds / 60)
        time_delta_min = round((time_this_week_seconds - time_prev_week_seconds) / 60)

        # Days since last activity
        last_activity_result = await db.execute(
            select(func.max(ExerciseSession.completed_at)).where(
                ExerciseSession.profile_id == profile_id,
                ExerciseSession.status == SessionStatus.COMPLETED,
            )
        )
        last_activity = last_activity_result.scalar()
        days_inactive = (now - last_activity).days if last_activity else 999

        # Status: green / orange / red
        if avg_score >= 70 and days_inactive <= 1:
            status = "green"
        elif avg_score < 40 or days_inactive >= 4:
            status = "red"
        else:
            status = "orange"

        # Weakest skill (lowest SmartScore with at least 1 attempt)
        weakest_result = await db.execute(
            select(Progress.skill_id, Progress.smart_score)
            .where(Progress.profile_id == profile_id, Progress.total_attempts > 0)
            .order_by(Progress.smart_score.asc())
            .limit(1)
        )
        weakest_row = weakest_result.first()
        weakest_skill_name = None
        advice = None

        if weakest_row:
            skill_result = await db.execute(
                select(Skill.name).where(Skill.id == weakest_row[0])
            )
            weakest_skill_name = skill_result.scalar()
            if weakest_skill_name:
                if weakest_row[1] < 50:
                    advice = f"Parler de : {weakest_skill_name} (score en baisse)"
                else:
                    advice = f"Encourager à continuer : {weakest_skill_name}"

        if days_inactive >= 3 and not advice:
            advice = "Encourager à reprendre les exercices"

        # Unified risk level — same formula used by admin at-risk endpoint and
        # the parent-SMS cron, so the three surfaces stay in sync (admin sees
        # X as "high" → kid gets flagged in parent dashboard → parent gets SMS).
        risk_level = classify_risk(min(days_inactive, 999), float(avg_score))
        suggested = suggested_action(risk_level, min(days_inactive, 999), float(avg_score))

        return {
            "average_score": avg_score,
            "streak": streak,
            "status": status,
            "time_this_week_minutes": time_this_week_min,
            "time_delta_minutes": time_delta_min,
            "days_inactive": min(days_inactive, 999),
            "weakest_skill_name": weakest_skill_name,
            "advice": advice,
            "risk_level": risk_level,
            "suggested_action": suggested,
        }


progress_service = ProgressService()
