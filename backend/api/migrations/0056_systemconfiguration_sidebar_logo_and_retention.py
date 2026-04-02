from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0055_leavepreviewtoken_version"),
    ]

    operations = [
        migrations.AddField(
            model_name="systemconfiguration",
            name="leave_notification_employee_groups",
            field=models.JSONField(blank=True, default=list, help_text="Custom employee groups for leave notification routing"),
        ),
        migrations.AddField(
            model_name="systemconfiguration",
            name="leave_notification_employee_recipients",
            field=models.JSONField(blank=True, default=list, help_text="Employee-specific recipient mappings for leave notifications"),
        ),
        migrations.AddField(
            model_name="systemconfiguration",
            name="sidebar_logo",
            field=models.FileField(blank=True, help_text="Custom sidebar logo/image", null=True, upload_to="system/"),
        ),
        migrations.AddField(
            model_name="systemconfiguration",
            name="user_activity_log_retention_days",
            field=models.PositiveIntegerField(blank=True, help_text="Automatically delete user activity logs older than this many days", null=True),
        ),
    ]
