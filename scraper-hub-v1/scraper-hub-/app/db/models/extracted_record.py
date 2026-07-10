from sqlalchemy import Column, Integer, String, Text, Float, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class ExtractedRecord(Base):
    __tablename__ = "extracted_records"

    id = Column(Integer, primary_key=True, index=True)
    snapshot_id = Column(Integer, ForeignKey("raw_snapshots.id"), nullable=False)
    entity_name = Column(String, index=True, nullable=False)
    category = Column(String, index=True, nullable=False)
    market = Column(String, default="local")  # local or global
    subcategory = Column(String, nullable=True)

    title = Column(String, nullable=False)
    item_name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    price_value = Column(Float, nullable=True)
    price_currency = Column(String, nullable=True)
    billing_period = Column(String, nullable=True)
    unit_value = Column(Float, nullable=True)
    unit_type = Column(String, nullable=True)
    eligibility = Column(Text, nullable=True)
    effective_date = Column(DateTime, nullable=True)
    captured_at = Column(DateTime(timezone=True), index=True, server_default=func.now())
    source_url = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=True)

    snapshot = relationship("RawSnapshot", back_populates="records")

    @property
    def quality_status(self) -> str:
        score = self.confidence_score or 0.0
        if self.price_value is None or score < 0.5:
            return "poor"
        if score < 0.75:
            return "partial"
        return "good"

    @property
    def is_verified(self) -> bool:
        return self.price_value is not None and (self.confidence_score or 0.0) >= 0.75

    @property
    def has_price(self) -> bool:
        return self.price_value is not None