from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APIClient
from openpyxl import Workbook

from django.db import IntegrityError

from api.models import BoardPresence, CalendarEvent, Department, Employee, EmployeeLeave, ExternalUser, OvertimeRequest, Project, PurchaseRequest, SystemConfiguration, TaskAttachment, TaskGroup, TaskSubtask, TaskTimeLog, UserActivityLog, UserSession
from api.services.leave_notification_service import ensure_leave_preview_token, resolve_leave_agent_notification_recipients, resolve_leave_notification_recipients
from api.tasks import cleanup_user_activity_logs


TEST_MEDIA_ROOT = Path(settings.BASE_DIR) / "test_media"
User = get_user_model()


def aware_dt(year, month, day, hour=0, minute=0):
    return timezone.make_aware(datetime(year, month, day, hour, minute))


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class TaskAttachmentAuthorizationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.department = Department.objects.create(code="ENG", name="Engineering")
        self.project = Project.objects.create(name="Alpha")
        self.creator_employee = Employee.objects.create(name="Creator User", emp_id="E001", department=self.department)
        self.uploader_employee = Employee.objects.create(name="Uploader User", emp_id="E002", department=self.department)

        self.creator_user = self._make_user("creator", 1, "E001")
        self.uploader_user = self._make_user("uploader", 2, "E002")
        self.non_employee_user = self._make_user("outsider", 3, None)
        self.admin_user = self._make_user("admin", 4, None, is_ptb_admin=True)

        self.task = CalendarEvent.objects.create(
            title="Secured task",
            event_type="task",
            start=aware_dt(2026, 3, 1, 9, 0),
            end=aware_dt(2026, 3, 1, 10, 0),
            created_by=self.creator_employee,
            project=self.project,
        )
        self.task.assigned_to.add(self.uploader_employee)

        self.attachment = TaskAttachment.objects.create(
            task=self.task,
            file=self._uploaded_file("evidence.txt"),
            filename="evidence.txt",
            file_size=5,
            file_type="text/plain",
            uploaded_by=self.uploader_employee,
        )

    def tearDown(self):
        if TEST_MEDIA_ROOT.exists():
            for path in sorted(TEST_MEDIA_ROOT.rglob("*"), reverse=True):
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    path.rmdir()

    def _make_user(self, username, external_id, worker_id, is_ptb_admin=False):
        return ExternalUser.objects.create(
            external_id=external_id,
            username=username,
            email=f"{username}@example.com",
            worker_id=worker_id,
            is_ptb_admin=is_ptb_admin,
            is_active=True,
            is_superuser=False,
            is_staff=is_ptb_admin,
            date_joined=aware_dt(2026, 1, 1),
        )

    def _uploaded_file(self, name):
        return SimpleUploadedFile(name, b"hello", content_type="text/plain")

    def test_non_employee_cannot_delete_someone_elses_attachment(self):
        self.client.force_authenticate(self.non_employee_user)

        response = self.client.delete(reverse("task-attachment-detail", args=[self.attachment.id]))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(TaskAttachment.objects.filter(id=self.attachment.id).exists())

    def test_owner_can_delete_attachment(self):
        self.client.force_authenticate(self.uploader_user)

        response = self.client.delete(reverse("task-attachment-detail", args=[self.attachment.id]))

        self.assertEqual(response.status_code, 204)
        self.assertFalse(TaskAttachment.objects.filter(id=self.attachment.id).exists())

    def test_admin_can_delete_attachment_without_employee_record(self):
        self.client.force_authenticate(self.admin_user)

        response = self.client.delete(reverse("task-attachment-detail", args=[self.attachment.id]))

        self.assertEqual(response.status_code, 204)
        self.assertFalse(TaskAttachment.objects.filter(id=self.attachment.id).exists())


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class TaskEndpointAuthorizationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.department = Department.objects.create(code="QA", name="Quality")
        self.project = Project.objects.create(name="Beta")
        self.creator_employee = Employee.objects.create(name="Task Creator", emp_id="Q001", department=self.department)
        self.assigned_employee = Employee.objects.create(name="Task Assignee", emp_id="Q002", department=self.department)

        self.creator_user = self._make_user("task_creator", 11, "Q001")
        self.assigned_user = self._make_user("task_assignee", 12, "Q002")
        self.outsider_user = self._make_user("task_outsider", 13, None)

        self.task = CalendarEvent.objects.create(
            title="Restricted task",
            event_type="task",
            start=aware_dt(2026, 3, 2, 9, 0),
            end=aware_dt(2026, 3, 2, 11, 0),
            created_by=self.creator_employee,
            project=self.project,
        )
        self.task.assigned_to.add(self.assigned_employee)

        self.subtask = TaskSubtask.objects.create(
            task=self.task,
            title="Checklist",
            created_by=self.creator_employee,
            order=1,
        )
        self.running_log = TaskTimeLog.objects.create(
            task=self.task,
            employee=self.assigned_employee,
            description="In progress",
            started_at=aware_dt(2026, 3, 2, 9, 0),
            is_running=True,
        )

    def _make_user(self, username, external_id, worker_id):
        return ExternalUser.objects.create(
            external_id=external_id,
            username=username,
            email=f"{username}@example.com",
            worker_id=worker_id,
            is_active=True,
            is_superuser=False,
            is_staff=False,
            date_joined=aware_dt(2026, 1, 1),
        )

    def test_outsider_cannot_create_comment_for_inaccessible_task(self):
        self.client.force_authenticate(self.outsider_user)

        response = self.client.post("/api/v1/task-comments/", {"task": self.task.id, "content": "No access"}, format="json")

        self.assertEqual(response.status_code, 403)

    def test_assigned_user_can_create_comment_for_accessible_task(self):
        self.client.force_authenticate(self.assigned_user)

        response = self.client.post("/api/v1/task-comments/", {"task": self.task.id, "content": "Looks good"}, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["task"], self.task.id)

    def test_outsider_cannot_reorder_subtasks_for_inaccessible_task(self):
        self.client.force_authenticate(self.outsider_user)

        response = self.client.post(
            "/api/v1/task-subtasks/reorder/",
            {"task_id": self.task.id, "subtask_ids": [self.subtask.id]},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_outsider_cannot_view_time_summary_for_inaccessible_task(self):
        self.client.force_authenticate(self.outsider_user)

        response = self.client.get("/api/v1/task-time-logs/summary/", {"task_id": self.task.id})

        self.assertEqual(response.status_code, 403)

    def test_creator_cannot_stop_another_users_running_timer(self):
        self.client.force_authenticate(self.creator_user)

        response = self.client.post(f"/api/v1/task-time-logs/{self.running_log.id}/stop_timer/")

        self.assertEqual(response.status_code, 403)


class OvertimeRequestUniquenessTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(code="OT", name="Overtime")
        self.project = Project.objects.create(name="Gamma")
        self.employee = Employee.objects.create(name="Overtime User", emp_id="OT001", department=self.department)

    def _create_request(self, request_date):
        return OvertimeRequest.objects.create(
            employee=self.employee,
            employee_name=self.employee.name,
            department=self.department,
            department_code=self.department.code,
            project=self.project,
            project_name=self.project.name,
            request_date=request_date,
            time_start=datetime(2026, 3, 3, 18, 0).time(),
            time_end=datetime(2026, 3, 3, 20, 0).time(),
            total_hours="2.00",
            reason="Release support",
        )

    def test_duplicate_employee_project_date_is_blocked_by_model_constraint(self):
        self._create_request(datetime(2026, 3, 3).date())

        with self.assertRaises(IntegrityError):
            self._create_request(datetime(2026, 3, 3).date())


class PublicAuthEndpointCookieIsolationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.local_password = "secret123"
        self.local_user = User.objects.create_user(
            username="local_login_user",
            password=self.local_password,
            email="local_login_user@example.com",
        )
        self.external_user = ExternalUser.objects.create(
            external_id=801,
            username="external_login_user",
            email="external_login_user@example.com",
            worker_id="EX801",
            is_active=True,
            is_superuser=False,
            is_staff=False,
            date_joined=aware_dt(2026, 1, 1),
        )
        self.client.cookies["access_token"] = "stale.invalid.access.token"

    @patch("api.views.auth.ExternalAuthService.get_user_info")
    @patch("api.views.auth.ExternalAuthService.login")
    def test_external_login_ignores_stale_access_cookie(self, mocked_login, mocked_get_user_info):
        mocked_login.return_value = {
            "access": "fresh.external.access",
            "refresh": "fresh.external.refresh",
            "user_data": {},
        }
        mocked_get_user_info.return_value = {
            "id": self.external_user.external_id,
            "username": self.external_user.username,
            "email": self.external_user.email,
            "first_name": "External",
            "last_name": "User",
            "is_active": True,
            "is_superuser": False,
            "is_staff": False,
            "worker_id": self.external_user.worker_id,
            "is_ptb_admin": False,
            "groups": [],
            "permissions": {},
            "date_joined": aware_dt(2026, 1, 1),
        }

        response = self.client.post(
            reverse("login-external"),
            {"username": "external_login_user", "password": "correct-password"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user"]["username"], self.external_user.username)
        mocked_login.assert_called_once_with("external_login_user", "correct-password")

    def test_local_login_ignores_stale_access_cookie(self):
        response = self.client.post(
            reverse("login-local"),
            {"username": self.local_user.username, "password": self.local_password},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user"]["username"], self.local_user.username)

    @patch("api.views.auth.ExternalAuthService.get_user_info")
    def test_exchange_external_token_uses_posted_token_not_stale_cookie(self, mocked_get_user_info):
        mocked_get_user_info.return_value = {
            "id": self.external_user.external_id,
            "username": self.external_user.username,
            "email": self.external_user.email,
            "first_name": "External",
            "last_name": "User",
            "is_active": True,
            "is_superuser": False,
            "is_staff": False,
            "worker_id": self.external_user.worker_id,
            "is_ptb_admin": False,
            "groups": [],
            "permissions": {},
            "date_joined": aware_dt(2026, 1, 1),
        }

        response = self.client.post(
            reverse("exchange-token"),
            {"token": "posted.valid.external.token"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        mocked_get_user_info.assert_called_once_with("posted.valid.external.token")

    @patch("api.views.auth.ExternalAuthService.refresh_token")
    def test_token_refresh_uses_refresh_cookie_not_stale_access_cookie(self, mocked_refresh):
        self.client.cookies["refresh_token"] = "valid-refresh-token"
        mocked_refresh.return_value = "fresh.external.access"

        response = self.client.post(reverse("token-refresh"), format="json")

        self.assertEqual(response.status_code, 200)
        mocked_refresh.assert_called_once_with("valid-refresh-token")

    @patch("api.views.auth.ExternalAuthService.login")
    def test_external_login_still_returns_normal_invalid_credentials_error(self, mocked_login):
        mocked_login.side_effect = AuthenticationFailed("Invalid username or password")

        response = self.client.post(
            reverse("login-external"),
            {"username": "external_login_user", "password": "wrong-password"},
            format="json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["detail"], "Authentication failed.")


class ExternalLeaveAgentLookupTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.external_user = ExternalUser.objects.create(
            external_id=201,
            username="lookup_user",
            email="lookup_user@example.com",
            worker_id="LK001",
            is_active=True,
            is_superuser=False,
            is_staff=False,
            date_joined=aware_dt(2026, 1, 1),
        )
        self.local_user = User.objects.create_user(username="local_lookup_user", password="secret123")
        self.session = UserSession.objects.create(
            user=self.external_user,
            access_token="external-access-token",
            refresh_token="external-refresh-token",
            token_issued_at=aware_dt(2027, 3, 1, 8, 0),
            token_expires_at=aware_dt(2027, 3, 1, 12, 0),
            ip_address="127.0.0.1",
            user_agent="pytest",
        )

    @patch("api.views.holidays.ExternalAuthService.lookup_user_accounts")
    def test_external_user_can_lookup_leave_agents(self, mocked_lookup):
        mocked_lookup.return_value = [
            {
                "username": "Agent_One",
                "email": "agent.one@example.com",
                "employee": {"worker_id": "AG001", "site": "JKT"},
            }
        ]
        self.client.force_authenticate(self.external_user)

        response = self.client.get(reverse("employee-leave-agent-lookup"), {"keyword": "ag"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0],
            {
                "username": "Agent_One",
                "email": "agent.one@example.com",
                "worker_id": "AG001",
                "site": "JKT",
                "source": "external_lookup",
            },
        )
        mocked_lookup.assert_called_once_with("external-access-token", keyword="ag")

    @patch("api.views.holidays.ExternalAuthService.lookup_user_accounts")
    def test_short_keyword_is_rejected_before_upstream_call(self, mocked_lookup):
        self.client.force_authenticate(self.external_user)

        response = self.client.get(reverse("employee-leave-agent-lookup"), {"keyword": "a"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "invalid_lookup_keyword")
        mocked_lookup.assert_not_called()

    def test_local_user_cannot_use_external_agent_lookup(self):
        self.client.force_authenticate(self.local_user)

        response = self.client.get(reverse("employee-leave-agent-lookup"), {"keyword": "agent"})

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["code"], "external_lookup_requires_external_session")


class EmployeeLeaveExternalAgentPersistenceTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.department = Department.objects.create(code="HR", name="Human Resources")
        self.employee = Employee.objects.create(name="Leave Owner", emp_id="LV001", department=self.department)
        self.local_agent = Employee.objects.create(name="Local Agent", emp_id="AG001", department=self.department)
        self.user = ExternalUser.objects.create(
            external_id=301,
            username="leave_owner",
            email="leave_owner@example.com",
            worker_id="LV001",
            is_active=True,
            is_superuser=False,
            is_staff=False,
            date_joined=aware_dt(2026, 1, 1),
        )
        self.client.force_authenticate(self.user)
        self.external_agents_payload = [
            {
                "username": "Agent External",
                "email": "agent.external@example.com",
                "worker_id": "EXT001",
                "site": "JKT",
                "source": "external_lookup",
            }
        ]
        self.unified_agents_payload = [
            {
                "type": "employee",
                "employee_id": self.local_agent.id,
                "name": self.local_agent.name,
                "emp_id": self.local_agent.emp_id,
            },
            {
                "type": "external",
                "username": "Agent External",
                "email": "agent.external@example.com",
                "worker_id": "EXT001",
                "site": "JKT",
                "source": "external_lookup",
            },
            {
                "type": "manual",
                "name": "Manual Backup",
            },
        ]

    @patch("api.views.holidays.EmployeeLeaveViewSet._schedule_leave_created_side_effects")
    @patch("api.views.holidays.EmployeeLeaveViewSet._queue_leave_email_notification")
    def test_create_batch_persists_unified_agents(self, mocked_queue_email, mocked_schedule):
        response = self.client.post(
            "/api/v1/employee-leaves/batch/",
            {
                "employee": self.employee.id,
                "dates": ["2026-04-01", "2026-04-02"],
                "agents": self.unified_agents_payload,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data[0]["agents"],
            [
                {
                    "type": "employee",
                    "employee_id": self.local_agent.id,
                    "name": self.local_agent.name,
                    "emp_id": self.local_agent.emp_id,
                    "dept_code": self.department.code,
                },
                {
                    "type": "external",
                    "username": "Agent External",
                    "email": "agent.external@example.com",
                    "worker_id": "EXT001",
                    "site": "JKT",
                    "source": "external_lookup",
                },
                {
                    "type": "manual",
                    "name": "Manual Backup",
                },
            ],
        )
        self.assertEqual(EmployeeLeave.objects.count(), 2)
        created_leave = EmployeeLeave.objects.order_by("date").first()
        self.assertEqual(created_leave.external_agents, self.external_agents_payload)
        self.assertEqual(created_leave.agent_names, "Manual Backup")
        self.assertEqual(list(created_leave.agents.values_list("id", flat=True)), [self.local_agent.id])
        mocked_schedule.assert_called()
        mocked_queue_email.assert_not_called()

    @patch("api.views.holidays.EmployeeLeaveViewSet._schedule_leave_created_side_effects")
    @patch("api.views.holidays.EmployeeLeaveViewSet._queue_leave_email_notification")
    def test_create_batch_accepts_empty_agents_array(self, mocked_queue_email, mocked_schedule):
        response = self.client.post(
            "/api/v1/employee-leaves/batch/",
            {
                "employee": self.employee.id,
                "dates": ["2026-04-05"],
                "agents": [],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data[0]["agents"], [])
        created_leave = EmployeeLeave.objects.get(employee=self.employee, date="2026-04-05")
        self.assertEqual(created_leave.external_agents, [])
        self.assertIsNone(created_leave.agent_names)
        self.assertEqual(list(created_leave.agents.values_list("id", flat=True)), [])
        mocked_schedule.assert_called_once()
        mocked_queue_email.assert_not_called()

    @patch("api.views.holidays.EmployeeLeaveViewSet._schedule_leave_created_side_effects")
    @patch("api.views.holidays.EmployeeLeaveViewSet._queue_leave_email_notification")
    def test_create_batch_accepts_missing_agents_field(self, mocked_queue_email, mocked_schedule):
        response = self.client.post(
            "/api/v1/employee-leaves/batch/",
            {
                "employee": self.employee.id,
                "dates": ["2026-04-06"],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data[0]["agents"], [])
        created_leave = EmployeeLeave.objects.get(employee=self.employee, date="2026-04-06")
        self.assertEqual(created_leave.external_agents, [])
        self.assertIsNone(created_leave.agent_names)
        self.assertEqual(list(created_leave.agents.values_list("id", flat=True)), [])
        mocked_schedule.assert_called_once()
        mocked_queue_email.assert_not_called()

    @patch("api.views.holidays.EmployeeLeaveViewSet._broadcast_leave_batch_changes")
    @patch("api.views.holidays.EmployeeLeaveViewSet._queue_leave_email_notification")
    def test_update_batch_persists_unified_agents(self, mocked_queue_email, mocked_broadcast):
        leave = EmployeeLeave.objects.create(
            employee=self.employee,
            date=datetime(2026, 4, 1).date(),
            created_by=self.user,
            external_agents=[],
        )

        response = self.client.patch(
            "/api/v1/employee-leaves/batch-update/",
            {
                "leave_ids": [leave.id],
                "employee": self.employee.id,
                "dates": ["2026-04-03"],
                "agents": self.unified_agents_payload,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        updated_leave = EmployeeLeave.objects.get(pk=response.data[0]["id"])
        self.assertEqual(updated_leave.date.isoformat(), "2026-04-03")
        self.assertEqual(updated_leave.external_agents, self.external_agents_payload)
        self.assertEqual(updated_leave.agent_names, "Manual Backup")
        self.assertEqual(list(updated_leave.agents.values_list("id", flat=True)), [self.local_agent.id])
        mocked_broadcast.assert_called_once()
        mocked_queue_email.assert_not_called()

    def test_create_batch_rejects_external_agents_without_email(self):
        response = self.client.post(
            "/api/v1/employee-leaves/batch/",
            {
                "employee": self.employee.id,
                "dates": ["2026-04-01"],
                "agents": [
                    {
                        "type": "external",
                        "username": "Broken Agent",
                        "worker_id": "EXT404",
                    }
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("agents", response.data.get("details", {}))


class LeaveNotificationRecipientResolutionTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(code="OPS", name="Operations")
        self.leave_owner = Employee.objects.create(name="Leave Owner", emp_id="OWN001", department=self.department)
        self.local_agent = Employee.objects.create(name="Local Agent", emp_id="AG001", department=self.department)
        self.creator = ExternalUser.objects.create(
            external_id=401,
            username="leave_creator",
            email="leave_creator@example.com",
            worker_id="OWN001",
            is_active=True,
            is_superuser=False,
            is_staff=False,
            date_joined=aware_dt(2026, 1, 1),
        )
        ExternalUser.objects.create(
            external_id=402,
            username="local_agent_user",
            email="Local.Agent@Example.com",
            worker_id="AG001",
            is_active=True,
            is_superuser=False,
            is_staff=False,
            date_joined=aware_dt(2026, 1, 1),
        )

    def test_resolve_leave_agent_notification_recipients_merges_local_and_external_emails(self):
        leave = EmployeeLeave.objects.create(
            employee=self.leave_owner,
            date=datetime(2026, 4, 10).date(),
            created_by=self.creator,
            external_agents=[
                {
                    "username": "External One",
                    "email": "external.one@example.com",
                    "worker_id": "EXT001",
                    "source": "external_lookup",
                },
                {
                    "username": "Duplicate External",
                    "email": "external.one@example.com",
                    "worker_id": "EXT002",
                    "source": "external_lookup",
                },
                {
                    "username": "Local Agent Duplicate",
                    "email": "local.agent@example.com",
                    "worker_id": "AG001",
                    "source": "external_lookup",
                },
            ],
        )
        leave.agents.add(self.local_agent)

        recipients = resolve_leave_agent_notification_recipients([leave])

        self.assertCountEqual(recipients, ["local.agent@example.com", "external.one@example.com"])
        self.assertEqual(len(recipients), 2)

    def test_resolve_leave_notification_recipients_merges_employee_group_and_global_recipients(self):
        config = SystemConfiguration.objects.create(
            leave_notification_recipient_mode="global",
            leave_notification_recipients=["global@pegatroncorp.com"],
            leave_notification_employee_groups=[
                {
                    "id": "ops-team",
                    "name": "OPS Team",
                    "employee_ids": [self.leave_owner.id],
                    "recipients": ["group@pegatroncorp.com"],
                }
            ],
            leave_notification_employee_recipients=[
                {
                    "employee_id": self.leave_owner.id,
                    "recipients": ["owner@pegatroncorp.com"],
                    "group_ids": ["ops-team"],
                }
            ],
        )

        recipients = resolve_leave_notification_recipients(config, self.leave_owner)

        self.assertCountEqual(
            recipients,
            ["owner@pegatroncorp.com", "group@pegatroncorp.com", "global@pegatroncorp.com"],
        )

    def test_resolve_leave_notification_recipients_merges_group_membership_with_department_mode(self):
        config = SystemConfiguration.objects.create(
            leave_notification_recipient_mode="department",
            leave_notification_department_recipients=[{"department_code": "OPS", "recipients": ["department@pegatroncorp.com"]}],
            leave_notification_employee_groups=[
                {
                    "id": "coverage",
                    "name": "Coverage",
                    "employee_ids": [self.leave_owner.id],
                    "recipients": ["coverage@pegatroncorp.com"],
                }
            ],
        )

        recipients = resolve_leave_notification_recipients(config, self.leave_owner)

        self.assertCountEqual(recipients, ["coverage@pegatroncorp.com", "department@pegatroncorp.com"])


class UserActivityLogCleanupTests(TestCase):
    def setUp(self):
        self.user = ExternalUser.objects.create(
            external_id=901,
            username="activity_admin",
            email="activity_admin@example.com",
            worker_id="ACT901",
            is_active=True,
            is_superuser=False,
            is_staff=False,
            date_joined=aware_dt(2026, 1, 1),
        )

    def test_cleanup_user_activity_logs_deletes_only_logs_older_than_retention(self):
        SystemConfiguration.objects.create(user_activity_log_retention_days=7)
        old_log = UserActivityLog.objects.create(user=self.user, action="login")
        recent_log = UserActivityLog.objects.create(user=self.user, action="logout")
        UserActivityLog.objects.filter(pk=old_log.pk).update(timestamp=timezone.now() - timezone.timedelta(days=8))
        UserActivityLog.objects.filter(pk=recent_log.pk).update(timestamp=timezone.now() - timezone.timedelta(days=2))

        result = cleanup_user_activity_logs()

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["deleted_count"], 1)
        self.assertFalse(UserActivityLog.objects.filter(pk=old_log.pk).exists())
        self.assertTrue(UserActivityLog.objects.filter(pk=recent_log.pk).exists())


class LeavePreviewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.department = Department.objects.create(code="OPS", name="Operations")
        self.employee = Employee.objects.create(name="Preview Employee", emp_id="MW2400549", department=self.department)
        self.employee_external_user = ExternalUser.objects.create(
            external_id=501,
            username="preview_employee",
            email="preview.employee@example.com",
            worker_id="MW2400549",
            is_active=True,
            is_superuser=False,
            is_staff=False,
            date_joined=aware_dt(2026, 1, 1),
        )
        self.creator = ExternalUser.objects.create(
            external_id=502,
            username="preview_creator",
            email="preview.creator@example.com",
            worker_id="CR001",
            is_active=True,
            is_superuser=False,
            is_staff=False,
            date_joined=aware_dt(2026, 1, 1),
        )
        self.leave = EmployeeLeave.objects.create(
            employee=self.employee,
            date=datetime(2026, 4, 9).date(),
            created_by=self.creator,
            batch_key="6d6d3c95-3d25-4dbe-bf44-3bf9d5849b9c",
            external_agents=[],
            notes="Preview note",
        )

    def test_preview_includes_employee_email(self):
        token = ensure_leave_preview_token(self.leave.batch_key)

        response = self.client.get(reverse("employee-leave-preview"), {"token": token})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["employee_id"], "MW2400549")
        self.assertEqual(response.data["employee_email"], "preview.employee@example.com")

    def test_rotating_preview_token_invalidates_old_link(self):
        first_token = ensure_leave_preview_token(self.leave.batch_key)
        self.leave.notes = "Updated preview note"
        self.leave.save(update_fields=["notes"])

        from api.services.leave_notification_service import rotate_leave_preview_token

        second_token = rotate_leave_preview_token(self.leave.batch_key)

        first_response = self.client.get(reverse("employee-leave-preview"), {"token": first_token})
        second_response = self.client.get(reverse("employee-leave-preview"), {"token": second_token})

        self.assertEqual(first_response.status_code, 400)
        self.assertEqual(second_response.status_code, 200)


class DocumentMetadataSecurityTests(TestCase):
    def test_fetch_link_metadata_rejects_private_ip_urls(self):
        from api.services.document_metadata import fetch_link_metadata

        metadata = fetch_link_metadata("http://127.0.0.1/internal")

        self.assertEqual(metadata["metadata_status"], "failed")
        self.assertIn("not allowed", metadata["metadata_error"].lower())

    @patch("api.services.document_metadata.socket.getaddrinfo")
    def test_fetch_link_metadata_rejects_hostnames_resolving_to_private_ip(self, mocked_getaddrinfo):
        from api.services.document_metadata import fetch_link_metadata

        mocked_getaddrinfo.return_value = [(None, None, None, None, ("10.0.0.5", 443))]

        metadata = fetch_link_metadata("https://example.com/docs")

        self.assertEqual(metadata["metadata_status"], "failed")
        self.assertIn("internal networks", metadata["metadata_error"].lower())

    @patch("api.services.document_metadata.socket.getaddrinfo")
    @patch("api.services.document_metadata.MetadataSession.get")
    def test_fetch_link_metadata_allows_safe_public_url(self, mocked_get, mocked_getaddrinfo):
        from api.services.document_metadata import fetch_link_metadata

        mocked_getaddrinfo.return_value = [(None, None, None, None, ("93.184.216.34", 443))]
        response = Mock()
        response.url = "https://example.com/docs"
        response.headers = {"Content-Type": "text/html; charset=utf-8"}
        response.encoding = "utf-8"
        response.apparent_encoding = "utf-8"
        response.iter_content.return_value = [b"<html><head><title>Docs</title></head><body></body></html>"]
        response.raise_for_status.return_value = None
        mocked_get.return_value = response

        metadata = fetch_link_metadata("https://example.com/docs")

        self.assertEqual(metadata["metadata_status"], "success")
        self.assertEqual(metadata["link_title"], "Docs")


class HealthEndpointSanitizationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch("api.health.connection.cursor")
    def test_detailed_health_hides_database_exception_details(self, mocked_cursor):
        mocked_cursor.side_effect = Exception("sensitive-db-host.internal")

        response = self.client.get(reverse("health-check-detailed"))

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.data["checks"]["database"]["message"], "Database unavailable")
        self.assertNotIn("sensitive-db-host.internal", str(response.data))

    @patch("api.health.connection.cursor")
    def test_readiness_hides_exception_details(self, mocked_cursor):
        mocked_cursor.side_effect = Exception("redis://secret-host")

        response = self.client.get(reverse("readiness-check"))

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.data["message"], "Critical dependencies unavailable")
        self.assertNotIn("secret-host", str(response.data))


class PurchaseRequestImportTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = ExternalUser.objects.create(
            external_id=999,
            username="import_admin",
            email="import_admin@example.com",
            is_active=True,
            is_staff=False,
            is_superuser=False,
            role="developer",
            date_joined=aware_dt(2026, 1, 1),
        )
        self.client.force_authenticate(self.user)

    def _build_excel_upload(self, rows_by_sheet):
        workbook = Workbook()
        first_sheet = True
        for sheet_name, rows in rows_by_sheet.items():
            sheet = workbook.active if first_sheet else workbook.create_sheet(sheet_name)
            sheet.title = sheet_name
            first_sheet = False
            headers = list(rows[0].keys())
            sheet.append(headers)
            for row in rows:
                sheet.append([row.get(header) for header in headers])

        from io import BytesIO

        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)
        return SimpleUploadedFile(
            "purchase_requests.xlsx",
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def test_import_is_idempotent_and_updates_existing_row(self):
        initial_file = self._build_excel_upload(
            {
                "List of Purchase": [
                    {
                        "Request Date": "03/04/2026",
                        "Owner": "Alice",
                        "Doc ID": "DOC-1",
                        "Part No.": "PART-9",
                        "Description-Spec": "Motor",
                        "Material Category": "Mechanical",
                        "Purpose/Desc.": "Repair",
                        "Qty": "2",
                        "Plant": "A1",
                        "Project Code": "PROJ-7",
                        "PR Type": "NORMAL",
                        "MRPID": "MRP-1",
                        "Purch. Org.": "ORG",
                        "Sourcer Price": "10 USD",
                        "PR No.": "PR-001",
                        "Remarks": "Initial",
                    }
                ]
            }
        )

        first_response = self.client.post(
            "/api/v1/purchase-requests/import_data/",
            {"file": initial_file},
            format="multipart",
        )

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(first_response.data["created"], 1)
        self.assertEqual(first_response.data["updated"], 0)
        self.assertEqual(first_response.data["skipped"], 0)
        self.assertEqual(PurchaseRequest.objects.count(), 1)

        updated_file = self._build_excel_upload(
            {
                "List of Purchase": [
                    {
                        "Request Date": "03/04/2026",
                        "Owner": "Alice",
                        "Doc ID": "DOC-1",
                        "Part No.": "PART-9",
                        "Description-Spec": "Motor",
                        "Material Category": "Mechanical",
                        "Purpose/Desc.": "Repair",
                        "Qty": "5",
                        "Plant": "A1",
                        "Project Code": "PROJ-7",
                        "PR Type": "NORMAL",
                        "MRPID": "MRP-1",
                        "Purch. Org.": "ORG",
                        "Sourcer Price": "12 USD",
                        "PR No.": "PR-001-UPDATED",
                        "Remarks": "Updated",
                    }
                ]
            }
        )

        second_response = self.client.post(
            "/api/v1/purchase-requests/import_data/",
            {"file": updated_file},
            format="multipart",
        )

        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(second_response.data["created"], 0)
        self.assertEqual(second_response.data["updated"], 1)
        self.assertEqual(second_response.data["skipped"], 0)
        self.assertEqual(PurchaseRequest.objects.count(), 1)

        purchase_request = PurchaseRequest.objects.get()
        self.assertEqual(str(purchase_request.qty), "5.00")
        self.assertEqual(purchase_request.pr_no, "PR-001-UPDATED")
        self.assertEqual(purchase_request.remarks, "Updated")

    def test_import_deduplicates_duplicate_rows_within_same_file(self):
        duplicate_row = {
            "Request Date": "03/05/2026",
            "Owner": "Bob",
            "Doc ID": "DOC-2",
            "Part No.": "PART-2",
            "Description-Spec": "Cable",
            "Material Category": "Electrical",
            "Purpose/Desc.": "Install",
            "Qty": "1",
            "Plant": "A2",
            "Project Code": "PROJ-8",
            "PR Type": "NORMAL",
            "MRPID": "MRP-2",
            "Purch. Org.": "ORG",
            "Sourcer Price": "2 USD",
            "PR No.": "PR-002",
            "Remarks": "Duplicate",
        }
        upload = self._build_excel_upload(
            {
                "List of Purchase": [duplicate_row, dict(duplicate_row)],
                "Done": [dict(duplicate_row)],
            }
        )

        response = self.client.post(
            "/api/v1/purchase-requests/import_data/",
            {"file": upload},
            format="multipart",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["created"], 1)
        self.assertEqual(response.data["updated"], 0)
        self.assertEqual(response.data["skipped"], 0)
        self.assertEqual(PurchaseRequest.objects.count(), 1)


class BoardPresenceHeartbeatTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.department = Department.objects.create(code="KB", name="Kanban")
        self.employee = Employee.objects.create(name="Realtime User", emp_id="KB001", department=self.department)
        self.user = ExternalUser.objects.create(
            external_id=1200,
            username="realtime_user",
            email="realtime_user@example.com",
            worker_id="KB001",
            is_active=True,
            is_staff=False,
            is_superuser=False,
            date_joined=aware_dt(2026, 1, 1),
        )
        self.client.force_authenticate(self.user)

    def test_http_heartbeat_reuses_existing_presence_record(self):
        first_response = self.client.post(
            "/api/v1/board-presence/heartbeat/",
            {"editing_task_id": None, "channel_name": "chan-1"},
            format="json",
        )

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(self.employee.board_presences.count(), 1)

        second_response = self.client.post(
            "/api/v1/board-presence/heartbeat/",
            {"editing_task_id": None, "channel_name": "chan-1"},
            format="json",
        )

        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(self.employee.board_presences.count(), 1)

    def test_http_heartbeat_updates_existing_presence_row(self):
        BoardPresence.objects.create(user=self.employee, channel_name="chan-old")

        response = self.client.post(
            "/api/v1/board-presence/heartbeat/",
            {"editing_task_id": None, "channel_name": "chan-new"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.employee.board_presences.count(), 1)
        self.assertEqual(self.employee.board_presences.first().channel_name, "chan-new")


class TaskDeletionPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.department = Department.objects.create(code="TD", name="Tasks")
        self.project = Project.objects.create(name="Delete Test")
        self.creator_employee = Employee.objects.create(name="Task Owner", emp_id="TD001", department=self.department)
        self.developer_employee = Employee.objects.create(name="Task Developer", emp_id="TD002", department=self.department)
        self.creator_user = ExternalUser.objects.create(
            external_id=1401,
            username="task_owner",
            email="task_owner@example.com",
            worker_id="TD001",
            is_active=True,
            is_staff=False,
            is_superuser=False,
            date_joined=aware_dt(2026, 1, 1),
        )
        self.developer_user = ExternalUser.objects.create(
            external_id=1402,
            username="task_developer",
            email="task_developer@example.com",
            worker_id="TD002",
            role="developer",
            is_active=True,
            is_staff=False,
            is_superuser=False,
            date_joined=aware_dt(2026, 1, 1),
        )
        self.task = CalendarEvent.objects.create(
            title="Delete Me",
            event_type="task",
            start=aware_dt(2026, 4, 1, 9, 0),
            end=aware_dt(2026, 4, 1, 10, 0),
            created_by=self.creator_employee,
            project=self.project,
        )

    def test_developer_can_delete_task_created_by_another_user(self):
        self.client.force_authenticate(self.developer_user)

        response = self.client.delete(reverse("calendar-event-detail", args=[self.task.id]))

        self.assertEqual(response.status_code, 204)
        self.assertFalse(CalendarEvent.objects.filter(id=self.task.id).exists())


class TaskGroupPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.department = Department.objects.create(code="TG", name="Task Groups")
        self.owner_employee = Employee.objects.create(name="Group Owner", emp_id="TG001", department=self.department)
        self.member_employee = Employee.objects.create(name="Group Member", emp_id="TG002", department=self.department)
        self.owner_user = ExternalUser.objects.create(
            external_id=1501,
            username="group_owner",
            email="group_owner@example.com",
            worker_id="TG001",
            is_active=True,
            is_staff=False,
            is_superuser=False,
            date_joined=aware_dt(2026, 1, 1),
        )
        self.member_user = ExternalUser.objects.create(
            external_id=1502,
            username="group_member",
            email="group_member@example.com",
            worker_id="TG002",
            is_active=True,
            is_staff=False,
            is_superuser=False,
            date_joined=aware_dt(2026, 1, 1),
        )
        self.developer_user = ExternalUser.objects.create(
            external_id=1503,
            username="group_developer",
            email="group_developer@example.com",
            worker_id="TG999",
            role="developer",
            is_active=True,
            is_staff=False,
            is_superuser=False,
            date_joined=aware_dt(2026, 1, 1),
        )
        self.group = TaskGroup.objects.create(name="Review Group", color="#6366F1", created_by=self.owner_user)
        self.group.members.add(self.owner_employee, self.member_employee)

    def test_member_cannot_delete_group(self):
        self.client.force_authenticate(self.member_user)

        response = self.client.delete(reverse("task-group-detail", args=[self.group.id]))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(TaskGroup.objects.filter(id=self.group.id).exists())

    def test_developer_can_delete_group(self):
        self.client.force_authenticate(self.developer_user)

        response = self.client.delete(reverse("task-group-detail", args=[self.group.id]))

        self.assertEqual(response.status_code, 204)
        self.assertFalse(TaskGroup.objects.filter(id=self.group.id).exists())

    def test_member_can_leave_group(self):
        self.client.force_authenticate(self.member_user)

        response = self.client.post(reverse("task-group-leave-group", args=[self.group.id]))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.group.members.filter(id=self.member_employee.id).exists())
