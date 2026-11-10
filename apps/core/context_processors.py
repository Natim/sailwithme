from django.conf import settings

from apps.core.map_tiles import leaflet_tile_layer


def site_settings(request):
    ctx = {
        "SITE_NAME": "Sail with Me",
        "STRIPE_PUBLIC_KEY": getattr(settings, "STRIPE_PUBLIC_KEY", ""),
        "leaflet_tile": leaflet_tile_layer(),
        "nav_profile_photo_url": None,
    }
    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        profile = getattr(user, "profile", None)
        if profile and profile.photo:
            ctx["nav_profile_photo_url"] = profile.photo.url
    return ctx
