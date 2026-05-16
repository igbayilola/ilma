"""Risk detection — unified score across inactivity + SmartScore signals.

Used by:
- `tasks/notification_tasks._send_parent_inactivity_alerts` to decide which
  parents receive an SMS (with its own throttling on top).
- `api/v1/endpoints/admin.GET /admin/students/at-risk` to surface the same
  cohort to admins, regardless of whether a parent SMS was sent.

The classification formula lives in `classify_risk` so both consumers stay
in sync — diverging here would silently mean admins and parents see
different at-risk lists.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.content import GradeLevel
from app.models.profile import Profile
from app.models.progress import Progress
from app.models.session import ExerciseSession, SessionStatus
from app.models.user import User, UserRole

RiskLevel = Literal["low", "medium", "high"]

_RANK: dict[RiskLevel, int] = {"low": 0, "medium": 1, "high": 2}

# Neutral score when the kid has no Progress rows yet — avoids flagging a
# brand-new profile as low-scoring before they've attempted anything.
_NEUTRAL_AVG_SCORE = 50.0


def _as_utc_aware(dt: datetime) -> datetime:
    """SQLite (tests) drops tzinfo and any pre-tz legacy row would too —
    coerce to UTC-aware so subtraction with `now(utc)` never raises."""
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


def classify_risk(days_inactive: int, avg_score: float) -> RiskLevel:
    """Pure classifier — identical formula used by cron and admin endpoint."""
    if days_inactive >= 7 or avg_score < 30:
        return "high"
    if days_inactive >= 3 or avg_score < 40:
        return "medium"
    return "low"


def suggested_action(level: RiskLevel, days_inactive: int, avg_score: float) -> str:
    """Human-readable hint for the admin row. Empty for `low`."""
    if level == "high":
        if days_inactive >= 7:
            return "Appeler le parent — décrochage probable"
        return "Appeler le parent — score < 30 %"
    if level == "medium":
        if days_inactive >= 3:
            return "Relance SMS parent : session 10 min"
        return "Proposer micro-leçon de remédiation"
    return ""


@dataclass(frozen=True, slots=True)
class RiskSignals:
    days_inactive: int
    avg_score: float
    risk_level: RiskLevel
    action: str


@dataclass(frozen=True, slots=True)
class AtRiskRow:
    profile_id: UUID
    display_name: str
    grade_level: str | None
    parent_user_id: UUID | None
    parent_phone: str | None
    last_completed_at: datetime | None
    signals: RiskSignals


async def compute_for_profile(db: AsyncSession, profile: Profile) -> RiskSignals:
    """Compute the risk signals for a single profile (2 aggregate queries).

    No filter on recency — callers decide whether to act on `low`. The cron
    short-circuits on `low` to avoid SMS-spamming parents of active kids.
    """
    now = datetime.now(timezone.utc)
    last_completed = (
        await db.execute(
            select(func.max(ExerciseSession.completed_at)).where(
                ExerciseSession.profile_id == profile.id,
                ExerciseSession.status == SessionStatus.COMPLETED,
            )
        )
    ).scalar()
    reference = last_completed if last_completed is not None else profile.created_at
    days_inactive = (now - _as_utc_aware(reference)).days

    avg_raw = (
        await db.execute(
            select(func.avg(Progress.smart_score)).where(
                Progress.profile_id == profile.id,
                Progress.total_attempts > 0,
            )
        )
    ).scalar()
    avg_score = float(avg_raw) if avg_raw is not None else _NEUTRAL_AVG_SCORE

    level = classify_risk(days_inactive, avg_score)
    return RiskSignals(
        days_inactive=days_inactive,
        avg_score=avg_score,
        risk_level=level,
        action=suggested_action(level, days_inactive, avg_score),
    )


async def list_at_risk(
    db: AsyncSession,
    min_level: RiskLevel = "medium",
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[AtRiskRow], int]:
    """Enumerate active profiles whose risk_level is >= `min_level`.

    Sorted by risk_level desc then days_inactive desc — admin sees the most
    urgent cases first. Pagination is post-filter; total reflects the
    filtered cohort, not all profiles.
    """
    threshold = _RANK[min_level]

    result = await db.execute(
        select(Profile)
        .where(Profile.is_active.is_(True))
        .options(selectinload(Profile.grade_level))
    )
    profiles = list(result.scalars().all())

    # Resolve parent (user) for each profile — single batched fetch.
    user_ids = {p.user_id for p in profiles}
    parents_by_id: dict[UUID, User] = {}
    if user_ids:
        parents = (
            await db.execute(
                select(User).where(
                    User.id.in_(user_ids), User.role == UserRole.PARENT
                )
            )
        ).scalars().all()
        parents_by_id = {u.id: u for u in parents}

    rows: list[AtRiskRow] = []
    for profile in profiles:
        signals = await compute_for_profile(db, profile)
        if _RANK[signals.risk_level] < threshold:
            continue

        last_completed = (
            await db.execute(
                select(func.max(ExerciseSession.completed_at)).where(
                    ExerciseSession.profile_id == profile.id,
                    ExerciseSession.status == SessionStatus.COMPLETED,
                )
            )
        ).scalar()
        parent = parents_by_id.get(profile.user_id)
        grade: GradeLevel | None = profile.grade_level
        rows.append(
            AtRiskRow(
                profile_id=profile.id,
                display_name=profile.display_name,
                grade_level=grade.name if grade else None,
                parent_user_id=parent.id if parent else None,
                parent_phone=parent.phone if parent else None,
                last_completed_at=last_completed,
                signals=signals,
            )
        )

    rows.sort(key=lambda r: (-_RANK[r.signals.risk_level], -r.signals.days_inactive))
    total = len(rows)
    return rows[skip : skip + limit], total
