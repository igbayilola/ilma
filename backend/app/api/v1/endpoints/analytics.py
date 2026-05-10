"""Analytics event ingestion endpoint."""
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_active_profile
from app.db.session import get_db_session
from app.models.analytics import AnalyticsEvent
from app.models.profile import Profile
from app.schemas.response import ok

router = APIRouter(prefix="/analytics", tags=["Analytics"])

ALLOWED_EVENT_TYPES = {
    "exercise_start",
    "exercise_step_completed",
    "hint_requested",
    "exercise_completed",
    "drop_off",
    "content_viewed",
}


class EventPayload(BaseModel):
    event_type: str
    session_id: Optional[UUID] = None
    data: Optional[dict[str, Any]] = None
    client_ts: Optional[datetime] = None


class EventBatch(BaseModel):
    events: list[EventPayload] = Field(..., min_length=1, max_length=50)


@router.post("/events")
async def ingest_events(
    batch: EventBatch,
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    """Ingest a batch of analytics events (max 50)."""
    accepted = 0
    for evt in batch.events:
        if evt.event_type not in ALLOWED_EVENT_TYPES:
            continue
        db.add(AnalyticsEvent(
            event_type=evt.event_type,
            profile_id=profile.id,
            session_id=evt.session_id,
            data=evt.data,
            client_ts=evt.client_ts or datetime.now(timezone.utc),
        ))
        accepted += 1

    if accepted:
        await db.commit()

    return ok(data={"accepted": accepted})
