"""Service helpers for employee operations."""

from ..models import Employee


def get_employee_queryset():
    """Return employee queryset with department prefetch for downstream views."""
    return Employee.objects.select_related("department").all()
