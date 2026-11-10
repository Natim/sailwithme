from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.listings.models import Listing, ListingStatus


class Command(BaseCommand):
    help = "Mark published listings past their end date as expired."

    def handle(self, *args, **options):
        today = timezone.now().date()
        updated = Listing.objects.filter(
            status=ListingStatus.PUBLISHED,
            date_to__lt=today,
        ).update(status=ListingStatus.EXPIRED)
        self.stdout.write(self.style.SUCCESS(f"Expired {updated} listing(s)."))
