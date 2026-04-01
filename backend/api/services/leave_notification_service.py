import re
from collections import OrderedDict
from email.utils import formataddr
from urllib.parse import quote, urlsplit, urlunsplit

from django.conf import settings
from django.core import signing
from django.core.mail import EmailMultiAlternatives, get_connection
from django.utils import timezone
from django.utils.html import escape


DEFAULT_LEAVE_NOTIFICATION_SUBJECT_TEMPLATE = "[PTB Calendar] Leave Request {action_label} - {employee_name} ({leave_day_label})"
DEFAULT_LEAVE_NOTIFICATION_BODY_TEMPLATE = (
    "Hello Team,\n\n"
    "A leave request has been {action_label_lower} in PTB Calendar.\n\n"
    "Employee: {employee_name} ({employee_id})\n"
    "Department: {department_name} ({department_code})\n"
    "Leave Dates: {leave_dates}\n"
    "Total Days: {leave_day_count}\n"
    "Agent(s): {agents}\n"
    "Note: {note}\n"
    "Submitted by: {submitted_by}\n"
    "{updated_by_line}\n"
)
DEFAULT_LEAVE_NOTIFICATION_FOOTER_TEMPLATE = (
    "Please review the leave coverage details. The current Preview link will no longer be valid if the leave data is updated. This is an automated notification from PTB Calendar."
)

ALLOWED_LEAVE_NOTIFICATION_TEMPLATE_VARIABLES = {
    "action_label",
    "action_label_lower",
    "agents",
    "department_code",
    "department_name",
    "employee_id",
    "employee_name",
    "leave_dates",
    "leave_day_count",
    "leave_day_label",
    "note",
    "sender_name",
    "submitted_by",
    "updated_by",
    "updated_by_line",
}

TEMPLATE_VARIABLE_PATTERN = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")
SYSTEM_MANAGED_LINK_LINE_PATTERN = re.compile(r"^(details|preview)\s*:\s*.*$", re.IGNORECASE)
LEAVE_PREVIEW_SIGNING_SALT = "api.leave-preview"


class SafeNotificationTemplateContext(dict):
    def __missing__(self, key):
        return ""


def find_unsupported_template_variables(template):
    placeholders = {match.group(1) for match in TEMPLATE_VARIABLE_PATTERN.finditer(template or "")}
    return sorted(placeholders - ALLOWED_LEAVE_NOTIFICATION_TEMPLATE_VARIABLES)


def normalize_recipient_list(value):
    if not isinstance(value, list):
        return []
    return list(OrderedDict((str(email).strip().lower(), True) for email in value if str(email).strip()).keys())


def merge_recipient_lists(*recipient_groups):
    merged = OrderedDict()
    for group in recipient_groups:
        for email in normalize_recipient_list(group):
            merged[email] = True
    return list(merged.keys())


def normalize_external_agent_names(value):
    if not isinstance(value, list):
        return []

    names = []
    for item in value:
        if not isinstance(item, dict):
            continue
        display_name = str(item.get("username") or item.get("email") or item.get("worker_id") or "").strip()
        if display_name:
            names.append(display_name)

    return list(OrderedDict((name, True) for name in names).keys())


def render_notification_template(template, context):
    return (template or "").format_map(SafeNotificationTemplateContext(context)).strip()


def normalize_frontend_base_url():
    raw_value = (getattr(settings, "FRONTEND_BASE_URL", "") or "").strip().rstrip("/")
    if not raw_value:
        return ""

    parsed = urlsplit(raw_value)
    hostname = (parsed.hostname or "").strip().lower()
    if hostname not in {"localhost", "127.0.0.1"}:
        return raw_value

    netloc = "172.18.220.56"
    if parsed.port:
        netloc = f"{netloc}:{parsed.port}"

    return urlunsplit((parsed.scheme or "http", netloc, parsed.path, parsed.query, parsed.fragment)).rstrip("/")


def format_timezone_label(value):
    localized = timezone.localtime(value)
    offset = localized.utcoffset()
    if offset is None:
        return "UTC"

    total_minutes = int(offset.total_seconds() // 60)
    sign = "+" if total_minutes >= 0 else "-"
    absolute_minutes = abs(total_minutes)
    hours, minutes = divmod(absolute_minutes, 60)
    if minutes == 0:
        return f"UTC{sign}{hours}"
    return f"UTC{sign}{hours}:{minutes:02d}"


def format_actor_timestamp(username, value):
    actor_name = (username or "Unknown").strip() or "Unknown"
    if not value:
        return actor_name

    localized = timezone.localtime(value)
    timestamp = localized.strftime("%Y/%m/%d, %H:%M:%S")
    return f"{actor_name} | {timestamp} ({format_timezone_label(localized)})"


def build_leave_preview_token(batch_key):
    return signing.dumps({"batch_key": str(batch_key)}, salt=LEAVE_PREVIEW_SIGNING_SALT)


def resolve_leave_preview_token(token):
    payload = signing.loads(token, salt=LEAVE_PREVIEW_SIGNING_SALT)
    batch_key = str(payload.get("batch_key") or "").strip()
    if not batch_key:
        raise signing.BadSignature("Missing batch_key")
    return batch_key


def ensure_leave_preview_token(batch_key):
    from api.models import LeavePreviewToken

    raw_token = build_leave_preview_token(batch_key)
    LeavePreviewToken.objects.update_or_create(
        batch_key=batch_key,
        defaults={"token_hash": LeavePreviewToken.hash_token(raw_token)},
    )
    return raw_token


def strip_system_managed_link_lines(text):
    if not text:
        return ""
    cleaned_lines = [line for line in (text or "").splitlines() if not SYSTEM_MANAGED_LINK_LINE_PATTERN.match(line.strip())]
    cleaned_text = "\n".join(cleaned_lines)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)
    return cleaned_text.strip()


def build_leave_links(leaves):
    frontend_base_url = normalize_frontend_base_url()
    if not frontend_base_url:
        return {}

    batch_key = getattr(leaves[0], "batch_key", None)
    details_url = f"{frontend_base_url}/ptb-calendar"
    preview_url = None
    if batch_key:
        details_url = f"{details_url}?leaveBatch={quote(str(batch_key), safe='')}"
        preview_token = ensure_leave_preview_token(batch_key)
        preview_url = f"{frontend_base_url}/leave-preview?token={quote(preview_token, safe='')}"

    return {
        "details_url": details_url,
        "preview_url": preview_url,
    }


def build_leave_link_text(links):
    lines = []
    if links.get("details_url"):
        lines.append(f"Details: {links['details_url']}")
    if links.get("preview_url"):
        lines.append(f"Preview: {links['preview_url']}")
        lines.append("Note: The current Preview link will no longer be valid if the leave data is updated.")
    return "\n".join(lines).strip()


def build_leave_link_html(links):
    if not links.get("details_url") and not links.get("preview_url"):
        return ""

    items = []
    if links.get("details_url"):
        items.append(
            "<tr>"
            "<td style=\"padding:10px 14px;border-bottom:1px solid #e5e7eb;width:180px;font-weight:600;color:#111827;background:#f9fafb;vertical-align:top;\">Details</td>"
            f"<td style=\"padding:10px 14px;border-bottom:1px solid #e5e7eb;color:#1f2937;\"><a href=\"{escape(links['details_url'])}\" style=\"color:#2563eb;text-decoration:none;word-break:break-all;\">{escape(links['details_url'])}</a></td>"
            "</tr>"
        )
    if links.get("preview_url"):
        items.append(
            "<tr>"
            "<td style=\"padding:10px 14px;width:180px;font-weight:600;color:#111827;background:#f9fafb;vertical-align:top;\">Preview</td>"
            f"<td style=\"padding:10px 14px;color:#1f2937;\"><a href=\"{escape(links['preview_url'])}\" style=\"color:#2563eb;text-decoration:none;word-break:break-all;\">{escape(links['preview_url'])}</a></td>"
            "</tr>"
        )

    return (
        "<div style=\"margin:0 0 18px;border:1px solid #e5e7eb;border-radius:14px;overflow:hidden;\">"
        "<table role=\"presentation\" style=\"width:100%;border-collapse:collapse;\">"
        f"{''.join(items)}"
        "</table>"
        "<div style=\"padding:12px 14px;border-top:1px solid #e5e7eb;background:#fff7ed;color:#9a3412;font-size:12px;line-height:1.6;\">"
        "The current Preview link will no longer be valid if this leave data is updated or deleted."
        "</div></div>"
    )


def resolve_leave_notification_recipients(config, employee):
    mode = (config.leave_notification_recipient_mode or "global").lower()
    if mode == "custom":
        return normalize_recipient_list(config.leave_notification_custom_recipients)

    if mode == "department":
        employee_department = getattr(employee, "department", None)
        department_code = (getattr(employee_department, "code", "") or "").strip().upper()
        for entry in config.leave_notification_department_recipients or []:
            if not isinstance(entry, dict):
                continue
            entry_department_code = str(entry.get("department_code") or "").strip().upper()
            if entry_department_code == department_code:
                return normalize_recipient_list(entry.get("recipients", []))
        return []

    return normalize_recipient_list(config.leave_notification_recipients)


def resolve_leave_agent_notification_recipients(leaves):
    from api.models import ExternalUser

    agent_emp_ids = OrderedDict()
    external_agent_emails = OrderedDict()
    for leave in leaves:
        for agent in leave.agents.all():
            if agent.emp_id:
                agent_emp_ids[str(agent.emp_id).strip()] = True
        for external_agent in leave.external_agents or []:
            if not isinstance(external_agent, dict):
                continue
            email = str(external_agent.get("email") or "").strip().lower()
            if email:
                external_agent_emails[email] = True

    agent_recipients = []
    if agent_emp_ids:
        agent_users = ExternalUser.objects.filter(worker_id__in=list(agent_emp_ids.keys()), is_active=True).exclude(email__isnull=True).exclude(email="")
        agent_recipients = [user.email for user in agent_users]

    return merge_recipient_lists(agent_recipients, list(external_agent_emails.keys()))


def build_leave_notification_context(leaves, action, actor_username, sender_name):
    leave = leaves[0]
    employee = leave.employee
    department = getattr(employee, "department", None)

    structured_agent_names = []
    custom_agent_names = []
    unique_notes = OrderedDict()
    for leave_item in leaves:
        structured_agent_names.extend(agent.name for agent in leave_item.agents.all())
        structured_agent_names.extend(normalize_external_agent_names(leave_item.external_agents))
        if leave_item.agent_names:
            custom_agent_names.extend(name.strip() for name in leave_item.agent_names.split(",") if name.strip())
        if leave_item.notes and leave_item.notes.strip():
            unique_notes[leave_item.notes.strip()] = True

    note_text = " | ".join(unique_notes.keys()) if unique_notes else "-"
    submitted_by = format_actor_timestamp(leave.created_by.username if leave.created_by else "Unknown", leave.created_at)
    latest_updated_at = max((leave_item.updated_at for leave_item in leaves if leave_item.updated_at), default=None)
    updated_by = format_actor_timestamp(actor_username, latest_updated_at) if action == "updated" and actor_username else "-"
    updated_by_line = f"Updated By: {updated_by}" if updated_by != "-" else ""
    leave_day_count = len(leaves)
    unique_agent_names = list(OrderedDict((name, True) for name in [*structured_agent_names, *custom_agent_names]).keys())

    return {
        "action_label": "Updated" if action == "updated" else "Created",
        "action_label_lower": "updated" if action == "updated" else "created",
        "agents": ", ".join(unique_agent_names or ["None"]),
        "department_code": getattr(department, "code", "-") or "-",
        "department_name": getattr(department, "name", "-") or "-",
        "employee_id": employee.emp_id or "-",
        "employee_name": employee.name,
        "leave_dates": ", ".join(leave_item.date.strftime("%B %d, %Y") for leave_item in leaves),
        "leave_day_count": leave_day_count,
        "leave_day_label": f"{leave_day_count} day" + ("s" if leave_day_count != 1 else ""),
        "note": note_text,
        "sender_name": sender_name,
        "submitted_by": submitted_by,
        "updated_by": updated_by,
        "updated_by_line": updated_by_line,
    }


def _text_to_html(text):
    if not text:
        return ""

    def render_key_value_block(lines):
        rows = []
        for line in lines:
            label, value = line.split(":", 1)
            rows.append(
                "<tr>"
                f"<td style=\"padding:10px 14px;border-bottom:1px solid #e5e7eb;width:180px;font-weight:600;color:#111827;background:#f9fafb;vertical-align:top;\">{escape(label.strip())}</td>"
                f"<td style=\"padding:10px 14px;border-bottom:1px solid #e5e7eb;color:#1f2937;\">{escape(value.strip() or '-')}</td>"
                "</tr>"
            )
        return (
            "<div style=\"margin:0 0 18px;border:1px solid #e5e7eb;border-radius:14px;overflow:hidden;\">"
            "<table role=\"presentation\" style=\"width:100%;border-collapse:collapse;\">"
            f"{''.join(rows)}"
            "</table></div>"
        )

    paragraphs = []
    for block in text.split("\n\n"):
        block = block.strip()
        if not block:
            continue

        raw_lines = [line.strip() for line in block.split("\n") if line.strip()]
        key_value_lines = [line for line in raw_lines if ":" in line and not line.startswith("http")]
        if raw_lines and len(key_value_lines) == len(raw_lines):
            paragraphs.append(render_key_value_block(raw_lines))
            continue

        escaped_block = escape(block).replace("\n", "<br>")
        paragraphs.append(f"<p style=\"margin:0 0 16px;line-height:1.6;color:#1f2937;\">{escaped_block}</p>")
    return "".join(paragraphs)


def send_leave_notification_email_message(*, leave_ids, action, actor_username=None):
    from api.models import EmployeeLeave, SystemConfiguration

    leaves = list(
        EmployeeLeave.objects.filter(id__in=leave_ids)
        .select_related("employee", "employee__department", "created_by")
        .prefetch_related("agents")
        .order_by("date")
    )
    if not leaves:
        return {"status": "skipped", "reason": "no_leaves"}

    config, _ = SystemConfiguration.objects.get_or_create(pk=1)
    recipients = merge_recipient_lists(
        resolve_leave_notification_recipients(config, leaves[0].employee),
        resolve_leave_agent_notification_recipients(leaves),
    )
    if not recipients:
        return {"status": "skipped", "reason": "no_recipients"}

    sender_name = (config.leave_notification_sender_name or "OMS").strip() or "OMS"
    context = build_leave_notification_context(leaves, action, actor_username, sender_name)

    subject = render_notification_template(
        config.leave_notification_subject_template or DEFAULT_LEAVE_NOTIFICATION_SUBJECT_TEMPLATE,
        context,
    )
    body = render_notification_template(
        config.leave_notification_body_template or DEFAULT_LEAVE_NOTIFICATION_BODY_TEMPLATE,
        context,
    )
    footer = render_notification_template(
        config.leave_notification_footer_template or DEFAULT_LEAVE_NOTIFICATION_FOOTER_TEMPLATE,
        context,
    )
    sanitized_body = strip_system_managed_link_lines(body)
    links = build_leave_links(leaves)
    link_text = build_leave_link_text(links)
    plain_message = "\n\n".join(part for part in [sanitized_body, link_text, footer] if part).strip()
    html_message = (
        "<div style=\"font-family:Segoe UI,Arial,sans-serif;background:#f3f4f6;padding:24px;\">"
        "<div style=\"max-width:720px;margin:0 auto;background:#ffffff;border:1px solid #e5e7eb;border-radius:16px;overflow:hidden;\">"
        f"<div style=\"padding:24px 28px;border-bottom:1px solid #e5e7eb;background:#111827;color:#ffffff;\"><h2 style=\"margin:0;font-size:20px;font-weight:600;\">{escape(subject)}</h2></div>"
        f"<div style=\"padding:28px;\">{_text_to_html(sanitized_body)}{build_leave_link_html(links)}"
        f"<div style=\"margin-top:24px;padding-top:20px;border-top:1px solid #e5e7eb;\">{_text_to_html(footer)}</div>"
        "</div></div></div>"
    )

    connection = get_connection(
        backend=settings.EMAIL_BACKEND,
        host=(config.notification_email_host or "").strip() or settings.EMAIL_HOST,
        port=config.notification_email_port or settings.EMAIL_PORT,
        username=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
        use_tls=settings.EMAIL_USE_TLS,
        use_ssl=settings.EMAIL_USE_SSL,
        timeout=settings.EMAIL_TIMEOUT,
        fail_silently=False,
    )
    message = EmailMultiAlternatives(
        subject=subject,
        body=plain_message,
        from_email=formataddr((sender_name, settings.LEAVE_NOTIFICATION_FROM_EMAIL)),
        to=recipients,
        connection=connection,
    )
    message.attach_alternative(html_message, "text/html")
    message.send(fail_silently=False)

    return {"status": "success", "leave_ids": leave_ids, "recipients": recipients}