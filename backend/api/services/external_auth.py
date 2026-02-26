"""
External Authentication Service
Handles communication with external authentication API at http://172.18.220.56:9001
"""

import logging

import requests
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed

logger = logging.getLogger(__name__)


class ExternalAuthService:
    """Service for interacting with external authentication API"""

    BASE_URL = getattr(settings, "EXTERNAL_API_URL", "http://172.18.220.56:9001")
    TIMEOUT = getattr(settings, "EXTERNAL_API_TIMEOUT", 10)

    @classmethod
    def login(cls, username, password):
        """
        Login to external API and get tokens

        Args:
            username: User's username
            password: User's password

        Returns:
            dict: {
                'access': 'token...',
                'refresh': 'token...',
                'user_data': {...}
            }

        Raises:
            AuthenticationFailed: If login fails
        """
        url = f"{cls.BASE_URL}/api/user/token/"

        try:
            response = requests.post(url, json={"username": username, "password": password}, timeout=cls.TIMEOUT)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successful login for user: {username}")
                return {"access": data.get("access"), "refresh": data.get("refresh"), "user_data": data}
            elif response.status_code == 401:
                logger.warning(f"Invalid credentials for user: {username}")
                raise AuthenticationFailed("Invalid username or password")
            else:
                logger.error(f"Login failed with status {response.status_code}")
                raise AuthenticationFailed("Authentication service error")

        except requests.exceptions.Timeout as e:
            logger.error(f"External API timeout for user: {username}")
            raise AuthenticationFailed("Authentication service timeout") from e
        except requests.exceptions.RequestException as e:
            logger.error(f"External API error: {str(e)}")
            raise AuthenticationFailed("Authentication service unavailable") from e

    @classmethod
    def refresh_token(cls, refresh_token):
        """
        Refresh access token using refresh token

        Args:
            refresh_token: The refresh token from login

        Returns:
            str: New access token

        Raises:
            AuthenticationFailed: If refresh fails
        """
        url = f"{cls.BASE_URL}/api/user/token/refresh/"

        try:
            response = requests.post(url, json={"refresh": refresh_token}, timeout=cls.TIMEOUT)

            if response.status_code == 200:
                data = response.json()
                logger.info("Token refreshed successfully")
                return data.get("access")
            else:
                logger.warning("Token refresh failed")
                raise AuthenticationFailed("Token refresh failed")

        except requests.exceptions.RequestException as e:
            logger.error(f"Token refresh error: {str(e)}")
            raise AuthenticationFailed("Token refresh service unavailable") from e

    @classmethod
    def get_user_info(cls, access_token):
        """
        Get user account info from external API

        Args:
            access_token: The access token from login

        Returns:
            dict: User account information including permissions and groups

        Raises:
            AuthenticationFailed: If request fails or token invalid
        """
        url = f"{cls.BASE_URL}/api/user/account/info"
        headers = {"Authorization": f"Bearer {access_token}"}

        try:
            response = requests.get(url, headers=headers, timeout=cls.TIMEOUT)

            if response.status_code == 200:
                data = response.json()
                logger.debug(f"Retrieved user info for: {data.get('username')}")
                return data
            elif response.status_code == 401:
                logger.warning("Invalid or expired token")
                raise AuthenticationFailed("Token is invalid or expired")
            else:
                logger.error(f"Get user info failed with status {response.status_code}")
                raise AuthenticationFailed("Failed to retrieve user information")

        except requests.exceptions.RequestException as e:
            logger.error(f"Get user info error: {str(e)}")
            raise AuthenticationFailed("User info service unavailable") from e

    @classmethod
    def verify_token(cls, access_token):
        """
        Verify token with external API

        Args:
            access_token: The access token to verify

        Returns:
            bool: True if token is valid, False otherwise

        Raises:
            AuthenticationFailed: If verification request fails
        """
        url = f"{cls.BASE_URL}/user/token/verify"

        try:
            response = requests.post(url, json={"token": access_token}, timeout=cls.TIMEOUT)

            if response.status_code == 200:
                logger.debug("External token is valid")
                return True
            elif response.status_code == 401:
                logger.debug("External token is invalid or expired")
                return False
            else:
                logger.warning(f"Token verification returned status {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Token verification error: {str(e)}")
            raise AuthenticationFailed("Token verification service unavailable") from e

    @classmethod
    def decode_token_payload(cls, access_token):
        """
        Decode JWT token payload (without verification)
        Used to get expiration time and other metadata

        Args:
            access_token: The JWT token to decode

        Returns:
            dict: Token payload with exp, iat, user_id, etc.
        """
        import base64
        import json

        try:
            # JWT format: header.payload.signature
            parts = access_token.split(".")
            if len(parts) != 3:
                raise ValueError("Invalid token format")

            # Decode payload (add padding if needed)
            payload = parts[1]
            payload += "=" * (4 - len(payload) % 4)
            decoded = base64.urlsafe_b64decode(payload)

            return json.loads(decoded)
        except Exception as e:
            logger.error(f"Token decode error: {str(e)}")
            return {}
