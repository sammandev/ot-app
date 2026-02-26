"""
Backend package
"""

# Import Celery app to ensure it's registered with Django
from .celery import app as celery_app

__all__ = ("celery_app",)
