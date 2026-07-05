
from fastapi import APIRouter, HTTPException , Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy import select, func, and_

from app.models import (
    ForecastAnalytics,
    ForecastAlertTable,
    ZoneLoadSummary
)

from app.schemas import (
    ForecastRequest,
    ForecastAnalyticsResponse,
    ForecastAlertResponse
)

router = APIRouter(
    prefix="/forecast",
    tags=["Forecast"]
)


# ==========================================
# FORECAST ANALYTICS
# ==========================================

@router.get(
    "/analytics",
    response_model=list[ForecastAnalyticsResponse]
)


async def get_forecast_analytics(
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(

        select(ForecastAnalytics)

        .order_by(
            ForecastAnalytics.calculated_time.desc()
        )

    )

    return result.scalars().all()

# ==========================================
# FORECAST ANALYTICS BY ZONE
# ==========================================


@router.get(
    "/analytics/{zone_id}",
    response_model=list[ForecastAnalyticsResponse]
)
async def get_zone_forecast_analytics(
    zone_id: str,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(

        select(ForecastAnalytics)

        .where(
            ForecastAnalytics.zone_id == zone_id
        )

        .order_by(
            ForecastAnalytics.calculated_time.desc()
        )

    )

    rows = result.scalars().all()

    if not rows:

        raise HTTPException(
            status_code=404,
            detail="Forecast Analytics Not Found"
        )

    return rows

# ==========================================
# LATEST FORECAST ANALYTICS
# ==========================================

@router.get(
    "/analytics/{zone_id}/latest",
    response_model=ForecastAnalyticsResponse
)
async def get_latest_forecast(
    zone_id: str,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(

        select(ForecastAnalytics)

        .where(
            ForecastAnalytics.zone_id == zone_id
        )

        .order_by(
            ForecastAnalytics.calculated_time.desc()
        )

    )

    row = result.scalars().first()

    if row is None:

        raise HTTPException(
            status_code=404,
            detail="Forecast Analytics Not Found"
        )

    return row


# ==========================================
# FORECAST ALERTS
# ==========================================

@router.get(
    "/alerts",
    response_model=list[ForecastAlertResponse]
)
async def get_forecast_alerts(
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(

        select(ForecastAlertTable)

        .order_by(
            ForecastAlertTable.created_time.desc()
        )

    )

    return result.scalars().all()


# ==========================================
# FORECAST ALERTS BY ZONE
# ==========================================

@router.post("/generate")
async def generate_forecast(
    request: ForecastRequest,
    db: AsyncSession = Depends(get_db)
):

    # -----------------------------------------
    # Time
    # -----------------------------------------

    start_datetime = datetime.strptime(
        f"{request.forecast_date} {request.start_time}",
        "%Y-%m-%d %H:%M"
    )

    end_datetime = start_datetime + timedelta(hours=1)

    forecast_points = 12

    # -----------------------------------------
    # Fetch latest 600 rows of selected zone
    # -----------------------------------------

    result = await db.execute(

        select(ZoneLoadSummary)

        .where(
            ZoneLoadSummary.zone_id == request.zone_id
        )

        .order_by(
            ZoneLoadSummary.record_time.desc()
        )

    )

    history = result.scalars().all()

    if not history:

        raise HTTPException(
            status_code=404,
            detail="No historical data found."
        )

    # =====================================================
    # Latest reading of every house
    # =====================================================

    latest_subquery = (

        select(

            ZoneLoadSummary.house_id,

            func.max(
                ZoneLoadSummary.record_time
            ).label("latest_time")

        )

        .where(
            ZoneLoadSummary.zone_id == request.zone_id
        )

        .group_by(
            ZoneLoadSummary.house_id
        )

    ).subquery()

    result = await db.execute(

        select(ZoneLoadSummary)

        .join(

            latest_subquery,

            and_(

                ZoneLoadSummary.house_id ==
                latest_subquery.c.house_id,

                ZoneLoadSummary.record_time ==
                latest_subquery.c.latest_time

            )

        )

        .where(
            ZoneLoadSummary.zone_id == request.zone_id
        )

    )

    latest_rows = result.scalars().all()

    # =====================================================
    # Current Zone Statistics
    # =====================================================

    house_count = len(latest_rows)

    total_power = sum(
        row.avg_power_kw
        for row in latest_rows
    )

    avg_power = (
        total_power / house_count
        if house_count else 0
    )

    avg_voltage = (
        sum(row.avg_voltage for row in latest_rows)
        / house_count
        if house_count else 0
    )

    avg_current = (
        sum(row.avg_current for row in latest_rows)
        / house_count
        if house_count else 0
    )

    total_power_capacity = house_count * 5

    utilization_percent = (

        total_power /
        total_power_capacity

    ) * 100 if total_power_capacity else 0

    # =====================================================
    # Historical Zone Average Power
    # =====================================================

    history_by_time = defaultdict(list)

    for row in history:

        key = row.record_time.replace(
            second=0,
            microsecond=0
        )

        history_by_time[key].append(
            row.avg_power_kw
        )

    powers = []

    for timestamp in sorted(

        history_by_time.keys(),

        reverse=True

    ):

        values = history_by_time[timestamp]

        powers.append(
            sum(values) / len(values)
        )

    powers = powers[:12]

    if len(powers) > 1:

        changes = []

        for i in range(len(powers)-1):

            changes.append(
                powers[i] - powers[i+1]
            )

        avg_change = (
            sum(changes) /
            len(changes)
        )

    else:

        avg_change = 0

    last_power = powers[0]

    # =====================================================
    # Forecast
    # =====================================================

    forecast = []

    for i in range(forecast_points):

        forecast_time = start_datetime + timedelta(
            minutes=i*5
        )

        last_power += avg_change

        predicted_avg_power = max(
            last_power,
            0
        )

        predicted_total_power = (
            predicted_avg_power *
            house_count
        )

        predicted_utilization = (

            predicted_total_power /

            total_power_capacity

        ) * 100 if total_power_capacity else 0

        forecast.append({

            "time":
            forecast_time.strftime("%H:%M"),

            "predicted_avg_power_kw":
            round(predicted_avg_power,2),

            "predicted_total_power_kw":
            round(predicted_total_power,2),

            "utilization_percent":
            round(predicted_utilization,0),

            "avg_voltage":
            round(avg_voltage,2),

            "avg_current":
            round(avg_current,2)

        })

    # =====================================================
    # Response
    # =====================================================

    return {

        "zone_id": request.zone_id,

        "forecast_date":
        str(request.forecast_date),

        "start_time":
        request.start_time,

        "end_time":
        end_datetime.strftime("%H:%M"),

        "house_count":
        house_count,

        "total_power_kw":
        round(total_power,2),

        "avg_power_kw":
        round(avg_power,2),

        "avg_voltage":
        round(avg_voltage,2),

        "avg_current":
        round(avg_current,2),

        "total_power_capacity":
        round(total_power_capacity,2),

        "utilization_percent":
        round(utilization_percent,2),

        "forecast":
        forecast

    }