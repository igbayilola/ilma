"""Mock exam (Examen Blanc) models for CEP preparation."""
from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, Text
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
    # CEP format fields
    context_text = Column(Text, nullable=True)  # overall exam context if shared across items
    exam_type = Column(String(20), default="qcm", nullable=False)  # "cep" or "qcm"

    grade_level = relationship("GradeLevel", lazy="selectin")
    subject = relationship("Subject", lazy="selectin")
    sessions = relationship("ExamSession", back_populates="mock_exam", lazy="noload")
    items = relationship("ExamItem", back_populates="mock_exam", lazy="noload", order_by="ExamItem.order")


class ExamItem(Base, BaseMixin):
    """A contextual item (problem) within a mock exam."""
    __tablename__ = "exam_items"

    mock_exam_id = Column(UUID(as_uuid=True), ForeignKey("mock_exams.id", ondelete="CASCADE"), nullable=False, index=True)
    item_number = Column(Integer, nullable=False)  # 1, 2, or 3
    domain = Column(String(50), nullable=False)  # "data_proportionality", "measures_operations", "geometry"
    context_text = Column(Text, nullable=True)  # The shared situation/support text
    points = Column(Float, default=6.67)  # ~20/3 per item
    order = Column(Integer, default=0)

    mock_exam = relationship("MockExam", back_populates="items", lazy="raise")
    sub_questions = relationship("ExamSubQuestion", back_populates="exam_item", lazy="raise", order_by="ExamSubQuestion.order")


class ExamSubQuestion(Base, BaseMixin):
    """A sub-question within an exam item."""
    __tablename__ = "exam_sub_questions"

    exam_item_id = Column(UUID(as_uuid=True), ForeignKey("exam_items.id", ondelete="CASCADE"), nullable=False, index=True)
    sub_label = Column(String(5), nullable=False)  # "a", "b", "c"
    text = Column(Text, nullable=False)  # The question text
    question_type = Column(String(30), nullable=False)  # "numeric_input", "fill_blank", "true_false", "mcq"
    correct_answer = Column(Text, nullable=False)  # Expected answer
    choices = Column(JSONB, nullable=True)  # For MCQ only
    explanation = Column(Text, nullable=True)
    hint = Column(Text, nullable=True)  # e.g. "Utilise le résultat de la question précédente"
    points = Column(Float, default=2.22)  # ~20/9 per sub-question
    depends_on_previous = Column(Boolean, default=False)  # True if answer chains from previous
    order = Column(Integer, default=0)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="SET NULL"), nullable=True)  # Link to curriculum skill

    exam_item = relationship("ExamItem", back_populates="sub_questions", lazy="raise")
    skill = relationship("Skill", lazy="raise")


class ExamSession(Base, BaseMixin):
    """A student's attempt at a mock exam."""
    __tablename__ = "exam_sessions"

    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    mock_exam_id = Column(UUID(as_uuid=True), ForeignKey("mock_exams.id", ondelete="CASCADE"), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    time_spent_seconds = Column(Integer, nullable=True)
    score = Column(Float, nullable=True)  # percentage 0-100 (for QCM) or /20 (for CEP)
    total_correct = Column(Integer, nullable=True)
    total_questions = Column(Integer, nullable=False)
    predicted_cep_score = Column(Float, nullable=True)  # X/20 prediction
    answers = Column(JSONB, default=list)  # [{question_id, answer, correct, time_seconds}] or [{item_number, sub_label, answer, correct, points_earned, time_seconds}]
    status = Column(String(20), default="in_progress", nullable=False)  # in_progress, completed, abandoned

    profile = relationship("Profile", lazy="raise")
    mock_exam = relationship("MockExam", back_populates="sessions", lazy="selectin")  # Always needed in exam_service
