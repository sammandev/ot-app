from collections import OrderedDict

from django.conf import settings
from django.db import models
from django.db.utils import IntegrityError
from django.utils import timezone
from rest_framework import serializers

from .models import (
    Asset,
    BoardPresence,
    CalendarEvent,
    Department,
    Document,
    Employee,
    EmployeeLeave,
    Holiday,
    Notification,
    OvertimeBreak,
    OvertimeLimitConfig,
    OvertimeRegulation,
    OvertimeRegulationDocument,
    OvertimeRequest,
    PersonalNote,
    Project,
    PurchaseRequest,
    ReleaseNote,
    SMBConfiguration,
    SystemConfiguration,
    TaskActivity,
    TaskAttachment,
    TaskComment,
    TaskGroup,
    TaskReminder,
    TaskSubtask,
    TaskTimeLog,
    UserActivityLog,
    UserReport,
)
from .services.leave_notification_service import (
    ALLOWED_LEAVE_NOTIFICATION_TEMPLATE_VARIABLES,
    find_unsupported_template_variables,
)


def normalize_external_leave_agents(value):
    if value in (None, ""):
        return []

    if not isinstance(value, list):
        raise serializers.ValidationError("External agents must be provided as an array.")

    normalized = []
    seen = set()
    for item in value:
        if not isinstance(item, dict):
            raise serializers.ValidationError("Each external agent must be an object.")

        username = str(item.get("username") or "").strip()
        email = str(item.get("email") or "").strip().lower()
        worker_id = str(item.get("worker_id") or "").strip()
        site = str(item.get("site") or "").strip()
        source = str(item.get("source") or "external_lookup").strip() or "external_lookup"

        if not email:
            raise serializers.ValidationError("Each external agent must include an email address.")
        if not worker_id and not email:
            raise serializers.ValidationError("Each external agent must include a worker_id or email.")

        if not username:
            username = email or worker_id

        dedupe_key = worker_id.lower() if worker_id else email
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)

        normalized.append(
            {
                "username": username,
                "email": email,
                "worker_id": worker_id,
                "site": site,
                "source": source,
            }
        )

    return normalized


def normalize_manual_leave_agent_names(value):
    if value in (None, ""):
        return []

    if isinstance(value, str):
        raw_items = value.split(",")
    elif isinstance(value, list):
        raw_items = value
    else:
        raise serializers.ValidationError("Manual agents must be provided as a comma-separated string or array.")

    normalized = []
    seen = set()
    for item in raw_items:
        name = str(item or "").strip()
        if not name:
            continue
        dedupe_key = " ".join(name.lower().split())
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        normalized.append(name)

    return normalized


def format_manual_leave_agent_names(value):
    normalized = normalize_manual_leave_agent_names(value)
    return ", ".join(normalized) if normalized else None


def uses_unified_leave_agents_payload(value):
    return isinstance(value, list) and any(isinstance(item, dict) for item in value)


def normalize_unified_leave_agents(value):
    if value in (None, ""):
        return {"employees": [], "external_agents": [], "manual_names": []}

    if not isinstance(value, list):
        raise serializers.ValidationError("Agents must be provided as an array.")

    employee_ids = []
    seen_employee_ids = set()
    external_candidates = []
    manual_names = []

    for item in value:
        if isinstance(item, bool):
            raise serializers.ValidationError("Boolean values are not valid agents.")

        if isinstance(item, int):
            if item <= 0:
                raise serializers.ValidationError("Employee agent ids must be positive integers.")
            if item not in seen_employee_ids:
                seen_employee_ids.add(item)
                employee_ids.append(item)
            continue

        if not isinstance(item, dict):
            raise serializers.ValidationError("Each agent must be an object.")

        agent_type = str(item.get("type") or "").strip().lower()
        if not agent_type:
            if item.get("employee_id") is not None or item.get("id") is not None:
                agent_type = "employee"
            elif item.get("email") or item.get("worker_id") or item.get("source") == "external_lookup":
                agent_type = "external"
            elif item.get("name"):
                agent_type = "manual"

        if agent_type == "employee":
            raw_employee_id = item.get("employee_id", item.get("id"))
            if isinstance(raw_employee_id, bool):
                raise serializers.ValidationError("Employee agent ids must be positive integers.")
            try:
                employee_id = int(raw_employee_id)
            except (TypeError, ValueError):
                raise serializers.ValidationError("Employee agents must include a valid employee_id.")
            if employee_id <= 0:
                raise serializers.ValidationError("Employee agent ids must be positive integers.")
            if employee_id not in seen_employee_ids:
                seen_employee_ids.add(employee_id)
                employee_ids.append(employee_id)
            continue

        if agent_type == "external":
            external_candidates.append(item)
            continue

        if agent_type == "manual":
            manual_names.append(str(item.get("name") or "").strip())
            continue

        raise serializers.ValidationError("Each agent must use type employee, external, or manual.")

    employee_lookup = {employee.id: employee for employee in Employee.objects.filter(id__in=employee_ids, is_enabled=True).select_related("department")}
    missing_employee_ids = [employee_id for employee_id in employee_ids if employee_id not in employee_lookup]
    if missing_employee_ids:
        raise serializers.ValidationError(f"Unknown or disabled employee agent ids: {', '.join(str(employee_id) for employee_id in missing_employee_ids)}.")

    return {
        "employees": [employee_lookup[employee_id] for employee_id in employee_ids],
        "external_agents": normalize_external_leave_agents(external_candidates),
        "manual_names": normalize_manual_leave_agent_names(manual_names),
    }


def build_unified_leave_agents(employee_agents, external_agents, manual_agent_names):
    unified_agents = []

    for employee in employee_agents:
        unified_agents.append(
            {
                "type": "employee",
                "employee_id": employee.id,
                "name": employee.name,
                "emp_id": employee.emp_id,
                "dept_code": employee.department.code if employee.department else None,
            }
        )

    for agent in normalize_external_leave_agents(external_agents):
        unified_agents.append(
            {
                "type": "external",
                "username": agent["username"],
                "email": agent["email"],
                "worker_id": agent["worker_id"],
                "site": agent["site"],
                "source": agent["source"],
            }
        )

    for name in normalize_manual_leave_agent_names(manual_agent_names):
        unified_agents.append({"type": "manual", "name": name})

    return unified_agents


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "code", "name", "is_enabled"]
        read_only_fields = ["id"]

    def validate_code(self, value):
        if not value.strip():
            raise serializers.ValidationError("Department code cannot be empty")
        return value.strip().upper()

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Department name cannot be empty")
        return value.strip()


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "name", "is_enabled"]
        read_only_fields = ["id"]

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Project name cannot be empty")
        return value.strip()


class EmployeeSerializer(serializers.ModelSerializer):
    department_id = serializers.IntegerField(source="department.id", read_only=True, allow_null=True)
    department_name = serializers.CharField(source="department.name", read_only=True, allow_null=True)

    class Meta:
        model = Employee
        fields = ["id", "name", "emp_id", "department", "department_id", "department_name", "is_enabled", "exclude_from_reports"]
        read_only_fields = ["id", "department_id", "department_name"]

    def validate(self, data):
        # Only validate name if it's being updated
        if "name" in data and not data["name"].strip():
            raise serializers.ValidationError({"name": "Employee name cannot be empty"})

        # Only validate emp_id if it's being updated
        if "emp_id" in data and not data["emp_id"].strip():
            raise serializers.ValidationError({"emp_id": "Employee ID cannot be empty"})

        # Check for duplicate emp_id on create or when emp_id is being updated
        if "emp_id" in data:
            if not self.instance:
                # Creating new employee
                if Employee.objects.filter(emp_id=data["emp_id"]).exists():
                    raise serializers.ValidationError({"emp_id": "An employee with this ID already exists"})
            else:
                # Updating existing employee - check if emp_id changed and if new value is duplicate
                if self.instance.emp_id != data["emp_id"]:
                    if Employee.objects.filter(emp_id=data["emp_id"]).exists():
                        raise serializers.ValidationError({"emp_id": "An employee with this ID already exists"})

        return data

    def create(self, validated_data):
        return super().create(validated_data)


class CalendarEventSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(many=True, queryset=Employee.objects.all(), required=False)
    created_by = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), required=False, allow_null=True)
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), required=False, allow_null=True)
    applied_by = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), required=False, allow_null=True)
    agent = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), required=False, allow_null=True)
    group = serializers.PrimaryKeyRelatedField(queryset=TaskGroup.objects.all(), required=False, allow_null=True)

    # Frontend-compatible field aliases
    employee = serializers.IntegerField(source="created_by.id", read_only=True, allow_null=True)
    employee_id = serializers.IntegerField(source="created_by.id", read_only=True, allow_null=True)
    employee_name = serializers.CharField(source="created_by.name", read_only=True, allow_null=True)
    project_name = serializers.CharField(source="project.name", read_only=True, allow_null=True)
    group_name = serializers.CharField(source="group.name", read_only=True, allow_null=True)
    group_color = serializers.CharField(source="group.color", read_only=True, allow_null=True)

    # Subtask progress counts
    subtask_count = serializers.SerializerMethodField()
    subtask_completed = serializers.SerializerMethodField()

    def get_subtask_count(self, obj):
        # Use annotated value from queryset; no fallback query to avoid N+1
        return getattr(obj, "_subtask_count", 0)

    def get_subtask_completed(self, obj):
        # Use annotated value from queryset; no fallback query to avoid N+1
        return getattr(obj, "_subtask_completed", 0)

    def validate(self, data):
        """
        Check that start is before end and required fields are present
        """
        # Validate title only if it's being updated
        if "title" in data and not data["title"]:
            raise serializers.ValidationError({"title": "Title is required"})

        # Get dates from data (update) or instance (fallback)
        start = data.get("start")
        end = data.get("end")

        if self.instance:
            if start is None:
                start = self.instance.start
            if end is None:
                end = self.instance.end

        if start and end and start > end:
            raise serializers.ValidationError({"end": "End date must be after start date"})

        # Set default event_type if not provided and creating
        if not self.instance and "event_type" not in data:
            data["event_type"] = "task"

        # Validate required fields based on event type
        event_type = data.get("event_type")
        if self.instance and not event_type:
            event_type = self.instance.event_type

        if event_type == "meeting":
            # Check if url is present if it's being updated, or check if it exists in instance
            url_in_data = "meeting_url" in data
            if url_in_data and not data.get("meeting_url"):
                raise serializers.ValidationError({"meeting_url": "URL is required for meetings"})
            elif not self.instance and not data.get("meeting_url"):
                raise serializers.ValidationError({"meeting_url": "URL is required for meetings"})

        elif event_type == "task":
            if "project" in data and not data.get("project"):
                # Allow project to be cleared? Comments said optional for tasks.
                data["project"] = None

        # Validate color format if provided
        if "color" in data:
            color = data.get("color", "")
            if color and not color.startswith("#"):
                raise serializers.ValidationError({"color": "Color must be a hex code starting with #"})
            if color and len(color) not in [4, 7]:  # #FFF or #FFFFFF
                raise serializers.ValidationError({"color": "Color must be in format #RGB or #RRGGBB"})

        return data

    def create(self, validated_data):
        assigned_to = validated_data.pop("assigned_to", [])
        event = super().create(validated_data)
        if assigned_to is not None:
            event.assigned_to.set(assigned_to)
        return event

    def update(self, instance, validated_data):
        assigned_to = validated_data.pop("assigned_to", None)
        event = super().update(instance, validated_data)
        if assigned_to is not None:
            event.assigned_to.set(assigned_to)
        return event

    class Meta:
        model = CalendarEvent
        fields = [
            "id",
            "title",
            "event_type",
            "status",
            "description",
            "start",
            "end",
            "all_day",
            "location",
            "color",
            "priority",
            "labels",
            "is_repeating",
            "repeat_frequency",
            "parent_event",
            "created_by",
            "employee",
            "employee_id",
            "employee_name",
            "assigned_to",
            "meeting_url",
            "project",
            "project_name",
            "group",
            "group_name",
            "group_color",
            "subtask_count",
            "subtask_completed",
            "estimated_hours",
            "actual_hours",
            "applied_by",
            "leave_type",
            "agent",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "employee", "employee_id", "employee_name", "project_name", "group_name", "group_color", "subtask_count", "subtask_completed", "actual_hours", "created_at", "updated_at"]


class HolidaySerializer(serializers.ModelSerializer):
    """Serializer for Holiday model - used in the new HolidayCalendar page"""

    created_by_username = serializers.CharField(source="created_by.username", read_only=True, allow_null=True)

    class Meta:
        model = Holiday
        fields = [
            "id",
            "title",
            "date",
            "color",
            "description",
            "is_recurring",
            "created_by",
            "created_by_username",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_by_username", "created_at", "updated_at"]

    def validate_color(self, value):
        """Validate hex color format"""
        if value and not value.startswith("#"):
            raise serializers.ValidationError("Color must be a hex code starting with #")
        if value and len(value) not in [4, 7]:
            raise serializers.ValidationError("Color must be in format #RGB or #RRGGBB")
        return value


class EmployeeLeaveSerializer(serializers.ModelSerializer):
    """Serializer for EmployeeLeave model - leave tracking with agent coverage"""

    employee_name = serializers.CharField(source="employee.name", read_only=True)
    employee_emp_id = serializers.CharField(source="employee.emp_id", read_only=True)
    employee_dept_code = serializers.CharField(source="employee.department.code", read_only=True, allow_null=True)
    created_by_username = serializers.CharField(source="created_by.username", read_only=True, allow_null=True)
    batch_key = serializers.UUIDField(read_only=True, allow_null=True)

    agents = serializers.JSONField(required=False, write_only=True)
    agent_ids = serializers.SerializerMethodField()
    agent_details = serializers.SerializerMethodField()
    external_agents = serializers.JSONField(required=False, write_only=True)
    agent_names = serializers.CharField(required=False, allow_blank=True, allow_null=True, write_only=True)

    class Meta:
        model = EmployeeLeave
        fields = [
            "id",
            "employee",
            "employee_name",
            "employee_emp_id",
            "employee_dept_code",
            "date",
            "batch_key",
            "notes",
            "agents",
            "agent_ids",
            "agent_details",
            "external_agents",
            "agent_names",
            "created_by",
            "created_by_username",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "employee_name", "employee_emp_id", "employee_dept_code", "batch_key", "agent_ids", "agent_details", "created_by", "created_by_username", "created_at", "updated_at"]

    def validate_agents(self, value):
        return normalize_unified_leave_agents(value)

    def validate_external_agents(self, value):
        return normalize_external_leave_agents(value)

    def validate_agent_names(self, value):
        return format_manual_leave_agent_names(value)

    def validate(self, attrs):
        attrs = super().validate(attrs)

        raw_agents = getattr(self, "initial_data", {}).get("agents", serializers.empty)
        parsed_agents = attrs.get("agents", serializers.empty)
        legacy_external_agents = attrs.get("external_agents", serializers.empty)
        legacy_agent_names = attrs.get("agent_names", serializers.empty)

        if parsed_agents is not serializers.empty:
            if not uses_unified_leave_agents_payload(raw_agents):
                external_candidates = [*parsed_agents["external_agents"]]
                if legacy_external_agents is not serializers.empty:
                    external_candidates.extend(legacy_external_agents)
                manual_candidates = [*parsed_agents["manual_names"]]
                if legacy_agent_names is not serializers.empty:
                    manual_candidates.extend(normalize_manual_leave_agent_names(legacy_agent_names))
                parsed_agents = {
                    **parsed_agents,
                    "external_agents": normalize_external_leave_agents(external_candidates),
                    "manual_names": normalize_manual_leave_agent_names(manual_candidates),
                }

            attrs["agents"] = parsed_agents["employees"]
            attrs["external_agents"] = parsed_agents["external_agents"]
            attrs["agent_names"] = format_manual_leave_agent_names(parsed_agents["manual_names"])
        else:
            if legacy_external_agents is not serializers.empty:
                attrs["external_agents"] = normalize_external_leave_agents(legacy_external_agents)
            if legacy_agent_names is not serializers.empty:
                attrs["agent_names"] = format_manual_leave_agent_names(legacy_agent_names)

        return attrs

    def get_agent_ids(self, obj):
        # Use prefetched agents to avoid extra query
        return [a.id for a in obj.agents.all()]

    def get_agent_details(self, obj):
        # Use prefetched agents (with select_related department) to avoid N+1
        return [{"id": a.id, "name": a.name, "emp_id": a.emp_id, "dept_code": a.department.code if a.department else None} for a in obj.agents.all()]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["agents"] = build_unified_leave_agents(instance.agents.all(), instance.external_agents, instance.agent_names)
        return data

    def create(self, validated_data):
        agents = validated_data.pop("agents", [])
        leave = EmployeeLeave.objects.create(**validated_data)
        if agents:
            leave.agents.set(agents)
        return leave

    def update(self, instance, validated_data):
        agents = validated_data.pop("agents", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if agents is not None:
            instance.agents.set(agents)
        return instance


class EmployeeLeaveBatchCreateSerializer(serializers.Serializer):
    employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.filter(is_enabled=True))
    dates = serializers.ListField(child=serializers.DateField(), allow_empty=False)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    agents = serializers.JSONField(required=False)
    external_agents = serializers.JSONField(required=False)
    agent_names = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_agents(self, value):
        return normalize_unified_leave_agents(value)

    def validate_external_agents(self, value):
        return normalize_external_leave_agents(value)

    def validate_agent_names(self, value):
        return format_manual_leave_agent_names(value)

    def validate_dates(self, value):
        unique_dates = list(OrderedDict((date_value, True) for date_value in value).keys())
        if not unique_dates:
            raise serializers.ValidationError("At least one leave date is required.")
        return unique_dates

    def validate(self, attrs):
        raw_agents = getattr(self, "initial_data", {}).get("agents", serializers.empty)
        parsed_agents = attrs.get("agents", serializers.empty)
        legacy_external_agents = attrs.get("external_agents", serializers.empty)
        legacy_agent_names = attrs.get("agent_names", serializers.empty)

        if parsed_agents is not serializers.empty:
            if not uses_unified_leave_agents_payload(raw_agents):
                external_candidates = [*parsed_agents["external_agents"]]
                if legacy_external_agents is not serializers.empty:
                    external_candidates.extend(legacy_external_agents)
                manual_candidates = [*parsed_agents["manual_names"]]
                if legacy_agent_names is not serializers.empty:
                    manual_candidates.extend(normalize_manual_leave_agent_names(legacy_agent_names))
                parsed_agents = {
                    **parsed_agents,
                    "external_agents": normalize_external_leave_agents(external_candidates),
                    "manual_names": normalize_manual_leave_agent_names(manual_candidates),
                }

            attrs["agents"] = parsed_agents["employees"]
            attrs["external_agents"] = parsed_agents["external_agents"]
            attrs["agent_names"] = format_manual_leave_agent_names(parsed_agents["manual_names"])
        else:
            attrs["agents"] = []
            attrs["external_agents"] = normalize_external_leave_agents(legacy_external_agents) if legacy_external_agents is not serializers.empty else []
            attrs["agent_names"] = format_manual_leave_agent_names(legacy_agent_names) if legacy_agent_names is not serializers.empty else None

        employee = attrs["employee"]
        dates = attrs["dates"]
        existing_dates = list(EmployeeLeave.objects.filter(employee=employee, date__in=dates).order_by("date").values_list("date", flat=True))
        if existing_dates:
            formatted_dates = ", ".join(date_value.isoformat() for date_value in existing_dates)
            raise serializers.ValidationError({"dates": f"Leave already exists for {employee.name} on: {formatted_dates}."})
        return attrs


class EmployeeLeaveBatchUpdateSerializer(serializers.Serializer):
    leave_ids = serializers.ListField(child=serializers.IntegerField(min_value=1), allow_empty=False)
    employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.filter(is_enabled=True))
    dates = serializers.ListField(child=serializers.DateField(), allow_empty=False)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    agents = serializers.JSONField(required=False)
    external_agents = serializers.JSONField(required=False)
    agent_names = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate_agents(self, value):
        return normalize_unified_leave_agents(value)

    def validate_external_agents(self, value):
        return normalize_external_leave_agents(value)

    def validate_agent_names(self, value):
        return format_manual_leave_agent_names(value)

    def validate_leave_ids(self, value):
        unique_ids = list(OrderedDict((leave_id, True) for leave_id in value).keys())
        if not unique_ids:
            raise serializers.ValidationError("At least one leave record is required for batch update.")
        return unique_ids

    def validate_dates(self, value):
        unique_dates = list(OrderedDict((date_value, True) for date_value in value).keys())
        if not unique_dates:
            raise serializers.ValidationError("At least one leave date is required.")
        return unique_dates

    def validate(self, attrs):
        raw_agents = getattr(self, "initial_data", {}).get("agents", serializers.empty)
        parsed_agents = attrs.get("agents", serializers.empty)
        legacy_external_agents = attrs.get("external_agents", serializers.empty)
        legacy_agent_names = attrs.get("agent_names", serializers.empty)

        if parsed_agents is not serializers.empty:
            if not uses_unified_leave_agents_payload(raw_agents):
                external_candidates = [*parsed_agents["external_agents"]]
                if legacy_external_agents is not serializers.empty:
                    external_candidates.extend(legacy_external_agents)
                manual_candidates = [*parsed_agents["manual_names"]]
                if legacy_agent_names is not serializers.empty:
                    manual_candidates.extend(normalize_manual_leave_agent_names(legacy_agent_names))
                parsed_agents = {
                    **parsed_agents,
                    "external_agents": normalize_external_leave_agents(external_candidates),
                    "manual_names": normalize_manual_leave_agent_names(manual_candidates),
                }

            attrs["agents"] = parsed_agents["employees"]
            attrs["external_agents"] = parsed_agents["external_agents"]
            attrs["agent_names"] = format_manual_leave_agent_names(parsed_agents["manual_names"])
        else:
            attrs["agents"] = []
            attrs["external_agents"] = normalize_external_leave_agents(legacy_external_agents) if legacy_external_agents is not serializers.empty else []
            attrs["agent_names"] = format_manual_leave_agent_names(legacy_agent_names) if legacy_agent_names is not serializers.empty else None

        return attrs


class EmployeeLeaveBatchDeleteSerializer(serializers.Serializer):
    leave_ids = serializers.ListField(child=serializers.IntegerField(min_value=1), allow_empty=False)

    def validate_leave_ids(self, value):
        unique_ids = list(OrderedDict((leave_id, True) for leave_id in value).keys())
        if not unique_ids:
            raise serializers.ValidationError("At least one leave record is required for batch delete.")
        return unique_ids


class OvertimeBreakSerializer(serializers.ModelSerializer):
    duration_minutes = serializers.SerializerMethodField()

    class Meta:
        model = OvertimeBreak
        fields = ["id", "start_time", "end_time", "duration_minutes"]
        read_only_fields = ["id", "duration_minutes"]

    def get_duration_minutes(self, obj):
        """Convert duration_hours to minutes for frontend"""
        return int(float(obj.duration_hours) * 60) if obj.duration_hours else 0


class OvertimeSerializer(serializers.ModelSerializer):
    breaks = OvertimeBreakSerializer(many=True, required=False, read_only=True)

    # Computed fields
    employee_name = serializers.CharField(source="employee.name", read_only=True, allow_null=True)
    employee_id = serializers.IntegerField(source="employee.id", read_only=True, allow_null=True)
    employee_emp_id = serializers.CharField(source="employee.emp_id", read_only=True, allow_null=True)
    department_code = serializers.CharField(source="employee.department.code", read_only=True, allow_null=True)
    department_name = serializers.CharField(source="employee.department.name", read_only=True, allow_null=True)
    project_name = serializers.CharField(source="project.name", read_only=True, allow_null=True)

    # Approver information
    approver_name = serializers.CharField(source="approved_by.name", read_only=True, allow_null=True)

    class Meta:
        model = OvertimeRequest
        fields = [
            "id",
            "employee",
            "employee_name",
            "employee_id",
            "employee_emp_id",
            "department_code",
            "department_name",
            "project",
            "project_name",
            "request_date",
            "time_start",
            "time_end",
            "total_hours",
            "has_break",
            "breaks",
            "break_start",
            "break_end",
            "break_hours",
            "reason",
            "detail",
            "is_holiday",
            "is_weekend",
            "status",
            "approved_by",
            "approver_name",  # NEW: Approver name
            "approved_at",
            "rejection_reason",
            "status_changed_by",
            "rejected_at",
        ]
        read_only_fields = ["id", "employee_name", "employee_id", "employee_emp_id", "department_code", "department_name", "project_name", "approver_name", "status_changed_by", "rejected_at"]

    def _populate_denormalized_fields(self, validated_data):
        """Ensure denormalized fields are kept in sync when saving."""
        employee = validated_data.get("employee")
        project = validated_data.get("project")

        if employee:
            # Ensure department is loaded to avoid extra query
            if not hasattr(employee, "_department_cache") and employee.department_id:
                employee = Employee.objects.select_related("department").get(pk=employee.pk)
                validated_data["employee"] = employee
            validated_data["employee_name"] = getattr(employee, "name", "")
            # NOTE: Do NOT set employee_id here!
            # The 'employee' field is already the FK and Django handles employee_id automatically.
            # Previously this line was setting employee_id to emp_id (worker_id like 'MW2400549')
            # which caused "Field 'id' expected a number but got 'MW2400549'" errors.
            # validated_data["employee_id"] = getattr(employee, "emp_id", "")  # WRONG - REMOVED!

            # Persist department linkage for reporting
            dept = getattr(employee, "department", None)
            if dept:
                validated_data["department"] = dept
                validated_data["department_code"] = getattr(dept, "code", "")
                # Note: department_name is a read-only computed field, don't set it here

        if project:
            validated_data["project_name"] = getattr(project, "name", "")

    def validate(self, data):
        errors = {}

        if not data.get("employee"):
            errors["employee"] = "Employee is required"

        if not data.get("project"):
            errors["project"] = "Project is required"

        reason = (data.get("reason") or "").strip()
        if not reason:
            errors["reason"] = "Reason is required"
        else:
            data["reason"] = reason

        total_hours = data.get("total_hours")
        if total_hours is not None:
            try:
                if float(total_hours) <= 0:
                    errors["total_hours"] = "Total hours must be greater than zero"
            except (TypeError, ValueError):
                errors["total_hours"] = "Total hours must be a number"

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        # Note: grouped Excel export is handled in OvertimeRequest.save(); serializer remains thin.
        self._populate_denormalized_fields(validated_data)
        breaks_data = validated_data.pop("breaks", [])

        try:
            overtime_request = OvertimeRequest.objects.create(**validated_data)
        except IntegrityError as exc:
            if "unique_overtime_employee_project_date" in str(exc):
                raise serializers.ValidationError({"non_field_errors": ["An overtime request already exists for this employee, project, and date."]}) from exc
            raise

        for break_data in breaks_data:
            OvertimeBreak.objects.create(overtime_request=overtime_request, **break_data)

        return overtime_request

    def update(self, instance, validated_data):
        # Note: grouped Excel export is handled in OvertimeRequest.save(); serializer remains thin.
        self._populate_denormalized_fields(validated_data)
        breaks_data = validated_data.pop("breaks", [])

        # Update the main instance fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        try:
            instance.save()
        except IntegrityError as exc:
            if "unique_overtime_employee_project_date" in str(exc):
                raise serializers.ValidationError({"non_field_errors": ["An overtime request already exists for this employee, project, and date."]}) from exc
            raise

        # Handle breaks - replace all breaks
        instance.breaks.all().delete()
        for break_data in breaks_data:
            OvertimeBreak.objects.create(overtime_request=instance, **break_data)

        return instance


class OvertimeRegulationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OvertimeRegulation
        fields = ["id", "title", "description", "category", "order", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        return value.strip()

    def validate_order(self, value):
        if value < 0:
            raise serializers.ValidationError("Order must be a non-negative number")
        return value


class OvertimeLimitConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = OvertimeLimitConfig
        fields = ["id", "max_weekly_hours", "max_monthly_hours", "advised_weekly_hours", "advised_monthly_hours", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_max_weekly_hours(self, value):
        if value <= 0:
            raise serializers.ValidationError("Max weekly hours must be positive")
        if value > 168:
            raise serializers.ValidationError("Max weekly hours cannot exceed 168 (hours in a week)")
        return value

    def validate_max_monthly_hours(self, value):
        if value <= 0:
            raise serializers.ValidationError("Max monthly hours must be positive")
        if value > 744:
            raise serializers.ValidationError("Max monthly hours cannot exceed 744 (hours in a month)")
        return value


class OvertimeRegulationDocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source="uploaded_by.username", read_only=True)

    class Meta:
        model = OvertimeRegulationDocument
        fields = ["id", "title", "description", "file", "file_size", "version", "is_active", "uploaded_by", "uploaded_by_name", "created_at", "updated_at"]
        read_only_fields = ["id", "file_size", "version", "created_at", "updated_at"]

    def create(self, validated_data):
        # Auto-calculate file size
        if "file" in validated_data:
            validated_data["file_size"] = validated_data["file"].size
        return super().create(validated_data)


class TagListField(serializers.Field):
    """Expose pipe-delimited tags as a normalized string list."""

    def to_representation(self, value):
        if not value:
            return []
        return [tag for tag in value.split("|") if tag]

    def to_internal_value(self, data):
        if data in (None, ""):
            return ""

        if isinstance(data, str):
            normalized = data.strip()
            if normalized.startswith("["):
                try:
                    import json

                    data = json.loads(normalized)
                except json.JSONDecodeError as exc:
                    raise serializers.ValidationError("Tags must be a list of strings.") from exc
            else:
                data = [part.strip() for part in normalized.split(",") if part.strip()]

        if not isinstance(data, list):
            raise serializers.ValidationError("Tags must be a list of strings.")

        normalized_tags = []
        seen = set()
        for item in data:
            tag = str(item).strip().lower()
            if not tag or tag in seen:
                continue
            seen.add(tag)
            normalized_tags.append(tag)

        return f"|{'|'.join(normalized_tags)}|" if normalized_tags else ""


class DocumentListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)
    tags = TagListField(required=False)
    file_url = serializers.SerializerMethodField()
    host = serializers.SerializerMethodField()
    can_preview = serializers.SerializerMethodField()
    preview_type = serializers.SerializerMethodField()
    is_external = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "source_type",
            "category",
            "tags",
            "is_pinned",
            "original_filename",
            "stored_file_size",
            "mime_type",
            "extension",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
            "file_url",
            "external_url",
            "host",
            "can_preview",
            "preview_type",
            "is_external",
            "link_site_name",
            "metadata_status",
            "metadata_fetched_at",
        ]
        read_only_fields = fields

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

    def get_host(self, obj):
        from urllib.parse import urlparse

        url = obj.normalized_url or obj.external_url
        return urlparse(url).netloc if url else ""

    def get_can_preview(self, obj):
        return obj.can_preview

    def get_preview_type(self, obj):
        return obj.preview_type

    def get_is_external(self, obj):
        return obj.source_type == Document.SourceType.LINK


class DocumentDetailSerializer(DocumentListSerializer):
    class Meta(DocumentListSerializer.Meta):
        fields = DocumentListSerializer.Meta.fields + [
            "description",
            "normalized_url",
            "updated_by",
            "link_title",
            "link_description",
            "link_favicon_url",
            "link_image_url",
            "metadata_error",
        ]
        read_only_fields = fields


class DocumentWriteSerializer(serializers.ModelSerializer):
    MAX_UPLOAD_SIZE = 25 * 1024 * 1024

    tags = TagListField(required=False)
    title = serializers.CharField(required=False, allow_blank=True, max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    category = serializers.CharField(required=False, allow_blank=True, max_length=100)
    external_url = serializers.URLField(required=False, allow_blank=True, max_length=1000)

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "description",
            "source_type",
            "file",
            "external_url",
            "category",
            "tags",
            "is_pinned",
        ]
        read_only_fields = ["id"]

    def validate_file(self, value):
        if not value:
            return value
        if value.size <= 0:
            raise serializers.ValidationError("Uploaded file is empty.")
        if value.size > self.MAX_UPLOAD_SIZE:
            raise serializers.ValidationError(
                f"File size exceeds {self.MAX_UPLOAD_SIZE // (1024 * 1024)} MB limit.",
            )
        return value

    def validate(self, attrs):
        source_type = attrs.get("source_type")
        file = attrs.get("file")
        external_url = attrs.get("external_url")

        if self.instance:
            source_type = source_type or self.instance.source_type
            if file is None:
                file = self.instance.file
            if external_url is None:
                external_url = self.instance.external_url

        has_file = bool(file)
        has_url = bool(str(external_url or "").strip())

        if source_type == Document.SourceType.FILE and not has_file:
            raise serializers.ValidationError({"file": "A file is required when source type is file."})
        if source_type == Document.SourceType.LINK and not has_url:
            raise serializers.ValidationError({"external_url": "A URL is required when source type is link."})
        if has_file and has_url:
            raise serializers.ValidationError("Provide either a file or a URL, not both.")

        title = (attrs.get("title") or "").strip()
        if not title:
            if source_type == Document.SourceType.FILE and file:
                attrs["title"] = getattr(file, "name", "Document").split("/")[-1]
            elif source_type == Document.SourceType.LINK and external_url:
                from urllib.parse import urlparse

                parsed = urlparse(str(external_url).strip())
                attrs["title"] = parsed.netloc or parsed.path or "Link"
        else:
            attrs["title"] = title

        if "description" in attrs:
            attrs["description"] = attrs["description"].strip()
        if "category" in attrs:
            attrs["category"] = attrs["category"].strip()
        if has_url:
            attrs["external_url"] = self._normalize_url(str(external_url).strip())

        return attrs

    @staticmethod
    def _normalize_url(url):
        from urllib.parse import urlsplit, urlunsplit

        parsed = urlsplit(url)
        normalized_netloc = parsed.netloc.lower()
        normalized_scheme = parsed.scheme.lower()
        normalized_path = parsed.path or ""
        normalized_query = parsed.query or ""
        return urlunsplit((normalized_scheme, normalized_netloc, normalized_path, normalized_query, ""))

    @staticmethod
    def _apply_file_metadata(validated_data, uploaded_file):
        import mimetypes

        validated_data["source_type"] = Document.SourceType.FILE
        validated_data["normalized_url"] = ""
        validated_data["external_url"] = ""
        validated_data["original_filename"] = uploaded_file.name.split("/")[-1]
        validated_data["stored_file_size"] = uploaded_file.size
        mime_type = getattr(uploaded_file, "content_type", "") or mimetypes.guess_type(uploaded_file.name)[0] or ""
        validated_data["mime_type"] = mime_type
        extension = uploaded_file.name.rsplit(".", 1)[-1].lower() if "." in uploaded_file.name else ""
        validated_data["extension"] = extension

    @staticmethod
    def _apply_link_metadata(validated_data, url):
        validated_data["source_type"] = Document.SourceType.LINK
        validated_data["normalized_url"] = url
        validated_data["external_url"] = url
        validated_data["file"] = None
        validated_data["original_filename"] = ""
        validated_data["stored_file_size"] = None
        validated_data["mime_type"] = ""
        validated_data["extension"] = ""

    @staticmethod
    def _reset_link_metadata(validated_data, url=""):
        from .services.document_metadata import fetch_link_metadata

        if not url:
            validated_data["link_title"] = ""
            validated_data["link_description"] = ""
            validated_data["link_site_name"] = ""
            validated_data["link_favicon_url"] = ""
            validated_data["link_image_url"] = ""
            validated_data["metadata_status"] = Document.MetadataStatus.PENDING
            validated_data["metadata_error"] = ""
            validated_data["metadata_fetched_at"] = None
            return

        validated_data.update(fetch_link_metadata(url))

    def create(self, validated_data):
        uploaded_file = validated_data.get("file")
        external_url = validated_data.get("external_url", "")

        if uploaded_file:
            self._apply_file_metadata(validated_data, uploaded_file)
            self._reset_link_metadata(validated_data)
        else:
            self._apply_link_metadata(validated_data, external_url)
            self._reset_link_metadata(validated_data, external_url)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        old_file = instance.file if instance.file else None
        uploaded_file = validated_data.get("file")
        external_url = validated_data.get("external_url")
        source_type = validated_data.get("source_type", instance.source_type)

        if source_type == Document.SourceType.FILE:
            if uploaded_file:
                self._apply_file_metadata(validated_data, uploaded_file)
            else:
                validated_data["external_url"] = ""
                validated_data["normalized_url"] = ""
            self._reset_link_metadata(validated_data)
        else:
            effective_url = str(external_url if external_url is not None else instance.external_url).strip()
            self._apply_link_metadata(validated_data, effective_url)
            existing_url = (instance.normalized_url or instance.external_url or "").strip()
            if instance.source_type != Document.SourceType.LINK or effective_url != existing_url:
                self._reset_link_metadata(validated_data, effective_url)

        document = super().update(instance, validated_data)

        should_remove_old_file = old_file and (source_type == Document.SourceType.LINK or uploaded_file is not None)
        if should_remove_old_file:
            old_name = getattr(old_file, "name", "")
            current_name = getattr(document.file, "name", "") if document.file else ""
            if old_name and old_name != current_name:
                old_file.delete(save=False)

        return document


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for text notifications"""

    time_ago = serializers.SerializerMethodField()
    computed_event_type = serializers.SerializerMethodField()
    meeting_url = serializers.SerializerMethodField()
    target_data = serializers.JSONField(read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "recipient", "title", "message", "event", "is_read", "is_archived", "event_type", "target_data", "created_at", "time_ago", "computed_event_type", "meeting_url"]
        read_only_fields = ["id", "created_at", "recipient"]

    def get_time_ago(self, obj):
        from .utils.time_helpers import format_time_ago

        return format_time_ago(obj.created_at)

    def get_computed_event_type(self, obj):
        """Return the event type - prefer stored value, fallback to linked event"""
        if obj.event_type:
            return obj.event_type
        if obj.event:
            return obj.event.event_type
        return None

    def get_meeting_url(self, obj):
        """Return the meeting URL if the notification is for a meeting event"""
        if obj.event and obj.event.event_type == "meeting":
            return obj.event.meeting_url
        return None


class SystemConfigurationSerializer(serializers.ModelSerializer):
    tab_icon_url = serializers.SerializerMethodField()
    sidebar_logo_url = serializers.SerializerMethodField()
    user_activity_log_cleanup_time = serializers.TimeField(required=False, format="%H:%M", input_formats=["%H:%M", "%H:%M:%S"])

    class Meta:
        model = SystemConfiguration
        fields = [
            "app_name",
            "app_acronym",
            "version",
            "build_date",
            "event_reminders_disabled_globally",
            "event_reminders_disabled_roles",
            "event_reminders_disabled_users",
            "tab_icon",
            "tab_icon_url",
            "sidebar_logo",
            "sidebar_logo_url",
            "notification_email_host",
            "notification_email_port",
            "leave_notification_recipients",
            "leave_notification_sender_name",
            "leave_notification_recipient_mode",
            "leave_notification_department_recipients",
            "leave_notification_employee_recipients",
            "leave_notification_employee_groups",
            "user_activity_log_retention_days",
            "user_activity_log_cleanup_time",
            "leave_notification_subject_template",
            "leave_notification_body_template",
            "leave_notification_footer_template",
            "updated_at",
        ]
        read_only_fields = ["updated_at", "version", "build_date", "tab_icon_url", "sidebar_logo_url"]

    def _enabled_employee_lookup(self):
        return {employee.id: employee for employee in Employee.objects.filter(is_enabled=True).select_related("department")}

    def _validate_group_recipient_entry(self, value, *, field_name):
        if not isinstance(value, dict):
            raise serializers.ValidationError(f"Each {field_name} entry must be an object.")

        group_id = str(value.get("id") or "").strip()
        name = str(value.get("name") or "").strip()
        employee_ids = value.get("employee_ids", [])
        recipients = self._validate_recipient_list(value.get("recipients", []), field_name=f"Recipients for {name or group_id or 'group'}")

        if not group_id:
            raise serializers.ValidationError(f"Each {field_name} entry must include an id.")
        if not name:
            raise serializers.ValidationError(f"Each {field_name} entry must include a name.")
        if not isinstance(employee_ids, list):
            raise serializers.ValidationError(f"Employee ids for {name} must be a list.")

        normalized_employee_ids = []
        seen_employee_ids = set()
        employee_lookup = self._enabled_employee_lookup()
        for raw_employee_id in employee_ids:
            try:
                employee_id = int(raw_employee_id)
            except (TypeError, ValueError):
                raise serializers.ValidationError(f"Employee ids for {name} must be integers.")
            if employee_id in seen_employee_ids:
                continue
            if employee_id not in employee_lookup:
                raise serializers.ValidationError(f"Unknown or disabled employee id {employee_id} in {name}.")
            seen_employee_ids.add(employee_id)
            normalized_employee_ids.append(employee_id)

        return {
            "id": group_id,
            "name": name,
            "employee_ids": normalized_employee_ids,
            "recipients": recipients,
        }

    def validate_leave_notification_employee_groups(self, value):
        if value in (None, ""):
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError("Employee groups must be a list.")

        normalized = []
        seen_group_ids = set()
        for item in value:
            group = self._validate_group_recipient_entry(item, field_name="employee group")
            if group["id"] in seen_group_ids:
                raise serializers.ValidationError(f"Duplicate employee group id: {group['id']}.")
            seen_group_ids.add(group["id"])
            normalized.append(group)
        return normalized

    def validate_leave_notification_employee_recipients(self, value):
        if value in (None, ""):
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError("Employee recipient mappings must be a list.")

        employee_lookup = self._enabled_employee_lookup()
        instance = getattr(self, "instance", None)
        groups = self.initial_data.get(
            "leave_notification_employee_groups",
            getattr(instance, "leave_notification_employee_groups", []),
        )
        normalized_groups = self.validate_leave_notification_employee_groups(groups)
        available_group_ids = {group["id"] for group in normalized_groups}

        normalized = []
        seen_employee_ids = set()
        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError("Each employee recipient mapping must be an object.")
            try:
                employee_id = int(item.get("employee_id"))
            except (TypeError, ValueError):
                raise serializers.ValidationError("Each employee recipient mapping must include a valid employee_id.")
            if employee_id in seen_employee_ids:
                raise serializers.ValidationError(f"Duplicate employee recipient mapping for employee {employee_id}.")
            if employee_id not in employee_lookup:
                raise serializers.ValidationError(f"Unknown or disabled employee id: {employee_id}.")

            group_ids = item.get("group_ids", [])
            if group_ids in (None, ""):
                group_ids = []
            if not isinstance(group_ids, list):
                raise serializers.ValidationError(f"Group ids for employee {employee_id} must be a list.")
            normalized_group_ids = []
            seen_group_ids = set()
            for raw_group_id in group_ids:
                group_id = str(raw_group_id or "").strip()
                if not group_id:
                    continue
                if group_id in seen_group_ids:
                    continue
                if group_id not in available_group_ids:
                    raise serializers.ValidationError(f"Unknown employee group id {group_id} for employee {employee_id}.")
                seen_group_ids.add(group_id)
                normalized_group_ids.append(group_id)

            normalized.append(
                {
                    "employee_id": employee_id,
                    "recipients": self._validate_recipient_list(item.get("recipients", []), field_name=f"Recipients for employee {employee_id}"),
                    "group_ids": normalized_group_ids,
                }
            )
            seen_employee_ids.add(employee_id)

        return normalized

    def validate_user_activity_log_retention_days(self, value):
        if value in (None, ""):
            return None
        if value < 1:
            raise serializers.ValidationError("Activity log retention must be a positive number of days.")
        return value

    def validate_user_activity_log_cleanup_time(self, value):
        if value is None:
            raise serializers.ValidationError("Activity log cleanup time is required.")
        return value

    def _allowed_notification_domain(self):
        from_email = getattr(settings, "LEAVE_NOTIFICATION_FROM_EMAIL", "")
        if "@" in from_email:
            return from_email.split("@", 1)[1].lower()
        return "pegatroncorp.com"

    def _validate_recipient_list(self, value, *, field_name):
        if value in (None, ""):
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError(f"{field_name} must be a list of email addresses.")

        validator = serializers.EmailField()
        normalized = []
        allowed_domain = self._allowed_notification_domain()
        for raw_email in value:
            if not isinstance(raw_email, str):
                raise serializers.ValidationError("Each recipient must be a valid email address.")
            email = raw_email.strip().lower()
            if not email:
                continue
            if not email.endswith(f"@{allowed_domain}"):
                raise serializers.ValidationError(f"All recipients must use the @{allowed_domain} domain.")
            validator.run_validation(email)
            normalized.append(email)

        return list(OrderedDict((email, True) for email in normalized).keys())

    def _validate_template_field(self, value, *, field_label):
        template = (value or "").strip()
        if not template:
            raise serializers.ValidationError(f"{field_label} cannot be empty.")

        unsupported = find_unsupported_template_variables(template)
        if unsupported:
            allowed = ", ".join(sorted(ALLOWED_LEAVE_NOTIFICATION_TEMPLATE_VARIABLES))
            invalid = ", ".join(unsupported)
            raise serializers.ValidationError(f"Unsupported template variables: {invalid}. Allowed variables: {allowed}.")
        return template

    def validate_notification_email_host(self, value):
        host = (value or "").strip()
        if not host:
            raise serializers.ValidationError("Notification email host cannot be empty.")
        return host

    def validate_notification_email_port(self, value):
        if value is None:
            raise serializers.ValidationError("Notification email port is required.")
        if value < 1 or value > 65535:
            raise serializers.ValidationError("Notification email port must be between 1 and 65535.")
        return value

    def validate_leave_notification_recipients(self, value):
        return self._validate_recipient_list(value, field_name="Leave notification recipients")

    def validate_leave_notification_sender_name(self, value):
        sender_name = (value or "").strip()
        if not sender_name:
            raise serializers.ValidationError("Leave notification sender name cannot be empty.")
        return sender_name

    def validate_leave_notification_department_recipients(self, value):
        if value in (None, ""):
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError("Department recipients must be a list of department recipient mappings.")

        department_lookup = {department.code.upper(): department for department in Department.objects.filter(is_enabled=True) if department.code}
        normalized = []
        seen_department_codes = set()

        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError("Each department recipient entry must be an object.")

            department_code = str(item.get("department_code") or "").strip().upper()
            if not department_code:
                raise serializers.ValidationError("Each department recipient entry must include a department_code.")
            if department_code in seen_department_codes:
                raise serializers.ValidationError(f"Duplicate department recipient entry for {department_code}.")
            if department_code not in department_lookup:
                raise serializers.ValidationError(f"Unknown or disabled department code: {department_code}.")

            recipients = self._validate_recipient_list(item.get("recipients", []), field_name=f"Recipients for {department_code}")
            normalized.append({"department_code": department_code, "recipients": recipients})
            seen_department_codes.add(department_code)

        return normalized

    def validate_leave_notification_subject_template(self, value):
        return self._validate_template_field(value, field_label="Leave notification subject template")

    def validate_leave_notification_body_template(self, value):
        return self._validate_template_field(value, field_label="Leave notification body template")

    def validate_leave_notification_footer_template(self, value):
        return self._validate_template_field(value, field_label="Leave notification footer template")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        instance = getattr(self, "instance", None)

        notification_fields = {
            "leave_notification_recipient_mode",
            "leave_notification_recipients",
            "leave_notification_department_recipients",
            "leave_notification_employee_recipients",
            "leave_notification_employee_groups",
        }
        if not any(field in attrs for field in notification_fields):
            return attrs

        mode = attrs.get(
            "leave_notification_recipient_mode",
            getattr(instance, "leave_notification_recipient_mode", "global"),
        )
        global_recipients = attrs.get(
            "leave_notification_recipients",
            getattr(instance, "leave_notification_recipients", []),
        )
        department_recipients = attrs.get(
            "leave_notification_department_recipients",
            getattr(instance, "leave_notification_department_recipients", []),
        )
        employee_recipients = attrs.get(
            "leave_notification_employee_recipients",
            getattr(instance, "leave_notification_employee_recipients", []),
        )
        employee_groups = attrs.get(
            "leave_notification_employee_groups",
            getattr(instance, "leave_notification_employee_groups", []),
        )

        if mode == "global" and not global_recipients:
            raise serializers.ValidationError({"leave_notification_recipients": "Global mode requires at least one recipient."})
        if mode == "department" and not department_recipients:
            raise serializers.ValidationError({"leave_notification_department_recipients": "Department mode requires at least one department recipient mapping."})
        if mode == "custom" and not employee_recipients and not employee_groups:
            raise serializers.ValidationError({"leave_notification_employee_groups": "Custom mode requires at least one employee group or employee-specific rule."})

        return attrs

    def get_tab_icon_url(self, obj):
        if obj.tab_icon:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.tab_icon.url)
            return obj.tab_icon.url
        return None

    def get_sidebar_logo_url(self, obj):
        if obj.sidebar_logo:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.sidebar_logo.url)
            return obj.sidebar_logo.url
        return None


class UserActivityLogPurgeSerializer(serializers.Serializer):
    days = serializers.IntegerField(min_value=1)


class UserActivityLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    worker_id = serializers.CharField(source="user.worker_id", read_only=True)
    action_display = serializers.CharField(source="get_action_display", read_only=True)

    class Meta:
        model = UserActivityLog
        fields = ["id", "user", "username", "worker_id", "action", "action_display", "resource", "resource_id", "details", "ip_address", "user_agent", "timestamp"]
        read_only_fields = ["id", "timestamp"]


class TaskCommentSerializer(serializers.ModelSerializer):
    """Serializer for task comments with threading and mentions"""

    author_name = serializers.CharField(source="author.name", read_only=True)
    author_id = serializers.IntegerField(source="author.id", read_only=True)
    mentions = serializers.PrimaryKeyRelatedField(many=True, queryset=Employee.objects.all(), required=False)
    reply_count = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = TaskComment
        fields = ["id", "task", "author", "author_id", "author_name", "content", "parent", "mentions", "is_edited", "edited_at", "reply_count", "replies", "time_ago", "created_at", "updated_at"]
        read_only_fields = ["id", "author", "author_id", "author_name", "is_edited", "edited_at", "created_at", "updated_at"]

    def validate(self, attrs):
        mentions = attrs.get("mentions")
        if mentions is None:
            return attrs

        task = attrs.get("task") or getattr(self.instance, "task", None)
        if not task:
            return attrs

        # Single query to get allowed employee IDs for mention validation
        mention_ids = {m.id for m in mentions}
        if task.group_id:
            allowed_count = task.group.members.filter(id__in=mention_ids).count()
        else:
            allowed_count = task.assigned_to.filter(id__in=mention_ids).count()

        if allowed_count != len(mention_ids):
            # Only compute names for the error message if validation fails
            if task.group_id:
                allowed_employee_ids = set(task.group.members.filter(id__in=mention_ids).values_list("id", flat=True))
            else:
                allowed_employee_ids = set(task.assigned_to.filter(id__in=mention_ids).values_list("id", flat=True))
            invalid_mentions = [m.name for m in mentions if m.id not in allowed_employee_ids]
            if invalid_mentions:
                raise serializers.ValidationError({"mentions": "Invalid mentions for this task context: " + ", ".join(invalid_mentions)})

        return attrs

    def get_reply_count(self, obj):
        # Use prefetched replies if available to avoid N+1
        if hasattr(obj, "_prefetched_objects_cache") and "replies" in obj._prefetched_objects_cache:
            return len(obj._prefetched_objects_cache["replies"])
        return obj.replies.count()

    def get_replies(self, obj):
        # Only include replies for top-level comments; prevent deep nesting
        max_depth = self.context.get("max_reply_depth", 1)
        current_depth = self.context.get("_reply_depth", 0)
        if obj.parent is None and current_depth < max_depth:
            reply_limit = self.context.get("reply_limit", 20)
            if hasattr(obj, "_prefetched_objects_cache") and "replies" in obj._prefetched_objects_cache:
                replies = obj._prefetched_objects_cache["replies"][:reply_limit]
            else:
                replies = obj.replies.select_related("author").all()[:reply_limit]
            ctx = {**self.context, "_reply_depth": current_depth + 1}
            return TaskCommentSerializer(replies, many=True, context=ctx).data
        return []

    def get_time_ago(self, obj):
        from .utils.time_helpers import format_time_ago

        return format_time_ago(obj.created_at, compact=True)

    def create(self, validated_data):
        mentions = validated_data.pop("mentions", [])
        comment = super().create(validated_data)
        if mentions:
            comment.mentions.set(mentions)
        return comment

    def update(self, instance, validated_data):
        mentions = validated_data.pop("mentions", None)
        validated_data["is_edited"] = True
        validated_data["edited_at"] = timezone.now()
        comment = super().update(instance, validated_data)
        if mentions is not None:
            comment.mentions.set(mentions)
        return comment


class TaskSubtaskSerializer(serializers.ModelSerializer):
    """Serializer for task subtasks/checklist items"""

    created_by_name = serializers.CharField(source="created_by.name", read_only=True)
    completed_by_name = serializers.CharField(source="completed_by.name", read_only=True, allow_null=True)

    class Meta:
        model = TaskSubtask
        fields = ["id", "task", "title", "is_completed", "completed_at", "completed_by", "completed_by_name", "order", "created_by", "created_by_name", "created_at", "updated_at"]
        read_only_fields = ["id", "completed_at", "completed_by", "completed_by_name", "created_by", "created_by_name", "created_at", "updated_at"]

    def create(self, validated_data):
        # Auto-assign order if not provided
        if "order" not in validated_data:
            task = validated_data.get("task")
            max_order = TaskSubtask.objects.filter(task=task).aggregate(models.Max("order"))["order__max"] or 0
            validated_data["order"] = max_order + 1
        return super().create(validated_data)


class TaskTimeLogSerializer(serializers.ModelSerializer):
    """Serializer for task time logs/timer entries"""

    employee_name = serializers.CharField(source="employee.name", read_only=True)
    task_title = serializers.CharField(source="task.title", read_only=True)
    duration_formatted = serializers.SerializerMethodField()

    class Meta:
        model = TaskTimeLog
        fields = ["id", "task", "task_title", "employee", "employee_name", "description", "started_at", "ended_at", "duration_minutes", "duration_formatted", "is_running", "created_at", "updated_at"]
        read_only_fields = ["id", "employee", "employee_name", "task_title", "duration_formatted", "created_at", "updated_at"]

    def get_duration_formatted(self, obj):
        """Format duration as Xh Ym"""
        minutes = obj.duration_minutes or 0
        hours = minutes // 60
        mins = minutes % 60
        if hours > 0:
            return f"{hours}h {mins}m"
        return f"{mins}m"

    def create(self, validated_data):
        # Set started_at to now if not provided
        if "started_at" not in validated_data:
            validated_data["started_at"] = timezone.now()
        return super().create(validated_data)


class TaskActivitySerializer(serializers.ModelSerializer):
    """Serializer for task activity log"""

    actor_name = serializers.CharField(source="actor.name", read_only=True)
    actor_id = serializers.IntegerField(source="actor.id", read_only=True)
    action_display = serializers.CharField(source="get_action_display", read_only=True)
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = TaskActivity
        fields = ["id", "task", "actor", "actor_id", "actor_name", "action", "action_display", "old_value", "new_value", "extra_data", "time_ago", "created_at"]
        read_only_fields = ["id", "created_at"]

    def get_time_ago(self, obj):
        from .utils.time_helpers import format_time_ago

        return format_time_ago(obj.created_at, compact=True)


class BoardPresenceSerializer(serializers.ModelSerializer):
    """Serializer for board presence tracking"""

    user_name = serializers.CharField(source="user.name", read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = BoardPresence
        fields = ["id", "user", "user_id", "user_name", "editing_task", "last_seen", "channel_name"]
        read_only_fields = ["id", "last_seen"]


class PersonalNoteSerializer(serializers.ModelSerializer):
    """Serializer for personal notes - private user notes board"""

    owner_username = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = PersonalNote
        fields = ["id", "owner", "owner_username", "title", "content", "color", "is_pinned", "is_completed", "due_date", "order", "created_at", "updated_at"]
        read_only_fields = ["id", "owner", "owner_username", "created_at", "updated_at"]

    def validate_color(self, value):
        if value and not value.startswith("#"):
            value = f"#{value}"
        if value and len(value) not in [4, 7]:
            raise serializers.ValidationError("Color must be in format #RGB or #RRGGBB")
        return value


class TaskGroupSerializer(serializers.ModelSerializer):
    """Serializer for task groups"""

    created_by_username = serializers.CharField(source="created_by.username", read_only=True)
    member_ids = serializers.PrimaryKeyRelatedField(many=True, queryset=Employee.objects.all(), source="members", required=False)
    member_names = serializers.SerializerMethodField()
    task_count = serializers.SerializerMethodField()
    department_name = serializers.CharField(source="department.name", read_only=True, allow_null=True)

    class Meta:
        model = TaskGroup
        fields = [
            "id",
            "name",
            "description",
            "color",
            "icon",
            "created_by",
            "created_by_username",
            "members",
            "member_ids",
            "member_names",
            "is_private",
            "order",
            "task_count",
            "is_department_group",
            "department",
            "department_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_by_username", "member_names", "task_count", "is_department_group", "department", "department_name", "created_at", "updated_at"]

    def get_member_names(self, obj):
        # Use prefetched members if available to avoid N+1
        members = obj.members.all()  # will use prefetch cache if available
        return [{"id": m.id, "name": m.name, "emp_id": m.emp_id} for m in members]

    def get_task_count(self, obj):
        # Use annotated value from queryset if available
        if hasattr(obj, "_task_count"):
            return obj._task_count
        return obj.tasks.values("id").distinct().count()

    def validate_color(self, value):
        if value and not value.startswith("#"):
            value = f"#{value}"
        if value and len(value) not in [4, 7]:
            raise serializers.ValidationError("Color must be in format #RGB or #RRGGBB")
        return value


class TaskAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for task file attachments"""

    uploaded_by_name = serializers.CharField(source="uploaded_by.name", read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = TaskAttachment
        fields = ["id", "task", "file", "file_url", "filename", "file_size", "file_type", "uploaded_by", "uploaded_by_name", "description", "created_at", "updated_at"]
        read_only_fields = ["id", "file_url", "filename", "file_size", "file_type", "uploaded_by", "uploaded_by_name", "created_at", "updated_at"]

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class TaskReminderSerializer(serializers.ModelSerializer):
    """Serializer for task reminders/alerts"""

    user_username = serializers.CharField(source="user.username", read_only=True)
    task_title = serializers.CharField(source="task.title", read_only=True)
    task_due = serializers.DateTimeField(source="task.end", read_only=True)
    reminder_type_display = serializers.CharField(source="get_reminder_type_display", read_only=True)

    class Meta:
        model = TaskReminder
        fields = ["id", "task", "task_title", "task_due", "user", "user_username", "reminder_type", "reminder_type_display", "remind_at", "message", "is_triggered", "is_dismissed", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "user_username", "task_title", "task_due", "reminder_type_display", "created_at", "updated_at"]


class PurchaseRequestSerializer(serializers.ModelSerializer):
    """Serializer for purchase requests"""

    created_by_username = serializers.CharField(source="created_by.username", read_only=True, allow_null=True)
    owner_employee_name = serializers.CharField(source="owner_employee.name", read_only=True, allow_null=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = PurchaseRequest
        fields = [
            "id",
            "request_date",
            "owner",
            "created_by",
            "created_by_username",
            "owner_employee",
            "owner_employee_name",
            "doc_id",
            "part_no",
            "description_spec",
            "material_category",
            "purpose_desc",
            "qty",
            "plant",
            "project_code",
            "pr_type",
            "mrp_id",
            "purch_org",
            "sourcer_price",
            "pr_no",
            "remarks",
            "status",
            "status_display",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_by_username", "owner_employee_name", "status_display", "created_at", "updated_at"]


class AssetSerializer(serializers.ModelSerializer):
    """Serializer for assets"""

    created_by_username = serializers.CharField(source="created_by.username", read_only=True, allow_null=True)
    department_code = serializers.CharField(source="department.code", read_only=True, allow_null=True)
    department_name = serializers.CharField(source="department.name", read_only=True, allow_null=True)

    class Meta:
        model = Asset
        fields = [
            "id",
            "created_by",
            "created_by_username",
            "company_code",
            "asset_id",
            "fixed_asset_id",
            "is_fixed_asset",
            "is_customs_control",
            "part_number",
            "group_3",
            "product_name",
            "spec",
            "quantity",
            "receive_date",
            "status",
            "cost_center",
            "cost_center_name",
            "keeper_dept",
            "keeper_dept_name",
            "department",
            "department_code",
            "department_name",
            "keeper",
            "keeper_name",
            "group_1",
            "group_2",
            "storage",
            "location_code",
            "storage_desc",
            "consign",
            "vendor",
            "pr_no",
            "pr_sequence",
            "po_no",
            "po_sequence",
            "dn_no",
            "dn_sequence",
            "dn_date",
            "application_number",
            "sequence",
            "import_number",
            "picking_no",
            "picking_sequence",
            "picking_year",
            "picking_date",
            "chinese_product_name",
            "hs_code",
            "declaration_number",
            "declaration_date",
            "control_end_date",
            "outsource_number",
            "price",
            "currency",
            "local_price",
            "price_level",
            "sn",
            "is_qualified",
            "itc_end_date",
            "elec_declaration_number",
            "national_inspection_certification",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_by_username", "department_code", "department_name", "created_at", "updated_at"]


class AssetSummarySerializer(serializers.ModelSerializer):
    """Simplified serializer for asset lists"""

    created_by_username = serializers.CharField(source="created_by.username", read_only=True, allow_null=True)
    department_code = serializers.CharField(source="department.code", read_only=True, allow_null=True)

    class Meta:
        model = Asset
        fields = ["id", "created_by", "created_by_username", "asset_id", "part_number", "product_name", "spec", "quantity", "receive_date", "status", "cost_center", "keeper_dept", "department", "department_code", "keeper_name"]


# ---------------------------------------------------------------------------
# SMB Configuration
# ---------------------------------------------------------------------------


class SMBConfigurationSerializer(serializers.ModelSerializer):
    """
    SMB Configuration serializer.
    Never exposes the encrypted password. Accepts `new_password` write-only field.
    """

    new_password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    has_password = serializers.SerializerMethodField()

    class Meta:
        model = SMBConfiguration
        fields = [
            "id",
            "name",
            "server",
            "share_name",
            "username",
            "domain",
            "port",
            "path_prefix",
            "is_active",
            "new_password",
            "has_password",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_has_password(self, obj):
        return bool(obj._encrypted_password)

    def update(self, instance, validated_data):
        new_password = validated_data.pop("new_password", None)
        if new_password is not None and new_password != "":
            instance.set_password(new_password)
        return super().update(instance, validated_data)

    def create(self, validated_data):
        new_password = validated_data.pop("new_password", None)
        instance = super().create(validated_data)
        if new_password:
            instance.set_password(new_password)
            instance.save(update_fields=["_encrypted_password"])
        return instance


# ---------------------------------------------------------------------------
# User Reports (Bug reports & Feature requests)
# ---------------------------------------------------------------------------


class UserReportSerializer(serializers.ModelSerializer):
    reporter_name = serializers.CharField(source="reporter.name", read_only=True)
    reporter_username = serializers.CharField(source="reporter.username", read_only=True)
    reporter_worker_id = serializers.CharField(source="reporter.worker_id", read_only=True)
    reporter_email = serializers.EmailField(source="reporter.email", read_only=True)
    report_type_display = serializers.CharField(source="get_report_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)

    class Meta:
        model = UserReport
        fields = [
            "id",
            "reporter",
            "reporter_name",
            "reporter_username",
            "reporter_worker_id",
            "reporter_email",
            "report_type",
            "report_type_display",
            "title",
            "description",
            "page_url",
            "priority",
            "priority_display",
            "status",
            "status_display",
            "admin_notes",
            "resolved_in_version",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "reporter",
            "reporter_name",
            "reporter_username",
            "reporter_worker_id",
            "reporter_email",
            "created_at",
            "updated_at",
        ]


class UserReportAdminSerializer(UserReportSerializer):
    """Extended serializer for super admin — can update status & admin_notes."""

    class Meta(UserReportSerializer.Meta):
        read_only_fields = [
            "id",
            "reporter",
            "reporter_name",
            "reporter_username",
            "reporter_worker_id",
            "reporter_email",
            "report_type",
            "title",
            "description",
            "page_url",
            "created_at",
            "updated_at",
        ]


# ---------------------------------------------------------------------------
# Release Notes / Version History
# ---------------------------------------------------------------------------


class ReleaseNoteSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.name", read_only=True, allow_null=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = ReleaseNote
        fields = [
            "id",
            "version",
            "release_date",
            "status",
            "status_display",
            "summary",
            "new_features",
            "improvements",
            "bug_fixes",
            "breaking_changes",
            "security",
            "known_issues",
            "deprecations",
            "contributors",
            "published",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_by_name", "created_at", "updated_at"]
