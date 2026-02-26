"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from api.middleware import TokenAuthMiddlewareStack
from api.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        # Token-based auth handles WebSocket security; AllowedHostsOriginValidator
        # removed because cross-origin connections (frontend:3333 → backend:8008)
        # are rejected even when the hostname matches ALLOWED_HOSTS.
        "websocket": TokenAuthMiddlewareStack(AuthMiddlewareStack(URLRouter(websocket_urlpatterns))),
    }
)
