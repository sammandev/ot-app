from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Document
from ..pagination import StandardPageNumberPagination
from ..permissions import ResourcePermission
from ..serializers import DocumentDetailSerializer, DocumentListSerializer, DocumentWriteSerializer
from ..services.document_metadata import fetch_link_metadata


class DocumentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ResourcePermission]
    resource_name = "documents"
    queryset = Document.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    search_fields = ["title", "description", "original_filename", "external_url", "category"]
    ordering_fields = ["title", "source_type", "created_at", "updated_at", "category", "stored_file_size", "is_pinned"]
    ordering = ["-is_pinned", "-created_at"]
    pagination_class = StandardPageNumberPagination

    def get_queryset(self):
        queryset = Document.objects.select_related("created_by", "updated_by")

        if self.action == "list":
            queryset = queryset.defer("description", "normalized_url")

        source_type = self.request.query_params.get("source_type")
        if source_type:
            parts = [v.strip() for v in source_type.split(",") if v.strip()]
            queryset = queryset.filter(source_type__in=parts)

        category_values = self._extract_filter_values("categories", "category")
        if category_values:
            category_query = Q()
            for category in category_values:
                category_query |= Q(category__iexact=category)
            queryset = queryset.filter(category_query)

        tag_values = self._extract_filter_values("tags", "tag")
        if tag_values:
            tag_query = Q()
            for tag in tag_values:
                tag_query |= Q(tags__icontains=f"|{tag.lower()}|")
            queryset = queryset.filter(tag_query)

        pinned = self.request.query_params.get("pinned")
        if pinned is not None:
            queryset = queryset.filter(is_pinned=pinned.lower() == "true")

        previewable = self.request.query_params.get("previewable")
        if previewable is not None:
            preview_query = (
                Q(mime_type__startswith="image/")
                | Q(mime_type="application/pdf")
                | Q(mime_type__in=["application/json", "text/plain", "text/csv", "application/csv", "application/vnd.ms-excel"])
                | Q(extension__in=["png", "jpg", "jpeg", "gif", "webp", "svg", "bmp", "pdf", "txt", "json", "ini", "log", "csv"])
            )
            if previewable.lower() == "true":
                queryset = queryset.filter(source_type=Document.SourceType.FILE).filter(preview_query)
            else:
                queryset = queryset.exclude(Q(source_type=Document.SourceType.FILE) & preview_query)

        return queryset

    def _extract_filter_values(self, plural_name, singular_name):
        values = []
        for raw_value in self.request.query_params.getlist(plural_name):
            values.extend(part.strip() for part in raw_value.split(",") if part.strip())

        singular_value = self.request.query_params.get(singular_name)
        if singular_value:
            values.extend(part.strip() for part in singular_value.split(",") if part.strip())

        seen = set()
        normalized = []
        for value in values:
            lowered = value.lower()
            if lowered in seen:
                continue
            seen.add(lowered)
            normalized.append(value)
        return normalized

    @action(detail=False, methods=["get"], url_path="filter-options")
    def filter_options(self, request):
        queryset = self.get_queryset()
        categories = sorted({document.category.strip() for document in queryset if document.category.strip()}, key=str.lower)

        tags = set()
        for document in queryset:
            for tag in document.tags.split("|"):
                normalized_tag = tag.strip().lower()
                if normalized_tag:
                    tags.add(normalized_tag)

        return Response({
            "categories": categories,
            "tags": sorted(tags),
        })

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return DocumentWriteSerializer
        if self.action == "retrieve":
            return DocumentDetailSerializer
        return DocumentListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=False, methods=["post"], url_path="bulk-pin")
    def bulk_pin(self, request):
        ids = request.data.get("ids") or []
        pinned = request.data.get("pinned")

        if not isinstance(ids, list) or not ids:
            return Response({"detail": "A non-empty ids list is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(pinned, bool):
            return Response({"detail": "A boolean pinned value is required."}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset().filter(id__in=ids)
        updated_count = queryset.update(is_pinned=pinned, updated_by=request.user)
        return Response({"count": updated_count, "pinned": pinned})

    @action(detail=False, methods=["post"], url_path="bulk-delete")
    def bulk_delete(self, request):
        ids = request.data.get("ids") or []
        if not isinstance(ids, list) or not ids:
            return Response({"detail": "A non-empty ids list is required."}, status=status.HTTP_400_BAD_REQUEST)

        queryset = list(self.get_queryset().filter(id__in=ids))
        deleted_count = 0
        for document in queryset:
            document.delete()
            deleted_count += 1

        return Response({"count": deleted_count}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="refresh-metadata")
    def refresh_metadata(self, request, pk=None):
        document = self.get_object()
        if document.source_type != Document.SourceType.LINK:
            return Response({"detail": "Metadata refresh is only available for link documents."}, status=status.HTTP_400_BAD_REQUEST)

        metadata = fetch_link_metadata(document.normalized_url or document.external_url)
        document.normalized_url = metadata["normalized_url"]
        document.link_title = metadata["link_title"]
        document.link_description = metadata["link_description"]
        document.link_site_name = metadata["link_site_name"]
        document.link_favicon_url = metadata["link_favicon_url"]
        document.link_image_url = metadata["link_image_url"]
        document.metadata_status = metadata["metadata_status"]
        document.metadata_error = metadata["metadata_error"]
        document.metadata_fetched_at = metadata["metadata_fetched_at"]
        document.updated_by = request.user
        document.save(update_fields=[
            "normalized_url",
            "link_title",
            "link_description",
            "link_site_name",
            "link_favicon_url",
            "link_image_url",
            "metadata_status",
            "metadata_error",
            "metadata_fetched_at",
            "updated_by",
            "updated_at",
        ])

        serializer = DocumentDetailSerializer(document, context=self.get_serializer_context())
        return Response(serializer.data)
