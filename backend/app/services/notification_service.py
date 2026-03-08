"""Notification service: multi-channel (in-app, SMS mock, push mock)."""
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationChannel, NotificationType


class NotificationProvider:
    """Base interface for notification providers."""
    async def send(self, to: str, title: str, body: str, data: dict | None = None) -> bool:
        raise NotImplementedError


class MockSMSProvider(NotificationProvider):
    async def send(self, to: str, title: str, body: str, data: dict | None = None) -> bool:
        print(f"[SMS MOCK] To: {to} | {title}: {body}")
        return True


class MockPushProvider(NotificationProvider):
    async def send(self, to: str, title: str, body: str, data: dict | None = None) -> bool:
        print(f"[PUSH MOCK] To: {to} | {title}: {body}")
        return True


class NotificationService:
    def __init__(self):
        self.sms_provider: NotificationProvider = MockSMSProvider()
        self.push_provider: NotificationProvider = MockPushProvider()

    async def create(
        self,
        db: AsyncSession,
        user_id: UUID,
        type: NotificationType,
        title: str,
        body: str | None = None,
        data: dict | None = None,
        channel: NotificationChannel = NotificationChannel.IN_APP,
    ) -> Notification:
        notif = Notification(
            user_id=user_id,
            type=type,
            channel=channel,
            title=title,
            body=body,
            data=data,
        )
        db.add(notif)
        await db.flush()

        # Dispatch to external channels
        if channel == NotificationChannel.SMS:
            await self.sms_provider.send(str(user_id), title, body or "")
        elif channel == NotificationChannel.PUSH:
            await self.push_provider.send(str(user_id), title, body or "")

        return notif

    async def list_user_notifications(
        self, db: AsyncSession, user_id: UUID, unread_only: bool = False, limit: int = 50
    ) -> list[Notification]:
        query = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            query = query.where(Notification.is_read.is_(False))
        query = query.order_by(Notification.created_at.desc()).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def mark_read(self, db: AsyncSession, notification_id: UUID, user_id: UUID) -> bool:
        result = await db.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
        )
        notif = result.scalar_one_or_none()
        if not notif:
            return False
        notif.is_read = True
        notif.read_at = datetime.now(timezone.utc)
        await db.flush()
        return True

    async def mark_all_read(self, db: AsyncSession, user_id: UUID) -> int:
        result = await db.execute(
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
            .values(is_read=True, read_at=datetime.now(timezone.utc))
        )
        await db.flush()
        return result.rowcount


notification_service = NotificationService()
