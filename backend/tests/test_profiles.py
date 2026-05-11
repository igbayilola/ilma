"""Profile CRUD + PIN verification tests (Netflix-style profiles)."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import auth_header


@pytest.mark.asyncio
async def test_list_profiles_empty(client: AsyncClient, test_parent):
    resp = await client.get("/api/v1/profiles", headers=auth_header(test_parent))
    assert resp.status_code == 200
    assert resp.json()["data"] == []


@pytest.mark.asyncio
async def test_create_profile(client: AsyncClient, test_parent):
    resp = await client.post(
        "/api/v1/profiles",
        json={"display_name": "Aïcha", "avatar_url": "https://example.com/avatar.png"},
        headers=auth_header(test_parent),
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["display_name"] == "Aïcha"
    assert data["is_active"] is True
    assert data["has_pin"] is False


@pytest.mark.asyncio
async def test_create_profile_with_pin(client: AsyncClient, test_parent):
    resp = await client.post(
        "/api/v1/profiles",
        json={"display_name": "Kofi", "pin": "1234"},
        headers=auth_header(test_parent),
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["display_name"] == "Kofi"
    assert data["has_pin"] is True


@pytest.mark.asyncio
async def test_create_profile_max_limit(client: AsyncClient, test_parent):
    # Create 5 profiles (the limit)
    for i in range(5):
        resp = await client.post(
            "/api/v1/profiles",
            json={"display_name": f"Child {i}"},
            headers=auth_header(test_parent),
        )
        assert resp.status_code == 201

    # 6th should fail
    resp = await client.post(
        "/api/v1/profiles",
        json={"display_name": "Child 6"},
        headers=auth_header(test_parent),
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_list_profiles(client: AsyncClient, test_parent, test_parent_profiles):
    resp = await client.get("/api/v1/profiles", headers=auth_header(test_parent))
    assert resp.status_code == 200
    profiles = resp.json()["data"]
    assert len(profiles) == 2
    names = {p["display_name"] for p in profiles}
    assert "Aïcha" in names
    assert "Kofi" in names


@pytest.mark.asyncio
async def test_get_profile(client: AsyncClient, test_parent, test_parent_profiles):
    profile = test_parent_profiles[0]
    resp = await client.get(
        f"/api/v1/profiles/{profile.id}",
        headers=auth_header(test_parent),
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["display_name"] == profile.display_name


@pytest.mark.asyncio
async def test_get_profile_wrong_user(client: AsyncClient, test_student, test_parent_profiles):
    """A student cannot access a parent's profiles."""
    profile = test_parent_profiles[0]
    resp = await client.get(
        f"/api/v1/profiles/{profile.id}",
        headers=auth_header(test_student),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_profile(client: AsyncClient, test_parent, test_parent_profiles):
    profile = test_parent_profiles[0]
    resp = await client.patch(
        f"/api/v1/profiles/{profile.id}",
        json={"display_name": "Aïcha Updated"},
        headers=auth_header(test_parent),
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["display_name"] == "Aïcha Updated"


@pytest.mark.asyncio
async def test_delete_profile(client: AsyncClient, test_parent, test_parent_profiles):
    profile = test_parent_profiles[1]
    resp = await client.delete(
        f"/api/v1/profiles/{profile.id}",
        headers=auth_header(test_parent),
    )
    assert resp.status_code == 200

    # Verify profile is soft-deleted (not in list)
    resp = await client.get("/api/v1/profiles", headers=auth_header(test_parent))
    ids = [p["id"] for p in resp.json()["data"]]
    assert str(profile.id) not in ids


@pytest.mark.asyncio
async def test_verify_pin_success(client: AsyncClient, test_parent, db_session: AsyncSession):
    # Create profile with PIN via API
    resp = await client.post(
        "/api/v1/profiles",
        json={"display_name": "PIN Child", "pin": "5678"},
        headers=auth_header(test_parent),
    )
    profile_id = resp.json()["data"]["id"]

    # Verify correct PIN
    resp = await client.post(
        f"/api/v1/profiles/{profile_id}/verify-pin",
        json={"pin": "5678"},
        headers=auth_header(test_parent),
    )
    assert resp.status_code == 200
    assert resp.json()["success"] is True


@pytest.mark.asyncio
async def test_verify_pin_wrong(client: AsyncClient, test_parent):
    resp = await client.post(
        "/api/v1/profiles",
        json={"display_name": "PIN Child 2", "pin": "1111"},
        headers=auth_header(test_parent),
    )
    profile_id = resp.json()["data"]["id"]

    resp = await client.post(
        f"/api/v1/profiles/{profile_id}/verify-pin",
        json={"pin": "9999"},
        headers=auth_header(test_parent),
    )
    # Wrong PIN returns 403
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_set_weekly_goal(client: AsyncClient, test_parent, test_parent_profiles):
    profile = test_parent_profiles[0]
    resp = await client.patch(
        f"/api/v1/profiles/{profile.id}/goal",
        json={"weekly_goal_minutes": 90},
        headers=auth_header(test_parent),
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_student_self_profile_auto_select(client: AsyncClient, test_student, test_student_profile):
    """Standalone student with 1 profile: auto-selected by get_active_profile (no X-Profile-Id needed)."""
    resp = await client.get("/api/v1/profiles", headers=auth_header(test_student))
    assert resp.status_code == 200
    profiles = resp.json()["data"]
    assert len(profiles) == 1
    assert profiles[0]["display_name"] == test_student.full_name


@pytest.mark.asyncio
async def test_register_creates_parent_no_auto_profile(client: AsyncClient):
    """Registration always creates a PARENT account with no auto-profile."""
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "selfprofile@test.com", "password": "Pass1234!", "full_name": "Auto Profile"},
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert "profiles" in data
    assert len(data["profiles"]) == 0
    assert data["user"]["role"] == "PARENT"
