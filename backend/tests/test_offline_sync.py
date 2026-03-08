"""Offline sync endpoint tests (profile-aware)."""
import uuid
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import DifficultyLevel, Domain, Question, QuestionType, Skill, Subject
from tests.conftest import auth_header


@pytest.fixture
async def sync_content(db_session: AsyncSession):
    subj = Subject(id=uuid.uuid4(), name="FR", slug="fr-sync", order=1)
    db_session.add(subj)
    await db_session.flush()

    domain = Domain(id=uuid.uuid4(), name="Gram", slug="gram-sync", subject_id=subj.id, order=1)
    db_session.add(domain)
    await db_session.flush()

    skill = Skill(id=uuid.uuid4(), name="Verbs", slug="verbs-sync", domain_id=domain.id, order=1)
    db_session.add(skill)
    await db_session.flush()

    q = Question(
        id=uuid.uuid4(),
        skill_id=skill.id,
        text="Conjugue 'être' au présent",
        question_type=QuestionType.MCQ,
        difficulty=DifficultyLevel.EASY,
        choices=["je suis", "je es"],
        correct_answer="je suis",
        points=1,
    )
    db_session.add(q)
    await db_session.flush()
    return skill, q


@pytest.mark.asyncio
async def test_sync_batch(client: AsyncClient, test_student, test_student_profile, sync_content):
    skill, question = sync_content

    # Start a session first (auto-selects single profile)
    resp = await client.post(
        "/api/v1/sessions/start",
        json={"skill_id": str(skill.id), "mode": "practice"},
        headers=auth_header(test_student),
    )
    session_id = resp.json()["data"]["id"]

    events = [
        {
            "event_type": "attempt_created",
            "client_event_id": f"sync_{uuid.uuid4().hex[:8]}",
            "payload": {
                "session_id": session_id,
                "question_id": str(question.id),
                "skill_id": str(skill.id),
                "answer": "je suis",
                "time_spent_seconds": 10,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    ]

    resp = await client.post(
        "/api/v1/offline/sync",
        json={"events": events},
        headers=auth_header(test_student),
    )
    assert resp.status_code == 200
    body = resp.json()["data"]
    assert body["processed"] == 1
    assert body["accepted"] == 1
    assert body["duplicates"] == 0


@pytest.mark.asyncio
async def test_sync_duplicate_event(client: AsyncClient, test_student, test_student_profile, sync_content):
    skill, question = sync_content

    resp = await client.post(
        "/api/v1/sessions/start",
        json={"skill_id": str(skill.id), "mode": "practice"},
        headers=auth_header(test_student),
    )
    session_id = resp.json()["data"]["id"]

    event_id = f"dup_{uuid.uuid4().hex[:8]}"
    event = {
        "event_type": "attempt_created",
        "client_event_id": event_id,
        "payload": {
            "session_id": session_id,
            "question_id": str(question.id),
            "skill_id": str(skill.id),
            "answer": "je suis",
            "time_spent_seconds": 10,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # First sync
    r1 = await client.post(
        "/api/v1/offline/sync",
        json={"events": [event]},
        headers=auth_header(test_student),
    )
    assert r1.json()["data"]["accepted"] == 1

    # Replay -> duplicate
    r2 = await client.post(
        "/api/v1/offline/sync",
        json={"events": [event]},
        headers=auth_header(test_student),
    )
    assert r2.json()["data"]["duplicates"] == 1
    assert r2.json()["data"]["accepted"] == 0


@pytest.mark.asyncio
async def test_sync_with_explicit_profile(
    client: AsyncClient, test_parent, test_parent_profiles, sync_content
):
    """Parent syncing offline events for a specific child profile."""
    skill, question = sync_content
    child_profile = test_parent_profiles[0]

    # Start session with explicit profile
    resp = await client.post(
        "/api/v1/sessions/start",
        json={"skill_id": str(skill.id), "mode": "practice"},
        headers=auth_header(test_parent, profile=child_profile),
    )
    session_id = resp.json()["data"]["id"]

    events = [
        {
            "event_type": "attempt_created",
            "client_event_id": f"sync_{uuid.uuid4().hex[:8]}",
            "payload": {
                "session_id": session_id,
                "question_id": str(question.id),
                "skill_id": str(skill.id),
                "answer": "je suis",
                "time_spent_seconds": 8,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    ]

    resp = await client.post(
        "/api/v1/offline/sync",
        json={"events": events},
        headers=auth_header(test_parent, profile=child_profile),
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["accepted"] == 1
