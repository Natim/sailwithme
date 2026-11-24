from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.core.management.base import BaseCommand
from django.urls import reverse
from django.utils.translation import gettext as _

from apps.core.mail import absolute_url, send_branded_mail
from apps.listings.iso_weeks import weeks_overlap
from apps.listings.models import Listing, SearchAlert
from apps.listings.search import nm_to_meters
from apps.listings.visibility import filter_searchable_listings

SEARCH_ALERT_TEMPLATE = "emails/listings/search_alert"


def _listing_route(listing: Listing) -> str:
    departure = listing.departure_name or "—"
    arrival = listing.arrival_name or "—"
    return f"{departure} → {arrival}"


def _listing_weeks(listing: Listing) -> str:
    if listing.year and listing.week_from and listing.week_to:
        return _("Weeks %(from)s–%(to)s, %(year)s") % {
            "from": listing.week_from,
            "to": listing.week_to,
            "year": listing.year,
        }
    return ""


def _listing_payload(listing: Listing) -> dict:
    return {
        "title": listing.title,
        "route": _listing_route(listing),
        "weeks": _listing_weeks(listing),
        "url": absolute_url(listing.get_absolute_url()),
    }


class Command(BaseCommand):
    help = "Email users when new listings match their saved alerts."

    def handle(self, *args, **options):
        sent = 0
        search_url = absolute_url(reverse("listings:search"))
        for alert in SearchAlert.objects.filter(active=True).select_related("user"):
            qs = filter_searchable_listings(Listing.objects.filter(created_at__gte=alert.created_at))
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
                listings = [_listing_payload(listing) for listing in matches]
                send_branded_mail(
                    subject=_("Sail with Me — new listings for your alert"),
                    template=SEARCH_ALERT_TEMPLATE,
                    context={
                        "listings": listings,
                        "listing_count": len(listings),
                        "search_url": search_url,
                    },
                    recipient_list=[alert.user.email],
                )
                sent += 1
        self.stdout.write(self.style.SUCCESS(f"Sent {sent} alert email(s)."))
