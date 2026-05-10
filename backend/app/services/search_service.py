"""Full-text search service using PostgreSQL pg_trgm similarity."""
from sqlalchemy import func, literal, select, union_all
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import ContentStatus, Domain, MicroLesson, Question, Skill

# Minimum trigram similarity threshold (0.0–1.0)
_MIN_SIMILARITY = 0.15


class SearchService:
    async def search(
        self,
        db: AsyncSession,
        query: str,
        *,
        limit: int = 20,
    ) -> list[dict]:
        """Search across skills, questions, domains, and lessons.

        Returns a flat list of results sorted by relevance, each with:
        ``{type, id, title, subtitle, score, skill_id, domain_id}``
        """
        if not query or len(query.strip()) < 2:
            return []

        q = query.strip()

        # Use pg_trgm similarity() for ranking
        sim = func.similarity

        # ── Skills ────────────────────────────────────────
        skill_q = (
            select(
                literal("skill").label("type"),
                Skill.id.label("id"),
                Skill.name.label("title"),
                Skill.description.label("subtitle"),
                sim(Skill.name, q).label("score"),
                Skill.id.label("skill_id"),
                Skill.domain_id.label("domain_id"),
            )
            .where(
                Skill.is_active.is_(True),
                sim(Skill.name, q) >= _MIN_SIMILARITY,
            )
        )

        # ── Domains ───────────────────────────────────────
        domain_q = (
            select(
                literal("domain").label("type"),
                Domain.id.label("id"),
                Domain.name.label("title"),
                Domain.description.label("subtitle"),
                sim(Domain.name, q).label("score"),
                literal(None).label("skill_id"),
                Domain.id.label("domain_id"),
            )
            .where(
                Domain.is_active.is_(True),
                sim(Domain.name, q) >= _MIN_SIMILARITY,
            )
        )

        # ── Questions ─────────────────────────────────────
        question_q = (
            select(
                literal("question").label("type"),
                Question.id.label("id"),
                func.left(Question.text, 120).label("title"),
                Question.explanation.label("subtitle"),
                sim(Question.text, q).label("score"),
                Question.skill_id.label("skill_id"),
                literal(None).label("domain_id"),
            )
            .where(
                Question.is_active.is_(True),
                Question.status == ContentStatus.PUBLISHED,
                sim(Question.text, q) >= _MIN_SIMILARITY,
            )
        )

        # ── Lessons ───────────────────────────────────────
        lesson_q = (
            select(
                literal("lesson").label("type"),
                MicroLesson.id.label("id"),
                MicroLesson.title.label("title"),
                MicroLesson.summary.label("subtitle"),
                sim(MicroLesson.title, q).label("score"),
                MicroLesson.skill_id.label("skill_id"),
                literal(None).label("domain_id"),
            )
            .where(
                MicroLesson.is_active.is_(True),
                MicroLesson.status == ContentStatus.PUBLISHED,
                sim(MicroLesson.title, q) >= _MIN_SIMILARITY,
            )
        )

        # ── Combine & sort ────────────────────────────────
        combined = union_all(skill_q, domain_q, question_q, lesson_q).subquery()
        stmt = (
            select(combined)
            .order_by(combined.c.score.desc())
            .limit(limit)
        )

        result = await db.execute(stmt)
        rows = result.all()

        return [
            {
                "type": row.type,
                "id": str(row.id),
                "title": row.title or "",
                "subtitle": (row.subtitle or "")[:200],
                "score": round(float(row.score), 3),
                "skill_id": str(row.skill_id) if row.skill_id else None,
                "domain_id": str(row.domain_id) if row.domain_id else None,
            }
            for row in rows
        ]


search_service = SearchService()
