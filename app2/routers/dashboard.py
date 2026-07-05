      
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import (
    ZoneLoadSummary,
    ZoneAnalyticsSummary,
    ForecastAnalytics
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

templates = Jinja2Templates(
    directory="app/templates"
)


# ==========================================
# MAIN DASHBOARD
# ==========================================

@router.get("/")
async def dashboard(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html"
    )


# ==========================================
# GRID OPERATOR DASHBOARD
# ==========================================

@router.get("/grid")
async def grid_dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db)
):

    load_result = await db.execute(

        select(ZoneLoadSummary)

        .order_by(
            ZoneLoadSummary.record_time.desc()
        )

        .limit(20)

    )

    loads = load_result.scalars().all()

    analytics_result = await db.execute(

        select(ZoneAnalyticsSummary)

        .order_by(
            ZoneAnalyticsSummary.zone_id
        )

    )

    analytics = analytics_result.scalars().all()

    return templates.TemplateResponse(
        request=request,
        name="grid_operator.html",
        context={
            "loads": loads,
            "analytics": analytics
        }
    )


# ==========================================
# ENERGY ANALYTICS DASHBOARD
# ==========================================

@router.get("/analytics")
async def energy_analytics(
    request: Request,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(ForecastAnalytics).order_by(
            ForecastAnalytics.zone_id
        )
    )

    analytics = result.scalars().all()

    return templates.TemplateResponse(
        request=request,
        name="energy_analytics.html",
        context={
            "analytics": analytics
        }
    )