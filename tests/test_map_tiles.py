from apps.core.map_tiles import leaflet_tile_layer


def test_default_tiles_use_osm_france(settings):
    settings.CARTO_API_KEY = ""
    cfg = leaflet_tile_layer()
    assert "openstreetmap.fr" in cfg["url"]
    assert "cartocdn" not in cfg["url"]


def test_carto_when_api_key_set(settings):
    settings.CARTO_API_KEY = "test-key"
    cfg = leaflet_tile_layer()
    assert "cartocdn.com" in cfg["url"]
    assert "api_key=test-key" in cfg["url"]
