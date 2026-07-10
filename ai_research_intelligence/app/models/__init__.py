from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, String, Integer, Float, Text, DateTime, Boolean, 
    ForeignKey, Index, JSON, Enum as SQLEnum, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
import uuid

Base = declarative_base()


class ContentType(str, enum.Enum):
    """Content types."""
    RESEARCH_PAPER = "research_paper"
    NEWS_ARTICLE = "news_article"
    BLOG_POST = "blog_post"
    GITHUB_REPO = "github_repo"
    MODEL_RELEASE = "model_release"
    STARTUP_ANNOUNCEMENT = "startup_announcement"
    FUNDING_ROUND = "funding_round"
    BENCHMARK_RESULT = "benchmark_result"
    CONFERENCE_ANNOUNCEMENT = "conference_announcement"
    GRANT_ANNOUNCEMENT = "grant_announcement"
    REGULATORY_POLICY = "regulatory_policy"
    GPU_MARKET_INDEX = "gpu_market_index"
    PATENT_FILING = "patent_filing"



class ResearchCategory(str, enum.Enum):
    """AI Research categories."""
    LLM = "llm"
    AGENTS = "agents"
    ROBOTICS = "robotics"
    COMPUTER_VISION = "computer_vision"
    NLP = "nlp"
    SPEECH_AI = "speech_ai"
    MULTIMODAL = "multimodal_ai"
    INFRASTRUCTURE = "ai_infrastructure"
    SAFETY = "ai_safety"
    ALIGNMENT = "ai_alignment"
    HARDWARE = "ai_hardware"
    HEALTHCARE = "ai_healthcare"
    FINANCE = "ai_finance"
    EDUCATION = "ai_education"
    SECURITY = "ai_security"
    POLICY = "ai_policy"
    SUSTAINABILITY = "ai_sustainability"


class AlertPriority(str, enum.Enum):
    """Alert priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SourceStatus(str, enum.Enum):
    """Source health status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEGRADED = "degraded"
    ERROR = "error"


class ResearchSource(Base):
    """Research and news sources configuration."""
    __tablename__ = "research_sources"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), unique=True, nullable=False, index=True)
    source_type = Column(String(50), nullable=False)  # arxiv, papers_with_code, news, twitter, etc.
    url = Column(String(500), nullable=False)
    category = Column(String(100), nullable=True)
    authority_score = Column(Float, default=0.5)  # 0-1, weights importance
    is_active = Column(Boolean, default=True, index=True)
    last_checked = Column(DateTime, nullable=True)
    next_check = Column(DateTime, nullable=True)
    status = Column(SQLEnum(SourceStatus), default=SourceStatus.ACTIVE, index=True)
    consecutive_failures = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    timeout_seconds = Column(Integer, default=30)
    headers = Column(JSON, nullable=True)
    authentication = Column(JSON, nullable=True)
    rate_limit_per_minute = Column(Integer, default=10)
    last_rate_limit_reset = Column(DateTime, nullable=True)
    extra_metadata = Column(JSON, nullable=True)  # renamed from metadata (reserved by SQLAlchemy)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    items = relationship("ResearchItem", back_populates="source", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_source_type_active", "source_type", "is_active"),
        Index("idx_source_next_check", "next_check"),
    )


class ResearchItem(Base):
    """Discovered AI research papers, articles, and announcements."""
    __tablename__ = "research_items"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(String(36), ForeignKey("research_sources.id"), nullable=False, index=True)
    
    # Metadata
    title = Column(String(500), nullable=False, index=True)
    url = Column(String(1000), unique=True, nullable=False, index=True)
    content_type = Column(SQLEnum(ContentType), nullable=False, index=True)
    source_url = Column(String(1000), nullable=True)  # Original source
    
    # Content
    abstract = Column(Text, nullable=True)
    full_text = Column(Text, nullable=True)
    authors = Column(JSON, nullable=True)  # List[str] stored as JSON
    keywords = Column(JSON, nullable=True)  # List[str] stored as JSON
    
    # Publication Info
    published_date = Column(DateTime, nullable=True, index=True)
    discovered_date = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Categorization
    categories = Column(JSON, nullable=True)  # List[str] stored as JSON
    primary_category = Column(SQLEnum(ResearchCategory), nullable=True, index=True)
    
    # Image and metadata
    image_url = Column(String(1000), nullable=True)
    extra_metadata = Column(JSON, nullable=True)  # renamed from metadata (reserved by SQLAlchemy)
    url_hash = Column(String(64), unique=True, nullable=False, index=True)
    content_hash = Column(String(64), nullable=True, index=True)
    duplicate_of = Column(String(36), ForeignKey("research_items.id"), nullable=True)
    
    # Relationship
    source = relationship("ResearchSource", back_populates="items")
    enrichment = relationship("ItemEnrichment", back_populates="item", uselist=False, cascade="all, delete-orphan")
    classifications = relationship("ItemClassification", back_populates="item", cascade="all, delete-orphan")
    embeddings = relationship("ItemEmbedding", back_populates="item", cascade="all, delete-orphan")
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def source_name(self) -> Optional[str]:
        return self.source.name if self.source else None
    
    __table_args__ = (
        Index("idx_item_type_published", "content_type", "published_date"),
        Index("idx_item_source_discovered", "source_id", "discovered_date"),
        Index("idx_item_category", "primary_category"),
    )


class ItemEnrichment(Base):
    """AI-generated enrichments for research items."""
    __tablename__ = "item_enrichments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_id = Column(String(36), ForeignKey("research_items.id"), nullable=False, unique=True, index=True)
    
    # Summaries
    executive_summary = Column(Text, nullable=True)
    technical_summary = Column(Text, nullable=True)
    business_impact = Column(Text, nullable=True)
    
    # Scores (0-100)
    innovation_score = Column(Float, default=0.0)
    market_impact_score = Column(Float, default=0.0)
    research_significance_score = Column(Float, default=0.0)
    citation_velocity = Column(Float, default=0.0)
    social_engagement_score = Column(Float, default=0.0)
    technical_novelty_score = Column(Float, default=0.0)
    
    # Final Ranking
    importance_score = Column(Float, default=0.0, index=True)
    intelligence_score = Column(Float, default=0.0, index=True)  # Enhanced hedge-fund score
    virality_prediction = Column(Float, default=0.0)
    impact_prediction = Column(Float, default=0.0)
    valuation_potential_score = Column(Float, default=0.0)  # For hedge-fund scoring
    regulatory_feasibility_score = Column(Float, default=0.0)  # Regulatory risk factor
    
    # Generation Info
    model_used = Column(String(100), nullable=True)
    generation_timestamp = Column(DateTime, default=datetime.utcnow)
    
    # AI Insights
    key_insights = Column(JSON, nullable=True)  # List[str] stored as JSON
    potential_applications = Column(JSON, nullable=True)  # List[str] stored as JSON
    research_gaps = Column(JSON, nullable=True)  # List[str] stored as JSON
    
    item = relationship("ResearchItem", back_populates="enrichment")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_enrichment_importance", "importance_score"),
        Index("idx_enrichment_intelligence", "intelligence_score"),
    )


class ItemClassification(Base):
    """Classification tags for research items."""
    __tablename__ = "item_classifications"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_id = Column(String(36), ForeignKey("research_items.id"), nullable=False, index=True)
    category = Column(SQLEnum(ResearchCategory), nullable=False)
    confidence = Column(Float, default=0.0)  # 0-1
    
    created_at = Column(DateTime, default=datetime.utcnow)
    item = relationship("ResearchItem", back_populates="classifications")
    
    __table_args__ = (
        Index("idx_classification_category", "category"),
        UniqueConstraint("item_id", "category", name="unique_item_category"),
    )


class ItemEmbedding(Base):
    """Vector embeddings for semantic search and deduplication."""
    __tablename__ = "item_embeddings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_id = Column(String(36), ForeignKey("research_items.id"), nullable=False, unique=True, index=True)
    embedding_model = Column(String(100), nullable=False)
    vector_dimension = Column(Integer, nullable=False)
    vector_data = Column(JSON, nullable=False)  # List[float] stored as JSON
    
    item = relationship("ResearchItem", back_populates="embeddings")
    
    created_at = Column(DateTime, default=datetime.utcnow)


class User(Base):
    """User accounts."""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    is_admin = Column(Boolean, default=False)
    preferred_categories = Column(JSON, nullable=True)  # List[str] stored as JSON
    alert_frequency = Column(String(50), default="realtime")  # realtime, daily, weekly
    digest_frequency_hours = Column(Integer, default=4)
    email_verified = Column(Boolean, default=False)
    api_key = Column(String(255), unique=True, nullable=True)
    preferences = Column(JSON, nullable=True)
    
    subscriptions = relationship("UserSubscription", back_populates="user", cascade="all, delete-orphan")
    alert_history = relationship("AlertLog", back_populates="user", cascade="all, delete-orphan")
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserSubscription(Base):
    """User preferences for content categories."""
    __tablename__ = "user_subscriptions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    category = Column(SQLEnum(ResearchCategory), nullable=False)
    alert_threshold = Column(Float, default=0.0)  # Importance score threshold
    
    user = relationship("User", back_populates="subscriptions")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint("user_id", "category", name="unique_user_category"),
    )


class AlertLog(Base):
    """Log of sent alerts."""
    __tablename__ = "alert_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    item_id = Column(String(36), ForeignKey("research_items.id"), nullable=False, index=True)
    priority = Column(SQLEnum(AlertPriority), default=AlertPriority.MEDIUM, index=True)
    importance_score = Column(Float, default=0.0)
    sent_at = Column(DateTime, default=datetime.utcnow, index=True)
    email_sent = Column(Boolean, default=False)
    email_status = Column(String(100), nullable=True)
    read = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="alert_history")
    
    __table_args__ = (
        Index("idx_alert_user_sent", "user_id", "sent_at"),
        Index("idx_alert_item_sent", "item_id", "sent_at"),
    )


class EmailLog(Base):
    """Email delivery logs."""
    __tablename__ = "email_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    recipient_email = Column(String(255), nullable=False, index=True)
    subject = Column(String(500), nullable=False)
    email_type = Column(String(100), nullable=False)  # alert, digest, report
    status = Column(String(50), default="pending", index=True)  # pending, sent, failed, bounced
    error_message = Column(Text, nullable=True)
    message_id = Column(String(255), nullable=True, unique=True)
    items_count = Column(Integer, default=0)
    sent_at = Column(DateTime, nullable=True)
    delivery_confirmation_at = Column(DateTime, nullable=True)
    opened_at = Column(DateTime, nullable=True)
    clicked_links = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_email_recipient_type", "recipient_email", "email_type"),
        Index("idx_email_status_sent", "status", "sent_at"),
    )


class Trend(Base):
    """Detected trends and emerging topics."""
    __tablename__ = "trends"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    category = Column(SQLEnum(ResearchCategory), nullable=True, index=True)
    description = Column(Text, nullable=True)
    
    # Trend Metrics
    mention_count = Column(Integer, default=0)
    growth_rate = Column(Float, default=0.0)  # % change
    trend_score = Column(Float, default=0.0)  # 0-100
    emergence_date = Column(DateTime, nullable=True)
    peak_date = Column(DateTime, nullable=True)
    
    # Related Data
    related_papers_count = Column(Integer, default=0)
    related_startups_count = Column(Integer, default=0)
    related_funding = Column(Float, default=0.0)
    
    # Sentiment
    sentiment_score = Column(Float, default=0.0)  # -1 to 1
    sentiment_label = Column(String(50), nullable=True)  # positive, negative, neutral
    
    # Predictions
    viability_prediction = Column(Float, default=0.0)  # 0-1
    market_impact_prediction = Column(Float, default=0.0)  # 0-1
    adoption_timeline_months = Column(Integer, nullable=True)
    
    is_emerging = Column(Boolean, default=True, index=True)
    is_declining = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Startup(Base):
    """AI startup tracking."""
    __tablename__ = "startups"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    website = Column(String(500), nullable=True)
    
    # Funding Information
    total_funding = Column(Float, default=0.0)
    latest_funding_round = Column(Float, default=0.0)
    latest_funding_date = Column(DateTime, nullable=True)
    funding_stage = Column(String(100), nullable=True)  # seed, series_a, etc.
    
    # Company Info
    founded_date = Column(DateTime, nullable=True)
    headquarters = Column(String(255), nullable=True)
    team_size = Column(Integer, nullable=True)
    focus_areas = Column(JSON, nullable=True)  # List[str] stored as JSON
    
    # Valuation Prediction
    current_valuation = Column(Float, nullable=True)
    predicted_valuation = Column(Float, nullable=True)
    valuation_confidence = Column(Float, default=0.0)
    
    # Tracking
    mentioned_in_papers = Column(Integer, default=0)
    mentioned_in_news = Column(Integer, default=0)
    reputation_score = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AIModel(Base):
    """AI Model benchmark tracking."""
    __tablename__ = "ai_models"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), unique=True, nullable=False, index=True)
    organization = Column(String(255), nullable=False)
    model_type = Column(String(100), nullable=False)  # llm, vision, etc.
    
    # Performance Metrics
    benchmark_dataset = Column(String(255), nullable=True)
    benchmark_score = Column(Float, nullable=True)
    vs_gpt4_performance = Column(Float, nullable=True)  # percentage
    parameter_count = Column(Integer, nullable=True)
    context_length = Column(Integer, nullable=True)
    
    # Availability
    is_open_source = Column(Boolean, default=False)
    release_date = Column(DateTime, nullable=True, index=True)
    
    # Tracking
    paper_id = Column(String(36), ForeignKey("research_items.id"), nullable=True)
    monthly_mentions = Column(Integer, default=0)
    adoption_score = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Patent(Base):
    """AI-related patent tracking."""
    __tablename__ = "patents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patent_number = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    organization = Column(String(255), nullable=False, index=True)
    abstract = Column(Text, nullable=True)
    filing_date = Column(DateTime, nullable=True, index=True)
    grant_date = Column(DateTime, nullable=True)
    technology_area = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class ScheduledReport(Base):
    """Scheduled digest reports."""
    __tablename__ = "scheduled_reports"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_type = Column(String(100), nullable=False)  # digest, weekly, monthly
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    scheduled_time = Column(DateTime, nullable=False, index=True)
    generated_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="pending", index=True)  # pending, generated, sent, failed
    
    top_papers = Column(JSON, nullable=True)  # List of item IDs
    top_news = Column(JSON, nullable=True)
    top_releases = Column(JSON, nullable=True)
    emerging_trends = Column(JSON, nullable=True)
    
    report_data = Column(JSON, nullable=True)  # Full report content
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SystemMetric(Base):
    """System health and performance metrics."""
    __tablename__ = "system_metrics"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_name = Column(String(255), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50), nullable=True)
    tags = Column(JSON, nullable=True)
    
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index("idx_metric_name_recorded", "metric_name", "recorded_at"),
    )


class SourceHealth(Base):
    """Source health and reliability metrics."""
    __tablename__ = "source_health"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(String(36), ForeignKey("research_sources.id"), nullable=False, index=True)
    check_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Health Metrics
    response_time_ms = Column(Integer, nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(String(500), nullable=True)
    http_status_code = Column(Integer, nullable=True)
    items_found = Column(Integer, default=0)
    
    # Uptime tracking
    availability_percentage = Column(Float, default=100.0)
    average_response_time = Column(Float, default=0.0)
    total_checks = Column(Integer, default=0)
    total_failures = Column(Integer, default=0)


class Grant(Base):
    """AI research grants tracking."""
    __tablename__ = "grants"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False)
    agency = Column(String(255), nullable=False, index=True)
    amount = Column(Float, nullable=True)
    award_date = Column(DateTime, nullable=True, index=True)
    recipient_organization = Column(String(255), nullable=True)
    abstract = Column(Text, nullable=True)
    url = Column(String(1000), nullable=True)
    focus_areas = Column(JSON, nullable=True)  # List[str] stored as JSON
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class RegulationPolicy(Base):
    """Global AI policy and regulation tracking."""
    __tablename__ = "regulation_policies"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False)
    governing_body = Column(String(255), nullable=False, index=True)
    jurisdiction = Column(String(100), nullable=False, index=True)  # US, EU, Global, etc.
    status = Column(String(100), nullable=False)  # Draft, Active, Proposed, etc.
    announcement_date = Column(DateTime, nullable=True, index=True)
    summary = Column(Text, nullable=True)
    impact_level = Column(String(50), default="medium")  # low, medium, high, critical
    url = Column(String(1000), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class GPUMarketIndex(Base):
    """GPU pricing and availability index."""
    __tablename__ = "gpu_market_indices"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    gpu_model = Column(String(100), nullable=False, index=True)  # H100, A100, B200, etc.
    provider = Column(String(100), nullable=False, index=True)  # AWS, GCP, Lambda Labs, RunPod, etc.
    price_per_hour = Column(Float, nullable=False)
    availability_status = Column(String(50), default="available")  # available, scarce, out_of_stock
    demand_index = Column(Float, default=1.0)  # relative demand multiplier
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)

