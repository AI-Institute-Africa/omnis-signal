from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import AnyHttpUrl, BaseModel, Field
from app.db.session import get_db
from app.db.models.webhook_target import WebhookTarget
from app.services.webhook_publisher import WebhookPublisher


class WebhookTargetCreate(BaseModel):
    name: str = Field(..., min_length=1)
    url: AnyHttpUrl
    secret: str = Field(..., min_length=16)
    is_active: bool = True


class WebhookTargetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    url: Optional[AnyHttpUrl] = None
    secret: Optional[str] = Field(None, min_length=16)
    is_active: Optional[bool] = None


class WebhookTargetResponse(BaseModel):
    model_config = {"from_attributes": True}
    
    id: int
    name: str
    url: str
    is_active: bool
    created_at: Optional[str]
    updated_at: Optional[str]


router = APIRouter()


@router.get("/")
async def list_webhook_targets(db: Session = Depends(get_db)):
    targets = db.query(WebhookTarget).all()
    return [{"id": t.id, "name": t.name, "url": t.url, "is_active": t.is_active, "created_at": str(t.created_at), "updated_at": str(t.updated_at)} for t in targets]


@router.post("/")
async def create_webhook_target(target: WebhookTargetCreate, db: Session = Depends(get_db)):
    target_data = target.dict()
    target_data['url'] = str(target.url)  # Convert URL to string
    db_target = WebhookTarget(**target_data)
    db.add(db_target)
    db.commit()
    db.refresh(db_target)
    return {"id": db_target.id, "name": db_target.name, "url": db_target.url, "is_active": db_target.is_active, "created_at": str(db_target.created_at), "updated_at": str(db_target.updated_at)}


@router.patch("/{target_id}", response_model=WebhookTargetResponse)
async def update_webhook_target(target_id: int, target: WebhookTargetUpdate, db: Session = Depends(get_db)):
    db_target = db.query(WebhookTarget).filter(WebhookTarget.id == target_id).first()
    if not db_target:
        raise HTTPException(status_code=404, detail="Webhook target not found")
    
    update_data = target.dict(exclude_unset=True)
    if 'url' in update_data:
        update_data['url'] = str(update_data['url'])  # Convert URL to string
    for key, value in update_data.items():
        setattr(db_target, key, value)
    
    db.commit()
    db.refresh(db_target)
    return db_target


@router.delete("/{target_id}")
async def delete_webhook_target(target_id: int, db: Session = Depends(get_db)):
    db_target = db.query(WebhookTarget).filter(WebhookTarget.id == target_id).first()
    if not db_target:
        raise HTTPException(status_code=404, detail="Webhook target not found")
    
    db.delete(db_target)
    db.commit()
    return {"message": "Webhook target deleted"}


@router.post("/{target_id}/replay-failed")
async def replay_failed_deliveries(target_id: int, db: Session = Depends(get_db)):
    """Replay failed webhook deliveries for a specific target."""
    db_target = db.query(WebhookTarget).filter(WebhookTarget.id == target_id).first()
    if not db_target:
        raise HTTPException(status_code=404, detail="Webhook target not found")
    
    publisher = WebhookPublisher(db)
    publisher.replay_failed_deliveries(target_id)
    return {"message": f"Replayed failed deliveries for target {target_id}"}


@router.post("/replay-all-failed")
async def replay_all_failed_deliveries(db: Session = Depends(get_db)):
    """Replay all failed webhook deliveries."""
    publisher = WebhookPublisher(db)
    publisher.replay_failed_deliveries()
    return {"message": "Replayed all failed deliveries"}