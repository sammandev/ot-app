import logging

from django.contrib.auth import get_user_model
from django.db import models
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import (
    PersonalNote,
)
from ..pagination import DynamicPagination
from ..serializers import (
    PersonalNoteSerializer,
)
from .helpers import get_employee_for_user, is_developer_user, is_ptb_admin, is_superadmin_user  # noqa: F401

logger = logging.getLogger(__name__)
User = get_user_model()


class PersonalNoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for personal notes (sticky notes / personal board).
    Users can only see and manage their own notes.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PersonalNoteSerializer
    pagination_class = DynamicPagination

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return PersonalNote.objects.none()
        if not getattr(self.request, "user", None) or not self.request.user.is_authenticated:
            return PersonalNote.objects.none()
        return PersonalNote.objects.filter(owner=self.request.user).order_by("-is_pinned", "order", "-created_at")

    def get_object(self):
        """Enforce object-level ownership — users can only access their own notes."""
        obj = super().get_object()
        if obj.owner_id != self.request.user.id:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("You do not have permission to access this note.")
        return obj

    def perform_create(self, serializer):
        # Get max order for user's notes
        max_order = PersonalNote.objects.filter(owner=self.request.user).aggregate(max_order=models.Max("order"))["max_order"] or 0
        serializer.save(owner=self.request.user, order=max_order + 1)

    @action(detail=False, methods=["post"])
    def reorder(self, request):
        """
        Reorder notes. Expects: { "order": [id1, id2, id3, ...] }
        """
        order_list = request.data.get("order", [])

        if order_list:
            from django.db.models import Case, IntegerField, Value, When

            cases = [When(id=nid, then=Value(idx)) for idx, nid in enumerate(order_list)]
            PersonalNote.objects.filter(id__in=order_list, owner=request.user).update(order=Case(*cases, output_field=IntegerField()))

        return Response({"status": "ok"})

    @action(detail=True, methods=["post"])
    def toggle_pin(self, request, pk=None):
        """Toggle pinned status of a note."""
        note = self.get_object()
        note.is_pinned = not note.is_pinned
        note.save(update_fields=["is_pinned"])
        return Response(self.get_serializer(note).data)

    @action(detail=True, methods=["post"])
    def toggle_complete(self, request, pk=None):
        """Toggle completed status of a note."""
        note = self.get_object()
        note.is_completed = not note.is_completed
        note.save(update_fields=["is_completed"])
        return Response(self.get_serializer(note).data)
