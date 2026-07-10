from fastapi import APIRouter
from app.api.v2.routes import market_data

api_v2_router = APIRouter()
api_v2_router.include_router(market_data.router, prefix="/market-data", tags=["Market Data (v2)"])
