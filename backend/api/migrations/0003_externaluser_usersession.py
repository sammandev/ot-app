"""
Migration for Phase 1: External User and Session models
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0002_overtimebreak"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExternalUser",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("external_id", models.IntegerField(db_index=True, unique=True)),
                ("username", models.CharField(db_index=True, max_length=150, unique=True)),
                ("email", models.EmailField(max_length=254)),
                ("first_name", models.CharField(blank=True, max_length=150)),
                ("last_name", models.CharField(blank=True, max_length=150)),
                ("worker_id", models.CharField(blank=True, db_index=True, max_length=50, null=True)),
                ("is_ptb_admin", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("is_superuser", models.BooleanField(default=False)),
                ("is_staff", models.BooleanField(default=False)),
                ("date_joined", models.DateTimeField()),
                ("last_login", models.DateTimeField(blank=True, null=True)),
                ("permissions_cache", models.JSONField(blank=True, default=dict)),
                ("groups_cache", models.JSONField(blank=True, default=list)),
                ("models_perm_cache", models.JSONField(blank=True, default=dict)),
                ("cache_updated_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "external_users",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="UserSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("access_token", models.TextField(db_index=True, unique=True)),
                ("refresh_token", models.TextField(blank=True, null=True)),
                ("token_expires_at", models.DateTimeField(db_index=True)),
                ("token_issued_at", models.DateTimeField()),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True)),
                ("last_activity", models.DateTimeField(auto_now=True, db_index=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="sessions", to="api.externaluser")),
            ],
            options={
                "db_table": "user_sessions",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="externaluser",
            index=models.Index(fields=["external_id"], name="external_us_externa_idx"),
        ),
        migrations.AddIndex(
            model_name="externaluser",
            index=models.Index(fields=["username"], name="external_us_usernam_idx"),
        ),
        migrations.AddIndex(
            model_name="externaluser",
            index=models.Index(fields=["worker_id"], name="external_us_worker__idx"),
        ),
        migrations.AddIndex(
            model_name="externaluser",
            index=models.Index(fields=["is_active"], name="external_us_is_acti_idx"),
        ),
        migrations.AddIndex(
            model_name="usersession",
            index=models.Index(fields=["user", "is_active"], name="user_sessio_user_id_idx"),
        ),
        migrations.AddIndex(
            model_name="usersession",
            index=models.Index(fields=["token_expires_at"], name="user_sessio_token_e_idx"),
        ),
        migrations.AddIndex(
            model_name="usersession",
            index=models.Index(fields=["last_activity"], name="user_sessio_last_ac_idx"),
        ),
    ]
