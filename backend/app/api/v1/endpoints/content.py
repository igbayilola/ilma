"""Public content endpoints — subjects, domains, skills, micro_skills, questions, lessons.

Route order matters in FastAPI: static segments (/skills/..., /micro-skills/...) must be
declared BEFORE dynamic segments (/{subject_id}) to avoid shadowing.
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db_session
from app.models.content import GradeLevel
from app.models.user import User
from app.schemas.content import DomainOut, GradeLevelOut, LessonOut, MicroSkillOut, QuestionOut, SkillOut, SubjectOut
from app.schemas.response import ok
from app.services.content_service import content_service

router = APIRouter(prefix="/subjects", tags=["Content"])


# ── Public grade-levels (no auth — needed at registration) ─────────────────
@router.get("/grade-levels")
async def list_grade_levels_public(
    db: AsyncSession = Depends(get_db_session),
):
    result = await db.execute(
        select(GradeLevel).where(GradeLevel.is_active.is_(True)).order_by(GradeLevel.order)
    )
    grades = result.scalars().all()
    return ok(data=[GradeLevelOut.model_validate(g) for g in grades])


# ── Static sub-routes first (avoid shadowing by /{subject_id}) ─────────────

@router.get("/skills/{skill_id}/micro-skills")
async def list_micro_skills(
    skill_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(get_current_user),
):
    micro_skills = await content_service.list_micro_skills(db, skill_id)
    return ok(data=[MicroSkillOut.model_validate(ms) for ms in micro_skills])


@router.get("/micro-skills/{micro_skill_id}")
async def get_micro_skill(
    micro_skill_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(get_current_user),
):
    ms = await content_service.get_micro_skill(db, micro_skill_id)
    return ok(data=MicroSkillOut.model_validate(ms))


@router.get("/skills/{skill_id}/questions")
async def list_questions(
    skill_id: UUID,
    micro_skill_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(get_current_user),
):
    questions = await content_service.list_questions(db, skill_id, micro_skill_id=micro_skill_id)
    return ok(data=[QuestionOut.model_validate(q) for q in questions])


@router.get("/skills/{skill_id}")
async def get_skill(
    skill_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(get_current_user),
):
    skill = await content_service.get_skill(db, skill_id)
    data = SkillOut.model_validate(skill)
    lessons = [LessonOut.model_validate(lesson) for lesson in skill.lessons] if skill.lessons else []
    micro_skills = [MicroSkillOut.model_validate(ms) for ms in skill.micro_skills] if skill.micro_skills else []
    return ok(data={"skill": data, "lessons": lessons, "micro_skills": micro_skills})


# ── Subject-scoped routes ───────────────────────────────────────────────────

@router.get("")
async def list_subjects(
    grade_level_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    # Default to user's grade_level_id if not specified
    gid = grade_level_id or getattr(user, "grade_level_id", None)
    subjects = await content_service.list_subjects(db, grade_level_id=gid)
    return ok(data=[SubjectOut.model_validate(s) for s in subjects])


@router.get("/{subject_id}/chapters/{domain_id}/skills")
async def list_skills(
    domain_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(get_current_user),
):
    skills = await content_service.list_skills(db, domain_id)
    return ok(data=[SkillOut.model_validate(s) for s in skills])


@router.get("/{subject_id}/chapters")
async def list_domains(
    subject_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(get_current_user),
):
    domains = await content_service.list_domains(db, subject_id)
    return ok(data=[DomainOut.model_validate(d) for d in domains])


@router.get("/{subject_id}/skills")
async def list_skills_by_subject(
    subject_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(get_current_user),
):
    skills = await content_service.list_skills_by_subject(db, subject_id)
    data = []
    for s in skills:
        d = SkillOut.model_validate(s).model_dump()
        d["domain_name"] = s.domain.name if s.domain else None
        data.append(d)
    return ok(data=data)


@router.get("/{subject_id}")
async def get_subject(
    subject_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(get_current_user),
):
    subj = await content_service.get_subject(db, subject_id)
    return ok(data=SubjectOut.model_validate(subj))
