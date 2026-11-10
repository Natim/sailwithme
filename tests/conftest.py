import pytest

from apps.accounts.models import User


@pytest.fixture
def user(db):
    return User.objects.create_user(email="crew@example.com", password="test-pass-123")
