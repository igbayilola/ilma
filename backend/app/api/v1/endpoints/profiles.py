"""Profile endpoints: Netflix-style child profiles CRUD + PIN verification."""
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.exceptions import AppException
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.profile import (
    PinVerifyRequest,
    ProfileCreate,
    ProfileOut,
    ProfileUpdate,
    WeeklyGoalRequest,
)
from app.schemas.response import ok
from app.services.profile_service import profile_service

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.get("")
async def list_profiles(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """List all active profiles for the current account (Netflix selector)."""
    profiles = await profile_service.list_profiles(db, current_user)
    return ok(data=profiles)


@router.post("", status_code=201)
async def create_profile(
    body: ProfileCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Create a child profile (parent creates profiles for children)."""
    profile = await profile_service.create_profile(
        db, current_user,
        display_name=body.display_name,
        avatar_url=body.avatar_url,
        pin=body.pin,
        grade_level_id=body.grade_level_id,
    )
    await db.commit()
    profiles = await profile_service.list_profiles(db, current_user)
    # Return the newly created profile
    created = next((p for p in profiles if p["id"] == str(profile.id)), None)
    return ok(data=created, message="Profil créé avec succès")


@router.get("/{profile_id}")
async def get_profile(
    profile_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get a single profile by ID."""
    profile = await profile_service.get_profile(db, current_user, profile_id)
    profiles = await profile_service.list_profiles(db, current_user)
    data = next((p for p in profiles if p["id"] == str(profile.id)), None)
    return ok(data=data)


@router.patch("/{profile_id}")
async def update_profile(
    profile_id: UUID,
    body: ProfileUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Update a profile (name, avatar, PIN, grade)."""
    profile = await profile_service.get_profile(db, current_user, profile_id)
    await profile_service.update_profile(
        db, profile,
        display_name=body.display_name,
        avatar_url=body.avatar_url,
        pin=body.pin,
        grade_level_id=body.grade_level_id,
    )
    await db.commit()
    # Return updated profile data
    profiles = await profile_service.list_profiles(db, current_user)
    updated = next((p for p in profiles if p["id"] == str(profile.id)), None)
    return ok(data=updated, message="Profil mis à jour")


@router.delete("/{profile_id}")
async def delete_profile(
    profile_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Soft-delete a profile."""
    profile = await profile_service.get_profile(db, current_user, profile_id)
    await profile_service.delete_profile(db, profile)
    await db.commit()
    return ok(message="Profil supprimé")


@router.post("/{profile_id}/verify-pin")
async def verify_pin(
    profile_id: UUID,
    body: PinVerifyRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Verify the PIN of a profile before entering it."""
    profile = await profile_service.get_profile(db, current_user, profile_id)
    valid = await profile_service.verify_pin(db, profile, body.pin)
    if not valid:
        raise AppException(status_code=403, code="INVALID_PIN", message="Code PIN incorrect.")
    return ok(message="PIN vérifié")


@router.patch("/{profile_id}/goal")
async def set_weekly_goal(
    profile_id: UUID,
    body: WeeklyGoalRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Set the weekly goal for a profile."""
    profile = await profile_service.get_profile(db, current_user, profile_id)
    await profile_service.set_weekly_goal(db, profile, body.weekly_goal_minutes)
    await db.commit()
    return ok(message="Objectif hebdomadaire mis à jour")
