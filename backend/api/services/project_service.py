"""Service helpers for project operations."""

from ..models import Project


def get_project_queryset():
    """Return project queryset for downstream views."""
    return Project.objects.all()
