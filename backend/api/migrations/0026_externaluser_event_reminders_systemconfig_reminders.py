# Generated migration for event reminder settings

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0025_taskgroup_department_taskgroup_is_department_group_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="externaluser",
            name="event_reminders_enabled",
            field=models.BooleanField(default=True, help_text="Whether event reminders are shown to this user"),
        ),
        migrations.AddField(
            model_name="systemconfiguration",
            name="event_reminders_disabled_globally",
            field=models.BooleanField(default=False, help_text="Disable event reminders for all users"),
        ),
        migrations.AddField(
            model_name="systemconfiguration",
            name="event_reminders_disabled_roles",
            field=models.JSONField(blank=True, default=list, help_text="Roles with reminders disabled, e.g. ['regular', 'staff']"),
        ),
        migrations.AddField(
            model_name="systemconfiguration",
            name="event_reminders_disabled_users",
            field=models.JSONField(blank=True, default=list, help_text="User IDs with reminders disabled"),
        ),
    ]
