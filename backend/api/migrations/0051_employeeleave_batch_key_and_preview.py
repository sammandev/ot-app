from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0050_notification_center_leave_settings"),
    ]

    operations = [
        migrations.AddField(
            model_name="employeeleave",
            name="batch_key",
            field=models.UUIDField(blank=True, db_index=True, editable=False, help_text="Stable identifier shared by leave dates created or updated together", null=True),
        ),
        migrations.CreateModel(
            name="LeavePreviewToken",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("batch_key", models.UUIDField(db_index=True, unique=True)),
                ("token_hash", models.CharField(db_index=True, max_length=64, unique=True)),
                ("last_accessed_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "db_table": "leave_preview_tokens",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="leavepreviewtoken",
            index=models.Index(fields=["last_accessed_at"], name="leave_previ_last_ac_0ef459_idx"),
        ),
    ]
