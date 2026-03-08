"""Offline sync schemas."""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SyncEvent(BaseModel):
    event_type: str  # attempt_created | session_completed | badge_gained | profile_updated
    client_event_id: str
    payload: dict
    timestamp: datetime


class SyncRequest(BaseModel):
    events: list[SyncEvent]


class SyncEventResult(BaseModel):
    client_event_id: str
    status: str  # accepted | duplicate | error
    message: Optional[str] = None


class SyncResponse(BaseModel):
    processed: int
    accepted: int
    duplicates: int
    errors: int
    results: list[SyncEventResult]


class ContentPackOut(BaseModel):
    id: uuid.UUID
    name: str
    version: int
    checksum: Optional[str]
    size_bytes: Optional[int]
    description: Optional[str]
    published_at: Optional[datetime]
