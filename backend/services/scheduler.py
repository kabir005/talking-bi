"""
Scheduler Service
APScheduler-based task scheduling for automated briefings.
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def init_scheduler():
    """Initialize scheduler on startup."""
    scheduler.start()
    logger.info("Scheduler started")


async def shutdown_scheduler():
    """Shutdown scheduler on app shutdown."""
    scheduler.shutdown()
    logger.info("Scheduler stopped")


def schedule_briefing(
    briefing_id: str,
    dataset_id: str,
    recipients: list[str],
    schedule: str,
    timezone: str = "UTC",
    config: dict = None
):
    """Schedule a recurring briefing."""
    try:
        tz = pytz.timezone(timezone)
        trigger = CronTrigger.from_crontab(schedule, timezone=tz)
        
        scheduler.add_job(
            func=generate_and_send_briefing,
            trigger=trigger,
            args=[briefing_id, dataset_id, recipients, config or {}],
            id=briefing_id,
            replace_existing=True
        )
        
        logger.info(f"Scheduled briefing {briefing_id} with schedule: {schedule}")
        return True
    except Exception as e:
        logger.error(f"Failed to schedule briefing: {e}")
        raise


def unschedule_briefing(briefing_id: str):
    """Remove a scheduled briefing."""
    try:
        scheduler.remove_job(briefing_id)
        logger.info(f"Unscheduled briefing {briefing_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to unschedule briefing: {e}")
        return False


def get_next_run_time(briefing_id: str):
    """Get next scheduled run time for a briefing."""
    try:
        job = scheduler.get_job(briefing_id)
        if job:
            return job.next_run_time
        return None
    except:
        return None


async def generate_and_send_briefing(
    briefing_id: str,
    dataset_id: str,
    recipients: list[str],
    config: dict
):
    """Generate briefing and send via email."""
    try:
        logger.info(f"Generating briefing {briefing_id} for dataset {dataset_id}")
        
        # Import here to avoid circular dependencies
        from services.email_service import send_briefing_email
        from services.briefing_generator import generate_briefing_content
        
        # Generate briefing content
        content = await generate_briefing_content(dataset_id, config)
        
        # Send email
        await send_briefing_email(
            recipients=recipients,
            subject=content["subject"],
            html_body=content["html"],
            pdf_attachment=content["pdf"],
            pdf_filename=content["pdf_filename"]
        )
        
        logger.info(f"Briefing {briefing_id} sent successfully to {len(recipients)} recipients")
        
    except Exception as e:
        logger.error(f"Failed to generate/send briefing {briefing_id}: {e}")
