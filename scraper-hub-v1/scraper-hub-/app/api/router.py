from fastapi import APIRouter

from app.api.routes import health, sources, manual_scrape, records, webhook_targets, delivery_attempts
from app.api.routes import organizations
from app.api.routes import catalog

from app.services.email_reporter import EmailReporterService

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(sources.router, prefix="/sources", tags=["sources"])
api_router.include_router(manual_scrape.router, prefix="/manual-scrape", tags=["manual-scrape"])
api_router.include_router(records.router, prefix="/records", tags=["records"])
api_router.include_router(webhook_targets.router, prefix="/webhook-targets", tags=["webhook-targets"])
api_router.include_router(delivery_attempts.router, prefix="/delivery-attempts", tags=["delivery-attempts"])
api_router.include_router(organizations.router)
api_router.include_router(catalog.router)

@api_router.get("/reports/send-4h-digest", tags=["reports"])
@api_router.post("/reports/send-4h-digest", tags=["reports"])
def send_4h_report_endpoint():
    """Trigger the 4-hour comprehensive product and service price digest email."""
    return EmailReporterService.send_4h_digest_email()


@api_router.get("/reports/send-12h-digest", tags=["reports"])
@api_router.post("/reports/send-12h-digest", tags=["reports"])
def send_12h_report_endpoint():
    """Backward-compatible endpoint for triggering price digest email."""
    return EmailReporterService.send_digest_email()


@api_router.get("/subscribers", tags=["subscribers"])
def list_subscribers():
    """List all registered report subscribers."""
    from app.db.session import get_db_session
    from app.db.models.subscriber import ReportSubscriber
    db = next(get_db_session())
    try:
        subs = db.query(ReportSubscriber).order_by(ReportSubscriber.id.asc()).all()
        return {"total": len(subs), "subscribers": [s.to_dict() for s in subs]}
    finally:
        db.close()


@api_router.post("/subscribers", tags=["subscribers"])
def add_subscriber(payload: dict):
    """Add a new report email subscriber or update an existing one."""
    from app.db.session import get_db_session
    from app.db.models.subscriber import ReportSubscriber
    email = payload.get("email", "").strip().lower()
    if not email or "@" not in email:
        return {"status": "error", "message": "A valid email address is required."}

    db = next(get_db_session())
    try:
        existing = db.query(ReportSubscriber).filter(ReportSubscriber.email == email).first()
        if existing:
            existing.name = payload.get("name", existing.name)
            existing.organization = payload.get("organization", existing.organization)
            existing.role = payload.get("role", existing.role)
            existing.frequency = payload.get("frequency", existing.frequency)
            existing.sector_filter = payload.get("sector_filter", existing.sector_filter)
            existing.is_active = payload.get("is_active", True)
            db.commit()
            return {"status": "updated", "subscriber": existing.to_dict()}
        else:
            sub = ReportSubscriber(
                email=email,
                name=payload.get("name"),
                organization=payload.get("organization"),
                role=payload.get("role"),
                frequency=payload.get("frequency", "4h"),
                sector_filter=payload.get("sector_filter", "all"),
                is_active=payload.get("is_active", True)
            )
            db.add(sub)
            db.commit()
            db.refresh(sub)
            return {"status": "created", "subscriber": sub.to_dict()}
    finally:
        db.close()


@api_router.delete("/subscribers/{subscriber_id}", tags=["subscribers"])
def delete_subscriber(subscriber_id: int):
    """Remove a subscriber by ID."""
    from app.db.session import get_db_session
    from app.db.models.subscriber import ReportSubscriber
    db = next(get_db_session())
    try:
        sub = db.query(ReportSubscriber).filter(ReportSubscriber.id == subscriber_id).first()
        if not sub:
            return {"status": "error", "message": "Subscriber not found"}
        db.delete(sub)
        db.commit()
        return {"status": "deleted", "id": subscriber_id}
    finally:
        db.close()
