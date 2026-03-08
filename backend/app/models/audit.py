"""Audit log for security events."""
from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.db.base import Base
from app.models.base import BaseMixin


class AuditLog(Base, BaseMixin):
    __tablename__ = "audit_logs"

    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    details = Column(JSONB, nullable=True)
