"""Offline sync + content packs endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_active_profile, get_current_user
from app.db.session import get_db_session
from app.models.profile import Profile
from app.models.user import User
from app.schemas.offline import ContentPackOut, SyncRequest, SyncResponse
from app.schemas.response import ok
from app.services.sync_service import sync_service

router = APIRouter(prefix="/offline", tags=["Offline / Sync"])


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
    # In production, this would stream a ZIP file with ETag / versioning
    # For now, return metadata + a placeholder message
    from sqlalchemy import select

    from app.core.exceptions import NotFoundException
    from app.models.offline import ContentPack

    result = await db.execute(select(ContentPack).where(ContentPack.id == pack_id))
    pack = result.scalar_one_or_none()
    if not pack:
        raise NotFoundException("Content pack", str(pack_id))
    return ok(data=ContentPackOut.model_validate(pack), message="Download endpoint — ZIP streaming à implémenter avec file_path")


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
