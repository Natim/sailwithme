import pytest

from apps.accounts.models import User
from apps.profiles.templatetags.profile_extras import public_name


@pytest.mark.django_db
def test_public_name_uses_pseudo():
    user = User.objects.create_user(email="private@example.com", password="x")
    profile = user.profile
    profile.pseudo = "CapAuLarge"
    profile.save()
    assert profile.public_name() == "CapAuLarge"


@pytest.mark.django_db
def test_public_name_fallback_without_pseudo():
    user = User.objects.create_user(email="private@example.com", password="x")
    profile = user.profile
    assert profile.public_name().startswith("Marin-")
    assert "@" not in profile.public_name()


@pytest.mark.django_db
def test_public_name_filter_does_not_expose_email():
    user = User.objects.create_user(email="private@example.com", password="x")
    user.profile.pseudo = "Skip"
    user.profile.save()
    assert public_name(user) == "Skip"
    assert "@" not in public_name(user)
