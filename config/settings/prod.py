from .base import *  # noqa: F403
from .base import ALLOWED_HOSTS, env

DEBUG = False

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        engine="django.contrib.gis.db.backends.postgis",
    )
}

SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SITE_DOMAIN = "sailwithme.net"
_site_hosts = [SITE_DOMAIN, f"www.{SITE_DOMAIN}"]
ALLOWED_HOSTS = list(dict.fromkeys([*ALLOWED_HOSTS, *_site_hosts]))
CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in _site_hosts]
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
DEFAULT_FROM_EMAIL = env(
    "DEFAULT_FROM_EMAIL",
    default="Sail with Me <noreply@sailwithme.net>",
)
EMAIL_BCC = ["contact@sailwithme.net"]
