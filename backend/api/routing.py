"""
WebSocket routing configuration for Task Board real-time features.
"""

from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/board/$", consumers.BoardConsumer.as_asgi()),
    re_path(r"ws/board/task/(?P<task_id>\d+)/$", consumers.TaskDetailConsumer.as_asgi()),
    re_path(r"ws/notifications/$", consumers.NotificationConsumer.as_asgi()),
    re_path(r"ws/calendar/$", consumers.CalendarConsumer.as_asgi()),
]
