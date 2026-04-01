from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0048_document_link_metadata"),
    ]

    operations = [
        migrations.AddField(
            model_name="systemconfiguration",
            name="leave_notification_recipients",
            field=models.JSONField(blank=True, default=list, help_text="Internal recipients for leave notifications"),
        ),
        migrations.AddField(
            model_name="systemconfiguration",
            name="leave_notification_sender_name",
            field=models.CharField(default="OMS", help_text="Display name used for leave notification emails", max_length=100),
        ),
    ]