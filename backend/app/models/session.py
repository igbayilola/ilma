"""Exercise sessions and attempts."""
import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseMixin


class SessionMode(str, enum.Enum):
    PRACTICE = "practice"
    DAILY_CHALLENGE = "daily_challenge"
    REVISION = "revision"
    EXAM = "exam"
    CALCUL_MENTAL = "calcul_mental"


class SessionStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class ExerciseSession(Base, BaseMixin):
    __tablename__ = "exercise_sessions"

    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=True, index=True)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="SET NULL"), nullable=True, index=True)
    micro_skill_id = Column(UUID(as_uuid=True), ForeignKey("micro_skills.id", ondelete="SET NULL"), nullable=True, index=True)
    mode = Column(Enum(SessionMode), nullable=False, default=SessionMode.PRACTICE)
    status = Column(Enum(SessionStatus), nullable=False, default=SessionStatus.IN_PROGRESS)
    total_questions = Column(Integer, default=0, nullable=False)
    correct_answers = Column(Integer, default=0, nullable=False)
    score = Column(Float, default=0.0, nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    synced_at = Column(DateTime(timezone=True), nullable=True)

    profile = relationship("Profile", back_populates="sessions")
    attempts = relationship("Attempt", back_populates="session", order_by="Attempt.created_at", lazy="raise")


class Attempt(Base, BaseMixin):
    __tablename__ = "attempts"

    session_id = Column(UUID(as_uuid=True), ForeignKey("exercise_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="SET NULL"), nullable=True, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=True, index=True)
    client_event_id = Column(String(100), unique=True, nullable=False, index=True)
    answer = Column(JSONB, nullable=True)
    is_correct = Column(Boolean, nullable=False, default=False)
    points_earned = Column(Integer, default=0, nullable=False)
    time_spent_seconds = Column(Integer, nullable=True)
    synced_at = Column(DateTime(timezone=True), nullable=True)

    session = relationship("ExerciseSession", back_populates="attempts")
