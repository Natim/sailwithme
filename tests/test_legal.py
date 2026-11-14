import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_cgu_page(client):
    response = client.get(reverse("cgu"))
    assert response.status_code == 200
    assert b"SAS CLOUDY" in response.content


@pytest.mark.django_db
def test_cloudy_cross_link(client):
    response = client.get(reverse("cloudy"))
    assert response.status_code == 200
    body = response.content.decode()
    assert "https://www.cloudy.fr/" in body
    assert "logbook" in body.lower()
    assert "support@cloudy.fr" in body
    home = client.get(reverse("home"))
    assert reverse("cloudy") in home.content.decode()
    french = client.get(reverse("cloudy"), HTTP_ACCEPT_LANGUAGE="fr")
    assert "carnet de vol" in french.content.decode()
    assert "Carnet Cloudy" in client.get(reverse("home"), HTTP_ACCEPT_LANGUAGE="fr").content.decode()
