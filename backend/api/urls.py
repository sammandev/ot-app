from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Import ViewSets and auth views from views.py
from . import views
from .health import HealthCheckDetailedView, HealthCheckView, LivenessCheckView, ReadinessCheckView

# API v1 Router (current stable)
v1_router = DefaultRouter()
v1_router.register(r"projects", views.ProjectViewSet, basename="project")
v1_router.register(r"employees", views.EmployeeViewSet, basename="employee")
v1_router.register(r"departments", views.DepartmentViewSet, basename="department")
v1_router.register(r"overtime-requests", views.OvertimeRequestViewSet, basename="overtime-request")
v1_router.register(r"overtime-regulations", views.OvertimeRegulationViewSet, basename="overtime-regulation")
v1_router.register(r"regulation-documents", views.OvertimeRegulationDocumentViewSet, basename="regulation-document")
v1_router.register(r"overtime-limits", views.OvertimeLimitConfigViewSet, basename="overtime-limit")
v1_router.register(r"calendar-events", views.CalendarEventViewSet, basename="calendar-event")
v1_router.register(r"users/access-control", views.UserAccessViewSet, basename="user-access-control")
v1_router.register(r"notifications", views.NotificationViewSet, basename="notification")
v1_router.register(r"activity-logs", views.UserActivityLogViewSet, basename="activity-log")
# Task Board Advanced Features
v1_router.register(r"task-comments", views.TaskCommentViewSet, basename="task-comment")
v1_router.register(r"task-subtasks", views.TaskSubtaskViewSet, basename="task-subtask")
v1_router.register(r"task-time-logs", views.TaskTimeLogViewSet, basename="task-time-log")
v1_router.register(r"task-activities", views.TaskActivityViewSet, basename="task-activity")
v1_router.register(r"board-presence", views.BoardPresenceViewSet, basename="board-presence")
# Holiday Calendar (new separate calendar for holidays and leaves)
v1_router.register(r"holidays", views.HolidayViewSet, basename="holiday")
v1_router.register(r"employee-leaves", views.EmployeeLeaveViewSet, basename="employee-leave")
# Kanban Advanced Features (Personal Notes, Groups, Attachments, Reminders)
v1_router.register(r"personal-notes", views.PersonalNoteViewSet, basename="personal-note")
v1_router.register(r"task-groups", views.TaskGroupViewSet, basename="task-group")
v1_router.register(r"task-attachments", views.TaskAttachmentViewSet, basename="task-attachment")
v1_router.register(r"task-reminders", views.TaskReminderViewSet, basename="task-reminder")
# Purchasing and Assets
v1_router.register(r"purchase-requests", views.PurchaseRequestViewSet, basename="purchase-request")
v1_router.register(r"assets", views.AssetViewSet, basename="asset")
# User Reports & Release Notes
v1_router.register(r"user-reports", views.UserReportViewSet, basename="user-report")
v1_router.register(r"release-notes", views.ReleaseNoteViewSet, basename="release-note")
v1_router.register(r"smb-configs", views.SMBConfigurationViewSet, basename="smb-config")

# API v2 Router (future; currently mirrors v1)
v2_router = DefaultRouter()
v2_router.register(r"projects", views.ProjectViewSet, basename="project-v2")
v2_router.register(r"employees", views.EmployeeViewSet, basename="employee-v2")
v2_router.register(r"departments", views.DepartmentViewSet, basename="department-v2")
v2_router.register(r"overtime-requests", views.OvertimeRequestViewSet, basename="overtime-request-v2")
v2_router.register(r"overtime-regulations", views.OvertimeRegulationViewSet, basename="overtime-regulation-v2")
v2_router.register(r"calendar-events", views.CalendarEventViewSet, basename="calendar-event-v2")

urlpatterns = [
    # Health check endpoints
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("health/detailed/", HealthCheckDetailedView.as_view(), name="health-check-detailed"),
    path("health/ready/", ReadinessCheckView.as_view(), name="readiness-check"),
    path("health/live/", LivenessCheckView.as_view(), name="liveness-check"),
    # API v1 endpoints (main routes)
    path("v1/", include(v1_router.urls)),
    path("v1/system/config/", views.SystemConfigurationView.as_view(), name="system-config-v1"),
    # Authentication endpoints (version-independent)
    path("auth/login/local/", views.LocalLoginView.as_view(), name="login-local"),
    path("auth/login/external/", views.ExternalLoginView.as_view(), name="login-external"),
    path("auth/token/verify/", views.TokenVerifyView.as_view(), name="token-verify"),
    path("auth/token/refresh/", views.TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/logout/", views.LogoutView.as_view(), name="logout"),
    path("auth/exchange-token/", views.ExchangeExternalTokenView.as_view(), name="exchange-token"),
    path("auth/me/", views.CurrentUserView.as_view(), name="current-user"),
    path("system/config/", views.SystemConfigurationView.as_view(), name="system-config"),
]
