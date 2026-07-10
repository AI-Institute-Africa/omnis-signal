from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.db.session import get_db
from app.db.models.extracted_record import ExtractedRecord
from app.api.v2.schemas import PaginatedMarketData, MarketDataResponse, LatestMarketDataBySector
from app.api.dependencies.auth import get_api_key

router = APIRouter()

@router.get("/", response_model=PaginatedMarketData)
async def get_market_data(
    category: Optional[str] = Query(None, description="Filter by category"),
    entity_name: Optional[str] = Query(None, description="Filter by entity"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    query = db.query(ExtractedRecord)
    
    if category:
        query = query.filter(ExtractedRecord.category == category)
    if entity_name:
        query = query.filter(ExtractedRecord.entity_name == entity_name)
        
    total = query.count()
    records = query.order_by(ExtractedRecord.captured_at.desc()).offset(offset).limit(limit).all()
    
    return PaginatedMarketData(
        total=total,
        limit=limit,
        offset=offset,
        data=[MarketDataResponse.model_validate(r) for r in records]
    )


@router.get("/latest-by-sector", response_model=LatestMarketDataBySector)
async def get_latest_market_data_by_sector(
    categories: Optional[List[str]] = Query(None, description="Optional list of sectors to include"),
    limit_per_category: int = Query(10, ge=1, le=50, description="Maximum latest records to return per sector"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    query = db.query(ExtractedRecord.category).distinct()
    if categories:
        query = query.filter(ExtractedRecord.category.in_(categories))

    category_rows = query.all()
    sectors = []

    for row in category_rows:
        category_name = row[0]
        records = (
            db.query(ExtractedRecord)
            .filter(
                ExtractedRecord.category == category_name,
                ExtractedRecord.price_value.isnot(None)
            )
            .order_by(ExtractedRecord.captured_at.desc())
            .limit(limit_per_category)
            .all()
        )

        sectors.append({
            "category": category_name,
            "latest_records": [MarketDataResponse.model_validate(r) for r in records]
        })

    return LatestMarketDataBySector(sectors=sectors)
