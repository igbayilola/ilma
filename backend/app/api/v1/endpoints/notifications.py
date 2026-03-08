"""Notification endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.notification import NotificationOut
from app.schemas.response import ok
from app.services.notification_service import notification_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("")
async def list_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    notifs = await notification_service.list_user_notifications(
        db, current_user.id, unread_only=unread_only, limit=limit
    )
    return ok(data=[NotificationOut.model_validate(n) for n in notifs])


@router.post("/{notification_id}/read")
async def mark_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    await notification_service.mark_read(db, notification_id, current_user.id)
    await db.commit()
    return ok(message="Notification marquée comme lue")


@router.post("/read-all")
async def mark_all_read(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    count = await notification_service.mark_all_read(db, current_user.id)
    await db.commit()
    return ok(data={"marked": count})
