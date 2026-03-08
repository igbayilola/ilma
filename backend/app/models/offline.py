"""Offline content packs metadata."""
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base
from app.models.base import BaseMixin


class ContentPack(Base, BaseMixin):
    __tablename__ = "content_packs"

    name = Column(String(255), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    checksum = Column(String(64), nullable=True)
    size_bytes = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    file_path = Column(Text, nullable=True)
    manifest = Column(JSONB, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
