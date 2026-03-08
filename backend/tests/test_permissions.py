"""Permission tests: role enforcement + profile access control."""
import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import auth_header


@pytest.mark.asyncio
async def test_student_cannot_access_admin(client: AsyncClient, test_student):
    resp = await client.get("/api/v1/admin/users", headers=auth_header(test_student))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_parent_cannot_access_admin(client: AsyncClient, test_parent):
    resp = await client.get("/api/v1/admin/users", headers=auth_header(test_parent))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_access_admin(client: AsyncClient, test_admin):
    resp = await client.get("/api/v1/admin/users", headers=auth_header(test_admin))
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_parent_without_profile_cannot_start_session(
    client: AsyncClient, test_parent, test_parent_profiles
):
    """Parent with 2+ profiles must specify X-Profile-Id for session endpoints."""
    resp = await client.post(
        "/api/v1/sessions/start",
        json={"skill_id": str(uuid.uuid4()), "mode": "practice"},
        headers=auth_header(test_parent),  # No profile header
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_cannot_access_other_users_profile(
    client: AsyncClient, test_student, test_parent_profiles
):
    """Student cannot use a parent's profile via X-Profile-Id."""
    foreign_profile = test_parent_profiles[0]
    resp = await client.get(
        f"/api/v1/profiles/{foreign_profile.id}",
        headers=auth_header(test_student),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_user_without_profiles_gets_400_on_session(client: AsyncClient, test_parent):
    """Parent with 0 profiles gets a 400 when hitting session endpoints."""
    resp = await client.post(
        "/api/v1/sessions/start",
        json={"skill_id": str(uuid.uuid4()), "mode": "practice"},
        headers=auth_header(test_parent),
    )
    assert resp.status_code == 400
