"""Seed the database with sample data for development."""
import asyncio
import json
import pathlib
import uuid

from sqlalchemy import select

from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal
from app.models.badge import Badge, BadgeCategory
from app.models.content import (
    DifficultyLevel,
    GradeLevel,
    MicroLesson,
    Question,
    QuestionType,
    Skill,
)
from app.models.mock_exam import ExamItem, ExamSubQuestion, MockExam
from app.models.subscription import Plan, PlanTier
from app.models.user import User, UserRole
from app.schemas.content import CurriculumImportRequest
from app.services.curriculum_import_service import import_curriculum

# Resolve path to the content directory
# Inside container: /app/content/  |  Local dev: backend/content/
# Inside container: /app/app/scripts/seed.py → parents[2] = /app
# Local dev: backend/app/scripts/seed.py → parents[2] = backend/
_WORKDIR = pathlib.Path(__file__).resolve().parents[2]
_CONTENT_DIR = _WORKDIR / "content"
_PROGRAMME_DIR = _CONTENT_DIR / "benin" / "cm2" / "programme"
_EXERCICES_DIR = _CONTENT_DIR / "benin" / "cm2" / "exercices"
_EPREUVES_DIR = _CONTENT_DIR / "benin" / "cm2" / "epreuves"


# ── Users ──────────────────────────────────────────────────
SEED_USERS = [
    {"email": "admin@sitou.bj", "full_name": "Administrateur Sitou", "role": UserRole.ADMIN, "password": "Xr;aTRKMx_1CI1Wd@HF1c!9"},
    {"email": "parent@sitou.bj", "full_name": "Koffi Mensah", "role": UserRole.PARENT, "password": "Xr;aTRKMx_1CI1Wd@HF1c!9"},
    {"email": "editeur@sitou.bj", "full_name": "Éditeur Contenu", "role": UserRole.EDITOR, "password": "Xr;aTRKMx_1CI1Wd@HF1c!9"},
    {"email": "eleve@sitou.bj", "full_name": "Afi Mensah", "role": UserRole.STUDENT, "password": "Xr;aTRKMx_1CI1Wd@HF1c!9"},
    {"email": "eleve2@sitou.bj", "full_name": "Kofi Junior", "role": UserRole.STUDENT, "password": "Xr;aTRKMx_1CI1Wd@HF1c!9"},
]

# ── Subjects ──────────────────────────────────────────────
# Only Mathématiques — domains & skills come from JSON curriculum files.
SEED_CONTENT = [
    {
        "name": "Mathématiques", "slug": "mathematiques", "icon": "calculator", "color": "#1E5AA8", "order": 1,
        "domains": [],
    },
]

# ── Badges ─────────────────────────────────────────────────
SEED_BADGES = [
    {"code": "first_exercise", "name": "Premier pas", "description": "Terminer son premier exercice", "category": BadgeCategory.COMPLETION, "icon": "star"},
    {"code": "streak_3", "name": "En forme !", "description": "3 bonnes réponses d'affilée", "category": BadgeCategory.STREAK, "icon": "flame"},
    {"code": "streak_10", "name": "Inarrêtable", "description": "10 bonnes réponses d'affilée", "category": BadgeCategory.STREAK, "icon": "zap"},
    {"code": "mastery_skill", "name": "Expert", "description": "Atteindre 90% sur une compétence", "category": BadgeCategory.MASTERY, "icon": "award"},
    {"code": "daily_challenge", "name": "Défi du jour", "description": "Compléter le défi quotidien", "category": BadgeCategory.SPECIAL, "icon": "trophy"},
    {"code": "week_streak", "name": "Assidu", "description": "Se connecter 7 jours consécutifs", "category": BadgeCategory.STREAK, "icon": "calendar-check"},
    {"code": "all_subjects", "name": "Polyvalent", "description": "Exercice dans chaque matière", "category": BadgeCategory.COMPLETION, "icon": "layout-grid"},
]

# ── Plans ──────────────────────────────────────────────────
SEED_PLANS = [
    {"name": "Gratuit", "tier": PlanTier.FREE, "price_xof": 0, "duration_days": 365, "features": {"max_exercises_day": 5, "exam_blanc": False}},
    {"name": "Pass Journalier", "tier": PlanTier.BASIC, "price_xof": 100, "duration_days": 1, "features": {"max_exercises_day": 20, "exam_blanc": False}},
    {"name": "Pass Hebdomadaire", "tier": PlanTier.BASIC, "price_xof": 500, "duration_days": 7, "features": {"max_exercises_day": 20, "exam_blanc": False}},
    {"name": "Basique", "tier": PlanTier.BASIC, "price_xof": 1000, "duration_days": 30, "features": {"max_exercises_day": 20, "exam_blanc": False}},
    {"name": "Premium", "tier": PlanTier.PREMIUM, "price_xof": 2500, "duration_days": 30, "features": {"max_exercises_day": -1, "exam_blanc": True}},
]

# ── Map question_type strings from JSON to QuestionType enum ──
_QTYPE_MAP = {
    "MCQ": QuestionType.MCQ, "TRUE_FALSE": QuestionType.TRUE_FALSE,
    "FILL_BLANK": QuestionType.FILL_BLANK, "NUMERIC_INPUT": QuestionType.NUMERIC_INPUT,
    "SHORT_ANSWER": QuestionType.SHORT_ANSWER, "ORDERING": QuestionType.ORDERING,
    "MATCHING": QuestionType.MATCHING, "ERROR_CORRECTION": QuestionType.ERROR_CORRECTION,
    "CONTEXTUAL_PROBLEM": QuestionType.CONTEXTUAL_PROBLEM,
    "GUIDED_STEPS": QuestionType.GUIDED_STEPS, "JUSTIFICATION": QuestionType.JUSTIFICATION,
    "TRACING": QuestionType.TRACING,
    "DRAG_DROP": QuestionType.DRAG_DROP, "INTERACTIVE_DRAW": QuestionType.INTERACTIVE_DRAW,
    "CHART_INPUT": QuestionType.CHART_INPUT, "AUDIO_COMPREHENSION": QuestionType.AUDIO_COMPREHENSION,
}
_DIFF_MAP = {
    "EASY": DifficultyLevel.EASY, "easy": DifficultyLevel.EASY,
    "MEDIUM": DifficultyLevel.MEDIUM, "medium": DifficultyLevel.MEDIUM,
    "HARD": DifficultyLevel.HARD, "hard": DifficultyLevel.HARD,
}


def _slugify(text: str) -> str:
    """Very basic slug from a string (lowercase, spaces→hyphens, keep alphanum/hyphens)."""
    import re
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s]+", "-", text)
    return text[:120]


async def _upsert(session, model, unique_field: str, data: dict):
    """Insert if not exists (by unique_field), return the object."""
    col = getattr(model, unique_field)
    result = await session.execute(select(model).where(col == data[unique_field]))
    existing = result.scalar_one_or_none()
    if existing:
        print(f"  [skip] {model.__tablename__}.{data[unique_field]}")
        return existing
    obj = model(id=uuid.uuid4(), **data)
    session.add(obj)
    print(f"  [seed] {model.__tablename__}.{data[unique_field]}")
    return obj


def _load_exercises_from_content() -> dict:
    """Load exercise JSON files from content/benin/cm2/exercices/ into a dict keyed by skill slug."""
    exercises = {}
    if not _EXERCICES_DIR.exists():
        print(f"  [warn] exercices directory not found at {_EXERCICES_DIR}")
        return exercises
    for json_file in sorted(_EXERCICES_DIR.rglob("*.json")):
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)
        slug = data.get("skill_slug")
        if not slug:
            print(f"  [warn] no skill_slug in {json_file.name}, skipping")
            continue
        exercises[slug] = data
    return exercises


def _load_exams_from_content() -> list:
    """Load CEP exam JSON files from content/benin/cm2/epreuves/."""
    exams = []
    if not _EPREUVES_DIR.exists():
        print(f"  [warn] epreuves directory not found at {_EPREUVES_DIR}")
        return exams
    for json_file in sorted(_EPREUVES_DIR.rglob("*.json")):
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)
        exams.append(data)
    return exams


async def seed_v2_exercises(session) -> None:
    """Seed exercises from v2-converted files (v1.0 format with micro_skill_external_id)."""
    from app.models.content import ContentStatus, MicroSkill

    v2_files = sorted(_EXERCICES_DIR.rglob("v2_*.json"))
    if not v2_files:
        print("  [skip] no v2_*.json exercise files found")
        return

    total_created = 0
    total_skipped = 0
    for json_file in v2_files:
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)

        file_created = 0
        for block in data.get("exercises", []):
            ms_ext_id = block.get("micro_skill_external_id", "")
            if ms_ext_id.startswith("_UNMAPPED"):
                continue

            # Resolve micro-skill
            ms_result = await session.execute(
                select(MicroSkill).where(MicroSkill.external_id == ms_ext_id)
            )
            ms_obj = ms_result.scalar_one_or_none()

            # If no micro-skill, try to find the parent skill
            skill_obj = None
            if ms_obj:
                skill_obj_result = await session.execute(
                    select(Skill).where(Skill.id == ms_obj.skill_id)
                )
                skill_obj = skill_obj_result.scalar_one_or_none()
            else:
                # Try skill by external_id (the part before ::)
                skill_ext = ms_ext_id.split("::")[0] if "::" in ms_ext_id else ms_ext_id
                skill_result = await session.execute(
                    select(Skill).where(Skill.external_id == skill_ext).limit(1)
                )
                skill_obj = skill_result.scalar_one_or_none()

            if not skill_obj:
                total_skipped += len(block.get("exercises", []))
                continue

            for ex in block.get("exercises", []):
                ext_id = f"{ms_ext_id}::{ex.get('exercise_id', '')}" if ms_obj else None

                # Skip if already exists
                if ext_id:
                    existing = await session.execute(
                        select(Question).where(Question.external_id == ext_id)
                    )
                    if existing.scalar_one_or_none():
                        total_skipped += 1
                        continue

                q_type = _QTYPE_MAP.get(ex.get("type", "MCQ"), QuestionType.SHORT_ANSWER)
                q_diff = _DIFF_MAP.get(ex.get("difficulty", "medium"), DifficultyLevel.MEDIUM)

                q = Question(
                    id=uuid.uuid4(),
                    skill_id=skill_obj.id,
                    micro_skill_id=ms_obj.id if ms_obj else None,
                    external_id=ext_id,
                    question_type=q_type,
                    difficulty=q_diff,
                    text=ex.get("text", ""),
                    choices=ex.get("choices"),
                    correct_answer=ex.get("correct_answer", ""),
                    explanation=ex.get("explanation", ""),
                    hint=ex.get("hint", ""),
                    hints=[ex["hint"]] if ex.get("hint") else None,
                    points=ex.get("points", 1),
                    time_limit_seconds=ex.get("time_limit_seconds", 60),
                    bloom_level=ex.get("bloom_level"),
                    ilma_level=ex.get("ilma_level"),
                    media_references=ex.get("media_references"),
                    interactive_config=ex.get("interactive_config"),
                    status=ContentStatus.PUBLISHED,
                )
                session.add(q)
                file_created += 1

            await session.flush()

        total_created += file_created
        if file_created > 0:
            print(f"  [seed] {json_file.name}: {file_created} questions")

    print(f"  Total V2 exercises: {total_created} created, {total_skipped} skipped")


async def seed_cep_exams(session, cm2_grade, subject_map: dict) -> None:
    """Seed CEP exams from content/benin/cm2/epreuves/ JSON files.
    subject_map: {"mathematiques": Subject, "est": Subject, ...}
    """
    cep_exams = _load_exams_from_content()
    if not cep_exams:
        print("  [warn] no CEP exam files found")
        return

    for exam_data in cep_exams:
        # Check if exam already exists
        result = await session.execute(
            select(MockExam).where(MockExam.title == exam_data["title"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            print(f"  [skip] CEP exam: {exam_data['title']}")
            continue

        # Resolve subject from JSON "subject" field
        exam_subject_key = exam_data.get("subject", "mathematiques")
        subject = subject_map.get(exam_subject_key)
        if not subject:
            print(f"  [warn] unknown subject '{exam_subject_key}' in {exam_data['title']}, skipping")
            continue

        mock_exam = MockExam(
            id=uuid.uuid4(),
            grade_level_id=cm2_grade.id,
            subject_id=subject.id,
            title=exam_data["title"],
            duration_minutes=exam_data.get("duration_minutes", 60),
            total_questions=sum(len(item.get("sub_questions", [])) for item in exam_data.get("items", [])),
            exam_type="cep",
            context_text=exam_data.get("context_text", ""),
            is_free=True,
            is_national=False,
            is_active=True,
        )
        session.add(mock_exam)
        await session.flush()

        for item_data in exam_data.get("items", []):
            item = ExamItem(
                id=uuid.uuid4(),
                mock_exam_id=mock_exam.id,
                item_number=item_data["item_number"],
                domain=item_data["domain"],
                context_text=item_data["context_text"],
                points=item_data.get("points", 6.67),
                order=item_data["item_number"],
            )
            session.add(item)
            await session.flush()

            for sq_data in item_data.get("sub_questions", []):
                sub_q = ExamSubQuestion(
                    id=uuid.uuid4(),
                    exam_item_id=item.id,
                    sub_label=sq_data["sub_label"],
                    text=sq_data["text"],
                    question_type=sq_data["question_type"],
                    correct_answer=sq_data["correct_answer"],
                    choices=sq_data.get("choices"),
                    explanation=sq_data.get("explanation"),
                    hint=sq_data.get("hint"),
                    points=sq_data.get("points", 2.22),
                    depends_on_previous=sq_data.get("depends_on_previous", False),
                    order=sq_data.get("order", 0),
                )
                session.add(sub_q)

        await session.flush()
        print(f"  [seed] CEP exam: {exam_data['title']}")


async def seed_curriculum_via_import(session) -> None:
    """Build a CurriculumImportRequest from SEED_CONTENT + content/ JSON files and run import_curriculum()."""

    # Build the base payload from SEED_CONTENT
    from app.schemas.content import (
        CurriculumDomainNode,
        CurriculumGradeNode,
        CurriculumSkillNode,
        CurriculumSubjectNode,
    )

    subjects_nodes = []
    for subj_data in SEED_CONTENT:
        domain_nodes = []
        for dom_data in subj_data["domains"]:
            skill_nodes = []
            for sk_data in dom_data["skills"]:
                skill_nodes.append(CurriculumSkillNode(
                    name=sk_data["name"],
                    order=sk_data.get("order", 0),
                ))
            domain_nodes.append(CurriculumDomainNode(
                name=dom_data["name"],
                slug=dom_data["slug"],
                order=dom_data.get("order", 0),
                skills=skill_nodes,
            ))
        subjects_nodes.append(CurriculumSubjectNode(
            name=subj_data["name"],
            slug=subj_data["slug"],
            icon=subj_data.get("icon"),
            color=subj_data.get("color"),
            order=subj_data.get("order", 0),
            domains=domain_nodes,
        ))

    payload = CurriculumImportRequest(
        grade=CurriculumGradeNode(name="CM2", slug="cm2", description="Cours Moyen 2e année — préparation CEP"),
        subjects=subjects_nodes,
    )

    print("  ── Curriculum import (base content) ──")
    result = await import_curriculum(session, payload)
    print(f"  Created: {result.created}, Updated: {result.updated}, Errors: {len(result.errors)}")

    # Import all programme files (v2.0 format): maths domains + other subjects
    all_programme_files = []
    math_programme_dir = _PROGRAMME_DIR / "mathematiques"
    if math_programme_dir.exists():
        all_programme_files.extend(sorted(math_programme_dir.glob("*.json")))
    if _PROGRAMME_DIR.exists():
        all_programme_files.extend(sorted(_PROGRAMME_DIR.glob("*.json")))

    for programme_file in all_programme_files:
        print(f"  ── Curriculum import ({programme_file.relative_to(_PROGRAMME_DIR)}) ──")
        with open(programme_file, encoding="utf-8") as f:
            v2_data = json.load(f)
        if v2_data.get("schema_version") != "2.0":
            print(f"  [skip] {programme_file.name} is not v2.0 format, skipping")
            continue
        file_payload = CurriculumImportRequest(**v2_data)
        result_file = await import_curriculum(session, file_payload)
        print(f"  Created: {result_file.created}, Updated: {result_file.updated}, "
              f"Skills: {result_file.skills}, Micro-skills: {result_file.micro_skills}, "
              f"Errors: {len(result_file.errors)}")


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        # Grade Levels
        print("── Grade Levels ──")
        cm2_grade = await _upsert(session, GradeLevel, "slug", {
            "name": "CM2", "slug": "cm2", "description": "Cours Moyen 2e année — préparation CEP", "order": 1,
        })
        await session.flush()

        # Users
        print("── Users ──")
        for u in SEED_USERS:
            pwd = u.pop("password")
            result = await session.execute(select(User).where(User.email == u["email"]))
            existing = result.scalar_one_or_none()
            if existing:
                # Assign grade_level_id to existing students
                if existing.role == UserRole.STUDENT and not existing.grade_level_id:
                    existing.grade_level_id = cm2_grade.id
                print(f"  [skip] {u['email']}")
                u["password"] = pwd
                continue
            extra = {}
            if u.get("role") == UserRole.STUDENT:
                extra["grade_level_id"] = cm2_grade.id
            user = User(id=uuid.uuid4(), hashed_password=get_password_hash(pwd), **u, **extra)
            session.add(user)
            print(f"  [seed] {u['email']}")
            u["password"] = pwd
        await session.flush()

        # Content (via curriculum import service)
        print("── Content ──")
        await seed_curriculum_via_import(session)
        # Refresh cm2_grade reference after import (may have been updated)
        result = await session.execute(select(GradeLevel).where(GradeLevel.slug == "cm2"))
        cm2_grade = result.scalar_one()

        # Questions and micro-lessons from content/benin/cm2/exercices/
        print("── Questions ──")
        exercise_data = _load_exercises_from_content()
        for slug, data in exercise_data.items():
            skill_result = await session.execute(select(Skill).where(Skill.slug == slug).limit(1))
            skill_obj = skill_result.scalars().first()
            if not skill_obj:
                print(f"  [warn] skill {slug} not found, skipping questions")
                continue

            # Seed questions
            for q_data in data.get("questions", []):
                question_row = {
                    "text": q_data["text"],
                    "question_type": _QTYPE_MAP.get(q_data["question_type"], QuestionType.MCQ),
                    "difficulty": _DIFF_MAP.get(q_data["difficulty"], DifficultyLevel.EASY),
                    "choices": q_data.get("choices"),
                    "correct_answer": q_data["correct_answer"],
                    "explanation": q_data.get("explanation"),
                    "points": q_data.get("points", 1),
                    "skill_id": skill_obj.id,
                }
                await _upsert(session, Question, "text", question_row)

            # Seed micro-lesson if present
            lesson = data.get("micro_lesson")
            if lesson:
                lesson_row = {
                    "title": lesson["title"],
                    "content_html": lesson["content_html"],
                    "summary": lesson.get("summary"),
                    "duration_minutes": lesson.get("duration_minutes", 3),
                    "skill_id": skill_obj.id,
                }
                await _upsert(session, MicroLesson, "title", lesson_row)

        await session.flush()

        # V2 exercises (converted to v1.0 format with micro_skill_external_id)
        print("── V2 Exercises ──")
        await seed_v2_exercises(session)
        await session.flush()

        # Badges
        print("── Badges ──")
        for b_data in SEED_BADGES:
            await _upsert(session, Badge, "code", b_data)
        await session.flush()

        # Plans
        print("── Plans ──")
        for p_data in SEED_PLANS:
            await _upsert(session, Plan, "tier", p_data)
        await session.flush()

        # Mock Exams (Examens Blancs)
        print("── Mock Exams ──")
        # Find the Mathématiques subject for CM2
        from app.models.content import Subject
        math_result = await session.execute(
            select(Subject).where(Subject.slug == "mathematiques").limit(1)
        )
        math_subject = math_result.scalars().first()
        if math_subject and cm2_grade:
            import datetime as dt
            seed_exams = [
                {
                    "title": "Examen Blanc Mathématiques CM2",
                    "grade_level_id": cm2_grade.id,
                    "subject_id": math_subject.id,
                    "duration_minutes": 60,
                    "total_questions": 30,
                    "question_distribution": {"easy": 10, "medium": 15, "hard": 5},
                    "is_free": True,
                    "is_national": False,
                    "is_active": True,
                },
                {
                    "title": "Examen Blanc National Mars 2026",
                    "grade_level_id": cm2_grade.id,
                    "subject_id": math_subject.id,
                    "duration_minutes": 90,
                    "total_questions": 40,
                    "question_distribution": {"easy": 12, "medium": 18, "hard": 10},
                    "is_free": False,
                    "is_national": True,
                    "national_date": dt.date(2026, 3, 28),
                    "is_active": True,
                },
            ]
            for exam_data in seed_exams:
                await _upsert(session, MockExam, "title", exam_data)
        else:
            print("  [warn] math subject or cm2 grade not found, skipping mock exams")

        # CEP-format exams (real annales) from content/benin/cm2/epreuves/
        print("── CEP Exams (Annales) ──")
        if cm2_grade:
            # Build subject map for all subjects
            from app.models.content import Subject
            all_subjects_result = await session.execute(select(Subject).where(Subject.is_active.is_(True)))
            all_subjects = list(all_subjects_result.scalars().all())
            subject_map = {}
            for s in all_subjects:
                if "math" in s.name.lower():
                    subject_map["mathematiques"] = s
                elif "scientifique" in s.name.lower() or "technologique" in s.name.lower():
                    subject_map["est"] = s
                elif "français" in s.name.lower() or "francais" in s.name.lower():
                    subject_map["francais"] = s
                elif "sociale" in s.name.lower():
                    subject_map["education_sociale"] = s
            await seed_cep_exams(session, cm2_grade, subject_map)
        else:
            print("  [warn] cm2 grade not found, skipping CEP exams")

        await session.commit()
    print("\nSeed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
