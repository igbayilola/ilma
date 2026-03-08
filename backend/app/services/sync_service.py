"""Offline sync engine: process batch events with idempotence and conflict resolution."""
from datetime import datetime, timezone
from uuid import UUID as PyUUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Question
from app.models.offline import ContentPack
from app.models.profile import Profile
from app.models.session import Attempt, ExerciseSession, SessionStatus
from app.schemas.offline import SyncEvent, SyncEventResult
from app.services.badge_service import badge_service
from app.services.progress_service import progress_service


class SyncService:
    async def process_batch(
        self, db: AsyncSession, profile: Profile, events: list[SyncEvent]
    ) -> dict:
        """Process a batch of offline events. Priority: attempts → badges → profile."""
        results: list[SyncEventResult] = []
        accepted = 0
        duplicates = 0
        errors = 0

        # Sort by priority: attempt_created first, then session_completed, badge_gained, profile_updated
        priority = {"attempt_created": 0, "session_completed": 1, "badge_gained": 2, "profile_updated": 3}
        sorted_events = sorted(events, key=lambda e: priority.get(e.event_type, 99))

        for event in sorted_events:
            try:
                result = await self._process_event(db, profile, event)
                results.append(result)
                if result.status == "accepted":
                    accepted += 1
                elif result.status == "duplicate":
                    duplicates += 1
                else:
                    errors += 1
            except Exception as e:
                errors += 1
                results.append(
                    SyncEventResult(
                        client_event_id=event.client_event_id,
                        status="error",
                        message=str(e),
                    )
                )

        return {
            "processed": len(events),
            "accepted": accepted,
            "duplicates": duplicates,
            "errors": errors,
            "results": results,
        }

    async def _process_event(
        self, db: AsyncSession, profile: Profile, event: SyncEvent
    ) -> SyncEventResult:
        handler = getattr(self, f"_handle_{event.event_type}", None)
        if not handler:
            return SyncEventResult(
                client_event_id=event.client_event_id,
                status="error",
                message=f"Unknown event type: {event.event_type}",
            )
        return await handler(db, profile, event)

    # ── Attempt created ────────────────────────────────────
    async def _handle_attempt_created(
        self, db: AsyncSession, profile: Profile, event: SyncEvent
    ) -> SyncEventResult:
        eid = event.client_event_id
        # Idempotence check
        existing = await db.execute(select(Attempt).where(Attempt.client_event_id == eid))
        if existing.scalar_one_or_none():
            return SyncEventResult(client_event_id=eid, status="duplicate")

        p = event.payload
        question_id = PyUUID(p["question_id"]) if p.get("question_id") else None
        session_id = PyUUID(p["session_id"]) if p.get("session_id") else None
        skill_id = PyUUID(p["skill_id"]) if p.get("skill_id") else None
        answer = p.get("answer")
        time_spent = p.get("time_spent_seconds")

        # Check correct answer
        is_correct = False
        question = None
        if question_id:
            q_result = await db.execute(select(Question).where(Question.id == question_id))
            question = q_result.scalar_one_or_none()
            if question:
                correct = question.correct_answer
                if isinstance(correct, str) and isinstance(answer, str):
                    is_correct = correct.strip().lower() == answer.strip().lower()
                else:
                    is_correct = correct == answer

        attempt = Attempt(
            session_id=session_id,
            question_id=question_id,
            profile_id=profile.id,
            client_event_id=eid,
            answer=answer,
            is_correct=is_correct,
            points_earned=p.get("points_earned", 1 if is_correct else 0),
            time_spent_seconds=time_spent,
            synced_at=datetime.now(timezone.utc),
        )
        db.add(attempt)
        await db.flush()

        # Update progress — best-score conflict resolution happens in progress_service
        if question_id and skill_id:
            await progress_service.update_progress_after_attempt(
                db, profile.id, skill_id, is_correct,
                micro_skill_id=question.micro_skill_id if question else None,
            )

        return SyncEventResult(client_event_id=eid, status="accepted")

    # ── Session completed ──────────────────────────────────
    async def _handle_session_completed(
        self, db: AsyncSession, profile: Profile, event: SyncEvent
    ) -> SyncEventResult:
        eid = event.client_event_id
        p = event.payload
        raw_sid = p.get("session_id")

        if not raw_sid:
            return SyncEventResult(client_event_id=eid, status="error", message="Missing session_id")

        session_id = PyUUID(raw_sid)
        result = await db.execute(
            select(ExerciseSession).where(ExerciseSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            return SyncEventResult(client_event_id=eid, status="error", message="Session not found")

        if session.status == SessionStatus.COMPLETED:
            return SyncEventResult(client_event_id=eid, status="duplicate")

        session.status = SessionStatus.COMPLETED
        session.completed_at = event.timestamp
        session.score = p.get("score", session.score)
        session.correct_answers = p.get("correct_answers", session.correct_answers)
        session.synced_at = datetime.now(timezone.utc)
        await db.flush()

        # Award badges after session
        await badge_service.award_badges(db, profile.id)

        return SyncEventResult(client_event_id=eid, status="accepted")

    # ── Badge gained ───────────────────────────────────────
    async def _handle_badge_gained(
        self, db: AsyncSession, profile: Profile, event: SyncEvent
    ) -> SyncEventResult:
        eid = event.client_event_id
        p = event.payload
        badge_code = p.get("badge_code")
        if not badge_code:
            return SyncEventResult(client_event_id=eid, status="error", message="Missing badge_code")

        created = await badge_service.sync_badge_event(
            db, profile.id, badge_code, eid, event.timestamp
        )
        return SyncEventResult(
            client_event_id=eid,
            status="accepted" if created else "duplicate",
        )

    # ── Profile updated ────────────────────────────────────
    async def _handle_profile_updated(
        self, db: AsyncSession, profile: Profile, event: SyncEvent
    ) -> SyncEventResult:
        eid = event.client_event_id
        p = event.payload

        # Last-write-wins: update profile fields
        if "display_name" in p:
            profile.display_name = p["display_name"]
        if "avatar_url" in p:
            profile.avatar_url = p["avatar_url"]

        db.add(profile)
        await db.flush()
        return SyncEventResult(client_event_id=eid, status="accepted")

    # ── Content packs ──────────────────────────────────────
    async def list_packs(self, db: AsyncSession) -> list[ContentPack]:
        result = await db.execute(
            select(ContentPack).where(ContentPack.published_at.isnot(None)).order_by(ContentPack.name)
        )
        return list(result.scalars().all())


sync_service = SyncService()
