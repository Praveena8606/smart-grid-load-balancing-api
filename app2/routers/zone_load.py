from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import ZoneLoadSummary

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/test")
def test():
    return {
        "message": "zone load router working"
    }


@router.post("/")
def create_zone_load(
    data: dict,
    db: Session = Depends(get_db)
):
    try:

        row = ZoneLoadSummary(
            zone_id=data["zone_id"],
            house_id=data["house_id"],
            total_power_kw=data["total_power_kw"],
            avg_voltage=data["avg_voltage"],
            avg_current=data["avg_current"],
            record_time=data["record_time"]
        )

        db.add(row)
        db.commit()
        db.refresh(row)

        return {
            "message": "Inserted Successfully",
            "id": row.id
        }

    except Exception as e:

        db.rollback()

        return {
            "status": "error",
            "message": str(e)
        }


@router.get("/")
def get_zone_loads(
    db: Session = Depends(get_db)
):
    return db.query(
        ZoneLoadSummary
    ).all()


@router.get("/{zone_id}")
def get_zone(
    zone_id: str,
    db: Session = Depends(get_db)
):
    return (
        db.query(ZoneLoadSummary)
        .filter(
            ZoneLoadSummary.zone_id == zone_id
        )
        .all()
    )


@router.get("/{zone_id}/latest")
def get_latest_zone_record(
    zone_id: str,
    db: Session = Depends(get_db)
):
    return (
        db.query(ZoneLoadSummary)
        .filter(
            ZoneLoadSummary.zone_id == zone_id
        )
        .order_by(
            ZoneLoadSummary.record_time.desc()
        )
        .first()
    )


@router.get("/latest/all")
def get_latest(
    db: Session = Depends(get_db)
):
    return (
        db.query(ZoneLoadSummary)
        .order_by(
            ZoneLoadSummary.record_time.desc()
        )
        .first()
    )
