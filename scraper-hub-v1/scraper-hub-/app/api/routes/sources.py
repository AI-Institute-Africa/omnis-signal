from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import redis
from app.db.session import get_db
from app.db.models.source import Source
from app.jobs.tasks import scrape_source
from app.scheduler import run_scrape_task
from rq import Queue
from redis import Redis
from app.config import settings
from pydantic import BaseModel


class SourceCreate(BaseModel):
    name: str
    category: str
    base_url: str
    schedule: str = None


class SourceUpdate(BaseModel):
    name: str = None
    category: str = None
    base_url: str = None
    schedule: str = None


router = APIRouter()

def get_queue():
    try:
        redis_conn = Redis.from_url(settings.REDIS_URL)
        redis_conn.ping()
        return Queue(connection=redis_conn)
    except:
        return None

@router.get("/", response_model=List[dict])
async def list_sources(db: Session = Depends(get_db)):
    sources = db.query(Source).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "category": s.category,
            "base_url": s.base_url,
            "schedule": s.schedule,
            "created_at": s.created_at,
            "updated_at": s.updated_at,
        }
        for s in sources
    ]


@router.post("/", response_model=dict)
async def create_source(source: SourceCreate, db: Session = Depends(get_db)):
    db_source = Source(**source.dict())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return {
        "id": db_source.id,
        "name": db_source.name,
        "category": db_source.category,
        "base_url": db_source.base_url,
        "schedule": db_source.schedule,
        "created_at": db_source.created_at,
        "updated_at": db_source.updated_at,
    }


@router.patch("/{source_id}", response_model=dict)
async def update_source(source_id: int, source: SourceUpdate, db: Session = Depends(get_db)):
    db_source = db.query(Source).filter(Source.id == source_id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    update_data = source.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_source, key, value)
    
    db.commit()
    db.refresh(db_source)
    return {
        "id": db_source.id,
        "name": db_source.name,
        "category": db_source.category,
        "base_url": db_source.base_url,
        "schedule": db_source.schedule,
        "created_at": db_source.created_at,
        "updated_at": db_source.updated_at,
    }


@router.post("/{source_id}/scrape")
async def run_source_scrape(source_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    db_source = db.query(Source).filter(Source.id == source_id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    queue = get_queue()
    if queue:
        try:
            job = queue.enqueue(scrape_source, source_id)
            return {"message": f"Scrape job enqueued in Redis for source {source_id}", "job_id": job.id}
        except Exception as e:
            print(f"Redis enqueue failed: {e}")
    
    # Fallback to FastAPI BackgroundTasks
    background_tasks.add_task(scrape_source, source_id)
    return {"message": f"Scrape job started in background for source {source_id}"}


@router.post("/realtime")
async def run_realtime_scrape_all(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    sources = db.query(Source).all()
    if not sources:
        raise HTTPException(status_code=404, detail="No sources available for realtime extraction")

    for source in sources:
        background_tasks.add_task(run_scrape_task, source.id)

    return {
        "message": f"Realtime extraction triggered for {len(sources)} sources.",
        "source_count": len(sources),
    }
