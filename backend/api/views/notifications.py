import logging

from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import (
    Notification,
)
from ..serializers import (
    NotificationSerializer,
)
from .helpers import get_employee_for_user, is_developer_user, is_ptb_admin, is_superadmin_user  # noqa: F401

logger = logging.getLogger(__name__)
User = get_user_model()


class NotificationPagination(PageNumberPagination):
    """
    Pagination for notifications.
    Supports 'limit' query param for different page sizes.
    """

    page_size = 20
    page_size_query_param = "limit"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({"count": self.page.paginator.count, "next": self.get_next_link(), "previous": self.get_previous_link(), "total_pages": self.page.paginator.num_pages, "current_page": self.page.number, "results": data})


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user notifications.
    Supports list, retrieve, mark as read, archive, and delete.

    Query Parameters:
    - limit: Number of notifications per page (default: 20, max: 100)
    - page: Page number for pagination
    - no_pagination: If 'true', returns all notifications without pagination (for dropdown menu)
    - include_archived: If 'true', includes archived notifications
    - archived_only: If 'true', returns only archived notifications
    """

    http_method_names = ["get", "post", "delete", "head", "options"]

    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    pagination_class = NotificationPagination

    def get_queryset(self):
        # Fix for swagger schema generation and unauthenticated access
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return Notification.objects.none()

        # Filter notifications for the current user
        queryset = Notification.objects.filter(recipient=self.request.user)

        # Detail actions (archive, unarchive, destroy, retrieve) must see ALL
        # notifications regardless of archive status, otherwise archived items
        # return 404 when the user tries to unarchive or delete them.
        if self.action in ("archive", "unarchive", "destroy", "retrieve", "mark_read"):
            return queryset.select_related("recipient", "event").only(
                "id", "title", "message", "is_read", "is_archived", "event_type", "created_at", "recipient__id", "recipient__username", "event__id", "event__title", "event__meeting_url", "event__event_type"
            )

        # Exclude archived by default unless explicitly requested
        include_archived = self.request.query_params.get("include_archived", "").lower() == "true"
        archived_only = self.request.query_params.get("archived_only", "").lower() == "true"
        if archived_only:
            queryset = queryset.filter(is_archived=True)
        elif not include_archived:
            queryset = queryset.filter(is_archived=False)

        # Use select_related for efficient queries
        return queryset.select_related("recipient", "event").only(
            "id",
            "title",
            "message",
            "is_read",
            "is_archived",
            "event_type",
            "created_at",
            "recipient__id",
            "recipient__username",
            "event__id",
            "event__title",
            "event__meeting_url",
            "event__event_type",
        )

    def list(self, request, *args, **kwargs):
        """
        List notifications with optional pagination.
        Use ?no_pagination=true to get all notifications without pagination.
        Use ?limit=10 to get specific number of notifications.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Check if no_pagination is requested (for notification dropdown)
        no_pagination = request.query_params.get("no_pagination", "").lower() == "true"
        limit = request.query_params.get("limit")

        if no_pagination:
            # For dropdown menu - return limited results without pagination structure
            if limit:
                try:
                    limit_int = int(limit)
                    queryset = queryset[:limit_int]
                except ValueError:
                    pass
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        # Standard paginated response
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        """Get unread notification count"""
        count = Notification.get_unread_count(request.user)
        return Response({"unread_count": count})

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        """Mark a single notification as read"""
        notification = self.get_object()
        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=["is_read"])
        return Response({"status": "marked as read"})

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        """Mark all notifications for the user as read"""
        updated = self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({"status": "all marked as read", "count": updated})

    @action(detail=False, methods=["post"], url_path="archive-old")
    def archive_old(self, request):
        """Archive old notifications (admin only)"""
        if not is_superadmin_user(request.user):
            return Response({"detail": "Only super admin can archive notifications."}, status=status.HTTP_403_FORBIDDEN)
        days = int(request.data.get("days", 90))
        archived_count = Notification.archive_old_notifications(days=days)
        return Response({"status": "archived", "count": archived_count})

    @action(detail=True, methods=["post"], url_path="archive")
    def archive(self, request, pk=None):
        """Archive a single notification (idempotent)"""
        notification = self.get_object()
        if not notification.is_archived:
            notification.is_archived = True
            notification.save(update_fields=["is_archived"])
        return Response({"status": "archived"})

    @action(detail=True, methods=["post"], url_path="unarchive")
    def unarchive(self, request, pk=None):
        """Unarchive a single notification (idempotent)"""
        notification = self.get_object()
        if notification.is_archived:
            notification.is_archived = False
            notification.save(update_fields=["is_archived"])
        return Response({"status": "unarchived"})

    def destroy(self, request, *args, **kwargs):
        """Delete a single notification"""
        notification = self.get_object()
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
