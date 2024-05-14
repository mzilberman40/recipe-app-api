"""
Django command to wait for the database to be available
"""
from django.core.management.base import BaseCommand
import time
from psycopg2 import OperationalError as Psycop2OpError
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args, **options):
        """
        EntryPoint for command
        """
        self.stdout.write("Waiting for DB.......")
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycop2OpError, OperationalError):
                self.stdout.write("The DB is not available. Waiting for 1 sec...")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("DB is ready!"))
