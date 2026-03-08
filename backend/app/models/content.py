"""Educational content hierarchy: GradeLevel → Subject → Domain/Chapter → Skill → MicroSkill → Question / Lesson."""
import enum

from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseMixin


class DifficultyLevel(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionType(str, enum.Enum):
    MCQ = "mcq"
    TRUE_FALSE = "true_false"
    FILL_BLANK = "fill_blank"
    NUMERIC_INPUT = "numeric_input"
    SHORT_ANSWER = "short_answer"
    ORDERING = "ordering"
    MATCHING = "matching"
    ERROR_CORRECTION = "error_correction"
    CONTEXTUAL_PROBLEM = "contextual_problem"
    GUIDED_STEPS = "guided_steps"
    JUSTIFICATION = "justification"
    TRACING = "tracing"


class GradeLevel(Base, BaseMixin):
    """School grade / class level (e.g. CM2, CM1, CE2, 6e)."""
    __tablename__ = "grade_levels"

    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    subjects = relationship("Subject", back_populates="grade_level", order_by="Subject.order", lazy="selectin", cascade="all, delete-orphan", passive_deletes=True)


class Subject(Base, BaseMixin):
    __tablename__ = "subjects"
    __table_args__ = (
        UniqueConstraint("slug", "grade_level_id", name="uq_subject_slug_grade"),
    )

    grade_level_id = Column(UUID(as_uuid=True), ForeignKey("grade_levels.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)
    color = Column(String(7), nullable=True)
    order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    grade_level = relationship("GradeLevel", back_populates="subjects")
    domains = relationship("Domain", back_populates="subject", order_by="Domain.order", lazy="selectin", cascade="all, delete-orphan", passive_deletes=True)


class Domain(Base, BaseMixin):
    """Chapter / domain inside a subject."""
    __tablename__ = "domains"

    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    subject = relationship("Subject", back_populates="domains")
    skills = relationship("Skill", back_populates="domain", order_by="Skill.order", lazy="selectin", cascade="all, delete-orphan", passive_deletes=True)


class Skill(Base, BaseMixin):
    __tablename__ = "skills"

    domain_id = Column(UUID(as_uuid=True), ForeignKey("domains.id", ondelete="CASCADE"), nullable=False, index=True)
    external_id = Column(String(100), unique=True, nullable=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    cep_frequency = Column(Integer, nullable=True)
    prerequisites = Column(JSONB, nullable=True)          # list of external_ids e.g. ["NUM-ENTIERS-0-1B"]
    common_mistakes = Column(JSONB, nullable=True)        # list of strings
    exercise_types = Column(JSONB, nullable=True)         # list of strings e.g. ["Choix multiples", "Compléter"]
    mastery_threshold = Column(String(100), nullable=True)  # e.g. "80% sur 10 exercices"
    order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    domain = relationship("Domain", back_populates="skills")
    micro_skills = relationship("MicroSkill", back_populates="skill", order_by="MicroSkill.order", lazy="selectin", cascade="all, delete-orphan", passive_deletes=True)
    questions = relationship("Question", back_populates="skill", lazy="selectin", cascade="all, delete-orphan", passive_deletes=True)
    lessons = relationship("MicroLesson", back_populates="skill", lazy="selectin", cascade="all, delete-orphan", passive_deletes=True)


class MicroSkill(Base, BaseMixin):
    """Sub-unit of a Skill — the most granular level of the curriculum."""
    __tablename__ = "micro_skills"

    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    # Business ID from the curriculum JSON, e.g. "NUM-ENTIERS-0-1B::MS01"
    external_id = Column(String(100), unique=True, nullable=True, index=True)
    name = Column(String(255), nullable=False)
    difficulty_index = Column(Integer, nullable=True)          # 1–10
    estimated_time_minutes = Column(Integer, nullable=True)
    bloom_taxonomy_level = Column(String(50), nullable=True)   # e.g. "Appliquer"
    mastery_threshold = Column(String(100), nullable=True)     # e.g. "85% sur 8 exercices"
    cep_frequency = Column(Integer, nullable=True)             # 0–100 or null
    # JSONB arrays
    prerequisites = Column(JSONB, nullable=True)               # list of external_ids
    recommended_exercise_types = Column(JSONB, nullable=True)  # list of strings
    external_prerequisites = Column(JSONB, nullable=True)      # list of {skill_id, micro_skill_id, why}
    order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    skill = relationship("Skill", back_populates="micro_skills")
    questions = relationship("Question", back_populates="micro_skill", lazy="selectin")
    lessons = relationship("MicroLesson", back_populates="micro_skill", lazy="selectin")


class Question(Base, BaseMixin):
    __tablename__ = "questions"

    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    micro_skill_id = Column(UUID(as_uuid=True), ForeignKey("micro_skills.id", ondelete="SET NULL"), nullable=True, index=True)
    external_id = Column(String(150), unique=True, nullable=True, index=True)
    question_type = Column(Enum(QuestionType, values_callable=lambda e: [x.value for x in e]), nullable=False, default=QuestionType.MCQ)
    difficulty = Column(Enum(DifficultyLevel, values_callable=lambda e: [x.value for x in e]), nullable=False, default=DifficultyLevel.MEDIUM)
    text = Column(Text, nullable=False)
    choices = Column(JSONB, nullable=True)
    correct_answer = Column(JSONB, nullable=False)
    explanation = Column(Text, nullable=True)
    hint = Column(Text, nullable=True)
    media_url = Column(Text, nullable=True)
    points = Column(Integer, default=1, nullable=False)
    time_limit_seconds = Column(Integer, default=60, nullable=True)
    bloom_level = Column(String(50), nullable=True)
    ilma_level = Column(String(50), nullable=True)
    tags = Column(JSONB, nullable=True)
    common_mistake_targeted = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    skill = relationship("Skill", back_populates="questions")
    micro_skill = relationship("MicroSkill", back_populates="questions")


class MicroLesson(Base, BaseMixin):
    __tablename__ = "micro_lessons"

    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    micro_skill_id = Column(UUID(as_uuid=True), ForeignKey("micro_skills.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    content_html = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    media_url = Column(Text, nullable=True)
    duration_minutes = Column(Integer, default=5, nullable=False)
    order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    skill = relationship("Skill", back_populates="lessons")
    micro_skill = relationship("MicroSkill", back_populates="lessons")
