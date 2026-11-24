from datetime import timedelta

import pytest
from django.contrib.gis.geos import Point
from django.utils import timezone

from apps.accounts.models import User
from apps.billing.models import Membership, MembershipPlan
from apps.billing.services import (
    author_listing_searchable,
    grant_registration_crew_trial,
    user_has_crew_pass,
)
from apps.listings.models import Listing, ListingKind, ListingStatus, ProgrammeType
from apps.listings.search import search_listings
from apps.profiles.models import ProfileRole


@pytest.mark.django_db
def test_new_user_receives_crew_trial():
    user = User.objects.create_user(email="trial@example.com", password="x")
    trial = Membership.objects.get(user=user, plan=MembershipPlan.CREW_TRIAL)
    assert trial.active
    assert trial.valid_until is not None
    assert trial.valid_until > timezone.now() + timedelta(days=29)
    assert user_has_crew_pass(user)


@pytest.mark.django_db
def test_grant_registration_crew_trial_is_idempotent():
    user = User.objects.create_user(email="once@example.com", password="x")
    assert Membership.objects.filter(user=user, plan=MembershipPlan.CREW_TRIAL).count() == 1
    assert grant_registration_crew_trial(user) is None
    assert Membership.objects.filter(user=user, plan=MembershipPlan.CREW_TRIAL).count() == 1


@pytest.mark.django_db
def test_crew_listing_hidden_after_trial_expires(user):
    Membership.objects.filter(user=user).update(valid_until=timezone.now() - timedelta(days=1))
    Listing.objects.create(
        author=user,
        kind=ListingKind.BERTH_WANTED,
        title="Hidden berth",
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
    assert not author_listing_searchable(user)
    assert len(search_listings({})) == 0


@pytest.mark.django_db
def test_skipper_listing_visible_without_crew_pass(user):
    user.profile.role = ProfileRole.SKIPPER
    user.profile.save(update_fields=["role"])
    Membership.objects.filter(user=user).update(valid_until=timezone.now() - timedelta(days=1))
    Listing.objects.create(
        author=user,
        kind=ListingKind.CREW_WANTED,
        title="Skipper ARC",
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
    assert author_listing_searchable(user)
    assert len(search_listings({})) == 1


@pytest.mark.django_db
def test_crew_cannot_create_listing_without_pass(client, user):
    Membership.objects.filter(user=user).update(valid_until=timezone.now() - timedelta(days=1))
    client.force_login(user)
    response = client.get("/listings/new/")
    assert response.status_code == 302
    assert "/billing/pricing" in response.url
