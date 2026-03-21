"""Badge endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_active_profile, require_role
from app.db.session import get_db_session
from app.models.profile import Profile
from app.models.user import User, UserRole
from app.schemas.response import ok
from app.services.badge_service import badge_service

router = APIRouter(tags=["Badges"])


@router.get("/students/me/badges")
async def my_badges(
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    badges = await badge_service.get_student_badges(db, profile.id)
    return ok(data=badges)


@router.get("/students/me/badges/collection")
async def my_badge_collection(
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    """All badges with earned/locked status for the collection page."""
    badges = await badge_service.get_all_badges_with_status(db, profile.id)
    return ok(data=badges)


@router.get("/students/{profile_id}/badges")
async def student_badges(
    profile_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(require_role(UserRole.PARENT, UserRole.ADMIN)),
):
    badges = await badge_service.get_student_badges(db, profile_id)
    return ok(data=badges)
