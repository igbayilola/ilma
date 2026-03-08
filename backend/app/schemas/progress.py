"""Micro-skill progress Pydantic schemas."""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MicroSkillProgressOut(BaseModel):
    micro_skill_id: uuid.UUID
    micro_skill_name: str
    external_id: Optional[str] = None
    difficulty_index: Optional[int] = None
    smart_score: float
    total_attempts: int
    correct_attempts: int
    streak: int
    best_streak: int
    last_attempt_at: Optional[datetime] = None
