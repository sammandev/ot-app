from django.db import migrations, models


def create_default_overtime_limit_config(apps, schema_editor):
    OvertimeLimitConfig = apps.get_model("api", "OvertimeLimitConfig")
    if OvertimeLimitConfig.objects.exists():
        return

    OvertimeLimitConfig.objects.create(
        max_weekly_hours="18.00",
        max_monthly_hours="72.00",
        recommended_weekly_hours="15.00",
        recommended_monthly_hours="60.00",
        is_active=True,
    )


def delete_default_overtime_limit_config(apps, schema_editor):
    OvertimeLimitConfig = apps.get_model("api", "OvertimeLimitConfig")
    OvertimeLimitConfig.objects.filter(
        max_weekly_hours="18.00",
        max_monthly_hours="72.00",
        recommended_weekly_hours="15.00",
        recommended_monthly_hours="60.00",
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0033_add_overtime_status_index"),
    ]

    operations = [
        migrations.CreateModel(
            name="OvertimeLimitConfig",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("max_weekly_hours", models.DecimalField(decimal_places=2, default=18, help_text="Maximum overtime hours per week (Mon-Sun)", max_digits=5)),
                ("max_monthly_hours", models.DecimalField(decimal_places=2, default=72, help_text="Maximum overtime hours per month (26th-25th cycle)", max_digits=5)),
                ("recommended_weekly_hours", models.DecimalField(decimal_places=2, default=15, help_text="Recommended weekly overtime warning threshold", max_digits=5)),
                ("recommended_monthly_hours", models.DecimalField(decimal_places=2, default=60, help_text="Recommended monthly overtime warning threshold", max_digits=5)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Overtime Limit Configuration",
                "verbose_name_plural": "Overtime Limit Configurations",
                "ordering": ["-created_at"],
            },
        ),
        migrations.RunPython(create_default_overtime_limit_config, delete_default_overtime_limit_config),
    ]
