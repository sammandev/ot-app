from django.db import migrations, models


def dedupe_board_presence_rows(apps, schema_editor):
    BoardPresence = apps.get_model("api", "BoardPresence")

    duplicate_user_ids = BoardPresence.objects.values_list("user_id", flat=True).annotate(row_count=models.Count("id")).filter(row_count__gt=1)

    for user_id in duplicate_user_ids.iterator():
        rows = list(BoardPresence.objects.filter(user_id=user_id).order_by("-last_seen", "id"))
        for duplicate in rows[1:]:
            duplicate.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0045_overtime_request_unique_constraint"),
    ]

    operations = [
        migrations.RunPython(dedupe_board_presence_rows, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="boardpresence",
            constraint=models.UniqueConstraint(fields=("user",), name="unique_board_presence_user"),
        ),
    ]
