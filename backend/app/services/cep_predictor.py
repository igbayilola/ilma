"""CEP score predictor.

Simple weighted-average regression: predicted /20 grade from a profile's
SmartScore distribution across CEP-relevant skills, weighted by
Skill.cep_frequency (historical occurrence in past annales).

Output:
    {
      "predicted": 14.5,       # /20
      "confidence": 0.72,      # 0..1, function of total attempts
      "coverage": 0.65,        # fraction of CEP skills practiced at least once
      "weighted_avg_score": 72.3,  # /100
      "weak_skills": [
        {"skill_id": "...", "name": "Fractions", "smart_score": 32.5, "cep_frequency": 5}
      ],
      "subject_id": "..." | null
    }
"""
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Domain, Skill, Subject
from app.models.profile import Profile
from app.models.progress import Progress

_FULL_CONFIDENCE_ATTEMPTS = 200
_WEAK_SCORE_THRESHOLD = 60.0
_WEAK_SKILLS_LIMIT = 5


async def predict_cep_score(
    db: AsyncSession,
    profile: Profile,
    subject_id: UUID | None = None,
) -> dict:
    grade_level_id = profile.grade_level_id

    skill_q = (
        select(Skill.id, Skill.name, Skill.cep_frequency, Domain.subject_id)
        .join(Domain, Domain.id == Skill.domain_id)
        .join(Subject, Subject.id == Domain.subject_id)
        .where(Skill.is_active.is_(True))
    )
    if grade_level_id is not None:
        skill_q = skill_q.where(Subject.grade_level_id == grade_level_id)
    if subject_id is not None:
        skill_q = skill_q.where(Subject.id == subject_id)

    skill_rows = (await db.execute(skill_q)).all()
    if not skill_rows:
        return {
            "predicted": 0.0,
            "confidence": 0.0,
            "coverage": 0.0,
            "weighted_avg_score": 0.0,
            "weak_skills": [],
            "subject_id": str(subject_id) if subject_id else None,
        }

    skill_ids = [row.id for row in skill_rows]

    progress_q = select(
        Progress.skill_id,
        Progress.smart_score,
        Progress.total_attempts,
    ).where(
        Progress.profile_id == profile.id,
        Progress.skill_id.in_(skill_ids),
    )
    progress_rows = (await db.execute(progress_q)).all()
    progress_by_skill = {row.skill_id: row for row in progress_rows}

    total_attempts_q = select(func.coalesce(func.sum(Progress.total_attempts), 0)).where(
        Progress.profile_id == profile.id,
        Progress.skill_id.in_(skill_ids),
    )
    total_attempts = int((await db.execute(total_attempts_q)).scalar_one())

    total_weight = 0.0
    weighted_score_sum = 0.0
    practiced = 0
    weak: list[dict] = []

    for row in skill_rows:
        weight = float(row.cep_frequency) if row.cep_frequency and row.cep_frequency > 0 else 1.0
        total_weight += weight

        p = progress_by_skill.get(row.id)
        if p is None:
            weighted_score_sum += 0.0
            continue

        practiced += 1
        score = float(p.smart_score or 0.0)
        weighted_score_sum += score * weight
        if score < _WEAK_SCORE_THRESHOLD and weight > 1:
            weak.append({
                "skill_id": str(row.id),
                "name": row.name,
                "smart_score": round(score, 1),
                "cep_frequency": int(row.cep_frequency or 0),
            })

    weighted_avg = (weighted_score_sum / total_weight) if total_weight > 0 else 0.0
    predicted = round(weighted_avg / 100.0 * 20.0, 1)
    coverage = round(practiced / len(skill_rows), 2) if skill_rows else 0.0
    confidence = round(min(total_attempts / _FULL_CONFIDENCE_ATTEMPTS, 1.0), 2)

    weak.sort(key=lambda w: (-w["cep_frequency"], w["smart_score"]))
    weak = weak[:_WEAK_SKILLS_LIMIT]

    return {
        "predicted": predicted,
        "confidence": confidence,
        "coverage": coverage,
        "weighted_avg_score": round(weighted_avg, 1),
        "weak_skills": weak,
        "subject_id": str(subject_id) if subject_id else None,
    }
