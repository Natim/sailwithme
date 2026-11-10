import pytest
from django.urls import reverse

from apps.accounts.models import User


@pytest.mark.django_db
def test_profile_detail_shows_skill_labels(client):
    user = User.objects.create_user(email="crew@example.com", password="x")
    profile = user.profile
    profile.skills = ["cooking", "mechanics"]
    profile.save()

    response = client.get(
        reverse("profiles:detail", kwargs={"pk": user.pk}),
        HTTP_ACCEPT_LANGUAGE="fr",
    )

    assert response.status_code == 200
    content = response.content.decode()
    assert "Compétences" in content
    assert "Cuisine" in content
    assert "Mécanique" in content
    assert "cooking" not in content
