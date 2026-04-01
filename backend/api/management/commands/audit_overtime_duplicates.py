from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

from api.models import OvertimeRequest


class Command(BaseCommand):
    help = "Audit duplicate overtime requests by employee, project, and request date."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=20,
            help="Maximum number of duplicate groups to print (default: 20).",
        )
        parser.add_argument(
            "--show-ids",
            action="store_true",
            help="Include duplicate record IDs for each duplicate group.",
        )
        parser.add_argument(
            "--fail-on-duplicates",
            action="store_true",
            help="Exit with a non-zero status code if duplicate groups are found.",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        show_ids = options["show_ids"]
        fail_on_duplicates = options["fail_on_duplicates"]

        duplicate_groups = list(OvertimeRequest.objects.values("employee_id", "project_id", "request_date").annotate(record_count=Count("id")).filter(record_count__gt=1).order_by("-record_count", "request_date", "employee_id", "project_id"))

        total_groups = len(duplicate_groups)
        if total_groups == 0:
            self.stdout.write(self.style.SUCCESS("No duplicate overtime request groups found."))
            return

        self.stdout.write(self.style.WARNING(f"Found {total_groups} duplicate overtime request group(s)."))

        for group in duplicate_groups[:limit]:
            records = list(
                OvertimeRequest.objects.filter(
                    employee_id=group["employee_id"],
                    project_id=group["project_id"],
                    request_date=group["request_date"],
                )
                .select_related("employee", "project")
                .order_by("id")
            )
            sample = records[0]
            ids_text = f" ids={[record.id for record in records]}" if show_ids else ""
            self.stdout.write(
                "- employee_id={employee_id} employee={employee_name} project_id={project_id} project={project_name} request_date={request_date} count={count}{ids}".format(
                    employee_id=group["employee_id"],
                    employee_name=sample.employee_name or getattr(sample.employee, "name", "N/A"),
                    project_id=group["project_id"],
                    project_name=sample.project_name or getattr(sample.project, "name", "N/A"),
                    request_date=group["request_date"],
                    count=group["record_count"],
                    ids=ids_text,
                )
            )

        if total_groups > limit:
            self.stdout.write(self.style.WARNING(f"Output truncated to {limit} group(s). Re-run with --limit to inspect more."))

        self.stdout.write(self.style.WARNING("Resolve duplicate groups before applying migration 0045_overtime_request_unique_constraint."))

        if fail_on_duplicates:
            raise CommandError("Duplicate overtime request groups detected.")
