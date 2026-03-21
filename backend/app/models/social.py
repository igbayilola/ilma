"""Social features: weekly leaderboard + friend challenges."""
import enum

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseMixin


class WeeklyLeaderboard(Base, BaseMixin):
    """Weekly XP leaderboard entry per profile."""
    __tablename__ = "weekly_leaderboard"

    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    week_iso = Column(String(10), nullable=False, index=True)  # e.g. "2026-W11"
    xp_earned = Column(Integer, default=0, nullable=False)
    pseudonym = Column(String(100), nullable=False)

    profile = relationship("Profile")


class ChallengeStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    COMPLETED = "completed"
    EXPIRED = "expired"
    DECLINED = "declined"


class Challenge(Base, BaseMixin):
    """Friend-to-friend skill challenge."""
    __tablename__ = "challenges"

    challenger_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    challenged_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="SET NULL"), nullable=True)
    status = Column(Enum(ChallengeStatus), nullable=False, default=ChallengeStatus.PENDING)
    challenger_score = Column(Float, nullable=True)
    challenged_score = Column(Float, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    challenger = relationship("Profile", foreign_keys=[challenger_id])
    challenged = relationship("Profile", foreign_keys=[challenged_id])
    skill = relationship("Skill")
