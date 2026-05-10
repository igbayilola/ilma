"""Badges and student badge awards."""
import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID  # noqa: F401 — JSONB used by Badge.criteria
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseMixin


class BadgeCategory(str, enum.Enum):
    STREAK = "streak"
    MASTERY = "mastery"
    COMPLETION = "completion"
    EXPLORATION = "exploration"
    CEP = "cep"
    SOCIAL = "social"
    SPECIAL = "special"


class Badge(Base, BaseMixin):
    __tablename__ = "badges"

    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)
    category = Column(Enum(BadgeCategory), nullable=False, default=BadgeCategory.COMPLETION)
    criteria = Column(JSONB, nullable=True)

    student_badges = relationship("StudentBadge", back_populates="badge", lazy="raise")


class StudentBadge(Base, BaseMixin):
    __tablename__ = "student_badges"

    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=True, index=True)
    badge_id = Column(UUID(as_uuid=True), ForeignKey("badges.id", ondelete="CASCADE"), nullable=False, index=True)
    client_event_id = Column(String(100), unique=True, nullable=True, index=True)
    awarded_at = Column(DateTime(timezone=True), nullable=False)
    synced_at = Column(DateTime(timezone=True), nullable=True)

    profile = relationship("Profile", back_populates="student_badges")
    badge = relationship("Badge", back_populates="student_badges")
