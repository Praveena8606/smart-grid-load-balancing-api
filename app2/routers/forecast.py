from fastapi import APIRouter
from sqlalchemy import text
from app.database import SessionLocal

router = APIRouter()

@router.get("/forecast-analytics")
def forecast_analytics():

    db = SessionLocal()

    try:
        result = db.execute(
            text("""
            SELECT *
            FROM forecast_analytics
            """)
        )

        return result.mappings().all()

    finally:
        db.close()


@router.get("/forecast-alerts")
def forecast_alerts():

    db = SessionLocal()

    try:
        result = db.execute(
            text("""
            SELECT *
            FROM forecast_alert_table
            ORDER BY created_time DESC
            """)
        )

        return result.mappings().all()

    finally:
        db.close()

from fastapi import APIRouter
from sqlalchemy import text

from app.database import SessionLocal

router = APIRouter()

@router.get("/analytics")
def forecast_analytics():

    db = SessionLocal()

    result = db.execute(
        text("""
        SELECT *
        FROM forecast_analytics
        """)
    )

    return result.mappings().all()


@router.get("/alerts")
def forecast_alerts():

    db = SessionLocal()

    result = db.execute(
        text("""
        SELECT *
        FROM forecast_alert_table
        ORDER BY created_time DESC
        """)
    )

    return result.mappings().all()        