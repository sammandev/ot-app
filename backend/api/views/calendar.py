import logging
import traceback

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.dateparse import parse_datetime
from rest_framework import status, viewsets
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import (
    CalendarEvent,
    Employee,
)
from ..pagination import CalendarEventPagination
from ..permissions import ResourcePermission
from ..serializers import (
    CalendarEventSerializer,
)
from .helpers import get_employee_for_user, is_developer_user, is_ptb_admin, is_superadmin_user  # noqa: F401

logger = logging.getLogger(__name__)
User = get_user_model()


def generate_recurring_events(parent_event, assigned_to_ids=None):
    """
    Generate recurring event instances based on the parent event's repeat_frequency.
    - hourly: 24 hours from start
    - daily: 1 year from start
    - weekly: 1 year from start
    - monthly: 1 year from start
    - yearly: next 5 years
    """
    from datetime import timedelta

    from dateutil.relativedelta import relativedelta

    if not parent_event.is_repeating or not parent_event.repeat_frequency:
        return []

    frequency = parent_event.repeat_frequency
    start = parent_event.start
    end = parent_event.end
    duration = end - start  # Duration of each event

    # Calculate 1 year from start date for daily, weekly, monthly recurrence
    one_year_from_start = start + relativedelta(years=1)

    child_events = []
    current_start = start

    if frequency == "hourly":
        # Generate for 24 hours from start
        end_time = start + timedelta(hours=24)
        current_start = start + timedelta(hours=1)
        while current_start < end_time:
            child_events.append(
                {
                    "start": current_start,
                    "end": current_start + duration,
                }
            )
            current_start += timedelta(hours=1)

    elif frequency == "daily":
        # Generate for 1 year from start
        current_start = start + timedelta(days=1)
        while current_start <= one_year_from_start:
            child_events.append(
                {
                    "start": current_start,
                    "end": current_start + duration,
                }
            )
            current_start += timedelta(days=1)

    elif frequency == "weekly":
        # Generate for 1 year from start
        current_start = start + timedelta(weeks=1)
        while current_start <= one_year_from_start:
            child_events.append(
                {
                    "start": current_start,
                    "end": current_start + duration,
                }
            )
            current_start += timedelta(weeks=1)

    elif frequency == "monthly":
        # Generate for 1 year from start
        current_start = start + relativedelta(months=1)
        while current_start <= one_year_from_start:
            child_events.append(
                {
                    "start": current_start,
                    "end": current_start + duration,
                }
            )
            current_start += relativedelta(months=1)

    elif frequency == "yearly":
        # Generate for next 5 years
        for i in range(1, 6):
            current_start = start + relativedelta(years=i)
            child_events.append(
                {
                    "start": current_start,
                    "end": current_start + duration,
                }
            )

    # Create child events in database using bulk_create for performance
    events_to_create = []
    for event_data in child_events:
        events_to_create.append(
            CalendarEvent(
                title=parent_event.title,
                event_type=parent_event.event_type,
                status=parent_event.status,
                description=parent_event.description,
                start=event_data["start"],
                end=event_data["end"],
                all_day=parent_event.all_day,
                location=parent_event.location,
                color=parent_event.color,
                is_repeating=False,  # Child events are not repeating themselves
                repeat_frequency=None,
                parent_event=parent_event,
                created_by=parent_event.created_by,
                meeting_url=parent_event.meeting_url,
                project=parent_event.project,
                leave_type=parent_event.leave_type,
                applied_by=parent_event.applied_by,
                agent=parent_event.agent,
            )
        )

    created_events = CalendarEvent.objects.bulk_create(events_to_create, batch_size=100)

    # Set assigned_to for all created events in bulk
    if assigned_to_ids and created_events:
        through_model = CalendarEvent.assigned_to.through
        through_objects = []
        for event in created_events:
            for emp_id in assigned_to_ids:
                through_objects.append(through_model(calendarevent_id=event.id, employee_id=emp_id))
        if through_objects:
            through_model.objects.bulk_create(through_objects, batch_size=500)

    logger.info("Generated %s recurring events for parent event %s", len(created_events), parent_event.id)
    return created_events


def update_recurring_child_events(parent_event, update_data, assigned_to_ids=None):
    """
    Update all child events when parent is updated.
    Propagates time changes relative to original.
    Uses bulk_update for efficiency instead of saving one-by-one.
    """
    child_events = list(parent_event.child_events.all())

    if not child_events:
        return

    # Fields to propagate to children
    propagate_fields = ["title", "event_type", "status", "description", "all_day", "location", "color", "meeting_url", "project", "leave_type", "applied_by", "agent"]

    # Calculate time shift if start/end changed
    time_shift = None
    if "start" in update_data or "end" in update_data:
        # Get the original times before update
        original_start = parent_event.start
        new_start = update_data.get("start", original_start)
        if isinstance(new_start, str):
            new_start = parse_datetime(new_start)
        time_shift = new_start - original_start

    # Collect fields that actually changed for bulk_update
    update_fields = []
    if time_shift:
        update_fields.extend(["start", "end"])
    for field in propagate_fields:
        if field in update_data:
            update_fields.append(field)

    for child in child_events:
        # Update time if shifted
        if time_shift:
            child.start = child.start + time_shift
            child.end = child.end + time_shift

        # Update propagate fields
        for field in propagate_fields:
            if field in update_data:
                setattr(child, field, update_data[field])

    # Bulk update all children at once instead of individual saves
    if update_fields:
        from ..models import CalendarEvent

        CalendarEvent.objects.bulk_update(child_events, update_fields, batch_size=100)

    # Update assigned_to if provided (M2M requires per-object set)
    if assigned_to_ids is not None:
        for child in child_events:
            child.assigned_to.set(assigned_to_ids)

    logger.info("Updated %s child events for parent event %s", len(child_events), parent_event.id)


def create_event_notification(event, notification_type="created"):
    """
    Create notifications for event participants.
    Excludes PTB admins from receiving task notifications - they only get leave notifications.
    For leave events, also notifies agents and PTB admins.
    For group tasks, also notifies group members who aren't directly assigned.
    """
    from ..models import ExternalUser, Notification
    from ..signals import notify_leave_event_participants, send_websocket_notification

    notifications = []

    # Handle leave events specially - notify agents and PTB admins
    if event.event_type == "leave":
        is_update = notification_type == "updated"
        leave_notifications = notify_leave_event_participants(event, is_update=is_update)
        if leave_notifications:
            notifications.extend(leave_notifications)
        return notifications

    # Get all assigned employees and find their ExternalUser accounts
    assigned_employees = list(event.assigned_to.all())

    # Batch lookup: fetch all matching ExternalUsers in one query instead of N+1
    emp_ids = [e.emp_id for e in assigned_employees if e.emp_id]
    user_map = {}
    if emp_ids:
        for eu in ExternalUser.objects.filter(worker_id__in=emp_ids):
            user_map[eu.worker_id.lower()] = eu

    # Track which employee IDs already got notified (to avoid duplicates with group members)
    notified_user_ids = set()

    # Check if this task belongs to a group
    group = getattr(event, "group", None)
    group_name = group.name if group else None

    notifs_to_create = []
    ws_payloads = []
    for employee in assigned_employees:
        if not employee.emp_id:
            continue

        external_user = user_map.get(employee.emp_id.lower())
        if not external_user:
            logger.debug("No ExternalUser found for employee %s", employee.emp_id)
            continue

        # Skip PTB admins - they shouldn't receive task notifications
        if external_user.is_ptb_admin:
            logger.debug("Skipping notification for PTB admin %s", employee.emp_id)
            continue

        notified_user_ids.add(external_user.id)

        if notification_type == "created":
            title = f"New {event.event_type.title()}: {event.title}"
            if group_name:
                message = f"You have been assigned to a new {event.event_type} '{event.title}' for group '{group_name}' on {event.start.strftime('%Y-%m-%d %H:%M')}."
            else:
                message = f"You have been assigned to a new {event.event_type} '{event.title}' on {event.start.strftime('%Y-%m-%d %H:%M')}."
        elif notification_type == "updated":
            title = f"{event.event_type.title()} Updated: {event.title}"
            message = f"The {event.event_type} '{event.title}' has been updated."
        elif notification_type == "deleted":
            title = f"{event.event_type.title()} Deleted: {event.title}"
            message = f"The {event.event_type} '{event.title}' has been cancelled."
        else:
            continue

        notifs_to_create.append(
            Notification(
                recipient=external_user,
                title=title,
                message=message,
                event=event if notification_type != "deleted" else None,
                event_type=event.event_type,
            )
        )
        ws_payloads.append(
            (
                external_user.id,
                {
                    "title": title,
                    "message": message,
                    "event_type": event.event_type,
                    "event_id": event.id if notification_type != "deleted" else None,
                    "is_read": False,
                },
            )
        )

    # Notify group members who are NOT already assigned (only for task creation)
    if group and notification_type == "created" and event.event_type == "task":
        group_members = list(group.members.all())
        group_emp_ids = [e.emp_id for e in group_members if e.emp_id]
        group_user_map = {}
        if group_emp_ids:
            for eu in ExternalUser.objects.filter(worker_id__in=group_emp_ids):
                group_user_map[eu.worker_id.lower()] = eu

        for member in group_members:
            if not member.emp_id:
                continue
            external_user = group_user_map.get(member.emp_id.lower())
            if not external_user:
                continue
            # Skip if already notified as an assignee
            if external_user.id in notified_user_ids:
                continue
            # Skip PTB admins
            if external_user.is_ptb_admin:
                continue
            notified_user_ids.add(external_user.id)

            title = f"New Group Task: {event.title}"
            message = f"A new task '{event.title}' has been created for your group '{group_name}' on {event.start.strftime('%Y-%m-%d %H:%M')}."

            notifs_to_create.append(
                Notification(
                    recipient=external_user,
                    title=title,
                    message=message,
                    event=event,
                    event_type="task",
                )
            )
            ws_payloads.append(
                (
                    external_user.id,
                    {
                        "title": title,
                        "message": message,
                        "event_type": "task",
                        "event_id": event.id,
                        "is_read": False,
                    },
                )
            )

    if notifs_to_create:
        try:
            created = Notification.objects.bulk_create(notifs_to_create)
            notifications.extend(created)
            for notif, (uid, payload) in zip(created, ws_payloads, strict=True):
                payload["id"] = notif.id
                payload["created_at"] = notif.created_at.isoformat()
                send_websocket_notification(uid, payload)
        except Exception as e:
            logger.error("Error bulk creating notifications for event %s: %s", event.id, e)

    logger.info("Created %s notifications for event %s", len(notifications), event.id)
    return notifications


class CalendarEventViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ResourcePermission]
    resource_name = "calendar"
    queryset = CalendarEvent.objects.all()
    serializer_class = CalendarEventSerializer
    pagination_class = CalendarEventPagination
    ordering_fields = ["id", "start", "end", "created_at"]
    ordering = ["-start"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return CalendarEvent.objects.none()
        if not self.request.user.is_authenticated:
            return CalendarEvent.objects.none()

        queryset = (
            CalendarEvent.objects.select_related(
                "created_by",
                "project",
                "group",
                "applied_by",
                "agent",
            )
            .prefetch_related(
                "assigned_to",
            )
            .annotate(
                _subtask_count=models.Count("subtasks"),
                _subtask_completed=models.Count("subtasks", filter=models.Q(subtasks__is_completed=True)),
            )
        )

        # Filter by event_type if provided (for separating calendar and task board data)
        event_type = self.request.query_params.get("event_type")
        if event_type:
            queryset = queryset.filter(event_type=event_type)

        # Filter to user's own events + holidays (for reminders)
        my_events = self.request.query_params.get("my_events")
        if my_events and my_events.lower() == "true":
            user = self.request.user
            worker_id = getattr(user, "worker_id", None)
            if worker_id:
                # Use subquery to avoid JOIN + DISTINCT overhead on M2M
                from django.db.models import Exists, OuterRef

                assigned_subquery = CalendarEvent.assigned_to.through.objects.filter(
                    calendarevent_id=OuterRef("pk"),
                    employee__emp_id=worker_id,
                )
                queryset = queryset.filter(models.Q(created_by__emp_id=worker_id) | Exists(assigned_subquery) | models.Q(event_type="holiday"))
            else:
                queryset = queryset.filter(event_type="holiday")

        return queryset

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())

            # Use pagination instead of returning all events at once
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except APIException:
            raise
        except Exception as e:
            logger.error("CalendarEvent list error: %s", e)
            logger.error("Traceback: %s", traceback.format_exc())
            return Response({"detail": "An unexpected error occurred. Please try again or contact support."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            # Explicitly support partial updates for PATCH
            partial = kwargs.pop("partial", request.method.upper() == "PATCH")
            instance = self.get_object()
            logger.info("CalendarEvent update - ID: %s, Data: %s", instance.id, request.data)

            # Check if this is a parent repeating event
            is_parent_repeating = instance.is_repeating and instance.parent_event is None

            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            if serializer.is_valid():
                self.perform_update(serializer)

                # If parent repeating event, update all children
                if is_parent_repeating:
                    assigned_to_ids = request.data.get("assigned_to", None)
                    update_recurring_child_events(instance, request.data, assigned_to_ids)

                # Create notification for update
                create_event_notification(instance, "updated")

                # Broadcast to task board if this is a task
                if instance.event_type == "task":
                    try:
                        from ..consumers import broadcast_task_updated

                        broadcast_task_updated(serializer.data, request.user.username)
                    except Exception as ws_error:
                        logger.debug("WebSocket broadcast failed (non-critical): %s", ws_error)

                logger.info("CalendarEvent %s updated successfully", instance.id)
                return Response(serializer.data)
            logger.warning("CalendarEvent update validation failed: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except APIException:
            raise
        except Exception as e:
            logger.error("CalendarEvent update error: %s", e)
            logger.error("Traceback: %s", traceback.format_exc())
            logger.error("Request data: %s", request.data)
            return Response({"detail": "An unexpected error occurred. Please try again or contact support."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            task_id = instance.id
            event_type = instance.event_type
            logger.info("CalendarEvent delete - ID: %s", task_id)

            # No notification for deleted events per user request

            # If this is a parent event, child events will be deleted by CASCADE
            self.perform_destroy(instance)

            # Broadcast to task board if this was a task
            if event_type == "task":
                try:
                    from ..consumers import broadcast_task_deleted

                    broadcast_task_deleted(task_id, request.user.username)
                except Exception as ws_error:
                    logger.debug("WebSocket broadcast failed (non-critical): %s", ws_error)

            logger.info("CalendarEvent %s deleted successfully", task_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except APIException:
            raise
        except Exception as e:
            logger.error("CalendarEvent delete error: %s", e)
            logger.error("Traceback: %s", traceback.format_exc())
            return Response({"detail": "An unexpected error occurred. Please try again or contact support."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        # Auto-set created_by to the current user's Employee record if not provided
        if not serializer.validated_data.get("created_by"):
            user = self.request.user
            worker_id = getattr(user, "worker_id", None)
            if worker_id:
                employee = Employee.objects.filter(emp_id=worker_id).first()
                if employee:
                    serializer.save(created_by=employee)
                    return
        return super().perform_create(serializer)

    def perform_update(self, serializer):
        return super().perform_update(serializer)

    def perform_destroy(self, instance):
        return super().perform_destroy(instance)

    def create(self, request, *args, **kwargs):
        try:
            logger.info("CalendarEvent create - Data: %s", request.data)
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                # Use perform_create to auto-set created_by
                self.perform_create(serializer)
                event = serializer.instance

                # Re-fetch the event with related fields to include employee_name
                event.refresh_from_db()
                fresh_serializer = self.get_serializer(event)

                # Generate recurring events if this is a repeating event
                if event.is_repeating and event.repeat_frequency:
                    assigned_to_ids = request.data.get("assigned_to", [])
                    generate_recurring_events(event, assigned_to_ids)

                # Create notification for new event
                create_event_notification(event, "created")

                # Broadcast to task board if this is a task
                if event.event_type == "task":
                    try:
                        from ..consumers import broadcast_task_created

                        broadcast_task_created(fresh_serializer.data)
                    except Exception as ws_error:
                        logger.debug("WebSocket broadcast failed (non-critical): %s", ws_error)

                logger.info("CalendarEvent created successfully: %s", fresh_serializer.data.get("id"))
                return Response(fresh_serializer.data, status=status.HTTP_201_CREATED)
            logger.warning("CalendarEvent create validation errors: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except APIException:
            raise
        except Exception as e:
            logger.error("CalendarEvent create error: %s", e)
            logger.error("Traceback: %s", traceback.format_exc())
            logger.error("Request data: %s", request.data)
            return Response({"detail": "An unexpected error occurred. Please try again or contact support."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
