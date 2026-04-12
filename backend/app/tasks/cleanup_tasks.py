"""Scheduled cleanup tasks: profile purge (30-day grace) + audit log retention (90 days)."""
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select

from app.db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def _purge_expired_profiles() -> None:
    """Hard-delete profiles past their 30-day grace period."""
    async with AsyncSessionLocal() as db:
        try:
            from app.models.profile import Profile

            now = datetime.now(timezone.utc)
            result = await db.execute(
                select(Profile).where(
                    Profile.is_active.is_(False),
                    Profile.scheduled_purge_at.isnot(None),
                    Profile.scheduled_purge_at <= now,
                )
            )
            profiles = result.scalars().all()

            for profile in profiles:
                logger.info("[Cleanup] Purging profile %s (scheduled_purge_at=%s)", profile.id, profile.scheduled_purge_at)
                await db.delete(profile)

            await db.commit()
            if profiles:
                logger.info("[Cleanup] Purged %d expired profiles", len(profiles))
        except Exception:
            await db.rollback()
            logger.exception("[Cleanup] Failed to purge expired profiles")


async def _cleanup_old_audit_logs() -> None:
    """Delete audit log entries older than 90 days."""
    async with AsyncSessionLocal() as db:
        try:
            from app.models.audit import AuditLog

            cutoff = datetime.now(timezone.utc) - timedelta(days=90)
            result = await db.execute(
                delete(AuditLog).where(AuditLog.created_at < cutoff)
            )
            await db.commit()
            if result.rowcount:
                logger.info("[Cleanup] Deleted %d audit logs older than 90 days", result.rowcount)
        except Exception:
            await db.rollback()
            logger.exception("[Cleanup] Failed to cleanup audit logs")
