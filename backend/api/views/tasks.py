import logging

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import (
    BoardPresence,
    CalendarEvent,
    Employee,
    ExternalUser,
    Notification,
    TaskActivity,
    TaskAttachment,
    TaskComment,
    TaskGroup,
    TaskReminder,
    TaskSubtask,
    TaskTimeLog,
)
from ..pagination import DynamicPagination
from ..serializers import (
    BoardPresenceSerializer,
    TaskActivitySerializer,
    TaskAttachmentSerializer,
    TaskCommentSerializer,
    TaskGroupSerializer,
    TaskReminderSerializer,
    TaskSubtaskSerializer,
    TaskTimeLogSerializer,
)
from .helpers import get_employee_for_user, is_developer_user, is_ptb_admin, is_superadmin_user  # noqa: F401

logger = logging.getLogger(__name__)
User = get_user_model()


class TaskCommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for task comments with threading and mentions support.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TaskCommentSerializer
    pagination_class = DynamicPagination

    def get_queryset(self):
        queryset = TaskComment.objects.select_related("author", "task").prefetch_related(
            "mentions",
            models.Prefetch(
                "replies",
                queryset=TaskComment.objects.select_related("author").prefetch_related("mentions"),
            ),
        )

        # Require task_id to prevent enumerating all comments
        task_id = self.request.query_params.get("task_id")
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        elif self.action == "list":
            return queryset.none()

        # Only return top-level comments by default (replies are nested)
        if self.request.query_params.get("top_level", "true").lower() == "true":
            queryset = queryset.filter(parent__isnull=True)

        return queryset

    def perform_create(self, serializer):
        # Get or create the employee for the current user
        employee = get_employee_for_user(self.request.user)

        comment = serializer.save(author=employee)

        # Create activity log for comment
        TaskActivity.objects.create(task=comment.task, actor=employee, action="comment_added", extra_data={"comment_id": comment.id, "preview": comment.content[:100]})

        # Create notifications for mentioned users
        mentioned_employees = comment.mentions.all()
        if mentioned_employees.exists():
            task = comment.task

            # Determine valid mention targets based on group or assigned_to
            if task.group_id:
                valid_employee_ids = set(task.group.members.values_list("id", flat=True))
            else:
                valid_employee_ids = set(task.assigned_to.values_list("id", flat=True))

            from ..consumers import send_notification_to_user

            eligible_mentions = [mentioned_emp for mentioned_emp in mentioned_employees if mentioned_emp.id in valid_employee_ids and mentioned_emp.id != employee.id]

            emp_ids = [m.emp_id for m in eligible_mentions if m.emp_id]
            ext_users = ExternalUser.objects.filter(worker_id__in=emp_ids, is_active=True)
            ext_user_map = {u.worker_id.lower(): u for u in ext_users if u.worker_id}

            # Build notification objects for bulk creation
            notification_data = []
            for mentioned_emp in eligible_mentions:
                worker_id = (mentioned_emp.emp_id or "").lower()
                ext_user = ext_user_map.get(worker_id)
                if not ext_user:
                    logger.warning("No ExternalUser found for employee %s (emp_id=%s)", mentioned_emp.name, mentioned_emp.emp_id)
                    continue
                notification_data.append(
                    (
                        ext_user,
                        Notification(
                            recipient=ext_user,
                            title="You were mentioned in a comment",
                            message=f'{employee.name} mentioned you in a comment on "{task.title}"',
                            event=task,
                            event_type="task_mention",
                        ),
                    )
                )

            if notification_data:
                created_notifications = Notification.objects.bulk_create([n for _, n in notification_data])
                for (ext_user, _), notif in zip(notification_data, created_notifications, strict=True):
                    send_notification_to_user(
                        ext_user.id,
                        {
                            "id": notif.id,
                            "title": notif.title,
                            "message": notif.message,
                            "event_type": "task_mention",
                            "event_id": task.id,
                            "is_read": False,
                            "created_at": notif.created_at.isoformat(),
                        },
                    )

        return comment

    def perform_update(self, serializer):
        comment = self.get_object()
        employee = get_employee_for_user(self.request.user)
        if comment.author_id != employee.id:
            raise PermissionDenied("You can only edit your own comments.")
        serializer.save(is_edited=True, edited_at=timezone.now())

    def perform_destroy(self, instance):
        employee = get_employee_for_user(self.request.user)
        # Only the comment author or a PTB admin can delete comments
        if instance.author_id != employee.id and not getattr(self.request.user, "is_ptb_admin", False):
            raise PermissionDenied("You can only delete your own comments.")
        instance.delete()

    @action(detail=True, methods=["get"])
    def replies(self, request, pk=None):
        """Get all replies for a comment"""
        comment = self.get_object()
        replies = comment.replies.all()
        serializer = self.get_serializer(replies, many=True)
        return Response(serializer.data)


class TaskActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for task activity logs.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TaskActivitySerializer
    pagination_class = DynamicPagination

    def get_queryset(self):
        queryset = TaskActivity.objects.select_related("actor", "task").all()

        # Require task_id to prevent enumerating all activities
        task_id = self.request.query_params.get("task_id")
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        elif self.action == "list":
            return queryset.none()

        # Limit results for performance (cap at 200)
        limit = self.request.query_params.get("limit", 50)
        try:
            limit = min(int(limit), 200)
        except ValueError:
            limit = 50

        # Use proper filtering instead of slicing to keep queryset operations safe
        pks = list(queryset.order_by("-created_at").values_list("pk", flat=True)[:limit])
        return queryset.filter(pk__in=pks).order_by("-created_at")


class TaskSubtaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for task subtasks/checklist items.
    Restricted to users who are the creator or an assignee of the parent task.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TaskSubtaskSerializer
    pagination_class = DynamicPagination

    def _check_task_membership(self, task):
        """Verify the current user is the creator, an assignee, or a PTB admin of the task."""
        if getattr(self.request.user, "is_ptb_admin", False):
            return
        employee = get_employee_for_user(self.request.user)
        is_creator = task.created_by_id == employee.id
        is_assigned = task.assigned_to.filter(id=employee.id).exists() if hasattr(task.assigned_to, "filter") else False
        if not is_creator and not is_assigned:
            raise PermissionDenied("You can only manage subtasks on tasks you created or are assigned to.")

    def get_queryset(self):
        queryset = TaskSubtask.objects.select_related("task", "created_by", "completed_by")

        # Filter by task if specified
        task_id = self.request.query_params.get("task_id")
        if task_id:
            queryset = queryset.filter(task_id=task_id)

        return queryset.order_by("order", "created_at")

    def perform_create(self, serializer):
        employee = get_employee_for_user(self.request.user)
        task = serializer.validated_data.get("task")
        if task:
            self._check_task_membership(task)

        subtask = serializer.save(created_by=employee)

        # Create activity log
        TaskActivity.objects.create(task=subtask.task, actor=employee, action="updated", extra_data={"type": "subtask_added", "subtask_title": subtask.title})

        return subtask

    def perform_destroy(self, instance):
        employee = get_employee_for_user(self.request.user, raise_if_not_found=False)

        if employee:
            TaskActivity.objects.create(task=instance.task, actor=employee, action="updated", extra_data={"type": "subtask_removed", "subtask_title": instance.title})

        instance.delete()

    @action(detail=True, methods=["post"])
    def toggle(self, request, pk=None):
        """Toggle subtask completion status"""
        subtask = self.get_object()
        employee = get_employee_for_user(request.user, raise_if_not_found=False)

        is_completed = subtask.toggle_complete(employee)

        # Create activity log
        if employee:
            TaskActivity.objects.create(task=subtask.task, actor=employee, action="updated", extra_data={"type": "subtask_toggled", "subtask_title": subtask.title, "is_completed": is_completed})

        serializer = self.get_serializer(subtask)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def reorder(self, request):
        """Reorder subtasks within a task"""
        task_id = request.data.get("task_id")
        subtask_ids = request.data.get("subtask_ids", [])

        if not task_id or not subtask_ids:
            return Response({"detail": "task_id and subtask_ids required"}, status=400)

        # Bulk update order using Case/When (single query instead of N queries)
        from django.db.models import Case, IntegerField, Value, When

        cases = [When(id=sid, then=Value(idx)) for idx, sid in enumerate(subtask_ids)]
        TaskSubtask.objects.filter(id__in=subtask_ids, task_id=task_id).update(order=Case(*cases, output_field=IntegerField()))

        # Return updated subtasks
        subtasks = TaskSubtask.objects.filter(task_id=task_id).order_by("order")
        serializer = self.get_serializer(subtasks, many=True)
        return Response(serializer.data)


class TaskTimeLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet for task time logs and timer functionality.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TaskTimeLogSerializer
    pagination_class = DynamicPagination

    def get_queryset(self):
        queryset = TaskTimeLog.objects.select_related("task", "employee")

        # Filter by task if specified
        task_id = self.request.query_params.get("task_id")
        if task_id:
            queryset = queryset.filter(task_id=task_id)

        # Filter by employee if specified
        employee_id = self.request.query_params.get("employee_id")
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)

        return queryset.order_by("-started_at")

    def perform_create(self, serializer):
        employee = get_employee_for_user(self.request.user)

        # Stop any running timers for this employee first (use stop_timer for proper duration calc)
        running_timers = TaskTimeLog.objects.filter(employee=employee, is_running=True)
        for timer in running_timers:
            timer.stop_timer()

        time_log = serializer.save(employee=employee)

        # Create activity log
        TaskActivity.objects.create(task=time_log.task, actor=employee, action="updated", extra_data={"type": "time_logged", "duration": time_log.duration_minutes})

        return time_log

    def perform_destroy(self, instance):
        employee = get_employee_for_user(self.request.user)
        # Only the time log owner or a PTB admin can delete entries
        if instance.employee_id != employee.id and not getattr(self.request.user, "is_ptb_admin", False):
            raise PermissionDenied("You can only delete your own time entries.")
        instance.delete()

    @action(detail=False, methods=["post"])
    def start_timer(self, request):
        """Start a new timer for a task"""
        task_id = request.data.get("task_id")
        description = request.data.get("description", "")

        if not task_id:
            return Response({"detail": "task_id required"}, status=400)

        employee = get_employee_for_user(request.user)

        # Stop any existing running timer for this user
        existing_running = TaskTimeLog.objects.filter(employee=employee, is_running=True).first()
        if existing_running:
            existing_running.stop_timer()

        # Create new timer
        time_log = TaskTimeLog.objects.create(task_id=task_id, employee=employee, description=description, started_at=timezone.now(), is_running=True)

        serializer = self.get_serializer(time_log)
        return Response(serializer.data, status=201)

    @action(detail=True, methods=["post"])
    def stop_timer(self, request, pk=None):
        """Stop a running timer"""
        time_log = self.get_object()

        if not time_log.is_running:
            return Response({"detail": "Timer is not running"}, status=400)

        time_log.stop_timer()

        # Create activity log
        employee = get_employee_for_user(request.user, raise_if_not_found=False)
        if employee:
            TaskActivity.objects.create(task=time_log.task, actor=employee, action="updated", extra_data={"type": "time_logged", "duration": time_log.duration_minutes})

        serializer = self.get_serializer(time_log)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def active(self, request):
        """Get currently running timer for the user"""
        employee = get_employee_for_user(request.user, raise_if_not_found=False)

        if not employee:
            return Response(None)

        running = TaskTimeLog.objects.filter(employee=employee, is_running=True).first()
        if running:
            serializer = self.get_serializer(running)
            return Response(serializer.data)
        return Response(None)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Get time summary for a task"""
        task_id = request.query_params.get("task_id")

        if not task_id:
            return Response({"detail": "task_id required"}, status=400)

        from django.db.models import Sum

        logs = TaskTimeLog.objects.filter(task_id=task_id)
        total_minutes = logs.aggregate(total=Sum("duration_minutes"))["total"] or 0

        # Get task estimated hours
        try:
            task = CalendarEvent.objects.get(id=task_id)
            estimated_hours = float(task.estimated_hours or 0)
        except CalendarEvent.DoesNotExist:
            estimated_hours = 0

        return Response({"task_id": task_id, "total_minutes": total_minutes, "total_hours": round(total_minutes / 60, 2), "estimated_hours": estimated_hours, "log_count": logs.count()})


class BoardPresenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for tracking board presence (who's viewing/editing).
    """

    permission_classes = [IsAuthenticated]
    serializer_class = BoardPresenceSerializer

    def get_queryset(self):
        # Only return presence records from last 5 minutes
        from datetime import timedelta

        cutoff = timezone.now() - timedelta(minutes=5)
        return BoardPresence.objects.filter(last_seen__gte=cutoff).select_related("user", "editing_task")

    @action(detail=False, methods=["post"])
    def heartbeat(self, request):
        """
        Update presence heartbeat. Called periodically by clients.
        """
        employee = get_employee_for_user(request.user, raise_if_not_found=False)

        if not employee:
            return Response({"detail": "Employee not found"}, status=status.HTTP_400_BAD_REQUEST)

        editing_task_id = request.data.get("editing_task_id")
        channel_name = request.data.get("channel_name", "")

        # Update or create presence record
        presence, created = BoardPresence.objects.update_or_create(user=employee, defaults={"editing_task_id": editing_task_id, "channel_name": channel_name})

        # Get all current viewers (excluding self)
        from datetime import timedelta

        cutoff = timezone.now() - timedelta(minutes=5)
        viewers = BoardPresence.objects.filter(last_seen__gte=cutoff).exclude(user=employee).select_related("user", "editing_task")

        serializer = self.get_serializer(viewers, many=True)
        return Response({"status": "ok", "viewers": serializer.data})

    @action(detail=False, methods=["post"])
    def leave(self, request):
        """
        Called when user leaves the board.
        """
        employee = get_employee_for_user(request.user, raise_if_not_found=False)

        if employee:
            BoardPresence.objects.filter(user=employee).delete()

        return Response({"status": "ok"})


class TaskGroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet for task groups (folders/categories for organizing tasks).
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TaskGroupSerializer
    pagination_class = DynamicPagination

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return TaskGroup.objects.none()
        user = self.request.user
        if not user or not user.is_authenticated:
            return TaskGroup.objects.none()
        # User can see groups they created or groups they are a member of (if not private)
        worker_id = getattr(user, "worker_id", None)
        employee = None
        if worker_id:
            employee = Employee.objects.filter(emp_id=worker_id).first()

        base_qs = TaskGroup.objects.select_related("created_by", "department").prefetch_related("members").annotate(_task_count=models.Count("tasks"))

        if employee:
            return base_qs.filter(models.Q(created_by=user) | models.Q(is_private=False) | models.Q(members=employee)).distinct().order_by("order", "name")
        else:
            return base_qs.filter(models.Q(created_by=user) | models.Q(is_private=False)).distinct().order_by("order", "name")

    def perform_create(self, serializer):
        max_order = TaskGroup.objects.filter(created_by=self.request.user).aggregate(max_order=models.Max("order"))["max_order"] or 0
        instance = serializer.save(created_by=self.request.user, order=max_order + 1)
        # Notify members that they were added to the new group
        self._notify_group_members(instance, list(instance.members.all()))

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.is_department_group:
            raise PermissionDenied("Department groups cannot be edited. Use 'Sync Departments' to update them.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.is_department_group:
            raise PermissionDenied("Department groups cannot be deleted.")
        instance.delete()

    def _notify_group_members(self, group, members):
        """Notify employees that they were added to a task group."""
        from ..signals import send_websocket_notification

        emp_ids = [e.emp_id for e in members if e.emp_id]
        if not emp_ids:
            return

        user_map = {}
        for eu in ExternalUser.objects.filter(worker_id__in=emp_ids):
            user_map[eu.worker_id.lower()] = eu

        creator = self.request.user
        creator_name = getattr(creator, "username", str(creator))

        notifs_to_create = []
        ws_payloads = []
        for member in members:
            if not member.emp_id:
                continue
            external_user = user_map.get(member.emp_id.lower())
            if not external_user:
                continue
            # Don't notify the creator themselves
            if external_user.id == creator.id:
                continue

            title = f"Added to Group: {group.name}"
            message = f"{creator_name} added you as a member of the group '{group.name}'."

            notifs_to_create.append(
                Notification(
                    recipient=external_user,
                    title=title,
                    message=message,
                    event_type="task_group",
                )
            )
            ws_payloads.append(
                (
                    external_user.id,
                    {
                        "title": title,
                        "message": message,
                        "event_type": "task_group",
                        "is_read": False,
                    },
                )
            )

        if notifs_to_create:
            try:
                created = Notification.objects.bulk_create(notifs_to_create)
                for notif, (uid, payload) in zip(created, ws_payloads, strict=True):
                    payload["id"] = notif.id
                    payload["created_at"] = notif.created_at.isoformat()
                    send_websocket_notification(uid, payload)
            except Exception as e:
                logger.error("Error creating group member notifications: %s", e)

    @action(detail=True, methods=["post"])
    def add_member(self, request, pk=None):
        """Add a member to the group. Only the group creator or admin can modify membership."""
        group = self.get_object()
        if group.created_by != request.user and not getattr(request.user, "is_ptb_admin", False):
            raise PermissionDenied("Only the group creator or an admin can modify membership.")
        employee_id = request.data.get("employee_id")

        if not employee_id:
            return Response({"detail": "employee_id required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            employee = Employee.objects.get(id=employee_id)
            group.members.add(employee)
            # Notify the newly added member
            self._notify_group_members(group, [employee])
            return Response(self.get_serializer(group).data)
        except Employee.DoesNotExist:
            return Response({"detail": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"])
    def remove_member(self, request, pk=None):
        """Remove a member from the group. Only the group creator or admin can modify membership."""
        group = self.get_object()
        if group.created_by != request.user and not getattr(request.user, "is_ptb_admin", False):
            raise PermissionDenied("Only the group creator or an admin can modify membership.")
        employee_id = request.data.get("employee_id")

        if not employee_id:
            return Response({"detail": "employee_id required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            employee = Employee.objects.get(id=employee_id)
            group.members.remove(employee)
            return Response(self.get_serializer(group).data)
        except Employee.DoesNotExist:
            return Response({"detail": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["post"])
    def reorder(self, request):
        """Reorder groups. Expects: { "order": [id1, id2, id3, ...] }"""
        order_list = request.data.get("order", [])

        if order_list:
            from django.db.models import Case, IntegerField, Value, When

            cases = [When(id=gid, then=Value(idx)) for idx, gid in enumerate(order_list)]
            TaskGroup.objects.filter(id__in=order_list, created_by=request.user).update(order=Case(*cases, output_field=IntegerField()))

        return Response({"status": "ok"})

    @action(detail=False, methods=["post"])
    def sync_departments(self, request):
        """
        Create or update groups for each department with their employees as members.
        Uses department code/name as the group name.
        Admin-only action.
        """
        if not (getattr(request.user, "is_ptb_admin", False) or is_superadmin_user(request.user)):
            raise PermissionDenied("Only administrators can sync department groups.")

        from ..models import Department

        # Define colors for departments (cycling through a palette)
        colors = [
            "#3B82F6",  # Blue
            "#10B981",  # Emerald
            "#F59E0B",  # Amber
            "#EF4444",  # Red
            "#8B5CF6",  # Violet
            "#EC4899",  # Pink
            "#06B6D4",  # Cyan
            "#84CC16",  # Lime
            "#F97316",  # Orange
            "#6366F1",  # Indigo
        ]

        departments = Department.objects.prefetch_related("employees").all()
        created_count = 0
        updated_count = 0

        for idx, dept in enumerate(departments):
            # Check if a department group already exists
            existing_group = TaskGroup.objects.filter(is_department_group=True, department=dept).first()

            # Get all employee IDs for this department
            employee_ids = [employee.id for employee in dept.employees.all()]

            if existing_group:
                # Update existing group's members and name (use dept code)
                existing_group.name = dept.code
                existing_group.save(update_fields=["name"])
                existing_group.members.set(employee_ids)
                updated_count += 1
            else:
                # Create new department group
                color = colors[idx % len(colors)]
                group = TaskGroup.objects.create(name=dept.code, description=f"Default group for {dept.name} department", color=color, created_by=request.user, is_department_group=True, department=dept, is_private=False, order=idx)
                group.members.set(employee_ids)
                created_count += 1

        return Response({"status": "ok", "created": created_count, "updated": updated_count})


class TaskAttachmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for task attachments (files attached to tasks).
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TaskAttachmentSerializer
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = DynamicPagination

    def get_queryset(self):
        queryset = TaskAttachment.objects.select_related("task", "uploaded_by")

        # Filter by task if provided
        task_id = self.request.query_params.get("task_id")
        if task_id:
            queryset = queryset.filter(task_id=task_id)

        return queryset.order_by("-created_at")

    # 10 MB upload limit
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024
    ALLOWED_CONTENT_TYPES = {
        # Documents
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        # Text
        "text/plain",
        "text/csv",
        "text/xml",
        "application/json",
        "application/xml",
        # Archives
        "application/zip",
        "application/x-rar-compressed",
        "application/x-7z-compressed",
        "application/gzip",
        # Images
        "image/png",
        "image/jpeg",
        "image/gif",
        "image/svg+xml",
        "image/webp",
        "image/bmp",
    }

    def perform_create(self, serializer):
        user = self.request.user
        worker_id = getattr(user, "worker_id", None)
        employee = None
        if worker_id:
            # Note: Employee model uses emp_id field, not worker_id
            employee = Employee.objects.filter(emp_id=worker_id).first()

        # Get file info
        file = self.request.FILES.get("file")
        if file:
            # Validate file size
            if file.size > self.MAX_UPLOAD_SIZE:
                raise serializers.ValidationError({"file": f"File size exceeds {self.MAX_UPLOAD_SIZE // (1024 * 1024)} MB limit."})
            # Validate content type
            if file.content_type and file.content_type not in self.ALLOWED_CONTENT_TYPES:
                raise serializers.ValidationError({"file": f'File type "{file.content_type}" is not allowed.'})
            serializer.save(uploaded_by=employee, filename=file.name, file_size=file.size, file_type=file.content_type or "")
        else:
            serializer.save(uploaded_by=employee)

    def perform_destroy(self, instance):
        employee = get_employee_for_user(self.request.user, raise_if_not_found=False)
        # Only the uploader or a PTB admin can delete attachments
        is_admin = getattr(self.request.user, "is_ptb_admin", False)
        if employee and instance.uploaded_by_id != employee.id and not is_admin:
            raise PermissionDenied("You can only delete your own attachments.")
        instance.delete()

    @action(detail=False, methods=["get"])
    def by_task(self, request):
        """Get all attachments for a specific task."""
        task_id = request.query_params.get("task_id")
        if not task_id:
            return Response({"detail": "task_id required"}, status=status.HTTP_400_BAD_REQUEST)

        attachments = self.get_queryset().filter(task_id=task_id)
        serializer = self.get_serializer(attachments, many=True)
        return Response(serializer.data)


class TaskReminderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for task reminders/alerts.
    Users can only see and manage their own reminders.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TaskReminderSerializer
    pagination_class = DynamicPagination

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return TaskReminder.objects.none()
        if not getattr(self.request, "user", None) or not self.request.user.is_authenticated:
            return TaskReminder.objects.none()
        return TaskReminder.objects.filter(user=self.request.user).select_related("task").order_by("remind_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"])
    def pending(self, request):
        """Get pending (not triggered and not dismissed) reminders."""
        reminders = self.get_queryset().filter(is_triggered=False, is_dismissed=False, remind_at__gte=timezone.now())
        serializer = self.get_serializer(reminders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def due(self, request):
        """Get reminders that are due (remind_at <= now and not yet triggered)."""
        reminders = self.get_queryset().filter(is_triggered=False, is_dismissed=False, remind_at__lte=timezone.now())
        serializer = self.get_serializer(reminders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def trigger(self, request, pk=None):
        """Mark a reminder as triggered."""
        reminder = self.get_object()
        reminder.is_triggered = True
        reminder.save(update_fields=["is_triggered"])
        return Response(self.get_serializer(reminder).data)

    @action(detail=True, methods=["post"])
    def dismiss(self, request, pk=None):
        """Dismiss a reminder."""
        reminder = self.get_object()
        reminder.is_dismissed = True
        reminder.save(update_fields=["is_dismissed"])
        return Response(self.get_serializer(reminder).data)

    @action(detail=False, methods=["get"])
    def by_task(self, request):
        """Get all reminders for a specific task."""
        task_id = request.query_params.get("task_id")
        if not task_id:
            return Response({"detail": "task_id required"}, status=status.HTTP_400_BAD_REQUEST)

        reminders = self.get_queryset().filter(task_id=task_id)
        serializer = self.get_serializer(reminders, many=True)
        return Response(serializer.data)
