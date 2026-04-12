"""Social endpoints: leaderboard + challenges."""
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_active_profile
from app.db.session import get_db_session
from app.models.profile import Profile
from app.schemas.response import ok
from app.services.social_service import social_service

router = APIRouter(prefix="/social", tags=["Social"])


# ── Leaderboard ──────────────────────────────────────────────


@router.get("/leaderboard/weekly")
async def weekly_leaderboard(
    limit: int = Query(20, ge=1, le=100),
    classroom_id: UUID | None = Query(None, description="Scope to a specific classroom"),
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    data = await social_service.get_weekly_leaderboard(db, profile.id, limit, classroom_id=classroom_id)
    return ok(data=data)


@router.get("/leaderboard/weekly/history")
async def weekly_leaderboard_history(
    weeks: int = Query(4, ge=1, le=12),
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    data = await social_service.get_leaderboard_history(db, profile.id, weeks)
    return ok(data=data)


# ── Challenges ───────────────────────────────────────────────


class CreateChallengeRequest(BaseModel):
    challenged_id: UUID
    skill_id: UUID | None = None


class CompleteChallengeRequest(BaseModel):
    score: float


@router.post("/challenges")
async def create_challenge(
    body: CreateChallengeRequest,
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    challenge = await social_service.create_challenge(
        db, profile.id, body.challenged_id, body.skill_id
    )
    await db.commit()
    return ok(data={"id": str(challenge.id), "status": challenge.status.value})


@router.post("/challenges/{challenge_id}/accept")
async def accept_challenge(
    challenge_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    challenge = await social_service.accept_challenge(db, challenge_id, profile.id)
    await db.commit()
    return ok(data={"id": str(challenge.id), "status": challenge.status.value})


@router.post("/challenges/{challenge_id}/complete")
async def complete_challenge(
    challenge_id: UUID,
    body: CompleteChallengeRequest,
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    challenge = await social_service.complete_challenge(
        db, challenge_id, profile.id, body.score
    )
    await db.commit()
    return ok(data={
        "id": str(challenge.id),
        "status": challenge.status.value,
        "challenger_score": challenge.challenger_score,
        "challenged_score": challenge.challenged_score,
    })


@router.post("/challenges/{challenge_id}/decline")
async def decline_challenge(
    challenge_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    challenge = await social_service.decline_challenge(db, challenge_id, profile.id)
    await db.commit()
    return ok(data={"id": str(challenge.id), "status": challenge.status.value})


class ReportRequest(BaseModel):
    reported_profile_id: UUID | None = None
    reason: str  # insult | cheating | other
    description: str | None = None


@router.post("/reports", status_code=201)
async def submit_report(
    body: ReportRequest,
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    """Submit a content/behavior report."""
    from app.models.social import ContentReport, ReportReason
    report = ContentReport(
        reporter_id=profile.id,
        reported_profile_id=body.reported_profile_id,
        reason=ReportReason(body.reason),
        description=body.description,
    )
    db.add(report)
    await db.commit()
    return ok(data={"id": str(report.id), "status": "pending"})


@router.get("/challenges")
async def my_challenges(
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    challenges = await social_service.get_my_challenges(db, profile.id, status)
    return ok(data=challenges)
