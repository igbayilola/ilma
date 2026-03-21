import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.middleware import register_middleware
from app.schemas.response import ok
from app.tasks.scheduler import setup_scheduler, start_scheduler, stop_scheduler

# Structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: seed badges + start notification scheduler
    if not os.environ.get("TESTING"):
        from app.db.session import AsyncSessionLocal
        from app.services.badge_service import badge_service

        async with AsyncSessionLocal() as db:
            try:
                await badge_service.seed_badges(db)
                await db.commit()
            except Exception:
                logging.getLogger(__name__).warning("Badge seeding failed", exc_info=True)

        setup_scheduler()
        start_scheduler()
    yield
    # Shutdown: stop the scheduler gracefully
    if not os.environ.get("TESTING"):
        stop_scheduler()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Exception handlers (response envelope)
register_exception_handlers(app)

# Custom middleware (security headers, access log, request_id)
register_middleware(app)

# CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/", tags=["Root"])
async def read_root():
    return ok(message=f"Welcome to {settings.PROJECT_NAME}")


app.include_router(api_router, prefix=settings.API_V1_STR)
