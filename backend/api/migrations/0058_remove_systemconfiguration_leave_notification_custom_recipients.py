from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0057_systemconfiguration_activity_log_cleanup_time"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="systemconfiguration",
            name="leave_notification_custom_recipients",
        ),
    ]