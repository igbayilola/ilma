"""Tests for POST /teacher/classrooms/join — the A6.6 invite-code flow.

Covers both call shapes:
- Active-profile context (student-as-self / kid-profile selected) — no header
  needed if the user has a single profile.
- Parent-managing-kid context — X-Profile-Id header points at the kid's
  profile; the existing `get_active_profile` dep checks parent ownership.
"""
import uuid
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.classroom import Classroom
from app.models.profile import Profile
from app.models.user import User, UserRole
from tests.conftest import auth_header


def _make_teacher(db_session: AsyncSession) -> User:
    return User(
        id=uuid.uuid4(),
        email=f"prof-{uuid.uuid4().hex[:6]}@test.com",
        full_name="Prof Test",
        hashed_password=get_password_hash("Xr;aTRKMx_1CI1Wd@HF1c!9"),
        role=UserRole.TEACHER,
        is_active=True,
    )


async def _make_classroom(
    db_session: AsyncSession, teacher_id: uuid.UUID, invite_code: str,
    max_students: int = 30,
) -> Classroom:
    classroom = Classroom(
        id=uuid.uuid4(),
        teacher_id=teacher_id,
        name="CM2-A",
        invite_code=invite_code,
        is_active=True,
        max_students=max_students,
    )
    db_session.add(classroom)
    await db_session.flush()
    return classroom


# ── Single-profile student (auto active profile) ───────────


@pytest.mark.asyncio
async def test_join_classroom_auto_active_profile(
    client: AsyncClient, db_session: AsyncSession,
    test_student: User, test_student_profile: Profile,
):
    teacher = _make_teacher(db_session)
    db_session.add(teacher)
    await db_session.flush()
    classroom = await _make_classroom(db_session, teacher.id, "STU1JOIN")

    resp = await client.post(
        "/api/v1/teacher/classrooms/join",
        json={"invite_code": "STU1JOIN"},
        headers=auth_header(test_student),
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["classroom_id"] == str(classroom.id)
    assert body["data"]["classroom_name"] == "CM2-A"


# ── Parent picking a specific kid via X-Profile-Id ─────────


@pytest.mark.asyncio
async def test_join_classroom_parent_with_explicit_profile_id(
    client: AsyncClient, db_session: AsyncSession,
    test_parent: User, test_parent_profiles: list,
):
    """Parent has 2 kids → must specify X-Profile-Id to disambiguate."""
    teacher = _make_teacher(db_session)
    db_session.add(teacher)
    await db_session.flush()
    classroom = await _make_classroom(db_session, teacher.id, "PARENT12")

    # Pick the second kid intentionally to verify the right profile is picked
    target = test_parent_profiles[1]
    resp = await client.post(
        "/api/v1/teacher/classrooms/join",
        json={"invite_code": "PARENT12"},
        headers={**auth_header(test_parent), "X-Profile-Id": str(target.id)},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["data"]["profile_id"] == str(target.id)
    assert body["data"]["classroom_id"] == str(classroom.id)


@pytest.mark.asyncio
async def test_join_classroom_parent_without_profile_header_fails(
    client: AsyncClient, db_session: AsyncSession,
    test_parent: User, test_parent_profiles: list,
):
    """Parent with 2 profiles + no X-Profile-Id → 400 (ambiguous, per
    `get_active_profile` contract)."""
    teacher = _make_teacher(db_session)
    db_session.add(teacher)
    await db_session.flush()
    await _make_classroom(db_session, teacher.id, "AMBIGUE1")

    resp = await client.post(
        "/api/v1/teacher/classrooms/join",
        json={"invite_code": "AMBIGUE1"},
        headers=auth_header(test_parent),
    )
    assert resp.status_code in (400, 422)


# ── Error cases ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_join_classroom_invalid_code(
    client: AsyncClient, db_session: AsyncSession,
    test_student: User, test_student_profile: Profile,
):
    resp = await client.post(
        "/api/v1/teacher/classrooms/join",
        json={"invite_code": "NOPENOPE"},
        headers=auth_header(test_student),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_join_classroom_already_joined_returns_conflict(
    client: AsyncClient, db_session: AsyncSession,
    test_student: User, test_student_profile: Profile,
):
    teacher = _make_teacher(db_session)
    db_session.add(teacher)
    await db_session.flush()
    await _make_classroom(db_session, teacher.id, "DOUBLE12")

    first = await client.post(
        "/api/v1/teacher/classrooms/join",
        json={"invite_code": "DOUBLE12"},
        headers=auth_header(test_student),
    )
    assert first.status_code == 200

    second = await client.post(
        "/api/v1/teacher/classrooms/join",
        json={"invite_code": "DOUBLE12"},
        headers=auth_header(test_student),
    )
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_join_classroom_full_returns_400(
    client: AsyncClient, db_session: AsyncSession,
    test_student: User, test_student_profile: Profile,
):
    teacher = _make_teacher(db_session)
    db_session.add(teacher)
    await db_session.flush()
    # Capacity 0 → already full.
    await _make_classroom(db_session, teacher.id, "FULL1234", max_students=0)

    resp = await client.post(
        "/api/v1/teacher/classrooms/join",
        json={"invite_code": "FULL1234"},
        headers=auth_header(test_student),
    )
    assert resp.status_code == 400
    body = resp.json()
    assert "CLASSROOM_FULL" in body.get("error", {}).get("code", "") or "pleine" in body.get("message", "").lower() or "pleine" in body.get("detail", "").lower()
