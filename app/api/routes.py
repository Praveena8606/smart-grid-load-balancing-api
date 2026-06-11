from fastapi import APIRouter
from app.schemas.load import LoadData

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "healthy"}

@router.post("/load")
def create_load(data: LoadData):
    return {
        "area": data.area,
        "current_load": data.current_load,
        "max_capacity": data.max_capacity
    }