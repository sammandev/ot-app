"""Custom API exceptions for unified error handling."""

from rest_framework.exceptions import APIException, NotAuthenticated, PermissionDenied, ValidationError


class ApplicationError(APIException):
    """Generic application error with configurable status and code."""

    status_code = 400
    default_detail = "Application error"
    default_code = "application_error"

    def __init__(self, detail=None, status_code=None, code=None):
        if status_code is not None:
            self.status_code = status_code
        if code is not None:
            self.default_code = code
        super().__init__(detail or self.default_detail, code=self.default_code)


__all__ = [
    "ApplicationError",
    "ValidationError",
    "NotAuthenticated",
    "PermissionDenied",
]
