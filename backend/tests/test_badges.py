"""Badge endpoint and service tests (profile-aware).

Comprehensive tests for all badge condition_types in the badge engine.
"""
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.badge import Badge, BadgeCategory, StudentBadge
from app.models.content import DifficultyLevel, Domain, Question, QuestionType, Skill, Subject
from app.models.progress import Progress
from app.models.session import ExerciseSession, SessionMode, SessionStatus
from app.services.badge_service import BADGE_DEFINITIONS, badge_service
from tests.conftest import auth_header

# ── Fixtures ──────────────────────────────────────────────


@pytest.fixture
async def seed_badges(db_session: AsyncSession):
    """Create badge definitions in the DB with criteria for rule engine."""
    badges = []
    badge_data = [
        ("first_exercise", "Premier exercice", "Complete ton premier exercice", BadgeCategory.COMPLETION, {"condition_type": "min_sessions", "params": {"min": 1}}),
        ("streak_3", "Serie de 3", "3 jours de suite", BadgeCategory.STREAK, {"condition_type": "min_best_streak", "params": {"min": 3}}),
        ("streak_10", "Serie de 10", "10 jours de suite", BadgeCategory.STREAK, {"condition_type": "min_best_streak", "params": {"min": 10}}),
        ("mastery_skill", "Maitre de competence", "90%+ sur une competence", BadgeCategory.MASTERY, {"condition_type": "min_skill_score", "params": {"min_score": 90, "min_count": 1}}),
        ("all_subjects", "Explorateur", "Exercice dans chaque matiere", BadgeCategory.EXPLORATION, {"condition_type": "all_subjects_practiced", "params": {}}),
    ]
    for code, name, desc, category, criteria in badge_data:
        b = Badge(
            id=uuid.uuid4(),
            code=code,
            name=name,
            description=desc,
            icon=f"badge-{code}",
            category=category,
            criteria=criteria,
        )
        db_session.add(b)
        badges.append(b)
    await db_session.flush()
    return badges


@pytest.fixture
async def badge_content(db_session: AsyncSession):
    """Create content for badge testing."""
    subj = Subject(id=uuid.uuid4(), name="Math", slug="math-badge", order=1)
    db_session.add(subj)
    await db_session.flush()

    domain = Domain(id=uuid.uuid4(), name="Num", slug="num-badge", subject_id=subj.id, order=1)
    db_session.add(domain)
    await db_session.flush()

    skill = Skill(id=uuid.uuid4(), name="Add", slug="add-badge", domain_id=domain.id, order=1)
    db_session.add(skill)
    await db_session.flush()

    q = Question(
        id=uuid.uuid4(),
        skill_id=skill.id,
        text="1+1=?",
        question_type=QuestionType.MCQ,
        difficulty=DifficultyLevel.EASY,
        choices=["2", "3"],
        correct_answer="2",
        points=1,
    )
    db_session.add(q)
    await db_session.flush()
    return skill


def _make_badge(code: str, condition_type: str, params: dict, category: BadgeCategory = BadgeCategory.COMPLETION) -> Badge:
    """Helper to create a Badge object for testing."""
    return Badge(
        id=uuid.uuid4(),
        code=code,
        name=f"Badge {code}",
        description=f"Test badge {code}",
        icon=f"icon-{code}",
        category=category,
        criteria={"condition_type": condition_type, "params": params},
    )


def _make_session(
    profile_id,
    skill_id,
    *,
    status=SessionStatus.COMPLETED,
    total_questions=5,
    correct_answers=3,
    score=60.0,
    started_at=None,
    completed_at=None,
) -> ExerciseSession:
    """Helper to create an ExerciseSession object."""
    now = datetime.now(timezone.utc)
    return ExerciseSession(
        id=uuid.uuid4(),
        profile_id=profile_id,
        skill_id=skill_id,
        mode=SessionMode.PRACTICE,
        status=status,
        total_questions=total_questions,
        correct_answers=correct_answers,
        score=score,
        started_at=started_at or now,
        completed_at=completed_at or now,
    )


async def _create_full_content(db_session: AsyncSession, num_subjects: int = 1, skills_per_domain: int = 1) -> dict:
    """Create a full content hierarchy (subjects -> domains -> skills) and return a dict of references."""
    subjects = []
    domains = []
    skills = []

    for i in range(num_subjects):
        subj = Subject(id=uuid.uuid4(), name=f"Subject {i}", slug=f"subj-{i}-{uuid.uuid4().hex[:6]}", order=i)
        db_session.add(subj)
        subjects.append(subj)

    await db_session.flush()

    for subj in subjects:
        dom = Domain(id=uuid.uuid4(), name=f"Domain for {subj.name}", slug=f"dom-{subj.id.hex[:6]}-{uuid.uuid4().hex[:6]}", subject_id=subj.id, order=1)
        db_session.add(dom)
        domains.append(dom)

    await db_session.flush()

    for dom in domains:
        for j in range(skills_per_domain):
            sk = Skill(id=uuid.uuid4(), name=f"Skill {j} in {dom.name}", slug=f"sk-{dom.id.hex[:6]}-{j}-{uuid.uuid4().hex[:6]}", domain_id=dom.id, order=j)
            db_session.add(sk)
            skills.append(sk)

    await db_session.flush()

    return {"subjects": subjects, "domains": domains, "skills": skills}


# ── Badge listing (student) ────────────────────────────────


@pytest.mark.asyncio
async def test_my_badges_empty(client: AsyncClient, test_student, test_student_profile):
    """Student with profile auto-select can list badges."""
    resp = await client.get(
        "/api/v1/students/me/badges", headers=auth_header(test_student)
    )
    assert resp.status_code == 200
    assert resp.json()["data"] == []


@pytest.mark.asyncio
async def test_my_badges_with_earned(
    client: AsyncClient, test_student, test_student_profile, db_session: AsyncSession, seed_badges
):
    badge = seed_badges[0]  # first_exercise
    sb = StudentBadge(
        profile_id=test_student_profile.id,
        badge_id=badge.id,
        awarded_at=datetime.now(timezone.utc),
    )
    db_session.add(sb)
    await db_session.flush()

    resp = await client.get(
        "/api/v1/students/me/badges", headers=auth_header(test_student)
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1
    assert data[0]["badge_code"] == "first_exercise"
    assert data[0]["badge_name"] == "Premier exercice"
    assert data[0]["category"] == "completion"
    assert data[0]["awarded_at"] is not None


# ── Badge listing (parent/admin) ──────────────────────────


@pytest.mark.asyncio
async def test_parent_view_student_badges(
    client: AsyncClient, test_parent, test_student_profile, db_session: AsyncSession, seed_badges,
    test_student,
):
    badge = seed_badges[0]
    sb = StudentBadge(
        profile_id=test_student_profile.id,
        badge_id=badge.id,
        awarded_at=datetime.now(timezone.utc),
    )
    db_session.add(sb)
    await db_session.flush()

    resp = await client.get(
        f"/api/v1/students/{test_student_profile.id}/badges",
        headers=auth_header(test_parent),
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1


@pytest.mark.asyncio
async def test_admin_view_student_badges(
    client: AsyncClient, test_admin, test_student, test_student_profile, db_session: AsyncSession, seed_badges
):
    resp = await client.get(
        f"/api/v1/students/{test_student_profile.id}/badges",
        headers=auth_header(test_admin),
    )
    assert resp.status_code == 200
    assert resp.json()["data"] == []


@pytest.mark.asyncio
async def test_student_cannot_view_other_badges(
    client: AsyncClient, test_student, test_student_profile
):
    other_id = uuid.uuid4()
    resp = await client.get(
        f"/api/v1/students/{other_id}/badges",
        headers=auth_header(test_student),
    )
    # Students can't use /students/{id}/badges — requires PARENT or ADMIN
    assert resp.status_code == 403


# ── Badge service: award logic ────────────────────────────


@pytest.mark.asyncio
async def test_badge_rules_defined():
    """Verify all expected badge definitions exist."""
    codes = {d["code"] for d in BADGE_DEFINITIONS}
    assert "first_exercise" in codes
    assert "streak_3" in codes
    assert "streak_7" in codes
    assert "mastery_skill" in codes
    assert "all_subjects" in codes
    assert len(BADGE_DEFINITIONS) >= 26  # 26+ badge definitions


@pytest.mark.asyncio
async def test_award_first_exercise_badge(
    db_session: AsyncSession, test_student, test_student_profile, seed_badges, badge_content
):
    skill = badge_content

    # Create a completed session using profile_id
    session = ExerciseSession(
        id=uuid.uuid4(),
        profile_id=test_student_profile.id,
        skill_id=skill.id,
        mode=SessionMode.PRACTICE,
        status=SessionStatus.COMPLETED,
        total_questions=1,
        correct_answers=1,
        score=100.0,
    )
    db_session.add(session)
    await db_session.flush()

    # Award badges using profile_id
    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "first_exercise" in awarded


@pytest.mark.asyncio
async def test_award_badges_no_duplicates(
    db_session: AsyncSession, test_student, test_student_profile, seed_badges, badge_content
):
    skill = badge_content

    session = ExerciseSession(
        id=uuid.uuid4(),
        profile_id=test_student_profile.id,
        skill_id=skill.id,
        mode=SessionMode.PRACTICE,
        status=SessionStatus.COMPLETED,
        total_questions=1,
        correct_answers=1,
        score=100.0,
    )
    db_session.add(session)
    await db_session.flush()

    # First award
    first_awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "first_exercise" in first_awarded

    # Second award — should not re-award
    second_awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "first_exercise" not in second_awarded


@pytest.mark.asyncio
async def test_get_student_badges_service(
    db_session: AsyncSession, test_student, test_student_profile, seed_badges
):
    badge = seed_badges[0]
    sb = StudentBadge(
        profile_id=test_student_profile.id,
        badge_id=badge.id,
        awarded_at=datetime.now(timezone.utc),
    )
    db_session.add(sb)
    await db_session.flush()

    badges = await badge_service.get_student_badges(db_session, test_student_profile.id)
    assert len(badges) == 1
    assert badges[0]["badge_code"] == "first_exercise"


@pytest.mark.asyncio
async def test_sync_badge_event(
    db_session: AsyncSession, test_student, test_student_profile, seed_badges
):
    result = await badge_service.sync_badge_event(
        db_session,
        profile_id=test_student_profile.id,
        badge_code="first_exercise",
        client_event_id="offline_badge_001",
        awarded_at=datetime.now(timezone.utc),
    )
    assert result is True

    # Duplicate — same client_event_id
    result2 = await badge_service.sync_badge_event(
        db_session,
        profile_id=test_student_profile.id,
        badge_code="first_exercise",
        client_event_id="offline_badge_001",
        awarded_at=datetime.now(timezone.utc),
    )
    assert result2 is False


@pytest.mark.asyncio
async def test_sync_badge_event_unknown_code(
    db_session: AsyncSession, test_student, test_student_profile, seed_badges
):
    result = await badge_service.sync_badge_event(
        db_session,
        profile_id=test_student_profile.id,
        badge_code="nonexistent_badge",
        client_event_id="offline_badge_002",
        awarded_at=datetime.now(timezone.utc),
    )
    assert result is False


# ══════════════════════════════════════════════════════════════
# Comprehensive condition_type tests
# ══════════════════════════════════════════════════════════════


# ── 1. min_sessions ───────────────────────────────────────


@pytest.mark.asyncio
async def test_min_sessions_not_met(db_session: AsyncSession, test_student, test_student_profile):
    """Badge should NOT be awarded when session count is below threshold."""
    content = await _create_full_content(db_session)
    skill = content["skills"][0]

    badge = _make_badge("sessions_3", "min_sessions", {"min": 3})
    db_session.add(badge)
    await db_session.flush()

    # Only 2 completed sessions — below threshold of 3
    for _ in range(2):
        db_session.add(_make_session(test_student_profile.id, skill.id))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "sessions_3" not in awarded


@pytest.mark.asyncio
async def test_min_sessions_exactly_met(db_session: AsyncSession, test_student, test_student_profile):
    """Badge should be awarded when session count equals threshold."""
    content = await _create_full_content(db_session)
    skill = content["skills"][0]

    badge = _make_badge("sessions_3", "min_sessions", {"min": 3})
    db_session.add(badge)
    await db_session.flush()

    for _ in range(3):
        db_session.add(_make_session(test_student_profile.id, skill.id))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "sessions_3" in awarded


@pytest.mark.asyncio
async def test_min_sessions_ignores_incomplete(db_session: AsyncSession, test_student, test_student_profile):
    """Only COMPLETED sessions count toward min_sessions."""
    content = await _create_full_content(db_session)
    skill = content["skills"][0]

    badge = _make_badge("sessions_1", "min_sessions", {"min": 1})
    db_session.add(badge)
    await db_session.flush()

    # Add an in-progress and an abandoned session
    db_session.add(_make_session(test_student_profile.id, skill.id, status=SessionStatus.IN_PROGRESS))
    db_session.add(_make_session(test_student_profile.id, skill.id, status=SessionStatus.ABANDONED))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "sessions_1" not in awarded


# ── 2. min_best_streak ────────────────────────────────────


@pytest.mark.asyncio
async def test_min_best_streak_not_met(db_session: AsyncSession, test_student, test_student_profile):
    """Badge should NOT be awarded when best_streak is below threshold."""
    content = await _create_full_content(db_session)
    skill = content["skills"][0]

    badge = _make_badge("streak_5", "min_best_streak", {"min": 5})
    db_session.add(badge)

    progress = Progress(
        id=uuid.uuid4(),
        profile_id=test_student_profile.id,
        skill_id=skill.id,
        smart_score=50.0,
        total_attempts=10,
        correct_attempts=5,
        streak=2,
        best_streak=4,  # below threshold of 5
    )
    db_session.add(progress)
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "streak_5" not in awarded


@pytest.mark.asyncio
async def test_min_best_streak_met(db_session: AsyncSession, test_student, test_student_profile):
    """Badge should be awarded when best_streak meets threshold."""
    content = await _create_full_content(db_session)
    skill = content["skills"][0]

    badge = _make_badge("streak_5", "min_best_streak", {"min": 5})
    db_session.add(badge)

    progress = Progress(
        id=uuid.uuid4(),
        profile_id=test_student_profile.id,
        skill_id=skill.id,
        smart_score=50.0,
        total_attempts=10,
        correct_attempts=5,
        streak=5,
        best_streak=5,
    )
    db_session.add(progress)
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "streak_5" in awarded


@pytest.mark.asyncio
async def test_min_best_streak_uses_max_across_skills(db_session: AsyncSession, test_student, test_student_profile):
    """Badge should check MAX(best_streak) across all skill progress records."""
    content = await _create_full_content(db_session, num_subjects=1, skills_per_domain=2)
    skill_a, skill_b = content["skills"]

    badge = _make_badge("streak_7", "min_best_streak", {"min": 7})
    db_session.add(badge)

    # Low streak on skill A, high streak on skill B
    db_session.add(Progress(
        id=uuid.uuid4(), profile_id=test_student_profile.id, skill_id=skill_a.id,
        smart_score=40.0, total_attempts=5, correct_attempts=2, streak=2, best_streak=3,
    ))
    db_session.add(Progress(
        id=uuid.uuid4(), profile_id=test_student_profile.id, skill_id=skill_b.id,
        smart_score=80.0, total_attempts=10, correct_attempts=8, streak=7, best_streak=7,
    ))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "streak_7" in awarded


# ── 3. min_skill_score ────────────────────────────────────


@pytest.mark.asyncio
async def test_min_skill_score_not_met(db_session: AsyncSession, test_student, test_student_profile):
    """Badge should NOT be awarded when no skill has score >= min_score."""
    content = await _create_full_content(db_session)
    skill = content["skills"][0]

    badge = _make_badge("mastery_1", "min_skill_score", {"min_score": 90, "min_count": 1})
    db_session.add(badge)

    db_session.add(Progress(
        id=uuid.uuid4(), profile_id=test_student_profile.id, skill_id=skill.id,
        smart_score=89.0, total_attempts=10, correct_attempts=8, streak=0, best_streak=3,
    ))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "mastery_1" not in awarded


@pytest.mark.asyncio
async def test_min_skill_score_single_skill(db_session: AsyncSession, test_student, test_student_profile):
    """Badge awarded when at least min_count skills reach min_score."""
    content = await _create_full_content(db_session)
    skill = content["skills"][0]

    badge = _make_badge("mastery_1", "min_skill_score", {"min_score": 90, "min_count": 1})
    db_session.add(badge)

    db_session.add(Progress(
        id=uuid.uuid4(), profile_id=test_student_profile.id, skill_id=skill.id,
        smart_score=92.0, total_attempts=20, correct_attempts=18, streak=5, best_streak=8,
    ))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "mastery_1" in awarded


@pytest.mark.asyncio
async def test_min_skill_score_multiple_needed(db_session: AsyncSession, test_student, test_student_profile):
    """Badge NOT awarded when min_count=3 but only 2 skills are above threshold."""
    content = await _create_full_content(db_session, num_subjects=1, skills_per_domain=3)
    skills = content["skills"]

    badge = _make_badge("mastery_3", "min_skill_score", {"min_score": 90, "min_count": 3})
    db_session.add(badge)

    # Two skills at 95, one at 85
    for i, sk in enumerate(skills):
        score = 95.0 if i < 2 else 85.0
        db_session.add(Progress(
            id=uuid.uuid4(), profile_id=test_student_profile.id, skill_id=sk.id,
            smart_score=score, total_attempts=10, correct_attempts=9, streak=0, best_streak=0,
        ))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "mastery_3" not in awarded

    # Now bump the third to 91
    # (We just add a new progress for a different skill to test count >= 3)
    content2 = await _create_full_content(db_session)
    db_session.add(Progress(
        id=uuid.uuid4(), profile_id=test_student_profile.id, skill_id=content2["skills"][0].id,
        smart_score=91.0, total_attempts=10, correct_attempts=9, streak=0, best_streak=0,
    ))
    await db_session.flush()

    awarded2 = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "mastery_3" in awarded2


# ── 4. min_total_attempts ─────────────────────────────────


@pytest.mark.asyncio
async def test_min_total_attempts_not_met(db_session: AsyncSession, test_student, test_student_profile):
    """Badge should NOT be awarded when total_attempts sum is below threshold."""
    content = await _create_full_content(db_session)
    skill = content["skills"][0]

    badge = _make_badge("questions_100", "min_total_attempts", {"min": 100})
    db_session.add(badge)

    db_session.add(Progress(
        id=uuid.uuid4(), profile_id=test_student_profile.id, skill_id=skill.id,
        smart_score=50.0, total_attempts=99, correct_attempts=50, streak=0, best_streak=0,
    ))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "questions_100" not in awarded


@pytest.mark.asyncio
async def test_min_total_attempts_met(db_session: AsyncSession, test_student, test_student_profile):
    """Badge awarded when total_attempts sum across all progress meets threshold."""
    content = await _create_full_content(db_session, num_subjects=1, skills_per_domain=2)
    skills = content["skills"]

    badge = _make_badge("questions_100", "min_total_attempts", {"min": 100})
    db_session.add(badge)

    # 60 + 40 = 100 total attempts across two skills
    db_session.add(Progress(
        id=uuid.uuid4(), profile_id=test_student_profile.id, skill_id=skills[0].id,
        smart_score=50.0, total_attempts=60, correct_attempts=30, streak=0, best_streak=0,
    ))
    db_session.add(Progress(
        id=uuid.uuid4(), profile_id=test_student_profile.id, skill_id=skills[1].id,
        smart_score=50.0, total_attempts=40, correct_attempts=20, streak=0, best_streak=0,
    ))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "questions_100" in awarded


# ── 5. all_subjects_practiced ─────────────────────────────


@pytest.mark.asyncio
async def test_all_subjects_practiced_not_all(db_session: AsyncSession, test_student, test_student_profile):
    """Badge NOT awarded when student hasn't practiced every active subject."""
    content = await _create_full_content(db_session, num_subjects=3)
    skills = content["skills"]

    badge = _make_badge("all_subjects", "all_subjects_practiced", {})
    db_session.add(badge)
    await db_session.flush()

    # Practice only 2 of 3 subjects
    for sk in skills[:2]:
        db_session.add(_make_session(test_student_profile.id, sk.id))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "all_subjects" not in awarded


@pytest.mark.asyncio
async def test_all_subjects_practiced_all(db_session: AsyncSession, test_student, test_student_profile):
    """Badge awarded when student has practiced every active subject."""
    content = await _create_full_content(db_session, num_subjects=3)
    skills = content["skills"]

    badge = _make_badge("all_subjects", "all_subjects_practiced", {})
    db_session.add(badge)
    await db_session.flush()

    # Practice all 3 subjects
    for sk in skills:
        db_session.add(_make_session(test_student_profile.id, sk.id))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "all_subjects" in awarded


@pytest.mark.asyncio
async def test_all_subjects_practiced_no_subjects(db_session: AsyncSession, test_student, test_student_profile):
    """Badge NOT awarded when there are no active subjects at all."""
    badge = _make_badge("all_subjects", "all_subjects_practiced", {})
    db_session.add(badge)
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "all_subjects" not in awarded


# ── 6. domain_mastered ────────────────────────────────────


@pytest.mark.asyncio
async def test_domain_mastered_not_all_skills(db_session: AsyncSession, test_student, test_student_profile):
    """Badge NOT awarded when only some skills in a domain meet the threshold."""
    content = await _create_full_content(db_session, num_subjects=1, skills_per_domain=3)
    skills = content["skills"]

    badge = _make_badge("domain_complete", "domain_mastered", {"min_score": 80})
    db_session.add(badge)

    # Only 2 of 3 skills at 80+
    db_session.add(Progress(
        id=uuid.uuid4(), profile_id=test_student_profile.id, skill_id=skills[0].id,
        smart_score=85.0, total_attempts=10, correct_attempts=8, streak=0, best_streak=0,
    ))
    db_session.add(Progress(
        id=uuid.uuid4(), profile_id=test_student_profile.id, skill_id=skills[1].id,
        smart_score=90.0, total_attempts=10, correct_attempts=9, streak=0, best_streak=0,
    ))
    # Third skill below threshold
    db_session.add(Progress(
        id=uuid.uuid4(), profile_id=test_student_profile.id, skill_id=skills[2].id,
        smart_score=50.0, total_attempts=10, correct_attempts=5, streak=0, best_streak=0,
    ))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "domain_complete" not in awarded


@pytest.mark.asyncio
async def test_domain_mastered_all_skills(db_session: AsyncSession, test_student, test_student_profile):
    """Badge awarded when ALL skills in at least one domain meet the threshold."""
    content = await _create_full_content(db_session, num_subjects=1, skills_per_domain=2)
    skills = content["skills"]

    badge = _make_badge("domain_complete", "domain_mastered", {"min_score": 80})
    db_session.add(badge)

    for sk in skills:
        db_session.add(Progress(
            id=uuid.uuid4(), profile_id=test_student_profile.id, skill_id=sk.id,
            smart_score=85.0, total_attempts=10, correct_attempts=8, streak=0, best_streak=0,
        ))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "domain_complete" in awarded


@pytest.mark.asyncio
async def test_domain_mastered_multiple_domains_one_mastered(db_session: AsyncSession, test_student, test_student_profile):
    """Badge awarded if at least one domain is fully mastered, even if others are not."""
    # Create 2 subjects, each with 1 domain and 1 skill
    content = await _create_full_content(db_session, num_subjects=2, skills_per_domain=1)
    skills = content["skills"]

    badge = _make_badge("domain_complete", "domain_mastered", {"min_score": 80})
    db_session.add(badge)

    # First domain: mastered
    db_session.add(Progress(
        id=uuid.uuid4(), profile_id=test_student_profile.id, skill_id=skills[0].id,
        smart_score=90.0, total_attempts=10, correct_attempts=9, streak=0, best_streak=0,
    ))
    # Second domain: not mastered
    db_session.add(Progress(
        id=uuid.uuid4(), profile_id=test_student_profile.id, skill_id=skills[1].id,
        smart_score=50.0, total_attempts=10, correct_attempts=5, streak=0, best_streak=0,
    ))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "domain_complete" in awarded


# ── 7. subject_mastered ───────────────────────────────────


@pytest.mark.asyncio
async def test_subject_mastered_not_all_skills(db_session: AsyncSession, test_student, test_student_profile):
    """Badge NOT awarded when not all skills in any subject meet threshold."""
    content = await _create_full_content(db_session, num_subjects=1, skills_per_domain=2)
    skills = content["skills"]

    badge = _make_badge("subject_complete", "subject_mastered", {"min_score": 80})
    db_session.add(badge)

    # One skill above, one below
    db_session.add(Progress(
        id=uuid.uuid4(), profile_id=test_student_profile.id, skill_id=skills[0].id,
        smart_score=85.0, total_attempts=10, correct_attempts=8, streak=0, best_streak=0,
    ))
    db_session.add(Progress(
        id=uuid.uuid4(), profile_id=test_student_profile.id, skill_id=skills[1].id,
        smart_score=70.0, total_attempts=10, correct_attempts=7, streak=0, best_streak=0,
    ))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "subject_complete" not in awarded


@pytest.mark.asyncio
async def test_subject_mastered_all_skills(db_session: AsyncSession, test_student, test_student_profile):
    """Badge awarded when all skills in at least one subject meet the threshold."""
    content = await _create_full_content(db_session, num_subjects=1, skills_per_domain=2)
    skills = content["skills"]

    badge = _make_badge("subject_complete", "subject_mastered", {"min_score": 80})
    db_session.add(badge)

    for sk in skills:
        db_session.add(Progress(
            id=uuid.uuid4(), profile_id=test_student_profile.id, skill_id=sk.id,
            smart_score=85.0, total_attempts=10, correct_attempts=8, streak=0, best_streak=0,
        ))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "subject_complete" in awarded


# ── 8. all_subjects_mastered ──────────────────────────────


@pytest.mark.asyncio
async def test_all_subjects_mastered_not_all(db_session: AsyncSession, test_student, test_student_profile):
    """Badge NOT awarded when not all subjects are mastered."""
    content = await _create_full_content(db_session, num_subjects=2, skills_per_domain=1)
    skills = content["skills"]

    badge = _make_badge("cep_all", "all_subjects_mastered", {"min_score": 70})
    db_session.add(badge)

    # First subject mastered, second not
    db_session.add(Progress(
        id=uuid.uuid4(), profile_id=test_student_profile.id, skill_id=skills[0].id,
        smart_score=80.0, total_attempts=10, correct_attempts=8, streak=0, best_streak=0,
    ))
    db_session.add(Progress(
        id=uuid.uuid4(), profile_id=test_student_profile.id, skill_id=skills[1].id,
        smart_score=60.0, total_attempts=10, correct_attempts=6, streak=0, best_streak=0,
    ))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "cep_all" not in awarded


@pytest.mark.asyncio
async def test_all_subjects_mastered_all(db_session: AsyncSession, test_student, test_student_profile):
    """Badge awarded when every active subject has all skills >= min_score."""
    content = await _create_full_content(db_session, num_subjects=2, skills_per_domain=1)
    skills = content["skills"]

    badge = _make_badge("cep_all", "all_subjects_mastered", {"min_score": 70})
    db_session.add(badge)

    for sk in skills:
        db_session.add(Progress(
            id=uuid.uuid4(), profile_id=test_student_profile.id, skill_id=sk.id,
            smart_score=75.0, total_attempts=10, correct_attempts=7, streak=0, best_streak=0,
        ))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "cep_all" in awarded


@pytest.mark.asyncio
async def test_all_subjects_mastered_no_subjects(db_session: AsyncSession, test_student, test_student_profile):
    """Badge NOT awarded when there are no active subjects."""
    badge = _make_badge("cep_all", "all_subjects_mastered", {"min_score": 70})
    db_session.add(badge)
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "cep_all" not in awarded


@pytest.mark.asyncio
async def test_all_subjects_mastered_subject_with_no_skills(db_session: AsyncSession, test_student, test_student_profile):
    """Badge NOT awarded when a subject has no skills (empty domain)."""
    # Create a subject with a domain but no skills
    subj = Subject(id=uuid.uuid4(), name="Empty Subject", slug=f"empty-{uuid.uuid4().hex[:6]}", order=1)
    db_session.add(subj)
    await db_session.flush()

    dom = Domain(id=uuid.uuid4(), name="Empty Domain", slug=f"empty-dom-{uuid.uuid4().hex[:6]}", subject_id=subj.id, order=1)
    db_session.add(dom)

    badge = _make_badge("cep_all", "all_subjects_mastered", {"min_score": 70})
    db_session.add(badge)
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "cep_all" not in awarded


# ── 9. session_before_hour (early_bird) ───────────────────


@pytest.mark.asyncio
async def test_early_bird_no_early_session(db_session: AsyncSession, test_student, test_student_profile):
    """Badge NOT awarded when no session started before the target hour."""
    content = await _create_full_content(db_session)
    skill = content["skills"][0]

    badge = _make_badge("early_bird", "session_before_hour", {"hour": 8})
    db_session.add(badge)

    # Session at 10:00 — not early enough
    late_start = datetime(2025, 6, 1, 10, 0, 0, tzinfo=timezone.utc)
    db_session.add(_make_session(test_student_profile.id, skill.id, started_at=late_start))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "early_bird" not in awarded


@pytest.mark.asyncio
async def test_early_bird_with_early_session(db_session: AsyncSession, test_student, test_student_profile):
    """Badge awarded when at least one completed session started before the target hour."""
    content = await _create_full_content(db_session)
    skill = content["skills"][0]

    badge = _make_badge("early_bird", "session_before_hour", {"hour": 8})
    db_session.add(badge)

    # Session at 6:30 AM
    early_start = datetime(2025, 6, 1, 6, 30, 0, tzinfo=timezone.utc)
    db_session.add(_make_session(test_student_profile.id, skill.id, started_at=early_start))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "early_bird" in awarded


@pytest.mark.asyncio
async def test_early_bird_incomplete_session_ignored(db_session: AsyncSession, test_student, test_student_profile):
    """Early session that is not COMPLETED should not trigger the badge."""
    content = await _create_full_content(db_session)
    skill = content["skills"][0]

    badge = _make_badge("early_bird", "session_before_hour", {"hour": 8})
    db_session.add(badge)

    early_start = datetime(2025, 6, 1, 5, 0, 0, tzinfo=timezone.utc)
    db_session.add(_make_session(
        test_student_profile.id, skill.id,
        started_at=early_start, status=SessionStatus.ABANDONED,
    ))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "early_bird" not in awarded


# ── 10. perfect_session ───────────────────────────────────


@pytest.mark.asyncio
async def test_perfect_session_not_met(db_session: AsyncSession, test_student, test_student_profile):
    """Badge NOT awarded when no session has 100% correct."""
    content = await _create_full_content(db_session)
    skill = content["skills"][0]

    badge = _make_badge("perfect_score", "perfect_session", {})
    db_session.add(badge)

    # 4 out of 5 correct — not perfect
    db_session.add(_make_session(
        test_student_profile.id, skill.id,
        total_questions=5, correct_answers=4, score=80.0,
    ))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "perfect_score" not in awarded


@pytest.mark.asyncio
async def test_perfect_session_awarded(db_session: AsyncSession, test_student, test_student_profile):
    """Badge awarded when a completed session has correct_answers == total_questions > 0."""
    content = await _create_full_content(db_session)
    skill = content["skills"][0]

    badge = _make_badge("perfect_score", "perfect_session", {})
    db_session.add(badge)

    db_session.add(_make_session(
        test_student_profile.id, skill.id,
        total_questions=10, correct_answers=10, score=100.0,
    ))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "perfect_score" in awarded


@pytest.mark.asyncio
async def test_perfect_session_zero_questions(db_session: AsyncSession, test_student, test_student_profile):
    """Badge NOT awarded for a session with 0 total_questions (vacuous truth guard)."""
    content = await _create_full_content(db_session)
    skill = content["skills"][0]

    badge = _make_badge("perfect_score", "perfect_session", {})
    db_session.add(badge)

    db_session.add(_make_session(
        test_student_profile.id, skill.id,
        total_questions=0, correct_answers=0, score=0.0,
    ))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "perfect_score" not in awarded


@pytest.mark.asyncio
async def test_perfect_session_incomplete_ignored(db_session: AsyncSession, test_student, test_student_profile):
    """An in-progress session with perfect answers so far should not trigger the badge."""
    content = await _create_full_content(db_session)
    skill = content["skills"][0]

    badge = _make_badge("perfect_score", "perfect_session", {})
    db_session.add(badge)

    db_session.add(_make_session(
        test_student_profile.id, skill.id,
        total_questions=5, correct_answers=5, score=100.0,
        status=SessionStatus.IN_PROGRESS,
    ))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "perfect_score" not in awarded


# ── 11. comeback ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_comeback_not_enough_sessions(db_session: AsyncSession, test_student, test_student_profile):
    """Comeback badge NOT awarded when fewer than 2 completed sessions exist."""
    content = await _create_full_content(db_session)
    skill = content["skills"][0]

    badge = _make_badge("comeback", "comeback", {"min_days": 7})
    db_session.add(badge)

    now = datetime.now(timezone.utc)
    db_session.add(_make_session(test_student_profile.id, skill.id, completed_at=now))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "comeback" not in awarded


@pytest.mark.asyncio
async def test_comeback_gap_too_small(db_session: AsyncSession, test_student, test_student_profile):
    """Comeback badge NOT awarded when gap between two most recent sessions < min_days."""
    content = await _create_full_content(db_session)
    skill = content["skills"][0]

    badge = _make_badge("comeback", "comeback", {"min_days": 7})
    db_session.add(badge)

    now = datetime.now(timezone.utc)
    db_session.add(_make_session(test_student_profile.id, skill.id, completed_at=now - timedelta(days=3)))
    db_session.add(_make_session(test_student_profile.id, skill.id, completed_at=now))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "comeback" not in awarded


@pytest.mark.asyncio
async def test_comeback_gap_met(db_session: AsyncSession, test_student, test_student_profile):
    """Comeback badge awarded when gap between two most recent sessions >= min_days."""
    content = await _create_full_content(db_session)
    skill = content["skills"][0]

    badge = _make_badge("comeback", "comeback", {"min_days": 7})
    db_session.add(badge)

    now = datetime.now(timezone.utc)
    db_session.add(_make_session(test_student_profile.id, skill.id, completed_at=now - timedelta(days=10)))
    db_session.add(_make_session(test_student_profile.id, skill.id, completed_at=now))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "comeback" in awarded


# ── 12. min_correct_streak ────────────────────────────────


@pytest.mark.asyncio
async def test_min_correct_streak_not_met(db_session: AsyncSession, test_student, test_student_profile):
    """Badge NOT awarded when best_streak is below min for correct streak."""
    content = await _create_full_content(db_session)
    skill = content["skills"][0]

    badge = _make_badge("zero_errors_10", "min_correct_streak", {"min": 10})
    db_session.add(badge)

    db_session.add(Progress(
        id=uuid.uuid4(), profile_id=test_student_profile.id, skill_id=skill.id,
        smart_score=70.0, total_attempts=15, correct_attempts=10, streak=5, best_streak=9,
    ))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "zero_errors_10" not in awarded


@pytest.mark.asyncio
async def test_min_correct_streak_met(db_session: AsyncSession, test_student, test_student_profile):
    """Badge awarded when best_streak meets the min for correct streak."""
    content = await _create_full_content(db_session)
    skill = content["skills"][0]

    badge = _make_badge("zero_errors_10", "min_correct_streak", {"min": 10})
    db_session.add(badge)

    db_session.add(Progress(
        id=uuid.uuid4(), profile_id=test_student_profile.id, skill_id=skill.id,
        smart_score=90.0, total_attempts=20, correct_attempts=18, streak=10, best_streak=10,
    ))
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "zero_errors_10" in awarded


# ── 13. manual badges ────────────────────────────────────


@pytest.mark.asyncio
async def test_manual_badges_not_auto_awarded(db_session: AsyncSession, test_student, test_student_profile):
    """Manual (social) badges should never be awarded by award_badges."""
    badge = _make_badge("first_challenge", "manual", {}, category=BadgeCategory.SOCIAL)
    db_session.add(badge)
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "first_challenge" not in awarded


# ── 14. exam_score (stub) ────────────────────────────────


@pytest.mark.asyncio
async def test_exam_score_never_awarded(db_session: AsyncSession, test_student, test_student_profile):
    """exam_score condition always returns False (not yet implemented)."""
    badge = _make_badge("cep_exam_80", "exam_score", {"min_pct": 80}, category=BadgeCategory.CEP)
    db_session.add(badge)
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "cep_exam_80" not in awarded


# ── 15. unknown condition_type ────────────────────────────


@pytest.mark.asyncio
async def test_unknown_condition_type_ignored(db_session: AsyncSession, test_student, test_student_profile):
    """An unknown condition_type should not cause errors, just returns False."""
    badge = _make_badge("mystery", "completely_unknown_type", {"foo": "bar"})
    db_session.add(badge)
    await db_session.flush()

    awarded = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "mystery" not in awarded


# ── 16. seed_badges ───────────────────────────────────────


@pytest.mark.asyncio
async def test_seed_badges_idempotent(db_session: AsyncSession):
    """Seeding badges twice should not create duplicates."""
    count1 = await badge_service.seed_badges(db_session)
    assert count1 == len(BADGE_DEFINITIONS)

    count2 = await badge_service.seed_badges(db_session)
    assert count2 == 0


# ── 17. get_all_badges_with_status ────────────────────────


@pytest.mark.asyncio
async def test_get_all_badges_with_status(db_session: AsyncSession, test_student, test_student_profile, seed_badges):
    """get_all_badges_with_status returns earned status and progress for unearned."""
    # Award one badge manually
    badge = seed_badges[0]  # first_exercise
    sb = StudentBadge(
        profile_id=test_student_profile.id,
        badge_id=badge.id,
        awarded_at=datetime.now(timezone.utc),
    )
    db_session.add(sb)
    await db_session.flush()

    result = await badge_service.get_all_badges_with_status(db_session, test_student_profile.id)
    assert len(result) == len(seed_badges)

    earned_badges = [b for b in result if b["earned"]]
    unearned_badges = [b for b in result if not b["earned"]]

    assert len(earned_badges) == 1
    assert earned_badges[0]["badge_code"] == "first_exercise"
    assert earned_badges[0]["awarded_at"] is not None

    assert len(unearned_badges) == len(seed_badges) - 1
    for ub in unearned_badges:
        assert ub["awarded_at"] is None
        # Progress should be computed for unearned badges
        assert ub["progress"] is not None


# ── 18. Cross-profile isolation ───────────────────────────


@pytest.mark.asyncio
async def test_badges_isolated_between_profiles(db_session: AsyncSession, test_student, test_student_profile, test_parent_profiles):
    """Badges earned by one profile should not appear for another."""
    content = await _create_full_content(db_session)
    skill = content["skills"][0]

    badge = _make_badge("sessions_1", "min_sessions", {"min": 1})
    db_session.add(badge)
    await db_session.flush()

    # Profile A completes a session
    db_session.add(_make_session(test_student_profile.id, skill.id))
    await db_session.flush()

    awarded_a = await badge_service.award_badges(db_session, test_student_profile.id)
    assert "sessions_1" in awarded_a

    # Profile B (from parent) should NOT have earned it
    other_profile = test_parent_profiles[0]
    awarded_b = await badge_service.award_badges(db_session, other_profile.id)
    assert "sessions_1" not in awarded_b

    badges_b = await badge_service.get_student_badges(db_session, other_profile.id)
    assert len(badges_b) == 0
