from .base import *  # noqa: F403
from .base import env  # noqa: F401

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
