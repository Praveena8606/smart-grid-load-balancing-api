from datetime import datetime, timedelta
import asyncio

from sqlalchemy import delete

from app.database import AsyncSessionLocal
from app.models import ZoneLoadSummary
from app.celery_app import celery


@celery.task
def delete_old_zone_data():
    asyncio.run(cleanup())


async def cleanup():

    async with AsyncSessionLocal() as db:

        cutoff_date = datetime.utcnow() - timedelta(days=30)

        result = await db.execute(
            delete(ZoneLoadSummary).where(
                ZoneLoadSummary.record_time < cutoff_date
            )
        )

        await db.commit()

        print(f"Deleted {result.rowcount} rows")