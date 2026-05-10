"""Content read service — subjects, domains, skills, micro_skills, questions, lessons."""
from typing import Optional
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.models.content import ContentStatus, Domain, MicroLesson, MicroSkill, Question, Skill, Subject


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
    async def list_skills(
        self, db: AsyncSession, domain_id: UUID, *, skip: int = 0, limit: int = 50,
    ) -> tuple[list[Skill], int]:
        base = select(Skill).where(Skill.domain_id == domain_id, Skill.is_active.is_(True))
        total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
        result = await db.execute(base.order_by(Skill.order).offset(skip).limit(limit))
        return list(result.scalars().all()), total

    async def list_skills_by_subject(
        self, db: AsyncSession, subject_id: UUID, *, skip: int = 0, limit: int = 50,
    ) -> tuple[list[Skill], int]:
        base = (
            select(Skill)
            .join(Domain, Skill.domain_id == Domain.id)
            .where(Domain.subject_id == subject_id, Skill.is_active.is_(True))
        )
        total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
        result = await db.execute(
            base.options(selectinload(Skill.domain))
            .order_by(Domain.order, Skill.order)
            .offset(skip).limit(limit)
        )
        return list(result.scalars().all()), total

    async def get_skill(self, db: AsyncSession, skill_id: UUID) -> Skill:
        result = await db.execute(
            select(Skill)
            .options(selectinload(Skill.lessons), selectinload(Skill.micro_skills))
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
        self, db: AsyncSession, skill_id: UUID, micro_skill_id: UUID | None = None,
        *, skip: int = 0, limit: int = 50,
    ) -> tuple[list[Question], int]:
        from app.models.content import ContentStatus
        base = select(Question).where(
            Question.skill_id == skill_id,
            Question.is_active.is_(True),
            Question.status == ContentStatus.PUBLISHED,
        )
        if micro_skill_id:
            base = base.where(Question.micro_skill_id == micro_skill_id)
        total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
        result = await db.execute(base.offset(skip).limit(limit))
        return list(result.scalars().all()), total

    # ── Lessons ────────────────────────────────────────────
    async def list_lessons(self, db: AsyncSession, skill_id: UUID) -> list[MicroLesson]:
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

    # ── Formulas (for the Formulaire page) ────────────────
    async def list_formulas(
        self, db: AsyncSession, grade_level_id: UUID | None = None,
    ) -> list[dict]:
        """Return all lessons that have a formula or a retenons section, grouped by domain."""
        query = (
            select(
                MicroLesson.id,
                MicroLesson.title,
                MicroLesson.formula,
                MicroLesson.sections,
                MicroLesson.summary,
                MicroLesson.skill_id,
                Skill.name.label("skill_name"),
                Skill.id.label("skill_id_col"),
                Domain.name.label("domain_name"),
                Domain.id.label("domain_id"),
                Subject.name.label("subject_name"),
            )
            .join(Skill, MicroLesson.skill_id == Skill.id)
            .join(Domain, Skill.domain_id == Domain.id)
            .join(Subject, Domain.subject_id == Subject.id)
            .where(
                MicroLesson.is_active.is_(True),
                MicroLesson.status == ContentStatus.PUBLISHED,
                or_(
                    MicroLesson.formula.isnot(None),
                    MicroLesson.sections.isnot(None),
                ),
            )
            .order_by(Subject.order, Domain.order, Skill.order, MicroLesson.order)
        )
        if grade_level_id:
            query = query.where(Subject.grade_level_id == grade_level_id)

        result = await db.execute(query)
        rows = result.all()

        formulas = []
        for row in rows:
            # Extract retenons rules from sections if present
            retenons = None
            if row.sections and isinstance(row.sections, dict):
                ret_section = row.sections.get("retenons")
                if ret_section:
                    retenons = {
                        "body_html": ret_section.get("body_html", ""),
                        "rules": ret_section.get("rules", []),
                    }

            formulas.append({
                "id": str(row.id),
                "title": row.title,
                "formula": row.formula,
                "retenons": retenons,
                "summary": row.summary,
                "skill_id": str(row.skill_id_col),
                "skill_name": row.skill_name,
                "domain_id": str(row.domain_id),
                "domain_name": row.domain_name,
                "subject_name": row.subject_name,
            })

        return formulas


content_service = ContentService()
