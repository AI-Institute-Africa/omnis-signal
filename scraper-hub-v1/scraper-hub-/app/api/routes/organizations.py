"""
API routes for Zimbabwe Organizations.
"""
import json
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional, List
from app.db.session import SessionLocal
from app.db.models.organization import Organization
from app.db.models.org_change_event import OrgChangeEvent

router = APIRouter(prefix="/organizations", tags=["organizations"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("")
def list_organizations(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    scrape_status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """List all organizations with optional filters."""
    q = db.query(Organization)

    if category:
        q = q.filter(Organization.category == category)
    if scrape_status:
        q = q.filter(Organization.scrape_status == scrape_status)
    if search:
        term = f"%{search}%"
        q = q.filter(
            or_(
                Organization.name.ilike(term),
                Organization.description.ilike(term),
                Organization.keywords.ilike(term),
                Organization.industry_tags.ilike(term),
            )
        )

    total = q.count()
    orgs = q.order_by(Organization.name).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
        "results": [o.to_dict() for o in orgs],
    }


@router.get("/stats")
def org_stats(db: Session = Depends(get_db)):
    """Return aggregate stats across all organizations."""
    total = db.query(func.count(Organization.id)).scalar()
    by_category = db.query(
        Organization.category,
        func.count(Organization.id),
        func.avg(Organization.data_completeness),
    ).group_by(Organization.category).order_by(Organization.category).all()

    by_status = db.query(
        Organization.scrape_status,
        func.count(Organization.id),
    ).group_by(Organization.scrape_status).all()

    return {
        "total": total,
        "by_category": [
            {"category": c, "count": n, "avg_completeness": round(float(a or 0), 1)}
            for c, n, a in by_category
        ],
        "by_scrape_status": [{"status": s, "count": n} for s, n in by_status],
    }


@router.get("/{slug}")
def get_organization(slug: str, db: Session = Depends(get_db)):
    """Get full organization profile by slug."""
    org = db.query(Organization).filter(Organization.slug == slug).first()
    if not org:
        raise HTTPException(status_code=404, detail=f"Organization '{slug}' not found")
    return org.to_dict()


@router.get("/{slug}/changes")
def get_org_changes(slug: str, db: Session = Depends(get_db)):
    """Get change history for an organization."""
    org = db.query(Organization).filter(Organization.slug == slug).first()
    if not org:
        raise HTTPException(status_code=404, detail="Not found")
    events = db.query(OrgChangeEvent).filter(
        OrgChangeEvent.organization_id == org.id
    ).order_by(OrgChangeEvent.detected_at.desc()).limit(100).all()
    return [
        {
            "id": e.id,
            "change_type": e.change_type,
            "field_name": e.field_name,
            "old_value": e.old_value,
            "new_value": e.new_value,
            "change_summary": e.change_summary,
            "source_url": e.source_url,
            "confidence": e.confidence,
            "detected_at": e.detected_at.isoformat() if e.detected_at else None,
        }
        for e in events
    ]


@router.post("/{slug}/trigger-scrape")
def trigger_scrape(slug: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger a fresh scrape for a single organization."""
    org = db.query(Organization).filter(Organization.slug == slug).first()
    if not org:
        raise HTTPException(status_code=404, detail="Not found")

    org.scrape_status = "queued"
    db.commit()

    # Queue the scrape in the background
    background_tasks.add_task(_run_org_scrape, org.id)
    return {"message": f"Scrape queued for {org.name}", "org_id": org.id}


def _run_org_scrape(org_id: int):
    """Background task: run the org scraper pipeline."""
    db = SessionLocal()
    try:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            return
        org.scrape_status = "scraping"
        db.commit()

        from app.scraping.org_pipeline import OrgScrapePipeline
        pipeline = OrgScrapePipeline(db)
        pipeline.run(org)

        db.refresh(org)
        org.scrape_status = "done"
        db.commit()
    except Exception as e:
        try:
            org = db.query(Organization).filter(Organization.id == org_id).first()
            if org:
                org.scrape_status = "failed"
                org.scrape_error = str(e)[:500]
                db.commit()
        except Exception:
            pass
    finally:
        db.close()
