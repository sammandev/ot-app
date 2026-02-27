from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .health import HealthCheckDetailedView, HealthCheckView, LivenessCheckView, ReadinessCheckView
from .views.assets import AssetViewSet, PurchaseRequestViewSet
from .views.auth import (
    CurrentUserView,
    ExchangeExternalTokenView,
    ExternalLoginView,
    LocalLoginView,
    LogoutView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views.calendar import CalendarEventViewSet
from .views.config import (
    ReleaseNoteViewSet,
    SMBConfigurationViewSet,
    SystemConfigurationView,
    UserAccessViewSet,
    UserActivityLogViewSet,
    UserReportViewSet,
)
from .views.employees import EmployeeViewSet
from .views.holidays import EmployeeLeaveViewSet, HolidayViewSet
from .views.notifications import NotificationViewSet
from .views.overtime import (
    OvertimeLimitConfigViewSet,
    OvertimeRegulationDocumentViewSet,
    OvertimeRegulationViewSet,
    OvertimeRequestViewSet,
)
from .views.personal_notes import PersonalNoteViewSet
from .views.projects import DepartmentViewSet, ProjectViewSet
from .views.tasks import (
    BoardPresenceViewSet,
    TaskActivityViewSet,
    TaskAttachmentViewSet,
    TaskCommentViewSet,
    TaskGroupViewSet,
    TaskReminderViewSet,
    TaskSubtaskViewSet,
    TaskTimeLogViewSet,
)

# API v1 Router (current stable)
v1_router = DefaultRouter()
v1_router.register(r"projects", ProjectViewSet, basename="project")
v1_router.register(r"employees", EmployeeViewSet, basename="employee")
v1_router.register(r"departments", DepartmentViewSet, basename="department")
v1_router.register(r"overtime-requests", OvertimeRequestViewSet, basename="overtime-request")
v1_router.register(r"overtime-regulations", OvertimeRegulationViewSet, basename="overtime-regulation")
v1_router.register(r"regulation-documents", OvertimeRegulationDocumentViewSet, basename="regulation-document")
v1_router.register(r"overtime-limits", OvertimeLimitConfigViewSet, basename="overtime-limit")
v1_router.register(r"calendar-events", CalendarEventViewSet, basename="calendar-event")
v1_router.register(r"users/access-control", UserAccessViewSet, basename="user-access-control")
v1_router.register(r"notifications", NotificationViewSet, basename="notification")
v1_router.register(r"activity-logs", UserActivityLogViewSet, basename="activity-log")
# Task Board Advanced Features
v1_router.register(r"task-comments", TaskCommentViewSet, basename="task-comment")
v1_router.register(r"task-subtasks", TaskSubtaskViewSet, basename="task-subtask")
v1_router.register(r"task-time-logs", TaskTimeLogViewSet, basename="task-time-log")
v1_router.register(r"task-activities", TaskActivityViewSet, basename="task-activity")
v1_router.register(r"board-presence", BoardPresenceViewSet, basename="board-presence")
# Holiday Calendar (new separate calendar for holidays and leaves)
v1_router.register(r"holidays", HolidayViewSet, basename="holiday")
v1_router.register(r"employee-leaves", EmployeeLeaveViewSet, basename="employee-leave")
# Kanban Advanced Features (Personal Notes, Groups, Attachments, Reminders)
v1_router.register(r"personal-notes", PersonalNoteViewSet, basename="personal-note")
v1_router.register(r"task-groups", TaskGroupViewSet, basename="task-group")
v1_router.register(r"task-attachments", TaskAttachmentViewSet, basename="task-attachment")
v1_router.register(r"task-reminders", TaskReminderViewSet, basename="task-reminder")
# Purchasing and Assets
v1_router.register(r"purchase-requests", PurchaseRequestViewSet, basename="purchase-request")
v1_router.register(r"assets", AssetViewSet, basename="asset")
# User Reports & Release Notes
v1_router.register(r"user-reports", UserReportViewSet, basename="user-report")
v1_router.register(r"release-notes", ReleaseNoteViewSet, basename="release-note")
v1_router.register(r"smb-configs", SMBConfigurationViewSet, basename="smb-config")

urlpatterns = [
    # Health check endpoints
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("health/detailed/", HealthCheckDetailedView.as_view(), name="health-check-detailed"),
    path("health/ready/", ReadinessCheckView.as_view(), name="readiness-check"),
    path("health/live/", LivenessCheckView.as_view(), name="liveness-check"),
    # API v1 endpoints (main routes)
    path("v1/", include(v1_router.urls)),
    path("v1/system/config/", SystemConfigurationView.as_view(), name="system-config-v1"),
    # Authentication endpoints (version-independent)
    path("auth/login/local/", LocalLoginView.as_view(), name="login-local"),
    path("auth/login/external/", ExternalLoginView.as_view(), name="login-external"),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token-verify"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/exchange-token/", ExchangeExternalTokenView.as_view(), name="exchange-token"),
    path("auth/me/", CurrentUserView.as_view(), name="current-user"),
]
