"""Content pack builder: generates per-skill micro packs for offline use.

Each pack includes the skill's questions (JSON) + micro-lessons (HTML),
along with metadata for versioning and integrity checking.
"""
import hashlib
import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Domain, MicroLesson, MicroSkill, Question, Skill, Subject

logger = logging.getLogger(__name__)


class PackService:
    async def list_skill_packs(
        self, db: AsyncSession, grade_level_id: UUID | None = None
    ) -> list[dict]:
        """List available per-skill packs with size estimates."""
        query = (
            select(
                Skill.id,
                Skill.name,
                Skill.slug,
                Domain.id.label("domain_id"),
                Domain.name.label("domain_name"),
                Subject.id.label("subject_id"),
                Subject.name.label("subject_name"),
                Skill.updated_at,
            )
            .join(Domain, Skill.domain_id == Domain.id)
            .join(Subject, Domain.subject_id == Subject.id)
            .where(Skill.is_active.is_(True))
        )
        if grade_level_id:
            query = query.where(Subject.grade_level_id == grade_level_id)

        result = await db.execute(query.order_by(Subject.name, Domain.order, Skill.order))
        rows = result.all()

        packs = []
        for row in rows:
            # Count questions and lessons for size estimation
            q_count = await db.execute(
                select(func.count(Question.id)).where(Question.skill_id == row.id)
            )
            l_count = await db.execute(
                select(func.count(MicroLesson.id)).where(MicroLesson.skill_id == row.id)
            )
            questions_count = q_count.scalar() or 0
            lessons_count = l_count.scalar() or 0

            # Rough size estimate: ~2KB per question, ~5KB per lesson
            estimated_size = (questions_count * 2048) + (lessons_count * 5120) + 1024  # +1KB metadata

            packs.append({
                "skill_id": str(row.id),
                "skill_name": row.name,
                "skill_slug": row.slug,
                "domain_id": str(row.domain_id),
                "domain_name": row.domain_name,
                "subject_id": str(row.subject_id),
                "subject_name": row.subject_name,
                "questions_count": questions_count,
                "lessons_count": lessons_count,
                "estimated_size_bytes": estimated_size,
                "version": row.updated_at.isoformat() if row.updated_at else None,
            })

        return packs

    async def build_skill_pack(self, db: AsyncSession, skill_id: UUID) -> dict | None:
        """Build a full content pack for a single skill."""
        skill_result = await db.execute(
            select(Skill).where(Skill.id == skill_id, Skill.is_active.is_(True))
        )
        skill = skill_result.scalar_one_or_none()
        if not skill:
            return None

        # Get domain + subject info
        domain_result = await db.execute(select(Domain).where(Domain.id == skill.domain_id))
        domain = domain_result.scalar_one_or_none()
        subject_result = await db.execute(
            select(Subject).where(Subject.id == domain.subject_id)
        ) if domain else None
        subject = subject_result.scalar_one_or_none() if subject_result else None

        # Get micro-skills
        ms_result = await db.execute(
            select(MicroSkill)
            .where(MicroSkill.skill_id == skill_id)
            .order_by(MicroSkill.order)
        )
        micro_skills = ms_result.scalars().all()

        # Get questions
        q_result = await db.execute(
            select(Question).where(Question.skill_id == skill_id)
        )
        questions = q_result.scalars().all()

        # Get lessons
        l_result = await db.execute(
            select(MicroLesson)
            .where(MicroLesson.skill_id == skill_id)
            .order_by(MicroLesson.order)
        )
        lessons = l_result.scalars().all()

        # Build pack payload
        pack_data = {
            "skill_id": str(skill.id),
            "skill_name": skill.name,
            "skill_slug": skill.slug,
            "domain_id": str(domain.id) if domain else None,
            "domain_name": domain.name if domain else None,
            "subject_id": str(subject.id) if subject else None,
            "subject_name": subject.name if subject else None,
            "micro_skills": [
                {
                    "id": str(ms.id),
                    "external_id": ms.external_id,
                    "name": ms.name,
                    "difficulty_index": ms.difficulty_index,
                    "bloom_level": ms.bloom_taxonomy_level,
                    "order": getattr(ms, "order", 0),
                }
                for ms in micro_skills
            ],
            "questions": [
                {
                    "id": str(q.id),
                    "micro_skill_id": str(q.micro_skill_id) if q.micro_skill_id else None,
                    "question_type": q.question_type.value if q.question_type else None,
                    "difficulty": q.difficulty.value if q.difficulty else None,
                    "text": q.text,
                    "choices": q.choices,
                    "correct_answer": q.correct_answer,
                    "explanation": q.explanation,
                    "hint": q.hint,
                    "hints": q.hints,
                    "media_url": q.media_url,
                    "points": q.points,
                    "time_limit_seconds": q.time_limit_seconds,
                    "tags": q.tags,
                }
                for q in questions
            ],
            "lessons": [
                {
                    "id": str(lesson.id),
                    "micro_skill_id": str(lesson.micro_skill_id) if lesson.micro_skill_id else None,
                    "title": lesson.title,
                    "content_html": lesson.content_html,
                    "sections": lesson.sections,
                    "formula": lesson.formula,
                    "summary": lesson.summary,
                    "media_url": lesson.media_url,
                    "duration_minutes": lesson.duration_minutes,
                    "order": lesson.order,
                }
                for lesson in lessons
            ],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        # Compute checksum from serialized questions+lessons
        import json
        content_str = json.dumps(pack_data["questions"] + pack_data["lessons"], sort_keys=True)
        pack_data["checksum"] = hashlib.md5(content_str.encode()).hexdigest()

        # Upload to S3/Minio
        try:
            from app.services.s3_service import s3_service
            s3_service.upload_pack(str(skill_id), pack_data)
            pack_data["download_url"] = s3_service.get_pack_url(str(skill_id))
        except Exception as exc:
            logger.warning("S3 upload failed for skill %s: %s", skill_id, exc)
            # Pack is still usable as inline JSON even if S3 upload fails

        return pack_data

    async def get_delta_packs(
        self, db: AsyncSession, since: datetime, grade_level_id: UUID | None = None
    ) -> list[dict]:
        """Return skill IDs that have changed since the given timestamp."""
        query = (
            select(Skill.id, Skill.name, Skill.updated_at)
            .where(Skill.is_active.is_(True), Skill.updated_at > since)
        )
        if grade_level_id:
            query = (
                query
                .join(Domain, Skill.domain_id == Domain.id)
                .join(Subject, Domain.subject_id == Subject.id)
                .where(Subject.grade_level_id == grade_level_id)
            )

        result = await db.execute(query)
        return [
            {
                "skill_id": str(row.id),
                "skill_name": row.name,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None,
            }
            for row in result.all()
        ]


pack_service = PackService()
