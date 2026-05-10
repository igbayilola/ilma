"""Service for structured lesson import (upsert by external_id).

Pattern mirrors exercise_import_service.py: resolve micro_skill by external_id,
upsert MicroLesson records, track stats.
"""
from typing import Any, Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import ContentStatus, MicroLesson, MicroSkill, Skill


async def import_lesson(
    db: AsyncSession,
    lesson_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Import a single structured lesson (upsert by external_id).

    Expected lesson_data keys:
        - external_id (str, required): e.g. "NUM-ENTIERS-0::LESSON01"
        - skill_external_id (str, required): resolve to Skill
        - micro_skill_external_id (str, optional): resolve to MicroSkill
        - title, content_html, sections, formula, summary, media_url,
          duration_minutes, order
    """
    ext_id = lesson_data.get("external_id")
    if not ext_id:
        return {"error": "external_id manquant"}

    # Resolve skill
    skill_ext = lesson_data.get("skill_external_id")
    if not skill_ext:
        return {"error": f"skill_external_id manquant pour leçon {ext_id}"}

    result = await db.execute(select(Skill).where(Skill.external_id == skill_ext))
    skill = result.scalar_one_or_none()
    if not skill:
        return {"error": f"Compétence introuvable: {skill_ext}"}

    # Resolve micro_skill (optional)
    micro_skill_id = None
    ms_ext = lesson_data.get("micro_skill_external_id")
    if ms_ext:
        ms_result = await db.execute(
            select(MicroSkill).where(MicroSkill.external_id == ms_ext)
        )
        ms = ms_result.scalar_one_or_none()
        if ms:
            micro_skill_id = ms.id

    # Build fields
    fields = {
        "skill_id": skill.id,
        "micro_skill_id": micro_skill_id,
        "external_id": ext_id,
        "title": lesson_data.get("title", ""),
        "content_html": lesson_data.get("content_html"),
        "sections": lesson_data.get("sections"),
        "formula": lesson_data.get("formula"),
        "summary": lesson_data.get("summary"),
        "media_url": lesson_data.get("media_url"),
        "duration_minutes": lesson_data.get("duration_minutes", 5),
        "order": lesson_data.get("order", 0),
        "status": ContentStatus.PUBLISHED,
        "is_active": True,
    }

    # Upsert
    existing_result = await db.execute(
        select(MicroLesson).where(MicroLesson.external_id == ext_id)
    )
    existing = existing_result.scalar_one_or_none()

    if existing:
        for k, v in fields.items():
            setattr(existing, k, v)
        return {"action": "updated", "external_id": ext_id}
    else:
        db.add(MicroLesson(**fields))
        return {"action": "created", "external_id": ext_id}


async def import_lessons_file(
    db: AsyncSession,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    """Import multiple lessons from a JSON payload.

    Expected payload:
        {
            "schema_version": "1.0",
            "lessons": [ { ...lesson_data }, ... ]
        }
    """
    lessons = payload.get("lessons", [])
    stats = {"created": 0, "updated": 0, "errors": []}

    for idx, lesson_data in enumerate(lessons):
        try:
            result = await import_lesson(db, lesson_data)
            if "error" in result:
                stats["errors"].append({"index": idx, **result})
            elif result["action"] == "created":
                stats["created"] += 1
            elif result["action"] == "updated":
                stats["updated"] += 1
        except Exception as e:
            stats["errors"].append({
                "index": idx,
                "external_id": lesson_data.get("external_id", "?"),
                "error": str(e),
            })

    await db.commit()
    stats["total"] = len(lessons)
    return stats
