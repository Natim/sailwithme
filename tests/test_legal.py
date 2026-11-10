import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_cgu_page(client):
    response = client.get(reverse("cgu"))
    assert response.status_code == 200
    assert b"SAS CLOUDY" in response.content
