from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.load import LoadData, LoadResponse
from app.models.load import Load
from app.db.database import get_db

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "healthy"}

@router.post("/load")
def create_load(data: LoadData, db: Session = Depends(get_db)):

    new_load = Load(
        area=data.area,
        current_load=data.current_load,
        max_capacity=data.max_capacity
    )

    db.add(new_load)
    db.commit()
    db.refresh(new_load)

    return {
        "id": new_load.id,
        "area": new_load.area,
        "current_load": new_load.current_load,
        "max_capacity": new_load.max_capacity
    }
@router.get("/loads", response_model=list[LoadResponse])
def get_loads(db: Session = Depends(get_db)):
    loads = db.query(Load).all()
    return loads

@router.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    loads = db.query(Load).all()

    alerts = []

    for load in loads:
        usage_percent = (load.current_load / load.max_capacity) * 100

        if usage_percent > 90:
            alerts.append({
                "area": load.area,
                "current_load": load.current_load,
                "max_capacity": load.max_capacity,
                "usage_percent": round(usage_percent, 2),
                "status": "OVERLOADED"
            })

    return alerts

@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    loads = db.query(Load).all()

    total_sectors = len(loads)

    overloaded_sectors = 0
    total_usage = 0

    for load in loads:
        usage_percent = (load.current_load / load.max_capacity) * 100

        total_usage += usage_percent

        if usage_percent > 90:
            overloaded_sectors += 1

    average_usage = 0

    if total_sectors > 0:
        average_usage = total_usage / total_sectors

    return {
        "total_sectors": total_sectors,
        "overloaded_sectors": overloaded_sectors,
        "average_usage": round(average_usage, 2)
    }

@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    loads = db.query(Load).all()

    total_sectors = len(loads)

    overloaded_sectors = 0
    total_usage = 0

    for load in loads:
        usage_percent = (load.current_load / load.max_capacity) * 100

        total_usage += usage_percent

        if usage_percent > 90:
            overloaded_sectors += 1

    average_usage = 0

    if total_sectors > 0:
        average_usage = total_usage / total_sectors

    return {
        "total_sectors": total_sectors,
        "overloaded_sectors": overloaded_sectors,
        "average_usage": round(average_usage, 2)
    }

@router.get("/grid-status")
def get_grid_status(db: Session = Depends(get_db)):
    loads = db.query(Load).all()

    total_sectors = len(loads)
    overloaded = 0

    for load in loads:
        usage_percent = (load.current_load / load.max_capacity) * 100

        if usage_percent > 90:
            overloaded += 1

    if total_sectors == 0:
        return {
            "grid_status": "NO DATA"
        }

    if overloaded == 0:
        status = "HEALTHY"
    elif overloaded < total_sectors:
        status = "WARNING"
    else:
        status = "CRITICAL"

    return {
        "grid_status": status,
        "total_sectors": total_sectors,
        "overloaded_sectors": overloaded
    }

@router.get("/prediction")
def get_prediction(db: Session = Depends(get_db)):
    loads = db.query(Load).all()

    predictions = []

    for load in loads:
        predicted_load = load.current_load * 1.10

        predictions.append({
            "area": load.area,
            "current_load": load.current_load,
            "predicted_load": round(predicted_load, 2)
        })

    return predictions

@router.get("/recommendations")
def get_recommendations(db: Session = Depends(get_db)):
    loads = db.query(Load).all()

    recommendations = []

    for load in loads:
        usage_percent = (load.current_load / load.max_capacity) * 100

        if usage_percent > 90:
            action = "Reduce load immediately"
        elif usage_percent > 70:
            action = "Monitor closely"
        else:
            action = "Normal operation"

        recommendations.append({
            "area": load.area,
            "usage_percent": round(usage_percent, 2),
            "recommendation": action
        })

    return recommendations