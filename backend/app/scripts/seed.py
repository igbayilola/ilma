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
from app.models.mock_exam import MockExam, ExamItem, ExamSubQuestion
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


async def seed_cep_exams(session, cm2_grade, math_subject) -> None:
    """Seed the 4 real CEP exams from past annales."""
    CEP_EXAMS = [
        {
            "title": "CEP 2024 Session Normale — Mathématiques",
            "context_text": "Dans le cadre de la riposte contre le COVID 19, le gouvernement du Bénin avait lancé le 06 mai 2020 un appel aux artisans locaux pour confectionner des masques en tissu. Cette opération avait pris fin le 16 mai 2020. Au cours de cette période, la couturière Sènanmi a cousu 8600 masques en tissu de différentes couleurs : bleu, vert et jaune.",
            "items": [
                {
                    "item_number": 1, "domain": "data_proportionality",
                    "context_text": "La couturière Sènanmi a cousu 8600 masques en tissu de différentes couleurs : bleu (40%), vert (35%) et jaune (25%).",
                    "sub_questions": [
                        {"sub_label": "a", "text": "Dresse le tableau des effectifs de cette série statistique.", "question_type": "fill_blank", "correct_answer": "Bleu: 3440, Vert: 3010, Jaune: 2150", "explanation": "Bleu: 8600 × 40/100 = 3440. Vert: 8600 × 35/100 = 3010. Jaune: 8600 × 25/100 = 2150.", "order": 0},
                        {"sub_label": "b", "text": "Complète-le par des fréquences par fraction.", "question_type": "fill_blank", "correct_answer": "Bleu: 4/10, Vert: 35/100, Jaune: 1/4", "explanation": "Bleu: 3440/8600 = 4/10. Vert: 3010/8600 = 35/100. Jaune: 2150/8600 = 1/4.", "depends_on_previous": True, "order": 1},
                        {"sub_label": "c", "text": "Complète-le par des fréquences exprimées sous forme de pourcentage.", "question_type": "fill_blank", "correct_answer": "Bleu: 40%, Vert: 35%, Jaune: 25%", "explanation": "Les pourcentages correspondent directement aux données du diagramme circulaire.", "depends_on_previous": True, "order": 2},
                    ],
                },
                {
                    "item_number": 2, "domain": "measures_operations",
                    "context_text": "Les masques sont rangés dans des boîtes puis dans des cartons. Une boîte mesure 20 cm × 10 cm × 8 cm. Un carton mesure 60 cm × 40 cm × 50 cm.",
                    "sub_questions": [
                        {"sub_label": "a", "text": "Calcule le volume d'une boîte. (20 cm × 10 cm × 8 cm)", "question_type": "numeric_input", "correct_answer": "1600", "explanation": "V = L × l × h = 20 × 10 × 8 = 1 600 cm³", "order": 0},
                        {"sub_label": "b", "text": "Calcule le volume d'un carton. (60 cm × 40 cm × 50 cm)", "question_type": "numeric_input", "correct_answer": "120000", "explanation": "V = 60 × 40 × 50 = 120 000 cm³", "order": 1},
                        {"sub_label": "c", "text": "Détermine le nombre de boîtes que peut contenir un carton.", "question_type": "numeric_input", "correct_answer": "75", "depends_on_previous": True, "explanation": "120 000 ÷ 1 600 = 75 boîtes", "hint": "Utilise les résultats des questions a) et b).", "order": 2},
                    ],
                },
                {
                    "item_number": 3, "domain": "geometry",
                    "context_text": "On considère la base ABCD d'un carton de dimensions 60 cm × 40 cm.",
                    "sub_questions": [
                        {"sub_label": "a", "text": "Représente à l'échelle de 1/10 la base ABCD d'un carton.", "question_type": "mcq", "choices": ["Rectangle 6cm × 4cm", "Rectangle 60cm × 40cm", "Carré 6cm × 6cm", "Rectangle 3cm × 2cm"], "correct_answer": "Rectangle 6cm × 4cm", "explanation": "Échelle 1/10 : 60cm ÷ 10 = 6cm et 40cm ÷ 10 = 4cm.", "order": 0},
                        {"sub_label": "b", "text": "Trace les diagonales de cette figure.", "question_type": "mcq", "choices": ["Deux segments reliant les sommets opposés", "Deux segments reliant les milieux des côtés", "Un seul segment diagonal"], "correct_answer": "Deux segments reliant les sommets opposés", "explanation": "Les diagonales d'un rectangle relient les sommets opposés : AC et BD.", "order": 1},
                        {"sub_label": "c", "text": "Trace la figure symétrique du triangle ABC par rapport au point C.", "question_type": "mcq", "choices": ["Triangle BCE avec E symétrique de A par rapport à C", "Triangle identique à ABC", "Triangle inversé par rapport à la diagonale"], "correct_answer": "Triangle BCE avec E symétrique de A par rapport à C", "explanation": "Le symétrique de A par rapport à C est le point E tel que C est le milieu de [AE].", "order": 2},
                    ],
                },
            ],
        },
        {
            "title": "CEP 2019 Session Normale — Mathématiques",
            "context_text": "Pour les fêtes de retrouvaille, le comité d'organisation décide d'acheter 20 bouteilles de Fanta à 7 000 F, 150 bouteilles d'eau à 52 500 F, des bouteilles de bières pour 10 500 F et 50 bouteilles de Coca-Cola. Pour recevoir les invités, un espace est aménagé.",
            "items": [
                {
                    "item_number": 1, "domain": "data_proportionality",
                    "context_text": "Le comité achète : 20 bouteilles de Fanta à 7 000 F, 150 bouteilles d'eau à 52 500 F, des bouteilles de bières pour 10 500 F et 50 bouteilles de Coca-Cola.",
                    "sub_questions": [
                        {"sub_label": "a", "text": "Présente les données dans un tableau de correspondance.", "question_type": "fill_blank", "correct_answer": "Fanta: 20 bouteilles = 7000F, Eau: 150 bouteilles = 52500F, Bière: ? bouteilles = 10500F, Coca: 50 bouteilles = ?", "explanation": "On organise les données en colonnes : boisson, nombre de bouteilles, prix total.", "order": 0},
                        {"sub_label": "b", "text": "Dis si ce tableau est un tableau de proportionnalité.", "question_type": "true_false", "correct_answer": "Faux", "explanation": "Les prix unitaires sont différents : Fanta = 350 F, Eau = 350 F, mais ce n'est pas constant pour tous les produits.", "order": 1},
                        {"sub_label": "c", "text": "Calcule le montant à payer pour les bouteilles de Coca-Cola et le nombre de bouteilles de bières à acheter.", "question_type": "numeric_input", "correct_answer": "17500", "depends_on_previous": True, "explanation": "Prix unitaire = 350 F. Coca : 50 × 350 = 17 500 F. Bières : 10 500 ÷ 350 = 30 bouteilles.", "hint": "Utilise le prix unitaire trouvé à la question précédente.", "order": 2},
                    ],
                },
                {
                    "item_number": 2, "domain": "measures_operations",
                    "context_text": "Pour recevoir les invités, un espace rectangulaire de 60 m × 40 m est aménagé sous une bâche.",
                    "sub_questions": [
                        {"sub_label": "a", "text": "Calcule l'aire de l'espace occupé par la bâche. (60 m × 40 m)", "question_type": "numeric_input", "correct_answer": "2400", "explanation": "A = 60 × 40 = 2 400 m²", "order": 0},
                        {"sub_label": "b", "text": "Sachant que chaque invité doit occuper une superficie de 6 m², détermine le nombre d'invités.", "question_type": "numeric_input", "correct_answer": "400", "depends_on_previous": True, "explanation": "2 400 ÷ 6 = 400 invités", "hint": "Utilise l'aire calculée à la question a).", "order": 1},
                        {"sub_label": "c", "text": "Quel est le périmètre du domaine ?", "question_type": "numeric_input", "correct_answer": "200", "explanation": "P = 2 × (60 + 40) = 200 m", "order": 2},
                    ],
                },
                {
                    "item_number": 3, "domain": "geometry",
                    "context_text": "L'espace rectangulaire mesure 60 m × 40 m.",
                    "sub_questions": [
                        {"sub_label": "a", "text": "Construis ce rectangle à l'échelle de 1/1000.", "question_type": "mcq", "choices": ["Rectangle 6cm × 4cm", "Rectangle 60cm × 40cm", "Rectangle 0.6cm × 0.4cm"], "correct_answer": "Rectangle 6cm × 4cm", "explanation": "Échelle 1/1000 : 60m = 6000cm ÷ 1000 = 6cm. 40m = 4000cm ÷ 1000 = 4cm.", "order": 0},
                        {"sub_label": "b", "text": "Place un point I à l'extérieur du rectangle.", "question_type": "mcq", "choices": ["Un point situé hors du rectangle", "Un point au centre", "Un point sur un côté"], "correct_answer": "Un point situé hors du rectangle", "explanation": "Un point extérieur est situé en dehors des côtés du rectangle.", "order": 1},
                        {"sub_label": "c", "text": "Construis le symétrique de ce rectangle par rapport au point I.", "question_type": "mcq", "choices": ["Un rectangle de mêmes dimensions de l'autre côté de I", "Un rectangle réduit de moitié", "Le même rectangle retourné"], "correct_answer": "Un rectangle de mêmes dimensions de l'autre côté de I", "explanation": "Le symétrique par rapport à un point conserve les dimensions. Chaque sommet a son symétrique de l'autre côté de I, à égale distance.", "order": 2},
                    ],
                },
            ],
        },
        {
            "title": "CEP 2018 Session des Malades — Mathématiques",
            "context_text": "Après leur formation au lycée agricole Mèdji de Sékou, Suzanne et Paul décident d'installer ensemble une ferme à Pahou pour y élever de la volaille. Le terrain qu'ils ont acheté a une forme rectangulaire qui mesure 125 m de longueur sur 75 m de largeur.",
            "items": [
                {
                    "item_number": 1, "domain": "data_proportionality",
                    "context_text": "Les poussins commandés coûtent 600 000 francs CFA. Suzanne paie les 3/5 de ce montant et Paul le reste. Les élèves de 3ème année du lycée d'Adja-Ouèrè visitent la ferme. Transport : 162 700 F. Le lycée paie 92 500 F. Chaque élève cotise 2 600 F.",
                    "sub_questions": [
                        {"sub_label": "a", "text": "Les poussins commandés coûtent 600 000 francs CFA. Suzanne paie les 3/5 de ce montant et Paul le reste. Détermine le montant payé par chacun.", "question_type": "numeric_input", "correct_answer": "360000", "explanation": "Suzanne : 3/5 × 600 000 = 360 000 F. Paul : 600 000 - 360 000 = 240 000 F.", "order": 0},
                        {"sub_label": "b", "text": "Les élèves de 3ème année du lycée d'Adja-Ouèrè visitent. Transport : 162 700 F. Le lycée paie 92 500 F. Chaque élève cotise 2 600 F. Calcule le nombre d'élèves.", "question_type": "numeric_input", "correct_answer": "27", "explanation": "Reste : 162 700 - 92 500 = 70 200 F. Élèves : 70 200 ÷ 2 600 = 27.", "order": 1},
                        {"sub_label": "c", "text": "Les sacs de provende : 2 sacs = 25 000 F, 3 sacs = 37 500 F, 5 sacs = 62 500 F. Calcule le nombre de sacs qu'on peut acheter avec 87 500 F.", "question_type": "numeric_input", "correct_answer": "7", "explanation": "Prix unitaire : 12 500 F. 87 500 ÷ 12 500 = 7 sacs.", "order": 2},
                    ],
                },
                {
                    "item_number": 2, "domain": "measures_operations",
                    "context_text": "Les sacs de provende coûtent : 2 sacs = 25 000 F, 3 sacs = 37 500 F, 5 sacs = 62 500 F.",
                    "sub_questions": [
                        {"sub_label": "a", "text": "Présente ces données dans un tableau de correspondance.", "question_type": "fill_blank", "correct_answer": "2 sacs: 25000F, 3 sacs: 37500F, 5 sacs: 62500F", "explanation": "On organise les données : nombre de sacs et prix correspondant.", "order": 0},
                        {"sub_label": "b", "text": "Dis s'il s'agit d'une situation de proportionnalité. Justifie.", "question_type": "true_false", "correct_answer": "Vrai", "explanation": "Prix unitaire constant : 25 000 ÷ 2 = 12 500 F. 37 500 ÷ 3 = 12 500 F. 62 500 ÷ 5 = 12 500 F.", "order": 1},
                        {"sub_label": "c", "text": "Calcule le nombre de sacs de provende qu'on peut acheter avec 87 500 F.", "question_type": "numeric_input", "correct_answer": "7", "depends_on_previous": True, "explanation": "87 500 ÷ 12 500 = 7 sacs.", "hint": "Utilise le prix unitaire trouvé à la question précédente.", "order": 2},
                    ],
                },
                {
                    "item_number": 3, "domain": "geometry",
                    "context_text": "Le terrain rectangulaire mesure 125 m de longueur sur 75 m de largeur.",
                    "sub_questions": [
                        {"sub_label": "a", "text": "Détermine les dimensions réduites du terrain à l'échelle 1/2500.", "question_type": "fill_blank", "correct_answer": "5 cm × 3 cm", "explanation": "125 m = 12 500 cm ÷ 2 500 = 5 cm. 75 m = 7 500 cm ÷ 2 500 = 3 cm.", "order": 0},
                        {"sub_label": "b", "text": "Représente cette figure sur ta feuille.", "question_type": "mcq", "choices": ["Rectangle 5cm × 3cm", "Rectangle 12.5cm × 7.5cm", "Carré 5cm × 5cm"], "correct_answer": "Rectangle 5cm × 3cm", "explanation": "D'après le calcul de la question a), le rectangle réduit mesure 5 cm × 3 cm.", "depends_on_previous": True, "order": 1},
                        {"sub_label": "c", "text": "Trace son symétrique par rapport à une droite OD placée à l'intérieur de la figure.", "question_type": "mcq", "choices": ["Rectangle symétrique par rapport à OD", "Même rectangle décalé", "Rectangle réduit"], "correct_answer": "Rectangle symétrique par rapport à OD", "explanation": "Le symétrique par rapport à une droite est une figure de mêmes dimensions, reflétée de l'autre côté de la droite.", "order": 2},
                    ],
                },
            ],
        },
        {
            "title": "CEP 2019 Session des Malades — Mathématiques",
            "context_text": "Codjo est un maraîcher. Il dispose d'un domaine de 150 m de long sur 80 m de large qu'il veut exploiter. Pour cela, il demande et obtient auprès d'une banque un prêt de 2 500 000 FCFA au taux annuel de 12%.",
            "items": [
                {
                    "item_number": 1, "domain": "measures_operations",
                    "context_text": "Le domaine de Codjo mesure 150 m de long sur 80 m de large.",
                    "sub_questions": [
                        {"sub_label": "a", "text": "Calcule en hectare (ha) la superficie du domaine à exploiter.", "question_type": "numeric_input", "correct_answer": "1.2", "explanation": "150 × 80 = 12 000 m² = 1,2 ha (1 ha = 10 000 m²).", "order": 0},
                        {"sub_label": "b", "text": "Détermine l'aire de la superficie occupée par les produits. (Le plan montre des allées de 2 m.)", "question_type": "numeric_input", "correct_answer": "11200", "depends_on_previous": True, "explanation": "Aire totale moins l'aire des allées. Aire utile = 11 200 m².", "hint": "Soustrais l'aire des allées de l'aire totale.", "order": 1},
                        {"sub_label": "c", "text": "Calcule le nombre de planches que l'on peut installer sur cette superficie utile. (Chaque planche = 5 m × 2 m)", "question_type": "numeric_input", "correct_answer": "1120", "depends_on_previous": True, "explanation": "Aire d'une planche = 5 × 2 = 10 m². 11 200 ÷ 10 = 1 120 planches.", "hint": "Utilise la superficie utile de la question b).", "order": 2},
                    ],
                },
                {
                    "item_number": 2, "domain": "geometry",
                    "context_text": "Une planche rectangulaire mesure 5 m × 2 m.",
                    "sub_questions": [
                        {"sub_label": "a", "text": "Reproduis à l'échelle de 1/100 une planche. (rectangulaire 5 m × 2 m)", "question_type": "mcq", "choices": ["Rectangle 5cm × 2cm", "Rectangle 50cm × 20cm", "Rectangle 0.5cm × 0.2cm"], "correct_answer": "Rectangle 5cm × 2cm", "explanation": "Échelle 1/100 : 5 m = 500 cm ÷ 100 = 5 cm. 2 m = 200 cm ÷ 100 = 2 cm.", "order": 0},
                        {"sub_label": "b", "text": "Trace son symétrique par rapport à une droite (D) placée hors du rectangle.", "question_type": "mcq", "choices": ["Rectangle symétrique de l'autre côté de D", "Même rectangle sur D", "Rectangle réduit"], "correct_answer": "Rectangle symétrique de l'autre côté de D", "explanation": "Le symétrique par rapport à une droite est une figure de mêmes dimensions reflétée de l'autre côté de (D).", "order": 1},
                        {"sub_label": "c", "text": "Indique la nature du quadrilatère formé par la planche et son symétrique.", "question_type": "mcq", "choices": ["Un hexagone", "Deux rectangles symétriques", "Un losange"], "correct_answer": "Deux rectangles symétriques", "explanation": "La figure et son symétrique forment deux rectangles identiques de part et d'autre de (D).", "order": 2},
                    ],
                },
                {
                    "item_number": 3, "domain": "data_proportionality",
                    "context_text": "Codjo obtient un prêt de 2 500 000 FCFA au taux annuel de 12 %. Il rembourse au bout de 6 mois.",
                    "sub_questions": [
                        {"sub_label": "a", "text": "Calcule l'intérêt annuel du prêt effectué par Codjo.", "question_type": "numeric_input", "correct_answer": "300000", "explanation": "I = C × t = 2 500 000 × 12/100 = 300 000 F.", "order": 0},
                        {"sub_label": "b", "text": "Calcule l'intérêt payé au bout de 6 mois.", "question_type": "numeric_input", "correct_answer": "150000", "depends_on_previous": True, "explanation": "300 000 × 6/12 = 150 000 F.", "hint": "Utilise l'intérêt annuel de la question a).", "order": 1},
                        {"sub_label": "c", "text": "Calcule le montant remboursé par Codjo.", "question_type": "numeric_input", "correct_answer": "2650000", "depends_on_previous": True, "explanation": "2 500 000 + 150 000 = 2 650 000 F.", "hint": "Additionne le capital et l'intérêt de la question b).", "order": 2},
                    ],
                },
            ],
        },
    ]

    for exam_data in CEP_EXAMS:
        # Check if exam already exists
        result = await session.execute(
            select(MockExam).where(MockExam.title == exam_data["title"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            print(f"  [skip] CEP exam: {exam_data['title']}")
            continue

        mock_exam = MockExam(
            id=uuid.uuid4(),
            grade_level_id=cm2_grade.id,
            subject_id=math_subject.id,
            title=exam_data["title"],
            duration_minutes=60,
            total_questions=9,  # 3 items × 3 sub-questions
            exam_type="cep",
            context_text=exam_data["context_text"],
            is_free=True,
            is_national=False,
            is_active=True,
        )
        session.add(mock_exam)
        await session.flush()

        for item_data in exam_data["items"]:
            item = ExamItem(
                id=uuid.uuid4(),
                mock_exam_id=mock_exam.id,
                item_number=item_data["item_number"],
                domain=item_data["domain"],
                context_text=item_data["context_text"],
                points=6.67,
                order=item_data["item_number"],
            )
            session.add(item)
            await session.flush()

            for sq_data in item_data["sub_questions"]:
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
                    points=2.22,
                    depends_on_previous=sq_data.get("depends_on_previous", False),
                    order=sq_data["order"],
                )
                session.add(sub_q)

        await session.flush()
        print(f"  [seed] CEP exam: {exam_data['title']}")


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

        # CEP-format exams (real annales)
        print("── CEP Exams (Annales) ──")
        if math_subject and cm2_grade:
            await seed_cep_exams(session, cm2_grade, math_subject)
        else:
            print("  [warn] math subject or cm2 grade not found, skipping CEP exams")

        await session.commit()
    print("\nSeed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
