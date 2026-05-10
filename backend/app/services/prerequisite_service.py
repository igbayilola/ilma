"""Prerequisite verification for skills.

Checks whether a profile has mastered the prerequisite skills
(SmartScore >= threshold) before starting an exercise.
"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Skill
from app.models.progress import Progress

# SmartScore threshold to consider a prerequisite "met"
_MASTERY_THRESHOLD = 70.0


class PrerequisiteService:
    async def check_skill_prerequisites(
        self,
        db: AsyncSession,
        profile_id: UUID,
        skill_id: UUID,
    ) -> dict:
        """Check whether the profile meets the prerequisites for a skill.

        Returns:
            {
                "met": True/False,
                "prerequisites": [
                    {"external_id": "NUM-ENTIERS-0-1B", "name": "...", "skill_id": "...",
                     "smart_score": 45.2, "threshold": 70, "met": False},
                    ...
                ]
            }
        """
        # Get the target skill's prerequisite list
        result = await db.execute(select(Skill).where(Skill.id == skill_id))
        skill = result.scalar_one_or_none()
        if not skill or not skill.prerequisites:
            return {"met": True, "prerequisites": []}

        prereq_ext_ids: list[str] = skill.prerequisites  # e.g. ["NUM-ENTIERS-0-1B", "NUM-POSITION"]

        # Resolve prerequisite skills by external_id
        prereq_result = await db.execute(
            select(Skill).where(Skill.external_id.in_(prereq_ext_ids))
        )
        prereq_skills = {s.external_id: s for s in prereq_result.scalars().all()}

        # Get progress for these skills
        prereq_skill_ids = [s.id for s in prereq_skills.values()]
        progress_result = await db.execute(
            select(Progress).where(
                Progress.profile_id == profile_id,
                Progress.skill_id.in_(prereq_skill_ids),
            )
        ) if prereq_skill_ids else None
        progress_map: dict[UUID, float] = {}
        if progress_result:
            for p in progress_result.scalars().all():
                progress_map[p.skill_id] = p.smart_score

        # Build result
        items = []
        all_met = True
        for ext_id in prereq_ext_ids:
            prereq_skill = prereq_skills.get(ext_id)
            if not prereq_skill:
                # Prerequisite skill not found in DB — skip (don't block)
                continue
            score = progress_map.get(prereq_skill.id, 0.0)
            met = score >= _MASTERY_THRESHOLD
            if not met:
                all_met = False
            items.append({
                "external_id": ext_id,
                "name": prereq_skill.name,
                "skill_id": str(prereq_skill.id),
                "smart_score": round(score, 1),
                "threshold": _MASTERY_THRESHOLD,
                "met": met,
            })

        return {"met": all_met, "prerequisites": items}


prerequisite_service = PrerequisiteService()
