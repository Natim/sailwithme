import pytest
from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.accounts.models import User
from apps.boats.models import Boat, BoatPhoto
from apps.listings.models import Listing, ListingKind, ListingStatus, ProgrammeType

GIF_1PX = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,"
    b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


@pytest.fixture
def boat(user):
    return Boat.objects.create(owner=user, name="Aurore", berths=4)


@pytest.mark.django_db
def test_create_boat_with_berths(client, user):
    client.force_login(user)
    response = client.post(
        "/boats/new/",
        {"name": "Mistral", "boat_type": "monohull", "berths": 6},
    )
    assert response.status_code == 302
    assert Boat.objects.get(name="Mistral").berths == 6


@pytest.mark.django_db
def test_other_user_cannot_delete_boat(client, boat):
    other = User.objects.create_user(email="other@example.com", password="x")
    client.force_login(other)
    assert client.post(f"/boats/{boat.pk}/delete/").status_code == 404
    assert Boat.objects.filter(pk=boat.pk).exists()


@pytest.mark.django_db
def test_delete_boat_detaches_listings(client, user, boat):
    listing = Listing.objects.create(
        author=user,
        boat=boat,
        kind=ListingKind.CREW_WANTED,
        title="Transat",
        description="x",
        programme_type=ProgrammeType.TRANSATLANTIC,
        departure_name="A",
        arrival_name="B",
        departure_point=Point(0, 0, srid=4326),
        arrival_point=Point(1, 1, srid=4326),
        year=2026,
        week_from=10,
        week_to=12,
        status=ListingStatus.PUBLISHED,
    )
    client.force_login(user)
    client.post(f"/boats/{boat.pk}/delete/")
    listing.refresh_from_db()
    assert listing.boat is None
    assert not Boat.objects.filter(pk=boat.pk).exists()


@pytest.mark.django_db
def test_add_and_delete_photo(client, user, boat, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    client.force_login(user)
    upload = SimpleUploadedFile("pont.gif", GIF_1PX, content_type="image/gif")
    client.post(f"/boats/{boat.pk}/photos/", {"image": upload, "sort_order": 0})
    photo = BoatPhoto.objects.get(boat=boat)
    client.post(f"/boats/photos/{photo.pk}/delete/")
    assert not BoatPhoto.objects.filter(pk=photo.pk).exists()


@pytest.mark.django_db
def test_photo_upload_rejects_non_image_extension(client, user, boat, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    client.force_login(user)
    upload = SimpleUploadedFile("script.exe", GIF_1PX, content_type="image/gif")
    client.post(f"/boats/{boat.pk}/photos/", {"image": upload, "sort_order": 0})
    assert not BoatPhoto.objects.filter(boat=boat).exists()
