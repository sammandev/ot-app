"""Service helpers for overtime request operations."""

from ..models import OvertimeRequest


def get_overtime_queryset():
    """Return overtime queryset with related fields for efficient access."""
    return OvertimeRequest.objects.select_related("employee", "employee__department", "project", "department", "approved_by").prefetch_related("breaks").all()
