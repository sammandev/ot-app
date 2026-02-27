"""
Custom pagination classes for API responses.

Provides pagination strategies:
- PageNumberPagination: Traditional page number based
- CursorPagination: Cursor-based (better for large datasets)
- LimitOffsetPagination: Limit/offset based
- DynamicPagination: Paginate only if data exceeds threshold

Features:
    - Configurable page size
    - Default page size
    - Max page size
    - Custom response format
    - Performance optimized
"""

import logging

from rest_framework.pagination import (
    CursorPagination as DRFCursorPagination,
)
from rest_framework.pagination import (
    PageNumberPagination as DRFPageNumberPagination,
)
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class StandardPageNumberPagination(DRFPageNumberPagination):
    """
    Standard page number pagination for list endpoints.

    Features:
    - Page size: configurable per request via ?page_size=50
    - Default: 25 items per page
    - Max: 100 items per page

    Response format:
    {
        "count": 100,
        "next": "http://api.example.com/users/?page=2",
        "previous": null,
        "results": [...]
    }
    """

    page_size = 50
    page_size_query_param = "page_size"
    page_size_query_description = "Number of results to return per page"
    max_page_size = 500
    page_query_param = "page"
    page_query_description = "A page number within the paginated result set"


class EmployeePagination(DRFPageNumberPagination):
    """
    Pagination for employee list endpoint.

    - Default: 100 employees per page
    - Max: 500 employees per page
    """

    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 500


class ProjectPagination(DRFPageNumberPagination):
    """
    Pagination for project list endpoint.

    - Default: 100 projects per page
    - Max: 500 projects per page
    """

    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 500


class OvertimeRequestPagination(DRFPageNumberPagination):
    """
    Pagination for overtime request list endpoint.

    - Default: 100 requests per page (larger history views)
    - Max: 500 requests per page
    """

    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 500


class CalendarEventPagination(DRFPageNumberPagination):
    """
    Pagination for calendar event list endpoint.

    - Default: 100 events per page
    - Max: 500 events per page
    """

    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 500


class SmallResultSetPagination(DRFPageNumberPagination):
    """
    Pagination for small result sets.

    - Default: 10 items per page
    - Max: 20 items per page
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 20


class LargeResultSetPagination(DRFPageNumberPagination):
    """
    Pagination for large result sets.

    - Default: 100 items per page
    - Max: 500 items per page
    """

    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 500


class CursorBasedPagination(DRFCursorPagination):
    """
    Cursor-based pagination for efficient large dataset handling.

    Better than offset pagination for large datasets:
    - O(1) lookup instead of O(n)
    - More stable with insertions/deletions
    - Perfect for mobile/streaming use cases

    Features:
    - Ordered by timestamp (most recent first)
    - Opaque cursor encoding
    - Forward/backward navigation

    Usage: Include ?cursor=... in request

    Response format:
    {
        "next": "http://api.example.com/users/?cursor=xxx",
        "previous": "http://api.example.com/users/?cursor=yyy",
        "results": [...]
    }
    """

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100
    ordering = "-created_at"  # Must exist on model
    cursor_query_description = "Opaque pagination cursor"


class DynamicPagination(DRFPageNumberPagination):
    """
    Dynamic pagination that paginates only if results exceed threshold.

    Useful for:
    - Small result sets that fit in single response
    - Avoiding pagination overhead for small queries
    - Automatic pagination when needed

    Features:
    - Returns all results if count <= threshold
    - Paginates if count > threshold
    - Threshold configurable per request
    """

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100
    threshold = 50  # Paginate if more than 50 results
    max_threshold = 500  # Upper limit for user-supplied threshold

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate only if results exceed threshold.

        Args:
            queryset: QuerySet to paginate
            request: HTTP request
            view: ViewSet instance

        Returns:
            Paginated results or unpaginated list
        """
        # Get threshold from request or use default, clamped to safe range
        try:
            threshold = int(request.query_params.get("threshold", self.threshold))
        except (ValueError, TypeError):
            threshold = self.threshold
        threshold = max(1, min(threshold, self.max_threshold))

        # Count results
        count = queryset.count()

        # If below threshold, return all without pagination
        if count <= threshold:
            logger.debug("Result count %s <= threshold %s, skipping pagination", count, threshold)
            return list(queryset)

        # Otherwise, use normal pagination
        logger.debug("Result count %s > threshold %s, applying pagination", count, threshold)
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        """
        Return paginated response with metadata.

        Args:
            data: Paginated data

        Returns:
            Response with pagination info
        """
        return Response(
            {"count": self.page.paginator.count, "next": self.get_next_link(), "previous": self.get_previous_link(), "page_size": self.page.paginator.per_page, "total_pages": self.page.paginator.num_pages, "current_page": self.page.number, "results": data}
        )


class PaginationMetadata(DRFPageNumberPagination):
    """
    Enhanced pagination with detailed metadata.

    Provides additional information:
    - Total pages
    - Current page
    - Items per page
    - Start/end indices

    Response format:
    {
        "count": 100,
        "total_pages": 4,
        "page_size": 25,
        "current_page": 1,
        "start_index": 1,
        "end_index": 25,
        "next": "...",
        "previous": null,
        "results": [...]
    }
    """

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        """
        Return response with enhanced pagination metadata.

        Args:
            data: Paginated results

        Returns:
            Response with detailed metadata
        """
        page = self.page
        paginator = page.paginator

        # Calculate start and end indices
        start_index = (page.number - 1) * page.paginator.per_page + 1
        end_index = min(page.number * page.paginator.per_page, paginator.count)

        return Response(
            {
                "count": paginator.count,
                "total_pages": paginator.num_pages,
                "page_size": paginator.per_page,
                "current_page": page.number,
                "start_index": start_index,
                "end_index": end_index,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )
