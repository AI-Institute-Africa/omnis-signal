from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    
    name = Column(String, index=True, nullable=False)
    brand = Column(String, index=True, nullable=True)
    category = Column(String, index=True, nullable=False)
    subcategory = Column(String, index=True, nullable=True)
    sku = Column(String, index=True, nullable=True)
    
    description = Column(Text, nullable=True)
    images = Column(JSON, nullable=True)  # List of image URLs
    specifications = Column(JSON, nullable=True)  # Dict of specs
    tags = Column(JSON, nullable=True)  # List of tags
    
    captured_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    source = relationship("Source")
    organization = relationship("Organization", back_populates="products_list")
    price_history = relationship("PriceEntry", back_populates="product", cascade="all, delete-orphan")
