"""Public content endpoints — subjects, domains, skills, micro_skills, questions, lessons.

Route order matters in FastAPI: static segments (/skills/..., /micro-skills/...) must be
declared BEFORE dynamic segments (/{subject_id}) to avoid shadowing.
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_active_profile, get_current_user
from app.db.session import get_db_session
from app.models.content import GradeLevel
from app.models.profile import Profile
from app.models.user import User
from app.schemas.content import DomainOut, GradeLevelOut, LessonOut, MicroSkillOut, QuestionOut, SkillOut, SubjectOut
from app.schemas.response import ok, paginated
from app.services.content_cache import get_or_set as cached
from app.services.content_service import content_service

router = APIRouter(prefix="/subjects", tags=["Content"])


# ── Public grade-levels (no auth — needed at registration) ─────────────────
@router.get("/grade-levels")
async def list_grade_levels_public(
    db: AsyncSession = Depends(get_db_session),
):
    async def _fetch():
        result = await db.execute(
            select(GradeLevel).where(GradeLevel.is_active.is_(True)).order_by(GradeLevel.order)
        )
        grades = result.scalars().all()
        return ok(data=[GradeLevelOut.model_validate(g).model_dump(mode="json") for g in grades])

    return await cached("grade_levels", _fetch)


# ── Static sub-routes first (avoid shadowing by /{subject_id}) ─────────────

@router.get("/formulas")
async def list_formulas(
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    """List all formulas and rules for the Formulaire page."""
    gid = getattr(user, "grade_level_id", None)

    async def _fetch():
        formulas = await content_service.list_formulas(db, grade_level_id=gid)
        return ok(data=formulas)

    return await cached(f"formulas:{gid or 'all'}", _fetch)


@router.get("/skills/{skill_id}/micro-skills")
async def list_micro_skills(
    skill_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(get_current_user),
):
    async def _fetch():
        micro_skills = await content_service.list_micro_skills(db, skill_id)
        return ok(data=[MicroSkillOut.model_validate(ms).model_dump(mode="json") for ms in micro_skills])

    return await cached(f"micro_skills:{skill_id}", _fetch)


@router.get("/skills/{skill_id}/prerequisites")
async def check_prerequisites(
    skill_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    """Check if the active profile meets the prerequisites for a skill."""
    from app.services.prerequisite_service import prerequisite_service
    result = await prerequisite_service.check_skill_prerequisites(db, profile.id, skill_id)
    return ok(data=result)


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
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(get_current_user),
):
    ms_part = f":{micro_skill_id}" if micro_skill_id else ""
    cache_key = f"questions:{skill_id}{ms_part}:p{page}:{page_size}"

    async def _fetch():
        skip = (page - 1) * page_size
        questions, total = await content_service.list_questions(
            db, skill_id, micro_skill_id=micro_skill_id, skip=skip, limit=page_size,
        )
        return paginated(
            items=[QuestionOut.model_validate(q).model_dump(mode="json") for q in questions],
            total=total, page=page, page_size=page_size,
        )

    return await cached(cache_key, _fetch)


@router.get("/skills/{skill_id}")
async def get_skill(
    skill_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(get_current_user),
):
    async def _fetch():
        skill = await content_service.get_skill(db, skill_id)
        data = SkillOut.model_validate(skill).model_dump(mode="json")
        lessons = [LessonOut.model_validate(lesson).model_dump(mode="json") for lesson in skill.lessons] if skill.lessons else []
        micro_skills = [MicroSkillOut.model_validate(ms).model_dump(mode="json") for ms in skill.micro_skills] if skill.micro_skills else []
        return ok(data={"skill": data, "lessons": lessons, "micro_skills": micro_skills})

    return await cached(f"skill:{skill_id}", _fetch)


# ── Subject-scoped routes ───────────────────────────────────────────────────

@router.get("")
async def list_subjects(
    grade_level_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    gid = grade_level_id or getattr(user, "grade_level_id", None)

    async def _fetch():
        subjects = await content_service.list_subjects(db, grade_level_id=gid)
        return ok(data=[SubjectOut.model_validate(s).model_dump(mode="json") for s in subjects])

    return await cached(f"subjects:{gid or 'all'}", _fetch)


@router.get("/{subject_id}/chapters/{domain_id}/skills")
async def list_skills(
    domain_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(get_current_user),
):
    async def _fetch():
        skip = (page - 1) * page_size
        skills, total = await content_service.list_skills(db, domain_id, skip=skip, limit=page_size)
        return paginated(
            items=[SkillOut.model_validate(s).model_dump(mode="json") for s in skills],
            total=total, page=page, page_size=page_size,
        )

    return await cached(f"skills:{domain_id}:p{page}:{page_size}", _fetch)


@router.get("/{subject_id}/chapters")
async def list_domains(
    subject_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(get_current_user),
):
    async def _fetch():
        domains = await content_service.list_domains(db, subject_id)
        return ok(data=[DomainOut.model_validate(d).model_dump(mode="json") for d in domains])

    return await cached(f"domains:{subject_id}", _fetch)


@router.get("/{subject_id}/skills")
async def list_skills_by_subject(
    subject_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(get_current_user),
):
    async def _fetch():
        skip = (page - 1) * page_size
        skills, total = await content_service.list_skills_by_subject(
            db, subject_id, skip=skip, limit=page_size,
        )
        items = []
        for s in skills:
            d = SkillOut.model_validate(s).model_dump(mode="json")
            d["domain_name"] = s.domain.name if s.domain else None
            items.append(d)
        return paginated(items=items, total=total, page=page, page_size=page_size)

    return await cached(f"skills_by_subject:{subject_id}:p{page}:{page_size}", _fetch)


@router.get("/{subject_id}")
async def get_subject(
    subject_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(get_current_user),
):
    async def _fetch():
        subj = await content_service.get_subject(db, subject_id)
        return ok(data=SubjectOut.model_validate(subj).model_dump(mode="json"))

    return await cached(f"subject:{subject_id}", _fetch)
