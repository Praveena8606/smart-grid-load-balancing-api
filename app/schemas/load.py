from pydantic import BaseModel, Field

class LoadData(BaseModel):
    area: str = Field(..., min_length=2)
    current_load: float = Field(..., gt=0)
    max_capacity: float = Field(..., gt=0)

class LoadResponse(LoadData):
    id: int

    class Config:
        from_attributes = True