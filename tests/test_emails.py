import pytest
from django.contrib.gis.geos import Point
from django.core import mail
from django.test import override_settings
from django.urls import reverse

from apps.accounts.models import User
from apps.listings.models import (
    Listing,
    ListingKind,
    ListingStatus,
    ProgrammeType,
)

BCC = ["contact@sailwithme.net"]


def make_berth_listing(author, **overrides):
    data = {
        "author": author,
        "kind": ListingKind.BERTH_WANTED,
        "title": "Croisière Méditerranée",
        "description": "x",
        "programme_type": ProgrammeType.MEDITERRANEAN,
        "departure_name": "Marseille",
        "arrival_name": "Corse",
        "departure_point": Point(5.37, 43.29, srid=4326),
        "arrival_point": Point(8.73, 41.92, srid=4326),
        "year": 2026,
        "week_from": 20,
        "week_to": 22,
        "status": ListingStatus.PUBLISHED,
    }
    data.update(overrides)
    return Listing.objects.create(**data)


@pytest.fixture
def other_user(db):
    return User.objects.create_user(email="other@example.com", password="test-pass-123")


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
@pytest.mark.django_db
def test_signup_sends_confirmation_email(client):
    with override_settings(EMAIL_BCC=BCC):
        response = client.post(
            reverse("account_signup"),
            {
                "email": "new-crew@example.com",
                "password1": "a-long-passphrase-1",
                "password2": "a-long-passphrase-1",
            },
        )
    assert response.status_code == 302
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["new-crew@example.com"]
    assert mail.outbox[0].bcc == BCC


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
@pytest.mark.django_db
def test_password_reset_sends_email(client, user):
    with override_settings(EMAIL_BCC=BCC):
        response = client.post(
            reverse("account_reset_password"),
            {"email": user.email},
        )
    assert response.status_code == 302
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [user.email]
    assert mail.outbox[0].bcc == BCC


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
@pytest.mark.django_db
def test_application_sends_email_to_author(client, user, other_user):
    listing = make_berth_listing(user)
    client.force_login(other_user)
    with override_settings(EMAIL_BCC=BCC):
        response = client.post(
            reverse("listings:apply", kwargs={"pk": listing.pk}),
            {"message": "Bonjour, je suis motivé."},
        )
    assert response.status_code == 302
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [user.email]
    assert mail.outbox[0].bcc == BCC
    assert listing.title in mail.outbox[0].subject


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
@pytest.mark.django_db
def test_duplicate_application_does_not_send_second_email(client, user, other_user):
    listing = make_berth_listing(user)
    client.force_login(other_user)
    url = reverse("listings:apply", kwargs={"pk": listing.pk})
    with override_settings(EMAIL_BCC=BCC):
        client.post(url, {"message": "First"})
        client.post(url, {"message": "Again"})
    assert len(mail.outbox) == 1
