"""Redis cache layer for content endpoints.

Usage in endpoints:
    result = await content_cache.get_or_set("subjects:cm2", 300, lambda: fetch_from_db())

Invalidation (called from admin_content after any write):
    await content_cache.invalidate_all()
"""
import json
import logging
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)

_PREFIX = "content:"
_DEFAULT_TTL = 300  # 5 minutes


def _get_redis():
    try:
        import redis.asyncio as aioredis

        from app.core.config import settings
        return aioredis.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
            decode_responses=True,
        )
    except Exception:
        return None


async def get_or_set(
    key: str,
    factory: Callable[[], Awaitable[Any]],
    ttl: int = _DEFAULT_TTL,
) -> Any:
    """Return cached value or call factory, cache result, and return it.

    Falls back to calling factory directly if Redis is unavailable.
    """
    redis = _get_redis()
    full_key = f"{_PREFIX}{key}"

    # Try cache hit
    if redis:
        try:
            cached = await redis.get(full_key)
            if cached is not None:
                await redis.aclose()
                return json.loads(cached)
        except Exception:
            logger.debug("Cache miss for %s", full_key)
        finally:
            try:
                await redis.aclose()
            except Exception:
                pass

    # Cache miss — call factory
    result = await factory()

    # Store in cache (best-effort)
    if redis:
        try:
            redis = _get_redis()
            if redis:
                await redis.set(full_key, json.dumps(result, default=str), ex=ttl)
                await redis.aclose()
        except Exception:
            logger.debug("Cache set failed for %s", full_key)

    return result


async def invalidate_all() -> int:
    """Delete all content cache keys. Returns count of deleted keys."""
    redis = _get_redis()
    if not redis:
        return 0
    try:
        cursor = b"0"
        deleted = 0
        while True:
            cursor, keys = await redis.scan(cursor=cursor, match=f"{_PREFIX}*", count=200)
            if keys:
                deleted += await redis.delete(*keys)
            if cursor == 0:
                break
        await redis.aclose()
        logger.info("Content cache invalidated: %d keys", deleted)
        return deleted
    except Exception:
        logger.debug("Cache invalidation failed", exc_info=True)
        return 0
