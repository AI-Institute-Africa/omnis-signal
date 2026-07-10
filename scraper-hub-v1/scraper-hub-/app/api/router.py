from fastapi import APIRouter

from app.api.routes import health, sources, manual_scrape, records, webhook_targets, delivery_attempts
from app.api.routes import organizations

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(sources.router, prefix="/sources", tags=["sources"])
api_router.include_router(manual_scrape.router, prefix="/manual-scrape", tags=["manual-scrape"])
api_router.include_router(records.router, prefix="/records", tags=["records"])
api_router.include_router(webhook_targets.router, prefix="/webhook-targets", tags=["webhook-targets"])
api_router.include_router(delivery_attempts.router, prefix="/delivery-attempts", tags=["delivery-attempts"])
api_router.include_router(organizations.router)