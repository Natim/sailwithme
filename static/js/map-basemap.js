/**
 * Tile URLs come from django (leaflet_tile via json_script).
 * Default: OSM France — not tile.openstreetmap.org (usage policy) or CARTO without API key.
 */
function addSailsWithMeBasemap(map) {
  const el = document.getElementById("sails-map-tile-config");
  const cfg = el ? JSON.parse(el.textContent) : null;
  const fallback = {
    url: "https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png",
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> / OSM France',
    subdomains: "abc",
    maxZoom: 19,
  };
  const opts = cfg || fallback;
  return L.tileLayer(opts.url, {
    attribution: opts.attribution,
    subdomains: opts.subdomains,
    maxZoom: opts.maxZoom,
  }).addTo(map);
}
