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
from app.models.mock_exam import MockExam
from app.models.subscription import Plan, PlanTier
from app.models.user import User, UserRole
from app.schemas.content import CurriculumImportRequest
from app.services.curriculum_import_service import import_curriculum
from app.scripts.convert_legacy_json import convert as convert_legacy

# Resolve path to the curriculum JSON directory
# Inside container: /app/cm2_maths/  |  Local dev: backend/cm2_maths/
# Inside container: /app/app/scripts/seed.py → parents[2] = /app
# Local dev: backend/app/scripts/seed.py → parents[2] = backend/
_WORKDIR = pathlib.Path(__file__).resolve().parents[2]
_CM2_MATHS_DIR = _WORKDIR / "cm2_maths"

# ── Users ──────────────────────────────────────────────────
SEED_USERS = [
    {"email": "admin@ilma.bj", "full_name": "Administrateur ILMA", "role": UserRole.ADMIN, "password": "Xr;aTRKMx_1CI1Wd@HF1c!9"},
    {"email": "parent@ilma.bj", "full_name": "Koffi Mensah", "role": UserRole.PARENT, "password": "Xr;aTRKMx_1CI1Wd@HF1c!9"},
    {"email": "eleve@ilma.bj", "full_name": "Afi Mensah", "role": UserRole.STUDENT, "password": "Xr;aTRKMx_1CI1Wd@HF1c!9"},
    {"email": "eleve2@ilma.bj", "full_name": "Kofi Junior", "role": UserRole.STUDENT, "password": "Xr;aTRKMx_1CI1Wd@HF1c!9"},
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
    {"name": "Basique", "tier": PlanTier.BASIC, "price_xof": 1000, "duration_days": 30, "features": {"max_exercises_day": 20, "exam_blanc": False}},
    {"name": "Premium", "tier": PlanTier.PREMIUM, "price_xof": 2500, "duration_days": 30, "features": {"max_exercises_day": -1, "exam_blanc": True}},
]

# ── Questions par compétence (slug → questions) ──────────
# Slugs match the external_ids from curriculum JSON files (slugified).
QUESTIONS_BY_SKILL = {
    "num-entiers-0-1b": [
        {"text": "Comment écrit-on le nombre 2 456 en lettres ?", "question_type": QuestionType.MCQ, "difficulty": DifficultyLevel.EASY,
         "choices": ["deux mille quatre cent cinquante-six", "deux milles quatre cents cinquante-six", "deux-mille-quatre-cent-cinquante-six", "deux mil quatre cent cinquante six"],
         "correct_answer": "deux mille quatre cent cinquante-six", "explanation": "On écrit 'mille' sans 's' et 'cent' sans 's' quand il est suivi d'un autre nombre.", "points": 1},
        {"text": "Quel est le chiffre des centaines dans 8 375 ?", "question_type": QuestionType.MCQ, "difficulty": DifficultyLevel.EASY,
         "choices": ["8", "3", "7", "5"], "correct_answer": "3", "explanation": "Dans 8 375 : 8 milliers, 3 centaines, 7 dizaines, 5 unités.", "points": 1},
        {"text": "1 250 > 1 520", "question_type": QuestionType.TRUE_FALSE, "difficulty": DifficultyLevel.EASY,
         "choices": ["Vrai", "Faux"], "correct_answer": "Faux", "explanation": "1 250 est inférieur à 1 520.", "points": 1},
        {"text": "Combien de dizaines y a-t-il dans 4 930 ?", "question_type": QuestionType.MCQ, "difficulty": DifficultyLevel.MEDIUM,
         "choices": ["493", "93", "3", "49"], "correct_answer": "493", "explanation": "4 930 ÷ 10 = 493 dizaines.", "points": 2},
        {"text": "Quel nombre vient juste après 9 999 ?", "question_type": QuestionType.FILL_BLANK, "difficulty": DifficultyLevel.EASY,
         "choices": None, "correct_answer": "10000", "explanation": "9 999 + 1 = 10 000.", "points": 1},
    ],
    "num-droite-num-entiers": [
        {"text": "Range du plus petit au plus grand : 482, 248, 824", "question_type": QuestionType.MCQ, "difficulty": DifficultyLevel.EASY,
         "choices": ["248, 482, 824", "482, 248, 824", "824, 482, 248", "248, 824, 482"], "correct_answer": "248, 482, 824", "explanation": "On compare chiffre par chiffre en partant de la gauche.", "points": 1},
        {"text": "3 456 < 3 465", "question_type": QuestionType.TRUE_FALSE, "difficulty": DifficultyLevel.EASY,
         "choices": ["Vrai", "Faux"], "correct_answer": "Vrai", "explanation": "Les milliers et centaines sont égaux, mais 5 dizaines < 6 dizaines.", "points": 1},
        {"text": "Quel signe convient ? 7 891 … 7 819", "question_type": QuestionType.MCQ, "difficulty": DifficultyLevel.EASY,
         "choices": [">", "<", "="], "correct_answer": ">", "explanation": "7 891 > 7 819 car 9 dizaines > 1 dizaine.", "points": 1},
    ],
    "ops-tech-entiers": [
        {"text": "Combien font 1 547 + 2 368 ?", "question_type": QuestionType.MCQ, "difficulty": DifficultyLevel.EASY,
         "choices": ["3 915", "3 815", "3 905", "4 915"], "correct_answer": "3 915", "explanation": "On additionne colonne par colonne avec les retenues.", "points": 1},
        {"text": "5 000 − 1 237 = ?", "question_type": QuestionType.FILL_BLANK, "difficulty": DifficultyLevel.MEDIUM,
         "choices": None, "correct_answer": "3763", "explanation": "5 000 − 1 237 = 3 763.", "points": 2},
        {"text": "Combien font 25 × 4 ?", "question_type": QuestionType.MCQ, "difficulty": DifficultyLevel.EASY,
         "choices": ["100", "80", "125", "104"], "correct_answer": "100", "explanation": "25 × 4 = 100. C'est un résultat à retenir !", "points": 1},
        {"text": "347 × 6 = ?", "question_type": QuestionType.FILL_BLANK, "difficulty": DifficultyLevel.MEDIUM,
         "choices": None, "correct_answer": "2082", "explanation": "347 × 6 : (7×6=42, retenue 4) (4×6=24+4=28, retenue 2) (3×6=18+2=20) → 2 082.", "points": 2},
        {"text": "Combien font 144 ÷ 12 ?", "question_type": QuestionType.MCQ, "difficulty": DifficultyLevel.MEDIUM,
         "choices": ["12", "11", "13", "14"], "correct_answer": "12", "explanation": "12 × 12 = 144, donc 144 ÷ 12 = 12.", "points": 2},
        {"text": "Quel est le quotient de 85 ÷ 5 ?", "question_type": QuestionType.FILL_BLANK, "difficulty": DifficultyLevel.EASY,
         "choices": None, "correct_answer": "17", "explanation": "85 ÷ 5 = 17.", "points": 1},
    ],
    "ops-calcul-mental": [
        {"text": "Le double de 450 est 900.", "question_type": QuestionType.TRUE_FALSE, "difficulty": DifficultyLevel.EASY,
         "choices": ["Vrai", "Faux"], "correct_answer": "Vrai", "explanation": "450 × 2 = 900.", "points": 1},
        {"text": "12 + 8 = 20", "question_type": QuestionType.TRUE_FALSE, "difficulty": DifficultyLevel.EASY,
         "choices": ["Vrai", "Faux"], "correct_answer": "Vrai", "explanation": "12 + 8 = 20.", "points": 1},
    ],
}

# ── Micro-leçons (une par compétence) ────────────────────
# Slugs match the external_ids from curriculum JSON files (slugified).
SEED_LESSONS = {
    "num-entiers-0-1b": {
        "title": "Lire et écrire les nombres entiers",
        "content_html": "<h2>Les nombres entiers</h2><p>Un nombre entier est composé de <b>chiffres</b> (0 à 9). La <b>position</b> de chaque chiffre détermine sa valeur :</p><ul><li><b>Unités</b> (à droite)</li><li><b>Dizaines</b></li><li><b>Centaines</b></li><li><b>Milliers</b></li><li><b>Millions</b></li><li><b>Milliards</b></li></ul><p>Exemple : dans <b>3 450 000</b>, le 3 vaut 3 millions, le 4 vaut 4 centaines de mille, le 5 vaut 5 dizaines de mille.</p><h3>Règle d'écriture</h3><p>« Mille » ne prend <b>jamais</b> de « s ». « Cent » prend un « s » seulement quand il est multiplié et non suivi d'un autre nombre (ex: deux cents, mais deux cent trois).</p>",
        "summary": "Position des chiffres et règles d'écriture des nombres en lettres (0 à 1 milliard).",
        "duration_minutes": 3,
    },
    "ops-tech-entiers": {
        "title": "Les techniques opératoires écrites (entiers)",
        "content_html": "<h2>Poser une addition</h2><p>Aligne les chiffres par colonne (unités sous unités, dizaines sous dizaines…). Additionne de <b>droite à gauche</b>. Si le résultat dépasse 9, <b>retiens</b> la dizaine.</p><h2>Poser une soustraction</h2><p>Même principe : aligne les colonnes. Si le chiffre du haut est plus petit, <b>emprunte</b> une dizaine à la colonne de gauche.</p><h2>La multiplication posée</h2><p>Multiplie le nombre du haut par chaque chiffre du nombre du bas, en décalant d'une colonne à chaque ligne. Additionne les résultats partiels.</p><h2>La division posée</h2><p>Divise chiffre par chiffre, de la gauche vers la droite. Note le quotient au-dessus et le reste en dessous. Vérifie : quotient × diviseur + reste = dividende.</p>",
        "summary": "Techniques de l'addition, soustraction, multiplication et division posées.",
        "duration_minutes": 5,
    },
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


async def seed_curriculum_via_import(session) -> None:
    """Build a CurriculumImportRequest from SEED_CONTENT + legacy JSON and run import_curriculum()."""

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

    # Import all domain JSON files from cm2_maths/
    if _CM2_MATHS_DIR.exists():
        domain_files = sorted(_CM2_MATHS_DIR.glob("progamme_mathematiquesCM2_deeeep_*.json"))
        for domain_file in domain_files:
            domain_tag = domain_file.stem.split("_")[-1]  # e.g. NUM, OPS, GEO...
            print(f"  ── Curriculum import ({domain_tag}) ──")
            with open(domain_file, encoding="utf-8") as f:
                legacy_data = json.load(f)
            v2_data = convert_legacy(legacy_data)
            legacy_payload = CurriculumImportRequest(**v2_data)
            result_domain = await import_curriculum(session, legacy_payload)
            print(f"  Created: {result_domain.created}, Updated: {result_domain.updated}, "
                  f"Skills: {result_domain.skills}, Micro-skills: {result_domain.micro_skills}, "
                  f"Errors: {len(result_domain.errors)}")
    else:
        print(f"  [skip] cm2_maths directory not found at {_CM2_MATHS_DIR}")


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

        # Questions per skill
        print("── Questions ──")
        for slug, questions in QUESTIONS_BY_SKILL.items():
            skill_result = await session.execute(select(Skill).where(Skill.slug == slug).limit(1))
            skill_obj = skill_result.scalars().first()
            if not skill_obj:
                print(f"  [warn] skill {slug} not found, skipping questions")
                continue
            for q_data in questions:
                q_data["skill_id"] = skill_obj.id
                await _upsert(session, Question, "text", q_data)
        await session.flush()

        # Micro-lessons
        print("── Micro-leçons ──")
        for slug, lesson_data in SEED_LESSONS.items():
            skill_result = await session.execute(select(Skill).where(Skill.slug == slug).limit(1))
            skill_obj = skill_result.scalars().first()
            if not skill_obj:
                continue
            lesson_data["skill_id"] = skill_obj.id
            await _upsert(session, MicroLesson, "title", lesson_data)
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

        await session.commit()
    print("\nSeed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
