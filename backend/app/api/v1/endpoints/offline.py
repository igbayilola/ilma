"""Offline sync + content packs endpoints."""
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_active_profile, get_current_user
from app.core.exceptions import NotFoundException
from app.db.session import get_db_session
from app.models.profile import Profile
from app.models.user import User
from app.schemas.offline import ContentPackOut, SyncRequest, SyncResponse
from app.schemas.response import ok
from app.services.pack_service import pack_service
from app.services.sync_service import sync_service

router = APIRouter(prefix="/offline", tags=["Offline / Sync"])


# ── Per-skill content packs ──────────────────────────────────


@router.get("/packs/skills")
async def list_skill_packs(
    grade_level_id: UUID | None = Query(None),
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(get_current_user),
):
    """List available per-skill micro packs with size estimates."""
    packs = await pack_service.list_skill_packs(db, grade_level_id)
    return ok(data=packs)


@router.get("/packs/skills/{skill_id}")
async def get_skill_pack(
    skill_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(get_current_user),
):
    """Download a full content pack for a single skill (questions + lessons JSON)."""
    pack = await pack_service.build_skill_pack(db, skill_id)
    if not pack:
        raise NotFoundException("Skill", str(skill_id))
    return ok(data=pack)


@router.get("/packs/skills/{skill_id}/download")
async def download_skill_pack_s3(
    skill_id: UUID,
    _user: User = Depends(get_current_user),
):
    """Redirect to the S3/Minio URL for a pre-built skill pack."""
    from app.services.s3_service import s3_service

    if not s3_service.pack_exists(str(skill_id)):
        raise NotFoundException("Skill pack", str(skill_id))
    url = s3_service.get_pack_url(str(skill_id))
    return RedirectResponse(url=url, status_code=302)


@router.get("/packs/delta")
async def get_delta_packs(
    since: datetime = Query(..., description="ISO timestamp to check changes since"),
    grade_level_id: UUID | None = Query(None),
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(get_current_user),
):
    """Return skill IDs that have changed since the given timestamp (delta sync)."""
    changes = await pack_service.get_delta_packs(db, since, grade_level_id)
    return ok(data=changes)


# ── Legacy monolithic packs (backward compat) ────────────────


@router.get("/packs")
async def list_packs(
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(get_current_user),
):
    packs = await sync_service.list_packs(db)
    return ok(data=[ContentPackOut.model_validate(p) for p in packs])


@router.get("/packs/{pack_id}/download")
async def download_pack(
    pack_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(get_current_user),
):
    from sqlalchemy import select

    from app.models.offline import ContentPack

    result = await db.execute(select(ContentPack).where(ContentPack.id == pack_id))
    pack = result.scalar_one_or_none()
    if not pack:
        raise NotFoundException("Content pack", str(pack_id))
    return ok(data=ContentPackOut.model_validate(pack), message="Download endpoint — ZIP streaming à implémenter avec file_path")


# ── Sync events ──────────────────────────────────────────────


@router.post("/sync")
async def sync_events(
    body: SyncRequest,
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    result = await sync_service.process_batch(db, profile, body.events)
    await db.commit()
    return ok(data=SyncResponse(**result))


@router.get("/sync/status")
async def sync_status(
    _user: User = Depends(get_current_user),
):
    return ok(data={"status": "idle", "last_sync": None, "pending_events": 0})
