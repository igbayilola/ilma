"""Custom middleware: request_id, structured logging, security headers, maintenance mode."""
import logging
import time
import uuid

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.schemas.response import err

logger = logging.getLogger("ilma")


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Inject X-Request-ID into every request/response."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class AccessLogMiddleware(BaseHTTPMiddleware):
    """Structured access logging."""

    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = round((time.time() - start) * 1000, 2)
        logger.info(
            "request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": duration,
                "request_id": getattr(request.state, "request_id", "-"),
            },
        )
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to every response."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response


class MaintenanceModeMiddleware(BaseHTTPMiddleware):
    """Return 503 when maintenance mode is enabled."""

    def __init__(self, app, enabled: bool = False):
        super().__init__(app)
        self.enabled = enabled

    async def dispatch(self, request: Request, call_next):
        if self.enabled and not request.url.path.startswith("/api/v1/health"):
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=503,
                content=err(
                    code="MAINTENANCE",
                    message="ILMA est en maintenance. Veuillez réessayer plus tard.",
                ),
            )
        return await call_next(request)


def register_middleware(app: FastAPI) -> None:
    """Register all middleware in correct order (outermost first)."""
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(AccessLogMiddleware)
    app.add_middleware(RequestIdMiddleware)
