"""
Django signals for cache invalidation on model changes.

This module registers signal handlers that automatically invalidate
relevant caches when models are created, updated, or deleted.

Signals handled:
- post_save: Invalidates caches when Employee, Project, or OvertimeRequest is saved
- post_delete: Invalidates caches when objects are deleted
"""

import logging

# Bounded thread-pool for Excel generation fallback when Celery is unavailable.
# Imported from models where it was originally defined.
from concurrent.futures import ThreadPoolExecutor

from django.db import transaction
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from .models import CalendarEvent, Employee, ExternalUser, Notification, OvertimeRequest, Project, PurchaseRequest
from .services.cache_service import CacheService

logger = logging.getLogger(__name__)

_bg_executor = ThreadPoolExecutor(max_workers=2)


def _trigger_excel_fallback(ot_id, request_date):
    """Generate Excel files in a background thread when Celery is not available."""

    def _generate_sync(ot_id_inner, date_inner):
        try:
            from api.utils.excel_generator import ExcelGenerator

            export_data_grouped = OvertimeRequest.export_daily_data_by_department(date_inner)
            monthly_data_grouped = OvertimeRequest.export_monthly_data_by_department(date_inner)
            if export_data_grouped or monthly_data_grouped:
                ExcelGenerator.generate_all_excel_files(
                    export_data_grouped,
                    monthly_data_grouped,
                    date_inner,
                    upload=True,
                    temp_only=ExcelGenerator.EXCEL_TEMP_ONLY,
                )
                logger.info("Background thread Excel generation completed for OT %s (date: %s)", ot_id_inner, date_inner)
            else:
                logger.warning("No data to export for OT %s (date: %s)", ot_id_inner, date_inner)
        except Exception as sync_err:
            logger.error("Background thread Excel generation failed for OT %s: %s", ot_id_inner, sync_err, exc_info=True)

    _bg_executor.submit(_generate_sync, ot_id, request_date)


def send_websocket_notification(user_id: int, notification_data: dict):
    """
    Send notification via WebSocket if possible.
    Falls back silently if WebSocket is not available.

    notification_data should include:
    - id: The notification ID
    - title: Notification title
    - message: Notification message
    - event_type: Type of event (leave, purchase_request, calendar, etc.)
    - created_at: ISO format datetime string
    - is_read: Boolean (usually False for new notifications)
    - event_id: Optional linked event ID
    """
    try:
        from .consumers import send_notification_to_user

        send_notification_to_user(user_id, notification_data)
    except Exception as e:
        logger.debug("WebSocket notification failed (non-critical): %s", e)


def notify_leave_event_participants(event, is_update=False):
    """
    Send notifications for leave events to:
    1. The agent assigned to cover for the employee on leave
    2. All PTB admins about the leave request
    """
    if event.event_type != "leave":
        return

    notifications_created = []
    action = "updated" if is_update else "created"

    # Get leave details
    applied_by = event.applied_by
    agent = event.agent
    leave_start = event.start.strftime("%Y-%m-%d") if event.start else "N/A"
    leave_end = event.end.strftime("%Y-%m-%d") if event.end else leave_start

    employee_name = applied_by.name if applied_by else "Unknown"
    employee_dept = applied_by.dept_code if applied_by else ""
    employee_worker_id = applied_by.emp_id if applied_by else ""

    # 1. Notify the agent (if assigned)
    if agent and agent.emp_id:
        try:
            agent_user = ExternalUser.objects.get(worker_id=agent.emp_id, is_active=True)

            title = f"Leave Agent Assignment: {employee_name}"
            message = f"You have been assigned as agent for {employee_name} ({employee_worker_id}) from {applied_by.dept_code if applied_by else 'N/A'} department.\nLeave Period: {leave_start} to {leave_end}\nLeave Type: {event.leave_type or 'N/A'}"

            notification = Notification.objects.create(recipient=agent_user, title=title, message=message, event=event, event_type="leave")
            notifications_created.append(notification)
            send_websocket_notification(agent_user.id, {"id": notification.id, "title": title, "message": message, "event_type": "leave", "event_id": event.id if event else None, "is_read": False, "created_at": notification.created_at.isoformat()})
            logger.info("Notified agent %s about leave coverage for %s", agent.name, employee_name)
        except ExternalUser.DoesNotExist:
            logger.debug("No ExternalUser found for agent %s", agent.emp_id)
        except Exception as e:
            logger.error("Error notifying agent: %s", e)

    # 2. Notify all PTB admins about the leave
    try:
        ptb_admins = list(ExternalUser.objects.filter(is_ptb_admin=True, is_active=True))

        agent_info = ""
        if agent:
            agent_info = f"\nAgent: {agent.name} ({agent.emp_id}) - {agent.dept_code or 'N/A'}"

        title = f"Leave Request {action.title()}: {employee_name}"
        message = f"Employee: {employee_name} ({employee_worker_id})\nDepartment: {employee_dept or 'N/A'}\nLeave Period: {leave_start} to {leave_end}\nLeave Type: {event.leave_type or 'N/A'}{agent_info}"

        notifs_to_create = []
        ws_payloads = []
        for admin_user in ptb_admins:
            # Don't notify if admin is the one who created the leave
            if applied_by and admin_user.worker_id and admin_user.worker_id.lower() == applied_by.emp_id.lower():
                continue

            notifs_to_create.append(Notification(recipient=admin_user, title=title, message=message, event=event, event_type="leave"))
            ws_payloads.append(
                (
                    admin_user.id,
                    {
                        "title": title,
                        "message": message,
                        "event_type": "leave",
                        "event_id": event.id if event else None,
                        "is_read": False,
                    },
                )
            )

        if notifs_to_create:
            created = Notification.objects.bulk_create(notifs_to_create)
            notifications_created.extend(created)
            for notif, (uid, payload) in zip(created, ws_payloads, strict=True):
                payload["id"] = notif.id
                payload["created_at"] = notif.created_at.isoformat()
                send_websocket_notification(uid, payload)

        logger.info("Notified %s PTB admins about leave for %s", len(notifs_to_create), employee_name)
    except Exception as e:
        logger.error("Error notifying PTB admins about leave: %s", e)

    return notifications_created


def notify_purchase_request_status_change(purchase_request, old_status, new_status):
    """
    Send notification when purchase request status changes to 'done' or 'canceled'.
    """
    if new_status not in ["done", "canceled"]:
        return

    if old_status == new_status:
        return

    # Find the user who created the request (by owner_employee or owner name)
    owner_employee = purchase_request.owner_employee
    recipient = None

    if owner_employee and owner_employee.emp_id:
        try:
            recipient = ExternalUser.objects.get(worker_id=owner_employee.emp_id, is_active=True)
        except ExternalUser.DoesNotExist:
            pass

    if not recipient and purchase_request.owner:
        # Try to find user by exact username match first, then exact name match
        # (avoid icontains which can match the wrong person)
        owner_str = purchase_request.owner.strip()
        try:
            recipient = ExternalUser.objects.filter(username__iexact=owner_str, is_active=True).first()
        except Exception:
            pass

        if not recipient:
            parts = owner_str.split()
            if len(parts) >= 2:
                try:
                    recipient = ExternalUser.objects.filter(
                        first_name__iexact=parts[0],
                        last_name__iexact=parts[-1],
                        is_active=True,
                    ).first()
                except Exception:
                    pass

    if not recipient:
        logger.debug("Could not find recipient for purchase request %s", purchase_request.id)
        return

    status_text = "Completed" if new_status == "done" else "Canceled"
    title = f"Purchase Request {status_text}: {purchase_request.part_no or purchase_request.description_spec or 'N/A'}"
    message = f"Your purchase request has been {new_status}.\nDoc ID: {purchase_request.doc_id or 'N/A'}\nPart No: {purchase_request.part_no or 'N/A'}\nDescription: {purchase_request.description_spec or 'N/A'}\nPR No: {purchase_request.pr_no or 'N/A'}"

    notification = Notification.objects.create(recipient=recipient, title=title, message=message, event_type="purchase_request")
    send_websocket_notification(recipient.id, {"id": notification.id, "title": title, "message": message, "event_type": "purchase_request", "event_id": None, "is_read": False, "created_at": notification.created_at.isoformat()})
    logger.info("Notified %s about purchase request status change to %s", recipient.username, new_status)
    return notification


def notify_ptb_admins_new_purchase_request(purchase_request):
    """
    Notify all PTB admins when a new purchase request is created.
    Uses bulk_create for efficiency.
    """
    try:
        ptb_admins = list(ExternalUser.objects.filter(is_ptb_admin=True, is_active=True))

        owner_name = purchase_request.owner or "Unknown"
        if purchase_request.owner_employee:
            owner_name = f"{purchase_request.owner_employee.name} ({purchase_request.owner_employee.emp_id})"

        title = f"New Purchase Request: {purchase_request.part_no or purchase_request.description_spec or 'N/A'}"
        message = (
            f"Requestor: {owner_name}\n"
            f"Doc ID: {purchase_request.doc_id or 'N/A'}\n"
            f"Part No: {purchase_request.part_no or 'N/A'}\n"
            f"Description: {purchase_request.description_spec or 'N/A'}\n"
            f"Qty: {purchase_request.qty}\n"
            f"Purpose: {purchase_request.purpose_desc or 'N/A'}"
        )

        notifs_to_create = [Notification(recipient=admin_user, title=title, message=message, event_type="purchase_request") for admin_user in ptb_admins]

        if notifs_to_create:
            created = Notification.objects.bulk_create(notifs_to_create)
            for notif, admin_user in zip(created, ptb_admins, strict=True):
                send_websocket_notification(admin_user.id, {"id": notif.id, "title": title, "message": message, "event_type": "purchase_request", "event_id": None, "is_read": False, "created_at": notif.created_at.isoformat()})

        logger.info("Notified %s PTB admins about new purchase request", len(ptb_admins))
        return created if notifs_to_create else []
    except Exception as e:
        logger.error("Error notifying PTB admins about purchase request: %s", e)
        return []


@receiver(m2m_changed, sender=CalendarEvent.assigned_to.through)
def notify_assigned_employees(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Create notifications when employees are assigned to a calendar event.
    Excludes PTB admins from receiving task notifications.
    Uses bulk_create for efficiency when notifying multiple users.
    """
    if action == "post_add" and pk_set:
        try:
            notifications_to_create = []
            ws_payloads = []  # (user_id, payload) tuples

            if not reverse:
                # Instance is CalendarEvent, pk_set is Employee IDs
                event = instance
                emp_ids = list(Employee.objects.filter(id__in=pk_set).exclude(emp_id="").values_list("emp_id", flat=True))
                if not emp_ids:
                    return

                users = ExternalUser.objects.filter(worker_id__in=emp_ids, is_active=True, is_ptb_admin=False)

                for user in users:
                    title = f"New {event.event_type.capitalize()}: {event.title}"
                    message = f"You have been assigned to a {event.event_type}: {event.title}."
                    if event.start:
                        message += f"\nDate: {event.start.strftime('%Y-%m-%d %H:%M')}"

                    notifications_to_create.append(Notification(recipient=user, title=title, message=message, event=event, event_type="calendar"))
                    ws_payloads.append(
                        (
                            user.id,
                            {
                                "title": title,
                                "message": message,
                                "event_type": "calendar",
                                "event_id": event.id,
                                "is_read": False,
                            },
                        )
                    )
            else:
                # Reverse: Instance is Employee, pk_set is CalendarEvent IDs
                employee = instance
                if not employee.emp_id:
                    return

                users = list(ExternalUser.objects.filter(worker_id=employee.emp_id, is_active=True, is_ptb_admin=False))
                if not users:
                    return

                events = CalendarEvent.objects.filter(id__in=pk_set)

                for user in users:
                    for event in events:
                        title = f"New {event.event_type.capitalize()}: {event.title}"
                        message = f"You have been assigned to a {event.event_type}: {event.title}."
                        if event.start:
                            message += f"\nDate: {event.start.strftime('%Y-%m-%d %H:%M')}"

                        notifications_to_create.append(Notification(recipient=user, title=title, message=message, event=event, event_type="calendar"))
                        ws_payloads.append(
                            (
                                user.id,
                                {
                                    "title": title,
                                    "message": message,
                                    "event_type": "calendar",
                                    "event_id": event.id,
                                    "is_read": False,
                                },
                            )
                        )

            # Bulk create all notifications at once
            if notifications_to_create:
                created_notifications = Notification.objects.bulk_create(notifications_to_create)
                logger.info("Bulk created %s notifications for event assignment", len(created_notifications))

                # Send WebSocket notifications with the created IDs
                for notification, (user_id, payload) in zip(created_notifications, ws_payloads, strict=True):
                    payload["id"] = notification.id
                    payload["created_at"] = notification.created_at.isoformat()
                    send_websocket_notification(user_id, payload)

        except Exception as e:
            logger.error("Error creating notifications: %s", e)


@receiver(post_save, sender=Employee)
def invalidate_employee_cache(sender, instance, created, **kwargs):
    """
    Invalidate employee-related caches when an Employee is saved.

    Args:
        sender: The model class (Employee)
        instance: The instance being saved
        created: Boolean indicating if object was created
        **kwargs: Additional signal arguments
    """
    try:
        action = "created" if created else "updated"
        logger.debug("Employee %s: %s (ID: %s)", action, instance.name, instance.id)

        # Invalidate all employee list caches
        CacheService.invalidate_all_for_view("employees")

        # Invalidate individual employee object cache if it exists
        CacheService.invalidate(
            view_name="employees",
            cache_type="obj",
        )

        logger.debug("Invalidated employee cache for %s", instance.name)
    except Exception as e:
        logger.error("Error invalidating employee cache: %s", e)


@receiver(post_delete, sender=Employee)
def invalidate_employee_cache_on_delete(sender, instance, **kwargs):
    """
    Invalidate employee-related caches when an Employee is deleted.

    Args:
        sender: The model class (Employee)
        instance: The instance being deleted
        **kwargs: Additional signal arguments
    """
    try:
        logger.debug("Employee deleted: %s (ID: %s)", instance.name, instance.id)

        # Invalidate all employee caches
        CacheService.invalidate_all_for_view("employees")

        logger.debug("Invalidated employee cache (deleted)")
    except Exception as e:
        logger.error("Error invalidating employee cache on delete: %s", e)


@receiver(post_save, sender=Project)
def invalidate_project_cache(sender, instance, created, **kwargs):
    """
    Invalidate project-related caches when a Project is saved.

    Args:
        sender: The model class (Project)
        instance: The instance being saved
        created: Boolean indicating if object was created
        **kwargs: Additional signal arguments
    """
    try:
        action = "created" if created else "updated"
        logger.debug("Project %s: %s (ID: %s)", action, instance.name, instance.id)

        # Invalidate all project list caches
        CacheService.invalidate_all_for_view("projects")

        # Invalidate individual project object cache
        CacheService.invalidate(
            view_name="projects",
            cache_type="obj",
        )

        logger.debug("Invalidated project cache for %s", instance.name)
    except Exception as e:
        logger.error("Error invalidating project cache: %s", e)


@receiver(post_delete, sender=Project)
def invalidate_project_cache_on_delete(sender, instance, **kwargs):
    """
    Invalidate project-related caches when a Project is deleted.

    Args:
        sender: The model class (Project)
        instance: The instance being deleted
        **kwargs: Additional signal arguments
    """
    try:
        logger.debug("Project deleted: %s (ID: %s)", instance.name, instance.id)

        # Invalidate all project caches
        CacheService.invalidate_all_for_view("projects")

        logger.debug("Invalidated project cache (deleted)")
    except Exception as e:
        logger.error("Error invalidating project cache on delete: %s", e)


@receiver(post_save, sender=OvertimeRequest)
def invalidate_overtime_cache(sender, instance, created, **kwargs):
    """
    Invalidate overtime request caches when an OvertimeRequest is saved,
    then offload Excel generation + SMB upload to Celery (or thread-pool fallback).

    Args:
        sender: The model class (OvertimeRequest)
        instance: The instance being saved
        created: Boolean indicating if object was created
        **kwargs: Additional signal arguments
    """
    try:
        action = "created" if created else "updated"
        logger.debug("OvertimeRequest %s: ID %s", action, instance.id)

        # Invalidate all overtime request caches
        CacheService.invalidate_all_for_view("overtime_requests")

        logger.debug("Invalidated overtime cache")
    except Exception as e:
        logger.error("Error invalidating overtime cache: %s", e)

    # Offload Excel generation to Celery (or bounded thread-pool fallback)
    # so the HTTP response is never blocked.
    # Use on_commit to ensure the OT record is committed before the task reads it.
    if instance.request_date:
        ot_id = instance.id
        ot_date = instance.request_date

        def _queue_excel():
            try:
                from api.tasks import generate_excel_files_async

                generate_excel_files_async.delay(ot_id)
                logger.info("Queued async Excel generation for OvertimeRequest %s (date: %s)", ot_id, ot_date)
            except Exception as e:
                logger.warning("Failed to queue async Excel generation for OT %s: %s. Falling back to background thread pool.", ot_id, e)
                _trigger_excel_fallback(ot_id, ot_date)

        transaction.on_commit(_queue_excel)


@receiver(post_delete, sender=OvertimeRequest)
def invalidate_overtime_cache_on_delete(sender, instance, **kwargs):
    """
    Invalidate overtime request caches when an OvertimeRequest is deleted,
    then offload Excel regeneration to Celery (or thread-pool fallback).

    Args:
        sender: The model class (OvertimeRequest)
        instance: The instance being deleted
        **kwargs: Additional signal arguments
    """
    try:
        logger.debug("OvertimeRequest deleted: ID %s", instance.id)

        # Invalidate related caches
        CacheService.invalidate_all_for_view("overtime_requests")

        logger.debug("Invalidated overtime cache (deleted)")
    except Exception as e:
        logger.error("Error invalidating overtime cache on delete: %s", e)

    # Offload Excel regeneration to Celery (or bounded thread-pool fallback)
    # Use on_commit to ensure the deletion is committed before the task runs.
    if instance.request_date:
        ot_id = instance.id
        ot_date = instance.request_date

        def _queue_regen():
            try:
                from api.tasks import regenerate_excel_after_delete

                regenerate_excel_after_delete.delay(ot_date.isoformat())
                logger.info("Queued async Excel regeneration after OT deletion (date: %s)", ot_date)
            except Exception as e:
                logger.warning("Failed to queue async Excel regeneration after delete for %s: %s. Falling back to background thread pool.", ot_date, e)
                _trigger_excel_fallback(ot_id, ot_date)

        transaction.on_commit(_queue_regen)


@receiver(post_save, sender=CalendarEvent)
def invalidate_calendar_cache(sender, instance, created, **kwargs):
    """
    Invalidate calendar event caches when a CalendarEvent is saved.

    Args:
        sender: The model class (CalendarEvent)
        instance: The instance being saved
        created: Boolean indicating if object was created
        **kwargs: Additional signal arguments
    """
    try:
        action = "created" if created else "updated"
        logger.debug("CalendarEvent %s: ID %s", action, instance.id)

        # Invalidate all calendar event caches
        CacheService.invalidate_all_for_view("calendar_events")

        logger.debug("Invalidated calendar cache")
    except Exception as e:
        logger.error("Error invalidating calendar cache: %s", e)


@receiver(post_delete, sender=CalendarEvent)
def invalidate_calendar_cache_on_delete(sender, instance, **kwargs):
    """
    Invalidate calendar event caches when a CalendarEvent is deleted.

    Args:
        sender: The model class (CalendarEvent)
        instance: The instance being deleted
        **kwargs: Additional signal arguments
    """
    try:
        logger.debug("CalendarEvent deleted: ID %s", instance.id)

        # Invalidate calendar caches
        CacheService.invalidate_all_for_view("calendar_events")

        logger.debug("Invalidated calendar cache (deleted)")
    except Exception as e:
        logger.error("Error invalidating calendar cache on delete: %s", e)


@receiver(post_save, sender=PurchaseRequest)
def handle_purchase_request_save(sender, instance, created, **kwargs):
    """
    Handle purchase request save events:
    - Notify PTB admins when a new purchase request is created
    - Notify the requestor when status changes to done/canceled
    """
    try:
        if created:
            # New purchase request - notify PTB admins
            notify_ptb_admins_new_purchase_request(instance)
            logger.info("Purchase request created: ID %s", instance.id)
        # Status-change notifications are handled in the view (PurchaseRequestViewSet)
        # where old_status is available for comparison.
    except Exception as e:
        logger.error("Error handling purchase request save: %s", e)
