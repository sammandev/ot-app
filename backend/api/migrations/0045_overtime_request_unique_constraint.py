from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0044_usersession_refresh_token_index"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="overtimerequest",
            constraint=models.UniqueConstraint(
                fields=("employee", "project", "request_date"),
                name="unique_overtime_employee_project_date",
            ),
        ),
    ]
