from sqlalchemy import func, text
from datetime import datetime, timezone

from app.database import SessionLocal

from app.models import (
    ZoneLoadSummary,
    ZoneAnalyticsSummary,
    AlertTable,
    ForecastAnalytics,
    ForecastAlertTable,
    ZoneForecast
)

from app.celery_app import celery

@celery.task
def calculate_forecast_analytics():

    print(
        f"FORECAST ANALYTICS STARTED AT "
        f"{datetime.now(timezone.utc)}"
    )

# ==========================================
# ZONE ANALYTICS
# ==========================================

@celery.task
def calculate_zone_averages():

    print("CALCULATING ZONE ANALYTICS...")

    db = SessionLocal()

    zones = db.query(
        ZoneLoadSummary.zone_id
    ).distinct().all()

    for zone in zones:

        zone_id = zone[0]

        avg_power = db.query(
            func.avg(ZoneLoadSummary.total_power_kw)
        ).filter(
            ZoneLoadSummary.zone_id == zone_id
        ).scalar()

        avg_voltage = db.query(
            func.avg(ZoneLoadSummary.avg_voltage)
        ).filter(
            ZoneLoadSummary.zone_id == zone_id
        ).scalar()

        avg_current = db.query(
            func.avg(ZoneLoadSummary.avg_current)
        ).filter(
            ZoneLoadSummary.zone_id == zone_id
        ).scalar()

        house_count = db.query(
            func.count(
                func.distinct(
                    ZoneLoadSummary.house_id
                )
            )
        ).filter(
            ZoneLoadSummary.zone_id == zone_id
        ).scalar()

        total_current_capacity = house_count * 5

        utilization_percent = (
            (avg_current / total_current_capacity) * 100
            if total_current_capacity > 0
            else 0
        )

        existing = db.query(
            ZoneAnalyticsSummary
        ).filter(
            ZoneAnalyticsSummary.zone_id == zone_id
        ).first()

        if existing:

            existing.avg_power_kw = avg_power
            existing.avg_voltage = avg_voltage
            existing.avg_current = avg_current
            existing.house_count = house_count
            existing.total_current_capacity = total_current_capacity
            existing.utilization_percent = utilization_percent
            existing.calculated_time = datetime.now(
                timezone.utc
            )

        else:

            db.add(
                ZoneAnalyticsSummary(
                    zone_id=zone_id,
                    avg_power_kw=avg_power,
                    avg_voltage=avg_voltage,
                    avg_current=avg_current,
                    house_count=house_count,
                    total_current_capacity=total_current_capacity,
                    utilization_percent=utilization_percent,
                    calculated_time=datetime.now(
                        timezone.utc
                    )
                )
            )

    db.commit()
    db.close()


# ==========================================
# ZONE ALERTS
# ==========================================

@celery.task
def check_zone_alerts():

    print("ZONE ALERT TASK RUNNING...")

    db = SessionLocal()

    zones = db.query(
        ZoneAnalyticsSummary
    ).all()

    for zone in zones:

        if zone.utilization_percent >= 90:

            db.add(
                AlertTable(
                    zone_id=zone.zone_id,
                    avg_current=zone.avg_current,
                    utilization_percent=zone.utilization_percent,
                    alert_message="Current Utilization Above 90%",
                    alert_time=datetime.now(
                        timezone.utc
                    )
                )
            )

            print(
                f"ZONE ALERT -> {zone.zone_id}"
            )

    db.commit()
    db.close()


# ==========================================
# FORECAST GENERATION
# ==========================================

@celery.task
def generate_forecast():

    print("FORECAST TASK RUNNING...")

    from app.forecast import run_forecast

    run_forecast()


# ==========================================
# FORECAST ANALYTICS
# ==========================================

@celery.task
def calculate_forecast_analytics():

    print("CALCULATING FORECAST ANALYTICS...")

    db = SessionLocal()

    zones = db.query(
        ZoneForecast.zone_id
    ).distinct().all()

    for zone in zones:

        zone_id = zone[0]

        avg_forecast_power = db.query(
            func.avg(
                ZoneForecast.predicted_power_kw
            )
        ).filter(
            ZoneForecast.zone_id == zone_id
        ).scalar()

        max_forecast_power = db.query(
            func.max(
                ZoneForecast.predicted_power_kw
            )
        ).filter(
            ZoneForecast.zone_id == zone_id
        ).scalar()

        min_forecast_power = db.query(
            func.min(
                ZoneForecast.predicted_power_kw
            )
        ).filter(
            ZoneForecast.zone_id == zone_id
        ).scalar()

        house_count = db.query(
            func.count(
                func.distinct(
                    ZoneLoadSummary.house_id
                )
            )
        ).filter(
            ZoneLoadSummary.zone_id == zone_id
        ).scalar()

        total_capacity = house_count * 5

        forecast_utilization_percent = (
            (avg_forecast_power / total_capacity) * 100
            if total_capacity > 0
            else 0
        )

        existing = db.query(
            ForecastAnalytics
        ).filter(
            ForecastAnalytics.zone_id == zone_id
        ).first()

        if existing:

            existing.avg_forecast_power = avg_forecast_power
            existing.max_forecast_power = max_forecast_power
            existing.min_forecast_power = min_forecast_power
            existing.house_count = house_count
            existing.total_capacity = total_capacity
            existing.forecast_utilization_percent = (
                forecast_utilization_percent
            )
            existing.calculated_time = datetime.now(
                timezone.utc
            )

        else:

            db.add(
                ForecastAnalytics(
                    zone_id=zone_id,
                    avg_forecast_power=avg_forecast_power,
                    max_forecast_power=max_forecast_power,
                    min_forecast_power=min_forecast_power,
                    house_count=house_count,
                    total_capacity=total_capacity,
                    forecast_utilization_percent=forecast_utilization_percent,
                    calculated_time=datetime.now(
                        timezone.utc
                    )
                )
            )

        print(
            f"{zone_id} | "
            f"AvgForecast={avg_forecast_power:.2f} | "
            f"Capacity={total_capacity} | "
            f"Utilization={forecast_utilization_percent:.2f}%"
        )

        print("COMMITTING FORECAST ANALYTICS")
        db.commit()
        print("COMMIT COMPLETE")

    db.commit()
    db.close()

# ==========================================
# FORECAST ALERTS
# ==========================================

@celery.task
def check_forecast_alerts():

    print("FORECAST ALERT TASK RUNNING...")

    db = SessionLocal()

    rows = db.query(
        ForecastAnalytics
    ).all()

    for row in rows:

        if row.forecast_utilization_percent >= 90:

            db.add(
                ForecastAlertTable(
                    zone_id=row.zone_id,
                    forecast_time=row.calculated_time,
                    predicted_power_kw=row.avg_forecast_power,
                    alert_message="Forecast Utilization Above 90%",
                    created_time=datetime.utcnow()
                )
            )

            print(
                f"FORECAST ALERT -> {row.zone_id}"
            )

    db.commit()
    db.close()