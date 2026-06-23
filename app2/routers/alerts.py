from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import SessionLocal
from app.models import AlertTable

router = APIRouter()


# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get All Alerts
@router.get("/")
def get_alerts(
    db: Session = Depends(get_db)
):
    return (
        db.query(AlertTable)
        .order_by(AlertTable.alert_time.desc())
        .all()
    )


# Get Alerts By Zone
@router.get("/{zone_id}")
def get_zone_alerts(
    zone_id: str,
    db: Session = Depends(get_db)
):
    return (
        db.query(AlertTable)
        .filter(AlertTable.zone_id == zone_id)
        .order_by(AlertTable.alert_time.desc())
        .all()
    )


# Optional Raw SQL Endpoint
@router.get("/raw/all")
def alerts_raw():

    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                SELECT *
                FROM alert_table
                ORDER BY alert_time DESC
            """)
        )

        return result.mappings().all()

    finally:
        db.close()