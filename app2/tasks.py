from sqlalchemy import func
from datetime import datetime, timezone

from app.database import SessionLocal
from app.models import (
    ZoneLoadSummary,
    ZoneAnalyticsSummary,
    AlertTable
)

from app.celery_app import celery


@celery.task
def calculate_zone_averages():

    print("CALCULATING ZONE ANALYTICS...")

    db = SessionLocal()

    zones = db.query(
        ZoneLoadSummary.zone_id
    ).distinct().all()

    for zone in zones:

        zone_id = zone[0]

        # Average Power
        avg_power = db.query(
            func.avg(ZoneLoadSummary.total_power_kw)
        ).filter(
            ZoneLoadSummary.zone_id == zone_id
        ).scalar()

        # Average Voltage
        avg_voltage = db.query(
            func.avg(ZoneLoadSummary.avg_voltage)
        ).filter(
            ZoneLoadSummary.zone_id == zone_id
        ).scalar()

        # Average Current
        avg_current = db.query(
            func.avg(ZoneLoadSummary.avg_current)
        ).filter(
            ZoneLoadSummary.zone_id == zone_id
        ).scalar()

        # House Count (Distinct Houses)
        house_count = db.query(
            func.count(
                func.distinct(
                    ZoneLoadSummary.house_id
                )
            )
        ).filter(
            ZoneLoadSummary.zone_id == zone_id
        ).scalar()

        # Capacity Calculation
        total_current_capacity = house_count * 5

        # Utilization %
        if total_current_capacity > 0:
            utilization_percent = (
                avg_current / total_current_capacity
            ) * 100
        else:
            utilization_percent = 0

        existing = db.query(
            ZoneAnalyticsSummary
        ).filter(
            ZoneAnalyticsSummary.zone_id == zone_id
        ).first()

        if existing:

            existing.avg_power_kw = avg_power
            existing.avg_voltage = avg_voltage
            existing.avg_current = avg_current
            existing.house_count = house_count
            existing.total_current_capacity = total_current_capacity
            existing.utilization_percent = utilization_percent
            existing.calculated_time = datetime.now(
                timezone.utc
            )

        else:

            db.add(
                ZoneAnalyticsSummary(
                    zone_id=zone_id,
                    avg_power_kw=avg_power,
                    avg_voltage=avg_voltage,
                    avg_current=avg_current,
                    house_count=house_count,
                    total_current_capacity=total_current_capacity,
                    utilization_percent=utilization_percent,
                    calculated_time=datetime.now(
                        timezone.utc
                    )
                )
            )

        print(
            f"{zone_id} | Houses={house_count} | "
            f"AvgCurrent={avg_current} | "
            f"Capacity={total_current_capacity} | "
            f"Utilization={utilization_percent:.2f}%"
        )

    db.commit()
    db.close()


@celery.task
def check_zone_alerts():

    print("ALERT TASK RUNNING...")

    db = SessionLocal()

    zones = db.query(
        ZoneAnalyticsSummary
    ).all()

    print("Total Zones:", len(zones))

    for zone in zones:

        print(
            f"{zone.zone_id} -> "
            f"Utilization={zone.utilization_percent}"
        )

        if zone.utilization_percent >= 90:

            print(
                f"ALERT GENERATED FOR {zone.zone_id}"
            )

            alert = AlertTable(
                zone_id=zone.zone_id,
                avg_current=zone.avg_current,
                utilization_percent=zone.utilization_percent,
                alert_message="Current Utilization Above 90%",
                alert_time=datetime.now(
                    timezone.utc
                )
            )

            db.add(alert)

    db.commit()
    db.close()

