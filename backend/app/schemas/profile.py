"""Profile schemas for Netflix-style child profiles."""
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProfileCreate(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=255)
    avatar_url: Optional[str] = None
    pin: Optional[str] = Field(None, pattern=r"^\d{4}$")
    grade_level_id: Optional[uuid.UUID] = None


class ProfileUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=1, max_length=255)
    avatar_url: Optional[str] = None
    pin: Optional[str] = Field(None, pattern=r"^\d{4}$")
    grade_level_id: Optional[uuid.UUID] = None


class ProfileOut(BaseModel):
    id: uuid.UUID
    display_name: str
    avatar_url: Optional[str]
    grade_level_id: Optional[uuid.UUID]
    is_active: bool
    has_pin: bool
    subscription_tier: str = "free"
    weekly_goal_minutes: int = 120
    model_config = ConfigDict(from_attributes=True)


class PinVerifyRequest(BaseModel):
    pin: str = Field(..., pattern=r"^\d{4}$")


class WeeklyGoalRequest(BaseModel):
    weekly_goal_minutes: int = Field(..., ge=10, le=600)
