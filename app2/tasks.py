import os
import json
import redis

from datetime import datetime, timezone,timedelta
from sqlalchemy import func, and_

from app.database import SessionLocal
from app.celery_app import celery

from app.models import (
    ZoneLoadSummary,
    ZoneAnalyticsSummary,
    AlertTable
)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

r = redis.Redis(
    host=REDIS_HOST,
    port=6379,
    decode_responses=True
)


@celery.task
def calculate_zone_averages():

    print("CALCULATING ZONE ANALYTICS...")

    db = SessionLocal()

    try:

        zones = (
            db.query(ZoneLoadSummary.zone_id)
            .distinct()
            .all()
        )

        for zone in zones:

            zone_id = zone[0]

            # -----------------------------------------
            # Get latest reading for each house
            # -----------------------------------------

            latest_subquery = (
                db.query(
                    ZoneLoadSummary.house_id,
                    func.max(ZoneLoadSummary.record_time).label("latest_time")
                )
                .filter(
                    ZoneLoadSummary.zone_id == zone_id
                )
                .group_by(
                    ZoneLoadSummary.house_id
                )
                .subquery()
            )

            latest_rows = (
                db.query(ZoneLoadSummary)
                .join(
                    latest_subquery,
                    and_(
                        ZoneLoadSummary.house_id == latest_subquery.c.house_id,
                        ZoneLoadSummary.record_time == latest_subquery.c.latest_time
                    )
                )
                .filter(
                    ZoneLoadSummary.zone_id == zone_id
                )
                .all()
            )

            if not latest_rows:
                continue

            # -----------------------------------------
            # Debug
            # -----------------------------------------

            print(f"\nZone : {zone_id}")

            for row in latest_rows:
                print(
                    row.house_id,
                    row.avg_power_kw,
                    row.record_time
                )

            # -----------------------------------------
            # Calculate values
            # -----------------------------------------

            house_count = len(latest_rows)

            total_power = sum(
                row.avg_power_kw
                for row in latest_rows
            )

            avg_power = (
                total_power / house_count
                if house_count > 0
                else 0
            )

            avg_voltage = (
                sum(row.avg_voltage for row in latest_rows)
                / house_count
                if house_count > 0
                else 0
            )

            avg_current = (
                sum(row.avg_current for row in latest_rows)
                / house_count
                if house_count > 0
                else 0
            )

            total_power_capacity = house_count * 5

            utilization_percent = (
                (total_power / total_power_capacity) * 100
                if total_power_capacity > 0
                else 0
            )

            # -----------------------------------------
            # Update / Insert Analytics
            # -----------------------------------------

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

            # -----------------------------------------
            # Publish Redis Update
            # -----------------------------------------

            data = {
                "type": "grid_update",
                "zone_id": existing.zone_id,
                "avg_power_kw": round(float(existing.avg_power_kw), 2),
                "avg_voltage": round(float(existing.avg_voltage), 2),
                "avg_current": round(float(existing.avg_current), 2),
                "house_count": existing.house_count,
                "total_power_capacity": float(existing.total_power_capacity),
                "utilization_percent": round(
                    float(existing.utilization_percent), 2
                ),
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

    print("========== ZONE ALERT TASK STARTED ==========")

    db = SessionLocal()

    try:

        zones = db.query(ZoneAnalyticsSummary).all()

        print(f"Total Zones : {len(zones)}")

        for zone in zones:

            print(f"{zone.zone_id} -> {zone.utilization_percent}%")

            # Skip if utilization below 90%
            if float(zone.utilization_percent) < 90:
                continue

            current_utilization = round(
                float(zone.utilization_percent), 2
            )

            current_message = "Current Utilization Above 90%"

            # ------------------------------------
            # Duplicate Check (Last 30 Minutes)
            # ------------------------------------

            duplicate = (
                db.query(AlertTable)
                .filter(
                    AlertTable.zone_id == zone.zone_id,
                    AlertTable.alert_time >= (
                        datetime.now(timezone.utc)
                        - timedelta(minutes=30)
                    )
                )
                .first()
            )

            print("ZONE :", zone.zone_id)
            print("UTIL :", current_utilization)
            print("Duplicate :", duplicate)

            if duplicate:
                print("SKIPPING DUPLICATE")
                continue

            print("NO DUPLICATE FOUND")

            # ------------------------------------
            # Save Alert
            # ------------------------------------

            new_alert = AlertTable(
                zone_id=zone.zone_id,
                avg_current=zone.avg_current,
                utilization_percent=current_utilization,
                alert_message=current_message,
                alert_time=datetime.now(timezone.utc)
            )

            db.add(new_alert)
            db.commit()
            db.refresh(new_alert)

            print(f"Alert Saved -> {zone.zone_id}")

            # ------------------------------------
            # Publish Redis
            # ------------------------------------

            redis_message = {
                "type": "zone",
                "zone": zone.zone_id,
                "utilization": current_utilization,
                "message": current_message,
                "alert_time": new_alert.alert_time.strftime(
                    "%d-%m-%Y %H:%M:%S"
                )
            }

            print("Publishing Redis ->", redis_message)

            subscribers = r.publish(
                "grid_updates",
                json.dumps(redis_message)
            )

            print(
                f"Redis Published -> {zone.zone_id} | Subscribers = {subscribers}"
            )

    except Exception as e:

        db.rollback()
        print("ZONE ALERT ERROR :", str(e))

    finally:

        db.close()

    print("========== ZONE ALERT TASK COMPLETED ==========")
    
# @celery.task
# def calculate_zone_averages():

#     print("CALCULATING ZONE ANALYTICS...")

#     db = SessionLocal()

#     try:

#         zones = (
#             db.query(ZoneLoadSummary.zone_id)
#             .distinct()
#             .all()
#         )

#         for zone in zones:

#             zone_id = zone[0]

#             # -------------------------------------------------
#             # Get latest reading of every unique house
#             # -------------------------------------------------

#             latest_rows = (
#                 db.query(ZoneLoadSummary)
#                 .filter(
#                     ZoneLoadSummary.zone_id == zone_id
#                 )
#                 .order_by(
#                     ZoneLoadSummary.house_id,
#                     ZoneLoadSummary.record_time.desc()
#                 )
#                 .distinct(ZoneLoadSummary.house_id)
#                 .all()
#             )

#             if len(latest_rows) == 0:
#                 continue

#             # -------------------------------------------------
#             # Calculate values
#             # -------------------------------------------------

#             house_count = len(latest_rows)

#             total_power = sum(
#                 row.avg_power_kw
#                 for row in latest_rows
#             )

#             avg_power = (
#                 total_power / house_count
#                 if house_count > 0
#                 else 0
#             )

#             avg_voltage = (
#                 sum(
#                     row.avg_voltage
#                     for row in latest_rows
#                 ) / house_count
#                 if house_count > 0
#                 else 0
#             )

#             avg_current = (
#                 sum(
#                     row.avg_current
#                     for row in latest_rows
#                 ) / house_count
#                 if house_count > 0
#                 else 0
#             )

#             # Every unique house contributes 5 kW

#             total_power_capacity = house_count * 5

#             utilization_percent = (
#                 (avg_power / total_power_capacity) * 100
#                 if total_power_capacity > 0
#                 else 0
#             )

#             # -------------------------------------------------
#             # Update / Insert analytics
#             # -------------------------------------------------

#             existing = (
#                 db.query(ZoneAnalyticsSummary)
#                 .filter(
#                     ZoneAnalyticsSummary.zone_id == zone_id
#                 )
#                 .first()
#             )

#             if existing:

#                 existing.avg_power_kw = avg_power
#                 existing.avg_voltage = avg_voltage
#                 existing.avg_current = avg_current
#                 existing.house_count = house_count
#                 existing.total_power_capacity = total_power_capacity
#                 existing.utilization_percent = utilization_percent
#                 existing.calculated_time = datetime.now(timezone.utc)

#             else:

#                 existing = ZoneAnalyticsSummary(

#                     zone_id=zone_id,

#                     avg_power_kw=avg_power,

#                     avg_voltage=avg_voltage,

#                     avg_current=avg_current,

#                     house_count=house_count,

#                     total_power_capacity=total_power_capacity,

#                     utilization_percent=utilization_percent,

#                     calculated_time=datetime.now(timezone.utc)

#                 )

#                 db.add(existing)

#             db.commit()
#             db.refresh(existing)

#             # -------------------------------------------------
#             # Publish Redis Update
#             # -------------------------------------------------

#             data = {

#                 "type": "grid_update",

#                 "zone_id": existing.zone_id,

#                 "avg_power_kw": round(float(existing.avg_power_kw), 2),

#                 "avg_voltage": round(float(existing.avg_voltage), 2),

#                 "avg_current": round(float(existing.avg_current), 2),

#                 "house_count": existing.house_count,

#                 "total_power_capacity": float(existing.total_power_capacity),

#                 "utilization_percent": round(
#                     float(existing.utilization_percent), 2
#                 ),

#                 "calculated_time": existing.calculated_time.strftime(
#                     "%d-%m-%Y %H:%M:%S"
#                 )

#             }

#             r.publish(
#                 "grid_updates",
#                 json.dumps(data)
#             )

#             print(f"Published Grid Update -> {zone_id}")

#     except Exception as e:

#         db.rollback()

#         print("Zone Analytics Error:", e)

#     finally:

#         db.close()

#     print("ZONE ANALYTICS COMPLETED")


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
#                 db.query(func.avg(ZoneLoadSummary.avg_power_kw))
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