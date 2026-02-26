from django.core.management import call_command
from django.core.management.base import BaseCommand

from api.models import Employee, Project


class Command(BaseCommand):
    help = "Initialize employee and project data if not already loaded."

    def handle(self, *args, **options):
        if not Employee.objects.exists():
            self.stdout.write("Loading employees data...")
            try:
                call_command("loaddata", "generate_data/employees.json")
            except Exception as e:
                self.stdout.write(self.style.ERROR("Failed to load employees: " + str(e)))
        else:
            self.stdout.write("Employees data already exists. Skipping.")

        if not Project.objects.exists():
            self.stdout.write("Loading projects data...")
            try:
                call_command("loaddata", "generate_data/projects.json")
            except Exception as e:
                self.stdout.write(self.style.ERROR("Failed to load projects: " + str(e)))
        else:
            self.stdout.write("Projects data already exists. Skipping.")

        self.stdout.write("Data initialization complete.")
