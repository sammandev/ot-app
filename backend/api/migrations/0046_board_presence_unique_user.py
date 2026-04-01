from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0045_overtime_request_unique_constraint"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="boardpresence",
            constraint=models.UniqueConstraint(fields=("user",), name="unique_board_presence_user"),
        ),
    ]
