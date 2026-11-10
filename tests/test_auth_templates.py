import pytest
from django.test import Client


@pytest.mark.django_db
def test_login_page_renders(client: Client):
    response = client.get("/accounts/login/")
    assert response.status_code == 200
    assert b"cdn.tailwindcss.com" in response.content
    assert b"Log in" in response.content
