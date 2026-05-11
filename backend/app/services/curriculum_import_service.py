"""Service for importing a full curriculum tree (grade → subjects → domains → skills → micro_skills)."""
import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Domain, GradeLevel, MicroSkill, Skill, Subject
from app.schemas.content import CurriculumImportRequest, CurriculumImportResult


def _slugify(text: str) -> str:
    """Basic slug: lowercase, strip accents via NFD, keep alphanum/hyphens."""
    import unicodedata
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s]+", "-", text)
    return text[:120]


async def import_curriculum(db: AsyncSession, payload: CurriculumImportRequest) -> CurriculumImportResult:
    """Import/upsert a full curriculum tree in a single transaction."""
    result = CurriculumImportResult()

    try:
        # ── Grade Level ─────────────────────────────────────
        grade_data = payload.grade
        stmt = select(GradeLevel).where(GradeLevel.slug == grade_data.slug)
        grade_obj = (await db.execute(stmt)).scalar_one_or_none()
        if grade_obj:
            grade_obj.name = grade_data.name
            if grade_data.description is not None:
                grade_obj.description = grade_data.description
            result.updated += 1
        else:
            grade_obj = GradeLevel(
                name=grade_data.name,
                slug=grade_data.slug,
                description=grade_data.description,
            )
            db.add(grade_obj)
            result.created += 1
        result.grade_levels = 1
        await db.flush()

        # ── Subjects ────────────────────────────────────────
        for subj_node in payload.subjects:
            stmt = select(Subject).where(
                Subject.slug == subj_node.slug,
                Subject.grade_level_id == grade_obj.id,
            )
            subj_obj = (await db.execute(stmt)).scalar_one_or_none()
            if subj_obj:
                subj_obj.name = subj_node.name
                if subj_node.icon is not None:
                    subj_obj.icon = subj_node.icon
                if subj_node.color is not None:
                    subj_obj.color = subj_node.color
                subj_obj.order = subj_node.order
                result.updated += 1
            else:
                subj_obj = Subject(
                    grade_level_id=grade_obj.id,
                    name=subj_node.name,
                    slug=subj_node.slug,
                    icon=subj_node.icon,
                    color=subj_node.color,
                    order=subj_node.order,
                )
                db.add(subj_obj)
                result.created += 1
            result.subjects += 1
            await db.flush()

            # ── Domains ─────────────────────────────────────
            for dom_node in subj_node.domains:
                stmt = select(Domain).where(
                    Domain.slug == dom_node.slug,
                    Domain.subject_id == subj_obj.id,
                )
                dom_obj = (await db.execute(stmt)).scalar_one_or_none()
                if dom_obj:
                    dom_obj.name = dom_node.name
                    dom_obj.order = dom_node.order
                    result.updated += 1
                else:
                    dom_obj = Domain(
                        subject_id=subj_obj.id,
                        name=dom_node.name,
                        slug=dom_node.slug,
                        order=dom_node.order,
                    )
                    db.add(dom_obj)
                    result.created += 1
                result.domains += 1
                await db.flush()

                # ── Skills ──────────────────────────────────
                for sk_node in dom_node.skills:
                    skill_obj = None
                    # Try external_id first
                    if sk_node.external_id:
                        stmt = select(Skill).where(Skill.external_id == sk_node.external_id)
                        skill_obj = (await db.execute(stmt)).scalar_one_or_none()
                    # Fall back to slug + domain_id
                    if not skill_obj:
                        sk_slug = _slugify(sk_node.external_id or sk_node.name)
                        stmt = select(Skill).where(
                            Skill.slug == sk_slug,
                            Skill.domain_id == dom_obj.id,
                        )
                        skill_obj = (await db.execute(stmt)).scalar_one_or_none()

                    if skill_obj:
                        skill_obj.name = sk_node.name
                        skill_obj.order = sk_node.order
                        if sk_node.external_id:
                            skill_obj.external_id = sk_node.external_id
                        if sk_node.cep_frequency is not None:
                            skill_obj.cep_frequency = sk_node.cep_frequency
                        if sk_node.prerequisites is not None:
                            skill_obj.prerequisites = sk_node.prerequisites
                        if sk_node.common_mistakes is not None:
                            skill_obj.common_mistakes = sk_node.common_mistakes
                        if sk_node.exercise_types is not None:
                            skill_obj.exercise_types = sk_node.exercise_types
                        if sk_node.mastery_threshold is not None:
                            skill_obj.mastery_threshold = sk_node.mastery_threshold
                        if sk_node.trimester is not None:
                            skill_obj.trimester = sk_node.trimester
                        if sk_node.week_order is not None:
                            skill_obj.week_order = sk_node.week_order
                        # Ensure it's linked to this domain
                        skill_obj.domain_id = dom_obj.id
                        result.updated += 1
                    else:
                        sk_slug = _slugify(sk_node.external_id or sk_node.name)
                        skill_obj = Skill(
                            domain_id=dom_obj.id,
                            external_id=sk_node.external_id,
                            name=sk_node.name,
                            slug=sk_slug,
                            cep_frequency=sk_node.cep_frequency,
                            prerequisites=sk_node.prerequisites,
                            common_mistakes=sk_node.common_mistakes,
                            exercise_types=sk_node.exercise_types,
                            mastery_threshold=sk_node.mastery_threshold,
                            order=sk_node.order,
                            trimester=sk_node.trimester,
                            week_order=sk_node.week_order,
                        )
                        db.add(skill_obj)
                        result.created += 1
                    result.skills += 1
                    await db.flush()

                    # ── MicroSkills ─────────────────────────
                    for ms_node in sk_node.micro_skills:
                        stmt = select(MicroSkill).where(
                            MicroSkill.external_id == ms_node.external_id,
                        )
                        ms_obj = (await db.execute(stmt)).scalar_one_or_none()
                        if ms_obj:
                            ms_obj.name = ms_node.name
                            ms_obj.skill_id = skill_obj.id
                            ms_obj.difficulty_index = ms_node.difficulty_index
                            ms_obj.estimated_time_minutes = ms_node.estimated_time_minutes
                            ms_obj.bloom_taxonomy_level = ms_node.bloom_taxonomy_level
                            ms_obj.mastery_threshold = ms_node.mastery_threshold
                            ms_obj.cep_frequency = ms_node.cep_frequency
                            ms_obj.prerequisites = ms_node.prerequisites
                            ms_obj.recommended_exercise_types = ms_node.recommended_exercise_types
                            if ms_node.external_prerequisites is not None:
                                ms_obj.external_prerequisites = ms_node.external_prerequisites
                            ms_obj.order = ms_node.order
                            result.updated += 1
                        else:
                            ms_obj = MicroSkill(
                                skill_id=skill_obj.id,
                                external_id=ms_node.external_id,
                                name=ms_node.name,
                                difficulty_index=ms_node.difficulty_index,
                                estimated_time_minutes=ms_node.estimated_time_minutes,
                                bloom_taxonomy_level=ms_node.bloom_taxonomy_level,
                                mastery_threshold=ms_node.mastery_threshold,
                                cep_frequency=ms_node.cep_frequency,
                                prerequisites=ms_node.prerequisites,
                                recommended_exercise_types=ms_node.recommended_exercise_types,
                                external_prerequisites=ms_node.external_prerequisites,
                                order=ms_node.order,
                            )
                            db.add(ms_obj)
                            result.created += 1
                        result.micro_skills += 1
                        await db.flush()

        await db.commit()
    except Exception as e:
        await db.rollback()
        result.errors.append({"error": str(e)})

    return result
