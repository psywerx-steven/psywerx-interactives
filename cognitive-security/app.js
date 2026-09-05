"use strict";

const DATA_BASE = "../data/cognitive-security/";
const DISCOVERY_BASE = "../data/cognitive-security-discovery/";
const ICON_BASE = "./assets/entry-icons/";
const DISCOVERY_DATA_FILES = Object.freeze([
  "episode_metadata.json",
  "episode_discovery.json",
  "topic_episode_index.json",
  "similarity_data.json",
  "presentation_copy.json",
]);
const EAGER_DISCOVERY_FILES = Object.freeze([
  "episode_metadata.json", "episode_discovery.json", "topic_episode_index.json",
]);
const PUBLIC_DATA_FILES = Object.freeze([
  "manifest.json",
  "coverage.json",
  "categories.json",
  "clusters.json",
  "cluster_summaries.json",
  "families.json",
  "themes.json",
  "tensions.json",
  "narratives.json",
  "category_findings.json",
  "scenarios.json",
  "episodes.json",
  "episode_summaries.json",
  "relationships.json",
  "relationship_semantics.json",
  "provenance.json",
  "heatmap.json",
  "qa_report.json",
]);
const LAZY_PUBLIC_FILES = Object.freeze(["relationships.json", "provenance.json"]);
const EAGER_PUBLIC_FILES = Object.freeze(
  PUBLIC_DATA_FILES.filter(function (fileName) {
    return fileName !== "manifest.json" && !LAZY_PUBLIC_FILES.includes(fileName);
  })
);
const EXPECTED_COUNTS = Object.freeze({
  category: 7,
  family: 50,
  cluster: 127,
  clusterSummary: 127,
  theme: 11,
  tension: 20,
  narrative: 5,
  categoryFinding: 64,
  scenario: 6,
  episode: 242,
  heatmapCell: 77,
});
const MANIFEST_COUNT_KEYS = Object.freeze({
  category: "categoryCount",
  family: "familyCount",
  cluster: "clusterCount",
  clusterSummary: "clusterSummaryCount",
  theme: "themeCount",
  tension: "tensionCount",
  narrative: "narrativeCount",
  categoryFinding: "categoryFindingCount",
  scenario: "scenarioCount",
  episode: "publicReleaseCount",
  heatmapCell: "heatmapCellCount",
});
const SUPPORT_INTERPRETATION = "Corpus support reflects recurrence and breadth within this practitioner discourse corpus. It does not indicate scientific validity, consensus, importance, prevalence, or real-world effect size.";
const SC04_PUBLIC_NOTICE = "Legal, privacy, civil-liberties, ethics, consent, and affected-community reviews are required before any operational use. Response options are analytical possibilities, not validated recommendations. This scenario is not a recommendation to deploy identity-linked monitoring.";

const DEEP_LINK_ENTITY_TYPES = Object.freeze([
  "category", "family", "cluster", "theme", "tension", "narrative",
  "scenario", "episode",
]);
const DATA_ENTITY_TYPES = Object.freeze([
  "category", "family", "cluster", "theme", "tension", "narrative",
  "categoryFinding", "scenario", "episode",
]);
const ENTITY_ROUTES = Object.freeze({
  category: "category",
  family: "family",
  cluster: "cluster",
  theme: "theme",
  tension: "tension",
  narrative: "narrative",
  scenario: "scenario",
  episode: "episode",
});
const ROUTE_ENTITIES = Object.freeze(
  Object.fromEntries(Object.entries(ENTITY_ROUTES).map(function (entry) {
    return [entry[1], entry[0]];
  }))
);
const PRIMARY_VIEWS = Object.freeze([
  "start", "families", "themes", "tensions", "narratives", "scenarios",
  "episodes", "search", "methodology",
]);
const ENTITY_INDEX_VIEWS = Object.freeze({
  category: "families",
  family: "families",
  cluster: "families",
  theme: "themes",
  tension: "tensions",
  narrative: "narratives",
  scenario: "scenarios",
  episode: "episodes",
});
const ENTITY_LABELS = Object.freeze({
  category: "Category",
  family: "Subcategory",
  cluster: "Topic",
  theme: "Theme",
  tension: "Tension",
  narrative: "Narrative",
  categoryFinding: "Finding or open question",
  scenario: "Scenario",
  episode: "Episode",
});
const ENTITY_PLURAL_LABELS = Object.freeze({
  category: "Categories",
  family: "Subcategories",
  cluster: "Topics",
  theme: "Themes",
  tension: "Tensions",
  narrative: "Narratives",
  scenario: "Scenarios",
  episode: "Episodes",
});
const SEARCH_ENTITY_TYPES = Object.freeze(DEEP_LINK_ENTITY_TYPES.slice());
const ID_FIELDS = Object.freeze({
  category: "categoryId",
  family: "familyId",
  cluster: "clusterId",
  theme: "themeId",
  tension: "tensionId",
  narrative: "narrativeId",
  categoryFinding: "findingId",
  scenario: "scenarioId",
  episode: "episodeId",
});
const RECORD_FILES = Object.freeze({
  category: "categories.json",
  family: "families.json",
  cluster: "clusters.json",
  theme: "themes.json",
  tension: "tensions.json",
  narrative: "narratives.json",
  categoryFinding: "category_findings.json",
  scenario: "scenarios.json",
  episode: "episodes.json",
});
const ROUTE_PARAMETER_ORDER = Object.freeze([
  "view", "id", "q", "type", "category", "family", "theme", "scenario",
  "tensionType", "support", "display", "path", "range", "sort", "number",
  "position", "topic",
]);
const LEGACY_VIEW_ALIASES = Object.freeze({
  overview: "start",
  browse: "families",
  "meta-clusters": "families",
  "meta-narratives": "narratives",
});
const LEGACY_DETAIL_FALLBACKS = Object.freeze({
  "meta-cluster": "families",
  "meta-narrative": "narratives",
});

// Keys are SHA-256(view + "\u0000" + id). The table contains only governed,
// one-successor redirects. Split, merged, or unresolved records deliberately
// fall through to the generic reorganized-architecture destination.
const LEGACY_SUCCESSOR_HASHES = Object.freeze({
  "fdaed2149df9199a363ae44a5557da400a5fe906dddd28bec708db57bb2c40f6": Object.freeze({ view: "narrative", id: "CN-01" }),
  "b4d2cde63ceb93ade94039dcdc9ac36a3a60985d5b194b84c27ddbb08e30d347": Object.freeze({ view: "narrative", id: "CN-02" }),
  "f64770a9afb20376f350a9cd3b94e73095a9837bbfec323da77f1e35d82be4a0": Object.freeze({ view: "narrative", id: "CN-02" }),
  "12a67c23e1f535487fe778f419ba5cfd17cc0ddc9775c913b5a1d67ad1c4ec13": Object.freeze({ view: "narrative", id: "CN-03" }),
  "3929a92e1c8018f15068663b925c42fe618e131201e44e04a0815388630ebdee": Object.freeze({ view: "narrative", id: "CN-04" }),
  "7b502fe23799ef036d89a82bc9150122ae216592e702f61d91496c10103908d9": Object.freeze({ view: "narrative", id: "CN-03" }),
  "7b60192d86ff03bd5f5c19fdd93a9d354bba344a879e2312a68b05164a17211b": Object.freeze({ view: "narrative", id: "CN-05" }),
  "d9681e74ae655cf3bb8cf4f11b33739e5ab995bbd5c138ba532200eb533dda02": Object.freeze({ view: "scenario", id: "SC-01" }),
  "4d9b5ff18edc9d211276805885b2fab7652e7ffa33025084e5db8bc89798d629": Object.freeze({ view: "scenario", id: "SC-02" }),
  "a56491d05f2f0c1e239b0aafe5b32f23a5f61cd739fed50caec8c9e7e262497a": Object.freeze({ view: "scenario", id: "SC-03" }),
  "1390836475b7aa3f3c37c65fdb4d1795c875327e324c4dc5526d7170709a28d9": Object.freeze({ view: "scenario", id: "SC-04" }),
  "9e6dfc2311c64d369e6496a4f9ab1e0d8f488f23f5c6b3efb4d88ca4fe76d3df": Object.freeze({ view: "scenario", id: "SC-05" }),
  "9044203db704b946363a514ffc21d69e0d0db8ff1abdad14b058f729f61c09bd": Object.freeze({ view: "scenario", id: "SC-06" }),
  "6ed4da4f1557cdbec77e8cf7772ddfdfa8d91e9c3285dd563db2a31a4be6084b": Object.freeze({ view: "tension", id: "CT-001" }),
  "af361f76a6c3435ef492bd18003f5f87bd3540bbdb6d0bf24b245676eb8a2938": Object.freeze({ view: "tension", id: "CT-008" }),
  "473cc1ff77a9ec69de01ee06d43b6d08b8e2a68fcac3009954425fc010f96de6": Object.freeze({ view: "tension", id: "CT-001" }),
  "52e0247b8537e4740916269c9fec29b2bd513fbffc0adacc7e48bf675588cea9": Object.freeze({ view: "tension", id: "CT-006" }),
  "129be59e049067328ec217251a1cc65a4f46bfb699adbf71de9f8bad4f9869b6": Object.freeze({ view: "tension", id: "CT-003" }),
  "b97ec52c024d3eb631558844a0fc19ffc58a01d85db62bdd38cb27d9d8008470": Object.freeze({ view: "tension", id: "CT-009" }),
  "c5541243a420b4db832be1aafa8342e6676a870bc0eef7cfe289fa02b3cf21d1": Object.freeze({ view: "tension", id: "CT-010" }),
  "6cf9d704e605c58b53488bc5a8a587989172d561e4b60547e5ee58a1707e2624": Object.freeze({ view: "tension", id: "CT-004" }),
  "a222a5e0dd96e2967a7d7391b7069c69bd417d1f3e512a1fc64d5dc774453ef0": Object.freeze({ view: "tension", id: "CT-011" }),
  "b949b8854ceb6c467d021079dd2adbd42e912398fa2369a04dd8475b8362b3bd": Object.freeze({ view: "tension", id: "CT-012" }),
  "0ef72b2d1d806f7632f644f338ce1208f92b8681c29d63740bc7167820ec99c8": Object.freeze({ view: "tension", id: "CT-007" }),
  "1f6824899d6e9571efa9e7bf16a24b6df6e252fbca35f8e34d7b9a02bdf21ee2": Object.freeze({ view: "tension", id: "CT-006" }),
  "d58a17b4fcce0fd07ceab1a0f8a548b7f972ad1f7f0f7ad6043b737fb535cbc7": Object.freeze({ view: "tension", id: "CT-005" }),
  "89b50357be054d14133c94b5cc3dbdc5a697760e1a3fb21fa86660972390b19c": Object.freeze({ view: "tension", id: "CT-001" }),
  "3783707088f3fb8d1f30e8285741811f36391ffc8678925c66ea6f2031d3feed": Object.freeze({ view: "tension", id: "CT-013" }),
  "deeeaa32f5826c127f90192b38b57422b027c4b8d2fc0aad085c3ee652e82802": Object.freeze({ view: "tension", id: "CT-014" }),
  "1d038209ecad6871ea1e0a6f4fa082a2669a8d5c726fca68c8a722fdff0c0c7b": Object.freeze({ view: "tension", id: "CT-015" }),
  "9de77d3f476d375ff4dd4d321760ef2a4cacd03f72573a6103f6ee527c85b88d": Object.freeze({ view: "tension", id: "CT-016" }),
  "039321dd919eb68b28681b33761eb6f1f13ecc0154516937a262549d936b5436": Object.freeze({ view: "tension", id: "CT-006" }),
  "a2c02177d723d65a493868e76bb8076df7ae8fe5c1a8dadce4038013c43ab5b1": Object.freeze({ view: "tension", id: "CT-006" }),
  "ef3add4d05a0ae3cb97ea9f5be5cfa7089789e222ab91cae17aa955d7bcdb507": Object.freeze({ view: "tension", id: "CT-017" }),
  "e31eb18dcba1d83f9e5f236311d781b75b756353f58e88998df3f635c1a4cdcb": Object.freeze({ view: "tension", id: "CT-018" }),
  "c45ff8303ad344f2dcde78c57e79fa052ceb1c418e81e89113d8a60b650eefac": Object.freeze({ view: "tension", id: "CT-006" }),
  "9c8ec827a7da1ed61f2c17bd31583c0c7f93f4c957c56966051c14fadf1bc8a0": Object.freeze({ view: "tension", id: "CT-006" }),
  "2db8eb54cd3e2d1c56b3826685998ddc3a79e93931195b69b3e9af92c3cbf0ae": Object.freeze({ view: "tension", id: "CT-019" }),
  "0bb319064b152eb79a88509a516d4536a4bd3462873691fcf370f7a2959856d4": Object.freeze({ view: "tension", id: "CT-020" }),
  "6195b528e032d73ee28104bc2fdf4a44c154252ab6ad945c07b65829a4282c4e": Object.freeze({ view: "theme", id: "TH-01" }),
  "b8dd85079dd458c0c4c5588e3a3dd3ca8a94ceae52906ca9469804045576af6a": Object.freeze({ view: "theme", id: "TH-02" }),
  "bc0ca59646073483a1cd129acd01293b4feaa6d0f0151e11ead7eb82543d3a39": Object.freeze({ view: "theme", id: "TH-03" }),
  "aef7b61f3a1be14233abaf555937143e5a30ce372ba5f7632518730e0c2a0e55": Object.freeze({ view: "theme", id: "TH-04" }),
  "2ac61d32e09233e7203d60cfc6c99744fc2209f881ae66dd5f1c53f02c85fba9": Object.freeze({ view: "theme", id: "TH-05" }),
  "47064f39d747a69d4efe42c53a68533c65b94ac8739803f50323422c6d0fa18c": Object.freeze({ view: "theme", id: "TH-06" }),
  "5853c40d5ace61c82d3870b988e635d678af34ee10380ae9a49a7e4dc0a6ba60": Object.freeze({ view: "theme", id: "TH-07" }),
  "116032415a82d5112ae027d7020dab1d62cda0a1abc7e77a187dfece6ab65ad4": Object.freeze({ view: "theme", id: "TH-08" }),
  "0abc52327707b8d09f0282275dc506a1d4594f4b8c85f720c3bf17da5809163e": Object.freeze({ view: "theme", id: "TH-09" }),
  "75e5b4ca540e741b4be0cf018049bd229da7665fe4f82363f70d99eed89a16a2": Object.freeze({ view: "theme", id: "TH-10" }),
  "277051c492668a3decbfe4777277a3ec5d82738b433e6a58e262e798fe0cfc55": Object.freeze({ view: "theme", id: "TH-11" }),
  "2f78c76fc5094a663de560fee920f552958fa0efe549ebc9ae8183f6d7695d35": Object.freeze({ view: "family", id: "TTP-F01" }),
  "0575e7dfe3c65fe8b87b953fc230c665e87563becdefe3454d188ecd65d4abfb": Object.freeze({ view: "family", id: "TTP-F03" }),
  "e7725fa4e372a61a215ca40c2986e42e45d3432d4d3d1bd334a41a20f7432395": Object.freeze({ view: "family", id: "TTP-F04" }),
  "94e07e07b4f74747ecd73b966446a99d7e6f29d676fbd7a3de6eddddd218e8a4": Object.freeze({ view: "family", id: "ORG-F01" }),
  "91ca6508782e61506855973559c1277fb0fe7353ea3d4642b5133823e6ab54d8": Object.freeze({ view: "family", id: "ORG-F04" }),
  "595206b485a1be6326682c306730d5ca3824a648ff98a05226dfa8094b301e4c": Object.freeze({ view: "family", id: "ORG-F05" }),
  "a4944eaffc29f724a1b79af1aa8b77fb99ab56fd2b1000e74eecad9d1197da56": Object.freeze({ view: "family", id: "ORG-F06" }),
  "576856746f5d7052ddcdb30c0013c2248ba28215e7065e08a0791107831b459a": Object.freeze({ view: "family", id: "CRB-F06" }),
  "91123f9d6d3a8dd6f6b03f9f5416af5bcd25f53a1a4dcc2301405e5e1dc991d4": Object.freeze({ view: "family", id: "CRB-F07" }),
  "5c3e3fa6efde7fbc7096deacf9dec2b4f7ae6377c354bc5bc1067228ef29984b": Object.freeze({ view: "family", id: "KCF-F07" }),
  "6f13c073e9165a2e26226c1b7a1587f5073a53ce581d896228b5361aed93192c": Object.freeze({ view: "family", id: "KEH-F03" }),
  "4a425bfd11e5a95bbcbe0bf50c5fe71a36afff4b29f24981839d18cfafc334cf": Object.freeze({ view: "family", id: "KEH-F05" }),
  "6250079c550f8a6bbae80cb54525e6b5cc7d9320e6b4c026c4257ca8fe082f69": Object.freeze({ view: "family", id: "KEH-F06" }),
  "ca64a350d9b2be3db13fc0e69d356440f0371990799703406e7884d1fb3e85bb": Object.freeze({ view: "family", id: "FTP-F02" }),
  "ea74fb707ab4c7b80692c267f6a7fbdbbd9f48de98d54a344150788531f0137e": Object.freeze({ view: "family", id: "OPP-F03" }),
  "e847af7634f2d6c2198975f2de65d460395771fcfbf791769a62f33aab62600a": Object.freeze({ view: "family", id: "OPP-F06" }),
  "abee22bd2963a44d76b273af0784f9c639d0ad89bafb2d31434e14121bc72e4e": Object.freeze({ view: "family", id: "OPP-F07" }),
  "3b5d7381d4b426c0e580c0aec2b37a95cf7a6ac61774457a05fb3a4750500cee": Object.freeze({ view: "family", id: "OPP-F08" }),
});

const FORBIDDEN_PUBLIC_RECORD_KEYS = new Set([
  "historicalThemeIds", "historicalTensionIds", "historicalNarrativeIds",
  "historicalScenarioId", "historicalMetaClusterIds", "sourceCandidateIds",
  "supportingCanonicalContentUnits", "reviewFlags", "reviewRequired",
  "evidenceSelection", "internalAnalyticalRole", "adjudicationStatus",
  "adjudicationConfidence", "adjudicationDecision", "adjudicationRationale",
  "privateRepresentativeItemIds", "itemIds", "contentUnitIds",
]);

const state = {
  data: new Map(),
  records: {},
  maps: {},
  manifestFiles: new Set(),
  searchDocuments: [],
  relationshipAdjacency: new Map(),
  relationshipSemantics: new Map(),
  provenanceAdjacency: new Map(),
  lazyPromises: new Map(),
  discoveryData: new Map(),
  discoveryManifestFiles: new Set(),
  discoveryPromises: new Map(),
  iconRegistry: new Map(),
  discoveryMethod: null,
  similarityMethod: null,
  initialized: false,
  renderToken: 0,
};

const $ = function (selector) { return document.querySelector(selector); };
const globalSearchForm = $("#global-search-form");
const globalSearchInput = $("#global-search-input");
const viewNavigation = $("#view-navigation");
const landingHero = $("#landing-hero");
const viewHeader = $("#view-header");
const viewToolbar = $("#view-toolbar");
const appStatus = $("#app-status");
const loadError = $("#load-error");
const loadErrorMessage = $("#load-error-message");
const loadingState = $("#loading-state");
const emptyState = $("#empty-state");
const emptyStateTitle = $("#empty-state-title");
const emptyStateMessage = $("#empty-state-message");
const linkNotice = $("#link-notice");
const breadcrumbs = $("#view-breadcrumbs");
const viewKicker = $("#view-kicker");
const viewTitle = $("#view-title");
const viewDescription = $("#view-description");
const viewActions = $("#view-actions");
const viewSummary = $("#view-summary");
const viewContent = $("#view-content");
const searchControls = $("#search-controls");
const searchForm = $("#search-form");
const searchInput = $("#search-input");
const searchEntityType = $("#search-entity-type");
const searchCategory = $("#search-category");
const searchFamily = $("#search-family");
const searchCluster = $("#search-cluster");
const searchClear = $("#search-clear");
const searchActiveFilters = $("#search-active-filters");

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function asArray(value) {
  if (Array.isArray(value)) return value;
  return value === null || value === undefined || value === "" ? [] : [value];
}

function hasValue(value) {
  return value !== null && value !== undefined && String(value).trim() !== "";
}

function firstValue(record, names, fallback) {
  for (const name of names) {
    if (record && hasValue(record[name])) return record[name];
  }
  return fallback === undefined ? "" : fallback;
}

function flattenText(value) {
  if (!hasValue(value)) return [];
  if (Array.isArray(value)) return value.flatMap(flattenText);
  if (isObject(value)) return Object.values(value).flatMap(flattenText);
  return [String(value)];
}

function normalizeText(value) {
  return String(value || "").normalize("NFKD").replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase().replace(/\s+/g, " ").trim();
}

function formatNumber(value) {
  const number = Number(value);
  return Number.isFinite(number) ? new Intl.NumberFormat("en-US").format(number) : "—";
}

function formatPercent(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) return "—";
  const normalized = Math.abs(number) <= 1 ? number * 100 : number;
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 }).format(normalized) + "%";
}

function truncate(value, maximum) {
  const text = String(value || "").trim();
  if (text.length <= maximum) return text;
  return text.slice(0, Math.max(0, maximum - 1)).trimEnd() + "…";
}

function humanize(value) {
  return String(value || "")
    .replace(/([a-z0-9])([A-Z])/g, "$1 $2")
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, function (character) { return character.toUpperCase(); });
}

function element(tagName, className, text) {
  const node = document.createElement(tagName);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = String(text);
  return node;
}

function append(parent) {
  Array.prototype.slice.call(arguments, 1).flat().forEach(function (child) {
    if (child !== null && child !== undefined) parent.appendChild(child);
  });
  return parent;
}

function recordsFrom(payload, fileName) {
  const records = Array.isArray(payload) ? payload : payload && payload.records;
  if (!Array.isArray(records)) throw new Error(fileName + " must contain a records array.");
  return records;
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function assertExactInteger(value, message) {
  assert(typeof value === "number" && Number.isInteger(value), message);
}

function sameStringSet(left, right) {
  if (left.length !== right.length) return false;
  const rightSet = new Set(right);
  return left.every(function (value) { return rightSet.has(value); });
}

function uniqueRecordMap(records, idField, label) {
  const result = new Map();
  records.forEach(function (record) {
    const id = record && record[idField];
    assert(typeof id === "string" && id.length > 0, label + " has a missing ID.");
    assert(!result.has(id), label + " contains duplicate ID " + id + ".");
    result.set(id, record);
  });
  return result;
}

function assertNoForbiddenRecordKeys(value, path) {
  if (Array.isArray(value)) {
    value.forEach(function (item, index) {
      assertNoForbiddenRecordKeys(item, path + "[" + index + "]");
    });
    return;
  }
  if (!isObject(value)) return;
  Object.entries(value).forEach(function (entry) {
    const key = entry[0];
    assert(!FORBIDDEN_PUBLIC_RECORD_KEYS.has(key), "Private field " + key + " found at " + path + ".");
    assertNoForbiddenRecordKeys(entry[1], path + "." + key);
  });
}

async function fetchPublicJson(fileName) {
  assert(PUBLIC_DATA_FILES.includes(fileName), "Blocked non-canonical public file request: " + fileName);
  if (fileName !== "manifest.json") {
    assert(state.manifestFiles.has(fileName), "File is not declared by the canonical manifest: " + fileName);
  }
  if (state.data.has(fileName)) return state.data.get(fileName);
  const response = await fetch(DATA_BASE + fileName, { cache: "default" });
  if (!response.ok) throw new Error("Unable to load " + fileName + " (HTTP " + response.status + ").");
  const payload = await response.json();
  state.data.set(fileName, payload);
  return payload;
}

async function ensureDiscoveryManifest() {
  if (state.discoveryData.has("discovery_manifest.json")) return state.discoveryData.get("discovery_manifest.json");
  if (!state.discoveryPromises.has("discovery_manifest.json")) {
    state.discoveryPromises.set("discovery_manifest.json", fetch(DISCOVERY_BASE + "discovery_manifest.json", { cache: "default" }).then(async function (response) {
      if (!response.ok) throw new Error("Unable to load the episode discovery manifest (HTTP " + response.status + ").");
      const manifest = await response.json();
      assert(isObject(manifest), "The discovery manifest is missing.");
      assert(manifest.schemaVersion === "1.0", "Unsupported discovery schema.");
      assert(Array.isArray(manifest.publicFiles) && sameStringSet(manifest.publicFiles, DISCOVERY_DATA_FILES), "The discovery allowlist is invalid.");
      assert(manifest.fileCount === DISCOVERY_DATA_FILES.length, "The discovery file count is invalid.");
      assert(manifest.counts.publicReleaseCount === EXPECTED_COUNTS.episode, "The discovery release count changed.");
      manifest.publicFiles.forEach(function (fileName) { state.discoveryManifestFiles.add(fileName); });
      state.discoveryData.set("discovery_manifest.json", manifest);
      return manifest;
    }));
  }
  return state.discoveryPromises.get("discovery_manifest.json");
}

async function fetchDiscoveryJson(fileName) {
  assert(DISCOVERY_DATA_FILES.includes(fileName), "Blocked non-discovery file request: " + fileName);
  await ensureDiscoveryManifest();
  assert(state.discoveryManifestFiles.has(fileName), "File is not declared by the discovery manifest: " + fileName);
  if (state.discoveryData.has(fileName)) return state.discoveryData.get(fileName);
  if (!state.discoveryPromises.has(fileName)) {
    state.discoveryPromises.set(fileName, fetch(DISCOVERY_BASE + fileName, { cache: "default" }).then(async function (response) {
      if (!response.ok) throw new Error("Unable to load " + fileName + " (HTTP " + response.status + ").");
      const payload = await response.json();
      assertNoForbiddenRecordKeys(payload, fileName);
      state.discoveryData.set(fileName, payload);
      return payload;
    }));
  }
  return state.discoveryPromises.get(fileName);
}

async function ensureIconRegistry() {
  if (state.iconRegistry.size) return;
  const response = await fetch(ICON_BASE + "icon_registry.json", { cache: "default" });
  if (!response.ok) throw new Error("Unable to load the entry icon registry (HTTP " + response.status + ").");
  const payload = await response.json();
  assert(payload.schemaVersion === "1.0" && Array.isArray(payload.icons) && payload.icons.length === 11, "The entry icon registry is invalid.");
  payload.icons.forEach(function (icon) {
    assert(typeof icon.key === "string" && !state.iconRegistry.has(icon.key), "Duplicate or missing entry icon key.");
    assert(icon.width === 256 && icon.height === 256, "Entry icon dimensions must be 256 by 256.");
    assert(/^png\/[a-z-]+\.png$/.test(icon.png) && /^webp\/[a-z-]+\.webp$/.test(icon.webp), "Entry icon path is invalid.");
    state.iconRegistry.set(icon.key, icon);
  });
}

function entryIcon(key, size, className) {
  const icon = state.iconRegistry.get(key);
  assert(icon, "Missing entry icon: " + key);
  const picture = element("picture", "entry-icon" + (className ? " " + className : ""));
  const source = element("source");
  source.srcset = ICON_BASE + icon.webp;
  source.type = "image/webp";
  const image = element("img");
  image.src = ICON_BASE + icon.png;
  image.width = icon.width;
  image.height = icon.height;
  image.alt = "";
  image.decoding = "async";
  image.style.width = Math.min(128, size || 80) + "px";
  image.style.height = Math.min(128, size || 80) + "px";
  picture.appendChild(source);
  picture.appendChild(image);
  return picture;
}

function validateEpisodeMetadata(records) {
  assert(Array.isArray(records) && records.length === EXPECTED_COUNTS.episode, "Episode metadata must cover all releases.");
  const seen = new Set();
  records.forEach(function (record) {
    assert(isObject(record) && sameStringSet(Object.keys(record), ["episodeId", "publishedAt", "guests", "officialEpisodeUrl"]), "Episode metadata field allowlist mismatch.");
    assert(getEntity("episode", record.episodeId) && !seen.has(record.episodeId), "Episode metadata has an unknown or duplicate ID.");
    seen.add(record.episodeId);
    assert(record.publishedAt === null || /^\d{4}-\d{2}-\d{2}$/.test(record.publishedAt), "Invalid publication date.");
    assert(record.guests === null || (Array.isArray(record.guests) && record.guests.length && record.guests.every(hasValue)), "Invalid guest metadata.");
    if (record.officialEpisodeUrl !== null) {
      const url = new URL(record.officialEpisodeUrl);
      assert(url.protocol === "https:" && url.hostname === "information-professionals.org", "Episode source URL is outside the official publisher domain.");
    }
  });
  return records;
}

async function ensureEpisodeMetadata() {
  if (state.maps.metadataByEpisode) return;
  const records = validateEpisodeMetadata(await fetchDiscoveryJson("episode_metadata.json"));
  state.maps.metadataByEpisode = uniqueRecordMap(records, "episodeId", "Episode metadata");
}

async function ensureEpisodeDiscovery() {
  if (state.maps.discoveryByEpisode && state.maps.topicEpisodes) return;
  const payloads = await Promise.all(EAGER_DISCOVERY_FILES.map(fetchDiscoveryJson));
  validateEpisodeMetadata(payloads[0]);
  const discovery = payloads[1];
  const topicIndex = payloads[2];
  assert(discovery.schemaVersion === "1.0" && Array.isArray(discovery.records) && discovery.records.length === EXPECTED_COUNTS.episode, "Episode discovery records are invalid.");
  assert(topicIndex.schemaVersion === "1.0" && Array.isArray(topicIndex.records) && topicIndex.records.length === EXPECTED_COUNTS.cluster, "Topic episode index is invalid.");
  state.maps.metadataByEpisode = uniqueRecordMap(payloads[0], "episodeId", "Episode metadata");
  state.maps.discoveryByEpisode = uniqueRecordMap(discovery.records, "episodeId", "Episode discovery");
  state.discoveryMethod = discovery.method;
  state.maps.topicEpisodes = new Map();
  topicIndex.records.forEach(function (record) {
    assert(getEntity("cluster", record.topicId) && !state.maps.topicEpisodes.has(record.topicId), "Unknown or duplicate topic index ID.");
    assert(Array.isArray(record.episodeIds) && record.episodeIds.every(function (id) { return Boolean(getEntity("episode", id)); }), "Topic index has an unknown episode.");
    state.maps.topicEpisodes.set(record.topicId, record.episodeIds.slice());
  });
}

async function ensureSimilarityData() {
  if (state.maps.similarityProfiles) return;
  await ensureEpisodeDiscovery();
  const payload = await fetchDiscoveryJson("similarity_data.json");
  assert(payload.schemaVersion === "1.0" && payload.contentUnitCount === 241 && Array.isArray(payload.profiles) && payload.profiles.length === 241, "Similarity profiles are invalid.");
  state.similarityMethod = payload.method;
  state.maps.similarityProfiles = new Map();
  payload.profiles.forEach(function (profile) {
    assert(getEntity("episode", profile.contentEpisodeId) && !state.maps.similarityProfiles.has(profile.contentEpisodeId), "Unknown or duplicate similarity profile.");
    const vector = new Map();
    asArray(profile.topics).forEach(function (topic) {
      assert(getEntity("cluster", topic.topicId) && Number.isFinite(topic.normalizedWeight) && topic.normalizedWeight > 0, "Invalid similarity topic vector.");
      vector.set(topic.topicId, topic.normalizedWeight);
    });
    state.maps.similarityProfiles.set(profile.contentEpisodeId, vector);
  });
}

function validateManifest(manifest) {
  assert(isObject(manifest), "The canonical manifest is missing.");
  assert(manifest.schemaVersion === "2.0", "The Explorer requires Cognitive Security schema 2.0.");
  assert(Array.isArray(manifest.publicFiles), "The manifest publicFiles list is missing.");
  assert(sameStringSet(manifest.publicFiles, PUBLIC_DATA_FILES), "The manifest does not match the canonical public-file allowlist.");
  assertExactInteger(manifest.fileCount, "The manifest fileCount must be an integer.");
  assert(manifest.fileCount === PUBLIC_DATA_FILES.length, "The manifest fileCount does not match the allowlist.");
  assert(Array.isArray(manifest.lazyFiles) && sameStringSet(manifest.lazyFiles, LAZY_PUBLIC_FILES), "The manifest lazyFiles list is invalid.");
  state.manifestFiles = new Set(manifest.publicFiles);
}

function validateSupport(support, label) {
  if (support === null || support === undefined) return;
  assert(isObject(support), label + " support must be an object.");
  const primary = support.primarySupport;
  const reach = support.broaderTraceableReach;
  assert(isObject(primary), label + " support.primarySupport is missing.");
  assert(isObject(reach), label + " support.broaderTraceableReach is missing.");
  assertExactInteger(primary.itemCount, label + " primary item count must be an integer.");
  assert(typeof primary.share === "number" && Number.isFinite(primary.share), label + " primary share must be numeric.");
  ["primaryContentUnitCount", "primaryClusterCount", "primaryFamilyCount", "categoryBreadth"].forEach(function (key) {
    assertExactInteger(primary[key], label + " primary " + key + " must be an integer.");
  });
  ["itemCount", "derivedItemCount", "contentUnitCount", "publicReleaseCount",
    "inheritedPublicReleaseCount", "clusterCount", "familyCount", "categoryBreadth"]
    .forEach(function (key) {
      assertExactInteger(reach[key], label + " " + key + " must be an integer.");
    });
  assert(support.interpretation === SUPPORT_INTERPRETATION, label + " support interpretation changed.");
}

function validateInitialData() {
  const manifest = state.data.get("manifest.json");
  const qa = state.data.get("qa_report.json");
  assert(isObject(qa) && qa.status === "pass", "The canonical QA report did not pass.");
  assert(isObject(qa.checks) && Object.values(qa.checks).every(function (value) { return value === true; }), "A canonical public QA check did not pass.");

  const categories = recordsFrom(state.data.get("categories.json"), "categories.json");
  const families = recordsFrom(state.data.get("families.json"), "families.json");
  const clusters = recordsFrom(state.data.get("clusters.json"), "clusters.json");
  const clusterSummaries = recordsFrom(state.data.get("cluster_summaries.json"), "cluster_summaries.json");
  const themes = recordsFrom(state.data.get("themes.json"), "themes.json");
  const tensions = recordsFrom(state.data.get("tensions.json"), "tensions.json");
  const narratives = recordsFrom(state.data.get("narratives.json"), "narratives.json");
  const findings = recordsFrom(state.data.get("category_findings.json"), "category_findings.json");
  const scenarios = recordsFrom(state.data.get("scenarios.json"), "scenarios.json");
  const episodes = recordsFrom(state.data.get("episodes.json"), "episodes.json");
  const episodeSummaries = recordsFrom(state.data.get("episode_summaries.json"), "episode_summaries.json");
  const heatmapPayload = state.data.get("heatmap.json");
  const heatmapCells = heatmapPayload && heatmapPayload.cells;

  const actualCounts = {
    category: categories.length,
    family: families.length,
    cluster: clusters.length,
    clusterSummary: clusterSummaries.length,
    theme: themes.length,
    tension: tensions.length,
    narrative: narratives.length,
    categoryFinding: findings.length,
    scenario: scenarios.length,
    episode: episodes.length,
    heatmapCell: Array.isArray(heatmapCells) ? heatmapCells.length : -1,
  };
  Object.keys(EXPECTED_COUNTS).forEach(function (key) {
    assert(actualCounts[key] === EXPECTED_COUNTS[key], "Canonical " + key + " count mismatch.");
    const manifestKey = MANIFEST_COUNT_KEYS[key];
    assertExactInteger(manifest.counts && manifest.counts[manifestKey], "Manifest " + manifestKey + " must be an integer.");
    assert(manifest.counts[manifestKey] === actualCounts[key], "Manifest " + manifestKey + " does not match its file.");
  });
  assert(episodeSummaries.length === EXPECTED_COUNTS.episode, "Episode summary count mismatch.");

  const maps = {
    category: uniqueRecordMap(categories, "categoryId", "Category"),
    family: uniqueRecordMap(families, "familyId", "Family"),
    cluster: uniqueRecordMap(clusters, "clusterId", "Cluster"),
    clusterSummary: uniqueRecordMap(clusterSummaries, "clusterId", "Cluster summary"),
    theme: uniqueRecordMap(themes, "themeId", "Theme"),
    tension: uniqueRecordMap(tensions, "tensionId", "Tension"),
    narrative: uniqueRecordMap(narratives, "narrativeId", "Narrative"),
    categoryFinding: uniqueRecordMap(findings, "findingId", "Category finding"),
    scenario: uniqueRecordMap(scenarios, "scenarioId", "Scenario"),
    episode: uniqueRecordMap(episodes, "episodeId", "Episode"),
    episodeSummary: uniqueRecordMap(episodeSummaries, "episodeId", "Episode summary"),
  };
  assert(sameStringSet(Array.from(maps.cluster.keys()), Array.from(maps.clusterSummary.keys())), "Cluster summaries do not cover exactly the canonical clusters.");
  assert(sameStringSet(Array.from(maps.episode.keys()), Array.from(maps.episodeSummary.keys())), "Episode summaries do not cover exactly the public releases.");

  families.forEach(function (family) {
    assert(maps.category.has(family.categoryId), "Family " + family.familyId + " references an unknown category.");
    validateSupport(family.support, "Family " + family.familyId);
  });
  clusters.forEach(function (cluster) {
    assert(maps.category.has(cluster.categoryId), "Cluster " + cluster.clusterId + " references an unknown category.");
  });
  clusterSummaries.forEach(function (summary) { validateSupport(summary.support, "Cluster " + summary.clusterId); });
  themes.forEach(function (theme) {
    validateSupport(theme.support, "Theme " + theme.themeId);
    assert(Array.isArray(theme.familyRelationships), "Theme " + theme.themeId + " familyRelationships are missing.");
    theme.familyRelationships.forEach(function (relationship) {
      assert(maps.family.has(relationship.familyId), "Theme family relationship references an unknown family.");
      assert(["primary-theme-support", "secondary-theme-support", "conceptual-framing", "future-extension"].includes(relationship.semanticRole), "Theme family relationship has an invalid role.");
    });
  });
  tensions.forEach(function (tension) {
    assert(hasValue(tension.poleALabel) && hasValue(tension.poleBLabel), "Tension " + tension.tensionId + " is missing a pole label.");
    validateSupport(tension.support, "Tension " + tension.tensionId);
  });
  narratives.forEach(function (narrative) { validateSupport(narrative.support, "Narrative " + narrative.narrativeId); });
  findings.forEach(function (finding) {
    assert(maps.category.has(finding.categoryId), "Finding " + finding.findingId + " references an unknown category.");
    validateSupport(finding.support, "Finding " + finding.findingId);
  });
  scenarios.forEach(function (scenario) {
    validateSupport(scenario.support, "Scenario " + scenario.scenarioId);
    if (scenario.scenarioId === "SC-04") {
      assert(scenario.publicNotice === SC04_PUBLIC_NOTICE, "SC-04 must carry the required public governance notice.");
    } else {
      assert(scenario.publicNotice === null, "Only SC-04 may carry a public governance notice.");
    }
  });

  assert(isObject(heatmapPayload), "heatmap.json must be an object.");
  assert(Array.isArray(heatmapCells), "heatmap.json cells are missing.");
  const heatmapKeys = new Set();
  heatmapCells.forEach(function (cell) {
    assert(maps.category.has(cell.categoryId), "Heatmap cell references an unknown category.");
    assert(maps.theme.has(cell.themeId), "Heatmap cell references an unknown theme.");
    assertExactInteger(cell.primaryFamilyCount, "Heatmap primaryFamilyCount must be an integer.");
    assertExactInteger(cell.categoryFamilyCount, "Heatmap categoryFamilyCount must be an integer.");
    assertExactInteger(cell.primaryClusterCount, "Heatmap primaryClusterCount must be an integer.");
    assertExactInteger(cell.primaryContentUnitCount, "Heatmap primaryContentUnitCount must be an integer.");
    assert(typeof cell.normalizedPrimarySupportBreadth === "number" && Number.isFinite(cell.normalizedPrimarySupportBreadth), "Heatmap normalization must be numeric.");
    const key = cell.categoryId + "\u0000" + cell.themeId;
    assert(!heatmapKeys.has(key), "Heatmap contains a duplicate category/theme cell.");
    heatmapKeys.add(key);
  });
  categories.forEach(function (category) {
    themes.forEach(function (theme) {
      assert(heatmapKeys.has(category.categoryId + "\u0000" + theme.themeId), "Heatmap is not a complete 7 × 11 matrix.");
    });
  });

  ["categories.json", "families.json", "clusters.json", "cluster_summaries.json",
    "themes.json", "tensions.json", "narratives.json", "category_findings.json",
    "scenarios.json", "episodes.json", "episode_summaries.json"]
    .forEach(function (fileName) {
      assertNoForbiddenRecordKeys(state.data.get(fileName), fileName);
    });
}

function entityId(type, record) {
  return record && record[ID_FIELDS[type]];
}

function entityName(type, record) {
  if (!record) return "Unknown record";
  if (type === "scenario") return firstValue(record, ["title", "name"], entityId(type, record));
  if (type === "episode") return firstValue(record, ["episodeTitle", "title"], entityId(type, record));
  return firstValue(record, ["name", "title", "clusterName"], entityId(type, record));
}

function sortByName(type, records) {
  return records.slice().sort(function (left, right) {
    const compared = entityName(type, left).localeCompare(entityName(type, right), undefined, { numeric: true, sensitivity: "base" });
    return compared || String(entityId(type, left)).localeCompare(String(entityId(type, right)));
  });
}

function memberClusterIds(family) {
  return asArray(firstValue(family, ["memberClusterIds", "clusterIds"], []));
}

function secondaryClusterIds(family) {
  return asArray(firstValue(family, ["secondaryRelatedClusterIds", "secondaryClusterIds"], []));
}

function buildIndexes() {
  const categories = recordsFrom(state.data.get("categories.json"), "categories.json");
  const families = recordsFrom(state.data.get("families.json"), "families.json");
  const baseClusters = recordsFrom(state.data.get("clusters.json"), "clusters.json");
  const clusterSummaries = recordsFrom(state.data.get("cluster_summaries.json"), "cluster_summaries.json");
  const themes = recordsFrom(state.data.get("themes.json"), "themes.json");
  const tensions = recordsFrom(state.data.get("tensions.json"), "tensions.json");
  const narratives = recordsFrom(state.data.get("narratives.json"), "narratives.json");
  const findings = recordsFrom(state.data.get("category_findings.json"), "category_findings.json");
  const scenarios = recordsFrom(state.data.get("scenarios.json"), "scenarios.json");
  const baseEpisodes = recordsFrom(state.data.get("episodes.json"), "episodes.json");
  const episodeSummaries = recordsFrom(state.data.get("episode_summaries.json"), "episode_summaries.json");

  const summaryMap = uniqueRecordMap(clusterSummaries, "clusterId", "Cluster summary");
  const clusters = baseClusters.map(function (cluster) {
    const summary = summaryMap.get(cluster.clusterId) || {};
    return Object.assign({}, cluster, summary, { name: cluster.name || summary.clusterName });
  });
  const episodeSummaryMap = uniqueRecordMap(episodeSummaries, "episodeId", "Episode summary");
  const episodes = baseEpisodes.map(function (episode) {
    return Object.assign({}, episode, episodeSummaryMap.get(episode.episodeId) || {});
  });

  state.records = {
    category: categories,
    family: families,
    cluster: clusters,
    theme: themes,
    tension: tensions,
    narrative: narratives,
    categoryFinding: findings,
    scenario: scenarios,
    episode: episodes,
  };
  DATA_ENTITY_TYPES.forEach(function (type) {
    state.maps[type] = uniqueRecordMap(state.records[type], ID_FIELDS[type], ENTITY_LABELS[type]);
  });
  state.maps.familyByCategory = new Map();
  categories.forEach(function (category) { state.maps.familyByCategory.set(category.categoryId, []); });
  families.forEach(function (family) { state.maps.familyByCategory.get(family.categoryId).push(family); });

  state.maps.familyByCluster = new Map();
  families.forEach(function (family) {
    memberClusterIds(family).forEach(function (clusterId) {
      assert(state.maps.cluster.has(clusterId), "Family " + family.familyId + " references unknown cluster " + clusterId + ".");
      assert(!state.maps.familyByCluster.has(clusterId), "Cluster " + clusterId + " has more than one primary family.");
      state.maps.familyByCluster.set(clusterId, family);
    });
  });
  clusters.forEach(function (cluster) {
    const declaredFamilyId = firstValue(cluster, ["primaryFamilyId", "familyId"], "");
    if (declaredFamilyId && !state.maps.familyByCluster.has(cluster.clusterId)) {
      const family = state.maps.family.get(declaredFamilyId);
      assert(Boolean(family), "Cluster " + cluster.clusterId + " references an unknown family.");
      state.maps.familyByCluster.set(cluster.clusterId, family);
    }
  });
  assert(state.maps.familyByCluster.size === EXPECTED_COUNTS.cluster, "Every cluster must have exactly one primary family.");
  families.forEach(function (family) {
    assert(Array.from(state.maps.familyByCluster.values()).includes(family), "Every canonical family must contain at least one cluster.");
  });

  state.maps.heatmap = new Map();
  state.data.get("heatmap.json").cells.forEach(function (cell) {
    state.maps.heatmap.set(cell.categoryId + "\u0000" + cell.themeId, cell);
  });

  const semanticRecords = recordsFrom(state.data.get("relationship_semantics.json"), "relationship_semantics.json");
  semanticRecords.forEach(function (record) {
    assert(typeof record.semanticRole === "string" && record.semanticRole, "Relationship semantic role is missing.");
    assert(!state.relationshipSemantics.has(record.semanticRole), "Duplicate relationship semantic role.");
    state.relationshipSemantics.set(record.semanticRole, record);
  });
  state.searchDocuments = buildSearchDocuments();
}

function getEntity(type, id) {
  return state.maps[type] && state.maps[type].get(id);
}

function canonicalEntityType(value) {
  const aliases = {
    "category-finding": "categoryFinding",
    category_finding: "categoryFinding",
    finding: "categoryFinding",
    release: "episode",
  };
  return aliases[value] || value;
}

function routeHref(route) {
  const params = new URLSearchParams();
  ROUTE_PARAMETER_ORDER.forEach(function (key) {
    if (route && hasValue(route[key])) params.set(key, String(route[key]));
  });
  if (!params.has("view")) params.set("view", "start");
  return "?" + params.toString();
}

function parseRoute(url) {
  const params = new URL(url || window.location.href, window.location.href).searchParams;
  const route = {};
  ROUTE_PARAMETER_ORDER.forEach(function (key) {
    const value = params.get(key);
    if (value !== null && value !== "") route[key] = value;
  });
  route.view = route.view || "start";
  return route;
}

function routeForEntity(type, id) {
  return { view: ENTITY_ROUTES[type], id: id };
}

function routeLink(route, label, className) {
  const anchor = element("a", className, label);
  anchor.href = routeHref(route);
  anchor.dataset.appRoute = "true";
  return anchor;
}

function entityLink(type, id, label, className) {
  return routeLink(routeForEntity(type, id), label || entityName(type, getEntity(type, id)), className || "entity-link");
}

function updateActiveNavigation(view) {
  const activeView = PRIMARY_VIEWS.includes(view) ? view : (ENTITY_INDEX_VIEWS[ROUTE_ENTITIES[view]] || "start");
  viewNavigation.querySelectorAll("[data-view-link]").forEach(function (anchor) {
    if (anchor.dataset.viewLink === activeView) anchor.setAttribute("aria-current", "page");
    else anchor.removeAttribute("aria-current");
  });
}

function setHeader(kicker, title, description, summary) {
  viewKicker.textContent = kicker;
  viewTitle.textContent = title;
  viewDescription.textContent = description;
  viewSummary.textContent = summary || "";
  document.title = title + " · PSYWERX Cognitive Security Map";
}

function setBreadcrumbs(items) {
  breadcrumbs.replaceChildren();
  items.forEach(function (item, index) {
    if (index) breadcrumbs.appendChild(element("span", "breadcrumb-separator", "/"));
    if (item.current) breadcrumbs.appendChild(element("span", "breadcrumb-current", item.label));
    else breadcrumbs.appendChild(routeLink(item.route || { view: item.view }, item.label, "breadcrumb-link"));
  });
  breadcrumbs.hidden = items.length === 0;
}

function clearSurface() {
  viewContent.replaceChildren();
  viewActions.replaceChildren();
  searchControls.hidden = true;
  emptyState.hidden = true;
  linkNotice.hidden = true;
  linkNotice.replaceChildren();
  breadcrumbs.hidden = true;
  breadcrumbs.replaceChildren();
}

function showNotice(message) {
  linkNotice.textContent = message;
  linkNotice.hidden = false;
}

function showEmpty(title, message) {
  emptyStateTitle.textContent = title;
  emptyStateMessage.textContent = message;
  emptyState.hidden = false;
}

function focusViewHeading() {
  requestAnimationFrame(function () {
    const target = landingHero.hidden ? viewTitle : $("#page-title");
    if (target) {
      target.tabIndex = -1;
      target.focus({ preventScroll: false });
    }
  });
}

function setLoading(active) {
  loadingState.hidden = !active;
  viewContent.hidden = active;
  viewContent.setAttribute("aria-busy", active ? "true" : "false");
}

function showLoadError(error) {
  setLoading(false);
  loadErrorMessage.textContent = error && error.message ? error.message : "The public map data could not be loaded.";
  loadError.hidden = false;
  appStatus.textContent = "The Cognitive Security map could not be loaded.";
}

function chip(text, variant) {
  return element("span", "map-chip" + (variant ? " map-chip--" + variant : ""), text);
}

function statCard(value, label, detail) {
  const card = element("div", "stat-card");
  card.appendChild(element("strong", "stat-card__value", value));
  card.appendChild(element("span", "stat-card__label", label));
  if (detail) card.appendChild(element("span", "stat-card__detail", detail));
  return card;
}

function cardShell(type, record, bodyText, stretched) {
  const card = element("article", "map-card map-card--" + type);
  card.dataset.entityType = type;
  const id = entityId(type, record);
  card.appendChild(element("p", "map-card__kicker", ENTITY_LABELS[type]));
  const heading = element("h3", "map-card__title");
  heading.appendChild(entityLink(type, id, entityName(type, record), "entity-link" + (stretched ? " map-card__stretched-link" : "")));
  card.appendChild(heading);
  if (bodyText) card.appendChild(element("p", "map-card__body", truncate(bodyText, 260)));
  return card;
}

function sectionBlock(title, introduction, className) {
  const section = element("section", "section-block" + (className ? " " + className : ""));
  section.appendChild(element("h3", "section-title", title));
  if (introduction) section.appendChild(element("p", "section-intro", introduction));
  return section;
}

function cautionBox(title, message, variant) {
  const box = element("aside", "caution-box" + (variant ? " caution-box--" + variant : ""));
  box.appendChild(element("h3", "caution-box__title", title));
  box.appendChild(element("p", null, message));
  return box;
}

function textList(values, ordered, className) {
  const items = asArray(values).filter(hasValue);
  if (!items.length) return element("p", "quiet-note", "No additional public detail is recorded.");
  const list = element(ordered ? "ol" : "ul", className || (ordered ? "numbered-list" : "plain-list"));
  items.forEach(function (item) {
    const listItem = element("li");
    if (isObject(item)) {
      const headingValue = firstValue(item, ["title", "name", "label", "step", "dynamic", "condition"], "");
      if (headingValue) listItem.appendChild(element("strong", null, headingValue));
      const details = Object.entries(item).filter(function (entry) {
        return hasValue(entry[1]) && !["title", "name", "label", "step", "dynamic", "condition"].includes(entry[0]);
      });
      if (details.length) {
        const definitions = element("dl", "compact-definition-list");
        details.forEach(function (entry) {
          definitions.appendChild(element("dt", null, humanize(entry[0])));
          definitions.appendChild(element("dd", null, flattenText(entry[1]).join(" · ")));
        });
        listItem.appendChild(definitions);
      }
    } else {
      listItem.textContent = String(item);
    }
    list.appendChild(listItem);
  });
  return list;
}

function recurringPatternList(values) {
  const patterns = asArray(values).filter(hasValue);
  if (!patterns.length) return element("p", "quiet-note", "No additional public detail is recorded.");
  const list = element("ul", "plain-list recurring-pattern-list");
  patterns.forEach(function (pattern) {
    const item = element("li");
    if (isObject(pattern)) {
      const name = firstValue(pattern, ["title", "name"], "");
      const description = firstValue(pattern, ["description"], "");
      if (name) item.appendChild(element("strong", null, name));
      if (description) item.appendChild(element("p", null, description));
    } else {
      item.textContent = String(pattern);
    }
    list.appendChild(item);
  });
  return list;
}

function definitionRows(rows) {
  const list = element("dl", "definition-list");
  rows.filter(function (row) { return hasValue(row.value); }).forEach(function (row) {
    list.appendChild(element("dt", null, row.label));
    const definition = element("dd");
    if (row.value instanceof Node) definition.appendChild(row.value);
    else definition.textContent = flattenText(row.value).join(" · ");
    list.appendChild(definition);
  });
  return list;
}

function entityChipList(type, ids, emptyText) {
  const valid = Array.from(new Set(asArray(ids))).filter(function (id) { return getEntity(type, id); });
  if (!valid.length) return element("p", "quiet-note", emptyText || "No links are recorded.");
  const list = element("div", "entity-chip-list");
  valid.sort(function (left, right) {
    return entityName(type, getEntity(type, left)).localeCompare(entityName(type, getEntity(type, right)), undefined, { numeric: true });
  }).forEach(function (id) {
    list.appendChild(entityLink(type, id, entityName(type, getEntity(type, id)), "entity-chip"));
  });
  return list;
}

function supportReach(record) {
  return record && record.support && record.support.broaderTraceableReach;
}

const SUPPORT_DERIVATION = Object.freeze({
  cluster: "For a cluster, primary support comes from retained items directly coded to that cluster.",
  family: "For a subcategory, primary support comes from its member topics; the subcategory was not directly coded at item level.",
  theme: "For a theme, primary support comes from primary-support subcategories and topics; the theme was not directly coded at item level.",
  tension: "For a tension, primary support comes from evidence directly allocated to Pole A or Pole B.",
  narrative: "For a narrative, primary evidence is inherited through integrated map constructs; the narrative was not directly coded at item level.",
  finding: "For a finding, primary evidence is traced through supporting subcategories and topics; the finding was not directly coded at item level.",
  scenario: "For a scenario, primary evidence is traced through relevant map constructs; the scenario was not directly coded at item level.",
});

function renderSupportPanel(record, entityType, extraContent) {
  if (!record || !record.support) return null;
  const support = record.support;
  const primary = support.primarySupport;
  const reach = support.broaderTraceableReach;
  const disclosure = element("details", "support-panel analytical-details");
  disclosure.appendChild(element("summary", null, "Analytical details"));
  const section = element("div", "analytical-details__body");
  section.appendChild(element("p", "section-intro", "Primary support is the evidence designated as primary for this entity. Its path depends on entity type; broader reach describes where that evidence can be traced."));
  asArray(extraContent).forEach(function (node) { if (node) section.appendChild(node); });
  section.appendChild(element("h3", "support-layer-title", "Primary corpus support"));
  section.appendChild(element("p", "evidence-boundary-note", SUPPORT_DERIVATION[entityType] || "Primary support follows the governed evidence path for this entity type."));
  const summary = element("div", "support-summary");
  summary.appendChild(statCard(formatNumber(primary.itemCount), "primary-support items", "governed primary evidence"));
  summary.appendChild(statCard(formatPercent(primary.share), "primary-support share", "share of this entity’s traceable item support"));
  summary.appendChild(statCard(formatNumber(primary.primaryContentUnitCount), "primary-support content units", "primary evidence breadth"));
  summary.appendChild(statCard(formatNumber(primary.primaryFamilyCount), "primary subcategories", "subcategories in the primary evidence path"));
  summary.appendChild(statCard(formatNumber(primary.primaryClusterCount), "primary topics", "topics in the primary evidence path"));
  summary.appendChild(statCard(formatNumber(primary.categoryBreadth), "primary category breadth", "categories in the primary evidence path"));
  section.appendChild(summary);
  if (isObject(primary.concentration)) {
    const primaryConcentration = element("div", "primary-concentration");
    primaryConcentration.appendChild(element("h4", null, "Primary-support concentration"));
    primaryConcentration.appendChild(definitionRows([
      { label: "Top content unit", value: formatPercent(primary.concentration.topOneContentUnitShare) },
      { label: "Top two", value: formatPercent(primary.concentration.topTwoContentUnitShare) },
      { label: "Top five", value: formatPercent(primary.concentration.topFiveContentUnitShare) },
      { label: "Effective content units", value: formatNumber(primary.concentration.effectiveContentUnitCount) },
    ]));
    section.appendChild(primaryConcentration);
  }
  const details = element("details", "support-details");
  details.appendChild(element("summary", null, "Show broader traceable reach and limitations"));
  details.appendChild(definitionRows([
    { label: "All traceable items", value: formatNumber(reach.itemCount) },
    { label: "Derived items", value: formatNumber(reach.derivedItemCount) },
    { label: "Content units", value: formatNumber(reach.contentUnitCount) },
    { label: "Public releases", value: formatNumber(reach.publicReleaseCount) },
    { label: "Inherited release coverage", value: formatNumber(reach.inheritedPublicReleaseCount) },
    { label: "Topics", value: formatNumber(reach.clusterCount) },
    { label: "Subcategories", value: formatNumber(reach.familyCount) },
    { label: "Category breadth", value: formatNumber(reach.categoryBreadth) },
    { label: "Interpretation", value: support.interpretation },
    { label: "Limitations", value: support.limitations },
  ]));
  if (isObject(reach.concentration)) {
    details.appendChild(element("h4", null, "Support concentration"));
    details.appendChild(definitionRows([
      { label: "Top content unit", value: formatPercent(reach.concentration.topOneContentUnitShare) },
      { label: "Top two", value: formatPercent(reach.concentration.topTwoContentUnitShare) },
      { label: "Top five", value: formatPercent(reach.concentration.topFiveContentUnitShare) },
      { label: "Effective content units", value: formatNumber(reach.concentration.effectiveContentUnitCount) },
    ]));
  }
  section.appendChild(details);
  disclosure.appendChild(section);
  return disclosure;
}

function searchFieldsFor(type, record) {
  const fields = {
    category: ["name", "summary", "soWhat", "limitations"],
    family: ["name", "definition", "inclusionRules", "exclusionRules", "distinguishingBoundaries", "limitations"],
    cluster: ["name", "definition", "inclusionCriteria", "exclusionCriteria", "nearNeighborDistinctions", "anchorExamples", "summary", "strategicSignificance", "operationalImplications", "primarySecondaryDistinction", "recurringThemes", "limitations"],
    theme: ["name", "definition", "strategicSignificance", "operationalImplications", "boundaryConditions", "limitations"],
    tension: ["name", "definition", "tensionType", "poleALabel", "poleAAssumption", "poleBLabel", "poleBAssumption", "conditionsFavoringA", "conditionsFavoringB", "falseDichotomyCaveat", "neighborDistinctions", "limitations"],
    narrative: ["name", "shortVersion", "coreClaim", "unresolvedIssue", "boundaryConditions", "limitations"],
    scenario: ["title", "description", "scenarioType", "triggerConditions", "branchPoints", "plausiblePathways", "indicators", "counterSignposts", "mitigatingConditions", "tensionPoleDynamics", "strategicImplications", "responseOptions", "researchQuestions", "uncertaintyStatement", "limitations", "publicNotice"],
    episode: ["episodeTitle", "podcast", "summary", "whyItMatters", "keyTopics"],
  };
  return fields[type].flatMap(function (field) { return flattenText(record[field]); }).filter(hasValue);
}

function familyIdsForRecord(type, record) {
  if (type === "family") return [record.familyId];
  if (type === "cluster") {
    const family = state.maps.familyByCluster.get(record.clusterId);
    return family ? [family.familyId] : [];
  }
  return Array.from(new Set([
    ...asArray(record.primaryFamilyIds), ...asArray(record.secondaryFamilyIds),
    ...asArray(record.supportingFamilyIds), ...asArray(record.relevantFutureTrendFamilyIds),
    ...asArray(record.relevantKeyConceptFamilyIds),
  ])).filter(function (id) { return state.maps.family.has(id); });
}

function categoryIdsForRecord(type, record) {
  if (type === "category") return [record.categoryId];
  if (type === "family" || type === "cluster" || type === "categoryFinding") return record.categoryId ? [record.categoryId] : [];
  const categoryIds = new Set(asArray(record.categoryIds));
  familyIdsForRecord(type, record).forEach(function (familyId) {
    const family = getEntity("family", familyId);
    if (family) categoryIds.add(family.categoryId);
  });
  return Array.from(categoryIds).filter(function (id) { return state.maps.category.has(id); });
}

function buildSearchDocuments() {
  const documents = [];
  DEEP_LINK_ENTITY_TYPES.forEach(function (type) {
    state.records[type].forEach(function (record) {
      const fields = searchFieldsFor(type, record);
      const name = entityName(type, record);
      documents.push({
        type: type,
        id: entityId(type, record),
        name: name,
        record: record,
        fields: fields,
        normalizedName: normalizeText(name),
        normalizedText: normalizeText(fields.join(" ")),
        familyIds: familyIdsForRecord(type, record),
        categoryIds: categoryIdsForRecord(type, record),
      });
    });
  });
  return documents;
}

function populateSelect(select, records, type, firstLabel) {
  select.replaceChildren();
  const first = element("option", null, firstLabel);
  first.value = "";
  select.appendChild(first);
  sortByName(type, records).forEach(function (record) {
    const option = element("option", null, entityName(type, record));
    option.value = entityId(type, record);
    select.appendChild(option);
  });
  select.disabled = false;
}

function populateSearchFilters() {
  searchEntityType.replaceChildren();
  const allTypes = element("option", null, "All entity types");
  allTypes.value = "";
  searchEntityType.appendChild(allTypes);
  SEARCH_ENTITY_TYPES.forEach(function (type) {
    const option = element("option", null, ENTITY_PLURAL_LABELS[type]);
    option.value = type;
    searchEntityType.appendChild(option);
  });
  searchEntityType.disabled = false;
  populateSelect(searchCategory, state.records.category, "category", "All categories");
  populateSelect(searchFamily, state.records.family, "family", "All families");
  populateSelect(searchCluster, state.records.cluster, "cluster", "All clusters");
  searchInput.disabled = false;
  searchClear.disabled = false;
  globalSearchInput.disabled = false;
  const globalButton = globalSearchForm.querySelector("button");
  if (globalButton) globalButton.disabled = false;
}

function keyFor(type, id) {
  return type + "\u0000" + id;
}

function addAdjacency(store, type, id, entry) {
  const key = keyFor(type, id);
  if (!store.has(key)) store.set(key, []);
  store.get(key).push(entry);
}

function validateRelationships(payload) {
  const relationships = recordsFrom(payload, "relationships.json");
  assertNoForbiddenRecordKeys(payload, "relationships.json");
  const ids = new Set();
  relationships.forEach(function (relationship) {
    assert(typeof relationship.relationshipId === "string" && relationship.relationshipId, "Relationship ID is missing.");
    assert(!ids.has(relationship.relationshipId), "Duplicate relationship ID.");
    ids.add(relationship.relationshipId);
    const sourceType = canonicalEntityType(relationship.sourceType);
    const targetType = canonicalEntityType(relationship.targetType);
    assert(DATA_ENTITY_TYPES.includes(sourceType), "Unknown relationship source type.");
    assert(DATA_ENTITY_TYPES.includes(targetType), "Unknown relationship target type.");
    assert(getEntity(sourceType, relationship.sourceId), "Relationship has an unknown source endpoint.");
    assert(getEntity(targetType, relationship.targetId), "Relationship has an unknown target endpoint.");
    assert(state.relationshipSemantics.has(relationship.semanticRole), "Relationship uses an unknown semantic role.");
    assert(relationship.qualifier === null || typeof relationship.qualifier === "string", "Relationship qualifier must be null or a string.");
    assert(relationship.causalClaim === false, "The public Explorer does not accept causal relationship claims.");
  });
  return relationships;
}

function buildRelationshipIndex(relationships) {
  state.relationshipAdjacency.clear();
  relationships.forEach(function (relationship) {
    const sourceType = canonicalEntityType(relationship.sourceType);
    const targetType = canonicalEntityType(relationship.targetType);
    addAdjacency(state.relationshipAdjacency, sourceType, relationship.sourceId, {
      otherType: targetType,
      otherId: relationship.targetId,
      direction: "from",
      relationship: relationship,
    });
    addAdjacency(state.relationshipAdjacency, targetType, relationship.targetId, {
      otherType: sourceType,
      otherId: relationship.sourceId,
      direction: "to",
      relationship: relationship,
    });
  });
}

async function ensureRelationships() {
  if (state.data.has("relationships.json") && state.relationshipAdjacency.size) return;
  if (!state.lazyPromises.has("relationships.json")) {
    state.lazyPromises.set("relationships.json", fetchPublicJson("relationships.json").then(function (payload) {
      buildRelationshipIndex(validateRelationships(payload));
      return payload;
    }));
  }
  await state.lazyPromises.get("relationships.json");
}

function validateProvenance(payload) {
  assert(isObject(payload), "provenance.json must be an object.");
  assertNoForbiddenRecordKeys(payload, "provenance.json");
  assert(isObject(payload.clusterRelationship), "Cluster provenance relationship descriptor is missing.");
  assert(payload.clusterRelationship.semanticRole === "direct-coded-support", "Cluster provenance must use direct-coded-support.");
  assert(payload.clusterRelationship.causalClaim === false, "Cluster provenance must be noncausal.");
  assert(isObject(payload.clusterToReleases), "Provenance clusterToReleases is missing.");
  assert(isObject(payload.tensionToReleases), "Provenance tensionToReleases is missing.");
  assert(Array.isArray(payload.sharedContentRelationships), "Provenance shared-content relationships are missing.");
  const directlyWeightedEpisodes = new Set();
  Object.entries(payload.clusterToReleases).forEach(function (entry) {
    assert(getEntity("cluster", entry[0]), "Provenance references an unknown cluster.");
    assert(Array.isArray(entry[1]), "Cluster provenance rows must be an array.");
    entry[1].forEach(function (row) {
      assert(getEntity("episode", row.episodeId), "Cluster provenance references an unknown release.");
      ["primaryItemCount", "secondaryItemCount", "governedWeightedCount"].forEach(function (key) {
        assertExactInteger(row[key], "Cluster provenance " + key + " must be an integer.");
      });
      directlyWeightedEpisodes.add(row.episodeId);
    });
  });
  Object.entries(payload.tensionToReleases).forEach(function (entry) {
    assert(getEntity("tension", entry[0]), "Provenance references an unknown tension.");
    assert(Array.isArray(entry[1]), "Tension provenance rows must be an array.");
    entry[1].forEach(function (row) {
      assert(getEntity("episode", row.episodeId), "Tension provenance references an unknown release.");
      assert(Array.isArray(row.relationships) && row.relationships.length >= 1 && row.relationships.length <= 2, "Tension provenance must expose one or two pole relationships.");
      const roles = new Set();
      row.relationships.forEach(function (relationship) {
        assert(isObject(relationship), "Tension provenance relationship must be an object.");
        assert(relationship.semanticRole === "tension-evidence-pole-a" || relationship.semanticRole === "tension-evidence-pole-b", "Tension provenance must use a governed pole role.");
        assert(!roles.has(relationship.semanticRole), "Tension provenance repeats a pole role.");
        roles.add(relationship.semanticRole);
        assert(typeof relationship.analyticalWeight === "number" && Number.isFinite(relationship.analyticalWeight) && relationship.analyticalWeight > 0, "Tension provenance analytical weight must be positive and numeric.");
        assert(relationship.causalClaim === false, "Tension provenance must be noncausal.");
      });
      directlyWeightedEpisodes.add(row.episodeId);
    });
  });
  payload.sharedContentRelationships.forEach(function (relationship) {
    assert(getEntity("episode", relationship.sourceEpisodeId), "Shared-content provenance has an unknown source release.");
    assert(getEntity("episode", relationship.targetEpisodeId), "Shared-content provenance has an unknown target release.");
    assert(relationship.semanticRole === "shared-content-inheritance", "Unexpected shared-content semantic role.");
    assert(relationship.contributesAnalyticalWeight === false, "Shared-content inheritance must contribute zero analytical weight.");
    assert(!directlyWeightedEpisodes.has(relationship.sourceEpisodeId), "A shared-content reuse release cannot have direct analytical rows.");
  });
  return payload;
}

function buildProvenanceIndex(payload) {
  state.provenanceAdjacency.clear();
  Object.entries(payload.clusterToReleases).forEach(function (entry) {
    entry[1].forEach(function (row) {
      const detail = formatNumber(row.primaryItemCount) + " primary · " + formatNumber(row.secondaryItemCount) + " secondary · governed weight " + formatNumber(row.governedWeightedCount);
      const relationship = { semanticRole: payload.clusterRelationship.semanticRole, qualifier: detail, causalClaim: payload.clusterRelationship.causalClaim };
      addAdjacency(state.provenanceAdjacency, "cluster", entry[0], { otherType: "episode", otherId: row.episodeId, direction: "from", relationship: relationship });
      addAdjacency(state.provenanceAdjacency, "episode", row.episodeId, { otherType: "cluster", otherId: entry[0], direction: "to", relationship: relationship });
    });
  });
  Object.entries(payload.tensionToReleases).forEach(function (entry) {
    entry[1].forEach(function (row) {
      row.relationships.forEach(function (sourceRelationship) {
        const pole = sourceRelationship.semanticRole === "tension-evidence-pole-a" ? "Pole A" : "Pole B";
        const relationship = {
          semanticRole: sourceRelationship.semanticRole,
          qualifier: pole + " analytical weight " + formatNumber(sourceRelationship.analyticalWeight),
          causalClaim: sourceRelationship.causalClaim,
        };
        addAdjacency(state.provenanceAdjacency, "tension", entry[0], { otherType: "episode", otherId: row.episodeId, direction: "from", relationship: relationship });
        addAdjacency(state.provenanceAdjacency, "episode", row.episodeId, { otherType: "tension", otherId: entry[0], direction: "to", relationship: relationship });
      });
    });
  });
  payload.sharedContentRelationships.forEach(function (row) {
    const relationship = { semanticRole: row.semanticRole, qualifier: "Shared recording; zero analytical weight", causalClaim: false };
    addAdjacency(state.provenanceAdjacency, "episode", row.sourceEpisodeId, { otherType: "episode", otherId: row.targetEpisodeId, direction: "from", relationship: relationship });
    addAdjacency(state.provenanceAdjacency, "episode", row.targetEpisodeId, { otherType: "episode", otherId: row.sourceEpisodeId, direction: "to", relationship: relationship });
  });
}

async function ensureProvenance() {
  if (state.data.has("provenance.json") && state.provenanceAdjacency.size) return;
  if (!state.lazyPromises.has("provenance.json")) {
    state.lazyPromises.set("provenance.json", fetchPublicJson("provenance.json").then(function (payload) {
      buildProvenanceIndex(validateProvenance(payload));
      return payload;
    }));
  }
  await state.lazyPromises.get("provenance.json");
}

function adjacentRelationships(type, id) {
  return (state.relationshipAdjacency.get(keyFor(type, id)) || []).slice();
}

function relatedIds(type, id, otherType, roles) {
  const roleSet = roles ? new Set(roles) : null;
  return Array.from(new Set(adjacentRelationships(type, id).filter(function (entry) {
    return entry.otherType === otherType && (!roleSet || roleSet.has(entry.relationship.semanticRole));
  }).map(function (entry) { return entry.otherId; })));
}

function supportingEpisodeIdsForFamily(family) {
  const episodeIds = new Set();
  memberClusterIds(family).forEach(function (clusterId) {
    (state.provenanceAdjacency.get(keyFor("cluster", clusterId)) || []).forEach(function (entry) {
      if (entry.otherType === "episode" && getEntity("episode", entry.otherId)) {
        episodeIds.add(entry.otherId);
      }
    });
  });
  return Array.from(episodeIds).sort(function (leftId, rightId) {
    return episodeSort(getEntity("episode", leftId), getEntity("episode", rightId));
  });
}

function semanticLabel(role) {
  const semantic = state.relationshipSemantics.get(role);
  return firstValue(semantic, ["label", "name"], humanize(role));
}

async function sha256Hex(value) {
  if (!window.crypto || !window.crypto.subtle || typeof TextEncoder === "undefined") return "";
  const bytes = new TextEncoder().encode(value);
  const digest = await window.crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest)).map(function (byte) {
    return byte.toString(16).padStart(2, "0");
  }).join("");
}

async function governedLegacySuccessor(view, id) {
  if (!id || !Object.keys(LEGACY_SUCCESSOR_HASHES).length) return null;
  const hash = await sha256Hex(view + "\u0000" + id);
  return hash && LEGACY_SUCCESSOR_HASHES[hash] ? Object.assign({}, LEGACY_SUCCESSOR_HASHES[hash]) : null;
}

async function canonicalizeRoute(input) {
  const route = Object.assign({}, input);
  if (route.view === "category-finding") {
    const finding = route.id ? getEntity("categoryFinding", route.id) : null;
    const category = finding ? getEntity("category", finding.categoryId) : null;
    return {
      route: category ? { view: "category", id: category.categoryId } : { view: "families" },
      replace: true,
      notice: category
        ? "This former link now opens its parent category."
        : "This former link now opens Categories.",
    };
  }
  if (LEGACY_VIEW_ALIASES[route.view]) {
    route.view = LEGACY_VIEW_ALIASES[route.view];
    delete route.id;
    return { route: route, replace: true, notice: "" };
  }
  if (LEGACY_DETAIL_FALLBACKS[route.view]) {
    const exact = await governedLegacySuccessor(route.view, route.id);
    if (exact) return { route: exact, replace: true, notice: "" };
    return {
      route: { view: LEGACY_DETAIL_FALLBACKS[route.view] },
      replace: true,
      notice: "This link points to content that has been reorganized. No single successor was inferred; the relevant index is shown.",
    };
  }
  if (!PRIMARY_VIEWS.includes(route.view) && !ROUTE_ENTITIES[route.view]) {
    return { route: { view: "start" }, replace: true, notice: "That view is not part of this public map. Start Here is shown." };
  }
  const type = ROUTE_ENTITIES[route.view];
  if (type && (!route.id || !getEntity(type, route.id))) {
    const exact = await governedLegacySuccessor(route.view, route.id);
    if (exact) return { route: exact, replace: true, notice: "" };
    return {
      route: { view: ENTITY_INDEX_VIEWS[type] },
      replace: true,
      notice: "This link points to content that has been reorganized. The relevant index is shown without inferring a replacement.",
    };
  }
  return { route: route, replace: false, notice: "" };
}

function navigate(route, options) {
  const settings = options || {};
  const url = new URL(routeHref(route), window.location.href);
  if (settings.replace) history.replaceState({ route: route }, "", url);
  else history.pushState({ route: route }, "", url);
  return renderRoute({ focus: settings.focus !== false });
}

async function copyCurrentLink() {
  const value = window.location.href;
  if (navigator.clipboard && typeof navigator.clipboard.writeText === "function") {
    try {
      await navigator.clipboard.writeText(value);
      return true;
    } catch (_error) {
      // Continue to the selection fallback.
    }
  }
  const field = element("textarea", "clipboard-fallback");
  field.value = value;
  field.setAttribute("readonly", "");
  field.setAttribute("aria-hidden", "true");
  document.body.appendChild(field);
  field.select();
  field.setSelectionRange(0, value.length);
  let copied = false;
  try { copied = document.execCommand("copy"); } catch (_error) { copied = false; }
  field.remove();
  return copied;
}

function renderCopyLinkAction(route) {
  const isEpisode = route && route.view === "episode";
  const button = element("button", isEpisode ? "text-button" : "secondary-button", isEpisode ? "Share this summary" : "Copy link");
  button.type = "button";
  button.addEventListener("click", async function () {
    const copied = await copyCurrentLink();
    showNotice(copied ? "Link copied." : "Copy the URL from the browser address bar.");
  });
  viewActions.appendChild(button);
}

function modeFilterForm(route, config) {
  const form = element("form", "mode-filter");
  form.setAttribute("role", "search");
  form.setAttribute("aria-label", config.label);
  const queryLabel = element("label");
  queryLabel.appendChild(element("span", null, config.queryLabel || "Search this section"));
  const queryInput = element("input");
  queryInput.type = "search";
  queryInput.name = "q";
  queryInput.value = route.q || "";
  queryInput.placeholder = config.placeholder || "Search names and definitions";
  queryLabel.appendChild(queryInput);
  form.appendChild(queryLabel);

  const controls = {};
  asArray(config.filters).forEach(function (filter) {
    const label = element("label");
    label.appendChild(element("span", null, filter.label));
    const select = element("select");
    select.name = filter.name;
    const all = element("option", null, filter.allLabel || "All");
    all.value = "";
    select.appendChild(all);
    filter.options.forEach(function (option) {
      const node = element("option", null, option.label);
      node.value = option.value;
      select.appendChild(node);
    });
    select.value = route[filter.name] || "";
    label.appendChild(select);
    form.appendChild(label);
    controls[filter.name] = select;
  });
  const submit = element("button", "secondary-button", "Apply");
  submit.type = "submit";
  form.appendChild(submit);
  if (route.q || asArray(config.filters).some(function (filter) { return route[filter.name]; })) {
    form.appendChild(routeLink({ view: config.view }, "Clear", "text-link"));
  }
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    const next = { view: config.view, q: queryInput.value.trim() };
    Object.keys(controls).forEach(function (name) { next[name] = controls[name].value; });
    navigate(next);
  });
  return form;
}

function iconKeyForEntity(type) {
  return {
    category: "categories",
    family: "subcategories",
    cluster: "topics",
    theme: "themes",
    tension: "tensions",
    narrative: "narratives",
    scenario: "scenarios",
    episode: "episodes",
  }[type];
}

function detailHero(type, record) {
  const marker = element("div", "record-detail__marker");
  marker.dataset.entityType = type;
  marker.appendChild(entryIcon(iconKeyForEntity(type), 52, "entry-icon--heading"));
  marker.appendChild(element("p", "map-card__kicker", ENTITY_LABELS[type]));
  return marker;
}

function detailSection(title, content, introduction) {
  const section = element("section", "detail-section");
  section.appendChild(element("h3", null, title));
  if (introduction) section.appendChild(element("p", "section-intro", introduction));
  if (content instanceof Node) section.appendChild(content);
  else if (Array.isArray(content)) content.forEach(function (node) { if (node) section.appendChild(node); });
  else if (hasValue(content)) section.appendChild(element("p", null, content));
  return section;
}

function broaderCategoryBreadth(record) {
  const reach = supportReach(record);
  return reach && Number.isInteger(reach.categoryBreadth) ? reach.categoryBreadth : 0;
}

function primarySupport(record) {
  return record && record.support && record.support.primarySupport;
}

function primaryCategoryBreadth(record) {
  const primary = primarySupport(record);
  return primary && Number.isInteger(primary.categoryBreadth) ? primary.categoryBreadth : 0;
}

function recordMatches(record, type, query) {
  if (!query) return true;
  const normalized = normalizeText([entityName(type, record), ...searchFieldsFor(type, record)].join(" "));
  return normalized.includes(query) || query.split(/[^a-z0-9]+/).filter(Boolean).every(function (token) {
    return normalized.split(/[^a-z0-9]+/).includes(token);
  });
}

function updateHeroStats() {
  const counts = state.data.get("manifest.json").counts;
  $("#total-episode-count").textContent = formatNumber(counts.publicReleaseCount);
  $("#total-family-count").textContent = formatNumber(counts.familyCount);
  $("#total-cluster-count").textContent = formatNumber(counts.clusterCount);
  $("#total-theme-count").textContent = formatNumber(counts.themeCount);
}

function renderStart() {
  const counts = state.data.get("manifest.json").counts;
  setHeader(
    "Start Here",
    "Cognitive Security Explorer",
    "Explore recurring subjects, cross-cutting interpretations, possible futures, and the conversations behind the map.",
    ""
  );
  setBreadcrumbs([]);

  const entryDefinitions = [
    { key: "categories", label: "Categories", route: { view: "families" }, description: "Broad areas of the analysis.", count: counts.categoryCount },
    { key: "subcategories", label: "Subcategories", route: { view: "families", display: "subcategories" }, description: "Related subjects grouped inside a category.", count: counts.familyCount },
    { key: "topics", label: "Topics", route: { view: "families", display: "topics" }, description: "Specific recurring subjects.", count: counts.clusterCount },
    { key: "themes", label: "Themes", route: { view: "themes" }, description: "Patterns spanning different areas.", count: counts.themeCount },
    { key: "tensions", label: "Tensions", route: { view: "tensions" }, description: "Competing priorities, assumptions, or approaches.", count: counts.tensionCount },
    { key: "narratives", label: "Narratives", route: { view: "narratives" }, description: "Broader interpretations integrating multiple analytical threads.", count: counts.narrativeCount },
    { key: "scenarios", label: "Scenarios", route: { view: "scenarios" }, description: "Possible future situations for exploration.", count: counts.scenarioCount },
    { key: "episodes", label: "Episodes", route: { view: "episodes" }, description: "Individual conversations and original sources.", count: counts.publicReleaseCount },
    { key: "search", label: "Search", route: { view: "search" }, description: "Find subjects across the entire map." },
    { key: "methodology", label: "Methodology", route: { view: "methodology" }, description: "Understand the process, evidence, and limits." },
  ];

  const entries = sectionBlock("Choose an entry point", "Start with a broad area, a cross-cutting interpretation, a possible future, or an individual conversation.");
  const grid = element("div", "entry-grid");
  entryDefinitions.forEach(function (entry) {
    const card = routeLink(entry.route, "", "entry-card");
    card.appendChild(entryIcon(entry.key, 88, "entry-icon--tile"));
    const copy = element("span", "entry-card__copy");
    copy.appendChild(element("strong", "entry-card__title", entry.label));
    copy.appendChild(element("span", "entry-card__description", entry.description));
    if (Number.isInteger(entry.count)) copy.appendChild(element("span", "entry-card__count", formatNumber(entry.count)));
    card.appendChild(copy);
    grid.appendChild(card);
  });
  entries.appendChild(grid);
  viewContent.appendChild(entries);

  function overviewNode(key) {
    const entry = entryDefinitions.find(function (item) { return item.key === key; });
    const link = routeLink(entry.route, "", "overview-node overview-node--" + key);
    link.appendChild(entryIcon(key, 60, "entry-icon--overview"));
    link.appendChild(element("span", null, entry.label));
    return link;
  }

  const overview = sectionBlock("How the Explorer fits together", "The connections below organize browsing; they do not assert causation or imply that every record connects to every other record.", "functional-overview");
  const map = element("div", "overview-map");
  const sources = element("section", "overview-group overview-group--sources");
  sources.appendChild(element("h4", null, "Source conversations"));
  sources.appendChild(overviewNode("episodes"));
  const hierarchy = element("section", "overview-group overview-group--hierarchy");
  hierarchy.appendChild(element("h4", null, "Organizational hierarchy"));
  const hierarchyNodes = element("div", "overview-hierarchy");
  hierarchyNodes.appendChild(overviewNode("categories"));
  hierarchyNodes.appendChild(element("span", "overview-relation", "contains"));
  hierarchyNodes.appendChild(overviewNode("subcategories"));
  hierarchyNodes.appendChild(element("span", "overview-relation", "contains"));
  hierarchyNodes.appendChild(overviewNode("topics"));
  hierarchy.appendChild(hierarchyNodes);
  const cross = element("section", "overview-group overview-group--cross");
  cross.appendChild(element("h4", null, "Cross-cutting interpretations"));
  append(cross, overviewNode("themes"), overviewNode("tensions"));
  const synthesis = element("section", "overview-group overview-group--synthesis");
  synthesis.appendChild(element("h4", null, "Synthesis and exploration"));
  append(synthesis, overviewNode("narratives"), overviewNode("scenarios"));
  append(map, sources, hierarchy, cross, synthesis);
  overview.appendChild(map);

  const alternative = element("details", "overview-text");
  alternative.appendChild(element("summary", null, "Text version of this overview"));
  const textNav = element("nav");
  textNav.setAttribute("aria-label", "Explorer overview destinations");
  const list = element("ul", "plain-list");
  entryDefinitions.forEach(function (entry) {
    const item = element("li");
    item.appendChild(routeLink(entry.route, entry.label + " — " + entry.description, "entity-link"));
    list.appendChild(item);
  });
  textNav.appendChild(list);
  alternative.appendChild(textNav);
  overview.appendChild(alternative);
  viewContent.appendChild(overview);
}

function familyCard(family) {
  const card = cardShell("family", family, family.definition);
  const metrics = element("div", "card-metrics");
  const category = getEntity("category", family.categoryId);
  if (category) metrics.appendChild(entityLink("category", category.categoryId, category.name, "entity-chip"));
  metrics.appendChild(chip(formatNumber(memberClusterIds(family).length) + " topics"));
  if (state.relationshipAdjacency.size) {
    metrics.appendChild(chip(formatNumber(relatedIds("family", family.familyId, "theme").length) + " themes", "theme"));
    metrics.appendChild(chip(formatNumber(relatedIds("family", family.familyId, "tension").length) + " tensions", "tension"));
  }
  card.appendChild(metrics);
  return card;
}

function categoryCard(category) {
  const families = state.maps.familyByCategory.get(category.categoryId) || [];
  const card = cardShell("category", category, firstValue(category, ["summary", "soWhat"], ""));
  const metrics = element("div", "card-metrics");
  metrics.appendChild(chip(formatNumber(families.length) + " subcategories"));
  const clusterCount = families.reduce(function (sum, family) { return sum + memberClusterIds(family).length; }, 0);
  metrics.appendChild(chip(formatNumber(clusterCount) + " topics", "quiet"));
  card.appendChild(metrics);
  return card;
}

async function renderFamilies(route) {
  const query = normalizeText(route.q);
  const selectedCategory = state.maps.category.has(route.category) ? route.category : "";
  setHeader(
    "Browse the hierarchy",
    "Categories, subcategories, and topics",
    "Start with seven broad categories, then expand a category to discover its subcategories and topics.",
    "7 categories · 50 subcategories · 127 topics"
  );
  setBreadcrumbs([{ label: "Categories", current: true }]);
  viewContent.appendChild(modeFilterForm(route, {
    view: "families",
    label: "Search and filter categories, subcategories, and topics",
    placeholder: "Search names and short descriptions",
    filters: [{
      name: "category",
      label: "Category",
      allLabel: "All categories",
      options: sortByName("category", state.records.category).map(function (record) { return { value: record.categoryId, label: record.name }; }),
    }],
  }));

  const firstCategory = sortByName("category", state.records.category)[0];
  const firstFamily = sortByName("family", state.maps.familyByCategory.get(firstCategory.categoryId) || [])[0];
  const firstTopic = firstFamily && sortByName("cluster", memberClusterIds(firstFamily).map(function (id) { return getEntity("cluster", id); }).filter(Boolean))[0];
  if (firstCategory && firstFamily && firstTopic) {
    viewContent.appendChild(element("p", "hierarchy-example", "Example: “" + firstCategory.name + "” is a category; “" + firstFamily.name + "” is one of its subcategories; and “" + firstTopic.name + "” is a topic inside that subcategory."));
  }

  const categoryContainer = element("div", "hierarchy-browser");
  let visibleCategoryCount = 0;
  sortByName("category", state.records.category).forEach(function (category) {
    if (selectedCategory && category.categoryId !== selectedCategory) return;
    const families = sortByName("family", state.maps.familyByCategory.get(category.categoryId) || []);
    const familyMatches = new Map();
    let descendantMatch = false;
    families.forEach(function (family) {
      const topics = sortByName("cluster", memberClusterIds(family).map(function (id) { return getEntity("cluster", id); }).filter(Boolean));
      const matchingTopics = topics.filter(function (topic) { return recordMatches(topic, "cluster", query); });
      const familyMatch = recordMatches(family, "family", query);
      if (familyMatch || matchingTopics.length) descendantMatch = true;
      familyMatches.set(family.familyId, { familyMatch: familyMatch, topics: topics, matchingTopics: matchingTopics });
    });
    const categoryMatch = recordMatches(category, "category", query);
    if (query && !categoryMatch && !descendantMatch) return;
    visibleCategoryCount += 1;

    const categoryDetails = element("details", "hierarchy-category");
    categoryDetails.dataset.categoryId = category.categoryId;
    categoryDetails.open = Boolean(
      query || selectedCategory || route.display === "subcategories" || route.display === "topics"
    );
    const summary = element("summary", "hierarchy-category__summary");
    summary.appendChild(entryIcon("categories", 64, "entry-icon--hierarchy"));
    const summaryCopy = element("span");
    summaryCopy.appendChild(element("strong", null, category.name));
    summaryCopy.appendChild(element("span", null, truncate(firstValue(category, ["summary", "soWhat"], ""), 180)));
    summaryCopy.appendChild(element("small", null, formatNumber(families.length) + " subcategories"));
    summary.appendChild(summaryCopy);
    categoryDetails.appendChild(summary);
    const categoryBody = element("div", "hierarchy-category__body");
    categoryBody.appendChild(entityLink("category", category.categoryId, "Read category overview", "card-link"));
    const familyList = element("div", "hierarchy-family-list");
    families.forEach(function (family, familyIndex) {
      const match = familyMatches.get(family.familyId);
      if (query && !categoryMatch && !match.familyMatch && !match.matchingTopics.length) return;
      const familyDetails = element("details", "hierarchy-family");
      familyDetails.dataset.familyId = family.familyId;
      familyDetails.open = Boolean(
        (query && (match.familyMatch || match.matchingTopics.length))
        || (route.display === "topics" && familyIndex === 0)
      );
      const familySummary = element("summary", "hierarchy-family__summary");
      familySummary.appendChild(element("strong", null, family.name));
      familySummary.appendChild(element("span", null, truncate(family.definition, 165)));
      familySummary.appendChild(element("small", null, formatNumber(match.topics.length) + " topics"));
      familyDetails.appendChild(familySummary);
      const familyBody = element("div", "hierarchy-family__body");
      familyBody.appendChild(entityLink("family", family.familyId, "Read subcategory overview", "card-link"));
      const topicList = element("ul", "hierarchy-topic-list");
      const topicsToShow = query && !categoryMatch && !match.familyMatch ? match.matchingTopics : match.topics;
      topicsToShow.forEach(function (topic) {
        const item = element("li");
        item.appendChild(entityLink("cluster", topic.clusterId, topic.name, "entity-link"));
        item.appendChild(element("span", null, truncate(topic.summary || topic.definition, 150)));
        topicList.appendChild(item);
      });
      familyBody.appendChild(topicList);
      familyDetails.appendChild(familyBody);
      familyList.appendChild(familyDetails);
    });
    categoryBody.appendChild(familyList);
    categoryDetails.appendChild(categoryBody);
    categoryContainer.appendChild(categoryDetails);
  });
  if (!visibleCategoryCount) {
    showEmpty("No category, subcategory, or topic matched", "Try a broader term or remove the category filter.");
    return;
  }
  viewSummary.textContent = formatNumber(visibleCategoryCount) + " matching categories";
  viewContent.appendChild(categoryContainer);
}

async function renderCategory(route) {
  const category = getEntity("category", route.id);
  await Promise.all([ensureRelationships(), ensureProvenance()]);
  const families = state.maps.familyByCategory.get(category.categoryId) || [];
  setHeader("Category", category.name, category.summary || "A broad area of the practitioner discourse map.", formatNumber(families.length) + " subcategories");
  setBreadcrumbs([
    { label: "Categories", view: "families" },
    { label: category.name, current: true },
  ]);
  const record = element("div", "record-detail");
  record.appendChild(detailHero("category", category, category.summary));
  if (category.soWhat) record.appendChild(detailSection("Why this category matters", category.soWhat));
  const familySection = detailSection("Explore subcategories", element("div", "map-card-grid"), "Each subcategory groups related topics within this category.");
  const grid = familySection.querySelector(".map-card-grid");
  sortByName("family", families).forEach(function (family) { grid.appendChild(familyCard(family)); });
  record.appendChild(familySection);
  await appendEvidenceExplorer(record, "category", category.categoryId, route);
  viewContent.appendChild(record);
}

async function renderFamily(route) {
  const family = getEntity("family", route.id);
  await Promise.all([ensureRelationships(), ensureProvenance()]);
  const category = getEntity("category", family.categoryId);
  const clusters = memberClusterIds(family).map(function (id) { return getEntity("cluster", id); }).filter(Boolean);
  setHeader("Subcategory", family.name, family.definition, formatNumber(clusters.length) + " topics");
  setBreadcrumbs([
    { label: "Categories", view: "families" },
    { label: category.name, route: routeForEntity("category", category.categoryId) },
    { label: family.name, current: true },
  ]);
  const record = element("div", "record-detail");
  record.appendChild(detailHero("family", family, family.definition));
  const clusterGrid = element("div", "map-card-grid");
  sortByName("cluster", clusters).forEach(function (cluster) {
    clusterGrid.appendChild(cardShell("cluster", cluster, cluster.summary || cluster.definition));
  });
  record.appendChild(detailSection("Member topics", clusterGrid, "These topics are grouped here as their primary subcategory."));
  if (secondaryClusterIds(family).length) {
    record.appendChild(detailSection("Related topics", entityChipList("cluster", secondaryClusterIds(family)), "These secondary connections preserve useful adjacency without changing topic membership."));
  }
  const relatedThemes = relatedIds("family", family.familyId, "theme");
  const relatedTensions = relatedIds("family", family.familyId, "tension");
  record.appendChild(detailSection("Related themes and tensions", definitionRows([
    { label: "Themes", value: entityChipList("theme", relatedThemes) },
    { label: "Tensions", value: entityChipList("tension", relatedTensions) },
  ])));
  const supportingEpisodes = supportingEpisodeIdsForFamily(family);
  const episodeDisclosure = element("details", "support-details supporting-episodes");
  episodeDisclosure.appendChild(element("summary", null, formatNumber(supportingEpisodes.length) + " source episodes"));
  episodeDisclosure.appendChild(entityChipList("episode", supportingEpisodes));
  record.appendChild(detailSection("Source episodes", episodeDisclosure, "Open the list to browse the conversations connected through member topics."));
  const scope = element("details", "scope-details");
  scope.appendChild(element("summary", null, "Scope and coding boundaries"));
  scope.appendChild(definitionRows([
    { label: "Include", value: family.inclusionRules },
    { label: "Exclude", value: family.exclusionRules },
    { label: "Distinguishing boundaries", value: family.distinguishingBoundaries },
    { label: "Limitations", value: family.limitations },
  ]));
  record.appendChild(scope);
  record.appendChild(renderSupportPanel(family, "family"));
  await appendEvidenceExplorer(record, "family", family.familyId, route);
  viewContent.appendChild(record);
}

async function renderCluster(route) {
  const cluster = getEntity("cluster", route.id);
  const category = getEntity("category", cluster.categoryId);
  const family = state.maps.familyByCluster.get(cluster.clusterId);
  setHeader("Topic", cluster.name, cluster.summary || cluster.definition, family ? "In “" + family.name + "”" : "Topic");
  setBreadcrumbs([
    { label: "Categories", view: "families" },
    { label: category.name, route: routeForEntity("category", category.categoryId) },
    { label: family.name, route: routeForEntity("family", family.familyId) },
    { label: cluster.name, current: true },
  ]);
  const record = element("div", "record-detail");
  record.appendChild(detailHero("cluster", cluster, cluster.summary || cluster.definition));
  if (cluster.definition && normalizeText(cluster.definition) !== normalizeText(cluster.summary)) {
    record.appendChild(detailSection("Definition", cluster.definition));
  }
  if (cluster.recurringThemes) record.appendChild(detailSection("Recurring patterns", recurringPatternList(cluster.recurringThemes)));
  record.appendChild(detailSection("Why it matters", definitionRows([
    { label: "Strategic significance", value: cluster.strategicSignificance },
    { label: "Operational implications", value: cluster.operationalImplications },
  ])));
  record.appendChild(detailSection("Where this topic sits", definitionRows([
    { label: "Category", value: entityLink("category", category.categoryId, category.name, "entity-chip") },
    { label: "Subcategory", value: entityLink("family", family.familyId, family.name, "entity-chip") },
  ])));
  const episodePath = element("p", "topic-episode-path");
  episodePath.appendChild(routeLink({ view: "episodes", topic: cluster.clusterId, range: "all", sort: "earliest" }, "More on this topic in Episodes", "secondary-button"));
  record.appendChild(detailSection("Explore related conversations", episodePath, "Shows episodes where this topic received sustained attention in the structured analysis."));
  const boundaries = element("details", "scope-details");
  boundaries.appendChild(element("summary", null, "Scope and coding boundaries"));
  boundaries.appendChild(definitionRows([
    { label: "Include", value: cluster.inclusionCriteria },
    { label: "Exclude", value: cluster.exclusionCriteria },
    { label: "Near neighbors", value: cluster.nearNeighborDistinctions },
    { label: "Primary / secondary distinction", value: cluster.primarySecondaryDistinction },
  ]));
  record.appendChild(boundaries);
  record.appendChild(renderSupportPanel(cluster, "cluster"));
  await appendEvidenceExplorer(record, "cluster", cluster.clusterId, route);
  viewContent.appendChild(record);
}

function renderCategoryThemeHeatmap() {
  const payload = state.data.get("heatmap.json");
  const region = element("div", "heatmap-region");
  region.tabIndex = 0;
  region.setAttribute("role", "region");
  region.setAttribute("aria-label", "Scrollable Theme by Category heatmap");
  const table = element("table", "heatmap-table");
  const caption = element("caption", null, "Normalized primary-support breadth by category and theme.");
  table.appendChild(caption);
  const head = element("thead");
  const headRow = element("tr");
  headRow.appendChild(element("th", null, "Theme"));
  sortByName("category", state.records.category).forEach(function (category) {
    const header = element("th");
    header.scope = "col";
    header.appendChild(entityLink("category", category.categoryId, category.name, "heatmap-category-link"));
    headRow.appendChild(header);
  });
  head.appendChild(headRow);
  table.appendChild(head);
  const body = element("tbody");
  sortByName("theme", state.records.theme).forEach(function (theme) {
    const row = element("tr");
    const rowHeader = element("th");
    rowHeader.scope = "row";
    const themeLink = entityLink("theme", theme.themeId, theme.name, "heatmap-theme-link");
    rowHeader.appendChild(themeLink);
    row.appendChild(rowHeader);
    sortByName("category", state.records.category).forEach(function (category) {
      const cell = state.maps.heatmap.get(category.categoryId + "\u0000" + theme.themeId);
      const dataCell = element("td", "heatmap-cell heatmap-cell--" + Math.max(0, Math.min(5, Math.round(cell.normalizedPrimarySupportBreadth * 5))));
      const label = formatPercent(cell.normalizedPrimarySupportBreadth);
      const link = routeLink({ view: "theme", id: theme.themeId, category: category.categoryId }, label, "heatmap-cell__link");
      link.setAttribute("aria-label", theme.name + " in " + category.name + ": normalized primary-support breadth " + label + "; " + formatNumber(cell.primaryFamilyCount) + " primary subcategories; " + formatNumber(cell.primaryClusterCount) + " primary topics; " + formatNumber(cell.primaryContentUnitCount) + " primary-support content units. Corpus support is descriptive, not evidence strength. Open focused support.");
      dataCell.appendChild(link);
      row.appendChild(dataCell);
    });
    body.appendChild(row);
  });
  table.appendChild(body);
  region.appendChild(table);
  const legend = element("div", "heatmap-legend");
  legend.appendChild(element("strong", null, "Cell meaning:"));
  legend.appendChild(document.createTextNode(" normalized primary-support breadth. Focus a cell for its subcategory, topic, and content-unit counts. Every cell includes a percentage; color is only a secondary cue."));
  region.appendChild(legend);
  region.appendChild(element("p", "evidence-boundary-note", "The matrix excludes secondary-theme-support, conceptual-framing, and future-extension relationships. Zero means no primary-theme support in this corpus, not that the category is irrelevant."));
  return region;
}

function themeCard(theme) {
  return cardShell("theme", theme, theme.definition, true);
}

function renderThemes(route) {
  const query = normalizeText(route.q);
  const themes = state.records.theme.filter(function (theme) { return recordMatches(theme, "theme", query); });
  setHeader("Cross-cutting patterns", "Themes", "Eleven themes connect recurring patterns across categories. All themes appear at the same public level.", formatNumber(themes.length) + " matching themes");
  setBreadcrumbs([{ label: "Themes", current: true }]);
  viewContent.appendChild(modeFilterForm(route, {
    view: "themes",
    label: "Search themes",
    placeholder: "Search theme definitions and implications",
    filters: [],
  }));
  if (!themes.length) {
    showEmpty("No theme matched", "Try a broader term.");
    return;
  }
  const cards = sectionBlock("Explore themes", "Open a theme to read the common pattern, why it matters, and where it appears.");
  const grid = element("div", "map-card-grid");
  sortByName("theme", themes).forEach(function (theme) { grid.appendChild(themeCard(theme)); });
  cards.appendChild(grid);
  viewContent.appendChild(cards);
  const comparison = element("details", "comparison-disclosure");
  comparison.appendChild(element("summary", null, "Compare themes"));
  comparison.appendChild(element("p", "section-intro", "The optional heatmap compares primary-support breadth across all seven categories and eleven themes."));
  comparison.appendChild(renderCategoryThemeHeatmap());
  viewContent.appendChild(comparison);
}

async function renderTheme(route) {
  const theme = getEntity("theme", route.id);
  const selectedCategory = state.maps.category.has(route.category) ? route.category : "";
  const familyRelationships = asArray(theme.familyRelationships);
  function familiesForRole(role) {
    return familyRelationships.filter(function (relationship) {
      return relationship.semanticRole === role && getEntity("family", relationship.familyId);
    }).map(function (relationship) { return relationship.familyId; });
  }
  let primaryFamilies = familiesForRole("primary-theme-support");
  let secondaryFamilies = familiesForRole("secondary-theme-support");
  let conceptualFamilies = familiesForRole("conceptual-framing");
  let futureFamilies = familiesForRole("future-extension");
  if (selectedCategory) {
    primaryFamilies = primaryFamilies.filter(function (id) { return getEntity("family", id).categoryId === selectedCategory; });
    secondaryFamilies = secondaryFamilies.filter(function (id) { return getEntity("family", id).categoryId === selectedCategory; });
    conceptualFamilies = conceptualFamilies.filter(function (id) { return getEntity("family", id).categoryId === selectedCategory; });
    futureFamilies = futureFamilies.filter(function (id) { return getEntity("family", id).categoryId === selectedCategory; });
  }
  setHeader("Theme", theme.name, theme.definition, "Cross-cutting pattern");
  setBreadcrumbs([{ label: "Themes", view: "themes" }, { label: theme.name, current: true }]);
  if (selectedCategory) showNotice("This theme view is focused on " + getEntity("category", selectedCategory).name + ". Primary-support roles remain labelled.");
  const record = element("div", "record-detail");
  record.appendChild(detailHero("theme", theme, theme.definition));
  record.appendChild(detailSection("Why it matters", definitionRows([
    { label: "Strategic significance", value: theme.strategicSignificance },
    { label: "Operational implications", value: theme.operationalImplications },
  ])));
  record.appendChild(detailSection("Boundaries", definitionRows([
    { label: "Boundary conditions", value: theme.boundaryConditions },
    { label: "Limitations", value: theme.limitations },
  ])));
  record.appendChild(detailSection("Where it appears", entityChipList("family", primaryFamilies), "These subcategories form the theme's primary evidence path."));
  if (secondaryFamilies.length) record.appendChild(detailSection("Additional subcategory connections", entityChipList("family", secondaryFamilies)));
  if (conceptualFamilies.length || futureFamilies.length) {
    record.appendChild(detailSection("Broader conceptual reach", definitionRows([
      { label: "Conceptual framing", value: entityChipList("family", conceptualFamilies) },
      { label: "Future extension", value: entityChipList("family", futureFamilies) },
    ])));
  }
  record.appendChild(renderSupportPanel(theme, "theme"));
  await appendEvidenceExplorer(record, "theme", theme.themeId, route);
  viewContent.appendChild(record);
}

function parseEvidencePath(value) {
  if (!value) return [];
  return String(value).split("/").map(function (segment) {
    const separator = segment.indexOf(":");
    if (separator < 1) return null;
    const type = canonicalEntityType(segment.slice(0, separator));
    const id = segment.slice(separator + 1);
    return DEEP_LINK_ENTITY_TYPES.includes(type) && getEntity(type, id) ? { type: type, id: id } : null;
  }).filter(Boolean);
}

function serializeEvidencePath(path) {
  return path.map(function (entry) { return entry.type + ":" + entry.id; }).join("/");
}

function evidenceNeighbors(type, id) {
  const combined = [
    ...(state.relationshipAdjacency.get(keyFor(type, id)) || []),
    ...(state.provenanceAdjacency.get(keyFor(type, id)) || []),
  ];
  const seen = new Set();
  return combined.filter(function (entry) {
    if (entry.otherType === "categoryFinding") return false;
    if (!getEntity(entry.otherType, entry.otherId)) return false;
    const key = entry.otherType + "\u0000" + entry.otherId + "\u0000" + entry.relationship.semanticRole;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  }).sort(function (left, right) {
    const typeOrder = ["category", "family", "cluster", "theme", "tension", "narrative", "scenario", "episode"];
    const byType = typeOrder.indexOf(left.otherType) - typeOrder.indexOf(right.otherType);
    if (byType) return byType;
    return entityName(left.otherType, getEntity(left.otherType, left.otherId)).localeCompare(
      entityName(right.otherType, getEntity(right.otherType, right.otherId)), undefined, { numeric: true }
    );
  });
}

function pathsAreAdjacent(root, path) {
  let current = root;
  return path.every(function (next) {
    const valid = evidenceNeighbors(current.type, current.id).some(function (entry) {
      return entry.otherType === next.type && entry.otherId === next.id;
    });
    current = next;
    return valid;
  });
}

function renderEvidenceSlice(section, root, path, route) {
  section.replaceChildren();
  section.appendChild(element("h3", "section-title", "Explore support and relationships"));
  section.appendChild(element("p", "section-intro", "Move one public relationship slice at a time. Connections are bidirectional for navigation, but no arrow or causal direction is asserted. The path stops at public releases."));
  const trail = [root, ...path];
  const trailNav = element("nav", "evidence-trail");
  trailNav.setAttribute("aria-label", "Current evidence path");
  trail.forEach(function (entry, index) {
    if (index) trailNav.appendChild(element("span", "breadcrumb-separator", "/"));
    const record = getEntity(entry.type, entry.id);
    if (index === trail.length - 1) {
      trailNav.appendChild(element("span", "breadcrumb-current", entityName(entry.type, record)));
    } else {
      const shorterPath = trail.slice(1, index + 1);
      const targetRoute = Object.assign({}, route);
      if (shorterPath.length) targetRoute.path = serializeEvidencePath(shorterPath);
      else delete targetRoute.path;
      trailNav.appendChild(routeLink(targetRoute, entityName(entry.type, record), "breadcrumb-link"));
    }
  });
  section.appendChild(trailNav);

  const current = trail[trail.length - 1];
  const currentRecord = getEntity(current.type, current.id);
  const currentBox = element("div", "evidence-current");
  currentBox.appendChild(element("p", "map-card__kicker", ENTITY_LABELS[current.type] + " · current slice"));
  currentBox.appendChild(element("h4", null, entityName(current.type, currentRecord)));
  currentBox.appendChild(element("p", null, "Choose one directly connected public record to inspect the next slice."));
  section.appendChild(currentBox);

  const neighbors = evidenceNeighbors(current.type, current.id);
  if (!neighbors.length) {
    section.appendChild(element("p", "quiet-note", "No further public relationship slice is available from this record."));
    return;
  }
  const groups = new Map();
  neighbors.forEach(function (entry) {
    if (!groups.has(entry.otherType)) groups.set(entry.otherType, []);
    groups.get(entry.otherType).push(entry);
  });
  const groupContainer = element("div", "evidence-groups");
  groups.forEach(function (entries, otherType) {
    const group = element("section", "evidence-group");
    group.appendChild(element("h4", null, entries.length === 1 ? ENTITY_LABELS[otherType] : ENTITY_PLURAL_LABELS[otherType]));
    const list = element("ul", "evidence-choice-list");
    let visible = Math.min(24, entries.length);
    function draw() {
      list.replaceChildren();
      entries.slice(0, visible).forEach(function (entry) {
        const item = element("li");
        const nextPath = path.concat([{ type: entry.otherType, id: entry.otherId }]);
        const targetRoute = Object.assign({}, route, { path: serializeEvidencePath(nextPath) });
        const link = routeLink(targetRoute, entityName(entry.otherType, getEntity(entry.otherType, entry.otherId)), "evidence-choice");
        item.appendChild(link);
        const relationshipCopy = element("div", "evidence-choice__relationship");
        relationshipCopy.appendChild(chip(semanticLabel(entry.relationship.semanticRole)));
        if (entry.relationship.qualifier) relationshipCopy.appendChild(element("span", null, entry.relationship.qualifier));
        item.appendChild(relationshipCopy);
        list.appendChild(item);
      });
      if (visible < entries.length) {
        const item = element("li", "evidence-choice-list__more");
        const more = element("button", "text-button", "Show " + formatNumber(Math.min(24, entries.length - visible)) + " more");
        more.type = "button";
        more.addEventListener("click", function () {
          const firstNew = visible;
          visible = Math.min(entries.length, visible + 24);
          draw();
          const links = list.querySelectorAll("a.evidence-choice");
          if (links[firstNew]) links[firstNew].focus();
        });
        item.appendChild(more);
        list.appendChild(item);
      }
    }
    draw();
    group.appendChild(list);
    groupContainer.appendChild(group);
  });
  section.appendChild(groupContainer);
  section.appendChild(element("p", "evidence-boundary-note", "Relationship roles describe governed analytical connections. They do not assert causality, endorsement, source quotation, or evidence quality. Release-level rows contain aggregates only; item text and private provenance are not loaded."));
}

async function appendEvidenceExplorer(container, type, id, route) {
  const section = element("section", "section-block evidence-explorer");
  const root = { type: type, id: id };
  container.appendChild(section);
  const requestedPath = parseEvidencePath(route.path);
  if (requestedPath.length) {
    section.appendChild(element("p", "inline-loading", "Loading the requested public relationship slice…"));
    await Promise.all([ensureRelationships(), ensureProvenance()]);
    const validPath = pathsAreAdjacent(root, requestedPath) ? requestedPath : [];
    if (!validPath.length && requestedPath.length) showNotice("The requested connection path is not valid for this record. The starting view is shown.");
    renderEvidenceSlice(section, root, validPath, route);
    return;
  }
  section.appendChild(element("h3", "section-title", "Explore connections & sources"));
  section.appendChild(element("p", "section-intro", "Open a connected slice of topics, interpretations, and source episodes. Formal roles and weights remain available inside the explorer."));
  const load = element("button", "secondary-button", "Open connections & sources");
  load.type = "button";
  load.addEventListener("click", async function () {
    load.disabled = true;
    load.textContent = "Loading connections…";
    try {
      await Promise.all([ensureRelationships(), ensureProvenance()]);
      renderEvidenceSlice(section, root, [], route);
      const heading = section.querySelector("h3");
      if (heading) {
        heading.tabIndex = -1;
        heading.focus();
      }
    } catch (error) {
      section.replaceChildren(cautionBox("Connections unavailable", error.message, "warning"));
    }
  });
  section.appendChild(load);
}

function relationIdsForTension(tension, type) {
  return relatedIds("tension", tension.tensionId, type);
}

function tensionCategoryIds(tension) {
  const ids = new Set();
  relationIdsForTension(tension, "family").forEach(function (familyId) {
    const family = getEntity("family", familyId);
    if (family) ids.add(family.categoryId);
  });
  relationIdsForTension(tension, "cluster").forEach(function (clusterId) {
    const cluster = getEntity("cluster", clusterId);
    if (cluster) ids.add(cluster.categoryId);
  });
  return Array.from(ids);
}

function tensionMatchesBreadth(tension, filter) {
  if (!filter) return true;
  const breadth = primaryCategoryBreadth(tension);
  if (filter === "focused") return breadth <= 2;
  if (filter === "cross-category") return breadth >= 3 && breadth <= 4;
  if (filter === "broad") return breadth >= 5;
  return true;
}

function tensionBalance(tension) {
  return tension.evidenceBalanceAcrossPoles || tension.poleBalance || {};
}

function renderTensionMatrix(tensions) {
  const region = element("div", "matrix-region");
  region.tabIndex = 0;
  region.setAttribute("role", "region");
  region.setAttribute("aria-label", "Scrollable tension comparison");
  const table = element("table", "tension-matrix");
  table.appendChild(element("caption", null, "Tensions shown as neutral two-position constructs. Neither position is ranked or preferred."));
  const head = element("thead");
  const row = element("tr");
  ["Tension", "Type", "Position A", "Position B"].forEach(function (label) {
    const header = element("th", null, label);
    header.scope = "col";
    row.appendChild(header);
  });
  head.appendChild(row);
  table.appendChild(head);
  const body = element("tbody");
  sortByName("tension", tensions).forEach(function (tension) {
    const tableRow = element("tr");
    const nameCell = element("th");
    nameCell.scope = "row";
    nameCell.appendChild(entityLink("tension", tension.tensionId, tension.name));
    tableRow.appendChild(nameCell);
    tableRow.appendChild(element("td", null, humanize(tension.tensionType)));
    tableRow.appendChild(element("td", "pole-cell pole-cell--a", tension.poleALabel));
    tableRow.appendChild(element("td", "pole-cell pole-cell--b", tension.poleBLabel));
    body.appendChild(tableRow);
  });
  table.appendChild(body);
  region.appendChild(table);
  region.appendChild(element("p", "evidence-boundary-note", "The comparison is descriptive and noncausal. It does not rank or endorse either position."));
  return region;
}

function tensionCard(tension) {
  const card = cardShell("tension", tension, tension.definition, true);
  const positions = element("div", "tension-card__positions");
  positions.appendChild(element("p", null, "A · " + tension.poleALabel));
  positions.appendChild(element("p", null, "B · " + tension.poleBLabel));
  card.appendChild(positions);
  return card;
}

async function renderTensions(route) {
  setHeader("Competing priorities and approaches", "Tensions", "Explore twenty two-position constructs without treating either position as a winner, recommendation, or causal endpoint.", "Loading filters…");
  setBreadcrumbs([{ label: "Tensions", current: true }]);
  viewContent.appendChild(element("p", "inline-loading", "Loading connections for the filters…"));
  await ensureRelationships();
  viewContent.replaceChildren();
  const query = normalizeText(route.q);
  const validCategory = state.maps.category.has(route.category) ? route.category : "";
  const validTheme = state.maps.theme.has(route.theme) ? route.theme : "";
  const validScenario = state.maps.scenario.has(route.scenario) ? route.scenario : "";
  const typeValues = Array.from(new Set(state.records.tension.map(function (record) { return record.tensionType; }).filter(hasValue))).sort();
  const validType = typeValues.includes(route.tensionType) ? route.tensionType : "";
  const breadthValues = ["focused", "cross-category", "broad"];
  const validBreadth = breadthValues.includes(route.support) ? route.support : "";
  const normalizedRoute = Object.assign({}, route, {
    category: validCategory,
    theme: validTheme,
    scenario: validScenario,
    tensionType: validType,
    support: validBreadth,
  });
  viewContent.appendChild(modeFilterForm(normalizedRoute, {
    view: "tensions",
    label: "Search and filter tensions",
    placeholder: "Search tension names, poles, and conditions",
    filters: [
      { name: "tensionType", label: "Type", allLabel: "All types", options: typeValues.map(function (value) { return { value: value, label: humanize(value) }; }) },
      { name: "category", label: "Category", allLabel: "All categories", options: sortByName("category", state.records.category).map(function (record) { return { value: record.categoryId, label: record.name }; }) },
      { name: "theme", label: "Theme", allLabel: "All themes", options: sortByName("theme", state.records.theme).map(function (record) { return { value: record.themeId, label: record.name }; }) },
      { name: "scenario", label: "Scenario", allLabel: "All scenarios", options: sortByName("scenario", state.records.scenario).map(function (record) { return { value: record.scenarioId, label: entityName("scenario", record) }; }) },
      { name: "support", label: "Primary category breadth", allLabel: "All breadths", options: [
        { value: "focused", label: "Focused · 1–2 categories" },
        { value: "cross-category", label: "Cross-category · 3–4" },
        { value: "broad", label: "Broad · 5–7" },
      ] },
    ],
  }));
  const tensions = state.records.tension.filter(function (tension) {
    if (!recordMatches(tension, "tension", query)) return false;
    if (validType && tension.tensionType !== validType) return false;
    if (validCategory && !tensionCategoryIds(tension).includes(validCategory)) return false;
    if (validTheme && !relationIdsForTension(tension, "theme").includes(validTheme)) return false;
    if (validScenario && !relationIdsForTension(tension, "scenario").includes(validScenario)) return false;
    return tensionMatchesBreadth(tension, validBreadth);
  });
  viewSummary.textContent = formatNumber(tensions.length) + " of 20 tensions";
  if (!tensions.length) {
    showEmpty("No tension matched", "Remove a filter or try a broader search term.");
    return;
  }
  const grid = element("div", "map-card-grid");
  sortByName("tension", tensions).forEach(function (tension) { grid.appendChild(tensionCard(tension)); });
  viewContent.appendChild(grid);
  const comparison = element("details", "optional-analysis");
  comparison.appendChild(element("summary", null, "Compare tensions"));
  comparison.appendChild(renderTensionMatrix(tensions));
  viewContent.appendChild(comparison);
}

async function renderTension(route) {
  const tension = getEntity("tension", route.id);
  await ensureRelationships();
  setHeader("Tension", tension.name, tension.definition, humanize(tension.tensionType));
  setBreadcrumbs([{ label: "Tensions", view: "tensions" }, { label: tension.name, current: true }]);
  const record = element("div", "record-detail");
  record.appendChild(detailHero("tension", tension, tension.definition));
  if (tension.strategicSignificance) record.appendChild(detailSection("Why it matters", tension.strategicSignificance));
  const poles = element("div", "two-pole canonical-poles");
  const poleA = element("article", "pole-card pole-card--a");
  poleA.appendChild(element("p", "map-card__kicker", "Pole A"));
  poleA.appendChild(element("h4", null, tension.poleALabel));
  poleA.appendChild(element("p", null, tension.poleAAssumption));
  poleA.appendChild(element("h5", null, "Conditions that favor this pole"));
  poleA.appendChild(textList(tension.conditionsFavoringA, false));
  const neutral = element("div", "tension-axis");
  neutral.appendChild(element("span", null, "Held in tension"));
  const poleB = element("article", "pole-card pole-card--b");
  poleB.appendChild(element("p", "map-card__kicker", "Pole B"));
  poleB.appendChild(element("h4", null, tension.poleBLabel));
  poleB.appendChild(element("p", null, tension.poleBAssumption));
  poleB.appendChild(element("h5", null, "Conditions that favor this pole"));
  poleB.appendChild(textList(tension.conditionsFavoringB, false));
  append(poles, poleA, neutral, poleB);
  record.appendChild(detailSection("Two positions", poles, "The construct preserves competing assumptions. It does not prescribe a midpoint or declare a winner."));
  const practitionerQuestion = "When might " + tension.poleALabel.toLocaleLowerCase() + " be more useful, when might " + tension.poleBLabel.toLocaleLowerCase() + " be more useful, and what conditions could make the choice a false dichotomy?";
  record.appendChild(detailSection("A question for practitioners", practitionerQuestion));
  record.appendChild(detailSection("Construct boundaries", definitionRows([
    { label: "Type", value: humanize(tension.tensionType) },
    { label: "False-dichotomy caveat", value: tension.falseDichotomyCaveat },
    { label: "Neighbor distinctions", value: tension.neighborDistinctions },
    { label: "Limitations", value: tension.limitations },
  ])));
  const balance = tensionBalance(tension);
  const balanceDetails = detailSection("Pole balance in this corpus", definitionRows([
    { label: "Pole A items", value: formatNumber(balance.poleAItemCount) },
    { label: "Pole A analytical weight", value: formatNumber(balance.poleAAnalyticalWeight) },
    { label: "Pole A share", value: formatPercent(balance.poleAShare) },
    { label: "Pole B items", value: formatNumber(balance.poleBItemCount) },
    { label: "Pole B analytical weight", value: formatNumber(balance.poleBAnalyticalWeight) },
    { label: "Pole B share", value: formatPercent(balance.poleBShare) },
    { label: "Shared across poles", value: formatNumber(balance.sharedAcrossPolesItemCount) },
    { label: "Total analytical weight", value: formatNumber(balance.totalAnalyticalWeight) },
    { label: "Both poles", value: balance.bothPolesDirectlySupported === true ? "Both poles have directly allocated evidence" : "Not established" },
    { label: "Evidence assessment", value: tension.evidenceAssessment },
  ]), "These values describe the corpus; they do not resolve or rank the positions.");
  record.appendChild(detailSection("Related ideas", definitionRows([
    { label: "Subcategories", value: entityChipList("family", relationIdsForTension(tension, "family")) },
    { label: "Topics", value: entityChipList("cluster", relationIdsForTension(tension, "cluster")) },
    { label: "Themes", value: entityChipList("theme", relationIdsForTension(tension, "theme")) },
    { label: "Narratives", value: entityChipList("narrative", relationIdsForTension(tension, "narrative")) },
    { label: "Scenarios", value: entityChipList("scenario", relationIdsForTension(tension, "scenario")) },
  ]), "Theme connections provide context through shared topics; they are not direct tension evidence."));
  record.appendChild(renderSupportPanel(tension, "tension", balanceDetails));
  await appendEvidenceExplorer(record, "tension", tension.tensionId, route);
  viewContent.appendChild(record);
}

function narrativeCard(narrative) {
  return cardShell("narrative", narrative, narrative.shortVersion || narrative.coreClaim, true);
}

function renderNarratives(route) {
  const query = normalizeText(route.q);
  const narratives = state.records.narrative.filter(function (narrative) { return recordMatches(narrative, "narrative", query); });
  setHeader("Broader interpretations", "Narratives", "Five narratives connect themes, tensions, subcategories, and topics while preserving unresolved issues and boundaries.", formatNumber(narratives.length) + " of 5 narratives");
  setBreadcrumbs([{ label: "Narratives", current: true }]);
  viewContent.appendChild(modeFilterForm(route, {
    view: "narratives",
    label: "Search narratives",
    placeholder: "Search claims, boundaries, and unresolved issues",
    filters: [],
  }));
  if (!narratives.length) {
    showEmpty("No narrative matched", "Try a broader term.");
    return;
  }
  const grid = element("div", "map-card-grid");
  sortByName("narrative", narratives).forEach(function (narrative) { grid.appendChild(narrativeCard(narrative)); });
  viewContent.appendChild(grid);
}

async function renderNarrative(route) {
  const narrative = getEntity("narrative", route.id);
  await ensureRelationships();
  const familyIds = relatedIds("narrative", narrative.narrativeId, "family");
  const categoryIds = Array.from(new Set(familyIds.map(function (familyId) {
    const family = getEntity("family", familyId);
    return family && family.categoryId;
  }).filter(Boolean)));
  setHeader("Narrative", narrative.name, narrative.shortVersion || narrative.coreClaim, "Integrative interpretation");
  setBreadcrumbs([{ label: "Narratives", view: "narratives" }, { label: narrative.name, current: true }]);
  const record = element("div", "record-detail");
  record.appendChild(detailHero("narrative", narrative, narrative.shortVersion || narrative.coreClaim));
  if (normalizeText(narrative.coreClaim) !== normalizeText(narrative.shortVersion)) record.appendChild(detailSection("Narrative arc", narrative.coreClaim));
  if (narrative.strategicSignificance) record.appendChild(detailSection("Why it matters", narrative.strategicSignificance));
  const embeddedTensions = relatedIds("narrative", narrative.narrativeId, "tension");
  if (embeddedTensions.length) record.appendChild(detailSection("Tensions inside the interpretation", entityChipList("tension", embeddedTensions)));
  record.appendChild(detailSection("Boundaries and unresolved issue", definitionRows([
    { label: "Boundary conditions", value: narrative.boundaryConditions },
    { label: "Unresolved issue", value: narrative.unresolvedIssue },
    { label: "Limitations", value: narrative.limitations },
  ])));
  record.appendChild(detailSection("What this narrative integrates", definitionRows([
    { label: "Themes", value: entityChipList("theme", relatedIds("narrative", narrative.narrativeId, "theme")) },
    { label: "Tensions", value: entityChipList("tension", relatedIds("narrative", narrative.narrativeId, "tension")) },
    { label: "Categories", value: entityChipList("category", categoryIds) },
    { label: "Subcategories", value: entityChipList("family", familyIds) },
    { label: "Topics", value: entityChipList("cluster", relatedIds("narrative", narrative.narrativeId, "cluster")) },
  ]), "Integration is an interpretive relationship, not a causal chain."));
  record.appendChild(renderSupportPanel(narrative, "narrative"));
  await appendEvidenceExplorer(record, "narrative", narrative.narrativeId, route);
  viewContent.appendChild(record);
}

function scenarioCard(scenario) {
  const card = cardShell("scenario", scenario, scenario.description, true);
  const meta = element("div", "card-metrics");
  meta.appendChild(chip(humanize(scenario.scenarioType)));
  meta.appendChild(chip("Possible future, not a prediction", "quiet"));
  if (scenario.publicNotice) meta.appendChild(chip("Rights and governance safeguards", "warning"));
  card.appendChild(meta);
  return card;
}

function renderScenarios(route) {
  const query = normalizeText(route.q);
  const types = Array.from(new Set(state.records.scenario.map(function (record) { return record.scenarioType; }).filter(hasValue))).sort();
  const selectedType = types.includes(route.type) ? route.type : "";
  const scenarios = state.records.scenario.filter(function (scenario) {
    return (!selectedType || scenario.scenarioType === selectedType) && recordMatches(scenario, "scenario", query);
  });
  setHeader("Possible futures for exploration", "Scenarios", "Six scenarios connect triggers, branches, pathways, signals, implications, and response options without predicting what will happen.", formatNumber(scenarios.length) + " of 6 scenarios");
  setBreadcrumbs([{ label: "Scenarios", current: true }]);
  viewContent.appendChild(modeFilterForm(Object.assign({}, route, { type: selectedType }), {
    view: "scenarios",
    label: "Search and filter scenarios",
    placeholder: "Search triggers, pathways, and indicators",
    filters: [{ name: "type", label: "Scenario type", allLabel: "All types", options: types.map(function (value) { return { value: value, label: humanize(value) }; }) }],
  }));
  if (!scenarios.length) {
    showEmpty("No scenario matched", "Try a broader term or remove the type filter.");
    return;
  }
  const grid = element("div", "map-card-grid map-card-grid--categories");
  sortByName("scenario", scenarios).forEach(function (scenario) { grid.appendChild(scenarioCard(scenario)); });
  viewContent.appendChild(grid);
  viewContent.appendChild(cautionBox("Scenario boundary", "Scenarios are structured possibilities for inquiry and preparation. They are not predictions, validated recommendations, or permissions to deploy a capability.", "quiet"));
}

function scenarioEntityIds(scenario, type) {
  const fieldMap = {
    theme: ["relevantThemeIds", "themeIds"],
    tension: ["relevantTensionIds", "tensionIds"],
    family: ["relevantFutureTrendFamilyIds", "relevantKeyConceptFamilyIds", "familyIds"],
  };
  return Array.from(new Set(fieldMap[type].flatMap(function (field) { return asArray(scenario[field]); }))).filter(function (id) { return getEntity(type, id); });
}

function scenarioRelationshipEntries(scenario) {
  const entries = [];
  const seen = new Set();
  state.records.scenario.forEach(function (source) {
    asArray(source.relationshipsToOtherScenarios).forEach(function (relationship) {
      let otherId = "";
      let orientation = "";
      if (source.scenarioId === scenario.scenarioId) {
        otherId = relationship.targetScenarioId;
        orientation = "recorded from this scenario";
      } else if (relationship.targetScenarioId === scenario.scenarioId) {
        otherId = source.scenarioId;
        orientation = "recorded from the related scenario";
      }
      if (!otherId || !getEntity("scenario", otherId)) return;
      const key = [otherId, relationship.semanticRole, relationship.qualifier || ""].join("\u0000");
      if (seen.has(key)) return;
      seen.add(key);
      entries.push({
        otherId: otherId,
        orientation: orientation,
        semanticRole: relationship.semanticRole,
        qualifier: relationship.qualifier,
        rationale: relationship.rationale,
        causalClaim: relationship.causalClaim,
      });
    });
  });
  return entries.sort(function (left, right) {
    return entityName("scenario", getEntity("scenario", left.otherId)).localeCompare(
      entityName("scenario", getEntity("scenario", right.otherId)), undefined, { numeric: true }
    ) || left.semanticRole.localeCompare(right.semanticRole);
  });
}

function renderRelatedScenarios(scenario) {
  const entries = scenarioRelationshipEntries(scenario);
  if (!entries.length) return element("p", "quiet-note", "No related scenario is recorded.");
  const list = element("ul", "related-scenario-list");
  entries.forEach(function (entry) {
    const item = element("li", "related-scenario-list__item");
    item.appendChild(entityLink("scenario", entry.otherId, entityName("scenario", getEntity("scenario", entry.otherId)), "entity-chip"));
    const semantics = element("p", "related-scenario-list__semantics");
    semantics.appendChild(chip(semanticLabel(entry.semanticRole)));
    if (entry.qualifier) semantics.appendChild(chip(humanize(entry.qualifier), "quiet"));
    semantics.appendChild(chip("Noncausal", "quiet"));
    item.appendChild(semantics);
    if (entry.rationale) item.appendChild(element("p", null, entry.rationale));
    item.appendChild(element("p", "quiet-note", "Relationship " + entry.orientation + "; it does not assert causality."));
    list.appendChild(item);
  });
  return list;
}

async function renderScenario(route) {
  const scenario = getEntity("scenario", route.id);
  await ensureRelationships();
  setHeader("Possible future, not a prediction", entityName("scenario", scenario), scenario.description, humanize(scenario.scenarioType));
  setBreadcrumbs([{ label: "Scenarios", view: "scenarios" }, { label: entityName("scenario", scenario), current: true }]);
  const record = element("div", "record-detail");
  record.appendChild(detailHero("scenario", scenario, scenario.description));
  if (scenario.publicNotice) {
    const warning = element("aside", "scenario-governance-notice");
    warning.setAttribute("role", "note");
    warning.setAttribute("aria-label", "Governance and rights notice");
    warning.appendChild(element("h3", null, "Rights and governance safeguards are essential"));
    warning.appendChild(element("p", null, "Any operational consideration requires legal, privacy, civil-liberties, ethics, consent, and affected-community review."));
    const fullSafeguard = element("details", "scenario-safeguard");
    fullSafeguard.appendChild(element("summary", null, "Read the full safeguard"));
    fullSafeguard.appendChild(element("p", null, scenario.publicNotice));
    warning.appendChild(fullSafeguard);
    record.appendChild(warning);
  }
  record.appendChild(detailSection("What this scenario explores", scenario.uncertaintyStatement || "A structured possibility for inquiry and preparation, not a forecast or recommendation."));
  record.appendChild(detailSection("Triggers", textList(scenario.triggerConditions, false)));
  record.appendChild(detailSection("Plausible unfolding", textList(scenario.plausiblePathways, true), "These pathways are plausible sequences, not causal predictions."));
  record.appendChild(detailSection("Branches", textList(scenario.branchPoints, false)));
  record.appendChild(detailSection("What to watch", textList(scenario.indicators, false)));
  record.appendChild(detailSection("Tension dynamics", textList(scenario.tensionPoleDynamics, false), "Directions describe how scenario conditions could favor a pole; they do not endorse that pole."));
  record.appendChild(detailSection("Implications and response options", [
    element("h4", null, "Strategic implications"), textList(scenario.strategicImplications, false),
    element("h4", null, "Response options"), textList(scenario.responseOptions, false),
  ], "Response options are analytical possibilities, not validated recommendations."));
  record.appendChild(detailSection("Counter-signposts and mitigating conditions", [
    element("h4", null, "Counter-signposts"), textList(scenario.counterSignposts, false),
    element("h4", null, "Mitigating conditions"), textList(scenario.mitigatingConditions, false),
  ]));
  record.appendChild(detailSection("Research questions", textList(scenario.researchQuestions, false), "These questions mark evidence and decision gaps."));
  record.appendChild(detailSection("Connections", definitionRows([
    { label: "Themes", value: entityChipList("theme", scenarioEntityIds(scenario, "theme")) },
    { label: "Tensions", value: entityChipList("tension", scenarioEntityIds(scenario, "tension")) },
    { label: "Subcategories", value: entityChipList("family", scenarioEntityIds(scenario, "family")) },
  ])));
  record.appendChild(detailSection("Related scenarios", renderRelatedScenarios(scenario), "These relationships provide context only; none is a causal claim."));
  if (scenario.limitations) record.appendChild(detailSection("Limitations", textList(scenario.limitations, false)));
  record.appendChild(renderSupportPanel(scenario, "scenario"));
  await appendEvidenceExplorer(record, "scenario", scenario.scenarioId, route);
  viewContent.appendChild(record);
}

function episodeSort(left, right) {
  const leftNumber = left.parsedEpisodeNumber;
  const rightNumber = right.parsedEpisodeNumber;
  if (Number.isFinite(leftNumber) && Number.isFinite(rightNumber) && leftNumber !== rightNumber) return leftNumber - rightNumber;
  if (Number.isFinite(leftNumber)) return -1;
  if (Number.isFinite(rightNumber)) return 1;
  const byName = entityName("episode", left).localeCompare(entityName("episode", right), undefined, { numeric: true });
  return byName || left.episodeId.localeCompare(right.episodeId);
}

function formatPublishedDate(value) {
  if (!value) return "";
  const date = new Date(value + "T00:00:00Z");
  return Number.isNaN(date.getTime()) ? "" : new Intl.DateTimeFormat("en-US", {
    year: "numeric", month: "long", day: "numeric", timeZone: "UTC",
  }).format(date);
}

function episodeRangeOptions() {
  const numbers = state.records.episode.map(function (episode) { return episode.parsedEpisodeNumber; }).filter(Number.isFinite);
  const maximum = Math.max.apply(null, numbers);
  const options = [
    { value: "all", label: "All episodes" },
    { value: "intro", label: "Trailer, introduction & unnumbered" },
    { value: "1-29", label: "Episodes 1–29" },
  ];
  for (let start = 30; start <= maximum; start += 30) {
    const end = Math.min(start + 29, maximum);
    options.push({ value: start + "-" + end, label: "Episodes " + start + "–" + end });
  }
  return options;
}

function episodeInRange(episode, range) {
  if (!range || range === "all") return true;
  const number = episode.parsedEpisodeNumber;
  if (range === "intro") return !Number.isFinite(number) || number < 1;
  const parts = range.split("-").map(Number);
  return parts.length === 2 && Number.isFinite(number) && number >= parts[0] && number <= parts[1];
}

function episodeSortMode(route) {
  if (route.sort === "earliest" || route.sort === "newest") return route.sort;
  try {
    const saved = window.localStorage.getItem("psywerx-episode-sort");
    if (saved === "earliest" || saved === "newest") return saved;
  } catch (_error) {
    // Storage is optional.
  }
  return "earliest";
}

function sortEpisodes(records, mode) {
  return records.slice().sort(function (left, right) {
    const leftNumbered = Number.isFinite(left.parsedEpisodeNumber) && left.parsedEpisodeNumber >= 1;
    const rightNumbered = Number.isFinite(right.parsedEpisodeNumber) && right.parsedEpisodeNumber >= 1;
    if (leftNumbered !== rightNumbered) return leftNumbered ? -1 : 1;
    if (leftNumbered && rightNumbered && left.parsedEpisodeNumber !== right.parsedEpisodeNumber) {
      return mode === "newest" ? right.parsedEpisodeNumber - left.parsedEpisodeNumber : left.parsedEpisodeNumber - right.parsedEpisodeNumber;
    }
    return entityName("episode", left).localeCompare(entityName("episode", right), undefined, { numeric: true }) || left.episodeId.localeCompare(right.episodeId);
  });
}

function episodeListRoute(route, overrides) {
  const next = { view: "episodes" };
  ["q", "range", "sort", "number", "position", "topic"].forEach(function (key) {
    if (route && hasValue(route[key])) next[key] = route[key];
  });
  return Object.assign(next, overrides || {});
}

function episodeDetailRoute(episode, route, position) {
  const next = episodeListRoute(route, { view: "episode", id: episode.episodeId, position: position });
  delete next.number;
  return next;
}

function episodeBrowseRecords(route) {
  const query = normalizeText(route.q);
  const range = episodeRangeOptions().some(function (option) { return option.value === route.range; }) ? route.range : "all";
  const topicIds = route.topic && state.maps.topicEpisodes ? new Set(state.maps.topicEpisodes.get(route.topic) || []) : null;
  const exactNumber = hasValue(route.number) && /^\d+$/.test(route.number) ? Number(route.number) : null;
  return sortEpisodes(state.records.episode.filter(function (episode) {
    if (exactNumber !== null && episode.parsedEpisodeNumber !== exactNumber) return false;
    if (!episodeInRange(episode, range)) return false;
    if (topicIds && !topicIds.has(episode.episodeId)) return false;
    return recordMatches(episode, "episode", query);
  }), episodeSortMode(route));
}

function episodeMetadataLine(episode) {
  const metadata = state.maps.metadataByEpisode && state.maps.metadataByEpisode.get(episode.episodeId);
  if (!metadata) return "";
  const pieces = [];
  const date = formatPublishedDate(metadata.publishedAt);
  if (date) pieces.push(date);
  if (metadata.guests) pieces.push(metadata.guests.join("; "));
  return pieces.join(" · ");
}

function episodeCard(episode, route, position) {
  const link = routeLink(episodeDetailRoute(episode, route, position), "", "episode-card-link");
  link.id = "episode-card-" + episode.episodeId;
  link.appendChild(element("strong", "episode-card-link__title", entityName("episode", episode)));
  const metadata = episodeMetadataLine(episode);
  if (metadata) link.appendChild(element("span", "episode-card-link__meta", metadata));
  link.appendChild(element("span", "episode-card-link__summary", truncate(episode.summary, 240)));
  if (episode.contentRole === "shared-content-inheritance") link.appendChild(element("span", "episode-card-link__note", "Re-release"));
  else {
    const relatedRerelease = state.records.episode.some(function (candidate) {
      const candidateDiscovery = state.maps.discoveryByEpisode && state.maps.discoveryByEpisode.get(candidate.episodeId);
      return candidateDiscovery && candidateDiscovery.isSharedContentRelease && candidateDiscovery.contentEpisodeId === episode.episodeId;
    });
    if (relatedRerelease) link.appendChild(element("span", "episode-card-link__note", "Original release · also re-released"));
  }
  return link;
}

function renderIncrementalCards(records, container, renderer, pageSize) {
  let visible = Math.min(pageSize, records.length);
  const controls = element("div", "load-more-row");
  function draw(focusIndex) {
    container.replaceChildren();
    records.slice(0, visible).forEach(function (record) { container.appendChild(renderer(record)); });
    controls.replaceChildren();
    if (visible < records.length) {
      const button = element("button", "secondary-button", "Show " + formatNumber(Math.min(pageSize, records.length - visible)) + " more");
      button.type = "button";
      button.addEventListener("click", function () {
        const firstNew = visible;
        visible += pageSize;
        draw(firstNew);
      });
      controls.appendChild(button);
    }
    if (Number.isInteger(focusIndex)) {
      const links = container.querySelectorAll("a.entity-link");
      if (links[focusIndex]) links[focusIndex].focus();
    }
  }
  draw();
  return controls;
}

function episodeBrowseForm(route) {
  const form = element("form", "episode-browser");
  form.setAttribute("role", "search");
  form.setAttribute("aria-label", "Browse episodes");
  const searchLabel = element("label");
  searchLabel.appendChild(element("span", null, "Search titles, summaries, and key topics"));
  const search = element("input");
  search.type = "search";
  search.value = route.q || "";
  search.placeholder = "Search the episode library";
  searchLabel.appendChild(search);
  form.appendChild(searchLabel);
  const rangeLabel = element("label");
  rangeLabel.appendChild(element("span", null, "Episode range"));
  const range = element("select");
  episodeRangeOptions().forEach(function (entry) {
    const option = element("option", null, entry.label);
    option.value = entry.value;
    range.appendChild(option);
  });
  range.value = episodeRangeOptions().some(function (entry) { return entry.value === route.range; }) ? route.range : "all";
  rangeLabel.appendChild(range);
  form.appendChild(rangeLabel);
  const sortLabel = element("label");
  sortLabel.appendChild(element("span", null, "Order"));
  const sort = element("select");
  [{ value: "earliest", label: "Earliest first" }, { value: "newest", label: "Newest first" }].forEach(function (entry) {
    const option = element("option", null, entry.label);
    option.value = entry.value;
    sort.appendChild(option);
  });
  sort.value = episodeSortMode(route);
  sortLabel.appendChild(sort);
  form.appendChild(sortLabel);
  const apply = element("button", "secondary-button", "Apply");
  apply.type = "submit";
  form.appendChild(apply);
  if (route.q || route.range || route.number || route.topic) form.appendChild(routeLink({ view: "episodes", sort: sort.value }, "Clear filters", "text-link"));
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    try { window.localStorage.setItem("psywerx-episode-sort", sort.value); } catch (_error) { /* Optional. */ }
    navigate({ view: "episodes", q: search.value.trim(), range: range.value, sort: sort.value, topic: route.topic || "" });
  });
  return form;
}

function episodeJumpForm(route) {
  const form = element("form", "episode-jump");
  form.setAttribute("aria-label", "Jump to episode number");
  const label = element("label");
  label.appendChild(element("span", null, "Jump to episode number"));
  const input = element("input");
  input.type = "number";
  input.min = "1";
  input.step = "1";
  input.inputMode = "numeric";
  label.appendChild(input);
  form.appendChild(label);
  const submit = element("button", "secondary-button", "Go");
  submit.type = "submit";
  form.appendChild(submit);
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    const number = Number(input.value);
    if (!Number.isInteger(number) || number < 1) {
      showNotice("Enter a positive episode number.");
      return;
    }
    const matches = state.records.episode.filter(function (episode) { return episode.parsedEpisodeNumber === number; });
    if (matches.length === 1) {
      navigate(episodeDetailRoute(matches[0], { sort: episodeSortMode(route), range: "all" }, 0));
    } else if (matches.length > 1) {
      navigate({ view: "episodes", number: String(number), range: "all", sort: episodeSortMode(route) });
    } else {
      showNotice("No release is recorded as episode " + number + ". Numbering gaps are preserved.");
    }
  });
  return form;
}

async function renderEpisodes(route) {
  await ensureEpisodeDiscovery();
  const episodes = episodeBrowseRecords(route);
  const topic = route.topic ? getEntity("cluster", route.topic) : null;
  setHeader("The Cognitive Crucible", "Episodes", "Browse individual conversations and their transcript-grounded PSYWERX summaries.", formatNumber(episodes.length) + " matching releases");
  setBreadcrumbs([{ label: "Episodes", current: true }]);
  viewContent.appendChild(episodeBrowseForm(route));
  viewContent.appendChild(episodeJumpForm(route));
  if (topic) {
    const topicContext = element("div", "active-topic-filter");
    topicContext.appendChild(element("span", null, "More on this topic: "));
    topicContext.appendChild(entityLink("cluster", topic.clusterId, topic.name));
    topicContext.appendChild(routeLink(episodeListRoute(route, { topic: "", position: "" }), "Remove topic filter", "text-link"));
    viewContent.appendChild(topicContext);
  }
  if (route.number && episodes.length > 1) {
    viewContent.appendChild(cautionBox("More than one matching release", "Episode number " + route.number + " appears on multiple catalog records. Choose the title you intended; no record was guessed.", "quiet"));
  }
  if (!episodes.length) {
    showEmpty("No episode matched", "Try another title word, topic, range, or episode number.");
    return;
  }
  const grid = element("div", "episode-card-grid");
  episodes.forEach(function (episode, index) { grid.appendChild(episodeCard(episode, route, index)); });
  viewContent.appendChild(grid);
  const position = Number(route.position);
  if (Number.isInteger(position) && episodes[position]) {
    requestAnimationFrame(function () {
      const target = document.getElementById("episode-card-" + episodes[position].episodeId);
      if (target) target.scrollIntoView({ block: "center" });
    });
  }
}

function episodeNavigation(episode, route, records, index) {
  const nav = element("nav", "episode-navigation");
  nav.setAttribute("aria-label", "Episode navigation");
  nav.appendChild(routeLink(episodeListRoute(route, { position: Math.max(index, 0), number: "" }), "Back to episode list", "episode-navigation__back"));
  const siblings = element("div", "episode-navigation__siblings");
  if (index > 0) siblings.appendChild(routeLink(episodeDetailRoute(records[index - 1], route, index - 1), "← Previous", "secondary-button"));
  else {
    const previous = element("button", "secondary-button", "← Previous");
    previous.type = "button";
    previous.disabled = true;
    siblings.appendChild(previous);
  }
  if (index >= 0 && index < records.length - 1) siblings.appendChild(routeLink(episodeDetailRoute(records[index + 1], route, index + 1), "Next →", "secondary-button"));
  else {
    const next = element("button", "secondary-button", "Next →");
    next.type = "button";
    next.disabled = true;
    siblings.appendChild(next);
  }
  nav.appendChild(siblings);
  return nav;
}

function episodeTopicList(topicIds, route, includeMoreControl) {
  const container = element("div", "episode-topic-list");
  topicIds.forEach(function (topicId) {
    const topic = getEntity("cluster", topicId);
    if (!topic) return;
    const group = element("span", "episode-topic-list__item");
    group.appendChild(entityLink("cluster", topicId, topic.name, "entity-chip"));
    if (includeMoreControl) group.appendChild(routeLink({ view: "episodes", topic: topicId, sort: episodeSortMode(route), range: "all" }, "More on this topic", "topic-more-link"));
    container.appendChild(group);
  });
  return container;
}

function similarEpisodeCards(episode, route) {
  const discovery = state.maps.discoveryByEpisode.get(episode.episodeId);
  const section = sectionBlock("Similar episodes", "Other conversations with substantial overlap in their main topics. Topic overlap does not imply agreement, importance, or truth.");
  if (!discovery || !discovery.similarOverall.length) {
    section.appendChild(element("p", "quiet-note", "No other conversation has enough main-topic overlap for this release."));
    return section;
  }
  const grid = element("div", "similar-episode-grid");
  discovery.similarOverall.forEach(function (recommendation, index) {
    const candidate = getEntity("episode", recommendation.episodeId);
    if (!candidate) return;
    const card = element("article", "similar-episode-card");
    const heading = element("h4");
    heading.appendChild(routeLink(episodeDetailRoute(candidate, route, index), entityName("episode", candidate), "entity-link"));
    card.appendChild(heading);
    const topics = recommendation.sharedTopicIds.map(function (id) { return entityName("cluster", getEntity("cluster", id)); });
    card.appendChild(element("p", null, "Shared main topics: " + topics.join(" · ")));
    grid.appendChild(card);
  });
  section.appendChild(grid);
  return section;
}

function weightedJaccard(left, right) {
  if (!left || !right || !left.size || !right.size) return null;
  const ids = new Set(Array.from(left.keys()).concat(Array.from(right.keys())));
  let minimum = 0;
  let maximum = 0;
  ids.forEach(function (id) {
    const a = left.get(id) || 0;
    const b = right.get(id) || 0;
    minimum += Math.min(a, b);
    maximum += Math.max(a, b);
  });
  return maximum > 0 ? minimum / maximum : null;
}

function sharedSimilarityTopics(left, right) {
  if (!left || !right) return [];
  return Array.from(left.keys()).filter(function (id) { return right.has(id); }).sort(function (a, b) {
    const overlap = Math.min(left.get(b), right.get(b)) - Math.min(left.get(a), right.get(a));
    return overlap || entityName("cluster", getEntity("cluster", a)).localeCompare(entityName("cluster", getEntity("cluster", b)));
  });
}

function episodeMatrixLabel(episode) {
  return Number.isFinite(episode.parsedEpisodeNumber) && episode.parsedEpisodeNumber >= 1
    ? "#" + episode.parsedEpisodeNumber
    : truncate(entityName("episode", episode), 22);
}

async function renderEpisodeSimilarityMatrix(container, episode, route) {
  container.replaceChildren(element("p", "inline-loading", "Loading comparison data…"));
  try {
    await ensureSimilarityData();
    const discovery = state.maps.discoveryByEpisode.get(episode.episodeId);
    const currentContentId = discovery && discovery.contentEpisodeId;
    const currentVector = state.maps.similarityProfiles.get(currentContentId);
    if (!currentVector || !currentVector.size) {
      container.replaceChildren(element("p", "quiet-note", "Comparison is unavailable because this release has no qualifying topic profile."));
      return;
    }
    const method = state.similarityMethod || state.discoveryMethod || {};
    const eligible = [];
    state.maps.similarityProfiles.forEach(function (vector, contentEpisodeId) {
      if (contentEpisodeId === currentContentId) return;
      const shared = sharedSimilarityTopics(currentVector, vector);
      const score = weightedJaccard(currentVector, vector);
      if (shared.length >= (method.sharedTopicMinimum || 2) && score !== null && score >= (method.similarityMinimum || 0.15)) {
        const candidate = getEntity("episode", contentEpisodeId);
        if (candidate) eligible.push({ contentEpisodeId: contentEpisodeId, episode: candidate, score: score, sharedTopicIds: shared });
      }
    });
    eligible.sort(function (left, right) { return right.score - left.score || episodeSort(left.episode, right.episode); });
    const candidates = eligible.slice(0, 14);
    if (!candidates.length) {
      container.replaceChildren(element("p", "quiet-note", "No related conversation has enough main-topic overlap for comparison."));
      return;
    }
    const controls = element("fieldset", "matrix-selector");
    controls.appendChild(element("legend", null, "Choose up to 14 related episodes to compare with this one"));
    const selected = new Set(candidates.slice(0, 8).map(function (entry) { return entry.contentEpisodeId; }));
    const status = element("p", "quiet-note");
    status.setAttribute("aria-live", "polite");
    candidates.forEach(function (entry) {
      const label = element("label", "matrix-selector__option");
      const checkbox = element("input");
      checkbox.type = "checkbox";
      checkbox.checked = selected.has(entry.contentEpisodeId);
      checkbox.value = entry.contentEpisodeId;
      label.appendChild(checkbox);
      label.appendChild(document.createTextNode(entityName("episode", entry.episode)));
      controls.appendChild(label);
      checkbox.addEventListener("change", function () {
        if (checkbox.checked && selected.size >= 14) {
          checkbox.checked = false;
          status.textContent = "The comparison is limited to 15 unique content units including the current episode.";
          return;
        }
        if (checkbox.checked) selected.add(checkbox.value);
        else selected.delete(checkbox.value);
        status.textContent = formatNumber(selected.size + 1) + " episodes selected.";
        draw();
      });
    });
    controls.appendChild(status);
    const output = element("div", "episode-matrix-output");
    const pairDetail = element("div", "matrix-pair-detail");
    pairDetail.setAttribute("aria-live", "polite");
    container.replaceChildren(
      element("p", "section-intro", "Values are normalized IDF-weighted Jaccard topic overlap. They do not measure agreement, importance, or truth."),
      controls,
      output,
      pairDetail
    );

    function showPair(leftEntry, rightEntry, score, shared) {
      pairDetail.replaceChildren();
      const heading = element("h4", null, "Compared episodes");
      pairDetail.appendChild(heading);
      const links = element("p");
      links.appendChild(entityLink("episode", leftEntry.episode.episodeId, entityName("episode", leftEntry.episode)));
      links.appendChild(document.createTextNode(" and "));
      links.appendChild(entityLink("episode", rightEntry.episode.episodeId, entityName("episode", rightEntry.episode)));
      pairDetail.appendChild(links);
      pairDetail.appendChild(element("p", null, "Topic-overlap value: " + score.toFixed(2) + ". Shared main topics: " + (shared.length ? shared.map(function (id) { return entityName("cluster", getEntity("cluster", id)); }).join(" · ") : "none") + "."));
    }

    function draw() {
      output.replaceChildren();
      pairDetail.replaceChildren();
      const entries = [{ contentEpisodeId: currentContentId, episode: episode }].concat(candidates.filter(function (entry) { return selected.has(entry.contentEpisodeId); }));
      const matrixRegion = element("div", "episode-matrix-region");
      matrixRegion.tabIndex = 0;
      matrixRegion.setAttribute("role", "region");
      matrixRegion.setAttribute("aria-label", "Scrollable episode topic-overlap matrix");
      const table = element("table", "episode-similarity-matrix");
      const caption = element("caption", null, "Pairwise topic overlap for selected episodes");
      table.appendChild(caption);
      const head = element("thead");
      const headRow = element("tr");
      headRow.appendChild(element("th", null, "Episode"));
      entries.forEach(function (entry) {
        const header = element("th", null, episodeMatrixLabel(entry.episode));
        header.scope = "col";
        header.title = entityName("episode", entry.episode);
        header.setAttribute("aria-label", entityName("episode", entry.episode));
        headRow.appendChild(header);
      });
      head.appendChild(headRow);
      table.appendChild(head);
      const body = element("tbody");
      const pairList = element("ul", "matrix-pair-list");
      entries.forEach(function (rowEntry, rowIndex) {
        const row = element("tr");
        const rowHeader = element("th", null, episodeMatrixLabel(rowEntry.episode));
        rowHeader.scope = "row";
        rowHeader.title = entityName("episode", rowEntry.episode);
        rowHeader.setAttribute("aria-label", entityName("episode", rowEntry.episode));
        row.appendChild(rowHeader);
        entries.forEach(function (columnEntry, columnIndex) {
          const cell = element("td");
          if (rowIndex === columnIndex) {
            cell.appendChild(element("span", "matrix-same", "Same episode"));
          } else {
            const leftVector = state.maps.similarityProfiles.get(rowEntry.contentEpisodeId);
            const rightVector = state.maps.similarityProfiles.get(columnEntry.contentEpisodeId);
            const score = weightedJaccard(leftVector, rightVector);
            const shared = sharedSimilarityTopics(leftVector, rightVector);
            if (score === null) {
              cell.appendChild(element("span", "quiet-note", "Unavailable"));
            } else {
              const button = element("button", "matrix-value", score.toFixed(2));
              button.type = "button";
              button.setAttribute("aria-label", entityName("episode", rowEntry.episode) + " and " + entityName("episode", columnEntry.episode) + ": topic-overlap value " + score.toFixed(2));
              button.addEventListener("click", function () { showPair(rowEntry, columnEntry, score, shared); });
              button.addEventListener("focus", function () { showPair(rowEntry, columnEntry, score, shared); });
              cell.appendChild(button);
              if (rowIndex < columnIndex) pairList.appendChild(element("li", null, episodeMatrixLabel(rowEntry.episode) + " ↔ " + episodeMatrixLabel(columnEntry.episode) + ": " + score.toFixed(2) + "; " + (shared.length ? shared.map(function (id) { return entityName("cluster", getEntity("cluster", id)); }).join(", ") : "no shared main topics")));
            }
          }
          row.appendChild(cell);
        });
        body.appendChild(row);
      });
      table.appendChild(body);
      matrixRegion.appendChild(table);
      output.appendChild(matrixRegion);
      const alternative = element("details", "matrix-list-alternative");
      alternative.appendChild(element("summary", null, "Read the comparison as a list"));
      alternative.appendChild(pairList);
      output.appendChild(alternative);
    }
    draw();
  } catch (error) {
    container.replaceChildren(cautionBox("Comparison unavailable", error.message, "warning"));
  }
}

async function renderEpisode(route) {
  await ensureEpisodeDiscovery();
  const episode = getEntity("episode", route.id);
  const metadata = state.maps.metadataByEpisode.get(episode.episodeId);
  let records = episodeBrowseRecords(route);
  let index = records.findIndex(function (entry) { return entry.episodeId === episode.episodeId; });
  if (index < 0) {
    records = sortEpisodes(state.records.episode, episodeSortMode(route));
    index = records.findIndex(function (entry) { return entry.episodeId === episode.episodeId; });
  }
  setHeader("Episode", entityName("episode", episode), episode.summary, episodeMetadataLine(episode) || "The Cognitive Crucible");
  setBreadcrumbs([{ label: "Episodes", route: episodeListRoute(route, { position: Math.max(index, 0), number: "" }) }, { label: entityName("episode", episode), current: true }]);
  if (metadata && metadata.officialEpisodeUrl) {
    const listen = element("a", "primary-button", "Listen & show notes ↗");
    listen.href = metadata.officialEpisodeUrl;
    listen.target = "_blank";
    listen.rel = "noopener noreferrer";
    viewActions.appendChild(listen);
  } else {
    viewActions.appendChild(element("span", "quiet-note", "Verified source page unavailable"));
  }
  const record = element("div", "record-detail record-detail--episode");
  record.appendChild(detailHero("episode", episode));
  record.appendChild(episodeNavigation(episode, route, records, index));
  if (metadata && (metadata.publishedAt || metadata.guests)) {
    const facts = element("dl", "episode-metadata");
    if (metadata.publishedAt) {
      facts.appendChild(element("dt", null, "Published"));
      facts.appendChild(element("dd", null, formatPublishedDate(metadata.publishedAt)));
    }
    if (metadata.guests) {
      facts.appendChild(element("dt", null, "Guests"));
      facts.appendChild(element("dd", null, metadata.guests.join("; ")));
    }
    record.appendChild(facts);
  }
  const discovery = state.maps.discoveryByEpisode.get(episode.episodeId);
  if (episode.contentRole === "shared-content-inheritance") {
    const notice = element("p", "episode-rerelease-note", "Re-release · This catalog page preserves a distinct public release of a conversation represented elsewhere in the library.");
    record.appendChild(notice);
  } else {
    const rerelease = state.records.episode.find(function (candidate) {
      const entry = state.maps.discoveryByEpisode.get(candidate.episodeId);
      return entry && entry.isSharedContentRelease && entry.contentEpisodeId === episode.episodeId;
    });
    if (rerelease) {
      const note = element("p", "episode-rerelease-note", "This conversation also appears as a ");
      note.appendChild(entityLink("episode", rerelease.episodeId, "re-release"));
      note.appendChild(document.createTextNode(" in the public catalog."));
      record.appendChild(note);
    }
  }
  record.appendChild(detailSection("Why it matters", episode.whyItMatters));
  const keyTopics = element("div", "key-topic-links");
  asArray(episode.keyTopics).forEach(function (topic) {
    keyTopics.appendChild(routeLink({ view: "episodes", q: topic, sort: episodeSortMode(route), range: "all" }, topic, "entity-chip"));
  });
  record.appendChild(detailSection("Key topics", keyTopics, "These phrases come from the transcript-grounded episode summary; selecting one searches the library text."));
  const mainTopicSection = sectionBlock("Main topics in this episode", "Topics that received sustained attention in the structured analysis. They are a browsing aid, not a claim of guest agreement.");
  const defaultTopicIds = discovery ? discovery.defaultMainTopicIds : [];
  const allTopicIds = discovery ? discovery.mainTopicIds : [];
  if (defaultTopicIds.length) mainTopicSection.appendChild(episodeTopicList(defaultTopicIds, route, true));
  else mainTopicSection.appendChild(element("p", "quiet-note", "No topic received enough sustained attention to appear in this release's main-topic list."));
  if (allTopicIds.length > defaultTopicIds.length) {
    const more = element("details", "more-main-topics");
    more.appendChild(element("summary", null, "Show more main topics"));
    more.appendChild(episodeTopicList(allTopicIds.slice(defaultTopicIds.length), route, true));
    mainTopicSection.appendChild(more);
  }
  record.appendChild(mainTopicSection);
  record.appendChild(similarEpisodeCards(episode, route));
  const compare = element("details", "episode-comparison");
  compare.appendChild(element("summary", null, "Compare related episodes"));
  const comparisonBody = element("div", "episode-comparison__body");
  compare.appendChild(comparisonBody);
  let comparisonLoaded = false;
  compare.addEventListener("toggle", function () {
    if (compare.open && !comparisonLoaded) {
      comparisonLoaded = true;
      renderEpisodeSimilarityMatrix(comparisonBody, episode, route);
    }
  });
  record.appendChild(compare);
  const sourceSection = sectionBlock("Source", "Verified publisher attribution for this release.");
  if (metadata && metadata.officialEpisodeUrl) {
    const citation = element("p", "source-citation");
    citation.appendChild(document.createTextNode("Source: "));
    const source = element("a", "text-link", "Information Professionals Association");
    source.href = metadata.officialEpisodeUrl;
    source.target = "_blank";
    source.rel = "noopener noreferrer";
    citation.appendChild(source);
    sourceSection.appendChild(citation);
  } else sourceSection.appendChild(element("p", "quiet-note", "A verified publisher episode page is unavailable for this release."));
  record.appendChild(sourceSection);
  await appendEvidenceExplorer(record, "episode", episode.episodeId, route);
  viewContent.appendChild(record);
}

function textMatchesQuery(text, query) {
  if (!query) return true;
  const textTokens = new Set(text.split(/[^a-z0-9]+/).filter(Boolean));
  const queryTokens = query.split(/[^a-z0-9]+/).filter(Boolean);
  if (queryTokens.length === 1 && queryTokens[0].length <= 2) return textTokens.has(queryTokens[0]);
  if (text.includes(query)) return true;
  return queryTokens.length > 0 && queryTokens.every(function (token) { return textTokens.has(token); });
}

function searchRank(documentRecord, query) {
  if (!query) return 10;
  if (documentRecord.normalizedName === query) return 0;
  if (documentRecord.normalizedName.startsWith(query)) return 1;
  if (textMatchesQuery(documentRecord.normalizedName, query)) return 2;
  if (textMatchesQuery(documentRecord.normalizedText, query)) return 4;
  return Number.POSITIVE_INFINITY;
}

function relationshipContext(documentRecord) {
  const familyIds = new Set(documentRecord.familyIds);
  const categoryIds = new Set(documentRecord.categoryIds);
  const clusterIds = new Set(documentRecord.type === "cluster" ? [documentRecord.id] : []);
  adjacentRelationships(documentRecord.type, documentRecord.id).forEach(function (entry) {
    if (entry.otherType === "family") familyIds.add(entry.otherId);
    if (entry.otherType === "cluster") {
      clusterIds.add(entry.otherId);
      const family = state.maps.familyByCluster.get(entry.otherId);
      if (family) familyIds.add(family.familyId);
    }
    if (entry.otherType === "category") categoryIds.add(entry.otherId);
  });
  familyIds.forEach(function (familyId) {
    const family = getEntity("family", familyId);
    if (family) categoryIds.add(family.categoryId);
  });
  return { familyIds: Array.from(familyIds), categoryIds: Array.from(categoryIds), clusterIds: Array.from(clusterIds) };
}

function searchSnippet(documentRecord, query) {
  const candidate = documentRecord.fields.find(function (field) {
    return !query || textMatchesQuery(normalizeText(field), query);
  }) || documentRecord.fields[0] || "";
  return truncate(candidate, 250);
}

function searchResultCard(documentRecord, query) {
  const card = element("article", "map-card map-card--search-result");
  card.appendChild(element("p", "map-card__kicker", ENTITY_LABELS[documentRecord.type]));
  const title = element("h3", "map-card__title");
  title.appendChild(entityLink(documentRecord.type, documentRecord.id, documentRecord.name, "entity-link map-card__stretched-link"));
  card.appendChild(title);
  card.appendChild(element("p", null, searchSnippet(documentRecord, query)));
  return card;
}

function activeFilter(label, value) {
  const chipNode = element("span", "filter-chip");
  chipNode.appendChild(element("strong", null, label + ": "));
  chipNode.appendChild(document.createTextNode(value));
  return chipNode;
}

async function renderSearch(route) {
  setHeader("Find ideas and conversations", "Search the map", "Search definitions, themes, tension positions, narrative interpretations, scenario paths, and episode summaries.", "Public map records");
  setBreadcrumbs([{ label: "Search", current: true }]);
  searchControls.hidden = false;
  const typeFilter = SEARCH_ENTITY_TYPES.includes(route.type) ? route.type : "";
  const categoryFilter = state.maps.category.has(route.category) ? route.category : "";
  const familyFilter = state.maps.family.has(route.family) ? route.family : "";
  const clusterFilter = state.maps.cluster.has(route.cluster) ? route.cluster : "";
  if (categoryFilter || familyFilter || clusterFilter) await ensureRelationships();
  searchInput.value = route.q || "";
  searchEntityType.value = typeFilter;
  searchCategory.value = categoryFilter;
  searchFamily.value = familyFilter;
  searchCluster.value = clusterFilter;
  const query = normalizeText(route.q);
  const results = state.searchDocuments.map(function (documentRecord) {
    return { documentRecord: documentRecord, rank: searchRank(documentRecord, query) };
  }).filter(function (candidate) {
    const documentRecord = candidate.documentRecord;
    if (!Number.isFinite(candidate.rank)) return false;
    if (typeFilter && documentRecord.type !== typeFilter) return false;
    const context = relationshipContext(documentRecord);
    if (categoryFilter && !context.categoryIds.includes(categoryFilter)) return false;
    if (familyFilter && !context.familyIds.includes(familyFilter)) return false;
    if (clusterFilter && !context.clusterIds.includes(clusterFilter)) return false;
    return true;
  }).sort(function (left, right) {
    if (left.rank !== right.rank) return left.rank - right.rank;
    const typeCompared = ENTITY_LABELS[left.documentRecord.type].localeCompare(ENTITY_LABELS[right.documentRecord.type]);
    if (typeCompared) return typeCompared;
    const nameCompared = left.documentRecord.name.localeCompare(right.documentRecord.name, undefined, { numeric: true, sensitivity: "base" });
    return nameCompared || left.documentRecord.id.localeCompare(right.documentRecord.id);
  }).map(function (candidate) { return candidate.documentRecord; });

  searchActiveFilters.replaceChildren();
  if (route.q) searchActiveFilters.appendChild(activeFilter("Search", route.q));
  if (typeFilter) searchActiveFilters.appendChild(activeFilter("Type", ENTITY_LABELS[typeFilter]));
  if (categoryFilter) searchActiveFilters.appendChild(activeFilter("Category", entityName("category", getEntity("category", categoryFilter))));
  if (familyFilter) searchActiveFilters.appendChild(activeFilter("Subcategory", entityName("family", getEntity("family", familyFilter))));
  if (clusterFilter) searchActiveFilters.appendChild(activeFilter("Topic", entityName("cluster", getEntity("cluster", clusterFilter))));
  viewSummary.textContent = formatNumber(results.length) + " matching records";
  if (!results.length) {
    showEmpty("No records matched", "Try a broader phrase or remove a facet.");
    return;
  }
  if (!route.q && !typeFilter && !categoryFilter && !familyFilter && !clusterFilter) {
    viewContent.appendChild(cautionBox("Search scope", "With no criteria, the complete public map and episode catalog is shown.", "quiet"));
  }
  const grid = element("div", "map-card-grid search-results");
  viewContent.appendChild(grid);
  viewContent.appendChild(renderIncrementalCards(results, grid, function (documentRecord) { return searchResultCard(documentRecord, query); }, 60));
}

async function renderMethodology() {
  await ensureEpisodeDiscovery();
  const manifest = state.data.get("manifest.json");
  const counts = manifest.counts;
  const coverage = state.data.get("coverage.json");
  const qa = state.data.get("qa_report.json");
  const discoveryManifest = await ensureDiscoveryManifest();
  setHeader("Method and limits", "Methodology", "How the synthesis, support model, relationships, privacy boundary, release accounting, and discovery aids should be interpreted.", "Core schema " + manifest.schemaVersion + " · QA passed");
  setBreadcrumbs([{ label: "Methodology", current: true }]);
  const grid = element("div", "methodology-grid");
  const cards = [
    ["Canonical architecture", "The public hierarchy is Category → Subcategory → Topic: " + formatNumber(counts.categoryCount) + " categories, " + formatNumber(counts.familyCount) + " subcategories, and " + formatNumber(counts.clusterCount) + " topics. The cross-cutting layer contains " + formatNumber(counts.themeCount) + " themes, " + formatNumber(counts.tensionCount) + " tensions, " + formatNumber(counts.narrativeCount) + " narratives, and " + formatNumber(counts.scenarioCount) + " scenarios."],
    ["Corpus accounting", "This is one practitioner podcast corpus. " + formatNumber(counts.publicReleaseCount) + " public releases represent " + formatNumber(counts.canonicalContentUnitCount) + " canonical content units. The selected canonical corpus contains " + formatNumber(counts.canonicalItemCount) + " items, including " + formatNumber(counts.canonicalFocalItemCount) + " focal and " + formatNumber(counts.canonicalContextualItemCount) + " contextual items. Duplicate-source analytical weight was removed. Separately, one shared-content rerelease inherits public coverage but adds zero analytical weight."],
    ["Synthesis process", "The analytical architecture is a human-guided, AI-assisted synthesis. Governed definitions, boundaries, assignments, adjudications, and validation constrain the synthesis; human review remains responsible for analytical judgment."],
    ["Distinct evidence pipelines", "Transcript → public episode summary is the release-reading pipeline. Structured qualitative analysis → analytical map relationships is the synthesis pipeline. Episode summaries do not independently generate or validate map relationships."],
    ["Two support layers", "Primary support represents the governed evidence designated as primary for an entity; its evidence path depends on entity type. A cluster traces to directly coded items, while higher-order entities trace through their governed supporting constructs or, for tensions, directly allocated pole evidence. Broader traceable reach reports items, derived items, content units, public releases, inherited coverage, clusters, families, category breadth, and concentration. No composite evidence score is produced. " + SUPPORT_INTERPRETATION],
    ["Episode discovery", "Main topics require at least two primary coded items and at least a 0.05 share of an episode's governed weighted topic count; up to six are shown by default. Similar overall uses all qualifying topics across " + formatNumber(discoveryManifest.counts.contentUnitCount) + " unique content units, normalized IDF-weighted Jaccard, at least two shared topics, and a 0.15 minimum. Recommendations are browsing aids, not evidence edges or claims of agreement."],
    ["Verified episode metadata", formatNumber(discoveryManifest.counts.verifiedPublishedDateCount) + " of " + formatNumber(counts.publicReleaseCount) + " releases have a verified publisher date, " + formatNumber(discoveryManifest.counts.verifiedGuestLineCount) + " have a verified guest line, and " + formatNumber(discoveryManifest.counts.verifiedSourceUrlCount) + " have a verified official source URL. Missing values remain unavailable rather than guessed."],
    ["Theme heatmap", "The 11 × 7 matrix reports normalized primary-support breadth. Only primary-theme-support relationships contribute. Secondary support, conceptual framing, and future extension remain visible elsewhere but do not inflate heatmap breadth."],
    ["Tension interpretation", "Tensions are neutral two-pole constructs. Pole balance describes this corpus and does not declare a winner. Theme filters use a labelled contextual connection derived from shared governed cluster support; that connection is not direct tension evidence."],
    ["Scenarios", "Scenarios are plausible analytical constructions, not forecasts, causal models, permissions, or validated recommendations. Triggers, branch points, indicators, counter-signposts, mitigations, and response options preserve uncertainty. SC-04 carries an additional public governance and rights notice."],
    ["Public relationship paths", "Relationships and release-level provenance load only when a view needs them. The explorer shows one bidirectional navigation slice at a time, labels its semantic role, asserts no causal arrow, and stops at public releases."],
    ["Public / private boundary", "The Explorer presents the governed canonical architecture only. Public records include canonical definitions, syntheses, aggregate support, semantic relationships, release-level aggregate provenance, and transcript-grounded release summaries. They exclude transcript text, source identities, item IDs and text, quotations, speakers, local paths, internal lineage and migration records, adjudication rationale, raw model output, and review queues. Private provenance remains preserved and reproducible behind this public boundary."],
    ["Determinism and QA", "The manifest fixes the schema, file allowlist, and counts. Browser validation rejects unexpected files, unresolved endpoints, duplicate IDs, incomplete heatmap cells, causal relationship claims, unexpected private fields, and a QA report that has not passed."],
  ];
  cards.forEach(function (entry) {
    const card = element("article", "methodology-card");
    card.appendChild(element("h3", null, entry[0]));
    card.appendChild(element("p", null, entry[1]));
    grid.appendChild(card);
  });
  viewContent.appendChild(grid);
  if (coverage && coverage.supportModel && coverage.supportModel.interpretation) {
    viewContent.appendChild(cautionBox("Coverage interpretation", coverage.supportModel.interpretation, "quiet"));
  }
  viewContent.appendChild(cautionBox("Mandatory support interpretation", SUPPORT_INTERPRETATION, "warning"));
  viewContent.appendChild(element("p", "quiet-note", "Build status: " + (qa.status || "pass") + ". Public schema: " + manifest.schemaVersion + "."));
}

const RENDERERS = Object.freeze({
  start: renderStart,
  families: renderFamilies,
  category: renderCategory,
  family: renderFamily,
  cluster: renderCluster,
  themes: renderThemes,
  theme: renderTheme,
  tensions: renderTensions,
  tension: renderTension,
  narratives: renderNarratives,
  narrative: renderNarrative,
  scenarios: renderScenarios,
  scenario: renderScenario,
  episodes: renderEpisodes,
  episode: renderEpisode,
  search: renderSearch,
  methodology: renderMethodology,
});

async function renderRoute(options) {
  if (!state.initialized) return;
  const settings = options || {};
  const token = ++state.renderToken;
  const resolved = await canonicalizeRoute(parseRoute());
  if (token !== state.renderToken) return;
  const route = resolved.route;
  if (resolved.replace) history.replaceState({ route: route }, "", new URL(routeHref(route), window.location.href));
  clearSurface();
  landingHero.hidden = route.view !== "start";
  viewHeader.hidden = route.view === "start";
  viewToolbar.hidden = route.view === "start";
  updateActiveNavigation(route.view);
  if (resolved.notice) showNotice(resolved.notice);
  viewContent.hidden = false;
  viewContent.setAttribute("aria-busy", "true");
  try {
    await RENDERERS[route.view](route);
    if (token !== state.renderToken) return;
    renderCopyLinkAction(route);
    viewContent.setAttribute("aria-busy", "false");
    if (settings.focus !== false) focusViewHeading();
    appStatus.textContent = viewTitle.textContent + " loaded.";
  } catch (error) {
    if (token !== state.renderToken) return;
    viewContent.replaceChildren(cautionBox("This view could not be displayed", error.message, "warning"));
    viewContent.setAttribute("aria-busy", "false");
    appStatus.textContent = "The requested view could not be displayed.";
    console.error(error);
  }
}

function installEventHandlers() {
  document.addEventListener("click", function (event) {
    const anchor = event.target.closest("a[data-app-route], a[data-route-view], a[data-view-link]");
    if (!anchor) {
      const action = event.target.closest("[data-action]");
      if (action && action.dataset.action === "retry-load") window.location.reload();
      return;
    }
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || (anchor.target && anchor.target !== "_self")) return;
    event.preventDefault();
    if (anchor.dataset.appRoute) navigate(parseRoute(anchor.href));
    else navigate({ view: anchor.dataset.routeView || anchor.dataset.viewLink || "start" });
  });

  globalSearchForm.addEventListener("submit", function (event) {
    event.preventDefault();
    navigate({ view: "search", q: globalSearchInput.value.trim() });
  });
  searchForm.addEventListener("submit", function (event) {
    event.preventDefault();
    navigate({
      view: "search",
      q: searchInput.value.trim(),
      type: searchEntityType.value,
      category: searchCategory.value,
      family: searchFamily.value,
      cluster: searchCluster.value,
    });
  });
  searchForm.addEventListener("change", function (event) {
    if (!state.initialized || parseRoute().view !== "search" || event.target === searchInput) return;
    navigate({
      view: "search",
      q: searchInput.value.trim(),
      type: searchEntityType.value,
      category: searchCategory.value,
      family: searchFamily.value,
      cluster: searchCluster.value,
    }, { focus: false });
  });
  searchClear.addEventListener("click", function () { navigate({ view: "search" }); });
  window.addEventListener("popstate", function () { renderRoute({ focus: true }); });
}

async function initialize() {
  try {
    setLoading(true);
    const manifest = await fetchPublicJson("manifest.json");
    validateManifest(manifest);
    const iconPromise = ensureIconRegistry();
    const payloads = await Promise.all(EAGER_PUBLIC_FILES.map(fetchPublicJson));
    EAGER_PUBLIC_FILES.forEach(function (fileName, index) { state.data.set(fileName, payloads[index]); });
    validateInitialData();
    buildIndexes();
    await iconPromise;
    populateSearchFilters();
    updateHeroStats();
    state.initialized = true;
    loadError.hidden = true;
    setLoading(false);
    await renderRoute({ focus: false });
  } catch (error) {
    console.error(error);
    showLoadError(error);
  }
}

installEventHandlers();
initialize();
