import logging
import uuid
from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.db import IntegrityError, models, transaction
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from ..models import (
    Employee,
    EmployeeLeave,
    ExternalUser,
    Holiday,
    Notification,
)
from ..pagination import DynamicPagination
from ..serializers import (
    EmployeeLeaveBatchCreateSerializer,
    EmployeeLeaveBatchDeleteSerializer,
    EmployeeLeaveBatchUpdateSerializer,
    EmployeeLeaveSerializer,
    HolidaySerializer,
)
from ..services.external_auth import ExternalAuthService, ExternalServiceError
from .helpers import get_employee_for_user, is_developer_user, is_ptb_admin, is_superadmin_user  # noqa: F401
from ..services.leave_notification_service import format_actor_timestamp, resolve_leave_preview_token, rotate_leave_preview_token

logger = logging.getLogger(__name__)
User = get_user_model()


def _external_agent_names(external_agents):
    names = []
    for agent in external_agents or []:
        if not isinstance(agent, dict):
            continue
        display_name = str(agent.get("username") or agent.get("email") or agent.get("worker_id") or "").strip()
        if display_name:
            names.append(display_name)
    return names


class HolidayViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing holidays on the calendar.
    Separate from CalendarEvent for simpler holiday management.
    """

    permission_classes = [IsAuthenticated]
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    pagination_class = DynamicPagination
    ordering = ["date"]

    def get_queryset(self):
        queryset = Holiday.objects.select_related("created_by")

        # Filter by year if provided
        year = self.request.query_params.get("year")
        if year:
            try:
                year = int(year)
                queryset = queryset.filter(date__year=year)
            except ValueError:
                pass

        # Filter by month if provided
        month = self.request.query_params.get("month")
        if month:
            try:
                month = int(month)
                queryset = queryset.filter(date__month=month)
            except ValueError:
                pass

        # Filter by date range
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        return queryset.order_by("date")

    def perform_create(self, serializer):
        """Set the created_by field to the current user"""
        user = self.request.user
        if isinstance(user, ExternalUser):
            instance = serializer.save(created_by=user)
        else:
            # Try to find matching ExternalUser
            ext_user = ExternalUser.objects.filter(username=user.username).first()
            instance = serializer.save(created_by=ext_user)
        # Broadcast calendar update
        try:
            from ..consumers import broadcast_calendar_update

            broadcast_calendar_update("created", "holiday", HolidaySerializer(instance).data)
        except Exception as e:
            logger.debug("Calendar broadcast failed (non-critical): %s", e)

    def perform_update(self, serializer):
        instance = serializer.save()
        try:
            from ..consumers import broadcast_calendar_update

            broadcast_calendar_update("updated", "holiday", HolidaySerializer(instance).data)
        except Exception as e:
            logger.debug("Calendar broadcast failed (non-critical): %s", e)

    def perform_destroy(self, instance):
        holiday_id = instance.id
        instance.delete()
        try:
            from ..consumers import broadcast_calendar_update

            broadcast_calendar_update("deleted", "holiday", {"id": holiday_id})
        except Exception as e:
            logger.debug("Calendar broadcast failed (non-critical): %s", e)


class EmployeeLeaveViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing employee leaves.
    Includes agent coverage tracking.
    """

    permission_classes = [IsAuthenticated]
    queryset = EmployeeLeave.objects.all()
    serializer_class = EmployeeLeaveSerializer
    pagination_class = DynamicPagination
    ordering = ["date", "employee__name"]

    EXTERNAL_LOOKUP_MIN_KEYWORD_LENGTH = 2

    def _resolve_external_user(self, user):
        if isinstance(user, ExternalUser):
            return user
        username = getattr(user, "username", None)
        if not username:
            return None
        return ExternalUser.objects.filter(username=username).first()

    @staticmethod
    def _resolve_preview_employee_email(employee):
        employee_id = str(getattr(employee, "emp_id", "") or "").strip()
        if not employee_id:
            return "-"

        matched_emails = {}
        for raw_email in (
            ExternalUser.objects.filter(worker_id=employee_id, is_active=True)
            .exclude(email__isnull=True)
            .exclude(email="")
            .values_list("email", flat=True)
        ):
            email = str(raw_email or "").strip()
            if not email:
                continue
            matched_emails.setdefault(email.lower(), email)

        if len(matched_emails) != 1:
            return "-"

        return next(iter(matched_emails.values()))

    def _get_external_lookup_token(self, request):
        if not isinstance(request.user, ExternalUser):
            return None

        if isinstance(request.auth, str) and request.auth.strip():
            return request.auth

        session = request.user.sessions.filter(is_active=True).order_by("-created_at").first()
        if session is None or session.is_token_expired():
            return None

        return session.access_token

    @staticmethod
    def _normalize_external_lookup_results(results):
        normalized_results = []
        for item in results:
            employee = item.get("employee") or {}
            normalized_results.append(
                {
                    "username": item.get("username", ""),
                    "email": item.get("email", ""),
                    "worker_id": employee.get("worker_id", ""),
                    "site": employee.get("site", ""),
                    "source": "external_lookup",
                }
            )
        return normalized_results

    def _queue_leave_email_notification(self, leave_ids, action, actor_username):
        from ..tasks import dispatch_leave_notification_email

        dispatch_leave_notification_email(leave_ids=leave_ids, action=action, actor_username=actor_username)

    def _can_manage_leave(self, request_user, leave):
        if is_superadmin_user(request_user) or is_ptb_admin(request_user):
            return True

        external_user = self._resolve_external_user(request_user)
        return external_user is not None and leave.created_by_id == external_user.id

    def _assert_can_manage_leaves(self, request_user, leaves):
        if all(self._can_manage_leave(request_user, leave) for leave in leaves):
            return
        raise PermissionDenied("Only PTB Admins or the user who created this leave can edit or delete it.")

    def _broadcast_leave_batch_changes(self, *, created_ids=None, updated_ids=None, deleted_ids=None):
        created_ids = created_ids or []
        updated_ids = updated_ids or []
        deleted_ids = deleted_ids or []

        def _broadcast():
            from ..consumers import broadcast_calendar_update

            if created_ids:
                for leave_obj in (
                    EmployeeLeave.objects.filter(pk__in=created_ids)
                    .select_related("employee", "employee__department", "created_by")
                    .prefetch_related(models.Prefetch("agents", queryset=Employee.objects.select_related("department")))
                    .order_by("date", "employee__name")
                ):
                    try:
                        broadcast_calendar_update("created", "leave", EmployeeLeaveSerializer(leave_obj).data)
                    except Exception as exc:
                        logger.debug("Calendar broadcast failed (non-critical): %s", exc)

            if updated_ids:
                for leave_obj in (
                    EmployeeLeave.objects.filter(pk__in=updated_ids)
                    .select_related("employee", "employee__department", "created_by")
                    .prefetch_related(models.Prefetch("agents", queryset=Employee.objects.select_related("department")))
                    .order_by("date", "employee__name")
                ):
                    try:
                        broadcast_calendar_update("updated", "leave", EmployeeLeaveSerializer(leave_obj).data)
                    except Exception as exc:
                        logger.debug("Calendar broadcast failed (non-critical): %s", exc)

            for leave_id in deleted_ids:
                try:
                    broadcast_calendar_update("deleted", "leave", {"id": leave_id})
                except Exception as exc:
                    logger.debug("Calendar broadcast failed (non-critical): %s", exc)

        transaction.on_commit(_broadcast)

    @staticmethod
    def _rotate_leave_preview_token_on_commit(batch_key):
        if not batch_key:
            return

        transaction.on_commit(lambda: rotate_leave_preview_token(batch_key))

    def _rotate_leave_preview_tokens_on_commit(self, batch_keys):
        unique_batch_keys = [batch_key for batch_key in OrderedDict((key, True) for key in batch_keys if key).keys()]
        for batch_key in unique_batch_keys:
            self._rotate_leave_preview_token_on_commit(batch_key)

    def _schedule_leave_created_side_effects(self, leave, request_user, send_email=True):
        from ..consumers import send_notification_to_user

        leave_id = leave.id
        actor_username = getattr(request_user, "username", None) or "Unknown"

        def _send_leave_notifications():
            from ..consumers import broadcast_calendar_update

            leave_obj = EmployeeLeave.objects.get(pk=leave_id)
            employee_name = leave_obj.employee.name
            leave_date = leave_obj.date.strftime("%B %d, %Y")

            agent_employees = list(leave_obj.agents.all())
            structured_agent_names = [agent.name for agent in agent_employees]
            external_agent_names = _external_agent_names(leave_obj.external_agents)
            custom_agent_names = [name.strip() for name in (leave_obj.agent_names or "").split(",") if name.strip()]
            agent_names = structured_agent_names + external_agent_names + custom_agent_names
            agent_names_str = ", ".join(agent_names) if agent_names else "None assigned"

            title = "New Leave Request"
            message = f"{employee_name} has taken leave on {leave_date}.\nAgent(s): {agent_names_str}\nSubmitted by {actor_username}."

            ptb_admins = list(ExternalUser.objects.filter(is_ptb_admin=True, is_active=True))
            admin_notifs = [Notification(recipient=admin, title=title, message=message, event_type="leave") for admin in ptb_admins]
            if admin_notifs:
                created_admin = Notification.objects.bulk_create(admin_notifs)
                for notif, admin in zip(created_admin, ptb_admins, strict=True):
                    send_notification_to_user(admin.id, {"id": notif.id, "title": title, "message": message, "event_type": "leave", "event_id": None, "is_read": False, "created_at": notif.created_at.isoformat()})

            if agent_employees:
                agent_emp_ids = [agent.emp_id for agent in agent_employees if agent.emp_id]
                agent_users = {user.worker_id.lower(): user for user in ExternalUser.objects.filter(worker_id__in=agent_emp_ids, is_active=True)} if agent_emp_ids else {}

                agent_title = "Agent Assignment"
                agent_notifs = []
                agent_ws = []
                for agent_employee in agent_employees:
                    if not agent_employee.emp_id:
                        continue
                    agent_user = agent_users.get(agent_employee.emp_id.lower())
                    if agent_user:
                        agent_message = f"You have been assigned as agent for {employee_name} on {leave_date}."
                        agent_notifs.append(Notification(recipient=agent_user, title=agent_title, message=agent_message, event_type="leave"))
                        agent_ws.append((agent_user.id, agent_title, agent_message))

                if agent_notifs:
                    created_agents = Notification.objects.bulk_create(agent_notifs)
                    for notif, (uid, atitle, amsg) in zip(created_agents, agent_ws, strict=True):
                        send_notification_to_user(uid, {"id": notif.id, "title": atitle, "message": amsg, "event_type": "leave", "event_id": None, "is_read": False, "created_at": notif.created_at.isoformat()})

            try:
                broadcast_calendar_update("created", "leave", EmployeeLeaveSerializer(leave_obj).data)
            except Exception as exc:
                logger.debug("Calendar broadcast failed (non-critical): %s", exc)

            if send_email:
                self._queue_leave_email_notification([leave_id], "created", actor_username)

        transaction.on_commit(_send_leave_notifications)

    def _schedule_leave_updated_side_effects(self, leave, request_user):
        leave_id = leave.id
        actor_username = getattr(request_user, "username", None) or "Unknown"

        def _send_leave_update_notifications():
            from ..consumers import broadcast_calendar_update

            leave_obj = EmployeeLeave.objects.get(pk=leave_id)
            try:
                broadcast_calendar_update("updated", "leave", EmployeeLeaveSerializer(leave_obj).data)
            except Exception as exc:
                logger.debug("Calendar broadcast failed (non-critical): %s", exc)

            self._queue_leave_email_notification([leave_id], "updated", actor_username)

        transaction.on_commit(_send_leave_update_notifications)

    def get_queryset(self):
        queryset = EmployeeLeave.objects.select_related("employee", "employee__department", "created_by").prefetch_related(models.Prefetch("agents", queryset=Employee.objects.select_related("department")))

        # Filter by year if provided
        year = self.request.query_params.get("year")
        if year:
            try:
                year = int(year)
                queryset = queryset.filter(date__year=year)
            except ValueError:
                pass

        # Filter by month if provided
        month = self.request.query_params.get("month")
        if month:
            try:
                month = int(month)
                queryset = queryset.filter(date__month=month)
            except ValueError:
                pass

        # Filter by date range
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        # Filter by employee
        employee_id = self.request.query_params.get("employee")
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)

        # Filter by specific date
        date = self.request.query_params.get("date")
        if date:
            queryset = queryset.filter(date=date)

        batch_key = self.request.query_params.get("batch_key")
        if batch_key:
            queryset = queryset.filter(batch_key=batch_key)

        return queryset.order_by("date", "employee__name")

    @action(detail=False, methods=["get"], url_path="agent-lookup")
    @swagger_auto_schema(
        operation_summary="Search external leave agents",
        operation_description="Proxy the external user directory for leave-agent selection using the current external-authenticated session.",
        manual_parameters=[
            openapi.Parameter(
                "keyword",
                openapi.IN_QUERY,
                description="Minimum 2-character search keyword.",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Normalized external leave-agent lookup results",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "count": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "results": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "username": openapi.Schema(type=openapi.TYPE_STRING),
                                    "email": openapi.Schema(type=openapi.TYPE_STRING),
                                    "worker_id": openapi.Schema(type=openapi.TYPE_STRING),
                                    "site": openapi.Schema(type=openapi.TYPE_STRING),
                                    "source": openapi.Schema(type=openapi.TYPE_STRING, enum=["external_lookup"]),
                                },
                            ),
                        ),
                    },
                ),
            ),
            400: "Invalid lookup keyword or upstream lookup parameters",
            401: "External session expired",
            403: "Current session cannot access external lookup in phase 1",
            502: "External lookup unavailable",
            503: "External lookup timeout or service unavailable",
        },
        tags=["calendar"],
    )
    def agent_lookup(self, request):
        if not isinstance(request.user, ExternalUser):
            return Response(
                {
                    "detail": "External leave-agent lookup is available only for external-authenticated sessions.",
                    "code": "external_lookup_requires_external_session",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        keyword = str(request.query_params.get("keyword") or "").strip()
        if len(keyword) < self.EXTERNAL_LOOKUP_MIN_KEYWORD_LENGTH:
            return Response(
                {
                    "detail": f"Keyword must be at least {self.EXTERNAL_LOOKUP_MIN_KEYWORD_LENGTH} characters.",
                    "code": "invalid_lookup_keyword",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        access_token = self._get_external_lookup_token(request)
        if not access_token:
            return Response(
                {
                    "detail": "No active external session is available for leave-agent lookup.",
                    "code": "external_lookup_session_unavailable",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            upstream_results = ExternalAuthService.lookup_user_accounts(access_token, keyword=keyword)
        except ExternalServiceError as exc:
            return Response({"detail": exc.message, "code": exc.code}, status=exc.status_code)

        results = self._normalize_external_lookup_results(upstream_results)
        return Response({"count": len(results), "results": results}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="batch")
    def create_batch(self, request):
        serializer = EmployeeLeaveBatchCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        employee = validated_data["employee"]
        dates = validated_data["dates"]
        notes = validated_data.get("notes")
        agents = validated_data.get("agents", [])
        external_agents = validated_data.get("external_agents", [])
        agent_names = validated_data.get("agent_names")
        created_by = self._resolve_external_user(request.user)

        leaves = []
        batch_key = uuid.uuid4()
        actor_username = getattr(request.user, "username", None) or "Unknown"
        with transaction.atomic():
            try:
                for leave_date in dates:
                    leave = EmployeeLeave.objects.create(
                        employee=employee,
                        date=leave_date,
                        batch_key=batch_key,
                        notes=notes,
                        external_agents=external_agents,
                        agent_names=agent_names,
                        created_by=created_by,
                    )
                    if agents:
                        leave.agents.set(agents)
                    leaves.append(leave)
                    self._schedule_leave_created_side_effects(leave, request.user, send_email=False)
            except IntegrityError:
                return Response(
                    {"detail": "One or more leave dates already exist for this employee. Refresh and try again."},
                    status=status.HTTP_409_CONFLICT,
                )

            leave_ids = [leave.id for leave in leaves]
            transaction.on_commit(lambda: self._queue_leave_email_notification(leave_ids, "created", actor_username))
            self._rotate_leave_preview_token_on_commit(batch_key)

        response_serializer = EmployeeLeaveSerializer(leaves, many=True)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["patch"], url_path="batch-update")
    def update_batch(self, request):
        serializer = EmployeeLeaveBatchUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        leave_ids = validated_data["leave_ids"]
        target_leaves = list(EmployeeLeave.objects.filter(pk__in=leave_ids).select_related("employee", "employee__department", "created_by").prefetch_related("agents").order_by("date", "id"))
        if len(target_leaves) != len(leave_ids):
            return Response({"detail": "Some leave records could not be found."}, status=status.HTTP_404_NOT_FOUND)

        self._assert_can_manage_leaves(request.user, target_leaves)

        employee = validated_data["employee"]
        dates = validated_data["dates"]
        notes = validated_data.get("notes")
        agents = validated_data.get("agents", [])
        external_agents = validated_data.get("external_agents", [])
        agent_names = validated_data.get("agent_names")

        conflicting_dates = list(EmployeeLeave.objects.filter(employee=employee, date__in=dates).exclude(pk__in=leave_ids).order_by("date").values_list("date", flat=True))
        if conflicting_dates:
            formatted_dates = ", ".join(date_value.isoformat() for date_value in conflicting_dates)
            return Response(
                {"dates": f"Leave already exists for {employee.name} on: {formatted_dates}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created_ids = []
        updated_ids = []
        deleted_ids = []
        final_leaves = []
        original_creator = target_leaves[0].created_by if target_leaves else self._resolve_external_user(request.user)
        batch_key = next((leave.batch_key for leave in target_leaves if leave.batch_key), None) or uuid.uuid4()
        existing_by_date = {leave.date: leave for leave in target_leaves}
        actor_username = getattr(request.user, "username", None) or "Unknown"

        with transaction.atomic():
            try:
                for leave_date in dates:
                    leave = existing_by_date.pop(leave_date, None)
                    if leave is None:
                        leave = EmployeeLeave.objects.create(
                            employee=employee,
                            date=leave_date,
                            batch_key=batch_key,
                            notes=notes,
                            external_agents=external_agents,
                            agent_names=agent_names,
                            created_by=original_creator,
                        )
                        created_ids.append(leave.id)
                    else:
                        leave.employee = employee
                        leave.batch_key = batch_key
                        leave.notes = notes
                        leave.external_agents = external_agents
                        leave.agent_names = agent_names
                        leave.save()
                        updated_ids.append(leave.id)

                    leave.agents.set(agents)
                    final_leaves.append(leave)

                for obsolete_leave in existing_by_date.values():
                    deleted_ids.append(obsolete_leave.id)
                    obsolete_leave.delete()

                final_leave_ids = [leave.id for leave in final_leaves]
                transaction.on_commit(lambda: self._queue_leave_email_notification(final_leave_ids, "updated", actor_username))
                self._rotate_leave_preview_token_on_commit(batch_key)
            except IntegrityError:
                return Response(
                    {"detail": "One or more leave dates already exist for this employee. Refresh and try again."},
                    status=status.HTTP_409_CONFLICT,
                )

        self._broadcast_leave_batch_changes(created_ids=created_ids, updated_ids=updated_ids, deleted_ids=deleted_ids)

        response_serializer = EmployeeLeaveSerializer(sorted(final_leaves, key=lambda leave: (leave.date, leave.employee.name)), many=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="batch-delete")
    def delete_batch(self, request):
        serializer = EmployeeLeaveBatchDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        leave_ids = serializer.validated_data["leave_ids"]
        target_leaves = list(EmployeeLeave.objects.filter(pk__in=leave_ids).order_by("date", "id"))
        if len(target_leaves) != len(leave_ids):
            return Response({"detail": "Some leave records could not be found."}, status=status.HTTP_404_NOT_FOUND)

        self._assert_can_manage_leaves(request.user, target_leaves)

        deleted_ids = [leave.id for leave in target_leaves]
        batch_keys = [leave.batch_key for leave in target_leaves if leave.batch_key]
        with transaction.atomic():
            EmployeeLeave.objects.filter(pk__in=deleted_ids).delete()
            self._rotate_leave_preview_tokens_on_commit(batch_keys)

        self._broadcast_leave_batch_changes(deleted_ids=deleted_ids)
        return Response({"deleted_ids": deleted_ids}, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        user = self.request.user
        batch_key = uuid.uuid4()
        try:
            leave = serializer.save(created_by=self._resolve_external_user(user), batch_key=batch_key)
        except IntegrityError as exc:
            raise ValidationError({"detail": "A leave record already exists for this employee on that date."}) from exc
        self._rotate_leave_preview_token_on_commit(batch_key)
        self._schedule_leave_created_side_effects(leave, user)

    def perform_update(self, serializer):
        self._assert_can_manage_leaves(self.request.user, [serializer.instance])
        batch_key = serializer.instance.batch_key or uuid.uuid4()
        try:
            instance = serializer.save(batch_key=batch_key)
        except IntegrityError as exc:
            raise ValidationError({"detail": "A leave record already exists for this employee on that date."}) from exc
        self._rotate_leave_preview_token_on_commit(batch_key)
        self._schedule_leave_updated_side_effects(instance, self.request.user)

    @action(detail=False, methods=["get"], permission_classes=[AllowAny], url_path="preview")
    def preview(self, request):
        from ..models import LeavePreviewToken

        token = str(request.query_params.get("token") or "").strip()
        if not token:
            return Response({"detail": "Preview token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            batch_key, token_version = resolve_leave_preview_token(token)
        except Exception:
            return Response({"detail": "Preview link is invalid."}, status=status.HTTP_400_BAD_REQUEST)

        token_hash = LeavePreviewToken.hash_token(token)
        token_record = LeavePreviewToken.objects.filter(batch_key=batch_key, version=token_version, token_hash=token_hash).first()
        if token_record is None:
            return Response({"detail": "Preview link is invalid."}, status=status.HTTP_400_BAD_REQUEST)

        leaves = list(EmployeeLeave.objects.filter(batch_key=batch_key).select_related("employee", "employee__department", "created_by").prefetch_related("agents").order_by("date", "id"))
        if not leaves:
            return Response({"detail": "Leave preview is no longer available."}, status=status.HTTP_404_NOT_FOUND)

        token_record.last_accessed_at = timezone.now()
        token_record.save(update_fields=["last_accessed_at", "updated_at"])

        leave = leaves[0]
        department = getattr(leave.employee, "department", None)
        employee_email = self._resolve_preview_employee_email(leave.employee)
        structured_agent_names = []
        custom_agent_names = []
        unique_notes = []
        seen_notes = set()
        for leave_item in leaves:
            structured_agent_names.extend(agent.name for agent in leave_item.agents.all())
            structured_agent_names.extend(_external_agent_names(leave_item.external_agents))
            if leave_item.agent_names:
                custom_agent_names.extend(name.strip() for name in leave_item.agent_names.split(",") if name.strip())
            note = (leave_item.notes or "").strip()
            if note and note not in seen_notes:
                seen_notes.add(note)
                unique_notes.append(note)

        preview_payload = {
            "batch_key": str(batch_key),
            "employee_name": leave.employee.name,
            "employee_id": leave.employee.emp_id or "-",
            "employee_email": employee_email,
            "department_name": getattr(department, "name", "-") or "-",
            "department_code": getattr(department, "code", "-") or "-",
            "dates": [leave_item.date.isoformat() for leave_item in leaves],
            "leave_day_count": len(leaves),
            "agents": list(OrderedDict((name, True) for name in [*structured_agent_names, *custom_agent_names]).keys()),
            "note": " | ".join(unique_notes) if unique_notes else "-",
            "submitted_by": format_actor_timestamp(leave.created_by.username if leave.created_by else "Unknown", leave.created_at),
            "created_at": leave.created_at,
            "updated_at": max(leave_item.updated_at for leave_item in leaves),
            "created_at_label": format_actor_timestamp("Submitted", leave.created_at),
            "updated_at_label": format_actor_timestamp("Updated", max(leave_item.updated_at for leave_item in leaves)),
        }

        return Response(preview_payload)

    def perform_destroy(self, instance):
        self._assert_can_manage_leaves(self.request.user, [instance])
        leave_id = instance.id
        batch_key = instance.batch_key
        with transaction.atomic():
            instance.delete()
            self._rotate_leave_preview_token_on_commit(batch_key)
        try:
            from ..consumers import broadcast_calendar_update

            broadcast_calendar_update("deleted", "leave", {"id": leave_id})
        except Exception as e:
            logger.debug("Calendar broadcast failed (non-critical): %s", e)
