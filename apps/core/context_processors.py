from django.conf import settings

from apps.core.map_tiles import leaflet_tile_layer


def site_settings(request):
    return {
        "SITE_NAME": "Sails with Me",
        "STRIPE_PUBLIC_KEY": getattr(settings, "STRIPE_PUBLIC_KEY", ""),
        "leaflet_tile": leaflet_tile_layer(),
    }
