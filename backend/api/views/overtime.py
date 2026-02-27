import logging
import traceback
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import (
    ExternalUser,
    Notification,
    OvertimeLimitConfig,
    OvertimeRegulation,
    OvertimeRegulationDocument,
    OvertimeRequest,
)
from ..pagination import OvertimeRequestPagination
from ..permissions import ResourcePermission
from ..serializers import (
    OvertimeLimitConfigSerializer,
    OvertimeRegulationDocumentSerializer,
    OvertimeRegulationSerializer,
    OvertimeSerializer,
)
from ..services.cache_service import cache_invalidate_on_change, cached_list
from ..services.overtime_service import get_overtime_queryset
from ..utils.excel_generator import ExcelGenerator
from .helpers import get_employee_for_user, is_developer_user, is_ptb_admin, is_superadmin_user  # noqa: F401

logger = logging.getLogger(__name__)
User = get_user_model()


class OvertimeRequestViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = OvertimeRequest.objects.all()
    serializer_class = OvertimeSerializer
    pagination_class = OvertimeRequestPagination

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "employee__name",
        "project__name",
        "request_date",
    ]
    ordering_fields = ["id", "request_date", "employee_name", "project_name", "total_hours", "status", "created_at"]
    ordering = ["-request_date", "-created_at"]

    @swagger_auto_schema(
        operation_summary="List overtime requests",
        operation_description="Get list of overtime requests. Admins see all, regular users see only their own.",
        manual_parameters=[
            openapi.Parameter(name="page", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False, description="Page number (default: 1)"),
            openapi.Parameter(name="page_size", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False, description="Items per page (default: 20, max: 50)"),
            openapi.Parameter(name="search", in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False, description="Search by employee name, project, or date"),
            openapi.Parameter(
                name="employee",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=False,
                description="Filter by employee ID",
            ),
            openapi.Parameter(
                name="project",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=False,
                description="Filter by project ID",
            ),
            openapi.Parameter(
                name="request_date",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=False,
                description="Filter by specific date (YYYY-MM-DD)",
            ),
            openapi.Parameter(name="start_date", in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, required=False, description="Filter by date range start (YYYY-MM-DD)"),
            openapi.Parameter(name="end_date", in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, required=False, description="Filter by date range end (YYYY-MM-DD)"),
            openapi.Parameter(name="ordering", in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False, description="Order by field (use - for descending): -request_date, employee, etc."),
        ],
        responses={
            200: OvertimeSerializer(many=True),
            400: openapi.Response(
                description="Bad Request",
                examples={"application/json": {"detail": "Invalid parameters"}},
            ),
        },
    )
    def list(self, request, *args, **kwargs):
        # Return fresh data to avoid stale entries
        return super().list(request, *args, **kwargs)

    def _get_permission_queryset(self):
        """Return queryset with only permission checks applied (no query param filters).

        Used by stats endpoints that apply their own filters to avoid double-filtering.
        """
        queryset = get_overtime_queryset()

        # Skip filtering during schema generation
        if getattr(self, "swagger_fake_view", False):
            return queryset

        user = self.request.user
        if not user.is_authenticated:
            return queryset.none()

        # Apply Permission Checks
        is_god_mode = is_superadmin_user(user)

        if getattr(user, "is_ptb_admin", False) or is_god_mode:
            pass  # Admin sees all
        else:
            # Regular user sees only their own requests
            worker_id = getattr(user, "worker_id", None)
            employee_id = getattr(user, "employee_id", None)

            if worker_id:
                queryset = queryset.filter(employee__emp_id=worker_id)
            elif employee_id:
                queryset = queryset.filter(employee__id=employee_id)
            else:
                return queryset.none()

        return queryset

    def get_queryset(self):
        queryset = self._get_permission_queryset()

        # Apply Filters from Query Params
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        employee = self.request.query_params.get("employee")
        project = self.request.query_params.get("project")
        date = self.request.query_params.get("request_date")

        if start_date and end_date:
            queryset = queryset.filter(request_date__range=[start_date, end_date])
        if employee:
            try:
                queryset = queryset.filter(employee=int(employee))
            except (ValueError, TypeError):
                return queryset.none()
        if project:
            try:
                queryset = queryset.filter(project=int(project))
            except (ValueError, TypeError):
                return queryset.none()
        if date:
            queryset = queryset.filter(request_date=date)

        # Additional filters: status and department_code
        status_filter = self.request.query_params.get("status")
        department_code = self.request.query_params.get("department_code")

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if department_code:
            queryset = queryset.filter(department_code=department_code)

        return queryset

    @swagger_auto_schema(
        operation_summary="Create overtime request",
        request_body=OvertimeSerializer,
        responses={201: OvertimeSerializer(), 400: "Validation Error"},
    )
    @cache_invalidate_on_change(["overtime_requests", "employees", "projects"])
    def create(self, request, *args, **kwargs):
        cache_key = f"ot_request_{request.data.get('employee')}_{request.data.get('project')}_{request.data.get('request_date')}"

        try:
            logger.info("OvertimeRequest create - Data: %s", request.data)
            if not cache.add(cache_key, "locked", timeout=30):
                return Response({"detail": "Request in progress. Please wait."}, status=409)

            with transaction.atomic():
                # Check existing inside transaction
                # Be defensive: if record exists but has corrupted data, skip it
                existing = None
                try:
                    existing = (
                        OvertimeRequest.objects.select_for_update()
                        .filter(
                            employee_id=request.data.get("employee"),
                            project_id=request.data.get("project"),
                            request_date=request.data.get("request_date"),
                        )
                        .first()
                    )

                    # Verify the existing record is valid
                    if existing and not existing.employee_id:
                        logger.warning("Found existing record %s but employee FK is null", existing.id)
                        existing = None
                except Exception as query_error:
                    logger.warning("Error querying for existing record: %s", query_error)
                    existing = None

                if existing:
                    logger.info("Existing OvertimeRequest found: %s, returning 409", existing.id)
                    return Response(
                        {"detail": "An overtime request already exists for this employee, project, and date.", "existing_id": existing.id},
                        status=status.HTTP_409_CONFLICT,
                    )

                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                logger.info("OvertimeRequest created successfully: %s", serializer.data.get("id"))
                return Response(serializer.data, status=201)
        except APIException:
            raise
        except Exception as e:
            logger.error("OvertimeRequest create error: %s", e)
            logger.error("Traceback: %s", traceback.format_exc())
            logger.error("Request data: %s", request.data)
            return Response({"detail": "An unexpected error occurred. Please try again or contact support."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            cache.delete(cache_key)

    @cache_invalidate_on_change(["overtime_requests", "employees", "projects"])
    def destroy(self, request, *args, **kwargs):
        cache_key = f"ot_delete_{kwargs['pk']}"
        try:
            logger.info("OvertimeRequest delete - ID: %s", kwargs["pk"])
            if not cache.add(cache_key, "locked", timeout=30):
                return Response({"detail": "Delete in progress"}, status=409)

            with transaction.atomic():
                try:
                    instance = self.get_object()
                    # Lock the record within transaction
                    OvertimeRequest.objects.select_for_update().get(pk=instance.pk)
                    response = super().destroy(request, *args, **kwargs)
                    logger.info("OvertimeRequest %s deleted successfully", kwargs["pk"])
                    return response
                except OvertimeRequest.DoesNotExist:
                    logger.warning("OvertimeRequest %s not found (already deleted)", kwargs["pk"])
                    return Response({"detail": "Request already deleted"}, status=404)
        except APIException:
            raise
        except Exception as e:
            logger.error("OvertimeRequest delete error: %s", e)
            logger.error("Traceback: %s", traceback.format_exc())
            return Response({"detail": "An unexpected error occurred. Please try again or contact support."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            cache.delete(cache_key)

    @swagger_auto_schema(
        operation_summary="Update overtime request",
        request_body=OvertimeSerializer,
        responses={200: OvertimeSerializer(), 404: "Not Found"},
    )
    @cache_invalidate_on_change(["overtime_requests", "employees", "projects"])
    def update(self, request, *args, **kwargs):
        cache_key = f"ot_update_{kwargs['pk']}"
        try:
            logger.info("OvertimeRequest update - ID: %s, Data: %s", kwargs["pk"], request.data)
            if not cache.add(cache_key, "locked", timeout=30):
                return Response({"detail": "Update in progress"}, status=409)

            with transaction.atomic():
                instance = self.get_object()
                # Lock the record
                OvertimeRequest.objects.select_for_update().get(pk=instance.pk)

                # Block editing approved or rejected requests (admins can still change status via bulk endpoint)
                if instance.status in ("approved", "rejected"):
                    return Response(
                        {"detail": f"Cannot edit an overtime request that has been {instance.status}."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Prevent regular users from changing the status field directly
                user = request.user
                if "status" in request.data and not (getattr(user, "is_ptb_admin", False) or is_superadmin_user(user)):
                    return Response(
                        {"detail": "Only admins can change request status. Use the approval workflow."},
                        status=status.HTTP_403_FORBIDDEN,
                    )

                response = super().update(request, *args, **kwargs)
                logger.info("OvertimeRequest %s updated successfully", kwargs["pk"])
                return response
        except APIException:
            raise
        except Exception as e:
            logger.error("OvertimeRequest update error: %s", e)
            logger.error("Traceback: %s", traceback.format_exc())
            logger.error("Request data: %s", request.data)
            return Response({"detail": "An unexpected error occurred. Please try again or contact support."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            cache.delete(cache_key)

    @swagger_auto_schema(
        operation_summary="Bulk update overtime request statuses",
        operation_description="Update status of multiple overtime requests at once. Admin only.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["ids", "status"],
            properties={
                "ids": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER), description="List of overtime request IDs"),
                "status": openapi.Schema(type=openapi.TYPE_STRING, enum=["approved", "rejected", "pending"], description="New status to set"),
            },
        ),
        responses={200: openapi.Response(description="Bulk update successful", examples={"application/json": {"message": "10 requests updated successfully", "updated_count": 10}})},
    )
    @action(detail=False, methods=["post"], url_path="bulk-update-status")
    @cache_invalidate_on_change(["overtime_requests"])
    def bulk_update_status(self, request):
        """Bulk update status for multiple overtime requests - much faster than individual updates"""
        user = request.user
        if not (getattr(user, "is_ptb_admin", False) or is_superadmin_user(user)):
            return Response({"detail": "Permission denied. Admin only."}, status=status.HTTP_403_FORBIDDEN)

        ids = request.data.get("ids", [])
        new_status = request.data.get("status")

        if not ids:
            return Response({"detail": "No IDs provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate ids is a list of integers
        if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
            return Response({"detail": "IDs must be a list of integers"}, status=status.HTTP_400_BAD_REQUEST)

        if len(ids) > 500:
            return Response({"detail": "Cannot update more than 500 requests at once"}, status=status.HTTP_400_BAD_REQUEST)

        if new_status not in ["approved", "rejected", "pending"]:
            return Response({"detail": "Invalid status. Must be 'approved', 'rejected', or 'pending'"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # Collect affected dates BEFORE updating (for Excel regeneration)
                affected_requests = list(OvertimeRequest.objects.filter(id__in=ids).values("id", "request_date", "employee__emp_id", "employee_name"))
                affected_dates = list({r["request_date"] for r in affected_requests})

                # Build update kwargs with status_changed_by and timestamps
                update_kwargs = {
                    "status": new_status,
                    "status_changed_by": getattr(user, "username", ""),
                }
                if new_status == "approved":
                    update_kwargs["approved_at"] = timezone.now()
                    update_kwargs["rejected_at"] = None
                elif new_status == "rejected":
                    update_kwargs["rejected_at"] = timezone.now()
                    update_kwargs["approved_at"] = None
                else:
                    # pending — clear both timestamps
                    update_kwargs["approved_at"] = None
                    update_kwargs["rejected_at"] = None

                # Lock and update all records in a single query
                updated_count = OvertimeRequest.objects.filter(id__in=ids).update(**update_kwargs)
                logger.info("Bulk status update: %s requests updated to '%s' by user %s", updated_count, new_status, user.username)

            # After commit: send notifications to affected employees
            if updated_count > 0 and new_status in ("approved", "rejected"):
                try:
                    from ..consumers import send_notification_to_user

                    status_label = "approved" if new_status == "approved" else "rejected"
                    admin_name = getattr(user, "username", "Admin")

                    # Collect unique emp_ids to look up ExternalUser records
                    emp_ids = list({r["employee__emp_id"] for r in affected_requests if r["employee__emp_id"]})
                    ext_users_map = {}
                    if emp_ids:
                        ext_users_map = {u.worker_id.lower(): u for u in ExternalUser.objects.filter(worker_id__in=emp_ids, is_active=True)}

                    notifs_to_create = []
                    ws_send_list = []
                    for req_info in affected_requests:
                        emp_id = (req_info["employee__emp_id"] or "").lower()
                        ext_user = ext_users_map.get(emp_id)
                        if not ext_user:
                            continue
                        date_str = req_info["request_date"].strftime("%B %d, %Y") if hasattr(req_info["request_date"], "strftime") else str(req_info["request_date"])
                        title = f"Overtime Request {status_label.title()}"
                        message = f"Your overtime request for {date_str} has been {status_label} by {admin_name}."
                        notifs_to_create.append(Notification(recipient=ext_user, title=title, message=message, event_type=f"overtime_{status_label}"))
                        ws_send_list.append((ext_user.id, title, message))

                    if notifs_to_create:
                        created_notifs = Notification.objects.bulk_create(notifs_to_create)
                        for notif, (uid, ntitle, nmsg) in zip(created_notifs, ws_send_list, strict=True):
                            send_notification_to_user(
                                uid,
                                {
                                    "id": notif.id,
                                    "title": ntitle,
                                    "message": nmsg,
                                    "event_type": notif.event_type,
                                    "event_id": None,
                                    "is_read": False,
                                    "created_at": notif.created_at.isoformat(),
                                },
                            )
                        logger.info("Sent %s notifications for %s overtime requests", len(created_notifs), status_label)
                except Exception as notif_err:
                    logger.warning("Failed to send notifications after bulk status update: %s", notif_err)

            # After commit: regenerate Excel files for affected dates
            # This ensures rejected requests are excluded from reports
            if updated_count > 0 and affected_dates:
                try:
                    from api.tasks import regenerate_excel_after_delete

                    for d in affected_dates:
                        d_str = d.isoformat() if hasattr(d, "isoformat") else str(d)
                        regenerate_excel_after_delete.delay(d_str)
                    logger.info("Queued Excel regeneration for %s affected dates after bulk status update", len(affected_dates))
                except Exception as regen_err:
                    logger.warning("Failed to queue Excel regeneration after bulk status update: %s", regen_err)

            return Response({"message": f"{updated_count} requests updated successfully", "updated_count": updated_count, "status": new_status})
        except APIException:
            raise
        except Exception as e:
            logger.error("Bulk update error: %s", e)
            return Response({"detail": "An unexpected error occurred. Please try again or contact support."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["post"])
    def export_files(self, request):
        # Only PTB admins and superadmins can export files
        user = request.user
        if not (getattr(user, "is_ptb_admin", False) or is_superadmin_user(user)):
            return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        try:
            date = datetime.strptime(request.data["date"], "%Y-%m-%d").date()

            # Use grouped (by-department) variants for consistency with model save()
            daily_data = OvertimeRequest.export_daily_data_by_department(date)
            monthly_data = OvertimeRequest.export_monthly_data_by_department(date)

            # Generate Excel files
            ExcelGenerator.generate_all_excel_files(daily_data, monthly_data, date)

            return Response({"status": "success", "message": "Excel files exported successfully"})

        except Exception as e:
            logger.error("Export files error: %s", e)
            return Response({"detail": "An error occurred while exporting files."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def employee_stats(self, request):
        """Get overtime statistics grouped by employee"""
        try:
            start_date = request.query_params.get("start_date")
            end_date = request.query_params.get("end_date")
            status_filter = request.query_params.get("status")
            employee_id = request.query_params.get("employee")

            # Cache key based on user + query params (stats change infrequently)
            user_id = getattr(request.user, "id", "anon")
            cache_key = f"ot_employee_stats:{user_id}:{start_date}:{end_date}:{status_filter}:{employee_id}"
            cached = cache.get(cache_key)
            if cached is not None:
                return Response(cached)

            queryset = self._get_permission_queryset()
            if start_date:
                queryset = queryset.filter(request_date__gte=start_date)
            if end_date:
                queryset = queryset.filter(request_date__lte=end_date)
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            else:
                # Exclude rejected requests by default for stats
                queryset = queryset.exclude(status="rejected")
            if employee_id:
                queryset = queryset.filter(employee=employee_id)

            from django.db.models import Case, Count, DecimalField, Q, Sum, Value, When

            _decimal = DecimalField(max_digits=10, decimal_places=2)
            # NOTE: The annotation name must NOT be 'total_hours' because it would
            # shadow the model field of the same name, causing FieldError when
            # Case/When expressions reference "total_hours" (Django resolves it to
            # the aggregate instead of the DB column).
            stats = (
                queryset.values("employee", "employee_name")
                .annotate(
                    sum_total_hours=Sum("total_hours"),
                    total_requests=Count("id"),
                    weekday_hours=Sum(Case(When(Q(is_weekend=False) & Q(is_holiday=False), then="total_hours"), default=Value(0), output_field=_decimal)),
                    weekend_hours=Sum(Case(When(is_weekend=True, then="total_hours"), default=Value(0), output_field=_decimal)),
                    holiday_hours=Sum(Case(When(is_holiday=True, then="total_hours"), default=Value(0), output_field=_decimal)),
                    approved_hours=Sum(Case(When(status="approved", then="total_hours"), default=Value(0), output_field=_decimal)),
                    pending_hours=Sum(Case(When(status="pending", then="total_hours"), default=Value(0), output_field=_decimal)),
                )
                .order_by("-sum_total_hours")
            )

            # Map 'sum_total_hours' back to 'total_hours' for frontend compatibility
            result = []
            for row in stats:
                row["total_hours"] = row.pop("sum_total_hours", 0)
                result.append(row)

            cache.set(cache_key, result, 120)  # Cache for 2 minutes
            return Response(result)
        except Exception as e:
            logger.error("employee_stats error: %s", e, exc_info=True)
            return Response({"detail": "Failed to compute employee stats. Please try again."}, status=500)

    @action(detail=False, methods=["get"])
    def project_stats(self, request):
        """Get overtime statistics grouped by project"""
        try:
            start_date = request.query_params.get("start_date")
            end_date = request.query_params.get("end_date")
            status_filter = request.query_params.get("status")
            project_id = request.query_params.get("project")

            # Cache key based on user + query params
            user_id = getattr(request.user, "id", "anon")
            cache_key = f"ot_project_stats:{user_id}:{start_date}:{end_date}:{status_filter}:{project_id}"
            cached = cache.get(cache_key)
            if cached is not None:
                return Response(cached)

            queryset = self._get_permission_queryset()
            if start_date:
                queryset = queryset.filter(request_date__gte=start_date)
            if end_date:
                queryset = queryset.filter(request_date__lte=end_date)
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            else:
                queryset = queryset.exclude(status="rejected")
            if project_id:
                queryset = queryset.filter(project=project_id)

            from django.db.models import Count, Sum

            stats = queryset.values("project", "project_name").annotate(total_hours=Sum("total_hours"), total_requests=Count("id"), unique_employees=Count("employee", distinct=True)).order_by("-total_hours")

            result = list(stats)
            cache.set(cache_key, result, 120)  # Cache for 2 minutes
            return Response(result)
        except Exception as e:
            logger.error("project_stats error: %s", e, exc_info=True)
            return Response({"detail": "Failed to compute project stats. Please try again."}, status=500)

    @action(detail=False, methods=["get"])
    def summary_stats(self, request):
        """Get overall overtime summary statistics.

        Accepts optional prev_start_date/prev_end_date to return previous-period
        stats alongside current stats (useful for trend calculations).
        """
        try:
            start_date = request.query_params.get("start_date")
            end_date = request.query_params.get("end_date")
            prev_start_date = request.query_params.get("prev_start_date")
            prev_end_date = request.query_params.get("prev_end_date")

            # Cache key based on user + query params
            user_id = getattr(request.user, "id", "anon")
            cache_key = f"ot_summary_stats:{user_id}:{start_date}:{end_date}:{prev_start_date}:{prev_end_date}"
            cached = cache.get(cache_key)
            if cached is not None:
                return Response(cached)

            base_queryset = self._get_permission_queryset().exclude(status="rejected")

            def _aggregate(qs):
                from django.db.models import Case, Count, DecimalField, Q, Sum, Value, When

                _decimal = DecimalField(max_digits=10, decimal_places=2)
                # Use 'sum_total_hours' to avoid shadowing the 'total_hours' model field.
                # Case/When expressions reference the DB column "total_hours" by name;
                # if an aggregate annotation has the same name, Django resolves to the
                # aggregate → FieldError: "'total_hours' is an aggregate".
                data = qs.aggregate(
                    sum_total_hours=Sum("total_hours"),
                    total_requests=Count("id"),
                    unique_employees=Count("employee", distinct=True),
                    unique_projects=Count("project", distinct=True),
                    weekday_hours=Sum(Case(When(Q(is_weekend=False) & Q(is_holiday=False), then="total_hours"), default=Value(0), output_field=_decimal)),
                    weekend_hours=Sum(Case(When(is_weekend=True, then="total_hours"), default=Value(0), output_field=_decimal)),
                    holiday_hours=Sum(Case(When(is_holiday=True, then="total_hours"), default=Value(0), output_field=_decimal)),
                    approved_hours=Sum(Case(When(status="approved", then="total_hours"), default=Value(0), output_field=_decimal)),
                    pending_hours=Sum(Case(When(status="pending", then="total_hours"), default=Value(0), output_field=_decimal)),
                )
                # Map back to 'total_hours' for frontend compatibility
                data["total_hours"] = data.pop("sum_total_hours", 0)
                return data

            current_qs = base_queryset
            if start_date:
                current_qs = current_qs.filter(request_date__gte=start_date)
            if end_date:
                current_qs = current_qs.filter(request_date__lte=end_date)

            result = _aggregate(current_qs)

            # Compute previous-period stats if dates provided
            if prev_start_date and prev_end_date:
                prev_qs = base_queryset.filter(
                    request_date__gte=prev_start_date,
                    request_date__lte=prev_end_date,
                )
                result["previous"] = _aggregate(prev_qs)

            cache.set(cache_key, result, 120)  # Cache for 2 minutes
            return Response(result)
        except Exception as e:
            logger.error("summary_stats error: %s", e, exc_info=True)
            return Response({"detail": "Failed to compute summary stats. Please try again."}, status=500)


class OvertimeRegulationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing overtime regulations and rules"""

    permission_classes = [IsAuthenticated, ResourcePermission]
    resource_name = "regulations"

    queryset = OvertimeRegulation.objects.all()
    serializer_class = OvertimeRegulationSerializer
    filter_backends = [SearchFilter]
    search_fields = ["title", "description", "category"]
    ordering_fields = ["id", "order", "category", "created_at"]
    ordering = ["order", "id"]

    def get_permissions(self):
        """Allow all authenticated users to read regulations (shown on OT Form).
        Only admin/authorized users can create/update/delete."""
        if self.action in ("list", "retrieve"):
            return [IsAuthenticated()]
        return [IsAuthenticated(), ResourcePermission()]

    @swagger_auto_schema(
        operation_summary="List all overtime regulations",
        responses={200: OvertimeRegulationSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(name="category", in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False, description="Filter by category"),
            openapi.Parameter(name="is_active", in_=openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, required=False, description="Filter by active status"),
            openapi.Parameter(name="search", in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False, description="Search by title, description, or category"),
            openapi.Parameter(name="page_size", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False, description="Items per page"),
        ],
    )
    @cached_list("overtime_regulations", ttl=3600)
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Filter by category
        category = request.query_params.get("category")
        if category:
            queryset = queryset.filter(category=category)

        # Filter by active status
        is_active = request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        # Check if pagination is requested
        page_size = request.query_params.get("page_size")
        if page_size and page_size.isdigit():
            # Use standard pagination
            return super().list(request, *args, **kwargs)

        # Return non-paginated response for compatibility
        serializer = self.get_serializer(queryset, many=True)
        return Response({"results": serializer.data, "count": len(serializer.data)})

    @cache_invalidate_on_change(["overtime_regulations"])
    def perform_create(self, serializer):
        """Create and invalidate cache"""
        return super().perform_create(serializer)

    @cache_invalidate_on_change(["overtime_regulations"])
    def perform_update(self, serializer):
        """Update and invalidate cache"""
        return super().perform_update(serializer)

    @cache_invalidate_on_change(["overtime_regulations"])
    def perform_destroy(self, instance):
        """Delete and invalidate cache"""
        return super().perform_destroy(instance)

    def create(self, request, *args, **kwargs):
        try:
            logger.debug("Received regulation data: %s", request.data)
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                self.perform_create(serializer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            logger.warning("Validation errors: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Error creating regulation: %s", e)
            return Response({"detail": "An unexpected error occurred. Please try again or contact support."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            logger.debug("Updating regulation with data: %s", request.data)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                self.perform_update(serializer)
                return Response(serializer.data)
            logger.warning("Validation errors: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Error updating regulation: %s", e)
            logger.error("Traceback: %s", traceback.format_exc())
            return Response({"detail": "An unexpected error occurred. Please try again or contact support."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OvertimeRegulationDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing overtime regulation PDF documents"""

    permission_classes = [IsAuthenticated, ResourcePermission]
    resource_name = "regulations"
    queryset = OvertimeRegulationDocument.objects.filter(is_deleted=False)
    serializer_class = OvertimeRegulationDocumentSerializer
    filter_backends = [SearchFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["id", "version", "created_at"]
    ordering = ["-created_at"]

    def get_permissions(self):
        """Allow all authenticated users to read regulation documents (shown on OT Form).
        Only admin/authorized users can create/upload/delete."""
        if self.action in ("list", "retrieve"):
            return [IsAuthenticated()]
        return [IsAuthenticated(), ResourcePermission()]

    @swagger_auto_schema(
        operation_summary="List all regulation documents",
        responses={200: OvertimeRegulationDocumentSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(name="is_active", in_=openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, required=False, description="Filter by active status"),
            openapi.Parameter(name="page_size", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False, description="Items per page"),
        ],
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Filter by active status
        is_active = request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        # Check if pagination is requested
        page_size = request.query_params.get("page_size")
        if page_size and page_size.isdigit():
            # Use standard pagination
            return super().list(request, *args, **kwargs)

        # Return non-paginated response for compatibility
        serializer = self.get_serializer(queryset, many=True)
        return Response({"results": serializer.data, "count": len(serializer.data)})

    def perform_create(self, serializer):
        """Set uploaded_by to current user."""
        serializer.save(uploaded_by=self.request.user)

    def perform_destroy(self, instance):
        """Soft delete instead of hard delete"""
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        # instance.deleted_by = self.request.user  # Set when auth is implemented
        instance.save()


class OvertimeLimitConfigViewSet(viewsets.ModelViewSet):
    """ViewSet for managing overtime limit configuration (singleton-like)."""

    permission_classes = [IsAuthenticated, ResourcePermission]
    resource_name = "regulations"

    queryset = OvertimeLimitConfig.objects.all()
    serializer_class = OvertimeLimitConfigSerializer

    def get_permissions(self):
        """Allow all authenticated users to read limits (used on OT Form).
        Only admin/authorized users can update."""
        if self.action in ("list", "retrieve", "active"):
            return [IsAuthenticated()]
        return [IsAuthenticated(), ResourcePermission()]

    def list(self, request, *args, **kwargs):
        """Return the active config (singleton pattern)."""
        config = OvertimeLimitConfig.get_active()
        serializer = self.get_serializer(config)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def active(self, request):
        """Return the active overtime limit configuration."""
        config = OvertimeLimitConfig.get_active()
        serializer = self.get_serializer(config)
        return Response(serializer.data)

    @action(detail=False, methods=["put", "patch"])
    def update_limits(self, request):
        """Update the active overtime limit configuration."""
        config = OvertimeLimitConfig.get_active()
        serializer = self.get_serializer(config, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
