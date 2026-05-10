"""Progress & statistics endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_active_profile, require_role
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


@router.get("/health-summary")
async def parent_health_summary(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role(UserRole.PARENT)),
):
    """Health-at-a-glance for all children of the current parent."""
    # Get all profiles belonging to this parent
    result = await db.execute(
        select(Profile).where(
            Profile.user_id == current_user.id,
            Profile.is_active.is_(True),
        )
    )
    profiles = list(result.scalars().all())

    children = []
    for profile in profiles:
        health = await progress_service.get_child_health(db, profile.id)
        children.append({
            "profile_id": str(profile.id),
            "display_name": profile.display_name,
            "avatar_url": profile.avatar_url,
            "weekly_goal_minutes": profile.weekly_goal_minutes,
            **health,
        })

    return ok(data=children)
