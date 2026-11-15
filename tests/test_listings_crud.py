import uuid

import pytest
from django.contrib.gis.geos import Point

from apps.accounts.models import User
from apps.listings.models import (
    ApplicationStatus,
    Listing,
    ListingApplication,
    ListingKind,
    ListingStatus,
    ProgrammeType,
    Voyage,
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
def test_reject_application(client, user, other_user):
    listing = make_listing(user)
    application = ListingApplication.objects.create(listing=listing, applicant=other_user, message="Hello")
    client.force_login(user)
    response = client.get(f"/listings/applications/{application.pk}/reject/", follow=True)
    assert response.status_code == 200
    application.refresh_from_db()
    assert application.status == ApplicationStatus.REJECTED
    assert b"Application declined." in response.content


@pytest.mark.django_db
def test_accept_application_creates_voyage(client, user, other_user):
    listing = make_listing(user)
    application = ListingApplication.objects.create(listing=listing, applicant=other_user, message="Hello")
    client.force_login(user)
    response = client.get(f"/listings/applications/{application.pk}/accept/", follow=True)
    assert response.status_code == 200
    application.refresh_from_db()
    assert application.status == ApplicationStatus.ACCEPTED
    voyage = Voyage.objects.get(listing=listing)
    assert other_user in voyage.crew.all()
    assert b"Application accepted" in response.content


@pytest.mark.django_db
def test_edit_form_prefills_route_coords(client, user):
    listing = make_listing(user)
    client.force_login(user)
    response = client.get(f"/listings/{listing.pk}/edit/")
    assert response.status_code == 200
    assert b'value="28.1' in response.content


@pytest.mark.django_db
def test_create_berth_wanted_listing_strips_skipper_fields(client, user):
    client.force_login(user)
    data = {
        "kind": ListingKind.BERTH_WANTED,
        "title": "Cherche place",
        "description": "Disponible pour transat.",
        "programme_type": ProgrammeType.TRANSATLANTIC,
        "departure_name": "Las Palmas",
        "arrival_name": "Le Marin",
        "departure_lat": 28.1,
        "departure_lng": -15.4,
        "arrival_lat": 14.5,
        "arrival_lng": -61.0,
        "year": 2026,
        "week_from": 46,
        "week_to": 50,
        "flexibility_nm": 50,
    }
    response = client.post("/listings/new/", data)
    assert response.status_code == 302
    listing = Listing.objects.get(title="Cherche place")
    assert listing.kind == ListingKind.BERTH_WANTED
    assert listing.boat_id is None
    assert listing.min_skill_level == ""
    assert listing.berths_available == 1


@pytest.mark.django_db
def test_create_training_listing(client, user):
    client.force_login(user)
    data = {
        "kind": ListingKind.TRAINING,
        "title": "Four days in Martinique",
        "description": "Harbour training while circumnavigating.",
        "departure_name": "Le Marin",
        "arrival_name": "",
        "departure_lat": 14.47,
        "departure_lng": -60.87,
        "arrival_lat": "",
        "arrival_lng": "",
        "year": 2026,
        "week_from": 4,
        "week_to": 5,
        "duration_days": 4,
        "berths_available": 4,
        "daily_contribution_eur": "400",
        "flexibility_nm": 50,
    }
    response = client.post("/listings/new/", data)
    assert response.status_code == 302
    listing = Listing.objects.get(title="Four days in Martinique")
    assert listing.kind == ListingKind.TRAINING
    assert listing.programme_type == ProgrammeType.ROUND_TRIP_CRUISE
    assert listing.arrival_name == "Le Marin"
    assert listing.daily_contribution_eur == 400
    assert listing.departure_point.equals(listing.arrival_point)


@pytest.mark.django_db
def test_training_listing_detail_shows_training_fee(client, user):
    listing = make_listing(
        user,
        kind=ListingKind.TRAINING,
        programme_type=ProgrammeType.ROUND_TRIP_CRUISE,
        departure_name="Le Marin",
        arrival_name="Le Marin",
        arrival_point=Point(-60.87, 14.47, srid=4326),
        daily_contribution_eur=400,
    )
    response = client.get(listing.get_absolute_url())
    assert response.status_code == 200
    assert b"Training fee" in response.content
    assert b"non-commercial" not in response.content
    assert b"Round-trip cruise" in response.content


@pytest.mark.django_db
def test_training_form_includes_authorization_warning(client, user):
    client.force_login(user)
    response = client.get("/listings/new/")
    assert response.status_code == 200
    assert b"authorized to organize this kind of session" in response.content


@pytest.mark.django_db
def test_apply_training_listing(client, user, other_user):
    other_user.is_staff = True
    other_user.save(update_fields=["is_staff"])
    listing = make_listing(user, kind=ListingKind.TRAINING, programme_type=ProgrammeType.ROUND_TRIP_CRUISE)
    client.force_login(other_user)
    response = client.post(
        f"/listings/{listing.pk}/apply/",
        {"message": "I would like to join."},
    )
    assert response.status_code == 302
    assert ListingApplication.objects.filter(listing=listing, applicant=other_user).exists()


@pytest.mark.django_db
def test_accept_application_berth_wanted_inverts_voyage_roles(client, user, other_user):
    listing = make_listing(user, kind=ListingKind.BERTH_WANTED)
    application = ListingApplication.objects.create(listing=listing, applicant=other_user, message="Bateau prêt")
    client.force_login(user)
    response = client.get(f"/listings/applications/{application.pk}/accept/", follow=True)
    assert response.status_code == 200
    voyage = Voyage.objects.get(listing=listing)
    assert voyage.skipper_id == other_user.id
    assert user in voyage.crew.all()
