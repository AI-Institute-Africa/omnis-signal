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

def schedule_recurring_scrapes():
    db = next(get_db_session())
    sources = db.query(Source).filter(Source.schedule.isnot(None)).all()
    for source in sources:
        scheduler.add_job(
            func=lambda sid=source.id: run_scrape_task(sid),
            trigger=CronTrigger.from_crontab(source.schedule),
            id=f"scrape_{source.id}",
            replace_existing=True
        )
    db.close()

def start_scheduler():
    schedule_recurring_scrapes()
    scheduler.start()

def stop_scheduler():
    scheduler.shutdown()