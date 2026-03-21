"""Tests for ANALYTICS.1-5 admin analytics endpoints."""
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Domain, Skill, Subject
from app.models.profile import Profile
from app.models.session import ExerciseSession, SessionMode, SessionStatus
from app.models.social import Challenge, ChallengeStatus
from app.models.subscription import (
    Payment,
    PaymentProvider,
    PaymentStatus,
    Plan,
    PlanTier,
    Subscription,
    SubscriptionStatus,
)
from app.models.user import User, UserRole
from tests.conftest import auth_header


# ── Helpers ────────────────────────────────────────────────


async def _create_session(
    db: AsyncSession,
    profile_id: uuid.UUID,
    created_at: datetime | None = None,
) -> ExerciseSession:
    s = ExerciseSession(
        id=uuid.uuid4(),
        profile_id=profile_id,
        mode=SessionMode.PRACTICE,
        status=SessionStatus.COMPLETED,
        total_questions=5,
        correct_answers=3,
        score=60.0,
    )
    db.add(s)
    await db.flush()
    if created_at:
        # Update created_at after flush (BaseMixin sets default)
        s.created_at = created_at
        await db.flush()
    return s


# ── ANALYTICS.1: Engagement ───────────────────────────────


@pytest.mark.asyncio
async def test_engagement_endpoint(
    client: AsyncClient,
    db_session: AsyncSession,
    test_admin: User,
    test_student: User,
    test_student_profile: Profile,
):
    # Create a session for today
    await _create_session(db_session, test_student_profile.id)
    await db_session.commit()

    resp = await client.get(
        "/api/v1/admin/analytics/engagement",
        headers=auth_header(test_admin),
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["dau"] >= 1
    assert data["wau"] >= 1
    assert data["mau"] >= 1
    assert "stickiness" in data
    assert "time_series" in data
    assert len(data["time_series"]) == 30


@pytest.mark.asyncio
async def test_engagement_requires_admin(
    client: AsyncClient,
    test_student: User,
):
    resp = await client.get(
        "/api/v1/admin/analytics/engagement",
        headers=auth_header(test_student),
    )
    assert resp.status_code in (401, 403)


# ── ANALYTICS.2: Retention ────────────────────────────────


@pytest.mark.asyncio
async def test_retention_endpoint(
    client: AsyncClient,
    db_session: AsyncSession,
    test_admin: User,
    test_student: User,
    test_student_profile: Profile,
):
    # Create profile "created 2 weeks ago" and a session on day+1
    now = datetime.now(timezone.utc)
    two_weeks_ago = now - timedelta(days=14)
    test_student_profile.created_at = two_weeks_ago
    await db_session.flush()

    await _create_session(
        db_session, test_student_profile.id, created_at=two_weeks_ago + timedelta(days=1)
    )
    await db_session.commit()

    resp = await client.get(
        "/api/v1/admin/analytics/retention",
        headers=auth_header(test_admin),
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert isinstance(data, list)
    assert len(data) == 8
    # Each cohort has expected keys
    for cohort in data:
        assert "cohort_week" in cohort
        assert "cohort_size" in cohort
        assert "d1" in cohort


# ── ANALYTICS.3: Conversion Funnel ───────────────────────


@pytest.mark.asyncio
async def test_conversion_endpoint(
    client: AsyncClient,
    db_session: AsyncSession,
    test_admin: User,
    test_student: User,
    test_student_profile: Profile,
):
    # Create a session so conversion counts something
    await _create_session(db_session, test_student_profile.id)
    await db_session.commit()

    resp = await client.get(
        "/api/v1/admin/analytics/conversion",
        headers=auth_header(test_admin),
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "stages" in data
    stages = data["stages"]
    assert len(stages) == 6
    # First stage should have a 100% conversion rate
    assert stages[0]["conversion_rate"] == 100.0
    # Total users should be at least 2 (admin + student)
    assert stages[0]["count"] >= 2


# ── ANALYTICS.4: Virality ────────────────────────────────


@pytest.mark.asyncio
async def test_virality_endpoint(
    client: AsyncClient,
    db_session: AsyncSession,
    test_admin: User,
    test_student: User,
    test_student_profile: Profile,
):
    resp = await client.get(
        "/api/v1/admin/analytics/virality",
        headers=auth_header(test_admin),
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "k_factor" in data
    assert "challenges_this_month" in data
    assert "invitations_per_user" in data
    assert "new_users_this_month" in data


@pytest.mark.asyncio
async def test_virality_with_challenges(
    client: AsyncClient,
    db_session: AsyncSession,
    test_admin: User,
    test_student: User,
    test_student_profile: Profile,
    test_parent: User,
    test_parent_profiles: list[Profile],
):
    now = datetime.now(timezone.utc)
    # Create a session for the student (needed for MAU)
    await _create_session(db_session, test_student_profile.id)

    # Create a challenge
    challenge = Challenge(
        id=uuid.uuid4(),
        challenger_id=test_student_profile.id,
        challenged_id=test_parent_profiles[0].id,
        status=ChallengeStatus.PENDING,
        expires_at=now + timedelta(days=7),
    )
    db_session.add(challenge)
    await db_session.commit()

    resp = await client.get(
        "/api/v1/admin/analytics/virality",
        headers=auth_header(test_admin),
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total_challenges"] >= 1
    assert data["challenges_this_month"] >= 1
    assert data["active_challengers"] >= 1
