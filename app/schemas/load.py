from pydantic import BaseModel

class LoadData(BaseModel):
    area: str
    current_load: float
    max_capacity: float