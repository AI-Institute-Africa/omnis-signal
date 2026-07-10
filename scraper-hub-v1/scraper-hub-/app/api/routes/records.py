from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
from app.db.session import get_db
from app.db.models.extracted_record import ExtractedRecord
from pydantic import BaseModel


class RecordResponse(BaseModel):
    model_config = {"from_attributes": True}
    
    id: int
    snapshot_id: int
    entity_name: str
    category: str
    subcategory: Optional[str]
    title: str
    item_name: Optional[str]
    description: Optional[str]
    price_value: Optional[float]
    price_currency: Optional[str]
    billing_period: Optional[str]
    unit_value: Optional[float]
    unit_type: Optional[str]
    eligibility: Optional[str]
    effective_date: Optional[str]
    captured_at: str
    source_url: str
    confidence_score: Optional[float]
    quality_status: Optional[str]
    is_verified: Optional[bool]
    has_price: Optional[bool]


router = APIRouter()


@router.get("/", response_model=List[RecordResponse])
async def list_records(
    db: Session = Depends(get_db),
    category: Optional[str] = Query(None, description="Filter by category (telecom, banking)"),
    entity_name: Optional[str] = Query(None, description="Filter by entity name"),
    subcategory: Optional[str] = Query(None, description="Filter by subcategory"),
    min_confidence: Optional[float] = Query(None, description="Minimum confidence score to include", ge=0.0, le=1.0),
    verified_only: bool = Query(False, description="Only return verified high-confidence records"),
    has_price_only: bool = Query(False, description="Only return records with a detected price"),
    limit: int = Query(100, description="Maximum number of records to return", ge=1, le=1000),
    offset: int = Query(0, description="Number of records to skip", ge=0)
):
    """List extracted records with optional filtering."""
    query = db.query(ExtractedRecord)

    if category:
        query = query.filter(ExtractedRecord.category == category)

    if entity_name:
        query = query.filter(ExtractedRecord.entity_name == entity_name)

    if subcategory:
        query = query.filter(ExtractedRecord.subcategory == subcategory)

    if verified_only:
        query = query.filter(
            ExtractedRecord.price_value.isnot(None),
            ExtractedRecord.confidence_score.isnot(None),
            ExtractedRecord.confidence_score >= 0.75,
        )
    elif min_confidence is not None:
        query = query.filter(
            ExtractedRecord.confidence_score.isnot(None),
            ExtractedRecord.confidence_score >= min_confidence,
        )

    if has_price_only:
        query = query.filter(ExtractedRecord.price_value.isnot(None))

    query = query.order_by(ExtractedRecord.captured_at.desc())

    records = query.offset(offset).limit(limit).all()

    return [
        RecordResponse(
            id=r.id,
            snapshot_id=r.snapshot_id,
            entity_name=r.entity_name,
            category=r.category,
            subcategory=r.subcategory,
            title=r.title,
            item_name=r.item_name,
            description=r.description,
            price_value=r.price_value,
            price_currency=r.price_currency,
            billing_period=r.billing_period,
            unit_value=r.unit_value,
            unit_type=r.unit_type,
            eligibility=r.eligibility,
            effective_date=r.effective_date.isoformat() if r.effective_date else None,
            captured_at=r.captured_at.isoformat(),
            source_url=r.source_url,
            confidence_score=r.confidence_score,
            quality_status=r.quality_status,
            is_verified=r.is_verified,
            has_price=r.has_price,
        )
        for r in records
    ]


@router.get("/quality-summary", response_model=dict)
async def quality_summary(db: Session = Depends(get_db)):
    total_count = db.query(ExtractedRecord).count()
    good_count = db.query(ExtractedRecord).filter(
        ExtractedRecord.price_value.isnot(None),
        ExtractedRecord.confidence_score.isnot(None),
        ExtractedRecord.confidence_score >= 0.75,
    ).count()
    partial_count = db.query(ExtractedRecord).filter(
        ExtractedRecord.price_value.isnot(None),
        ExtractedRecord.confidence_score.isnot(None),
        ExtractedRecord.confidence_score >= 0.5,
        ExtractedRecord.confidence_score < 0.75,
    ).count()
    poor_count = db.query(ExtractedRecord).filter(
        or_(
            ExtractedRecord.price_value.is_(None),
            ExtractedRecord.confidence_score.is_(None),
            ExtractedRecord.confidence_score < 0.5,
        )
    ).count()
    category_counts = {
        cat or 'Unknown': count
        for cat, count in db.query(ExtractedRecord.category, func.count(ExtractedRecord.id)).group_by(ExtractedRecord.category).all()
    }
    return {
        "total_count": total_count,
        "quality_breakdown": {
            "good": good_count,
            "partial": partial_count,
            "poor": poor_count,
        },
        "category_counts": category_counts,
    }


@router.get("/{record_id}", response_model=RecordResponse)
async def get_record(record_id: int, db: Session = Depends(get_db)):
    """Get a specific extracted record by ID."""
    record = db.query(ExtractedRecord).filter(ExtractedRecord.id == record_id).first()
    if not record:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Record not found")

    return RecordResponse(
        id=record.id,
        snapshot_id=record.snapshot_id,
        entity_name=record.entity_name,
        category=record.category,
        subcategory=record.subcategory,
        title=record.title,
        item_name=record.item_name,
        description=record.description,
        price_value=record.price_value,
        price_currency=record.price_currency,
        billing_period=record.billing_period,
        unit_value=record.unit_value,
        unit_type=record.unit_type,
        eligibility=record.eligibility,
        effective_date=record.effective_date.isoformat() if record.effective_date else None,
        captured_at=record.captured_at.isoformat(),
        source_url=record.source_url,
        confidence_score=record.confidence_score,
    )