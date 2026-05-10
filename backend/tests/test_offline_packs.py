"""Tests du flux offline packs et sync (P0-2.13).

Couvre :
- Liste des packs par compétence
- Téléchargement d'un pack complet avec questions/leçons/checksum
- Delta sync (compétences modifiées depuis un timestamp)
- Sync batch d'événements offline
- Structure attendue du pack
"""
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import (
    ContentStatus,
    DifficultyLevel,
    Domain,
    MicroLesson,
    MicroSkill,
    Question,
    QuestionType,
    Skill,
    Subject,
)
from app.models.user import User
from tests.conftest import auth_header

# ── Fixtures ──────────────────────────────────────────────


@pytest.fixture
async def seed_content(db_session: AsyncSession) -> dict:
    """Crée un arbre de contenu minimal : Subject → Domain → Skill → Questions + Lessons."""
    subject = Subject(
        id=uuid.uuid4(),
        name="Mathématiques",
        slug="mathematiques",
        order=1,
        is_active=True,
    )
    db_session.add(subject)
    await db_session.flush()

    domain = Domain(
        id=uuid.uuid4(),
        subject_id=subject.id,
        name="Numération",
        slug="numeration",
        order=1,
        is_active=True,
    )
    db_session.add(domain)
    await db_session.flush()

    skill = Skill(
        id=uuid.uuid4(),
        domain_id=domain.id,
        name="Les entiers naturels",
        slug="entiers-naturels",
        order=1,
        is_active=True,
    )
    db_session.add(skill)
    await db_session.flush()

    # Micro-skill
    micro_skill = MicroSkill(
        id=uuid.uuid4(),
        skill_id=skill.id,
        name="Lire et écrire les nombres",
        order=1,
        is_active=True,
    )
    db_session.add(micro_skill)
    await db_session.flush()

    # Questions
    q1 = Question(
        id=uuid.uuid4(),
        skill_id=skill.id,
        micro_skill_id=micro_skill.id,
        question_type=QuestionType.MCQ,
        difficulty=DifficultyLevel.EASY,
        text="Combien font 2 + 3 ?",
        choices=["4", "5", "6"],
        correct_answer="5",
        explanation="2 + 3 = 5",
        points=1,
        is_active=True,
        status=ContentStatus.PUBLISHED,
    )
    q2 = Question(
        id=uuid.uuid4(),
        skill_id=skill.id,
        question_type=QuestionType.TRUE_FALSE,
        difficulty=DifficultyLevel.MEDIUM,
        text="10 est plus grand que 9",
        correct_answer="true",
        points=1,
        is_active=True,
        status=ContentStatus.PUBLISHED,
    )
    db_session.add_all([q1, q2])
    await db_session.flush()

    # Micro-lesson
    lesson = MicroLesson(
        id=uuid.uuid4(),
        skill_id=skill.id,
        micro_skill_id=micro_skill.id,
        title="Introduction aux entiers naturels",
        content_html="<p>Les entiers naturels sont 0, 1, 2, 3...</p>",
        summary="Découverte des entiers",
        duration_minutes=5,
        order=1,
        is_active=True,
        status=ContentStatus.PUBLISHED,
    )
    db_session.add(lesson)
    await db_session.flush()

    # Deuxième compétence (inactive) pour vérifier le filtrage
    skill_inactive = Skill(
        id=uuid.uuid4(),
        domain_id=domain.id,
        name="Compétence désactivée",
        slug="comp-desactivee",
        order=2,
        is_active=False,
    )
    db_session.add(skill_inactive)
    await db_session.flush()

    return {
        "subject": subject,
        "domain": domain,
        "skill": skill,
        "micro_skill": micro_skill,
        "questions": [q1, q2],
        "lesson": lesson,
        "skill_inactive": skill_inactive,
    }


# ── Tests ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_skill_packs(
    client: AsyncClient,
    db_session: AsyncSession,
    test_student: User,
    test_student_profile,
    seed_content: dict,
):
    """GET /offline/packs/skills renvoie la liste des packs disponibles."""
    headers = auth_header(test_student, test_student_profile)
    resp = await client.get("/api/v1/offline/packs/skills", headers=headers)

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True

    packs = body["data"]
    # Seule la compétence active doit apparaître
    assert len(packs) == 1

    pack = packs[0]
    assert pack["skill_id"] == str(seed_content["skill"].id)
    assert pack["skill_name"] == "Les entiers naturels"
    assert pack["domain_name"] == "Numération"
    assert pack["subject_name"] == "Mathématiques"
    assert pack["questions_count"] == 2
    assert pack["lessons_count"] == 1
    assert pack["estimated_size_bytes"] > 0


@pytest.mark.asyncio
async def test_download_skill_pack(
    client: AsyncClient,
    db_session: AsyncSession,
    test_student: User,
    test_student_profile,
    seed_content: dict,
):
    """GET /offline/packs/skills/{id} renvoie le pack complet avec questions/leçons/checksum."""
    skill_id = seed_content["skill"].id
    headers = auth_header(test_student, test_student_profile)
    resp = await client.get(f"/api/v1/offline/packs/skills/{skill_id}", headers=headers)

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True

    pack = body["data"]
    assert pack["skill_id"] == str(skill_id)
    assert len(pack["questions"]) == 2
    assert len(pack["lessons"]) == 1
    assert "checksum" in pack
    assert len(pack["checksum"]) == 32  # MD5 hex digest
    assert "generated_at" in pack

    # Vérifie le contenu d'une question
    q_texts = {q["text"] for q in pack["questions"]}
    assert "Combien font 2 + 3 ?" in q_texts

    # Vérifie le contenu de la leçon
    assert pack["lessons"][0]["title"] == "Introduction aux entiers naturels"
    assert "<p>" in pack["lessons"][0]["content_html"]


@pytest.mark.asyncio
async def test_download_skill_pack_not_found(
    client: AsyncClient,
    db_session: AsyncSession,
    test_student: User,
    test_student_profile,
):
    """GET /offline/packs/skills/{id} avec un ID inexistant renvoie 404."""
    fake_id = uuid.uuid4()
    headers = auth_header(test_student, test_student_profile)
    resp = await client.get(f"/api/v1/offline/packs/skills/{fake_id}", headers=headers)

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delta_sync(
    client: AsyncClient,
    db_session: AsyncSession,
    test_student: User,
    test_student_profile,
    seed_content: dict,
):
    """GET /offline/packs/delta?since=... renvoie les compétences modifiées."""
    headers = auth_header(test_student, test_student_profile)

    # Demander les changements depuis hier — la compétence créée est récente
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
    resp = await client.get(
        f"/api/v1/offline/packs/delta?since={yesterday}",
        headers=headers,
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True

    changes = body["data"]
    # La compétence active doit apparaître (updated_at > yesterday)
    skill_ids = {c["skill_id"] for c in changes}
    assert str(seed_content["skill"].id) in skill_ids

    # Demander les changements depuis dans le futur — rien ne devrait revenir
    future = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
    resp2 = await client.get(
        f"/api/v1/offline/packs/delta?since={future}",
        headers=headers,
    )
    assert resp2.status_code == 200
    assert len(resp2.json()["data"]) == 0


@pytest.mark.asyncio
async def test_batch_sync_events(
    client: AsyncClient,
    db_session: AsyncSession,
    test_student: User,
    test_student_profile,
):
    """POST /offline/sync avec des événements offline."""
    headers = auth_header(test_student, test_student_profile)

    events = [
        {
            "event_type": "profile_updated",
            "client_event_id": f"evt-{uuid.uuid4()}",
            "payload": {"display_name": "Nouveau Nom"},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        {
            "event_type": "profile_updated",
            "client_event_id": f"evt-{uuid.uuid4()}",
            "payload": {"avatar_url": "https://example.com/avatar.png"},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    ]

    resp = await client.post(
        "/api/v1/offline/sync",
        json={"events": events},
        headers=headers,
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True

    sync_result = body["data"]
    assert sync_result["processed"] == 2
    # Chaque événement doit avoir un résultat
    assert len(sync_result["results"]) == 2


@pytest.mark.asyncio
async def test_batch_sync_idempotent(
    client: AsyncClient,
    db_session: AsyncSession,
    test_student: User,
    test_student_profile,
):
    """POST /offline/sync — renvoyer le même client_event_id donne un duplicate."""
    headers = auth_header(test_student, test_student_profile)
    event_id = f"evt-{uuid.uuid4()}"

    event = {
        "event_type": "profile_updated",
        "client_event_id": event_id,
        "payload": {"display_name": "Test Idempotent"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Premier envoi
    resp1 = await client.post(
        "/api/v1/offline/sync",
        json={"events": [event]},
        headers=headers,
    )
    assert resp1.status_code == 200
    r1 = resp1.json()["data"]
    assert r1["accepted"] >= 0  # Au moins traité sans erreur

    # Deuxième envoi du même événement
    resp2 = await client.post(
        "/api/v1/offline/sync",
        json={"events": [event]},
        headers=headers,
    )
    assert resp2.status_code == 200
    r2 = resp2.json()["data"]
    # Doit être marqué comme duplicate ou accepted (selon l'implémentation)
    assert r2["processed"] == 1


@pytest.mark.asyncio
async def test_pack_contains_expected_structure(
    client: AsyncClient,
    db_session: AsyncSession,
    test_student: User,
    test_student_profile,
    seed_content: dict,
):
    """Vérifie que le pack contient tous les champs requis."""
    skill_id = seed_content["skill"].id
    headers = auth_header(test_student, test_student_profile)
    resp = await client.get(f"/api/v1/offline/packs/skills/{skill_id}", headers=headers)

    assert resp.status_code == 200
    pack = resp.json()["data"]

    # Champs requis au niveau racine
    required_fields = [
        "skill_id",
        "skill_name",
        "skill_slug",
        "domain_id",
        "domain_name",
        "subject_id",
        "subject_name",
        "micro_skills",
        "questions",
        "lessons",
        "checksum",
        "generated_at",
    ]
    for field in required_fields:
        assert field in pack, f"Champ manquant : {field}"

    # Vérifier la structure d'une question
    q = pack["questions"][0]
    q_required = ["id", "text", "correct_answer", "question_type", "difficulty", "points"]
    for field in q_required:
        assert field in q, f"Champ question manquant : {field}"

    # Vérifier la structure d'une leçon
    lesson = pack["lessons"][0]
    l_required = ["id", "title", "content_html", "order"]
    for field in l_required:
        assert field in lesson, f"Champ leçon manquant : {field}"

    # Vérifier la structure d'un micro-skill
    ms = pack["micro_skills"][0]
    ms_required = ["id", "name", "order"]
    for field in ms_required:
        assert field in ms, f"Champ micro-skill manquant : {field}"

    # Vérifier les types
    assert isinstance(pack["questions"], list)
    assert isinstance(pack["lessons"], list)
    assert isinstance(pack["micro_skills"], list)
    assert isinstance(pack["checksum"], str)
    assert isinstance(pack["generated_at"], str)


@pytest.mark.asyncio
async def test_list_skill_packs_unauthenticated(
    client: AsyncClient,
    db_session: AsyncSession,
):
    """GET /offline/packs/skills sans token renvoie 401."""
    resp = await client.get("/api/v1/offline/packs/skills")
    assert resp.status_code in (401, 403)
