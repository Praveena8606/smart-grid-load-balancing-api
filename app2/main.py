from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import ZoneLoadSummary

from app.models import ZoneLoadSummary, ZoneAnalyticsSummary

from app.models import AlertTable

from sqlalchemy import func

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/zone-load/")
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

        return {"message": "Inserted Successfully"}

    except Exception as e:
        return {"error": str(e)}

URL = "http://127.0.0.1:8000/zone-load/"    

@app.get("/zone-load/")
def get_zone_loads(db: Session = Depends(get_db)):
    data = db.query(ZoneLoadSummary).all()
    return data    


@app.get("/zone-load/{zone_id}")
def get_zone(zone_id: str, db: Session = Depends(get_db)):
    return db.query(ZoneLoadSummary)\
             .filter(ZoneLoadSummary.zone_id == zone_id)\
             .all()    

@app.get("/zone-load/{zone_id}/latest")
def get_latest_zone_record(zone_id: str, db: Session = Depends(get_db)):
    return (
        db.query(ZoneLoadSummary)
        .filter(ZoneLoadSummary.zone_id == zone_id)
        .order_by(ZoneLoadSummary.record_time.desc())
        .first()
    )


@app.get("/latest")
def get_latest(db: Session = Depends(get_db)):
    return db.query(ZoneLoadSummary)\
             .order_by(ZoneLoadSummary.record_time.desc())\
             .first()



@app.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    return db.query(ZoneAnalyticsSummary).all()


@app.get("/analytics/{zone_id}/latest")
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


@app.get("/analytics/{zone_id}")
def get_zone_analytics(
    zone_id: str,
    db: Session = Depends(get_db)
):
    return db.query(
        ZoneAnalyticsSummary
    ).filter(
        ZoneAnalyticsSummary.zone_id == zone_id
    ).all()

@app.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):

    return db.query(
        AlertTable
    ).order_by(
        AlertTable.alert_time.desc()
    ).all()


@app.get("/alerts/{zone_id}")
def get_zone_alerts(
    zone_id: str,
    db: Session = Depends(get_db)
):

    return db.query(
        AlertTable
    ).filter(
        AlertTable.zone_id == zone_id
    ).all()


from fastapi import WebSocket

active_connections = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()

    active_connections.append(websocket)

    while True:
        await websocket.receive_text()


import os

DATABASE_URL = os.getenv("DATABASE_URL")

@app.get("/health")
def health():

    return {
        "status": "running"
    }

@app.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):

    total_records = db.query(
        ZoneLoadSummary
    ).count()

    total_zones = db.query(
        ZoneLoadSummary.zone_id
    ).distinct().count()

    total_alerts = db.query(
        AlertTable
    ).count()

    total_analytics = db.query(
        ZoneAnalyticsSummary
    ).count()

    return {
        "total_records": total_records,
        "total_zones": total_zones,
        "total_alerts": total_alerts,
        "total_analytics": total_analytics
    }

# @app.get("/metrics")
# def get_metrics(db: Session = Depends(get_db)):

#     return {
#         "total_records": db.query(ZoneLoadSummary).count(),
#         "total_zones": db.query(
#             ZoneLoadSummary.zone_id
#         ).distinct().count(),
#         "total_alerts": db.query(AlertTable).count(),
#         "latest_record": db.query(
#             ZoneLoadSummary
#         ).order_by(
#             ZoneLoadSummary.record_time.desc()
#         ).first().record_time
#     }
