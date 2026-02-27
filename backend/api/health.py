"""
Health check endpoints for monitoring system status.
"""

import logging
import time

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """
    Basic health check endpoint.
    Returns 200 if the service is running.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "healthy", "service": "overtime-api", "timestamp": time.time()}, status=status.HTTP_200_OK)


class HealthCheckDetailedView(APIView):
    """
    Detailed health check with database and cache status.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        health_status = {"status": "healthy", "service": "overtime-api", "timestamp": time.time(), "checks": {}}

        overall_healthy = True

        # Check database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            health_status["checks"]["database"] = {"status": "healthy", "message": "Database connection successful"}
        except Exception as e:
            logger.error("Database health check failed: %s", e)
            health_status["checks"]["database"] = {"status": "unhealthy", "message": str(e)}
            overall_healthy = False

        # Check cache connection (Redis)
        try:
            cache_key = "_health_check_test"
            cache.set(cache_key, "ok", timeout=10)
            cache_value = cache.get(cache_key)
            cache.delete(cache_key)

            if cache_value == "ok":
                health_status["checks"]["cache"] = {"status": "healthy", "message": "Cache connection successful"}
            else:
                raise Exception("Cache read/write mismatch")
        except Exception as e:
            logger.warning("Cache health check failed: %s", e)
            health_status["checks"]["cache"] = {"status": "degraded", "message": f"Cache unavailable: {str(e)}"}
            # Cache failure is not critical, mark as degraded not unhealthy

        # Check Celery (if configured)
        if hasattr(settings, "CELERY_BROKER_URL"):
            try:
                from celery import current_app

                inspector = current_app.control.inspect()
                stats = inspector.stats()

                if stats:
                    health_status["checks"]["celery"] = {"status": "healthy", "message": f"{len(stats)} worker(s) active"}
                else:
                    health_status["checks"]["celery"] = {"status": "degraded", "message": "No active workers"}
            except Exception as e:
                logger.warning("Celery health check failed: %s", e)
                health_status["checks"]["celery"] = {"status": "degraded", "message": f"Celery unavailable: {str(e)}"}

        # Set overall status
        if not overall_healthy:
            health_status["status"] = "unhealthy"
            return Response(health_status, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        elif any(check.get("status") == "degraded" for check in health_status["checks"].values()):
            health_status["status"] = "degraded"
            return Response(health_status, status=status.HTTP_200_OK)
        else:
            return Response(health_status, status=status.HTTP_200_OK)


class ReadinessCheckView(APIView):
    """
    Readiness check - returns 200 only when all critical services are ready.
    Used by load balancers and orchestrators.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        try:
            # Check database
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()

            return Response({"status": "ready", "timestamp": time.time()}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error("Readiness check failed: %s", e)
            return Response({"status": "not_ready", "message": str(e), "timestamp": time.time()}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class LivenessCheckView(APIView):
    """
    Liveness check - returns 200 if the application is alive.
    Used to detect if the application needs to be restarted.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "alive", "timestamp": time.time()}, status=status.HTTP_200_OK)
