"""In-app / SMS / push notifications."""
import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseMixin


class NotificationType(str, enum.Enum):
    INACTIVITY = "inactivity"
    BADGE_EARNED = "badge_earned"
    GOAL_REACHED = "goal_reached"
    WEEKLY_REPORT = "weekly_report"
    SUBSCRIPTION = "subscription"
    SYSTEM = "system"


class NotificationChannel(str, enum.Enum):
    IN_APP = "in_app"
    SMS = "sms"
    PUSH = "push"


class Notification(Base, BaseMixin):
    __tablename__ = "notifications"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(Enum(NotificationType), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False, default=NotificationChannel.IN_APP)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=True)
    data = Column(JSONB, nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="notifications")
