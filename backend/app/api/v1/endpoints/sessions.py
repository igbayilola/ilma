"""Exercise session endpoints: start, next, attempt, complete."""
from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_active_profile
from app.core.exceptions import AppException
from app.db.session import get_db_session
from app.models.content import Question
from app.models.profile import Profile
from app.schemas.response import ok
from app.schemas.session import (
    AttemptOut,
    AttemptRequest,
    NextQuestionOut,
    SessionOut,
    SessionStartRequest,
)
from app.services.progress_service import progress_service
from app.services.session_service import session_service
from app.services.subscription_service import subscription_service


def _build_criteria_feedback(
    criteria: Dict[str, Any],
    student_answer: Any,
) -> List[Dict[str, Any]]:
    """Build C1/C2/C3 feedback for a contextual problem.

    Each criterion in the evaluation_criteria dict has:
        {
            "C1": {"label": "Interprétation", "description": "...", "guide": "..."},
            "C2": {"label": "Utilisation des outils", "description": "...", "guide": "..."},
            "C3": {"label": "Cohérence de la réponse", "description": "...", "guide": "..."}
        }

    Returns a list of feedback items for the frontend to display.
    """
    feedback = []
    for key in sorted(criteria.keys()):
        criterion = criteria[key]
        feedback.append({
            "code": key,
            "label": criterion.get("label", key),
            "description": criterion.get("description", ""),
            "guide": criterion.get("guide", ""),
        })
    return feedback


router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("/start", status_code=201)
async def start_session(
    body: SessionStartRequest,
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    # Enforce freemium daily limit
    allowed, remaining = await subscription_service.check_daily_limit(db, profile)
    if not allowed:
        raise AppException(
            status_code=403,
            code="DAILY_LIMIT_REACHED",
            message="Tu as atteint ta limite quotidienne d'exercices gratuits. Passe en Premium pour continuer !",
        )

    # Check prerequisites (non-blocking warning)
    from app.services.prerequisite_service import prerequisite_service
    prereq_check = await prerequisite_service.check_skill_prerequisites(db, profile.id, body.skill_id)

    session = await session_service.start_session(
        db, profile, body.skill_id, body.mode, micro_skill_id=body.micro_skill_id
    )
    await db.commit()

    data = SessionOut.model_validate(session).model_dump(mode="json")
    if not prereq_check["met"]:
        data["prerequisites_warning"] = prereq_check["prerequisites"]
    return ok(data=data)


@router.get("/{session_id}/next")
async def get_next_question(
    session_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    question = await session_service.get_next_question(db, session_id, profile)
    if not question:
        return ok(data=None, message="Plus de questions disponibles")
    return ok(
        data=NextQuestionOut(
            question_id=question.id,
            text=question.text,
            question_type=question.question_type.value,
            difficulty=question.difficulty.value,
            choices=question.choices,
            media_url=question.media_url,
            time_limit_seconds=question.time_limit_seconds,
            points=question.points,
            micro_skill_id=question.micro_skill_id,
            interactive_config=question.interactive_config,
            hints=question.hints,
        )
    )


@router.post("/{session_id}/attempt")
async def record_attempt(
    session_id: UUID,
    body: AttemptRequest,
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    attempt = await session_service.record_attempt(
        db,
        session_id,
        profile,
        body.question_id,
        body.client_event_id,
        body.answer,
        body.time_spent_seconds,
    )

    # Update progress (skill + micro-skill if applicable)
    q_result = await db.execute(select(Question).where(Question.id == body.question_id))
    question = q_result.scalar_one_or_none()
    if question and question.skill_id:
        await progress_service.update_progress_after_attempt(
            db, profile.id, question.skill_id, attempt.is_correct,
            micro_skill_id=question.micro_skill_id,
        )

    await db.commit()

    # Build enriched response with feedback for incorrect contextual problems
    from app.models.content import QuestionType
    base = AttemptOut.model_validate(attempt)
    feedback_data = base.model_dump(mode="json")
    feedback_data["explanation"] = question.explanation if question else None
    feedback_data["correct_answer"] = question.correct_answer if question else None

    if (
        question
        and not attempt.is_correct
        and question.question_type == QuestionType.CONTEXTUAL_PROBLEM
        and question.interactive_config
        and "evaluation_criteria" in question.interactive_config
    ):
        feedback_data["criteria_feedback"] = _build_criteria_feedback(
            question.interactive_config["evaluation_criteria"],
            body.answer,
        )

    return ok(data=feedback_data)


@router.post("/{session_id}/complete")
async def complete_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    profile: Profile = Depends(get_active_profile),
):
    session = await session_service.complete_session(db, session_id, profile)
    await db.commit()
    return ok(data=SessionOut.model_validate(session))
