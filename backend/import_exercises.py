"""Import exercises from cm2_maths/exercices_cm2_*.json into the questions table."""
import asyncio
import json
import os
import uuid
from pathlib import Path

# Type mapping from exercise files to DB QuestionType enum
TYPE_MAP = {
    "mcq": "MCQ",
    "true_false": "TRUE_FALSE",
    "fill_blank": "FILL_BLANK",
    "numeric_input": "NUMERIC_INPUT",
    "short_answer": "SHORT_ANSWER",
    "ordering": "ORDERING",
    "matching": "MATCHING",
    "error_correction": "ERROR_CORRECTION",
    "contextual_problem": "CONTEXTUAL_PROBLEM",
    "guided_steps": "GUIDED_STEPS",
    "justification": "JUSTIFICATION",
    "tracing": "TRACING",
}

DIFF_MAP = {
    "easy": "EASY",
    "medium": "MEDIUM",
    "hard": "HARD",
}

async def main():
    from app.db.session import AsyncSessionLocal
    from app.models.content import Question, QuestionType, DifficultyLevel, MicroSkill
    from sqlalchemy import select, func

    content_dir = Path("/app/content/../cm2_maths") 
    # Files are mounted at /opt/sitou/cm2_maths but we're inside the container
    # They might not be mounted. Let's check both paths.
    for p in [Path("/app/cm2_maths"), Path("/opt/sitou/cm2_maths"), Path("cm2_maths")]:
        if p.exists():
            content_dir = p
            break

    if not content_dir.exists():
        print(f"ERROR: content dir not found")
        return

    async with AsyncSessionLocal() as db:
        # Build external_id -> (micro_skill_id, skill_id) mapping
        result = await db.execute(
            select(MicroSkill.external_id, MicroSkill.id, MicroSkill.skill_id)
            .where(MicroSkill.external_id.isnot(None))
        )
        ms_map = {row[0]: (row[1], row[2]) for row in result.all()}
        print(f"Loaded {len(ms_map)} micro-skills from DB")

        # Count existing questions
        existing_count_result = await db.execute(select(func.count(Question.id)))
        existing_count = existing_count_result.scalar() or 0
        print(f"Existing questions in DB: {existing_count}")

        total_imported = 0
        total_skipped = 0
        total_missing_ms = 0

        for f in sorted(content_dir.glob("exercices_cm2_*.json")):
            data = json.load(open(f))
            domain = data.get("metadata", {}).get("domain", f.stem)
            file_imported = 0
            file_skipped = 0

            for ms_block in data.get("exercises", []):
                ms_ext_id = ms_block.get("micro_skill_external_id")
                if ms_ext_id not in ms_map:
                    print(f"  [WARN] micro-skill {ms_ext_id} not found in DB")
                    total_missing_ms += 1
                    continue

                ms_id, skill_id = ms_map[ms_ext_id]

                for ex in ms_block.get("exercises", []):
                    # Build unique external_id for deduplication
                    ex_ext_id = f"{ms_ext_id}::{ex.get('exercise_id', uuid.uuid4().hex[:8])}"

                    # Check if already imported
                    check = await db.execute(
                        select(Question.id).where(Question.external_id == ex_ext_id)
                    )
                    if check.scalar_one_or_none():
                        file_skipped += 1
                        total_skipped += 1
                        continue

                    q_type = TYPE_MAP.get(ex.get("type", "mcq"), "MCQ")
                    difficulty = DIFF_MAP.get(ex.get("difficulty", "medium"), "MEDIUM")

                    # Build choices
                    choices = ex.get("choices")
                    if choices and isinstance(choices, list):
                        choices = choices  # keep as list of strings
                    elif ex.get("type") == "true_false":
                        choices = ["Vrai", "Faux"]

                    # Normalize correct_answer
                    correct = ex.get("correct_answer")
                    if isinstance(correct, bool):
                        correct = "Vrai" if correct else "Faux"
                    elif isinstance(correct, (int, float)):
                        correct = str(correct)

                    q = Question(
                        id=uuid.uuid4(),
                        skill_id=skill_id,
                        micro_skill_id=ms_id,
                        external_id=ex_ext_id,
                        question_type=QuestionType(q_type),
                        difficulty=DifficultyLevel(difficulty),
                        text=ex.get("text", ""),
                        choices=choices,
                        correct_answer=correct,
                        explanation=ex.get("explanation"),
                        hint=ex.get("hint"),
                        points=ex.get("points", 1),
                        time_limit_seconds=ex.get("time_limit_seconds", 60),
                        is_active=True,
                        status="PUBLISHED",
                        version=1,
                    )
                    db.add(q)
                    file_imported += 1
                    total_imported += 1

            await db.flush()
            print(f"  {domain:30s}  +{file_imported:4d} imported, {file_skipped:4d} skipped")

        await db.commit()
        print(f"\n{'='*60}")
        print(f"TOTAL: {total_imported} imported, {total_skipped} skipped, {total_missing_ms} missing micro-skills")
        print(f"Questions in DB now: {existing_count + total_imported}")

asyncio.run(main())
