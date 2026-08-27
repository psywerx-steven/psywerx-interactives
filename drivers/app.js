"use strict";

const PAGE_SIZE = 24;
const DRIVER_QUERY_PARAMETER = "driver";
const FAMILY_QUERY_PARAMETER = "family";
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
const totalFamilyCount = document.querySelector("#total-family-count");
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
let families = [];
let familyById = new Map();
let familyByIdentity = new Map();
let driversByFamilyId = new Map();
let relationships = [];
let incomingRelationshipsByDriverId = new Map();
let outgoingRelationshipsByDriverId = new Map();
let hierarchy = new Map();
let filteredDrivers = [];
let detailDrivers = [];
let visibleCount = PAGE_SIZE;
let currentDriverId = null;
let detailOpenedFromExplorer = false;
let activeMode = "browse";
let selectedBrowseLayer = null;
let selectedBrowseFamilyId = null;
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

function familyIdentityKey(layer, familyName) {
  return JSON.stringify([layer, familyName]);
}

function assertString(record, field, label, errors) {
  if (typeof record[field] !== "string" || record[field].trim() === "") {
    errors.push(label + " has no valid " + field + ".");
  }
}

function validateTaxonomyData(driverData, familyEnvelope, relationshipEnvelope) {
  const errors = [];
  if (!Array.isArray(driverData)) {
    throw new Error("Driver data is not an array.");
  }
  if (
    !familyEnvelope ||
    typeof familyEnvelope !== "object" ||
    !Array.isArray(familyEnvelope.families)
  ) {
    throw new Error("Family data does not contain a families array.");
  }
  if (familyEnvelope.schemaVersion !== "1.0") {
    throw new Error("Family data does not use Family Schema v1.0.");
  }
  if (
    !relationshipEnvelope ||
    typeof relationshipEnvelope !== "object" ||
    !Array.isArray(relationshipEnvelope.relationships)
  ) {
    throw new Error("Relationship data does not contain a relationships array.");
  }
  if (relationshipEnvelope.schemaVersion !== "1.0") {
    throw new Error("Relationship data does not use Relationship Schema v1.0.");
  }

  const candidateDriverById = new Map();
  driverData.forEach((driver, index) => {
    const label = "Driver record " + String(index + 1);
    ["id", "name", "layer", "family"].forEach((field) =>
      assertString(driver, field, label, errors)
    );
    if (candidateDriverById.has(driver.id)) {
      errors.push("Duplicate Driver ID: " + driver.id + ".");
    }
    candidateDriverById.set(driver.id, driver);
  });

  const candidateFamilyById = new Map();
  const candidateFamilyByIdentity = new Map();
  const candidateFamilyNames = new Set();
  familyEnvelope.families.forEach((family, index) => {
    const label = "Family record " + String(index + 1);
    ["id", "name", "layer", "definition", "includes", "exclusions"].forEach(
      (field) => assertString(family, field, label, errors)
    );
    if (!Number.isInteger(family.driverCount) || family.driverCount < 1) {
      errors.push(label + " has no valid driverCount.");
    }
    if (
      !Array.isArray(family.representativeDrivers) ||
      !Array.isArray(family.representativeDriverIds)
    ) {
      errors.push(label + " has invalid representative Driver arrays.");
    } else if (
      family.representativeDrivers.length !== family.representativeDriverIds.length
    ) {
      errors.push(
        "Family " + family.id + " has misaligned representative Driver arrays."
      );
    }
    if (candidateFamilyById.has(family.id)) {
      errors.push("Duplicate Family ID: " + family.id + ".");
    }
    candidateFamilyById.set(family.id, family);
    if (candidateFamilyNames.has(family.name)) {
      errors.push("Duplicate Family name: " + family.name + ".");
    }
    candidateFamilyNames.add(family.name);
    const identity = familyIdentityKey(family.layer, family.name);
    if (candidateFamilyByIdentity.has(identity)) {
      errors.push(
        "Duplicate Family identity: " + family.layer + " / " + family.name + "."
      );
    }
    candidateFamilyByIdentity.set(identity, family);
  });

  const actualCounts = new Map();
  driverData.forEach((driver) => {
    const family = candidateFamilyByIdentity.get(
      familyIdentityKey(driver.layer, driver.family)
    );
    if (!family) {
      errors.push(
        "Driver " + driver.id + " does not resolve to an exact Layer + Family."
      );
      return;
    }
    actualCounts.set(family.id, (actualCounts.get(family.id) || 0) + 1);
  });

  familyEnvelope.families.forEach((family) => {
    const actualCount = actualCounts.get(family.id) || 0;
    if (actualCount !== family.driverCount) {
      errors.push(
        "Family " + family.id + " declares " + family.driverCount +
          " Drivers but resolves to " + actualCount + "."
      );
    }
    if (
      Array.isArray(family.representativeDrivers) &&
      Array.isArray(family.representativeDriverIds)
    ) {
      family.representativeDriverIds.forEach((driverId, position) => {
        const driver = candidateDriverById.get(driverId);
        if (
          !driver ||
          driver.layer !== family.layer ||
          driver.family !== family.name ||
          driver.name !== family.representativeDrivers[position]
        ) {
          errors.push(
            "Family " + family.id + " has an invalid representative Driver link at position " +
              String(position + 1) + "."
          );
        }
      });
    }
  });

  const candidateRelationshipById = new Map();
  relationshipEnvelope.relationships.forEach((relationship, index) => {
    const label = "Relationship record " + String(index + 1);
    [
      "id",
      "sourceDriverId",
      "sourceDriverName",
      "targetDriverId",
      "targetDriverName",
      "relationshipType",
      "expectedDirection",
      "functionalForm",
      "moderatorsConditions",
      "timeLag",
      "evidenceStrength",
      "evidenceNotes",
    ].forEach((field) => assertString(relationship, field, label, errors));

    if (candidateRelationshipById.has(relationship.id)) {
      errors.push("Duplicate Relationship ID: " + relationship.id + ".");
    }
    candidateRelationshipById.set(relationship.id, relationship);

    const sourceDriver = candidateDriverById.get(relationship.sourceDriverId);
    const targetDriver = candidateDriverById.get(relationship.targetDriverId);
    if (!sourceDriver) {
      errors.push(
        "Relationship " + relationship.id + " has an unknown source Driver ID."
      );
    } else if (sourceDriver.name !== relationship.sourceDriverName) {
      errors.push(
        "Relationship " + relationship.id + " has a source Driver name mismatch."
      );
    }
    if (!targetDriver) {
      errors.push(
        "Relationship " + relationship.id + " has an unknown target Driver ID."
      );
    } else if (targetDriver.name !== relationship.targetDriverName) {
      errors.push(
        "Relationship " + relationship.id + " has a target Driver name mismatch."
      );
    }
    if (
      hasValue(relationship.sourceDriverId) &&
      relationship.sourceDriverId === relationship.targetDriverId
    ) {
      errors.push("Relationship " + relationship.id + " is a self-relationship.");
    }
    if (
      !Array.isArray(relationship.evidenceIds) ||
      relationship.evidenceIds.length === 0 ||
      relationship.evidenceIds.some(
        (evidenceId) =>
          typeof evidenceId !== "string" || evidenceId.trim() === ""
      )
    ) {
      errors.push(label + " has invalid evidenceIds.");
    }
  });

  if (errors.length > 0) {
    throw new Error(
      "Driver, Family, and Relationship data validation failed: " +
        errors.slice(0, 5).join(" ") +
        (errors.length > 5 ? " " + String(errors.length - 5) + " more errors." : "")
    );
  }
}

function buildRelationshipIndexes() {
  incomingRelationshipsByDriverId = new Map(
    drivers.map((driver) => [driver.id, []])
  );
  outgoingRelationshipsByDriverId = new Map(
    drivers.map((driver) => [driver.id, []])
  );

  relationships.forEach((relationship) => {
    incomingRelationshipsByDriverId
      .get(relationship.targetDriverId)
      .push(relationship);
    outgoingRelationshipsByDriverId
      .get(relationship.sourceDriverId)
      .push(relationship);
  });

  const sortRelationshipIndex = (index, relatedDriverNameField) => {
    index.forEach((driverRelationships) =>
      driverRelationships.sort(
        (first, second) =>
          first[relatedDriverNameField].localeCompare(
            second[relatedDriverNameField],
            undefined,
            { sensitivity: "base", numeric: true }
          ) || first.id.localeCompare(second.id, undefined, { numeric: true })
      )
    );
  };
  sortRelationshipIndex(incomingRelationshipsByDriverId, "sourceDriverName");
  sortRelationshipIndex(outgoingRelationshipsByDriverId, "targetDriverName");
}

function buildHierarchy() {
  hierarchy = new Map();
  driversByFamilyId = new Map(families.map((family) => [family.id, []]));

  families.forEach((family) => {
    if (!hierarchy.has(family.layer)) {
      hierarchy.set(family.layer, []);
    }
    hierarchy.get(family.layer).push(family);
  });

  drivers.forEach((driver) => {
    const family = familyByIdentity.get(
      familyIdentityKey(driver.layer, driver.family)
    );
    driversByFamilyId.get(family.id).push(driver);
  });

  hierarchy.forEach((layerFamilies) =>
    layerFamilies.sort((a, b) =>
      a.name.localeCompare(b.name, undefined, { sensitivity: "base", numeric: true })
    )
  );
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

function driverCountLabel(count) {
  return count.toLocaleString() + (count === 1 ? " driver" : " drivers");
}

function createFamilyCard(family) {
  const article = element("article", "hierarchy-card family-card");
  setLayerIdentity(article, family.layer);
  const button = element("button", "hierarchy-card__button family-card__button");
  button.type = "button";
  button.dataset.browseFamily = family.id;
  button.setAttribute(
    "aria-label",
    "Explore family " + family.name + ", " + driverCountLabel(family.driverCount)
  );
  const title = element("span", "hierarchy-card__title", family.name);
  const definition = element(
    "span",
    "family-card__definition",
    family.definition
  );
  const meta = element(
    "span",
    "hierarchy-card__meta",
    driverCountLabel(family.driverCount)
  );
  const action = element("span", "hierarchy-card__action", "Explore family");
  action.setAttribute("aria-hidden", "true");
  action.append(" \u2192");
  button.append(title, definition, meta, action);
  article.append(button);
  return article;
}

function createFamilyTextSection(title, value, className) {
  if (!hasValue(value)) {
    return null;
  }
  const section = element("section", className || "family-overview__section");
  section.append(element("h5", "", title), element("p", "", value));
  return section;
}

function createFamilyOverview(family) {
  const article = element("article", "family-overview");
  setLayerIdentity(article, family.layer);

  const identity = element("header", "family-overview__identity");
  identity.append(element("p", "eyebrow", "Family record"));
  const badges = element("div", "family-overview__badges");
  const layer = element("span", "layer-badge", family.layer);
  setLayerIdentity(layer, family.layer);
  badges.append(
    layer,
    element("span", "driver-id", family.id),
    element("span", "family-badge", driverCountLabel(family.driverCount))
  );
  identity.append(badges, element("h4", "", family.name));
  article.append(identity);

  const definition = createFamilyTextSection("Definition", family.definition);
  if (definition) {
    article.append(definition);
  }

  if (hasValue(family.includes) || hasValue(family.exclusions)) {
    const scope = element("section", "family-overview__section");
    scope.append(element("h5", "", "Scope"));
    const scopeGrid = element("div", "family-scope");
    if (hasValue(family.includes)) {
      const inclusion = element("div", "family-scope__item");
      inclusion.append(
        element("h6", "", "Inclusion rule"),
        element("p", "", family.includes)
      );
      scopeGrid.append(inclusion);
    }
    if (hasValue(family.exclusions)) {
      const exclusion = element("div", "family-scope__item");
      exclusion.append(
        element("h6", "", "Exclusion / boundary rule"),
        element("p", "", family.exclusions)
      );
      scopeGrid.append(exclusion);
    }
    scope.append(scopeGrid);
    article.append(scope);
  }

  if (family.representativeDriverIds.length > 0) {
    const representatives = element("section", "family-overview__section");
    representatives.append(element("h5", "", "Representative drivers"));
    const links = element("div", "representative-drivers");
    family.representativeDriverIds.forEach((driverId, index) => {
      const button = element(
        "button",
        "representative-driver",
        family.representativeDrivers[index]
      );
      button.type = "button";
      button.dataset.driverId = driverId;
      button.setAttribute(
        "aria-label",
        "Open representative Driver: " + family.representativeDrivers[index]
      );
      const arrow = element("span", "", " \u2192");
      arrow.setAttribute("aria-hidden", "true");
      button.append(arrow);
      links.append(button);
    });
    representatives.append(links);
    article.append(representatives);
  }

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

    hierarchy.forEach((layerFamilies, layer) => {
      const count = layerFamilies.reduce(
        (total, family) => total + family.driverCount,
        0
      );
      fragment.append(
        hierarchyButton(
          layer,
          layerFamilies.length.toLocaleString() + " families \u00b7 " +
            count.toLocaleString() + " drivers",
          "browseLayer",
          layer,
          layer
        )
      );
    });
  } else if (!selectedBrowseFamilyId) {
    const layerFamilies = hierarchy.get(selectedBrowseLayer);
    crumbs.append(" / ", breadcrumbButton(selectedBrowseLayer, "layer"));
    browseKicker.textContent = selectedBrowseLayer + " layer";
    browseHeading.textContent = "Choose a family";
    browseDescription.textContent =
      "Families group closely related drivers within this layer.";
    const layerCount = layerFamilies.reduce(
      (total, family) => total + family.driverCount,
      0
    );
    browseSummary.textContent =
      layerFamilies.length.toLocaleString() + " families \u00b7 " +
      layerCount.toLocaleString() + " drivers";
    browseContent.className = "hierarchy-grid";

    layerFamilies.forEach((family) => fragment.append(createFamilyCard(family)));
  } else {
    const family = familyById.get(selectedBrowseFamilyId);
    const familyDrivers = driversByFamilyId.get(family.id);
    crumbs.append(
      " / ",
      breadcrumbButton(selectedBrowseLayer, "layer"),
      " / ",
      element("span", "breadcrumbs__current", family.name)
    );
    browseKicker.textContent = selectedBrowseLayer + " layer";
    browseHeading.textContent = family.name;
    browseDescription.textContent =
      "Review this Family record, then select a Driver for its complete taxonomy record.";
    browseSummary.textContent = family.id + " \u00b7 " + driverCountLabel(familyDrivers.length);
    browseContent.className = "family-view";
    fragment.append(createFamilyOverview(family));

    const driverSection = element("section", "family-drivers");
    driverSection.append(
      element("h4", "family-drivers__heading", "Drivers in this family")
    );
    const list = element("div", "driver-list");
    familyDrivers.forEach((driver) => list.append(createDriverCard(driver)));
    driverSection.append(list);
    fragment.append(driverSection);
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
  if (!hasValue(value) && !(options && options.content)) {
    return false;
  }
  const wrapper = element(
    "div",
    "detail-field" + (options && options.wide ? " detail-field--wide" : "")
  );
  wrapper.append(element("dt", "", label));
  const description = element("dd");
  if (options && options.content) {
    description.append(options.content);
  } else if (Array.isArray(value)) {
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
      appendDetailField(list, field.label, field.value, {
        wide: field.wide,
        content: field.content,
      }) ||
      populated;
  });
  if (!populated) {
    return null;
  }
  section.append(element("h3", "", title), list);
  return section;
}

function createFamilyDetailLink(driver) {
  const family = familyByIdentity.get(
    familyIdentityKey(driver.layer, driver.family)
  );
  const wrapper = element("span", "detail-family-action");
  wrapper.append(element("span", "", driver.family));
  if (family) {
    const button = element("button", "text-button", "View family \u2192");
    button.type = "button";
    button.dataset.viewFamilyId = family.id;
    button.setAttribute("aria-label", "View Family: " + family.name);
    wrapper.append(button);
  }
  return wrapper;
}

function relationshipCountLabel(count, direction) {
  const noun = count === 1 ? "relationship" : "relationships";
  return String(count) + " " + direction + " " + noun;
}

function appendRelationshipField(list, label, value, options = {}) {
  const wrapper = element("div", "relationship-metadata__field");
  wrapper.append(element("dt", "", label));
  const description = element("dd");
  if (options.content) {
    description.append(options.content);
  } else {
    description.textContent = hasValue(value) ? value : "Not specified";
  }
  wrapper.append(description);
  list.append(wrapper);
}

function createEvidenceIdList(evidenceIds) {
  if (!Array.isArray(evidenceIds) || evidenceIds.length === 0) {
    return element("span", "", "None recorded");
  }
  const list = element("ul", "relationship-evidence-ids");
  evidenceIds.forEach((evidenceId) => list.append(element("li", "", evidenceId)));
  return list;
}

function createRelationshipCard(relationship, direction) {
  const incoming = direction === "incoming";
  const relatedDriverId = incoming
    ? relationship.sourceDriverId
    : relationship.targetDriverId;
  const relatedDriver = driverById.get(relatedDriverId);
  const article = element("article", "relationship-card");
  setLayerIdentity(article, relatedDriver.layer);

  const directionLabel = incoming ? "Upstream driver" : "Downstream driver";
  const directionLine = element("p", "relationship-card__direction");
  const directionArrow = element("span", "", "\u2192");
  directionArrow.setAttribute("aria-hidden", "true");
  if (incoming) {
    directionLine.append(
      element("span", "", directionLabel),
      directionArrow,
      element("span", "", "This Driver")
    );
  } else {
    directionLine.append(
      element("span", "", "This Driver"),
      directionArrow,
      element("span", "", directionLabel.toLocaleLowerCase())
    );
  }

  const driverLink = element(
    "a",
    "relationship-card__driver-link",
    relatedDriver.name
  );
  driverLink.href = driverUrl(relatedDriver.id).toString();
  driverLink.dataset.relationshipDriverId = relatedDriver.id;
  driverLink.setAttribute(
    "aria-label",
    "Open " + directionLabel.toLocaleLowerCase() + ": " + relatedDriver.name
  );

  const identity = element("div", "relationship-card__identity");
  const layer = element("span", "layer-badge", relatedDriver.layer);
  setLayerIdentity(layer, relatedDriver.layer);
  identity.append(layer, element("span", "family-badge", relatedDriver.family));

  const facts = element("dl", "relationship-card__facts");
  [
    ["Relationship type", relationship.relationshipType],
    ["Expected direction", relationship.expectedDirection],
    ["Evidence strength", relationship.evidenceStrength],
  ].forEach(([label, value]) => {
    const fact = element("div", "relationship-card__fact");
    fact.append(element("dt", "", label), element("dd", "", value));
    facts.append(fact);
  });

  const details = element("details", "relationship-details");
  details.append(element("summary", "", "View relationship details"));
  const metadata = element("dl", "relationship-metadata");
  appendRelationshipField(metadata, "Relationship ID", relationship.id);
  appendRelationshipField(
    metadata,
    "Relationship type",
    relationship.relationshipType
  );
  appendRelationshipField(
    metadata,
    "Expected direction",
    relationship.expectedDirection
  );
  appendRelationshipField(metadata, "Functional form", relationship.functionalForm);
  appendRelationshipField(
    metadata,
    "Moderators / conditions",
    relationship.moderatorsConditions
  );
  appendRelationshipField(metadata, "Time lag", relationship.timeLag);
  appendRelationshipField(
    metadata,
    "Evidence strength",
    relationship.evidenceStrength
  );
  appendRelationshipField(metadata, "Evidence notes", relationship.evidenceNotes);
  appendRelationshipField(metadata, "Evidence IDs", null, {
    content: createEvidenceIdList(relationship.evidenceIds),
  });
  details.append(metadata);

  article.append(directionLine, driverLink, identity, facts, details);
  return article;
}

function createRelationshipGroup(title, direction, driverRelationships) {
  const section = element("section", "relationship-group");
  const heading = element("h4", "relationship-group__heading");
  const arrow = element("span", "relationship-group__arrow", "\u2192");
  arrow.setAttribute("aria-hidden", "true");
  if (direction === "incoming") {
    heading.append(arrow, element("span", "", title));
  } else {
    heading.append(element("span", "", title), arrow);
  }
  heading.append(
    element(
      "span",
      "relationship-group__count",
      String(driverRelationships.length)
    )
  );
  section.append(heading);

  if (driverRelationships.length === 0) {
    section.append(
      element(
        "p",
        "relationship-group__empty",
        direction === "incoming"
          ? "No incoming structured relationships are currently represented for this Driver."
          : "No outgoing structured relationships are currently represented for this Driver."
      )
    );
    return section;
  }

  const list = element("div", "relationship-list");
  driverRelationships.forEach((relationship) =>
    list.append(createRelationshipCard(relationship, direction))
  );
  section.append(list);
  return section;
}

function createRelationshipsSection(driver) {
  const incoming = incomingRelationshipsByDriverId.get(driver.id) || [];
  const outgoing = outgoingRelationshipsByDriverId.get(driver.id) || [];
  const section = element("section", "detail-section relationships-section");
  section.append(element("h3", "", "Structured relationships"));

  const content = element("div", "relationships-section__content");
  content.append(
    element(
      "p",
      "relationships-section__intro",
      "These canonical, evidence-bearing relationships are a curated and non-exhaustive subset of the connections relevant to this Driver."
    )
  );
  const counts = element("div", "relationship-counts", "");
  counts.setAttribute("aria-label", "Structured relationship counts");
  counts.append(
    element("span", "", relationshipCountLabel(incoming.length, "upstream")),
    element("span", "", relationshipCountLabel(outgoing.length, "downstream"))
  );
  content.append(counts);

  if (incoming.length === 0 && outgoing.length === 0) {
    content.append(
      element(
        "p",
        "relationships-empty",
        "No structured relationships are currently represented for this Driver."
      )
    );
  } else {
    const groups = element("div", "relationship-groups");
    groups.append(
      createRelationshipGroup("Upstream drivers (incoming)", "incoming", incoming),
      createRelationshipGroup("Downstream drivers (outgoing)", "outgoing", outgoing)
    );
    content.append(groups);
  }

  section.append(content);
  return section;
}

function createCausalNarrativeSection(driver) {
  const section = createDetailSection("Causal narrative", [
    { label: "Mechanism", value: driver.mechanism, wide: true },
    {
      label: "Other reported upstream influences",
      value: driver.likelyUpstreamInfluences,
      wide: true,
    },
    {
      label: "Other reported downstream influences",
      value: driver.likelyDownstreamInfluences,
      wide: true,
    },
    {
      label: "Moderators / boundary conditions",
      value: driver.moderatorsBoundaryConditions,
      wide: true,
    },
    {
      label: "Interaction candidates",
      value: driver.typicalInteractionCandidates,
      wide: true,
    },
  ]);
  if (!section) {
    return null;
  }
  const list = section.querySelector(".detail-grid");
  const content = element("div", "detail-section__content");
  content.append(
    element(
      "p",
      "causal-narrative-note",
      "These source-language fields provide broader reported context. They are not canonical graph edges."
    ),
    list
  );
  section.append(content);
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
      {
        label: "Family",
        value: driver.family,
        content: createFamilyDetailLink(driver),
      },
      { label: "Driver ID", value: driver.id },
    ]),
    createDetailSection("Definition & representation", [
      { label: "Definition", value: driver.definition, wide: true },
      { label: "Data type", value: driver.dataType },
      { label: "Representation / scale", value: driver.representationScale, wide: true },
      { label: "Polarity / direction", value: driver.polarityDirection, wide: true },
    ]),
    createRelationshipsSection(driver),
    createCausalNarrativeSection(driver),
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

function taxonomyUrl(parameters = {}) {
  const url = new URL(window.location.href);
  url.searchParams.delete(DRIVER_QUERY_PARAMETER);
  url.searchParams.delete(FAMILY_QUERY_PARAMETER);
  if (parameters.familyId) {
    url.searchParams.set(FAMILY_QUERY_PARAMETER, parameters.familyId);
  }
  if (parameters.driverId) {
    url.searchParams.set(DRIVER_QUERY_PARAMETER, parameters.driverId);
  }
  return url;
}

function driverUrl(driverId) {
  return taxonomyUrl({ driverId });
}

function familyUrl(familyId) {
  return taxonomyUrl({ familyId });
}

function baseUrl() {
  return taxonomyUrl();
}

function writeHistory(action, state, url) {
  if (action === "push") {
    history.pushState(state, "", url);
  } else if (action === "replace") {
    history.replaceState(state, "", url);
  }
}

function currentBackgroundState() {
  if (activeMode === "search") {
    return { view: "search" };
  }
  if (selectedBrowseFamilyId) {
    return {
      view: "family",
      layer: selectedBrowseLayer,
      familyId: selectedBrowseFamilyId,
    };
  }
  if (selectedBrowseLayer) {
    return { view: "layer", layer: selectedBrowseLayer };
  }
  return { view: "root" };
}

function showBrowseRoot(urlAction, focus) {
  currentDriverId = null;
  hideDialog();
  setMode("browse");
  selectedBrowseLayer = null;
  selectedBrowseFamilyId = null;
  renderBrowse();
  writeHistory(urlAction, { view: "root" }, baseUrl());
  if (focus) {
    browseHeading.focus();
  }
}

function showBrowseLayer(layer, urlAction, focus) {
  if (!hierarchy.has(layer)) {
    return false;
  }
  currentDriverId = null;
  hideDialog();
  setMode("browse");
  selectedBrowseLayer = layer;
  selectedBrowseFamilyId = null;
  renderBrowse();
  writeHistory(urlAction, { view: "layer", layer }, baseUrl());
  if (focus) {
    browseHeading.focus();
  }
  return true;
}

function showFamily(familyId, urlAction, focus) {
  const family = familyById.get(familyId);
  if (!family) {
    return false;
  }
  currentDriverId = null;
  detailOpenedFromExplorer = false;
  hideDialog();
  setMode("browse");
  selectedBrowseLayer = family.layer;
  selectedBrowseFamilyId = family.id;
  renderBrowse();
  writeHistory(
    urlAction,
    { view: "family", layer: family.layer, familyId: family.id },
    familyUrl(family.id)
  );
  if (focus) {
    browseHeading.focus();
  }
  return true;
}

function showSearch(urlAction, focus) {
  currentDriverId = null;
  hideDialog();
  setMode("search", { focus });
  writeHistory(urlAction, { view: "search" }, baseUrl());
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
    const background = currentBackgroundState();
    history.pushState(
      { view: "driver", driverId, fromExplorer: true, background },
      "",
      driverUrl(driverId)
    );
    detailOpenedFromExplorer = true;
  } else if (urlAction === "replace") {
    const background =
      history.state && history.state.background
        ? history.state.background
        : currentBackgroundState();
    history.replaceState(
      {
        view: "driver",
        driverId,
        fromExplorer: detailOpenedFromExplorer,
        background,
      },
      "",
      driverUrl(driverId)
    );
  }
  return true;
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
  const background =
    history.state && history.state.background
      ? history.state.background
      : { view: "root" };
  if (background.view === "family" && familyById.has(background.familyId)) {
    showFamily(background.familyId, "replace", true);
  } else if (background.view === "layer" && hierarchy.has(background.layer)) {
    showBrowseLayer(background.layer, "replace", true);
  } else if (background.view === "search") {
    showSearch("replace", true);
  } else {
    showBrowseRoot("replace", true);
  }
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

function restoreBackground(background) {
  if (background && background.view === "family" && familyById.has(background.familyId)) {
    const family = familyById.get(background.familyId);
    setMode("browse");
    selectedBrowseLayer = family.layer;
    selectedBrowseFamilyId = family.id;
    renderBrowse();
    detailDrivers = driversByFamilyId.get(family.id);
  } else if (background && background.view === "layer" && hierarchy.has(background.layer)) {
    setMode("browse");
    selectedBrowseLayer = background.layer;
    selectedBrowseFamilyId = null;
    renderBrowse();
    detailDrivers = drivers;
  } else if (background && background.view === "search") {
    setMode("search");
    detailDrivers = filteredDrivers;
  } else {
    setMode("browse");
    selectedBrowseLayer = null;
    selectedBrowseFamilyId = null;
    renderBrowse();
    detailDrivers = drivers;
  }
}

function applyLocationState(state) {
  const url = new URL(window.location.href);
  const driverId = url.searchParams.get(DRIVER_QUERY_PARAMETER);
  const familyId = url.searchParams.get(FAMILY_QUERY_PARAMETER);
  linkNotice.hidden = true;

  if (driverId) {
    const background =
      state && state.background
        ? state.background
        : familyId && familyById.has(familyId)
          ? { view: "family", familyId }
          : { view: "root" };
    restoreBackground(background);
    detailOpenedFromExplorer = Boolean(state && state.fromExplorer);
    if (!openDriver(driverId, null)) {
      linkNotice.textContent =
        "The linked Driver " + driverId + " was not found in this taxonomy.";
      linkNotice.hidden = false;
      hideDialog();
    }
    return;
  }

  detailOpenedFromExplorer = false;
  currentDriverId = null;
  hideDialog();

  if (familyId) {
    if (!showFamily(familyId, null, false)) {
      linkNotice.textContent =
        "The linked Family " + familyId + " was not found in this taxonomy.";
      linkNotice.hidden = false;
      showBrowseRoot(null, false);
    }
  } else if (state && state.view === "layer") {
    showBrowseLayer(state.layer, null, false);
  } else if (state && state.view === "search") {
    showSearch(null, false);
  } else {
    showBrowseRoot(null, false);
  }
}

function clearAllFilters() {
  searchInput.value = "";
  FACETS.forEach(({ field }) => facetSelections[field].clear());
  renderFacets();
  applyFilters();
}

async function fetchJson(url, label) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(label + " request failed with status " + response.status + ".");
  }
  return response.json();
}

async function loadTaxonomy() {
  try {
    const [driverData, familyEnvelope, relationshipEnvelope] = await Promise.all([
      fetchJson("../data/drivers.json", "Driver data"),
      fetchJson("../data/families.json", "Family data"),
      fetchJson("../data/relationships.json", "Relationship data"),
    ]);
    validateTaxonomyData(driverData, familyEnvelope, relationshipEnvelope);

    drivers = driverData.map((driver) =>
      Object.assign({}, driver, { _searchText: searchableText(driver) })
    );
    driverById = new Map(drivers.map((driver) => [driver.id, driver]));
    families = familyEnvelope.families;
    familyById = new Map(families.map((family) => [family.id, family]));
    familyByIdentity = new Map(
      families.map((family) => [
        familyIdentityKey(family.layer, family.name),
        family,
      ])
    );
    relationships = relationshipEnvelope.relationships;
    buildHierarchy();
    buildRelationshipIndexes();
    totalDriverCount.textContent = drivers.length.toLocaleString();
    totalLayerCount.textContent = hierarchy.size.toLocaleString();
    totalFamilyCount.textContent = families.length.toLocaleString();
    searchInput.disabled = false;
    renderFacets();
    applyFilters();
    const url = new URL(window.location.href);
    const initialDriverId = url.searchParams.get(DRIVER_QUERY_PARAMETER);
    const initialFamilyId = url.searchParams.get(FAMILY_QUERY_PARAMETER);
    const initialState = initialDriverId
      ? {
          view: "driver",
          driverId: initialDriverId,
          fromExplorer: false,
          background: initialFamilyId
            ? { view: "family", familyId: initialFamilyId }
            : { view: "root" },
        }
      : initialFamilyId
        ? { view: "family", familyId: initialFamilyId }
        : { view: "root" };
    history.replaceState(initialState, "", window.location.href);
    applyLocationState(initialState);
  } catch (error) {
    console.error("Unable to load PSYWERX taxonomy:", error);
    browseSummary.textContent = "Taxonomy unavailable";
    resultSummary.textContent = "Taxonomy unavailable";
    browseContent.replaceChildren();
    driverList.replaceChildren();
    const message = loadError.querySelector("p");
    message.textContent =
      "The required Driver, Family, and Relationship datasets could not be loaded or did not agree. " +
      "Check the browser console, then reload the page. For local preview, use an HTTP server.";
    loadError.hidden = false;
  }
}

browseModeButton.addEventListener("click", () => {
  if (activeMode === "browse") {
    browseHeading.focus();
  } else if (selectedBrowseFamilyId) {
    showFamily(selectedBrowseFamilyId, "push", true);
  } else if (selectedBrowseLayer) {
    showBrowseLayer(selectedBrowseLayer, "push", true);
  } else {
    showBrowseRoot("push", true);
  }
});

searchModeButton.addEventListener("click", () => {
  if (activeMode === "search") {
    searchInput.focus();
  } else {
    showSearch("push", true);
  }
});

browseContent.addEventListener("click", (event) => {
  const layerButton = event.target.closest("[data-browse-layer]");
  const familyButton = event.target.closest("[data-browse-family]");
  const driverButton = event.target.closest("[data-driver-id]");
  if (layerButton) {
    showBrowseLayer(layerButton.dataset.browseLayer, "push", true);
  } else if (familyButton) {
    showFamily(familyButton.dataset.browseFamily, "push", true);
  } else if (driverButton) {
    const familyDrivers = driversByFamilyId.get(selectedBrowseFamilyId);
    openDriver(driverButton.dataset.driverId, "push", familyDrivers);
  }
});

browseBreadcrumbs.addEventListener("click", (event) => {
  const button = event.target.closest("[data-browse-level]");
  if (!button) {
    return;
  }
  if (button.dataset.browseLevel === "root") {
    showBrowseRoot("push", true);
  } else {
    showBrowseLayer(selectedBrowseLayer, "push", true);
  }
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

driverDetail.addEventListener("click", (event) => {
  const relationshipLink = event.target.closest("[data-relationship-driver-id]");
  const familyButton = event.target.closest("[data-view-family-id]");
  if (
    relationshipLink &&
    !event.ctrlKey &&
    !event.metaKey &&
    !event.shiftKey &&
    !event.altKey
  ) {
    event.preventDefault();
    openDriver(relationshipLink.dataset.relationshipDriverId, "push");
    driverDetail.scrollTop = 0;
  } else if (familyButton) {
    showFamily(familyButton.dataset.viewFamilyId, "push", true);
  }
});

driverDialog.addEventListener("cancel", (event) => {
  event.preventDefault();
  closeDriverDetail();
});

driverDialog.addEventListener("click", (event) => {
  if (event.target === driverDialog) {
    closeDriverDetail();
  }
});

window.addEventListener("popstate", (event) => applyLocationState(event.state));

loadTaxonomy();
