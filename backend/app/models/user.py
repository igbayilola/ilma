"""User model — students, parents, admins."""
import enum

from sqlalchemy import Boolean, Column, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseMixin


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    PARENT = "parent"
    STUDENT = "student"
    TEACHER = "teacher"
    GUEST = "guest"


class User(Base, BaseMixin):
    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String(255), index=True)
    role = Column(Enum(UserRole), default=UserRole.STUDENT, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    avatar_url = Column(Text, nullable=True)
    link_code = Column(String(6), unique=True, nullable=True, index=True)
    grade_level_id = Column(UUID(as_uuid=True), ForeignKey("grade_levels.id", ondelete="SET NULL"), nullable=True, index=True)
    notification_prefs = Column(JSONB, nullable=True, default=lambda: {
        "sms_digest": True,
        "push_enabled": True,
        "inactivity_alerts": True,
    })

    # Relationships
    grade_level = relationship("GradeLevel", lazy="selectin")
    profiles = relationship("Profile", back_populates="user", lazy="selectin")
    notifications = relationship("Notification", back_populates="user", lazy="selectin")

    # Parent-student relationships (legacy — kept for migration period)
    children = relationship(
        "ParentStudent", foreign_keys="ParentStudent.parent_id", back_populates="parent", lazy="selectin"
    )
    parents = relationship(
        "ParentStudent", foreign_keys="ParentStudent.student_id", back_populates="student", lazy="selectin"
    )
