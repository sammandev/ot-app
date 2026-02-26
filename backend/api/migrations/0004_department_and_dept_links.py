"""
Migration for Task 4: Add Department model and link Employee/OvertimeRequest to it
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0003_externaluser_usersession"),
    ]

    operations = [
        # Create Department model
        migrations.CreateModel(
            name="Department",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(db_index=True, max_length=50, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("is_enabled", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "departments",
                "ordering": ["code"],
            },
        ),
        # Add department FK to Employee
        migrations.AddField(
            model_name="employee",
            name="department",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="employees", to="api.department"),
        ),
        # Add indexes to Employee
        migrations.AddIndex(
            model_name="employee",
            index=models.Index(fields=["emp_id"], name="api_employee_emp_id_idx"),
        ),
        migrations.AddIndex(
            model_name="employee",
            index=models.Index(fields=["department"], name="api_employee_department_idx"),
        ),
        # Add department FK and department_code cache to OvertimeRequest
        migrations.AddField(
            model_name="overtimerequest",
            name="department",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="overtime_requests", to="api.department"),
        ),
        migrations.AddField(
            model_name="overtimerequest",
            name="department_code",
            field=models.CharField(blank=True, db_index=True, default="", max_length=50),
        ),
        # Add indexes to OvertimeRequest
        migrations.AddIndex(
            model_name="overtimerequest",
            index=models.Index(fields=["request_date", "department"], name="api_ot_date_dept_idx"),
        ),
        migrations.AddIndex(
            model_name="overtimerequest",
            index=models.Index(fields=["department_code"], name="api_ot_dept_code_idx"),
        ),
    ]
