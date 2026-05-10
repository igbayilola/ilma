"""Content endpoint tests — subjects, domains, skills, questions."""
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import (
    DifficultyLevel,
    Domain,
    MicroLesson,
    MicroSkill,
    Question,
    QuestionType,
    Skill,
    Subject,
)
from tests.conftest import auth_header


@pytest.fixture
async def content_tree(db_session: AsyncSession):
    """Create a full content tree: subject -> domain -> skill -> questions + lesson."""
    subj = Subject(
        id=uuid.uuid4(),
        name="Mathematiques",
        slug="math-content-test",
        description="Math subject",
        icon="calculator",
        color="#3B82F6",
        order=1,
    )
    db_session.add(subj)
    await db_session.flush()

    domain = Domain(
        id=uuid.uuid4(),
        name="Numeration",
        slug="num-content-test",
        subject_id=subj.id,
        description="Numbers chapter",
        order=1,
    )
    db_session.add(domain)
    await db_session.flush()

    skill = Skill(
        id=uuid.uuid4(),
        name="Addition",
        slug="add-content-test",
        domain_id=domain.id,
        description="Basic addition",
        order=1,
    )
    db_session.add(skill)
    await db_session.flush()

    questions = []
    for i in range(3):
        q = Question(
            id=uuid.uuid4(),
            skill_id=skill.id,
            text=f"Combien font 2 + {i} ?",
            question_type=QuestionType.MCQ,
            difficulty=DifficultyLevel.EASY,
            choices=[str(2 + i), "99", "0"],
            correct_answer=str(2 + i),
            points=1,
        )
        db_session.add(q)
        questions.append(q)

    lesson = MicroLesson(
        id=uuid.uuid4(),
        skill_id=skill.id,
        title="Introduction a l'addition",
        content_html="<p>L'addition consiste a combiner deux nombres.</p>",
        summary="Les bases de l'addition",
        duration_minutes=5,
        order=1,
    )
    db_session.add(lesson)
    await db_session.flush()

    return {"subject": subj, "domain": domain, "skill": skill, "questions": questions, "lesson": lesson}


@pytest.fixture
async def second_subject(db_session: AsyncSession):
    """Create a second subject to test listing multiple."""
    subj = Subject(
        id=uuid.uuid4(),
        name="Francais",
        slug="fr-content-test",
        order=2,
    )
    db_session.add(subj)
    await db_session.flush()
    return subj


# ── Subject listing ────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_subjects(client: AsyncClient, test_student, content_tree):
    resp = await client.get("/api/v1/subjects", headers=auth_header(test_student))
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    subjects = body["data"]
    assert len(subjects) >= 1
    assert any(s["name"] == "Mathematiques" for s in subjects)


@pytest.mark.asyncio
async def test_list_subjects_multiple(
    client: AsyncClient, test_student, content_tree, second_subject
):
    resp = await client.get("/api/v1/subjects", headers=auth_header(test_student))
    assert resp.status_code == 200
    subjects = resp.json()["data"]
    assert len(subjects) >= 2
    names = {s["name"] for s in subjects}
    assert "Mathematiques" in names
    assert "Francais" in names


@pytest.mark.asyncio
async def test_list_subjects_unauthenticated(client: AsyncClient):
    resp = await client.get("/api/v1/subjects")
    assert resp.status_code == 401


# ── Single subject ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_subject(client: AsyncClient, test_student, content_tree):
    subj_id = str(content_tree["subject"].id)
    resp = await client.get(f"/api/v1/subjects/{subj_id}", headers=auth_header(test_student))
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["name"] == "Mathematiques"
    assert data["slug"] == "math-content-test"
    assert data["id"] == subj_id


@pytest.mark.asyncio
async def test_get_subject_not_found(client: AsyncClient, test_student):
    fake_id = str(uuid.uuid4())
    resp = await client.get(f"/api/v1/subjects/{fake_id}", headers=auth_header(test_student))
    assert resp.status_code == 404


# ── Domain (chapter) listing ──────────────────────────────


@pytest.mark.asyncio
async def test_list_domains(client: AsyncClient, test_student, content_tree):
    subj_id = str(content_tree["subject"].id)
    resp = await client.get(
        f"/api/v1/subjects/{subj_id}/chapters", headers=auth_header(test_student)
    )
    assert resp.status_code == 200
    domains = resp.json()["data"]
    assert len(domains) >= 1
    assert domains[0]["name"] == "Numeration"
    assert domains[0]["subject_id"] == subj_id


@pytest.mark.asyncio
async def test_list_domains_empty(client: AsyncClient, test_student, second_subject):
    subj_id = str(second_subject.id)
    resp = await client.get(
        f"/api/v1/subjects/{subj_id}/chapters", headers=auth_header(test_student)
    )
    assert resp.status_code == 200
    assert resp.json()["data"] == []


# ── Skill listing ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_skills(client: AsyncClient, test_student, content_tree):
    subj_id = str(content_tree["subject"].id)
    domain_id = str(content_tree["domain"].id)
    resp = await client.get(
        f"/api/v1/subjects/{subj_id}/chapters/{domain_id}/skills",
        headers=auth_header(test_student),
    )
    assert resp.status_code == 200
    skills = resp.json()["data"]["items"]
    assert len(skills) >= 1
    assert skills[0]["name"] == "Addition"


# ── Skill detail with lessons ─────────────────────────────


@pytest.mark.asyncio
async def test_get_skill_with_lessons(client: AsyncClient, test_student, content_tree):
    skill_id = str(content_tree["skill"].id)
    resp = await client.get(
        f"/api/v1/subjects/skills/{skill_id}", headers=auth_header(test_student)
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["skill"]["name"] == "Addition"
    assert len(data["lessons"]) >= 1
    assert data["lessons"][0]["title"] == "Introduction a l'addition"


@pytest.mark.asyncio
async def test_get_skill_not_found(client: AsyncClient, test_student):
    fake_id = str(uuid.uuid4())
    resp = await client.get(
        f"/api/v1/subjects/skills/{fake_id}", headers=auth_header(test_student)
    )
    assert resp.status_code == 404


# ── Question listing ──────────────────────────────────────


@pytest.mark.asyncio
async def test_list_questions(client: AsyncClient, test_student, content_tree):
    skill_id = str(content_tree["skill"].id)
    resp = await client.get(
        f"/api/v1/subjects/skills/{skill_id}/questions",
        headers=auth_header(test_student),
    )
    assert resp.status_code == 200
    questions = resp.json()["data"]["items"]
    assert len(questions) == 3
    # Verify question structure
    q = questions[0]
    assert "text" in q
    assert "choices" in q
    assert "correct_answer" in q
    assert "question_type" in q
    assert "difficulty" in q


@pytest.mark.asyncio
async def test_list_questions_empty_skill(client: AsyncClient, test_student, content_tree):
    """A skill with no questions should return an empty list."""
    # Create a new skill without questions

    resp = await client.get(
        f"/api/v1/subjects/skills/{uuid.uuid4()}/questions",
        headers=auth_header(test_student),
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["items"] == []


# ── Bulk Exercise Import ─────────────────────────────────

IMPORT_URL = "/api/v1/admin/content/exercises/import"
MS_EXTERNAL_ID = "NUM-ENTIERS-0-1B::MS01"


@pytest.fixture
async def micro_skill(db_session: AsyncSession, content_tree):
    """Create a MicroSkill linked to the content_tree's skill."""
    ms = MicroSkill(
        id=uuid.uuid4(),
        skill_id=content_tree["skill"].id,
        external_id=MS_EXTERNAL_ID,
        name="Lire les nombres entiers jusqu'a 1 milliard",
        order=1,
    )
    db_session.add(ms)
    await db_session.flush()
    return ms


@pytest.mark.asyncio
async def test_bulk_import_exercises_mcq(client: AsyncClient, test_admin, micro_skill):
    """Basic MCQ import should create questions."""
    payload = {
        "micro_skill_external_id": MS_EXTERNAL_ID,
        "exercises": [
            {
                "exercise_id": "EX001",
                "type": "mcq",
                "text": "Quel nombre est le plus grand ?",
                "choices": ["100", "1000", "10"],
                "correct_answer": "1000",
                "difficulty": "easy",
            },
            {
                "exercise_id": "EX002",
                "type": "mcq",
                "text": "Combien de chiffres dans 1 000 000 ?",
                "choices": ["5", "6", "7", "8"],
                "correct_answer": "7",
                "hint": "Compte les zeros",
                "bloom_level": "Connaitre",
                "ilma_level": "Decouverte",
            },
        ],
    }
    resp = await client.post(IMPORT_URL, json=payload, headers=auth_header(test_admin))
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["created"] == 2
    assert data["updated"] == 0
    assert data["errors"] == []


@pytest.mark.asyncio
async def test_bulk_import_exercises_idempotent(client: AsyncClient, test_admin, micro_skill):
    """Re-importing the same exercises should update, not duplicate."""
    payload = {
        "micro_skill_external_id": MS_EXTERNAL_ID,
        "exercises": [
            {
                "exercise_id": "EX010",
                "type": "true_false",
                "text": "1000 > 999",
                "correct_answer": True,
            },
        ],
    }
    # First import
    resp1 = await client.post(IMPORT_URL, json=payload, headers=auth_header(test_admin))
    assert resp1.status_code == 201
    assert resp1.json()["data"]["created"] == 1

    # Second import — same exercise_id → update
    payload["exercises"][0]["text"] = "1000 est superieur a 999"
    resp2 = await client.post(IMPORT_URL, json=payload, headers=auth_header(test_admin))
    assert resp2.status_code == 201
    data2 = resp2.json()["data"]
    assert data2["updated"] == 1
    assert data2["created"] == 0


@pytest.mark.asyncio
async def test_bulk_import_exercises_mixed_types(client: AsyncClient, test_admin, micro_skill):
    """Import with multiple exercise types in one batch."""
    payload = {
        "micro_skill_external_id": MS_EXTERNAL_ID,
        "exercises": [
            {
                "exercise_id": "EX020",
                "type": "mcq",
                "text": "2 + 2 = ?",
                "choices": ["3", "4", "5"],
                "correct_answer": "4",
            },
            {
                "exercise_id": "EX021",
                "type": "ordering",
                "text": "Range du plus petit au plus grand",
                "items": ["100", "10", "1000"],
                "correct_answer": ["10", "100", "1000"],
            },
            {
                "exercise_id": "EX022",
                "type": "numeric_input",
                "text": "Combien font 5 x 6 ?",
                "correct_answer": 30,
                "tolerance": 0,
            },
            {
                "exercise_id": "EX023",
                "type": "fill_blank",
                "text": "Le nombre ___ vient apres 999",
                "correct_answer": "1000",
            },
        ],
    }
    resp = await client.post(IMPORT_URL, json=payload, headers=auth_header(test_admin))
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["created"] == 4
    assert data["errors"] == []


@pytest.mark.asyncio
async def test_bulk_import_micro_skill_not_found(client: AsyncClient, test_admin):
    """404 when micro_skill_external_id does not exist."""
    payload = {
        "micro_skill_external_id": "DOES-NOT-EXIST",
        "exercises": [
            {
                "exercise_id": "EX001",
                "type": "mcq",
                "text": "Test",
                "choices": ["a", "b"],
                "correct_answer": "a",
            },
        ],
    }
    resp = await client.post(IMPORT_URL, json=payload, headers=auth_header(test_admin))
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_bulk_import_requires_admin(client: AsyncClient, test_student, micro_skill):
    """Non-admin users should get 403."""
    payload = {
        "micro_skill_external_id": MS_EXTERNAL_ID,
        "exercises": [
            {
                "exercise_id": "EX001",
                "type": "mcq",
                "text": "Test",
                "choices": ["a", "b"],
                "correct_answer": "a",
            },
        ],
    }
    resp = await client.post(IMPORT_URL, json=payload, headers=auth_header(test_student))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_bulk_import_validation_error(client: AsyncClient, test_admin, micro_skill):
    """MCQ with < 2 choices should fail validation (422)."""
    payload = {
        "micro_skill_external_id": MS_EXTERNAL_ID,
        "exercises": [
            {
                "exercise_id": "EX_BAD",
                "type": "mcq",
                "text": "Question invalide",
                "choices": ["seul"],
                "correct_answer": "seul",
            },
        ],
    }
    resp = await client.post(IMPORT_URL, json=payload, headers=auth_header(test_admin))
    assert resp.status_code == 422
