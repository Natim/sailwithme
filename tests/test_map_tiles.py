import pytest

from apps.accounts.models import User
from apps.core.map_tiles import leaflet_tile_layer, openlayers_tile_layer


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


def test_admin_tiles_avoid_osm_volunteer_servers(settings):
    settings.CARTO_API_KEY = ""
    cfg = openlayers_tile_layer()
    assert "tile.openstreetmap.fr/osmfr" in cfg["url"]
    assert "{a-c}" in cfg["url"]
    assert "{s}" not in cfg["url"]
    assert "tile.openstreetmap.org" not in cfg["url"]


def test_admin_tiles_use_carto_when_api_key_set(settings):
    settings.CARTO_API_KEY = "test-key"
    cfg = openlayers_tile_layer()
    assert cfg["url"].startswith("https://{a-d}.basemaps.cartocdn.com/")
    assert "{r}" not in cfg["url"]
    assert "api_key=test-key" in cfg["url"]


@pytest.mark.django_db
def test_port_admin_map_uses_configured_tiles(client, settings):
    settings.CARTO_API_KEY = ""
    User.objects.create_superuser(email="admin@example.com", password="test-pass-123")
    assert client.login(email="admin@example.com", password="test-pass-123")
    response = client.get("/admin/listings/port/add/")
    assert response.status_code == 200
    body = response.content.decode()
    assert "tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png" in body
    assert "tile.openstreetmap.org" not in body
    assert "ol.source.OSM()" not in body
