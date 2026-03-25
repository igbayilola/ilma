"""Dynamic configuration service with Redis cache + DB + defaults fallback."""
import json
import logging
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_config import AppConfig

logger = logging.getLogger("sitou.config")

CACHE_TTL = 300  # 5 minutes
CACHE_PREFIX = "sitou:config:"

# Ultimate fallback defaults if both Redis and DB are unavailable
DEFAULTS: dict[str, Any] = {
    "freemium_daily_limit": 5,
    "smart_score_decay_rate": 0.05,
    "smart_score_streak_bonus": 0.02,
    "smart_score_max": 100,
    "min_attempt_time_seconds": 2,
    "badge_streak_3_threshold": 3,
    "badge_streak_10_threshold": 10,
    "badge_mastery_threshold": 90,
    "maintenance_mode": False,
    "registration_open": True,
    "min_app_version": "1.0.0",
    "promo_code_active": "",
    "monthly_price_xof": 2500,
    "payment_providers": ["kkiapay", "fedapay"],
    "allowed_phone_prefixes": ["90", "91", "92", "93", "94", "95", "96", "97"],
}

# Keys safe to expose publicly (no auth required)
PUBLIC_KEYS = {
    "freemium_daily_limit",
    "maintenance_mode",
    "registration_open",
    "min_app_version",
    "payment_providers",
    "allowed_phone_prefixes",
    "monthly_price_xof",
}


def _get_redis():
    """Get a Redis client, returns None if unavailable."""
    try:
        import redis.asyncio as aioredis
        from app.core.config import settings
        return aioredis.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
            decode_responses=True,
        )
    except Exception:
        return None


def _deserialize(raw_value: Any) -> Any:
    """Deserialize a JSONB value from DB (already Python-native from SQLAlchemy)."""
    return raw_value


class ConfigService:
    async def get(self, db: AsyncSession, key: str) -> Any:
        """Get a config value: Redis → DB → DEFAULTS (3-tier fallback)."""
        # Tier 1: Redis cache
        redis = _get_redis()
        if redis:
            try:
                cached = await redis.get(f"{CACHE_PREFIX}{key}")
                if cached is not None:
                    return json.loads(cached)
            except Exception:
                logger.debug("Redis cache miss for %s", key)
            finally:
                try:
                    await redis.aclose()
                except Exception:
                    pass

        # Tier 2: Database
        try:
            result = await db.execute(
                select(AppConfig.value).where(AppConfig.key == key)
            )
            row = result.scalar_one_or_none()
            if row is not None:
                value = _deserialize(row)
                # Populate Redis cache
                await self._cache_set(key, value)
                return value
        except Exception:
            logger.warning("DB read failed for config key %s", key)

        # Tier 3: Hardcoded defaults
        return DEFAULTS.get(key)

    async def get_all(self, db: AsyncSession, category: str | None = None) -> dict[str, Any]:
        """Get all config values, optionally filtered by category."""
        query = select(AppConfig)
        if category:
            query = query.where(AppConfig.category == category)

        try:
            result = await db.execute(query)
            configs = result.scalars().all()
            return {
                c.key: {
                    "value": _deserialize(c.value),
                    "category": c.category,
                    "label": c.label,
                    "description": c.description,
                    "value_type": c.value_type.value if c.value_type else "string",
                }
                for c in configs
            }
        except Exception:
            logger.warning("DB read failed for get_all configs")
            return {k: {"value": v, "category": "default", "label": k, "description": "", "value_type": "string"} for k, v in DEFAULTS.items()}

    async def set(self, db: AsyncSession, key: str, value: Any) -> None:
        """Set a config value in DB and invalidate Redis cache."""
        result = await db.execute(select(AppConfig).where(AppConfig.key == key))
        config = result.scalar_one_or_none()

        if config:
            config.value = value
        else:
            config = AppConfig(key=key, value=value, category="custom", label=key)
            db.add(config)

        await db.flush()
        await self._cache_invalidate(key)

    async def set_bulk(self, db: AsyncSession, updates: dict[str, Any]) -> None:
        """Set multiple config values at once."""
        for key, value in updates.items():
            await self.set(db, key, value)

    async def get_public_config(self, db: AsyncSession) -> dict[str, Any]:
        """Get only the public (non-sensitive) configs for frontend consumption."""
        all_configs = await self.get_all(db)
        result = {}
        for key in PUBLIC_KEYS:
            if key in all_configs:
                result[key] = all_configs[key]["value"]
            elif key in DEFAULTS:
                result[key] = DEFAULTS[key]
        return result

    async def _cache_set(self, key: str, value: Any) -> None:
        """Store a value in Redis cache."""
        redis = _get_redis()
        if not redis:
            return
        try:
            await redis.set(f"{CACHE_PREFIX}{key}", json.dumps(value), ex=CACHE_TTL)
        except Exception:
            logger.debug("Failed to set Redis cache for %s", key)
        finally:
            try:
                await redis.aclose()
            except Exception:
                pass

    async def _cache_invalidate(self, key: str) -> None:
        """Remove a value from Redis cache."""
        redis = _get_redis()
        if not redis:
            return
        try:
            await redis.delete(f"{CACHE_PREFIX}{key}")
        except Exception:
            logger.debug("Failed to invalidate Redis cache for %s", key)
        finally:
            try:
                await redis.aclose()
            except Exception:
                pass


config_service = ConfigService()
