from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel

from app.db import get_db
from app.models import (
    ResearchItem, ItemEnrichment, User, Trend, AlertLog, 
    ResearchCategory, EmailLog, ScheduledReport, Startup, AIModel
)

router = APIRouter(prefix="/api/v1", tags=["research"])


# ============================================================================
# SCHEMAS
# ============================================================================

class ItemResponse(BaseModel):
    id: str
    title: str
    url: str
    abstract: str
    authors: List[str]
    published_date: Optional[datetime]
    categories: List[str]
    content_type: str
    source_name: Optional[str]
    
    class Config:
        from_attributes = True


class ItemDetailResponse(ItemResponse):
    enrichment: Optional['EnrichmentResponse']


class EnrichmentResponse(BaseModel):
    executive_summary: Optional[str]
    technical_summary: Optional[str]
    business_impact: Optional[str]
    innovation_score: float
    market_impact_score: float
    research_significance_score: float
    importance_score: float
    intelligence_score: float
    virality_prediction: float
    impact_prediction: float
    key_insights: List[str]
    potential_applications: List[str]
    
    class Config:
        from_attributes = True


class TrendResponse(BaseModel):
    id: str
    name: str
    category: Optional[str]
    mention_count: int
    growth_rate: float
    trend_score: float
    is_emerging: bool
    
    class Config:
        from_attributes = True


class DashboardMetricsResponse(BaseModel):
    total_items: int
    total_sources: int
    alerts_sent_24h: int
    high_priority_items: int
    trending_topics: int
    email_success_rate: float
    avg_processing_latency_ms: float


class SourceResponse(BaseModel):
    id: str
    name: str
    source_type: str
    url: str
    category: Optional[str] = None
    authority_score: float
    is_active: bool
    status: str
    
    class Config:
        from_attributes = True


# ============================================================================
# RESEARCH ITEMS ENDPOINTS
# ============================================================================

@router.get("/items", response_model=List[ItemDetailResponse])
@router.get("/research/items", response_model=List[ItemDetailResponse])
async def get_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    min_score: float = Query(0, ge=0, le=100),
    hours: int = Query(24, ge=1),
    db: Session = Depends(get_db)
):
    """Get research items with optional filtering."""
    query = db.query(ResearchItem).filter(
        ResearchItem.created_at > datetime.utcnow() - timedelta(hours=hours)
    )
    
    if category:
        query = query.filter(ResearchItem.primary_category == category)
    
    if min_score > 0:
        query = query.join(ItemEnrichment).filter(
            ItemEnrichment.importance_score >= min_score
        )
    
    items = query.order_by(ResearchItem.created_at.desc()).offset(skip).limit(limit).all()
    
    return items


@router.get("/items/{item_id}", response_model=ItemDetailResponse)
async def get_item(item_id: str, db: Session = Depends(get_db)):
    """Get specific research item with full details."""
    item = db.query(ResearchItem).filter(ResearchItem.id == item_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item


@router.get("/items/trending/today", response_model=List[ItemDetailResponse])
async def get_trending_items(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get today's trending items by importance score."""
    cutoff = datetime.utcnow() - timedelta(hours=24)
    
    items = db.query(ResearchItem).join(ItemEnrichment).filter(
        ResearchItem.created_at > cutoff
    ).order_by(ItemEnrichment.importance_score.desc()).limit(limit).all()
    
    return items


@router.get("/items/high-priority", response_model=List[ItemDetailResponse])
async def get_high_priority_items(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get high-priority items (importance score > 85)."""
    items = db.query(ResearchItem).join(ItemEnrichment).filter(
        ItemEnrichment.importance_score > 85
    ).order_by(ItemEnrichment.intelligence_score.desc()).limit(limit).all()
    
    return items


@router.get("/items/by-category/{category}", response_model=List[ItemDetailResponse])
async def get_items_by_category(
    category: str,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get items by research category."""
    items = db.query(ResearchItem).filter(
        ResearchItem.primary_category == category
    ).order_by(ResearchItem.created_at.desc()).limit(limit).all()
    
    return items


# ============================================================================
# TRENDS ENDPOINTS
# ============================================================================

@router.get("/trends", response_model=List[TrendResponse])
@router.get("/research/trends", response_model=List[TrendResponse])
async def get_trends(
    emerging_only: bool = Query(False),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get detected trends."""
    query = db.query(Trend)
    
    if emerging_only:
        query = query.filter(Trend.is_emerging == True)
    
    trends = query.order_by(Trend.trend_score.desc()).limit(limit).all()
    return trends


@router.get("/trends/emerging", response_model=List[TrendResponse])
async def get_emerging_trends(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get emerging trends (fast-growing topics)."""
    trends = db.query(Trend).filter(
        Trend.is_emerging == True,
        Trend.growth_rate > 50  # >50% growth
    ).order_by(Trend.growth_rate.desc()).limit(limit).all()
    
    return trends


# ============================================================================
# DASHBOARD & MONITORING ENDPOINTS
# ============================================================================

@router.get("/dashboard/metrics", response_model=DashboardMetricsResponse)
async def get_dashboard_metrics(db: Session = Depends(get_db)):
    """Get system metrics for dashboard."""
    from app.models import ResearchSource, EmailLog
    
    total_items = db.query(ResearchItem).count()
    total_sources = db.query(ResearchSource).filter(ResearchSource.is_active == True).count()
    
    cutoff_24h = datetime.utcnow() - timedelta(hours=24)
    alerts_sent_24h = db.query(AlertLog).filter(AlertLog.sent_at > cutoff_24h).count()
    
    high_priority = db.query(ResearchItem).join(ItemEnrichment).filter(
        ItemEnrichment.importance_score > 85
    ).count()
    
    trending = db.query(Trend).filter(Trend.is_emerging == True).count()
    
    # Email success rate
    total_emails = db.query(EmailLog).filter(EmailLog.sent_at > cutoff_24h).count()
    successful_emails = db.query(EmailLog).filter(
        and_(
            EmailLog.sent_at > cutoff_24h,
            EmailLog.status == "sent"
        )
    ).count()
    
    email_success_rate = (successful_emails / total_emails * 100) if total_emails > 0 else 0
    
    return DashboardMetricsResponse(
        total_items=total_items,
        total_sources=total_sources,
        alerts_sent_24h=alerts_sent_24h,
        high_priority_items=high_priority,
        trending_topics=trending,
        email_success_rate=email_success_rate,
        avg_processing_latency_ms=250.0  # Placeholder
    )


@router.get("/dashboard/sources-health")
async def get_sources_health(db: Session = Depends(get_db)):
    """Get health status of all sources."""
    from app.models import ResearchSource
    
    sources = db.query(ResearchSource).all()
    health_data = []
    
    for source in sources:
        items_24h = db.query(ResearchItem).filter(
            and_(
                ResearchItem.source_id == source.id,
                ResearchItem.created_at > datetime.utcnow() - timedelta(hours=24)
            )
        ).count()
        
        health_data.append({
            "name": source.name,
            "status": source.status.value,
            "items_24h": items_24h,
            "authority_score": source.authority_score,
            "last_checked": source.last_checked
        })
    
    return health_data


@router.get("/dashboard/summary-stats")
async def get_summary_stats(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Get summary statistics for time period."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    total_items = db.query(ResearchItem).filter(
        ResearchItem.created_at > cutoff
    ).count()
    
    high_priority = db.query(ResearchItem).join(ItemEnrichment).filter(
        and_(
            ResearchItem.created_at > cutoff,
            ItemEnrichment.importance_score > 85
        )
    ).count()
    
    # By category
    by_category = db.query(
        ResearchItem.primary_category,
        db.func.count(ResearchItem.id)
    ).filter(
        ResearchItem.created_at > cutoff
    ).group_by(ResearchItem.primary_category).all()
    
    return {
        "period_days": days,
        "total_items": total_items,
        "high_priority_items": high_priority,
        "by_category": [
            {"category": cat.value if cat else "unknown", "count": count}
            for cat, count in by_category if cat
        ]
    }


# ============================================================================
# SEARCH ENDPOINTS
# ============================================================================

@router.get("/search")
async def search_items(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Full-text search across items."""
    search_term = f"%{q}%"
    
    items = db.query(ResearchItem).filter(
        or_(
            ResearchItem.title.ilike(search_term),
            ResearchItem.abstract.ilike(search_term),
            ResearchItem.keywords.contains([q])  # For array search
        )
    ).limit(limit).all()
    
    return items


# ============================================================================
# INTELLIGENCE & PREDICTIONS
# ============================================================================

@router.get("/intelligence/summary")
async def get_intelligence_summary(
    hours: int = Query(24, ge=1),
    db: Session = Depends(get_db)
):
    """Get AI intelligence summary for period."""
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    items = db.query(ResearchItem).join(ItemEnrichment).filter(
        ResearchItem.created_at > cutoff
    ).order_by(ItemEnrichment.intelligence_score.desc()).limit(10).all()
    
    summary = {
        "period_hours": hours,
        "top_items": [
            {
                "title": item.title,
                "url": item.url,
                "intelligence_score": item.enrichment.intelligence_score,
                "impact_prediction": item.enrichment.impact_prediction,
                "virality_prediction": item.enrichment.virality_prediction
            }
            for item in items if item.enrichment
        ]
    }
    
    return summary


@router.get("/intelligence/key-findings")
async def get_key_findings(
    hours: int = Query(24, ge=1),
    db: Session = Depends(get_db)
):
    """Get key findings from latest research."""
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    items = db.query(ResearchItem).join(ItemEnrichment).filter(
        and_(
            ResearchItem.created_at > cutoff,
            ItemEnrichment.importance_score > 80
        )
    ).order_by(ItemEnrichment.importance_score.desc()).limit(5).all()
    
    findings = []
    for item in items:
        if item.enrichment:
            findings.append({
                "title": item.title,
                "insights": item.enrichment.key_insights,
                "applications": item.enrichment.potential_applications,
                "research_gaps": item.enrichment.research_gaps
            })
    
    return findings


class AnalystQueryRequest(BaseModel):
    question: str


@router.post("/analyst/query")
async def query_analyst_agent(
    request: AnalystQueryRequest,
    db: Session = Depends(get_db)
):
    """Query the RAG AI Research Analyst Agent."""
    from app.services.agents import RAGAnalystAgent
    agent = RAGAnalystAgent()
    response = await agent.answer_question(request.question)
    return response


@router.get("/startups")
async def get_startups(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get tracked AI startups with funding and valuation predictions."""
    startups = db.query(Startup).order_by(Startup.latest_funding_date.desc()).limit(limit).all()
    return startups


@router.get("/models")
async def get_models(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get AI models and performance benchmarks."""
    models = db.query(AIModel).order_by(AIModel.release_date.desc()).limit(limit).all()
    return models


@router.get("/market/gpu")
async def get_gpu_market(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get GPU cloud pricing indices."""
    gpu_indices = db.query(GPUMarketIndex).order_by(GPUMarketIndex.recorded_at.desc()).limit(limit).all()
    return gpu_indices


@router.get("/policy-alerts")
async def get_policy_alerts(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get critical AI policy and regulatory updates."""
    policies = db.query(RegulationPolicy).order_by(RegulationPolicy.announcement_date.desc()).limit(limit).all()
    return policies


@router.get("/digests/{report_id}/pdf")
async def download_digest_pdf(
    report_id: str,
    db: Session = Depends(get_db)
):
    """Download PDF executive report for a scheduled digest."""
    from fastapi.responses import Response
    from app.email_service.sender import EmailService
    
    report = db.query(ScheduledReport).filter_by(id=report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Digest report not found")
        
    items = []
    if report.top_papers:
        items = db.query(ResearchItem).filter(ResearchItem.id.in_(report.top_papers)).all()
        
    enrichments = {item.id: item.enrichment for item in items if item.enrichment}
    
    email_service = EmailService()
    pdf_bytes = email_service.generate_digest_pdf(
        items=items,
        enrichments=enrichments,
        report_data={"trending_topics": report.emerging_trends or []}
    )
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=AI_Executive_Report_{report_id}.pdf"}
    )


@router.get("/sources", response_model=List[SourceResponse])
@router.get("/research/sources", response_model=List[SourceResponse])
async def get_sources(db: Session = Depends(get_db)):
    """Get all research and news sources."""
    from app.models import ResearchSource
    sources = db.query(ResearchSource).all()
    return sources


# Update response model references
ItemDetailResponse.update_forward_refs()
SourceResponse.update_forward_refs()

