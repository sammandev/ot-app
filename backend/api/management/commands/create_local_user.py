"""
Management command to create local users with custom data.
Usage: python manage.py create_local_user --username admin --password "SecurePass123" --email admin@example.com --is-superuser
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()


class Command(BaseCommand):
    help = "Create a new local user with custom data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            required=True,
            help="Username for the new user",
        )
        parser.add_argument(
            "--password",
            type=str,
            required=True,
            help="Password for the new user (must be strong)",
        )
        parser.add_argument(
            "--email",
            type=str,
            required=False,
            default="",
            help="Email address for the user (optional)",
        )
        parser.add_argument(
            "--first-name",
            type=str,
            required=False,
            default="",
            help="First name of the user (optional)",
        )
        parser.add_argument(
            "--last-name",
            type=str,
            required=False,
            default="",
            help="Last name of the user (optional)",
        )
        parser.add_argument(
            "--is-ptb-admin",
            action="store_true",
            help="Make the user a ptb admin",
        )
        parser.add_argument(
            "--is-superuser",
            action="store_true",
            help="Make the user a superuser",
        )
        parser.add_argument(
            "--is-staff",
            action="store_true",
            help="Make the user a staff member",
        )
        parser.add_argument(
            "--is-active",
            action="store_true",
            default=True,
            help="Set the user as active (default: True)",
        )

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]
        email = options["email"]
        first_name = options["first_name"]
        last_name = options["last_name"]
        is_ptb_admin = options["is_ptb_admin"]
        is_superuser = options["is_superuser"]
        is_staff = options["is_staff"]
        is_active = options["is_active"]

        # Validate username length
        if len(username) < 3:
            raise CommandError("Username must be at least 3 characters long")

        # Validate password strength
        if len(password) < 8:
            raise CommandError("Password must be at least 8 characters long")

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            raise CommandError(f'User with username "{username}" already exists')

        try:
            if is_superuser:
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_ptb_admin=is_ptb_admin,
                    is_staff=is_staff,
                    is_active=is_active,
                )
            else:
                User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_ptb_admin=is_ptb_admin,
                    is_staff=is_staff,
                    is_active=is_active,
                )

            self.stdout.write(self.style.SUCCESS(f'✓ User "{username}" created successfully!'))
            self.stdout.write(self.style.SUCCESS(f"  - Email: {email}"))
            self.stdout.write(self.style.SUCCESS(f"  - PTB Admin: {is_ptb_admin}"))
            self.stdout.write(self.style.SUCCESS(f"  - Superuser: {is_superuser}"))
            self.stdout.write(self.style.SUCCESS(f"  - Staff: {is_staff}"))
            self.stdout.write(self.style.SUCCESS(f"  - Active: {is_active}"))

        except Exception as e:
            raise CommandError(f"Error creating user: {str(e)}") from e
