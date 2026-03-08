"""Health and version endpoint tests."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["status"] in ("ok", "degraded")
    assert "duration_ms" in data
    assert "services" in data
    assert "database" in data["services"]
    assert data["services"]["database"]["status"] == "ok"


@pytest.mark.asyncio
async def test_health_check_db_service(client: AsyncClient):
    resp = await client.get("/api/v1/health")
    body = resp.json()
    db_info = body["data"]["services"]["database"]
    assert db_info["status"] == "ok"
    assert db_info["error"] is None


@pytest.mark.asyncio
async def test_health_check_redis_service(client: AsyncClient):
    resp = await client.get("/api/v1/health")
    body = resp.json()
    redis_info = body["data"]["services"]["redis"]
    # Redis may be unavailable in test env — that's fine
    assert redis_info["status"] in ("ok", "unavailable")


@pytest.mark.asyncio
async def test_version(client: AsyncClient):
    resp = await client.get("/api/v1/version")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["version"] == "0.1.0"
    assert "project" in data
    assert data["project"] == "ILMA Backend"


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    resp = await client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "ILMA" in body["message"]
