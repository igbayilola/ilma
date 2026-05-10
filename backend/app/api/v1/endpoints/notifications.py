"""Notification endpoints."""
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db_session
from app.models.notification import NotificationType
from app.models.parent_student import ParentStudent
from app.models.push_subscription import PushSubscription
from app.models.session import ExerciseSession, SessionStatus
from app.models.user import User, UserRole
from app.schemas.notification import NotificationOut
from app.schemas.response import ok
from app.services.notification_service import notification_service

logger = logging.getLogger(__name__)

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


@router.post("/trigger-digest")
async def trigger_digest(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Send an on-demand weekly SMS digest for the current parent user."""
    if current_user.role != UserRole.PARENT:
        raise HTTPException(status_code=403, detail="Réservé aux parents")

    week_ago = datetime.now(timezone.utc) - timedelta(days=7)

    # Find linked children
    children_result = await db.execute(
        select(ParentStudent).where(ParentStudent.parent_id == current_user.id)
    )
    links = list(children_result.scalars().all())

    if not links:
        return ok(message="Aucun enfant lié à votre compte")

    # Build summary per child
    summaries: list[str] = []
    for link in links:
        child_result = await db.execute(
            select(User).where(User.id == link.student_id)
        )
        child = child_result.scalar_one_or_none()
        if not child:
            continue

        sessions_count = await db.execute(
            select(func.count(ExerciseSession.id)).where(
                ExerciseSession.student_id == child.id,
                ExerciseSession.status == SessionStatus.COMPLETED,
                ExerciseSession.completed_at >= week_ago,
            )
        )
        count = sessions_count.scalar() or 0

        time_result = await db.execute(
            select(func.coalesce(func.sum(ExerciseSession.duration_seconds), 0)).where(
                ExerciseSession.student_id == child.id,
                ExerciseSession.status == SessionStatus.COMPLETED,
                ExerciseSession.completed_at >= week_ago,
            )
        )
        total_seconds = time_result.scalar() or 0
        total_minutes = total_seconds // 60

        name = child.full_name or "Votre enfant"
        if count == 0:
            summaries.append(f"- {name} : inactif cette semaine")
        else:
            summaries.append(f"- {name} : {count} exercice(s), {total_minutes} min")

    if not summaries:
        return ok(message="Aucun résumé disponible")

    body = "Résumé de la semaine :\n" + "\n".join(summaries)

    await notification_service.create_multi_channel(
        db=db,
        user_id=current_user.id,
        type=NotificationType.WEEKLY_REPORT,
        title="Résumé hebdomadaire Sitou",
        body=body,
        phone=current_user.phone,
    )
    await db.commit()

    logger.info("[DIGEST] On-demand digest sent for parent %s", current_user.id)
    return ok(message="Digest SMS envoyé avec succès")


# ── Notification Preferences ──────────────────────────────────


class NotificationPrefsUpdate(PydanticBaseModel):
    sms_digest: Optional[bool] = None
    push_enabled: Optional[bool] = None
    inactivity_alerts: Optional[bool] = None


@router.get("/preferences")
async def get_notification_prefs(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    prefs = current_user.notification_prefs or {
        "sms_digest": True,
        "push_enabled": True,
        "inactivity_alerts": True,
    }
    return ok(data=prefs)


@router.patch("/preferences")
async def update_notification_prefs(
    body: NotificationPrefsUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    prefs = dict(current_user.notification_prefs or {
        "sms_digest": True,
        "push_enabled": True,
        "inactivity_alerts": True,
    })
    updates = body.model_dump(exclude_unset=True)
    prefs.update(updates)
    current_user.notification_prefs = prefs
    await db.commit()
    return ok(data=prefs)


# ── Push Subscription ────────────────────────────────────────


class PushSubscriptionCreate(PydanticBaseModel):
    endpoint: str
    keys: dict


@router.post("/push-subscription")
async def register_push_subscription(
    body: PushSubscriptionCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Register or update a Web Push subscription for the current user."""
    # Upsert: if endpoint already exists, update keys and user
    result = await db.execute(
        select(PushSubscription).where(PushSubscription.endpoint == body.endpoint)
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.user_id = current_user.id
        existing.keys_json = body.keys
    else:
        sub = PushSubscription(
            id=uuid.uuid4(),
            user_id=current_user.id,
            endpoint=body.endpoint,
            keys_json=body.keys,
        )
        db.add(sub)
    await db.commit()
    return ok(message="Push subscription enregistrée")


@router.delete("/push-subscription")
async def remove_push_subscription(
    body: PushSubscriptionCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Remove a Web Push subscription."""
    result = await db.execute(
        select(PushSubscription).where(
            PushSubscription.endpoint == body.endpoint,
            PushSubscription.user_id == current_user.id,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        await db.delete(existing)
        await db.commit()
    return ok(message="Push subscription supprimée")
