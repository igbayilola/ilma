"""Classroom, classroom-student link, and assignment models for teacher features."""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseMixin


class Classroom(Base, BaseMixin):
    __tablename__ = "classrooms"

    teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    invite_code = Column(String(8), unique=True, nullable=False, index=True)
    grade_level_id = Column(UUID(as_uuid=True), ForeignKey("grade_levels.id", ondelete="SET NULL"), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    max_students = Column(Integer, default=30, nullable=False)

    # Relationships
    teacher = relationship("User", foreign_keys=[teacher_id], lazy="raise")
    grade_level = relationship("GradeLevel", lazy="selectin")
    students = relationship("ClassroomStudent", back_populates="classroom", lazy="raise")
    assignments = relationship("Assignment", back_populates="classroom", lazy="raise")


class ClassroomStudent(Base, BaseMixin):
    __tablename__ = "classroom_students"
    __table_args__ = (
        UniqueConstraint("classroom_id", "profile_id", name="uq_classroom_profile"),
    )

    classroom_id = Column(UUID(as_uuid=True), ForeignKey("classrooms.id", ondelete="CASCADE"), nullable=False, index=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    classroom = relationship("Classroom", back_populates="students")
    profile = relationship("Profile", lazy="selectin")


class Assignment(Base, BaseMixin):
    __tablename__ = "assignments"

    classroom_id = Column(UUID(as_uuid=True), ForeignKey("classrooms.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    question_count = Column(Integer, default=10, nullable=False)

    # Relationships
    classroom = relationship("Classroom", back_populates="assignments")
    skill = relationship("Skill", lazy="selectin")
    creator = relationship("User", foreign_keys=[created_by], lazy="raise")
