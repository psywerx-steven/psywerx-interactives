"use strict";

const PAGE_SIZE = 24;
const DRIVER_QUERY_PARAMETER = "driver";

const searchInput = document.querySelector("#driver-search");
const familyFilter = document.querySelector("#family-filter");
const clearFiltersButton = document.querySelector("#clear-filters");
const layerCheckboxes = [...document.querySelectorAll('input[name="layer"]')];
const layerOptions = [...document.querySelectorAll(".layer-option")];
const activeLayerSummary = document.querySelector("#active-layer-summary");
const totalDriverCount = document.querySelector("#total-driver-count");
const resultSummary = document.querySelector("#result-summary");
const driverList = document.querySelector("#driver-list");
const loadMoreButton = document.querySelector("#load-more");
const loadError = document.querySelector("#load-error");
const linkNotice = document.querySelector("#link-notice");
const driverDialog = document.querySelector("#driver-dialog");
const driverDetail = document.querySelector("#driver-detail");
const closeDetailButton = document.querySelector("#close-detail");
const previousDriverButton = document.querySelector("#previous-driver");
const nextDriverButton = document.querySelector("#next-driver");
const detailPosition = document.querySelector("#detail-position");
const copyLinkButton = document.querySelector("#copy-link");
const copyStatus = document.querySelector("#copy-status");

let drivers = [];
let driverById = new Map();
let filteredDrivers = [];
let visibleCount = PAGE_SIZE;
let currentDriverId = null;
let detailOpenedFromList = false;
let searchTimer;

layerCheckboxes.forEach((checkbox) => {
  checkbox.disabled = true;
});

function normalizeSearchText(value) {
  return String(value || "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase();
}

function searchableText(driver) {
  return normalizeSearchText(
    [
      driver.name,
      ...(driver.aliases || []),
      driver.family,
      driver.definition,
      driver.mechanism,
    ].join(" ")
  );
}

function selectedLayers() {
  return new Set(
    layerCheckboxes
      .filter((checkbox) => checkbox.checked)
      .map((checkbox) => checkbox.value)
  );
}

function hasValue(value) {
  if (Array.isArray(value)) {
    return value.length > 0;
  }
  return value !== null && value !== undefined && String(value).trim() !== "";
}

function element(tagName, className, text) {
  const node = document.createElement(tagName);
  if (className) {
    node.className = className;
  }
  if (text !== undefined) {
    node.textContent = text;
  }
  return node;
}

function setLayerIdentity(node, layer) {
  node.dataset.layer = layer;
}

function initializeLayerFilters() {
  const counts = new Map();
  drivers.forEach((driver) => {
    counts.set(driver.layer, (counts.get(driver.layer) || 0) + 1);
  });

  layerOptions.forEach((option) => {
    const layer = option.dataset.layer;
    const count = option.querySelector("[data-layer-count]");
    count.textContent = String(counts.get(layer) || 0);
  });
}

function updateFamilyChoices() {
  const layers = selectedLayers();
  const currentFamily = familyFilter.value;
  const families = new Set(
    drivers
      .filter((driver) => layers.size === 0 || layers.has(driver.layer))
      .map((driver) => driver.family)
      .filter(hasValue)
  );
  const sortedFamilies = [...families].sort((a, b) =>
    a.localeCompare(b, undefined, { sensitivity: "base" })
  );

  const fragment = document.createDocumentFragment();
  fragment.append(element("option", "", "All families"));
  fragment.firstChild.value = "";
  sortedFamilies.forEach((family) => {
    const option = element("option", "", family);
    option.value = family;
    fragment.append(option);
  });
  familyFilter.replaceChildren(fragment);
  familyFilter.value = families.has(currentFamily) ? currentFamily : "";
}

function updateFilterSummary() {
  const layers = selectedLayers();
  if (layers.size === 0) {
    activeLayerSummary.textContent = "All eight layers";
  } else if (layers.size === 1) {
    activeLayerSummary.textContent = [...layers][0];
  } else {
    activeLayerSummary.textContent = String(layers.size) + " layers selected";
  }

  const filtersActive =
    layers.size > 0 || Boolean(familyFilter.value) || Boolean(searchInput.value.trim());
  clearFiltersButton.disabled = !filtersActive;
}

function applyFilters(options) {
  const shouldResetLimit = !options || options.resetLimit !== false;
  if (shouldResetLimit) {
    visibleCount = PAGE_SIZE;
  }

  const layers = selectedLayers();
  const family = familyFilter.value;
  const query = normalizeSearchText(searchInput.value.trim());

  filteredDrivers = drivers.filter((driver) => {
    const matchesLayer = layers.size === 0 || layers.has(driver.layer);
    const matchesFamily = !family || driver.family === family;
    const matchesSearch = !query || driver._searchText.includes(query);
    return matchesLayer && matchesFamily && matchesSearch;
  });

  updateFilterSummary();
  renderResults();
}

function createDriverCard(driver) {
  const article = element("article", "driver-card");
  setLayerIdentity(article, driver.layer);

  const button = element("button", "driver-card__button");
  button.type = "button";
  button.dataset.driverId = driver.id;
  button.setAttribute("aria-label", "Open " + driver.name);

  const meta = element("div", "driver-card__meta");
  const layer = element("span", "layer-badge", driver.layer);
  setLayerIdentity(layer, driver.layer);
  meta.append(layer);
  if (hasValue(driver.evidenceStrength)) {
    meta.append(
      element(
        "span",
        "evidence-badge",
        driver.evidenceStrength + " evidence"
      )
    );
  }

  const heading = element("h3", "driver-card__title", driver.name);
  const family = element("p", "driver-card__family", driver.family);
  const definition = element("p", "driver-card__definition", driver.definition);
  const action = element("span", "driver-card__action", "View driver record");
  action.append(element("span", "", " →"));

  button.append(meta, heading, family, definition, action);
  article.append(button);
  return article;
}

function renderResults() {
  const total = filteredDrivers.length;
  const shownDrivers = filteredDrivers.slice(0, visibleCount);
  const fragment = document.createDocumentFragment();

  if (total === 0) {
    const emptyState = element("div", "empty-state");
    emptyState.append(
      element("h3", "", "No drivers match these filters"),
      element(
        "p",
        "",
        "Try a broader search, choose another family, or clear the active filters."
      )
    );
    fragment.append(emptyState);
  } else {
    shownDrivers.forEach((driver) => {
      fragment.append(createDriverCard(driver));
    });
  }

  driverList.replaceChildren(fragment);
  const noun = total === 1 ? "driver" : "drivers";
  if (total > shownDrivers.length) {
    resultSummary.textContent =
      total.toLocaleString() +
      " " +
      noun +
      " found · Showing " +
      shownDrivers.length.toLocaleString();
  } else {
    resultSummary.textContent = total.toLocaleString() + " " + noun + " found";
  }

  loadMoreButton.hidden = shownDrivers.length >= total;
}

function appendDetailField(list, label, value, options) {
  if (!hasValue(value)) {
    return false;
  }
  const wrapper = element(
    "div",
    "detail-field" + (options && options.wide ? " detail-field--wide" : "")
  );
  wrapper.append(element("dt", "", label));
  const description = element("dd");

  if (Array.isArray(value)) {
    const values = element("ul", "detail-value-list");
    value.forEach((item) => {
      values.append(element("li", "", item));
    });
    description.append(values);
  } else {
    description.textContent = value;
  }

  wrapper.append(description);
  list.append(wrapper);
  return true;
}

function createDetailSection(title, fields) {
  const section = element("section", "detail-section");
  const list = element("dl", "detail-grid");
  let populated = false;
  fields.forEach((field) => {
    populated =
      appendDetailField(list, field.label, field.value, {
        wide: field.wide,
      }) || populated;
  });
  if (!populated) {
    return null;
  }
  section.append(element("h3", "", title), list);
  return section;
}

function renderDriverDetail(driver) {
  const fragment = document.createDocumentFragment();
  const header = element("header", "driver-detail__header");
  const badges = element("div", "driver-detail__badges");
  const layer = element("span", "layer-badge", driver.layer);
  setLayerIdentity(layer, driver.layer);
  badges.append(layer, element("span", "driver-id", driver.id));
  const title = element("h2", "", driver.name);
  title.id = "detail-title";
  header.append(badges, title, element("p", "", driver.definition));
  fragment.append(header);

  const sections = [
    createDetailSection("Identity", [
      { label: "Canonical name", value: driver.name },
      { label: "Aliases", value: driver.aliases, wide: true },
      { label: "Layer", value: driver.layer },
      { label: "Family", value: driver.family },
      { label: "Driver ID", value: driver.id },
    ]),
    createDetailSection("Definition & representation", [
      { label: "Definition", value: driver.definition, wide: true },
      { label: "Data type", value: driver.dataType },
      { label: "Representation / scale", value: driver.representationScale, wide: true },
      { label: "Polarity / direction", value: driver.polarityDirection, wide: true },
    ]),
    createDetailSection("Causal logic", [
      { label: "Mechanism", value: driver.mechanism, wide: true },
      {
        label: "Likely upstream influences",
        value: driver.likelyUpstreamInfluences,
        wide: true,
      },
      {
        label: "Likely downstream influences",
        value: driver.likelyDownstreamInfluences,
        wide: true,
      },
      {
        label: "Moderators / boundary conditions",
        value: driver.moderatorsBoundaryConditions,
        wide: true,
      },
      {
        label: "Typical interaction candidates",
        value: driver.typicalInteractionCandidates,
        wide: true,
      },
    ]),
    createDetailSection("Dynamics", [
      { label: "Modifiability", value: driver.modifiability },
      { label: "Volatility", value: driver.volatility },
      { label: "Time scale of change", value: driver.timeScaleOfChange },
      { label: "Onset / causal lag", value: driver.onsetCausalLag },
      {
        label: "Persistence / recovery",
        value: driver.persistenceRecovery,
        wide: true,
      },
    ]),
    createDetailSection("Observation & measurement", [
      { label: "Indicators", value: driver.indicators, wide: true },
      {
        label: "Measurement / assessment methods",
        value: driver.measurementAssessmentMethods,
        wide: true,
      },
      { label: "Observability", value: driver.observability },
      {
        label: "Measurement caveats",
        value: driver.measurementCaveats,
        wide: true,
      },
    ]),
    createDetailSection("Evidence & interpretation", [
      { label: "Evidence strength", value: driver.evidenceStrength },
      { label: "Evidence notes", value: driver.evidenceNotes, wide: true },
      {
        label: "Common misinterpretations",
        value: driver.commonMisinterpretations,
        wide: true,
      },
      { label: "Key sources", value: driver.keySources, wide: true },
    ]),
    createDetailSection("Provenance", [
      {
        label: "Source workbook",
        value: driver.source && driver.source.workbook,
        wide: true,
      },
      {
        label: "Source worksheet",
        value: driver.source && driver.source.sheet,
      },
    ]),
  ];

  sections.filter(Boolean).forEach((section) => fragment.append(section));
  driverDetail.replaceChildren(fragment);
}

function driverUrl(driverId) {
  const url = new URL(window.location.href);
  url.searchParams.set(DRIVER_QUERY_PARAMETER, driverId);
  return url;
}

function updateDetailNavigation() {
  const index = filteredDrivers.findIndex(
    (driver) => driver.id === currentDriverId
  );
  const hasPosition = index !== -1;
  previousDriverButton.disabled = !hasPosition || index === 0;
  nextDriverButton.disabled =
    !hasPosition || index === filteredDrivers.length - 1;
  detailPosition.textContent = hasPosition
    ? String(index + 1) + " of " + filteredDrivers.length
    : "Linked driver";
}

function showDialog() {
  if (driverDialog.open) {
    return;
  }
  if (typeof driverDialog.showModal === "function") {
    driverDialog.showModal();
  } else {
    driverDialog.setAttribute("open", "");
  }
}

function hideDialog() {
  if (!driverDialog.open) {
    return;
  }
  if (typeof driverDialog.close === "function") {
    driverDialog.close();
  } else {
    driverDialog.removeAttribute("open");
  }
}

function openDriver(driverId, urlAction) {
  const driver = driverById.get(driverId);
  if (!driver) {
    return false;
  }
  currentDriverId = driverId;
  renderDriverDetail(driver);
  updateDetailNavigation();
  copyLinkButton.textContent = "Copy driver link";
  copyStatus.textContent = "";
  showDialog();

  if (urlAction === "push") {
    history.pushState(
      { driverId: driverId, fromExplorer: true },
      "",
      driverUrl(driverId)
    );
    detailOpenedFromList = true;
  } else if (urlAction === "replace") {
    history.replaceState(
      { driverId: driverId, fromExplorer: detailOpenedFromList },
      "",
      driverUrl(driverId)
    );
  }
  return true;
}

function urlWithoutDriver() {
  const url = new URL(window.location.href);
  url.searchParams.delete(DRIVER_QUERY_PARAMETER);
  return url;
}

function closeDriverDetail() {
  if (detailOpenedFromList && new URL(window.location.href).searchParams.has(DRIVER_QUERY_PARAMETER)) {
    detailOpenedFromList = false;
    history.back();
    return;
  }
  history.replaceState({}, "", urlWithoutDriver());
  currentDriverId = null;
  hideDialog();
}

function moveWithinResults(offset) {
  const index = filteredDrivers.findIndex(
    (driver) => driver.id === currentDriverId
  );
  const destination = filteredDrivers[index + offset];
  if (destination) {
    openDriver(destination.id, "replace");
    driverDetail.scrollTop = 0;
  }
}

async function copyCurrentLink() {
  const url = driverUrl(currentDriverId).toString();
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(url);
    } else {
      const temporaryInput = element("textarea", "clipboard-fallback");
      temporaryInput.value = url;
      temporaryInput.setAttribute("readonly", "");
      document.body.append(temporaryInput);
      temporaryInput.select();
      document.execCommand("copy");
      temporaryInput.remove();
    }
    copyLinkButton.textContent = "Link copied";
    copyStatus.textContent = "Driver link copied to clipboard.";
  } catch (error) {
    console.error("Unable to copy driver link:", error);
    copyLinkButton.textContent = "Copy failed";
    copyStatus.textContent = "The driver link could not be copied.";
  }
}

function openDriverFromUrl() {
  const driverId = new URL(window.location.href).searchParams.get(
    DRIVER_QUERY_PARAMETER
  );
  if (!driverId) {
    return;
  }
  if (!openDriver(driverId, null)) {
    linkNotice.textContent =
      "The linked driver " + driverId + " was not found in this taxonomy.";
    linkNotice.hidden = false;
  }
}

function enableExplorer() {
  searchInput.disabled = false;
  familyFilter.disabled = false;
  layerCheckboxes.forEach((checkbox) => {
    checkbox.disabled = false;
  });
}

async function loadDrivers() {
  try {
    const response = await fetch("../data/drivers.json");
    if (!response.ok) {
      throw new Error(
        "Driver data request failed with status " + response.status + "."
      );
    }

    const data = await response.json();
    if (!Array.isArray(data)) {
      throw new Error("Driver data is not an array.");
    }

    drivers = data.map((driver) =>
      Object.assign({}, driver, { _searchText: searchableText(driver) })
    );
    driverById = new Map(drivers.map((driver) => [driver.id, driver]));

    totalDriverCount.textContent = drivers.length.toLocaleString();
    initializeLayerFilters();
    updateFamilyChoices();
    enableExplorer();
    applyFilters();
    openDriverFromUrl();
  } catch (error) {
    console.error("Unable to load driver taxonomy:", error);
    resultSummary.textContent = "Driver taxonomy unavailable";
    driverList.replaceChildren();
    loadError.hidden = false;
  }
}

searchInput.addEventListener("input", () => {
  window.clearTimeout(searchTimer);
  searchTimer = window.setTimeout(() => applyFilters(), 80);
});

familyFilter.addEventListener("change", () => applyFilters());

layerCheckboxes.forEach((checkbox) => {
  checkbox.addEventListener("change", () => {
    updateFamilyChoices();
    applyFilters();
  });
});

clearFiltersButton.addEventListener("click", () => {
  searchInput.value = "";
  familyFilter.value = "";
  layerCheckboxes.forEach((checkbox) => {
    checkbox.checked = false;
  });
  updateFamilyChoices();
  applyFilters();
  searchInput.focus();
});

driverList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-driver-id]");
  if (button) {
    openDriver(button.dataset.driverId, "push");
  }
});

loadMoreButton.addEventListener("click", () => {
  visibleCount += PAGE_SIZE;
  applyFilters({ resetLimit: false });
});

closeDetailButton.addEventListener("click", closeDriverDetail);
previousDriverButton.addEventListener("click", () => moveWithinResults(-1));
nextDriverButton.addEventListener("click", () => moveWithinResults(1));
copyLinkButton.addEventListener("click", copyCurrentLink);

driverDialog.addEventListener("cancel", (event) => {
  event.preventDefault();
  closeDriverDetail();
});

driverDialog.addEventListener("click", (event) => {
  if (event.target === driverDialog) {
    closeDriverDetail();
  }
});

window.addEventListener("popstate", (event) => {
  const driverId = new URL(window.location.href).searchParams.get(
    DRIVER_QUERY_PARAMETER
  );
  detailOpenedFromList = Boolean(event.state && event.state.fromExplorer);
  if (driverId && driverById.has(driverId)) {
    openDriver(driverId, null);
  } else {
    currentDriverId = null;
    hideDialog();
  }
});

loadDrivers();
