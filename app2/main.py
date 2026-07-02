
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.routers import websocket
import asyncio
from app.redis_listener import redis_listener
from app.routers import (
    zone_load,
    analytics,
    alerts,
    forecast,
    dashboard
)

app = FastAPI(
    title="Grid Analytics Platform",
    version="1.0.0"
)

@app.on_event("startup")
async def startup():

    asyncio.create_task(redis_listener())

# Static Files
app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Include Routers
# DO NOT add prefixes here because each router
# already has its own prefix.
# --------------------------------------------------

app.include_router(zone_load.router)
app.include_router(analytics.router)
app.include_router(alerts.router)
app.include_router(dashboard.router)
app.include_router(websocket.router)
app.include_router(forecast.router)



# --------------------------------------------------
# Root
# --------------------------------------------------

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/dashboard/")

# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/health")
async def health():
    return {
        "status": "running"
    }

