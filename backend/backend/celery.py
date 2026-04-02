"""
Celery Configuration
Async task processing for long-running operations
"""

import os

from celery import Celery
from celery.schedules import crontab

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# Create Celery app
app = Celery("backend")

# Load configuration from Django settings with CELERY namespace
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "cleanup-expired-sessions-daily": {
        "task": "api.tasks.cleanup_expired_sessions",
        "schedule": crontab(minute=0, hour=0),
    },
    "cleanup-user-activity-logs-daily": {
        "task": "api.tasks.cleanup_user_activity_logs",
        "schedule": crontab(minute=15, hour=0),
    },
}


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery"""
    print(f"Request: {self.request!r}")
