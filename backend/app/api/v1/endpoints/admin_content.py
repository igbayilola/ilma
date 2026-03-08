"""Admin CRUD endpoints for content management."""
import csv
import io
import json
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_role
from app.core.exceptions import AppException, NotFoundException
from app.db.session import get_db_session
from app.models.content import Domain, GradeLevel, MicroLesson, MicroSkill, Question, QuestionType, Skill, Subject
from app.models.user import User, UserRole
from app.schemas.content import (
    BulkExerciseImportRequest,
    BulkExerciseImportResult,
    CurriculumImportRequest,
    DomainCreate,
    DomainOut,
    DomainUpdate,
    ExerciseFileImportRequest,
    ExerciseItem,
    GradeLevelCreate,
    GradeLevelOut,
    GradeLevelUpdate,
    LessonCreate,
    LessonOut,
    LessonUpdate,
    MicroSkillCreate,
    MicroSkillOut,
    MicroSkillUpdate,
    QuestionCreate,
    QuestionOut,
    QuestionUpdate,
    SkillCreate,
    SkillOut,
    SkillUpdate,
    SubjectCreate,
    SubjectOut,
    SubjectUpdate,
    TreeGradeOut,
)
from app.schemas.response import ok
from app.services.curriculum_import_service import import_curriculum
from app.services.exercise_import_service import (
    exercise_to_question_dict as _exercise_to_question_dict,
    import_exercises_file,
    import_exercises_for_micro_skill,
)

router = APIRouter(prefix="/admin/content", tags=["Admin - Content"])

_admin = require_role(UserRole.ADMIN)


# ── Helper ─────────────────────────────────────────────────
async def _get_or_404(db: AsyncSession, model, id: UUID, label: str):
    result = await db.execute(select(model).where(model.id == id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise NotFoundException(label, str(id))
    return obj


# ── Grade Levels ──────────────────────────────────────────
@router.get("/grade-levels")
async def list_grade_levels(
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    result = await db.execute(select(GradeLevel).order_by(GradeLevel.order))
    grades = result.scalars().all()
    return ok(data=[GradeLevelOut.model_validate(g) for g in grades])


@router.post("/grade-levels", status_code=201)
async def create_grade_level(
    body: GradeLevelCreate,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    gl = GradeLevel(**body.model_dump())
    db.add(gl)
    await db.commit()
    await db.refresh(gl)
    return ok(data=GradeLevelOut.model_validate(gl))


@router.put("/grade-levels/{id}")
async def update_grade_level(
    id: UUID,
    body: GradeLevelUpdate,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    gl = await _get_or_404(db, GradeLevel, id, "Classe")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(gl, k, v)
    await db.commit()
    await db.refresh(gl)
    return ok(data=GradeLevelOut.model_validate(gl))


@router.delete("/grade-levels/{id}", status_code=204)
async def delete_grade_level(
    id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    gl = await _get_or_404(db, GradeLevel, id, "Classe")
    await db.delete(gl)
    await db.commit()


# ── Curriculum Tree ───────────────────────────────────────
@router.get("/curriculum/tree", summary="Get full curriculum tree")
async def get_curriculum_tree(
    grade_level_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    """Return the full nested curriculum tree: grades → subjects → domains → skills → micro_skills.

    Relationships use lazy='selectin' so eager loading happens automatically.
    """
    stmt = select(GradeLevel).order_by(GradeLevel.order)
    if grade_level_id:
        stmt = stmt.where(GradeLevel.id == grade_level_id)
    result = await db.execute(stmt)
    grades = result.scalars().unique().all()
    return ok(data=[TreeGradeOut.model_validate(g) for g in grades])


# ── Subjects ───────────────────────────────────────────────
@router.get("/subjects")
async def admin_list_subjects(
    grade_level_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    stmt = select(Subject).order_by(Subject.order)
    if grade_level_id:
        stmt = stmt.where(Subject.grade_level_id == grade_level_id)
    result = await db.execute(stmt)
    subjects = result.scalars().all()
    return ok(data=[SubjectOut.model_validate(s) for s in subjects])


@router.post("/subjects", status_code=201)
async def create_subject(
    body: SubjectCreate,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    subj = Subject(**body.model_dump())
    db.add(subj)
    await db.commit()
    await db.refresh(subj)
    return ok(data=SubjectOut.model_validate(subj))


@router.put("/subjects/{id}")
async def update_subject(
    id: UUID,
    body: SubjectUpdate,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    subj = await _get_or_404(db, Subject, id, "Matière")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(subj, k, v)
    await db.commit()
    await db.refresh(subj)
    return ok(data=SubjectOut.model_validate(subj))


@router.delete("/subjects/{id}", status_code=204)
async def delete_subject(
    id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    subj = await _get_or_404(db, Subject, id, "Matière")
    await db.delete(subj)
    await db.commit()


# ── Domains ────────────────────────────────────────────────
@router.post("/domains", status_code=201)
async def create_domain(
    body: DomainCreate,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    dom = Domain(**body.model_dump())
    db.add(dom)
    await db.commit()
    await db.refresh(dom)
    return ok(data=DomainOut.model_validate(dom))


@router.put("/domains/{id}")
async def update_domain(
    id: UUID,
    body: DomainUpdate,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    dom = await _get_or_404(db, Domain, id, "Domaine")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(dom, k, v)
    await db.commit()
    await db.refresh(dom)
    return ok(data=DomainOut.model_validate(dom))


@router.delete("/domains/{id}", status_code=204)
async def delete_domain(
    id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    dom = await _get_or_404(db, Domain, id, "Domaine")
    await db.delete(dom)
    await db.commit()


# ── Skills ─────────────────────────────────────────────────
@router.post("/skills", status_code=201)
async def create_skill(
    body: SkillCreate,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    skill = Skill(**body.model_dump())
    db.add(skill)
    await db.commit()
    await db.refresh(skill)
    return ok(data=SkillOut.model_validate(skill))


@router.put("/skills/{id}")
async def update_skill(
    id: UUID,
    body: SkillUpdate,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    skill = await _get_or_404(db, Skill, id, "Compétence")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(skill, k, v)
    await db.commit()
    await db.refresh(skill)
    return ok(data=SkillOut.model_validate(skill))


@router.delete("/skills/{id}", status_code=204)
async def delete_skill(
    id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    skill = await _get_or_404(db, Skill, id, "Compétence")
    await db.delete(skill)
    await db.commit()


# ── MicroSkills ────────────────────────────────────────────
@router.get("/micro-skills")
async def list_micro_skills(
    skill_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    stmt = select(MicroSkill).order_by(MicroSkill.order)
    if skill_id:
        stmt = stmt.where(MicroSkill.skill_id == skill_id)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return ok(data=[MicroSkillOut.model_validate(ms) for ms in items])


@router.post("/micro-skills", status_code=201)
async def create_micro_skill(
    body: MicroSkillCreate,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    ms = MicroSkill(**body.model_dump())
    db.add(ms)
    await db.commit()
    await db.refresh(ms)
    return ok(data=MicroSkillOut.model_validate(ms))


@router.put("/micro-skills/{id}")
async def update_micro_skill(
    id: UUID,
    body: MicroSkillUpdate,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    ms = await _get_or_404(db, MicroSkill, id, "Micro-compétence")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(ms, k, v)
    await db.commit()
    await db.refresh(ms)
    return ok(data=MicroSkillOut.model_validate(ms))


@router.delete("/micro-skills/{id}", status_code=204)
async def delete_micro_skill(
    id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    ms = await _get_or_404(db, MicroSkill, id, "Micro-compétence")
    await db.delete(ms)
    await db.commit()


# ── Questions ──────────────────────────────────────────────
@router.post("/questions", status_code=201)
async def create_question(
    body: QuestionCreate,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    q = Question(**body.model_dump())
    db.add(q)
    await db.commit()
    await db.refresh(q)
    return ok(data=QuestionOut.model_validate(q))


@router.put("/questions/{id}")
async def update_question(
    id: UUID,
    body: QuestionUpdate,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    q = await _get_or_404(db, Question, id, "Question")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(q, k, v)
    await db.commit()
    await db.refresh(q)
    return ok(data=QuestionOut.model_validate(q))


@router.delete("/questions/{id}", status_code=204)
async def delete_question(
    id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    q = await _get_or_404(db, Question, id, "Question")
    await db.delete(q)
    await db.commit()


# ── Lessons ────────────────────────────────────────────────
@router.post("/lessons", status_code=201)
async def create_lesson(
    body: LessonCreate,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    lesson = MicroLesson(**body.model_dump())
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)
    return ok(data=LessonOut.model_validate(lesson))


@router.put("/lessons/{id}")
async def update_lesson(
    id: UUID,
    body: LessonUpdate,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    lesson = await _get_or_404(db, MicroLesson, id, "Leçon")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(lesson, k, v)
    await db.commit()
    await db.refresh(lesson)
    return ok(data=LessonOut.model_validate(lesson))


@router.delete("/lessons/{id}", status_code=204)
async def delete_lesson(
    id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    lesson = await _get_or_404(db, MicroLesson, id, "Leçon")
    await db.delete(lesson)
    await db.commit()


# ── CSV/Excel Import ─────────────────────────────────────
REQUIRED_COLUMNS = {"skill_id", "text", "correct_answer"}


@router.post("/import/questions", summary="Import questions from CSV file")
async def import_questions_csv(
    file: UploadFile,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    """Import questions from a CSV file.

    Expected columns: skill_id, question_type, difficulty, text,
    choices (semicolon-separated), correct_answer, explanation, points
    """
    if not file.filename or not file.filename.endswith(".csv"):
        raise AppException(status_code=400, code="INVALID_FILE", message="Seuls les fichiers CSV sont acceptés.")

    content = await file.read()
    text_content = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text_content))

    if not reader.fieldnames or not REQUIRED_COLUMNS.issubset(set(reader.fieldnames)):
        raise AppException(
            status_code=400,
            code="INVALID_FORMAT",
            message=f"Colonnes requises : {', '.join(sorted(REQUIRED_COLUMNS))}",
        )

    created = 0
    errors = []

    for i, row in enumerate(reader, start=2):
        try:
            skill_id = UUID(row["skill_id"].strip())
            # Verify skill exists
            skill_result = await db.execute(select(Skill).where(Skill.id == skill_id))
            if not skill_result.scalar_one_or_none():
                errors.append({"row": i, "error": f"Compétence {skill_id} introuvable"})
                continue

            q_type = row.get("question_type", "MCQ").strip().upper()
            choices_raw = row.get("choices", "")
            choices = [c.strip() for c in choices_raw.split(";") if c.strip()] if choices_raw else None

            q = Question(
                skill_id=skill_id,
                question_type=QuestionType(q_type) if q_type in QuestionType.__members__ else QuestionType.MCQ,
                text=row["text"].strip(),
                choices=choices,
                correct_answer=row["correct_answer"].strip(),
                explanation=row.get("explanation", "").strip() or None,
                points=int(row.get("points", "1").strip() or "1"),
            )
            db.add(q)
            created += 1
        except Exception as e:
            errors.append({"row": i, "error": str(e)})

    await db.commit()
    return ok(data={"created": created, "errors": errors})


# ── Curriculum Import (full tree) ────────────────────────

@router.post("/curriculum/import", summary="Import a full curriculum tree (JSON body)")
async def import_curriculum_json(
    body: CurriculumImportRequest,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    """Import/upsert grade → subjects → domains → skills → micro_skills from a JSON body."""
    stats = await import_curriculum(db, body)
    return ok(data=stats.model_dump())


@router.post("/curriculum/import/file", summary="Import a full curriculum tree (file upload)")
async def import_curriculum_file(
    file: UploadFile,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    """Import/upsert curriculum from an uploaded JSON file."""
    if not file.filename or not file.filename.endswith(".json"):
        raise AppException(status_code=400, code="INVALID_FILE", message="Seuls les fichiers JSON sont acceptés.")
    content = await file.read()
    try:
        raw = json.loads(content.decode("utf-8-sig"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise AppException(status_code=400, code="INVALID_JSON", message=f"JSON invalide : {e}")
    try:
        payload = CurriculumImportRequest(**raw)
    except Exception as e:
        raise AppException(status_code=400, code="VALIDATION_ERROR", message=f"Format invalide : {e}")
    stats = await import_curriculum(db, payload)
    return ok(data=stats.model_dump())


# ── Bulk Exercise Import (JSON) ──────────────────────────


@router.post("/exercises/import", status_code=201, summary="Bulk import exercises for a micro-skill")
async def import_exercises_bulk(
    body: BulkExerciseImportRequest,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    """Import exercises in bulk for a given micro-skill (upsert by external_id)."""
    stats = await import_exercises_for_micro_skill(db, body)
    if stats.errors and stats.errors[0].get("error") == "Micro-compétence introuvable":
        raise NotFoundException("Micro-compétence", body.micro_skill_external_id)
    await db.commit()
    return ok(data=stats.model_dump())


@router.post("/exercises/import/batch", status_code=201, summary="Bulk import exercises for multiple micro-skills (JSON body)")
async def import_exercises_batch(
    body: ExerciseFileImportRequest,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    """Import exercises for multiple micro-skills from a single JSON body."""
    stats = await import_exercises_file(db, body)
    return ok(data=stats.model_dump())


@router.post("/exercises/import/file", status_code=201, summary="Bulk import exercises from uploaded JSON file")
async def import_exercises_file_upload(
    file: UploadFile,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    """Import exercises for multiple micro-skills from an uploaded JSON file."""
    if not file.filename or not file.filename.endswith(".json"):
        raise AppException(status_code=400, code="INVALID_FILE", message="Seuls les fichiers JSON sont acceptés.")
    content = await file.read()
    try:
        raw = json.loads(content.decode("utf-8-sig"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise AppException(status_code=400, code="INVALID_JSON", message=f"JSON invalide : {e}")
    try:
        payload = ExerciseFileImportRequest(**raw)
    except Exception as e:
        raise AppException(status_code=400, code="VALIDATION_ERROR", message=f"Format invalide : {e}")
    stats = await import_exercises_file(db, payload)
    return ok(data=stats.model_dump())
