
from pydantic import BaseModel
from datetime import datetime
from datetime import date

class ForecastRequest(BaseModel):

    zone_id:str

    forecast_date:date

    start_time:str

    end_time:str

class ForecastResponse(BaseModel):
    zone_id: str
    forecast_date: date
    predicted_avg_power_kw: float
    avg_power_kw: float
    max_power_kw: float
    min_power_kw: float
    house_count: int
    utilization_percent: float
    historical_power: list[float]


class ZoneLoadCreate(BaseModel):
    zone_id: str
    house_id: str
    avg_power_kw: float
    avg_voltage: float
    avg_current: float
    record_time: datetime    


class ZoneLoadResponse(BaseModel):
    id: int
    zone_id: str
    house_id: str
    avg_power_kw: float
    avg_voltage: float
    avg_current: float
    record_time: datetime

    class Config:
        from_attributes = True


class ForecastAnalyticsResponse(BaseModel):
    id: int
    zone_id: str
    avg_forecast_power: float
    max_forecast_power: float
    min_forecast_power: float
    house_count: int
    total_capacity: float
    forecast_utilization_percent: float
    calculated_time: datetime

    class Config:
        from_attributes = True


class ForecastAlertResponse(BaseModel):
    id: int
    zone_id: str
    forecast_time: datetime
    predicted_avg_power_kw: float
    alert_message: str
    created_time: datetime

    class Config:
        from_attributes = True


class ZoneAnalyticsResponse(BaseModel):
    id: int
    zone_id: str
    avg_power_kw: float
    avg_voltage: float
    avg_current: float
    house_count: int
    total_power_capacity: float
    utilization_percent: float
    calculated_time: datetime

    class Config:
        from_attributes = True       



class AlertResponse(BaseModel):
    id: int
    zone_id: str
    avg_current: float
    utilization_percent: float
    alert_message: str
    alert_time: datetime

    class Config:
        from_attributes = True           