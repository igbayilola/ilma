"""Session flow tests (profile-aware)."""
import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import DifficultyLevel, Domain, Question, QuestionType, Skill, Subject
from tests.conftest import auth_header


@pytest_asyncio.fixture
async def seed_content(db_session: AsyncSession):
    """Create a subject -> domain -> skill -> questions for testing."""
    subj = Subject(id=uuid.uuid4(), name="Math", slug="math-test", order=1)
    db_session.add(subj)
    await db_session.flush()

    domain = Domain(id=uuid.uuid4(), name="Num", slug="num-test", subject_id=subj.id, order=1)
    db_session.add(domain)
    await db_session.flush()

    skill = Skill(id=uuid.uuid4(), name="Add", slug="add-test", domain_id=domain.id, order=1)
    db_session.add(skill)
    await db_session.flush()

    for i in range(3):
        q = Question(
            id=uuid.uuid4(),
            skill_id=skill.id,
            text=f"Q{i}: 1+{i}=?",
            question_type=QuestionType.MCQ,
            difficulty=DifficultyLevel.EASY,
            choices=[str(1 + i), "99"],
            correct_answer=str(1 + i),
            points=1,
        )
        db_session.add(q)

    await db_session.flush()
    return skill


@pytest.mark.asyncio
async def test_session_flow(client: AsyncClient, test_student, test_student_profile, seed_content):
    """Full session flow with profile-based auth (auto-select single profile)."""
    skill = seed_content

    # Start session — no X-Profile-Id needed since student has exactly 1 profile
    resp = await client.post(
        "/api/v1/sessions/start",
        json={"skill_id": str(skill.id), "mode": "practice"},
        headers=auth_header(test_student),
    )
    assert resp.status_code == 201
    session_id = resp.json()["data"]["id"]

    # Get next question
    resp = await client.get(
        f"/api/v1/sessions/{session_id}/next",
        headers=auth_header(test_student),
    )
    assert resp.status_code == 200
    q = resp.json()["data"]
    assert q is not None

    # Submit attempt
    resp = await client.post(
        f"/api/v1/sessions/{session_id}/attempt",
        json={
            "question_id": q["question_id"],
            "client_event_id": f"evt_{uuid.uuid4().hex[:8]}",
            "answer": q["choices"][0],
            "time_spent_seconds": 5,
        },
        headers=auth_header(test_student),
    )
    assert resp.status_code == 200

    # Complete session
    resp = await client.post(
        f"/api/v1/sessions/{session_id}/complete",
        headers=auth_header(test_student),
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "completed"


@pytest.mark.asyncio
async def test_session_flow_with_explicit_profile(
    client: AsyncClient, test_parent, test_parent_profiles, seed_content
):
    """Parent starting a session for a specific child profile via X-Profile-Id header."""
    skill = seed_content
    child_profile = test_parent_profiles[0]

    # Start session with explicit profile header
    resp = await client.post(
        "/api/v1/sessions/start",
        json={"skill_id": str(skill.id), "mode": "practice"},
        headers=auth_header(test_parent, profile=child_profile),
    )
    assert resp.status_code == 201
    session_id = resp.json()["data"]["id"]

    # Get next question
    resp = await client.get(
        f"/api/v1/sessions/{session_id}/next",
        headers=auth_header(test_parent, profile=child_profile),
    )
    assert resp.status_code == 200
    q = resp.json()["data"]
    assert q is not None


@pytest.mark.asyncio
async def test_session_requires_profile(client: AsyncClient, test_parent, test_parent_profiles, seed_content):
    """Parent with 2+ profiles must specify X-Profile-Id, otherwise 400."""
    skill = seed_content

    resp = await client.post(
        "/api/v1/sessions/start",
        json={"skill_id": str(skill.id), "mode": "practice"},
        headers=auth_header(test_parent),  # No profile specified
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_attempt_idempotence(client: AsyncClient, test_student, test_student_profile, seed_content):
    skill = seed_content

    resp = await client.post(
        "/api/v1/sessions/start",
        json={"skill_id": str(skill.id), "mode": "practice"},
        headers=auth_header(test_student),
    )
    session_id = resp.json()["data"]["id"]

    resp = await client.get(
        f"/api/v1/sessions/{session_id}/next",
        headers=auth_header(test_student),
    )
    q = resp.json()["data"]
    event_id = f"idem_{uuid.uuid4().hex[:8]}"

    # First attempt
    r1 = await client.post(
        f"/api/v1/sessions/{session_id}/attempt",
        json={
            "question_id": q["question_id"],
            "client_event_id": event_id,
            "answer": "1",
            "time_spent_seconds": 5,
        },
        headers=auth_header(test_student),
    )
    assert r1.status_code == 200

    # Same client_event_id -> idempotent (no error)
    r2 = await client.post(
        f"/api/v1/sessions/{session_id}/attempt",
        json={
            "question_id": q["question_id"],
            "client_event_id": event_id,
            "answer": "1",
            "time_spent_seconds": 5,
        },
        headers=auth_header(test_student),
    )
    assert r2.status_code == 200
    assert r1.json()["data"]["id"] == r2.json()["data"]["id"]
