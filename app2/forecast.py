from prophet import Prophet
import pandas as pd

from sqlalchemy import text, create_engine
from datetime import datetime

from app.database import SessionLocal
from app.models import ForecastAlertTable

engine = create_engine(
    "postgresql://postgres:12345@localhost:5433/tsdb"
)


def run_forecast():

    print("FORECAST TASK RUNNING...")

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
            avg_power_kw
        FROM zone_load_summary
        WHERE zone_id = '{zone_id}'
        ORDER BY record_time
        """

        df = pd.read_sql(query, engine)

        # Prophet needs enough data
        if len(df) < 20:
            print(f"Skipping {zone_id} - not enough data")
            continue

        df = df.rename(
            columns={
                "record_time": "ds",
                "avg_power_kw": "y"
            }
        )

        df["ds"] = pd.to_datetime(
            df["ds"]
        ).dt.tz_localize(None)

        model = Prophet()

        model.fit(df)

        future = model.make_future_dataframe(
            periods=1,
            freq="5min"
        )

        forecast = model.predict(future)

        row = forecast.tail(1).iloc[0]

        predicted_total_power  = float(row["yhat"])

        # Store forecast
        db.execute(
            text("""
            INSERT INTO zone_forecast
            (
                zone_id,
                forecast_time,
                predicted_total_power _kw,
                created_time
            )
            VALUES
            (
                :zone_id,
                :forecast_time,
                :ppredicted_total_power ,
                :created_time
            )
            """),
            {
                "zone_id": zone_id,
                "forecast_time": row["ds"],
                "predicted_total_power ": predicted_total_power ,
                "created_time": datetime.utcnow()
            }
        )

        # Forecast Alert
        if predicted_total_power  > 135:

            db.add(
                ForecastAlertTable(
                    zone_id=zone_id,
                    forecast_time=row["ds"],
                    predicted_avg_power_kw=predicted_total_power ,
                    alert_message="Forecasted Power Above Threshold",
                    created_time=datetime.utcnow()
                )
            )

            print(
                f"FORECAST ALERT -> {zone_id} | "
                f"Predicted Power = {predicted_total_power }"
            )

        print(
            f"{zone_id} Forecast = "
            f"{round(predicted_total_power, 2)} kW"
        )

    db.commit()
    db.close()

    print("FORECAST COMPLETED")

