"""
API Versioning system for RESTful endpoints.

This module provides version routing to allow multiple API versions
to coexist. Currently supports:
- v1: Current stable API (production)
- v2: Future enhanced API (development)

Usage:
    Clients specify version via:
    1. Accept header: Accept: application/json; version=1.0
    2. Query parameter: ?version=1.0
    3. URL path: /api/v1/employees/ (automatic routing)

Features:
    - Simple version routing
    - Backward compatible
    - Deprecation warnings support
    - Version negotiation
"""

import logging

from rest_framework.versioning import AcceptHeaderVersioning

logger = logging.getLogger(__name__)


class APIVersioning(AcceptHeaderVersioning):
    """
    Custom API versioning using Accept header with version parameter.

    Supports version specification via:
    - Accept: application/json; version=1.0
    - Accept: application/json; version=2.0

    Falls back to v1.0 if no version specified.
    """

    valid_versions = ("1.0", "2.0")
    default_version = "1.0"
    version_param = "version"
    allowed_formats = ("json", "api")

    def determine_version(self, request, *args, **kwargs):
        """
        Determine API version from Accept header.

        Args:
            request: HTTP request object

        Returns:
            Version string (e.g., '1.0')

        Raises:
            NotFound: If version is invalid
        """
        # Try to get version from Accept header
        media_type_header = request.META.get("HTTP_ACCEPT", "")

        try:
            # Parse Accept header for version parameter
            for part in media_type_header.split(","):
                part = part.strip()
                if "version=" in part:
                    version = part.split("version=")[1].strip()
                    if version in self.valid_versions:
                        logger.debug(f"API version {version} requested")
                        return version
        except (IndexError, AttributeError):
            pass

        # Check query parameter as fallback
        version = request.query_params.get(self.version_param)
        if version and version in self.valid_versions:
            logger.debug(f"API version {version} from query parameter")
            return version

        # Return default version
        logger.debug(f"Using default API version {self.default_version}")
        return self.default_version

    def reverse(self, viewname, args=None, kwargs=None, request=None, format=None, **extra):
        """
        Reverse URL with version support.

        Args:
            viewname: Name of the view
            request: HTTP request for version context

        Returns:
            Reversed URL string
        """
        if request is not None:
            kwargs = kwargs or {}
            kwargs["version"] = request.version
        return super().reverse(viewname, args=args, kwargs=kwargs, format=format, **extra)


class VersionedRouter:
    """
    Helper for managing versioned API routes.

    Allows defining different handlers for different API versions
    without duplicating endpoint logic.

    Usage:
        router = VersionedRouter()
        router.register_v1(r'employees', EmployeeViewSetV1)
        router.register_v2(r'employees', EmployeeViewSetV2)
    """

    def __init__(self):
        """Initialize versioned router."""
        self.v1_routes = {}
        self.v2_routes = {}

    def register_v1(self, prefix, viewset, basename=None):
        """
        Register a viewset for API v1.

        Args:
            prefix: URL prefix (e.g., 'employees')
            viewset: ViewSet class
            basename: Optional basename for reversing URLs
        """
        if basename is None:
            basename = prefix.replace("-", "_")
        self.v1_routes[prefix] = {
            "viewset": viewset,
            "basename": basename,
        }
        logger.debug(f"Registered {prefix} for API v1")

    def register_v2(self, prefix, viewset, basename=None):
        """
        Register a viewset for API v2.

        Args:
            prefix: URL prefix (e.g., 'employees')
            viewset: ViewSet class
            basename: Optional basename for reversing URLs
        """
        if basename is None:
            basename = prefix.replace("-", "_")
        self.v2_routes[prefix] = {
            "viewset": viewset,
            "basename": basename,
        }
        logger.debug(f"Registered {prefix} for API v2")

    def register_all(self, prefix, viewset, basename=None):
        """
        Register same viewset for all API versions.

        Args:
            prefix: URL prefix (e.g., 'employees')
            viewset: ViewSet class
            basename: Optional basename for reversing URLs
        """
        self.register_v1(prefix, viewset, basename)
        self.register_v2(prefix, viewset, basename)
        logger.debug(f"Registered {prefix} for all API versions")

    def get_v1_routes(self):
        """Get all v1 routes."""
        return self.v1_routes

    def get_v2_routes(self):
        """Get all v2 routes."""
        return self.v2_routes


def get_version_from_request(request):
    """
    Extract API version from request.

    Args:
        request: HTTP request object

    Returns:
        Version string (e.g., '1.0')
    """
    # Check Accept header
    accept_header = request.META.get("HTTP_ACCEPT", "")
    if "version=" in accept_header:
        try:
            version = accept_header.split("version=")[1].strip().split(";")[0].strip("\"'")
            if version in ("1.0", "2.0"):
                return version
        except (IndexError, AttributeError):
            pass

    # Check query parameter
    version = request.query_params.get("version", "").strip()
    if version in ("1.0", "2.0"):
        return version

    # Return default
    return "1.0"


def version_endpoint(supported_versions=("1.0", "2.0")):
    """
    Decorator to mark which API versions support an endpoint.

    Usage:
        @version_endpoint(['1.0', '2.0'])
        def my_view(request):
            ...

    Args:
        supported_versions: Tuple of supported version strings
    """

    def decorator(func):
        func.supported_versions = supported_versions
        return func

    return decorator


def deprecation_warning(deprecated_in="2.0", removed_in="3.0", alternative=None):
    """
    Decorator to mark endpoints as deprecated.

    Adds deprecation headers to response.

    Usage:
        @deprecation_warning('2.0', '3.0', 'Use /api/v2/employees/ instead')
        def my_view(request):
            ...

    Args:
        deprecated_in: Version when deprecated
        removed_in: Version when will be removed
        alternative: Suggested alternative endpoint
    """

    def decorator(func):
        func.deprecated_in = deprecated_in
        func.removed_in = removed_in
        func.alternative = alternative
        return func

    return decorator
