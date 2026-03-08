"""Subscription + payment endpoints — per-profile subscriptions."""
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_active_profile, get_current_user
from app.db.session import get_db_session
from app.models.profile import Profile
from app.models.user import User
from app.schemas.response import ok
from app.schemas.subscription import PaymentInitRequest, PaymentOut, PlanOut, SubscriptionOut
from app.services.subscription_service import subscription_service

router = APIRouter(tags=["Subscriptions"])


@router.get("/subscriptions/plans")
async def list_plans(
    db: AsyncSession = Depends(get_db_session),
):
    plans = await subscription_service.list_plans(db)
    return ok(data=[PlanOut.model_validate(p) for p in plans])


@router.get("/me/subscription")
async def my_subscription(
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    """Get subscription for the active profile."""
    sub = await subscription_service.get_profile_subscription(db, profile)
    if not sub:
        return ok(data=None, message="Aucun abonnement actif")
    return ok(data=SubscriptionOut.model_validate(sub))


@router.get("/me/subscriptions")
async def my_subscriptions(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get all subscriptions across all profiles of the account."""
    subs = await subscription_service.get_user_subscriptions(db, current_user)
    return ok(data=subs)


@router.post("/payments/init")
async def init_payment(
    body: PaymentInitRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    # Resolve profile: use profile_id from body, or fall back to active profile
    if body.profile_id:
        result = await db.execute(
            select(Profile).where(
                Profile.id == body.profile_id,
                Profile.user_id == current_user.id,
                Profile.is_active.is_(True),
            )
        )
        profile = result.scalar_one_or_none()
        if not profile:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Profil introuvable.")
    else:
        # Fall back to auto-select single profile
        from sqlalchemy import select as sa_select
        from app.models.profile import Profile as ProfileModel
        result = await db.execute(
            sa_select(ProfileModel).where(
                ProfileModel.user_id == current_user.id,
                ProfileModel.is_active.is_(True),
            )
        )
        auto_profiles = list(result.scalars().all())
        if len(auto_profiles) == 1:
            profile = auto_profiles[0]
        elif len(auto_profiles) == 0:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Aucun profil actif.")
        else:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Veuillez spécifier profile_id.")

    payment = await subscription_service.init_payment(
        db, current_user, profile, body.plan_id, body.provider
    )
    await db.commit()
    return ok(data=PaymentOut.model_validate(payment))


@router.post("/payments/webhook/{provider}")
async def payment_webhook(
    provider: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
):
    payload = await request.json()
    success = await subscription_service.handle_webhook(db, provider, payload)
    await db.commit()
    return ok(data={"processed": success})
