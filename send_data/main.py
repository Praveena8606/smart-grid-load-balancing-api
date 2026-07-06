from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import text

from database import SessionLocal

app = FastAPI()


class ZoneLoad(BaseModel):
    zone_id: str
    house_id: str
    total_power_kw: float
    avg_voltage: float
    avg_current: float
    record_time: datetime


@app.post("/zone-load/")
def insert_data(data: ZoneLoad):

    print("RECEIVED:", data)

    db = SessionLocal()

    query = text("""
        INSERT INTO zone_load_summary
        (
            zone_id,
            house_id,
            total_power_kw,
            avg_voltage,
            avg_current,
            record_time
        )
        VALUES
        (
            :zone_id,
            :house_id,
            :power,
            :voltage,
            :current,
            :time
        )
    """)

    try:

        db.execute(
            query,
            {
                "zone_id": data.zone_id,
                "house_id": data.house_id,
                "power": data.total_power_kw,
                "voltage": data.avg_voltage,
                "current": data.avg_current,
                "time": data.record_time
            }
        )

        db.commit()

        print("DATA SAVED")

    except Exception as e:

        db.rollback()
        print("DB ERROR:", e)

    finally:
        db.close()

    return {"message": "saved"}