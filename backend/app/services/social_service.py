"""Social features service: leaderboard + challenges."""
import logging
import random
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.social import Challenge, ChallengeStatus, WeeklyLeaderboard

logger = logging.getLogger(__name__)

# ── Pseudonym generator (~500+ unique combinations) ──────────

_ADJECTIVES = [
    "Agile", "Brave", "Calme", "Doré", "Étoilé", "Fort", "Grand", "Habile",
    "Intrépide", "Joyeux", "Loyal", "Malin", "Noble", "Poli", "Rapide",
    "Sage", "Tenace", "Vif", "Astucieux", "Brillant", "Curieux", "Doux",
    "Fier", "Gentil", "Hardi", "Léger", "Rusé", "Souple", "Vaillant", "Zélé",
]

_ANIMALS = [
    "Caméléon", "Éléphant", "Lion", "Perroquet", "Gazelle", "Hibou", "Tortue",
    "Aigle", "Panthère", "Dauphin", "Faucon", "Léopard", "Phénix", "Cobra",
    "Colibri", "Zèbre", "Guépard", "Pélican", "Cigogne", "Bison",
]


def generate_pseudonym() -> str:
    """Generate a random pseudonym like 'Brave Caméléon'."""
    return f"{random.choice(_ADJECTIVES)} {random.choice(_ANIMALS)}"


def current_week_iso() -> str:
    """Return current ISO week string like '2026-W11'."""
    now = datetime.now(timezone.utc)
    return f"{now.isocalendar()[0]}-W{now.isocalendar()[1]:02d}"


class SocialService:
    # ── Leaderboard ──────────────────────────────────────────

    async def increment_xp(
        self, db: AsyncSession, profile_id: UUID, xp: int
    ) -> None:
        """Add XP to the current week's leaderboard entry (create if needed)."""
        week = current_week_iso()
        result = await db.execute(
            select(WeeklyLeaderboard).where(
                WeeklyLeaderboard.profile_id == profile_id,
                WeeklyLeaderboard.week_iso == week,
            )
        )
        entry = result.scalar_one_or_none()
        if entry:
            entry.xp_earned += xp
        else:
            entry = WeeklyLeaderboard(
                profile_id=profile_id,
                week_iso=week,
                xp_earned=xp,
                pseudonym=generate_pseudonym(),
            )
            db.add(entry)
        await db.flush()

    async def get_weekly_leaderboard(
        self, db: AsyncSession, profile_id: UUID, limit: int = 20,
        classroom_id: UUID | None = None,
    ) -> dict:
        """Get current week's top N + the user's own position.
        If classroom_id is provided, scope to that classroom only."""
        week = current_week_iso()

        # Base filter: week + optional classroom scope
        base_filter = [WeeklyLeaderboard.week_iso == week]
        if classroom_id:
            from app.models.classroom import ClassroomStudent
            classroom_profile_ids = (
                select(ClassroomStudent.profile_id)
                .where(ClassroomStudent.classroom_id == classroom_id)
            )
            base_filter.append(WeeklyLeaderboard.profile_id.in_(classroom_profile_ids))

        # Top N
        top_result = await db.execute(
            select(WeeklyLeaderboard)
            .where(*base_filter)
            .order_by(WeeklyLeaderboard.xp_earned.desc())
            .limit(limit)
        )
        top = top_result.scalars().all()

        # User's position
        user_entry = None
        user_rank = None

        rank_subq = (
            select(
                WeeklyLeaderboard.profile_id,
                func.row_number()
                .over(order_by=WeeklyLeaderboard.xp_earned.desc())
                .label("rank"),
            )
            .where(*base_filter)
            .subquery()
        )
        user_rank_result = await db.execute(
            select(rank_subq.c.rank).where(rank_subq.c.profile_id == profile_id)
        )
        rank_row = user_rank_result.scalar_one_or_none()
        if rank_row:
            user_rank = rank_row

        user_entry_result = await db.execute(
            select(WeeklyLeaderboard).where(
                WeeklyLeaderboard.profile_id == profile_id,
                WeeklyLeaderboard.week_iso == week,
            )
        )
        user_entry = user_entry_result.scalar_one_or_none()

        return {
            "week": week,
            "scope": "classroom" if classroom_id else "global",
            "entries": [
                {
                    "rank": i + 1,
                    "pseudonym": e.pseudonym,
                    "xp_earned": e.xp_earned,
                    "is_me": e.profile_id == profile_id,
                }
                for i, e in enumerate(top)
            ],
            "my_rank": user_rank,
            "my_xp": user_entry.xp_earned if user_entry else 0,
            "my_pseudonym": user_entry.pseudonym if user_entry else None,
        }

    async def get_leaderboard_history(
        self, db: AsyncSession, profile_id: UUID, weeks: int = 4
    ) -> list[dict]:
        """Get past weeks' leaderboard summaries for the user."""
        current = current_week_iso()

        # Get all user entries ordered by week
        result = await db.execute(
            select(WeeklyLeaderboard)
            .where(WeeklyLeaderboard.profile_id == profile_id)
            .order_by(WeeklyLeaderboard.week_iso.desc())
            .limit(weeks)
        )
        entries = result.scalars().all()

        history = []
        for entry in entries:
            # Get user's rank for that week
            rank_subq = (
                select(
                    WeeklyLeaderboard.profile_id,
                    func.row_number()
                    .over(order_by=WeeklyLeaderboard.xp_earned.desc())
                    .label("rank"),
                )
                .where(WeeklyLeaderboard.week_iso == entry.week_iso)
                .subquery()
            )
            rank_result = await db.execute(
                select(rank_subq.c.rank).where(rank_subq.c.profile_id == profile_id)
            )
            rank = rank_result.scalar_one_or_none()

            # Count total participants
            count_result = await db.execute(
                select(func.count(WeeklyLeaderboard.id)).where(
                    WeeklyLeaderboard.week_iso == entry.week_iso
                )
            )
            total = count_result.scalar() or 0

            history.append({
                "week": entry.week_iso,
                "xp_earned": entry.xp_earned,
                "pseudonym": entry.pseudonym,
                "rank": rank,
                "total_participants": total,
                "is_current": entry.week_iso == current,
            })

        return history

    async def archive_week(self, db: AsyncSession) -> int:
        """Archive: no-op for now (data stays, new week starts fresh)."""
        return 0

    # ── Challenges ───────────────────────────────────────────

    async def create_challenge(
        self,
        db: AsyncSession,
        challenger_id: UUID,
        challenged_id: UUID,
        skill_id: UUID | None = None,
    ) -> Challenge:
        """Create a new challenge (expires in 24h)."""
        # Rate limit: max 5 per day
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        count_result = await db.execute(
            select(func.count(Challenge.id)).where(
                Challenge.challenger_id == challenger_id,
                Challenge.created_at >= today_start,
            )
        )
        if (count_result.scalar() or 0) >= 5:
            raise ValueError("Maximum 5 défis par jour")

        challenge = Challenge(
            challenger_id=challenger_id,
            challenged_id=challenged_id,
            skill_id=skill_id,
            status=ChallengeStatus.PENDING,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
        )
        db.add(challenge)
        await db.flush()

        # Notify challenged user
        await self._notify_challenge(db, challenge, "new")

        return challenge

    async def accept_challenge(self, db: AsyncSession, challenge_id: UUID, profile_id: UUID) -> Challenge:
        result = await db.execute(
            select(Challenge).where(
                Challenge.id == challenge_id,
                Challenge.challenged_id == profile_id,
                Challenge.status == ChallengeStatus.PENDING,
            )
        )
        challenge = result.scalar_one_or_none()
        if not challenge:
            raise ValueError("Défi introuvable ou déjà accepté")
        if challenge.expires_at < datetime.now(timezone.utc):
            challenge.status = ChallengeStatus.EXPIRED
            await db.flush()
            raise ValueError("Ce défi a expiré")
        challenge.status = ChallengeStatus.ACCEPTED
        await db.flush()
        return challenge

    async def complete_challenge(
        self, db: AsyncSession, challenge_id: UUID, profile_id: UUID, score: float
    ) -> Challenge:
        result = await db.execute(
            select(Challenge).where(
                Challenge.id == challenge_id,
                Challenge.status == ChallengeStatus.ACCEPTED,
            )
        )
        challenge = result.scalar_one_or_none()
        if not challenge:
            raise ValueError("Défi introuvable ou pas encore accepté")

        if profile_id == challenge.challenger_id:
            challenge.challenger_score = score
        elif profile_id == challenge.challenged_id:
            challenge.challenged_score = score
        else:
            raise ValueError("Vous ne participez pas à ce défi")

        # Mark completed when both scores are in
        if challenge.challenger_score is not None and challenge.challenged_score is not None:
            challenge.status = ChallengeStatus.COMPLETED
            await self._notify_challenge(db, challenge, "completed")

        await db.flush()
        return challenge

    async def decline_challenge(self, db: AsyncSession, challenge_id: UUID, profile_id: UUID) -> Challenge:
        """Decline a pending challenge."""
        result = await db.execute(
            select(Challenge).where(
                Challenge.id == challenge_id,
                Challenge.challenged_id == profile_id,
                Challenge.status == ChallengeStatus.PENDING,
            )
        )
        challenge = result.scalar_one_or_none()
        if not challenge:
            raise ValueError("Défi introuvable ou déjà traité")
        challenge.status = ChallengeStatus.DECLINED
        await db.flush()
        return challenge

    async def expire_old_challenges(self, db: AsyncSession) -> int:
        """Expire pending challenges past their deadline."""
        now = datetime.now(timezone.utc)
        result = await db.execute(
            update(Challenge)
            .where(
                Challenge.status == ChallengeStatus.PENDING,
                Challenge.expires_at < now,
            )
            .values(status=ChallengeStatus.EXPIRED)
        )
        return result.rowcount

    async def get_my_challenges(
        self, db: AsyncSession, profile_id: UUID, status: str | None = None
    ) -> list[dict]:
        """Get challenges for a profile (sent + received)."""
        query = select(Challenge).where(
            (Challenge.challenger_id == profile_id) | (Challenge.challenged_id == profile_id)
        )
        if status:
            query = query.where(Challenge.status == ChallengeStatus(status))
        query = query.order_by(Challenge.created_at.desc()).limit(50)

        result = await db.execute(query)
        challenges = result.scalars().all()
        return [
            {
                "id": str(c.id),
                "challenger_id": str(c.challenger_id),
                "challenged_id": str(c.challenged_id),
                "skill_id": str(c.skill_id) if c.skill_id else None,
                "status": c.status.value,
                "challenger_score": c.challenger_score,
                "challenged_score": c.challenged_score,
                "expires_at": c.expires_at.isoformat() if c.expires_at else None,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "is_challenger": c.challenger_id == profile_id,
            }
            for c in challenges
        ]


    async def _notify_challenge(self, db: AsyncSession, challenge: Challenge, event: str) -> None:
        """Send notification for challenge events."""
        try:
            from app.models.notification import NotificationType
            from app.models.profile import Profile
            from app.services.notification_service import notification_service

            if event == "new":
                # Notify the challenged user
                profile_result = await db.execute(
                    select(Profile).where(Profile.id == challenge.challenged_id)
                )
                profile = profile_result.scalar_one_or_none()
                if profile:
                    await notification_service.create(
                        db=db,
                        user_id=profile.user_id,
                        type=NotificationType.SYSTEM,
                        title="⚔️ Nouveau défi reçu !",
                        body="Un ami te défie ! Accepte le défi et montre ce que tu sais faire.",
                        data={"challenge_id": str(challenge.id)},
                    )
            elif event == "completed":
                # Notify both players
                for pid in [challenge.challenger_id, challenge.challenged_id]:
                    profile_result = await db.execute(
                        select(Profile).where(Profile.id == pid)
                    )
                    profile = profile_result.scalar_one_or_none()
                    if profile:
                        is_winner = (
                            (pid == challenge.challenger_id and (challenge.challenger_score or 0) >= (challenge.challenged_score or 0))
                            or (pid == challenge.challenged_id and (challenge.challenged_score or 0) >= (challenge.challenger_score or 0))
                        )
                        title = "🏆 Défi terminé — Victoire !" if is_winner else "⚔️ Défi terminé"
                        body = f"Score : {challenge.challenger_score:.0f} vs {challenge.challenged_score:.0f}"
                        await notification_service.create(
                            db=db,
                            user_id=profile.user_id,
                            type=NotificationType.SYSTEM,
                            title=title,
                            body=body,
                            data={"challenge_id": str(challenge.id)},
                        )
        except Exception:
            logger.warning("Failed to send challenge notification", exc_info=True)


social_service = SocialService()
