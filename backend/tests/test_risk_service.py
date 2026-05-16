"""Tests for risk_service — at-risk classification + admin endpoint."""
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Domain, GradeLevel, Skill, Subject
from app.models.notification import Notification, NotificationChannel, NotificationType
from app.models.profile import Profile
from app.models.progress import Progress
from app.models.session import ExerciseSession, SessionMode, SessionStatus
from app.models.user import User, UserRole
from app.services.risk_service import (
    classify_risk,
    compute_for_profile,
    compute_funnel,
    list_at_risk,
    suggested_action,
)
from tests.conftest import auth_header


# ── Pure classifier ────────────────────────────────────────


def test_classify_risk_low_when_recent_and_good_score():
    assert classify_risk(days_inactive=0, avg_score=80.0) == "low"
    assert classify_risk(days_inactive=2, avg_score=50.0) == "low"


def test_classify_risk_medium_at_3_days_or_score_below_40():
    assert classify_risk(days_inactive=3, avg_score=80.0) == "medium"
    assert classify_risk(days_inactive=0, avg_score=35.0) == "medium"
    assert classify_risk(days_inactive=6, avg_score=39.9) == "medium"


def test_classify_risk_high_at_7_days_or_score_below_30():
    assert classify_risk(days_inactive=7, avg_score=80.0) == "high"
    assert classify_risk(days_inactive=0, avg_score=29.9) == "high"
    assert classify_risk(days_inactive=10, avg_score=20.0) == "high"


def test_suggested_action_is_empty_for_low():
    assert suggested_action("low", days_inactive=0, avg_score=80.0) == ""


def test_suggested_action_mentions_parent_for_high():
    label = suggested_action("high", days_inactive=10, avg_score=80.0)
    assert "parent" in label.lower()


# ── compute_for_profile ────────────────────────────────────


def _make_user(role: UserRole = UserRole.PARENT) -> User:
    return User(
        id=uuid.uuid4(),
        email=f"{uuid.uuid4().hex[:8]}@test.com",
        full_name="Parent Test",
        hashed_password="x",
        role=role,
        is_active=True,
    )


async def _make_skill(db: AsyncSession) -> Skill:
    grade = GradeLevel(id=uuid.uuid4(), name="CM2", slug=f"cm2-{uuid.uuid4().hex[:6]}", order=0, is_active=True)
    db.add(grade)
    await db.flush()
    subject = Subject(id=uuid.uuid4(), grade_level_id=grade.id, name="Maths", slug=f"maths-{uuid.uuid4().hex[:6]}", order=0, is_active=True)
    db.add(subject)
    await db.flush()
    domain = Domain(id=uuid.uuid4(), subject_id=subject.id, name="Nombres", slug=f"num-{uuid.uuid4().hex[:6]}", order=0, is_active=True)
    db.add(domain)
    await db.flush()
    skill = Skill(id=uuid.uuid4(), domain_id=domain.id, name="Add", slug=f"add-{uuid.uuid4().hex[:6]}")
    db.add(skill)
    await db.flush()
    return skill


@pytest.mark.asyncio
async def test_compute_for_profile_no_data_uses_neutral_score_and_created_at(
    db_session: AsyncSession,
):
    """A brand-new profile (no sessions, no progress) older than 7 days is `high`
    purely on inactivity — but avg_score must default to 50, not 0."""
    user = _make_user()
    db_session.add(user)
    await db_session.flush()
    profile = Profile(
        id=uuid.uuid4(),
        user_id=user.id,
        display_name="Aïcha",
        is_active=True,
        created_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=8),
    )
    db_session.add(profile)
    await db_session.flush()

    signals = await compute_for_profile(db_session, profile)
    assert signals.days_inactive == 8
    assert signals.avg_score == 50.0  # neutral, not 0
    assert signals.risk_level == "high"  # 8 ≥ 7


@pytest.mark.asyncio
async def test_compute_for_profile_active_with_good_score_is_low(
    db_session: AsyncSession,
):
    user = _make_user()
    db_session.add(user)
    await db_session.flush()
    profile = Profile(id=uuid.uuid4(), user_id=user.id, display_name="K", is_active=True)
    db_session.add(profile)
    await db_session.flush()

    skill = await _make_skill(db_session)
    db_session.add(Progress(
        id=uuid.uuid4(), profile_id=profile.id, skill_id=skill.id,
        smart_score=85.0, total_attempts=10, correct_attempts=9, streak=0, best_streak=0,
    ))
    db_session.add(ExerciseSession(
        id=uuid.uuid4(), profile_id=profile.id, status=SessionStatus.COMPLETED,
        mode=SessionMode.PRACTICE, started_at=datetime.now(timezone.utc).replace(tzinfo=None),
        completed_at=datetime.now(timezone.utc).replace(tzinfo=None),
    ))
    await db_session.flush()

    signals = await compute_for_profile(db_session, profile)
    assert signals.days_inactive == 0
    assert signals.avg_score == 85.0
    assert signals.risk_level == "low"


# ── list_at_risk + sorting ─────────────────────────────────


@pytest.mark.asyncio
async def test_list_at_risk_excludes_low_by_default(db_session: AsyncSession):
    user = _make_user()
    db_session.add(user)
    await db_session.flush()

    # Profile 1: active + good score (low) — should be excluded
    p_low = Profile(id=uuid.uuid4(), user_id=user.id, display_name="Active", is_active=True)
    # Profile 2: inactive 10 days (high) — should be included
    p_high = Profile(
        id=uuid.uuid4(), user_id=user.id, display_name="Décrocheur", is_active=True,
        created_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=10),
    )
    db_session.add_all([p_low, p_high])
    await db_session.flush()

    skill = await _make_skill(db_session)
    db_session.add(Progress(
        id=uuid.uuid4(), profile_id=p_low.id, skill_id=skill.id,
        smart_score=80.0, total_attempts=5, correct_attempts=4, streak=0, best_streak=0,
    ))
    db_session.add(ExerciseSession(
        id=uuid.uuid4(), profile_id=p_low.id, status=SessionStatus.COMPLETED,
        mode=SessionMode.PRACTICE, started_at=datetime.now(timezone.utc).replace(tzinfo=None),
        completed_at=datetime.now(timezone.utc).replace(tzinfo=None),
    ))
    await db_session.flush()

    rows, total = await list_at_risk(db_session, min_level="medium")
    assert total == 1
    assert rows[0].display_name == "Décrocheur"
    assert rows[0].signals.risk_level == "high"


@pytest.mark.asyncio
async def test_list_at_risk_resolves_parent_phone(db_session: AsyncSession):
    parent = User(
        id=uuid.uuid4(), email=f"{uuid.uuid4().hex[:8]}@p.com",
        phone="+22912345678", full_name="Maman",
        hashed_password="x", role=UserRole.PARENT, is_active=True,
    )
    db_session.add(parent)
    await db_session.flush()
    profile = Profile(
        id=uuid.uuid4(), user_id=parent.id, display_name="Aïcha", is_active=True,
        created_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=10),
    )
    db_session.add(profile)
    await db_session.flush()

    rows, _ = await list_at_risk(db_session, min_level="medium")
    assert len(rows) == 1
    assert rows[0].parent_phone == "+22912345678"
    assert rows[0].parent_user_id == parent.id


# ── Admin endpoint ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_students_at_risk_requires_admin(
    client: AsyncClient, test_student, test_student_profile
):
    """Non-admin should be denied."""
    resp = await client.get("/api/v1/admin/students/at-risk", headers=auth_header(test_student))
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_students_at_risk_returns_paginated_payload(
    client: AsyncClient, db_session: AsyncSession, test_admin
):
    """End-to-end : admin sees an inactive profile flagged `high`."""
    parent = _make_user(role=UserRole.PARENT)
    db_session.add(parent)
    await db_session.flush()
    profile = Profile(
        id=uuid.uuid4(), user_id=parent.id, display_name="Inactive Kid", is_active=True,
        created_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=12),
    )
    db_session.add(profile)
    await db_session.flush()

    resp = await client.get("/api/v1/admin/students/at-risk", headers=auth_header(test_admin))
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert "items" in data and "total" in data
    assert data["total"] == 1
    item = data["items"][0]
    assert item["display_name"] == "Inactive Kid"
    assert item["risk_level"] == "high"
    assert item["days_inactive"] >= 12
    assert "suggested_action" in item and item["suggested_action"]


@pytest.mark.asyncio
async def test_get_students_at_risk_min_level_high_filters_medium(
    client: AsyncClient, db_session: AsyncSession, test_admin
):
    user = _make_user()
    db_session.add(user)
    await db_session.flush()
    # `medium` candidate (4 days inactive)
    p_med = Profile(
        id=uuid.uuid4(), user_id=user.id, display_name="Med", is_active=True,
        created_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=4),
    )
    # `high` candidate (10 days inactive)
    p_hi = Profile(
        id=uuid.uuid4(), user_id=user.id, display_name="Hi", is_active=True,
        created_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=10),
    )
    db_session.add_all([p_med, p_hi])
    await db_session.flush()

    resp = await client.get(
        "/api/v1/admin/students/at-risk?min_level=high",
        headers=auth_header(test_admin),
    )
    assert resp.status_code == 200
    items = resp.json()["data"]["items"]
    names = {it["display_name"] for it in items}
    assert names == {"Hi"}


# ── At-risk funnel ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_compute_funnel_no_data(db_session: AsyncSession):
    funnel = await compute_funnel(db_session, period_days=30)
    assert funnel.detected_now == 0
    assert funnel.sms_sent == 0
    assert funnel.sms_with_reactivation == 0
    assert funnel.reactivation_rate == 0.0


@pytest.mark.asyncio
async def test_compute_funnel_counts_reactivation_within_7d(db_session: AsyncSession):
    """SMS sent → kid completed a session in the 7d window → counted as reactivation."""
    parent = _make_user(role=UserRole.PARENT)
    db_session.add(parent)
    await db_session.flush()
    kid_reactivated = Profile(
        id=uuid.uuid4(), user_id=parent.id, display_name="Réactivé", is_active=True,
    )
    kid_stayed_silent = Profile(
        id=uuid.uuid4(), user_id=parent.id, display_name="Silencieux", is_active=True,
    )
    db_session.add_all([kid_reactivated, kid_stayed_silent])
    await db_session.flush()

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    sms_at = now - timedelta(days=5)

    # SMS for kid 1, then a session 2 days later → counted
    db_session.add(Notification(
        id=uuid.uuid4(), user_id=parent.id,
        type=NotificationType.INACTIVITY, channel=NotificationChannel.SMS,
        title="t", body="b", data={"subject_profile_id": str(kid_reactivated.id), "risk_level": "high"},
        created_at=sms_at,
    ))
    db_session.add(ExerciseSession(
        id=uuid.uuid4(), profile_id=kid_reactivated.id,
        status=SessionStatus.COMPLETED, mode=SessionMode.PRACTICE,
        started_at=sms_at + timedelta(days=2), completed_at=sms_at + timedelta(days=2),
    ))

    # SMS for kid 2, no follow-up session → not counted
    db_session.add(Notification(
        id=uuid.uuid4(), user_id=parent.id,
        type=NotificationType.INACTIVITY, channel=NotificationChannel.SMS,
        title="t", body="b", data={"subject_profile_id": str(kid_stayed_silent.id), "risk_level": "medium"},
        created_at=sms_at,
    ))
    await db_session.flush()

    funnel = await compute_funnel(db_session, period_days=30)
    assert funnel.sms_sent == 2
    assert funnel.sms_with_reactivation == 1
    assert funnel.reactivation_rate == 0.5


@pytest.mark.asyncio
async def test_compute_funnel_ignores_legacy_sms_without_subject_tag(
    db_session: AsyncSession,
):
    """Pre-iter-12 SMS without `subject_profile_id` count in sms_sent but never
    in sms_with_reactivation — a known caveat documented in the docstring."""
    parent = _make_user(role=UserRole.PARENT)
    db_session.add(parent)
    await db_session.flush()
    db_session.add(Notification(
        id=uuid.uuid4(), user_id=parent.id,
        type=NotificationType.INACTIVITY, channel=NotificationChannel.SMS,
        title="t", body="b", data=None,
        created_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1),
    ))
    await db_session.flush()

    funnel = await compute_funnel(db_session, period_days=30)
    assert funnel.sms_sent == 1
    assert funnel.sms_with_reactivation == 0
    assert funnel.reactivation_rate == 0.0


@pytest.mark.asyncio
async def test_get_at_risk_funnel_endpoint(
    client: AsyncClient, db_session: AsyncSession, test_admin
):
    resp = await client.get(
        "/api/v1/admin/analytics/at-risk-funnel?period_days=30",
        headers=auth_header(test_admin),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["period_days"] == 30
    assert "detected_now" in data
    assert "sms_sent" in data
    assert "reactivation_rate" in data
