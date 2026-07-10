from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func
from app.db.base import Base


class WebhookTarget(Base):
    __tablename__ = "webhook_targets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    secret = Column(String, nullable=False)  # For HMAC signing
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())