from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    name = Column(String, index=True, nullable=False)
    category = Column(String, index=True, nullable=False)
    subcategory = Column(String, index=True, nullable=True)
    
    description = Column(Text, nullable=True)
    features = Column(JSON, nullable=True)  # List of features/benefits
    requirements = Column(Text, nullable=True)
    eligibility = Column(Text, nullable=True)
    duration = Column(String, nullable=True)
    
    captured_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    source = relationship("Source")
    organization = relationship("Organization", back_populates="services_list")
    price_history = relationship("PriceEntry", back_populates="service", cascade="all, delete-orphan")
