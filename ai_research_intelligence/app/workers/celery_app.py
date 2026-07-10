from celery import Celery, group, chain
from celery.schedules import crontab
from datetime import datetime, timedelta
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Celery app
app = Celery(
    'ai_research_intelligence',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
)

# Define periodic tasks (beat schedule)
app.conf.beat_schedule = {
    'crawl-arxiv': {
        'task': 'app.workers.tasks.crawl_arxiv',
        'schedule': timedelta(minutes=settings.CRAWLER_SCHEDULE_MINUTES),
    },
    'crawl-techcrunch': {
        'task': 'app.workers.tasks.crawl_techcrunch',
        'schedule': timedelta(minutes=settings.CRAWLER_SCHEDULE_MINUTES),
    },
    'crawl-github': {
        'task': 'app.workers.tasks.crawl_github',
        'schedule': timedelta(minutes=settings.CRAWLER_SCHEDULE_MINUTES),
    },
    'process-new-items': {
        'task': 'app.workers.tasks.process_new_items',
        'schedule': timedelta(minutes=5),
    },
    'deduplication-task': {
        'task': 'app.workers.tasks.deduplicate_items',
        'schedule': timedelta(minutes=settings.DEDUPLICATION_SCHEDULE_MINUTES),
    },
    'detect-trends': {
        'task': 'app.workers.tasks.detect_trends',
        'schedule': timedelta(minutes=settings.TREND_ANALYSIS_SCHEDULE_MINUTES),
    },
    'send-digest-reports': {
        'task': 'app.workers.tasks.send_digest_reports',
        'schedule': timedelta(hours=settings.DIGEST_SCHEDULE_HOURS),
    },
    'update-source-health': {
        'task': 'app.workers.tasks.update_source_health',
        'schedule': timedelta(minutes=30),
    },
}


# Import tasks to register them
from app.workers import tasks  # noqa
