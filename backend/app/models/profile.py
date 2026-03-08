"""Profile model — child profiles within a parent account (Netflix-style)."""
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseMixin


class Profile(Base, BaseMixin):
    __tablename__ = "profiles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    avatar_url = Column(Text, nullable=True)
    pin_hash = Column(String(255), nullable=True)
    grade_level_id = Column(UUID(as_uuid=True), ForeignKey("grade_levels.id", ondelete="SET NULL"), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    weekly_goal_minutes = Column(Integer, default=120)

    # Relationships
    user = relationship("User", back_populates="profiles")
    grade_level = relationship("GradeLevel", lazy="selectin")
    sessions = relationship("ExerciseSession", back_populates="profile", lazy="selectin")
    progress_records = relationship("Progress", back_populates="profile", lazy="selectin")
    student_badges = relationship("StudentBadge", back_populates="profile", lazy="selectin")
    subscription = relationship("Subscription", back_populates="profile", uselist=False, lazy="selectin")
