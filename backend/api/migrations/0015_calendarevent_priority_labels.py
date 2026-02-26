# Generated migration for CalendarEvent priority and labels fields

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0014_calendarevent_repeating_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="calendarevent",
            name="priority",
            field=models.CharField(choices=[("low", "Low"), ("medium", "Medium"), ("high", "High"), ("urgent", "Urgent")], default="medium", max_length=10),
        ),
        migrations.AddField(
            model_name="calendarevent",
            name="labels",
            field=models.JSONField(blank=True, default=list, help_text="List of label strings for the task"),
        ),
    ]
