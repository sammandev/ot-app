import logging
from datetime import datetime, time

from django.contrib.auth import get_user_model
from django.utils.dateparse import parse_date
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import (
    ExternalUser,
    Notification,
    ReleaseNote,
    SMBConfiguration,
    SystemConfiguration,
    UserActivityLog,
    UserReport,
)
from ..pagination import StandardPageNumberPagination
from ..permissions import IsSuperAdmin
from ..serializers import (
    ReleaseNoteSerializer,
    SMBConfigurationSerializer,
    SystemConfigurationSerializer,
    UserActivityLogSerializer,
    UserReportAdminSerializer,
    UserReportSerializer,
)
from ..serializers_access import UserAccessSerializer, UserAccessUpdateSerializer
from .helpers import get_employee_for_user, is_developer_user, is_ptb_admin, is_superadmin_user  # noqa: F401

logger = logging.getLogger(__name__)
User = get_user_model()


class UserAccessViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user access control (PTB Admin, Superuser, Staff)
    Only accessible by users with the 'developer' or 'superadmin' role.
    """

    queryset = ExternalUser.objects.all()
    serializer_class = UserAccessSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @swagger_auto_schema(
        operation_summary="List all users with access control",
        responses={200: UserAccessSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get user access details",
        responses={200: UserAccessSerializer()},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update user access permissions",
        request_body=UserAccessUpdateSerializer,
        responses={200: UserAccessSerializer()},
    )
    def partial_update(self, request, *args, **kwargs):
        from django.utils import timezone

        instance = self.get_object()

        # Prevent modifying developer's permissions (highest privilege, protected)
        if is_developer_user(instance):
            return Response({"detail": "Cannot modify developer permissions"}, status=status.HTTP_403_FORBIDDEN)

        # Non-developer superadmins cannot change role field (only developer can)
        if "role" in request.data and not is_developer_user(request.user):
            return Response({"detail": "Only developer can change user roles"}, status=status.HTTP_403_FORBIDDEN)

        # Track if we need to force logout the user
        should_force_logout = False

        # Handle role change (only developer can do this)
        if "role" in request.data:
            new_role = request.data["role"]
            if new_role not in ("developer", "superadmin", "user"):
                return Response({"detail": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)
            # Cannot grant developer role to others
            if new_role == "developer":
                return Response({"detail": "Cannot grant developer role"}, status=status.HTTP_403_FORBIDDEN)
            if instance.role != new_role:
                should_force_logout = True
            instance.role = new_role

        # Update only the allowed fields
        if "is_ptb_admin" in request.data:
            if instance.is_ptb_admin != request.data["is_ptb_admin"]:
                should_force_logout = True
            instance.is_ptb_admin = request.data["is_ptb_admin"]
        if "is_superuser" in request.data:
            if instance.is_superuser != request.data["is_superuser"]:
                should_force_logout = True
            instance.is_superuser = request.data["is_superuser"]
        if "is_staff" in request.data:
            if instance.is_staff != request.data["is_staff"]:
                should_force_logout = True
            instance.is_staff = request.data["is_staff"]
        if "is_active" in request.data:
            if instance.is_active != request.data["is_active"]:
                should_force_logout = True
            instance.is_active = request.data["is_active"]
        if "menu_permissions" in request.data:
            if instance.menu_permissions != request.data["menu_permissions"]:
                should_force_logout = True
            instance.menu_permissions = request.data["menu_permissions"]
        if "event_reminders_enabled" in request.data:
            instance.event_reminders_enabled = request.data["event_reminders_enabled"]
            # Preference-only change: still push WebSocket so UI updates in real-time
            should_force_logout = True

        # If any permission-related field changed, update the timestamp and notify via WebSocket
        if should_force_logout:
            instance.permission_updated_at = timezone.now()
            logger.info("User %s permissions updated at %s", instance.username, instance.permission_updated_at)

        instance.save()

        serializer = self.get_serializer(instance)

        # Send real-time permission update via WebSocket
        if should_force_logout:
            try:
                from ..consumers import send_permission_update_to_user

                send_permission_update_to_user(instance.id, serializer.data)
                logger.info("WebSocket permission update sent to user %s (ID: %s)", instance.username, instance.id)
            except Exception as e:
                logger.warning("Failed to send WebSocket permission update: %s", e)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Prevent deletion of user records"""
        return Response({"detail": "User records cannot be deleted"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class SystemConfigurationView(APIView):
    """
    Get or Update System Configuration.
    Singleton logic.
    GET is public (app name/version is non-sensitive, needed on login page).
    PATCH requires Super Admin.
    POST tab-icon/ for favicon upload.
    """

    permission_classes = [AllowAny]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        config, created = SystemConfiguration.objects.get_or_create(pk=1)  # Ensure existing
        serializer = SystemConfigurationSerializer(config, context={"request": request})
        return Response(serializer.data)

    def patch(self, request):
        # Strict Super Admin Check
        user = request.user
        is_super_admin = is_superadmin_user(user)

        if not is_super_admin:
            return Response({"detail": "Only Super Admin can edit configuration."}, status=status.HTTP_403_FORBIDDEN)

        config, created = SystemConfiguration.objects.get_or_create(pk=1)

        # Handle tab_icon file upload from multipart form data
        data = request.data.copy() if hasattr(request.data, "copy") else dict(request.data)
        if "tab_icon" in request.FILES:
            data["tab_icon"] = request.FILES["tab_icon"]

        serializer = SystemConfigurationSerializer(config, data=data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            # Log activity
            UserActivityLog.log_activity(user=request.user, action="update", resource="system_configuration", resource_id=1, details={"changes": {k: str(v) for k, v in request.data.items()}}, request=request)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Remove the tab icon (reset to default)."""
        user = request.user
        if not is_superadmin_user(user):
            return Response({"detail": "Only Super Admin can edit configuration."}, status=status.HTTP_403_FORBIDDEN)

        config, _ = SystemConfiguration.objects.get_or_create(pk=1)
        if config.tab_icon:
            config.tab_icon.delete(save=False)
            config.tab_icon = None
            config.save()
        serializer = SystemConfigurationSerializer(config, context={"request": request})
        return Response(serializer.data)


class UserActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only view for user activity logs.
    Only accessible to super admins.
    Includes a custom action for frontend page-view tracking.
    """

    permission_classes = [IsAuthenticated]
    queryset = UserActivityLog.objects.none()  # Overridden by get_queryset
    serializer_class = UserActivityLogSerializer
    pagination_class = StandardPageNumberPagination

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return UserActivityLog.objects.none()

        user = self.request.user
        if not is_superadmin_user(user):
            return UserActivityLog.objects.none()

        queryset = UserActivityLog.objects.select_related("user").all()

        # Filter by user if specified
        user_id = self.request.query_params.get("user_id")
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Filter by action if specified
        action = self.request.query_params.get("action")
        if action:
            queryset = queryset.filter(action=action)

        # Filter by resource if specified
        resource = self.request.query_params.get("resource")
        if resource:
            queryset = queryset.filter(resource__icontains=resource)

        # Filter by date range using datetime bounds to allow index usage
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if start_date:
            parsed_start = parse_date(start_date)
            if parsed_start:
                queryset = queryset.filter(timestamp__gte=datetime.combine(parsed_start, time.min))
        if end_date:
            parsed_end = parse_date(end_date)
            if parsed_end:
                queryset = queryset.filter(timestamp__lte=datetime.combine(parsed_end, time.max))

        return queryset

    @action(detail=False, methods=["post"], url_path="log-page-view")
    def log_page_view(self, request):
        """
        Log a page view from the frontend.
        Any authenticated user can log their own page views.
        Payload: { "page": "/dashboard", "title": "Dashboard" }
        """
        user = request.user
        ext_user = None

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
            return Response({"detail": "User not resolvable"}, status=status.HTTP_400_BAD_REQUEST)

        page = request.data.get("page", "")
        title = request.data.get("title", "")

        if not page:
            return Response({"detail": "page is required"}, status=status.HTTP_400_BAD_REQUEST)

        UserActivityLog.log_activity(
            user=ext_user,
            action="page_view",
            resource=page,
            details={"title": title} if title else {},
            request=request,
        )

        return Response({"status": "ok"}, status=status.HTTP_201_CREATED)


class SMBConfigurationViewSet(viewsets.ModelViewSet):
    """
    CRUD for SMB configurations. Super admin only.
    Supports multiple configs — one marked `is_active` is used for file uploads.
    Custom actions: activate (POST), test (POST).
    """

    permission_classes = [IsAuthenticated]
    serializer_class = SMBConfigurationSerializer
    queryset = SMBConfiguration.objects.all()

    def list(self, request, *args, **kwargs):
        if not is_superadmin_user(request.user):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        if not is_superadmin_user(request.user):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        return super().retrieve(request, *args, **kwargs)

    def perform_create(self, serializer):
        if not is_superadmin_user(self.request.user):
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Only Super Admin can create SMB configs.")
        instance = serializer.save()
        # Invalidate cached SMB config in ExcelGenerator
        from .utils.excel_generator import ExcelGenerator

        ExcelGenerator.invalidate_smb_cache()
        UserActivityLog.log_activity(
            user=self.request.user,
            action="create",
            resource="smb_configuration",
            resource_id=instance.id,
            details={"name": instance.name, "server": instance.server},
            request=self.request,
        )

    def perform_update(self, serializer):
        if not is_superadmin_user(self.request.user):
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Only Super Admin can update SMB configs.")
        instance = serializer.save()
        from .utils.excel_generator import ExcelGenerator

        ExcelGenerator.invalidate_smb_cache()
        UserActivityLog.log_activity(
            user=self.request.user,
            action="update",
            resource="smb_configuration",
            resource_id=instance.id,
            details={"fields": list(self.request.data.keys())},
            request=self.request,
        )

    def perform_destroy(self, instance):
        if not is_superadmin_user(self.request.user):
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Only Super Admin can delete SMB configs.")
        from .utils.excel_generator import ExcelGenerator

        ExcelGenerator.invalidate_smb_cache()
        UserActivityLog.log_activity(
            user=self.request.user,
            action="delete",
            resource="smb_configuration",
            resource_id=instance.id,
            details={"name": instance.name},
            request=self.request,
        )
        instance.delete()

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, pk=None):
        """Set this config as the active one (deactivates all others)."""
        if not is_superadmin_user(request.user):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        config = self.get_object()
        config.is_active = True
        config.save()  # save() deactivates others
        from .utils.excel_generator import ExcelGenerator

        ExcelGenerator.invalidate_smb_cache()
        UserActivityLog.log_activity(
            user=request.user,
            action="update",
            resource="smb_configuration",
            resource_id=config.id,
            details={"action": "activate", "name": config.name},
            request=request,
        )
        return Response(SMBConfigurationSerializer(config).data)

    @action(detail=True, methods=["post"], url_path="test")
    def test_connection(self, request, pk=None):
        """Test SMB connection for a specific config."""
        if not is_superadmin_user(request.user):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        config = self.get_object()
        password = config.get_password()
        if not config.server or not config.username:
            return Response({"success": False, "detail": "Missing host or username"})
        if not password:
            return Response({"success": False, "detail": "Password could not be decrypted. Please re-enter the password and save before testing."})

        try:
            import socket

            from smb.SMBConnection import SMBConnection

            client_name = socket.gethostname()
            conn = SMBConnection(
                config.username,
                password,
                client_name,
                config.server,
                use_ntlm_v2=True,
                is_direct_tcp=True,
            )
            connected = conn.connect(config.server, int(config.port or 445), timeout=10)
            if connected:
                shares = conn.listShares()
                share_names = [s.name for s in shares]
                conn.close()
                return Response(
                    {
                        "success": True,
                        "message": f"Connected successfully. Found {len(shares)} shares.",
                        "shares": share_names,
                    }
                )
            else:
                return Response({"success": False, "detail": "Connection refused"})
        except Exception:
            return Response({"success": False, "detail": "Connection test failed. Check configuration and try again."})


# ===========================================================================
# User Reports (Bug reports & Feature requests)
# ===========================================================================


class UserReportViewSet(viewsets.ModelViewSet):
    """
    Users can create and view their own reports.
    Super admin can see all reports and update status.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserReportSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return UserReport.objects.none()

        user = self.request.user
        qs = UserReport.objects.select_related("reporter")

        if is_superadmin_user(user):
            # Super admin sees all
            report_type = self.request.query_params.get("report_type")
            if report_type:
                qs = qs.filter(report_type=report_type)

            report_status = self.request.query_params.get("status")
            if report_status:
                qs = qs.filter(status=report_status)

            priority = self.request.query_params.get("priority")
            if priority:
                qs = qs.filter(priority=priority)
        else:
            # Regular users see only their own reports
            qs = qs.filter(reporter=user)

        return qs

    def get_serializer_class(self):
        if self.action in ("partial_update", "update") and is_superadmin_user(self.request.user):
            return UserReportAdminSerializer
        return UserReportSerializer

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)
        UserActivityLog.log_activity(
            user=self.request.user,
            action="create",
            resource="user_report",
            resource_id=serializer.instance.id,
            details={"type": serializer.instance.report_type, "title": serializer.instance.title},
            request=self.request,
        )

        # Notify superadmin(s) about the new report
        from ..consumers import send_notification_to_user

        report = serializer.instance
        reporter_name = self.request.user.username
        type_label = report.get_report_type_display()
        title = f"New {type_label}"
        message = f'{reporter_name} submitted a {type_label.lower()}: "{report.title}"'

        # Find superadmin users and create DB notifications + WS push
        superadmin_users = list(ExternalUser.objects.filter(is_active=True, role__in=("developer", "superadmin")))
        if superadmin_users:
            admin_notifs = [Notification(recipient=admin, title=title, message=message, event_type="user_report") for admin in superadmin_users]
            created_notifs = Notification.objects.bulk_create(admin_notifs)
            for notif, admin in zip(created_notifs, superadmin_users, strict=True):
                send_notification_to_user(
                    admin.id,
                    {
                        "id": notif.id,
                        "title": title,
                        "message": message,
                        "event_type": "user_report",
                        "event_id": None,
                        "is_read": False,
                        "created_at": notif.created_at.isoformat(),
                    },
                )

    def perform_update(self, serializer):
        instance = serializer.instance
        user = self.request.user
        is_admin = is_superadmin_user(user)
        # Non-admin users can only edit their own open reports
        if not is_admin:
            if instance.reporter_id != user.id:
                raise PermissionDenied("You can only edit your own reports.")
            if instance.status != "open":
                raise PermissionDenied("You can only edit reports that are still open.")

        # Track what changed before saving (for notification message)
        old_status = instance.status
        old_admin_notes = instance.admin_notes

        serializer.save()
        UserActivityLog.log_activity(
            user=self.request.user,
            action="update",
            resource="user_report",
            resource_id=serializer.instance.id,
            details={"status": serializer.instance.status},
            request=self.request,
        )

        # If superadmin updated the report, notify the reporter
        if is_admin and instance.reporter_id != user.id:
            from ..consumers import send_notification_to_user

            report = serializer.instance
            changes = []
            if report.status != old_status:
                changes.append(f'status changed to "{report.get_status_display()}"')
            if report.admin_notes != old_admin_notes and report.admin_notes:
                changes.append("admin added a note")
            change_text = " and ".join(changes) if changes else "updated"

            title = "Report Updated"
            message = f'Your {report.get_report_type_display().lower()} "{report.title}" was {change_text} by admin.'

            notif = Notification.objects.create(
                recipient_id=report.reporter_id,
                title=title,
                message=message,
                event_type="user_report",
            )
            send_notification_to_user(
                report.reporter_id,
                {
                    "id": notif.id,
                    "title": title,
                    "message": message,
                    "event_type": "user_report",
                    "event_id": None,
                    "is_read": False,
                    "created_at": notif.created_at.isoformat(),
                },
            )

    def perform_destroy(self, instance):
        user = self.request.user
        # Non-admin users can only delete their own open reports
        if not is_superadmin_user(user):
            if instance.reporter_id != user.id:
                raise PermissionDenied("You can only delete your own reports.")
            if instance.status != "open":
                raise PermissionDenied("You can only delete reports that are still open.")
        UserActivityLog.log_activity(
            user=user,
            action="delete",
            resource="user_report",
            resource_id=instance.id,
            details={"type": instance.report_type, "title": instance.title},
            request=self.request,
        )
        instance.delete()

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        """Return aggregate stats for super admin dashboard."""
        if not is_superadmin_user(request.user):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        from django.db.models import Count

        qs = UserReport.objects.all()
        by_status = dict(qs.values_list("status").annotate(c=Count("id")).values_list("status", "c"))
        by_type = dict(qs.values_list("report_type").annotate(c=Count("id")).values_list("report_type", "c"))
        return Response(
            {
                "total": qs.count(),
                "by_status": by_status,
                "by_type": by_type,
            }
        )


# ===========================================================================
# Release Notes / Version History
# ===========================================================================


class ReleaseNoteViewSet(viewsets.ModelViewSet):
    """
    Public read for published release notes.
    Super admin can create / update / delete.
    Auto-syncs SystemConfiguration version + build_date from the latest release.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ReleaseNoteSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return ReleaseNote.objects.none()

        qs = ReleaseNote.objects.select_related("created_by")
        if not is_superadmin_user(self.request.user):
            qs = qs.filter(published=True)
        return qs

    @staticmethod
    def _sync_system_version():
        """Update SystemConfiguration version + build_date from the latest published ReleaseNote."""
        latest = ReleaseNote.objects.filter(published=True).order_by("-release_date", "-created_at").values("version", "release_date").first()
        if latest:
            from calendar import month_name

            rd = latest["release_date"]
            build_date = f"{month_name[rd.month]} {rd.year}"
            SystemConfiguration.objects.update_or_create(
                pk=1,
                defaults={"version": latest["version"], "build_date": build_date},
            )

    def perform_create(self, serializer):
        if not is_superadmin_user(self.request.user):
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Only Super Admin can create release notes.")
        serializer.save(created_by=self.request.user)
        self._sync_system_version()

    def perform_update(self, serializer):
        if not is_superadmin_user(self.request.user):
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Only Super Admin can update release notes.")
        serializer.save()
        self._sync_system_version()

    def perform_destroy(self, instance):
        if not is_superadmin_user(self.request.user):
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Only Super Admin can delete release notes.")
        instance.delete()
        self._sync_system_version()
