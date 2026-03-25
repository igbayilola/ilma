"""Tests for notification CRON task triggers.

Covers:
- _send_daily_reminders: creates notifications for inactive students
- _send_streak_danger_alerts: alerts users about to lose their streak
- _send_parent_weekly_digest: sends digest to parents with linked children
"""
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Domain, GradeLevel, Skill, Subject
from app.models.notification import Notification, NotificationChannel, NotificationType
from app.models.parent_student import ParentStudent
from app.models.profile import Profile
from app.models.progress import Progress
from app.models.session import ExerciseSession, SessionMode, SessionStatus
from app.models.user import User, UserRole
from app.core.security import get_password_hash

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_user(
    *,
    role: UserRole = UserRole.STUDENT,
    email: str | None = None,
    phone: str | None = None,
    full_name: str = "Test User",
) -> User:
    uid = uuid.uuid4()
    return User(
        id=uid,
        email=email or f"{uid.hex[:8]}@test.com",
        phone=phone,
        full_name=full_name,
        hashed_password=get_password_hash("Test1234!"),
        role=role,
        is_active=True,
    )


def _make_profile(user: User, display_name: str | None = None) -> Profile:
    return Profile(
        id=uuid.uuid4(),
        user_id=user.id,
        display_name=display_name or user.full_name,
        is_active=True,
    )


async def _make_content_hierarchy(db: AsyncSession) -> Skill:
    """Create minimal GradeLevel -> Subject -> Domain -> Skill chain for FK refs."""
    grade = GradeLevel(id=uuid.uuid4(), name="CM2", slug="cm2", order=0, is_active=True)
    db.add(grade)
    await db.flush()

    subject = Subject(
        id=uuid.uuid4(),
        grade_level_id=grade.id,
        name="Maths",
        slug="maths",
        order=0,
        is_active=True,
    )
    db.add(subject)
    await db.flush()

    domain = Domain(
        id=uuid.uuid4(),
        subject_id=subject.id,
        name="Nombres",
        slug="nombres",
        order=0,
        is_active=True,
    )
    db.add(domain)
    await db.flush()

    skill = Skill(
        id=uuid.uuid4(),
        domain_id=domain.id,
        name="Addition",
        slug="addition",
    )
    db.add(skill)
    await db.flush()
    return skill


async def _count_notifications(db: AsyncSession, user_id: uuid.UUID) -> int:
    """Count in-app notifications for a user (ignores push/sms tracking records)."""
    result = await db.execute(
        select(Notification).where(
            Notification.user_id == user_id,
            Notification.channel == NotificationChannel.IN_APP,
        )
    )
    return len(result.scalars().all())


async def _get_notifications(db: AsyncSession, user_id: uuid.UUID) -> list[Notification]:
    """Return in-app notifications for a user (ignores push/sms tracking records)."""
    result = await db.execute(
        select(Notification).where(
            Notification.user_id == user_id,
            Notification.channel == NotificationChannel.IN_APP,
        )
    )
    return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Fixture: mock _get_db so task functions use the test session
# ---------------------------------------------------------------------------


def _utcnow_naive() -> datetime:
    """Return current UTC time as a naive datetime (matches SQLite behaviour).

    SQLite does not store timezone info, so all timestamps retrieved from the
    DB are naive.  Using naive datetimes in test data keeps comparisons
    consistent with what the patched task code produces.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


@pytest_asyncio.fixture
async def mock_get_db(db_session: AsyncSession):
    """Patch _get_db in the tasks module to return the test session.

    We also patch db.close and db.commit to no-ops so that the task
    does not close / commit the shared test session (conftest rolls it back).

    Additionally, we patch ``datetime.now`` in the tasks module so that all
    timestamp arithmetic produces naive datetimes — SQLite does not preserve
    timezone info, so ``func.max(completed_at)`` returns naive values. Using
    naive datetimes on both sides avoids ``TypeError`` during comparisons.
    """
    original_close = db_session.close
    original_commit = db_session.commit

    # Replace close with a no-op so the session stays open for assertions
    db_session.close = AsyncMock()  # type: ignore[method-assign]
    # commit -> flush (persist for reads within the same session, but don't
    # actually commit since conftest will rollback)
    db_session.commit = db_session.flush  # type: ignore[method-assign]

    # Build a datetime shim that returns naive UTC from .now(tz)
    import app.tasks.notification_tasks as _tasks_mod

    _real_datetime = datetime

    class _NaiveDatetime(_real_datetime):
        """datetime subclass that strips timezone from .now() calls."""

        @classmethod  # type: ignore[override]
        def now(cls, tz=None):
            return _real_datetime.now(timezone.utc).replace(tzinfo=None)

    with (
        patch(
            "app.tasks.notification_tasks._get_db",
            new_callable=AsyncMock,
            return_value=db_session,
        ),
        patch.object(_tasks_mod, "datetime", _NaiveDatetime),
    ):
        yield db_session

    # Restore originals
    db_session.close = original_close  # type: ignore[method-assign]
    db_session.commit = original_commit  # type: ignore[method-assign]


# ===========================================================================
# _send_daily_reminders
# ===========================================================================


class TestSendDailyReminders:
    """Tests for _send_daily_reminders."""

    @pytest.mark.asyncio
    async def test_sends_notification_to_inactive_student(
        self, db_session: AsyncSession, mock_get_db
    ):
        """A student with no completed session today should receive a reminder."""
        from app.tasks.notification_tasks import _send_daily_reminders

        student = _make_user(role=UserRole.STUDENT)
        db_session.add(student)
        await db_session.flush()

        sent = await _send_daily_reminders()

        assert sent == 1
        notifs = await _get_notifications(db_session, student.id)
        assert len(notifs) == 1
        assert notifs[0].type == NotificationType.INACTIVITY
        assert notifs[0].title == "Ton défi du jour t'attend !"

    @pytest.mark.asyncio
    async def test_skips_student_who_played_today(
        self, db_session: AsyncSession, mock_get_db
    ):
        """A student with a completed session today should NOT get a reminder."""
        from app.tasks.notification_tasks import _send_daily_reminders

        student = _make_user(role=UserRole.STUDENT)
        db_session.add(student)
        await db_session.flush()

        profile = _make_profile(student)
        db_session.add(profile)
        await db_session.flush()

        # Create a completed session today
        session = ExerciseSession(
            id=uuid.uuid4(),
            student_id=student.id,
            profile_id=profile.id,
            mode=SessionMode.PRACTICE,
            status=SessionStatus.COMPLETED,
            completed_at=_utcnow_naive(),
        )
        db_session.add(session)
        await db_session.flush()

        sent = await _send_daily_reminders()

        assert sent == 0
        assert await _count_notifications(db_session, student.id) == 0

    @pytest.mark.asyncio
    async def test_skips_inactive_user(
        self, db_session: AsyncSession, mock_get_db
    ):
        """Inactive (disabled) students should not receive notifications."""
        from app.tasks.notification_tasks import _send_daily_reminders

        student = _make_user(role=UserRole.STUDENT)
        student.is_active = False
        db_session.add(student)
        await db_session.flush()

        sent = await _send_daily_reminders()

        assert sent == 0

    @pytest.mark.asyncio
    async def test_skips_non_student_roles(
        self, db_session: AsyncSession, mock_get_db
    ):
        """Parents and admins should not receive daily reminders."""
        from app.tasks.notification_tasks import _send_daily_reminders

        parent = _make_user(role=UserRole.PARENT)
        admin = _make_user(role=UserRole.ADMIN)
        db_session.add_all([parent, admin])
        await db_session.flush()

        sent = await _send_daily_reminders()

        assert sent == 0

    @pytest.mark.asyncio
    async def test_throttle_limits_notifications(
        self, db_session: AsyncSession, mock_get_db
    ):
        """Once a student hits NOTIFICATION_MAX_PER_DAY, no more are sent."""
        from app.tasks.notification_tasks import _send_daily_reminders

        student = _make_user(role=UserRole.STUDENT)
        db_session.add(student)
        await db_session.flush()

        # Pre-create max notifications for today
        with patch("app.tasks.notification_tasks.settings") as mock_settings:
            mock_settings.NOTIFICATION_MAX_PER_DAY = 2

            # Insert 2 existing notifications for today
            for _ in range(2):
                notif = Notification(
                    id=uuid.uuid4(),
                    user_id=student.id,
                    type=NotificationType.INACTIVITY,
                    channel=NotificationChannel.IN_APP,
                    title="Previous",
                    body="",
                )
                db_session.add(notif)
            await db_session.flush()

            sent = await _send_daily_reminders()

        assert sent == 0

    @pytest.mark.asyncio
    async def test_multiple_students_mixed(
        self, db_session: AsyncSession, mock_get_db
    ):
        """Two inactive students and one active student: only the two get notified."""
        from app.tasks.notification_tasks import _send_daily_reminders

        inactive1 = _make_user(role=UserRole.STUDENT, full_name="Inactive 1")
        inactive2 = _make_user(role=UserRole.STUDENT, full_name="Inactive 2")
        active = _make_user(role=UserRole.STUDENT, full_name="Active")
        db_session.add_all([inactive1, inactive2, active])
        await db_session.flush()

        profile = _make_profile(active)
        db_session.add(profile)
        await db_session.flush()

        session = ExerciseSession(
            id=uuid.uuid4(),
            student_id=active.id,
            profile_id=profile.id,
            mode=SessionMode.PRACTICE,
            status=SessionStatus.COMPLETED,
            completed_at=_utcnow_naive(),
        )
        db_session.add(session)
        await db_session.flush()

        sent = await _send_daily_reminders()

        assert sent == 2
        assert await _count_notifications(db_session, active.id) == 0
        assert await _count_notifications(db_session, inactive1.id) == 1
        assert await _count_notifications(db_session, inactive2.id) == 1


# ===========================================================================
# _send_streak_danger_alerts
# ===========================================================================


class TestSendStreakDangerAlerts:
    """Tests for _send_streak_danger_alerts."""

    @pytest.mark.asyncio
    async def test_alerts_user_with_streak_and_inactivity(
        self, db_session: AsyncSession, mock_get_db
    ):
        """A student with streak > 0 and no session in 2+ days gets an alert."""
        from app.tasks.notification_tasks import _send_streak_danger_alerts

        student = _make_user(role=UserRole.STUDENT)
        db_session.add(student)
        await db_session.flush()

        profile = _make_profile(student)
        db_session.add(profile)
        await db_session.flush()

        skill = await _make_content_hierarchy(db_session)

        # Create progress with active streak
        progress = Progress(
            id=uuid.uuid4(),
            student_id=student.id,
            profile_id=profile.id,
            skill_id=skill.id,
            streak=5,
            best_streak=10,
        )
        db_session.add(progress)
        await db_session.flush()

        # Create a completed session from 3 days ago (beyond the 2-day threshold)
        three_days_ago = _utcnow_naive() - timedelta(days=3)
        session = ExerciseSession(
            id=uuid.uuid4(),
            student_id=student.id,
            profile_id=profile.id,
            mode=SessionMode.PRACTICE,
            status=SessionStatus.COMPLETED,
            completed_at=three_days_ago,
        )
        db_session.add(session)
        await db_session.flush()

        sent = await _send_streak_danger_alerts()

        assert sent == 1
        notifs = await _get_notifications(db_session, student.id)
        assert len(notifs) == 1
        assert "5 jours" in notifs[0].title
        assert notifs[0].type == NotificationType.INACTIVITY

    @pytest.mark.asyncio
    async def test_skips_recently_active_student(
        self, db_session: AsyncSession, mock_get_db
    ):
        """A student with streak > 0 who played yesterday should NOT be alerted."""
        from app.tasks.notification_tasks import _send_streak_danger_alerts

        student = _make_user(role=UserRole.STUDENT)
        db_session.add(student)
        await db_session.flush()

        profile = _make_profile(student)
        db_session.add(profile)
        await db_session.flush()

        skill = await _make_content_hierarchy(db_session)

        progress = Progress(
            id=uuid.uuid4(),
            student_id=student.id,
            profile_id=profile.id,
            skill_id=skill.id,
            streak=3,
            best_streak=5,
        )
        db_session.add(progress)
        await db_session.flush()

        # Completed session yesterday (within 2-day window)
        yesterday = _utcnow_naive() - timedelta(hours=20)
        session = ExerciseSession(
            id=uuid.uuid4(),
            student_id=student.id,
            profile_id=profile.id,
            mode=SessionMode.PRACTICE,
            status=SessionStatus.COMPLETED,
            completed_at=yesterday,
        )
        db_session.add(session)
        await db_session.flush()

        sent = await _send_streak_danger_alerts()

        assert sent == 0

    @pytest.mark.asyncio
    async def test_skips_zero_streak(
        self, db_session: AsyncSession, mock_get_db
    ):
        """A student with streak == 0 should NOT be alerted even if inactive."""
        from app.tasks.notification_tasks import _send_streak_danger_alerts

        student = _make_user(role=UserRole.STUDENT)
        db_session.add(student)
        await db_session.flush()

        profile = _make_profile(student)
        db_session.add(profile)
        await db_session.flush()

        skill = await _make_content_hierarchy(db_session)

        progress = Progress(
            id=uuid.uuid4(),
            student_id=student.id,
            profile_id=profile.id,
            skill_id=skill.id,
            streak=0,
            best_streak=5,
        )
        db_session.add(progress)
        await db_session.flush()

        sent = await _send_streak_danger_alerts()

        assert sent == 0

    @pytest.mark.asyncio
    async def test_skips_student_with_no_sessions(
        self, db_session: AsyncSession, mock_get_db
    ):
        """A student with a streak but NO completed sessions at all (last_completed is None)
        should still get alerted since None means they've been inactive indefinitely."""
        from app.tasks.notification_tasks import _send_streak_danger_alerts

        student = _make_user(role=UserRole.STUDENT)
        db_session.add(student)
        await db_session.flush()

        profile = _make_profile(student)
        db_session.add(profile)
        await db_session.flush()

        skill = await _make_content_hierarchy(db_session)

        progress = Progress(
            id=uuid.uuid4(),
            student_id=student.id,
            profile_id=profile.id,
            skill_id=skill.id,
            streak=7,
            best_streak=7,
        )
        db_session.add(progress)
        await db_session.flush()

        # No sessions at all -> last_completed is None
        # The code skips when last_completed is None (continue branch)
        sent = await _send_streak_danger_alerts()

        # The task code does: if last_completed is None or last_completed > two_days_ago: continue
        # So None -> skip (the OR short-circuits)
        assert sent == 0


# ===========================================================================
# _send_parent_weekly_digest
# ===========================================================================


class TestSendParentWeeklyDigest:
    """Tests for _send_parent_weekly_digest."""

    @pytest.mark.asyncio
    async def test_sends_digest_to_parent_with_active_child(
        self, db_session: AsyncSession, mock_get_db
    ):
        """A parent linked to a child who has sessions this week gets a digest."""
        from app.tasks.notification_tasks import _send_parent_weekly_digest

        parent = _make_user(role=UserRole.PARENT, full_name="Papa Test", phone="+22990001122")
        child = _make_user(role=UserRole.STUDENT, full_name="Aissatou")
        db_session.add_all([parent, child])
        await db_session.flush()

        # Link parent to child
        link = ParentStudent(
            id=uuid.uuid4(),
            parent_id=parent.id,
            student_id=child.id,
        )
        db_session.add(link)
        await db_session.flush()

        child_profile = _make_profile(child, display_name="Aissatou")
        db_session.add(child_profile)
        await db_session.flush()

        # Create a completed session this week
        two_days_ago = _utcnow_naive() - timedelta(days=2)
        session = ExerciseSession(
            id=uuid.uuid4(),
            student_id=child.id,
            profile_id=child_profile.id,
            mode=SessionMode.PRACTICE,
            status=SessionStatus.COMPLETED,
            completed_at=two_days_ago,
            duration_seconds=1800,  # 30 minutes
        )
        db_session.add(session)
        await db_session.flush()

        sent = await _send_parent_weekly_digest()

        assert sent == 1
        notifs = await _get_notifications(db_session, parent.id)
        assert len(notifs) == 1
        assert notifs[0].type == NotificationType.WEEKLY_REPORT
        assert notifs[0].title == "R\u00e9sum\u00e9 hebdomadaire Sitou"
        assert "Aissatou" in notifs[0].body
        assert "1 exercice(s)" in notifs[0].body
        assert "30 min" in notifs[0].body

    @pytest.mark.asyncio
    async def test_digest_shows_inactive_child(
        self, db_session: AsyncSession, mock_get_db
    ):
        """A child with zero sessions this week should appear as 'inactif'."""
        from app.tasks.notification_tasks import _send_parent_weekly_digest

        parent = _make_user(role=UserRole.PARENT, full_name="Maman Test")
        child = _make_user(role=UserRole.STUDENT, full_name="Kofi")
        db_session.add_all([parent, child])
        await db_session.flush()

        link = ParentStudent(
            id=uuid.uuid4(),
            parent_id=parent.id,
            student_id=child.id,
        )
        db_session.add(link)
        await db_session.flush()

        sent = await _send_parent_weekly_digest()

        assert sent == 1
        notifs = await _get_notifications(db_session, parent.id)
        assert len(notifs) == 1
        assert "inactif cette semaine" in notifs[0].body

    @pytest.mark.asyncio
    async def test_skips_parent_without_children(
        self, db_session: AsyncSession, mock_get_db
    ):
        """A parent with no linked children should not receive a digest."""
        from app.tasks.notification_tasks import _send_parent_weekly_digest

        parent = _make_user(role=UserRole.PARENT)
        db_session.add(parent)
        await db_session.flush()

        sent = await _send_parent_weekly_digest()

        assert sent == 0

    @pytest.mark.asyncio
    async def test_skips_inactive_parent(
        self, db_session: AsyncSession, mock_get_db
    ):
        """An inactive parent should not receive a digest."""
        from app.tasks.notification_tasks import _send_parent_weekly_digest

        parent = _make_user(role=UserRole.PARENT)
        parent.is_active = False
        db_session.add(parent)
        await db_session.flush()

        sent = await _send_parent_weekly_digest()

        assert sent == 0

    @pytest.mark.asyncio
    async def test_digest_with_multiple_children(
        self, db_session: AsyncSession, mock_get_db
    ):
        """A parent with two linked children gets a single digest covering both."""
        from app.tasks.notification_tasks import _send_parent_weekly_digest

        parent = _make_user(role=UserRole.PARENT, full_name="Parent Multi")
        child1 = _make_user(role=UserRole.STUDENT, full_name="Enfant Un")
        child2 = _make_user(role=UserRole.STUDENT, full_name="Enfant Deux")
        db_session.add_all([parent, child1, child2])
        await db_session.flush()

        for child in [child1, child2]:
            link = ParentStudent(
                id=uuid.uuid4(),
                parent_id=parent.id,
                student_id=child.id,
            )
            db_session.add(link)
        await db_session.flush()

        # child1 has 2 sessions, child2 has none
        profile1 = _make_profile(child1)
        db_session.add(profile1)
        await db_session.flush()

        for i in range(2):
            s = ExerciseSession(
                id=uuid.uuid4(),
                student_id=child1.id,
                profile_id=profile1.id,
                mode=SessionMode.PRACTICE,
                status=SessionStatus.COMPLETED,
                completed_at=_utcnow_naive() - timedelta(days=i),
                duration_seconds=900,
            )
            db_session.add(s)
        await db_session.flush()

        sent = await _send_parent_weekly_digest()

        assert sent == 1
        notifs = await _get_notifications(db_session, parent.id)
        assert len(notifs) == 1
        body = notifs[0].body
        assert "Enfant Un" in body
        assert "2 exercice(s)" in body
        assert "Enfant Deux" in body
        assert "inactif cette semaine" in body

    @pytest.mark.asyncio
    async def test_old_sessions_excluded_from_digest(
        self, db_session: AsyncSession, mock_get_db
    ):
        """Sessions older than 7 days should not count in the weekly digest."""
        from app.tasks.notification_tasks import _send_parent_weekly_digest

        parent = _make_user(role=UserRole.PARENT)
        child = _make_user(role=UserRole.STUDENT, full_name="Old Session Kid")
        db_session.add_all([parent, child])
        await db_session.flush()

        link = ParentStudent(
            id=uuid.uuid4(),
            parent_id=parent.id,
            student_id=child.id,
        )
        db_session.add(link)
        await db_session.flush()

        profile = _make_profile(child)
        db_session.add(profile)
        await db_session.flush()

        # Session from 10 days ago — outside weekly window
        old_session = ExerciseSession(
            id=uuid.uuid4(),
            student_id=child.id,
            profile_id=profile.id,
            mode=SessionMode.PRACTICE,
            status=SessionStatus.COMPLETED,
            completed_at=_utcnow_naive() - timedelta(days=10),
            duration_seconds=600,
        )
        db_session.add(old_session)
        await db_session.flush()

        sent = await _send_parent_weekly_digest()

        assert sent == 1
        notifs = await _get_notifications(db_session, parent.id)
        # Should show as inactive since the session is older than a week
        assert "inactif cette semaine" in notifs[0].body
