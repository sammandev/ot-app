"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from rest_framework import permissions


class V1OnlySchemaGenerator(OpenAPISchemaGenerator):
    """Custom schema generator that only includes v1 API routes."""

    def get_schema(self, request=None, public=False):
        """Generate schema excluding v2 routes."""
        schema = super().get_schema(request, public)

        # Filter out v2 paths
        paths_to_keep = {}
        for path_name, path_item in schema.paths.items():
            # Keep paths that don't contain /v2/
            if "/v2/" not in path_name:
                paths_to_keep[path_name] = path_item

        schema.paths = paths_to_keep
        return schema


schema_view = get_schema_view(
    openapi.Info(
        title="OT App API",
        default_version="v1",
        description="API documentation for Overtime Application",
        terms_of_service="",
        contact=openapi.Contact(email="samuel_halomoan@pegatroncorp.com"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

# Serve media files - explicit pattern that works with Daphne ASGI server
# The static() helper only works with DEBUG=True, so we use explicit re_path
urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
