"""APScheduler configuration — CRON jobs for ILMA."""
import logging
import os

from app.core.config import settings

logger = logging.getLogger(__name__)

# Avoid importing APScheduler during tests or when disabled
_TESTING = os.environ.get("TESTING", "").lower() in ("1", "true", "yes")
_scheduler = None


def _get_scheduler():
    global _scheduler
    if _scheduler is None and not _TESTING:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        _scheduler = AsyncIOScheduler()
    return _scheduler


def setup_scheduler() -> None:
    """Register all scheduled jobs. Call once at app startup."""
    scheduler = _get_scheduler()
    if scheduler is None or not settings.NOTIFICATIONS_ENABLED:
        logger.info("[Scheduler] Notifications disabled or test mode, skipping setup")
        return

    from apscheduler.triggers.cron import CronTrigger

    from app.tasks.notification_tasks import (
        _send_daily_reminders,
        _send_parent_weekly_digest,
        _send_streak_danger_alerts,
    )

    # Daily reminder: every day at 16:00 UTC (17:00 WAT / Benin time)
    scheduler.add_job(
        _send_daily_reminders,
        CronTrigger(hour=16, minute=0),
        id="daily_reminder",
        name="Daily exercise reminder",
        replace_existing=True,
    )

    # Streak danger: every day at 10:00 UTC (11:00 WAT)
    scheduler.add_job(
        _send_streak_danger_alerts,
        CronTrigger(hour=10, minute=0),
        id="streak_danger",
        name="Streak danger alerts",
        replace_existing=True,
    )

    # Parent weekly digest: Sunday at 17:00 UTC (18:00 WAT)
    scheduler.add_job(
        _send_parent_weekly_digest,
        CronTrigger(day_of_week="sun", hour=17, minute=0),
        id="parent_digest",
        name="Weekly parent digest",
        replace_existing=True,
    )

    # Content quality: check question success rates daily at 6:00 UTC
    from app.tasks.content_tasks import _check_question_success_rates

    scheduler.add_job(
        _check_question_success_rates,
        CronTrigger(hour=6, minute=0),
        id="content_quality",
        name="Check question success rates",
        replace_existing=True,
    )

    # Social: expire old challenges every hour
    from app.tasks.social_tasks import _expire_challenges

    scheduler.add_job(
        _expire_challenges,
        CronTrigger(minute=0),  # Every hour at :00
        id="expire_challenges",
        name="Expire old challenges",
        replace_existing=True,
    )

    logger.info("[Scheduler] Registered %d jobs", len(scheduler.get_jobs()))


def start_scheduler() -> None:
    """Start the scheduler (call after setup)."""
    scheduler = _get_scheduler()
    if scheduler is not None and not scheduler.running and scheduler.get_jobs():
        scheduler.start()
        logger.info("[Scheduler] Started")


def stop_scheduler() -> None:
    """Gracefully stop the scheduler."""
    scheduler = _get_scheduler()
    if scheduler is not None and scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("[Scheduler] Stopped")
