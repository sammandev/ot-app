from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0047_document"),
    ]

    operations = [
        migrations.AddField(
            model_name="document",
            name="link_description",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="document",
            name="link_favicon_url",
            field=models.URLField(blank=True, max_length=1000),
        ),
        migrations.AddField(
            model_name="document",
            name="link_image_url",
            field=models.URLField(blank=True, max_length=1000),
        ),
        migrations.AddField(
            model_name="document",
            name="link_site_name",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="document",
            name="link_title",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="document",
            name="metadata_error",
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name="document",
            name="metadata_fetched_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="document",
            name="metadata_status",
            field=models.CharField(choices=[("pending", "Pending"), ("success", "Success"), ("failed", "Failed")], db_index=True, default="pending", max_length=20),
        ),
    ]