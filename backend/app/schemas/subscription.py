"""Subscription & payment schemas."""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.subscription import PaymentProvider, PaymentStatus, PlanTier, SubscriptionStatus


class PlanOut(BaseModel):
    id: uuid.UUID
    name: str
    tier: PlanTier
    price_xof: int
    duration_days: int
    description: Optional[str]
    features: Optional[dict]
    model_config = ConfigDict(from_attributes=True)


class SubscriptionOut(BaseModel):
    id: uuid.UUID
    plan_id: Optional[uuid.UUID]
    status: SubscriptionStatus
    starts_at: datetime
    expires_at: datetime
    auto_renew: bool
    plan: Optional[PlanOut] = None
    model_config = ConfigDict(from_attributes=True)


class PaymentInitRequest(BaseModel):
    plan_id: uuid.UUID
    provider: PaymentProvider = PaymentProvider.MOCK
    profile_id: Optional[uuid.UUID] = None


class PaymentOut(BaseModel):
    id: uuid.UUID
    provider: PaymentProvider
    provider_tx_id: Optional[str]
    amount_xof: int
    status: PaymentStatus
    model_config = ConfigDict(from_attributes=True)
