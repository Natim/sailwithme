import uuid

import pytest
from django.contrib.gis.geos import Point

from apps.accounts.models import User
from apps.listings.models import (
    Listing,
    ListingApplication,
    ListingKind,
    ListingStatus,
    ProgrammeType,
)


def make_listing(author, **overrides):
    data = {
        "author": author,
        "kind": ListingKind.CREW_WANTED,
        "title": "Transat",
        "description": "x",
        "programme_type": ProgrammeType.TRANSATLANTIC,
        "departure_name": "Las Palmas",
        "arrival_name": "Le Marin",
        "departure_point": Point(-15.4, 28.1, srid=4326),
        "arrival_point": Point(-61.0, 14.5, srid=4326),
        "year": 2026,
        "week_from": 46,
        "week_to": 50,
        "status": ListingStatus.PUBLISHED,
    }
    data.update(overrides)
    return Listing.objects.create(**data)


@pytest.fixture
def other_user(db):
    return User.objects.create_user(email="other@example.com", password="test-pass-123")


@pytest.mark.django_db
def test_listing_pk_is_uuid(user):
    listing = make_listing(user)
    assert isinstance(listing.pk, uuid.UUID)
    assert str(listing.pk) in listing.get_absolute_url()


@pytest.mark.django_db
def test_other_user_cannot_edit_or_delete(client, user, other_user):
    listing = make_listing(user)
    client.force_login(other_user)
    assert client.get(f"/listings/{listing.pk}/edit/").status_code == 404
    assert client.post(f"/listings/{listing.pk}/delete/").status_code == 404
    assert Listing.objects.filter(pk=listing.pk).exists()


@pytest.mark.django_db
def test_delete_without_applications_removes_listing(client, user):
    listing = make_listing(user)
    client.force_login(user)
    response = client.post(f"/listings/{listing.pk}/delete/")
    assert response.status_code == 302
    assert not Listing.objects.filter(pk=listing.pk).exists()


@pytest.mark.django_db
def test_delete_with_applications_withdraws_listing(client, user, other_user):
    listing = make_listing(user)
    ListingApplication.objects.create(listing=listing, applicant=other_user, message="Hello")
    client.force_login(user)
    client.post(f"/listings/{listing.pk}/delete/")
    listing.refresh_from_db()
    assert listing.status == ListingStatus.WITHDRAWN
    assert listing.applications.count() == 1


@pytest.mark.django_db
def test_withdrawn_listing_hidden_from_others(client, user, other_user):
    listing = make_listing(user, status=ListingStatus.WITHDRAWN)
    assert client.get(f"/listings/{listing.pk}/").status_code == 404
    client.force_login(user)
    assert client.get(f"/listings/{listing.pk}/").status_code == 200


@pytest.mark.django_db
def test_edit_form_prefills_route_coords(client, user):
    listing = make_listing(user)
    client.force_login(user)
    response = client.get(f"/listings/{listing.pk}/edit/")
    assert response.status_code == 200
    assert b'value="28.1' in response.content
