import logging

from django.contrib.auth import get_user_model
from django.db import models
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ..models import (
    Employee,
    EmployeeLeave,
    ExternalUser,
    Holiday,
    Notification,
)
from ..pagination import DynamicPagination
from ..serializers import (
    EmployeeLeaveSerializer,
    HolidaySerializer,
)
from .helpers import get_employee_for_user, is_developer_user, is_ptb_admin, is_superadmin_user  # noqa: F401

logger = logging.getLogger(__name__)
User = get_user_model()


class HolidayViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing holidays on the calendar.
    Separate from CalendarEvent for simpler holiday management.
    """

    permission_classes = [IsAuthenticated]
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    pagination_class = DynamicPagination
    ordering = ["date"]

    def get_queryset(self):
        queryset = Holiday.objects.select_related("created_by")

        # Filter by year if provided
        year = self.request.query_params.get("year")
        if year:
            try:
                year = int(year)
                queryset = queryset.filter(date__year=year)
            except ValueError:
                pass

        # Filter by month if provided
        month = self.request.query_params.get("month")
        if month:
            try:
                month = int(month)
                queryset = queryset.filter(date__month=month)
            except ValueError:
                pass

        # Filter by date range
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        return queryset.order_by("date")

    def perform_create(self, serializer):
        """Set the created_by field to the current user"""
        user = self.request.user
        if isinstance(user, ExternalUser):
            instance = serializer.save(created_by=user)
        else:
            # Try to find matching ExternalUser
            ext_user = ExternalUser.objects.filter(username=user.username).first()
            instance = serializer.save(created_by=ext_user)
        # Broadcast calendar update
        try:
            from ..consumers import broadcast_calendar_update

            broadcast_calendar_update("created", "holiday", HolidaySerializer(instance).data)
        except Exception as e:
            logger.debug("Calendar broadcast failed (non-critical): %s", e)

    def perform_update(self, serializer):
        instance = serializer.save()
        try:
            from ..consumers import broadcast_calendar_update

            broadcast_calendar_update("updated", "holiday", HolidaySerializer(instance).data)
        except Exception as e:
            logger.debug("Calendar broadcast failed (non-critical): %s", e)

    def perform_destroy(self, instance):
        holiday_id = instance.id
        instance.delete()
        try:
            from ..consumers import broadcast_calendar_update

            broadcast_calendar_update("deleted", "holiday", {"id": holiday_id})
        except Exception as e:
            logger.debug("Calendar broadcast failed (non-critical): %s", e)


class EmployeeLeaveViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing employee leaves.
    Includes agent coverage tracking.
    """

    permission_classes = [IsAuthenticated]
    queryset = EmployeeLeave.objects.all()
    serializer_class = EmployeeLeaveSerializer
    pagination_class = DynamicPagination
    ordering = ["date", "employee__name"]

    def get_queryset(self):
        queryset = EmployeeLeave.objects.select_related("employee", "employee__department", "created_by").prefetch_related(models.Prefetch("agents", queryset=Employee.objects.select_related("department")))

        # Filter by year if provided
        year = self.request.query_params.get("year")
        if year:
            try:
                year = int(year)
                queryset = queryset.filter(date__year=year)
            except ValueError:
                pass

        # Filter by month if provided
        month = self.request.query_params.get("month")
        if month:
            try:
                month = int(month)
                queryset = queryset.filter(date__month=month)
            except ValueError:
                pass

        # Filter by date range
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        # Filter by employee
        employee_id = self.request.query_params.get("employee")
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)

        # Filter by specific date
        date = self.request.query_params.get("date")
        if date:
            queryset = queryset.filter(date=date)

        return queryset.order_by("date", "employee__name")

    def perform_create(self, serializer):
        """Set the created_by field to the current user and notify PTB admins"""
        from django.db import transaction

        from ..consumers import send_notification_to_user

        user = self.request.user
        if isinstance(user, ExternalUser):
            leave = serializer.save(created_by=user)
        else:
            # Try to find matching ExternalUser
            ext_user = ExternalUser.objects.filter(username=user.username).first()
            leave = serializer.save(created_by=ext_user)

        # Capture values needed for the on_commit callback
        leave_id = leave.id
        request_user = user

        def _send_leave_notifications():
            """Send notifications after transaction commits (M2M data is guaranteed flushed)."""
            from ..consumers import broadcast_calendar_update

            leave_obj = EmployeeLeave.objects.get(pk=leave_id)
            employee_name = leave_obj.employee.name
            leave_date = leave_obj.date.strftime("%B %d, %Y")
            created_by_name = request_user.username if hasattr(request_user, "username") else "Unknown"

            # Collect agent names for richer notification messages
            agent_employees = list(leave_obj.agents.all())
            agent_names = [a.name for a in agent_employees] if agent_employees else []
            agent_names_str = ", ".join(agent_names) if agent_names else "None assigned"

            title = "New Leave Request"
            message = f"{employee_name} has taken leave on {leave_date}.\nAgent(s): {agent_names_str}\nSubmitted by {created_by_name}."

            # Bulk-create notifications for PTB admins
            ptb_admins = list(ExternalUser.objects.filter(is_ptb_admin=True, is_active=True))
            admin_notifs = [Notification(recipient=admin, title=title, message=message, event_type="leave") for admin in ptb_admins]
            if admin_notifs:
                created_admin = Notification.objects.bulk_create(admin_notifs)
                for notif, admin in zip(created_admin, ptb_admins, strict=True):
                    send_notification_to_user(admin.id, {"id": notif.id, "title": title, "message": message, "event_type": "leave", "event_id": None, "is_read": False, "created_at": notif.created_at.isoformat()})

            # Notify agents assigned to cover this leave (batch user lookup)
            if agent_employees:
                agent_emp_ids = [a.emp_id for a in agent_employees if a.emp_id]
                agent_users = {u.worker_id.lower(): u for u in ExternalUser.objects.filter(worker_id__in=agent_emp_ids, is_active=True)} if agent_emp_ids else {}

                agent_title = "Agent Assignment"
                agent_notifs = []
                agent_ws = []
                for agent_employee in agent_employees:
                    if not agent_employee.emp_id:
                        continue
                    agent_user = agent_users.get(agent_employee.emp_id.lower())
                    if agent_user:
                        agent_message = f"You have been assigned as agent for {employee_name} on {leave_date}."
                        agent_notifs.append(Notification(recipient=agent_user, title=agent_title, message=agent_message, event_type="leave"))
                        agent_ws.append((agent_user.id, agent_title, agent_message))

                if agent_notifs:
                    created_agents = Notification.objects.bulk_create(agent_notifs)
                    for notif, (uid, atitle, amsg) in zip(created_agents, agent_ws, strict=True):
                        send_notification_to_user(uid, {"id": notif.id, "title": atitle, "message": amsg, "event_type": "leave", "event_id": None, "is_read": False, "created_at": notif.created_at.isoformat()})

            # Broadcast calendar update for real-time PTB Calendar
            try:
                broadcast_calendar_update("created", "leave", EmployeeLeaveSerializer(leave_obj).data)
            except Exception as e:
                logger.debug("Calendar broadcast failed (non-critical): %s", e)

        transaction.on_commit(_send_leave_notifications)

    def perform_update(self, serializer):
        instance = serializer.save()
        try:
            from ..consumers import broadcast_calendar_update

            broadcast_calendar_update("updated", "leave", EmployeeLeaveSerializer(instance).data)
        except Exception as e:
            logger.debug("Calendar broadcast failed (non-critical): %s", e)

    def perform_destroy(self, instance):
        leave_id = instance.id
        instance.delete()
        try:
            from ..consumers import broadcast_calendar_update

            broadcast_calendar_update("deleted", "leave", {"id": leave_id})
        except Exception as e:
            logger.debug("Calendar broadcast failed (non-critical): %s", e)
