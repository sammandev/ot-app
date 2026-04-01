from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0053_backfill_purchase_request_asset_created_by"),
    ]

    operations = [
        migrations.AddField(
            model_name="employeeleave",
            name="external_agents",
            field=models.JSONField(blank=True, default=list, help_text="Structured external agent records selected from external lookup"),
        ),
    ]