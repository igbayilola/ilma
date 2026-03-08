"""Progress & statistics endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_active_profile, get_current_user, require_role
from app.db.session import get_db_session
from app.models.profile import Profile
from app.models.user import User, UserRole
from app.schemas.response import ok
from app.services.progress_service import progress_service

router = APIRouter(prefix="/students", tags=["Progress"])


@router.get("/me/progress/summary")
async def my_progress_summary(
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    summary = await progress_service.get_summary(db, profile.id)
    return ok(data=summary)


@router.get("/me/progress/skills")
async def my_skills_progress(
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    skills = await progress_service.get_skills_progress(db, profile.id)
    return ok(data=skills)


@router.get("/me/progress/micro-skills")
async def my_micro_skills_progress(
    skill_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    data = await progress_service.get_micro_skills_progress(db, profile.id, skill_id)
    return ok(data=data)


@router.get("/me/stats/daily")
async def my_daily_stats(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    stats = await progress_service.get_daily_stats(db, profile.id, days)
    return ok(data=stats)


# ── Parent / Admin: view a specific profile's progress ────────
@router.get("/{profile_id}/progress/summary")
async def student_progress_summary(
    profile_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role(UserRole.PARENT, UserRole.ADMIN)),
):
    summary = await progress_service.get_summary(db, profile_id)
    return ok(data=summary)


@router.get("/{profile_id}/progress/skills")
async def student_skills_progress(
    profile_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role(UserRole.PARENT, UserRole.ADMIN)),
):
    skills = await progress_service.get_skills_progress(db, profile_id)
    return ok(data=skills)


@router.get("/{profile_id}/progress/micro-skills")
async def student_micro_skills_progress(
    profile_id: UUID,
    skill_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role(UserRole.PARENT, UserRole.ADMIN)),
):
    data = await progress_service.get_micro_skills_progress(db, profile_id, skill_id)
    return ok(data=data)
