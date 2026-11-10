import os
from pathlib import Path

from .base import *  # noqa: F403
from .base import BASE_DIR, env  # noqa: F401

DEBUG = True

_conda = os.environ.get("CONDA_PREFIX")
if env.bool("USE_SPATIALITE", default=bool(_conda)):
    _spatialite = env(
        "SPATIALITE_LIBRARY_PATH",
        default=str(Path(_conda) / "lib/libspatialite.so.8") if _conda else "",
    )
    if _spatialite:
        SPATIALITE_LIBRARY_PATH = _spatialite  # noqa: F405
    DATABASES = {
        "default": {
            "ENGINE": "django.contrib.gis.db.backends.spatialite",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": env.db(
            "DATABASE_URL",
            default="postgis://sailswithme:sailswithme@127.0.0.1:5432/sailswithme",
            engine="django.contrib.gis.db.backends.postgis",
        )
    }

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
