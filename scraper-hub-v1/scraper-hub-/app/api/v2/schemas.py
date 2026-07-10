from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class MarketDataResponse(BaseModel):
    model_config = {"from_attributes": True}
    
    id: int
    entity_name: str
    category: str
    subcategory: Optional[str]
    title: str
    description: Optional[str]
    price_value: Optional[float]
    price_currency: Optional[str]
    captured_at: datetime
    source_url: str

class SectorMarketData(BaseModel):
    category: str
    latest_records: List[MarketDataResponse]

class LatestMarketDataBySector(BaseModel):
    sectors: List[SectorMarketData]


class PaginatedMarketData(BaseModel):
    total: int
    limit: int
    offset: int
    data: List[MarketDataResponse]
