/**
 * Toggle listing form fields and labels by kind (crew_wanted, berth_wanted, training).
 */
function initListingFormKinds(formId) {
  const form = document.getElementById(formId);
  if (!form) return;

  const hiddenKind = form.querySelector("#id_kind");
  const kindRadios = form.querySelectorAll('input[name="listing_kind_card"]');
  const skipperBlocks = form.querySelectorAll("[data-listing-kind='skipper']");
  const passageBlocks = form.querySelectorAll("[data-listing-kind='passage']");
  const trainingBlocks = form.querySelectorAll("[data-listing-kind='training']");
  const labelEls = form.querySelectorAll("[data-label-crew][data-label-berth]");
  const mapSectionTitle = document.getElementById("listing-map-section-title");

  const i18n = {
    routeTitle: mapSectionTitle?.dataset.titleRoute || "Route on the map",
    placeTitle: mapSectionTitle?.dataset.titlePlace || "Place on the map",
  };

  function currentKind() {
    const card = form.querySelector('input[name="listing_kind_card"]:checked');
    if (card) return card.value;
    if (hiddenKind && hiddenKind.value) return hiddenKind.value;
    return "crew_wanted";
  }

  function setKind(value) {
    if (hiddenKind) hiddenKind.value = value;
    kindRadios.forEach((r) => {
      r.checked = r.value === value;
    });
    applyVisibility(value);
    form.dispatchEvent(new CustomEvent("listing-kind-change", { detail: { kind: value } }));
  }

  function applyVisibility(kind) {
    const isBerth = kind === "berth_wanted";
    const isTraining = kind === "training";
    const isSkipperListing = kind === "crew_wanted" || isTraining;
    skipperBlocks.forEach((el) => {
      el.classList.toggle("hidden", !isSkipperListing);
      el.querySelectorAll("input, select, textarea").forEach((input) => {
        input.disabled = !isSkipperListing;
      });
    });
    passageBlocks.forEach((el) => {
      el.classList.toggle("hidden", isTraining);
      el.querySelectorAll("input, select, textarea").forEach((input) => {
        if (isTraining) {
          input.disabled = true;
        } else {
          input.disabled = false;
        }
      });
    });
    trainingBlocks.forEach((el) => {
      el.classList.toggle("hidden", !isTraining);
    });
    labelEls.forEach((el) => {
      const crew = el.getAttribute("data-label-crew");
      const berth = el.getAttribute("data-label-berth");
      const training = el.getAttribute("data-label-training");
      if (isTraining && training) {
        el.textContent = training;
      } else {
        el.textContent = isBerth ? berth : crew;
      }
    });
    form.querySelectorAll("[data-label-berths-crew]").forEach((el) => {
      const crew = el.getAttribute("data-label-berths-crew");
      const training = el.getAttribute("data-label-berths-training");
      if (isTraining && training) {
        el.textContent = training;
      } else if (crew) {
        el.textContent = crew;
      }
    });
    form.querySelectorAll("[data-label-departure-crew]").forEach((el) => {
      const crew = el.getAttribute("data-label-departure-crew");
      const training = el.getAttribute("data-label-departure-training");
      if (isTraining && training) {
        el.textContent = training;
      } else if (crew) {
        el.textContent = crew;
      }
    });
    const steps = form.querySelectorAll(".js-listing-step-crew");
    steps.forEach((el) => {
      el.classList.toggle("hidden", !isSkipperListing);
    });
    if (mapSectionTitle) {
      mapSectionTitle.textContent = isTraining ? i18n.placeTitle : i18n.routeTitle;
    }
  }

  kindRadios.forEach((radio) => {
    radio.addEventListener("change", () => {
      if (radio.checked) setKind(radio.value);
    });
  });

  form.addEventListener("submit", () => {
    const card = form.querySelector('input[name="listing_kind_card"]:checked');
    if (card && hiddenKind) hiddenKind.value = card.value;
    passageBlocks.forEach((el) => {
      if (el.classList.contains("hidden")) {
        el.querySelectorAll("input, select, textarea").forEach((input) => {
          input.disabled = false;
        });
      }
    });
    skipperBlocks.forEach((el) => {
      if (el.classList.contains("hidden")) {
        el.querySelectorAll("input, select, textarea").forEach((input) => {
          input.disabled = false;
        });
      }
    });
  });

  if (hiddenKind && hiddenKind.tagName === "SELECT") {
    hiddenKind.classList.add("hidden");
    hiddenKind.setAttribute("aria-hidden", "true");
    hiddenKind.addEventListener("change", () => applyVisibility(hiddenKind.value));
  }

  setKind(currentKind());
}