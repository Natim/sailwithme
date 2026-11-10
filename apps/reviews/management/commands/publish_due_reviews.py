from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.reviews.models import Review


class Command(BaseCommand):
    help = "Publish reviews after 14 days if counterpart review is missing."

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=14)
        updated = Review.objects.filter(published_at__isnull=True, created_at__lte=cutoff).update(
            published_at=timezone.now()
        )
        self.stdout.write(self.style.SUCCESS(f"Published {updated} review(s)."))
