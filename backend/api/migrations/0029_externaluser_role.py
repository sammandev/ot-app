"""
Add role field to ExternalUser model.
Developer role is protected from modification by other superadmins.
"""

from django.db import migrations, models


def set_developer_role(apps, schema_editor):
    """Set the developer role for the hardcoded superadmin user."""
    ExternalUser = apps.get_model("api", "ExternalUser")
    # Set developer role for Samuel_Halomoan
    ExternalUser.objects.filter(models.Q(username__iexact="Samuel_Halomoan") | models.Q(worker_id="MW2400549") | models.Q(email__iexact="samuel_halomoan@pegatroncorp.com")).update(role="developer")


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0028_add_preferred_language"),
    ]

    operations = [
        migrations.AddField(
            model_name="externaluser",
            name="role",
            field=models.CharField(
                choices=[("developer", "Developer"), ("superadmin", "Super Admin"), ("user", "User")],
                default="user",
                help_text="User role: developer, superadmin, or user",
                max_length=20,
            ),
        ),
        migrations.RunPython(set_developer_role, migrations.RunPython.noop),
    ]
