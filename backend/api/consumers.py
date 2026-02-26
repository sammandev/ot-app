"""
WebSocket consumers for Task Board real-time features.
Handles:
- Board presence (who's viewing)
- Real-time task updates
- Live comments
- Activity notifications
- System notifications (leave requests, etc.)
- Permission updates
"""

import logging
import time
from collections import deque
from datetime import timedelta

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer
from django.utils import timezone

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Per-connection rate limiter (B7)
# ---------------------------------------------------------------------------
_WS_RATE_LIMIT = 30  # max messages
_WS_RATE_WINDOW = 10  # per N seconds


class _RateLimitMixin:
    """
    Mixin for AsyncJsonWebsocketConsumer that enforces a sliding-window
    rate limit per connection.  Call ``self._check_rate_limit()`` at the
    top of ``receive_json``; it returns True when the limit is exceeded
    and sends an error frame + optional disconnect.
    """

    def _init_rate_limiter(self):
        self._msg_timestamps: deque = deque()

    def _check_rate_limit(self) -> bool:
        """Return True if the current message should be dropped."""
        now = time.monotonic()
        ts = self._msg_timestamps
        # Evict entries outside the window
        while ts and ts[0] < now - _WS_RATE_WINDOW:
            ts.popleft()
        if len(ts) >= _WS_RATE_LIMIT:
            return True  # caller should reject
        ts.append(now)
        return False


class _TokenAuthMixin:
    """
    Shared WebSocket authentication helpers.
    Provides _authenticate_token (validates UserSession) and
    _fetch_employee / get_employee (cached employee lookup).
    """

    @database_sync_to_async
    def _authenticate_token(self, token):
        """Validate an access token and return the authenticated user."""
        from api.models import UserSession

        try:
            session = UserSession.objects.select_related("user").get(
                access_token=token, is_active=True
            )
            if not session.is_token_expired():
                return session.user
        except UserSession.DoesNotExist:
            pass
        except Exception as e:
            consumer_name = type(self).__name__
            logger.error(f"{consumer_name} auth error: {e}")
        return None

    async def get_employee(self):
        """Get employee for this user (cached after first lookup)."""
        if getattr(self, "_employee_cache", None) is not None:
            return self._employee_cache
        self._employee_cache = await self._fetch_employee()
        return self._employee_cache

    @database_sync_to_async
    def _fetch_employee(self):
        from .models import Employee

        user = self.user if hasattr(self, "user") else self.scope.get("user")
        if user and hasattr(user, "worker_id"):
            return Employee.objects.filter(emp_id=user.worker_id).first()
        return None


# Helper function to send notifications via WebSocket
def send_notification_to_user(user_id: int, notification_data: dict):
    """
    Send a notification to a specific user via WebSocket.
    Call this from views/signals when creating notifications.
    """
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(f"notifications_{user_id}", {"type": "notification_message", **notification_data})


def send_permission_update_to_user(user_id: int, user_data: dict):
    """
    Send a permission update to a specific user via WebSocket.
    Call this from views when admin updates user permissions.

    Args:
        user_id: The ID of the user whose permissions changed
        user_data: The updated user data including new permissions
    """
    channel_layer = get_channel_layer()
    if channel_layer:
        logger.info(f"Sending permission update to user {user_id}")
        async_to_sync(channel_layer.group_send)(f"notifications_{user_id}", {"type": "permission_update", "user": user_data})


def broadcast_task_created(task_data: dict):
    """
    Broadcast a new task to all task board viewers.
    Call this from views when a task is created.
    """
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            "task_board",
            {
                "type": "task_created",
                "task_data": task_data,
                "created_by": task_data.get("created_by_name", "Unknown"),
            },
        )


def broadcast_task_updated(task_data: dict, updated_by: str = "Unknown"):
    """
    Broadcast a task update to all task board viewers.
    Call this from views when a task is updated.
    """
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            "task_board",
            {
                "type": "task_updated",
                "task_id": task_data.get("id"),
                "task_data": task_data,
                "updated_by": updated_by,
            },
        )


def broadcast_task_deleted(task_id: int, deleted_by: str = "Unknown"):
    """
    Broadcast a task deletion to all task board viewers.
    Call this from views when a task is deleted.
    """
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            "task_board",
            {
                "type": "task_deleted",
                "task_id": task_id,
                "deleted_by": deleted_by,
            },
        )


def send_notification_to_ptb_admins(notification_data: dict):
    """
    Send a notification to all PTB admin users.
    """
    from .models import ExternalUser

    channel_layer = get_channel_layer()
    if channel_layer:
        # Get all PTB admin user IDs
        ptb_admin_ids = ExternalUser.objects.filter(is_ptb_admin=True, is_active=True).values_list("id", flat=True)

        for user_id in ptb_admin_ids:
            async_to_sync(channel_layer.group_send)(f"notifications_{user_id}", {"type": "notification_message", **notification_data})


def send_notification_to_superadmins(notification_data: dict):
    """
    Send a notification to all super admin users via WebSocket.
    Super admin is identified by the 'role' field on ExternalUser.
    """
    from .models import ExternalUser

    channel_layer = get_channel_layer()
    if channel_layer:
        superadmin_ids = ExternalUser.objects.filter(
            is_active=True,
            role__in=("developer", "superadmin"),
        ).values_list("id", flat=True)

        for user_id in superadmin_ids:
            async_to_sync(channel_layer.group_send)(f"notifications_{user_id}", {"type": "notification_message", **notification_data})


# ── PTB Calendar broadcast helpers ──────────────────────────────────────────


def broadcast_calendar_update(action: str, entity_type: str, entity_data: dict):
    """
    Broadcast a calendar change (holiday or leave) to all connected PTB Calendar viewers.

    Args:
        action: 'created', 'updated', or 'deleted'
        entity_type: 'holiday' or 'leave'
        entity_data: Serialized data of the entity (or {'id': <id>} for deletes)
    """
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            "ptb_calendar",
            {
                "type": "calendar_update",
                "action": action,
                "entity_type": entity_type,
                "data": entity_data,
                "timestamp": timezone.now().isoformat(),
            },
        )


class NotificationConsumer(_RateLimitMixin, _TokenAuthMixin, AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications.
    Each user joins their own notification group.

    Supports three authentication modes (tried in order):
    1. Cookie auth (preferred): The httpOnly ``access_token`` cookie is read
       by ``TokenAuthMiddleware`` during the WebSocket handshake, which
       populates ``scope['user']`` before the consumer runs.
    2. First-message auth (fallback): Connect, then send
       {"type": "authenticate", "token": "<access_token>"} as the first message.
    3. Query-string auth (legacy): Connect with ?token=<access_token> in the URL.
    """

    async def connect(self):
        """Called when WebSocket connects."""
        self.user = self.scope.get("user")
        self.user_id = None
        self.notification_group = None
        self._authenticated = False
        self._is_accepted = False
        self._init_rate_limiter()

        if self.user and getattr(self.user, "is_authenticated", False) and hasattr(self.user, "id"):
            # User was authenticated via TokenAuthMiddleware (cookie or query-string)
            await self._setup_authenticated_user()
        else:
            # Accept connection and wait for first-message authentication
            await self.accept()
            self._is_accepted = True

    async def _setup_authenticated_user(self):
        """Set up an authenticated user's notification group."""
        self.user_id = self.user.id
        self.notification_group = f"notifications_{self.user_id}"
        self._authenticated = True

        # Join the user's notification group
        await self.channel_layer.group_add(self.notification_group, self.channel_name)

        if not self._is_accepted:
            await self.accept()
            self._is_accepted = True

        # Send initial unread count
        unread_count = await self.get_unread_count()
        await self.send_json({"type": "connected", "unread_count": unread_count})

    async def disconnect(self, close_code):
        """Called when WebSocket disconnects."""
        if hasattr(self, "notification_group") and self.notification_group:
            await self.channel_layer.group_discard(self.notification_group, self.channel_name)

    async def receive_json(self, content):
        """Handle incoming WebSocket messages."""
        message_type = content.get("type")

        # Handle first-message authentication
        if message_type == "authenticate":
            if self._authenticated:
                return  # Already authenticated
            token = content.get("token")
            if not token:
                await self.send_json({"type": "auth_error", "error": "Token required"})
                await self.close()
                return
            user = await self._authenticate_token(token)
            if user:
                self.user = user
                await self._setup_authenticated_user()
            else:
                await self.send_json({"type": "auth_error", "error": "Invalid token"})
                await self.close()
            return

        # Reject all other messages if not authenticated
        if not self._authenticated:
            await self.send_json({"type": "auth_error", "error": "Not authenticated"})
            await self.close()
            return

        # Rate-limit (B7)
        if self._check_rate_limit():
            await self.send_json({"type": "error", "error": "Rate limit exceeded"})
            return

        if message_type == "mark_read":
            notification_id = content.get("notification_id")
            if notification_id:
                await self.mark_notification_read(notification_id)
                await self.send_json({"type": "notification_read", "notification_id": notification_id})

        elif message_type == "mark_all_read":
            await self.mark_all_read()
            await self.send_json({"type": "all_read", "unread_count": 0})

        elif message_type == "get_notifications":
            notifications = await self.get_notifications()
            await self.send_json({"type": "notifications_list", "notifications": notifications})

    async def notification_message(self, event):
        """Handle notification broadcast from server."""
        # Remove the 'type' key used by channels
        data = {k: v for k, v in event.items() if k != "type"}
        await self.send_json({"type": "new_notification", **data})

    async def permission_update(self, event):
        """Handle permission update broadcast from server."""
        # Send the updated user data to the client
        await self.send_json({"type": "permission_update", "user": event.get("user", {})})

    @database_sync_to_async
    def get_unread_count(self):
        from .models import Notification

        user_id = getattr(self, "user_id", None)
        if user_id:
            return Notification.objects.filter(recipient_id=user_id, is_read=False, is_archived=False).count()
        return 0

    @database_sync_to_async
    def get_notifications(self):
        from .models import Notification

        user_id = getattr(self, "user_id", None)
        if user_id:
            notifications = Notification.objects.filter(recipient_id=user_id, is_archived=False).order_by("-created_at")[:50]
            return [{"id": n.id, "title": n.title, "message": n.message, "is_read": n.is_read, "created_at": n.created_at.isoformat(), "event_id": n.event_id} for n in notifications]
        return []

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        from .models import Notification

        user_id = getattr(self, "user_id", None)
        if user_id:
            Notification.objects.filter(id=notification_id, recipient_id=user_id).update(is_read=True)

    @database_sync_to_async
    def mark_all_read(self):
        from .models import Notification

        user_id = getattr(self, "user_id", None)
        if user_id:
            Notification.objects.filter(recipient_id=user_id, is_read=False, is_archived=False).update(is_read=True)


class BoardConsumer(_RateLimitMixin, _TokenAuthMixin, AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for the main Kanban board.
    Handles:
    - Presence tracking (join/leave)
    - Task updates broadcast
    - New task notifications

    Authentication: Cookie auth (preferred), first-message auth (fallback),
    or legacy query-string auth via TokenAuthMiddleware.
    """

    async def connect(self):
        """Called when WebSocket connects."""
        self.board_group = "task_board"
        self.user = self.scope.get("user")
        self._authenticated = False
        self._employee_cache = None
        self._init_rate_limiter()

        if self.user and getattr(self.user, "is_authenticated", False) and hasattr(self.user, "id"):
            # User was authenticated via TokenAuthMiddleware (cookie or query-string)
            await self.accept()
            await self._setup_authenticated_board()
        else:
            # Accept connection and wait for first-message authentication
            await self.accept()

    async def _setup_authenticated_board(self):
        """Set up an authenticated user's board connection."""
        self._authenticated = True

        # Join the board group
        await self.channel_layer.group_add(self.board_group, self.channel_name)

        # Get employee for this user (and cache it)
        employee = await self._fetch_employee()
        self._employee_cache = employee
        if employee:
            # Update presence
            await self.update_presence(employee, None)

            # Broadcast user joined
            await self.channel_layer.group_send(self.board_group, {"type": "user_joined", "user_id": employee.id, "user_name": employee.name, "timestamp": timezone.now().isoformat()})

            # Send current viewers to the new user
            viewers = await self.get_current_viewers(employee)
            await self.send_json({"type": "current_viewers", "viewers": viewers})

    async def disconnect(self, close_code):
        """Called when WebSocket disconnects."""
        employee = await self.get_employee()
        if employee:
            # Remove presence
            await self.remove_presence(employee)

            # Broadcast user left
            await self.channel_layer.group_send(self.board_group, {"type": "user_left", "user_id": employee.id, "user_name": employee.name, "timestamp": timezone.now().isoformat()})

        # Leave the board group
        await self.channel_layer.group_discard(self.board_group, self.channel_name)

    async def receive_json(self, content):
        """Handle incoming WebSocket messages."""
        message_type = content.get("type")

        # Handle first-message authentication
        if message_type == "authenticate":
            if self._authenticated:
                return
            token = content.get("token")
            if not token:
                await self.send_json({"type": "auth_error", "error": "Token required"})
                await self.close()
                return
            user = await self._authenticate_token(token)
            if user:
                self.user = user
                await self._setup_authenticated_board()
            else:
                await self.send_json({"type": "auth_error", "error": "Invalid token"})
                await self.close()
            return

        # Reject all other messages if not authenticated
        if not self._authenticated:
            await self.send_json({"type": "auth_error", "error": "Not authenticated"})
            await self.close()
            return

        # Rate-limit (B7)
        if self._check_rate_limit():
            await self.send_json({"type": "error", "error": "Rate limit exceeded"})
            return

        if message_type == "heartbeat":
            # Update presence heartbeat
            employee = await self.get_employee()
            if employee:
                editing_task_id = content.get("editing_task_id")
                await self.update_presence(employee, editing_task_id)

                # If user started editing a task, broadcast it
                if editing_task_id:
                    await self.channel_layer.group_send(self.board_group, {"type": "task_editing", "user_id": employee.id, "user_name": employee.name, "task_id": editing_task_id})

        elif message_type == "stop_editing":
            # User closed task detail drawer - broadcast to clear editing indicator
            employee = await self.get_employee()
            if employee:
                await self.update_presence(employee, None)
                await self.channel_layer.group_send(self.board_group, {"type": "task_editing", "user_id": employee.id, "user_name": employee.name, "task_id": None})

        elif message_type == "task_updated":
            task_id = content.get("task_id")
            if not task_id or not isinstance(task_id, int):
                return
            # Validate the task exists (B4)
            if not await self._task_exists(task_id):
                return
            employee = await self.get_employee()
            await self.channel_layer.group_send(
                self.board_group,
                {"type": "task_updated", "task_id": task_id, "task_data": content.get("task_data") if isinstance(content.get("task_data"), dict) else None, "updated_by": employee.name if employee else "Unknown", "timestamp": timezone.now().isoformat()},
            )

        elif message_type == "task_created":
            employee = await self.get_employee()
            task_data = content.get("task_data")
            await self.channel_layer.group_send(self.board_group, {"type": "task_created", "task_data": task_data if isinstance(task_data, dict) else None, "created_by": employee.name if employee else "Unknown", "timestamp": timezone.now().isoformat()})

        elif message_type == "task_deleted":
            task_id = content.get("task_id")
            if not task_id or not isinstance(task_id, int):
                return
            if not await self._task_exists(task_id):
                return
            employee = await self.get_employee()
            await self.channel_layer.group_send(self.board_group, {"type": "task_deleted", "task_id": task_id, "deleted_by": employee.name if employee else "Unknown", "timestamp": timezone.now().isoformat()})

        elif message_type == "task_moved":
            task_id = content.get("task_id")
            if not task_id or not isinstance(task_id, int):
                return
            if not await self._task_exists(task_id):
                return
            employee = await self.get_employee()
            await self.channel_layer.group_send(
                self.board_group,
                {
                    "type": "task_moved",
                    "task_id": task_id,
                    "from_status": str(content.get("from_status", ""))[:50],
                    "to_status": str(content.get("to_status", ""))[:50],
                    "moved_by": employee.name if employee else "Unknown",
                    "timestamp": timezone.now().isoformat(),
                },
            )

    # Message handlers for group_send
    async def user_joined(self, event):
        await self.send_json(event)

    async def user_left(self, event):
        await self.send_json(event)

    async def task_editing(self, event):
        await self.send_json(event)

    async def task_updated(self, event):
        await self.send_json(event)

    async def task_created(self, event):
        await self.send_json(event)

    async def task_deleted(self, event):
        await self.send_json(event)

    async def task_moved(self, event):
        await self.send_json(event)

    # Database helpers
    @database_sync_to_async
    def update_presence(self, employee, editing_task_id):
        from .models import BoardPresence

        BoardPresence.objects.update_or_create(user=employee, defaults={"editing_task_id": editing_task_id, "channel_name": self.channel_name})

    @database_sync_to_async
    def remove_presence(self, employee):
        from .models import BoardPresence

        BoardPresence.objects.filter(user=employee).delete()

    @database_sync_to_async
    def get_current_viewers(self, exclude_employee):
        from .models import BoardPresence

        cutoff = timezone.now() - timedelta(minutes=5)
        presences = BoardPresence.objects.filter(last_seen__gte=cutoff).exclude(user=exclude_employee).select_related("user", "editing_task")

        return [{"user_id": p.user.id, "user_name": p.user.name, "editing_task_id": p.editing_task_id} for p in presences]

    @database_sync_to_async
    def _task_exists(self, task_id):
        """Verify a CalendarEvent (task) record exists before broadcasting."""
        from .models import CalendarEvent

        return CalendarEvent.objects.filter(pk=task_id).exists()


class TaskDetailConsumer(_RateLimitMixin, _TokenAuthMixin, AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for individual task detail view.
    Handles:
    - Real-time comments
    - Task activity updates
    - Edit conflicts

    Authentication: Cookie auth (preferred), first-message auth (fallback),
    or legacy query-string auth via TokenAuthMiddleware.
    """

    async def connect(self):
        """Called when WebSocket connects."""
        self.task_id = self.scope["url_route"]["kwargs"]["task_id"]
        self.task_group = f"task_{self.task_id}"
        self.user = self.scope.get("user")
        self._authenticated = False
        self._employee_cache = None
        self._init_rate_limiter()

        if self.user and getattr(self.user, "is_authenticated", False) and hasattr(self.user, "id"):
            # User was authenticated via TokenAuthMiddleware (cookie or query-string)
            await self.accept()
            await self._setup_authenticated_task()
        else:
            # Accept connection and wait for first-message authentication
            await self.accept()

    async def _setup_authenticated_task(self):
        """Set up an authenticated user's task connection."""
        self._authenticated = True

        # Join the task group
        await self.channel_layer.group_add(self.task_group, self.channel_name)

        # Get and send current editors of this task
        editors = await self.get_task_editors()
        await self.send_json({"type": "current_editors", "editors": editors})

    async def disconnect(self, close_code):
        """Called when WebSocket disconnects."""
        # Leave the task group
        await self.channel_layer.group_discard(self.task_group, self.channel_name)

    async def receive_json(self, content):
        """Handle incoming WebSocket messages."""
        message_type = content.get("type")

        # Handle first-message authentication
        if message_type == "authenticate":
            if self._authenticated:
                return
            token = content.get("token")
            if not token:
                await self.send_json({"type": "auth_error", "error": "Token required"})
                await self.close()
                return
            user = await self._authenticate_token(token)
            if user:
                self.user = user
                await self._setup_authenticated_task()
            else:
                await self.send_json({"type": "auth_error", "error": "Invalid token"})
                await self.close()
            return

        # Reject all other messages if not authenticated
        if not self._authenticated:
            await self.send_json({"type": "auth_error", "error": "Not authenticated"})
            await self.close()
            return

        # Rate-limit (B7)
        if self._check_rate_limit():
            await self.send_json({"type": "error", "error": "Rate limit exceeded"})
            return

        if message_type == "comment_added":
            # Validate comment text (B4)
            comment_text = content.get("comment")
            if not comment_text or not isinstance(comment_text, str):
                return
            employee = await self.get_employee()
            await self.channel_layer.group_send(self.task_group, {"type": "comment_added", "comment": comment_text[:5000], "author_name": employee.name if employee else "Unknown", "timestamp": timezone.now().isoformat()})

        elif message_type == "comment_updated":
            comment_id = content.get("comment_id")
            new_content = content.get("new_content")
            if not comment_id or not isinstance(comment_id, int):
                return
            if not new_content or not isinstance(new_content, str):
                return
            if not await self._comment_exists(comment_id):
                return
            await self.channel_layer.group_send(self.task_group, {"type": "comment_updated", "comment_id": comment_id, "new_content": new_content[:5000], "timestamp": timezone.now().isoformat()})

        elif message_type == "comment_deleted":
            comment_id = content.get("comment_id")
            if not comment_id or not isinstance(comment_id, int):
                return
            if not await self._comment_exists(comment_id):
                return
            await self.channel_layer.group_send(self.task_group, {"type": "comment_deleted", "comment_id": comment_id, "timestamp": timezone.now().isoformat()})

        elif message_type == "typing":
            employee = await self.get_employee()
            await self.channel_layer.group_send(self.task_group, {"type": "user_typing", "user_id": employee.id if employee else None, "user_name": employee.name if employee else "Unknown", "is_typing": bool(content.get("is_typing", True))})

    # Message handlers for group_send
    async def comment_added(self, event):
        await self.send_json(event)

    async def comment_updated(self, event):
        await self.send_json(event)

    async def comment_deleted(self, event):
        await self.send_json(event)

    async def user_typing(self, event):
        await self.send_json(event)

    # Database helpers
    @database_sync_to_async
    def get_task_editors(self):
        from .models import BoardPresence

        cutoff = timezone.now() - timedelta(minutes=5)
        presences = BoardPresence.objects.filter(last_seen__gte=cutoff, editing_task_id=self.task_id).select_related("user")

        return [{"user_id": p.user.id, "user_name": p.user.name} for p in presences]

    @database_sync_to_async
    def _comment_exists(self, comment_id):
        """Verify a TaskComment record exists before broadcasting."""
        from .models import TaskComment

        return TaskComment.objects.filter(pk=comment_id).exists()


class CalendarConsumer(_RateLimitMixin, _TokenAuthMixin, AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for PTB Calendar real-time updates.
    All connected calendar viewers receive holiday/leave create/update/delete events.

    Authentication: Cookie auth (preferred), first-message auth (fallback),
    or legacy query-string auth via TokenAuthMiddleware.
    """

    async def connect(self):
        self.calendar_group = "ptb_calendar"
        self.user = self.scope.get("user")
        self._authenticated = False
        self._init_rate_limiter()

        if self.user and getattr(self.user, "is_authenticated", False) and hasattr(self.user, "id"):
            # User was authenticated via TokenAuthMiddleware (cookie or query-string)
            await self.accept()
            await self._setup_authenticated_calendar()
        else:
            # Accept connection and wait for first-message authentication
            await self.accept()

    async def _setup_authenticated_calendar(self):
        """Set up an authenticated user's calendar connection."""
        self._authenticated = True
        await self.channel_layer.group_add(self.calendar_group, self.channel_name)
        await self.send_json({"type": "connected"})

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.calendar_group, self.channel_name)

    async def receive_json(self, content):
        """Handle incoming WebSocket messages."""
        message_type = content.get("type")

        # Handle first-message authentication
        if message_type == "authenticate":
            if self._authenticated:
                return
            token = content.get("token")
            if not token:
                await self.send_json({"type": "auth_error", "error": "Token required"})
                await self.close()
                return
            user = await self._authenticate_token(token)
            if user:
                self.user = user
                await self._setup_authenticated_calendar()
            else:
                await self.send_json({"type": "auth_error", "error": "Invalid token"})
                await self.close()
            return

        # Reject all other messages if not authenticated
        if not self._authenticated:
            await self.send_json({"type": "auth_error", "error": "Not authenticated"})
            await self.close()
            return

        # Rate-limit (B7)
        if self._check_rate_limit():
            await self.send_json({"type": "error", "error": "Rate limit exceeded"})
            return

        # Client doesn't normally send messages; server-only broadcast via helpers
        if message_type == "heartbeat":
            await self.send_json({"type": "heartbeat_ack"})

    async def calendar_update(self, event):
        """Forward calendar update to WebSocket client."""
        await self.send_json(event)
