from django.conf import settings


def leaflet_tile_layer() -> dict:
    """Tile layer config for Leaflet (client-side); see .env.example."""
    carto_key = getattr(settings, "CARTO_API_KEY", "") or ""
    if carto_key:
        return {
            "url": (
                "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/"
                f"{{z}}/{{x}}/{{y}}{{r}}.png?api_key={carto_key}"
            ),
            "attribution": (
                '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> '
                '&copy; <a href="https://carto.com/attributions">CARTO</a>'
            ),
            "subdomains": "abcd",
            "maxZoom": 20,
        }
    return {
        "url": "https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png",
        "attribution": (
            '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> '
            '/ <a href="https://www.openstreetmap.fr/">OSM France</a>'
        ),
        "subdomains": "abc",
        "maxZoom": 19,
    }
