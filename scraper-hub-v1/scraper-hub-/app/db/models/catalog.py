"""
Catalog schema models — the single source of truth for the database-driven
sector/category/attribute/listing system.

Tables: sectors, categories, attribute_schema, providers, listings,
        listing_price_history, scrape_sources, scraped_items
"""
import json
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Float,
    DateTime, ForeignKey, Index, UniqueConstraint, func
)
from sqlalchemy.orm import relationship, backref
from app.db.base import Base


# ---------------------------------------------------------------------------
# Enums (stored as VARCHAR — portable across SQLite and PostgreSQL)
# ---------------------------------------------------------------------------

class SectorStatus:
    LIVE = "live"
    COMING_SOON = "coming_soon"
    ALL = ["live", "coming_soon"]


class CategoryLevel:
    STANDARD = "standard"
    FEE_CATEGORY = "fee_category"
    SUBCATEGORY = "subcategory"
    REVENUE_LINE = "revenue_line"
    ALL = ["standard", "fee_category", "subcategory", "revenue_line"]


class AttributeDataType:
    NUMBER = "number"
    STRING = "string"
    ENUM = "enum"
    BOOLEAN = "boolean"
    ALL = ["number", "string", "enum", "boolean"]


class QualityAxis:
    VALUE = "value"
    TRUST = "trust"
    AVAILABILITY = "availability"
    PERFORMANCE = "performance"
    RESILIENCE = "resilience"
    ALL = ["value", "trust", "availability", "performance", "resilience"]


class FreshnessStatus:
    FRESH = "fresh"
    STALE = "stale"
    UNVERIFIED = "unverified"
    ALL = ["fresh", "stale", "unverified"]


class ListingStatus:
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PUBLISHED = "published"
    REJECTED = "rejected"
    ALL = ["draft", "pending_review", "published", "rejected"]


class ListingUpdateSource:
    ADMIN = "admin"
    SCRAPER = "scraper"
    CORPORATE = "corporate"
    SEED = "seed"
    ALL = ["admin", "scraper", "corporate", "seed"]


class ScrapeTrigger:
    CRON = "cron"
    ADMIN_MANUAL = "admin_manual"
    ALL = ["cron", "admin_manual"]


class ScrapeItemStatus:
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ALL = ["pending", "approved", "rejected"]


# ---------------------------------------------------------------------------
# SectorConfig
# ---------------------------------------------------------------------------

class SectorConfig(Base):
    __tablename__ = "sectors"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    status = Column(String(20), nullable=False, default=SectorStatus.LIVE)
    icon = Column(String(100), nullable=True)
    blurb = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    categories = relationship("Category", back_populates="sector", cascade="all, delete-orphan")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "slug": self.slug,
                "status": self.status, "icon": self.icon, "blurb": self.blurb}


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------

class Category(Base):
    __tablename__ = "categories"

    id = Column(String(36), primary_key=True)
    sector_id = Column(String(36), ForeignKey("sectors.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False, index=True)
    _synonyms = Column("synonyms", Text, nullable=True)
    level = Column(String(20), nullable=False, default=CategoryLevel.STANDARD)
    parent_id = Column(String(36), ForeignKey("categories.id"), nullable=True)
    channel = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint("sector_id", "slug", name="uq_category_sector_slug"),)

    sector = relationship("SectorConfig", back_populates="categories")
    children = relationship("Category", backref=backref("parent", remote_side=[id]), cascade="all, delete-orphan")
    attribute_schema = relationship("AttributeSchemaField", back_populates="category",
                                    cascade="all, delete-orphan", order_by="AttributeSchemaField.sort_order")
    listings = relationship("Listing", back_populates="category")
    scrape_sources = relationship("ScrapeSource", back_populates="category")

    @property
    def synonyms(self):
        return json.loads(self._synonyms) if self._synonyms else []

    @synonyms.setter
    def synonyms(self, value):
        self._synonyms = json.dumps(value) if value else None

    def to_dict(self):
        return {"id": self.id, "sector_id": self.sector_id, "name": self.name,
                "slug": self.slug, "synonyms": self.synonyms, "level": self.level,
                "parent_id": self.parent_id, "channel": self.channel}


# ---------------------------------------------------------------------------
# AttributeSchemaField
# ---------------------------------------------------------------------------

class AttributeSchemaField(Base):
    __tablename__ = "attribute_schema"

    id = Column(String(36), primary_key=True)
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=False, index=True)
    key = Column(String(100), nullable=False)
    label = Column(String(255), nullable=False)
    consumer_label = Column(String(255), nullable=True)
    data_type = Column(String(20), nullable=False, default=AttributeDataType.STRING)
    unit = Column(String(50), nullable=True)
    is_comparable = Column(Boolean, nullable=False, default=True)
    sort_order = Column(Integer, nullable=False, default=0)
    quality_axis = Column(String(20), nullable=True)
    _synonyms = Column("synonyms", Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("category_id", "key", name="uq_attr_category_key"),)

    category = relationship("Category", back_populates="attribute_schema")

    @property
    def synonyms(self):
        return json.loads(self._synonyms) if self._synonyms else []

    @synonyms.setter
    def synonyms(self, value):
        self._synonyms = json.dumps(value) if value else None

    def to_dict(self):
        return {"id": self.id, "category_id": self.category_id, "key": self.key,
                "label": self.label, "consumer_label": self.consumer_label,
                "data_type": self.data_type, "unit": self.unit,
                "is_comparable": self.is_comparable, "sort_order": self.sort_order,
                "quality_axis": self.quality_axis}


# ---------------------------------------------------------------------------
# Provider
# ---------------------------------------------------------------------------

class Provider(Base):
    __tablename__ = "providers"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    logo_url = Column(Text, nullable=True)
    website_url = Column(Text, nullable=True)
    verified = Column(Boolean, nullable=False, default=True)
    owner_user_id = Column(String(36), nullable=True, unique=True)
    corporate_domain = Column(String(255), nullable=True, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    listings = relationship("Listing", back_populates="provider")
    scraped_items = relationship("ScrapedItem", back_populates="suggested_provider")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "logo_url": self.logo_url,
                "website_url": self.website_url, "verified": self.verified,
                "corporate_domain": self.corporate_domain, "description": self.description}


# ---------------------------------------------------------------------------
# Listing
# ---------------------------------------------------------------------------

class Listing(Base):
    __tablename__ = "listings"

    id = Column(String(36), primary_key=True)
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=False, index=True)
    provider_id = Column(String(36), ForeignKey("providers.id"), nullable=False, index=True)
    name = Column(String(512), nullable=False)
    description = Column(Text, nullable=True)
    _attributes = Column("attributes", Text, nullable=True)
    price = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False, default="USD")
    source_url = Column(Text, nullable=True)
    _images = Column("images", Text, nullable=True)
    rating = Column(Float, nullable=True)
    review_count = Column(Integer, nullable=False, default=0)
    last_verified_at = Column(DateTime(timezone=True), server_default=func.now())
    freshness_status = Column(String(20), nullable=False, default=FreshnessStatus.UNVERIFIED)
    status = Column(String(20), nullable=False, default=ListingStatus.PUBLISHED, index=True)
    rejection_reason = Column(Text, nullable=True)
    last_update_source = Column(String(20), nullable=False, default=ListingUpdateSource.SCRAPER)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_listings_cat_status_price", "category_id", "status", "price"),
        Index("ix_listings_provider_id", "provider_id"),
    )

    category = relationship("Category", back_populates="listings")
    provider = relationship("Provider", back_populates="listings")
    price_history = relationship("ListingPriceHistory", back_populates="listing",
                                 cascade="all, delete-orphan",
                                 order_by="ListingPriceHistory.recorded_at")

    @property
    def attributes(self):
        return json.loads(self._attributes) if self._attributes else {}

    @attributes.setter
    def attributes(self, value):
        self._attributes = json.dumps(value) if value is not None else None

    @property
    def images(self):
        return json.loads(self._images) if self._images else []

    @images.setter
    def images(self, value):
        self._images = json.dumps(value) if value else None

    def to_dict(self):
        return {"id": self.id, "category_id": self.category_id, "provider_id": self.provider_id,
                "name": self.name, "description": self.description, "attributes": self.attributes,
                "price": self.price, "currency": self.currency, "source_url": self.source_url,
                "rating": self.rating, "review_count": self.review_count,
                "last_verified_at": self.last_verified_at.isoformat() if self.last_verified_at else None,
                "freshness_status": self.freshness_status, "status": self.status,
                "last_update_source": self.last_update_source,
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "updated_at": self.updated_at.isoformat() if self.updated_at else None}


# ---------------------------------------------------------------------------
# ListingPriceHistory
# ---------------------------------------------------------------------------

class ListingPriceHistory(Base):
    __tablename__ = "listing_price_history"

    id = Column(String(36), primary_key=True)
    listing_id = Column(String(36), ForeignKey("listings.id"), nullable=False, index=True)
    price = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False, default="USD")
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    listing = relationship("Listing", back_populates="price_history")

    def to_dict(self):
        return {"id": self.id, "listing_id": self.listing_id, "price": self.price,
                "currency": self.currency,
                "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None}


# ---------------------------------------------------------------------------
# ScrapeSource (Mode B queue sources)
# ---------------------------------------------------------------------------

class ScrapeSource(Base):
    __tablename__ = "scrape_sources"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=True)
    enabled = Column(Boolean, nullable=False, default=True)
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    category = relationship("Category", back_populates="scrape_sources")
    scraped_items = relationship("ScrapedItem", back_populates="source", cascade="all, delete-orphan")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "url": self.url,
                "category_id": self.category_id, "enabled": self.enabled,
                "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None}


# ---------------------------------------------------------------------------
# ScrapedItem (Mode B — candidates awaiting human approval)
# ---------------------------------------------------------------------------

class ScrapedItem(Base):
    __tablename__ = "scraped_items"

    id = Column(String(36), primary_key=True)
    source_id = Column(String(36), ForeignKey("scrape_sources.id"), nullable=True)
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=True, index=True)
    source_url = Column(Text, nullable=True)
    triggered_by = Column(String(20), nullable=False, default=ScrapeTrigger.CRON)
    raw_content = Column(Text, nullable=True)
    _extracted_data = Column("extracted_data", Text, nullable=True)
    confidence = Column(Float, nullable=True)
    suggested_provider_id = Column(String(36), ForeignKey("providers.id"), nullable=True)
    suggested_listing_id = Column(String(36), ForeignKey("listings.id"), nullable=True)
    status = Column(String(20), nullable=False, default=ScrapeItemStatus.PENDING, index=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    source = relationship("ScrapeSource", back_populates="scraped_items")
    suggested_provider = relationship("Provider", back_populates="scraped_items")

    @property
    def extracted_data(self):
        return json.loads(self._extracted_data) if self._extracted_data else {}

    @extracted_data.setter
    def extracted_data(self, value):
        self._extracted_data = json.dumps(value) if value is not None else None

    def to_dict(self):
        return {"id": self.id, "source_id": self.source_id, "category_id": self.category_id,
                "source_url": self.source_url, "triggered_by": self.triggered_by,
                "extracted_data": self.extracted_data, "confidence": self.confidence,
                "suggested_provider_id": self.suggested_provider_id,
                "suggested_listing_id": self.suggested_listing_id,
                "status": self.status, "rejection_reason": self.rejection_reason,
                "created_at": self.created_at.isoformat() if self.created_at else None}
