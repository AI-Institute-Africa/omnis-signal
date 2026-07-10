"""
Sources Management API
======================
Full CRUD operations and management endpoints for Research Sources.

Endpoints
---------
GET    /api/v1/sources                  - List all sources (with filter/pagination)
GET    /api/v1/sources/{source_id}      - Get a single source by ID
POST   /api/v1/sources                  - Create a new source
PUT    /api/v1/sources/{source_id}      - Full update of a source
PATCH  /api/v1/sources/{source_id}      - Partial update (e.g., toggle active)
DELETE /api/v1/sources/{source_id}      - Delete (soft-delete) a source
POST   /api/v1/sources/{source_id}/activate   - Activate a source
POST   /api/v1/sources/{source_id}/deactivate - Deactivate a source
GET    /api/v1/sources/types            - List all distinct source types
GET    /api/v1/sources/{source_id}/stats     - Item count + health stats for a source
POST   /api/v1/sources/bulk             - Bulk create / upsert sources
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field
import uuid

from app.db import get_db
from app.models import ResearchSource, SourceStatus, ResearchItem

router = APIRouter(prefix="/api/v1/sources", tags=["sources"])


# ============================================================================
# SCHEMAS
# ============================================================================

class SourceBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Unique source name")
    source_type: str = Field(..., description="Type: arxiv | openreview | papers_with_code | huggingface | corporate | news | community | patent_grant | policy | gpu_market")
    url: str = Field(..., description="Primary URL of the source")
    category: Optional[str] = Field(None, description="Optional category tag")
    authority_score: float = Field(0.85, ge=0.0, le=1.0, description="Authority weight 0-1")
    is_active: bool = Field(True, description="Whether source is enabled")
    rate_limit_per_minute: int = Field(10, ge=1, le=600, description="Max requests/minute")
    timeout_seconds: int = Field(30, ge=5, le=120, description="Request timeout in seconds")
    max_retries: int = Field(3, ge=0, le=10, description="Max retry attempts on failure")
    extra_metadata: Optional[Dict[str, Any]] = Field(None, description="Arbitrary extra metadata")


class SourceCreate(SourceBase):
    """Schema for creating a new source."""
    pass


class SourceUpdate(SourceBase):
    """Schema for a full source update (PUT)."""
    pass


class SourcePatch(BaseModel):
    """Schema for partial source update (PATCH). All fields optional."""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    source_type: Optional[str] = None
    url: Optional[str] = None
    category: Optional[str] = None
    authority_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    is_active: Optional[bool] = None
    rate_limit_per_minute: Optional[int] = Field(None, ge=1, le=600)
    timeout_seconds: Optional[int] = Field(None, ge=5, le=120)
    max_retries: Optional[int] = Field(None, ge=0, le=10)
    extra_metadata: Optional[Dict[str, Any]] = None


class SourceResponse(BaseModel):
    id: str
    name: str
    source_type: str
    url: str
    category: Optional[str] = None
    authority_score: float
    is_active: bool
    status: str
    rate_limit_per_minute: int
    timeout_seconds: int
    max_retries: int
    consecutive_failures: int
    last_checked: Optional[datetime] = None
    next_check: Optional[datetime] = None
    extra_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SourceStatsResponse(BaseModel):
    source_id: str
    source_name: str
    status: str
    authority_score: float
    items_total: int
    items_last_24h: int
    items_last_7d: int
    consecutive_failures: int
    last_checked: Optional[datetime]
    next_check: Optional[datetime]


class BulkSourceItem(SourceBase):
    """Single item in a bulk upsert request."""
    pass


class BulkCreateResponse(BaseModel):
    created: int
    updated: int
    errors: List[Dict[str, str]]
    sources: List[SourceResponse]


# ============================================================================
# HELPER
# ============================================================================

def _source_or_404(source_id: str, db: Session) -> ResearchSource:
    src = db.query(ResearchSource).filter(ResearchSource.id == source_id).first()
    if not src:
        raise HTTPException(status_code=404, detail=f"Source '{source_id}' not found")
    return src


# ============================================================================
# LIST  GET /api/v1/sources
# ============================================================================

@router.get("", response_model=List[SourceResponse], summary="List all sources")
async def list_sources(
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
    source_type: Optional[str] = Query(None, description="Filter by source_type"),
    is_active: Optional[bool] = Query(None, description="Filter by active state"),
    status: Optional[str] = Query(None, description="Filter by status (active|inactive|degraded|error)"),
    db: Session = Depends(get_db),
):
    """
    Returns a paginated list of all configured research sources.

    **Usage by external agents / systems:**
    ```
    GET http://localhost:8002/api/v1/sources?source_type=arxiv&is_active=true&limit=10
    ```
    """
    q = db.query(ResearchSource)
    if source_type:
        q = q.filter(ResearchSource.source_type == source_type)
    if is_active is not None:
        q = q.filter(ResearchSource.is_active == is_active)
    if status:
        try:
            status_enum = SourceStatus(status)
            q = q.filter(ResearchSource.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid status value: {status}")
    return q.order_by(ResearchSource.authority_score.desc()).offset(skip).limit(limit).all()


# ============================================================================
# GET SINGLE  GET /api/v1/sources/{source_id}
# ============================================================================

@router.get("/types", response_model=List[str], summary="List distinct source types")
async def list_source_types(db: Session = Depends(get_db)):
    """Returns all distinct `source_type` values currently stored."""
    rows = db.query(ResearchSource.source_type).distinct().all()
    return [r[0] for r in rows]


@router.get("/{source_id}", response_model=SourceResponse, summary="Get source by ID")
async def get_source(source_id: str, db: Session = Depends(get_db)):
    """Retrieve a single source by its UUID."""
    return _source_or_404(source_id, db)


# ============================================================================
# CREATE  POST /api/v1/sources
# ============================================================================

@router.post("", response_model=SourceResponse, status_code=201, summary="Create a source")
async def create_source(payload: SourceCreate, db: Session = Depends(get_db)):
    """
    Create a new research source.

    **Example body:**
    ```json
    {
      "name": "Nature AI",
      "source_type": "news",
      "url": "https://www.nature.com/subjects/artificial-intelligence",
      "authority_score": 0.95,
      "is_active": true
    }
    ```
    """
    existing = db.query(ResearchSource).filter(ResearchSource.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Source with name '{payload.name}' already exists")

    source = ResearchSource(
        id=str(uuid.uuid4()),
        **payload.dict(),
        status=SourceStatus.ACTIVE if payload.is_active else SourceStatus.INACTIVE,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


# ============================================================================
# UPDATE (full)  PUT /api/v1/sources/{source_id}
# ============================================================================

@router.put("/{source_id}", response_model=SourceResponse, summary="Full update of a source")
async def update_source(source_id: str, payload: SourceUpdate, db: Session = Depends(get_db)):
    """Replace all mutable fields of a source."""
    source = _source_or_404(source_id, db)
    for field, value in payload.dict().items():
        setattr(source, field, value)
    source.status = SourceStatus.ACTIVE if payload.is_active else SourceStatus.INACTIVE
    source.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(source)
    return source


# ============================================================================
# PATCH (partial)  PATCH /api/v1/sources/{source_id}
# ============================================================================

@router.patch("/{source_id}", response_model=SourceResponse, summary="Partial update of a source")
async def patch_source(source_id: str, payload: SourcePatch, db: Session = Depends(get_db)):
    """
    Update only the supplied fields.  Useful for toggling `is_active` or adjusting
    `authority_score` without having to resend the full object.

    **Example – change authority score:**
    ```json
    { "authority_score": 0.92 }
    ```
    """
    source = _source_or_404(source_id, db)
    updates = payload.dict(exclude_unset=True)
    for field, value in updates.items():
        setattr(source, field, value)
    if "is_active" in updates:
        source.status = SourceStatus.ACTIVE if updates["is_active"] else SourceStatus.INACTIVE
    source.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(source)
    return source


# ============================================================================
# DELETE  DELETE /api/v1/sources/{source_id}
# ============================================================================

@router.delete("/{source_id}", status_code=204, summary="Delete a source")
async def delete_source(source_id: str, db: Session = Depends(get_db)):
    """
    Deletes a source permanently.  All associated ResearchItems are also deleted
    (cascade). This action is **irreversible**.
    """
    source = _source_or_404(source_id, db)
    db.delete(source)
    db.commit()
    return None


# ============================================================================
# ACTIVATE / DEACTIVATE  POST /api/v1/sources/{source_id}/activate|deactivate
# ============================================================================

@router.post("/{source_id}/activate", response_model=SourceResponse, summary="Activate a source")
async def activate_source(source_id: str, db: Session = Depends(get_db)):
    """Enable a previously disabled source so the scraper will collect from it."""
    source = _source_or_404(source_id, db)
    source.is_active = True
    source.status = SourceStatus.ACTIVE
    source.consecutive_failures = 0
    source.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(source)
    return source


@router.post("/{source_id}/deactivate", response_model=SourceResponse, summary="Deactivate a source")
async def deactivate_source(source_id: str, db: Session = Depends(get_db)):
    """Disable a source without deleting it."""
    source = _source_or_404(source_id, db)
    source.is_active = False
    source.status = SourceStatus.INACTIVE
    source.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(source)
    return source


# ============================================================================
# STATS  GET /api/v1/sources/{source_id}/stats
# ============================================================================

@router.get("/{source_id}/stats", response_model=SourceStatsResponse, summary="Source statistics")
async def get_source_stats(source_id: str, db: Session = Depends(get_db)):
    """
    Returns item collection statistics for a source.

    Useful for monitoring agents to determine if a source is producing data.
    """
    source = _source_or_404(source_id, db)
    now = datetime.utcnow()

    total = db.query(ResearchItem).filter(ResearchItem.source_id == source_id).count()
    last_24h = db.query(ResearchItem).filter(
        and_(ResearchItem.source_id == source_id,
             ResearchItem.created_at >= now - timedelta(hours=24))
    ).count()
    last_7d = db.query(ResearchItem).filter(
        and_(ResearchItem.source_id == source_id,
             ResearchItem.created_at >= now - timedelta(days=7))
    ).count()

    return SourceStatsResponse(
        source_id=source.id,
        source_name=source.name,
        status=source.status.value,
        authority_score=source.authority_score,
        items_total=total,
        items_last_24h=last_24h,
        items_last_7d=last_7d,
        consecutive_failures=source.consecutive_failures,
        last_checked=source.last_checked,
        next_check=source.next_check,
    )


# ============================================================================
# BULK UPSERT  POST /api/v1/sources/bulk
# ============================================================================

@router.post("/bulk", response_model=BulkCreateResponse, status_code=207, summary="Bulk create/upsert sources")
async def bulk_upsert_sources(
    payload: List[BulkSourceItem],
    db: Session = Depends(get_db),
):
    """
    Create or update multiple sources in a single request (upsert by name).

    - If a source with the same `name` already exists → **update** it.
    - Otherwise → **create** it.

    **Example body:**
    ```json
    [
      {"name": "arXiv", "source_type": "arxiv", "url": "https://arxiv.org", "authority_score": 0.95},
      {"name": "Hugging Face", "source_type": "huggingface", "url": "https://huggingface.co/papers", "authority_score": 0.85}
    ]
    ```
    """
    created_count = 0
    updated_count = 0
    errors: List[Dict[str, str]] = []
    results: List[ResearchSource] = []

    for item in payload:
        try:
            existing = db.query(ResearchSource).filter(ResearchSource.name == item.name).first()
            if existing:
                for field, value in item.dict().items():
                    setattr(existing, field, value)
                existing.status = SourceStatus.ACTIVE if item.is_active else SourceStatus.INACTIVE
                existing.updated_at = datetime.utcnow()
                db.flush()
                results.append(existing)
                updated_count += 1
            else:
                source = ResearchSource(
                    id=str(uuid.uuid4()),
                    **item.dict(),
                    status=SourceStatus.ACTIVE if item.is_active else SourceStatus.INACTIVE,
                )
                db.add(source)
                db.flush()
                results.append(source)
                created_count += 1
        except Exception as e:
            errors.append({"name": item.name, "error": str(e)})

    db.commit()
    for r in results:
        db.refresh(r)

    return BulkCreateResponse(
        created=created_count,
        updated=updated_count,
        errors=errors,
        sources=results,
    )
