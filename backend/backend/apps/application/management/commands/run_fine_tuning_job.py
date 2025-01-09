from django.core.management.base import BaseCommand
from backend.apps.application.tasks import run_scheduler


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        run_scheduler()
