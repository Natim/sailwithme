import pytest
from django.contrib.gis.geos import Point

from apps.listings.forms import ListingSearchForm
from apps.listings.models import Listing, ListingKind, ListingStatus, ProgrammeType
from apps.listings.search import search_listings


@pytest.mark.django_db
def test_search_form_empty_bound_is_valid():
    form = ListingSearchForm({})
    assert form.is_valid()


@pytest.mark.django_db
def test_search_returns_published_listings(user):
    Listing.objects.create(
        author=user,
        kind=ListingKind.CREW_WANTED,
        title="ARC Las Palmas",
        description="Transat",
        programme_type=ProgrammeType.TRANSATLANTIC,
        departure_name="Las Palmas",
        arrival_name="Le Marin",
        departure_point=Point(-15.4, 28.1, srid=4326),
        arrival_point=Point(-61.0, 14.5, srid=4326),
        year=2026,
        week_from=46,
        week_to=50,
        date_from="2026-11-09",
        date_to="2026-12-13",
        status=ListingStatus.PUBLISHED,
    )
    results = search_listings({})
    assert len(results) == 1


@pytest.mark.django_db
def test_search_page_lists_announcements(client, user):
    Listing.objects.create(
        author=user,
        kind=ListingKind.CREW_WANTED,
        title="Test",
        description="x",
        programme_type=ProgrammeType.TRANSATLANTIC,
        departure_name="A",
        arrival_name="B",
        departure_point=Point(0, 0, srid=4326),
        arrival_point=Point(1, 1, srid=4326),
        year=2026,
        week_from=10,
        week_to=12,
        date_from="2026-03-02",
        date_to="2026-03-22",
        status=ListingStatus.PUBLISHED,
    )
    response = client.get("/listings/")
    assert response.status_code == 200
    assert b"Test" in response.content
