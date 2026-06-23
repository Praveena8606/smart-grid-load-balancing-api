from fastapi import APIRouter
from sqlalchemy import text

from app.database import SessionLocal

router = APIRouter()

@router.get("/dashboard-summary")
def dashboard_summary():

    db = SessionLocal()

    zone_count = db.execute(
        text("""
        SELECT COUNT(DISTINCT zone_id)
        FROM zone_analytics_summary
        """)
    ).scalar()

    alert_count = db.execute(
        text("""
        SELECT COUNT(*)
        FROM alert_table
        """)
    ).scalar()

    forecast_alert_count = db.execute(
        text("""
        SELECT COUNT(*)
        FROM forecast_alert_table
        """)
    ).scalar()

    return {
        "zones": zone_count,
        "alerts": alert_count,
        "forecast_alerts": forecast_alert_count
    }




@router.get("/zone-analytics")
def get_zone_analytics():

    db = SessionLocal()

    try:
        result = db.execute(
            text("""
            SELECT *
            FROM zone_analytics_summary
            """)
        )

        return result.mappings().all()

    finally:
        db.close()

from fastapi import APIRouter
from sqlalchemy import text

from app.database import SessionLocal

router = APIRouter()

@router.get("/metrics")
def dashboard_metrics():

    db = SessionLocal()

    result = db.execute(
        text("""
        SELECT
            (SELECT COUNT(*) FROM zone_load_summary) AS total_records,
            (SELECT COUNT(DISTINCT zone_id) FROM zone_load_summary) AS total_zones,
            (SELECT COUNT(*) FROM alert_table) AS total_alerts,
            (SELECT COUNT(*) FROM forecast_alert_table) AS forecast_alerts
        """)
    )

    return result.mappings().first()        