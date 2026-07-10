"""
Agent Integration & Webhook API
================================
Designed for machine-to-machine communication:
  - External agents can push research items via webhook
  - Agents can query the AI Research Analyst
  - Agents can subscribe/unsubscribe from event webhooks
  - Agents can check system health and capability manifest

Endpoints
---------
POST   /api/v1/agent/ingest             - Push a research item from external source
POST   /api/v1/agent/ingest/batch       - Push multiple items in one call
POST   /api/v1/agent/query              - Natural-language query to RAG Analyst Agent
GET    /api/v1/agent/capabilities       - Machine-readable capability manifest
GET    /api/v1/agent/sources/active     - Quick list of active source IDs/types (for scrapers)
POST   /api/v1/agent/sources/{id}/heartbeat  - Scraper signals it is alive / last-seen
POST   /api/v1/agent/webhook/subscribe  - Register a webhook URL for events
DELETE /api/v1/agent/webhook/{wh_id}    - Unsubscribe a webhook
GET    /api/v1/agent/webhook            - List registered webhooks
"""

from fastapi import APIRouter, Depends, HTTPException, Header, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
import uuid
import httpx
import asyncio

from app.db import get_db
from app.models import (
    ResearchSource, ResearchItem, SourceStatus,
    ContentType, ResearchCategory
)

router = APIRouter(prefix="/api/v1/agent", tags=["agent-integration"])


# ============================================================================
# IN-MEMORY WEBHOOK STORE  (replace with DB table for production persistence)
# ============================================================================
_webhook_store: Dict[str, Dict[str, Any]] = {}


# ============================================================================
# SCHEMAS
# ============================================================================

class IngestItem(BaseModel):
    """A single research item submitted by an external agent / scraper."""
    title: str = Field(..., min_length=3, max_length=500)
    url: str = Field(..., description="Canonical URL of the item")
    abstract: Optional[str] = Field("", description="Abstract or summary text")
    authors: List[str] = Field(default_factory=list)
    published_date: Optional[datetime] = None
    content_type: str = Field("research_paper", description="ContentType enum value")
    source_name: str = Field(..., description="Must match an existing ResearchSource.name")
    categories: List[str] = Field(default_factory=list, description="ResearchCategory enum values")
    keywords: List[str] = Field(default_factory=list)
    extra_metadata: Optional[Dict[str, Any]] = None


class IngestResponse(BaseModel):
    item_id: str
    status: str
    message: str


class BatchIngestResponse(BaseModel):
    accepted: int
    rejected: int
    errors: List[Dict[str, str]]
    item_ids: List[str]


class AgentQueryRequest(BaseModel):
    question: str = Field(..., min_length=5, description="Natural-language question")
    context_hours: int = Field(24, ge=1, le=720, description="How many hours of context to include")


class AgentQueryResponse(BaseModel):
    answer: str
    sources_used: List[str]
    confidence: float
    generated_at: datetime


class CapabilityManifest(BaseModel):
    """Machine-readable description of what this API can do."""
    service: str
    version: str
    base_url: str
    capabilities: List[str]
    source_types: List[str]
    content_types: List[str]
    categories: List[str]
    endpoints: Dict[str, str]


class HeartbeatResponse(BaseModel):
    source_id: str
    source_name: str
    acknowledged_at: datetime
    status: str


class WebhookSubscription(BaseModel):
    callback_url: str = Field(..., description="URL that will receive POST notifications")
    events: List[str] = Field(
        default_factory=lambda: ["high_priority_item", "emerging_trend"],
        description="Events: high_priority_item | emerging_trend | source_error | daily_digest"
    )
    secret: Optional[str] = Field(None, description="Optional HMAC secret for signature verification")
    description: Optional[str] = None


class WebhookResponse(BaseModel):
    id: str
    callback_url: str
    events: List[str]
    description: Optional[str]
    created_at: datetime
    is_active: bool


# ============================================================================
# CAPABILITY MANIFEST  GET /api/v1/agent/capabilities
# ============================================================================

@router.get("/capabilities", response_model=CapabilityManifest, summary="Get API capabilities")
async def get_capabilities():
    """
    Returns a machine-readable manifest describing this service's capabilities.
    
    External orchestration agents should call this first to understand
    what the service can accept and expose.
    """
    return CapabilityManifest(
        service="AI Research Intelligence Platform",
        version="1.0.0",
        base_url="http://localhost:8002",
        capabilities=[
            "ingest_research_items",
            "rag_analyst_query",
            "source_management",
            "trend_detection",
            "intelligence_scoring",
            "webhook_subscriptions",
            "executive_report_generation",
        ],
        source_types=[
            "arxiv", "openreview", "papers_with_code", "huggingface",
            "corporate", "news", "community", "patent_grant", "policy", "gpu_market",
        ],
        content_types=[ct.value for ct in ContentType],
        categories=[rc.value for rc in ResearchCategory],
        endpoints={
            "ingest_single":   "POST /api/v1/agent/ingest",
            "ingest_batch":    "POST /api/v1/agent/ingest/batch",
            "analyst_query":   "POST /api/v1/agent/query",
            "list_sources":    "GET  /api/v1/sources",
            "create_source":   "POST /api/v1/sources",
            "bulk_sources":    "POST /api/v1/sources/bulk",
            "source_stats":    "GET  /api/v1/sources/{id}/stats",
            "research_items":  "GET  /api/v1/research/items",
            "trends":          "GET  /api/v1/research/trends",
            "emerging_trends": "GET  /api/v1/trends/emerging",
            "search":          "GET  /api/v1/search?q=<query>",
            "intelligence":    "GET  /api/v1/intelligence/summary",
            "webhook_sub":     "POST /api/v1/agent/webhook/subscribe",
            "webhook_list":    "GET  /api/v1/agent/webhook",
            "health":          "GET  /health",
            "docs":            "GET  /docs",
        },
    )


# ============================================================================
# INGEST SINGLE  POST /api/v1/agent/ingest
# ============================================================================

@router.post("/ingest", response_model=IngestResponse, status_code=201,
             summary="Ingest a single research item")
async def ingest_item(
    item: IngestItem,
    db: Session = Depends(get_db),
    x_agent_id: Optional[str] = Header(None, description="Optional agent identifier"),
):
    """
    Push a single research item from an external scraper or agent.
    
    The `source_name` must match an existing **ResearchSource.name** in the database.
    
    **Example call from an external agent:**
    ```bash
    curl -X POST http://localhost:8002/api/v1/agent/ingest \\
      -H "Content-Type: application/json" \\
      -H "X-Agent-Id: my-scraper-v1" \\
      -d '{
        "title": "GPT-5 Technical Report",
        "url": "https://openai.com/research/gpt5",
        "abstract": "We present GPT-5 ...",
        "source_name": "Corporate AI Labs",
        "content_type": "model_release",
        "categories": ["llm"]
      }'
    ```
    """
    source = db.query(ResearchSource).filter(ResearchSource.name == item.source_name).first()
    if not source:
        raise HTTPException(
            status_code=422,
            detail=f"Source '{item.source_name}' not found. "
                   f"Create it first at POST /api/v1/sources"
        )

    # Dedup by URL
    existing = db.query(ResearchItem).filter(ResearchItem.url == item.url).first()
    if existing:
        return IngestResponse(
            item_id=existing.id,
            status="duplicate",
            message="Item with this URL already exists"
        )

    research_item = ResearchItem(
        id=str(uuid.uuid4()),
        title=item.title,
        url=item.url,
        abstract=item.abstract or "",
        authors=item.authors,
        published_date=item.published_date,
        content_type=item.content_type,
        source_id=source.id,
        source_name=source.name,
        categories=item.categories,
        keywords=item.keywords,
        primary_category=item.categories[0] if item.categories else None,
        extra_metadata=item.extra_metadata,
    )
    db.add(research_item)

    # Update source last_checked
    source.last_checked = datetime.utcnow()
    db.commit()
    db.refresh(research_item)

    return IngestResponse(
        item_id=research_item.id,
        status="accepted",
        message="Item ingested successfully"
    )


# ============================================================================
# INGEST BATCH  POST /api/v1/agent/ingest/batch
# ============================================================================

@router.post("/ingest/batch", response_model=BatchIngestResponse, status_code=207,
             summary="Batch ingest multiple research items")
async def ingest_batch(
    items: List[IngestItem],
    db: Session = Depends(get_db),
    x_agent_id: Optional[str] = Header(None),
):
    """
    Push up to 100 items in a single request. Each item is processed independently;
    failures do not block the rest.

    Returns a `207 Multi-Status` with counts and any per-item errors.
    """
    if len(items) > 100:
        raise HTTPException(status_code=413, detail="Batch size limit is 100 items")

    accepted_ids: List[str] = []
    errors: List[Dict[str, str]] = []
    rejected = 0

    source_cache: Dict[str, Optional[ResearchSource]] = {}

    for item in items:
        try:
            if item.source_name not in source_cache:
                source_cache[item.source_name] = (
                    db.query(ResearchSource)
                    .filter(ResearchSource.name == item.source_name)
                    .first()
                )
            source = source_cache[item.source_name]
            if not source:
                raise ValueError(f"Unknown source: {item.source_name}")

            existing = db.query(ResearchItem).filter(ResearchItem.url == item.url).first()
            if existing:
                accepted_ids.append(existing.id)
                continue

            ri = ResearchItem(
                id=str(uuid.uuid4()),
                title=item.title,
                url=item.url,
                abstract=item.abstract or "",
                authors=item.authors,
                published_date=item.published_date,
                content_type=item.content_type,
                source_id=source.id,
                source_name=source.name,
                categories=item.categories,
                keywords=item.keywords,
                primary_category=item.categories[0] if item.categories else None,
                extra_metadata=item.extra_metadata,
            )
            db.add(ri)
            db.flush()
            accepted_ids.append(ri.id)
        except Exception as exc:
            rejected += 1
            errors.append({"url": item.url, "error": str(exc)})

    db.commit()

    return BatchIngestResponse(
        accepted=len(accepted_ids),
        rejected=rejected,
        errors=errors,
        item_ids=accepted_ids,
    )


# ============================================================================
# RAG ANALYST QUERY  POST /api/v1/agent/query
# ============================================================================

@router.post("/query", response_model=AgentQueryResponse, summary="Query the AI Analyst Agent")
async def agent_query(request: AgentQueryRequest, db: Session = Depends(get_db)):
    """
    Ask a natural-language question. The RAG agent searches the knowledge base
    and returns a structured answer with cited sources.

    **Example:**
    ```json
    {
      "question": "What are the top 3 breakthroughs in LLM reasoning from the last 24 hours?",
      "context_hours": 24
    }
    ```

    **Response fields:**
    - `answer` – The synthesized answer text
    - `sources_used` – URLs of items used to construct the answer  
    - `confidence` – 0.0–1.0 confidence score
    - `generated_at` – Timestamp of generation
    """
    try:
        from app.services.agents import RAGAnalystAgent
        agent = RAGAnalystAgent()
        raw = await agent.answer_question(request.question)

        return AgentQueryResponse(
            answer=raw.get("answer", str(raw)),
            sources_used=raw.get("sources", []),
            confidence=raw.get("confidence", 0.75),
            generated_at=datetime.utcnow(),
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Analyst agent unavailable: {exc}")


# ============================================================================
# ACTIVE SOURCES (for scrapers)  GET /api/v1/agent/sources/active
# ============================================================================

@router.get("/sources/active", summary="List active sources for scrapers")
async def list_active_sources(db: Session = Depends(get_db)):
    """
    Lightweight endpoint for scraper agents: returns only `id`, `name`,
    `source_type`, `url`, and `rate_limit_per_minute` for all active sources.
    
    Designed for fast polling by scraper services that need to know
    *what* to scrape without pulling full source details.
    """
    sources = (
        db.query(ResearchSource)
        .filter(ResearchSource.is_active == True)
        .order_by(ResearchSource.authority_score.desc())
        .all()
    )
    return [
        {
            "id": s.id,
            "name": s.name,
            "source_type": s.source_type,
            "url": s.url,
            "authority_score": s.authority_score,
            "rate_limit_per_minute": s.rate_limit_per_minute,
            "timeout_seconds": s.timeout_seconds,
        }
        for s in sources
    ]


# ============================================================================
# HEARTBEAT  POST /api/v1/agent/sources/{source_id}/heartbeat
# ============================================================================

@router.post("/sources/{source_id}/heartbeat", response_model=HeartbeatResponse,
             summary="Scraper heartbeat / last-seen update")
async def source_heartbeat(
    source_id: str,
    db: Session = Depends(get_db),
    x_agent_id: Optional[str] = Header(None),
):
    """
    Call this endpoint from your scraper to signal it is alive and has
    successfully checked the source. Resets `consecutive_failures` to 0
    and updates `last_checked`.

    This lets the monitoring dashboard show which scrapers are active.
    """
    source = db.query(ResearchSource).filter(ResearchSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail=f"Source '{source_id}' not found")

    source.last_checked = datetime.utcnow()
    source.consecutive_failures = 0
    if source.status == SourceStatus.ERROR or source.status == SourceStatus.DEGRADED:
        source.status = SourceStatus.ACTIVE
    db.commit()

    return HeartbeatResponse(
        source_id=source.id,
        source_name=source.name,
        acknowledged_at=source.last_checked,
        status=source.status.value,
    )


# ============================================================================
# WEBHOOK SUBSCRIBE  POST /api/v1/agent/webhook/subscribe
# ============================================================================

@router.post("/webhook/subscribe", response_model=WebhookResponse, status_code=201,
             summary="Subscribe to event webhooks")
async def subscribe_webhook(payload: WebhookSubscription):
    """
    Register a callback URL to receive real-time event notifications.

    **Supported events:**
    | Event | Description |
    |---|---|
    | `high_priority_item` | A new item with importance_score > 85 was ingested |
    | `emerging_trend` | A new emerging trend was detected |
    | `source_error` | A source has consecutive failures |
    | `daily_digest` | Daily digest report is ready |

    **Webhook payload shape (POST to your callback_url):**
    ```json
    {
      "event": "high_priority_item",
      "timestamp": "2026-07-10T08:00:00Z",
      "data": { ... }
    }
    ```

    If `secret` is provided, each webhook POST includes an
    `X-Signature-SHA256` header for verification.
    """
    valid_events = {"high_priority_item", "emerging_trend", "source_error", "daily_digest"}
    invalid = [e for e in payload.events if e not in valid_events]
    if invalid:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown events: {invalid}. Valid: {sorted(valid_events)}"
        )

    wh_id = str(uuid.uuid4())
    record = {
        "id": wh_id,
        "callback_url": payload.callback_url,
        "events": payload.events,
        "secret": payload.secret,
        "description": payload.description,
        "created_at": datetime.utcnow(),
        "is_active": True,
    }
    _webhook_store[wh_id] = record

    return WebhookResponse(**{k: v for k, v in record.items() if k != "secret"})


# ============================================================================
# LIST WEBHOOKS  GET /api/v1/agent/webhook
# ============================================================================

@router.get("/webhook", response_model=List[WebhookResponse], summary="List registered webhooks")
async def list_webhooks():
    """Returns all currently registered webhook subscriptions."""
    return [
        WebhookResponse(**{k: v for k, v in wh.items() if k != "secret"})
        for wh in _webhook_store.values()
    ]


# ============================================================================
# DELETE WEBHOOK  DELETE /api/v1/agent/webhook/{wh_id}
# ============================================================================

@router.delete("/webhook/{wh_id}", status_code=204, summary="Unsubscribe a webhook")
async def delete_webhook(wh_id: str):
    """Remove a webhook subscription."""
    if wh_id not in _webhook_store:
        raise HTTPException(status_code=404, detail=f"Webhook '{wh_id}' not found")
    del _webhook_store[wh_id]
    return None
