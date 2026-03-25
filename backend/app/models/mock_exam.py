"""Mock exam (Examen Blanc) models for CEP preparation."""
from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseMixin


class MockExam(Base, BaseMixin):
    """Template for a mock exam (examen blanc)."""
    __tablename__ = "mock_exams"

    grade_level_id = Column(UUID(as_uuid=True), ForeignKey("grade_levels.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    duration_minutes = Column(Integer, default=60, nullable=False)
    total_questions = Column(Integer, default=30, nullable=False)
    question_distribution = Column(JSONB, nullable=True)  # e.g. {"easy": 10, "medium": 15, "hard": 5}
    is_free = Column(Boolean, default=False, nullable=False)  # first exam per subject is free
    is_national = Column(Boolean, default=False, nullable=False)  # national monthly exam
    national_date = Column(Date, nullable=True)  # for national exams
    is_active = Column(Boolean, default=True, nullable=False)

    grade_level = relationship("GradeLevel", lazy="selectin")
    subject = relationship("Subject", lazy="selectin")
    sessions = relationship("ExamSession", back_populates="mock_exam", lazy="noload")


class ExamSession(Base, BaseMixin):
    """A student's attempt at a mock exam."""
    __tablename__ = "exam_sessions"

    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    mock_exam_id = Column(UUID(as_uuid=True), ForeignKey("mock_exams.id", ondelete="CASCADE"), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    time_spent_seconds = Column(Integer, nullable=True)
    score = Column(Float, nullable=True)  # percentage 0-100
    total_correct = Column(Integer, nullable=True)
    total_questions = Column(Integer, nullable=False)
    predicted_cep_score = Column(Float, nullable=True)  # X/20 prediction
    answers = Column(JSONB, default=list)  # [{question_id, answer, correct, time_seconds}]
    status = Column(String(20), default="in_progress", nullable=False)  # in_progress, completed, abandoned

    profile = relationship("Profile", lazy="selectin")
    mock_exam = relationship("MockExam", back_populates="sessions", lazy="selectin")
