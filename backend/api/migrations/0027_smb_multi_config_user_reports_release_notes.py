# Generated migration for SMBConfiguration (multi-config), UserReport, ReleaseNote

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0026_externaluser_event_reminders_systemconfig_reminders"),
    ]

    operations = [
        # --- SMBConfiguration: create table (multi-config, not singleton) ---
        migrations.CreateModel(
            name="SMBConfiguration",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(default="Default", help_text="Label for this configuration", max_length=100)),
                ("server", models.CharField(blank=True, help_text="SMB server hostname or IP", max_length=255)),
                ("share_name", models.CharField(blank=True, help_text="SMB share name", max_length=255)),
                ("username", models.CharField(blank=True, help_text="SMB username", max_length=255)),
                ("_encrypted_password", models.TextField(blank=True, db_column="encrypted_password", help_text="Fernet-encrypted SMB password")),
                ("domain", models.CharField(default="WORKGROUP", max_length=100)),
                ("port", models.IntegerField(default=445)),
                ("path_prefix", models.CharField(blank=True, default="", help_text="Path prefix on the SMB share", max_length=500)),
                ("is_active", models.BooleanField(default=False, help_text="Only one config should be active at a time")),
            ],
            options={
                "verbose_name": "SMB Configuration",
                "verbose_name_plural": "SMB Configurations",
                "db_table": "smb_configuration",
                "ordering": ["-is_active", "-updated_at"],
            },
        ),
        # --- UserReport ---
        migrations.CreateModel(
            name="UserReport",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("report_type", models.CharField(choices=[("bug", "Bug Report"), ("feature", "Feature Request")], db_index=True, max_length=10)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("page_url", models.CharField(blank=True, help_text="Page where the issue was found", max_length=500)),
                ("priority", models.CharField(choices=[("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")], default="medium", max_length=10)),
                ("status", models.CharField(choices=[("open", "Open"), ("in_progress", "In Progress"), ("resolved", "Resolved"), ("closed", "Closed"), ("wont_fix", "Won't Fix")], db_index=True, default="open", max_length=15)),
                ("admin_notes", models.TextField(blank=True, help_text="Super admin response / notes")),
                ("resolved_in_version", models.CharField(blank=True, help_text="Version where this was resolved", max_length=20)),
                ("reporter", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reports", to="api.externaluser")),
            ],
            options={
                "db_table": "user_reports",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="userreport",
            index=models.Index(fields=["report_type", "-created_at"], name="user_report_report__7c5e0e_idx"),
        ),
        migrations.AddIndex(
            model_name="userreport",
            index=models.Index(fields=["status", "-created_at"], name="user_report_status_3a1b2c_idx"),
        ),
        migrations.AddIndex(
            model_name="userreport",
            index=models.Index(fields=["reporter", "-created_at"], name="user_report_reporte_4d5e6f_idx"),
        ),
        # --- ReleaseNote ---
        migrations.CreateModel(
            name="ReleaseNote",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("version", models.CharField(max_length=20, unique=True)),
                ("release_date", models.DateField()),
                ("status", models.CharField(choices=[("stable", "Stable"), ("beta", "Beta"), ("hotfix", "Hotfix")], default="stable", max_length=10)),
                ("summary", models.TextField(blank=True, help_text="Short summary of this release")),
                ("new_features", models.JSONField(blank=True, default=list, help_text="New features list")),
                ("improvements", models.JSONField(blank=True, default=list, help_text="Improvements list")),
                ("bug_fixes", models.JSONField(blank=True, default=list, help_text="Bug fixes list")),
                ("breaking_changes", models.JSONField(blank=True, default=list, help_text="Breaking changes list")),
                ("security", models.JSONField(blank=True, default=list, help_text="Security patches list")),
                ("known_issues", models.JSONField(blank=True, default=list)),
                ("deprecations", models.JSONField(blank=True, default=list)),
                ("contributors", models.JSONField(blank=True, default=list, help_text="List of contributor names")),
                ("published", models.BooleanField(default=True, help_text="Visible to all users")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="release_notes", to="api.externaluser")),
            ],
            options={
                "db_table": "release_notes",
                "ordering": ["-release_date", "-created_at"],
            },
        ),
    ]
