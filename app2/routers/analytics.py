from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import SessionLocal
from app.models import ZoneAnalyticsSummary

router = APIRouter()


# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Get All Analytics Records
@router.get("/")
def get_analytics(
    db: Session = Depends(get_db)
):
    return db.query(
        ZoneAnalyticsSummary
    ).all()


# Get Analytics for Specific Zone
@router.get("/{zone_id}")
def get_zone_analytics(
    zone_id: str,
    db: Session = Depends(get_db)
):
    return (
        db.query(ZoneAnalyticsSummary)
        .filter(
            ZoneAnalyticsSummary.zone_id == zone_id
        )
        .all()
    )


# Get Latest Analytics Record for Zone
@router.get("/{zone_id}/latest")
def get_latest_zone_analytics(
    zone_id: str,
    db: Session = Depends(get_db)
):
    return (
        db.query(ZoneAnalyticsSummary)
        .filter(
            ZoneAnalyticsSummary.zone_id == zone_id
        )
        .order_by(
            ZoneAnalyticsSummary.id.desc()
        )
        .first()
    )


# Optional Raw SQL Endpoint
@router.get("/summary/all")
def analytics_summary():

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