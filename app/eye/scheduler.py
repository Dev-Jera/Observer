"""Background scheduler for the Digital Eye."""
import logging
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler

from .scraper import run_scrape
from ..database import SessionLocal
from ..services.sms import deliver_due_sms
from ..config import settings

logger = logging.getLogger("citizeneye.scheduler")
scheduler = BackgroundScheduler()


def scheduled_scrape():
    try:
        stats = run_scrape()
        logger.info("Digital Eye run: %s", stats)
    except Exception:
        logger.exception("Scheduled scrape failed")


def scheduled_sms_delivery():
    db = SessionLocal()
    try:
        delivered = deliver_due_sms(db)
        if delivered:
            logger.info("Delivered %s SMS digest(s)", delivered)
    except Exception:
        logger.exception("Scheduled SMS delivery failed")
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(
        scheduled_scrape,
        "interval",
        minutes=settings.scrape_interval_minutes,
        id="digital_eye",
        replace_existing=True,
        next_run_time=datetime.now(timezone.utc),
    )
    scheduler.add_job(
        scheduled_sms_delivery,
        "interval",
        minutes=settings.sms_delivery_interval_minutes,
        id="sms_delivery",
        replace_existing=True,
        next_run_time=datetime.now(timezone.utc),
    )
    scheduler.start()
    logger.info("Digital Eye scheduler started (%s min interval)", settings.scrape_interval_minutes)


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
