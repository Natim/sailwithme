/**
 * Route map on listing detail (coords from #listing-route-data json_script).
 */
(function () {
  const dataEl = document.getElementById("listing-route-data");
  const mapEl = document.getElementById("listing-detail-map");
  if (!dataEl || !mapEl || typeof L === "undefined") return;

  let route;
  try {
    route = JSON.parse(dataEl.textContent);
  } catch {
    return;
  }

  function validPair(pair) {
    return (
      Array.isArray(pair) &&
      pair.length >= 2 &&
      Number.isFinite(pair[0]) &&
      Number.isFinite(pair[1])
    );
  }

  if (!validPair(route.departure) || !validPair(route.arrival)) {
    mapEl.classList.add("hidden");
    return;
  }

  const depLl = L.latLng(route.departure[0], route.departure[1]);
  const arrLl = L.latLng(route.arrival[0], route.arrival[1]);
  const map = L.map(mapEl, { scrollWheelZoom: false });
  addSailsWithMeBasemap(map);
  L.marker(depLl).addTo(map);
  L.marker(arrLl).addTo(map);
  L.polyline([depLl, arrLl], {
    color: "#0d9488",
    weight: 3,
    dashArray: "6 8",
  }).addTo(map);

  if (depLl.equals(arrLl)) {
    map.setView(depLl, 6);
  } else {
    map.fitBounds(L.latLngBounds(depLl, arrLl), { padding: [20, 20] });
  }

  window.setTimeout(() => map.invalidateSize(), 100);
})();
