"""Notification schemas."""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.notification import NotificationChannel, NotificationType


class NotificationOut(BaseModel):
    id: uuid.UUID
    type: NotificationType
    channel: NotificationChannel
    title: str
    body: Optional[str]
    data: Optional[dict]
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class NotificationPrefs(BaseModel):
    inactivity: bool = True
    badges: bool = True
    goals: bool = True
    weekly_report: bool = True
    subscription: bool = True
