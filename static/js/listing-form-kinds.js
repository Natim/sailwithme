/**
 * Toggle listing form fields and labels by kind (crew_wanted vs berth_wanted).
 */
function initListingFormKinds(formId) {
  const form = document.getElementById(formId);
  if (!form) return;

  const hiddenKind = form.querySelector("#id_kind");
  const kindRadios = form.querySelectorAll('input[name="listing_kind_card"]');
  const skipperBlocks = form.querySelectorAll("[data-listing-kind='skipper']");
  const labelEls = form.querySelectorAll("[data-label-crew][data-label-berth]");

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
  }

  function applyVisibility(kind) {
    const isSkipperListing = kind === "crew_wanted";
    skipperBlocks.forEach((el) => {
      el.classList.toggle("hidden", !isSkipperListing);
      el.querySelectorAll("input, select, textarea").forEach((input) => {
        input.disabled = !isSkipperListing;
      });
    });
    labelEls.forEach((el) => {
      const crew = el.getAttribute("data-label-crew");
      const berth = el.getAttribute("data-label-berth");
      el.textContent = isSkipperListing ? crew : berth;
    });
    const steps = form.querySelectorAll(".js-listing-step-crew");
    steps.forEach((el) => {
      el.classList.toggle("hidden", !isSkipperListing);
    });
  }

  kindRadios.forEach((radio) => {
    radio.addEventListener("change", () => {
      if (radio.checked) setKind(radio.value);
    });
  });

  form.addEventListener("submit", () => {
    const card = form.querySelector('input[name="listing_kind_card"]:checked');
    if (card && hiddenKind) hiddenKind.value = card.value;
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