import pytest
from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from django.test import Client, override_settings

from apps.accounts.models import User

SOCIAL_PROVIDERS = {
    "google": {
        "APPS": [{"client_id": "google-client", "secret": "google-secret"}],
        "OAUTH_PKCE_ENABLED": True,
    },
    "facebook": {
        "APPS": [{"client_id": "fb-client", "secret": "fb-secret"}],
        "SCOPE": ["email", "public_profile"],
        "VERSION": "v23.0",
    },
}


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


@override_settings(SOCIALACCOUNT_PROVIDERS={})
@pytest.mark.django_db
def test_login_hides_social_buttons_without_credentials(client: Client):
    response = client.get("/accounts/login/")
    assert response.status_code == 200
    assert b"Continue with Google" not in response.content
    assert b"Continue with Facebook" not in response.content


@override_settings(SOCIALACCOUNT_PROVIDERS=SOCIAL_PROVIDERS)
@pytest.mark.django_db
def test_login_and_signup_show_social_buttons(client: Client):
    login = client.get("/accounts/login/")
    signup = client.get("/accounts/signup/")
    for response in (login, signup):
        assert response.status_code == 200
        content = response.content.decode()
        assert "Continue with Google" in content
        assert "Continue with Facebook" in content
        assert 'action="/accounts/google/login/?process=login"' in content
        assert 'action="/accounts/facebook/login/?process=login"' in content


@override_settings(SOCIALACCOUNT_PROVIDERS=SOCIAL_PROVIDERS)
@pytest.mark.django_db
def test_social_login_redirects_to_provider(client: Client):
    google = client.post("/accounts/google/login/?process=login")
    assert google.status_code == 302
    assert google.url.startswith("https://accounts.google.com/")
    assert "client_id=google-client" in google.url

    facebook = client.post("/accounts/facebook/login/?process=login")
    assert facebook.status_code == 302
    assert "facebook.com" in facebook.url
    assert "client_id=fb-client" in facebook.url


@override_settings(SOCIALACCOUNT_PROVIDERS=SOCIAL_PROVIDERS)
@pytest.mark.django_db
def test_profile_links_to_social_connections(client: Client, user):
    client.force_login(user)
    response = client.get("/profiles/me/")
    assert response.status_code == 200
    assert b"Google and Facebook sign-in" in response.content

    connections = client.get("/accounts/3rdparty/")
    assert connections.status_code == 200
    content = connections.content.decode()
    assert "Continue with Google" in content
    assert 'action="/accounts/google/login/?process=connect"' in content
    assert "No Google or Facebook account is linked yet." in content


@pytest.mark.django_db
def test_social_connections_require_login(client: Client):
    response = client.get("/accounts/3rdparty/")
    assert response.status_code == 302
    assert "/accounts/login/" in response.url


@pytest.mark.django_db
def test_email_confirm_shows_coral_button(client: Client, user):
    email_address = EmailAddress.objects.create(
        user=user,
        email=user.email,
        verified=False,
        primary=True,
    )
    confirmation = EmailConfirmationHMAC.create(email_address)
    response = client.get(f"/accounts/confirm-email/{confirmation.key}/")
    assert response.status_code == 200
    assert b"btn-coral" in response.content
    assert b'type="submit"' in response.content
