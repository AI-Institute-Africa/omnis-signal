from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class PriceInfo(BaseModel):
    price_value: float
    currency: str = "USD"
    discount_price: Optional[float] = None
    previous_price: Optional[float] = None
    billing_period: Optional[str] = None  # e.g., "monthly", "once"
    is_promotion: bool = False
    promotion_details: Optional[str] = None
    
    # Normalization & Comparable Metrics (Expanded based on user table)
    normalized_value: Optional[float] = None
    normalized_unit: Optional[str] = None
    formula: Optional[str] = None
    
    # Billing cycle flags
    per_second: bool = False
    per_minute: bool = False
    per_hour: bool = False
    daily: bool = False
    three_days: bool = False
    weekly: bool = False
    bi_weekly: bool = False
    monthly: bool = False
    yearly: bool = False
    
    metrics: Optional[Dict[str, Any]] = None # e.g. {"download_speed": "10Mbps"}

class ProductSchema(BaseModel):
    name: str
    brand: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    sku: Optional[str] = None
    description: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    price: PriceInfo
    images: List[str] = []
    tags: List[str] = []

class ServiceSchema(BaseModel):
    name: str
    category: str
    subcategory: Optional[str] = None
    description: Optional[str] = None
    features: List[str] = []
    requirements: Optional[str] = None
    eligibility: Optional[str] = None
    duration: Optional[str] = None
    price: PriceInfo

class ExtractionResponse(BaseModel):
    products: List[ProductSchema] = []
    services: List[ServiceSchema] = []
