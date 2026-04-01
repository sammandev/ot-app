from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0046_board_presence_unique_user"),
    ]

    operations = [
        migrations.CreateModel(
            name="Document",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("source_type", models.CharField(choices=[("file", "File"), ("link", "Link")], db_index=True, max_length=10)),
                ("file", models.FileField(blank=True, null=True, upload_to="documents/%Y/%m/")),
                ("external_url", models.URLField(blank=True, max_length=1000)),
                ("normalized_url", models.URLField(blank=True, max_length=1000)),
                ("original_filename", models.CharField(blank=True, max_length=255)),
                ("stored_file_size", models.BigIntegerField(blank=True, null=True)),
                ("mime_type", models.CharField(blank=True, max_length=150)),
                ("extension", models.CharField(blank=True, db_index=True, max_length=20)),
                ("category", models.CharField(blank=True, db_index=True, max_length=100)),
                ("tags", models.CharField(blank=True, default="", max_length=500)),
                ("is_pinned", models.BooleanField(db_index=True, default=False)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_documents", to="api.externaluser")),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="updated_documents", to="api.externaluser")),
            ],
            options={
                "db_table": "documents",
                "ordering": ["-is_pinned", "-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="document",
            index=models.Index(fields=["source_type", "-created_at"], name="documents_source__8b4f6c_idx"),
        ),
        migrations.AddIndex(
            model_name="document",
            index=models.Index(fields=["category", "-created_at"], name="documents_categor_3efff4_idx"),
        ),
        migrations.AddIndex(
            model_name="document",
            index=models.Index(fields=["is_pinned", "-created_at"], name="documents_is_pinn_6c67d5_idx"),
        ),
        migrations.AddIndex(
            model_name="document",
            index=models.Index(fields=["created_by", "-created_at"], name="documents_created_3819d2_idx"),
        ),
    ]