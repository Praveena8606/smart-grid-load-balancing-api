from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import ZoneLoadSummary
from app.schemas import (
    ZoneLoadCreate,
    ZoneLoadResponse
)

router = APIRouter(
    prefix="/zone-load",
    tags=["Zone Load"]
)


# ==========================================
# TEST API
# ==========================================

@router.get("/test")
async def test():
    return {
        "message": "Zone Load Router Working Successfully"
    }


# ==========================================
# INSERT NEW RECORD
# ==========================================

@router.post(
    "/",
    response_model=ZoneLoadResponse,
    status_code=201
)
async def create_zone_load(
    data: ZoneLoadCreate,
    db: AsyncSession = Depends(get_db)
):

    row = ZoneLoadSummary(
        zone_id=data.zone_id,
        house_id=data.house_id,
        avg_power_kw=data.avg_power_kw,
        avg_voltage=data.avg_voltage,
        avg_current=data.avg_current,
        record_time=data.record_time
    )

    db.add(row)

    await db.commit()

    await db.refresh(row)

    return row


# ==========================================
# GET ALL RECORDS
# ==========================================

@router.get(
    "/",
    response_model=list[ZoneLoadResponse]
)
async def get_zone_loads(
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(

        select(ZoneLoadSummary)

        .order_by(
            ZoneLoadSummary.record_time.desc()
        )

    )

    return result.scalars().all()


# ==========================================
# GET RECORDS BY ZONE
# ==========================================

@router.get(
    "/{zone_id}",
    response_model=list[ZoneLoadResponse]
)
async def get_zone(
    zone_id: str,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(

        select(ZoneLoadSummary)

        .where(
            ZoneLoadSummary.zone_id == zone_id
        )

        .order_by(
            ZoneLoadSummary.record_time.desc()
        )

    )

    rows = result.scalars().all()

    if not rows:

        raise HTTPException(
            status_code=404,
            detail="Zone not found"
        )

    return rows


# ==========================================
# GET LATEST RECORD OF ZONE
# ==========================================

@router.get(
    "/{zone_id}/latest",
    response_model=ZoneLoadResponse
)
async def get_latest_zone_record(
    zone_id: str,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(

        select(ZoneLoadSummary)

        .where(
            ZoneLoadSummary.zone_id == zone_id
        )

        .order_by(
            ZoneLoadSummary.record_time.desc()
        )

    )

    row = result.scalars().first()

    if row is None:

        raise HTTPException(
            status_code=404,
            detail="Zone not found"
        )

    return row


# ==========================================
# GET LATEST RECORD OF ALL ZONES
# ==========================================

@router.get(
    "/latest/all",
    response_model=ZoneLoadResponse
)
async def get_latest(
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(

        select(ZoneLoadSummary)

        .order_by(
            ZoneLoadSummary.record_time.desc()
        )

    )

    row = result.scalars().first()

    if row is None:

        raise HTTPException(
            status_code=404,
            detail="No records found"
        )

    return row