"""Auth-related Pydantic schemas."""
from typing import Optional

from pydantic import BaseModel, EmailStr


class OTPSendRequest(BaseModel):
    phone: str


class OTPVerifyRequest(BaseModel):
    phone: str
    code: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr
    new_password: str


class LoginRequest(BaseModel):
    identifier: Optional[str] = None  # email or phone — frontend field
    email: Optional[EmailStr] = None
    password: str


class RefreshRequest(BaseModel):
    refresh_token: Optional[str] = None
