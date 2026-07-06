
from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from app.database import Base, sync_engine
from app.redis_listener import redis_listener

# Import models
from app.models import (
    ZoneLoadSummary,
    ZoneAnalyticsSummary,
    AlertTable
)

# Routers
from app.routers import (
    zone_load,
    analytics,
    alerts,
    dashboard,
    websocket,
    forecast
)


# ==========================================
# Application Startup / Shutdown
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    print("================================")
    print("Starting Grid Analytics Platform")
    print("================================")

    # Create Tables
    Base.metadata.create_all(bind=sync_engine)

    print("Database Ready")

    # Start Redis Listener
    asyncio.create_task(redis_listener())

    print("Redis Listener Started")

    yield

    print("Application Stopped")


# ==========================================
# FastAPI
# ==========================================

app = FastAPI(
    title="Grid Analytics Platform",
    version="1.0.0",
    lifespan=lifespan
)

# ==========================================
# Static Files
# ==========================================

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)

# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# Routers
# ==========================================

app.include_router(zone_load.router)
app.include_router(analytics.router)
app.include_router(alerts.router)
app.include_router(dashboard.router)
app.include_router(websocket.router)
app.include_router(forecast.router)

# ==========================================
# Root
# ==========================================

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/dashboard/")

# ==========================================
# Health Check
# ==========================================

@app.get("/health")
async def health():
    return {
        "status": "running"
    }