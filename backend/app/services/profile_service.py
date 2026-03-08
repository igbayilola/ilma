"""Profile service: Netflix-style child profiles within a parent account."""
from uuid import UUID

from passlib.context import CryptContext
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException, NotFoundException
from app.models.profile import Profile
from app.models.subscription import PlanTier, Subscription, SubscriptionStatus
from app.models.user import User, UserRole

pin_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MAX_PROFILES_PER_ACCOUNT = 5


class ProfileService:
    # ── List profiles for a user ──────────────────────────────
    async def list_profiles(self, db: AsyncSession, user: User) -> list[dict]:
        result = await db.execute(
            select(Profile)
            .where(Profile.user_id == user.id, Profile.is_active.is_(True))
            .order_by(Profile.created_at)
        )
        profiles = result.scalars().all()
        out = []
        for p in profiles:
            tier = await self._get_profile_tier(db, p)
            out.append(self._to_dict(p, tier))
        return out

    # ── Create a child profile ────────────────────────────────
    async def create_profile(
        self, db: AsyncSession, user: User, display_name: str,
        avatar_url: str | None = None, pin: str | None = None,
        grade_level_id: UUID | None = None,
    ) -> Profile:
        # Check max profiles
        count_result = await db.execute(
            select(func.count(Profile.id)).where(
                Profile.user_id == user.id, Profile.is_active.is_(True)
            )
        )
        count = count_result.scalar() or 0
        if count >= MAX_PROFILES_PER_ACCOUNT:
            raise AppException(
                status_code=400, code="MAX_PROFILES",
                message=f"Maximum {MAX_PROFILES_PER_ACCOUNT} profils par compte.",
            )

        profile = Profile(
            user_id=user.id,
            display_name=display_name,
            avatar_url=avatar_url,
            pin_hash=pin_context.hash(pin) if pin else None,
            grade_level_id=grade_level_id,
        )
        db.add(profile)
        await db.flush()
        return profile

    # ── Update a profile ──────────────────────────────────────
    async def update_profile(
        self, db: AsyncSession, profile: Profile,
        display_name: str | None = None, avatar_url: str | None = None,
        pin: str | None = None, grade_level_id: UUID | None = None,
    ) -> Profile:
        if display_name is not None:
            profile.display_name = display_name
        if avatar_url is not None:
            profile.avatar_url = avatar_url
        if pin is not None:
            profile.pin_hash = pin_context.hash(pin)
        if grade_level_id is not None:
            profile.grade_level_id = grade_level_id
        db.add(profile)
        await db.flush()
        return profile

    # ── Soft-delete a profile ─────────────────────────────────
    async def delete_profile(self, db: AsyncSession, profile: Profile) -> None:
        profile.is_active = False
        db.add(profile)
        await db.flush()

    # ── Verify PIN ────────────────────────────────────────────
    async def verify_pin(self, db: AsyncSession, profile: Profile, pin: str) -> bool:
        if not profile.pin_hash:
            return True  # No PIN set → always passes
        return pin_context.verify(pin, profile.pin_hash)

    # ── Auto-create self-profile for standalone students ──────
    async def create_self_profile(self, db: AsyncSession, user: User) -> Profile:
        """Auto-create a single profile for a standalone student at registration."""
        profile = Profile(
            user_id=user.id,
            display_name=user.full_name or "Mon profil",
            avatar_url=user.avatar_url,
            grade_level_id=user.grade_level_id,
        )
        db.add(profile)
        await db.flush()
        return profile

    # ── Set weekly goal ───────────────────────────────────────
    async def set_weekly_goal(
        self, db: AsyncSession, profile: Profile, goal_minutes: int
    ) -> None:
        profile.weekly_goal_minutes = goal_minutes
        db.add(profile)
        await db.flush()

    # ── Get profile by ID with ownership check ────────────────
    async def get_profile(self, db: AsyncSession, user: User, profile_id: UUID) -> Profile:
        result = await db.execute(
            select(Profile).where(
                Profile.id == profile_id,
                Profile.user_id == user.id,
            )
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise NotFoundException("Profil", str(profile_id))
        return profile

    # ── Helpers ───────────────────────────────────────────────
    async def _get_profile_tier(self, db: AsyncSession, profile: Profile) -> str:
        result = await db.execute(
            select(Subscription).where(
                Subscription.profile_id == profile.id,
                Subscription.status == SubscriptionStatus.ACTIVE,
            ).order_by(Subscription.created_at.desc())
        )
        sub = result.scalar_one_or_none()
        if sub and sub.plan:
            return sub.plan.tier.value if hasattr(sub.plan, "tier") else "free"
        return "free"

    def _to_dict(self, profile: Profile, tier: str = "free") -> dict:
        return {
            "id": str(profile.id),
            "display_name": profile.display_name,
            "avatar_url": profile.avatar_url or f"https://api.dicebear.com/7.x/avataaars/svg?seed={profile.id}",
            "grade_level_id": str(profile.grade_level_id) if profile.grade_level_id else None,
            "is_active": profile.is_active,
            "has_pin": profile.pin_hash is not None,
            "subscription_tier": tier,
            "weekly_goal_minutes": profile.weekly_goal_minutes,
        }


profile_service = ProfileService()
