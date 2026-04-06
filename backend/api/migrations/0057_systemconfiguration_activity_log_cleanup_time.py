from datetime import time

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0056_systemconfiguration_sidebar_logo_and_retention"),
    ]

    operations = [
        migrations.AddField(
            model_name="systemconfiguration",
            name="user_activity_log_cleanup_time",
            field=models.TimeField(default=time(0, 15), help_text="Daily local time when the user activity log cleanup job should run"),
        ),
    ]