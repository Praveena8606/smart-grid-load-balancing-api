from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import AlertTable
from app.schemas import AlertResponse

router = APIRouter(
    prefix="/alerts",
    tags=["Zone Alerts"]
)


# ==========================================
# GET ALL ALERTS
# ==========================================

@router.get(
    "/",
    response_model=list[AlertResponse]
)
async def get_alerts(
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(

        select(AlertTable)

        .order_by(
            AlertTable.alert_time.desc()
        )

    )

    return result.scalars().all()


# ==========================================
# GET ALERTS BY ZONE
# ==========================================

@router.get(
    "/{zone_id}",
    response_model=list[AlertResponse]
)
async def get_zone_alerts(
    zone_id: str,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(

        select(AlertTable)

        .where(
            AlertTable.zone_id == zone_id
        )

        .order_by(
            AlertTable.alert_time.desc()
        )

    )

    rows = result.scalars().all()

    if not rows:

        raise HTTPException(
            status_code=404,
            detail="No alerts found for this zone"
        )

    return rows


# ==========================================
# GET LATEST ALERT OF ZONE
# ==========================================

@router.get(
    "/{zone_id}/latest",
    response_model=AlertResponse
)
async def get_latest_alert(
    zone_id: str,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(

        select(AlertTable)

        .where(
            AlertTable.zone_id == zone_id
        )

        .order_by(
            AlertTable.alert_time.desc()
        )

    )

    row = result.scalars().first()

    if row is None:

        raise HTTPException(
            status_code=404,
            detail="No alert found for this zone"
        )

    return row