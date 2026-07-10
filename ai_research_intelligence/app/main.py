from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

from app.config import settings
from app.db import init_db, verify_db_connection
from app.api import research
from app.api import sources as sources_api
from app.api import agents as agents_api

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Research Intelligence Platform",
    description="Production-grade AI research monitoring and analysis system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# LIFECYCLE EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    logger.info(f"Starting AI Research Intelligence Platform ({settings.ENVIRONMENT})")
    
    # Initialize database
    try:
        init_db()
        if verify_db_connection():
            logger.info("Database connection verified")
        else:
            logger.warning("Database connection verification failed")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    logger.info("Startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down AI Research Intelligence Platform")


# ============================================================================
# ROUTES
# ============================================================================

app.include_router(research.router)
app.include_router(sources_api.router)
app.include_router(agents_api.router)


# ============================================================================
# HEALTH CHECKS
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    db_ok = verify_db_connection()
    
    if not db_ok:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not ready", "reason": "database connection failed"}
        )
    
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "database": "ok"
        }
    }


# ============================================================================
# DOCUMENTATION ROUTES
# ============================================================================

from fastapi.templating import Jinja2Templates
from fastapi import Request
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import ResearchItem, ResearchSource, Trend, ItemEnrichment

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root(request: Request, db: Session = Depends(get_db)):
    """Root endpoint - Dashboard Frontend."""
    # Check Accept headers. If request wants HTML (e.g. from browser), serve the dashboard page
    accept = request.headers.get("accept", "")
    if "text/html" not in accept:
        return {
            "name": "AI Research Intelligence Platform",
            "version": "1.0.0",
            "description": "Production-grade AI research monitoring and analysis system",
            "documentation": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "ready": "/ready",
            "capabilities": "/api/v1/agent/capabilities",
        }

    # Query metrics and data
    items_count = db.query(ResearchItem).count()
    sources_count = db.query(ResearchSource).count()
    trends_count = db.query(Trend).count()

    top_items = (
        db.query(ResearchItem)
        .join(ItemEnrichment)
        .order_by(ItemEnrichment.importance_score.desc())
        .limit(5)
        .all()
    )
    
    # If no enrichments yet, fall back to recent items
    if not top_items:
        top_items = db.query(ResearchItem).order_by(ResearchItem.created_at.desc()).limit(5).all()

    trends = db.query(Trend).order_by(Trend.growth_rate.desc()).limit(5).all()
    sources = db.query(ResearchSource).order_by(ResearchSource.authority_score.desc()).all()
    all_items = db.query(ResearchItem).order_by(ResearchItem.created_at.desc()).limit(15).all()

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "items_count": items_count,
            "sources_count": sources_count,
            "trends_count": trends_count,
            "top_items": top_items,
            "trends": trends,
            "sources": sources,
            "all_items": all_items,
        }
    )


@app.get("/api/v1/info")
async def api_info():
    """Complete API endpoint index."""
    base = "/api/v1"
    return {
        "version": "1.0.0",
        "base_url": base,
        "groups": {
            "research": {
                "items":            f"{base}/research/items",
                "item_detail":      f"{base}/items/{{item_id}}",
                "trending_today":   f"{base}/items/trending/today",
                "high_priority":    f"{base}/items/high-priority",
                "by_category":      f"{base}/items/by-category/{{category}}",
                "trends":           f"{base}/research/trends",
                "emerging_trends":  f"{base}/trends/emerging",
                "search":           f"{base}/search?q=<query>",
            },
            "sources": {
                "list":             f"{base}/sources",
                "get":              f"{base}/sources/{{source_id}}",
                "create":           f"{base}/sources  [POST]",
                "update":           f"{base}/sources/{{source_id}}  [PUT]",
                "patch":            f"{base}/sources/{{source_id}}  [PATCH]",
                "delete":           f"{base}/sources/{{source_id}}  [DELETE]",
                "activate":         f"{base}/sources/{{source_id}}/activate  [POST]",
                "deactivate":       f"{base}/sources/{{source_id}}/deactivate  [POST]",
                "stats":            f"{base}/sources/{{source_id}}/stats",
                "types":            f"{base}/sources/types",
                "bulk":             f"{base}/sources/bulk  [POST]",
            },
            "agent_integration": {
                "capabilities":     f"{base}/agent/capabilities",
                "ingest":           f"{base}/agent/ingest  [POST]",
                "ingest_batch":     f"{base}/agent/ingest/batch  [POST]",
                "query_analyst":    f"{base}/agent/query  [POST]",
                "active_sources":   f"{base}/agent/sources/active",
                "heartbeat":        f"{base}/agent/sources/{{source_id}}/heartbeat  [POST]",
                "webhook_subscribe":f"{base}/agent/webhook/subscribe  [POST]",
                "webhook_list":     f"{base}/agent/webhook",
                "webhook_delete":   f"{base}/agent/webhook/{{wh_id}}  [DELETE]",
            },
            "intelligence": {
                "summary":          f"{base}/intelligence/summary",
                "key_findings":     f"{base}/intelligence/key-findings",
                "analyst_query":    f"{base}/analyst/query  [POST]",
            },
            "dashboard": {
                "metrics":          f"{base}/dashboard/metrics",
                "sources_health":   f"{base}/dashboard/sources-health",
                "summary_stats":    f"{base}/dashboard/summary-stats",
            },
            "market": {
                "startups":         f"{base}/startups",
                "models":           f"{base}/models",
                "gpu_market":       f"{base}/market/gpu",
                "policy_alerts":    f"{base}/policy-alerts",
            },
        },
    }


@app.get("/export/api-docs")
async def export_api_docs_ai():
    """Download a comprehensive AI & Agent integration guide as Markdown."""
    import io
    from fastapi.responses import StreamingResponse as SR

    doc = """# AI Research Intelligence — API Integration Guide
======================================================
Base URL: http://localhost:8002
Swagger UI: http://localhost:8002/docs
OpenAPI JSON: http://localhost:8002/openapi.json
Capabilities: http://localhost:8002/api/v1/agent/capabilities

============================
SECTION 1: FOR AI CODERS
(Cursor, GitHub Copilot, Gemini Code)
============================

When asking an AI assistant to write data pipelines or crawlers that feed this platform,
use the following snippet as context in your system prompt:

## Required Ingestion Schema
```json
{
  "title": "Paper or Article Title",
  "url": "https://source.com/item",
  "abstract": "Brief summary of the content",
  "source_name": "arXiv",
  "content_type": "research_paper",
  "categories": ["llm", "agents", "reasoning"],
  "published_date": "2025-07-01"
}
```

## Submitting Data (Python)
```python
import httpx

payload = {
    "title": "Scaling Reasoning with MCTS",
    "url": "https://arxiv.org/abs/2407.xxxxx",
    "abstract": "We propose a novel approach...",
    "source_name": "arXiv",
    "categories": ["llm", "reasoning"]
}
resp = httpx.post("http://localhost:8002/api/v1/agent/ingest", json=payload)
print(resp.json())
```

## Querying the Analyst (Python)
```python
resp = httpx.post("http://localhost:8002/api/v1/agent/query",
                  json={"question": "What are the latest LLM reasoning advances?", "context_hours": 168})
print(resp.json()["answer"])
```

============================
SECTION 2: FOR AGENT DEVELOPERS
(LangChain, CrewAI, OpenAI Agents, AutoGPT)
============================

## Step 1 — Discover Capabilities on Startup
Run this at agent boot to auto-configure which categories and content types are accepted:
```
GET http://localhost:8002/api/v1/agent/capabilities
```

## Step 2 — Define Tools (LangChain Example)
```python
from langchain.tools import tool
import httpx

BASE = "http://localhost:8002"

@tool
def ingest_research(title: str, url: str, abstract: str, source: str) -> dict:
    \"\"\"Push a new research finding into the AI Research Intelligence Platform.\"\"\"
    return httpx.post(f"{BASE}/api/v1/agent/ingest",
                      json={"title": title, "url": url, "abstract": abstract, "source_name": source}).json()

@tool
def query_analyst(question: str) -> str:
    \"\"\"Ask natural-language questions about AI research. Returns cited, structured answers.\"\"\"
    return httpx.post(f"{BASE}/api/v1/agent/query",
                      json={"question": question, "context_hours": 168}).json().get("answer")

@tool
def get_active_sources() -> list:
    \"\"\"Get the current list of active crawling sources.\"\"\"
    return httpx.get(f"{BASE}/api/v1/agent/sources/active").json()
```

## Step 3 — Subscribe to Webhooks (Real-time Updates)
```python
httpx.post(f"{BASE}/api/v1/agent/webhook/subscribe", json={
    "callback_url": "https://your-agent.example.com/hook",
    "events": ["new_item", "high_priority", "emerging_trend"]
})
```

============================
SECTION 3: COMPLETE API REFERENCE
============================

### Agent APIs
| Method | Endpoint                        | Description                      |
|--------|---------------------------------|----------------------------------|
| GET    | /api/v1/agent/capabilities      | Platform capabilities manifest   |
| POST   | /api/v1/agent/ingest            | Ingest a research item           |
| POST   | /api/v1/agent/ingest/batch      | Bulk ingest up to 100 items      |
| POST   | /api/v1/agent/query             | RAG analyst natural language Q&A |
| GET    | /api/v1/agent/sources/active    | Active source list for crawlers  |
| POST   | /api/v1/agent/webhook/subscribe | Subscribe to real-time events    |
| GET    | /api/v1/agent/webhook           | List your subscriptions          |

### Sources APIs
| Method | Endpoint                                  | Description             |
|--------|-------------------------------------------|-------------------------|
| GET    | /api/v1/sources                           | List all sources        |
| POST   | /api/v1/sources                           | Add a new source        |
| GET    | /api/v1/sources/{id}                      | Get source by ID        |
| PATCH  | /api/v1/sources/{id}                      | Update source fields    |
| DELETE | /api/v1/sources/{id}                      | Remove a source         |
| POST   | /api/v1/sources/{id}/activate             | Enable a source         |
| POST   | /api/v1/sources/{id}/deactivate           | Disable a source        |

### Research APIs
| Method | Endpoint                        | Description                      |
|--------|---------------------------------|----------------------------------|
| GET    | /api/v1/research/items          | List all research items          |
| GET    | /api/v1/research/trends         | Trend detection results          |
| GET    | /api/v1/research/sources        | Research source metadata         |

============================
SECTION 4: EXAMPLE AGENT WORKFLOW
============================

1. Agent boots → calls GET /api/v1/agent/capabilities
2. Crawler scrapes arXiv → calls POST /api/v1/agent/ingest for each paper
3. Agent calls GET /api/v1/research/trends to detect emerging topics
4. Agent calls POST /api/v1/agent/query with business question
5. Webhook fires when high-priority item detected → agent takes action
"""

    buf = io.BytesIO(doc.encode("utf-8"))
    return SR(buf, media_type="text/markdown",
              headers={"Content-Disposition": "attachment; filename=ai_research_api_guide.md"})


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
