"""Notification service: multi-channel (in-app, SMS, push) with real + mock providers."""
import json
import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.notification import Notification, NotificationChannel, NotificationType
from app.models.push_subscription import PushSubscription

logger = logging.getLogger(__name__)


# ── Provider interface ────────────────────────────────────────


class NotificationProvider:
    """Base interface for notification providers."""

    async def send(self, to: str, title: str, body: str, data: dict | None = None) -> bool:
        raise NotImplementedError


# ── SMS Providers ─────────────────────────────────────────────


class MockSMSProvider(NotificationProvider):
    async def send(self, to: str, title: str, body: str, data: dict | None = None) -> bool:
        logger.info("[SMS MOCK] To: %s | %s: %s", to, title, body)
        return True


class TwilioSMSProvider(NotificationProvider):
    """Real Twilio SMS provider. Requires TWILIO_* env vars."""

    def __init__(self) -> None:
        try:
            from twilio.rest import Client  # type: ignore[import-untyped]

            self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            self.from_number = settings.TWILIO_FROM_NUMBER
            self.available = True
        except Exception:
            logger.warning("Twilio SDK not available, falling back to mock SMS")
            self.available = False
            self._fallback = MockSMSProvider()

    async def send(self, to: str, title: str, body: str, data: dict | None = None) -> bool:
        if not self.available:
            return await self._fallback.send(to, title, body, data)
        try:
            message = self.client.messages.create(
                body=f"{title}\n{body}",
                from_=self.from_number,
                to=to,
            )
            logger.info("[SMS Twilio] Sent to %s, SID=%s", to, message.sid)
            return True
        except Exception as e:
            logger.error("[SMS Twilio] Failed to send to %s: %s", to, e)
            return False


# ── Push Providers ────────────────────────────────────────────


class MockPushProvider(NotificationProvider):
    async def send(self, to: str, title: str, body: str, data: dict | None = None) -> bool:
        logger.info("[PUSH MOCK] To: %s | %s: %s", to, title, body)
        return True


class WebPushProvider(NotificationProvider):
    """Real Web Push provider using pywebpush with VAPID."""

    def __init__(self) -> None:
        try:
            from pywebpush import WebPushException, webpush  # type: ignore[import-untyped]
            self._webpush = webpush
            self._WebPushException = WebPushException
            self.available = True
        except ImportError:
            logger.warning("pywebpush not available, falling back to mock push")
            self.available = False
            self._fallback = MockPushProvider()

    async def send(self, to: str, title: str, body: str, data: dict | None = None) -> bool:
        """'to' is a JSON-encoded push subscription info dict."""
        if not self.available:
            return await self._fallback.send(to, title, body, data)
        try:
            subscription_info = json.loads(to)
            payload = json.dumps({"title": title, "body": body, **(data or {})})
            self._webpush(
                subscription_info=subscription_info,
                data=payload,
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": f"mailto:{settings.VAPID_CONTACT_EMAIL}"},
            )
            logger.info("[PUSH WebPush] Sent to endpoint %s", subscription_info.get("endpoint", "")[:60])
            return True
        except self._WebPushException as e:
            logger.error("[PUSH WebPush] Failed: %s", e)
            return False
        except Exception as e:
            logger.error("[PUSH WebPush] Unexpected error: %s", e)
            return False


# ── Factory ───────────────────────────────────────────────────


def _create_sms_provider() -> NotificationProvider:
    if settings.SMS_PROVIDER == "twilio" and settings.TWILIO_ACCOUNT_SID:
        return TwilioSMSProvider()
    return MockSMSProvider()


def _create_push_provider() -> NotificationProvider:
    if settings.PUSH_PROVIDER == "webpush" and settings.VAPID_PRIVATE_KEY:
        return WebPushProvider()
    return MockPushProvider()


# ── Service ───────────────────────────────────────────────────


class NotificationService:
    def __init__(self) -> None:
        self.sms_provider: NotificationProvider = _create_sms_provider()
        self.push_provider: NotificationProvider = _create_push_provider()

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
            status="pending",
        )
        db.add(notif)
        await db.flush()

        # Dispatch to external channels and track delivery
        now = datetime.now(timezone.utc)
        if channel == NotificationChannel.IN_APP:
            # In-app notifications are delivered immediately
            notif.status = "delivered"
            notif.sent_at = now
            notif.delivered_at = now
        elif channel == NotificationChannel.SMS:
            try:
                # Fetch user's phone number
                from app.models.user import User
                user_result = await db.execute(select(User.phone).where(User.id == user_id))
                phone = user_result.scalar_one_or_none()
                if not phone:
                    notif.status = "failed"
                    notif.error_message = "No phone number on file"
                    await db.flush()
                    return notif
                success = await self.sms_provider.send(phone, title, body or "")
                notif.sent_at = now
                if success:
                    notif.status = "sent"
                else:
                    notif.status = "failed"
                    notif.error_message = "SMS provider returned failure"
            except Exception as e:
                notif.status = "failed"
                notif.error_message = str(e)[:500]
                logger.error("[SMS] Failed to send to user %s: %s", user_id, e)
        elif channel == NotificationChannel.PUSH:
            try:
                # Look up all push subscriptions for this user
                subs_result = await db.execute(
                    select(PushSubscription).where(PushSubscription.user_id == user_id)
                )
                subscriptions = list(subs_result.scalars().all())
                if not subscriptions:
                    notif.status = "failed"
                    notif.error_message = "No push subscriptions found"
                else:
                    any_success = False
                    for sub in subscriptions:
                        sub_info = json.dumps({"endpoint": sub.endpoint, "keys": sub.keys_json})
                        success = await self.push_provider.send(
                            sub_info, title, body or "", data
                        )
                        if success:
                            any_success = True
                        else:
                            # Track failures — only remove after 3 consecutive failures
                            sub.fail_count = getattr(sub, "fail_count", 0) + 1
                            if sub.fail_count >= 3:
                                logger.info("[PUSH] Removing stale subscription %s after %d failures", sub.endpoint[:50], sub.fail_count)
                                await db.execute(
                                    delete(PushSubscription).where(PushSubscription.id == sub.id)
                                )
                    notif.sent_at = now
                    notif.status = "sent" if any_success else "failed"
                    if not any_success:
                        notif.error_message = "All push subscriptions failed"
            except Exception as e:
                notif.status = "failed"
                notif.error_message = str(e)[:500]
                logger.error("[PUSH] Failed to send to user %s: %s", user_id, e)

        await db.flush()
        return notif

    async def create_multi_channel(
        self,
        db: AsyncSession,
        user_id: UUID,
        type: NotificationType,
        title: str,
        body: str | None = None,
        data: dict | None = None,
        phone: str | None = None,
    ) -> Notification:
        """Create an in-app notification and optionally send via SMS/Push too."""
        notif = await self.create(db, user_id, type, title, body, data, NotificationChannel.IN_APP)

        # Also send push (tracked separately)
        await self.create(db, user_id, type, title, body, data, NotificationChannel.PUSH)

        # Also send SMS if phone number is available (tracked separately)
        if phone:
            await self.create(db, user_id, type, title, body, data, NotificationChannel.SMS)

        return notif

    async def count_today(self, db: AsyncSession, user_id: UUID) -> int:
        """Count notifications sent to a user today (for throttling)."""
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        result = await db.execute(
            select(func.count(Notification.id)).where(
                Notification.user_id == user_id,
                Notification.created_at >= today_start,
            )
        )
        return result.scalar() or 0

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
