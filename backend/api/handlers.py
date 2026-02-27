"""Custom exception handler to normalize API error responses."""

import logging
import traceback

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from .exceptions import ApplicationError

logger = logging.getLogger(__name__)


def _build_error_payload(code: str, message: str, details=None):
    return {
        "code": code,
        "message": message,
        "details": details,
    }


def custom_exception_handler(exc, context):
    """Return standardized error responses while reusing DRF defaults."""

    response = exception_handler(exc, context)

    # If DRF already handled it, wrap the data
    if response is not None:
        code = getattr(exc, "default_code", "error")
        message = getattr(exc, "detail", response.data)
        details = response.data
        payload = _build_error_payload(str(code), str(message), details)
        response.data = payload
        return response

    # Fallback for unhandled exceptions
    if isinstance(exc, ApplicationError):
        return Response(
            _build_error_payload(exc.default_code, str(exc.detail), None),
            status=exc.status_code,
        )

    # Log unhandled exceptions with full traceback
    view = context.get("view", None)
    request = context.get("request", None)
    view_name = view.__class__.__name__ if view else "Unknown"
    method = request.method if request else "Unknown"
    path = request.path if request else "Unknown"

    logger.error("Unhandled exception in %s [%s %s]: %s", view_name, method, path, exc)
    logger.error("Exception type: %s", type(exc).__name__)
    logger.error("Traceback:\n%s", traceback.format_exc())

    return Response(
        _build_error_payload("server_error", f"An unexpected error occurred: {str(exc)}", None),
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
