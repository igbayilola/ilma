"""Badge endpoint and service tests (profile-aware)."""
import uuid
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.badge import Badge, BadgeCategory, StudentBadge
from app.models.content import DifficultyLevel, Domain, Question, QuestionType, Skill, Subject
from app.models.session import ExerciseSession, SessionMode, SessionStatus
from app.services.badge_service import BADGE_RULES, badge_service
from tests.conftest import auth_header


@pytest.fixture
async def seed_badges(db_session: AsyncSession):
    """Create badge definitions in the DB."""
    badges = []
    badge_data = [
        ("first_exercise", "Premier exercice", "Complete ton premier exercice", BadgeCategory.COMPLETION),
        ("streak_3", "Serie de 3", "3 bonnes reponses consecutives", BadgeCategory.STREAK),
        ("streak_10", "Serie de 10", "10 bonnes reponses consecutives", BadgeCategory.STREAK),
        ("mastery_skill", "Maitre de competence", "90%+ sur une competence", BadgeCategory.MASTERY),
        ("all_subjects", "Explorateur", "Exercice dans chaque matiere", BadgeCategory.SPECIAL),
    ]
    for code, name, desc, category in badge_data:
        b = Badge(
            id=uuid.uuid4(),
            code=code,
            name=name,
            description=desc,
            icon=f"badge-{code}",
            category=category,
        )
        db_session.add(b)
        badges.append(b)
    await db_session.flush()
    return badges


@pytest.fixture
async def badge_content(db_session: AsyncSession):
    """Create content for badge testing."""
    subj = Subject(id=uuid.uuid4(), name="Math", slug="math-badge", order=1)
    db_session.add(subj)
    await db_session.flush()

    domain = Domain(id=uuid.uuid4(), name="Num", slug="num-badge", subject_id=subj.id, order=1)
    db_session.add(domain)
    await db_session.flush()

    skill = Skill(id=uuid.uuid4(), name="Add", slug="add-badge", domain_id=domain.id, order=1)
    db_session.add(skill)
    await db_session.flush()

    q = Question(
        id=uuid.uuid4(),
        skill_id=skill.id,
        text="1+1=?",
        question_type=QuestionType.MCQ,
        difficulty=DifficultyLevel.EASY,
        choices=["2", "3"],
        correct_answer="2",
        points=1,
    )
    db_session.add(q)
    await db_session.flush()
    return skill


# ── Badge listing (student) ────────────────────────────────


@pytest.mark.asyncio
async def test_my_badges_empty(client: AsyncClient, test_student, test_student_profile):
    """Student with profile auto-select can list badges."""
    resp = await client.get(
        "/api/v1/students/me/badges", headers=auth_header(test_student)
    )
    assert resp.status_code == 200
    assert resp.json()["data"] == []


@pytest.mark.asyncio
async def test_my_badges_with_earned(
    client: AsyncClient, test_student, test_student_profile, db_session: AsyncSession, seed_badges
):
    badge = seed_badges[0]  # first_exercise
    sb = StudentBadge(
        profile_id=test_student_profile.id,
        badge_id=badge.id,
        awarded_at=datetime.now(timezone.utc),
    )
    db_session.add(sb)
    await db_session.flush()

    resp = await client.get(
        "/api/v1/students/me/badges", headers=auth_header(test_student)
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1
    assert data[0]["badge_code"] == "first_exercise"
    assert data[0]["badge_name"] == "Premier exercice"
    assert data[0]["category"] == "completion"
    assert data[0]["awarded_at"] is not None


# ── Badge listing (parent/admin) ──────────────────────────


@pytest.mark.asyncio
async def test_parent_view_student_badges(
    client: AsyncClient, test_parent, test_student_profile, db_session: AsyncSession, seed_badges,
    test_student,
):
    badge = seed_badges[0]
    sb = StudentBadge(
        profile_id=test_student_profile.id,
        badge_id=badge.id,
        awarded_at=datetime.now(timezone.utc),
    )
    db_session.add(sb)
    await db_session.flush()

    resp = await client.get(
        f"/api/v1/students/{test_student_profile.id}/badges",
        headers=auth_header(test_parent),
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1


@pytest.mark.asyncio
async def test_admin_view_student_badges(
    client: AsyncClient, test_admin, test_student, test_student_profile, db_session: AsyncSession, seed_badges
):
    resp = await client.get(
        f"/api/v1/students/{test_student_profile.id}/badges",
        headers=auth_header(test_admin),
    )
    assert resp.status_code == 200
    assert resp.json()["data"] == []


@pytest.mark.asyncio
async def test_student_cannot_view_other_badges(
    client: AsyncClient, test_student, test_student_profile
):
    other_id = uuid.uuid4()
    resp = await client.get(
        f"/api/v1/students/{other_id}/badges",
        headers=auth_header(test_student),
    )
    # Students can't use /students/{id}/badges — requires PARENT or ADMIN
    assert resp.status_code == 403


# ── Badge service: award logic ────────────────────────────


@pytest.mark.asyncio
async def test_badge_rules_defined():
    """Verify all expected badge rules exist."""
    assert "first_exercise" in BADGE_RULES
    assert "streak_3" in BADGE_RULES
    assert "streak_10" in BADGE_RULES
    assert "mastery_skill" in BADGE_RULES
    assert "all_subjects" in BADGE_RULES


@pytest.mark.asyncio
async def test_award_first_exercise_badge(
    db_session: AsyncSession, test_student, test_student_profile, seed_badges, badge_content
):
    skill = badge_content

    # Create a completed session using profile_id
    session = ExerciseSession(
        id=uuid.uuid4(),
        profile_id=test_student_profile.id,
        skill_id=skill.id,
        mode=SessionMode.PRACTICE,
        status=SessionStatus.COMPLETED,
        total_questions=1,
        correct_answers=1,
        score=100.0,
    )
    db_session.add(session)
    await db_session.flush()

    # Award badges using profile_id
    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "first_exercise" in awarded


@pytest.mark.asyncio
async def test_award_badges_no_duplicates(
    db_session: AsyncSession, test_student, test_student_profile, seed_badges, badge_content
):
    skill = badge_content

    session = ExerciseSession(
        id=uuid.uuid4(),
        profile_id=test_student_profile.id,
        skill_id=skill.id,
        mode=SessionMode.PRACTICE,
        status=SessionStatus.COMPLETED,
        total_questions=1,
        correct_answers=1,
        score=100.0,
    )
    db_session.add(session)
    await db_session.flush()

    # First award
    first_awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "first_exercise" in first_awarded

    # Second award — should not re-award
    second_awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "first_exercise" not in second_awarded


@pytest.mark.asyncio
async def test_get_student_badges_service(
    db_session: AsyncSession, test_student, test_student_profile, seed_badges
):
    badge = seed_badges[0]
    sb = StudentBadge(
        profile_id=test_student_profile.id,
        badge_id=badge.id,
        awarded_at=datetime.now(timezone.utc),
    )
    db_session.add(sb)
    await db_session.flush()

    badges = await badge_service.get_student_badges(db_session, test_student_profile.id)
    assert len(badges) == 1
    assert badges[0]["badge_code"] == "first_exercise"


@pytest.mark.asyncio
async def test_sync_badge_event(
    db_session: AsyncSession, test_student, test_student_profile, seed_badges
):
    result = await badge_service.sync_badge_event(
        db_session,
        profile_id=test_student_profile.id,
        badge_code="first_exercise",
        client_event_id="offline_badge_001",
        awarded_at=datetime.now(timezone.utc),
    )
    assert result is True

    # Duplicate — same client_event_id
    result2 = await badge_service.sync_badge_event(
        db_session,
        profile_id=test_student_profile.id,
        badge_code="first_exercise",
        client_event_id="offline_badge_001",
        awarded_at=datetime.now(timezone.utc),
    )
    assert result2 is False


@pytest.mark.asyncio
async def test_sync_badge_event_unknown_code(
    db_session: AsyncSession, test_student, test_student_profile, seed_badges
):
    result = await badge_service.sync_badge_event(
        db_session,
        profile_id=test_student_profile.id,
        badge_code="nonexistent_badge",
        client_event_id="offline_badge_002",
        awarded_at=datetime.now(timezone.utc),
    )
    assert result is False
