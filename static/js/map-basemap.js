/**
 * Do not use tile.openstreetmap.org in production (OSM tile usage policy).
 * CARTO/OSM-derived tiles — https://carto.com/attributions
 */
function addSailsWithMeBasemap(map) {
  return L.tileLayer(
    "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png",
    {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
      subdomains: "abcd",
      maxZoom: 20,
    }
  ).addTo(map);
}
