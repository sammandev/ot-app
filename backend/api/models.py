import base64
import calendar
import logging
from datetime import date, datetime, timedelta

from cryptography.fernet import Fernet
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from .utils.excel_generator import ExcelGenerator

logger = logging.getLogger(__name__)


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ExternalUser(models.Model):
    """
    Stores user info from external authentication API
    Links to internal Employee model for overtime tracking
    """

    class Role(models.TextChoices):
        DEVELOPER = "developer", "Developer"
        SUPERADMIN = "superadmin", "Super Admin"
        USER = "user", "User"

    # External API fields
    external_id = models.IntegerField(unique=True, db_index=True)
    username = models.CharField(max_length=150, unique=True, db_index=True)
    email = models.EmailField(max_length=254)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    # Worker info from external API
    worker_id = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    is_ptb_admin = models.BooleanField(default=False)

    # Status fields
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER, help_text="User role: developer, superadmin, or user")

    # Timestamps
    date_joined = models.DateTimeField()
    last_login = models.DateTimeField(null=True, blank=True)

    # Cache fields
    permissions_cache = models.JSONField(default=dict, blank=True)
    groups_cache = models.JSONField(default=list, blank=True)
    models_perm_cache = models.JSONField(default=dict, blank=True)

    # Menu Access Control
    menu_permissions = models.JSONField(default=list, blank=True, help_text="List of allowed menu keys")

    # User preferences
    event_reminders_enabled = models.BooleanField(default=True, help_text="Whether event reminders are shown to this user")
    preferred_language = models.CharField(max_length=5, default="en", help_text="User's preferred UI language (en, zh, id)")

    # Force logout tracking - when permissions change or user deactivated, this gets updated
    # Frontend checks this against stored value and forces logout if changed
    permission_updated_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp of last permission change, used to force logout")

    cache_updated_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "external_users"
        ordering = ["-created_at"]
        indexes = [
            # Note: external_id and username have unique=True which auto-creates indexes.
            # worker_id has db_index=True. Only add non-duplicate indexes here.
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.username} ({self.worker_id})"

    @property
    def is_authenticated(self):
        """Always return True for active users (compatibility with Django's User model)"""
        return self.is_active

    @property
    def is_anonymous(self):
        """Always return False (compatibility with Django's User model)"""
        return False

    @property
    def name(self):
        """Return username (external API has no reliable first_name/last_name)."""
        return self.username

    def has_permission(self, permission_name):
        """Check if user has specific permission"""
        if self.is_superuser:
            return True
        return permission_name in self.permissions_cache.get("perm_all", [])

    def has_model_permission(self, model_name, action="View"):
        """Check model-level permissions"""
        if self.is_superuser:
            return True
        model_perms = self.models_perm_cache.get(model_name, {})
        return model_perms.get(action, False)

    def update_from_external_api(self, api_data):
        """Update user data from external API response"""
        self.external_id = api_data.get("id", self.external_id)
        self.username = api_data.get("username", self.username)
        self.email = api_data.get("email", self.email)
        self.first_name = api_data.get("first_name", "")
        self.last_name = api_data.get("last_name", "")
        self.is_active = api_data.get("is_active", True)
        self.is_superuser = api_data.get("is_superuser", False)
        self.is_staff = api_data.get("is_staff", False)

        # Worker info
        employee_info = api_data.get("employee_info", {})
        self.worker_id = employee_info.get("worker_id", "")
        self.is_ptb_admin = employee_info.get("is_ptb_admin", False)

        # Note: Developer/superadmin role assignment is now handled exclusively
        # via the role field set by admin or the external API. The previous
        # hardcoded identity check has been removed for security.

        # Permissions
        self.permissions_cache = {
            "perm_all": api_data.get("perm_all", []),
            "permissions": api_data.get("permissions", []),
            "user_permissions": api_data.get("user_permissions", []),
        }
        self.groups_cache = api_data.get("groups_name", [])
        self.models_perm_cache = api_data.get("models_perm", {})
        self.cache_updated_at = timezone.now()

        # Dates - parse from ISO format strings to datetime objects
        if api_data.get("date_joined"):
            date_joined_value = api_data["date_joined"]
            if isinstance(date_joined_value, str):
                self.date_joined = parse_datetime(date_joined_value)
            else:
                self.date_joined = date_joined_value

        if api_data.get("last_login"):
            last_login_value = api_data["last_login"]
            if isinstance(last_login_value, str):
                self.last_login = parse_datetime(last_login_value)
            else:
                self.last_login = last_login_value

        self.save(
            update_fields=[
                "external_id",
                "username",
                "email",
                "first_name",
                "last_name",
                "is_active",
                "is_superuser",
                "is_staff",
                "worker_id",
                "is_ptb_admin",
                "role",
                "permissions_cache",
                "groups_cache",
                "models_perm_cache",
                "cache_updated_at",
                "date_joined",
                "last_login",
                "updated_at",
            ]
        )


class UserSession(models.Model):
    """
    Track active user sessions with external API tokens
    One session per user login
    """

    user = models.ForeignKey(ExternalUser, on_delete=models.CASCADE, related_name="sessions")

    # Token fields
    access_token = models.TextField(unique=True, db_index=True)
    refresh_token = models.TextField(blank=True, null=True)

    # Token metadata
    token_expires_at = models.DateTimeField(db_index=True)
    token_issued_at = models.DateTimeField()

    # Session tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    last_activity = models.DateTimeField(auto_now=True, db_index=True)

    # Status
    is_active = models.BooleanField(default=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_sessions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["token_expires_at"]),
            models.Index(fields=["last_activity"]),
        ]

    def __str__(self):
        return f"Session for {self.user.username} - {self.created_at}"

    def is_token_expired(self):
        """Check if access token is expired"""
        return timezone.now() >= self.token_expires_at

    def deactivate(self):
        """Deactivate this session"""
        self.is_active = False
        self.save(update_fields=["is_active"])


class Department(TimestampedModel):
    """Department info for overtime forms"""

    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    is_enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Project(TimestampedModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    is_enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name


class Employee(TimestampedModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    emp_id = models.CharField(max_length=20, db_index=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="employees", null=True, blank=True)
    is_enabled = models.BooleanField(default=True)
    exclude_from_reports = models.BooleanField(default=False)

    class Meta:
        ordering = ["emp_id"]
        indexes = [
            models.Index(fields=["emp_id"]),
            models.Index(fields=["department"]),
        ]

    def __str__(self):
        return self.name


class CalendarEvent(TimestampedModel):
    EVENT_TYPES = (
        ("holiday", "Holiday"),
        ("leave", "Leave"),
        ("meeting", "Meeting"),
        ("task", "Task"),
    )

    STATUS_CHOICES = (
        ("todo", "To Do"),
        ("in_progress", "In Progress"),
        ("done", "Done"),
    )

    REPEAT_FREQUENCY_CHOICES = (
        ("hourly", "Every Hour"),
        ("daily", "Every Day"),
        ("weekly", "Every Week"),
        ("monthly", "Every Month"),
        ("yearly", "Every Year"),
    )

    title = models.CharField(max_length=100)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default="task", db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="todo")
    description = models.TextField(null=True, blank=True)
    start = models.DateTimeField(default=timezone.now)
    end = models.DateTimeField(default=timezone.now)
    all_day = models.BooleanField(default=False)
    location = models.CharField(max_length=200, blank=True)
    color = models.CharField(max_length=7, blank=True, help_text="Hex color code (e.g., #FF5733)")

    # Repeating event fields
    is_repeating = models.BooleanField(default=False, help_text="Whether this is a repeating event")
    repeat_frequency = models.CharField(max_length=20, choices=REPEAT_FREQUENCY_CHOICES, null=True, blank=True, help_text="How often the event repeats")
    parent_event = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="child_events", help_text="Parent event for recurring instances")

    # Common fields
    created_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="created_events", null=True, blank=True)
    assigned_to = models.ManyToManyField(
        Employee,
        related_name="assigned_events",
        blank=True,
    )

    # Meeting specific fields
    meeting_url = models.URLField(max_length=1000, null=True, blank=True)

    # Task specific fields
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)

    # Task priority and labels
    PRIORITY_CHOICES = (
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("urgent", "Urgent"),
    )
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")
    labels = models.JSONField(default=list, blank=True, help_text="List of label strings for the task")

    # Task group
    group = models.ForeignKey("TaskGroup", on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")

    # Time tracking fields
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Estimated hours to complete the task")
    actual_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text="Total actual hours logged for this task")

    # Leave specific fields
    LEAVE_TYPES = (
        ("personal", "Personal"),
        ("legal", "Legal"),
        ("official", "Official"),
    )
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES, null=True, blank=True)
    applied_by = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="leave_applications",
        null=True,
        blank=True,
    )
    agent = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="agent_for_leaves",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.event_type}: {self.title}"

    def save(self, *args, **kwargs):
        # Fields have default=timezone.now, so this override is only needed
        # if start/end are explicitly set to None after initial creation.
        super().save(*args, **kwargs)


class Holiday(TimestampedModel):
    """
    Holiday model for marking holiday dates on the calendar.
    Separate from CalendarEvent to simplify the calendar UI.
    """

    title = models.CharField(max_length=200, help_text="Holiday name/title")
    date = models.DateField(help_text="Date of the holiday")
    color = models.CharField(
        max_length=7,
        default="#FFC0CB",  # Default soft pink
        help_text="Background color for the holiday (hex code)",
    )
    description = models.TextField(blank=True, null=True)
    is_recurring = models.BooleanField(default=False, help_text="Whether this holiday repeats every year")
    created_by = models.ForeignKey("ExternalUser", on_delete=models.SET_NULL, null=True, blank=True, related_name="created_holidays")

    class Meta:
        ordering = ["date"]
        unique_together = [["title", "date"]]
        indexes = [
            models.Index(fields=["date"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.date}"


class EmployeeLeave(TimestampedModel):
    """
    Employee Leave model for tracking when employees take time off.
    Includes agent assignments for coverage.
    """

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="leaves")
    date = models.DateField(help_text="Date of the leave")
    notes = models.TextField(blank=True, null=True, help_text="Optional notes about the leave")

    # Agents - employees who will cover during leave
    agents = models.ManyToManyField(Employee, blank=True, related_name="covering_leaves", help_text="Employees assigned to cover during leave")
    # Agent names for employees not in the system (free text)
    agent_names = models.TextField(blank=True, null=True, help_text="Comma-separated names of agents not in the employee list")

    created_by = models.ForeignKey("ExternalUser", on_delete=models.SET_NULL, null=True, blank=True, related_name="created_employee_leaves")

    class Meta:
        ordering = ["date", "employee__name"]
        unique_together = [["employee", "date"]]  # Prevent duplicate leaves
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["employee", "date"]),
        ]

    def __str__(self):
        return f"{self.employee.name} - {self.date}"


class OvertimeRequest(TimestampedModel):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    id = models.AutoField(primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    employee_name = models.CharField(max_length=100, blank=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True)
    department_code = models.CharField(max_length=50, blank=True, db_index=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    project_name = models.CharField(max_length=50, blank=True)
    request_date = models.DateField()
    time_start = models.TimeField()
    time_end = models.TimeField()
    total_hours = models.DecimalField(max_digits=4, decimal_places=2)
    has_break = models.BooleanField(default=False)
    break_start = models.TimeField(null=True, blank=True)
    break_end = models.TimeField(null=True, blank=True)
    break_hours = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    reason = models.TextField()
    detail = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_weekend = models.BooleanField(default=False)
    is_holiday = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True)
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_overtime_requests")
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    # Store the username (not user ID) of whoever approved/rejected, since external auth IDs can change
    status_changed_by = models.CharField(max_length=150, blank=True, help_text="Username of the user who last changed the status")
    rejected_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["request_date", "department"]),
            models.Index(fields=["department_code"]),
        ]

    def __str__(self):
        return f"{self.employee.name} - {self.request_date}"

    @classmethod
    def export_daily_data(cls, date):
        """Export daily overtime data for Excel generation (no JSON file).
        Rejected requests are excluded from all reports."""
        try:
            # No need for select_for_update — this is a read-only export
            daily_requests = list(cls.objects.filter(request_date=date).exclude(status="rejected").exclude(employee__exclude_from_reports=True).select_related("employee", "project").prefetch_related("breaks").order_by("time_start"))

            # If no data exists, return None
            if not daily_requests:
                return None

            # Process data outside transaction
            export_data = [
                {
                    "employee_id": request.employee.emp_id,
                    "employee_name": request.employee.name,
                    "project": request.project.name,
                    "time_start": request.time_start.strftime("%H:%M"),
                    "time_end": request.time_end.strftime("%H:%M"),
                    "total_hours": str(request.total_hours),
                    "has_break": request.has_break,
                    "breaks": [
                        {
                            "start_time": break_obj.start_time.strftime("%H:%M"),
                            "end_time": break_obj.end_time.strftime("%H:%M"),
                            "duration_hours": str(break_obj.duration_hours),
                        }
                        for break_obj in request.breaks.all()
                    ],
                    "break_start": (request.break_start.strftime("%H:%M") if request.break_start else None),
                    "break_end": (request.break_end.strftime("%H:%M") if request.break_end else None),
                    "break_hours": (str(request.break_hours) if request.break_hours else None),
                    "reason": request.reason,
                    "detail": request.detail,
                    "is_weekend": request.is_weekend,
                    "is_holiday": request.is_holiday,
                    "created_at": timezone.localtime(request.created_at).strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": timezone.localtime(request.updated_at).strftime("%Y-%m-%d %H:%M:%S"),
                }
                for request in daily_requests
            ]

            return export_data
        except Exception as e:
            logger.error(f"Error exporting daily data: {str(e)}")
            raise

    @classmethod
    def export_monthly_data(cls, date):
        """Export monthly overtime data for Excel generation"""
        try:
            # Calculate period dates
            current_period_start = date.replace(day=26)
            if date.day < 26:
                current_period_start = (date.replace(day=1) - timedelta(days=1)).replace(day=26)

            next_period_end = (current_period_start + timedelta(days=32)).replace(day=25)

            logger.debug(f"Exporting monthly data from {current_period_start} to {next_period_end}")

            # Get all requests in the period (rejected requests are excluded from reports)
            monthly_requests = (
                cls.objects.filter(
                    request_date__gte=current_period_start,
                    request_date__lte=next_period_end,
                )
                .exclude(status="rejected")
                .exclude(employee__exclude_from_reports=True)
                .select_related("employee", "project")
                .prefetch_related("breaks")
                .order_by("request_date", "time_start")
            )

            if not monthly_requests.exists():
                logger.debug(f"No monthly data found for period {current_period_start} to {next_period_end}")
                return None

            # Process monthly data
            monthly_data = [
                {
                    "employee_id": request.employee.emp_id,
                    "employee_name": request.employee.name,
                    "project": request.project.name,
                    "request_date": request.request_date.strftime("%Y-%m-%d"),
                    "time_start": request.time_start.strftime("%H:%M"),
                    "time_end": request.time_end.strftime("%H:%M"),
                    "total_hours": str(request.total_hours),
                    "has_break": request.has_break,
                    "breaks": [
                        {
                            "start_time": break_obj.start_time.strftime("%H:%M"),
                            "end_time": break_obj.end_time.strftime("%H:%M"),
                            "duration_hours": str(break_obj.duration_hours),
                        }
                        for break_obj in request.breaks.all()
                    ],
                    "reason": request.reason,
                    "detail": request.detail,
                    "is_weekend": request.is_weekend,
                    "is_holiday": request.is_holiday,
                }
                for request in monthly_requests
            ]

            return monthly_data
        except Exception as e:
            logger.error(f"Error exporting monthly data: {str(e)}")
            raise

    @classmethod
    def export_daily_data_by_department(cls, date):
        """Export daily overtime data grouped by department for multi-sheet Excel generation.

        Returns a mapping keyed by department code with dept metadata and row data list.
        """
        data = cls.export_daily_data(date)
        if not data:
            return {}

        # Build employee→department lookup in a single query instead of N+1
        emp_ids = [record["employee_id"] for record in data]
        dept_info = {}
        if emp_ids:
            qs = cls.objects.filter(request_date=date, employee__emp_id__in=emp_ids).exclude(status="rejected").select_related("department").only("employee__emp_id", "department__code", "department__name")
            for req in qs:
                if req.employee.emp_id not in dept_info and req.department:
                    dept_info[req.employee.emp_id] = (req.department.code, req.department.name)

        # Group by department
        grouped = {}
        for record in data:
            emp_id = record["employee_id"]
            if emp_id in dept_info:
                dept_key, dept_name = dept_info[emp_id]
            else:
                dept_key = ExcelGenerator.DEFAULT_DEPT_CODE
                dept_name = ExcelGenerator.DEFAULT_DEPT_NAME

            if dept_key not in grouped:
                grouped[dept_key] = {"dept_code": dept_key, "dept_name": dept_name, "data": []}

            grouped[dept_key]["data"].append(record)

        return grouped

    @classmethod
    def export_monthly_data_by_department(cls, date):
        """Export monthly overtime data grouped by department for multi-sheet Excel generation.

        Returns a mapping keyed by department code with dept metadata and row data list.
        """
        data = cls.export_monthly_data(date)
        if not data:
            return {}

        # Calculate period dates for queries
        current_period_start = date.replace(day=26)
        if date.day < 26:
            current_period_start = (date.replace(day=1) - timedelta(days=1)).replace(day=26)
        next_period_end = (current_period_start + timedelta(days=32)).replace(day=25)

        # Build employee→department lookup in a single query instead of N+1
        emp_ids = [record["employee_id"] for record in data]
        dept_info = {}
        if emp_ids:
            qs = (
                cls.objects.filter(
                    request_date__range=[current_period_start, next_period_end],
                    employee__emp_id__in=emp_ids,
                )
                .exclude(status="rejected")
                .select_related("department")
                .only("employee__emp_id", "request_date", "department__code", "department__name")
            )
            for req in qs:
                key = (req.employee.emp_id, req.request_date.strftime("%Y-%m-%d"))
                if key not in dept_info and req.department:
                    dept_info[key] = (req.department.code, req.department.name)

        # Group by department
        grouped = {}
        for record in data:
            emp_id = record["employee_id"]
            req_date = record["request_date"]
            lookup_key = (emp_id, req_date)

            if lookup_key in dept_info:
                dept_key, dept_name = dept_info[lookup_key]
            else:
                dept_key = ExcelGenerator.DEFAULT_DEPT_CODE
                dept_name = ExcelGenerator.DEFAULT_DEPT_NAME

            if dept_key not in grouped:
                grouped[dept_key] = {"dept_code": dept_key, "dept_name": dept_name, "data": []}

            grouped[dept_key]["data"].append(record)

        return grouped

    @classmethod
    def _delete_files(cls, date):
        """Delete Excel files for the date (no JSON files)"""
        try:
            # Get period folder path using ExcelGenerator
            period_path = ExcelGenerator.get_period_folder(date)
            date_str = date.strftime("%Y%m%d")

            # Delete Excel files from period folder
            excel_file = f"{period_path}/{date_str}OT.xlsx"
            summary_file = f"{period_path}/{date_str}OTSummary.xlsx"

            files_to_delete = [excel_file, summary_file]
            ExcelGenerator.delete_files_batch(files_to_delete)

            logger.info(f"Excel files deleted for date {date}")
        except Exception as e:
            logger.error(f"Error deleting files: {str(e)}")

    def delete(self, *args, **kwargs):
        date = self.request_date
        result = super().delete(*args, **kwargs)

        # Offload Excel regeneration to Celery async task
        try:
            from api.tasks import regenerate_excel_after_delete

            regenerate_excel_after_delete.delay(date.isoformat())
            logger.info(f"Queued async Excel regeneration after OT deletion for date {date}")
        except Exception as e:
            logger.warning(f"Failed to queue async Excel regeneration after delete for {date}: {e}. Falling back to synchronous regeneration.")
            # Synchronous fallback when Celery is unavailable
            try:
                from api.utils.excel_generator import ExcelGenerator

                daily_requests = OvertimeRequest.objects.filter(request_date=date).exclude(status="rejected")
                if daily_requests.exists():
                    export_data_grouped = OvertimeRequest.export_daily_data_by_department(date)
                    monthly_data_grouped = OvertimeRequest.export_monthly_data_by_department(date)
                    ExcelGenerator.generate_all_excel_files(
                        export_data_grouped,
                        monthly_data_grouped,
                        date,
                        upload=True,
                        temp_only=ExcelGenerator.EXCEL_TEMP_ONLY,
                    )
                    logger.info(f"Synchronous Excel regeneration completed after deletion for {date}")
            except Exception as sync_err:
                logger.error(f"Synchronous Excel regeneration failed after delete for {date}: {sync_err}", exc_info=True)

        return result

    def save(self, *args, **kwargs):
        logger.debug(f"Saving OvertimeRequest for date: {self.request_date}")

        if self.request_date:
            self.is_weekend = (
                calendar.weekday(
                    self.request_date.year,
                    self.request_date.month,
                    self.request_date.day,
                )
                >= 5
            )  # 5=Saturday, 6=Sunday
            logger.debug(f"Calculated is_weekend: {self.is_weekend}")

        # Capture employee info - only populate denormalized fields
        # Don't modify employee_id as it's set by the serializer/form
        try:
            if self.employee_id:
                # Use select_related to avoid N+1 queries when FK isn't prefetched
                if not self.employee_name or not self.department_code:
                    try:
                        emp = Employee.objects.select_related("department").get(pk=self.employee_id)
                        if not self.employee_name:
                            self.employee_name = emp.name
                        if emp.department:
                            self.department = emp.department
                            if not self.department_code:
                                self.department_code = emp.department.code
                    except Employee.DoesNotExist:
                        pass
        except (ValueError, TypeError, Employee.DoesNotExist, Department.DoesNotExist, AttributeError) as e:
            # Log the error but don't crash - the denormalized fields are optional
            logger.warning(f"Could not populate denormalized fields from employee FK: {e}")
            # Keep any existing values, don't overwrite with empty
            if not self.department_code:
                self.department_code = ""

        super().save(*args, **kwargs)

        # Excel generation + SMB upload is now handled by the
        # post_save signal in signals.py (invalidate_overtime_cache).

    @property
    def total_break_hours(self):
        """Get the sum of all break durations. Uses prefetched cache when available."""
        # Use prefetched cache if available (avoids N+1)
        try:
            cached_breaks = self.breaks.all()
            # .all() returns prefetched results if prefetch_related was used
            breaks_list = list(cached_breaks)
            if breaks_list:
                return sum(b.duration_hours for b in breaks_list)
            return self.break_hours or 0
        except Exception:
            return self.break_hours or 0


class OvertimeBreak(TimestampedModel):
    overtime_request = models.ForeignKey(OvertimeRequest, on_delete=models.CASCADE, related_name="breaks")
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_hours = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return f"Break for {self.overtime_request}: {self.start_time} - {self.end_time}"

    @property
    def duration_minutes(self):
        """Return duration in minutes for frontend compatibility"""
        return int(float(self.duration_hours) * 60) if self.duration_hours else 0

    def save(self, *args, **kwargs):
        # Calculate duration if not provided
        if not self.duration_hours and self.start_time and self.end_time:
            # Convert time objects to datetime for calculation
            start_dt = datetime.combine(date.today(), self.start_time)
            end_dt = datetime.combine(date.today(), self.end_time)

            # Handle case where break ends after midnight
            if end_dt < start_dt:
                end_dt += timedelta(days=1)

            # Calculate duration in hours
            duration = (end_dt - start_dt).total_seconds() / 3600
            self.duration_hours = round(duration, 2)

        super().save(*args, **kwargs)


class OvertimeRegulation(TimestampedModel):
    """Overtime regulations and rules for admin management (text-based)"""

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, default="general", db_index=True)
    order = models.IntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        indexes = [
            models.Index(fields=["category", "order"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.title


class OvertimeLimitConfig(TimestampedModel):
    """
    Singleton-like configuration for overtime hour limits.
    Only one active config should exist at a time.
    """

    max_weekly_hours = models.DecimalField(max_digits=5, decimal_places=2, default=18, help_text="Maximum overtime hours per week (Mon-Sun)")
    max_monthly_hours = models.DecimalField(max_digits=5, decimal_places=2, default=72, help_text="Maximum overtime hours per month (26th-25th cycle)")
    recommended_weekly_hours = models.DecimalField(max_digits=5, decimal_places=2, default=15, help_text="TPE weekly overtime warning threshold")
    recommended_monthly_hours = models.DecimalField(max_digits=5, decimal_places=2, default=60, help_text="TPE monthly overtime warning threshold")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Overtime Limit Configuration"
        verbose_name_plural = "Overtime Limit Configurations"

    def __str__(self):
        return f"OT Limits: {self.max_weekly_hours}h/week, {self.max_monthly_hours}h/month"

    @classmethod
    def get_active(cls):
        """Return the active configuration, or create default if none exists."""
        config = cls.objects.filter(is_active=True).first()
        if not config:
            config = cls.objects.create()
        return config


class OvertimeRegulationDocument(TimestampedModel):
    """
    PDF document storage for overtime regulations.
    Supports upload, versioning, soft delete, and audit trail.
    Use this for uploadable regulation PDF files.
    """

    from django.core.validators import FileExtensionValidator

    # Basic info
    title = models.CharField(max_length=255, help_text="Document title")
    description = models.TextField(blank=True, help_text="Document description or notes")

    # File storage
    file = models.FileField(upload_to="regulations/%Y/%m/", validators=[FileExtensionValidator(["pdf"])], help_text="PDF file only")
    file_size = models.IntegerField(help_text="File size in bytes")
    file_hash = models.CharField(max_length=64, blank=True, help_text="SHA256 hash for duplicate detection")

    # Versioning
    version = models.IntegerField(default=1, help_text="Version number")
    replaces = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="replaced_by_documents", help_text="Previous version this replaces")

    # Status tracking
    is_active = models.BooleanField(default=True, db_index=True, help_text="Is current/active version")
    is_deleted = models.BooleanField(default=False, db_index=True, help_text="Soft delete flag")
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey("ExternalUser", on_delete=models.SET_NULL, null=True, blank=True, related_name="deleted_regulation_documents")

    # Upload tracking
    uploaded_by = models.ForeignKey("ExternalUser", on_delete=models.CASCADE, related_name="uploaded_regulation_documents")

    # Optional: SMB backup tracking
    smb_path = models.CharField(max_length=500, blank=True, help_text="Path on SMB share if backed up")
    smb_uploaded = models.BooleanField(default=False)

    class Meta:
        db_table = "overtime_regulation_documents"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active", "is_deleted"]),
            models.Index(fields=["file_hash"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["uploaded_by"]),
        ]
        verbose_name = "Overtime Regulation Document"
        verbose_name_plural = "Overtime Regulation Documents"

    def __str__(self):
        return f"{self.title} (v{self.version})"

    def delete(self, using=None, keep_parents=False):
        """Override delete to implement soft delete"""
        self.is_deleted = True
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        """Permanently delete file and database record"""
        if self.file:
            self.file.delete(save=False)
        super().delete()

    def calculate_file_hash(self):
        """Calculate SHA256 hash of the file"""
        import hashlib

        if self.file:
            hash_sha256 = hashlib.sha256()
            for chunk in self.file.chunks():
                hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        return ""

    def save(self, *args, **kwargs):
        """Auto-calculate file size and hash on save"""
        if self.file and not self.file_size:
            self.file_size = self.file.size
        if self.file and not self.file_hash:
            self.file_hash = self.calculate_file_hash()
        super().save(*args, **kwargs)


class Notification(TimestampedModel):
    recipient = models.ForeignKey(ExternalUser, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255)
    message = models.TextField()
    event = models.ForeignKey(CalendarEvent, on_delete=models.SET_NULL, null=True, blank=True, related_name="notifications")
    is_read = models.BooleanField(default=False, db_index=True)
    # Event type for filtering and categorization
    event_type = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    # For archiving old notifications
    is_archived = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["recipient", "-created_at"]),
            models.Index(fields=["recipient", "is_read", "-created_at"]),
            models.Index(fields=["recipient", "is_archived"]),
            models.Index(fields=["recipient", "is_archived", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.recipient.username}: {self.title}"

    @classmethod
    def get_unread_count(cls, user):
        """Get unread notification count for a user (direct DB query)"""
        return cls.objects.filter(recipient=user, is_read=False, is_archived=False).count()

    @classmethod
    def archive_old_notifications(cls, days=90):
        """Archive notifications older than specified days"""
        from datetime import timedelta

        from django.utils import timezone

        cutoff_date = timezone.now() - timedelta(days=days)
        updated = cls.objects.filter(created_at__lt=cutoff_date, is_archived=False).update(is_archived=True)
        return updated


class SystemConfiguration(TimestampedModel):
    """
    Store global system settings.
    Singleton model - ensures only one record exists.
    """

    app_name = models.CharField(max_length=100, default="Overtime Management System")
    app_acronym = models.CharField(max_length=20, default="OMS")
    version = models.CharField(max_length=20, default="1.0.0")
    build_date = models.CharField(max_length=50, default="January 2026")

    # Event Reminder Controls (managed by superadmin)
    event_reminders_disabled_globally = models.BooleanField(default=False, help_text="Disable event reminders for all users")
    event_reminders_disabled_roles = models.JSONField(default=list, blank=True, help_text="Roles with reminders disabled, e.g. ['regular', 'staff']")
    event_reminders_disabled_users = models.JSONField(default=list, blank=True, help_text="User IDs with reminders disabled")

    # App tab icon (favicon) — supports .ico, .svg, .png
    tab_icon = models.FileField(upload_to="system/", blank=True, null=True, help_text="Custom browser tab icon (.ico, .svg, .png)")

    def save(self, *args, **kwargs):
        self.pk = 1  # Force singleton
        super().save(*args, **kwargs)

    def __str__(self):
        return "System Configuration"

    class Meta:
        verbose_name = "System Configuration"
        verbose_name_plural = "System Configuration"


class UserActivityLog(models.Model):
    """
    Track user login times and actions for super admin monitoring
    """

    ACTION_CHOICES = [
        ("login", "Login"),
        ("logout", "Logout"),
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("view", "View"),
        ("export", "Export"),
        ("page_view", "Page View"),
        ("import", "Import"),
    ]

    user = models.ForeignKey(ExternalUser, on_delete=models.CASCADE, related_name="activity_logs", help_text="User who performed the action")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, db_index=True, help_text="Type of action performed")
    resource = models.CharField(max_length=100, blank=True, null=True, help_text="Resource affected (e.g., 'overtime_request', 'employee')")
    resource_id = models.IntegerField(blank=True, null=True, help_text="ID of the affected resource")
    details = models.JSONField(default=dict, blank=True, help_text="Additional action details")
    ip_address = models.GenericIPAddressField(blank=True, null=True, help_text="User's IP address")
    user_agent = models.TextField(blank=True, help_text="Browser user agent")
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True, help_text="When the action occurred")

    class Meta:
        db_table = "user_activity_logs"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["-timestamp"]),
            models.Index(fields=["user", "-timestamp"]),
            models.Index(fields=["action", "-timestamp"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"

    @classmethod
    def log_activity(cls, user, action, resource=None, resource_id=None, details=None, request=None):
        """
        Helper method to create activity log entries
        """
        log_data = {
            "user": user,
            "action": action,
            "resource": resource,
            "resource_id": resource_id,
            "details": details or {},
        }

        if request:
            # Extract IP address
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(",")[0]
            else:
                ip_address = request.META.get("REMOTE_ADDR")

            log_data["ip_address"] = ip_address
            log_data["user_agent"] = request.META.get("HTTP_USER_AGENT", "")

        return cls.objects.create(**log_data)


class TaskComment(TimestampedModel):
    """
    Comments on calendar events (tasks) with threading and @mentions support
    """

    task = models.ForeignKey(CalendarEvent, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="task_comments")
    content = models.TextField()

    # Threading support
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies")

    # Mentions - store employee IDs that are mentioned
    mentions = models.ManyToManyField(Employee, related_name="mentioned_in_comments", blank=True)

    # Edit tracking
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "task_comments"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["task", "created_at"]),
            models.Index(fields=["author"]),
            models.Index(fields=["parent"]),
        ]

    def __str__(self):
        return f"Comment by {self.author.name} on {self.task.title}"


class TaskSubtask(TimestampedModel):
    """
    Subtasks/checklist items for tasks
    """

    task = models.ForeignKey(CalendarEvent, on_delete=models.CASCADE, related_name="subtasks")
    title = models.CharField(max_length=500)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="completed_subtasks")
    order = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="created_subtasks")

    class Meta:
        db_table = "task_subtasks"
        ordering = ["order", "created_at"]
        indexes = [
            models.Index(fields=["task", "order"]),
            models.Index(fields=["is_completed"]),
        ]

    def __str__(self):
        status = "✓" if self.is_completed else "○"
        return f"{status} {self.title}"

    def toggle_complete(self, employee=None):
        """Toggle completion status"""
        self.is_completed = not self.is_completed
        if self.is_completed:
            self.completed_at = timezone.now()
            self.completed_by = employee
        else:
            self.completed_at = None
            self.completed_by = None
        self.save()
        return self.is_completed


class TaskTimeLog(TimestampedModel):
    """
    Time log entries for tracking time spent on tasks.
    Supports both manual entry and timer-based tracking.
    """

    task = models.ForeignKey(CalendarEvent, on_delete=models.CASCADE, related_name="time_logs")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="time_logs")
    description = models.TextField(blank=True, help_text="What was worked on")

    # Time tracking
    started_at = models.DateTimeField(help_text="When the work started")
    ended_at = models.DateTimeField(null=True, blank=True, help_text="When the work ended (null if timer still running)")
    duration_minutes = models.PositiveIntegerField(default=0, help_text="Duration in minutes (calculated from start/end or manual entry)")

    # Timer state
    is_running = models.BooleanField(default=False, help_text="Whether this is an active timer")

    class Meta:
        db_table = "task_time_logs"
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["task", "started_at"]),
            models.Index(fields=["employee", "started_at"]),
            models.Index(fields=["is_running"]),
        ]

    def __str__(self):
        return f"{self.employee.name}: {self.duration_minutes}min on {self.task.title}"

    def stop_timer(self):
        """Stop the running timer and calculate duration"""
        if self.is_running and not self.ended_at:
            self.ended_at = timezone.now()
            self.is_running = False
            # Calculate duration in minutes
            delta = self.ended_at - self.started_at
            self.duration_minutes = int(delta.total_seconds() / 60)
            self.save()
            # Update task's actual_hours
            self._update_task_actual_hours()
        return self

    def _update_task_actual_hours(self):
        """Recalculate and update the task's actual_hours from all time logs"""
        from django.db.models import Sum

        total_minutes = self.task.time_logs.aggregate(total=Sum("duration_minutes"))["total"] or 0
        self.task.actual_hours = round(total_minutes / 60, 2)
        self.task.save(update_fields=["actual_hours"])

    def save(self, *args, **kwargs):
        # Calculate duration if both start and end are set
        if self.started_at and self.ended_at and not self.is_running:
            delta = self.ended_at - self.started_at
            self.duration_minutes = int(delta.total_seconds() / 60)
        super().save(*args, **kwargs)
        # Update task actual hours if this is a completed log
        if self.ended_at and not self.is_running:
            self._update_task_actual_hours()


class TaskActivity(TimestampedModel):
    """
    Activity log for tasks - tracks all changes, status updates, etc.
    """

    ACTION_TYPES = (
        ("created", "Created"),
        ("updated", "Updated"),
        ("status_changed", "Status Changed"),
        ("priority_changed", "Priority Changed"),
        ("assigned", "Assigned"),
        ("unassigned", "Unassigned"),
        ("label_added", "Label Added"),
        ("label_removed", "Label Removed"),
        ("comment_added", "Comment Added"),
        ("due_date_changed", "Due Date Changed"),
        ("moved", "Moved to Column"),
    )

    task = models.ForeignKey(CalendarEvent, on_delete=models.CASCADE, related_name="activities")
    actor = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="task_activities")
    action = models.CharField(max_length=30, choices=ACTION_TYPES)

    # Store old and new values for changes
    old_value = models.CharField(max_length=255, blank=True, null=True)
    new_value = models.CharField(max_length=255, blank=True, null=True)

    # Extra data for complex changes (like multiple assignees)
    extra_data = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "task_activities"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["task", "-created_at"]),
            models.Index(fields=["actor"]),
            models.Index(fields=["action"]),
        ]

    def __str__(self):
        return f"{self.actor.name} {self.action} on {self.task.title}"


class BoardPresence(models.Model):
    """
    Track who is currently viewing the Kanban board for presence indicators
    """

    user = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="board_presences")
    # Which task is being edited (null if just viewing board)
    editing_task = models.ForeignKey(CalendarEvent, on_delete=models.CASCADE, null=True, blank=True, related_name="editors")
    last_seen = models.DateTimeField(auto_now=True)

    # WebSocket channel name for sending updates
    channel_name = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "board_presence"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["last_seen"]),
        ]

    def __str__(self):
        return f"{self.user.name} - last seen {self.last_seen}"


class PersonalNote(TimestampedModel):
    """
    Personal notes/quick tasks for individual users.
    Private board for each user's personal notes.
    """

    owner = models.ForeignKey("ExternalUser", on_delete=models.CASCADE, related_name="personal_notes")
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, null=True)
    color = models.CharField(
        max_length=7,
        default="#FFEB3B",  # Default yellow like sticky note
        help_text="Note color (hex code)",
    )
    is_pinned = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    due_date = models.DateTimeField(null=True, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = "personal_notes"
        ordering = ["-is_pinned", "order", "-created_at"]
        indexes = [
            models.Index(fields=["owner", "-created_at"]),
            models.Index(fields=["owner", "is_completed"]),
        ]

    def __str__(self):
        return f"{self.owner.username}'s note: {self.title}"


class TaskGroup(TimestampedModel):
    """
    Groups for organizing tasks on the Kanban board.
    Each group can have a color and members.
    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(
        max_length=7,
        default="#6366F1",  # Default indigo
        help_text="Group color (hex code)",
    )
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Emoji or icon identifier")
    created_by = models.ForeignKey("ExternalUser", on_delete=models.CASCADE, related_name="created_task_groups")
    members = models.ManyToManyField(Employee, related_name="task_groups", blank=True)
    is_private = models.BooleanField(default=False, help_text="If true, only members can see tasks in this group")
    order = models.IntegerField(default=0)

    # Department-based group fields
    is_department_group = models.BooleanField(default=False, help_text="If true, this group was auto-generated from a department")
    department = models.ForeignKey("Department", on_delete=models.CASCADE, null=True, blank=True, related_name="task_group", help_text="The department this group represents (if is_department_group=True)")

    class Meta:
        db_table = "task_groups"
        ordering = ["order", "name"]
        indexes = [
            models.Index(fields=["created_by"]),
            models.Index(fields=["is_department_group"]),
        ]

    def __str__(self):
        return self.name


class TaskAttachment(TimestampedModel):
    """
    File attachments for tasks.
    """

    task = models.ForeignKey(CalendarEvent, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="task_attachments/%Y/%m/")
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField(help_text="File size in bytes")
    file_type = models.CharField(max_length=100, blank=True, help_text="MIME type")
    uploaded_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="uploaded_attachments")
    description = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = "task_attachments"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["task", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.filename} on {self.task.title}"

    def delete(self, *args, **kwargs):
        # Delete the file from storage
        if self.file:
            self.file.delete(save=False)
        super().delete(*args, **kwargs)


class TaskReminder(TimestampedModel):
    """
    Reminders/alerts for tasks.
    Users can set reminders to be notified before task due date.
    """

    REMINDER_TYPES = (
        ("15min", "15 minutes before"),
        ("30min", "30 minutes before"),
        ("1hour", "1 hour before"),
        ("2hours", "2 hours before"),
        ("1day", "1 day before"),
        ("custom", "Custom time"),
    )

    task = models.ForeignKey(CalendarEvent, on_delete=models.CASCADE, related_name="reminders")
    user = models.ForeignKey("ExternalUser", on_delete=models.CASCADE, related_name="task_reminders")
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPES, default="1hour")
    remind_at = models.DateTimeField(help_text="When to show the reminder")
    message = models.CharField(max_length=500, blank=True, null=True)
    is_triggered = models.BooleanField(default=False, help_text="Whether reminder has been shown")
    is_dismissed = models.BooleanField(default=False, help_text="User dismissed the reminder")

    class Meta:
        db_table = "task_reminders"
        ordering = ["remind_at"]
        indexes = [
            models.Index(fields=["user", "is_triggered", "remind_at"]),
            models.Index(fields=["task", "user"]),
        ]

    def __str__(self):
        return f"Reminder for {self.user.username} on {self.task.title}"


class PurchaseRequest(TimestampedModel):
    """
    Purchase Request model for managing purchasing requests.
    """

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("done", "Done"),
        ("canceled", "Canceled"),
    )

    id = models.AutoField(primary_key=True)
    request_date = models.DateField(null=True, blank=True)
    owner = models.CharField(max_length=100, blank=True, null=True, help_text="Can be employee or external person")
    owner_employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="purchase_requests", help_text="Link to employee if owner is from employee list")
    doc_id = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    part_no = models.CharField(max_length=100, blank=True, null=True)
    description_spec = models.TextField(blank=True, null=True)
    material_category = models.CharField(max_length=100, blank=True, null=True)
    purpose_desc = models.TextField(blank=True, null=True)
    qty = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    plant = models.CharField(max_length=50, blank=True, null=True)
    project_code = models.CharField(max_length=50, blank=True, null=True)
    pr_type = models.CharField(max_length=20, blank=True, null=True)
    mrp_id = models.CharField(max_length=20, blank=True, null=True)
    purch_org = models.CharField(max_length=20, blank=True, null=True)
    sourcer_price = models.CharField(max_length=100, blank=True, null=True)
    pr_no = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    remarks = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    class Meta:
        db_table = "purchase_requests"
        ordering = ["-request_date", "-id"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["request_date"]),
        ]

    def __str__(self):
        return f"PR-{self.id}: {self.part_no or self.description_spec or 'N/A'}"


class Asset(TimestampedModel):
    """
    Asset model for managing company assets by department.
    """

    id = models.AutoField(primary_key=True)
    company_code = models.CharField(max_length=20, blank=True, null=True)
    asset_id = models.CharField(max_length=50, unique=True, db_index=True)
    fixed_asset_id = models.CharField(max_length=50, blank=True, null=True)
    is_fixed_asset = models.BooleanField(default=False)
    is_customs_control = models.BooleanField(default=False)
    part_number = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    group_3 = models.CharField(max_length=50, blank=True, null=True)
    product_name = models.CharField(max_length=500, blank=True, null=True)
    spec = models.CharField(max_length=500, blank=True, null=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    receive_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, blank=True, null=True)

    # Cost Center / Department
    cost_center = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    cost_center_name = models.CharField(max_length=200, blank=True, null=True)
    keeper_dept = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    keeper_dept_name = models.CharField(max_length=200, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="assets", help_text="Link to department based on cost_center or keeper_dept")

    # Keeper info
    keeper = models.CharField(max_length=50, blank=True, null=True)
    keeper_name = models.CharField(max_length=200, blank=True, null=True)

    # Grouping
    group_1 = models.CharField(max_length=50, blank=True, null=True)
    group_2 = models.CharField(max_length=50, blank=True, null=True)

    # Storage
    storage = models.CharField(max_length=50, blank=True, null=True)
    location_code = models.CharField(max_length=50, blank=True, null=True)
    storage_desc = models.CharField(max_length=200, blank=True, null=True)

    # Consignment and Vendor
    consign = models.CharField(max_length=10, blank=True, null=True)
    vendor = models.CharField(max_length=50, blank=True, null=True)

    # PR/PO/DN info
    pr_no = models.CharField(max_length=50, blank=True, null=True)
    pr_sequence = models.CharField(max_length=20, blank=True, null=True)
    po_no = models.CharField(max_length=50, blank=True, null=True)
    po_sequence = models.CharField(max_length=20, blank=True, null=True)
    dn_no = models.CharField(max_length=50, blank=True, null=True)
    dn_sequence = models.CharField(max_length=20, blank=True, null=True)
    dn_date = models.DateField(null=True, blank=True)

    # Application info
    application_number = models.CharField(max_length=50, blank=True, null=True)
    sequence = models.CharField(max_length=20, blank=True, null=True)
    import_number = models.CharField(max_length=50, blank=True, null=True)

    # Picking info
    picking_no = models.CharField(max_length=50, blank=True, null=True)
    picking_sequence = models.CharField(max_length=20, blank=True, null=True)
    picking_year = models.CharField(max_length=10, blank=True, null=True)
    picking_date = models.DateField(null=True, blank=True)

    # Product info
    chinese_product_name = models.CharField(max_length=500, blank=True, null=True)
    hs_code = models.CharField(max_length=50, blank=True, null=True)

    # Declaration
    declaration_number = models.CharField(max_length=50, blank=True, null=True)
    declaration_date = models.DateField(null=True, blank=True)
    control_end_date = models.DateField(null=True, blank=True)
    outsource_number = models.CharField(max_length=50, blank=True, null=True)

    # Price info
    price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, blank=True, null=True)
    local_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    price_level = models.CharField(max_length=20, blank=True, null=True)

    # Serial/Qualification
    sn = models.CharField(max_length=100, blank=True, null=True)
    is_qualified = models.BooleanField(default=False)
    itc_end_date = models.DateField(null=True, blank=True)
    elec_declaration_number = models.CharField(max_length=100, blank=True, null=True)
    national_inspection_certification = models.CharField(max_length=200, blank=True, null=True)

    # Notes (10 note fields)
    note1 = models.TextField(blank=True, null=True)
    note2 = models.TextField(blank=True, null=True)
    note3 = models.TextField(blank=True, null=True)
    note4 = models.TextField(blank=True, null=True)
    note5 = models.TextField(blank=True, null=True)
    note6 = models.TextField(blank=True, null=True)
    note7 = models.TextField(blank=True, null=True)
    note8 = models.TextField(blank=True, null=True)
    note9 = models.TextField(blank=True, null=True)
    note10 = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "assets"
        ordering = ["-receive_date", "asset_id"]
        indexes = [
            models.Index(fields=["department"]),
            models.Index(fields=["cost_center"]),
            models.Index(fields=["keeper_dept"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.asset_id}: {self.product_name or 'N/A'}"


# ---------------------------------------------------------------------------
# SMB Configuration — encrypted password storage
# ---------------------------------------------------------------------------


def _get_fernet_key():
    """
    Derive a Fernet-compatible key using HKDF (HMAC-based Key Derivation).

    Improvements over the previous bare SHA-256 approach:
    * Uses HKDF with a separating ``info`` label so the derived key is
      domain-specific and cryptographically independent of other SECRET_KEY uses.
    * Reads an optional ``SMB_ENCRYPTION_KEY`` env var so the encryption key
      can be rotated independently of Django's SECRET_KEY.
    * Falls back to ``SECRET_KEY`` for backward-compatibility.
    """
    import os

    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF

    master_key = os.environ.get("SMB_ENCRYPTION_KEY") or settings.SECRET_KEY
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,  # deterministic; same key => same output
        info=b"ftp-otapp-smb-password-v1",  # domain separation label
    )
    derived = hkdf.derive(master_key.encode())
    return base64.urlsafe_b64encode(derived)


def _get_legacy_fernet_key():
    """Legacy SHA-256-only key for decrypting passwords stored before HKDF migration."""
    import hashlib

    key_bytes = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    return base64.urlsafe_b64encode(key_bytes)


class SMBConfiguration(TimestampedModel):
    """
    Store SMB credentials in the database with encrypted password.
    Multiple configs supported — one marked `is_active` is used for uploads.
    Falls back to env vars (.env.staging) if no active DB record exists.
    """

    name = models.CharField(max_length=100, default="Default", help_text="Label for this configuration")
    server = models.CharField(max_length=255, blank=True, help_text="SMB server hostname or IP")
    share_name = models.CharField(max_length=255, blank=True, help_text="SMB share name")
    username = models.CharField(max_length=255, blank=True, help_text="SMB username")
    _encrypted_password = models.TextField(blank=True, db_column="encrypted_password", help_text="Fernet-encrypted SMB password")
    domain = models.CharField(max_length=100, default="WORKGROUP")
    port = models.IntegerField(default=445)
    path_prefix = models.CharField(max_length=500, blank=True, default="", help_text="Path prefix on the SMB share")
    is_active = models.BooleanField(default=False, help_text="Only one config should be active at a time")

    class Meta:
        db_table = "smb_configuration"
        verbose_name = "SMB Configuration"
        verbose_name_plural = "SMB Configurations"
        ordering = ["-is_active", "-updated_at"]

    def save(self, *args, **kwargs):
        # If marking this as active, deactivate all others
        if self.is_active:
            SMBConfiguration.objects.exclude(pk=self.pk).filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        active = " [ACTIVE]" if self.is_active else ""
        return f"{self.name}: {self.server}/{self.share_name}{active}"

    # --- Password encryption ---
    def set_password(self, raw_password: str):
        """Encrypt and store the password using the current HKDF-derived key."""
        f = Fernet(_get_fernet_key())
        self._encrypted_password = f.encrypt(raw_password.encode()).decode()

    def get_password(self) -> str:
        """
        Decrypt the stored password.

        Tries the current HKDF key first; falls back to the legacy SHA-256 key
        for passwords encrypted before the migration.  On any failure an empty
        string is returned and the error is logged.
        """
        if not self._encrypted_password:
            return ""
        token = self._encrypted_password.encode()
        # 1. Try current HKDF-derived key
        try:
            return Fernet(_get_fernet_key()).decrypt(token).decode()
        except Exception:
            pass
        # 2. Fallback: legacy SHA-256 key (pre-migration passwords)
        try:
            plaintext = Fernet(_get_legacy_fernet_key()).decrypt(token).decode()
            logger.info(
                "SMB config '%s' (id=%s) decrypted with legacy key — re-save to migrate to HKDF key.",
                self.name,
                self.pk,
            )
            return plaintext
        except Exception as e:
            logger.error(
                "SMB password decryption failed for config '%s' (id=%s): %s",
                self.name,
                self.pk,
                type(e).__name__,
            )
            return ""

    @classmethod
    def get_active_config(cls):
        """Return the active SMB config dict, falling back to env vars."""
        import os

        try:
            obj = cls.objects.filter(is_active=True).first()
            if obj and obj.server and obj.username and obj._encrypted_password:
                return {
                    "host": obj.server,
                    "username": obj.username,
                    "password": obj.get_password(),
                    "share_name": obj.share_name,
                    "domain": obj.domain,
                    "port": obj.port,
                    "path": (obj.path_prefix or "").replace("\\", "/"),
                }
        except Exception:
            pass

        # Fallback to env vars
        return {
            "host": os.getenv("SMB_SERVER", ""),
            "username": os.getenv("SMB_USERNAME", ""),
            "password": os.getenv("SMB_PASSWORD", ""),
            "share_name": os.getenv("SMB_SHARE_NAME", ""),
            "domain": os.getenv("SMB_DOMAIN", "WORKGROUP"),
            "port": int(os.getenv("SMB_PORT", "445")),
            "path": os.getenv("SMB_PATH_PREFIX", "").replace("\\", "/"),
        }

    # Keep backward compat alias
    get_config = get_active_config


# ---------------------------------------------------------------------------
# User Reports (Bug reports & Feature requests)
# ---------------------------------------------------------------------------


class UserReport(TimestampedModel):
    """
    Users can submit bug reports or feature requests.
    Super admin can see and manage these in the dashboard.
    """

    TYPE_CHOICES = [
        ("bug", "Bug Report"),
        ("feature", "Feature Request"),
    ]

    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
        ("wont_fix", "Won't Fix"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    reporter = models.ForeignKey(ExternalUser, on_delete=models.CASCADE, related_name="reports")
    report_type = models.CharField(max_length=10, choices=TYPE_CHOICES, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    page_url = models.CharField(max_length=500, blank=True, help_text="Page where the issue was found")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="open", db_index=True)
    admin_notes = models.TextField(blank=True, help_text="Super admin response / notes")
    resolved_in_version = models.CharField(max_length=20, blank=True, help_text="Version where this was resolved")

    class Meta:
        db_table = "user_reports"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["report_type", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["reporter", "-created_at"]),
        ]

    def __str__(self):
        return f"[{self.get_report_type_display()}] {self.title}"


# ---------------------------------------------------------------------------
# Release Notes / Version History
# ---------------------------------------------------------------------------


class ReleaseNote(TimestampedModel):
    """
    Version history entries managed by super admin.
    """

    STATUS_CHOICES = [
        ("stable", "Stable"),
        ("beta", "Beta"),
        ("hotfix", "Hotfix"),
    ]

    version = models.CharField(max_length=20, unique=True)
    release_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="stable")
    summary = models.TextField(blank=True, help_text="Short summary of this release")

    # Categorized changes stored as JSON arrays of strings
    new_features = models.JSONField(default=list, blank=True, help_text="New features list")
    improvements = models.JSONField(default=list, blank=True, help_text="Improvements list")
    bug_fixes = models.JSONField(default=list, blank=True, help_text="Bug fixes list")
    breaking_changes = models.JSONField(default=list, blank=True, help_text="Breaking changes list")
    security = models.JSONField(default=list, blank=True, help_text="Security patches list")

    # Optional metadata
    known_issues = models.JSONField(default=list, blank=True)
    deprecations = models.JSONField(default=list, blank=True)
    contributors = models.JSONField(default=list, blank=True, help_text="List of contributor names")

    published = models.BooleanField(default=True, help_text="Visible to all users")
    created_by = models.ForeignKey(ExternalUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="release_notes")

    class Meta:
        db_table = "release_notes"
        ordering = ["-release_date", "-created_at"]

    def __str__(self):
        return f"v{self.version} ({self.release_date})"
