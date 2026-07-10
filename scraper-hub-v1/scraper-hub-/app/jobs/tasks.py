import logging
from rq import get_current_job
from app.services.extractor import ExtractorService
from app.db.session import get_db_session
from app.db.models import RawSnapshot, Source

logger = logging.getLogger(__name__)

import asyncio
from app.services.fetcher import PlaywrightFetcher

def scrape_source(source_id_or_page_id: int):
    # This was originally taking source_id, but maybe it should take page_id.
    # The existing codebase was calling scrape_source(page.id) in our scripts.
    # Actually, let's make it handle both or just page_id, wait, the scheduler calls run_scrape_task(source.id).
    # So it takes source_id.
    job = get_current_job()
    job_id = job.id if job else "manual_trigger"
    logger.info(f"Starting scrape job {job_id} for source {source_id_or_page_id}")
    
    db = next(get_db_session())
    try:
        source = db.query(Source).filter(Source.id == source_id_or_page_id).first()
        if not source:
            logger.error(f"Source {source_id_or_page_id} not found")
            return
            
        extractor_service = ExtractorService(db)
        fetcher = PlaywrightFetcher()
        
        # We need to run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        for page in source.pages:
            if not page.enabled: continue
            logger.info(f"Fetching {page.url}")
            
            try:
                content = loop.run_until_complete(fetcher.fetch_page_content(page.url))
                
                # Save snapshot
                snapshot = RawSnapshot(
                    source_page_id=page.id,
                    url=page.url,
                    content=content,
                    content_type="html"
                )

                db.add(snapshot)
                db.commit()
                db.refresh(snapshot)
                
                # Extract
                records = extractor_service.extract_from_snapshot(snapshot)
                logger.info(f"Extracted {len(records)} records from {page.url}")
                
            except Exception as e:
                logger.error(f"Failed processing page {page.url}: {e}")
                
        loop.close()
        db.commit()
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        raise
    finally:
        db.close()