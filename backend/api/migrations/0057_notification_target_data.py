from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0056_systemconfiguration_sidebar_logo_and_retention"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="target_data",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
