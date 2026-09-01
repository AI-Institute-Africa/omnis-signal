from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from rq import Queue
from redis import Redis
import asyncio
from app.config import settings
from app.jobs.tasks import scrape_source
from app.db.session import get_db_session
from app.db.models import Source

scheduler = AsyncIOScheduler()

def get_queue():
    try:
        redis_conn = Redis.from_url(settings.REDIS_URL)
        redis_conn.ping()
        return Queue(connection=redis_conn)
    except:
        return None

def run_scrape_task(source_id: int):
    """Wrapper to run scrape with optional Redis queue."""
    queue = get_queue()
    if queue:
        try:
            queue.enqueue(scrape_source, source_id)
            return
        except Exception as e:
            print(f"Failed to enqueue in Redis: {e}")
    
    # Fallback: Run directly (since this is called from AsyncIOScheduler, 
    # we should ideally run it in a thread or separate process, 
    # but for now we'll just call it if it's async-safe or use a thread)
    from threading import Thread
    Thread(target=scrape_source, args=(source_id,)).start()

def send_4h_report_job():
    try:
        from app.services.email_reporter import EmailReporterService
        import logging
        s_logger = logging.getLogger("app.scheduler")
        s_logger.info("Executing scheduled 4-hour market tariff digest email dispatch...")
        res = EmailReporterService.send_4h_digest_email()
        s_logger.info(f"4-hour digest dispatch completed: status={res.get('status')}, sent={res.get('sent_count', 0)}")
    except Exception as e:
        import logging
        s_logger = logging.getLogger("app.scheduler")
        s_logger.error(f"Error executing 4-hour email report job: {e}")

def send_12h_report_job():
    send_4h_report_job()

def schedule_recurring_scrapes():
    db = next(get_db_session())
    try:
        sources = db.query(Source).filter(Source.schedule.isnot(None)).all()
        for source in sources:
            scheduler.add_job(
                func=lambda sid=source.id: run_scrape_task(sid),
                trigger=CronTrigger.from_crontab(source.schedule),
                id=f"scrape_{source.id}",
                replace_existing=True
            )
    finally:
        db.close()

    # Schedule 4-Hour Email Comprehensive Product & Service Price Digest
    scheduler.add_job(
        func=send_4h_report_job,
        trigger=CronTrigger(hour="0,4,8,12,16,20", minute="0"),
        id="email_4h_price_digest_report",
        replace_existing=True
    )

def start_scheduler():
    schedule_recurring_scrapes()
    scheduler.start()
    import logging
    s_logger = logging.getLogger("app.scheduler")
    s_logger.info("APScheduler successfully initialized and started with 4-hour email digest trigger.")

def stop_scheduler():
    scheduler.shutdown()