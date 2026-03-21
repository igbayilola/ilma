"""Audit trail for content status transitions (questions & lessons)."""
from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base
from app.models.base import BaseMixin


class ContentTransition(Base, BaseMixin):
    __tablename__ = "content_transitions"

    content_type = Column(String(20), nullable=False, index=True)  # "question" or "lesson"
    content_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    from_status = Column(String(20), nullable=False)
    to_status = Column(String(20), nullable=False)
    transitioned_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    reviewer_notes = Column(Text, nullable=True)
