# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0009_alter_calendarevent_created_by"),
    ]

    operations = [
        migrations.AddField(
            model_name="calendarevent",
            name="leave_type",
            field=models.CharField(blank=True, choices=[("personal", "Personal"), ("legal", "Legal"), ("official", "Official")], max_length=20, null=True),
        ),
    ]
