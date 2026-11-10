import pytest

from apps.accounts.models import User
from apps.profiles.models import Profile


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
