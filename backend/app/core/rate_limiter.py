"""Redis-backed rate limiter middleware.

Uses a sliding-window counter per (client_key, route_group).
Falls back to no limiting if Redis is unavailable (fail-open).

Route groups and their limits:
  auth     — /auth/login, /auth/register, /auth/otp/*    → 10 req / 60 s
  attempt  — /sessions/*/attempt                          → 30 req / 60 s
  session  — /sessions/start                              → 10 req / 60 s
  search   — /search                                      → 20 req / 60 s
  default  — everything else                              → 60 req / 60 s
"""
import logging
import time

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.schemas.response import err

logger = logging.getLogger(__name__)

# (prefix, method_filter, label, max_requests, window_seconds)
_RULES: list[tuple[str, str | None, str, int, int]] = [
    ("/api/v1/auth/otp",       "POST", "auth",    10, 60),
    ("/api/v1/auth/login",     "POST", "auth",    10, 60),
    ("/api/v1/auth/register",  "POST", "auth",    10, 60),
    ("/api/v1/sessions/start", "POST", "session", 10, 60),
    ("/api/v1/search",         "GET",  "search",  20, 60),
]

# Attempt routes are matched by pattern (path contains /attempt)
_ATTEMPT_LIMIT = 30
_ATTEMPT_WINDOW = 60

_DEFAULT_LIMIT = 60
_DEFAULT_WINDOW = 60


def _match_rule(path: str, method: str) -> tuple[str, int, int]:
    """Return (label, max_requests, window_seconds) for the given path."""
    for prefix, method_filter, label, limit, window in _RULES:
        if path.startswith(prefix) and (method_filter is None or method == method_filter):
            return label, limit, window

    if "/attempt" in path and method == "POST":
        return "attempt", _ATTEMPT_LIMIT, _ATTEMPT_WINDOW

    return "default", _DEFAULT_LIMIT, _DEFAULT_WINDOW


def _get_client_key(request: Request) -> str:
    """Best-effort client identifier: user_id from JWT (if present) or IP."""
    # Try to extract user id from Authorization header without full decode
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer "):
        # Use a hash of the token's last segment as a stable per-user key
        token_tail = auth.rsplit(".", 1)[-1][:16]
        return f"u:{token_tail}"
    # Fallback to IP
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return f"ip:{forwarded.split(',')[0].strip()}"
    client = request.client
    return f"ip:{client.host}" if client else "ip:unknown"


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


class RateLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method

        # Skip non-API paths and health checks
        if not path.startswith("/api/") or path.endswith("/health"):
            return await call_next(request)

        label, max_req, window = _match_rule(path, method)

        # Skip rate limiting for the permissive default bucket on GET/HEAD
        if label == "default" and method in ("GET", "HEAD", "OPTIONS"):
            return await call_next(request)

        r = _get_redis()
        if not r:
            # Redis unavailable → fail open
            return await call_next(request)

        client_key = _get_client_key(request)
        redis_key = f"rl:{label}:{client_key}"

        try:
            now = time.time()
            pipe = r.pipeline()
            # Remove entries outside the window
            pipe.zremrangebyscore(redis_key, 0, now - window)
            # Add current request
            pipe.zadd(redis_key, {str(now): now})
            # Count entries in window
            pipe.zcard(redis_key)
            # Set TTL to auto-cleanup
            pipe.expire(redis_key, window + 1)
            results = await pipe.execute()
            count = results[2]
            await r.aclose()
        except Exception:
            # Redis error → fail open
            logger.debug("Rate limiter Redis error", exc_info=True)
            return await call_next(request)

        if count > max_req:
            retry_after = window
            return JSONResponse(
                status_code=429,
                content=err(
                    code="RATE_LIMITED",
                    message="Trop de requêtes. Réessaye dans quelques instants.",
                ),
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(max_req),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(now + window)),
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(max_req)
        response.headers["X-RateLimit-Remaining"] = str(max(0, max_req - count))
        return response
