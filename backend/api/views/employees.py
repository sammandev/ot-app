import logging

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import (
    Employee,
)
from ..pagination import EmployeePagination
from ..permissions import ResourcePermission
from ..serializers import (
    EmployeeSerializer,
)
from ..services.bulk_service import BulkImportExportService
from ..services.cache_service import CacheService
from ..services.employee_service import get_employee_queryset
from .helpers import get_employee_for_user, is_developer_user, is_ptb_admin, is_superadmin_user  # noqa: F401

logger = logging.getLogger(__name__)
User = get_user_model()


class EmployeeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ResourcePermission]
    resource_name = "employees"
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    pagination_class = EmployeePagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "emp_id"]
    ordering_fields = ["id", "name", "emp_id", "department__name", "is_enabled", "created_at"]
    ordering = ["-id"]

    def get_queryset(self):
        return get_employee_queryset()

    @swagger_auto_schema(
        operation_summary="List all employees",
        responses={200: EmployeeSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(name="page", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False, description="Page number (default: 1)"),
            openapi.Parameter(name="page_size", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False, description="Items per page (default: 50, max: 200)"),
            openapi.Parameter(name="search", in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False, description="Search by name or employee ID"),
            openapi.Parameter(name="ordering", in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False, description="Order by field (use - for descending): -name, emp_id, etc."),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Bulk import employees from CSV",
        operation_description="Upload a CSV file to import multiple employees at once. Maximum 1000 rows.",
        manual_parameters=[
            openapi.Parameter(name="file", in_=openapi.IN_FORM, type=openapi.TYPE_FILE, required=True, description="CSV file containing employee data"),
            openapi.Parameter(name="update_existing", in_=openapi.IN_FORM, type=openapi.TYPE_BOOLEAN, required=False, description="Update existing records (default: false)"),
        ],
        consumes=["multipart/form-data"],
        responses={
            200: openapi.Response(
                description="Import successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "created": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "updated": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "errors": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                        "total_rows": openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
            400: "Bad request - invalid file or format",
        },
    )
    @action(detail=False, methods=["post"], parser_classes=[MultiPartParser, FormParser])
    def bulk_import(self, request):
        """Import employees from CSV file."""
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response({"detail": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        update_existing = request.data.get("update_existing", "false").lower() == "true"

        try:
            results = BulkImportExportService.import_from_csv(file_obj=file_obj, serializer_class=EmployeeSerializer, max_rows=1000, update_existing=update_existing, lookup_field="emp_id")

            # Invalidate cache after bulk import
            CacheService.invalidate_cache(["employees"])

            logger.info("Bulk import completed: %s created, %s updated, %s errors", results["created"], results["updated"], len(results["errors"]))

            return Response(results, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error("Bulk import failed: %s", e)
            return Response({"detail": "Invalid request data. Please check your input and try again."}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Export employees to CSV",
        operation_description="Download all employees as a CSV file",
        manual_parameters=[openapi.Parameter(name="fields", in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Comma-separated list of fields to export (default: all)")],
        responses={200: "CSV file"},
    )
    @action(detail=False, methods=["get"])
    def export(self, request):
        """Export employees to CSV file."""
        # Get fields to export
        fields_param = request.query_params.get("fields", "")
        if fields_param:
            fields = [f.strip() for f in fields_param.split(",")]
        else:
            fields = ["id", "emp_id", "name", "department.name", "exclude_from_reports"]

        # Get queryset
        queryset = self.get_queryset()

        # Export to CSV
        csv_file = BulkImportExportService.export_to_csv(queryset=queryset, fields=fields)

        # Create response
        response = HttpResponse(csv_file.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="employees_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'

        return response
