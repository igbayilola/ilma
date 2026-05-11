"""Tests for the content editorial workflow (P1-2.15).

Service-level tests that create DB objects directly and exercise the
editorial state-machine logic defined in admin_content.py:

    DRAFT -> IN_REVIEW -> PUBLISHED -> ARCHIVED
                 |                         |
                 v                         v
               DRAFT  <------------------DRAFT

Covers: valid transitions, invalid transitions, audit trail
(ContentTransition), reviewer notes, status filtering, and lesson
transitions.
"""
import uuid

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.models.content import (
    ContentStatus,
    Domain,
    GradeLevel,
    MicroLesson,
    Question,
    QuestionType,
    Skill,
    Subject,
)
from app.models.content_audit import ContentTransition
from app.models.user import User

# ---------------------------------------------------------------------------
# Valid transitions map (mirrored from admin_content.py)
# ---------------------------------------------------------------------------
_VALID_TRANSITIONS = {
    ContentStatus.DRAFT: [ContentStatus.IN_REVIEW],
    ContentStatus.IN_REVIEW: [ContentStatus.PUBLISHED, ContentStatus.DRAFT],
    ContentStatus.PUBLISHED: [ContentStatus.ARCHIVED],
    ContentStatus.ARCHIVED: [ContentStatus.DRAFT],
}


# ---------------------------------------------------------------------------
# Helper: apply a transition (replicates endpoint logic without HTTP layer)
# ---------------------------------------------------------------------------
async def _apply_transition(
    db: AsyncSession,
    obj: Question | MicroLesson,
    target_status: ContentStatus,
    admin: User,
    reviewer_notes: str | None = None,
) -> None:
    """Apply a status transition to a Question or MicroLesson.

    Raises AppException on invalid transition, exactly like the endpoint.
    """
    allowed = _VALID_TRANSITIONS.get(obj.status, [])
    if target_status not in allowed:
        raise AppException(
            status_code=400,
            code="INVALID_TRANSITION",
            message=f"Transition {obj.status.value} -> {target_status.value} non autorisée",
        )

    from_status = obj.status.value
    obj.status = target_status
    if reviewer_notes:
        obj.reviewer_notes = reviewer_notes

    content_type = "question" if isinstance(obj, Question) else "lesson"
    db.add(
        ContentTransition(
            content_type=content_type,
            content_id=obj.id,
            from_status=from_status,
            to_status=target_status.value,
            transitioned_by=admin.id,
            reviewer_notes=reviewer_notes,
        )
    )
    await db.flush()


# ---------------------------------------------------------------------------
# Fixtures: minimal content hierarchy (GradeLevel -> Subject -> Domain -> Skill)
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def skill(db_session: AsyncSession) -> Skill:
    """Create the minimal hierarchy needed to attach questions/lessons."""
    grade = GradeLevel(id=uuid.uuid4(), name="CM2", slug="cm2", order=0)
    db_session.add(grade)
    await db_session.flush()

    subject = Subject(
        id=uuid.uuid4(),
        grade_level_id=grade.id,
        name="Mathématiques",
        slug="maths",
        order=0,
    )
    db_session.add(subject)
    await db_session.flush()

    domain = Domain(
        id=uuid.uuid4(),
        subject_id=subject.id,
        name="Numération",
        slug="numeration",
        order=0,
    )
    db_session.add(domain)
    await db_session.flush()

    skill = Skill(
        id=uuid.uuid4(),
        domain_id=domain.id,
        name="Entiers naturels",
        slug="entiers-naturels",
        order=0,
    )
    db_session.add(skill)
    await db_session.flush()
    return skill


@pytest_asyncio.fixture
async def draft_question(db_session: AsyncSession, skill: Skill) -> Question:
    """A question starting in DRAFT status."""
    q = Question(
        id=uuid.uuid4(),
        skill_id=skill.id,
        question_type=QuestionType.MCQ,
        text="Combien font 2 + 2 ?",
        choices=["3", "4", "5", "6"],
        correct_answer="4",
        status=ContentStatus.DRAFT,
    )
    db_session.add(q)
    await db_session.flush()
    return q


@pytest_asyncio.fixture
async def draft_lesson(db_session: AsyncSession, skill: Skill) -> MicroLesson:
    """A micro-lesson starting in DRAFT status."""
    lesson = MicroLesson(
        id=uuid.uuid4(),
        skill_id=skill.id,
        title="Les entiers naturels",
        content_html="<p>Un entier naturel est...</p>",
        status=ContentStatus.DRAFT,
    )
    db_session.add(lesson)
    await db_session.flush()
    return lesson


# ===================================================================
# 1. DRAFT -> IN_REVIEW
# ===================================================================
@pytest.mark.asyncio
async def test_draft_to_in_review(
    db_session: AsyncSession, draft_question: Question, test_admin: User
):
    await _apply_transition(db_session, draft_question, ContentStatus.IN_REVIEW, test_admin)
    assert draft_question.status == ContentStatus.IN_REVIEW


# ===================================================================
# 2. IN_REVIEW -> PUBLISHED
# ===================================================================
@pytest.mark.asyncio
async def test_in_review_to_published(
    db_session: AsyncSession, draft_question: Question, test_admin: User
):
    await _apply_transition(db_session, draft_question, ContentStatus.IN_REVIEW, test_admin)
    await _apply_transition(db_session, draft_question, ContentStatus.PUBLISHED, test_admin)
    assert draft_question.status == ContentStatus.PUBLISHED


# ===================================================================
# 3. IN_REVIEW -> DRAFT (returned with feedback)
# ===================================================================
@pytest.mark.asyncio
async def test_in_review_to_draft_with_feedback(
    db_session: AsyncSession, draft_question: Question, test_admin: User
):
    await _apply_transition(db_session, draft_question, ContentStatus.IN_REVIEW, test_admin)
    await _apply_transition(
        db_session,
        draft_question,
        ContentStatus.DRAFT,
        test_admin,
        reviewer_notes="Veuillez corriger l'explication.",
    )
    assert draft_question.status == ContentStatus.DRAFT
    assert draft_question.reviewer_notes == "Veuillez corriger l'explication."


# ===================================================================
# 4. PUBLISHED -> ARCHIVED
# ===================================================================
@pytest.mark.asyncio
async def test_published_to_archived(
    db_session: AsyncSession, draft_question: Question, test_admin: User
):
    await _apply_transition(db_session, draft_question, ContentStatus.IN_REVIEW, test_admin)
    await _apply_transition(db_session, draft_question, ContentStatus.PUBLISHED, test_admin)
    await _apply_transition(db_session, draft_question, ContentStatus.ARCHIVED, test_admin)
    assert draft_question.status == ContentStatus.ARCHIVED


# ===================================================================
# 5. ARCHIVED -> DRAFT (restore)
# ===================================================================
@pytest.mark.asyncio
async def test_archived_to_draft(
    db_session: AsyncSession, draft_question: Question, test_admin: User
):
    # Walk the full lifecycle: DRAFT -> IN_REVIEW -> PUBLISHED -> ARCHIVED -> DRAFT
    await _apply_transition(db_session, draft_question, ContentStatus.IN_REVIEW, test_admin)
    await _apply_transition(db_session, draft_question, ContentStatus.PUBLISHED, test_admin)
    await _apply_transition(db_session, draft_question, ContentStatus.ARCHIVED, test_admin)
    await _apply_transition(db_session, draft_question, ContentStatus.DRAFT, test_admin)
    assert draft_question.status == ContentStatus.DRAFT


# ===================================================================
# 6. Invalid transitions
# ===================================================================
@pytest.mark.asyncio
async def test_draft_to_published_is_invalid(
    db_session: AsyncSession, draft_question: Question, test_admin: User
):
    """DRAFT -> PUBLISHED must not be allowed (must go through IN_REVIEW)."""
    with pytest.raises(AppException) as exc_info:
        await _apply_transition(db_session, draft_question, ContentStatus.PUBLISHED, test_admin)
    assert exc_info.value.code == "INVALID_TRANSITION"
    # Status must remain unchanged
    assert draft_question.status == ContentStatus.DRAFT


@pytest.mark.asyncio
async def test_draft_to_archived_is_invalid(
    db_session: AsyncSession, draft_question: Question, test_admin: User
):
    """DRAFT -> ARCHIVED must not be allowed."""
    with pytest.raises(AppException) as exc_info:
        await _apply_transition(db_session, draft_question, ContentStatus.ARCHIVED, test_admin)
    assert exc_info.value.code == "INVALID_TRANSITION"
    assert draft_question.status == ContentStatus.DRAFT


@pytest.mark.asyncio
async def test_published_to_in_review_is_invalid(
    db_session: AsyncSession, draft_question: Question, test_admin: User
):
    """PUBLISHED -> IN_REVIEW must not be allowed."""
    await _apply_transition(db_session, draft_question, ContentStatus.IN_REVIEW, test_admin)
    await _apply_transition(db_session, draft_question, ContentStatus.PUBLISHED, test_admin)
    with pytest.raises(AppException) as exc_info:
        await _apply_transition(db_session, draft_question, ContentStatus.IN_REVIEW, test_admin)
    assert exc_info.value.code == "INVALID_TRANSITION"
    assert draft_question.status == ContentStatus.PUBLISHED


@pytest.mark.asyncio
async def test_archived_to_published_is_invalid(
    db_session: AsyncSession, draft_question: Question, test_admin: User
):
    """ARCHIVED -> PUBLISHED must not be allowed (must restore to DRAFT first)."""
    await _apply_transition(db_session, draft_question, ContentStatus.IN_REVIEW, test_admin)
    await _apply_transition(db_session, draft_question, ContentStatus.PUBLISHED, test_admin)
    await _apply_transition(db_session, draft_question, ContentStatus.ARCHIVED, test_admin)
    with pytest.raises(AppException) as exc_info:
        await _apply_transition(db_session, draft_question, ContentStatus.PUBLISHED, test_admin)
    assert exc_info.value.code == "INVALID_TRANSITION"
    assert draft_question.status == ContentStatus.ARCHIVED


# ===================================================================
# 7. Audit trail (ContentTransition records)
# ===================================================================
@pytest.mark.asyncio
async def test_audit_trail_created_for_each_transition(
    db_session: AsyncSession, draft_question: Question, test_admin: User
):
    """Each successful transition must create a ContentTransition record."""
    # Perform 3 transitions: DRAFT -> IN_REVIEW -> PUBLISHED -> ARCHIVED
    await _apply_transition(db_session, draft_question, ContentStatus.IN_REVIEW, test_admin)
    await _apply_transition(db_session, draft_question, ContentStatus.PUBLISHED, test_admin)
    await _apply_transition(db_session, draft_question, ContentStatus.ARCHIVED, test_admin)

    result = await db_session.execute(
        select(ContentTransition)
        .where(ContentTransition.content_id == draft_question.id)
        .order_by(ContentTransition.created_at)
    )
    transitions = result.scalars().all()

    assert len(transitions) == 3

    # First transition
    assert transitions[0].from_status == "DRAFT"
    assert transitions[0].to_status == "IN_REVIEW"
    assert transitions[0].content_type == "question"
    assert transitions[0].transitioned_by == test_admin.id

    # Second transition
    assert transitions[1].from_status == "IN_REVIEW"
    assert transitions[1].to_status == "PUBLISHED"

    # Third transition
    assert transitions[2].from_status == "PUBLISHED"
    assert transitions[2].to_status == "ARCHIVED"


@pytest.mark.asyncio
async def test_failed_transition_does_not_create_audit_record(
    db_session: AsyncSession, draft_question: Question, test_admin: User
):
    """An invalid transition must NOT create a ContentTransition record."""
    with pytest.raises(AppException):
        await _apply_transition(db_session, draft_question, ContentStatus.PUBLISHED, test_admin)

    result = await db_session.execute(
        select(ContentTransition).where(ContentTransition.content_id == draft_question.id)
    )
    transitions = result.scalars().all()
    assert len(transitions) == 0


# ===================================================================
# 8. Reviewer notes
# ===================================================================
@pytest.mark.asyncio
async def test_reviewer_notes_stored_on_question_and_transition(
    db_session: AsyncSession, draft_question: Question, test_admin: User
):
    """reviewer_notes should be stored on both the question and the transition."""
    notes = "Bonne question, mais ajouter un indice."
    await _apply_transition(db_session, draft_question, ContentStatus.IN_REVIEW, test_admin)
    await _apply_transition(
        db_session, draft_question, ContentStatus.DRAFT, test_admin, reviewer_notes=notes
    )

    # Check question
    assert draft_question.reviewer_notes == notes

    # Check transition record
    result = await db_session.execute(
        select(ContentTransition)
        .where(
            ContentTransition.content_id == draft_question.id,
            ContentTransition.to_status == "DRAFT",
        )
    )
    transition = result.scalar_one()
    assert transition.reviewer_notes == notes


@pytest.mark.asyncio
async def test_reviewer_notes_not_overwritten_when_none(
    db_session: AsyncSession, draft_question: Question, test_admin: User
):
    """When reviewer_notes is None, existing notes on the object should be preserved."""
    notes = "Corriger le choix B."
    await _apply_transition(db_session, draft_question, ContentStatus.IN_REVIEW, test_admin)
    await _apply_transition(
        db_session, draft_question, ContentStatus.DRAFT, test_admin, reviewer_notes=notes
    )
    assert draft_question.reviewer_notes == notes

    # Transition again without notes — existing notes should remain
    await _apply_transition(db_session, draft_question, ContentStatus.IN_REVIEW, test_admin)
    assert draft_question.reviewer_notes == notes


# ===================================================================
# 9. Status filtering (by-status query)
# ===================================================================
@pytest.mark.asyncio
async def test_filter_questions_by_status(
    db_session: AsyncSession, skill: Skill, test_admin: User
):
    """Filtering by status returns only questions in that status."""
    # Create 3 questions in different statuses
    q_draft = Question(
        id=uuid.uuid4(),
        skill_id=skill.id,
        question_type=QuestionType.MCQ,
        text="Question draft",
        choices=["a", "b"],
        correct_answer="a",
        status=ContentStatus.DRAFT,
    )
    q_review = Question(
        id=uuid.uuid4(),
        skill_id=skill.id,
        question_type=QuestionType.MCQ,
        text="Question en revue",
        choices=["a", "b"],
        correct_answer="b",
        status=ContentStatus.IN_REVIEW,
    )
    q_published = Question(
        id=uuid.uuid4(),
        skill_id=skill.id,
        question_type=QuestionType.TRUE_FALSE,
        text="Question publiée",
        choices=["Vrai", "Faux"],
        correct_answer="Vrai",
        status=ContentStatus.PUBLISHED,
    )
    db_session.add_all([q_draft, q_review, q_published])
    await db_session.flush()

    # Query for IN_REVIEW
    result = await db_session.execute(
        select(Question).where(Question.status == ContentStatus.IN_REVIEW)
    )
    in_review_questions = result.scalars().all()
    assert len(in_review_questions) == 1
    assert in_review_questions[0].id == q_review.id

    # Query for DRAFT
    result = await db_session.execute(
        select(Question).where(Question.status == ContentStatus.DRAFT)
    )
    draft_questions = result.scalars().all()
    assert len(draft_questions) == 1
    assert draft_questions[0].id == q_draft.id

    # Query for PUBLISHED
    result = await db_session.execute(
        select(Question).where(Question.status == ContentStatus.PUBLISHED)
    )
    published_questions = result.scalars().all()
    assert len(published_questions) == 1
    assert published_questions[0].id == q_published.id

    # Query for ARCHIVED — should be empty
    result = await db_session.execute(
        select(Question).where(Question.status == ContentStatus.ARCHIVED)
    )
    archived_questions = result.scalars().all()
    assert len(archived_questions) == 0


# ===================================================================
# 10. Lesson transitions (same workflow for MicroLesson)
# ===================================================================
@pytest.mark.asyncio
async def test_lesson_full_lifecycle(
    db_session: AsyncSession, draft_lesson: MicroLesson, test_admin: User
):
    """MicroLesson follows the exact same state machine as Question."""
    # DRAFT -> IN_REVIEW
    await _apply_transition(db_session, draft_lesson, ContentStatus.IN_REVIEW, test_admin)
    assert draft_lesson.status == ContentStatus.IN_REVIEW

    # IN_REVIEW -> PUBLISHED
    await _apply_transition(db_session, draft_lesson, ContentStatus.PUBLISHED, test_admin)
    assert draft_lesson.status == ContentStatus.PUBLISHED

    # PUBLISHED -> ARCHIVED
    await _apply_transition(db_session, draft_lesson, ContentStatus.ARCHIVED, test_admin)
    assert draft_lesson.status == ContentStatus.ARCHIVED

    # ARCHIVED -> DRAFT (restore)
    await _apply_transition(db_session, draft_lesson, ContentStatus.DRAFT, test_admin)
    assert draft_lesson.status == ContentStatus.DRAFT


@pytest.mark.asyncio
async def test_lesson_invalid_transition(
    db_session: AsyncSession, draft_lesson: MicroLesson, test_admin: User
):
    """Invalid transitions are rejected for lessons too."""
    with pytest.raises(AppException) as exc_info:
        await _apply_transition(db_session, draft_lesson, ContentStatus.PUBLISHED, test_admin)
    assert exc_info.value.code == "INVALID_TRANSITION"
    assert draft_lesson.status == ContentStatus.DRAFT


@pytest.mark.asyncio
async def test_lesson_audit_trail(
    db_session: AsyncSession, draft_lesson: MicroLesson, test_admin: User
):
    """Lesson transitions produce ContentTransition records with content_type='lesson'."""
    await _apply_transition(db_session, draft_lesson, ContentStatus.IN_REVIEW, test_admin)
    await _apply_transition(
        db_session,
        draft_lesson,
        ContentStatus.DRAFT,
        test_admin,
        reviewer_notes="Ajouter un résumé.",
    )

    result = await db_session.execute(
        select(ContentTransition)
        .where(ContentTransition.content_id == draft_lesson.id)
        .order_by(ContentTransition.created_at)
    )
    transitions = result.scalars().all()

    assert len(transitions) == 2
    assert all(t.content_type == "lesson" for t in transitions)
    assert transitions[0].from_status == "DRAFT"
    assert transitions[0].to_status == "IN_REVIEW"
    assert transitions[1].from_status == "IN_REVIEW"
    assert transitions[1].to_status == "DRAFT"
    assert transitions[1].reviewer_notes == "Ajouter un résumé."


@pytest.mark.asyncio
async def test_lesson_reviewer_notes(
    db_session: AsyncSession, draft_lesson: MicroLesson, test_admin: User
):
    """Reviewer notes are stored on the lesson object when returned."""
    await _apply_transition(db_session, draft_lesson, ContentStatus.IN_REVIEW, test_admin)
    await _apply_transition(
        db_session,
        draft_lesson,
        ContentStatus.DRAFT,
        test_admin,
        reviewer_notes="Le contenu HTML est mal formaté.",
    )
    assert draft_lesson.reviewer_notes == "Le contenu HTML est mal formaté."
