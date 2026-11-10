from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Q

from .iso_weeks import weeks_overlap
from .models import Listing, ListingStatus


def nm_to_meters(nm: int) -> float:
    return nm * 1852


def search_listings(cleaned_data: dict) -> list[Listing]:
    qs = Listing.objects.filter(status=ListingStatus.PUBLISHED).select_related(
        "author", "boat", "departure_port", "arrival_port"
    )

    kind = cleaned_data.get("kind")
    if kind:
        qs = qs.filter(kind=kind)

    programme = cleaned_data.get("programme_type")
    if programme:
        qs = qs.filter(programme_type=programme)

    q = cleaned_data.get("q")
    if q:
        qs = qs.filter(
            Q(title__icontains=q)
            | Q(description__icontains=q)
            | Q(departure_name__icontains=q)
            | Q(arrival_name__icontains=q)
        )

    d_lat = cleaned_data.get("departure_lat")
    d_lng = cleaned_data.get("departure_lng")
    d_radius = cleaned_data.get("departure_radius_nm") or 150
    if d_lat is not None and d_lng is not None:
        pt = Point(d_lng, d_lat, srid=4326)
        qs = qs.filter(departure_point__distance_lte=(pt, D(m=nm_to_meters(d_radius))))

    a_lat = cleaned_data.get("arrival_lat")
    a_lng = cleaned_data.get("arrival_lng")
    a_radius = cleaned_data.get("arrival_radius_nm") or 150
    if a_lat is not None and a_lng is not None:
        pt = Point(a_lng, a_lat, srid=4326)
        qs = qs.filter(arrival_point__distance_lte=(pt, D(m=nm_to_meters(a_radius))))

    year = cleaned_data.get("year")
    wf = cleaned_data.get("week_from")
    wt = cleaned_data.get("week_to")
    if year and wf and wt:
        matching_ids = []
        for listing in qs:
            if weeks_overlap(listing.year, listing.week_from, listing.week_to, year, wf, wt):
                matching_ids.append(listing.pk)
        qs = qs.filter(pk__in=matching_ids)

    sort = cleaned_data.get("sort") or "relevance"
    if sort == "date":
        qs = qs.order_by("date_from", "-featured")
    elif d_lat is not None and d_lng is not None:
        pt = Point(d_lng, d_lat, srid=4326)
        qs = qs.annotate(dep_distance=Distance("departure_point", pt)).order_by(
            "dep_distance", "-featured", "date_from"
        )
    else:
        qs = qs.order_by("-featured", "date_from")

    return list(qs)


def listings_for_map(listings: list[Listing]) -> list[dict]:
    out = []
    for listing in listings:
        out.append(
            {
                "id": listing.pk,
                "title": listing.title,
                "departure": [listing.departure_point.y, listing.departure_point.x],
                "arrival": [listing.arrival_point.y, listing.arrival_point.x],
                "url": listing.get_absolute_url(),
            }
        )
    return out
