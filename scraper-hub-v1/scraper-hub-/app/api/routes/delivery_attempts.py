from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.db.models.webhook_delivery_attempt import WebhookDeliveryAttempt, DeliveryStatus
from pydantic import BaseModel


router = APIRouter()


@router.get("/", response_model=List[dict])
async def list_delivery_attempts(
    db: Session = Depends(get_db),
    target_id: int = Query(None),
    record_id: int = Query(None),
    status: DeliveryStatus = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0)
):
    query = db.query(WebhookDeliveryAttempt)
    
    if target_id:
        query = query.filter(WebhookDeliveryAttempt.target_id == target_id)
    if record_id:
        query = query.filter(WebhookDeliveryAttempt.record_id == record_id)
    if status:
        query = query.filter(WebhookDeliveryAttempt.status == status)
    
    attempts = query.offset(offset).limit(limit).all()
    
    return [
        {
            "id": a.id,
            "target_id": a.target_id,
            "record_id": a.record_id,
            "status": a.status.value,
            "attempt_count": a.attempt_count,
            "error_message": a.error_message,
            "last_attempt_at": a.last_attempt_at.isoformat() if a.last_attempt_at else None,
            "created_at": a.created_at.isoformat(),
        }
        for a in attempts
    ]