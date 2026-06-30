from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime

Base = declarative_base()    

class ZoneLoadSummary(Base):

    __tablename__ = "zone_load_summary"

    id = Column(Integer, primary_key=True)

    zone_id = Column(String(50))

    house_id = Column(String(50))

    total_power_kw = Column(Float)

    avg_voltage = Column(Float)

    avg_current = Column(Float)

    record_time = Column(DateTime)


class ZoneAnalyticsSummary(Base):

    __tablename__ = "zone_analytics_summary"

    id = Column(Integer, primary_key=True)

    zone_id = Column(String(50), unique=True)

    avg_power_kw = Column(Float)

    avg_voltage = Column(Float)

    avg_current = Column(Float)

    house_count = Column(Integer)

    total_power_capacity = Column(Float)

    utilization_percent = Column(Float)

    calculated_time = Column(DateTime(timezone=True))


class AlertTable(Base):

    __tablename__ = "alert_table"

    id = Column(Integer, primary_key=True)

    zone_id = Column(String(50))

    avg_current = Column(Float)

    utilization_percent = Column(Float)

    alert_message = Column(String(255))

    alert_time = Column(DateTime(timezone=True))



class ForecastAlertTable(Base):

    __tablename__ = "forecast_alert_table"

    id = Column(Integer, primary_key=True, index=True)

    zone_id = Column(String)

    forecast_time = Column(DateTime)

    predicted_power_kw = Column(Float)

    alert_message = Column(String)

    created_time = Column(DateTime)



class ForecastAnalytics(Base):

    __tablename__ = "forecast_analytics"

    id = Column(Integer, primary_key=True)

    zone_id = Column(String)

    avg_forecast_power = Column(Float)

    max_forecast_power = Column(Float)

    min_forecast_power = Column(Float)

    house_count = Column(Integer)

    total_capacity = Column(Float)

    forecast_utilization_percent = Column(Float)

    calculated_time = Column(DateTime(timezone=True))


class ZoneForecast(Base):

    __tablename__ = "zone_forecast"

    id = Column(Integer, primary_key=True)

    zone_id = Column(String(50))

    forecast_time = Column(DateTime)

    predicted_power_kw = Column(Float)

    created_time = Column(DateTime)
