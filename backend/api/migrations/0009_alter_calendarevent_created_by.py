# Generated manually

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0008_overtimeregulationdocument"),
    ]

    operations = [
        migrations.AlterField(
            model_name="calendarevent",
            name="created_by",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="created_events", to="api.employee"),
        ),
    ]
