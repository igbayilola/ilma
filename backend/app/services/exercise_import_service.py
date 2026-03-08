"""Service for multi-micro-skill exercise import (file / batch)."""
from typing import Any, Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import MicroSkill, Question, QuestionType
from app.schemas.content import (
    BulkExerciseImportRequest,
    BulkExerciseImportResult,
    ExerciseFileImportRequest,
    ExerciseFileImportResult,
    ExerciseItem,
)


def exercise_to_question_dict(exercise: ExerciseItem, micro_skill: MicroSkill) -> Dict[str, Any]:
    """Convert a typed ExerciseItem into a flat dict suitable for Question(**d)."""
    d: Dict[str, Any] = {
        "skill_id": micro_skill.skill_id,
        "micro_skill_id": micro_skill.id,
        "external_id": f"{micro_skill.external_id}::{exercise.exercise_id}",
        "question_type": exercise.type,
        "difficulty": exercise.difficulty,
        "text": exercise.text,
        "correct_answer": exercise.correct_answer,
        "explanation": exercise.explanation,
        "hint": exercise.hint,
        "points": exercise.points,
        "time_limit_seconds": exercise.time_limit_seconds,
        "bloom_level": exercise.bloom_level,
        "ilma_level": exercise.ilma_level,
        "tags": exercise.tags,
        "common_mistake_targeted": exercise.common_mistake_targeted,
        "media_url": exercise.media_url,
    }

    # Map type-specific fields into the generic JSONB `choices` column
    qt = exercise.type
    if qt == QuestionType.MCQ:
        d["choices"] = exercise.choices  # type: ignore[union-attr]
    elif qt == QuestionType.ORDERING:
        d["choices"] = exercise.items  # type: ignore[union-attr]
    elif qt == QuestionType.MATCHING:
        d["choices"] = {  # type: ignore[union-attr]
            "left": exercise.left_items,
            "right": exercise.right_items,
        }
    elif qt == QuestionType.FILL_BLANK:
        d["choices"] = exercise.blanks if hasattr(exercise, "blanks") else None  # type: ignore[union-attr]
    elif qt == QuestionType.NUMERIC_INPUT:
        d["choices"] = {"tolerance": exercise.tolerance} if hasattr(exercise, "tolerance") and exercise.tolerance is not None else None  # type: ignore[union-attr]
    elif qt == QuestionType.SHORT_ANSWER:
        d["choices"] = exercise.accepted_answers if hasattr(exercise, "accepted_answers") else None  # type: ignore[union-attr]
    elif qt == QuestionType.ERROR_CORRECTION:
        d["choices"] = {"erroneous_content": exercise.erroneous_content} if hasattr(exercise, "erroneous_content") and exercise.erroneous_content else None  # type: ignore[union-attr]
    elif qt == QuestionType.CONTEXTUAL_PROBLEM:
        d["choices"] = exercise.sub_questions if hasattr(exercise, "sub_questions") else None  # type: ignore[union-attr]
    elif qt == QuestionType.GUIDED_STEPS:
        d["choices"] = exercise.steps  # type: ignore[union-attr]
    elif qt == QuestionType.JUSTIFICATION:
        d["choices"] = {"scoring_rubric": exercise.scoring_rubric} if hasattr(exercise, "scoring_rubric") and exercise.scoring_rubric else None  # type: ignore[union-attr]
    elif qt == QuestionType.TRACING:
        d["choices"] = exercise.number_line if hasattr(exercise, "number_line") else None  # type: ignore[union-attr]

    return d


async def import_exercises_for_micro_skill(
    db: AsyncSession,
    block: BulkExerciseImportRequest,
) -> BulkExerciseImportResult:
    """Import exercises for a single micro-skill (upsert by external_id)."""
    result = await db.execute(
        select(MicroSkill).where(MicroSkill.external_id == block.micro_skill_external_id)
    )
    micro_skill = result.scalar_one_or_none()
    if not micro_skill:
        stats = BulkExerciseImportResult()
        stats.errors.append({
            "micro_skill_external_id": block.micro_skill_external_id,
            "error": "Micro-compétence introuvable",
        })
        return stats

    stats = BulkExerciseImportResult()
    for idx, exercise in enumerate(block.exercises):
        try:
            q_dict = exercise_to_question_dict(exercise, micro_skill)
            ext_id = q_dict["external_id"]

            existing_result = await db.execute(
                select(Question).where(Question.external_id == ext_id)
            )
            existing = existing_result.scalar_one_or_none()

            if existing:
                for k, v in q_dict.items():
                    setattr(existing, k, v)
                stats.updated += 1
            else:
                db.add(Question(**q_dict))
                stats.created += 1
        except Exception as e:
            stats.errors.append({
                "index": idx,
                "exercise_id": exercise.exercise_id,
                "error": str(e),
            })

    return stats


async def import_exercises_file(
    db: AsyncSession,
    payload: ExerciseFileImportRequest,
) -> ExerciseFileImportResult:
    """Import exercises from a multi-micro-skill payload."""
    result = ExerciseFileImportResult()

    for block in payload.exercises:
        block_stats = await import_exercises_for_micro_skill(db, block)
        result.micro_skills_processed += 1
        result.created += block_stats.created
        result.updated += block_stats.updated
        result.skipped += block_stats.skipped
        if block_stats.errors:
            for err in block_stats.errors:
                err["micro_skill_external_id"] = block.micro_skill_external_id
                result.errors.append(err)

    await db.commit()
    return result
