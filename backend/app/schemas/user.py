"""User Pydantic schemas."""
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.user import UserRole


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    role: Optional[UserRole] = None
    grade_level_id: Optional[uuid.UUID] = None


class UserCreate(UserBase):
    email: Optional[EmailStr] = None
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[UserRole] = UserRole.PARENT
    grade_level_id: Optional[uuid.UUID] = None


class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


class User(UserInDBBase):
    """Returned to the client (no password)."""
    pass


class UserInDB(UserInDBBase):
    hashed_password: str
