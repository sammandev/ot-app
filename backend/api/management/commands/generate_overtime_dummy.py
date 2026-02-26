from datetime import datetime, time, timedelta
from random import choice, randint

from django.core.management.base import BaseCommand

from api.models import Employee, OvertimeRequest, Project


class Command(BaseCommand):
    help = "Generate dummy overtime requests"

    def add_arguments(self, parser):
        # Adding an argument to specify the number of records to generate
        parser.add_argument(
            "num_records",
            type=int,
            nargs="?",
            default=10,
            help="The number of overtime requests to generate (default is 10)",
        )

    def handle(self, *args, **kwargs):
        num_records = kwargs["num_records"]
        self.generate_dummy_data(num_records)

    # Generate <num_records> dummy data for testing
    def generate_dummy_data(self, num_records=10):
        employees = Employee.objects.all()
        projects = Project.objects.all()

        if not employees or not projects:
            self.stdout.write(self.style.ERROR("No employees or projects found in the database."))
            return

        start_date = datetime(2024, 12, 1)
        end_date = datetime(2025, 1, 20)

        for _ in range(num_records):
            employee = choice(employees)  # Randomly select an employee
            project = choice(projects)  # Randomly select a project

            # Randomize request date
            request_date = start_date + timedelta(days=randint(0, (end_date - start_date).days))

            # Determine if the day is a weekend or a holiday
            is_weekend = request_date.weekday() >= 5  # 5=Saturday, 6=Sunday
            is_holiday = choice([True, False])

            # Set time_start based on weekday/weekend/holiday
            if is_weekend or is_holiday:
                time_start = time(7, 50)
                max_hours = 7
            else:
                time_start = time(17, 20)
                max_hours = 4

            # Generate available time slots in 30-minute increments
            time_slots = []
            current_time = time_start
            for _ in range(max_hours * 2):  # 2 slots per hour
                time_slots.append(current_time)
                if current_time.minute == 20:
                    current_time = current_time.replace(minute=50)
                else:
                    current_time = (datetime.combine(request_date, current_time) + timedelta(minutes=30)).time()

            # Randomly select time_end ensuring it's after time_start
            time_end = choice(time_slots[1:])  # Ensure time_end > time_start

            # Calculate total_hours
            total_hours = (datetime.combine(request_date, time_end) - datetime.combine(request_date, time_start)).seconds / 3600

            # Determine if there was a break
            has_break = choice([True, False]) and total_hours > 1.5  # Only add a break if there's enough time
            break_start, break_end, break_hours = None, None, None
            if has_break:
                break_start_index = randint(1, len(time_slots) // 2)
                break_start = time_slots[break_start_index]
                # Ensure break_end is within time_end
                break_end_index = break_start_index + 1
                if break_end_index < len(time_slots) and time_slots[break_end_index] <= time_end:
                    break_end = time_slots[break_end_index]
                    break_hours = (datetime.combine(request_date, break_end) - datetime.combine(request_date, break_start)).seconds / 3600

            # Create and save the OvertimeRequest
            overtime_request = OvertimeRequest(
                employee=employee,
                employee_name=employee.name,
                project=project,
                project_name=project.name,
                request_date=request_date.date(),
                time_start=time_start,
                time_end=time_end,
                total_hours=total_hours,
                has_break=has_break,
                break_start=break_start,
                break_end=break_end,
                break_hours=break_hours,
                reason="Dummy reason for testing",
                detail="Detailed description of the overtime request",
                is_weekend=is_weekend,
                is_holiday=is_holiday,
            )

            overtime_request.save()
            self.stdout.write(f"Created overtime request for {employee.name} on {request_date.date()}")
