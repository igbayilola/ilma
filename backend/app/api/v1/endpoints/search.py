"""Full-text search endpoint."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.response import ok
from app.services.search_service import search_service

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("")
async def search(
    q: str = Query(..., min_length=2, max_length=200),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(get_current_user),
):
    """Search skills, questions, domains, and lessons by text similarity."""
    results = await search_service.search(db, q, limit=limit)
    return ok(data=results)
