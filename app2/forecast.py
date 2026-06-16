from prophet import Prophet
import pandas as pd

from sqlalchemy import text, create_engine
from datetime import datetime

from app.database import SessionLocal

engine = create_engine(
    "postgresql://postgres:12345@localhost:5434/tsdb"
)


def run_forecast():

    db = SessionLocal()

    zones = db.execute(
        text("""
            SELECT DISTINCT zone_id
            FROM zone_load_summary
        """)
    ).fetchall()

    for zone in zones:

        zone_id = zone[0]

        query = f"""
        SELECT
            record_time,
            total_power_kw
        FROM zone_load_summary
        WHERE zone_id = '{zone_id}'
        ORDER BY record_time
        """

        df = pd.read_sql(query, engine)

        if len(df) < 20:
            continue

        df = df.rename(
            columns={
                "record_time": "ds",
                "total_power_kw": "y"
            }
        )

        df["ds"] = pd.to_datetime(
            df["ds"]
        ).dt.tz_localize(None)

        model = Prophet()

        model.fit(df)

        future = model.make_future_dataframe(
            periods=12,
            freq="5min"
        )

        forecast = model.predict(future)

        for row in forecast.tail(12).itertuples():

            db.execute(
                text("""
                INSERT INTO zone_forecast
                (
                    zone_id,
                    forecast_time,
                    predicted_power_kw,
                    created_time
                )
                VALUES
                (
                    :zone_id,
                    :forecast_time,
                    :predicted_power,
                    :created_time
                )
                """),
                {
                    "zone_id": zone_id,
                    "forecast_time": row.ds,
                    "predicted_power": float(row.yhat),
                    "created_time": datetime.utcnow()
                }
            )

    db.commit()
    db.close()

    print("FORECAST COMPLETED")


