"""Session & attempt Pydantic schemas."""
import uuid
from datetime import datetime
from typing import Any, Optional, Union

from pydantic import BaseModel, ConfigDict

from app.models.session import SessionMode, SessionStatus


class SessionStartRequest(BaseModel):
    skill_id: uuid.UUID
    mode: SessionMode = SessionMode.PRACTICE
    micro_skill_id: Optional[uuid.UUID] = None


class AttemptRequest(BaseModel):
    question_id: uuid.UUID
    client_event_id: str
    answer: object
    time_spent_seconds: Optional[int] = None


class AttemptOut(BaseModel):
    id: uuid.UUID
    question_id: Optional[uuid.UUID]
    client_event_id: str
    is_correct: bool
    points_earned: int
    time_spent_seconds: Optional[int]
    model_config = ConfigDict(from_attributes=True)


class SessionOut(BaseModel):
    id: uuid.UUID
    student_id: Optional[uuid.UUID] = None
    profile_id: Optional[uuid.UUID] = None
    skill_id: Optional[uuid.UUID]
    micro_skill_id: Optional[uuid.UUID] = None
    mode: SessionMode
    status: SessionStatus
    total_questions: int
    correct_answers: int
    score: float
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    model_config = ConfigDict(from_attributes=True)


class NextQuestionOut(BaseModel):
    question_id: uuid.UUID
    text: str
    question_type: str
    difficulty: str
    choices: Optional[Union[list, dict]] = None
    media_url: Optional[str] = None
    time_limit_seconds: Optional[int] = None
    points: int
    micro_skill_id: Optional[uuid.UUID] = None
