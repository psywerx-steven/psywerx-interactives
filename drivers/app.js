"use strict";

const CONFIG = Object.assign(
  {
    causalExplorerEnabled: false,
    scenarioAiEnabled: false,
    scenarioApiUrl: "",
  },
  window.PSYWERX_CONFIG || {}
);

const PAGE_SIZE = 24;
const DRIVER_QUERY_PARAMETER = "driver";
const FAMILY_QUERY_PARAMETER = "family";
const VIEW_QUERY_PARAMETER = "view";
const SCENARIO_STORAGE_KEY = "psywerxScenarioV1";
const DEFAULT_DOCUMENT_TITLE = "PSYWERX Ontology Explorer";
const LAYER_ORDER = [
  "Biological", "Psychological", "Social", "Cultural",
  "Physical / Environmental", "Institutional / Structural",
  "Informational", "Technological",
];
const FALLBACK_TIME_ORDER = [
  "Seconds–Minutes", "Minutes–Hours", "Hours–Days", "Days–Weeks",
  "Weeks–Months", "Months–Years", "Years–Generations",
  "Mixed / Context-dependent", "Stable / Not applicable",
];
const FACETS = [
  { field: "entityType", label: "Entity type", codebookId: null },
  { field: "layer", label: "Layer", codebookId: "CB-DRV-LAYER" },
  { field: "family", label: "Family", codebookId: "CB-DRV-FAMILY" },
  { field: "dataType", label: "Data type", codebookId: "CB-DRV-DATA-TYPE" },
  { field: "modifiability", label: "Modifiability", codebookId: "CB-DRV-MODIFIABILITY" },
  { field: "volatility", label: "Volatility", codebookId: "CB-DRV-VOLATILITY" },
  { field: "timeScaleOfChange", label: "Time scale", codebookId: "CB-DRV-TIME-SCALE" },
  { field: "observability", label: "Observability", codebookId: "CB-DRV-OBSERVABILITY" },
  { field: "evidenceStrength", label: "Evidence strength", codebookId: "CB-DRV-EVIDENCE-STRENGTH" },
];
const PLAIN_LANGUAGE_KEYS = [
  "driverId", "plainLanguageLabel", "plainLanguageExplanation",
  "analyticQuestion", "whatThisDoesNotMean",
];
const SCENARIO_RESPONSE_KEYS = [
  "driverId", "scenarioMeaning", "operationalizationExamples",
  "importantCaveat", "inputSufficiency", "clarificationQuestion",
];
const SCENARIO_EXAMPLE_KEYS = [
  "title", "operationalization", "whatToLookFor", "questionToAsk",
];
const SCENARIO_EXAMPLES = {
  warning: {
    actor: "Residents in a coastal county",
    behaviorObjective: "Deciding whether and when to follow an emergency evacuation warning",
    context: "A fast-moving hurricane threat, uneven access to transportation, and warnings delivered through several local channels",
  },
  compliance: {
    actor: "Personnel in a large operational unit",
    behaviorObjective: "Following a newly issued safety procedure during routine operations",
    context: "The procedure changes established practice, supervisors vary in how they explain it, and teams work across several sites",
  },
  online: {
    actor: "Members of an online community during a public-health crisis",
    behaviorObjective: "Choosing which crisis updates to read, share, or act on",
    context: "Information is changing quickly, trusted and untrusted accounts post simultaneously, and users have different prior experiences",
  },
};

const $ = (selector) => document.querySelector(selector);
const browseModeButton = $("#browse-mode-button");
const searchModeButton = $("#search-mode-button");
const browsePanel = $("#browse-panel");
const searchPanel = $("#search-panel");
const browseBreadcrumbs = $("#browse-breadcrumbs");
const browseSummary = $("#browse-summary");
const browseKicker = $("#browse-kicker");
const browseHeading = $("#browse-heading");
const browseDescription = $("#browse-description");
const browseContent = $("#browse-content");
const searchInput = $("#driver-search");
const clearFiltersButton = $("#clear-filters");
const facetFilters = $("#facet-filters");
const activeFilters = $("#active-filters");
const totalDriverCount = $("#total-driver-count");
const totalRdsCount = $("#total-rds-count");
const totalEntityCount = $("#total-entity-count");
const totalFamilyCount = $("#total-family-count");
const resultSummary = $("#result-summary");
const driverList = $("#driver-list");
const loadMoreButton = $("#load-more");
const loadError = $("#load-error");
const linkNotice = $("#link-notice");
const driverDialog = $("#driver-dialog");
const driverDetail = $("#driver-detail");
const closeDetailButton = $("#close-detail");
const previousDriverButton = $("#previous-driver");
const nextDriverButton = $("#next-driver");
const detailPosition = $("#detail-position");
const copyLinkButton = $("#copy-link");
const copyStatus = $("#copy-status");
const scenarioEntryButton = $("#scenario-entry-button");
const scenarioComingSoon = $("#scenario-coming-soon");
const scenarioBanner = $("#scenario-banner");
const scenarioBannerActor = $("#scenario-banner-actor");
const scenarioBannerBehavior = $("#scenario-banner-behavior");
const scenarioBannerContext = $("#scenario-banner-context");
const scenarioEditButton = $("#scenario-edit-button");
const scenarioClearButton = $("#scenario-clear-button");
const scenarioDialog = $("#scenario-dialog");
const scenarioForm = $("#scenario-form");
const scenarioDialogClose = $("#scenario-dialog-close");
const scenarioFormClear = $("#scenario-form-clear");
const scenarioActor = $("#scenario-actor");
const scenarioBehavior = $("#scenario-behavior");
const scenarioContext = $("#scenario-context");
const codebookPopover = $("#codebook-popover");
const codebookPopoverClose = $("#codebook-popover-close");
const codebookPopoverTitle = $("#codebook-popover-title");
const codebookPopoverDefinition = $("#codebook-popover-definition");
const codebookPopoverLink = $("#codebook-popover-link");

let drivers = [];
let driverById = new Map();
let families = [];
let familyById = new Map();
let familyByIdentity = new Map();
let driversByFamilyId = new Map();
let hierarchy = new Map();
let plainLanguageByDriverId = new Map();
let codebookById = new Map();
let sourceById = new Map();
let filteredDrivers = [];
let detailDrivers = [];
let visibleCount = PAGE_SIZE;
let currentDriverId = null;
let detailOpenedFromExplorer = false;
let activeMode = "browse";
let selectedBrowseLayer = null;
let selectedBrowseFamilyId = null;
let searchTimer = null;
let timeScaleOrder = [...FALLBACK_TIME_ORDER];
let activeInfoButton = null;
const SCENARIO_AVAILABLE = Boolean(CONFIG.scenarioAiEnabled && CONFIG.scenarioApiUrl);
let activeScenario = SCENARIO_AVAILABLE ? readStoredScenario() : null;
if (!SCENARIO_AVAILABLE) {
  try { sessionStorage.removeItem(SCENARIO_STORAGE_KEY); } catch (_error) { /* no storage access */ }
}
let scenarioOutputs = new Map();
let pendingScenarioDriverId = null;
let scenarioRevision = 0;
let activeScenarioRequest = null;

const facetSelections = Object.fromEntries(
  FACETS.map(({ field }) => [field, new Set()])
);

function normalizeSearchText(value) {
  return String(value || "").normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase();
}

function normalizeComparable(value) {
  return normalizeSearchText(value).replace(/\s+/g, " ").trim();
}

function hasValue(value) {
  if (Array.isArray(value)) return value.length > 0;
  return value !== null && value !== undefined && String(value).trim() !== "";
}

function asValues(value, splitSemicolons = false) {
  const values = Array.isArray(value) ? value : hasValue(value) ? [value] : [];
  const expanded = splitSemicolons
    ? values.flatMap((item) => String(item).split(";")) : values;
  return expanded.map((item) => String(item).trim()).filter(Boolean);
}

function element(tagName, className, text) {
  const node = document.createElement(tagName);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function setLayerIdentity(node, layer) {
  node.dataset.layer = layer;
}

function sameKeys(record, expectedKeys) {
  if (!record || typeof record !== "object" || Array.isArray(record)) return false;
  const actual = Object.keys(record).sort();
  const expected = [...expectedKeys].sort();
  return actual.length === expected.length &&
    actual.every((key, index) => key === expected[index]);
}

function assertString(record, field, label, errors) {
  if (typeof record[field] !== "string" || record[field].trim() === "") {
    errors.push(label + " has no valid " + field + ".");
  }
}

function familyIdentityKey(layer, familyName) {
  return JSON.stringify([layer, familyName]);
}

function sortByName(records) {
  return records.sort((a, b) => a.name.localeCompare(
    b.name, undefined, { sensitivity: "base", numeric: true }
  ));
}

function validateTaxonomyData(driverData, familyEnvelope) {
  if (!Array.isArray(driverData)) throw new Error("Entity data is not an array.");
  if (!familyEnvelope || familyEnvelope.schemaVersion !== "1.0" ||
      !Array.isArray(familyEnvelope.families)) {
    throw new Error("Family data does not use Family Schema v1.0.");
  }
  const errors = [];
  const candidateDrivers = new Map();
  driverData.forEach((driver, index) => {
    const label = "Entity record " + String(index + 1);
    ["id", "name", "layer", "family", "definition"].forEach((field) =>
      assertString(driver, field, label, errors));
    if (!["DRIVER", "RELATIONAL_DERIVED_STATE"].includes(driver.entityType)) {
      errors.push(label + " has an invalid entityType.");
    }
    if (candidateDrivers.has(driver.id)) errors.push("Duplicate Entity ID: " + driver.id + ".");
    candidateDrivers.set(driver.id, driver);
  });
  const candidateFamilies = new Map();
  const candidateIdentities = new Map();
  familyEnvelope.families.forEach((family, index) => {
    const label = "Family record " + String(index + 1);
    ["id", "name", "layer", "definition"].forEach((field) =>
      assertString(family, field, label, errors));
    if (!Number.isInteger(family.driverCount) || family.driverCount < 0) {
      errors.push(label + " has no valid driverCount.");
    }
    if (!Number.isInteger(family.relationalDerivedStateCount) ||
        family.relationalDerivedStateCount < 0) {
      errors.push(label + " has no valid relationalDerivedStateCount.");
    }
    if (!Number.isInteger(family.totalEntityCount) || family.totalEntityCount < 1 ||
        family.totalEntityCount !== family.driverCount + family.relationalDerivedStateCount) {
      errors.push(label + " has no reconciled totalEntityCount.");
    }
    if (candidateFamilies.has(family.id)) errors.push("Duplicate Family ID: " + family.id + ".");
    candidateFamilies.set(family.id, family);
    const identity = familyIdentityKey(family.layer, family.name);
    if (candidateIdentities.has(identity)) errors.push("Duplicate Family identity: " + identity + ".");
    candidateIdentities.set(identity, family);
  });
  const counts = new Map();
  const driverCounts = new Map();
  const rdsCounts = new Map();
  driverData.forEach((driver) => {
    const family = candidateIdentities.get(familyIdentityKey(driver.layer, driver.family));
    if (!family) errors.push("Entity " + driver.id + " does not resolve to an exact Layer + Family.");
    else {
      counts.set(family.id, (counts.get(family.id) || 0) + 1);
      const typeCounts = driver.entityType === "DRIVER" ? driverCounts : rdsCounts;
      typeCounts.set(family.id, (typeCounts.get(family.id) || 0) + 1);
    }
  });
  familyEnvelope.families.forEach((family) => {
    if ((counts.get(family.id) || 0) !== family.totalEntityCount)
      errors.push("Family " + family.id + " total Entity count does not reconcile.");
    if ((driverCounts.get(family.id) || 0) !== family.driverCount)
      errors.push("Family " + family.id + " Driver count does not reconcile.");
    if ((rdsCounts.get(family.id) || 0) !== family.relationalDerivedStateCount)
      errors.push("Family " + family.id + " RDS count does not reconcile.");
  });
  if (errors.length) {
    throw new Error(errors.slice(0, 8).join(" ") +
      (errors.length > 8 ? " " + String(errors.length - 8) + " more errors." : ""));
  }
}

function validatePlainLanguageData(driverData, envelope) {
  if (!envelope || envelope.schemaVersion !== "1.0" || !Array.isArray(envelope.drivers)) {
    throw new Error("Public explanation data does not use Schema v1.0.");
  }
  const errors = [];
  const canonicalIds = new Set(driverData.map((driver) => driver.id));
  const indexed = new Map();
  envelope.drivers.forEach((record, index) => {
    const label = "Public explanation record " + String(index + 1);
    if (!sameKeys(record, PLAIN_LANGUAGE_KEYS)) errors.push(label + " has unexpected fields.");
    ["driverId", "plainLanguageLabel", "plainLanguageExplanation", "analyticQuestion"]
      .forEach((field) => assertString(record, field, label, errors));
    if (record.whatThisDoesNotMean !== null &&
        (typeof record.whatThisDoesNotMean !== "string" || !record.whatThisDoesNotMean.trim())) {
      errors.push(label + " has an invalid whatThisDoesNotMean value.");
    }
    if (!canonicalIds.has(record.driverId)) errors.push(label + " references an unknown Entity.");
    if (indexed.has(record.driverId)) errors.push("Duplicate explanation Driver ID: " + record.driverId + ".");
    indexed.set(record.driverId, record);
  });
  if (errors.length) throw new Error(errors.slice(0, 8).join(" "));
  return indexed;
}

function validateCodebook(envelope) {
  if (!envelope || envelope.schemaVersion !== "1.0" || !Array.isArray(envelope.entries)) {
    throw new Error("Codebook data does not use Schema v1.0.");
  }
  const indexed = new Map();
  envelope.entries.forEach((entry) => {
    ["id", "field", "definition"].forEach((field) => {
      if (typeof entry[field] !== "string" || !entry[field].trim()) {
        throw new Error("Codebook entry has no valid " + field + ".");
      }
    });
    if (indexed.has(entry.id)) throw new Error("Duplicate Codebook ID: " + entry.id + ".");
    indexed.set(entry.id, entry);
  });
  return indexed;
}

function validateSources(envelope) {
  if (!envelope || envelope.schemaVersion !== "1.0" || !Array.isArray(envelope.sources)) {
    throw new Error("Source data does not use Source Schema v1.0.");
  }
  const indexed = new Map();
  envelope.sources.forEach((source) => {
    if (typeof source.id !== "string" || !source.id.trim() ||
        typeof source.citationText !== "string" || !source.citationText.trim()) {
      throw new Error("Source data contains an invalid record.");
    }
    if (indexed.has(source.id)) throw new Error("Duplicate Source ID: " + source.id + ".");
    indexed.set(source.id, source);
  });
  return indexed;
}

function validateAliases(entityData, envelope) {
  if (!envelope || envelope.schemaVersion !== "1.0" || !Array.isArray(envelope.aliases)) {
    throw new Error("Alias data does not use Alias Schema v1.0.");
  }
  const entityIds = new Set(entityData.map((entity) => entity.id));
  const aliasIds = new Set();
  const indexed = new Map(entityData.map((entity) => [entity.id, {
    search: [], display: [],
  }]));
  envelope.aliases.forEach((alias) => {
    if (typeof alias.aliasId !== "string" || !alias.aliasId.trim() ||
        typeof alias.text !== "string" || !alias.text.trim() ||
        !Array.isArray(alias.entityIds) || alias.entityIds.length === 0 ||
        alias.entityIds.some((entityId) => !entityIds.has(entityId))) {
      throw new Error("Alias data contains an invalid or dangling record.");
    }
    if (aliasIds.has(alias.aliasId)) throw new Error("Duplicate Alias ID: " + alias.aliasId + ".");
    aliasIds.add(alias.aliasId);
    alias.entityIds.forEach((entityId) => {
      const target = indexed.get(entityId);
      target.search.push(alias.text);
      if (alias.publicDisplayRule === "DISPLAY_ON_ENTITY") target.display.push(alias.text);
    });
  });
  indexed.forEach((value) => {
    value.search = [...new Set(value.search)];
    value.display = [...new Set(value.display)];
  });
  return indexed;
}

function driverSearchFields(driver) {
  const plain = driver._plainLanguage;
  return [
    { weight: 0, values: [driver.name] },
    { weight: 10, values: driver._searchAliases || driver.aliases || [] },
    { weight: 20, values: [driver.definition] },
    { weight: 30, values: [plain && plain.plainLanguageExplanation] },
    { weight: 40, values: [plain && plain.analyticQuestion] },
    { weight: 50, values: [driver.family] },
    { weight: 60, values: [driver.layer] },
    { weight: 70, values: [plain && plain.plainLanguageLabel] },
  ].map((group) => ({
    weight: group.weight,
    values: group.values.filter(hasValue).map(normalizeSearchText),
  }));
}

function searchRank(driver, query) {
  if (!query) return 0;
  let best = Number.POSITIVE_INFINITY;
  driver._searchFields.forEach((group) => group.values.forEach((value) => {
    const position = value.indexOf(query);
    if (position === -1) return;
    const penalty = value === query ? 0 : position === 0 ? 1 : 2;
    best = Math.min(best, group.weight + penalty);
  }));
  return best;
}

function buildIndexes() {
  driverById = new Map(drivers.map((driver) => [driver.id, driver]));
  familyById = new Map(families.map((family) => [family.id, family]));
  familyByIdentity = new Map(families.map((family) => [
    familyIdentityKey(family.layer, family.name), family,
  ]));
  hierarchy = new Map();
  driversByFamilyId = new Map(families.map((family) => [family.id, []]));
  families.forEach((family) => {
    if (!hierarchy.has(family.layer)) hierarchy.set(family.layer, []);
    hierarchy.get(family.layer).push(family);
  });
  hierarchy.forEach((layerFamilies) => sortByName(layerFamilies));
  drivers.forEach((driver) => {
    const family = familyByIdentity.get(familyIdentityKey(driver.layer, driver.family));
    driversByFamilyId.get(family.id).push(driver);
  });
  driversByFamilyId.forEach((familyDrivers) => sortByName(familyDrivers));
  const timeEntry = codebookById.get("CB-DRV-TIME-SCALE");
  if (timeEntry && Array.isArray(timeEntry.allowedValues) && timeEntry.allowedValues.length) {
    timeScaleOrder = [...timeEntry.allowedValues];
  }
}

function setMode(mode, options = {}) {
  activeMode = mode === "search" ? "search" : "browse";
  const browsing = activeMode === "browse";
  browsePanel.hidden = !browsing;
  searchPanel.hidden = browsing;
  browseModeButton.setAttribute("aria-pressed", String(browsing));
  searchModeButton.setAttribute("aria-pressed", String(!browsing));
  if (options.focus) (browsing ? browseHeading : searchInput).focus();
}

function entityCountLabel(family) {
  const total = family.totalEntityCount;
  const rds = family.relationalDerivedStateCount;
  return total.toLocaleString() + (total === 1 ? " Entity" : " Entities") +
    (rds ? " · " + rds.toLocaleString() + " RDS" : "");
}

function hierarchyButton(title, meta, type, value, layer) {
  const article = element("article", "hierarchy-card");
  if (layer) setLayerIdentity(article, layer);
  const button = element("button", "hierarchy-card__button");
  button.type = "button";
  button.dataset[type] = value;
  button.append(element("span", "hierarchy-card__title", title),
    element("span", "hierarchy-card__meta", meta));
  const action = element("span", "hierarchy-card__action", "Explore →");
  action.setAttribute("aria-hidden", "true");
  button.append(action);
  article.append(button);
  return article;
}

function createFamilyCard(family) {
  const article = element("article", "hierarchy-card family-card");
  setLayerIdentity(article, family.layer);
  const button = element("button", "hierarchy-card__button family-card__button");
  button.type = "button";
  button.dataset.browseFamily = family.id;
  button.setAttribute("aria-label", "Explore Family " + family.name + ", " + entityCountLabel(family));
  button.append(element("span", "hierarchy-card__title", family.name),
    element("span", "family-card__definition", family.definition),
    element("span", "hierarchy-card__meta", entityCountLabel(family)));
  const action = element("span", "hierarchy-card__action", "Explore Family →");
  action.setAttribute("aria-hidden", "true");
  button.append(action);
  article.append(button);
  return article;
}

function createFamilyOverview(family) {
  const article = element("article", "family-overview family-overview--public");
  setLayerIdentity(article, family.layer);
  const identity = element("header", "family-overview__identity");
  identity.append(element("p", "eyebrow", "Entity Family"));
  const badges = element("div", "family-overview__badges");
  const layer = element("span", "layer-badge", family.layer);
  setLayerIdentity(layer, family.layer);
  badges.append(layer, element("span", "driver-id", family.id),
    element("span", "family-badge", entityCountLabel(family)));
  identity.append(badges, element("h4", "", family.name),
    element("p", "family-overview__definition", family.definition));
  article.append(identity);
  return article;
}

function breadcrumbButton(label, level) {
  const button = element("button", "breadcrumbs__button", label);
  button.type = "button";
  button.dataset.browseLevel = level;
  return button;
}

function renderBrowse() {
  const content = document.createDocumentFragment();
  const crumbs = document.createDocumentFragment();
  crumbs.append(breadcrumbButton("All Layers", "root"));
  if (!selectedBrowseLayer) {
    browseKicker.textContent = "Layer → Family → Entity";
    browseHeading.textContent = "Choose a Layer";
    browseDescription.textContent = "Start with one of the eight interacting Layers.";
    browseSummary.textContent = hierarchy.size.toLocaleString() + " Layers · " + drivers.length.toLocaleString() + " Entities";
    browseContent.className = "hierarchy-grid";
    LAYER_ORDER.filter((layer) => hierarchy.has(layer)).forEach((layer) => {
      const layerFamilies = hierarchy.get(layer);
      const count = layerFamilies.reduce((total, family) => total + family.totalEntityCount, 0);
      content.append(hierarchyButton(layer,
        layerFamilies.length.toLocaleString() + " Families · " + count.toLocaleString() + " Entities",
        "browseLayer", layer, layer));
    });
  } else if (!selectedBrowseFamilyId) {
    const layerFamilies = hierarchy.get(selectedBrowseLayer) || [];
    crumbs.append(" / ", element("span", "breadcrumbs__current", selectedBrowseLayer));
    browseKicker.textContent = selectedBrowseLayer + " Layer";
    browseHeading.textContent = "Choose a Family";
    browseDescription.textContent = "Families group closely related entities within this Layer.";
    const count = layerFamilies.reduce((total, family) => total + family.totalEntityCount, 0);
    browseSummary.textContent = layerFamilies.length.toLocaleString() + " Families · " + count.toLocaleString() + " Entities";
    browseContent.className = "hierarchy-grid";
    layerFamilies.forEach((family) => content.append(createFamilyCard(family)));
  } else {
    const family = familyById.get(selectedBrowseFamilyId);
    const familyDrivers = driversByFamilyId.get(family.id) || [];
    crumbs.append(" / ", breadcrumbButton(selectedBrowseLayer, "layer"), " / ",
      element("span", "breadcrumbs__current", family.name));
    browseKicker.textContent = selectedBrowseLayer + " Layer";
    browseHeading.textContent = family.name;
    browseDescription.textContent = "Explore all Drivers and relational/derived states governed within this Family.";
    browseSummary.textContent = family.id + " · " + entityCountLabel(family);
    browseContent.className = "family-view";
    content.append(createFamilyOverview(family));
    const driverSection = element("section", "family-drivers");
    driverSection.append(element("h4", "family-drivers__heading", "Entities in this Family"));
    const list = element("div", "driver-list");
    familyDrivers.forEach((driver) => list.append(createDriverCard(driver)));
    driverSection.append(list);
    content.append(driverSection);
  }
  browseBreadcrumbs.replaceChildren(crumbs);
  browseContent.replaceChildren(content);
}

function driverFacetValues(driver, field) {
  return field === "timeScaleOfChange" ? asValues(driver[field], true) : asValues(driver[field]);
}

function facetSourceDrivers(field) {
  if (field !== "family" || facetSelections.layer.size === 0) return drivers;
  return drivers.filter((driver) => facetSelections.layer.has(driver.layer));
}

function sortFacetValues(field, values) {
  if (field === "entityType") {
    return values.sort((a, b) => ["DRIVER", "RELATIONAL_DERIVED_STATE"].indexOf(a) -
      ["DRIVER", "RELATIONAL_DERIVED_STATE"].indexOf(b));
  }
  if (field === "layer") return values.sort((a, b) => LAYER_ORDER.indexOf(a) - LAYER_ORDER.indexOf(b));
  if (field === "timeScaleOfChange") {
    return values.sort((a, b) => {
      const ai = timeScaleOrder.indexOf(a);
      const bi = timeScaleOrder.indexOf(b);
      return (ai === -1 ? 999 : ai) - (bi === -1 ? 999 : bi) || a.localeCompare(b);
    });
  }
  return values.sort((a, b) => a.localeCompare(b, undefined, { sensitivity: "base", numeric: true }));
}

function uniqueFacetValues(field, sourceDrivers = drivers) {
  const values = new Set();
  sourceDrivers.forEach((driver) => driverFacetValues(driver, field).forEach((value) => values.add(value)));
  return sortFacetValues(field, [...values]);
}

function createInfoButton(codebookId, label) {
  if (!codebookById.has(codebookId)) return null;
  const button = element("button", "info-button", "i");
  button.type = "button";
  button.dataset.codebookId = codebookId;
  button.setAttribute("aria-label", "Codebook help for " + label);
  button.setAttribute("aria-expanded", "false");
  button.setAttribute("aria-controls", "codebook-popover");
  return button;
}

function appendConceptHeading(container, tagName, label, codebookId) {
  const heading = element(tagName, "concept-heading");
  heading.append(element("span", "", label));
  const info = createInfoButton(codebookId, label);
  if (info) heading.append(info);
  container.append(heading);
  return heading;
}

function renderFacet(field) {
  const config = FACETS.find((facet) => facet.field === field);
  const old = facetFilters.querySelector('[data-facet="' + field + '"]');
  const details = element("details", "facet");
  details.dataset.facet = field;
  details.open = old ? old.open : field === "layer" || field === "family";
  const summary = element("summary", "facet__summary");
  summary.append(element("span", "", config.label), element("span", "facet__selected-count"));
  details.append(summary);
  const info = createInfoButton(config.codebookId, config.label);
  if (info) { info.classList.add("facet__info"); details.append(info); }
  const sourceDrivers = facetSourceDrivers(field);
  const values = uniqueFacetValues(field, sourceDrivers);
  const counts = new Map(values.map((value) => [value, 0]));
  sourceDrivers.forEach((driver) => new Set(driverFacetValues(driver, field)).forEach((value) =>
    counts.set(value, (counts.get(value) || 0) + 1)));
  const choices = element("div", "facet__choices");
  values.forEach((value, index) => {
    const displayedValue = field === "entityType"
      ? entityTypeLabel({ entityType: value }) : value;
    const label = element("label", "facet-option");
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = value;
    checkbox.dataset.facetField = field;
    checkbox.id = "facet-" + field + "-" + String(index);
    checkbox.checked = facetSelections[field].has(value);
    label.htmlFor = checkbox.id;
    label.append(checkbox, element("span", "facet-option__label", displayedValue),
      element("span", "facet-option__count", String(counts.get(value) || 0)));
    choices.append(label);
  });
  details.append(choices);
  if (old) old.replaceWith(details); else facetFilters.append(details);
}

function renderFacets() {
  facetFilters.replaceChildren();
  FACETS.forEach(({ field }) => renderFacet(field));
  updateFacetSelectedCounts();
}

function updateFacetSelectedCounts() {
  FACETS.forEach(({ field }) => {
    const node = facetFilters.querySelector('[data-facet="' + field + '"] .facet__selected-count');
    if (node) node.textContent = facetSelections[field].size
      ? String(facetSelections[field].size) + " selected" : "Any";
  });
}

function syncAvailableFamilies() {
  const available = new Set(uniqueFacetValues("family", facetSourceDrivers("family")));
  [...facetSelections.family].forEach((family) => {
    if (!available.has(family)) facetSelections.family.delete(family);
  });
  renderFacet("family");
}

function matchesFacet(driver, field) {
  const selected = facetSelections[field];
  return selected.size === 0 || driverFacetValues(driver, field).some((value) => selected.has(value));
}

function applyFilters(options = {}) {
  if (options.resetLimit !== false) visibleCount = PAGE_SIZE;
  const query = normalizeSearchText(searchInput.value.trim());
  filteredDrivers = drivers.map((driver) => ({ driver, rank: searchRank(driver, query) }))
    .filter(({ driver, rank }) => Number.isFinite(rank) && FACETS.every(({ field }) => matchesFacet(driver, field)))
    .sort((a, b) => a.rank - b.rank || a.driver.name.localeCompare(
      b.driver.name, undefined, { sensitivity: "base", numeric: true }
    )).map(({ driver }) => driver);
  updateFacetSelectedCounts();
  renderActiveFilters();
  renderResults();
}

function filterChip(label, value, field) {
  const button = element("button", "filter-chip", label + ": " + value + " ");
  button.type = "button";
  button.dataset.clearFacet = field;
  button.dataset.clearValue = value;
  button.setAttribute("aria-label", "Remove " + label + " filter: " + value);
  const mark = element("span", "", "×");
  mark.setAttribute("aria-hidden", "true");
  button.append(mark);
  return button;
}

function renderActiveFilters() {
  const fragment = document.createDocumentFragment();
  const query = searchInput.value.trim();
  if (query) fragment.append(filterChip("Search", query, "search"));
  FACETS.forEach(({ field, label }) => facetSelections[field].forEach((value) =>
    fragment.append(filterChip(label, value, field))));
  activeFilters.replaceChildren(fragment);
  clearFiltersButton.disabled = !query && !FACETS.some(({ field }) => facetSelections[field].size);
}

function formatValues(value) {
  return asValues(value, true).join("; ");
}

function entityTypeLabel(entity) {
  return entity.entityType === "RELATIONAL_DERIVED_STATE"
    ? "Relational / derived state" : "Driver";
}

function formatEnumLabel(value) {
  return hasValue(value) ? String(value).replaceAll("_", " ").toLowerCase()
    .replace(/(^|\s)\S/g, (letter) => letter.toUpperCase()) : "";
}

function formatConstituents(specifications) {
  if (!Array.isArray(specifications)) return formatValues(specifications);
  return specifications.map((specification) => {
    if (!specification || typeof specification !== "object") return String(specification);
    const identity = specification.entityId || specification.externalParameterType;
    return identity + (specification.required ? " (required)" : " (optional)");
  }).join("; ");
}

function createDriverCard(driver) {
  const article = element("article", "driver-card");
  setLayerIdentity(article, driver.layer);
  const button = element("button", "driver-card__button");
  button.type = "button";
  button.dataset.driverId = driver.id;
  button.setAttribute("aria-label", "Open " + entityTypeLabel(driver) + " " + driver.name);
  const meta = element("div", "driver-card__meta");
  const layer = element("span", "layer-badge", driver.layer);
  setLayerIdentity(layer, driver.layer);
  meta.append(layer, element("span", "entity-type-badge", entityTypeLabel(driver)),
    element("span", "driver-id", driver.id));
  button.append(meta, element("h3", "driver-card__title", driver.name),
    element("p", "driver-card__taxonomy", driver.family),
    element("p", "driver-card__definition", driver.definition));
  const attributes = element("div", "driver-card__attributes");
  if (hasValue(driver.dataType)) attributes.append(element("span", "", driver.dataType));
  if (hasValue(driver.timeScaleOfChange)) attributes.append(element("span", "", formatValues(driver.timeScaleOfChange)));
  if (hasValue(driver.evidenceStrength)) attributes.append(element("span", "", driver.evidenceStrength + " evidence"));
  if (attributes.children.length) button.append(attributes);
  const action = element("span", "driver-card__action", "View Entity record →");
  action.setAttribute("aria-hidden", "true");
  button.append(action);
  article.append(button);
  return article;
}

function renderResults() {
  const total = filteredDrivers.length;
  const shown = filteredDrivers.slice(0, visibleCount);
  const fragment = document.createDocumentFragment();
  if (!total) {
    const empty = element("div", "empty-state");
    empty.append(element("h3", "", "No Entities match these filters"),
      element("p", "", "Try a broader search or remove one or more active filters."));
    fragment.append(empty);
  } else shown.forEach((driver) => fragment.append(createDriverCard(driver)));
  driverList.replaceChildren(fragment);
  resultSummary.textContent = total > shown.length
    ? total.toLocaleString() + " Entities found · Showing " + shown.length.toLocaleString()
    : total.toLocaleString() + (total === 1 ? " Entity found" : " Entities found");
  loadMoreButton.hidden = shown.length >= total;
}

function createPublicSection(title, className = "") {
  const section = element("section", "detail-section public-detail-section " + className);
  section.append(element("h3", "", title));
  return section;
}

function appendTextOrList(container, value, className = "") {
  const values = asValues(value);
  if (!values.length) return false;
  if (values.length === 1) container.append(element("p", className, values[0]));
  else {
    const list = element("ul", className ? className + " detail-value-list" : "detail-value-list");
    values.forEach((item) => list.append(element("li", "", item)));
    container.append(list);
  }
  return true;
}

function createDefinitionSection(driver) {
  const section = createPublicSection("Definition", "definition-section");
  section.append(element("p", "section-context", "Canonical scientific definition"),
    element("p", "canonical-definition", driver.definition));
  return section;
}

function createDerivationSection(driver) {
  if (driver.entityType !== "RELATIONAL_DERIVED_STATE") return null;
  const section = createPublicSection("Derivation", "derivation-section");
  const facts = element("dl", "derivation-facts");
  [
    ["Subtype", formatEnumLabel(driver.entitySubtype)],
    ["Derivation type", formatEnumLabel(driver.derivationType)],
    ["Constituent specification", formatConstituents(driver.constituentSpecifications)],
    ["Derivation logic", driver.derivationLogic],
    ["Scope", driver.scopeRequirements],
    ["Recalculation rule", driver.recalculationBehavior],
  ].filter(([, value]) => hasValue(value)).forEach(([label, value]) => {
    const item = element("div", "derivation-fact");
    item.append(element("dt", "", label), element("dd", "", value));
    facts.append(item);
  });
  section.append(facts);
  return section;
}

function createGovernanceStatusSection(driver) {
  if (driver.metadataStatus !== "PARTIAL_GOVERNED_PREVIEW") return null;
  const section = createPublicSection("Governance status", "governance-status-section");
  section.append(element("p", "",
    "Identity and definition are governed for this preview. Peripheral scientific metadata remains unpopulated where the migration specification did not supply it."));
  if (Array.isArray(driver.blockedFields) && driver.blockedFields.length) {
    section.append(element("p", "section-context", "Blocked pending governance input: " +
      driver.blockedFields.join(", ")));
  }
  return section;
}

function createInBriefSection(driver) {
  const section = createPublicSection("In brief", "in-brief-section");
  if (!driver._plainLanguage) {
    const notice = element("div", "explanation-placeholder");
    notice.append(element("p", "",
      "Additional explanatory description is not yet available for this entity."));
    section.append(notice);
    return section;
  }
  section.append(element("p", "in-brief-copy", driver._plainLanguage.plainLanguageExplanation));
  if (hasValue(driver._plainLanguage.whatThisDoesNotMean)) {
    const boundary = element("div", "meaning-boundary");
    boundary.append(element("h4", "", "What this doesn’t mean"),
      element("p", "", driver._plainLanguage.whatThisDoesNotMean));
    section.append(boundary);
  }
  return section;
}

function createQuestionSection(driver) {
  if (!driver._plainLanguage || !hasValue(driver._plainLanguage.analyticQuestion)) return null;
  const section = createPublicSection("Question to investigate", "question-section");
  section.append(element("p", "analytic-question", driver._plainLanguage.analyticQuestion));
  return section;
}

function createDynamicsFact(label, value, codebookId) {
  if (!hasValue(value)) return null;
  const item = element("li", "dynamics-fact");
  const term = element("span", "dynamics-fact__term", label);
  const info = createInfoButton(codebookId, label);
  if (info) term.append(info);
  item.append(term, element("span", "dynamics-fact__value", value));
  return item;
}

function createHowItOperatesSection(driver) {
  const section = createPublicSection("How it operates", "operations-section");
  if (hasValue(driver.mechanism)) {
    const mechanism = element("div", "operations-block");
    appendConceptHeading(mechanism, "h4", "Mechanism", "CB-DRV-MECHANISM");
    mechanism.append(element("p", "", driver.mechanism));
    section.append(mechanism);
  }
  const dynamics = element("div", "operations-block dynamics-block");
  dynamics.append(element("h4", "", "Dynamics"));
  const facts = element("ul", "dynamics-list");
  const temporal = formatValues(driver.timeScaleOfChange) +
    (hasValue(driver.timeScaleQualifier) ? ". " + driver.timeScaleQualifier : "");
  [
    createDynamicsFact("Data type", driver.dataType, "CB-DRV-DATA-TYPE"),
    createDynamicsFact("Polarity / direction", driver.polarityDirection, "CB-DRV-POLARITY-DIRECTION"),
    createDynamicsFact("Time scale of change", temporal, "CB-DRV-TIME-SCALE"),
    createDynamicsFact("Onset / causal lag", formatValues(driver.onsetCausalLag), "CB-DRV-ONSET-LAG"),
    createDynamicsFact("Persistence / recovery", driver.persistenceRecovery, "CB-DRV-PERSISTENCE-RECOVERY"),
    createDynamicsFact("Volatility", driver.volatility, "CB-DRV-VOLATILITY"),
    createDynamicsFact("Modifiability", driver.modifiability, "CB-DRV-MODIFIABILITY"),
  ].filter(Boolean).forEach((fact) => facts.append(fact));
  if (facts.children.length) dynamics.append(facts);
  section.append(dynamics);
  return section;
}

function createContextSection(driver) {
  if (!hasValue(driver.moderatorsBoundaryConditions)) return null;
  const section = createPublicSection("Context and conditions", "context-section");
  appendConceptHeading(section, "h4", "Moderators / boundary conditions", "CB-DRV-MODERATORS");
  appendTextOrList(section, driver.moderatorsBoundaryConditions);
  return section;
}

function createObservationBlock(label, value, codebookId) {
  if (!hasValue(value)) return null;
  const block = element("div", "observation-block");
  appendConceptHeading(block, "h4", label, codebookId);
  appendTextOrList(block, value);
  return block;
}

function createObservationSection(driver) {
  const blocks = [
    createObservationBlock("Possible indicators", driver.indicators, "CB-DRV-INDICATORS"),
    createObservationBlock("Assessment approaches", driver.measurementAssessmentMethods, "CB-DRV-MEASUREMENT-METHODS"),
    createObservationBlock("Observability", driver.observability, "CB-DRV-OBSERVABILITY"),
    createObservationBlock("Measurement considerations", driver.measurementCaveats, "CB-DRV-MEASUREMENT-CAVEATS"),
  ].filter(Boolean);
  if (!blocks.length) return null;
  const section = createPublicSection("How to observe it", "observation-section");
  blocks.forEach((block) => section.append(block));
  return section;
}

function createEvidenceSection(driver) {
  if (!hasValue(driver.evidenceStrength) && !hasValue(driver.evidenceNotes)) return null;
  const section = createPublicSection("Evidence", "evidence-section");
  if (hasValue(driver.evidenceStrength)) {
    const strength = element("div", "evidence-strength");
    appendConceptHeading(strength, "h4", "Evidence strength", "CB-DRV-EVIDENCE-STRENGTH");
    strength.append(element("p", "evidence-strength__value", driver.evidenceStrength));
    section.append(strength);
  }
  if (hasValue(driver.evidenceNotes)) {
    const notes = element("div", "evidence-notes");
    notes.append(element("h4", "", "Evidence notes"), element("p", "", driver.evidenceNotes));
    section.append(notes);
  }
  return section;
}

function safeExternalHref(value) {
  if (!hasValue(value)) return null;
  try {
    const url = new URL(value);
    return ["https:", "http:"].includes(url.protocol) ? url.href : null;
  } catch (_error) { return null; }
}

function createSourcesSection(driver) {
  if (!Array.isArray(driver.keySources) || !driver.keySources.length) return null;
  const section = createPublicSection("Key sources", "sources-section");
  const list = element("ol", "source-list");
  driver.keySources.forEach((sourceId) => {
    const source = sourceById.get(sourceId);
    const item = element("li", "source-item");
    if (!source) {
      item.append(element("p", "source-item__citation",
        "Citation details are unavailable for this governed source reference."));
      list.append(item);
      return;
    }
    item.append(element("p", "source-item__citation", source.citationText));
    const href = safeExternalHref(source.href);
    if (href) {
      const link = element("a", "source-item__link", source.linkLabel ||
        (source.resolutionType === "SEARCH" ? "Search for source ↗" : "View source ↗"));
      link.href = href;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      if (source.resolutionType === "SEARCH") link.classList.add("source-item__link--search");
      item.append(link);
    } else item.append(element("span", "source-item__unresolved", "Direct link unavailable"));
    list.append(item);
  });
  section.append(list);
  return section;
}

function createDriverBreadcrumbs(driver, family) {
  const nav = element("nav", "driver-breadcrumbs");
  nav.setAttribute("aria-label", "Entity hierarchy");
  const layer = element("button", "driver-breadcrumbs__link", driver.layer);
  layer.type = "button";
  layer.dataset.driverLayer = driver.layer;
  const familyButton = element("button", "driver-breadcrumbs__link", driver.family);
  familyButton.type = "button";
  if (family) familyButton.dataset.driverFamily = family.id;
  const separatorOne = element("span", "driver-breadcrumbs__separator", "›");
  separatorOne.setAttribute("aria-hidden", "true");
  nav.append(layer, separatorOne, familyButton, separatorOne.cloneNode(true),
    element("span", "driver-breadcrumbs__current", driver.id));
  return nav;
}

function createScenarioSection(driver) {
  if (!activeScenario) return null;
  const section = createPublicSection("Applied to this scenario", "scenario-application");
  section.dataset.scenarioSection = driver.id;
  section.append(element("p", "scenario-analysis-label", "AI-assisted illustrative analysis"),
    element("p", "scenario-disclaimer",
      "This AI-assisted operationalization identifies ways an entity could be defined, observed, or investigated in the scenario. It does not establish that the entity is present or that it caused the behavior."));
  const outputState = scenarioOutputs.get(driver.id);
  if (outputState && outputState.result) section.append(renderScenarioResult(outputState));
  const actions = element("div", "scenario-application__actions");
  const generate = element("button", "primary-button", outputState && outputState.result
    ? "Regenerate analysis" : "Operationalize this entity");
  generate.type = "button";
  generate.dataset.operationalizeDriver = driver.id;
  generate.disabled = !SCENARIO_AVAILABLE || pendingScenarioDriverId !== null;
  if (pendingScenarioDriverId === driver.id) generate.textContent = "Generating…";
  actions.append(generate);
  section.append(actions);
  const status = element("p", "scenario-request-status");
  status.dataset.scenarioStatus = driver.id;
  status.setAttribute("role", "status");
  status.setAttribute("aria-live", "polite");
  if (outputState && outputState.error) status.textContent = outputState.error;
  section.append(status);
  return section;
}

function renderScenarioResult(outputState) {
  const result = outputState.result;
  const wrapper = element("div", "scenario-result");
  const meaning = element("section", "scenario-result__meaning");
  meaning.append(element("h4", "", "What this entity means here"),
    element("p", "", result.scenarioMeaning));
  wrapper.append(meaning);
  const examples = element("section", "scenario-result__examples");
  examples.append(element("h4", "", "Operationalization examples"));
  const grid = element("div", "operationalization-grid");
  result.operationalizationExamples.forEach((example, index) => {
    const card = element("article", "operationalization-card");
    card.append(element("p", "operationalization-card__number", "Example " + String(index + 1)),
      element("h5", "", example.title), element("h6", "", "Operationalization"),
      element("p", "", example.operationalization), element("h6", "", "What to look for"));
    const indicators = element("ul", "");
    example.whatToLookFor.forEach((indicator) => indicators.append(element("li", "", indicator)));
    card.append(indicators, element("h6", "", "Question to ask"),
      element("p", "operationalization-card__question", example.questionToAsk));
    grid.append(card);
  });
  examples.append(grid);
  wrapper.append(examples);
  const caveat = element("section", "scenario-result__caveat");
  caveat.append(element("h4", "", "Important caveat"), element("p", "", result.importantCaveat));
  wrapper.append(caveat);
  const sufficiency = element("section", "scenario-result__sufficiency");
  sufficiency.append(element("h4", "", "Input sufficiency"),
    element("p", "sufficiency-badge", result.inputSufficiency.replaceAll("_", " ")));
  if (result.clarificationQuestion && !outputState.clarificationSkipped) {
    const form = element("form", "clarification-form");
    form.dataset.clarificationForm = result.driverId;
    const label = element("label", "", result.clarificationQuestion);
    const input = document.createElement("textarea");
    input.name = "clarificationAnswer";
    input.rows = 2;
    input.maxLength = 400;
    input.required = true;
    label.append(input);
    const actions = element("div", "clarification-form__actions");
    const submit = element("button", "primary-button", "Answer and regenerate");
    submit.type = "submit";
    const skip = element("button", "text-button", "Skip and keep this analysis");
    skip.type = "button";
    skip.dataset.skipClarification = result.driverId;
    actions.append(submit, skip);
    form.append(label, actions);
    sufficiency.append(form);
  } else if (result.clarificationQuestion) {
    sufficiency.append(element("p", "clarification-skipped",
      "Clarification skipped; the general analysis is retained."));
  }
  wrapper.append(sufficiency);
  return wrapper;
}

function renderDriverDetail(driver) {
  const family = familyByIdentity.get(familyIdentityKey(driver.layer, driver.family));
  const fragment = document.createDocumentFragment();
  const header = element("header", "driver-detail__header driver-detail__header--public");
  header.append(createDriverBreadcrumbs(driver, family));
  header.append(element("span", "entity-type-badge", entityTypeLabel(driver)));
  const title = element("h2", "", driver.name);
  title.id = "detail-title";
  header.append(title);
  const aliases = (driver._displayAliases || driver.aliases || []).filter((alias) =>
    normalizeComparable(alias) !== normalizeComparable(driver.name));
  if (aliases.length) {
    const aliasLine = element("p", "driver-aliases");
    aliasLine.append(element("span", "", "Also known as "), document.createTextNode(aliases.join(" · ")));
    header.append(aliasLine);
  }
  fragment.append(header);
  [
    createDefinitionSection(driver), createGovernanceStatusSection(driver),
    createDerivationSection(driver), createInBriefSection(driver),
    createQuestionSection(driver), createHowItOperatesSection(driver),
    createContextSection(driver), createObservationSection(driver),
    createEvidenceSection(driver), createSourcesSection(driver),
    createScenarioSection(driver),
  ].filter(Boolean).forEach((section) => fragment.append(section));
  driverDetail.replaceChildren(fragment);
  document.title = driver.name + " | " + DEFAULT_DOCUMENT_TITLE;
}

function taxonomyUrl(parameters = {}) {
  const url = new URL(window.location.href);
  [DRIVER_QUERY_PARAMETER, FAMILY_QUERY_PARAMETER, VIEW_QUERY_PARAMETER, "source", "target"]
    .forEach((parameter) => url.searchParams.delete(parameter));
  if (parameters.familyId) url.searchParams.set(FAMILY_QUERY_PARAMETER, parameters.familyId);
  if (parameters.driverId) url.searchParams.set(DRIVER_QUERY_PARAMETER, parameters.driverId);
  if (parameters.view === "search") url.searchParams.set(VIEW_QUERY_PARAMETER, "search");
  url.hash = "";
  return url;
}

function writeHistory(action, state, url) {
  if (action === "push") history.pushState(state, "", url);
  else if (action === "replace") history.replaceState(state, "", url);
}

function currentBackgroundState() {
  if (activeMode === "search") return { view: "search" };
  if (selectedBrowseFamilyId) return { view: "family", familyId: selectedBrowseFamilyId };
  if (selectedBrowseLayer) return { view: "layer", layer: selectedBrowseLayer };
  return { view: "root" };
}

function showBrowseRoot(urlAction, focus) {
  hideDriverDialog();
  setMode("browse");
  selectedBrowseLayer = null;
  selectedBrowseFamilyId = null;
  renderBrowse();
  detailDrivers = drivers;
  document.title = DEFAULT_DOCUMENT_TITLE;
  writeHistory(urlAction, { view: "root" }, taxonomyUrl());
  if (focus) browseHeading.focus();
}

function showBrowseLayer(layer, urlAction, focus) {
  if (!hierarchy.has(layer)) return false;
  hideDriverDialog();
  setMode("browse");
  selectedBrowseLayer = layer;
  selectedBrowseFamilyId = null;
  renderBrowse();
  detailDrivers = drivers.filter((driver) => driver.layer === layer);
  document.title = layer + " | " + DEFAULT_DOCUMENT_TITLE;
  writeHistory(urlAction, { view: "layer", layer }, taxonomyUrl());
  if (focus) browseHeading.focus();
  return true;
}

function showFamily(familyId, urlAction, focus) {
  const family = familyById.get(familyId);
  if (!family) return false;
  hideDriverDialog();
  setMode("browse");
  selectedBrowseLayer = family.layer;
  selectedBrowseFamilyId = family.id;
  renderBrowse();
  detailDrivers = driversByFamilyId.get(family.id);
  document.title = family.name + " | " + DEFAULT_DOCUMENT_TITLE;
  writeHistory(urlAction, { view: "family", familyId }, taxonomyUrl({ familyId }));
  if (focus) browseHeading.focus();
  return true;
}

function showSearch(urlAction, focus) {
  hideDriverDialog();
  setMode("search");
  detailDrivers = filteredDrivers;
  document.title = "Search | " + DEFAULT_DOCUMENT_TITLE;
  writeHistory(urlAction, { view: "search" }, taxonomyUrl({ view: "search" }));
  if (focus) searchInput.focus();
}

function showDriverDialog() {
  if (driverDialog.open) return;
  if (typeof driverDialog.showModal === "function") driverDialog.showModal();
  else driverDialog.setAttribute("open", "");
}

function hideDriverDialog() {
  closeCodebookPopover(false);
  if (!driverDialog.open) return;
  if (typeof driverDialog.close === "function") driverDialog.close();
  else driverDialog.removeAttribute("open");
}

function updateDetailNavigation() {
  const index = detailDrivers.findIndex((driver) => driver.id === currentDriverId);
  const found = index !== -1;
  previousDriverButton.disabled = !found || index === 0;
  nextDriverButton.disabled = !found || index === detailDrivers.length - 1;
  detailPosition.textContent = found
    ? String(index + 1) + " of " + String(detailDrivers.length) : "Linked Entity";
}

function openDriver(driverId, urlAction, contextDrivers) {
  const driver = driverById.get(driverId);
  if (!driver) return false;
  if (contextDrivers) detailDrivers = contextDrivers;
  else if (!detailDrivers.length) detailDrivers = drivers;
  currentDriverId = driverId;
  renderDriverDetail(driver);
  updateDetailNavigation();
  copyLinkButton.textContent = "Copy entity link";
  copyStatus.textContent = "";
  showDriverDialog();
  if (urlAction === "push") {
    history.pushState({ view: "driver", driverId, fromExplorer: true,
      background: currentBackgroundState() }, "", taxonomyUrl({ driverId }));
    detailOpenedFromExplorer = true;
  } else if (urlAction === "replace") {
    history.replaceState({ view: "driver", driverId,
      fromExplorer: detailOpenedFromExplorer,
      background: history.state && history.state.background
        ? history.state.background : currentBackgroundState() }, "", taxonomyUrl({ driverId }));
  }
  return true;
}

function closeDriverDetail() {
  if (detailOpenedFromExplorer && new URL(window.location.href).searchParams.has(DRIVER_QUERY_PARAMETER)) {
    detailOpenedFromExplorer = false;
    history.back();
    return;
  }
  const background = history.state && history.state.background
    ? history.state.background : { view: "root" };
  if (background.view === "family") showFamily(background.familyId, "replace", true);
  else if (background.view === "layer") showBrowseLayer(background.layer, "replace", true);
  else if (background.view === "search") showSearch("replace", true);
  else showBrowseRoot("replace", true);
}

function moveWithinResults(offset) {
  const index = detailDrivers.findIndex((driver) => driver.id === currentDriverId);
  const destination = detailDrivers[index + offset];
  if (destination) { openDriver(destination.id, "replace"); driverDetail.scrollTop = 0; }
}

async function copyCurrentLink() {
  const url = taxonomyUrl({ driverId: currentDriverId }).toString();
  try {
    if (navigator.clipboard && window.isSecureContext) await navigator.clipboard.writeText(url);
    else {
      const temporary = element("textarea", "clipboard-fallback");
      temporary.value = url;
      temporary.setAttribute("readonly", "");
      document.body.append(temporary);
      temporary.select();
      document.execCommand("copy");
      temporary.remove();
    }
    copyLinkButton.textContent = "Link copied";
    copyStatus.textContent = "Entity link copied to clipboard.";
  } catch (_error) {
    copyLinkButton.textContent = "Copy failed";
    copyStatus.textContent = "The Entity link could not be copied.";
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
    detailDrivers = drivers.filter((driver) => driver.layer === background.layer);
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
  const requestedView = url.searchParams.get(VIEW_QUERY_PARAMETER);
  linkNotice.hidden = true;
  if (driverId) {
    const background = state && state.background ? state.background
      : familyId && familyById.has(familyId) ? { view: "family", familyId } : { view: "root" };
    restoreBackground(background);
    detailOpenedFromExplorer = Boolean(state && state.fromExplorer);
    if (!openDriver(driverId, null)) {
      linkNotice.textContent = "The linked Entity " + driverId + " was not found in this taxonomy.";
      linkNotice.hidden = false;
      hideDriverDialog();
    }
    return;
  }
  detailOpenedFromExplorer = false;
  currentDriverId = null;
  hideDriverDialog();
  if (familyId) {
    if (!showFamily(familyId, null, false)) {
      linkNotice.textContent = "The linked Family " + familyId + " was not found in this taxonomy.";
      linkNotice.hidden = false;
      showBrowseRoot(null, false);
    }
  } else if (state && state.view === "layer") showBrowseLayer(state.layer, null, false);
  else if (requestedView === "search" || state && state.view === "search") showSearch(null, false);
  else {
    showBrowseRoot(null, false);
    if (requestedView || url.searchParams.has("source") || url.searchParams.has("target")) {
      history.replaceState({ view: "root" }, "", taxonomyUrl());
    }
  }
}

function clearAllFilters() {
  searchInput.value = "";
  FACETS.forEach(({ field }) => facetSelections[field].clear());
  renderFacets();
  applyFilters();
}

function codebookEntryUrl(termId) {
  const url = new URL("./codebook/", window.location.href);
  url.searchParams.set("term", termId);
  url.hash = "term-" + termId;
  return url.toString();
}

function positionCodebookPopover() {
  if (!activeInfoButton || codebookPopover.hidden) return;
  const rect = activeInfoButton.getBoundingClientRect();
  const margin = 12;
  const width = Math.min(360, window.innerWidth - margin * 2);
  codebookPopover.style.width = width + "px";
  codebookPopover.style.left = Math.max(
    margin, Math.min(rect.left, window.innerWidth - width - margin)
  ) + "px";
  const measuredHeight = codebookPopover.offsetHeight || 220;
  const below = rect.bottom + 10;
  codebookPopover.style.top = (below + measuredHeight <= window.innerHeight - margin
    ? below : Math.max(margin, rect.top - measuredHeight - 10)) + "px";
}

function openCodebookPopover(button) {
  const entry = codebookById.get(button.dataset.codebookId);
  if (!entry) return;
  closeCodebookPopover(false);
  activeInfoButton = button;
  button.setAttribute("aria-expanded", "true");
  (button.closest("dialog") || document.body).append(codebookPopover);
  codebookPopoverTitle.textContent = entry.field;
  codebookPopoverDefinition.textContent = entry.definition;
  codebookPopoverLink.href = codebookEntryUrl(entry.id);
  codebookPopover.hidden = false;
  positionCodebookPopover();
  codebookPopoverClose.focus();
}

function closeCodebookPopover(returnFocus = true) {
  if (activeInfoButton) {
    activeInfoButton.setAttribute("aria-expanded", "false");
    if (returnFocus && activeInfoButton.isConnected) activeInfoButton.focus();
  }
  activeInfoButton = null;
  codebookPopover.hidden = true;
}

function readStoredScenario() {
  try {
    const raw = sessionStorage.getItem(SCENARIO_STORAGE_KEY);
    if (!raw) return null;
    const candidate = JSON.parse(raw);
    return validScenario(candidate) ? candidate : null;
  } catch (_error) { return null; }
}

function validScenario(candidate) {
  return candidate && ["actor", "behaviorObjective", "context"].every((field) =>
    typeof candidate[field] === "string" && candidate[field].trim());
}

function showScenarioDialog() {
  if (!SCENARIO_AVAILABLE) return;
  scenarioActor.value = activeScenario ? activeScenario.actor : "";
  scenarioBehavior.value = activeScenario ? activeScenario.behaviorObjective : "";
  scenarioContext.value = activeScenario ? activeScenario.context : "";
  if (typeof scenarioDialog.showModal === "function") scenarioDialog.showModal();
  else scenarioDialog.setAttribute("open", "");
  window.setTimeout(() => scenarioActor.focus(), 0);
}

function hideScenarioDialog() {
  if (!scenarioDialog.open) return;
  if (typeof scenarioDialog.close === "function") scenarioDialog.close();
  else scenarioDialog.removeAttribute("open");
}

function updateScenarioUi() {
  const active = Boolean(activeScenario);
  scenarioBanner.hidden = !active;
  scenarioEntryButton.disabled = !SCENARIO_AVAILABLE;
  scenarioComingSoon.hidden = SCENARIO_AVAILABLE;
  if (!SCENARIO_AVAILABLE) {
    scenarioEntryButton.textContent = "Apply to a scenario";
    scenarioEntryButton.setAttribute("aria-describedby", "scenario-coming-soon");
    if (currentDriverId && driverDialog.open) renderDriverDetail(driverById.get(currentDriverId));
    return;
  }
  scenarioEntryButton.removeAttribute("aria-describedby");
  if (active) {
    scenarioBannerActor.textContent = activeScenario.actor;
    scenarioBannerBehavior.textContent = activeScenario.behaviorObjective;
    scenarioBannerContext.textContent = activeScenario.context;
    scenarioEntryButton.textContent = "Edit scenario";
  } else scenarioEntryButton.textContent = "Apply to a scenario";
  if (currentDriverId && driverDialog.open) renderDriverDetail(driverById.get(currentDriverId));
}

function invalidatePendingScenarioRequest() {
  scenarioRevision += 1;
  if (activeScenarioRequest) activeScenarioRequest.controller.abort();
  activeScenarioRequest = null;
  pendingScenarioDriverId = null;
}

function saveScenarioFromForm() {
  if (!SCENARIO_AVAILABLE) return false;
  const candidate = {
    actor: scenarioActor.value.trim(),
    behaviorObjective: scenarioBehavior.value.trim(),
    context: scenarioContext.value.trim(),
  };
  if (!validScenario(candidate)) return false;
  invalidatePendingScenarioRequest();
  activeScenario = candidate;
  scenarioOutputs.clear();
  sessionStorage.setItem(SCENARIO_STORAGE_KEY, JSON.stringify(candidate));
  hideScenarioDialog();
  updateScenarioUi();
  return true;
}

function clearScenario() {
  invalidatePendingScenarioRequest();
  activeScenario = null;
  scenarioOutputs.clear();
  sessionStorage.removeItem(SCENARIO_STORAGE_KEY);
  scenarioForm.reset();
  hideScenarioDialog();
  updateScenarioUi();
  scenarioEntryButton.focus();
}

function scenarioRequestPayload(driver, clarificationAnswer = null, scenario = activeScenario) {
  const family = familyByIdentity.get(familyIdentityKey(driver.layer, driver.family));
  const plain = driver._plainLanguage;
  return {
    actor: scenario.actor,
    behaviorObjective: scenario.behaviorObjective,
    context: scenario.context,
    clarificationAnswer: clarificationAnswer || null,
    driver: {
      id: driver.id,
      entityType: driver.entityType,
      entitySubtype: driver.entitySubtype ?? null,
      name: driver.name,
      definition: driver.definition,
      plainLanguageExplanation: plain ? plain.plainLanguageExplanation : null,
      analyticQuestion: plain ? plain.analyticQuestion : null,
      whatThisDoesNotMean: plain ? plain.whatThisDoesNotMean : null,
      layer: driver.layer,
      family: driver.family,
      familyDefinition: family ? family.definition : null,
      familyIncludes: family ? family.includes : null,
      familyExclusions: family ? family.exclusions : null,
      mechanism: driver.mechanism,
      moderatorsBoundaryConditions: driver.moderatorsBoundaryConditions,
      indicators: driver.indicators,
      measurementAssessmentMethods: driver.measurementAssessmentMethods,
      observability: driver.observability,
      measurementCaveats: driver.measurementCaveats,
      dataType: driver.dataType,
      timeScaleOfChange: driver.timeScaleOfChange,
      onsetCausalLag: driver.onsetCausalLag,
      commonMisinterpretations: driver.commonMisinterpretations,
      evidenceNotes: driver.evidenceNotes,
      constituentSpecifications: driver.constituentSpecifications || [],
      derivationType: driver.derivationType ?? null,
      derivationLogic: driver.derivationLogic ?? null,
      scopeRequirements: driver.scopeRequirements ?? null,
      directManipulability: driver.directManipulability ?? null,
      recalculationBehavior: driver.recalculationBehavior ?? null,
      uncertaintyPropagation: driver.uncertaintyPropagation ?? null,
      compositeSpecification: driver.compositeSpecification ?? null,
      differenceSpecification: driver.differenceSpecification ?? null,
      networkMetricSpecification: driver.networkMetricSpecification ?? null,
      ratioSpecification: driver.ratioSpecification ?? null,
      temporalSpecification: driver.temporalSpecification ?? null,
    },
  };
}

function validateScenarioResponse(candidate, driverId) {
  if (!sameKeys(candidate, SCENARIO_RESPONSE_KEYS)) {
    throw new Error("The service returned an unexpected response shape.");
  }
  if (candidate.driverId !== driverId) throw new Error("The service response does not match this Entity.");
  ["scenarioMeaning", "importantCaveat"].forEach((field) => {
    if (typeof candidate[field] !== "string" || !candidate[field].trim()) {
      throw new Error("The service response is missing " + field + ".");
    }
  });
  if (!Array.isArray(candidate.operationalizationExamples) ||
      candidate.operationalizationExamples.length !== 3) {
    throw new Error("The service must return exactly three operationalization examples.");
  }
  candidate.operationalizationExamples.forEach((example) => {
    if (!sameKeys(example, SCENARIO_EXAMPLE_KEYS)) {
      throw new Error("An operationalization example has an unexpected shape.");
    }
    ["title", "operationalization", "questionToAsk"].forEach((field) => {
      if (typeof example[field] !== "string" || !example[field].trim()) {
        throw new Error("An operationalization example is incomplete.");
      }
    });
    if (!Array.isArray(example.whatToLookFor) || example.whatToLookFor.length < 2 ||
        example.whatToLookFor.length > 4 || example.whatToLookFor.some((item) =>
          typeof item !== "string" || !item.trim())) {
      throw new Error("Each example must provide two to four observable items.");
    }
  });
  const allowed = ["SUFFICIENT", "PARTIALLY_SUFFICIENT", "INSUFFICIENT"];
  if (!allowed.includes(candidate.inputSufficiency)) {
    throw new Error("The service returned an invalid sufficiency value.");
  }
  if (candidate.inputSufficiency === "SUFFICIENT") {
    if (candidate.clarificationQuestion !== null) {
      throw new Error("A sufficient response cannot request clarification.");
    }
  } else if (typeof candidate.clarificationQuestion !== "string" ||
      !candidate.clarificationQuestion.trim()) {
    throw new Error("The service must return exactly one clarification question when input is incomplete.");
  }
  return candidate;
}

async function requestOperationalization(driver, clarificationAnswer = null) {
  if (!activeScenario || !SCENARIO_AVAILABLE || pendingScenarioDriverId !== null) return;
  const requestRevision = scenarioRevision;
  const scenarioSnapshot = Object.assign({}, activeScenario);
  pendingScenarioDriverId = driver.id;
  const existing = scenarioOutputs.get(driver.id);
  scenarioOutputs.set(driver.id, { result: existing && existing.result || null, error: null });
  renderDriverDetail(driver);
  const controller = new AbortController();
  const requestToken = { controller, driverId: driver.id, revision: requestRevision };
  activeScenarioRequest = requestToken;
  const timer = window.setTimeout(() => controller.abort(), 35000);
  try {
    const response = await fetch(CONFIG.scenarioApiUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(scenarioRequestPayload(driver, clarificationAnswer, scenarioSnapshot)),
      signal: controller.signal,
    });
    let body = null;
    try { body = await response.json(); } catch (_error) { body = null; }
    if (!response.ok) {
      throw new Error(body && typeof body.error === "string"
        ? body.error : "Scenario operationalization is temporarily unavailable.");
    }
    if (activeScenarioRequest !== requestToken || scenarioRevision !== requestRevision) return;
    scenarioOutputs.set(driver.id, {
      result: validateScenarioResponse(body, driver.id),
      clarificationSkipped: false,
      error: null,
    });
  } catch (error) {
    if (activeScenarioRequest !== requestToken || scenarioRevision !== requestRevision) return;
    const message = error && error.name === "AbortError"
      ? "The scenario request timed out. Please try again."
      : error && error.message ? error.message
        : "Scenario operationalization is temporarily unavailable.";
    const prior = scenarioOutputs.get(driver.id);
    scenarioOutputs.set(driver.id, {
      result: prior && prior.result || null,
      clarificationSkipped: false,
      error: message,
    });
  } finally {
    window.clearTimeout(timer);
    if (activeScenarioRequest !== requestToken || scenarioRevision !== requestRevision) return;
    activeScenarioRequest = null;
    pendingScenarioDriverId = null;
    if (currentDriverId === driver.id) {
      renderDriverDetail(driver);
      const section = driverDetail.querySelector(
        '[data-scenario-section="' + CSS.escape(driver.id) + '"]'
      );
      if (section) section.scrollIntoView({ block: "start" });
    }
  }
}

async function fetchJson(url, label) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(label + " request failed with status " + String(response.status) + ".");
  return response.json();
}

async function loadTaxonomy() {
  try {
    const [driverData, familyEnvelope, plainEnvelope, aliasEnvelope] = await Promise.all([
      fetchJson("../data/entities.json", "Entity data"),
      fetchJson("../data/families.json", "Family data"),
      fetchJson("../data/plain_language.json", "Public explanation data"),
      fetchJson("../data/aliases.json", "Alias data"),
    ]);
    validateTaxonomyData(driverData, familyEnvelope);
    plainLanguageByDriverId = validatePlainLanguageData(driverData, plainEnvelope);
    const aliasesByEntityId = validateAliases(driverData, aliasEnvelope);
    const supplemental = await Promise.allSettled([
      fetchJson("../data/codebook.json", "Codebook data"),
      fetchJson("../data/sources.json", "Source data"),
    ]);
    if (supplemental[0].status === "fulfilled") {
      codebookById = validateCodebook(supplemental[0].value);
    } else console.warn("Codebook help is unavailable:", supplemental[0].reason);
    if (supplemental[1].status === "fulfilled") {
      sourceById = validateSources(supplemental[1].value);
    } else console.warn("Governed source links are unavailable:", supplemental[1].reason);
    drivers = driverData.map((driver) => {
      const enriched = Object.assign({}, driver, {
        _plainLanguage: plainLanguageByDriverId.get(driver.id) || null,
        _searchAliases: aliasesByEntityId.get(driver.id).search,
        _displayAliases: aliasesByEntityId.get(driver.id).display,
      });
      enriched._searchFields = driverSearchFields(enriched);
      return enriched;
    });
    families = familyEnvelope.families;
    buildIndexes();
    totalDriverCount.textContent = drivers.filter((entity) => entity.entityType === "DRIVER").length.toLocaleString();
    totalRdsCount.textContent = drivers.filter((entity) => entity.entityType === "RELATIONAL_DERIVED_STATE").length.toLocaleString();
    totalEntityCount.textContent = drivers.length.toLocaleString();
    totalFamilyCount.textContent = families.length.toLocaleString();
    searchInput.disabled = false;
    renderFacets();
    applyFilters();
    updateScenarioUi();
    const url = new URL(window.location.href);
    const initialDriverId = url.searchParams.get(DRIVER_QUERY_PARAMETER);
    const initialFamilyId = url.searchParams.get(FAMILY_QUERY_PARAMETER);
    const requestedView = url.searchParams.get(VIEW_QUERY_PARAMETER);
    const initialState = initialDriverId
      ? { view: "driver", driverId: initialDriverId, fromExplorer: false,
          background: initialFamilyId ? { view: "family", familyId: initialFamilyId } : { view: "root" } }
      : initialFamilyId ? { view: "family", familyId: initialFamilyId }
        : requestedView === "search" ? { view: "search" } : { view: "root" };
    history.replaceState(initialState, "", window.location.href);
    applyLocationState(initialState);
  } catch (error) {
    console.error("Unable to load PSYWERX taxonomy:", error);
    browseSummary.textContent = "Taxonomy unavailable";
    resultSummary.textContent = "Taxonomy unavailable";
    browseContent.replaceChildren();
    driverList.replaceChildren();
    loadError.querySelector("p").textContent =
      "The required Entity, Family, and public explanation datasets could not be loaded or did not agree. " +
      "Check the browser console, then reload the page. For local preview, use an HTTP server.";
    loadError.hidden = false;
  }
}

browseModeButton.addEventListener("click", () => {
  if (activeMode === "browse") browseHeading.focus();
  else if (selectedBrowseFamilyId) showFamily(selectedBrowseFamilyId, "push", true);
  else if (selectedBrowseLayer) showBrowseLayer(selectedBrowseLayer, "push", true);
  else showBrowseRoot("push", true);
});
searchModeButton.addEventListener("click", () => {
  if (activeMode === "search") searchInput.focus(); else showSearch("push", true);
});
browseContent.addEventListener("click", (event) => {
  const layerButton = event.target.closest("[data-browse-layer]");
  const familyButton = event.target.closest("[data-browse-family]");
  const driverButton = event.target.closest("[data-driver-id]");
  if (layerButton) showBrowseLayer(layerButton.dataset.browseLayer, "push", true);
  else if (familyButton) showFamily(familyButton.dataset.browseFamily, "push", true);
  else if (driverButton) {
    openDriver(driverButton.dataset.driverId, "push", driversByFamilyId.get(selectedBrowseFamilyId));
  }
});
browseBreadcrumbs.addEventListener("click", (event) => {
  const button = event.target.closest("[data-browse-level]");
  if (!button) return;
  if (button.dataset.browseLevel === "root") showBrowseRoot("push", true);
  else showBrowseLayer(selectedBrowseLayer, "push", true);
});
searchInput.addEventListener("input", () => {
  window.clearTimeout(searchTimer);
  searchTimer = window.setTimeout(() => applyFilters(), 80);
});
facetFilters.addEventListener("change", (event) => {
  const checkbox = event.target.closest("[data-facet-field]");
  if (!checkbox) return;
  const selected = facetSelections[checkbox.dataset.facetField];
  if (checkbox.checked) selected.add(checkbox.value); else selected.delete(checkbox.value);
  if (checkbox.dataset.facetField === "layer") syncAvailableFamilies();
  applyFilters();
});
activeFilters.addEventListener("click", (event) => {
  const button = event.target.closest("[data-clear-facet]");
  if (!button) return;
  if (button.dataset.clearFacet === "search") searchInput.value = "";
  else {
    facetSelections[button.dataset.clearFacet].delete(button.dataset.clearValue);
    if (button.dataset.clearFacet === "layer") syncAvailableFamilies();
    const checkbox = [...facetFilters.querySelectorAll("[data-facet-field]")].find((input) =>
      input.dataset.facetField === button.dataset.clearFacet && input.value === button.dataset.clearValue);
    if (checkbox) checkbox.checked = false;
  }
  applyFilters();
});
clearFiltersButton.addEventListener("click", () => { clearAllFilters(); searchInput.focus(); });
driverList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-driver-id]");
  if (button) openDriver(button.dataset.driverId, "push", filteredDrivers);
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
  const layerButton = event.target.closest("[data-driver-layer]");
  const familyButton = event.target.closest("[data-driver-family]");
  const operationalizeButton = event.target.closest("[data-operationalize-driver]");
  const skipButton = event.target.closest("[data-skip-clarification]");
  if (layerButton) showBrowseLayer(layerButton.dataset.driverLayer, "push", true);
  else if (familyButton) showFamily(familyButton.dataset.driverFamily, "push", true);
  else if (operationalizeButton) {
    requestOperationalization(driverById.get(operationalizeButton.dataset.operationalizeDriver));
  } else if (skipButton) {
    const state = scenarioOutputs.get(skipButton.dataset.skipClarification);
    if (state) {
      state.clarificationSkipped = true;
      renderDriverDetail(driverById.get(skipButton.dataset.skipClarification));
    }
  }
});
driverDetail.addEventListener("submit", (event) => {
  const form = event.target.closest("[data-clarification-form]");
  if (!form) return;
  event.preventDefault();
  const answer = new FormData(form).get("clarificationAnswer");
  requestOperationalization(driverById.get(form.dataset.clarificationForm), String(answer || "").trim());
});
driverDialog.addEventListener("cancel", (event) => {
  event.preventDefault();
  if (!codebookPopover.hidden) closeCodebookPopover(); else closeDriverDetail();
});
driverDialog.addEventListener("click", (event) => {
  if (event.target === driverDialog) closeDriverDetail();
});

document.addEventListener("click", (event) => {
  const infoButton = event.target.closest("[data-codebook-id]");
  if (infoButton) {
    event.preventDefault();
    if (activeInfoButton === infoButton && !codebookPopover.hidden) closeCodebookPopover();
    else openCodebookPopover(infoButton);
    return;
  }
  if (!codebookPopover.hidden && !codebookPopover.contains(event.target)) {
    closeCodebookPopover(false);
  }
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !codebookPopover.hidden) {
    event.preventDefault();
    event.stopPropagation();
    closeCodebookPopover();
  }
});
codebookPopoverClose.addEventListener("click", () => closeCodebookPopover());
window.addEventListener("resize", positionCodebookPopover);

scenarioEntryButton.addEventListener("click", showScenarioDialog);
scenarioEditButton.addEventListener("click", showScenarioDialog);
scenarioClearButton.addEventListener("click", clearScenario);
scenarioDialogClose.addEventListener("click", hideScenarioDialog);
scenarioFormClear.addEventListener("click", () => { scenarioForm.reset(); scenarioActor.focus(); });
scenarioForm.addEventListener("submit", (event) => {
  event.preventDefault();
  if (scenarioForm.reportValidity()) saveScenarioFromForm();
});
scenarioForm.addEventListener("click", (event) => {
  const exampleButton = event.target.closest("[data-scenario-example]");
  if (!exampleButton) return;
  const example = SCENARIO_EXAMPLES[exampleButton.dataset.scenarioExample];
  scenarioActor.value = example.actor;
  scenarioBehavior.value = example.behaviorObjective;
  scenarioContext.value = example.context;
  scenarioActor.focus();
});
scenarioDialog.addEventListener("cancel", (event) => { event.preventDefault(); hideScenarioDialog(); });
scenarioDialog.addEventListener("click", (event) => {
  if (event.target === scenarioDialog) hideScenarioDialog();
});

window.addEventListener("popstate", (event) => applyLocationState(event.state));

updateScenarioUi();
loadTaxonomy();
