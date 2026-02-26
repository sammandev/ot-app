from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Fix auto-increment sequences for all tables"

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            # Fix Project sequence
            cursor.execute("""
                SELECT setval(
                    pg_get_serial_sequence('api_project', 'id'),
                    COALESCE((SELECT MAX(id) FROM api_project), 0) + 1,
                    false
                );
            """)

            # Fix Employee sequence
            cursor.execute("""
                SELECT setval(
                    pg_get_serial_sequence('api_employee', 'id'),
                    COALESCE((SELECT MAX(id) FROM api_employee), 0) + 1,
                    false
                );
            """)

        self.stdout.write(self.style.SUCCESS("Successfully fixed sequences"))
