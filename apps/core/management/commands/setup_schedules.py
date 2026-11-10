from django.core.management.base import BaseCommand
from django_q.models import Schedule


class Command(BaseCommand):
    help = "Register django-q2 schedules for listings and reviews."

    def handle(self, *args, **options):
        Schedule.objects.update_or_create(
            name="expire_listings",
            defaults={
                "func": "django.core.management.call_command",
                "args": "('expire_listings',)",
                "schedule_type": Schedule.DAILY,
            },
        )
        Schedule.objects.update_or_create(
            name="search_alerts",
            defaults={
                "func": "django.core.management.call_command",
                "args": "('send_search_alerts',)",
                "schedule_type": Schedule.DAILY,
            },
        )
        Schedule.objects.update_or_create(
            name="publish_reviews",
            defaults={
                "func": "django.core.management.call_command",
                "args": "('publish_due_reviews',)",
                "schedule_type": Schedule.DAILY,
            },
        )
        self.stdout.write(self.style.SUCCESS("Schedules registered. Run: python manage.py qcluster"))
