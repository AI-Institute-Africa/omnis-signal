"""
Organization model - core entity for the Zimbabwe Business Intelligence Platform.
Stores general, business, digital, and AI intelligence for each organization.
"""
import json
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, Text, func
)
from sqlalchemy.orm import relationship
from app.db.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    # ── Primary Key ───────────────────────────────────────────────────────────
    id = Column(Integer, primary_key=True, index=True)

    # ── General Data ──────────────────────────────────────────────────────────
    name = Column(String, nullable=False, index=True)
    slug = Column(String, nullable=False, unique=True, index=True)
    category = Column(String, nullable=False, index=True)   # banks, telecoms, etc.
    description = Column(Text, nullable=True)
    logo_url = Column(String, nullable=True)
    website = Column(String, nullable=True)

    # Contact info stored as JSON arrays
    emails = Column(Text, nullable=True)           # JSON: ["info@example.com"]
    phone_numbers = Column(Text, nullable=True)    # JSON: ["+263771234567"]
    whatsapp_numbers = Column(Text, nullable=True) # JSON: ["+263771234567"]
    physical_addresses = Column(Text, nullable=True) # JSON: ["123 Main St, Harare"]
    gps_lat = Column(Float, nullable=True)
    gps_lng = Column(Float, nullable=True)
    branches = Column(Text, nullable=True)         # JSON: [{name, address, phone}]
    operating_hours = Column(Text, nullable=True)  # JSON: {Mon: "8:00-17:00", ...}

    # Social media
    social_links = Column(Text, nullable=True)     # JSON: {linkedin, facebook, twitter, instagram}

    # Registration
    registration_status = Column(String, nullable=True)  # active, suspended, deregistered
    registration_number = Column(String, nullable=True)

    # Tags
    industry_tags = Column(Text, nullable=True)    # JSON: ["banking", "finance"]
    keywords = Column(Text, nullable=True)         # JSON: ["mortgage", "savings"]

    # ── Business Intelligence ─────────────────────────────────────────────────
    executive_leadership = Column(Text, nullable=True)  # JSON: [{name, title}]
    founders = Column(Text, nullable=True)              # JSON: ["Name Surname"]
    ceo = Column(String, nullable=True)
    board_members = Column(Text, nullable=True)         # JSON: [{name, role}]
    employee_size = Column(String, nullable=True)       # e.g. "100-500"
    revenue_estimate = Column(String, nullable=True)    # e.g. "$50M-$100M"
    partnerships = Column(Text, nullable=True)          # JSON: ["Company A", "Company B"]
    competitors = Column(Text, nullable=True)           # JSON: ["Competitor A"]
    services_offered = Column(Text, nullable=True)      # JSON: ["Service 1", "Service 2"]
    products = Column(Text, nullable=True)              # JSON: ["Product 1"]
    pricing_notes = Column(Text, nullable=True)
    customer_reviews = Column(Text, nullable=True)      # JSON: [{author, rating, text, date}]
    rating_avg = Column(Float, nullable=True)
    review_count = Column(Integer, default=0)
    sentiment_score = Column(Float, nullable=True)      # -1.0 to 1.0

    # ── Digital Intelligence ──────────────────────────────────────────────────
    seo_metadata = Column(Text, nullable=True)          # JSON: {title, description, og_image}
    tech_stack = Column(Text, nullable=True)            # JSON: ["WordPress", "Cloudflare"]
    hosting_provider = Column(String, nullable=True)
    analytics_tools = Column(Text, nullable=True)       # JSON: ["Google Analytics"]
    mobile_apps = Column(Text, nullable=True)           # JSON: [{name, platform, store_url}]
    api_endpoints = Column(Text, nullable=True)         # JSON: ["https://api.example.com"]
    traffic_estimate = Column(String, nullable=True)    # e.g. "50K-100K/month"
    digital_presence_score = Column(Float, nullable=True)  # 0-100

    # ── AI Enrichment ─────────────────────────────────────────────────────────
    ai_summary = Column(Text, nullable=True)
    ai_profile = Column(Text, nullable=True)            # JSON: structured profile
    sector_classification = Column(String, nullable=True)
    risk_score = Column(Float, nullable=True)           # 0-100
    market_influence_score = Column(Float, nullable=True)  # 0-100
    innovation_score = Column(Float, nullable=True)     # 0-100
    reputation_score = Column(Float, nullable=True)     # 0-100

    # ── Scraping Metadata ─────────────────────────────────────────────────────
    last_scraped_at = Column(DateTime(timezone=True), nullable=True)
    last_changed_at = Column(DateTime(timezone=True), nullable=True)
    scrape_status = Column(String, default="pending")   # pending, scraping, done, failed
    scrape_error = Column(Text, nullable=True)
    data_completeness = Column(Float, default=0.0)      # 0-100 percentage

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # ── Relationships ──────────────────────────────────────────────────────────
    change_events = relationship("OrgChangeEvent", back_populates="organization")
    products_list = relationship("Product", back_populates="organization")
    services_list = relationship("Service", back_populates="organization")

    # ── Helpers ────────────────────────────────────────────────────────────────
    def get_emails(self):
        return json.loads(self.emails) if self.emails else []

    def get_phones(self):
        return json.loads(self.phone_numbers) if self.phone_numbers else []

    def get_social_links(self):
        return json.loads(self.social_links) if self.social_links else {}

    def get_services(self):
        return json.loads(self.services_offered) if self.services_offered else []

    def get_tech_stack(self):
        return json.loads(self.tech_stack) if self.tech_stack else []

    def get_industry_tags(self):
        return json.loads(self.industry_tags) if self.industry_tags else []

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "category": self.category,
            "description": self.description,
            "logo_url": self.logo_url,
            "website": self.website,
            "emails": self.get_emails(),
            "phone_numbers": self.get_phones(),
            "whatsapp_numbers": json.loads(self.whatsapp_numbers) if self.whatsapp_numbers else [],
            "physical_addresses": json.loads(self.physical_addresses) if self.physical_addresses else [],
            "gps_lat": self.gps_lat,
            "gps_lng": self.gps_lng,
            "branches": json.loads(self.branches) if self.branches else [],
            "operating_hours": json.loads(self.operating_hours) if self.operating_hours else {},
            "social_links": self.get_social_links(),
            "registration_status": self.registration_status,
            "registration_number": self.registration_number,
            "industry_tags": self.get_industry_tags(),
            "keywords": json.loads(self.keywords) if self.keywords else [],
            "ceo": self.ceo,
            "employee_size": self.employee_size,
            "revenue_estimate": self.revenue_estimate,
            "services_offered": self.get_services(),
            "rating_avg": self.rating_avg,
            "review_count": self.review_count,
            "sentiment_score": self.sentiment_score,
            "tech_stack": self.get_tech_stack(),
            "hosting_provider": self.hosting_provider,
            "traffic_estimate": self.traffic_estimate,
            "digital_presence_score": self.digital_presence_score,
            "ai_summary": self.ai_summary,
            "risk_score": self.risk_score,
            "market_influence_score": self.market_influence_score,
            "innovation_score": self.innovation_score,
            "reputation_score": self.reputation_score,
            "scrape_status": self.scrape_status,
            "data_completeness": self.data_completeness,
            "last_scraped_at": self.last_scraped_at.isoformat() if self.last_scraped_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
