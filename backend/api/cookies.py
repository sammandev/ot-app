"""
JWT Cookie Helpers
Set and clear httpOnly JWT cookies for secure token storage.

Cookies use:
- httpOnly: prevents JavaScript access (XSS protection)
- Secure: only sent over HTTPS (in production)
- SameSite=Lax: prevents cross-site request forgery
- Path scoping: limits which endpoints receive the cookie
"""

from django.conf import settings

ACCESS_COOKIE_NAME = "access_token"
REFRESH_COOKIE_NAME = "refresh_token"


def set_auth_cookies(response, access_token, refresh_token=None):
    """
    Set httpOnly JWT cookies on the response.

    The access token cookie is scoped to /api/ (all API endpoints).
    The refresh token cookie is scoped to /api/auth/ (auth endpoints only).
    """
    secure = not settings.DEBUG
    samesite = "Lax"

    # Access token — sent with all API requests
    response.set_cookie(
        ACCESS_COOKIE_NAME,
        access_token,
        max_age=int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
        httponly=True,
        secure=secure,
        samesite=samesite,
        path="/api/",
    )

    # Refresh token — only sent with auth endpoints (narrower scope)
    if refresh_token:
        response.set_cookie(
            REFRESH_COOKIE_NAME,
            refresh_token,
            max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
            httponly=True,
            secure=secure,
            samesite=samesite,
            path="/api/auth/",
        )

    return response


def clear_auth_cookies(response):
    """
    Clear JWT cookies from the response.
    Must use the same path= as set_auth_cookies for the delete to work.
    """
    response.delete_cookie(ACCESS_COOKIE_NAME, path="/api/")
    response.delete_cookie(REFRESH_COOKIE_NAME, path="/api/auth/")
    return response
