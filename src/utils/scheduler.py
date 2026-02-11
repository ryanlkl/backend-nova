"""
Scheduler Module

Handles automated background tasks using APScheduler.
Currently schedules:
- Daily refresh of Bank of England payment data at 6 AM UTC
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from src.utils.db import SessionLocal
from src.services.payment import PaymentService
import logging

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler()


async def refresh_boe_data_job():
    """
    Background job to refresh Bank of England data.
    
    Runs automatically at scheduled times (default: daily at 6 AM UTC).
    Creates its own database session since it runs outside request context.
    """
    logger.info("Starting scheduled BoE data refresh...")
    
    db = SessionLocal()
    try:
        result = await PaymentService.fetch_boe_data(db)
        if result.get("success"):
            logger.info(f"Scheduled refresh complete: {result.get('records_saved')} records saved")
        else:
            logger.error(f"Scheduled refresh failed: {result.get('error')}")
    except Exception as e:
        logger.error(f"Scheduled refresh error: {str(e)}")
    finally:
        db.close()


def start_scheduler():
    """
    Start the background scheduler.
    
    Schedules:
    - BoE data refresh: Daily at 6:00 AM UTC
    
    The scheduler runs in the background and doesn't block the main application.
    """
    # Schedule daily BoE data refresh at 6 AM UTC
    # BoE typically updates their data in the morning UK time
    scheduler.add_job(
        refresh_boe_data_job,
        trigger=CronTrigger(hour=6, minute=0),  # 6:00 AM UTC daily
        id="boe_data_refresh",
        name="Daily BoE Data Refresh",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started - BoE data will refresh daily at 6:00 AM UTC")


def stop_scheduler():
    """Stop the scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
