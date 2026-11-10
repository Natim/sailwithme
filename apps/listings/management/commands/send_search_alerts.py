from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.core.mail import send_mail
from django.core.management.base import BaseCommand

from apps.listings.iso_weeks import weeks_overlap
from apps.listings.models import Listing, ListingStatus, SearchAlert
from apps.listings.search import nm_to_meters


class Command(BaseCommand):
    help = "Email users when new listings match their saved alerts."

    def handle(self, *args, **options):
        sent = 0
        for alert in SearchAlert.objects.filter(active=True).select_related("user"):
            qs = Listing.objects.filter(
                status=ListingStatus.PUBLISHED,
                created_at__gte=alert.created_at,
            )
            if alert.kind:
                qs = qs.filter(kind=alert.kind)
            if alert.programme_type:
                qs = qs.filter(programme_type=alert.programme_type)
            if alert.departure_lat is not None and alert.departure_lng is not None:
                pt = Point(alert.departure_lng, alert.departure_lat, srid=4326)
                qs = qs.filter(departure_point__distance_lte=(pt, D(m=nm_to_meters(alert.departure_radius_nm))))
            if alert.arrival_lat is not None and alert.arrival_lng is not None:
                pt = Point(alert.arrival_lng, alert.arrival_lat, srid=4326)
                qs = qs.filter(arrival_point__distance_lte=(pt, D(m=nm_to_meters(alert.arrival_radius_nm))))
            matches = []
            for listing in qs:
                if alert.year and alert.week_from and alert.week_to:
                    if not weeks_overlap(
                        listing.year,
                        listing.week_from,
                        listing.week_to,
                        alert.year,
                        alert.week_from,
                        alert.week_to,
                    ):
                        continue
                matches.append(listing)
            if matches:
                body = "\n".join(f"- {listing.title}: {listing.get_absolute_url()}" for listing in matches)
                send_mail(
                    subject="Sail with Me — nouvelles annonces pour ton alerte",
                    message=body,
                    from_email=None,
                    recipient_list=[alert.user.email],
                )
                sent += 1
        self.stdout.write(self.style.SUCCESS(f"Sent {sent} alert email(s)."))
