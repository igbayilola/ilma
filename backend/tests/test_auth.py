"""Auth endpoint tests."""
import pytest
from httpx import AsyncClient

from tests.conftest import auth_header


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "new@test.com", "password": "Pass1234!", "full_name": "New User"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    # Register now returns combined auth response: {access_token, refresh_token, user, profiles, ...}
    assert "access_token" in body["data"]
    assert body["data"]["user"]["email"] == "new@test.com"
    # Registration creates a PARENT account (no auto-profile)
    assert "profiles" in body["data"]
    assert len(body["data"]["profiles"]) == 0


@pytest.mark.asyncio
async def test_register_parent_no_auto_profile(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "parent_new@test.com", "password": "Pass1234!", "full_name": "Parent User", "role": "PARENT"},
    )
    assert resp.status_code == 201
    body = resp.json()
    # Parent registration does NOT auto-create profiles
    assert body["data"]["profiles"] == []


@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@test.com", "password": "Pass1234!", "full_name": "Dup"},
    )
    resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@test.com", "password": "Pass1234!", "full_name": "Dup2"},
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@test.com", "password": "Pass1234!", "full_name": "Login"},
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@test.com", "password": "Pass1234!"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "access_token" in body["data"]
    assert "refresh_token" in body["data"]


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "wrong@test.com", "password": "Pass1234!", "full_name": "Wrong"},
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@test.com", "password": "BadPass!"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_authenticated(client: AsyncClient, test_student):
    resp = await client.get("/api/v1/auth/me", headers=auth_header(test_student))
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["email"] == "student@test.com"


@pytest.mark.asyncio
async def test_me_unauthenticated(client: AsyncClient):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401
