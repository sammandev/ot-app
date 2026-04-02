from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0054_employeeleave_external_agents"),
    ]

    operations = [
        migrations.AddField(
            model_name="leavepreviewtoken",
            name="version",
            field=models.PositiveIntegerField(default=1),
        ),
    ]
