import os
from celery import Celery

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

celery = Celery(
    "grid_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery.conf.timezone = "Asia/Kolkata"

celery.conf.beat_schedule = {

    "calculate-zone-average": {
        "task": "app.tasks.calculate_zone_averages",
        "schedule": 10.0,
    },

    "check-zone-alerts": {
        "task": "app.tasks.check_zone_alerts",
        "schedule": 10.0,
    },

    "delete-old-zone-load-summary": {
        "task": "app.cleanup_task.delete_old_zone_data",
        "schedule": 86400.0,   # Every 24 Hours
    }

}

celery.autodiscover_tasks(["app"])


 # "generate-forecast": {
    #     "task": "app.tasks.generate_forecast",
    #     "schedule": 10.0,
    # },

    # "forecast-analytics": {
    #     "task": "app.tasks.calculate_forecast_analytics",
    #     "schedule": 10.0,
    # },

    # "forecast-alert": {
    #     "task": "app.tasks.check_forecast_alerts",
    #     "schedule": 10.0,
    # },


# celery.conf.timezone = "Asia/Kolkata"

# celery.conf.beat_schedule = {

#     "delete-old-zone-load-summary": {

#         "task": "app.tasks.cleanup_task.delete_old_zone_data",

#         "schedule": 86400.0,   # Every 24 Hours

#     }

# }



