import sys
import asyncio

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api.router import api_router
from app.api.v2.router import api_v2_router
from app.web.router import router as web_router
from app.config import settings
from app.scheduler import start_scheduler, stop_scheduler
import atexit

app = FastAPI(
    title=settings.APP_NAME,
    description="Scraper Hub API",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Register custom Jinja2 filters
import json as _json
templates.env.filters["from_json"] = lambda v: _json.loads(v) if v else []

app.include_router(api_router, prefix="/api/v1")
app.include_router(api_v2_router, prefix="/api/v2")
app.include_router(web_router)

@app.on_event("startup")
async def startup_event():
    if settings.APP_ENV == "test" or getattr(app.state, "testing", False):
        return
    try:
        start_scheduler()
    except Exception as e:
        print(f"Warning: Scheduler failed to start: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    try:
        stop_scheduler()
    except Exception as e:
        print(f"Warning: Scheduler failed to stop: {e}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}