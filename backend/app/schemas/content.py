"""Content Pydantic schemas."""
import uuid
from typing import Annotated, Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.content import DifficultyLevel, QuestionType


# ── GradeLevel ────────────────────────────────────────────
class GradeLevelBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    order: int = 0
    is_active: bool = True


class GradeLevelCreate(GradeLevelBase):
    pass


class GradeLevelUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None


class GradeLevelOut(GradeLevelBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


# ── French type name mapping ─────────────────────────────
FRENCH_TYPE_MAP: Dict[str, QuestionType] = {
    "QCM": QuestionType.MCQ,
    "Vrai/Faux": QuestionType.TRUE_FALSE,
    "Compléter": QuestionType.FILL_BLANK,
    "Réponse numérique": QuestionType.NUMERIC_INPUT,
    "Réponse courte": QuestionType.SHORT_ANSWER,
    "Classement": QuestionType.ORDERING,
    "Glisser-déposer": QuestionType.MATCHING,
    "Correction d'erreur": QuestionType.ERROR_CORRECTION,
    "Problème contextualisé": QuestionType.CONTEXTUAL_PROBLEM,
    "Étapes guidées": QuestionType.GUIDED_STEPS,
    "Justification": QuestionType.JUSTIFICATION,
    "Tracer": QuestionType.TRACING,
}


# ── Subject ────────────────────────────────────────────────
class SubjectBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    order: int = 0
    is_active: bool = True
    grade_level_id: Optional[uuid.UUID] = None


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None
    grade_level_id: Optional[uuid.UUID] = None


class SubjectOut(SubjectBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


# ── Domain ─────────────────────────────────────────────────
class DomainBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    order: int = 0
    is_active: bool = True


class DomainCreate(DomainBase):
    subject_id: uuid.UUID


class DomainUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None


class DomainOut(DomainBase):
    id: uuid.UUID
    subject_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


# ── Skill ──────────────────────────────────────────────────
class SkillBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    order: int = 0
    is_active: bool = True


class SkillCreate(SkillBase):
    domain_id: uuid.UUID


class SkillUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None


class SkillOut(SkillBase):
    id: uuid.UUID
    domain_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


# ── MicroSkill ─────────────────────────────────────────────
class MicroSkillBase(BaseModel):
    name: str
    external_id: Optional[str] = None
    difficulty_index: Optional[int] = None
    estimated_time_minutes: Optional[int] = None
    bloom_taxonomy_level: Optional[str] = None
    mastery_threshold: Optional[str] = None
    cep_frequency: Optional[int] = None
    prerequisites: Optional[List[str]] = None
    recommended_exercise_types: Optional[List[str]] = None
    order: int = 0
    is_active: bool = True


class MicroSkillCreate(MicroSkillBase):
    skill_id: uuid.UUID


class MicroSkillUpdate(BaseModel):
    name: Optional[str] = None
    difficulty_index: Optional[int] = None
    estimated_time_minutes: Optional[int] = None
    bloom_taxonomy_level: Optional[str] = None
    mastery_threshold: Optional[str] = None
    cep_frequency: Optional[int] = None
    prerequisites: Optional[List[str]] = None
    recommended_exercise_types: Optional[List[str]] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None


class MicroSkillOut(MicroSkillBase):
    id: uuid.UUID
    skill_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


# ── Question ───────────────────────────────────────────────
class QuestionBase(BaseModel):
    question_type: QuestionType = QuestionType.MCQ
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    text: str
    choices: Optional[list] = None
    correct_answer: object
    explanation: Optional[str] = None
    hint: Optional[str] = None
    media_url: Optional[str] = None
    points: int = 1
    time_limit_seconds: Optional[int] = 60
    bloom_level: Optional[str] = None
    ilma_level: Optional[str] = None
    tags: Optional[List[str]] = None
    common_mistake_targeted: Optional[str] = None
    is_active: bool = True


class QuestionCreate(QuestionBase):
    skill_id: uuid.UUID
    micro_skill_id: Optional[uuid.UUID] = None
    external_id: Optional[str] = None


class QuestionUpdate(BaseModel):
    question_type: Optional[QuestionType] = None
    difficulty: Optional[DifficultyLevel] = None
    text: Optional[str] = None
    choices: Optional[list] = None
    correct_answer: Optional[object] = None
    explanation: Optional[str] = None
    hint: Optional[str] = None
    points: Optional[int] = None
    time_limit_seconds: Optional[int] = None
    bloom_level: Optional[str] = None
    ilma_level: Optional[str] = None
    tags: Optional[List[str]] = None
    common_mistake_targeted: Optional[str] = None
    is_active: Optional[bool] = None


class QuestionOut(QuestionBase):
    id: uuid.UUID
    skill_id: uuid.UUID
    micro_skill_id: Optional[uuid.UUID] = None
    external_id: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# ── Micro Lesson ───────────────────────────────────────────
class LessonBase(BaseModel):
    title: str
    content_html: str
    summary: Optional[str] = None
    media_url: Optional[str] = None
    duration_minutes: int = 5
    order: int = 0
    is_active: bool = True


class LessonCreate(LessonBase):
    skill_id: uuid.UUID
    micro_skill_id: Optional[uuid.UUID] = None


class LessonUpdate(BaseModel):
    title: Optional[str] = None
    content_html: Optional[str] = None
    summary: Optional[str] = None
    media_url: Optional[str] = None
    duration_minutes: Optional[int] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None


class LessonOut(LessonBase):
    id: uuid.UUID
    skill_id: uuid.UUID
    micro_skill_id: Optional[uuid.UUID] = None
    model_config = ConfigDict(from_attributes=True)


# ── Bulk Exercise Import Schemas ──────────────────────────

class ExerciseBase(BaseModel):
    """Common fields for every exercise in the bulk import payload."""
    exercise_id: str = Field(..., description="Business ID, e.g. EX001")
    type: QuestionType
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    text: str = Field(..., min_length=1)
    correct_answer: Any
    explanation: Optional[str] = None
    hint: Optional[str] = None
    points: int = 1
    time_limit_seconds: Optional[int] = 60
    bloom_level: Optional[str] = None
    ilma_level: Optional[str] = None
    tags: Optional[List[str]] = None
    common_mistake_targeted: Optional[str] = None
    media_url: Optional[str] = None


class MCQExercise(ExerciseBase):
    type: Literal[QuestionType.MCQ] = QuestionType.MCQ
    choices: List[str] = Field(..., min_length=2)


class TrueFalseExercise(ExerciseBase):
    type: Literal[QuestionType.TRUE_FALSE] = QuestionType.TRUE_FALSE


class FillBlankExercise(ExerciseBase):
    type: Literal[QuestionType.FILL_BLANK] = QuestionType.FILL_BLANK
    blanks: Optional[List[str]] = None


class NumericInputExercise(ExerciseBase):
    type: Literal[QuestionType.NUMERIC_INPUT] = QuestionType.NUMERIC_INPUT
    tolerance: Optional[float] = None


class ShortAnswerExercise(ExerciseBase):
    type: Literal[QuestionType.SHORT_ANSWER] = QuestionType.SHORT_ANSWER
    accepted_answers: Optional[List[str]] = None


class OrderingExercise(ExerciseBase):
    type: Literal[QuestionType.ORDERING] = QuestionType.ORDERING
    items: List[str] = Field(..., min_length=2)


class MatchingExercise(ExerciseBase):
    type: Literal[QuestionType.MATCHING] = QuestionType.MATCHING
    left_items: List[str] = Field(..., min_length=2)
    right_items: List[str] = Field(..., min_length=2)


class ErrorCorrectionExercise(ExerciseBase):
    type: Literal[QuestionType.ERROR_CORRECTION] = QuestionType.ERROR_CORRECTION
    erroneous_content: Optional[str] = None


class ContextualProblemExercise(ExerciseBase):
    type: Literal[QuestionType.CONTEXTUAL_PROBLEM] = QuestionType.CONTEXTUAL_PROBLEM
    sub_questions: Optional[List[Dict[str, Any]]] = None


class GuidedStepsExercise(ExerciseBase):
    type: Literal[QuestionType.GUIDED_STEPS] = QuestionType.GUIDED_STEPS
    steps: List[Dict[str, Any]] = Field(..., min_length=1)


class JustificationExercise(ExerciseBase):
    type: Literal[QuestionType.JUSTIFICATION] = QuestionType.JUSTIFICATION
    scoring_rubric: Optional[str] = None


class TracingExercise(ExerciseBase):
    type: Literal[QuestionType.TRACING] = QuestionType.TRACING
    number_line: Optional[Dict[str, Any]] = None


ExerciseItem = Annotated[
    Union[
        MCQExercise,
        TrueFalseExercise,
        FillBlankExercise,
        NumericInputExercise,
        ShortAnswerExercise,
        OrderingExercise,
        MatchingExercise,
        ErrorCorrectionExercise,
        ContextualProblemExercise,
        GuidedStepsExercise,
        JustificationExercise,
        TracingExercise,
    ],
    Field(discriminator="type"),
]


class BulkExerciseImportRequest(BaseModel):
    micro_skill_external_id: str = Field(..., min_length=1)
    exercises: List[ExerciseItem] = Field(..., min_length=1)


class BulkExerciseImportResult(BaseModel):
    created: int = 0
    updated: int = 0
    skipped: int = 0
    errors: List[Dict[str, Any]] = Field(default_factory=list)


# ── Curriculum Import (full tree) ────────────────────────

class CurriculumMicroSkillNode(BaseModel):
    external_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    difficulty_index: Optional[int] = None
    estimated_time_minutes: Optional[int] = None
    bloom_taxonomy_level: Optional[str] = None
    mastery_threshold: Optional[str] = None
    cep_frequency: Optional[int] = None
    prerequisites: Optional[List[str]] = None
    recommended_exercise_types: Optional[List[str]] = None
    external_prerequisites: Optional[List[Dict[str, str]]] = None
    order: int = 0


class CurriculumSkillNode(BaseModel):
    external_id: Optional[str] = None
    name: str = Field(..., min_length=1)
    order: int = 0
    cep_frequency: Optional[int] = None
    prerequisites: Optional[List[str]] = None
    common_mistakes: Optional[List[str]] = None
    exercise_types: Optional[List[str]] = None
    mastery_threshold: Optional[str] = None
    micro_skills: List[CurriculumMicroSkillNode] = Field(default_factory=list)


class CurriculumDomainNode(BaseModel):
    name: str = Field(..., min_length=1)
    slug: str = Field(..., min_length=1)
    order: int = 0
    skills: List[CurriculumSkillNode] = Field(default_factory=list)


class CurriculumSubjectNode(BaseModel):
    name: str = Field(..., min_length=1)
    slug: str = Field(..., min_length=1)
    icon: Optional[str] = None
    color: Optional[str] = None
    order: int = 0
    domains: List[CurriculumDomainNode] = Field(default_factory=list)


class CurriculumGradeNode(BaseModel):
    name: str = Field(..., min_length=1)
    slug: str = Field(..., min_length=1)
    description: Optional[str] = None


class CurriculumImportRequest(BaseModel):
    schema_version: str = "2.0"
    grade: CurriculumGradeNode
    subjects: List[CurriculumSubjectNode] = Field(..., min_length=1)


# ── Curriculum Tree Output (nested read-only) ────────────

class TreeMicroSkillOut(BaseModel):
    id: uuid.UUID
    external_id: Optional[str] = None
    name: str
    difficulty_index: Optional[int] = None
    bloom_taxonomy_level: Optional[str] = None
    mastery_threshold: Optional[str] = None
    cep_frequency: Optional[int] = None
    external_prerequisites: Optional[List[Dict[str, str]]] = None
    order: int = 0
    model_config = ConfigDict(from_attributes=True)


class TreeSkillOut(BaseModel):
    id: uuid.UUID
    external_id: Optional[str] = None
    name: str
    cep_frequency: Optional[int] = None
    prerequisites: Optional[List[str]] = None
    common_mistakes: Optional[List[str]] = None
    exercise_types: Optional[List[str]] = None
    mastery_threshold: Optional[str] = None
    order: int = 0
    micro_skills: List[TreeMicroSkillOut] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class TreeDomainOut(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    order: int = 0
    skills: List[TreeSkillOut] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class TreeSubjectOut(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    icon: Optional[str] = None
    color: Optional[str] = None
    order: int = 0
    domains: List[TreeDomainOut] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class TreeGradeOut(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: Optional[str] = None
    order: int = 0
    subjects: List[TreeSubjectOut] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class CurriculumImportResult(BaseModel):
    grade_levels: int = 0
    subjects: int = 0
    domains: int = 0
    skills: int = 0
    micro_skills: int = 0
    created: int = 0
    updated: int = 0
    errors: List[Dict[str, Any]] = Field(default_factory=list)


# ── Multi-micro-skill Exercise File Import ───────────────

class ExerciseFileImportRequest(BaseModel):
    """Wraps multiple BulkExerciseImportRequest blocks into a single file."""
    schema_version: str = "1.0"
    metadata: Optional[Dict[str, Any]] = None
    exercises: List[BulkExerciseImportRequest] = Field(..., min_length=1)


class ExerciseFileImportResult(BaseModel):
    micro_skills_processed: int = 0
    created: int = 0
    updated: int = 0
    skipped: int = 0
    errors: List[Dict[str, Any]] = Field(default_factory=list)
