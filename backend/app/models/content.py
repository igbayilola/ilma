"""Educational content hierarchy: GradeLevel → Subject → Domain/Chapter → Skill → MicroSkill → Question / Lesson."""
import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, SmallInteger, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseMixin


class DifficultyLevel(str, enum.Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class ContentStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    IN_REVIEW = "IN_REVIEW"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class QuestionType(str, enum.Enum):
    MCQ = "MCQ"
    TRUE_FALSE = "TRUE_FALSE"
    FILL_BLANK = "FILL_BLANK"
    NUMERIC_INPUT = "NUMERIC_INPUT"
    SHORT_ANSWER = "SHORT_ANSWER"
    ORDERING = "ORDERING"
    MATCHING = "MATCHING"
    ERROR_CORRECTION = "ERROR_CORRECTION"
    CONTEXTUAL_PROBLEM = "CONTEXTUAL_PROBLEM"
    GUIDED_STEPS = "GUIDED_STEPS"
    JUSTIFICATION = "JUSTIFICATION"
    TRACING = "TRACING"
    # Interactive types (V2.1)
    DRAG_DROP = "DRAG_DROP"
    INTERACTIVE_DRAW = "INTERACTIVE_DRAW"
    CHART_INPUT = "CHART_INPUT"
    AUDIO_COMPREHENSION = "AUDIO_COMPREHENSION"


class GradeLevel(Base, BaseMixin):
    """School grade / class level (e.g. CM2, CM1, CE2, 6e)."""
    __tablename__ = "grade_levels"

    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    subjects = relationship("Subject", back_populates="grade_level", order_by="Subject.order", lazy="raise", cascade="all, delete-orphan", passive_deletes=True)


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
    domains = relationship("Domain", back_populates="subject", order_by="Domain.order", lazy="raise", cascade="all, delete-orphan", passive_deletes=True)


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
    skills = relationship("Skill", back_populates="domain", order_by="Skill.order", lazy="raise", cascade="all, delete-orphan", passive_deletes=True)


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
    # Curriculum sequencing — programme officiel MEMP Bénin, T1/T2/T3 + semaine
    # dans le trimestre (1-12). Nullable tant que le backfill contenu n'est pas
    # fait : le FE bascule sur l'heuristique "premier skill non-maîtrisé" si la
    # donnée manque.
    trimester = Column(SmallInteger, nullable=True)
    week_order = Column(SmallInteger, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    domain = relationship("Domain", back_populates="skills")
    micro_skills = relationship("MicroSkill", back_populates="skill", order_by="MicroSkill.order", lazy="raise", cascade="all, delete-orphan", passive_deletes=True)
    questions = relationship("Question", back_populates="skill", lazy="raise", cascade="all, delete-orphan", passive_deletes=True)
    lessons = relationship("MicroLesson", back_populates="skill", lazy="raise", cascade="all, delete-orphan", passive_deletes=True)


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
    questions = relationship("Question", back_populates="micro_skill", lazy="raise")
    lessons = relationship("MicroLesson", back_populates="micro_skill", lazy="raise")


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
    hint = Column(Text, nullable=True)  # Legacy single hint (kept for backward compat)
    hints = Column(JSONB, nullable=True)  # Progressive hints: ["level1", "level2", "level3"]
    media_url = Column(Text, nullable=True)
    media_references = Column(JSONB, nullable=True)    # [{id, type, url, alt_text, interactive, dimensions}]
    interactive_config = Column(JSONB, nullable=True)   # {type, config: {zones, items, canvas, validation...}}
    points = Column(Integer, default=1, nullable=False)
    time_limit_seconds = Column(Integer, default=60, nullable=True)
    bloom_level = Column(String(50), nullable=True)
    ilma_level = Column(String(50), nullable=True)
    tags = Column(JSONB, nullable=True)
    common_mistake_targeted = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    status = Column(Enum(ContentStatus, values_callable=lambda e: [x.value for x in e]), nullable=False, default=ContentStatus.PUBLISHED)
    reviewer_notes = Column(Text, nullable=True)
    version = Column(Integer, default=1, nullable=False)

    skill = relationship("Skill", back_populates="questions")
    micro_skill = relationship("MicroSkill", back_populates="questions")
    comments = relationship("QuestionComment", back_populates="question", order_by="QuestionComment.created_at", cascade="all, delete-orphan", passive_deletes=True)


class QuestionComment(Base, BaseMixin):
    """Inline comment on a question for the editorial workflow."""
    __tablename__ = "question_comments"

    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    text = Column(Text, nullable=False)

    question = relationship("Question", back_populates="comments")
    author = relationship("User", lazy="selectin")


class MicroLesson(Base, BaseMixin):
    __tablename__ = "micro_lessons"

    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    micro_skill_id = Column(UUID(as_uuid=True), ForeignKey("micro_skills.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    content_html = Column(Text, nullable=True)  # fallback for legacy lessons without sections
    sections = Column(JSONB, nullable=True)  # structured 4-step lesson: {activite_depart, retenons, exemples, evaluation_note}
    formula = Column(Text, nullable=True)  # quick-reference formula for the Formulaire page
    summary = Column(Text, nullable=True)
    media_url = Column(Text, nullable=True)
    duration_minutes = Column(Integer, default=5, nullable=False)
    order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    status = Column(Enum(ContentStatus, values_callable=lambda e: [x.value for x in e]), nullable=False, default=ContentStatus.PUBLISHED)
    reviewer_notes = Column(Text, nullable=True)
    version = Column(Integer, default=1, nullable=False)
    external_id = Column(String(100), unique=True, nullable=True, index=True)  # for upsert import

    skill = relationship("Skill", back_populates="lessons")
    micro_skill = relationship("MicroSkill", back_populates="lessons")


class ContentVersion(Base, BaseMixin):
    """Lightweight content versioning: stores JSON snapshots of questions and lessons."""
    __tablename__ = "content_versions"

    content_type = Column(String(20), nullable=False)  # "question" or "lesson"
    content_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    data_json = Column(JSONB, nullable=False)
    modified_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    modified_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
