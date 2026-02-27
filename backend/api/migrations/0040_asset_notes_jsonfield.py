"""Consolidate Asset note1–note10 TextFields into a single JSONField."""

from django.db import migrations, models


def forwards(apps, schema_editor):
    """Copy note1–note10 into the ``notes`` JSONField, then NULL the old columns."""
    Asset = apps.get_model("api", "Asset")
    NOTE_FIELDS = [f"note{i}" for i in range(1, 11)]

    # Batch in chunks to keep memory low on large tables.
    batch = []
    for asset in Asset.objects.only("pk", *NOTE_FIELDS).iterator(chunk_size=500):
        notes = {}
        for field in NOTE_FIELDS:
            val = getattr(asset, field)
            if val:
                notes[field] = val
        asset.notes = notes
        batch.append(asset)
        if len(batch) >= 500:
            Asset.objects.bulk_update(batch, ["notes"])
            batch = []
    if batch:
        Asset.objects.bulk_update(batch, ["notes"])


def backwards(apps, schema_editor):
    """Restore note1–note10 from the ``notes`` JSONField."""
    Asset = apps.get_model("api", "Asset")
    NOTE_FIELDS = [f"note{i}" for i in range(1, 11)]

    batch = []
    for asset in Asset.objects.only("pk", "notes").iterator(chunk_size=500):
        notes = asset.notes or {}
        for field in NOTE_FIELDS:
            setattr(asset, field, notes.get(field))
        batch.append(asset)
        if len(batch) >= 500:
            Asset.objects.bulk_update(batch, NOTE_FIELDS)
            batch = []
    if batch:
        Asset.objects.bulk_update(batch, NOTE_FIELDS)


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0039_overtime_limit_config_singleton"),
    ]

    operations = [
        # 1. Add the new JSONField
        migrations.AddField(
            model_name="asset",
            name="notes",
            field=models.JSONField(blank=True, default=dict),
        ),
        # 2. Copy data from old fields into the new JSONField
        migrations.RunPython(forwards, backwards),
        # 3. Remove the 10 old fields
        migrations.RemoveField(model_name="asset", name="note1"),
        migrations.RemoveField(model_name="asset", name="note2"),
        migrations.RemoveField(model_name="asset", name="note3"),
        migrations.RemoveField(model_name="asset", name="note4"),
        migrations.RemoveField(model_name="asset", name="note5"),
        migrations.RemoveField(model_name="asset", name="note6"),
        migrations.RemoveField(model_name="asset", name="note7"),
        migrations.RemoveField(model_name="asset", name="note8"),
        migrations.RemoveField(model_name="asset", name="note9"),
        migrations.RemoveField(model_name="asset", name="note10"),
    ]
