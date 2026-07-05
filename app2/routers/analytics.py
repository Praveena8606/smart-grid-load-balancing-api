from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import ZoneAnalyticsSummary
from app.schemas import ZoneAnalyticsResponse

router = APIRouter(
    prefix="/analytics",
    tags=["Zone Analytics"]
)


# ==========================================
# GET ALL ANALYTICS
# ==========================================

@router.get(
    "/",
    response_model=list[ZoneAnalyticsResponse]
)
async def get_analytics(
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(

        select(ZoneAnalyticsSummary)

        .order_by(
            ZoneAnalyticsSummary.calculated_time.desc()
        )

    )

    return result.scalars().all()


# ==========================================
# GET ANALYTICS BY ZONE
# ==========================================

@router.get(
    "/{zone_id}",
    response_model=list[ZoneAnalyticsResponse]
)
async def get_zone_analytics(
    zone_id: str,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(

        select(ZoneAnalyticsSummary)

        .where(
            ZoneAnalyticsSummary.zone_id == zone_id
        )

        .order_by(
            ZoneAnalyticsSummary.calculated_time.desc()
        )

    )

    rows = result.scalars().all()

    if not rows:

        raise HTTPException(
            status_code=404,
            detail="Zone Analytics Not Found"
        )

    return rows


# ==========================================
# GET LATEST ANALYTICS OF ZONE
# ==========================================

@router.get(
    "/{zone_id}/latest",
    response_model=ZoneAnalyticsResponse
)
async def get_latest_zone_analytics(
    zone_id: str,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(

        select(ZoneAnalyticsSummary)

        .where(
            ZoneAnalyticsSummary.zone_id == zone_id
        )

        .order_by(
            ZoneAnalyticsSummary.calculated_time.desc()
        )

    )

    row = result.scalars().first()

    if row is None:

        raise HTTPException(
            status_code=404,
            detail="Zone Analytics Not Found"
        )

    return row