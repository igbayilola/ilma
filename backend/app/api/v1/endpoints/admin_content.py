"""Admin CRUD endpoints for content management."""
import csv
import io
import json
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, UploadFile
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import require_role
from app.core.exceptions import AppException, NotFoundException
from app.db.session import get_db_session
from app.models.content import ContentStatus, ContentVersion, Domain, GradeLevel, MicroLesson, MicroSkill, Question, QuestionComment, QuestionType, Skill, Subject
from app.models.content_audit import ContentTransition
from app.models.user import User, UserRole
from app.schemas.content import (
    BulkExerciseImportRequest,
    BulkExerciseImportResult,
    BulkImportReport,
    BulkImportRowError,
    ContentVersionListOut,
    ContentVersionOut,
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
    QuestionCommentCreate,
    QuestionCommentOut,
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

async def _invalidate_content_cache_on_write(request: Request):
    """Dependency: invalidate content Redis cache after a successful write.

    Registered via BackgroundTasks-style: we schedule invalidation on the
    response. Since APIRouter has no .middleware() hook, we run this as a
    dependency and trigger invalidation post-response via a response hook
    set on request.state — the actual invalidation runs when the endpoint
    returns successfully on write methods.
    """
    yield
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        from app.services.content_cache import invalidate_all
        try:
            await invalidate_all()
        except Exception:
            pass  # best-effort


router = APIRouter(
    prefix="/admin/content",
    tags=["Admin - Content"],
    dependencies=[Depends(_invalidate_content_cache_on_write)],
)

_admin = require_role(UserRole.ADMIN, UserRole.EDITOR)


# ── Versioning helpers ─────────────────────────────────────
def _question_to_snapshot(q: Question) -> dict:
    """Serialize a Question to a JSON-safe dict for version snapshots."""
    return {
        "skill_id": str(q.skill_id),
        "micro_skill_id": str(q.micro_skill_id) if q.micro_skill_id else None,
        "external_id": q.external_id,
        "question_type": q.question_type.value if q.question_type else None,
        "difficulty": q.difficulty.value if q.difficulty else None,
        "text": q.text,
        "choices": q.choices,
        "correct_answer": q.correct_answer,
        "explanation": q.explanation,
        "hint": q.hint,
        "hints": q.hints,
        "media_url": q.media_url,
        "points": q.points,
        "time_limit_seconds": q.time_limit_seconds,
        "bloom_level": q.bloom_level,
        "ilma_level": q.ilma_level,
        "tags": q.tags,
        "common_mistake_targeted": q.common_mistake_targeted,
        "is_active": q.is_active,
        "status": q.status.value if q.status else None,
        "reviewer_notes": q.reviewer_notes,
        "version": q.version,
    }


def _lesson_to_snapshot(lesson: MicroLesson) -> dict:
    """Serialize a MicroLesson to a JSON-safe dict for version snapshots."""
    return {
        "skill_id": str(lesson.skill_id),
        "micro_skill_id": str(lesson.micro_skill_id) if lesson.micro_skill_id else None,
        "title": lesson.title,
        "content_html": lesson.content_html,
        "summary": lesson.summary,
        "media_url": lesson.media_url,
        "duration_minutes": lesson.duration_minutes,
        "order": lesson.order,
        "is_active": lesson.is_active,
        "status": lesson.status.value if lesson.status else None,
        "reviewer_notes": lesson.reviewer_notes,
        "version": lesson.version,
    }


async def _save_version_snapshot(
    db: AsyncSession,
    content_type: str,
    content_id: UUID,
    version: int,
    data_json: dict,
    modified_by: UUID | None,
) -> None:
    """Save a content version snapshot."""
    cv = ContentVersion(
        content_type=content_type,
        content_id=content_id,
        version=version,
        data_json=data_json,
        modified_by=modified_by,
    )
    db.add(cv)


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
    """Return the full nested curriculum tree: grades → subjects → domains → skills → micro_skills."""
    stmt = (
        select(GradeLevel)
        .options(
            selectinload(GradeLevel.subjects)
            .selectinload(Subject.domains)
            .selectinload(Domain.skills)
            .selectinload(Skill.micro_skills)
        )
        .order_by(GradeLevel.order)
    )
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
    user: User = Depends(_admin),
):
    q = await _get_or_404(db, Question, id, "Question")
    # Save current state as version snapshot before applying changes
    snapshot = _question_to_snapshot(q)
    await _save_version_snapshot(db, "question", q.id, q.version, snapshot, user.id)
    # Apply changes and increment version
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(q, k, v)
    q.version = (q.version or 1) + 1
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
    user: User = Depends(_admin),
):
    lesson = await _get_or_404(db, MicroLesson, id, "Leçon")
    # Save current state as version snapshot before applying changes
    snapshot = _lesson_to_snapshot(lesson)
    await _save_version_snapshot(db, "lesson", lesson.id, lesson.version, snapshot, user.id)
    # Apply changes and increment version
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(lesson, k, v)
    lesson.version = (lesson.version or 1) + 1
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


# ── CSV/JSON Question Import (validate-all-then-commit) ──
REQUIRED_COLUMNS = {"skill_id", "text", "correct_answer"}
VALID_QUESTION_TYPES = set(QuestionType.__members__.keys())


def _parse_csv_rows(text_content: str) -> List[Dict[str, str]]:
    """Parse CSV text into a list of row dicts. Raises on missing required columns."""
    reader = csv.DictReader(io.StringIO(text_content))
    if not reader.fieldnames or not REQUIRED_COLUMNS.issubset(set(reader.fieldnames)):
        raise AppException(
            status_code=400,
            code="INVALID_FORMAT",
            message=f"Colonnes requises : {', '.join(sorted(REQUIRED_COLUMNS))}",
        )
    return list(reader)


def _parse_json_rows(text_content: str) -> List[Dict[str, Any]]:
    """Parse JSON text into a list of question dicts. Raises on invalid JSON."""
    try:
        data = json.loads(text_content)
    except json.JSONDecodeError as e:
        raise AppException(status_code=400, code="INVALID_JSON", message=f"JSON invalide : {e}")
    if not isinstance(data, list):
        raise AppException(status_code=400, code="INVALID_FORMAT", message="Le JSON doit contenir un tableau de questions.")
    return data


def _validate_row(row: Dict[str, Any], row_num: int) -> tuple:
    """Validate a single row and return (parsed_data, error).
    Returns (data, None) on success or (None, error) on failure."""
    errors_parts: List[str] = []

    # Required: skill_id
    skill_id_raw = row.get("skill_id", "")
    if isinstance(skill_id_raw, str):
        skill_id_raw = skill_id_raw.strip()
    if not skill_id_raw:
        errors_parts.append("skill_id est requis")
    else:
        try:
            UUID(str(skill_id_raw))
        except (ValueError, AttributeError):
            errors_parts.append(f"skill_id invalide : {skill_id_raw}")

    # Required: text
    text_raw = row.get("text", "")
    if isinstance(text_raw, str):
        text_raw = text_raw.strip()
    if not text_raw:
        errors_parts.append("text est requis")

    # Required: correct_answer
    correct_raw = row.get("correct_answer", "")
    if isinstance(correct_raw, str):
        correct_raw = correct_raw.strip()
    if not correct_raw and correct_raw != 0 and correct_raw is not False:
        errors_parts.append("correct_answer est requis")

    # Optional: question_type validation
    q_type_raw = row.get("question_type", "MCQ")
    if isinstance(q_type_raw, str):
        q_type_raw = q_type_raw.strip().upper()
    if q_type_raw and q_type_raw not in VALID_QUESTION_TYPES:
        errors_parts.append(f"question_type invalide : {q_type_raw}. Valeurs acceptees : {', '.join(sorted(VALID_QUESTION_TYPES))}")

    # Optional: points validation
    points_raw = row.get("points", "1")
    if isinstance(points_raw, str):
        points_raw = points_raw.strip() or "1"
    try:
        points_val = int(points_raw)
        if points_val < 1:
            errors_parts.append("points doit etre >= 1")
    except (ValueError, TypeError):
        errors_parts.append(f"points invalide : {points_raw}")
        points_val = 1

    if errors_parts:
        return None, BulkImportRowError(row=row_num, message=" ; ".join(errors_parts))

    # Build validated data
    q_type = q_type_raw if q_type_raw in VALID_QUESTION_TYPES else "MCQ"

    # Parse choices (CSV: semicolon-separated string; JSON: list)
    choices_raw = row.get("choices", "")
    if isinstance(choices_raw, list):
        choices = [str(c).strip() for c in choices_raw if str(c).strip()]
    elif isinstance(choices_raw, str) and choices_raw.strip():
        choices = [c.strip() for c in choices_raw.split(";") if c.strip()]
    else:
        choices = None

    parsed: Dict[str, Any] = {
        "skill_id": UUID(str(row["skill_id"]).strip()),
        "question_type": QuestionType(q_type),
        "text": str(text_raw),
        "choices": choices or None,
        "correct_answer": str(correct_raw) if not isinstance(correct_raw, (int, float, bool)) else correct_raw,
        "explanation": (str(row.get("explanation", "")).strip() or None) if row.get("explanation") is not None else None,
        "points": points_val,
    }
    return parsed, None


@router.post("/import/questions", summary="Import questions from CSV or JSON file")
async def import_questions(
    file: UploadFile,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    """Import questions from a CSV or JSON file with validate-all-then-commit.

    CSV expected columns: skill_id, question_type, text, choices (semicolon-separated),
    correct_answer, explanation, points.

    JSON expected format: array of objects with the same fields.

    Phase 1: Validate ALL rows, collecting errors with row numbers.
    Phase 2: If errors found, return detailed error report WITHOUT committing.
    Phase 3: If all valid, commit atomically in a single transaction.
    """
    if not file.filename:
        raise AppException(status_code=400, code="INVALID_FILE", message="Nom de fichier manquant.")

    filename_lower = file.filename.lower()
    is_csv = filename_lower.endswith(".csv")
    is_json = filename_lower.endswith(".json")

    if not is_csv and not is_json:
        raise AppException(
            status_code=400,
            code="INVALID_FILE",
            message="Seuls les fichiers CSV (.csv) et JSON (.json) sont acceptes.",
        )

    content = await file.read()
    text_content = content.decode("utf-8-sig")

    # Parse file into rows
    if is_csv:
        rows = _parse_csv_rows(text_content)
    else:
        rows = _parse_json_rows(text_content)

    if not rows:
        return ok(data=BulkImportReport(
            status="failed",
            total_rows=0,
            invalid_rows=0,
            valid_rows=0,
            errors=[BulkImportRowError(row=0, message="Le fichier ne contient aucune ligne de donnees.")],
            rolled_back=False,
        ).model_dump())

    # ── Phase 1: Validate ALL rows ──────────────────────
    validated_rows: List[Dict[str, Any]] = []
    all_errors: List[BulkImportRowError] = []
    skill_ids_to_check: set = set()

    for i, row in enumerate(rows, start=1 if is_json else 2):
        parsed, error = _validate_row(row, i)
        if error:
            all_errors.append(error)
        else:
            assert parsed is not None
            validated_rows.append({**parsed, "_row": i})
            skill_ids_to_check.add(parsed["skill_id"])

    # Batch-check skill existence
    existing_skill_ids: set = set()
    if skill_ids_to_check:
        result = await db.execute(
            select(Skill.id).where(Skill.id.in_(list(skill_ids_to_check)))
        )
        existing_skill_ids = {r[0] for r in result.all()}

    # Check for missing skills
    final_valid: List[Dict[str, Any]] = []
    for vrow in validated_rows:
        if vrow["skill_id"] not in existing_skill_ids:
            all_errors.append(BulkImportRowError(
                row=vrow["_row"],
                message=f"Competence {vrow['skill_id']} introuvable",
            ))
        else:
            final_valid.append(vrow)

    total_rows = len(rows)

    # ── Phase 2: If errors, return report without committing ──
    if all_errors:
        all_errors.sort(key=lambda e: e.row)
        return ok(data=BulkImportReport(
            status="failed",
            total_rows=total_rows,
            valid_rows=len(final_valid),
            invalid_rows=len(all_errors),
            created=0,
            errors=all_errors,
            rolled_back=True,
        ).model_dump())

    # ── Phase 3: All valid -> commit atomically ──────────
    for vrow in final_valid:
        vrow.pop("_row")
        q = Question(**vrow)
        db.add(q)

    await db.commit()

    return ok(data=BulkImportReport(
        status="success",
        total_rows=total_rows,
        valid_rows=len(final_valid),
        invalid_rows=0,
        created=len(final_valid),
        errors=[],
        rolled_back=False,
    ).model_dump())


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


# ── Content Workflow (status transitions) ─────────────────────

_VALID_TRANSITIONS = {
    ContentStatus.DRAFT: [ContentStatus.IN_REVIEW],
    ContentStatus.IN_REVIEW: [ContentStatus.PUBLISHED, ContentStatus.DRAFT],
    ContentStatus.PUBLISHED: [ContentStatus.ARCHIVED],
    ContentStatus.ARCHIVED: [ContentStatus.DRAFT],
}


from pydantic import BaseModel as _BaseModel  # noqa: E402


class StatusTransitionBody(_BaseModel):
    target_status: ContentStatus
    reviewer_notes: Optional[str] = None


@router.post("/questions/{question_id}/transition")
async def transition_question_status(
    question_id: UUID,
    body: StatusTransitionBody,
    db: AsyncSession = Depends(get_db_session),
    _admin: User = Depends(_admin),
):
    """Transition question status: DRAFT → IN_REVIEW → PUBLISHED → ARCHIVED."""
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    if not question:
        raise NotFoundException("Question", str(question_id))

    allowed = _VALID_TRANSITIONS.get(question.status, [])
    if body.target_status not in allowed:
        raise AppException(
            status_code=400,
            code="INVALID_TRANSITION",
            message=f"Transition {question.status.value} → {body.target_status.value} non autorisée",
        )

    from_status = question.status.value
    question.status = body.target_status
    if body.reviewer_notes:
        question.reviewer_notes = body.reviewer_notes

    db.add(ContentTransition(
        content_type="question",
        content_id=question.id,
        from_status=from_status,
        to_status=body.target_status.value,
        transitioned_by=_admin.id,
        reviewer_notes=body.reviewer_notes,
    ))

    await db.flush()
    await db.commit()
    return ok(data={"id": str(question.id), "status": question.status.value})


@router.post("/lessons/{lesson_id}/transition")
async def transition_lesson_status(
    lesson_id: UUID,
    body: StatusTransitionBody,
    db: AsyncSession = Depends(get_db_session),
    _admin: User = Depends(_admin),
):
    """Transition lesson status: DRAFT → IN_REVIEW → PUBLISHED → ARCHIVED."""
    result = await db.execute(select(MicroLesson).where(MicroLesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise NotFoundException("MicroLesson", str(lesson_id))

    allowed = _VALID_TRANSITIONS.get(lesson.status, [])
    if body.target_status not in allowed:
        raise AppException(
            status_code=400,
            code="INVALID_TRANSITION",
            message=f"Transition {lesson.status.value} → {body.target_status.value} non autorisée",
        )

    from_status = lesson.status.value
    lesson.status = body.target_status
    if body.reviewer_notes:
        lesson.reviewer_notes = body.reviewer_notes

    db.add(ContentTransition(
        content_type="lesson",
        content_id=lesson.id,
        from_status=from_status,
        to_status=body.target_status.value,
        transitioned_by=_admin.id,
        reviewer_notes=body.reviewer_notes,
    ))

    await db.flush()
    await db.commit()
    return ok(data={"id": str(lesson.id), "status": lesson.status.value})


@router.get("/questions/by-status")
async def list_questions_by_status(
    status: ContentStatus = Query(ContentStatus.IN_REVIEW),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session),
    _admin: User = Depends(_admin),
):
    """List questions filtered by workflow status (for editorial Kanban)."""
    result = await db.execute(
        select(Question)
        .where(Question.status == status)
        .order_by(Question.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )
    questions = result.scalars().all()
    return ok(data=[
        {
            "id": str(q.id),
            "text": q.text[:100] if q.text else "",
            "question_type": q.question_type.value if q.question_type else None,
            "difficulty": q.difficulty.value if q.difficulty else None,
            "status": q.status.value,
            "reviewer_notes": q.reviewer_notes,
            "skill_id": str(q.skill_id),
            "updated_at": q.updated_at.isoformat() if q.updated_at else None,
        }
        for q in questions
    ])


@router.get("/questions/{question_id}/preview")
async def preview_question(
    question_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _admin_user: User = Depends(_admin),
):
    """Preview a question as a student would see it (works for any status)."""
    q = await _get_or_404(db, Question, question_id, "Question")

    return ok(data={
        "id": str(q.id),
        "question_type": q.question_type.value if q.question_type else "mcq",
        "difficulty": q.difficulty.value if q.difficulty else "medium",
        "text": q.text,
        "choices": q.choices,
        "correct_answer": q.correct_answer,
        "explanation": q.explanation,
        "hint": q.hint,
        "hints": q.hints,
        "media_url": q.media_url,
        "points": q.points,
        "time_limit_seconds": q.time_limit_seconds,
        "status": q.status.value,
    })


@router.get("/questions/{question_id}/stats")
async def get_question_stats(
    question_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _admin_user: User = Depends(_admin),
):
    """Get post-publication stats for a question: success rate, avg time, attempt count."""
    from app.models.session import Attempt

    q = await _get_or_404(db, Question, question_id, "Question")

    result = await db.execute(
        select(
            func.count(Attempt.id).label("total_attempts"),
            func.sum(case((Attempt.is_correct.is_(True), 1), else_=0)).label("correct"),
            func.avg(Attempt.time_spent_seconds).label("avg_time"),
        ).where(Attempt.question_id == question_id)
    )
    row = result.one()
    total = row[0] or 0
    correct = row[1] or 0
    avg_time = round(float(row[2]), 1) if row[2] else None
    success_rate = round(correct / total * 100, 1) if total > 0 else None

    return ok(data={
        "question_id": str(question_id),
        "status": q.status.value,
        "total_attempts": total,
        "correct_answers": correct,
        "success_rate": success_rate,
        "avg_time_seconds": avg_time,
    })


# ── Question Comments ─────────────────────────────────────

@router.get("/questions/{question_id}/comments")
async def list_question_comments(
    question_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    """List all comments for a question."""
    await _get_or_404(db, Question, question_id, "Question")
    result = await db.execute(
        select(QuestionComment)
        .where(QuestionComment.question_id == question_id)
        .order_by(QuestionComment.created_at)
    )
    comments = result.scalars().all()
    out = []
    for c in comments:
        author_name = ""
        if c.author:
            author_name = c.author.phone or str(c.author.id)[:8]
        out.append(QuestionCommentOut(
            id=c.id,
            question_id=c.question_id,
            author_id=c.author_id,
            author_name=author_name,
            text=c.text,
            created_at=c.created_at,
        ))
    return ok(data=[o.model_dump(mode="json") for o in out])


@router.post("/questions/{question_id}/comments", status_code=201)
async def create_question_comment(
    question_id: UUID,
    body: QuestionCommentCreate,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(_admin),
):
    """Add a comment to a question."""
    await _get_or_404(db, Question, question_id, "Question")
    comment = QuestionComment(
        question_id=question_id,
        author_id=user.id,
        text=body.text,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    author_name = user.phone or str(user.id)[:8]
    return ok(data=QuestionCommentOut(
        id=comment.id,
        question_id=comment.question_id,
        author_id=comment.author_id,
        author_name=author_name,
        text=comment.text,
        created_at=comment.created_at,
    ).model_dump(mode="json"))


@router.delete("/questions/{question_id}/comments/{comment_id}", status_code=204)
async def delete_question_comment(
    question_id: UUID,
    comment_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(_admin),
):
    """Delete own comment on a question."""
    result = await db.execute(
        select(QuestionComment).where(
            QuestionComment.id == comment_id,
            QuestionComment.question_id == question_id,
        )
    )
    comment = result.scalar_one_or_none()
    if not comment:
        raise NotFoundException("Commentaire", str(comment_id))
    if comment.author_id != user.id:
        raise AppException(
            status_code=403,
            code="FORBIDDEN",
            message="Vous ne pouvez supprimer que vos propres commentaires.",
        )
    await db.delete(comment)
    await db.commit()


# ── Content Versioning ─────────────────────────────────────

@router.get("/questions/{question_id}/versions")
async def list_question_versions(
    question_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    """List version history for a question (most recent first, no data_json)."""
    await _get_or_404(db, Question, question_id, "Question")
    result = await db.execute(
        select(ContentVersion)
        .where(ContentVersion.content_type == "question", ContentVersion.content_id == question_id)
        .order_by(ContentVersion.version.desc())
    )
    versions = result.scalars().all()
    return ok(data=[ContentVersionListOut.model_validate(v).model_dump(mode="json") for v in versions])


@router.get("/questions/{question_id}/versions/{version_num}")
async def get_question_version_detail(
    question_id: UUID,
    version_num: int,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    """Get a specific version snapshot with full data_json."""
    result = await db.execute(
        select(ContentVersion).where(
            ContentVersion.content_type == "question",
            ContentVersion.content_id == question_id,
            ContentVersion.version == version_num,
        )
    )
    cv = result.scalar_one_or_none()
    if not cv:
        raise NotFoundException("Version", f"{question_id} v{version_num}")
    return ok(data=ContentVersionOut.model_validate(cv).model_dump(mode="json"))


@router.post("/questions/{question_id}/rollback/{version_num}")
async def rollback_question(
    question_id: UUID,
    version_num: int,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(_admin),
):
    """Restore a question to a previous version. Saves current state as a new version first."""
    q = await _get_or_404(db, Question, question_id, "Question")

    # Find the target version
    result = await db.execute(
        select(ContentVersion).where(
            ContentVersion.content_type == "question",
            ContentVersion.content_id == question_id,
            ContentVersion.version == version_num,
        )
    )
    cv = result.scalar_one_or_none()
    if not cv:
        raise NotFoundException("Version", f"{question_id} v{version_num}")

    # Save current state as snapshot before rollback
    snapshot = _question_to_snapshot(q)
    await _save_version_snapshot(db, "question", q.id, q.version, snapshot, user.id)

    # Restore fields from the snapshot
    data = cv.data_json
    for field in [
        "text", "choices", "correct_answer", "explanation", "hint", "hints",
        "media_url", "points", "time_limit_seconds", "bloom_level",
        "ilma_level", "tags", "common_mistake_targeted", "is_active",
        "reviewer_notes",
    ]:
        if field in data:
            setattr(q, field, data[field])

    # Restore enum fields
    if "question_type" in data and data["question_type"]:
        from app.models.content import QuestionType as QT
        q.question_type = QT(data["question_type"])
    if "difficulty" in data and data["difficulty"]:
        from app.models.content import DifficultyLevel as DL
        q.difficulty = DL(data["difficulty"])
    if "status" in data and data["status"]:
        q.status = ContentStatus(data["status"])

    q.version = (q.version or 1) + 1
    await db.commit()
    await db.refresh(q)
    return ok(data=QuestionOut.model_validate(q).model_dump(mode="json"))


@router.get("/lessons/{lesson_id}/versions")
async def list_lesson_versions(
    lesson_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: User = Depends(_admin),
):
    """List version history for a lesson (most recent first, no data_json)."""
    await _get_or_404(db, MicroLesson, lesson_id, "Leçon")
    result = await db.execute(
        select(ContentVersion)
        .where(ContentVersion.content_type == "lesson", ContentVersion.content_id == lesson_id)
        .order_by(ContentVersion.version.desc())
    )
    versions = result.scalars().all()
    return ok(data=[ContentVersionListOut.model_validate(v).model_dump(mode="json") for v in versions])


@router.post("/lessons/{lesson_id}/rollback/{version_num}")
async def rollback_lesson(
    lesson_id: UUID,
    version_num: int,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(_admin),
):
    """Restore a lesson to a previous version. Saves current state as a new version first."""
    lesson = await _get_or_404(db, MicroLesson, lesson_id, "Leçon")

    result = await db.execute(
        select(ContentVersion).where(
            ContentVersion.content_type == "lesson",
            ContentVersion.content_id == lesson_id,
            ContentVersion.version == version_num,
        )
    )
    cv = result.scalar_one_or_none()
    if not cv:
        raise NotFoundException("Version", f"{lesson_id} v{version_num}")

    # Save current state
    snapshot = _lesson_to_snapshot(lesson)
    await _save_version_snapshot(db, "lesson", lesson.id, lesson.version, snapshot, user.id)

    # Restore fields
    data = cv.data_json
    for field in [
        "title", "content_html", "summary", "media_url",
        "duration_minutes", "order", "is_active", "reviewer_notes",
    ]:
        if field in data:
            setattr(lesson, field, data[field])

    if "status" in data and data["status"]:
        lesson.status = ContentStatus(data["status"])

    lesson.version = (lesson.version or 1) + 1
    await db.commit()
    await db.refresh(lesson)
    return ok(data=LessonOut.model_validate(lesson).model_dump(mode="json"))
