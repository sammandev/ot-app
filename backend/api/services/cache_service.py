"""
Cache Service for Redis-based caching of API responses and querysets.

This service provides:
- High-level cache operations (set/get/delete/invalidate)
- Decorator for caching list view responses
- Cache statistics and monitoring
- Graceful handling of cache failures

Features:
- Automatic cache key generation
- TTL (Time To Live) configuration per view
- Cache hit/miss logging
- Fail-open behavior (returns data even if cache fails)
"""

import hashlib
import json
import logging
from collections.abc import Callable
from functools import wraps

from django.core.cache import cache
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class CacheService:
    """
    High-level cache operations for API responses and querysets.

    Handles caching of list views, individual objects, and custom data.
    Automatically generates cache keys and manages TTL.
    """

    # Cache key prefixes for different data types
    PREFIX_LIST = "list"
    PREFIX_OBJECT = "obj"
    PREFIX_CUSTOM = "custom"

    # Default TTL values (seconds) per endpoint
    DEFAULT_TTLS = {
        "employees": 3600,  # 1 hour
        "projects": 3600,  # 1 hour
        "overtime_requests": 300,  # 5 minutes (changes frequently)
        "calendar_events": 600,  # 10 minutes
        "default": 1800,  # 30 minutes
    }

    @staticmethod
    def generate_cache_key(
        prefix: str,
        view_name: str,
        query_params: dict | None = None,
        user_id: int | None = None,
    ) -> str:
        """
        Generate a unique cache key for a request.

        Args:
            prefix: Type of cache (list, obj, custom)
            view_name: Name of the view/endpoint
            query_params: Query parameters to include in key
            user_id: User ID (if user-specific cache)

        Returns:
            Unique cache key string
        """
        key_parts = [prefix, view_name]

        if user_id:
            key_parts.append(f"user_{user_id}")

        if query_params:
            # Sort params for consistent key generation
            params_str = json.dumps(query_params, sort_keys=True, default=str)
            params_hash = hashlib.sha256(params_str.encode()).hexdigest()[:16]
            key_parts.append(params_hash)

        cache_key = ":".join(key_parts)
        logger.debug("Generated cache key: %s", cache_key)
        return cache_key

    @staticmethod
    def set_list(
        view_name: str,
        data: list,
        query_params: dict | None = None,
        user_id: int | None = None,
        ttl: int | None = None,
    ) -> bool:
        """
        Cache a list view response.

        Args:
            view_name: Name of the view (e.g., 'employees', 'projects')
            data: List data to cache
            query_params: Query parameters used in the request
            user_id: User ID (if user-specific)
            ttl: Time to live in seconds

        Returns:
            True if successfully cached, False otherwise
        """
        try:
            cache_key = CacheService.generate_cache_key(
                CacheService.PREFIX_LIST,
                view_name,
                query_params,
                user_id,
            )

            ttl = ttl or CacheService.DEFAULT_TTLS.get(view_name, CacheService.DEFAULT_TTLS["default"])
            cache.set(cache_key, data, timeout=ttl)
            logger.info("Cached list '%s' for %ss (key: %s)", view_name, ttl, cache_key)
            return True
        except Exception as e:
            logger.warning("Failed to cache list '%s': %s", view_name, e)
            return False

    @staticmethod
    def get_list(
        view_name: str,
        query_params: dict | None = None,
        user_id: int | None = None,
    ) -> list | None:
        """
        Retrieve a cached list view response.

        Args:
            view_name: Name of the view
            query_params: Query parameters used in the request
            user_id: User ID (if user-specific)

        Returns:
            Cached list data or None if not found
        """
        try:
            cache_key = CacheService.generate_cache_key(
                CacheService.PREFIX_LIST,
                view_name,
                query_params,
                user_id,
            )

            data = cache.get(cache_key)
            if data is not None:
                logger.debug("Cache HIT for list '%s'", view_name)
                return data
            logger.debug("Cache MISS for list '%s'", view_name)
            return None
        except Exception as e:
            logger.warning("Failed to retrieve cached list '%s': %s", view_name, e)
            return None

    @staticmethod
    def set_object(
        view_name: str,
        obj_id: int,
        data: dict,
        ttl: int | None = None,
    ) -> bool:
        """
        Cache a single object.

        Args:
            view_name: Name of the view
            obj_id: Object ID
            data: Object data to cache
            ttl: Time to live in seconds

        Returns:
            True if successfully cached
        """
        try:
            cache_key = CacheService.generate_cache_key(
                CacheService.PREFIX_OBJECT,
                view_name,
            )
            cache_key = f"{cache_key}:{obj_id}"

            ttl = ttl or CacheService.DEFAULT_TTLS.get(view_name, CacheService.DEFAULT_TTLS["default"])
            cache.set(cache_key, data, timeout=ttl)
            logger.debug("Cached object '%s:%s'", view_name, obj_id)
            return True
        except Exception as e:
            logger.warning("Failed to cache object '%s:%s': %s", view_name, obj_id, e)
            return False

    @staticmethod
    def get_object(view_name: str, obj_id: int) -> dict | None:
        """
        Retrieve a cached object.

        Args:
            view_name: Name of the view
            obj_id: Object ID

        Returns:
            Cached object data or None
        """
        try:
            cache_key = CacheService.generate_cache_key(
                CacheService.PREFIX_OBJECT,
                view_name,
            )
            cache_key = f"{cache_key}:{obj_id}"
            return cache.get(cache_key)
        except Exception as e:
            logger.warning("Failed to retrieve cached object '%s:%s': %s", view_name, obj_id, e)
            return None

    @staticmethod
    def invalidate(
        view_name: str,
        query_params: dict | None = None,
        user_id: int | None = None,
        cache_type: str = "list",
    ) -> bool:
        """
        Invalidate (delete) a cached entry.

        Args:
            view_name: Name of the view
            query_params: Query parameters (for specific cache entries)
            user_id: User ID (if user-specific)
            cache_type: Type of cache (list, obj)

        Returns:
            True if successfully invalidated
        """
        try:
            cache_key = CacheService.generate_cache_key(
                cache_type,
                view_name,
                query_params,
                user_id,
            )
            cache.delete(cache_key)
            logger.info("Invalidated cache for '%s' (key: %s)", view_name, cache_key)
            return True
        except Exception as e:
            logger.warning("Failed to invalidate cache for '%s': %s", view_name, e)
            return False

    @staticmethod
    def invalidate_all_for_view(view_name: str) -> int:
        """
        Invalidate all cache entries for a specific view.

        Uses django-redis's delete_pattern() for wildcard key deletion.
        Falls back to deleting known prefixed keys if delete_pattern
        is not available on the cache backend.

        Args:
            view_name: Name of the view

        Returns:
            Number of entries deleted (approximate)
        """
        deleted = 0
        try:
            # django-redis supports delete_pattern with glob-style wildcards
            if hasattr(cache, "delete_pattern"):
                for prefix in (CacheService.PREFIX_LIST, CacheService.PREFIX_OBJECT, CacheService.PREFIX_CUSTOM):
                    pattern = f"*{prefix}:{view_name}*"
                    cache.delete_pattern(pattern)
                    deleted += 1  # approximate — delete_pattern doesn't return count
                logger.info("Invalidated all cache for '%s' via delete_pattern", view_name)
            else:
                # Fallback: delete the known prefixed keys (no wildcard)
                for prefix in (CacheService.PREFIX_LIST, CacheService.PREFIX_OBJECT, CacheService.PREFIX_CUSTOM):
                    key = f"{prefix}:{view_name}"
                    if cache.delete(key):
                        deleted += 1
                logger.info("Invalidated %d cache key(s) for '%s' (no delete_pattern support)", deleted, view_name)
            return max(deleted, 1)
        except Exception as e:
            logger.warning("Failed to invalidate all cache for '%s': %s", view_name, e)
            return 0

    @staticmethod
    def get_stats() -> dict:
        """
        Get cache statistics and health info.

        Returns:
            Dictionary with cache stats
        """
        try:
            # Try to get cache stats if backend supports it
            return {
                "status": "ok",
                "backend": cache.__class__.__name__,
            }
        except Exception as e:
            logger.error("Failed to get cache stats: %s", e)
            return {"status": "error", "message": str(e)}


def cached_list(
    view_name: str,
    ttl: int | None = None,
    user_specific: bool = False,
):
    """
    Decorator for caching list view responses.

    Usage:
        @cached_list('employees', ttl=3600)
        def list(self, request, *args, **kwargs):
            return super().list(request, *args, **kwargs)

    Args:
        view_name: Name of the view for cache key generation
        ttl: Time to live in seconds (optional)
        user_specific: If True, cache is per-user

    Returns:
        Decorated function that caches responses
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            try:
                # Determine cache key components
                user_id = request.user.id if user_specific and request.user.is_authenticated else None
                query_params = dict(request.query_params) if request.query_params else None

                # Try to get from cache
                cached_data = CacheService.get_list(view_name, query_params, user_id)
                if cached_data is not None:
                    return Response(cached_data)

                # Call the original view
                response = func(self, request, *args, **kwargs)

                # Cache the response data if successful
                if response.status_code == 200 and response.data:
                    CacheService.set_list(
                        view_name,
                        response.data,
                        query_params,
                        user_id,
                        ttl,
                    )

                return response
            except Exception as e:
                # Fail-open: return uncached response on any error
                logger.error("Error in cached_list decorator for '%s': %s", view_name, e)
                return func(self, request, *args, **kwargs)

        return wrapper

    return decorator


def cache_invalidate_on_change(view_names: list):
    """
    Decorator to invalidate cache when a create/update/delete happens.

    Used with perform_create, perform_update, perform_destroy methods.

    Usage:
        @cache_invalidate_on_change(['employees'])
        def perform_update(self, serializer):
            serializer.save()

    Args:
        view_names: List of view names whose cache should be invalidated

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Call the original function
            result = func(self, *args, **kwargs)

            # Invalidate cache for specified views
            for view_name in view_names:
                try:
                    CacheService.invalidate_all_for_view(view_name)
                except Exception as e:
                    logger.error("Failed to invalidate cache for '%s': %s", view_name, e)

            return result

        return wrapper

    return decorator
