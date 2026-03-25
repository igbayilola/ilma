"""Push subscription storage for Web Push / FCM."""
from sqlalchemy import Column, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseMixin


class PushSubscription(Base, BaseMixin):
    __tablename__ = "push_subscriptions"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    endpoint = Column(Text, nullable=False, unique=True, index=True)
    keys_json = Column(JSONB, nullable=False)

    user = relationship("User")
