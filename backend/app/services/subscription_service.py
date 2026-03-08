"""Subscription + payment service with freemium gating — per-profile subscriptions."""
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.profile import Profile
from app.models.subscription import (
    Payment,
    PaymentProvider,
    PaymentStatus,
    Plan,
    PlanTier,
    Subscription,
    SubscriptionStatus,
)
from app.models.user import User
from app.services.payment_providers import get_payment_provider


class SubscriptionService:
    async def list_plans(self, db: AsyncSession) -> list[Plan]:
        result = await db.execute(
            select(Plan).where(Plan.is_active.is_(True)).order_by(Plan.price_xof)
        )
        return list(result.scalars().all())

    async def get_profile_subscription(self, db: AsyncSession, profile: Profile) -> Subscription | None:
        """Get the active subscription for a specific profile."""
        result = await db.execute(
            select(Subscription).where(
                Subscription.profile_id == profile.id
            ).order_by(Subscription.created_at.desc())
        )
        return result.scalar_one_or_none()

    async def get_user_subscriptions(self, db: AsyncSession, user: User) -> list[dict]:
        """Get all subscriptions for all profiles of a user."""
        result = await db.execute(
            select(Subscription, Profile)
            .join(Profile, Subscription.profile_id == Profile.id)
            .where(Profile.user_id == user.id)
            .order_by(Subscription.created_at.desc())
        )
        return [
            {
                "subscription_id": str(sub.id),
                "profile_id": str(profile.id),
                "profile_name": profile.display_name,
                "status": sub.status.value,
                "plan_id": str(sub.plan_id) if sub.plan_id else None,
                "starts_at": sub.starts_at.isoformat() if sub.starts_at else None,
                "expires_at": sub.expires_at.isoformat() if sub.expires_at else None,
            }
            for sub, profile in result.all()
        ]

    async def get_active_tier(self, db: AsyncSession, profile: Profile) -> PlanTier:
        """Return the profile's current active tier (for gating logic)."""
        sub = await self.get_profile_subscription(db, profile)
        if not sub or sub.status != SubscriptionStatus.ACTIVE:
            return PlanTier.FREE
        if sub.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            # Expired → downgrade
            sub.status = SubscriptionStatus.EXPIRED
            db.add(sub)
            await db.flush()
            return PlanTier.FREE
        if sub.plan_id:
            plan_result = await db.execute(select(Plan).where(Plan.id == sub.plan_id))
            plan = plan_result.scalar_one_or_none()
            if plan:
                return plan.tier
        return PlanTier.FREE

    async def init_payment(
        self,
        db: AsyncSession,
        user: User,
        profile: Profile,
        plan_id: uuid.UUID,
        provider: PaymentProvider,
    ) -> Payment:
        plan_result = await db.execute(select(Plan).where(Plan.id == plan_id))
        plan = plan_result.scalar_one_or_none()
        if not plan:
            raise NotFoundException("Plan", str(plan_id))

        # Create pending payment
        payment = Payment(
            user_id=user.id,
            profile_id=profile.id,
            provider=provider,
            amount_xof=plan.price_xof,
            status=PaymentStatus.PENDING,
        )
        db.add(payment)
        await db.flush()

        # Initialize via payment provider adapter
        adapter = get_payment_provider(provider.value)
        result = await adapter.create_transaction(
            amount=plan.price_xof,
            description=f"ILMA - {plan.name}",
            callback_url=f"/api/v1/payments/webhook/{provider.value}",
        )
        payment.provider_tx_id = result.get("transaction_id")

        if result.get("status") == "completed":
            payment.status = PaymentStatus.COMPLETED
            await self._activate_subscription(db, profile, plan, payment)

        await db.flush()
        return payment

    async def handle_webhook(
        self,
        db: AsyncSession,
        provider: str,
        payload: dict,
    ) -> bool:
        """Process payment webhook from KKiaPay/FedaPay."""
        tx_id = payload.get("transaction_id") or payload.get("id")
        status = payload.get("status", "").lower()

        if not tx_id:
            return False

        result = await db.execute(
            select(Payment).where(Payment.provider_tx_id == tx_id)
        )
        payment = result.scalar_one_or_none()
        if not payment:
            return False

        if status in ("success", "completed", "approved"):
            payment.status = PaymentStatus.COMPLETED
            # Activate subscription for the profile
            if payment.profile_id:
                profile_result = await db.execute(select(Profile).where(Profile.id == payment.profile_id))
                profile = profile_result.scalar_one_or_none()
                plan_result = await db.execute(
                    select(Plan).where(Plan.price_xof == payment.amount_xof, Plan.is_active.is_(True))
                )
                plan = plan_result.scalar_one_or_none()
                if profile and plan:
                    await self._activate_subscription(db, profile, plan, payment)
        elif status in ("failed", "declined"):
            payment.status = PaymentStatus.FAILED

        await db.flush()
        return True

    async def _activate_subscription(
        self,
        db: AsyncSession,
        profile: Profile,
        plan: Plan,
        payment: Payment,
    ) -> Subscription:
        now = datetime.now(timezone.utc)
        # Extend existing or create new
        existing = await self.get_profile_subscription(db, profile)
        if existing and existing.status == SubscriptionStatus.ACTIVE and existing.expires_at.replace(tzinfo=timezone.utc) > now:
            existing.expires_at = existing.expires_at.replace(tzinfo=timezone.utc) + timedelta(days=plan.duration_days)
            existing.plan_id = plan.id
            payment.subscription_id = existing.id
            return existing

        sub = Subscription(
            user_id=profile.user_id,
            profile_id=profile.id,
            plan_id=plan.id,
            status=SubscriptionStatus.ACTIVE,
            starts_at=now,
            expires_at=now + timedelta(days=plan.duration_days),
        )
        db.add(sub)
        await db.flush()
        payment.subscription_id = sub.id
        return sub


subscription_service = SubscriptionService()
