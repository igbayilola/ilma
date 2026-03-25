"""Mock exam (Examen Blanc) endpoints for CEP preparation."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_active_profile
from app.db.session import get_db_session
from app.models.profile import Profile
from app.schemas.response import ok
from app.services.exam_service import exam_service

router = APIRouter(prefix="/exams", tags=["Exams"])


class StartExamRequest(BaseModel):
    mock_exam_id: UUID


class SubmitAnswerRequest(BaseModel):
    # QCM-format fields
    question_id: UUID | None = None
    answer: object
    time_seconds: int | None = None
    # CEP-format fields
    item_number: int | None = None
    sub_label: str | None = None


@router.get("")
async def list_exams(
    grade_level_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db_session),
):
    """List available mock exams, optionally filtered by grade level."""
    exams = await exam_service.list_exams(db, grade_level_id=grade_level_id)
    return ok(data=exams)


@router.post("/start", status_code=201)
async def start_exam(
    body: StartExamRequest,
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    """Start an exam session. Checks paywall (1 free per subject, then premium)."""
    result = await exam_service.start_exam(db, profile, body.mock_exam_id)
    await db.commit()
    return ok(data=result)


@router.post("/sessions/{session_id}/answer")
async def submit_answer(
    session_id: UUID,
    body: SubmitAnswerRequest,
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    """Submit an answer for a question in an exam session."""
    result = await exam_service.submit_answer(
        db,
        session_id,
        profile.id,
        question_id=body.question_id,
        answer=body.answer,
        time_seconds=body.time_seconds,
        item_number=body.item_number,
        sub_label=body.sub_label,
    )
    await db.commit()
    return ok(data=result)


@router.post("/sessions/{session_id}/complete")
async def complete_exam(
    session_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    """Finish an exam and calculate scores."""
    result = await exam_service.complete_exam(db, session_id, profile.id)
    await db.commit()
    return ok(data=result)


@router.get("/sessions/{session_id}")
async def get_exam_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    """Get exam session details with correction."""
    result = await exam_service.get_exam_correction(db, session_id, profile.id)
    return ok(data=result)


@router.get("/history")
async def get_exam_history(
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    """Get exam history for the current profile."""
    history = await exam_service.get_exam_history(db, profile.id)
    return ok(data=history)
