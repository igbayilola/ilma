import time

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db_session
from app.schemas.response import ok
from app.services.config_service import config_service

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Check API and services health")
async def health_check(
    db_session: AsyncSession = Depends(get_db_session),
):
    start_time = time.time()

    db_status = "ok"
    redis_status = "ok"
    db_error = None
    redis_error = None

    try:
        await db_session.execute(text("SELECT 1"))
    except Exception as e:
        db_status = "error"
        db_error = str(e)

    # Redis check — optional, graceful degradation
    try:
        import redis.asyncio as aioredis

        r = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
        await r.ping()
        await r.aclose()
    except Exception as e:
        redis_status = "unavailable"
        redis_error = str(e)

    duration = time.time() - start_time

    return ok(
        data={
            "status": "ok" if db_status == "ok" else "degraded",
            "duration_ms": round(duration * 1000, 2),
            "services": {
                "database": {"status": db_status, "error": db_error},
                "redis": {"status": redis_status, "error": redis_error},
            },
        }
    )


@router.get("/version", summary="Get API version")
async def version():
    return ok(data={"version": "0.1.0", "project": settings.PROJECT_NAME})


@router.get("/config/public", summary="Get public configuration for frontend")
async def get_public_config(
    db: AsyncSession = Depends(get_db_session),
):
    data = await config_service.get_public_config(db)
    return ok(data=data)
