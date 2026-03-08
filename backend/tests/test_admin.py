"""Admin endpoint tests — user management, KPIs, exports."""
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.content import Domain, Skill, Subject
from app.models.session import ExerciseSession, SessionMode, SessionStatus
from app.models.user import User, UserRole
from tests.conftest import auth_header


@pytest.fixture
async def extra_users(db_session: AsyncSession):
    """Create additional users for admin tests."""
    users = []
    user_data = [
        ("alice@test.com", "Alice Dupont", UserRole.STUDENT, True),
        ("bob@test.com", "Bob Martin", UserRole.STUDENT, True),
        ("charlie@test.com", "Charlie Doe", UserRole.PARENT, True),
    ]
    for email, name, role, active in user_data:
        u = User(
            id=uuid.uuid4(),
            email=email,
            full_name=name,
            hashed_password=get_password_hash("Test1234!"),
            role=role,
            is_active=active,
        )
        db_session.add(u)
        users.append(u)
    await db_session.flush()
    return users


# ── User listing ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_admin_list_users(client: AsyncClient, test_admin, extra_users):
    resp = await client.get("/api/v1/admin/users", headers=auth_header(test_admin))
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "pages" in data
    # We have test_admin + 3 extra = at least 4 (test_admin is from the fixture)
    assert data["total"] >= 4


@pytest.mark.asyncio
async def test_admin_list_users_filter_by_role(
    client: AsyncClient, test_admin, extra_users
):
    resp = await client.get(
        "/api/v1/admin/users?role=student", headers=auth_header(test_admin)
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    # Should only contain students
    for user in data["items"]:
        assert user["role"] == "student"
    assert data["total"] >= 2  # alice + bob


@pytest.mark.asyncio
async def test_admin_list_users_search(
    client: AsyncClient, test_admin, extra_users
):
    resp = await client.get(
        "/api/v1/admin/users?search=alice", headers=auth_header(test_admin)
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total"] >= 1
    assert any("alice" in u["email"] for u in data["items"])


@pytest.mark.asyncio
async def test_admin_list_users_pagination(
    client: AsyncClient, test_admin, extra_users
):
    resp = await client.get(
        "/api/v1/admin/users?page=1&page_size=2", headers=auth_header(test_admin)
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data["items"]) <= 2
    assert data["page"] == 1
    assert data["page_size"] == 2


@pytest.mark.asyncio
async def test_student_cannot_list_users(client: AsyncClient, test_student):
    resp = await client.get("/api/v1/admin/users", headers=auth_header(test_student))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_parent_cannot_list_users(client: AsyncClient, test_parent):
    resp = await client.get("/api/v1/admin/users", headers=auth_header(test_parent))
    assert resp.status_code == 403


# ── Suspend / reactivate ─────────────────────────────────


@pytest.mark.asyncio
async def test_suspend_user(client: AsyncClient, test_admin, extra_users):
    target = extra_users[0]  # alice
    resp = await client.post(
        f"/api/v1/admin/users/{target.id}/suspend",
        headers=auth_header(test_admin),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["message"] == "Utilisateur suspendu"
    assert body["data"]["is_active"] is False


@pytest.mark.asyncio
async def test_reactivate_user(client: AsyncClient, test_admin, extra_users):
    target = extra_users[0]
    # First suspend
    await client.post(
        f"/api/v1/admin/users/{target.id}/suspend",
        headers=auth_header(test_admin),
    )
    # Then reactivate
    resp = await client.post(
        f"/api/v1/admin/users/{target.id}/reactivate",
        headers=auth_header(test_admin),
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "Utilisateur réactivé"
    assert resp.json()["data"]["is_active"] is True


@pytest.mark.asyncio
async def test_suspend_nonexistent_user(client: AsyncClient, test_admin):
    fake_id = uuid.uuid4()
    resp = await client.post(
        f"/api/v1/admin/users/{fake_id}/suspend",
        headers=auth_header(test_admin),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_reactivate_nonexistent_user(client: AsyncClient, test_admin):
    fake_id = uuid.uuid4()
    resp = await client.post(
        f"/api/v1/admin/users/{fake_id}/reactivate",
        headers=auth_header(test_admin),
    )
    assert resp.status_code == 404


# ── Reset password ────────────────────────────────────────


@pytest.mark.asyncio
async def test_reset_user_password(client: AsyncClient, test_admin, extra_users):
    target = extra_users[0]
    resp = await client.post(
        f"/api/v1/admin/users/{target.id}/reset-password",
        headers=auth_header(test_admin),
    )
    assert resp.status_code == 200
    assert "réinitialisé" in resp.json()["message"]


@pytest.mark.asyncio
async def test_reset_password_nonexistent_user(client: AsyncClient, test_admin):
    fake_id = uuid.uuid4()
    resp = await client.post(
        f"/api/v1/admin/users/{fake_id}/reset-password",
        headers=auth_header(test_admin),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_student_cannot_suspend(client: AsyncClient, test_student, extra_users):
    target = extra_users[0]
    resp = await client.post(
        f"/api/v1/admin/users/{target.id}/suspend",
        headers=auth_header(test_student),
    )
    assert resp.status_code == 403


# ── KPIs ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_admin_kpis(client: AsyncClient, test_admin):
    resp = await client.get("/api/v1/admin/analytics/kpis", headers=auth_header(test_admin))
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    kpis = body["data"]
    assert "dau" in kpis
    assert "mau" in kpis
    assert "total_users" in kpis
    assert "total_students" in kpis
    assert "sessions_today" in kpis
    assert "mrr_xof" in kpis
    assert "active_subscriptions" in kpis
    assert "avg_session_score" in kpis


@pytest.mark.asyncio
async def test_admin_kpis_with_data(
    client: AsyncClient, test_admin, extra_users, db_session: AsyncSession
):
    # Create a subject/domain/skill for sessions
    subj = Subject(id=uuid.uuid4(), name="Math", slug="math-admin", order=1)
    db_session.add(subj)
    await db_session.flush()
    domain = Domain(id=uuid.uuid4(), name="Num", slug="num-admin", subject_id=subj.id, order=1)
    db_session.add(domain)
    await db_session.flush()
    skill = Skill(id=uuid.uuid4(), name="Add", slug="add-admin", domain_id=domain.id, order=1)
    db_session.add(skill)
    await db_session.flush()

    # Create a completed session
    session = ExerciseSession(
        id=uuid.uuid4(),
        student_id=extra_users[0].id,
        skill_id=skill.id,
        mode=SessionMode.PRACTICE,
        status=SessionStatus.COMPLETED,
        total_questions=5,
        correct_answers=4,
        score=80.0,
    )
    db_session.add(session)
    await db_session.flush()

    resp = await client.get("/api/v1/admin/analytics/kpis", headers=auth_header(test_admin))
    kpis = resp.json()["data"]
    # With extra_users, total should be at least 4 (admin + 3 extra)
    assert kpis["total_users"] >= 4
    assert kpis["total_students"] >= 2


@pytest.mark.asyncio
async def test_student_cannot_access_kpis(client: AsyncClient, test_student):
    resp = await client.get(
        "/api/v1/admin/analytics/kpis", headers=auth_header(test_student)
    )
    assert resp.status_code == 403


# ── Question analytics ────────────────────────────────────


@pytest.mark.asyncio
async def test_admin_question_stats(client: AsyncClient, test_admin):
    resp = await client.get(
        "/api/v1/admin/analytics/questions", headers=auth_header(test_admin)
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)


@pytest.mark.asyncio
async def test_student_cannot_access_question_stats(client: AsyncClient, test_student):
    resp = await client.get(
        "/api/v1/admin/analytics/questions", headers=auth_header(test_student)
    )
    assert resp.status_code == 403


# ── Payments listing (admin) ──────────────────────────────


@pytest.mark.asyncio
async def test_admin_list_payments(client: AsyncClient, test_admin):
    resp = await client.get("/api/v1/admin/payments", headers=auth_header(test_admin))
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_student_cannot_list_payments(client: AsyncClient, test_student):
    resp = await client.get("/api/v1/admin/payments", headers=auth_header(test_student))
    assert resp.status_code == 403


# ── CSV export ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_admin_export_users_csv(client: AsyncClient, test_admin, extra_users):
    resp = await client.get(
        "/api/v1/admin/export/users.csv", headers=auth_header(test_admin)
    )
    assert resp.status_code == 200
    assert "text/csv" in resp.headers.get("content-type", "")
    content = resp.text
    # Check CSV headers
    lines = content.strip().split("\n")
    assert len(lines) >= 2  # header + at least 1 user
    header = lines[0]
    assert "id" in header
    assert "email" in header
    assert "full_name" in header
    assert "role" in header
    assert "is_active" in header


@pytest.mark.asyncio
async def test_student_cannot_export_csv(client: AsyncClient, test_student):
    resp = await client.get(
        "/api/v1/admin/export/users.csv", headers=auth_header(test_student)
    )
    assert resp.status_code == 403
