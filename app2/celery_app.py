from celery import Celery

celery = Celery(
    "grid_tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)


celery.conf.timezone = "UTC"

celery.conf.beat_schedule = {

    "calculate-zone-average": {
        "task": "app.tasks.calculate_zone_averages",
        "schedule": 10.0
    },

    "check-zone-alerts": {
        "task": "app.tasks.check_zone_alerts",
        "schedule": 10.0
    },

    "generate-forecast": {
        "task": "app.tasks.generate_forecast",
        "schedule": 60.0
    }

}