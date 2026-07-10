from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base


class DeliveryStatus(enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


class WebhookDeliveryAttempt(Base):
    __tablename__ = "webhook_delivery_attempts"

    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(Integer, ForeignKey("webhook_targets.id"), nullable=False)
    record_id = Column(Integer, ForeignKey("extracted_records.id"), nullable=False)
    payload = Column(Text, nullable=False)  # JSON payload
    status = Column(Enum(DeliveryStatus), default=DeliveryStatus.PENDING)
    attempt_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    last_attempt_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    target = relationship("WebhookTarget")
    record = relationship("ExtractedRecord")