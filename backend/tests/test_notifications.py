"""Notification endpoint tests."""
import uuid
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationChannel, NotificationType
from app.services.notification_service import notification_service
from tests.conftest import auth_header


@pytest.fixture
async def seed_notifications(db_session: AsyncSession, test_student):
    """Create sample notifications for the test student."""
    notifs = []
    notif_data = [
        ("Bravo !", "Tu as gagne un badge", NotificationType.BADGE_EARNED, False),
        ("Rappel", "Tu n'as pas joue depuis 3 jours", NotificationType.INACTIVITY, False),
        ("Rapport", "Ton rapport hebdomadaire est pret", NotificationType.WEEKLY_REPORT, True),
    ]
    for title, body, ntype, is_read in notif_data:
        n = Notification(
            id=uuid.uuid4(),
            user_id=test_student.id,
            type=ntype,
            channel=NotificationChannel.IN_APP,
            title=title,
            body=body,
            is_read=is_read,
            read_at=datetime.now(timezone.utc) if is_read else None,
        )
        db_session.add(n)
        notifs.append(n)
    await db_session.flush()
    return notifs


# ── Notification listing ──────────────────────────────────


@pytest.mark.asyncio
async def test_list_notifications(client: AsyncClient, test_student, seed_notifications):
    resp = await client.get(
        "/api/v1/notifications", headers=auth_header(test_student)
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    notifs = body["data"]
    assert len(notifs) == 3


@pytest.mark.asyncio
async def test_list_notifications_unread_only(
    client: AsyncClient, test_student, seed_notifications
):
    resp = await client.get(
        "/api/v1/notifications?unread_only=true",
        headers=auth_header(test_student),
    )
    assert resp.status_code == 200
    notifs = resp.json()["data"]
    assert len(notifs) == 2  # Only the 2 unread ones
    for n in notifs:
        assert n["is_read"] is False


@pytest.mark.asyncio
async def test_list_notifications_with_limit(
    client: AsyncClient, test_student, seed_notifications
):
    resp = await client.get(
        "/api/v1/notifications?limit=1",
        headers=auth_header(test_student),
    )
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1


@pytest.mark.asyncio
async def test_list_notifications_empty(client: AsyncClient, test_student):
    resp = await client.get(
        "/api/v1/notifications", headers=auth_header(test_student)
    )
    assert resp.status_code == 200
    assert resp.json()["data"] == []


@pytest.mark.asyncio
async def test_list_notifications_unauthenticated(client: AsyncClient):
    resp = await client.get("/api/v1/notifications")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_notification_structure(
    client: AsyncClient, test_student, seed_notifications
):
    resp = await client.get(
        "/api/v1/notifications", headers=auth_header(test_student)
    )
    n = resp.json()["data"][0]
    assert "id" in n
    assert "type" in n
    assert "channel" in n
    assert "title" in n
    assert "body" in n
    assert "is_read" in n
    assert "created_at" in n


# ── Mark single notification as read ──────────────────────


@pytest.mark.asyncio
async def test_mark_read(client: AsyncClient, test_student, seed_notifications):
    unread_notif = seed_notifications[0]  # First one is unread
    resp = await client.post(
        f"/api/v1/notifications/{unread_notif.id}/read",
        headers=auth_header(test_student),
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "Notification marquée comme lue"


@pytest.mark.asyncio
async def test_mark_read_nonexistent(client: AsyncClient, test_student):
    fake_id = uuid.uuid4()
    resp = await client.post(
        f"/api/v1/notifications/{fake_id}/read",
        headers=auth_header(test_student),
    )
    # Should still return 200 (graceful handling)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_mark_read_other_users_notification(
    client: AsyncClient, test_parent, test_student, seed_notifications
):
    """A parent cannot mark a student's notification as read."""
    notif = seed_notifications[0]
    resp = await client.post(
        f"/api/v1/notifications/{notif.id}/read",
        headers=auth_header(test_parent),
    )
    # mark_read filters by user_id, so it won't find it — returns 200 but does nothing
    assert resp.status_code == 200


# ── Mark all as read ──────────────────────────────────────


@pytest.mark.asyncio
async def test_mark_all_read(client: AsyncClient, test_student, seed_notifications):
    resp = await client.post(
        "/api/v1/notifications/read-all",
        headers=auth_header(test_student),
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["marked"] == 2  # 2 were unread

    # Verify all are now read
    resp2 = await client.get(
        "/api/v1/notifications?unread_only=true",
        headers=auth_header(test_student),
    )
    assert len(resp2.json()["data"]) == 0


@pytest.mark.asyncio
async def test_mark_all_read_when_none_unread(client: AsyncClient, test_student):
    resp = await client.post(
        "/api/v1/notifications/read-all",
        headers=auth_header(test_student),
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["marked"] == 0


# ── Notification service direct tests ─────────────────────


@pytest.mark.asyncio
async def test_notification_service_create(db_session: AsyncSession, test_student):
    notif = await notification_service.create(
        db_session,
        user_id=test_student.id,
        type=NotificationType.SYSTEM,
        title="Test direct",
        body="Created via service",
    )
    assert notif.id is not None
    assert notif.title == "Test direct"
    assert notif.is_read is False


@pytest.mark.asyncio
async def test_notification_service_list(db_session: AsyncSession, test_student):
    # Create two notifications
    await notification_service.create(
        db_session,
        user_id=test_student.id,
        type=NotificationType.BADGE_EARNED,
        title="Badge 1",
    )
    await notification_service.create(
        db_session,
        user_id=test_student.id,
        type=NotificationType.GOAL_REACHED,
        title="Objectif atteint",
    )

    notifs = await notification_service.list_user_notifications(
        db_session, test_student.id
    )
    assert len(notifs) == 2


@pytest.mark.asyncio
async def test_notification_service_mark_read(db_session: AsyncSession, test_student):
    notif = await notification_service.create(
        db_session,
        user_id=test_student.id,
        type=NotificationType.SUBSCRIPTION,
        title="Abonnement renouvele",
    )
    result = await notification_service.mark_read(db_session, notif.id, test_student.id)
    assert result is True

    # Mark non-existent
    result2 = await notification_service.mark_read(db_session, uuid.uuid4(), test_student.id)
    assert result2 is False
