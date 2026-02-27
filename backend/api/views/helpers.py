import logging

from django.contrib.auth import get_user_model
from rest_framework import serializers

from ..models import (
    Employee,
)

logger = logging.getLogger(__name__)
User = get_user_model()


def is_superadmin_user(user):
    """
    Check if a user is a superadmin (either developer or superadmin role).
    Uses the 'role' field on ExternalUser.
    """
    if not user:
        return False

    role = getattr(user, "role", "") or ""
    return role in ("developer", "superadmin")


def is_developer_user(user):
    """
    Check if a user is a developer (highest privilege, cannot be modified).
    Uses the 'role' field on ExternalUser.
    """
    if not user:
        return False

    role = getattr(user, "role", "") or ""
    return role == "developer"


def is_ptb_admin(user):
    """
    Check if a user has PTB admin privileges.
    """
    if not user:
        return False
    return bool(getattr(user, "is_ptb_admin", False))


def get_employee_for_user(user, raise_if_not_found=True):
    """
    Get the Employee record associated with the current user.

    Matching strategy (in order of priority):
    1. Match Employee.emp_id with User.worker_id
    2. Match Employee.name with User's full name (first_name + last_name)
    3. Match Employee.name with User.username (handles firstname_lastname format)

    If raise_if_not_found is True and employee is not found, raises ValidationError.
    If raise_if_not_found is False and employee is not found, returns None.

    This function also tries to auto-create an Employee record if the user has
    a valid worker_id but no matching employee exists.

    Uses per-request caching on the user object to avoid repeated DB lookups.
    """
    if not user:
        if raise_if_not_found:
            raise serializers.ValidationError({"detail": "User not authenticated. Please log in again."})
        return None

    # Per-request cache: avoid re-querying within the same request
    cache_attr = "_employee_cache"
    if hasattr(user, cache_attr):
        cached = getattr(user, cache_attr)
        if cached is not None or not raise_if_not_found:
            return cached

    employee = None

    # Build a single consolidated query with Q objects to replace
    # the sequential per-strategy lookup (avoids up to 5 queries).
    from django.db.models import Q

    q_filter = Q()

    # Strategy 1: emp_id == worker_id
    worker_id = getattr(user, "worker_id", None)
    if worker_id:
        q_filter |= Q(emp_id=worker_id)

    # Strategy 2: name == full_name
    full_name = f"{user.first_name} {user.last_name}".strip()
    if full_name:
        q_filter |= Q(name__iexact=full_name)

    # Strategy 3: name == username-derived name
    username = getattr(user, "username", None)
    name_from_username = None
    if username:
        name_from_username = username.replace("_", " ")
        if name_from_username.lower() != (full_name or "").lower():
            q_filter |= Q(name__iexact=name_from_username)

    if q_filter:
        # Run a single query with all conditions OR'd
        candidates = list(Employee.objects.filter(q_filter)[:10])

        # Pick the best match in priority order
        for candidate in candidates:
            if worker_id and candidate.emp_id == worker_id:
                employee = candidate
                break
        if not employee and full_name:
            for candidate in candidates:
                if candidate.name and candidate.name.lower() == full_name.lower():
                    employee = candidate
                    break
        if not employee and name_from_username:
            for candidate in candidates:
                if candidate.name and candidate.name.lower() == name_from_username.lower():
                    employee = candidate
                    break
            # Partial match fallback (contains)
            if not employee and name_from_username:
                for candidate in candidates:
                    if candidate.name and name_from_username.lower() in candidate.name.lower():
                        employee = candidate
                        break

    if employee:
        setattr(user, cache_attr, employee)
        return employee

    # Auto-provision: create a minimal Employee record so the user can use task
    # features (comments, checklists, time logs).  Admins should review and
    # complete the record (department, supervisor, etc.) via the Employee admin page.
    # Uses get_or_create to prevent duplicate records from race conditions.
    if hasattr(user, "worker_id") and user.worker_id:
        try:
            create_name = full_name if full_name else user.username.replace("_", " ")

            employee, created = Employee.objects.get_or_create(
                emp_id=user.worker_id,
                defaults={
                    "name": create_name,
                    "is_enabled": True,
                },
            )
            if created:
                logger.warning("Auto-provisioned Employee for user %s (worker_id=%s). Admin should review this record.", user.username, user.worker_id)
            setattr(user, cache_attr, employee)
            return employee
        except Exception as e:
            logger.error("Failed to auto-provision employee for user %s: %s", user.username, e)

    if raise_if_not_found:
        worker_id = getattr(user, "worker_id", "N/A")
        raise serializers.ValidationError({"detail": f"Employee not found for current user (username: {user.username}, worker_id: {worker_id}). Please contact your administrator to create an employee record."})
    setattr(user, cache_attr, None)
    return None
