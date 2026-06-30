from sqlalchemy import func, text
from datetime import datetime, timezone
import asyncio
from app.websocket_manager import manager
from app.database import SessionLocal
from app.celery_app import celery
import json
import redis

from app.models import (
    ZoneLoadSummary,
    ZoneAnalyticsSummary,
    AlertTable,
    ForecastAnalytics,
    ForecastAlertTable,
    ZoneForecast
)

r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)



@celery.task
def calculate_zone_averages():

    print("CALCULATING ZONE ANALYTICS...")

    db = SessionLocal()

    try:

        zones = db.query(
            ZoneLoadSummary.zone_id
        ).distinct().all()

        for zone in zones:

            zone_id = zone[0]

            # Average Power
            avg_power = (
                db.query(func.avg(ZoneLoadSummary.total_power_kw))
                .filter(ZoneLoadSummary.zone_id == zone_id)
                .scalar()
            ) or 0

            # Average Voltage
            avg_voltage = (
                db.query(func.avg(ZoneLoadSummary.avg_voltage))
                .filter(ZoneLoadSummary.zone_id == zone_id)
                .scalar()
            ) or 0

            # Average Current
            avg_current = (
                db.query(func.avg(ZoneLoadSummary.avg_current))
                .filter(ZoneLoadSummary.zone_id == zone_id)
                .scalar()
            ) or 0

            # House Count
            house_count = (
                db.query(
                    func.count(
                        func.distinct(ZoneLoadSummary.house_id)
                    )
                )
                .filter(ZoneLoadSummary.zone_id == zone_id)
                .scalar()
            ) or 0

            # Each house = 5 kW
            total_power_capacity = house_count * 5

            # POWER BASED UTILIZATION
            utilization_percent = (
                (avg_power / total_power_capacity) * 100
                if total_power_capacity > 0
                else 0
            )

            existing = (
                db.query(ZoneAnalyticsSummary)
                .filter(
                    ZoneAnalyticsSummary.zone_id == zone_id
                )
                .first()
            )

            if existing:

                existing.avg_power_kw = avg_power
                existing.avg_voltage = avg_voltage
                existing.avg_current = avg_current
                existing.house_count = house_count

                # Store power capacity
                existing.total_power_capacity = total_power_capacity

                existing.utilization_percent = utilization_percent
                existing.calculated_time = datetime.now(timezone.utc)

            else:

                existing = ZoneAnalyticsSummary(

                    zone_id=zone_id,

                    avg_power_kw=avg_power,

                    avg_voltage=avg_voltage,

                    avg_current=avg_current,

                    house_count=house_count,

                    total_power_capacity=total_power_capacity,

                    utilization_percent=utilization_percent,

                    calculated_time=datetime.now(timezone.utc)

                )

                db.add(existing)

            db.commit()
            db.refresh(existing)

            data = {

                "type": "grid_update",

                "zone_id": existing.zone_id,

                "avg_power_kw": float(existing.avg_power_kw),

                "avg_voltage": float(existing.avg_voltage),

                "avg_current": float(existing.avg_current),

                "house_count": existing.house_count,

                "total_power_capacity": float(existing.total_power_capacity),

                "utilization_percent": float(existing.utilization_percent),

                "calculated_time": existing.calculated_time.strftime(
                    "%d-%m-%Y %H:%M:%S"
                )

            }

            r.publish(
                "grid_updates",
                json.dumps(data)
            )

            print(f"Published Grid Update -> {zone_id}")

    except Exception as e:

        db.rollback()

        print("Zone Analytics Error:", e)

    finally:

        db.close()

    print("ZONE ANALYTICS COMPLETED")


# ==========================================
# ZONE ALERTS
# ==========================================
@celery.task
def check_zone_alerts():

    print("ZONE ALERT TASK RUNNING...")

    db = SessionLocal()

    try:

        zones = db.query(ZoneAnalyticsSummary).all()

        for zone in zones:

            if zone.utilization_percent >= 90:

                # Save alert
                db.add(
                    AlertTable(
                        zone_id=zone.zone_id,
                        avg_current=zone.avg_current,
                        utilization_percent=zone.utilization_percent,
                        alert_message="Current Utilization Above 90%",
                        alert_time=datetime.now(timezone.utc)
                    )
                )

                db.commit()

                data = {
                    "type": "zone",
                    "zone": zone.zone_id,
                    "utilization": round(
                        float(zone.utilization_percent), 2
                    ),
                    "message": "Current Utilization Above 90%"
                }

                try:

                    r.publish(
                        "grid_updates",
                        json.dumps(data)
                    )

                    print(
                        f"Zone Alert Published -> {zone.zone_id}"
                    )

                except Exception as redis_error:

                    print(
                        "Redis Publish Error:",
                        redis_error
                    )

    except Exception as db_error:

        db.rollback()

        print(
            "Zone Alert Database Error:",
            db_error
        )

    finally:

        db.close()

    print("ZONE ALERT TASK COMPLETED")



# @celery.task
# def generate_forecast():

#     print("GENERATING FORECAST...")

#     db = SessionLocal()

#     try:

#         zones = db.query(
#             ZoneLoadSummary.zone_id
#         ).distinct().all()

#         for zone in zones:

#             zone_id = zone[0]

#             avg_power = (
#                 db.query(func.avg(ZoneLoadSummary.total_power_kw))
#                 .filter(
#                     ZoneLoadSummary.zone_id == zone_id
#                 )
#                 .scalar()
#             )

#             if avg_power is None:
#                 continue

#             # Example forecast (+10%)
#             predicted_power = avg_power * 1.10

#             existing = (
#                 db.query(ZoneForecast)
#                 .filter(
#                     ZoneForecast.zone_id == zone_id
#                 )
#                 .first()
#             )

#             if existing:

#                 existing.predicted_power_kw = predicted_power
#                 existing.forecast_time = datetime.now(timezone.utc)

#             else:

#                 db.add(
#                     ZoneForecast(
#                         zone_id=zone_id,
#                         predicted_power_kw=predicted_power,
#                         forecast_time=datetime.now(timezone.utc),
#                         created_time=datetime.now(timezone.utc)
#                     )
#                 )

#         db.commit()

#         print("FORECAST GENERATED SUCCESSFULLY")

#     except Exception as e:

#         db.rollback()
#         print("Forecast Generation Error:", e)

#     finally:

#         db.close()


# # ==========================================
# # FORECAST ANALYTICS
# # ==========================================
# @celery.task
# def calculate_forecast_analytics():

#     print("CALCULATING FORECAST ANALYTICS...")

#     db = SessionLocal()

#     try:

#         zones = db.query(
#             ZoneForecast.zone_id
#         ).distinct().all()

#         for zone in zones:

#             zone_id = zone[0]

#             # Average Forecast Power
#             avg_forecast_power = (
#                 db.query(
#                     func.avg(ZoneForecast.predicted_power_kw)
#                 )
#                 .filter(ZoneForecast.zone_id == zone_id)
#                 .scalar()
#             )

#             # Maximum Forecast Power
#             max_forecast_power = (
#                 db.query(
#                     func.max(ZoneForecast.predicted_power_kw)
#                 )
#                 .filter(ZoneForecast.zone_id == zone_id)
#                 .scalar()
#             )

#             # Minimum Forecast Power
#             min_forecast_power = (
#                 db.query(
#                     func.min(ZoneForecast.predicted_power_kw)
#                 )
#                 .filter(ZoneForecast.zone_id == zone_id)
#                 .scalar()
#             )

#             # House Count
#             house_count = (
#                 db.query(
#                     func.count(
#                         func.distinct(ZoneLoadSummary.house_id)
#                     )
#                 )
#                 .filter(
#                     ZoneLoadSummary.zone_id == zone_id
#                 )
#                 .scalar()
#             )

#             total_capacity = house_count * 5

#             forecast_utilization_percent = (
#                 (avg_forecast_power / total_capacity) * 100
#                 if total_capacity > 0
#                 else 0
#             )

#             existing = (
#                 db.query(ForecastAnalytics)
#                 .filter(
#                     ForecastAnalytics.zone_id == zone_id
#                 )
#                 .first()
#             )

#             if existing:

#                 existing.avg_forecast_power = avg_forecast_power
#                 existing.max_forecast_power = max_forecast_power
#                 existing.min_forecast_power = min_forecast_power
#                 existing.house_count = house_count
#                 existing.total_capacity = total_capacity
#                 existing.forecast_utilization_percent = (
#                     forecast_utilization_percent
#                 )
#                 existing.calculated_time = datetime.now(
#                     timezone.utc
#                 )

#             else:

#                 existing = ForecastAnalytics(
#                     zone_id=zone_id,
#                     avg_forecast_power=avg_forecast_power,
#                     max_forecast_power=max_forecast_power,
#                     min_forecast_power=min_forecast_power,
#                     house_count=house_count,
#                     total_capacity=total_capacity,
#                     forecast_utilization_percent=forecast_utilization_percent,
#                     calculated_time=datetime.now(timezone.utc)
#                 )

#                 db.add(existing)

#             # Save
#             db.commit()

#             # Reload latest row
#             updated_row = (
#                 db.query(ForecastAnalytics)
#                 .filter(
#                     ForecastAnalytics.zone_id == zone_id
#                 )
#                 .first()
#             )

#             # Publish to Redis
#             data = {
#                 "type": "forecast_update",
#                 "zone_id": updated_row.zone_id,
#                 "avg_forecast_power": float(updated_row.avg_forecast_power),
#                 "max_forecast_power": float(updated_row.max_forecast_power),
#                 "min_forecast_power": float(updated_row.min_forecast_power),
#                 "house_count": updated_row.house_count,
#                 "forecast_utilization_percent": float(
#                     updated_row.forecast_utilization_percent
#                 ),
#                 "calculated_time": updated_row.calculated_time.strftime(
#                     "%d-%m-%Y %H:%M:%S"
#                 )
#             }

#             r.publish(
#                 "forecast_updates",
#                 json.dumps(data)
#             )

#             print(
#                 f"Forecast Update Published -> {zone_id}"
#             )

#             print(
#                 f"{zone_id} | "
#                 f"Avg={updated_row.avg_forecast_power:.2f} | "
#                 f"Utilization={updated_row.forecast_utilization_percent:.2f}%"
#             )

#     except Exception as e:

#         db.rollback()

#         print("Forecast Analytics Error:", e)

#     finally:

#         db.close()

#     print("FORECAST ANALYTICS COMPLETED")
# # ==========================================
# # FORECAST ALERTS
# # ==========================================

# @celery.task
# def check_forecast_alerts():

#     print("FORECAST ALERT TASK RUNNING...")

#     db = SessionLocal()

#     try:

#         rows = db.query(ForecastAnalytics).all()

#         for row in rows:

#             if row.forecast_utilization_percent >= 90:

#                 # Save alert into database
#                 db.add(
#                     ForecastAlertTable(
#                         zone_id=row.zone_id,
#                         forecast_time=row.calculated_time,
#                         predicted_power_kw=row.avg_forecast_power,
#                         alert_message="Forecast Utilization Above 90%",
#                         created_time=datetime.utcnow()
#                     )
#                 )

#                 db.commit()

#                 # Send Redis Message
#                 data = {
#                     "type": "forecast",
#                     "zone": row.zone_id,
#                     "utilization": round(
#                         row.forecast_utilization_percent, 2
#                     ),
#                     "message": "Forecast Utilization Above 90%"
#                 }

#                 r.publish(
#                     "forecast_updates",
#                     json.dumps(data)
#                 )

#                 print(
#                     f"Forecast Alert Published -> {row.zone_id}"
#                 )

#     except Exception as e:

#         db.rollback()

#         print("Forecast Alert Error :", e)

#     finally:

#         db.close()

#     print("FORECAST ALERT TASK COMPLETED")