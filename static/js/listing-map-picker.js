/**
 * Two-click route picker: departure then arrival, with markers and dashed polyline.
 */
function initListingMapPicker(mapId) {
  const i18nEl = document.getElementById("listing-map-i18n");
  const defaults = {
    hintStart: "First click: departure · second click: arrival",
    hintDeparture: "Departure set. Click for arrival.",
    hintEdit: "Route set. Click the map to change departure, then arrival.",
    departure: "Departure",
    arrival: "Arrival",
  };
  let i18n = defaults;
  if (i18nEl) {
    try {
      i18n = { ...defaults, ...JSON.parse(i18nEl.textContent) };
    } catch {
      /* use defaults */
    }
  }

  const depLat = document.getElementById("id_departure_lat");
  const depLng = document.getElementById("id_departure_lng");
  const arrLat = document.getElementById("id_arrival_lat");
  const arrLng = document.getElementById("id_arrival_lng");
  const hint = document.getElementById("listing-map-hint");
  if (!depLat || !depLng || !arrLat || !arrLng) {
    return;
  }

  const map = L.map(mapId).setView([28.1, -15.4], 4);
  addSailsWithMeBasemap(map);
  window.setTimeout(() => map.invalidateSize(), 100);

  const layer = L.layerGroup().addTo(map);
  let step = 0;
  let depMarker = null;
  let arrMarker = null;
  let routeLine = null;

  const setHint = (msg) => {
    if (hint) hint.textContent = msg;
  };

  const drawRoute = () => {
    layer.clearLayers();
    depMarker = null;
    arrMarker = null;
    routeLine = null;
    const dLat = parseFloat(depLat.value);
    const dLng = parseFloat(depLng.value);
    const aLat = parseFloat(arrLat.value);
    const aLng = parseFloat(arrLng.value);
    const bounds = [];
    if (!Number.isNaN(dLat) && !Number.isNaN(dLng)) {
      depMarker = L.marker([dLat, dLng], { alt: i18n.departure })
        .bindTooltip(i18n.departure, { permanent: false })
        .addTo(layer);
      bounds.push([dLat, dLng]);
    }
    if (!Number.isNaN(aLat) && !Number.isNaN(aLng)) {
      arrMarker = L.marker([aLat, aLng], { alt: i18n.arrival })
        .bindTooltip(i18n.arrival, { permanent: false })
        .addTo(layer);
      bounds.push([aLat, aLng]);
    }
    if (depMarker && arrMarker) {
      routeLine = L.polyline(
        [
          [dLat, dLng],
          [aLat, aLng],
        ],
        { color: "#0369a1", weight: 3, dashArray: "8 10" }
      ).addTo(layer);
      map.fitBounds(bounds, { padding: [32, 32], maxZoom: 8 });
      setHint(i18n.hintEdit);
      step = 2;
    } else if (depMarker) {
      setHint(i18n.hintDeparture);
      step = 1;
      map.setView([dLat, dLng], Math.max(map.getZoom(), 5));
    } else {
      setHint(i18n.hintStart);
      step = 0;
    }
  };

  map.on("click", (e) => {
    const { lat, lng } = e.latlng;
    if (step === 0) {
      depLat.value = lat.toFixed(6);
      depLng.value = lng.toFixed(6);
      arrLat.value = "";
      arrLng.value = "";
      step = 1;
    } else if (step === 1) {
      arrLat.value = lat.toFixed(6);
      arrLng.value = lng.toFixed(6);
      step = 2;
    } else {
      depLat.value = lat.toFixed(6);
      depLng.value = lng.toFixed(6);
      arrLat.value = "";
      arrLng.value = "";
      step = 1;
    }
    drawRoute();
  });

  const resetBtn = document.getElementById("listing-map-reset");
  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      depLat.value = "";
      depLng.value = "";
      arrLat.value = "";
      arrLng.value = "";
      drawRoute();
    });
  }

  drawRoute();
}
