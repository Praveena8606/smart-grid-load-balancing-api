from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    zone_load.router,
    prefix="/zone-load",
    tags=["Zone Load"]
)

app.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Analytics"]
)

app.include_router(
    alerts.router,
    prefix="/alerts",
    tags=["Alerts"]
)

app.include_router(
    forecast.router,
    prefix="/forecast",
    tags=["Forecast"]
)

app.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["Dashboard"]
)

@app.get("/health")
def health():
    return {"status": "running"}