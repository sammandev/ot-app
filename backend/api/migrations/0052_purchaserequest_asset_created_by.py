from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0051_employeeleave_batch_key_and_preview"),
    ]

    operations = [
        migrations.AddField(
            model_name="asset",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="created_assets",
                to="api.externaluser",
            ),
        ),
        migrations.AddField(
            model_name="purchaserequest",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="created_purchase_requests",
                to="api.externaluser",
            ),
        ),
    ]