"""
Performance monitoring and logging middleware.
"""

import http.cookies
import logging
import re
import time
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.conf import settings
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Get client IP address from request headers."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class TokenAuthMiddleware(BaseMiddleware):
    """
    WebSocket middleware for JWT token authentication.
    Reads the httpOnly access_token cookie from the WS handshake headers.
    Falls back to query string token (legacy).
    """

    async def __call__(self, scope, receive, send):
        token = None

        # 1. Try httpOnly cookie from WS handshake headers
        headers = dict(scope.get("headers", []))
        cookie_header = headers.get(b"cookie", b"").decode()
        if cookie_header:
            cookie = http.cookies.SimpleCookie()
            try:
                cookie.load(cookie_header)
                if "access_token" in cookie:
                    token = cookie["access_token"].value
            except http.cookies.CookieError:
                pass

        # 2. Fallback: query string (legacy)
        if not token:
            query_string = scope.get("query_string", b"").decode()
            query_params = parse_qs(query_string)
            token = query_params.get("token", [None])[0]

        if token:
            user = await self.get_user_from_token(token)
            if user:
                scope["user"] = user

        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user_from_token(self, token):
        """
        Authenticate a token.
        Tries local JWT validation first, then external UserSession lookup.
        """
        # 1. Try local JWT (SimpleJWT)
        try:
            from rest_framework_simplejwt.authentication import JWTAuthentication

            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)
            return user
        except Exception:
            pass

        # 2. Try external UserSession
        from api.models import UserSession

        try:
            session = UserSession.objects.select_related("user").get(token_hash=UserSession.hash_token(token), is_active=True)
            if not session.is_token_expired():
                return session.user
        except UserSession.DoesNotExist:
            pass
        except Exception as e:
            logger.error("WebSocket token auth error: %s", e)

        return None


def TokenAuthMiddlewareStack(inner):
    """Convenience function for wrapping the ASGI application."""
    return TokenAuthMiddleware(inner)


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to monitor request/response performance and log slow requests.
    Query monitoring is controlled by the QUERY_MONITORING setting
    (defaults to DEBUG, can be enabled independently in staging/production).
    """

    def process_request(self, request):
        """Store the start time when request comes in."""
        request._start_time = time.time()
        if settings.QUERY_MONITORING:
            # Force debug cursor so connection.queries is populated even
            # when DEBUG=False.  Adds minor per-query overhead.
            if not settings.DEBUG:
                connection.force_debug_cursor = True
            request._query_count_start = len(connection.queries)

    def process_response(self, request, response):
        """Calculate and log request processing time."""
        if hasattr(request, "_start_time"):
            # Calculate total time
            total_time = time.time() - request._start_time

            # Calculate query count
            query_count = 0
            if settings.QUERY_MONITORING:
                query_count = len(connection.queries) - getattr(request, "_query_count_start", 0)
                # Reset the forced debug cursor so it doesn't leak
                if not settings.DEBUG:
                    connection.force_debug_cursor = False

            # Log slow requests (> 1 second)
            if total_time > 1.0:
                if settings.QUERY_MONITORING:
                    logger.warning(
                        "SLOW REQUEST: %s %s took %.2fs with %d queries",
                        request.method,
                        request.path,
                        total_time,
                        query_count,
                    )
                else:
                    logger.warning(
                        "SLOW REQUEST: %s %s took %.2fs",
                        request.method,
                        request.path,
                        total_time,
                    )

            # Add performance headers for debugging
            response["X-Request-Time"] = f"{total_time:.4f}s"
            if settings.QUERY_MONITORING:
                response["X-Query-Count"] = str(query_count)

            logger.debug(
                "%s %s - Status: %s - Time: %.4fs",
                request.method,
                request.path,
                response.status_code,
                total_time,
            )

        return response


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to all responses.
    """

    def process_response(self, request, response):
        """Add security headers."""
        # Allow embedding for media files (PDF viewer) - use SAMEORIGIN for media
        # For other resources, check settings
        _EMBEDDABLE_EXTENSIONS = (".pdf", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")
        if request.path.startswith(settings.MEDIA_URL) and request.path.lower().endswith(_EMBEDDABLE_EXTENSIONS):
            # Allow embedding of embeddable media (PDFs, images) from same origin
            frame_option = "SAMEORIGIN"
            # Remove X-Frame-Options for media to allow cross-origin embedding
            # The frontend may be on a different port/origin
            if "X-Frame-Options" in response:
                del response["X-Frame-Options"]
        else:
            frame_option = getattr(settings, "X_FRAME_OPTIONS", "SAMEORIGIN")
            response["X-Frame-Options"] = frame_option

        # Prevent MIME type sniffing
        response["X-Content-Type-Options"] = "nosniff"

        # Enable XSS protection
        response["X-XSS-Protection"] = "1; mode=block"

        # Referrer policy
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content Security Policy
        # For embeddable media files (PDFs, images), allow embedding from any origin
        if request.path.startswith(settings.MEDIA_URL) and request.path.lower().endswith(_EMBEDDABLE_EXTENSIONS):
            # Relaxed CSP for media files to allow embedding
            csp = "default-src 'self'; frame-ancestors *; media-src 'self' data: blob:; object-src 'self' data: blob:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob: https:; font-src 'self' data:; connect-src 'self';"
        else:
            # Standard CSP for other resources — 'unsafe-inline' kept for Vue SFC styles
            csp = "default-src 'self'; frame-ancestors 'self'; media-src 'self' data: blob:; object-src 'self' data: blob:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob: https:; font-src 'self' data:; connect-src 'self';"
        response["Content-Security-Policy"] = csp

        # Permissions policy
        response["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Log all write operations (POST, PUT, PATCH, DELETE) for audit trail.
    Persists to UserActivityLog database table for super admin viewing.
    """

    # URL pattern to extract resource name and ID from /api/v1/<resource>/[<id>/]
    API_PATTERN = re.compile(r"^/api/v1/(?P<resource>[\w-]+)/(?:(?P<resource_id>\d+)/)?")

    # Map HTTP methods to action names
    METHOD_ACTION = {
        "POST": "create",
        "PUT": "update",
        "PATCH": "update",
        "DELETE": "delete",
    }

    # Paths to skip (already logged by their views, or not meaningful)
    SKIP_PREFIXES = (
        "/api/v1/activity-logs/",
        "/api/v1/board-presence/",
        "/api/v1/auth/",
        "/api/v1/system/",
    )

    def process_response(self, request, response):
        """Log write operations."""
        write_methods = ["POST", "PUT", "PATCH", "DELETE"]

        if request.method in write_methods:
            user = getattr(request, "user", None)
            user_info = "anonymous"

            if user and hasattr(user, "is_authenticated") and user.is_authenticated:
                user_info = f"{user.username} (ID: {user.id})"

            logger.info("AUDIT: %s %s - User: %s - Status: %s - IP: %s", request.method, request.path, user_info, response.status_code, get_client_ip(request))

            # Persist to UserActivityLog for successful write operations on API endpoints
            if 200 <= response.status_code < 300 and request.path.startswith("/api/v1/") and not any(request.path.startswith(p) for p in self.SKIP_PREFIXES) and user and hasattr(user, "is_authenticated") and user.is_authenticated:
                # Capture request data needed for logging (since request may be gone after response)
                persist_kwargs = {
                    "method": request.method,
                    "path": request.path,
                    "user": user,
                    "response_data": getattr(response, "data", None),
                    "client_ip": get_client_ip(request),
                }
                # Offload DB writes to after the current transaction commits
                from django.db import transaction as db_transaction

                db_transaction.on_commit(lambda: self._persist_activity(**persist_kwargs))

        return response

    def _persist_activity(self, method, path, user, response_data, client_ip):
        """Persist the write action to UserActivityLog (called via on_commit)."""
        try:
            from .models import ExternalUser, UserActivityLog

            ext_user = None

            # Resolve to ExternalUser
            if isinstance(user, ExternalUser):
                ext_user = user
            else:
                worker_id = getattr(user, "worker_id", None)
                if worker_id:
                    ext_user = ExternalUser.objects.filter(worker_id=worker_id).first()
                if not ext_user:
                    username = getattr(user, "username", None)
                    if username:
                        ext_user = ExternalUser.objects.filter(username__iexact=username).first()

            if not ext_user:
                return

            match = self.API_PATTERN.match(path)
            if not match:
                return

            resource = match.group("resource")
            resource_id_str = match.group("resource_id")
            resource_id = int(resource_id_str) if resource_id_str else None

            action = self.METHOD_ACTION.get(method, method.lower())

            # For POST (create), try to get the new resource ID from response
            if action == "create" and resource_id is None:
                try:
                    if isinstance(response_data, dict):
                        resource_id = response_data.get("id")
                except Exception:
                    pass

            # Build details dict
            details = {}
            remaining = path[match.end() :]
            if remaining and remaining.strip("/"):
                details["sub_action"] = remaining.strip("/")

            UserActivityLog.objects.create(
                user=ext_user,
                action=action,
                resource=resource,
                resource_id=resource_id,
                details=details or {},
                ip_address=client_ip,
            )
        except Exception as e:
            logger.warning("AuditLoggingMiddleware: Failed to persist activity log: %s", e)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Log all incoming requests with relevant details.
    Uses DEBUG level to avoid flooding production logs.
    """

    def process_request(self, request):
        """Log incoming request."""
        user = getattr(request, "user", None)
        user_info = "anonymous"

        if user and user.is_authenticated:
            user_info = f"{user.username} (ID: {user.id})"

        logger.debug("REQUEST: %s %s - User: %s - IP: %s", request.method, request.path, user_info, get_client_ip(request))
