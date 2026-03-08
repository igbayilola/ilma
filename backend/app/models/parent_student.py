"""Parent ↔ Student N:N link + weekly goal."""
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseMixin


class ParentStudent(Base, BaseMixin):
    __tablename__ = "parent_students"

    parent_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    weekly_goal_minutes = Column(Integer, default=120)
    nickname = Column(String(100), nullable=True)

    parent = relationship("User", foreign_keys=[parent_id], back_populates="children")
    student = relationship("User", foreign_keys=[student_id], back_populates="parents")
