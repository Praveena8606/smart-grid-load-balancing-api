from pydantic import BaseModel
from datetime import datetime

class ZoneLoadCreate(BaseModel):

    zone_id: str

    house_id: str

    total_power_kw: float

    avg_voltage: float

    avg_current: float

    record_time: datetime
