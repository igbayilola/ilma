"""Diagnostic onboarding endpoints."""
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_active_profile
from app.db.session import get_db_session
from app.models.profile import Profile
from app.schemas.response import ok
from app.services.diagnostic_service import get_diagnostic_questions, submit_diagnostic

router = APIRouter(prefix="/diagnostic", tags=["Diagnostic"])


class DiagnosticAnswer(BaseModel):
    question_id: str
    answer: Any


class DiagnosticSubmitRequest(BaseModel):
    answers: list[DiagnosticAnswer]


@router.get("/questions")
async def list_diagnostic_questions(
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    """Return 8 MCQ across the profile's top CEP domains. Empty list if already completed."""
    questions = await get_diagnostic_questions(db, profile)
    return ok(data={
        "completed_at": profile.diagnostic_completed_at.isoformat() if profile.diagnostic_completed_at else None,
        "questions": questions,
    })


@router.post("/submit", status_code=201)
async def submit(
    body: DiagnosticSubmitRequest,
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    """Grade answers, seed Progress, set diagnostic_completed_at."""
    payload = [{"question_id": a.question_id, "answer": a.answer} for a in body.answers]
    summary = await submit_diagnostic(db, profile, payload)
    await db.commit()
    return ok(data=summary, message="Diagnostic enregistré")
