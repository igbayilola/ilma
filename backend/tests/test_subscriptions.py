"""Subscription and payment endpoint tests (profile-aware)."""
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import (
    Plan,
    PlanTier,
)
from tests.conftest import auth_header


@pytest.fixture
async def seed_plans(db_session: AsyncSession):
    """Create subscription plans."""
    plans = []
    plan_data = [
        ("Gratuit", PlanTier.FREE, 0, 365, "Plan gratuit"),
        ("Basique", PlanTier.BASIC, 2000, 30, "Plan mensuel basique"),
        ("Premium", PlanTier.PREMIUM, 5000, 30, "Plan mensuel premium"),
    ]
    for name, tier, price, days, desc in plan_data:
        p = Plan(
            id=uuid.uuid4(),
            name=name,
            tier=tier,
            price_xof=price,
            duration_days=days,
            description=desc,
            is_active=True,
        )
        db_session.add(p)
        plans.append(p)
    await db_session.flush()
    return plans


# ── Plan listing ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_plans(client: AsyncClient, seed_plans):
    resp = await client.get("/api/v1/subscriptions/plans")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    plans = body["data"]
    assert len(plans) == 3
    # Ordered by price
    assert plans[0]["price_xof"] <= plans[1]["price_xof"]


@pytest.mark.asyncio
async def test_list_plans_structure(client: AsyncClient, seed_plans):
    resp = await client.get("/api/v1/subscriptions/plans")
    plan = resp.json()["data"][0]
    assert "id" in plan
    assert "name" in plan
    assert "tier" in plan
    assert "price_xof" in plan
    assert "duration_days" in plan
    assert "description" in plan


@pytest.mark.asyncio
async def test_list_plans_empty(client: AsyncClient):
    resp = await client.get("/api/v1/subscriptions/plans")
    assert resp.status_code == 200
    assert resp.json()["data"] == []


# ── User subscription (requires profile) ─────────────────


@pytest.mark.asyncio
async def test_my_subscription_none(client: AsyncClient, test_student, test_student_profile):
    """GET /me/subscription uses get_active_profile — needs profile fixture."""
    resp = await client.get("/api/v1/me/subscription", headers=auth_header(test_student))
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"] is None
    assert body["message"] == "Aucun abonnement actif"


@pytest.mark.asyncio
async def test_my_subscription_unauthenticated(client: AsyncClient):
    resp = await client.get("/api/v1/me/subscription")
    assert resp.status_code == 401


# ── Payment init ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_init_payment_mock(client: AsyncClient, test_student, test_student_profile, seed_plans):
    basic_plan = seed_plans[1]  # Basique
    resp = await client.post(
        "/api/v1/payments/init",
        json={
            "plan_id": str(basic_plan.id),
            "provider": "mock",
        },
        headers=auth_header(test_student),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    payment = body["data"]
    assert payment["provider"] == "mock"
    assert payment["amount_xof"] == 2000
    # Mock provider auto-completes
    assert payment["status"] == "completed"
    assert payment["provider_tx_id"] is not None


@pytest.mark.asyncio
async def test_init_payment_creates_subscription(
    client: AsyncClient, test_student, test_student_profile, seed_plans
):
    basic_plan = seed_plans[1]

    # Init payment
    await client.post(
        "/api/v1/payments/init",
        json={"plan_id": str(basic_plan.id), "provider": "mock"},
        headers=auth_header(test_student),
    )

    # Check subscription created for the profile
    resp = await client.get("/api/v1/me/subscription", headers=auth_header(test_student))
    assert resp.status_code == 200
    sub = resp.json()["data"]
    assert sub is not None
    assert sub["status"] == "active"


@pytest.mark.asyncio
async def test_init_payment_with_explicit_profile(
    client: AsyncClient, test_parent, test_parent_profiles, seed_plans
):
    """Parent pays for a specific child profile."""
    basic_plan = seed_plans[1]
    child_profile = test_parent_profiles[0]

    resp = await client.post(
        "/api/v1/payments/init",
        json={
            "plan_id": str(basic_plan.id),
            "provider": "mock",
            "profile_id": str(child_profile.id),
        },
        headers=auth_header(test_parent),
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "completed"


@pytest.mark.asyncio
async def test_init_payment_nonexistent_plan(client: AsyncClient, test_student, test_student_profile):
    fake_id = str(uuid.uuid4())
    resp = await client.post(
        "/api/v1/payments/init",
        json={"plan_id": fake_id, "provider": "mock"},
        headers=auth_header(test_student),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_init_payment_unauthenticated(client: AsyncClient, seed_plans):
    resp = await client.post(
        "/api/v1/payments/init",
        json={"plan_id": str(seed_plans[0].id), "provider": "mock"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_init_payment_kkiapay(client: AsyncClient, test_student, test_student_profile, seed_plans):
    premium_plan = seed_plans[2]
    resp = await client.post(
        "/api/v1/payments/init",
        json={"plan_id": str(premium_plan.id), "provider": "kkiapay"},
        headers=auth_header(test_student),
    )
    assert resp.status_code == 200
    payment = resp.json()["data"]
    assert payment["provider"] == "kkiapay"
    assert payment["amount_xof"] == 5000
    # Non-mock providers stay pending
    assert payment["status"] == "pending"


# ── Payment webhook ───────────────────────────────────────


@pytest.mark.asyncio
async def test_payment_webhook_unknown_tx(client: AsyncClient):
    resp = await client.post(
        "/api/v1/payments/webhook/kkiapay",
        json={"transaction_id": "unknown_tx_123", "status": "success"},
    )
    assert resp.status_code == 200
    # Returns processed: False since payment not found
    assert resp.json()["data"]["processed"] is False


@pytest.mark.asyncio
async def test_payment_webhook_missing_tx_id(client: AsyncClient):
    resp = await client.post(
        "/api/v1/payments/webhook/fedapay",
        json={"status": "success"},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["processed"] is False
