"""
OrgChangeEvent model - tracks detected changes in organization data over time.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class OrgChangeEvent(Base):
    __tablename__ = "org_change_events"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)

    change_type = Column(String, nullable=False, index=True)
    # Types: leadership_change, website_change, new_branch, new_service,
    #        contact_update, rebranding, shutdown_detected, pricing_change

    field_name = Column(String, nullable=True)       # Which field changed
    old_value = Column(Text, nullable=True)          # Previous value (JSON or string)
    new_value = Column(Text, nullable=True)          # New value (JSON or string)
    change_summary = Column(Text, nullable=True)     # Human-readable summary
    source_url = Column(String, nullable=True)       # Where the change was detected
    confidence = Column(String, default="high")      # high, medium, low
    reviewed = Column(String, default="pending")     # pending, confirmed, dismissed

    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("Organization", back_populates="change_events")
