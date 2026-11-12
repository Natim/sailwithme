import pytest
from django.test import Client

from apps.accounts.models import User


@pytest.mark.django_db
def test_login_page_renders(client: Client):
    response = client.get("/accounts/login/")
    assert response.status_code == 200
    assert b"cdn.tailwindcss.com" in response.content
    assert b"Log in" in response.content


@pytest.mark.django_db
def test_signup_page_renders(client: Client):
    response = client.get("/accounts/signup/")
    assert response.status_code == 200
    assert b"Sign up" in response.content


@pytest.mark.django_db
def test_authenticated_nav_can_log_out(client: Client, user):
    client.force_login(user)
    response = client.get("/")
    assert response.status_code == 200
    assert b'action="/accounts/logout/"' in response.content
    logged_out = client.post("/accounts/logout/")
    assert logged_out.status_code == 302
    assert logged_out.url == "/"
    follow = client.get("/")
    assert b'action="/accounts/logout/"' not in follow.content
    assert b"Log in" in follow.content


@pytest.mark.django_db
def test_signup_creates_user(client: Client):
    response = client.post(
        "/accounts/signup/",
        {
            "email": "new-crew@example.com",
            "password1": "a-long-passphrase-1",
            "password2": "a-long-passphrase-1",
        },
    )
    assert response.status_code == 302
    assert User.objects.filter(email="new-crew@example.com").exists()
