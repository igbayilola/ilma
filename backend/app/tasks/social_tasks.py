"""CRON tasks for social features."""
import logging

logger = logging.getLogger(__name__)


async def _expire_challenges() -> None:
    """Expire pending challenges past their deadline."""
    from app.db.session import AsyncSessionLocal
    from app.services.social_service import social_service

    async with AsyncSessionLocal() as db:
        try:
            count = await social_service.expire_old_challenges(db)
            await db.commit()
            if count:
                logger.info("Expired %d challenges", count)
        except Exception:
            logger.warning("Failed to expire challenges", exc_info=True)
