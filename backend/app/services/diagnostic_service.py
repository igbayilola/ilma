"""Diagnostic onboarding service.

Picks 8 medium-difficulty MCQ questions across the most CEP-relevant active
domains of the profile's grade level, grades the submission, and bootstraps
the profile's Progress so the CEP predictor (cep_predictor.py) has signal
from minute 1.

Not adaptive (v1): a fixed set of 8 questions, one per top-cep_frequency
domain. Future iters can swap in IRT-lite reactive picking.
"""
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import (
    DifficultyLevel,
    Domain,
    MicroLesson,
    Question,
    QuestionType,
    Skill,
    Subject,
)
from app.models.profile import Profile
from app.models.progress import Progress

_NUM_QUESTIONS = 8


async def get_diagnostic_questions(db: AsyncSession, profile: Profile) -> list[dict]:
    """Return up to 8 MCQ questions spread across distinct CEP-relevant domains.

    Strategy: pick one MCQ per domain ordered by aggregate cep_frequency desc.
    Falls back to any MCQ if a domain has none of medium difficulty.
    """
    if profile.diagnostic_completed_at is not None:
        return []

    grade_level_id = profile.grade_level_id

    # Top domains by sum of skill.cep_frequency, scoped to the profile's grade.
    domain_q = (
        select(Domain.id, func.coalesce(func.sum(Skill.cep_frequency), 0).label("freq_sum"))
        .join(Skill, Skill.domain_id == Domain.id)
        .join(Subject, Subject.id == Domain.subject_id)
        .where(Domain.is_active.is_(True), Skill.is_active.is_(True))
    )
    if grade_level_id is not None:
        domain_q = domain_q.where(Subject.grade_level_id == grade_level_id)
    domain_q = domain_q.group_by(Domain.id).order_by(desc("freq_sum")).limit(_NUM_QUESTIONS)

    domain_ids = [row.id for row in (await db.execute(domain_q)).all()]

    out: list[dict] = []
    for did in domain_ids:
        q_stmt = (
            select(Question)
            .join(Skill, Skill.id == Question.skill_id)
            .where(
                Skill.domain_id == did,
                Question.is_active.is_(True),
                Question.question_type == QuestionType.MCQ,
                Question.difficulty == DifficultyLevel.MEDIUM,
            )
            .order_by(func.random())
            .limit(1)
        )
        q = (await db.execute(q_stmt)).scalar_one_or_none()
        if q is None:
            # fallback: any MCQ in that domain
            q_stmt = (
                select(Question)
                .join(Skill, Skill.id == Question.skill_id)
                .where(
                    Skill.domain_id == did,
                    Question.is_active.is_(True),
                    Question.question_type == QuestionType.MCQ,
                )
                .order_by(func.random())
                .limit(1)
            )
            q = (await db.execute(q_stmt)).scalar_one_or_none()
        if q is None:
            continue
        out.append({
            "question_id": str(q.id),
            "skill_id": str(q.skill_id),
            "domain_id": str(did),
            "text": q.text,
            "choices": q.choices or [],
            "difficulty": q.difficulty.value if q.difficulty else None,
        })

    return out


async def submit_diagnostic(
    db: AsyncSession,
    profile: Profile,
    answers: list[dict],
) -> dict:
    """Grade the submission, seed Progress rows, mark profile diagnostic_completed_at.

    answers: [{ "question_id": "...", "answer": "..." }]

    Returns per-skill and per-domain breakdowns + an aggregate accuracy.
    """
    if not answers:
        return {"per_domain": [], "overall_accuracy": 0.0, "questions_answered": 0}

    question_ids = [UUID(a["question_id"]) for a in answers]
    questions_rows = (
        await db.execute(
            select(Question, Skill.id.label("sid"), Skill.domain_id, Skill.name.label("skill_name"))
            .join(Skill, Skill.id == Question.skill_id)
            .where(Question.id.in_(question_ids))
        )
    ).all()
    by_qid = {row.Question.id: row for row in questions_rows}

    domain_agg: dict[UUID, dict] = {}
    overall_correct = 0
    total = 0

    for ans in answers:
        qid = UUID(ans["question_id"])
        row = by_qid.get(qid)
        if row is None:
            continue
        q = row.Question
        is_correct = str(ans.get("answer")) == str(q.correct_answer)
        total += 1
        if is_correct:
            overall_correct += 1

        # Bootstrap Progress for this skill (idempotent)
        existing = await db.execute(
            select(Progress).where(
                Progress.profile_id == profile.id,
                Progress.skill_id == row.sid,
            )
        )
        progress = existing.scalar_one_or_none()
        if progress is None:
            progress = Progress(
                profile_id=profile.id,
                skill_id=row.sid,
                smart_score=100.0 if is_correct else 0.0,
                total_attempts=1,
                correct_attempts=1 if is_correct else 0,
                streak=1 if is_correct else 0,
                best_streak=1 if is_correct else 0,
                last_attempt_at=datetime.now(timezone.utc),
            )
            db.add(progress)
        else:
            progress.total_attempts += 1
            if is_correct:
                progress.correct_attempts += 1
                progress.streak += 1
                if progress.streak > progress.best_streak:
                    progress.best_streak = progress.streak
            else:
                progress.streak = 0
            if progress.total_attempts > 0:
                progress.smart_score = progress.correct_attempts / progress.total_attempts * 100
            progress.last_attempt_at = datetime.now(timezone.utc)

        agg = domain_agg.setdefault(row.domain_id, {
            "domain_id": str(row.domain_id),
            "correct": 0,
            "total": 0,
        })
        agg["total"] += 1
        if is_correct:
            agg["correct"] += 1

    profile.diagnostic_completed_at = datetime.now(timezone.utc)
    await db.flush()

    per_domain = [
        {
            "domain_id": d["domain_id"],
            "correct": d["correct"],
            "total": d["total"],
            "accuracy": round(d["correct"] / d["total"], 2) if d["total"] else 0.0,
        }
        for d in domain_agg.values()
    ]
    overall_accuracy = round(overall_correct / total, 2) if total else 0.0

    # Naive predicted: accuracy * 20
    predicted = round(overall_accuracy * 20, 1)

    return {
        "questions_answered": total,
        "overall_accuracy": overall_accuracy,
        "predicted": predicted,
        "per_domain": per_domain,
    }


# Silence unused-import warnings for models loaded for relationship resolution.
_ = MicroLesson
