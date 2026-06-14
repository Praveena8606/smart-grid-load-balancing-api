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

    total_current_capacity = Column(Float)

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