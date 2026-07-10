from sqlalchemy import Column, Integer, String, Text, Float, Boolean, JSON, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class PriceEntry(Base):
    __tablename__ = "price_entries"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    price_value = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    
    # Normalization fields
    normalized_value = Column(Float, nullable=True) # e.g., 0.0025
    normalized_unit = Column(String, nullable=True)  # e.g., "$/MB"
    comparable_metrics = Column(JSON, nullable=True) # e.g., {"download_speed": "10Mbps"}
    formula = Column(Text, nullable=True) # e.g., "price / quantity"

    # Duration Flags
    per_second = Column(Boolean, default=False)
    per_minute = Column(Boolean, default=False)
    per_hour = Column(Boolean, default=False)
    daily = Column(Boolean, default=False)
    three_days = Column(Boolean, default=False)
    weekly = Column(Boolean, default=False)
    bi_weekly = Column(Boolean, default=False)
    monthly = Column(Boolean, default=False)
    yearly = Column(Boolean, default=False)

    discount_price = Column(Float, nullable=True)
    previous_price = Column(Float, nullable=True)
    
    is_promotion = Column(Boolean, default=False)
    promotion_details = Column(Text, nullable=True)
    
    # Metadata
    captured_at = Column(DateTime(timezone=True), index=True, server_default=func.now())
    source_url = Column(String, nullable=True)
    snapshot_id = Column(Integer, ForeignKey("raw_snapshots.id"), nullable=True)

    product = relationship("Product", back_populates="price_history")
    service = relationship("Service", back_populates="price_history")
    organization = relationship("Organization")
    snapshot = relationship("RawSnapshot")
