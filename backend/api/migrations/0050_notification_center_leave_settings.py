from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0049_systemconfiguration_leave_notification_settings"),
    ]

    operations = [
        migrations.AddField(
            model_name="systemconfiguration",
            name="notification_email_host",
            field=models.CharField(default="mail.pegatroncorp.com", help_text="SMTP host for notification emails", max_length=255),
        ),
        migrations.AddField(
            model_name="systemconfiguration",
            name="notification_email_port",
            field=models.PositiveIntegerField(default=25, help_text="SMTP port for notification emails"),
        ),
        migrations.AddField(
            model_name="systemconfiguration",
            name="leave_notification_recipient_mode",
            field=models.CharField(default="global", help_text="Recipient mode for leave notifications: global, department, or custom", max_length=20),
        ),
        migrations.AddField(
            model_name="systemconfiguration",
            name="leave_notification_department_recipients",
            field=models.JSONField(blank=True, default=list, help_text="Department recipient mappings for leave notifications"),
        ),
        migrations.AddField(
            model_name="systemconfiguration",
            name="leave_notification_custom_recipients",
            field=models.JSONField(blank=True, default=list, help_text="Custom recipients for leave notifications"),
        ),
        migrations.AddField(
            model_name="systemconfiguration",
            name="leave_notification_subject_template",
            field=models.TextField(default="[PTB Calendar] Leave Request {action_label} - {employee_name} ({leave_day_label})", help_text="Subject template for leave notification emails"),
        ),
        migrations.AddField(
            model_name="systemconfiguration",
            name="leave_notification_body_template",
            field=models.TextField(default="Hello Team,\n\nA leave request has been {action_label_lower} in PTB Calendar.\n\nEmployee: {employee_name} ({employee_id})\nDepartment: {department_name} ({department_code})\nLeave dates: {leave_dates}\nNumber of days: {leave_day_count}\nAgent(s): {agents}\nNote: {note}\nSubmitted by: {submitted_by}\n{updated_by_line}\nPlease review the leave coverage details as needed.", help_text="Body template for leave notification emails"),
        ),
        migrations.AddField(
            model_name="systemconfiguration",
            name="leave_notification_footer_template",
            field=models.TextField(default="Best regards,\n{sender_name}\n\nThis is an automated notification from PTB Calendar.", help_text="Footer template for leave notification emails"),
        ),
    ]