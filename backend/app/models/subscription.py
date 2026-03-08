"""Subscription plans and payments."""
import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.base import BaseMixin


class PlanTier(str, enum.Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    TRIAL = "trial"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentProvider(str, enum.Enum):
    KKIAPAY = "kkiapay"
    FEDAPAY = "fedapay"
    MOCK = "mock"


class Plan(Base, BaseMixin):
    __tablename__ = "plans"

    name = Column(String(100), nullable=False)
    tier = Column(Enum(PlanTier), nullable=False, unique=True)
    price_xof = Column(Integer, default=0, nullable=False)
    duration_days = Column(Integer, default=30, nullable=False)
    description = Column(Text, nullable=True)
    features = Column(JSONB, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)


class Subscription(Base, BaseMixin):
    __tablename__ = "subscriptions"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=True, index=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id", ondelete="SET NULL"), nullable=True)
    status = Column(Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.TRIAL)
    starts_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    auto_renew = Column(Boolean, default=False, nullable=False)

    profile = relationship("Profile", back_populates="subscription")
    plan = relationship("Plan")
    payments = relationship("Payment", back_populates="subscription", lazy="selectin")


class Payment(Base, BaseMixin):
    __tablename__ = "payments"

    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True, index=True)
    provider = Column(Enum(PaymentProvider), nullable=False, default=PaymentProvider.MOCK)
    provider_tx_id = Column(String(255), nullable=True, index=True)
    amount_xof = Column(Integer, nullable=False)
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    metadata_ = Column("metadata", JSONB, nullable=True)

    subscription = relationship("Subscription", back_populates="payments")
