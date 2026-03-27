"""Dynamic application configuration model."""
import enum

from sqlalchemy import Column, DateTime, Enum, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base


class ValueType(str, enum.Enum):
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BOOL = "bool"
    JSON = "json"


class AppConfig(Base):
    __tablename__ = "app_config"

    key = Column(String(255), primary_key=True)
    value = Column(JSONB, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    label = Column(String(255), nullable=False, default="")
    description = Column(Text, nullable=True)
    value_type = Column(Enum(ValueType, values_callable=lambda e: [x.value for x in e]), nullable=False, default=ValueType.STRING)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
