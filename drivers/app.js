"use strict";

const PAGE_SIZE = 24;
const DRIVER_QUERY_PARAMETER = "driver";
const FACETS = [
  { field: "layer", label: "Layer" },
  { field: "family", label: "Family" },
  { field: "dataType", label: "Data type" },
  { field: "modifiability", label: "Modifiability" },
  { field: "volatility", label: "Volatility" },
  { field: "observability", label: "Observability" },
  { field: "evidenceStrength", label: "Evidence strength" },
];

const browseModeButton = document.querySelector("#browse-mode-button");
const searchModeButton = document.querySelector("#search-mode-button");
const browsePanel = document.querySelector("#browse-panel");
const searchPanel = document.querySelector("#search-panel");
const browseBreadcrumbs = document.querySelector("#browse-breadcrumbs");
const browseSummary = document.querySelector("#browse-summary");
const browseKicker = document.querySelector("#browse-kicker");
const browseHeading = document.querySelector("#browse-heading");
const browseDescription = document.querySelector("#browse-description");
const browseContent = document.querySelector("#browse-content");
const searchInput = document.querySelector("#driver-search");
const clearFiltersButton = document.querySelector("#clear-filters");
const facetFilters = document.querySelector("#facet-filters");
const activeFilters = document.querySelector("#active-filters");
const totalDriverCount = document.querySelector("#total-driver-count");
const totalLayerCount = document.querySelector("#total-layer-count");
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
let hierarchy = new Map();
let filteredDrivers = [];
let detailDrivers = [];
let visibleCount = PAGE_SIZE;
let currentDriverId = null;
let detailOpenedFromExplorer = false;
let activeMode = "browse";
let selectedBrowseLayer = null;
let selectedBrowseFamily = null;
let searchTimer;

const facetSelections = Object.fromEntries(
  FACETS.map(({ field }) => [field, new Set()])
);

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

function sortText(values) {
  return values.sort((a, b) =>
    a.localeCompare(b, undefined, { sensitivity: "base", numeric: true })
  );
}

function uniqueValues(field, sourceDrivers = drivers) {
  return sortText(
    [...new Set(sourceDrivers.map((driver) => driver[field]).filter(hasValue))]
  );
}

function buildHierarchy() {
  hierarchy = new Map();
  drivers.forEach((driver) => {
    if (!hierarchy.has(driver.layer)) {
      hierarchy.set(driver.layer, new Map());
    }
    const families = hierarchy.get(driver.layer);
    if (!families.has(driver.family)) {
      families.set(driver.family, []);
    }
    families.get(driver.family).push(driver);
  });
}

function setMode(mode, options = {}) {
  activeMode = mode === "search" ? "search" : "browse";
  const browsing = activeMode === "browse";
  browsePanel.hidden = !browsing;
  searchPanel.hidden = browsing;
  browseModeButton.setAttribute("aria-pressed", String(browsing));
  searchModeButton.setAttribute("aria-pressed", String(!browsing));
  if (options.focus) {
    (browsing ? browseHeading : searchInput).focus();
  }
}

function hierarchyButton(title, meta, type, value, layer) {
  const article = element("article", "hierarchy-card");
  if (layer) {
    setLayerIdentity(article, layer);
  }
  const button = element("button", "hierarchy-card__button");
  button.type = "button";
  button.dataset[type] = value;
  const titleNode = element("span", "hierarchy-card__title", title);
  const metaNode = element("span", "hierarchy-card__meta", meta);
  const action = element("span", "hierarchy-card__action", "Explore");
  action.setAttribute("aria-hidden", "true");
  action.append(" \u2192");
  button.append(titleNode, metaNode, action);
  article.append(button);
  return article;
}

function breadcrumbButton(label, level) {
  const button = element("button", "breadcrumbs__button", label);
  button.type = "button";
  button.dataset.browseLevel = level;
  return button;
}

function renderBrowse() {
  const fragment = document.createDocumentFragment();
  const crumbs = document.createDocumentFragment();
  crumbs.append(breadcrumbButton("All layers", "root"));

  if (!selectedBrowseLayer) {
    browseKicker.textContent = "Layer \u2192 Family \u2192 Driver";
    browseHeading.textContent = "Choose a layer";
    browseDescription.textContent = "Start with one of the eight interacting layers.";
    browseSummary.textContent =
      hierarchy.size.toLocaleString() + " layers \u00b7 " +
      drivers.length.toLocaleString() + " drivers";
    browseContent.className = "hierarchy-grid";

    hierarchy.forEach((families, layer) => {
      const count = [...families.values()].reduce(
        (total, familyDrivers) => total + familyDrivers.length,
        0
      );
      fragment.append(
        hierarchyButton(
          layer,
          families.size.toLocaleString() + " families \u00b7 " +
            count.toLocaleString() + " drivers",
          "browseLayer",
          layer,
          layer
        )
      );
    });
  } else if (!selectedBrowseFamily) {
    const families = hierarchy.get(selectedBrowseLayer);
    crumbs.append(" / ", breadcrumbButton(selectedBrowseLayer, "layer"));
    browseKicker.textContent = selectedBrowseLayer + " layer";
    browseHeading.textContent = "Choose a family";
    browseDescription.textContent =
      "Families group closely related drivers within this layer.";
    const layerCount = [...families.values()].reduce(
      (total, familyDrivers) => total + familyDrivers.length,
      0
    );
    browseSummary.textContent =
      families.size.toLocaleString() + " families \u00b7 " +
      layerCount.toLocaleString() + " drivers";
    browseContent.className = "hierarchy-grid";

    sortText([...families.keys()]).forEach((family) => {
      const familyDrivers = families.get(family);
      fragment.append(
        hierarchyButton(
          family,
          familyDrivers.length.toLocaleString() +
            (familyDrivers.length === 1 ? " driver" : " drivers"),
          "browseFamily",
          family,
          selectedBrowseLayer
        )
      );
    });
  } else {
    const familyDrivers = hierarchy
      .get(selectedBrowseLayer)
      .get(selectedBrowseFamily);
    crumbs.append(
      " / ",
      breadcrumbButton(selectedBrowseLayer, "layer"),
      " / ",
      element("span", "breadcrumbs__current", selectedBrowseFamily)
    );
    browseKicker.textContent = selectedBrowseLayer + " layer";
    browseHeading.textContent = selectedBrowseFamily;
    browseDescription.textContent =
      "Select a driver to view its complete taxonomy record.";
    browseSummary.textContent =
      familyDrivers.length.toLocaleString() +
      (familyDrivers.length === 1 ? " driver" : " drivers");
    browseContent.className = "driver-list";
    familyDrivers.forEach((driver) => fragment.append(createDriverCard(driver)));
  }

  browseBreadcrumbs.replaceChildren(crumbs);
  browseContent.replaceChildren(fragment);
}

function facetSourceDrivers(field) {
  if (field !== "family" || facetSelections.layer.size === 0) {
    return drivers;
  }
  return drivers.filter((driver) => facetSelections.layer.has(driver.layer));
}

function renderFacet(field) {
  const config = FACETS.find((facet) => facet.field === field);
  const old = facetFilters.querySelector('[data-facet="' + field + '"]');
  const wasOpen = old ? old.open : field === "layer" || field === "family";
  const details = element("details", "facet");
  details.dataset.facet = field;
  details.open = wasOpen;

  const summary = element("summary", "facet__summary");
  summary.append(
    element("span", "", config.label),
    element("span", "facet__selected-count")
  );
  details.append(summary);

  const values = uniqueValues(field, facetSourceDrivers(field));
  const counts = new Map();
  facetSourceDrivers(field).forEach((driver) => {
    if (hasValue(driver[field])) {
      counts.set(driver[field], (counts.get(driver[field]) || 0) + 1);
    }
  });

  const choices = element("div", "facet__choices");
  values.forEach((value, index) => {
    const label = element("label", "facet-option");
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = value;
    checkbox.dataset.facetField = field;
    checkbox.id = "facet-" + field + "-" + index;
    checkbox.checked = facetSelections[field].has(value);
    label.htmlFor = checkbox.id;
    label.append(
      checkbox,
      element("span", "facet-option__label", value),
      element("span", "facet-option__count", String(counts.get(value) || 0))
    );
    choices.append(label);
  });
  details.append(choices);

  if (old) {
    old.replaceWith(details);
  } else {
    facetFilters.append(details);
  }
}

function renderFacets() {
  facetFilters.replaceChildren();
  FACETS.forEach(({ field }) => renderFacet(field));
  updateFacetSelectedCounts();
}

function updateFacetSelectedCounts() {
  FACETS.forEach(({ field }) => {
    const countNode = facetFilters.querySelector(
      '[data-facet="' + field + '"] .facet__selected-count'
    );
    const count = facetSelections[field].size;
    if (countNode) {
      countNode.textContent = count ? String(count) + " selected" : "Any";
    }
  });
}

function syncAvailableFamilies() {
  const available = new Set(uniqueValues("family", facetSourceDrivers("family")));
  [...facetSelections.family].forEach((family) => {
    if (!available.has(family)) {
      facetSelections.family.delete(family);
    }
  });
  renderFacet("family");
}

function matchesFacet(driver, field) {
  const selected = facetSelections[field];
  return selected.size === 0 || selected.has(driver[field]);
}

function applyFilters(options = {}) {
  if (options.resetLimit !== false) {
    visibleCount = PAGE_SIZE;
  }
  const query = normalizeSearchText(searchInput.value.trim());
  filteredDrivers = drivers.filter(
    (driver) =>
      (!query || driver._searchText.includes(query)) &&
      FACETS.every(({ field }) => matchesFacet(driver, field))
  );
  updateFacetSelectedCounts();
  renderActiveFilters();
  renderResults();
}

function renderActiveFilters() {
  const fragment = document.createDocumentFragment();
  const query = searchInput.value.trim();

  if (query) {
    fragment.append(filterChip("Search", query, "search", query));
  }
  FACETS.forEach(({ field, label }) => {
    facetSelections[field].forEach((value) => {
      fragment.append(filterChip(label, value, field, value));
    });
  });

  activeFilters.replaceChildren(fragment);
  const filtersActive =
    Boolean(query) || FACETS.some(({ field }) => facetSelections[field].size > 0);
  clearFiltersButton.disabled = !filtersActive;
}

function filterChip(label, value, field, rawValue) {
  const button = element(
    "button",
    "filter-chip",
    label + ": " + value + " "
  );
  button.type = "button";
  button.dataset.clearFacet = field;
  button.dataset.clearValue = rawValue;
  button.setAttribute("aria-label", "Remove " + label + " filter: " + value);
  const mark = element("span", "", "\u00d7");
  mark.setAttribute("aria-hidden", "true");
  button.append(mark);
  return button;
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
  meta.append(layer, element("span", "family-badge", driver.family));

  const heading = element("h3", "driver-card__title", driver.name);
  const definition = element("p", "driver-card__definition", driver.definition);
  const action = element("span", "driver-card__action", "View driver record");
  action.append(element("span", "", " \u2192"));
  button.append(meta, heading, definition, action);
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
        "Try a broader search or remove one or more active filters."
      )
    );
    fragment.append(emptyState);
  } else {
    shownDrivers.forEach((driver) => fragment.append(createDriverCard(driver)));
  }
  driverList.replaceChildren(fragment);

  const noun = total === 1 ? "driver" : "drivers";
  resultSummary.textContent =
    total > shownDrivers.length
      ? total.toLocaleString() + " " + noun + " found \u00b7 Showing " +
        shownDrivers.length.toLocaleString()
      : total.toLocaleString() + " " + noun + " found";
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
    value.forEach((item) => values.append(element("li", "", item)));
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
      appendDetailField(list, field.label, field.value, { wide: field.wide }) ||
      populated;
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
      { label: "Likely upstream influences", value: driver.likelyUpstreamInfluences, wide: true },
      { label: "Likely downstream influences", value: driver.likelyDownstreamInfluences, wide: true },
      { label: "Moderators / boundary conditions", value: driver.moderatorsBoundaryConditions, wide: true },
      { label: "Typical interaction candidates", value: driver.typicalInteractionCandidates, wide: true },
    ]),
    createDetailSection("Dynamics", [
      { label: "Modifiability", value: driver.modifiability },
      { label: "Volatility", value: driver.volatility },
      { label: "Time scale of change", value: driver.timeScaleOfChange },
      { label: "Onset / causal lag", value: driver.onsetCausalLag },
      { label: "Persistence / recovery", value: driver.persistenceRecovery, wide: true },
    ]),
    createDetailSection("Observation & measurement", [
      { label: "Indicators", value: driver.indicators, wide: true },
      { label: "Measurement / assessment methods", value: driver.measurementAssessmentMethods, wide: true },
      { label: "Observability", value: driver.observability },
      { label: "Measurement caveats", value: driver.measurementCaveats, wide: true },
    ]),
    createDetailSection("Evidence & interpretation", [
      { label: "Evidence strength", value: driver.evidenceStrength },
      { label: "Evidence notes", value: driver.evidenceNotes, wide: true },
      { label: "Common misinterpretations", value: driver.commonMisinterpretations, wide: true },
      { label: "Key sources", value: driver.keySources, wide: true },
    ]),
    createDetailSection("Provenance", [
      { label: "Source workbook", value: driver.source && driver.source.workbook, wide: true },
      { label: "Source worksheet", value: driver.source && driver.source.sheet },
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
  const index = detailDrivers.findIndex((driver) => driver.id === currentDriverId);
  const hasPosition = index !== -1;
  previousDriverButton.disabled = !hasPosition || index === 0;
  nextDriverButton.disabled = !hasPosition || index === detailDrivers.length - 1;
  detailPosition.textContent = hasPosition
    ? String(index + 1) + " of " + detailDrivers.length
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

function openDriver(driverId, urlAction, contextDrivers) {
  const driver = driverById.get(driverId);
  if (!driver) {
    return false;
  }
  if (contextDrivers) {
    detailDrivers = contextDrivers;
  } else if (detailDrivers.length === 0) {
    detailDrivers = drivers;
  }
  currentDriverId = driverId;
  renderDriverDetail(driver);
  updateDetailNavigation();
  copyLinkButton.textContent = "Copy driver link";
  copyStatus.textContent = "";
  showDialog();

  if (urlAction === "push") {
    history.pushState(
      { driverId, fromExplorer: true },
      "",
      driverUrl(driverId)
    );
    detailOpenedFromExplorer = true;
  } else if (urlAction === "replace") {
    history.replaceState(
      { driverId, fromExplorer: detailOpenedFromExplorer },
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
  if (
    detailOpenedFromExplorer &&
    new URL(window.location.href).searchParams.has(DRIVER_QUERY_PARAMETER)
  ) {
    detailOpenedFromExplorer = false;
    history.back();
    return;
  }
  history.replaceState({}, "", urlWithoutDriver());
  currentDriverId = null;
  hideDialog();
}

function moveWithinResults(offset) {
  const index = detailDrivers.findIndex((driver) => driver.id === currentDriverId);
  const destination = detailDrivers[index + offset];
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
  detailDrivers = drivers;
  if (!openDriver(driverId, null)) {
    linkNotice.textContent =
      "The linked driver " + driverId + " was not found in this taxonomy.";
    linkNotice.hidden = false;
  }
}

function clearAllFilters() {
  searchInput.value = "";
  FACETS.forEach(({ field }) => facetSelections[field].clear());
  renderFacets();
  applyFilters();
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
    buildHierarchy();
    totalDriverCount.textContent = drivers.length.toLocaleString();
    totalLayerCount.textContent = hierarchy.size.toLocaleString();
    searchInput.disabled = false;
    renderBrowse();
    renderFacets();
    applyFilters();
    openDriverFromUrl();
  } catch (error) {
    console.error("Unable to load driver taxonomy:", error);
    browseSummary.textContent = "Driver taxonomy unavailable";
    resultSummary.textContent = "Driver taxonomy unavailable";
    browseContent.replaceChildren();
    driverList.replaceChildren();
    loadError.hidden = false;
  }
}

browseModeButton.addEventListener("click", () => setMode("browse", { focus: true }));
searchModeButton.addEventListener("click", () => setMode("search", { focus: true }));

browseContent.addEventListener("click", (event) => {
  const layerButton = event.target.closest("[data-browse-layer]");
  const familyButton = event.target.closest("[data-browse-family]");
  const driverButton = event.target.closest("[data-driver-id]");
  if (layerButton) {
    selectedBrowseLayer = layerButton.dataset.browseLayer;
    selectedBrowseFamily = null;
    renderBrowse();
    browseHeading.focus();
  } else if (familyButton) {
    selectedBrowseFamily = familyButton.dataset.browseFamily;
    renderBrowse();
    browseHeading.focus();
  } else if (driverButton) {
    const familyDrivers = hierarchy
      .get(selectedBrowseLayer)
      .get(selectedBrowseFamily);
    openDriver(driverButton.dataset.driverId, "push", familyDrivers);
  }
});

browseBreadcrumbs.addEventListener("click", (event) => {
  const button = event.target.closest("[data-browse-level]");
  if (!button) {
    return;
  }
  if (button.dataset.browseLevel === "root") {
    selectedBrowseLayer = null;
    selectedBrowseFamily = null;
  } else {
    selectedBrowseFamily = null;
  }
  renderBrowse();
  browseHeading.focus();
});

searchInput.addEventListener("input", () => {
  window.clearTimeout(searchTimer);
  searchTimer = window.setTimeout(() => applyFilters(), 80);
});

facetFilters.addEventListener("change", (event) => {
  const checkbox = event.target.closest("[data-facet-field]");
  if (!checkbox) {
    return;
  }
  const selected = facetSelections[checkbox.dataset.facetField];
  if (checkbox.checked) {
    selected.add(checkbox.value);
  } else {
    selected.delete(checkbox.value);
  }
  if (checkbox.dataset.facetField === "layer") {
    syncAvailableFamilies();
  }
  applyFilters();
});

activeFilters.addEventListener("click", (event) => {
  const button = event.target.closest("[data-clear-facet]");
  if (!button) {
    return;
  }
  if (button.dataset.clearFacet === "search") {
    searchInput.value = "";
  } else {
    facetSelections[button.dataset.clearFacet].delete(button.dataset.clearValue);
    const checkbox = [...facetFilters.querySelectorAll("[data-facet-field]")].find(
      (input) =>
        input.dataset.facetField === button.dataset.clearFacet &&
        input.value === button.dataset.clearValue
    );
    if (checkbox) {
      checkbox.checked = false;
    }
    if (button.dataset.clearFacet === "layer") {
      syncAvailableFamilies();
    }
  }
  applyFilters();
});

clearFiltersButton.addEventListener("click", () => {
  clearAllFilters();
  searchInput.focus();
});

driverList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-driver-id]");
  if (button) {
    openDriver(button.dataset.driverId, "push", filteredDrivers);
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
  detailOpenedFromExplorer = Boolean(event.state && event.state.fromExplorer);
  if (driverId && driverById.has(driverId)) {
    openDriver(driverId, null);
  } else {
    currentDriverId = null;
    hideDialog();
  }
});

loadDrivers();
