"""Content read service — subjects, domains, skills, micro_skills, questions, lessons."""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.models.content import Domain, MicroLesson, MicroSkill, Question, Skill, Subject


class ContentService:
    # ── Subjects ───────────────────────────────────────────
    async def list_subjects(self, db: AsyncSession, grade_level_id: Optional[UUID] = None) -> list[Subject]:
        stmt = select(Subject).where(Subject.is_active.is_(True)).order_by(Subject.order)
        if grade_level_id:
            stmt = stmt.where(Subject.grade_level_id == grade_level_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_subject(self, db: AsyncSession, subject_id: UUID) -> Subject:
        result = await db.execute(select(Subject).where(Subject.id == subject_id))
        subj = result.scalar_one_or_none()
        if not subj:
            raise NotFoundException("Matière", str(subject_id))
        return subj

    # ── Domains (chapters) ─────────────────────────────────
    async def list_domains(self, db: AsyncSession, subject_id: UUID) -> list[Domain]:
        result = await db.execute(
            select(Domain)
            .where(Domain.subject_id == subject_id, Domain.is_active.is_(True))
            .order_by(Domain.order)
        )
        return list(result.scalars().all())

    # ── Skills ─────────────────────────────────────────────
    async def list_skills(self, db: AsyncSession, domain_id: UUID) -> list[Skill]:
        result = await db.execute(
            select(Skill)
            .where(Skill.domain_id == domain_id, Skill.is_active.is_(True))
            .order_by(Skill.order)
        )
        return list(result.scalars().all())

    async def list_skills_by_subject(self, db: AsyncSession, subject_id: UUID) -> list[Skill]:
        result = await db.execute(
            select(Skill)
            .join(Domain, Skill.domain_id == Domain.id)
            .options(selectinload(Skill.domain))
            .where(Domain.subject_id == subject_id, Skill.is_active.is_(True))
            .order_by(Domain.order, Skill.order)
        )
        return list(result.scalars().all())

    async def get_skill(self, db: AsyncSession, skill_id: UUID) -> Skill:
        result = await db.execute(
            select(Skill)
            .options(selectinload(Skill.lessons))
            .where(Skill.id == skill_id)
        )
        skill = result.scalar_one_or_none()
        if not skill:
            raise NotFoundException("Compétence", str(skill_id))
        return skill

    # ── MicroSkills ────────────────────────────────────────
    async def list_micro_skills(self, db: AsyncSession, skill_id: UUID) -> list[MicroSkill]:
        result = await db.execute(
            select(MicroSkill)
            .where(MicroSkill.skill_id == skill_id, MicroSkill.is_active.is_(True))
            .order_by(MicroSkill.order)
        )
        return list(result.scalars().all())

    async def get_micro_skill(self, db: AsyncSession, micro_skill_id: UUID) -> MicroSkill:
        result = await db.execute(
            select(MicroSkill).where(MicroSkill.id == micro_skill_id)
        )
        ms = result.scalar_one_or_none()
        if not ms:
            raise NotFoundException("Micro-compétence", str(micro_skill_id))
        return ms

    # ── Questions ──────────────────────────────────────────
    async def list_questions(
        self, db: AsyncSession, skill_id: UUID, micro_skill_id: UUID | None = None
    ) -> list[Question]:
        from app.models.content import ContentStatus
        stmt = select(Question).where(
            Question.skill_id == skill_id,
            Question.is_active.is_(True),
            Question.status == ContentStatus.PUBLISHED,
        )
        if micro_skill_id:
            stmt = stmt.where(Question.micro_skill_id == micro_skill_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    # ── Lessons ────────────────────────────────────────────
    async def list_lessons(self, db: AsyncSession, skill_id: UUID) -> list[MicroLesson]:
        from app.models.content import ContentStatus
        result = await db.execute(
            select(MicroLesson)
            .where(
                MicroLesson.skill_id == skill_id,
                MicroLesson.is_active.is_(True),
                MicroLesson.status == ContentStatus.PUBLISHED,
            )
            .order_by(MicroLesson.order)
        )
        return list(result.scalars().all())


content_service = ContentService()
