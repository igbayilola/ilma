"""Lightweight product analytics events."""
from sqlalchemy import Column, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.db.base import Base
from app.models.base import BaseMixin


class AnalyticsEvent(Base, BaseMixin):
    """One analytics event (exercise_start, hint_requested, drop_off, etc.)."""
    __tablename__ = "analytics_events"
    __table_args__ = (
        Index("ix_analytics_event_type", "event_type"),
        Index("ix_analytics_profile_created", "profile_id", "created_at"),
    )

    event_type = Column(String(50), nullable=False)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=True, index=True)
    session_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    data = Column(JSONB, nullable=True)
    client_ts = Column(DateTime(timezone=True), nullable=True)
    server_ts = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
