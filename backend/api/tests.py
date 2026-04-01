from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from openpyxl import Workbook

from django.db import IntegrityError

from api.models import CalendarEvent, Department, Employee, EmployeeLeave, ExternalUser, OvertimeRequest, Project, PurchaseRequest, TaskAttachment, TaskSubtask, TaskTimeLog, UserSession
from api.services.leave_notification_service import ensure_leave_preview_token, resolve_leave_agent_notification_recipients


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
        self.assertEqual(response.data[0]["agents"], [
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
        ])
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
