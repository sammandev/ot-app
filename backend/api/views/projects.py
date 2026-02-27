import logging

from django.contrib.auth import get_user_model
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import (
    Department,
    Employee,
    Project,
)
from ..pagination import ProjectPagination
from ..permissions import ResourcePermission
from ..serializers import (
    DepartmentSerializer,
    EmployeeSerializer,
    ProjectSerializer,
)
from ..services.project_service import get_project_queryset
from .helpers import get_employee_for_user, is_developer_user, is_ptb_admin, is_superadmin_user  # noqa: F401

logger = logging.getLogger(__name__)
User = get_user_model()


class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ResourcePermission]
    resource_name = "projects"
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    pagination_class = ProjectPagination
    filter_backends = [SearchFilter]
    search_fields = ["name"]
    ordering_fields = ["id", "name", "created_at"]
    ordering = ["-id"]

    def get_queryset(self):
        return get_project_queryset()

    @swagger_auto_schema(
        operation_summary="List all projects",
        responses={200: ProjectSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(name="page", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False, description="Page number (default: 1)"),
            openapi.Parameter(name="page_size", in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False, description="Items per page (default: 30, max: 100)"),
            openapi.Parameter(name="search", in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False, description="Search by project name"),
            openapi.Parameter(name="ordering", in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False, description="Order by field (use - for descending): -name, id, etc."),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)


class DepartmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ResourcePermission]
    resource_name = "departments"
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filter_backends = [SearchFilter]
    search_fields = ["code", "name"]
    ordering_fields = ["id", "code", "name", "created_at"]
    ordering = ["code"]

    @swagger_auto_schema(
        operation_summary="List all departments",
        responses={200: DepartmentSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(name="search", in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False, description="Search by department code or name"),
            openapi.Parameter(name="ordering", in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False, description="Order by field (use - for descending): -code, name, etc."),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get employees in a department",
        responses={200: EmployeeSerializer(many=True)},
    )
    @action(detail=True, methods=["get"])
    def employees(self, request, pk=None):
        """Get all employees in this department"""
        department = self.get_object()
        employees = Employee.objects.filter(department=department).select_related("department").order_by("name")
        page = self.paginate_queryset(employees)
        if page is not None:
            serializer = EmployeeSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Remove employee from department",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "employee_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="Employee ID to remove"),
            },
            required=["employee_id"],
        ),
        responses={200: openapi.Response("Employee removed from department")},
    )
    @action(detail=True, methods=["post"])
    def remove_employee(self, request, pk=None):
        """Remove an employee from this department (PTB admin only)"""
        # Check if user is PTB admin
        if not request.user.is_ptb_admin and not request.user.is_superuser:
            return Response({"detail": "Only PTB admins can remove employees from departments"}, status=status.HTTP_403_FORBIDDEN)

        department = self.get_object()
        employee_id = request.data.get("employee_id")

        if not employee_id:
            return Response({"detail": "employee_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            employee = Employee.objects.get(id=employee_id, department=department)
            employee.department = None
            employee.save()
            return Response({"message": f"Employee {employee.name} removed from department {department.code}"})
        except Employee.DoesNotExist:
            return Response({"detail": "Employee not found in this department"}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)
