import logging
from datetime import datetime

from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from ..cookies import clear_auth_cookies, set_auth_cookies
from ..models import (
    ExternalUser,
    UserActivityLog,
    UserSession,
)
from ..services.external_auth import ExternalAuthService
from .helpers import get_employee_for_user, is_developer_user, is_ptb_admin, is_superadmin_user  # noqa: F401

logger = logging.getLogger(__name__)
User = get_user_model()


class LoginRateThrottle(AnonRateThrottle):
    """
    Strict rate limit for login endpoints — always active regardless of the
    global THROTTLING_ENABLED toggle.  Prevents brute-force credential stuffing.
    """

    rate = "10/min"
    scope = "login"


class LocalLoginView(APIView):
    """
    Local authentication endpoint for Django users
    Uses Django's built-in authentication and JWT tokens
    """

    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    @swagger_auto_schema(
        operation_summary="Login with local credentials",
        operation_description="Authenticate local Django user and return JWT tokens",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["username", "password"],
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING, description="Username"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, format="password", description="Password"),
            },
        ),
        responses={
            200: openapi.Response(
                description="Login successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "access": openapi.Schema(type=openapi.TYPE_STRING, description="JWT access token"),
                        "refresh": openapi.Schema(type=openapi.TYPE_STRING, description="JWT refresh token"),
                        "user": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "username": openapi.Schema(type=openapi.TYPE_STRING),
                                "email": openapi.Schema(type=openapi.TYPE_STRING),
                                "first_name": openapi.Schema(type=openapi.TYPE_STRING),
                                "last_name": openapi.Schema(type=openapi.TYPE_STRING),
                                "is_staff": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                "is_superuser": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            },
                        ),
                        "auth_type": openapi.Schema(type=openapi.TYPE_STRING, enum=["local"]),
                    },
                ),
            ),
            400: "Bad request - username or password missing",
            401: "Unauthorized - invalid credentials or inactive account",
        },
        tags=["auth"],
    )
    def post(self, request):
        """
        Authenticate local user and return JWT tokens

        Request Body:
            {
                "username": "user",
                "password": "password"
            }

        Response:
            {
                "access": "jwt_access_token",
                "refresh": "jwt_refresh_token",
                "user": {
                    "id": 1,
                    "username": "user",
                    "email": "user@example.com",
                    "first_name": "First",
                    "last_name": "Last",
                    "is_staff": true,
                    "is_superuser": false
                }
            }
        """
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"detail": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is None:
            logger.warning("Failed local login attempt for username: %s", username)
            return Response({"detail": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            logger.warning("Inactive user login attempt: %s", username)
            return Response({"detail": "User account is disabled"}, status=status.HTTP_401_UNAUTHORIZED)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        logger.info("Local user logged in successfully: %s", username)

        # Note: Local users don't have ExternalUser records, so we skip activity logging for now
        # Activity logging is designed for ExternalUser model

        # Check if this is the superadmin user
        is_super_admin = is_superadmin_user(user)
        permission_updated = getattr(user, "permission_updated_at", None)

        response = Response(
            {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email or "",
                    "first_name": user.first_name or "",
                    "last_name": user.last_name or "",
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                    # Include worker_id, is_ptb_admin, menu_permissions for consistency
                    "worker_id": getattr(user, "worker_id", None),
                    "is_ptb_admin": getattr(user, "is_ptb_admin", False) or is_super_admin,
                    "role": getattr(user, "role", "developer" if is_super_admin else "user"),
                    "menu_permissions": getattr(user, "menu_permissions", {}),
                    "permission_updated_at": permission_updated.isoformat() if permission_updated else None,
                    "employee_id": None,
                    "department_id": None,
                },
            },
            status=status.HTTP_200_OK,
        )

        # Deliver tokens exclusively via httpOnly cookies
        set_auth_cookies(response, access_token, refresh_token)
        return response


class ExternalLoginView(APIView):
    """
    External authentication endpoint
    Authenticates with external API and stores session
    """

    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    @swagger_auto_schema(
        operation_summary="Login with external credentials",
        operation_description="Authenticate with external API and return tokens",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["username", "password"],
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING, description="Username"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, format="password", description="Password"),
            },
        ),
        responses={
            200: openapi.Response(
                description="Login successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "access": openapi.Schema(type=openapi.TYPE_STRING, description="External JWT access token"),
                        "refresh": openapi.Schema(type=openapi.TYPE_STRING, description="External JWT refresh token"),
                        "user": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "username": openapi.Schema(type=openapi.TYPE_STRING),
                                "email": openapi.Schema(type=openapi.TYPE_STRING),
                                "first_name": openapi.Schema(type=openapi.TYPE_STRING),
                                "last_name": openapi.Schema(type=openapi.TYPE_STRING),
                                "is_staff": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                "is_superuser": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                "is_ptb_admin": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                "worker_id": openapi.Schema(type=openapi.TYPE_STRING),
                                "employee_id": openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True),
                                "department_id": openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True),
                                "date_joined": openapi.Schema(type=openapi.TYPE_STRING, format="date-time"),
                                "last_login": openapi.Schema(type=openapi.TYPE_STRING, format="date-time", nullable=True),
                                "groups": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                                "permissions": openapi.Schema(type=openapi.TYPE_OBJECT),
                            },
                        ),
                    },
                ),
            ),
            400: "Bad request - username or password missing",
            401: "Unauthorized - invalid credentials",
            500: "Internal server error - authentication service error",
        },
        tags=["auth"],
    )
    def post(self, request):
        """
        Authenticate with external API and return tokens

        Request Body:
            {
                "username": "user",
                "password": "password"
            }

        Response:
            {
                "access": "external_jwt_token",
                "refresh": "external_refresh_token",
                "user": {
                    "id": 1,
                    "external_id": 123,
                    "username": "user",
                    "email": "user@example.com",
                    "worker_id": "WORKER123",
                    "is_ptb_admin": true,
                    "first_name": "First",
                    "last_name": "Last"
                }
            }
        """
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"detail": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Login to external API
            auth_data = ExternalAuthService.login(username, password)

            # Get user info from external API
            user_info = ExternalAuthService.get_user_info(auth_data["access"])

            # Get or create user
            user, _ = ExternalUser.objects.get_or_create(external_id=user_info["id"], defaults={"username": user_info["username"], "email": user_info.get("email", ""), "date_joined": user_info.get("date_joined", timezone.now())})

            # Check if user is deactivated in our system (not the external system)
            if not user.is_active:
                logger.warning("Deactivated external user login attempt: %s", username)
                return Response({"detail": "Your account has been deactivated. Please contact your administrator."}, status=status.HTTP_401_UNAUTHORIZED)

            # Update user data from external API
            user.update_from_external_api(user_info)
            # update_from_external_api() already calls self.save(); update last_login
            # in the same save to avoid a redundant second write.
            ExternalUser.objects.filter(pk=user.pk).update(
                last_login=timezone.now(),
                updated_at=timezone.now(),
            )

            # Deactivate old sessions for this user
            UserSession.objects.filter(user=user, is_active=True).update(is_active=False)

            # Create new session
            payload = ExternalAuthService.decode_token_payload(auth_data["access"])
            UserSession.objects.create(
                user=user,
                access_token=auth_data["access"],
                refresh_token=auth_data.get("refresh", ""),
                token_issued_at=datetime.fromtimestamp(payload.get("iat", 0), tz=timezone.get_current_timezone()),
                token_expires_at=datetime.fromtimestamp(payload.get("exp", 0), tz=timezone.get_current_timezone()),
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )

            logger.info("External user logged in successfully: %s", username)

            # Log user login activity
            UserActivityLog.log_activity(user=user, action="login", details={"login_type": "external", "username": username}, request=request)

            # Helper function to safely format datetime fields
            def format_datetime(dt_value):
                """Safely convert datetime to ISO format string"""
                if dt_value is None:
                    return None
                if isinstance(dt_value, str):
                    return dt_value  # Already a string
                if hasattr(dt_value, "isoformat"):
                    return dt_value.isoformat()
                return str(dt_value)

            response = Response(
                {
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email or "",
                        "first_name": user.first_name or "",
                        "last_name": user.last_name or "",
                        "is_staff": user.is_staff,
                        "is_superuser": user.is_superuser,
                        "is_active": user.is_active,
                        "is_ptb_admin": user.is_ptb_admin,
                        "role": getattr(user, "role", "user"),
                        "worker_id": user.worker_id or "",
                        "menu_permissions": user.menu_permissions,  # CRITICAL: Include menu permissions
                        "event_reminders_enabled": user.event_reminders_enabled,
                        "preferred_language": getattr(user, "preferred_language", "en"),
                        "permission_updated_at": format_datetime(user.permission_updated_at),  # For force logout detection
                        "employee_id": None,
                        "department_id": None,
                        "date_joined": format_datetime(user.date_joined),
                        "last_login": format_datetime(user.last_login),
                        "groups": user.groups_cache,
                        "permissions": user.permissions_cache,
                    },
                },
                status=status.HTTP_200_OK,
            )

            # Deliver tokens exclusively via httpOnly cookies
            set_auth_cookies(response, auth_data["access"], auth_data.get("refresh"))
            return response

        except AuthenticationFailed as e:
            logger.warning("External login failed for user %s: %s", username, e)
            return Response({"detail": "Authentication failed."}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error("External login error for user %s: %s", username, e)
            return Response({"detail": "Authentication service error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def _get_client_ip(request):
        """Get client IP address"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class TokenVerifyView(APIView):
    """
    Token verification endpoint
    Determines if a token is from local API or external API
    """

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Verify token source",
        operation_description="Verify if a token is from local API or external API, and check if it's valid",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["token"],
            properties={
                "token": openapi.Schema(type=openapi.TYPE_STRING, description="JWT token to verify"),
            },
        ),
        responses={
            200: openapi.Response(
                description="Token verification result",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "valid": openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Whether the token is valid"),
                        "source": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Token source: 'local', 'external', or 'unknown'",
                            enum=["local", "external", "unknown"],
                        ),
                        "details": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description="Additional token details if valid",
                            properties={
                                "user_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "username": openapi.Schema(type=openapi.TYPE_STRING),
                                "exp": openapi.Schema(type=openapi.TYPE_INTEGER, description="Token expiration timestamp"),
                                "iat": openapi.Schema(type=openapi.TYPE_INTEGER, description="Token issued at timestamp"),
                            },
                        ),
                    },
                ),
            ),
            400: "Bad request - token missing",
        },
        tags=["auth"],
    )
    def post(self, request):
        """
        Verify token and determine its source

        Request Body:
            {
                "token": "jwt_token_here"
            }

        Response:
            {
                "valid": true,
                "source": "external",
                "details": {
                    "user_id": 123,
                    "username": "user",
                    "exp": 1759831574,
                    "iat": 1759745114
                }
            }
        """
        token = request.data.get("token")

        if not token:
            return Response({"detail": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Try to verify as local JWT token first
        try:
            from rest_framework_simplejwt.tokens import AccessToken

            # Validate local token
            validated_token = AccessToken(token)

            # Get user from token
            from django.contrib.auth import get_user_model

            User = get_user_model()

            try:
                user = User.objects.get(id=validated_token["user_id"])

                return Response(
                    {
                        "valid": True,
                        "source": "local",
                        "details": {
                            "user_id": user.id,
                            "username": user.username,
                            "exp": validated_token.get("exp"),
                            "iat": validated_token.get("iat"),
                        },
                    },
                    status=status.HTTP_200_OK,
                )
            except User.DoesNotExist:
                logger.warning("Local token valid but user not found: %s", validated_token.get("user_id"))
                return Response(
                    {"valid": False, "source": "local", "details": {"detail": "User not found"}},
                    status=status.HTTP_200_OK,
                )

        except Exception as e:
            # Not a valid local token, try external
            logger.debug("Not a valid local token: %s", e)

        # Try to verify as external token
        try:
            # First check if token exists in our session database
            from api.models import UserSession

            try:
                session = UserSession.objects.select_related("user").get(access_token=token, is_active=True)

                # Check if token is expired
                if not session.is_token_expired():
                    payload = ExternalAuthService.decode_token_payload(token)

                    return Response(
                        {
                            "valid": True,
                            "source": "external",
                            "details": {
                                "user_id": session.user.external_id,
                                "username": session.user.username,
                                "exp": payload.get("exp"),
                                "iat": payload.get("iat"),
                            },
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    # Token expired in our database
                    session.deactivate()
                    return Response(
                        {"valid": False, "source": "external", "details": {"detail": "Token expired"}},
                        status=status.HTTP_200_OK,
                    )

            except UserSession.DoesNotExist:
                # Not in our database, verify with external API
                pass

            # Verify with external API
            is_valid = ExternalAuthService.verify_token(token)

            if is_valid:
                # Decode payload for details
                payload = ExternalAuthService.decode_token_payload(token)

                return Response(
                    {
                        "valid": True,
                        "source": "external",
                        "details": {
                            "user_id": payload.get("user_id"),
                            "exp": payload.get("exp"),
                            "iat": payload.get("iat"),
                        },
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"valid": False, "source": "external", "details": {"detail": "Token is invalid or expired"}},
                    status=status.HTTP_200_OK,
                )

        except AuthenticationFailed as e:
            logger.error("External token verification failed: %s", e)
            return Response(
                {"valid": False, "source": "unknown", "details": {"detail": "Token verification failed."}},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error("Token verification error: %s", e, exc_info=True)
            return Response(
                {"valid": False, "source": "unknown", "details": {"detail": "Verification failed"}},
                status=status.HTTP_200_OK,
            )


class TokenRefreshView(APIView):
    """
    Token refresh endpoint for both local and external tokens
    """

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Refresh access token",
        operation_description="Refresh access token using refresh token. Supports both local and external tokens.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["refresh"],
            properties={
                "refresh": openapi.Schema(type=openapi.TYPE_STRING, description="Refresh token"),
                "auth_type": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=["local", "external"],
                    description="Token type (optional, auto-detected if not provided)",
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Token refreshed successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "access": openapi.Schema(type=openapi.TYPE_STRING, description="New access token"),
                        "refresh": openapi.Schema(type=openapi.TYPE_STRING, description="New refresh token (local only)"),
                    },
                ),
            ),
            400: "Bad request - refresh token missing or invalid auth_type",
            401: "Unauthorized - invalid or expired refresh token",
        },
        tags=["auth"],
    )
    def post(self, request):
        """
        Refresh access token using refresh token

        Request Body:
            {
                "refresh": "refresh_token",
                "auth_type": "local" | "external"  # optional, auto-detected if not provided
            }

        Response:
            {
                "access": "new_access_token",
                "refresh": "new_refresh_token"  # only for local tokens with rotation
            }
        """
        refresh_token = request.data.get("refresh")
        auth_type = request.data.get("auth_type")  # 'local' or 'external'

        # Fallback: read refresh token from httpOnly cookie
        if not refresh_token:
            refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response({"detail": "No refresh token provided. Please login first.", "code": "no_refresh_token"}, status=status.HTTP_400_BAD_REQUEST)

        # If auth_type not specified, try to detect
        if not auth_type:
            # Try local first (SimplJWT tokens are typically longer)
            try:
                refresh = RefreshToken(refresh_token)
                auth_type = "local"
            except (InvalidToken, TokenError):
                # Not a local token, assume external
                auth_type = "external"

        # Handle local token refresh
        if auth_type == "local":
            try:
                refresh = RefreshToken(refresh_token)
                new_access_token = str(refresh.access_token)

                # If token rotation is enabled, get new refresh token
                new_refresh = str(refresh) if hasattr(refresh, "access_token") else None

                logger.info("Local token refreshed successfully")
                response = Response({"message": "Token refreshed"}, status=status.HTTP_200_OK)

                # Deliver tokens exclusively via httpOnly cookies
                set_auth_cookies(response, new_access_token, new_refresh)
                return response

            except (InvalidToken, TokenError) as e:
                logger.warning("Local token refresh failed: %s", e)
                return Response({"detail": "Your session has expired. Please login again.", "code": "invalid_refresh_token"}, status=status.HTTP_401_UNAUTHORIZED)

        # Handle external token refresh
        elif auth_type == "external":
            try:
                new_access_token = ExternalAuthService.refresh_token(refresh_token)

                # Update session if exists
                try:
                    session = UserSession.objects.get(refresh_token=refresh_token, is_active=True)

                    payload = ExternalAuthService.decode_token_payload(new_access_token)
                    session.access_token = new_access_token
                    session.token_expires_at = datetime.fromtimestamp(payload.get("exp", 0), tz=timezone.get_current_timezone())
                    session.save()

                    logger.info("External token refreshed for user: %s", session.user.username)

                except UserSession.DoesNotExist:
                    logger.warning("Session not found for external token refresh")

                response = Response({"message": "Token refreshed"}, status=status.HTTP_200_OK)

                # Deliver token exclusively via httpOnly cookie
                set_auth_cookies(response, new_access_token)
                return response

            except AuthenticationFailed as e:
                logger.warning("External token refresh failed: %s", e)
                return Response({"detail": "Your session has expired. Please login again.", "code": "invalid_refresh_token"}, status=status.HTTP_401_UNAUTHORIZED)

        else:
            return Response({"detail": 'Invalid auth_type. Must be "local" or "external"', "code": "invalid_auth_type"}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    Logout endpoint - deactivates sessions
    """

    @swagger_auto_schema(
        operation_summary="Logout user",
        operation_description="Logout current user and deactivate sessions. For external users, deactivates all active sessions. For local users, client should discard tokens.",
        responses={
            200: openapi.Response(
                description="Logout successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING, description="Success message"),
                    },
                ),
            ),
        },
        tags=["auth"],
    )
    def post(self, request):
        """
        Logout current user
        Deactivates session for external users
        For local users, client should discard tokens
        """
        user = request.user

        if isinstance(user, ExternalUser):
            # Log logout activity before deactivating sessions
            UserActivityLog.log_activity(user=user, action="logout", details={"logout_type": "manual"}, request=request)
            # Deactivate all active sessions for external user
            UserSession.objects.filter(user=user, is_active=True).update(is_active=False)
            logger.info("External user logged out: %s", user.username)
        else:
            # For local users, just log the logout
            logger.info("Local user logged out: %s", user.username)

        response = Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)

        # Clear httpOnly auth cookies
        clear_auth_cookies(response)
        return response


class ExchangeExternalTokenView(APIView):
    """
    Exchange an external access token for httpOnly session cookies.
    Used when an external app redirects the user with a non-httpOnly
    access_token cookie; the frontend reads it and POSTs here to set
    secure httpOnly cookies for all subsequent API calls.
    """

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Exchange external token for httpOnly cookies",
        operation_description="Validates an external access token and sets httpOnly session cookies.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["token"],
            properties={
                "token": openapi.Schema(type=openapi.TYPE_STRING, description="External access token"),
            },
        ),
        responses={
            200: "Cookie set + user data returned",
            401: "Invalid token",
        },
        tags=["auth"],
    )
    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"detail": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_info = ExternalAuthService.get_user_info(token)
        except Exception:
            return Response({"detail": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

        # Get or create user
        user, _ = ExternalUser.objects.get_or_create(
            external_id=user_info["id"],
            defaults={
                "username": user_info["username"],
                "email": user_info.get("email", ""),
                "date_joined": user_info.get("date_joined", timezone.now()),
            },
        )
        user.update_from_external_api(user_info)

        # Ensure an active session exists
        try:
            UserSession.objects.get(access_token=token, is_active=True)
        except UserSession.DoesNotExist:
            payload = ExternalAuthService.decode_token_payload(token)
            UserSession.objects.create(
                user=user,
                access_token=token,
                refresh_token="",
                token_issued_at=datetime.fromtimestamp(payload.get("iat", 0), tz=timezone.get_current_timezone()),
                token_expires_at=datetime.fromtimestamp(payload.get("exp", 0), tz=timezone.get_current_timezone()),
                ip_address=request.META.get("REMOTE_ADDR", ""),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )

        def format_datetime(dt_value):
            if dt_value is None:
                return None
            if isinstance(dt_value, str):
                return dt_value
            if hasattr(dt_value, "isoformat"):
                return dt_value.isoformat()
            return str(dt_value)

        response = Response(
            {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email or "",
                    "first_name": user.first_name or "",
                    "last_name": user.last_name or "",
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                    "is_active": user.is_active,
                    "is_ptb_admin": user.is_ptb_admin,
                    "role": getattr(user, "role", "user"),
                    "worker_id": user.worker_id or "",
                    "menu_permissions": user.menu_permissions,
                    "event_reminders_enabled": user.event_reminders_enabled,
                    "preferred_language": getattr(user, "preferred_language", "en"),
                    "permission_updated_at": format_datetime(user.permission_updated_at),
                    "employee_id": None,
                    "department_id": None,
                    "date_joined": format_datetime(user.date_joined),
                    "last_login": format_datetime(user.last_login),
                    "groups": user.groups_cache,
                    "permissions": user.permissions_cache,
                },
            },
            status=status.HTTP_200_OK,
        )

        set_auth_cookies(response, token)
        return response


class CurrentUserView(APIView):
    """
    Get current authenticated user information
    """

    @swagger_auto_schema(
        operation_summary="Get current user",
        operation_description="Get current authenticated user information. Works for both local and external users.",
        responses={
            200: openapi.Response(
                description="User information retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "username": openapi.Schema(type=openapi.TYPE_STRING),
                        "email": openapi.Schema(type=openapi.TYPE_STRING),
                        "first_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "last_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "is_staff": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "is_superuser": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "employee_id": openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True),
                        "department_id": openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True),
                    },
                ),
            ),
            401: "Unauthorized - authentication required",
            500: "Internal server error",
        },
        tags=["auth"],
    )
    def get(self, request):
        """
        Get current user details
        Works for both local and external users
        """
        try:
            user = request.user

            # Check if user is authenticated
            if not user or not user.is_authenticated:
                logger.warning("Unauthenticated user trying to access /auth/me/: %s", user)
                return Response({"detail": "auth required"}, status=status.HTTP_401_UNAUTHORIZED)

            logger.info("CurrentUserView called for user: %s, type: %s", user.username, type(user).__name__)

            # Check if external user
            if isinstance(user, ExternalUser):
                logger.info("Processing external user: %s (ID: %s)", user.username, user.id)
                try:
                    # Build response safely with ALL required fields
                    permission_updated = getattr(user, "permission_updated_at", None)
                    user_data = {
                        "id": getattr(user, "id", None),
                        "username": getattr(user, "username", ""),
                        "email": getattr(user, "email", "") or "",
                        "first_name": getattr(user, "first_name", "") or "",
                        "last_name": getattr(user, "last_name", "") or "",
                        "is_staff": getattr(user, "is_staff", False),
                        "is_superuser": getattr(user, "is_superuser", False),
                        "is_active": getattr(user, "is_active", True),
                        # CRITICAL: Include external user specific fields
                        "worker_id": getattr(user, "worker_id", None),
                        "is_ptb_admin": getattr(user, "is_ptb_admin", False),
                        "role": getattr(user, "role", "user"),
                        "menu_permissions": getattr(user, "menu_permissions", []),
                        "event_reminders_enabled": getattr(user, "event_reminders_enabled", True),
                        "preferred_language": getattr(user, "preferred_language", "en"),
                        "permission_updated_at": permission_updated.isoformat() if permission_updated else None,
                        "employee_id": None,
                        "department_id": None,
                    }
                    logger.info("Successfully built external user data for: %s, worker_id=%s, is_ptb_admin=%s, menu_permissions_type=%s", user.username, user_data["worker_id"], user_data["is_ptb_admin"], type(user_data["menu_permissions"]).__name__)
                    return Response(user_data, status=status.HTTP_200_OK)
                except Exception as e:
                    logger.error("Error building external user response for %s: %s", user.username, e, exc_info=True)
                    return Response({"detail": "Failed to build user data. Check server logs for details."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                # Local Django user
                logger.info("Processing local user: %s (ID: %s)", user.username, user.id)
                try:
                    # For local users, check if matches superadmin criteria
                    # This ensures superadmin-role users can access SuperAdmin pages even as a local user
                    is_super_admin = is_superadmin_user(user)
                    permission_updated = getattr(user, "permission_updated_at", None)
                    user_data = {
                        "id": getattr(user, "id", None),
                        "username": getattr(user, "username", ""),
                        "email": getattr(user, "email", "") or "",
                        "first_name": getattr(user, "first_name", "") or "",
                        "last_name": getattr(user, "last_name", "") or "",
                        "is_active": getattr(user, "is_active", True),
                        "is_staff": getattr(user, "is_staff", False),
                        "is_superuser": getattr(user, "is_superuser", False),
                        # Include worker_id, is_ptb_admin, menu_permissions for consistency with external users
                        "worker_id": getattr(user, "worker_id", None),
                        "is_ptb_admin": getattr(user, "is_ptb_admin", False) or is_super_admin,
                        "role": getattr(user, "role", "developer" if is_super_admin else "user"),
                        "menu_permissions": getattr(user, "menu_permissions", {}),
                        "event_reminders_enabled": getattr(user, "event_reminders_enabled", True),
                        "preferred_language": getattr(user, "preferred_language", "en"),
                        "permission_updated_at": permission_updated.isoformat() if permission_updated else None,
                        "employee_id": None,
                        "department_id": None,
                    }
                    logger.info("Successfully built local user data for: %s, is_super_admin=%s", user.username, is_super_admin)
                    return Response(user_data, status=status.HTTP_200_OK)
                except Exception as e:
                    logger.error("Error building local user response for %s: %s", user.username, e, exc_info=True)
                    return Response({"detail": "Failed to build user data. Check server logs for details."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error("Unexpected error in CurrentUserView.get(): %s", e, exc_info=True)
            return Response({"detail": "Internal server error. Check server logs for details."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request):
        """Update current user preferences (e.g. event_reminders_enabled)"""
        try:
            user = request.user
            if not user or not user.is_authenticated:
                return Response({"detail": "auth required"}, status=status.HTTP_401_UNAUTHORIZED)

            if not isinstance(user, ExternalUser):
                return Response({"detail": "Only external users can update preferences"}, status=status.HTTP_400_BAD_REQUEST)

            allowed_fields = {"event_reminders_enabled", "preferred_language"}
            updated_fields = []
            for field in allowed_fields:
                if field in request.data:
                    setattr(user, field, request.data[field])
                    updated_fields.append(field)

            if updated_fields:
                user.save(update_fields=updated_fields + ["updated_at"])
                logger.info("User %s updated preferences: %s", user.username, updated_fields)

            return Response({"status": "ok", "updated": updated_fields}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Error updating user preferences: %s", e, exc_info=True)
            return Response({"detail": "An unexpected error occurred. Please try again or contact support."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
