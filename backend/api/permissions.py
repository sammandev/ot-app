import logging

from rest_framework import permissions

logger = logging.getLogger(__name__)


class IsSuperAdmin(permissions.BasePermission):
    """
    Only allows access to users with 'developer' or 'superadmin' role.
    Use this on ViewSets that require elevated admin access.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = getattr(request.user, "role", "") or ""
        return role in ("developer", "superadmin")


class ResourcePermission(permissions.BasePermission):
    """
    Custom permission for granular resource access control.
    Checks user.menu_permissions for explicit Allow/Deny of CRUD actions.

    Regular-user default access policy (when no explicit menu_permissions entry exists):
    - overtime_form: CRUD
    - overtime_history: read-only
    - projects: read-only
    - departments: read-only
    - calendar: CRUD
    - employees: read-only
    - kanban / calendar_events: CRUD
    - purchasing: CRUD (covers Purchase Requests and Request Purchase pages)
    - assets: CRUD
    - regulations: read-only

    Expected menu_permissions format:
    {
       "resource_name": ["create", "read", "update", "delete"],
       ...
    }

    If resource_name is not in menu_permissions, default behavior applies.
    """

    # Key aliases to handle naming differences between frontend sidebar/Access Control keys
    # and backend resource_name values (e.g., sidebar uses 'admin_employees' but backend uses 'employees').
    # Defined at class level to avoid re-creating the dict on every request.
    KEY_ALIASES = {
        "employees": ["employees", "admin_employees"],
        "admin_employees": ["employees", "admin_employees"],
        "regulations": ["regulations", "admin_regulations"],
        "admin_regulations": ["regulations", "admin_regulations"],
        "overtime_form": ["overtime_form", "ot_form"],
        "ot_form": ["overtime_form", "ot_form"],
        "overtime_history": ["overtime_history", "ot_history"],
        "ot_history": ["overtime_history", "ot_history"],
        "overtime_summary": ["overtime_summary", "ot_summary"],
        "ot_summary": ["overtime_summary", "ot_summary"],
    }

    def has_permission(self, request, view):
        # 1. Authentication check
        if not request.user or not request.user.is_authenticated:
            logger.debug("Permission denied: User not authenticated")
            return False

        # 2. Superadmin bypass via role field (developer / superadmin)
        # Note: We check this explicitly because is_superuser might be granted to others
        role = getattr(request.user, "role", "") or ""
        if role in ("developer", "superadmin"):
            logger.debug("Permission granted: %s role user", role)
            return True

        # Note: Hardcoded identity bypass was removed. Use the role field
        # (developer / superadmin) exclusively for elevated access.

        # 3. If view doesn't define a resource_name, assume default DRF permissions
        resource_name = getattr(view, "resource_name", None)
        if not resource_name:
            logger.debug("Permission granted: No resource_name defined for view")
            return True

        # 4. Map HTTP methods to actions
        method_map = {"GET": "read", "OPTIONS": "read", "HEAD": "read", "POST": "create", "PUT": "update", "PATCH": "update", "DELETE": "delete"}

        required_action = method_map.get(request.method)
        if not required_action:
            logger.warning("Permission denied: Unknown HTTP method %s", request.method)
            return False

        # 4a. Regulations are always readable by ALL authenticated users.
        # They are displayed on the OT Form page for every user.
        # Only admin/CRUD operations should respect menu_permissions.
        if resource_name == "regulations" and required_action == "read":
            logger.debug("Permission granted: regulations read access is universal")
            return True

        # Debug logging for permission checks
        is_ptb_admin = getattr(request.user, "is_ptb_admin", False)
        menu_perms = getattr(request.user, "menu_permissions", None)
        username = getattr(request.user, "username", "")
        worker_id = getattr(request.user, "worker_id", "")
        logger.debug("Permission check: user=%s, worker_id=%s, is_ptb_admin=%s, resource=%s, action=%s, method=%s, menu_perms_type=%s", username, worker_id, is_ptb_admin, resource_name, required_action, request.method, type(menu_perms).__name__)

        keys_to_check = self.KEY_ALIASES.get(resource_name, [resource_name])

        # CHECK 1: Explicit Permissions (Override defaults if present)
        # Only use explicit permissions if the user has a dictionary set for this specific resource.
        # If the user has a global permissions object but NO entry for this resource,
        # fall back to the default role-based logic below.
        if isinstance(menu_perms, dict):
            for key in keys_to_check:
                if key in menu_perms:
                    allowed_actions = menu_perms.get(key, [])
                    result = required_action in allowed_actions
                    logger.debug("Explicit permission check for key '%s': %s (allowed: %s)", key, result, allowed_actions)
                    return result

        # CHECK 2: PTB Admin Role (Default: Full Access to everything except Superadmin)
        # Note: Superadmin check is already done at step 2.
        if is_ptb_admin:
            # PTB Admin has full CRUD on all resources by default
            logger.debug("Permission granted: PTB Admin has full access to %s", resource_name)
            return True

        # CHECK 3: Legacy List Permissions
        # If user has a non-empty list, we treat it as an explicit whitelist.
        # Empty list falls through to defaults.
        if isinstance(menu_perms, list) and len(menu_perms) > 0:
            for key in keys_to_check:
                if key in menu_perms:
                    logger.debug("Legacy list permission granted for key '%s'", key)
                    return True
            logger.debug("Legacy list permission denied: none of %s in whitelist %s", keys_to_check, menu_perms)
            return False  # Strict whitelist behavior for legacy lists

        # CHECK 4: Regular User Defaults
        # If no explicit permission set for this resource, apply default policy
        logger.debug("Applying default permission rules for resource: %s", resource_name)

        # a) OT Form: Create, Read, Update, Delete
        if resource_name == "overtime_form":
            logger.debug("Default: overtime_form allows all actions")
            return True  # All actions allowed

        # b) OT History: Read Only
        elif resource_name == "overtime_history":
            result = required_action == "read"
            logger.debug("Default: overtime_history read-only: %s", result)
            return result

        # c) Projects: Read Only
        elif resource_name == "projects":
            result = required_action == "read"
            logger.debug("Default: projects read-only: %s", result)
            return result

        # d) Departments: Read Only
        elif resource_name == "departments":
            result = required_action == "read"
            logger.debug("Default: departments read-only: %s", result)
            return result

        # e) Calendar: Create, Read, Update, Delete
        elif resource_name == "calendar":
            logger.debug("Default: calendar allows all actions")
            return True  # All actions allowed

        # f) Employees: Read Only for regular users (needed for OT Form dropdown)
        elif resource_name == "employees":
            result = required_action == "read"
            logger.debug("Default: employees read-only: %s", result)
            return result

        # g) Kanban/Task Board: Create, Read, Update, Delete (assigned tasks only - enforced in queryset)
        elif resource_name == "kanban" or resource_name == "calendar_events":
            logger.debug("Default: %s allows all actions", resource_name)
            return True  # All actions allowed

        # h) Purchasing: Create, Read, Update, Delete
        elif resource_name == "purchasing":
            logger.debug("Default: purchasing allows all actions")
            return True

        # i) Assets: Create, Read, Update, Delete
        elif resource_name == "assets":
            logger.debug("Default: assets allows all actions")
            return True

        # j) Regulations: Read Only for everyone (needed for OT Form page)
        elif resource_name == "regulations":
            result = required_action == "read"
            logger.debug("Default: regulations read-only: %s", result)
            return result

        # Default Deny for unknown resources or admin-only resources
        else:
            logger.warning("Permission denied: Unknown resource '%s' - default deny", resource_name)
            return False
