"""
Custom JWT Authentication Backends
- LocalJWTAuthentication: For local Django users using djangorestframework-simplejwt
  Checks Authorization header first, then falls back to httpOnly cookie.
- ExternalJWTAuthentication: For external API tokens
  Checks Authorization header first, then falls back to httpOnly cookie.
"""

import logging
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication as SimpleJWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from api.cookies import ACCESS_COOKIE_NAME
from api.models import ExternalUser, UserSession
from api.services.external_auth import ExternalAuthService

logger = logging.getLogger(__name__)
User = get_user_model()


class LocalJWTAuthentication(SimpleJWTAuthentication):
    """
    Custom JWT authentication for local Django users.
    Uses djangorestframework-simplejwt for token validation.
    Checks Authorization header first, then falls back to the httpOnly
    access_token cookie for XSS-safe browser sessions.
    """

    def authenticate(self, request):
        """
        Authenticate local users using JWT tokens.
        Returns (user, validated_token) if successful, None if not a local token.
        """
        # 1. Try standard header-based auth (Authorization: Bearer <token>)
        try:
            result = super().authenticate(request)

            if result is not None:
                user, validated_token = result
                logger.info(f"Local user authenticated via header: {user.username}")
                return (user, validated_token)

        except (InvalidToken, TokenError):
            pass  # Not a valid header token, try cookie fallback
        except Exception as e:
            logger.error(f"Local header authentication error: {str(e)}")

        # 2. Fallback: try httpOnly cookie
        raw_token = request.COOKIES.get(ACCESS_COOKIE_NAME)
        if raw_token:
            try:
                validated_token = self.get_validated_token(raw_token)
                user = self.get_user(validated_token)
                logger.info(f"Local user authenticated via cookie: {user.username}")
                return (user, validated_token)
            except (InvalidToken, TokenError):
                return None
            except Exception as e:
                logger.error(f"Local cookie authentication error: {str(e)}")
                return None

        return None


class ExternalJWTAuthentication(BaseAuthentication):
    """
    Custom authentication using external API JWT tokens
    Validates tokens and manages sessions
    """

    keyword = "Bearer"

    def authenticate(self, request):
        """
        Authenticate user using access token from external API.
        Checks Authorization header first, then falls back to httpOnly cookie.

        Args:
            request: Django request object

        Returns:
            tuple: (user, token) if authenticated, None otherwise

        Raises:
            AuthenticationFailed: If token is invalid
        """
        # 1. Try Authorization header
        token = None
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0] == self.keyword:
                token = parts[1]

        # 2. Fallback: try httpOnly cookie
        if not token:
            token = request.COOKIES.get(ACCESS_COOKIE_NAME)

        if not token:
            return None

        try:
            # Try to find active session with this token
            try:
                session = UserSession.objects.select_related("user").get(access_token=token, is_active=True)

                # Check if token is expired
                if session.is_token_expired():
                    logger.info(f"Token expired for user: {session.user.username}")

                    # Try to refresh token
                    if session.refresh_token:
                        try:
                            new_access_token = ExternalAuthService.refresh_token(session.refresh_token)

                            # Update session with new token
                            payload = ExternalAuthService.decode_token_payload(new_access_token)
                            session.access_token = new_access_token
                            session.token_expires_at = datetime.fromtimestamp(payload.get("exp", 0), tz=timezone.get_current_timezone())
                            session.save(update_fields=["access_token", "token_expires_at"])

                            logger.info(f"Token refreshed for user: {session.user.username}")

                        except AuthenticationFailed:
                            session.deactivate()
                            raise AuthenticationFailed("Token expired and refresh failed") from None
                    else:
                        session.deactivate()
                        raise AuthenticationFailed("Token expired")

                # Throttle last_activity writes: only update if >5 minutes stale
                # This avoids a DB write on every single authenticated request
                now = timezone.now()
                if not session.last_activity or (now - session.last_activity).total_seconds() > 300:
                    session.last_activity = now
                    session.save(update_fields=["last_activity"])

                # Refresh user info from external API periodically (every 1 hour)
                if not session.user.cache_updated_at or timezone.now() - session.user.cache_updated_at > timedelta(hours=1):
                    try:
                        user_info = ExternalAuthService.get_user_info(token)
                        session.user.update_from_external_api(user_info)
                    except Exception as e:
                        logger.warning(f"Failed to refresh user info: {str(e)}")

                return (session.user, token)

            except UserSession.DoesNotExist:
                # Token not in our database, validate with external API
                logger.info("Token not found in database, validating with external API")

                user_info = ExternalAuthService.get_user_info(token)

                # Get or create user
                user, created = ExternalUser.objects.get_or_create(external_id=user_info["id"], defaults={"username": user_info["username"], "email": user_info.get("email", ""), "date_joined": user_info.get("date_joined", timezone.now())})

                # Update user data
                user.update_from_external_api(user_info)

                # Create session - handle race condition with get_or_create
                payload = ExternalAuthService.decode_token_payload(token)
                try:
                    session, session_created = UserSession.objects.get_or_create(
                        access_token=token,
                        defaults={
                            "user": user,
                            "token_issued_at": datetime.fromtimestamp(payload.get("iat", 0), tz=timezone.get_current_timezone()),
                            "token_expires_at": datetime.fromtimestamp(payload.get("exp", 0), tz=timezone.get_current_timezone()),
                            "ip_address": self.get_client_ip(request),
                            "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                        },
                    )
                    if session_created:
                        logger.info(f"Created new session for user: {user.username}")
                    else:
                        logger.info(f"Found existing session for user: {user.username}")
                except Exception as db_error:
                    # Handle any remaining race conditions by trying to get existing session
                    logger.warning(f"Session creation conflict, retrying get: {str(db_error)}")
                    try:
                        session = UserSession.objects.get(access_token=token)
                    except UserSession.DoesNotExist:
                        raise AuthenticationFailed("Failed to create or retrieve session") from None

                return (user, token)

        except AuthenticationFailed:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}", exc_info=True)
            raise AuthenticationFailed("Authentication failed") from e

    def authenticate_header(self, request):
        """
        Return WWW-Authenticate header for 401 responses
        """
        return self.keyword

    @staticmethod
    def get_client_ip(request):
        """
        Get client IP address from request
        Handles X-Forwarded-For header for proxied requests
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
