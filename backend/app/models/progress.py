"""Student progress per skill & micro-skill — SmartScore tracking."""
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseMixin


class Progress(Base, BaseMixin):
    __tablename__ = "progress"

    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=True, index=True)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    smart_score = Column(Float, default=0.0, nullable=False)
    total_attempts = Column(Integer, default=0, nullable=False)
    correct_attempts = Column(Integer, default=0, nullable=False)
    streak = Column(Integer, default=0, nullable=False)
    best_streak = Column(Integer, default=0, nullable=False)
    last_attempt_at = Column(DateTime(timezone=True), nullable=True)
    last_decay_at = Column(DateTime(timezone=True), nullable=True)

    profile = relationship("Profile", back_populates="progress_records")


class MicroSkillProgress(Base, BaseMixin):
    __tablename__ = "micro_skill_progress"
    __table_args__ = (
        UniqueConstraint("profile_id", "micro_skill_id", name="uq_profile_micro_skill"),
    )

    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=True, index=True)
    micro_skill_id = Column(UUID(as_uuid=True), ForeignKey("micro_skills.id", ondelete="CASCADE"), nullable=False, index=True)
    smart_score = Column(Float, default=0.0, nullable=False)
    total_attempts = Column(Integer, default=0, nullable=False)
    correct_attempts = Column(Integer, default=0, nullable=False)
    streak = Column(Integer, default=0, nullable=False)
    best_streak = Column(Integer, default=0, nullable=False)
    last_attempt_at = Column(DateTime(timezone=True), nullable=True)
    last_decay_at = Column(DateTime(timezone=True), nullable=True)

    micro_skill = relationship("MicroSkill")
