"use strict";

const DATA_BASE = "../data/cognitive-security/";
const PUBLIC_DATA_FILES = Object.freeze([
  "manifest.json",
  "corpus_reconciliation.json",
  "categories.json",
  "clusters.json",
  "cluster_summaries.json",
  "meta_clusters.json",
  "themes.json",
  "tensions.json",
  "meta_narratives.json",
  "category_findings.json",
  "scenarios.json",
  "episodes.json",
  "episode_summaries.json",
  "episode_relationships.json",
  "relationships.json",
  "coverage.json",
  "review_summary.json",
  "qa_report.json",
]);
const DEEP_LINK_ENTITY_TYPES = Object.freeze(["category", "metaCluster", "cluster", "theme", "tension", "metaNarrative", "categoryFinding", "scenario", "episode"]);
const ENTITY_ROUTES = Object.freeze({
  category: "category",
  metaCluster: "meta-cluster",
  cluster: "cluster",
  theme: "theme",
  tension: "tension",
  metaNarrative: "meta-narrative",
  categoryFinding: "category-finding",
  scenario: "scenario",
  episode: "episode",
});
const ROUTE_ENTITIES = Object.freeze(
  Object.fromEntries(Object.entries(ENTITY_ROUTES).map(function (entry) {
    return [entry[1], entry[0]];
  }))
);
const PRIMARY_VIEWS = Object.freeze([
  "overview", "browse", "themes", "tensions", "narratives", "scenarios",
  "episodes", "search", "methodology",
]);
const SEARCH_ENTITY_TYPES = Object.freeze([
  "category", "metaCluster", "cluster", "theme", "tension",
  "metaNarrative", "scenario", "episode",
]);
const SEARCH_TYPE_LABELS = Object.freeze({
  category: "Categories",
  metaCluster: "Meta-clusters",
  cluster: "Clusters",
  theme: "Themes",
  tension: "Tensions",
  metaNarrative: "Narratives",
  scenario: "Scenarios",
  episode: "Episodes",
});
const ENTITY_LABELS = Object.freeze({
  category: "Category",
  metaCluster: "Meta-cluster",
  cluster: "Intermediate cluster",
  theme: "Cross-cutting theme",
  tension: "Tension / debate",
  metaNarrative: "Meta-narrative",
  categoryFinding: "Category finding",
  scenario: "Future scenario",
  episode: "Episode",
});
const ENTITY_INDEX_VIEWS = Object.freeze({
  category: "browse",
  metaCluster: "browse",
  cluster: "browse",
  theme: "themes",
  tension: "tensions",
  metaNarrative: "narratives",
  categoryFinding: "browse",
  scenario: "scenarios",
  episode: "episodes",
});
const ENTITY_INDEX_LABELS = Object.freeze({
  browse: "Browse the map",
  episodes: "Episodes",
  themes: "Cross-cutting themes",
  tensions: "Tensions & debates",
  narratives: "Meta-narratives",
  scenarios: "Future scenarios",
  search: "Search the public map",
});
const RELATIONSHIP_SCHEMA = Object.freeze({
  "cluster-belongs-to-category": ["cluster", "category"],
  "meta-cluster-belongs-to-category": ["metaCluster", "category"],
  "cluster-belongs-to-meta-cluster": ["cluster", "metaCluster"],
  "theme-connects-meta-cluster": ["theme", "metaCluster"],
  "theme-supported-by-cluster": ["theme", "cluster"],
  "tension-maps-to-cross-cutting-theme": ["tension", "theme"],
  "tension-maps-to-meta-cluster": ["tension", "metaCluster"],
});
const EPISODE_RELATIONSHIP_SCHEMA = Object.freeze({
  "episode-participates-in-category": ["category", "direct-item-aggregation"],
  "episode-coded-to-cluster": ["cluster", "direct-coded-relationship"],
  "episode-derived-to-meta-cluster": ["metaCluster", "derived-through-cluster-membership"],
  "episode-derived-to-theme": ["theme", "derived-analytical-connection"],
  "episode-has-theme-lineage": ["theme", "direct-item-lineage"],
  "episode-has-tension-lineage": ["tension", "direct-item-lineage"],
});
const DEFAULT_TITLE = "PSYWERX Cognitive Security Practitioner Discourse Map";

const $ = function (selector) { return document.querySelector(selector); };
const viewNavigation = $("#view-navigation");
const appStatus = $("#app-status");
const loadingState = $("#loading-state");
const loadError = $("#load-error");
const loadErrorMessage = $("#load-error-message");
const linkNotice = $("#link-notice");
const emptyState = $("#empty-state");
const emptyStateTitle = $("#empty-state-title");
const emptyStateMessage = $("#empty-state-message");
const mapApp = $("#map-app");
const viewBreadcrumbs = $("#view-breadcrumbs");
const viewKicker = $("#view-kicker");
const viewTitle = $("#view-title");
const viewDescription = $("#view-description");
const viewSummary = $("#view-summary");
const viewActions = $("#view-actions");
const viewContent = $("#view-content");
const searchControls = $("#search-controls");
const searchForm = $("#search-form");
const searchInput = $("#search-input");
const searchEntityType = $("#search-entity-type");
const searchCategory = $("#search-category");
const searchMetaCluster = $("#search-meta-cluster");
const searchCluster = $("#search-cluster");
const searchClear = $("#search-clear");
const searchActiveFilters = $("#search-active-filters");
const entityDialog = $("#entity-dialog");
const entityDialogClose = $("#entity-dialog-close");
const copyLinkButton = $("#copy-link");
const copyStatus = $("#copy-status");

const payloadCache = new Map();
const data = {};
const indexes = {};
let searchDocuments = [];
let initialized = false;
let routeRenderToken = 0;

function hasValue(value) {
  if (Array.isArray(value)) return value.length > 0;
  return value !== null && value !== undefined && String(value).trim() !== "";
}

function asArray(value) {
  if (Array.isArray(value)) return value.filter(hasValue);
  return hasValue(value) ? [value] : [];
}

function normalizeText(value) {
  return String(value || "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\s+/g, " ")
    .trim()
    .toLocaleLowerCase();
}

function formatNumber(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number.toLocaleString() : "0";
}

function sentenceCase(value) {
  const text = String(value || "").replace(/[_-]+/g, " ").trim();
  return text ? text.charAt(0).toUpperCase() + text.slice(1) : "";
}

function element(tagName, className, text) {
  const node = document.createElement(tagName);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = String(text);
  return node;
}

function fragment() {
  return document.createDocumentFragment();
}

function appendChildren(parent, children) {
  asArray(children).forEach(function (child) {
    if (child) parent.appendChild(child);
  });
  return parent;
}

function sortByName(records) {
  return records.slice().sort(function (left, right) {
    return String(left.name || left.episodeTitle || "").localeCompare(
      String(right.name || right.episodeTitle || ""),
      undefined,
      { sensitivity: "base", numeric: true }
    );
  });
}

function unique(values) {
  return Array.from(new Set(asArray(values)));
}

function truncate(value, limit) {
  const text = String(value || "").trim();
  if (text.length <= limit) return text;
  const shortened = text.slice(0, limit - 1);
  const boundary = shortened.lastIndexOf(" ");
  return shortened.slice(0, boundary > limit * 0.65 ? boundary : shortened.length) + "…";
}

function routeHref(route) {
  const params = new URLSearchParams();
  params.set("view", route.view || "overview");
  ["id", "q", "type", "category", "meta", "cluster"].forEach(function (key) {
    if (hasValue(route[key])) params.set(key, String(route[key]));
  });
  return "./?" + params.toString();
}

function entityHref(type, id) {
  return routeHref({ view: ENTITY_ROUTES[type], id: id });
}

function viewLink(view, label, className) {
  const link = element("a", className || "text-link", label);
  link.href = routeHref({ view: view });
  link.dataset.routeView = view;
  return link;
}

function entityLink(type, id, label, className) {
  const link = element("a", className || "entity-link", label || id);
  link.href = entityHref(type, id);
  link.dataset.entityType = type;
  link.dataset.entityId = id;
  return link;
}

function chip(text, modifier) {
  return element("span", "map-chip" + (modifier ? " map-chip--" + modifier : ""), text);
}

function entityChipList(type, ids, emptyMessage) {
  const wrapper = element("div", "entity-chip-list");
  const resolved = asArray(ids).map(function (id) {
    const record = getEntity(type, id);
    return record ? entityLink(type, id, entityName(type, record), "entity-chip") : null;
  }).filter(Boolean);
  if (resolved.length) appendChildren(wrapper, resolved);
  else if (emptyMessage) wrapper.appendChild(element("p", "quiet-note", emptyMessage));
  return wrapper;
}

function episodeSort(left, right) {
  const leftNumber = left.parsedEpisodeNumber;
  const rightNumber = right.parsedEpisodeNumber;
  if (hasValue(leftNumber) && hasValue(rightNumber) &&
      Number(leftNumber) !== Number(rightNumber)) {
    return Number(leftNumber) - Number(rightNumber);
  }
  if (hasValue(leftNumber)) return -1;
  if (hasValue(rightNumber)) return 1;
  return String(left.episodeTitle || "").localeCompare(String(right.episodeTitle || ""));
}

function episodeRelationshipsForTarget(targetType, targetId) {
  return relationshipsTo(targetType, targetId).filter(function (relationship) {
    return relationship.sourceType === "episode";
  }).sort(function (left, right) {
    return episodeSort(
      getEntity("episode", left.sourceId),
      getEntity("episode", right.sourceId)
    );
  });
}

function relationshipSupportLabel(relationship) {
  if (relationship.relationshipType === "episode-participates-in-category") {
    return formatNumber(relationship.itemCount) + " retained items";
  }
  if (relationship.relationshipType === "episode-coded-to-cluster") {
    return formatNumber(relationship.primaryCount) + " primary · " +
      formatNumber(relationship.secondaryCount) + " secondary · " +
      formatNumber(relationship.weightedCount) + " weighted";
  }
  if (relationship.relationshipType === "episode-derived-to-meta-cluster" ||
      relationship.targetType === "theme") {
    const prefix = relationship.relationshipSemantics === "direct-item-lineage"
      ? "Direct lineage · " + formatNumber(relationship.itemCount) + " items · "
      : "Derived · ";
    return prefix + formatNumber(relationship.weightedCount) + " weighted cluster support";
  }
  if (relationship.relationshipType === "episode-has-tension-lineage") {
    return formatNumber(relationship.itemCount) + " direct-lineage items";
  }
  return sentenceCase(relationship.relationshipSemantics || "semantic connection");
}

function episodeRelationshipList(relationships, targetType, emptyMessage) {
  const list = element("ul", "relationship-list");
  asArray(relationships).slice().sort(function (left, right) {
    return entityName(targetType, getEntity(targetType, left.targetId)).localeCompare(
      entityName(targetType, getEntity(targetType, right.targetId))
    );
  }).forEach(function (relationship) {
    const target = getEntity(targetType, relationship.targetId);
    if (!target) return;
    const item = element("li", "relationship-list__item");
    item.appendChild(entityLink(
      targetType,
      relationship.targetId,
      entityName(targetType, target)
    ));
    item.appendChild(element(
      "span", "relationship-list__meta", relationshipSupportLabel(relationship)
    ));
    list.appendChild(item);
  });
  if (!list.children.length) {
    list.appendChild(element("li", "quiet-note", emptyMessage));
  }
  return list;
}

function episodeCoverageSection(targetType, targetId, options) {
  const settings = options || {};
  const relationships = episodeRelationshipsForTarget(targetType, targetId);
  const block = element("section", "overview-section episode-coverage");
  block.appendChild(element("h2", "section-title", settings.title || "Episode coverage"));
  block.appendChild(element(
    "p", "section-intro",
    relationships.length
      ? formatNumber(relationships.length) +
        " canonical public-feed releases have the governed relationship shown below. " +
        (settings.caveat || "Counts describe corpus coverage, not importance or evidence strength.")
      : (settings.emptyMessage ||
        "No retained canonical episode has this direct or governed derived relationship. No link has been inferred.")
  ));
  if (!relationships.length) return block;

  const list = element("ul", "relationship-list relationship-list--episodes");
  const controls = element("div", "load-more-row");
  let visible = 12;
  function draw(focusControl) {
    list.replaceChildren();
    relationships.slice(0, visible).forEach(function (relationship) {
      const episode = getEntity("episode", relationship.sourceId);
      if (!episode) return;
      const item = element("li", "relationship-list__item");
      item.appendChild(entityLink("episode", episode.episodeId, episode.episodeTitle));
      item.appendChild(element(
        "span", "relationship-list__meta", relationshipSupportLabel(relationship)
      ));
      list.appendChild(item);
    });
    controls.replaceChildren();
    if (visible < relationships.length) {
      const more = element(
        "button", "text-button",
        "Show more related episodes (" +
          formatNumber(relationships.length - visible) + " remaining)"
      );
      more.type = "button";
      more.addEventListener("click", function () {
        visible += 12;
        draw(true);
      });
      controls.appendChild(more);
      if (focusControl) more.focus();
    } else if (focusControl && list.lastElementChild) {
      const lastLink = list.lastElementChild.querySelector("a");
      if (lastLink) lastLink.focus();
    }
  }
  draw(false);
  block.appendChild(list);
  block.appendChild(controls);
  return block;
}

function textList(values, ordered) {
  const list = element(ordered ? "ol" : "ul", ordered ? "numbered-list" : "plain-list");
  asArray(values).forEach(function (value) {
    const item = element("li");
    if (value instanceof Node) item.appendChild(value);
    else item.textContent = String(value);
    list.appendChild(item);
  });
  return list;
}

function section(title, content, className) {
  if (!hasValue(content) && !(content instanceof Node)) return null;
  const block = element("section", "detail-section" + (className ? " " + className : ""));
  block.appendChild(element("h3", "detail-section__title", title));
  if (content instanceof Node) block.appendChild(content);
  else block.appendChild(element("p", null, content));
  return block;
}

function definitionList(items, className) {
  const list = element("dl", className || "metadata-list");
  items.forEach(function (item) {
    if (!hasValue(item.value) && !(item.value instanceof Node)) return;
    const group = element("div");
    group.appendChild(element("dt", null, item.label));
    const value = element("dd");
    if (item.value instanceof Node) value.appendChild(item.value);
    else value.textContent = String(item.value);
    group.appendChild(value);
    list.appendChild(group);
  });
  return list;
}

function cardShell(kicker, titleNode, body, modifier) {
  const card = element("article", "map-card" + (modifier ? " map-card--" + modifier : ""));
  if (kicker) card.appendChild(element("p", "map-card__kicker", kicker));
  const heading = element("h3", "map-card__title");
  if (titleNode instanceof Node) heading.appendChild(titleNode);
  else heading.textContent = String(titleNode);
  card.appendChild(heading);
  if (body) {
    const copy = element("div", "map-card__body");
    if (body instanceof Node) copy.appendChild(body);
    else copy.appendChild(element("p", null, body));
    card.appendChild(copy);
  }
  return card;
}

function statCard(value, label, detail) {
  const card = element("div", "stat-card");
  card.appendChild(element("strong", "stat-card__value", formatNumber(value)));
  card.appendChild(element("span", "stat-card__label", label));
  if (detail) card.appendChild(element("span", "stat-card__detail", detail));
  return card;
}

function cautionBox(title, text, modifier, headingLevel) {
  const box = element("aside", "caution-box" + (modifier ? " caution-box--" + modifier : ""));
  box.appendChild(element(headingLevel || "h2", "caution-box__title", title));
  box.appendChild(element("p", null, text));
  return box;
}

function setHeader(kicker, title, description, summary) {
  viewKicker.textContent = kicker || "";
  viewTitle.textContent = title || "";
  viewDescription.textContent = description || "";
  viewDescription.hidden = !description;
  viewSummary.textContent = summary || "";
  viewSummary.hidden = !summary;
  document.title = title ? title + " | PSYWERX" : DEFAULT_TITLE;
}

function setBreadcrumbs(items) {
  viewBreadcrumbs.replaceChildren();
  if (!items || !items.length) {
    viewBreadcrumbs.hidden = true;
    return;
  }
  viewBreadcrumbs.hidden = false;
  const entries = [
    { label: "Cognitive Security Map", view: "overview" },
  ].concat(items);
  entries.forEach(function (item, index) {
    if (index) {
      viewBreadcrumbs.appendChild(element("span", "breadcrumb-separator", "›"));
    }
    if (item.current) {
      const current = element("span", "breadcrumb-current", item.label);
      current.setAttribute("aria-current", "page");
      viewBreadcrumbs.appendChild(current);
    } else if (item.type && item.id) {
      viewBreadcrumbs.appendChild(entityLink(item.type, item.id, item.label, "breadcrumb-link"));
    } else {
      viewBreadcrumbs.appendChild(viewLink(item.view, item.label, "breadcrumb-link"));
    }
  });
}

function showNotice(message) {
  linkNotice.textContent = message;
  linkNotice.hidden = false;
}

function clearNotice() {
  linkNotice.textContent = "";
  linkNotice.hidden = true;
}

function showEmpty(title, message) {
  emptyStateTitle.textContent = title;
  emptyStateMessage.textContent = message;
  emptyState.hidden = false;
}

function clearEmpty() {
  emptyState.hidden = true;
}

function setLoading(isLoading) {
  loadingState.hidden = !isLoading;
  viewContent.setAttribute("aria-busy", isLoading ? "true" : "false");
  if (isLoading) appStatus.textContent = "Loading the public Cognitive Security Map data.";
}

function showLoadError(error) {
  setLoading(false);
  loadErrorMessage.textContent = error && error.message
    ? error.message
    : "The public map data could not be loaded.";
  loadError.hidden = false;
  appStatus.textContent = "The Cognitive Security Map could not be loaded.";
}

function updateActiveNavigation(view) {
  document.querySelectorAll("[data-view-link]").forEach(function (link) {
    const isActive = link.dataset.viewLink === view ||
      (view === "theme" && link.dataset.viewLink === "themes") ||
      (view === "tension" && link.dataset.viewLink === "tensions") ||
      (view === "episode" && link.dataset.viewLink === "episodes") ||
      (view === "meta-narrative" && link.dataset.viewLink === "narratives") ||
      (view === "scenario" && link.dataset.viewLink === "scenarios") ||
      (["category", "meta-cluster", "cluster", "category-finding"].includes(view) &&
        link.dataset.viewLink === "browse");
    if (isActive) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
}

function focusViewHeading() {
  viewTitle.setAttribute("tabindex", "-1");
  window.requestAnimationFrame(function () {
    viewTitle.focus();
  });
}

function resetViewSurface() {
  clearEmpty();
  viewContent.replaceChildren();
  viewActions.replaceChildren();
  searchActiveFilters.replaceChildren();
  searchControls.hidden = true;
}

async function fetchPublicJson(fileName) {
  if (!PUBLIC_DATA_FILES.includes(fileName)) {
    throw new Error("Attempted to load a file outside the governed public package.");
  }
  if (!payloadCache.has(fileName)) {
    payloadCache.set(fileName, fetch(DATA_BASE + fileName, { cache: "default" })
      .then(function (response) {
        if (!response.ok) {
          throw new Error(fileName + " returned HTTP " + String(response.status) + ".");
        }
        return response.json();
      }));
  }
  return payloadCache.get(fileName);
}

function requireArray(fileName) {
  if (!Array.isArray(data[fileName])) {
    throw new Error(fileName + " does not contain the expected record array.");
  }
}

function uniqueIdMap(records, idField, label) {
  const map = new Map();
  records.forEach(function (record, index) {
    const id = record && record[idField];
    if (typeof id !== "string" || !id.trim()) {
      throw new Error(label + " record " + String(index + 1) + " has no stable ID.");
    }
    if (map.has(id)) throw new Error("Duplicate " + label + " ID: " + id + ".");
    map.set(id, record);
  });
  return map;
}

function validateReferenceList(record, field, targetMap, label) {
  asArray(record[field]).forEach(function (id) {
    if (!targetMap.has(id)) {
      throw new Error(label + " references unknown ID " + id + " in " + field + ".");
    }
  });
}

function sameStringSet(left, right) {
  const leftSet = new Set(asArray(left));
  const rightSet = new Set(asArray(right));
  return leftSet.size === rightSet.size &&
    Array.from(leftSet).every(function (value) { return rightSet.has(value); });
}

function validatePublicData() {
  const manifest = data["manifest.json"];
  if (!manifest || manifest.schemaVersion !== "1.1") {
    throw new Error("The public package does not use Cognitive Security Schema v1.1.");
  }
  if (manifest.productId !== "psywerx-cognitive-security-practitioner-discourse-map" ||
      manifest.knowledgeProductType !== "practitioner-discourse-map") {
    throw new Error("The public package manifest identifies an unexpected product.");
  }
  const manifestFiles = manifest.publicFiles;
  if (!Array.isArray(manifestFiles) ||
      !sameStringSet(manifestFiles, PUBLIC_DATA_FILES) ||
      manifestFiles.length !== PUBLIC_DATA_FILES.length) {
    throw new Error("The public package manifest does not match the governed file allowlist.");
  }
  [
    "categories.json", "clusters.json", "cluster_summaries.json",
    "meta_clusters.json", "themes.json", "tensions.json",
    "meta_narratives.json", "category_findings.json", "scenarios.json",
    "episodes.json", "episode_summaries.json", "episode_relationships.json",
    "relationships.json",
  ].forEach(requireArray);

  const qa = data["qa_report.json"];
  if (!qa || qa.schemaVersion !== "1.1" || qa.passed !== true ||
      !Array.isArray(qa.errors) || qa.errors.length ||
      !Array.isArray(qa.missingReferences) || qa.missingReferences.length ||
      !Array.isArray(qa.duplicateIds) || qa.duplicateIds.length ||
      !Array.isArray(qa.validationIssues) || !Array.isArray(qa.unresolvedMappings) ||
      !Array.isArray(qa.unresolvedThemeClusterEvidence) ||
      !qa.deterministicBuild || qa.deterministicBuild.status !== "pass" ||
      !qa.publicExportChecks || qa.publicExportChecks.status !== "pass" ||
      qa.publicExportChecks.positiveAllowlist !== true ||
      !Array.isArray(qa.publicExportChecks.errors) || qa.publicExportChecks.errors.length) {
    throw new Error("The governed QA report does not authorize this public package.");
  }
  const coverage = data["coverage.json"];
  const reconciliation = data["corpus_reconciliation.json"];
  const reviewSummary = data["review_summary.json"];
  if (!coverage || !coverage.totals || !coverage.itemsByCategory ||
      !coverage.primaryAssignmentsByCluster || !coverage.secondaryAssignmentsByCluster ||
      !coverage.originalAnalyticRelease || !coverage.reconciledSensitivityDataset) {
    throw new Error("coverage.json is missing required aggregate coverage fields.");
  }
  if (!reviewSummary || !reviewSummary.metaNarrativeCountIssue) {
    throw new Error("review_summary.json is missing governed review metadata.");
  }
  if (!reconciliation || reconciliation.schemaVersion !== "1.1" ||
      reconciliation.status !== "complete" || !reconciliation.counts ||
      reconciliation.counts.pendingDecisionRecords !== 0) {
    throw new Error("corpus_reconciliation.json does not authorize a canonical public episode count.");
  }

  const entityMaps = {
    category: uniqueIdMap(data["categories.json"], "categoryId", "Category"),
    cluster: uniqueIdMap(data["clusters.json"], "clusterId", "Cluster"),
    metaCluster: uniqueIdMap(data["meta_clusters.json"], "metaClusterId", "Meta-cluster"),
    theme: uniqueIdMap(data["themes.json"], "themeId", "Theme"),
    tension: uniqueIdMap(data["tensions.json"], "tensionId", "Tension"),
    metaNarrative: uniqueIdMap(data["meta_narratives.json"], "narrativeId", "Meta-narrative"),
    categoryFinding: uniqueIdMap(data["category_findings.json"], "findingId", "Finding"),
    scenario: uniqueIdMap(data["scenarios.json"], "scenarioId", "Scenario"),
    episode: uniqueIdMap(data["episodes.json"], "episodeId", "Episode"),
  };
  const summaryMap = uniqueIdMap(
    data["cluster_summaries.json"], "clusterId", "Cluster summary"
  );
  if (summaryMap.size !== entityMaps.cluster.size) {
    throw new Error("Every public Cluster must have exactly one Cluster summary.");
  }
  const episodeSummaryMap = uniqueIdMap(
    data["episode_summaries.json"], "episodeId", "Episode summary"
  );
  if (episodeSummaryMap.size !== entityMaps.episode.size) {
    throw new Error("Every canonical public Episode must have exactly one grounded summary.");
  }
  data["episodes.json"].forEach(function (episode) {
    const summary = episodeSummaryMap.get(episode.episodeId);
    if (!summary || !String(summary.summary || "").trim() ||
        !String(summary.whyItMatters || "").trim() ||
        asArray(summary.keyTopics).length < 3 || asArray(summary.keyTopics).length > 6 ||
        Number(summary.sourceItemCount) <= 0 ||
        Number(summary.sourceItemCount) !== Number(summary.focalItemCount) +
          Number(summary.contextualItemCount) ||
        Number(summary.sourceItemCount) !== Number(episode.reconciledSensitivityItemCount)) {
      throw new Error("Episode summary grounding metadata is invalid for " + episode.episodeId + ".");
    }
  });

  data["clusters.json"].forEach(function (record) {
    if (!entityMaps.category.has(record.categoryId)) {
      throw new Error("Cluster " + record.clusterId + " has an unresolved Category.");
    }
    const summary = summaryMap.get(record.clusterId);
    if (!summary || summary.categoryId !== record.categoryId ||
        summary.clusterName !== record.name) {
      throw new Error("Cluster summary identity does not match " + record.clusterId + ".");
    }
  });
  const metaByCluster = new Map();
  data["meta_clusters.json"].forEach(function (record) {
    if (!entityMaps.category.has(record.categoryId)) {
      throw new Error("Meta-cluster " + record.metaClusterId + " has an unresolved Category.");
    }
    asArray(record.includedClusterIds).forEach(function (id) {
      const cluster = entityMaps.cluster.get(id);
      if (!cluster) {
        throw new Error("Meta-cluster " + record.metaClusterId + " references an unknown Cluster.");
      }
      if (cluster.categoryId !== record.categoryId) {
        throw new Error("Meta-cluster " + record.metaClusterId + " crosses Category boundaries.");
      }
      if (metaByCluster.has(id)) {
        throw new Error("Cluster " + id + " belongs to more than one Meta-cluster.");
      }
      metaByCluster.set(id, record.metaClusterId);
    });
  });

  data["themes.json"].forEach(function (record) {
    validateReferenceList(record, "categoryIds", entityMaps.category, "Theme " + record.themeId);
    validateReferenceList(record, "linkedClusterIds", entityMaps.cluster, "Theme " + record.themeId);
    validateReferenceList(record, "linkedMetaClusterIds", entityMaps.metaCluster, "Theme " + record.themeId);
    validateReferenceList(record, "relatedTensionIds", entityMaps.tension, "Theme " + record.themeId);
  });
  data["tensions.json"].forEach(function (record) {
    validateReferenceList(record, "categoryIds", entityMaps.category, "Tension " + record.tensionId);
    validateReferenceList(record, "clusterIds", entityMaps.cluster, "Tension " + record.tensionId);
  });
  data["meta_narratives.json"].forEach(function (record) {
    const label = "Meta-narrative " + record.narrativeId;
    validateReferenceList(record, "categoryIds", entityMaps.category, label);
    validateReferenceList(record, "supportingThemeIds", entityMaps.theme, label);
    validateReferenceList(record, "supportingTensionIds", entityMaps.tension, label);
    validateReferenceList(record, "supportingMetaClusterIds", entityMaps.metaCluster, label);
  });
  data["category_findings.json"].forEach(function (record) {
    const label = "Category finding " + record.findingId;
    validateReferenceList(record, "categoryId", entityMaps.category, label);
    validateReferenceList(record, "supportingClusterIds", entityMaps.cluster, label);
    validateReferenceList(record, "supportingMetaClusterIds", entityMaps.metaCluster, label);
  });
  data["scenarios.json"].forEach(function (record) {
    const label = "Scenario " + record.scenarioId;
    validateReferenceList(record, "categoryIds", entityMaps.category, label);
    validateReferenceList(record, "themeIds", entityMaps.theme, label);
    validateReferenceList(record, "tensionIds", entityMaps.tension, label);
  });

  const qaUnmappedClusterIds = qa.unresolvedMappings.filter(function (record) {
    return hasValue(record.clusterId);
  }).map(function (record) { return record.clusterId; });
  const actualUnmappedClusterIds = data["clusters.json"].filter(function (record) {
    return !metaByCluster.has(record.clusterId);
  }).map(function (record) { return record.clusterId; });
  if (!sameStringSet(qaUnmappedClusterIds, actualUnmappedClusterIds)) {
    throw new Error("Governed unmapped Cluster records do not match the hierarchy.");
  }
  const qaEmptyMetaIds = asArray(qa.metaClustersWithoutMappingRows).map(function (record) {
    return record.metaClusterId;
  });
  const actualEmptyMetaIds = data["meta_clusters.json"].filter(function (record) {
    return !asArray(record.includedClusterIds).length;
  }).map(function (record) { return record.metaClusterId; });
  if (!sameStringSet(qaEmptyMetaIds, actualEmptyMetaIds)) {
    throw new Error("Governed empty Meta-cluster records do not match the hierarchy.");
  }

  const expectedTotals = {
    categories: entityMaps.category.size,
    clusters: entityMaps.cluster.size,
    meta_clusters: entityMaps.metaCluster.size,
    themes: entityMaps.theme.size,
    tensions: entityMaps.tension.size,
    meta_narratives: entityMaps.metaNarrative.size,
    scenarios: entityMaps.scenario.size,
    episodes: entityMaps.episode.size,
  };
  Object.entries(expectedTotals).forEach(function (entry) {
    const coverageHasTotal = Object.prototype.hasOwnProperty.call(
      coverage.totals, entry[0]
    );
    if ((coverageHasTotal && Number(coverage.totals[entry[0]]) !== entry[1]) ||
        Number(qa.counts && qa.counts[entry[0]]) !== entry[1]) {
      throw new Error("Governed count mismatch for " + entry[0] + ".");
    }
  });
  if (Number(reconciliation.counts.canonicalEpisodes) !== entityMaps.episode.size ||
      Number(reconciliation.counts.originalSourceIdentities) !==
        Number(coverage.originalAnalyticRelease.sourceIdentities) ||
      Number(reconciliation.counts.originalItems) !==
        Number(coverage.originalAnalyticRelease.items) ||
      Number(reconciliation.counts.reconciledSensitivityItems) !==
        Number(coverage.reconciledSensitivityDataset.items)) {
    throw new Error("Corpus reconciliation counts do not match the governed public package.");
  }
  if (Number(reviewSummary.metaNarrativeCountIssue.currentSourceActual) !==
      entityMaps.metaNarrative.size) {
    throw new Error("The governed Meta-narrative review count is inconsistent.");
  }
  if (!sameStringSet(Object.keys(coverage.itemsByCategory), Array.from(entityMaps.category.keys())) ||
      !sameStringSet(Object.keys(coverage.primaryAssignmentsByCluster), Array.from(entityMaps.cluster.keys())) ||
      !sameStringSet(Object.keys(coverage.secondaryAssignmentsByCluster), Array.from(entityMaps.cluster.keys()))) {
    throw new Error("Coverage keys do not match the governed Category and Cluster IDs.");
  }
  const itemTotal = Object.values(coverage.itemsByCategory).reduce(function (total, value) {
    return total + Number(value || 0);
  }, 0);
  const focalItemTotal = data["categories.json"].filter(function (record) {
    return record.scope === "focal";
  }).reduce(function (total, record) {
    return total + Number(coverage.itemsByCategory[record.categoryId] || 0);
  }, 0);
  if (itemTotal !== Number(coverage.totals.items) || itemTotal !== Number(qa.counts.items) ||
      focalItemTotal !== Number(qa.counts.focal_items) ||
      Number(qa.counts.cluster_summaries) !== summaryMap.size ||
      Number(qa.counts.category_findings) !== entityMaps.categoryFinding.size) {
    throw new Error("Aggregate public-package counts do not match governed QA.");
  }

  const relationshipIds = new Set();
  const relationshipKeys = new Set();
  data["relationships.json"].forEach(function (relationship) {
    const contract = RELATIONSHIP_SCHEMA[relationship.relationshipType];
    if (!contract) {
      throw new Error("Unsupported public relationship type: " + relationship.relationshipType + ".");
    }
    if (relationshipIds.has(relationship.relationshipId)) {
      throw new Error("Duplicate public relationship ID: " + relationship.relationshipId + ".");
    }
    relationshipIds.add(relationship.relationshipId);
    if (relationship.sourceType !== contract[0] || relationship.targetType !== contract[1]) {
      throw new Error("Relationship " + relationship.relationshipId + " has invalid endpoint types.");
    }
    if (relationship.interpretation !== "semantic") {
      throw new Error("Relationship " + relationship.relationshipId + " is not explicitly semantic.");
    }
    if (!entityMaps[relationship.sourceType].has(relationship.sourceId) ||
        !entityMaps[relationship.targetType].has(relationship.targetId)) {
      throw new Error("Relationship " + relationship.relationshipId + " has an unresolved endpoint.");
    }
    const key = [
      relationship.relationshipType,
      relationship.sourceType + ":" + relationship.sourceId,
      relationship.targetType + ":" + relationship.targetId,
    ].join("|");
    if (relationshipKeys.has(key)) {
      throw new Error("Duplicate public semantic relationship endpoints: " + key + ".");
    }
    relationshipKeys.add(key);
  });

  const episodeRelationshipIds = new Set();
  data["episode_relationships.json"].forEach(function (relationship) {
    const contract = EPISODE_RELATIONSHIP_SCHEMA[relationship.relationshipType];
    if (!contract) {
      throw new Error(
        "Unsupported standalone episode relationship type: " +
        relationship.relationshipType + "."
      );
    }
    if (episodeRelationshipIds.has(relationship.relationshipId)) {
      throw new Error("Duplicate episode relationship ID: " + relationship.relationshipId + ".");
    }
    episodeRelationshipIds.add(relationship.relationshipId);
    if (relationship.sourceType !== "episode" ||
        relationship.targetType !== contract[0] ||
        relationship.relationshipSemantics !== contract[1] ||
        !entityMaps.episode.has(relationship.sourceId) ||
        !entityMaps[relationship.targetType].has(relationship.targetId)) {
      throw new Error(
        "Episode relationship " + relationship.relationshipId +
        " has invalid semantics or an unresolved endpoint."
      );
    }
    if (relationship.relationshipType === "episode-coded-to-cluster") {
      const primary = Number(relationship.primaryCount || 0);
      const secondary = Number(relationship.secondaryCount || 0);
      if (primary + secondary <= 0 ||
          Number(relationship.weightedCount) !== 2 * primary + secondary) {
        throw new Error(
          "Episode cluster relationship " + relationship.relationshipId +
          " has invalid support counts."
        );
      }
    }
  });

  function requireRelationship(type, sourceType, sourceId, targetType, targetId) {
    const key = [type, sourceType + ":" + sourceId, targetType + ":" + targetId].join("|");
    if (!relationshipKeys.has(key)) {
      throw new Error("Missing public semantic relationship: " + key + ".");
    }
  }
  data["clusters.json"].forEach(function (record) {
    requireRelationship(
      "cluster-belongs-to-category", "cluster", record.clusterId,
      "category", record.categoryId
    );
  });
  data["meta_clusters.json"].forEach(function (record) {
    requireRelationship(
      "meta-cluster-belongs-to-category", "metaCluster", record.metaClusterId,
      "category", record.categoryId
    );
    asArray(record.includedClusterIds).forEach(function (clusterId) {
      requireRelationship(
        "cluster-belongs-to-meta-cluster", "cluster", clusterId,
        "metaCluster", record.metaClusterId
      );
    });
  });
  data["themes.json"].forEach(function (record) {
    asArray(record.linkedClusterIds).forEach(function (clusterId) {
      requireRelationship(
        "theme-supported-by-cluster", "theme", record.themeId,
        "cluster", clusterId
      );
    });
    asArray(record.linkedMetaClusterIds).forEach(function (metaClusterId) {
      requireRelationship(
        "theme-connects-meta-cluster", "theme", record.themeId,
        "metaCluster", metaClusterId
      );
    });
  });
}

function buildIndexes() {
  indexes.episodeSummary = uniqueIdMap(
    data["episode_summaries.json"], "episodeId", "Episode summary"
  );
  data["episodes.json"].forEach(function (episode) {
    Object.assign(episode, indexes.episodeSummary.get(episode.episodeId));
  });
  indexes.category = uniqueIdMap(data["categories.json"], "categoryId", "Category");
  indexes.cluster = uniqueIdMap(data["clusters.json"], "clusterId", "Cluster");
  indexes.clusterSummary = uniqueIdMap(
    data["cluster_summaries.json"], "clusterId", "Cluster summary"
  );
  indexes.metaCluster = uniqueIdMap(
    data["meta_clusters.json"], "metaClusterId", "Meta-cluster"
  );
  indexes.theme = uniqueIdMap(data["themes.json"], "themeId", "Theme");
  indexes.tension = uniqueIdMap(data["tensions.json"], "tensionId", "Tension");
  indexes.metaNarrative = uniqueIdMap(
    data["meta_narratives.json"], "narrativeId", "Meta-narrative"
  );
  indexes.categoryFinding = uniqueIdMap(
    data["category_findings.json"], "findingId", "Finding"
  );
  indexes.scenario = uniqueIdMap(data["scenarios.json"], "scenarioId", "Scenario");
  indexes.episode = uniqueIdMap(data["episodes.json"], "episodeId", "Episode");
  indexes.clustersByCategory = new Map();
  indexes.metasByCategory = new Map();
  indexes.findingsByCategory = new Map();
  indexes.metaByCluster = new Map();
  indexes.relationshipsBySource = new Map();
  indexes.relationshipsByTarget = new Map();
  const qa = data["qa_report.json"];
  indexes.governedUnmappedClusters = qa.unresolvedMappings.filter(function (record) {
    return hasValue(record.clusterId);
  });
  indexes.unmappedClusterIds = new Set(
    indexes.governedUnmappedClusters.map(function (record) { return record.clusterId; })
  );
  indexes.governedEmptyMetaClusters = asArray(qa.metaClustersWithoutMappingRows);
  indexes.emptyMetaClusterIds = new Set(
    indexes.governedEmptyMetaClusters.map(function (record) {
      return record.metaClusterId;
    })
  );
  const focalCategoryRecords = data["categories.json"].filter(function (record) {
    return record.scope === "focal";
  });
  const contextualCategoryRecords = data["categories.json"].filter(function (record) {
    return record.scope === "contextual";
  });
  const coverageByCategory = data["coverage.json"].itemsByCategory;
  const reconciliationCounts = data["corpus_reconciliation.json"].counts;
  indexes.counts = Object.freeze({
    categories: data["categories.json"].length,
    focalCategories: focalCategoryRecords.length,
    contextualCategories: contextualCategoryRecords.length,
    clusters: data["clusters.json"].length,
    metaClusters: data["meta_clusters.json"].length,
    themes: data["themes.json"].length,
    tensions: data["tensions.json"].length,
    metaNarratives: data["meta_narratives.json"].length,
    categoryFindings: data["category_findings.json"].length,
    scenarios: data["scenarios.json"].length,
    episodes: data["episodes.json"].length,
    sourceIdentities: Number(reconciliationCounts.originalSourceIdentities),
    confirmedAliasGroups: Number(reconciliationCounts.confirmedAliasGroups),
    sensitivityItems: Number(reconciliationCounts.reconciledSensitivityItems),
    sensitivityFocalItems: Number(
      reconciliationCounts.reconciledSensitivityFocalItems
    ),
    sensitivityContextualItems: Number(
      reconciliationCounts.reconciledSensitivityContextualItems
    ),
    relationships: data["relationships.json"].length,
    episodeRelationships: data["episode_relationships.json"].length,
    items: Object.values(coverageByCategory).reduce(function (total, value) {
      return total + Number(value || 0);
    }, 0),
    focalItems: focalCategoryRecords.reduce(function (total, record) {
      return total + Number(coverageByCategory[record.categoryId] || 0);
    }, 0),
    contextualItems: contextualCategoryRecords.reduce(function (total, record) {
      return total + Number(coverageByCategory[record.categoryId] || 0);
    }, 0),
  });

  data["clusters.json"].forEach(function (record) {
    if (!indexes.clustersByCategory.has(record.categoryId)) {
      indexes.clustersByCategory.set(record.categoryId, []);
    }
    indexes.clustersByCategory.get(record.categoryId).push(record);
  });
  data["meta_clusters.json"].forEach(function (record) {
    if (!indexes.metasByCategory.has(record.categoryId)) {
      indexes.metasByCategory.set(record.categoryId, []);
    }
    indexes.metasByCategory.get(record.categoryId).push(record);
    asArray(record.includedClusterIds).forEach(function (id) {
      indexes.metaByCluster.set(id, record);
    });
  });
  data["category_findings.json"].forEach(function (record) {
    if (!indexes.findingsByCategory.has(record.categoryId)) {
      indexes.findingsByCategory.set(record.categoryId, []);
    }
    indexes.findingsByCategory.get(record.categoryId).push(record);
  });
  data["relationships.json"].concat(data["episode_relationships.json"]).forEach(function (record) {
    const sourceKey = record.sourceType + ":" + record.sourceId;
    const targetKey = record.targetType + ":" + record.targetId;
    if (!indexes.relationshipsBySource.has(sourceKey)) {
      indexes.relationshipsBySource.set(sourceKey, []);
    }
    if (!indexes.relationshipsByTarget.has(targetKey)) {
      indexes.relationshipsByTarget.set(targetKey, []);
    }
    indexes.relationshipsBySource.get(sourceKey).push(record);
    indexes.relationshipsByTarget.get(targetKey).push(record);
  });
  indexes.clustersByCategory.forEach(function (records) { sortByName(records); });
  indexes.metasByCategory.forEach(function (records) { sortByName(records); });
  indexes.findingsByCategory.forEach(function (records) { sortByName(records); });

  searchDocuments = buildSearchDocuments();
}

function getEntity(type, id) {
  return indexes[type] ? indexes[type].get(id) : null;
}

function entityId(type, record) {
  const fields = {
    category: "categoryId",
    metaCluster: "metaClusterId",
    cluster: "clusterId",
    theme: "themeId",
    tension: "tensionId",
    metaNarrative: "narrativeId",
    categoryFinding: "findingId",
    scenario: "scenarioId",
    episode: "episodeId",
  };
  return record ? record[fields[type]] : null;
}

function entityName(type, record) {
  if (!record) return "";
  return type === "episode" ? record.episodeTitle : record.name;
}

function relationshipsFrom(type, id, relationshipType) {
  return asArray(indexes.relationshipsBySource.get(type + ":" + id)).filter(
    function (record) {
      return !relationshipType || record.relationshipType === relationshipType;
    }
  );
}

function relationshipsTo(type, id, relationshipType) {
  return asArray(indexes.relationshipsByTarget.get(type + ":" + id)).filter(
    function (record) {
      return !relationshipType || record.relationshipType === relationshipType;
    }
  );
}

function relatedTargetIds(type, id, targetType, relationshipType) {
  return relationshipsFrom(type, id, relationshipType)
    .filter(function (record) { return record.targetType === targetType; })
    .map(function (record) { return record.targetId; });
}

function relatedSourceIds(type, id, sourceType, relationshipType) {
  return relationshipsTo(type, id, relationshipType)
    .filter(function (record) { return record.sourceType === sourceType; })
    .map(function (record) { return record.sourceId; });
}

function categoryIdsForRecord(type, record) {
  if (!record) return [];
  if (type === "category") return [record.categoryId];
  if (type === "episode") {
    return relatedTargetIds("episode", record.episodeId, "category");
  }
  if (type === "cluster" || type === "metaCluster" || type === "categoryFinding") {
    return record.categoryId ? [record.categoryId] : [];
  }
  return asArray(record.categoryIds);
}

function metaIdsForRecord(type, record) {
  if (!record) return [];
  if (type === "metaCluster") return [record.metaClusterId];
  if (type === "episode") {
    return relatedTargetIds("episode", record.episodeId, "metaCluster");
  }
  if (type === "cluster") {
    const meta = indexes.metaByCluster.get(record.clusterId);
    return meta ? [meta.metaClusterId] : [];
  }
  if (type === "theme") return asArray(record.linkedMetaClusterIds);
  if (type === "metaNarrative") return asArray(record.supportingMetaClusterIds);
  if (type === "categoryFinding") return asArray(record.supportingMetaClusterIds);
  if (type === "tension") {
    return relatedTargetIds("tension", record.tensionId, "metaCluster");
  }
  if (type === "category") {
    return asArray(indexes.metasByCategory.get(record.categoryId))
      .map(function (meta) { return meta.metaClusterId; });
  }
  return [];
}

function clusterIdsForRecord(type, record) {
  if (!record) return [];
  if (type === "cluster") return [record.clusterId];
  if (type === "episode") {
    return relatedTargetIds("episode", record.episodeId, "cluster");
  }
  if (type === "metaCluster") return asArray(record.includedClusterIds);
  if (type === "theme") return asArray(record.linkedClusterIds);
  if (type === "tension") return asArray(record.clusterIds);
  if (type === "categoryFinding") return asArray(record.supportingClusterIds);
  if (type === "category") {
    return asArray(indexes.clustersByCategory.get(record.categoryId))
      .map(function (cluster) { return cluster.clusterId; });
  }
  return [];
}

function buildSearchDocuments() {
  const specs = [
    ["category", data["categories.json"], ["name", "summary", "soWhat"]],
    ["cluster", data["clusters.json"], [
      "name", "definition", "inclusionCriteria", "exclusionCriteria",
      "nearNeighborDistinctions", "anchorExamples",
    ]],
    ["metaCluster", data["meta_clusters.json"], [
      "name", "definition", "categorySynthesis", "nearNeighborDistinctions",
    ]],
    ["theme", data["themes.json"], [
      "name", "definition", "crossCategoryLogic", "strategicSignificance",
      "operationalImplications", "boundaryConditions",
    ]],
    ["tension", data["tensions.json"], [
      "name", "description", "poleALabel", "poleAAssumption",
      "poleBLabel", "poleBAssumption",
    ]],
    ["metaNarrative", data["meta_narratives.json"], [
      "name", "shortVersion", "coreClaim", "strategicSignificance",
      "operationalImplications", "caveats",
    ]],
    ["categoryFinding", data["category_findings.json"], [
      "name", "coreFinding", "strategicSignificance",
      "operationalImplications", "unresolvedQuestions", "caveats",
    ]],
    ["scenario", data["scenarios.json"], [
      "name", "coreScenario", "drivingForces", "strategicImplications",
      "operationalImplications", "researchQuestions", "alternativeOutcomes",
    ]],
    ["episode", data["episodes.json"], [
      "episodeTitle", "podcast", "summary", "whyItMatters", "keyTopics",
    ]],
  ];
  const documents = [];
  specs.forEach(function (spec) {
    const type = spec[0];
    spec[1].forEach(function (record) {
      const fields = spec[2].flatMap(function (field) {
        return asArray(record[field]).map(function (value) {
          if (value && typeof value === "object") {
            return Object.values(value).filter(function (item) {
              return typeof item === "string" || typeof item === "number";
            }).join(" ");
          }
          return String(value);
        });
      }).filter(hasValue);
      if (type === "cluster") {
        const summary = indexes.clusterSummary.get(record.clusterId);
        if (summary) {
          [
            summary.summary, summary.strategicSignificance,
            summary.operationalImplications, summary.primarySecondaryDistinction,
          ].filter(hasValue).forEach(function (value) { fields.push(String(value)); });
          asArray(summary.recurringThemes).forEach(function (theme) {
            fields.push([theme.name, theme.description].filter(hasValue).join(" "));
          });
        }
      }
      const name = entityName(type, record);
      documents.push({
        type: type,
        id: entityId(type, record),
        name: name,
        record: record,
        categoryIds: categoryIdsForRecord(type, record),
        metaClusterIds: metaIdsForRecord(type, record),
        clusterIds: clusterIdsForRecord(type, record),
        fields: fields,
        normalizedName: normalizeText(name),
        normalizedText: normalizeText(fields.join(" ")),
      });
    });
  });
  return documents;
}

function populateSearchFilters() {
  function populate(select, records, valueField, labelField, firstLabel) {
    select.replaceChildren();
    const first = element("option", null, firstLabel);
    first.value = "";
    select.appendChild(first);
    sortByName(records).forEach(function (record) {
      const option = element("option", null, record[labelField]);
      option.value = record[valueField];
      select.appendChild(option);
    });
    select.disabled = false;
  }
  searchEntityType.replaceChildren();
  const allTypes = element("option", null, "All entity types");
  allTypes.value = "";
  searchEntityType.appendChild(allTypes);
  SEARCH_ENTITY_TYPES.forEach(function (type) {
    const option = element("option", null, SEARCH_TYPE_LABELS[type]);
    option.value = type;
    searchEntityType.appendChild(option);
  });
  searchEntityType.disabled = false;
  populate(
    searchCategory, data["categories.json"], "categoryId", "name", "All categories"
  );
  populate(
    searchMetaCluster, data["meta_clusters.json"],
    "metaClusterId", "name", "All meta-clusters"
  );
  populate(
    searchCluster, data["clusters.json"], "clusterId", "name", "All clusters"
  );
  [searchInput, searchClear].forEach(function (control) { control.disabled = false; });
}

function updateHeroStats() {
  const values = {
    "#total-episode-count": indexes.counts.episodes,
    "#total-item-count": indexes.counts.items,
    "#total-cluster-count": indexes.counts.clusters,
    "#total-theme-count": indexes.counts.themes,
  };
  Object.entries(values).forEach(function (entry) {
    const node = $(entry[0]);
    if (node) node.textContent = formatNumber(entry[1]);
  });
}

function parseRoute() {
  const params = new URL(window.location.href).searchParams;
  return {
    view: params.get("view") || "overview",
    id: params.get("id") || "",
    q: params.get("q") || "",
    type: params.get("type") || "",
    category: params.get("category") || "",
    meta: params.get("meta") || "",
    cluster: params.get("cluster") || "",
  };
}

function routeUrl(route) {
  return new URL(routeHref(route), window.location.href);
}

function navigate(route, options) {
  const settings = options || {};
  const url = routeUrl(route);
  if (settings.replace) history.replaceState({ route: route }, "", url);
  else history.pushState({ route: route }, "", url);
  return renderRoute({ focus: settings.focus !== false });
}

function fallbackInvalidRoute(message) {
  showNotice(message);
  const route = { view: "overview" };
  history.replaceState({ route: route }, "", routeUrl(route));
  renderOverview(route);
  updateActiveNavigation("overview");
  appStatus.textContent = message;
}

function renderMissingEntity(route, type) {
  const entityLabel = ENTITY_LABELS[type] || "Record";
  const indexView = ENTITY_INDEX_VIEWS[type] || "overview";
  const indexLabel = ENTITY_INDEX_LABELS[indexView] || "Return to the Overview";
  const message = "The requested " + entityLabel +
    " could not be found. No record has been inferred or substituted.";
  showNotice(message);
  setHeader(
    "Link not found",
    entityLabel + " not found",
    "The copied link may contain an incomplete or outdated stable ID.",
    route.id ? "Requested ID: " + route.id : "No stable ID was supplied"
  );
  setBreadcrumbs([
    { label: indexLabel, view: indexView },
    { label: entityLabel + " not found", current: true },
  ]);
  const recovery = cautionBox(
    "This record is not in the public package",
    message,
    "unresolved"
  );
  recovery.appendChild(viewLink(indexView, indexLabel, "secondary-button"));
  viewContent.appendChild(recovery);
  updateActiveNavigation(route.view);
  appStatus.textContent = message;
}

async function renderRoute(options) {
  if (!initialized) return;
  const token = ++routeRenderToken;
  const route = parseRoute();
  const settings = options || {};
  clearNotice();
  resetViewSurface();
  updateActiveNavigation(route.view);

  if (!PRIMARY_VIEWS.includes(route.view) && !ROUTE_ENTITIES[route.view] &&
      route.view !== "episode") {
    fallbackInvalidRoute("That Map view does not exist. The Overview is shown instead.");
    return;
  }
  if (ROUTE_ENTITIES[route.view] || route.view === "episode") {
    const type = ROUTE_ENTITIES[route.view];
    if (!route.id || !getEntity(type, route.id)) {
      renderMissingEntity(route, type);
      if (settings.focus !== false) focusViewHeading();
      return;
    }
  }

  const renderers = {
    overview: renderOverview,
    browse: renderBrowse,
    episodes: renderEpisodes,
    category: renderCategory,
    "meta-cluster": renderMetaCluster,
    cluster: renderCluster,
    themes: renderThemes,
    theme: renderTheme,
    tensions: renderTensions,
    tension: renderTension,
    narratives: renderNarratives,
    "meta-narrative": renderMetaNarrative,
    "category-finding": renderCategoryFinding,
    scenarios: renderScenarios,
    scenario: renderScenario,
    search: renderSearch,
    episode: renderEpisode,
    methodology: renderMethodology,
  };
  renderers[route.view](route);
  if (token !== routeRenderToken) return;
  if (route.id && ROUTE_ENTITIES[route.view]) {
    renderCopyLinkAction();
  }
  if (settings.focus !== false) focusViewHeading();
  appStatus.textContent = viewTitle.textContent + " loaded.";
}

async function initialize() {
  try {
    setLoading(true);
    const manifest = await fetchPublicJson("manifest.json");
    data["manifest.json"] = manifest;
    if (!manifest || manifest.schemaVersion !== "1.1") {
      throw new Error("The public manifest is missing Cognitive Security Schema v1.1.");
    }
    const remaining = PUBLIC_DATA_FILES.filter(function (file) {
      return file !== "manifest.json";
    });
    const payloads = await Promise.all(remaining.map(fetchPublicJson));
    remaining.forEach(function (file, index) { data[file] = payloads[index]; });
    validatePublicData();
    buildIndexes();
    populateSearchFilters();
    updateHeroStats();
    initialized = true;
    loadError.hidden = true;
    setLoading(false);
    await renderRoute({ focus: false });
  } catch (error) {
    console.error(error);
    showLoadError(error);
  }
}

function categoryCoverage(categoryId) {
  const coverage = data["coverage.json"] || {};
  return Number((coverage.itemsByCategory || {})[categoryId] || 0);
}

function focalCategories() {
  return sortByName(data["categories.json"].filter(function (category) {
    return category.scope === "focal";
  }));
}

function contextualCategories() {
  return sortByName(data["categories.json"].filter(function (category) {
    return category.scope === "contextual";
  }));
}

function categoryCard(category, compact) {
  const clusters = asArray(indexes.clustersByCategory.get(category.categoryId));
  const metas = asArray(indexes.metasByCategory.get(category.categoryId));
  const card = cardShell(
    category.scope === "focal" ? "Focal extraction category" : "Contextual extraction category",
    entityLink("category", category.categoryId, category.name),
    compact ? truncate(category.summary || "Corpus context retained without cluster coding.", 170) :
      category.summary,
    category.scope === "contextual" ? "contextual" : "category"
  );
  const metrics = element("div", "card-metrics");
  metrics.appendChild(chip(formatNumber(categoryCoverage(category.categoryId)) + " items"));
  if (category.scope === "focal") {
    metrics.appendChild(chip(formatNumber(metas.length) + " meta-clusters"));
    metrics.appendChild(chip(formatNumber(clusters.length) + " clusters"));
  } else {
    metrics.appendChild(chip("Context only", "quiet"));
  }
  card.appendChild(metrics);
  return card;
}

function metaClusterCard(metaCluster) {
  const card = cardShell(
    metaCluster.metaClusterId,
    entityLink("metaCluster", metaCluster.metaClusterId, metaCluster.name),
    truncate(metaCluster.definition, 190),
    "meta-cluster"
  );
  const metrics = element("div", "card-metrics");
  metrics.appendChild(chip(
    formatNumber(asArray(metaCluster.includedClusterIds).length) + " mapped clusters"
  ));
  if (metaCluster.salience) {
    metrics.appendChild(chip("Source salience: " + sentenceCase(metaCluster.salience), "source"));
  }
  card.appendChild(metrics);
  if (indexes.emptyMetaClusterIds.has(metaCluster.metaClusterId)) {
    card.appendChild(element(
      "p",
      "governed-status",
      "Source condition: no cluster-mapping rows. No membership has been inferred."
    ));
  }
  return card;
}

function clusterCard(cluster, modifier) {
  const summary = indexes.clusterSummary.get(cluster.clusterId);
  const card = cardShell(
    cluster.clusterId,
    entityLink("cluster", cluster.clusterId, cluster.name),
    truncate((summary && summary.summary) || cluster.definition, 190),
    modifier || "cluster"
  );
  if (summary) {
    const metrics = element("div", "card-metrics");
    metrics.appendChild(chip(formatNumber(summary.primaryCount) + " primary"));
    metrics.appendChild(chip(formatNumber(summary.secondaryCount) + " secondary"));
    card.appendChild(metrics);
  }
  return card;
}

function findingCard(finding) {
  const card = cardShell(
    finding.findingId,
    entityLink("categoryFinding", finding.findingId, finding.name),
    truncate(finding.coreFinding, 190),
    "finding"
  );
  if (finding.confidence) {
    card.appendChild(chip("Source confidence: " + sentenceCase(finding.confidence), "source"));
  }
  return card;
}

function linkedEntityCards(type, ids, cardBuilder) {
  const grid = element("div", "map-card-grid");
  asArray(ids).map(function (id) { return getEntity(type, id); })
    .filter(Boolean)
    .forEach(function (record) { grid.appendChild(cardBuilder(record)); });
  return grid;
}

function coverageChart(categories) {
  const chart = element("div", "coverage-chart");
  const maximum = Math.max.apply(null, categories.map(function (category) {
    return categoryCoverage(category.categoryId);
  }).concat([1]));
  categories.forEach(function (category) {
    const value = categoryCoverage(category.categoryId);
    const row = element("div", "coverage-row");
    const label = entityLink("category", category.categoryId, category.name, "coverage-row__label");
    row.appendChild(label);
    const track = element("div", "coverage-row__track");
    const bar = element("span", "coverage-row__bar");
    bar.style.width = String(Math.max(2, value / maximum * 100)) + "%";
    track.appendChild(bar);
    row.appendChild(track);
    row.appendChild(element("span", "coverage-row__value", formatNumber(value)));
    chart.appendChild(row);
  });
  return chart;
}

function renderOverview() {
  const coverage = data["coverage.json"];
  setHeader(
    "Practitioner discourse map",
    "A structured view of recurring practitioner discourse",
    "Explore concepts, technologies, actors, challenges, recommendations, examples, future expectations, and higher-order synthesis across the current corpus.",
    "Human-guided, AI-assisted qualitative synthesis"
  );
  setBreadcrumbs([{ label: "Overview", current: true }]);
  const explore = viewLink("browse", "Explore the map", "primary-button");
  viewActions.appendChild(explore);

  const content = fragment();
  content.appendChild(cautionBox(
    "Read the counts carefully",
    coverage.methodologyCaution,
    "methodology"
  ));

  const stats = element("section", "overview-section");
  stats.appendChild(element("h2", "section-title", "Current corpus at a glance"));
  const statGrid = element("div", "stat-grid");
  [
    [indexes.counts.episodes, "canonical public-feed releases"],
    [indexes.counts.sourceIdentities, "historical transcript / source identities"],
    [indexes.counts.items, "original analytic extraction items"],
    [indexes.counts.sensitivityItems, "reconciled sensitivity items"],
    [indexes.counts.focalCategories, "focal analytical categories"],
    [indexes.counts.focalItems, "focal items"],
    [indexes.counts.clusters, "intermediate clusters"],
    [indexes.counts.metaClusters, "meta-clusters"],
    [indexes.counts.themes, "cross-cutting themes"],
    [indexes.counts.tensions, "tensions / debates"],
    [indexes.counts.metaNarratives, "source meta-narratives"],
    [indexes.counts.scenarios, "future scenarios"],
  ].forEach(function (item) {
    statGrid.appendChild(statCard(item[0], item[1]));
  });
  stats.appendChild(statGrid);
  content.appendChild(stats);
  content.appendChild(cautionBox(
    "Original analysis and sensitivity view",
    "The original analytic release contains " + formatNumber(indexes.counts.items) +
      " items from " + formatNumber(indexes.counts.sourceIdentities) +
      " historical transcript/source identities. The separate reconciled sensitivity dataset retains " +
      formatNumber(indexes.counts.sensitivityItems) +
      " items after selecting one canonical source identity for each of " +
      formatNumber(indexes.counts.episodes) +
      " public-feed episodes. Neither denominator replaces the other.",
    "quiet"
  ));

  const entryPoints = element("section", "overview-section");
  entryPoints.appendChild(element("h2", "section-title", "Choose an entry point"));
  const entryGrid = element("div", "map-card-grid map-card-grid--three");
  const browseEntry = cardShell(
    "Categories",
    viewLink("browse", "Browse the field", "entity-link"),
    "Move from the seven focal categories into governed meta-clusters and concept clusters.",
    "entry-point"
  );
  entryGrid.appendChild(browseEntry);
  const crossEntry = cardShell(
    "Themes & tensions",
    viewLink("themes", "See what cuts across the field", "entity-link"),
    "Trace cross-category themes and the debates that preserve competing assumptions.",
    "entry-point"
  );
  crossEntry.appendChild(viewLink("tensions", "Explore tensions & debates", "text-link"));
  entryGrid.appendChild(crossEntry);
  const futuresEntry = cardShell(
    "Narratives & scenarios",
    viewLink("narratives", "Explore where the discourse points", "entity-link"),
    "Review higher-order storylines and plausible futures without treating scenarios as predictions.",
    "entry-point"
  );
  futuresEntry.appendChild(viewLink("scenarios", "Explore future scenarios", "text-link"));
  entryGrid.appendChild(futuresEntry);
  entryPoints.appendChild(entryGrid);
  content.appendChild(entryPoints);

  const hierarchy = element("section", "overview-section hierarchy-explainer");
  hierarchy.appendChild(element("h2", "section-title", "How the analytical structure works"));
  hierarchy.appendChild(element(
    "p",
    "section-intro",
    "The focal material is organized through a within-category hierarchy. Higher-order synthesis connects across that structure rather than forming one strict tree."
  ));
  const flow = element("ol", "hierarchy-flow");
  [
    ["1", "Canonical episode / extracted material", "Public feed releases, source identities, and interpretive extraction units"],
    ["2", "Category", "One of " + formatNumber(indexes.counts.focalCategories) + " focal analytical lenses"],
    ["3", "Meta-cluster", "A within-category family of related patterns"],
    ["4", "Intermediate cluster", "A governed recurring discourse concept"],
  ].forEach(function (step) {
    const item = element("li", "hierarchy-step");
    item.appendChild(element("span", "hierarchy-step__number", step[0]));
    const copy = element("div");
    copy.appendChild(element("strong", null, step[1]));
    copy.appendChild(element("span", null, step[2]));
    item.appendChild(copy);
    flow.appendChild(item);
  });
  hierarchy.appendChild(flow);
  const synthesis = element("div", "synthesis-band");
  [
    ["themes", formatNumber(indexes.counts.themes) + " Cross-cutting themes", "Patterns that connect categories"],
    ["tensions", formatNumber(indexes.counts.tensions) + " Tensions", "Competing assumptions and unresolved debates"],
    ["narratives", formatNumber(indexes.counts.metaNarratives) + " Meta-narratives", "High-level interpretive storylines"],
    ["scenarios", formatNumber(indexes.counts.scenarios) + " Scenarios", "Plausible futures, not forecasts"],
  ].forEach(function (entry) {
    const link = viewLink(entry[0], entry[1], "synthesis-band__link");
    const wrapper = element("div");
    wrapper.appendChild(link);
    wrapper.appendChild(element("span", null, entry[2]));
    synthesis.appendChild(wrapper);
  });
  hierarchy.appendChild(synthesis);
  content.appendChild(hierarchy);

  const categorySection = element("section", "overview-section");
  categorySection.appendChild(element(
    "h2", "section-title",
    "Browse the " + formatNumber(indexes.counts.focalCategories) + " focal categories"
  ));
  categorySection.appendChild(element(
    "p", "section-intro",
    "Start with a category, then move through its meta-clusters and intermediate clusters."
  ));
  const categoryGrid = element("div", "map-card-grid map-card-grid--categories");
  focalCategories().forEach(function (category) {
    categoryGrid.appendChild(categoryCard(category, true));
  });
  categorySection.appendChild(categoryGrid);
  content.appendChild(categorySection);

  const coverageSection = element("section", "overview-section");
  coverageSection.appendChild(element("h2", "section-title", "Corpus coverage by extraction category"));
  coverageSection.appendChild(element(
    "p", "section-intro",
    "These counts show how much extracted material appears in each corpus category. They are not rankings of importance, consensus, or scientific support."
  ));
  coverageSection.appendChild(coverageChart(data["categories.json"]));
  content.appendChild(coverageSection);

  const contextual = element("section", "overview-section contextual-scope");
  contextual.appendChild(element("h2", "section-title", "Context retained outside focal clustering"));
  contextual.appendChild(element(
    "p", "section-intro",
    formatNumber(indexes.counts.contextualCategories) +
      " extraction categories provide source and episode context. They were intentionally not included in the " +
      formatNumber(indexes.counts.focalCategories) + "-category cluster-coding workflow."
  ));
  const contextualGrid = element("div", "map-card-grid map-card-grid--three");
  contextualCategories().forEach(function (category) {
    contextualGrid.appendChild(categoryCard(category, true));
  });
  contextual.appendChild(contextualGrid);
  content.appendChild(contextual);

  viewContent.appendChild(content);
}

function renderBrowse() {
  setHeader(
    "Category → Meta-cluster → Intermediate cluster",
    "Browse the discourse map",
    "Choose one of the " + formatNumber(indexes.counts.focalCategories) + " focal categories to explore its synthesis, within-category families, clusters, findings, themes, and debates.",
    formatNumber(indexes.counts.focalCategories) + " focal categories · " +
      formatNumber(indexes.counts.metaClusters) + " meta-clusters · " +
      formatNumber(indexes.counts.clusters) + " intermediate clusters"
  );
  setBreadcrumbs([{ label: "Browse", current: true }]);
  const grid = element("div", "map-card-grid map-card-grid--categories");
  focalCategories().forEach(function (category) {
    grid.appendChild(categoryCard(category, false));
  });
  viewContent.appendChild(grid);

  const scope = cautionBox(
    "Why only " + formatNumber(indexes.counts.focalCategories) + " categories appear here",
    "The corpus also retains " + formatNumber(indexes.counts.contextualCategories) + " contextual categories: Guest Background / Experience, Memorable Insights / Quotes, and Strategic Landscape / Times. They provide scope and provenance context but were intentionally excluded from focal cluster coding.",
    "quiet"
  );
  viewContent.appendChild(scope);
}

function renderCategory(route) {
  const category = getEntity("category", route.id);
  const clusters = sortByName(asArray(indexes.clustersByCategory.get(category.categoryId)));
  const metas = sortByName(asArray(indexes.metasByCategory.get(category.categoryId)));
  const findings = sortByName(asArray(indexes.findingsByCategory.get(category.categoryId)));
  const relatedThemes = sortByName(data["themes.json"].filter(function (theme) {
    return asArray(theme.categoryIds).includes(category.categoryId);
  }));
  const relatedTensions = sortByName(data["tensions.json"].filter(function (tension) {
    return asArray(tension.categoryIds).includes(category.categoryId);
  }));
  const unmapped = clusters.filter(function (cluster) {
    return indexes.unmappedClusterIds.has(cluster.clusterId);
  });

  setHeader(
    category.scope === "focal" ? "Focal extraction category" : "Contextual extraction category",
    category.name,
    category.summary || "This category is retained as corpus context and was not part of the focal clustering workflow.",
    formatNumber(categoryCoverage(category.categoryId)) + " extracted items"
  );
  setBreadcrumbs([
    { label: "Browse", view: "browse" },
    { label: category.name, current: true },
  ]);

  const content = fragment();
  if (category.scope === "contextual") {
    content.appendChild(cautionBox(
      "Contextual category — no cluster hierarchy expected",
      "This category documents corpus and episode context. Its absence from the focal meta-cluster and cluster hierarchy is intentional, not missing data.",
      "quiet"
    ));
    content.appendChild(coverageChart([category]));
    content.appendChild(episodeCoverageSection(
      "category", category.categoryId,
      { caveat: "Category counts aggregate actual retained canonical structured items." }
    ));
    viewContent.appendChild(content);
    return;
  }

  const summary = element("section", "category-synthesis detail-lead");
  summary.appendChild(element("h2", "section-title", "Category synthesis"));
  summary.appendChild(element("p", null, category.summary));
  if (category.soWhat) {
    const soWhat = element("div", "so-what-block");
    soWhat.appendChild(element("h3", null, "Why it matters"));
    soWhat.appendChild(element("p", null, category.soWhat));
    summary.appendChild(soWhat);
  }
  const metrics = element("div", "stat-grid stat-grid--compact");
  metrics.appendChild(statCard(categoryCoverage(category.categoryId), "extracted items"));
  metrics.appendChild(statCard(metas.length, "meta-clusters"));
  metrics.appendChild(statCard(clusters.length, "intermediate clusters"));
  metrics.appendChild(statCard(findings.length, "category findings"));
  summary.appendChild(metrics);
  content.appendChild(summary);

  const metaSection = element("section", "overview-section");
  metaSection.appendChild(element("h2", "section-title", "Meta-clusters"));
  metaSection.appendChild(element(
    "p", "section-intro",
    "Within-category families that group related intermediate clusters."
  ));
  const metaGrid = element("div", "map-card-grid");
  metas.forEach(function (meta) { metaGrid.appendChild(metaClusterCard(meta)); });
  metaSection.appendChild(metaGrid);
  content.appendChild(metaSection);

  const clusterSection = element("section", "overview-section");
  clusterSection.appendChild(element("h2", "section-title", "Intermediate clusters"));
  clusterSection.appendChild(element(
    "p", "section-intro",
    "Every governed cluster in this category is linked here, including records without a current meta-cluster assignment."
  ));
  const clusterGrid = element("div", "map-card-grid");
  clusters.forEach(function (cluster) {
    clusterGrid.appendChild(clusterCard(
      cluster,
      indexes.unmappedClusterIds.has(cluster.clusterId) ? "unmapped" : null
    ));
  });
  clusterSection.appendChild(clusterGrid);
  content.appendChild(clusterSection);

  if (unmapped.length) {
    const unmappedSection = element("section", "overview-section governed-unresolved");
    unmappedSection.appendChild(element(
      "h2", "section-title", "Unmapped clusters retained for review"
    ));
    unmappedSection.appendChild(element(
      "p", "section-intro",
      "These source clusters do not currently have a meta-cluster mapping. They remain fully discoverable; no assignment has been guessed."
    ));
    unmappedSection.appendChild(entityChipList(
      "cluster",
      unmapped.map(function (cluster) { return cluster.clusterId; }),
      "No unmapped clusters."
    ));
    content.appendChild(unmappedSection);
  }

  const findingSection = element("section", "overview-section");
  findingSection.appendChild(element("h2", "section-title", "Category findings"));
  const findingGrid = element("div", "map-card-grid");
  findings.forEach(function (finding) { findingGrid.appendChild(findingCard(finding)); });
  findingSection.appendChild(findingGrid);
  content.appendChild(findingSection);

  const connections = element("section", "overview-section");
  connections.appendChild(element("h2", "section-title", "Cross-category connections"));
  const split = element("div", "connection-columns");
  const themeColumn = element("div");
  themeColumn.appendChild(element("h3", null, "Cross-cutting themes"));
  themeColumn.appendChild(entityChipList(
    "theme", relatedThemes.map(function (theme) { return theme.themeId; }),
    "No canonical theme links are present."
  ));
  split.appendChild(themeColumn);
  const tensionColumn = element("div");
  tensionColumn.appendChild(element("h3", null, "Tensions and debates"));
  tensionColumn.appendChild(entityChipList(
    "tension", relatedTensions.map(function (tension) { return tension.tensionId; }),
    "No canonical tension links are present."
  ));
  split.appendChild(tensionColumn);
  connections.appendChild(split);
  content.appendChild(connections);

  content.appendChild(episodeCoverageSection(
    "category", category.categoryId,
    { caveat: "Category counts aggregate actual retained canonical structured items." }
  ));

  viewContent.appendChild(content);
}

function renderMetaCluster(route) {
  const meta = getEntity("metaCluster", route.id);
  const category = getEntity("category", meta.categoryId);
  const clusters = asArray(meta.includedClusterIds).map(function (id) {
    return getEntity("cluster", id);
  }).filter(Boolean);
  const themeIds = relatedSourceIds(
    "metaCluster", meta.metaClusterId, "theme", "theme-connects-meta-cluster"
  );
  const tensionIds = relatedSourceIds(
    "metaCluster", meta.metaClusterId, "tension", "tension-maps-to-meta-cluster"
  );

  setHeader(
    "Within-category family · " + meta.metaClusterId,
    meta.name,
    meta.definition,
    formatNumber(clusters.length) + " mapped intermediate clusters"
  );
  setBreadcrumbs([
    { label: "Browse", view: "browse" },
    { label: category.name, type: "category", id: category.categoryId },
    { label: meta.name, current: true },
  ]);

  const content = fragment();
  const lead = element("section", "detail-lead");
  lead.appendChild(definitionList([
    { label: "Category", value: entityLink("category", category.categoryId, category.name) },
    {
      label: "Within-corpus source salience",
      value: meta.salience ? sentenceCase(meta.salience) : null,
    },
    { label: "Meta-cluster ID", value: meta.metaClusterId },
  ]));
  if (meta.categorySynthesis) {
    appendChildren(lead, [section("Category synthesis", meta.categorySynthesis)]);
  }
  if (meta.nearNeighborDistinctions) {
    appendChildren(lead, [section(
      "Near-neighbor distinctions", meta.nearNeighborDistinctions
    )]);
  }
  content.appendChild(lead);

  const members = element("section", "overview-section");
  members.appendChild(element("h2", "section-title", "Constituent intermediate clusters"));
  if (clusters.length) {
    const grid = element("div", "map-card-grid");
    sortByName(clusters).forEach(function (cluster) {
      grid.appendChild(clusterCard(cluster));
    });
    members.appendChild(grid);
  } else {
    members.appendChild(cautionBox(
      "No source cluster mappings",
      indexes.emptyMetaClusterIds.has(meta.metaClusterId)
        ? "The source preserves this meta-cluster as a strategic synthesis lens but contains no cluster-mapping rows. This is a governed unresolved source condition, not an ordinary empty family."
        : "The current source contains no mapped clusters for this record. No membership has been inferred.",
      "unresolved",
      "h3"
    ));
  }
  content.appendChild(members);

  const connections = element("section", "overview-section");
  connections.appendChild(element("h2", "section-title", "Mapped semantic connections"));
  connections.appendChild(element(
    "p", "section-intro",
    "These links represent source-supported conceptual mappings, not causal claims."
  ));
  const split = element("div", "connection-columns");
  const themes = element("div");
  themes.appendChild(element("h3", null, "Cross-cutting themes"));
  themes.appendChild(entityChipList("theme", themeIds, "No mapped theme links."));
  split.appendChild(themes);
  const tensions = element("div");
  tensions.appendChild(element("h3", null, "Tensions and debates"));
  tensions.appendChild(entityChipList("tension", tensionIds, "No mapped tension links."));
  split.appendChild(tensions);
  connections.appendChild(split);
  content.appendChild(connections);
  content.appendChild(episodeCoverageSection(
    "metaCluster", meta.metaClusterId,
    {
      caveat: "Coverage is derived only through actual episode cluster support and governed cluster membership.",
      emptyMessage: "No episode resolves through an actual cluster into this meta-cluster. This may reflect the governed unresolved membership condition.",
    }
  ));
  viewContent.appendChild(content);
}

function countMetric(value, label, explanation) {
  const card = element("div", "count-metric");
  card.appendChild(element("strong", "count-metric__value", formatNumber(value)));
  const title = element("span", "count-metric__label");
  const abbreviation = element("abbr", null, label);
  abbreviation.title = explanation;
  title.appendChild(abbreviation);
  card.appendChild(title);
  card.appendChild(element("span", "count-metric__explanation", explanation));
  return card;
}

function renderCluster(route) {
  const cluster = getEntity("cluster", route.id);
  const category = getEntity("category", cluster.categoryId);
  const meta = indexes.metaByCluster.get(cluster.clusterId);
  const summary = indexes.clusterSummary.get(cluster.clusterId);
  const themeIds = relatedSourceIds(
    "cluster", cluster.clusterId, "theme", "theme-supported-by-cluster"
  );
  const tensionIds = data["tensions.json"].filter(function (tension) {
    return asArray(tension.clusterIds).includes(cluster.clusterId);
  }).map(function (tension) { return tension.tensionId; });
  const findings = data["category_findings.json"].filter(function (finding) {
    return asArray(finding.supportingClusterIds).includes(cluster.clusterId);
  });

  setHeader(
    "Intermediate cluster · " + cluster.clusterId,
    cluster.name,
    cluster.definition,
    meta ? "Mapped to " + meta.name : "Unmapped cluster retained for review"
  );
  const crumbs = [
    { label: "Browse", view: "browse" },
    { label: category.name, type: "category", id: category.categoryId },
  ];
  if (meta) crumbs.push({
    label: meta.name, type: "metaCluster", id: meta.metaClusterId,
  });
  crumbs.push({ label: cluster.name, current: true });
  setBreadcrumbs(crumbs);

  const content = fragment();
  if (!meta && indexes.unmappedClusterIds.has(cluster.clusterId)) {
    content.appendChild(cautionBox(
      "Unmapped cluster retained for review",
      "The source contains this governed cluster but no meta-cluster assignment. The record and its corpus coverage remain visible; no family mapping has been guessed.",
      "unresolved"
    ));
  }

  const lead = element("section", "detail-lead");
  lead.appendChild(definitionList([
    { label: "Cluster ID", value: cluster.clusterId },
    { label: "Category", value: entityLink("category", category.categoryId, category.name) },
    {
      label: "Meta-cluster",
      value: meta
        ? entityLink("metaCluster", meta.metaClusterId, meta.name)
        : "No current source mapping",
    },
  ]));
  if (summary) {
    const counts = element("div", "count-metrics");
    counts.appendChild(countMetric(
      summary.primaryCount,
      "Primary count",
      "Items mainly coded to this cluster."
    ));
    counts.appendChild(countMetric(
      summary.secondaryCount,
      "Secondary count",
      "Items where this cluster represented substantive conceptual adjacency."
    ));
    counts.appendChild(countMetric(
      summary.weightedCount,
      "Weighted count",
      "Two times the primary count plus the secondary count."
    ));
    lead.appendChild(counts);
  }
  content.appendChild(lead);

  if (summary) {
    const synthesis = element("section", "overview-section");
    synthesis.appendChild(element("h2", "section-title", "Cluster synthesis"));
    synthesis.appendChild(element("p", null, summary.summary));
    const synthesisGrid = element("div", "detail-grid");
    appendChildren(synthesisGrid, [
      section("Why this matters", summary.strategicSignificance),
      section("Operational implications", summary.operationalImplications),
      section(
        "Primary-versus-secondary distinction",
        summary.primarySecondaryDistinction
      ),
    ]);
    synthesis.appendChild(synthesisGrid);
    content.appendChild(synthesis);

    if (asArray(summary.recurringThemes).length) {
      const recurring = element("section", "overview-section");
      recurring.appendChild(element(
        "h2", "section-title", "Recurring themes within this cluster"
      ));
      recurring.appendChild(element(
        "p", "section-intro",
        "These are source cluster-summary subthemes. They are distinct from the governed cross-cutting theme entities."
      ));
      const grid = element("div", "map-card-grid");
      asArray(summary.recurringThemes).forEach(function (theme) {
        const card = cardShell(
          theme.importance ? "Source importance: " + sentenceCase(theme.importance) : "Cluster subtheme",
          theme.name,
          theme.description,
          "subtheme"
        );
        const metrics = element("div", "card-metrics");
        if (hasValue(theme.primarySupportCountEstimate)) {
          metrics.appendChild(chip(formatNumber(theme.primarySupportCountEstimate) + " primary"));
        }
        if (hasValue(theme.secondarySupportCountEstimate)) {
          metrics.appendChild(chip(formatNumber(theme.secondarySupportCountEstimate) + " secondary"));
        }
        card.appendChild(metrics);
        grid.appendChild(card);
      });
      recurring.appendChild(grid);
      content.appendChild(recurring);
    }
  }

  const boundaries = element("section", "overview-section");
  boundaries.appendChild(element("h2", "section-title", "Coding boundaries"));
  const boundaryGrid = element("div", "detail-grid");
  appendChildren(boundaryGrid, [
    section("Inclusion criteria", cluster.inclusionCriteria),
    section("Exclusion criteria", cluster.exclusionCriteria),
    section("Near-neighbor distinctions", cluster.nearNeighborDistinctions),
    section(
      "Anchor examples",
      asArray(cluster.anchorExamples).length
        ? textList(cluster.anchorExamples)
        : null
    ),
  ]);
  boundaries.appendChild(boundaryGrid);
  content.appendChild(boundaries);

  const related = element("section", "overview-section");
  related.appendChild(element("h2", "section-title", "Mapped synthesis connections"));
  related.appendChild(element(
    "p", "section-intro",
    "Connections are semantic and source-supported. They do not imply cause or effect."
  ));
  const columns = element("div", "connection-columns connection-columns--three");
  const themeColumn = element("div");
  themeColumn.appendChild(element("h3", null, "Cross-cutting themes"));
  themeColumn.appendChild(entityChipList("theme", themeIds, "No mapped themes."));
  columns.appendChild(themeColumn);
  const tensionColumn = element("div");
  tensionColumn.appendChild(element("h3", null, "Tensions"));
  tensionColumn.appendChild(entityChipList("tension", tensionIds, "No linked tensions."));
  columns.appendChild(tensionColumn);
  const findingColumn = element("div");
  findingColumn.appendChild(element("h3", null, "Category findings"));
  findingColumn.appendChild(entityChipList(
    "categoryFinding",
    findings.map(function (finding) { return finding.findingId; }),
    "No linked category findings."
  ));
  columns.appendChild(findingColumn);
  related.appendChild(columns);
  content.appendChild(related);

  content.appendChild(episodeCoverageSection(
    "cluster", cluster.clusterId,
    { caveat: "Each relationship corresponds to at least one actual retained primary or secondary item code; weighted counts use 2:1 weighting." }
  ));

  content.appendChild(cautionBox(
    "Public evidence boundary",
    "Source-linked item and quotation browsing is being held for a separate publication and attribution review.",
    "quiet"
  ));
  viewContent.appendChild(content);
}

function validCategoryFilter(route, records, type) {
  if (!indexes.category.has(route.category)) return "";
  const represented = new Set(records.flatMap(function (record) {
    return categoryIdsForRecord(type, record);
  }));
  return represented.has(route.category) ? route.category : "";
}

function addCategoryViewFilter(view, route, records) {
  const categoryIds = unique(records.flatMap(function (record) {
    return categoryIdsForRecord(
      view === "themes" ? "theme" :
        view === "tensions" ? "tension" :
          view === "narratives" ? "metaNarrative" : "scenario",
      record
    );
  }));
  const label = element("label", "inline-filter");
  label.appendChild(element("span", null, "Filter by category"));
  const select = element("select");
  const all = element("option", null, "All categories");
  all.value = "";
  select.appendChild(all);
  focalCategories().filter(function (category) {
    return categoryIds.includes(category.categoryId);
  }).forEach(function (category) {
    const option = element("option", null, category.name);
    option.value = category.categoryId;
    option.selected = route.category === category.categoryId;
    select.appendChild(option);
  });
  select.addEventListener("change", function () {
    navigate({ view: view, category: select.value });
  });
  label.appendChild(select);
  viewActions.appendChild(label);
}

function themeCard(theme) {
  const card = cardShell(
    theme.themeId,
    entityLink("theme", theme.themeId, theme.name),
    truncate(theme.definition, 210),
    "theme"
  );
  const metrics = element("div", "card-metrics");
  metrics.appendChild(chip(formatNumber(asArray(theme.categoryIds).length) + " categories"));
  metrics.appendChild(chip(
    formatNumber(asArray(theme.linkedMetaClusterIds).length) + " meta-clusters"
  ));
  metrics.appendChild(chip(
    formatNumber(asArray(theme.linkedClusterIds).length) + " clusters"
  ));
  card.appendChild(metrics);
  if (theme.evidenceStrength) {
    card.appendChild(chip(
      "Within-corpus synthesis: " + sentenceCase(theme.evidenceStrength),
      "source"
    ));
  }
  return card;
}

function renderThemes(route) {
  const categoryFilter = validCategoryFilter(route, data["themes.json"], "theme");
  const records = sortByName(data["themes.json"].filter(function (theme) {
    return !categoryFilter || asArray(theme.categoryIds).includes(categoryFilter);
  }));
  setHeader(
    "Higher-order synthesis",
    "Cross-cutting themes",
    "Explore the " + formatNumber(indexes.counts.themes) + " source themes that connect recurring patterns across focal categories.",
    formatNumber(records.length) + " of " + formatNumber(indexes.counts.themes) + " themes"
  );
  setBreadcrumbs([{ label: "Cross-cutting themes", current: true }]);
  addCategoryViewFilter("themes", route, data["themes.json"]);
  viewContent.appendChild(cautionBox(
    "How to read themes",
    "A cross-cutting theme is a within-corpus synthesis that connects patterns across categories. Theme links are semantic and source-supported; they do not establish causation or scientific evidence strength.",
    "methodology"
  ));
  const grid = element("div", "map-card-grid");
  records.forEach(function (theme) { grid.appendChild(themeCard(theme)); });
  viewContent.appendChild(grid);
}

function renderTheme(route) {
  const theme = getEntity("theme", route.id);
  setHeader(
    "Cross-cutting theme · " + theme.themeId,
    theme.name,
    theme.definition,
    formatNumber(asArray(theme.categoryIds).length) + " categories · " +
      formatNumber(asArray(theme.linkedClusterIds).length) + " linked clusters"
  );
  setBreadcrumbs([
    { label: "Cross-cutting themes", view: "themes" },
    { label: theme.name, current: true },
  ]);

  const content = fragment();
  const lead = element("section", "detail-lead");
  lead.appendChild(definitionList([
    { label: "Theme ID", value: theme.themeId },
    {
      label: "Source synthesis / within-corpus evidence label",
      value: theme.evidenceStrength ? sentenceCase(theme.evidenceStrength) : null,
    },
    {
      label: "Categories represented",
      value: entityChipList("category", theme.categoryIds),
    },
  ]));
  lead.appendChild(element(
    "p",
    "evidence-boundary-note",
    "This label describes support within the source synthesis. It is not a rating of scientific evidence strength."
  ));
  content.appendChild(lead);

  const logic = element("section", "overview-section");
  logic.appendChild(element("h2", "section-title", "Theme summary"));
  logic.appendChild(element("p", null, theme.crossCategoryLogic));
  const grid = element("div", "detail-grid");
  appendChildren(grid, [
    section("Why this matters", theme.strategicSignificance),
    section("Operational implications", theme.operationalImplications),
    section("Boundary conditions", theme.boundaryConditions),
  ]);
  logic.appendChild(grid);
  content.appendChild(logic);

  const mapped = element("section", "overview-section");
  mapped.appendChild(element("h2", "section-title", "Mapped semantic support"));
  mapped.appendChild(element(
    "p", "section-intro",
    "Use these links to move back into the within-category analytical structure."
  ));
  const columns = element("div", "connection-columns connection-columns--three");
  [
    ["Meta-clusters", "metaCluster", theme.linkedMetaClusterIds,
      "No mapped meta-clusters."],
    ["Intermediate clusters", "cluster", theme.linkedClusterIds,
      "No mapped clusters."],
    ["Related tensions", "tension", theme.relatedTensionIds,
      "No canonical related tensions."],
  ].forEach(function (entry) {
    const column = element("div");
    column.appendChild(element("h3", null, entry[0]));
    column.appendChild(entityChipList(entry[1], entry[2], entry[3]));
    columns.appendChild(column);
  });
  mapped.appendChild(columns);
  content.appendChild(mapped);

  content.appendChild(episodeCoverageSection(
    "theme", theme.themeId,
    {
      caveat: "Direct lineage is labeled separately from connections derived through actual coded clusters; neither establishes consensus or causal influence.",
    }
  ));

  content.appendChild(cautionBox(
    "Evidence publication boundary",
    "Three unresolved source placeholders are retained in private QA but do not produce public cluster links. Source-linked item and quotation browsing is held for separate publication and attribution review.",
    "quiet"
  ));
  viewContent.appendChild(content);
}

function tensionCard(tension) {
  const card = cardShell(
    tension.tensionId + " · " + sentenceCase(tension.tensionLevel),
    entityLink("tension", tension.tensionId, tension.name),
    truncate(tension.description, 190),
    "tension"
  );
  const poles = element("div", "mini-poles");
  poles.appendChild(element("span", "mini-poles__a", tension.poleALabel));
  poles.appendChild(element("span", "mini-poles__divider", "↔"));
  poles.appendChild(element("span", "mini-poles__b", tension.poleBLabel));
  card.appendChild(poles);
  const metrics = element("div", "card-metrics");
  metrics.appendChild(chip(formatNumber(asArray(tension.categoryIds).length) + " categories"));
  metrics.appendChild(chip(formatNumber(asArray(tension.clusterIds).length) + " clusters"));
  card.appendChild(metrics);
  return card;
}

function renderTensions(route) {
  const categoryFilter = validCategoryFilter(route, data["tensions.json"], "tension");
  const records = sortByName(data["tensions.json"].filter(function (tension) {
    return !categoryFilter || asArray(tension.categoryIds).includes(categoryFilter);
  }));
  setHeader(
    "Unresolved debates and competing assumptions",
    "Tensions & debates",
    "Compare both poles of " + formatNumber(indexes.counts.tensions) + " source tensions without treating either position as endorsed.",
    formatNumber(records.length) + " of " + formatNumber(indexes.counts.tensions) + " tensions"
  );
  setBreadcrumbs([{ label: "Tensions & debates", current: true }]);
  addCategoryViewFilter("tensions", route, data["tensions.json"]);
  viewContent.appendChild(cautionBox(
    "A tension is not a poll",
    "The poles may apply under different conditions, reflect different institutional values, coexist, or require balancing. Their presence does not measure support for either position.",
    "methodology"
  ));
  const grid = element("div", "map-card-grid");
  records.forEach(function (tension) { grid.appendChild(tensionCard(tension)); });
  viewContent.appendChild(grid);
}

function renderTension(route) {
  const tension = getEntity("tension", route.id);
  const themeIds = relatedTargetIds(
    "tension", tension.tensionId, "theme", "tension-maps-to-cross-cutting-theme"
  );
  const metaIds = relatedTargetIds(
    "tension", tension.tensionId, "metaCluster", "tension-maps-to-meta-cluster"
  );
  setHeader(
    "Tension / debate · " + tension.tensionId,
    tension.name,
    tension.description,
    sentenceCase(tension.tensionLevel)
  );
  setBreadcrumbs([
    { label: "Tensions & debates", view: "tensions" },
    { label: tension.name, current: true },
  ]);

  const content = fragment();
  const twoPole = element("section", "two-pole");
  const poleA = element("article", "pole-card pole-card--a");
  poleA.appendChild(element("p", "pole-card__label", "Pole A"));
  poleA.appendChild(element("h2", null, tension.poleALabel));
  poleA.appendChild(element("p", null, tension.poleAAssumption));
  twoPole.appendChild(poleA);
  const axis = element("div", "tension-axis");
  axis.appendChild(element("span", null, "Tension"));
  axis.setAttribute("aria-hidden", "true");
  twoPole.appendChild(axis);
  const poleB = element("article", "pole-card pole-card--b");
  poleB.appendChild(element("p", "pole-card__label", "Pole B"));
  poleB.appendChild(element("h2", null, tension.poleBLabel));
  poleB.appendChild(element("p", null, tension.poleBAssumption));
  twoPole.appendChild(poleB);
  content.appendChild(twoPole);

  const interpret = element("section", "overview-section interpretation-panel");
  interpret.appendChild(element("h2", "section-title", "Why both positions persist"));
  interpret.appendChild(textList([
    "Each pole may be useful under different operational or institutional conditions.",
    "The poles may reflect different values, authorities, risk tolerances, or evidence standards.",
    "Both positions can coexist within one organization or problem setting.",
    "The current corpus preserves the disagreement rather than resolving it.",
    "Practical decisions may require balancing the poles rather than choosing one permanently.",
  ]));
  content.appendChild(interpret);

  const significance = element("section", "overview-section");
  significance.appendChild(element("h2", "section-title", "Strategic significance"));
  significance.appendChild(element("p", null, tension.description));
  significance.appendChild(element(
    "p",
    "evidence-boundary-note",
    "The governed tension record has no separate strategic-significance field; this section uses its source description without adding an inferred claim."
  ));
  content.appendChild(significance);

  const context = element("section", "overview-section");
  context.appendChild(element("h2", "section-title", "Where this tension is represented"));
  context.appendChild(definitionList([
    {
      label: "Categories involved",
      value: entityChipList("category", tension.categoryIds),
    },
    {
      label: "Intermediate clusters",
      value: entityChipList("cluster", tension.clusterIds),
    },
    {
      label: "Mapped cross-cutting themes",
      value: entityChipList("theme", themeIds, "No mapped theme links."),
    },
    {
      label: "Mapped meta-clusters",
      value: entityChipList("metaCluster", metaIds, "No mapped meta-cluster links."),
    },
  ], "metadata-list metadata-list--wide"));
  content.appendChild(context);

  content.appendChild(episodeCoverageSection(
    "tension", tension.tensionId,
    {
      caveat: "Only direct retained-item evidence lineage is published. A relationship does not mean the episode or speaker endorses either pole.",
      emptyMessage: "No retained canonical item has direct evidence lineage to this tension. Broad derived closures are intentionally not published.",
    }
  ));

  const labels = element("section", "overview-section");
  labels.appendChild(element("h2", "section-title", "Source synthesis labels"));
  labels.appendChild(definitionList([
    {
      label: "Within-corpus evidence label",
      value: tension.evidenceStrength ? sentenceCase(tension.evidenceStrength) : null,
    },
    {
      label: "Source synthesis confidence",
      value: tension.confidence ? sentenceCase(tension.confidence) : null,
    },
  ]));
  labels.appendChild(element(
    "p",
    "evidence-boundary-note",
    "These labels describe the source synthesis process. They are not scientific evidence ratings and do not establish which pole is correct."
  ));
  content.appendChild(labels);
  viewContent.appendChild(content);
}

function narrativeCard(narrative) {
  const card = cardShell(
    narrative.narrativeId,
    entityLink("metaNarrative", narrative.narrativeId, narrative.name),
    truncate(narrative.shortVersion || narrative.coreClaim, 210),
    "narrative"
  );
  const metrics = element("div", "card-metrics");
  metrics.appendChild(chip(
    formatNumber(asArray(narrative.supportingThemeIds).length) + " themes"
  ));
  metrics.appendChild(chip(
    formatNumber(asArray(narrative.supportingMetaClusterIds).length) + " meta-clusters"
  ));
  metrics.appendChild(chip(
    formatNumber(asArray(narrative.categoryIds).length) + " categories"
  ));
  card.appendChild(metrics);
  return card;
}

function renderNarratives(route) {
  const categoryFilter = validCategoryFilter(
    route, data["meta_narratives.json"], "metaNarrative"
  );
  const records = sortByName(data["meta_narratives.json"].filter(function (narrative) {
    return !categoryFilter || asArray(narrative.categoryIds).includes(categoryFilter);
  }));
  setHeader(
    "High-level interpretive storylines",
    "Meta-narratives",
    "Explore the " + formatNumber(indexes.counts.metaNarratives) + " canonical narratives synthesized from themes, meta-clusters, categories, and unresolved questions in the corpus.",
    formatNumber(records.length) + " of " +
      formatNumber(indexes.counts.metaNarratives) + " source meta-narratives"
  );
  setBreadcrumbs([{ label: "Meta-narratives", current: true }]);
  addCategoryViewFilter("narratives", route, data["meta_narratives.json"]);
  const narrativeIssue = data["review_summary.json"].metaNarrativeCountIssue;
  const note = cautionBox(
    formatNumber(narrativeIssue.currentSourceActual) + " canonical source records",
    "Earlier project documentation referenced " +
      formatNumber(narrativeIssue.priorDocumentedExpected) +
      " meta-narratives. The current canonical source contains " +
      formatNumber(narrativeIssue.currentSourceActual) +
      ", and this map preserves the source records without inventing a replacement.",
    "quiet"
  );
  viewContent.appendChild(note);
  const grid = element("div", "map-card-grid");
  records.forEach(function (record) { grid.appendChild(narrativeCard(record)); });
  viewContent.appendChild(grid);
}

function renderMetaNarrative(route) {
  const narrative = getEntity("metaNarrative", route.id);
  setHeader(
    "Meta-narrative · " + narrative.narrativeId,
    narrative.name,
    narrative.shortVersion,
    formatNumber(asArray(narrative.categoryIds).length) + " connected categories"
  );
  setBreadcrumbs([
    { label: "Meta-narratives", view: "narratives" },
    { label: narrative.name, current: true },
  ]);

  const content = fragment();
  const claim = element("section", "detail-lead narrative-claim");
  claim.appendChild(element("h2", "section-title", "Core claim"));
  claim.appendChild(element("p", null, narrative.coreClaim));
  claim.appendChild(definitionList([
    {
      label: "Source synthesis confidence",
      value: narrative.confidence ? sentenceCase(narrative.confidence) : null,
    },
  ]));
  claim.appendChild(element(
    "p", "evidence-boundary-note",
    "Confidence describes the source synthesis, not scientific evidence strength."
  ));
  content.appendChild(claim);

  const meaning = element("section", "overview-section");
  meaning.appendChild(element("h2", "section-title", "Significance and implications"));
  const grid = element("div", "detail-grid");
  appendChildren(grid, [
    section("Strategic significance", narrative.strategicSignificance),
    section(
      "Operational implications",
      asArray(narrative.operationalImplications).length
        ? textList(narrative.operationalImplications)
        : null
    ),
    section("Caveats", narrative.caveats),
  ]);
  meaning.appendChild(grid);
  content.appendChild(meaning);

  const support = element("section", "overview-section");
  support.appendChild(element("h2", "section-title", "Supporting synthesis entities"));
  support.appendChild(element(
    "p", "section-intro",
    "These are semantic support links retained from the canonical source."
  ));
  support.appendChild(definitionList([
    { label: "Categories", value: entityChipList("category", narrative.categoryIds) },
    {
      label: "Cross-cutting themes",
      value: entityChipList(
        "theme", narrative.supportingThemeIds, "No canonical supporting themes."
      ),
    },
    {
      label: "Tensions",
      value: entityChipList(
        "tension", narrative.supportingTensionIds,
        "No authoritative tension IDs are present in the current public source."
      ),
    },
    {
      label: "Meta-clusters",
      value: entityChipList(
        "metaCluster", narrative.supportingMetaClusterIds,
        "No canonical supporting meta-clusters."
      ),
    },
  ], "metadata-list metadata-list--wide"));
  content.appendChild(support);
  viewContent.appendChild(content);
}

function renderCategoryFinding(route) {
  const finding = getEntity("categoryFinding", route.id);
  const category = getEntity("category", finding.categoryId);
  setHeader(
    "Category finding · " + finding.findingId,
    finding.name,
    finding.coreFinding,
    category.name
  );
  setBreadcrumbs([
    { label: "Browse", view: "browse" },
    { label: category.name, type: "category", id: category.categoryId },
    { label: finding.name, current: true },
  ]);
  const content = fragment();
  const lead = element("section", "detail-lead");
  lead.appendChild(definitionList([
    { label: "Category", value: entityLink("category", category.categoryId, category.name) },
    {
      label: "Source synthesis confidence",
      value: finding.confidence ? sentenceCase(finding.confidence) : null,
    },
  ]));
  lead.appendChild(element(
    "p", "evidence-boundary-note",
    "Confidence is a source synthesis label, not scientific evidence strength."
  ));
  content.appendChild(lead);

  const implications = element("section", "overview-section");
  implications.appendChild(element("h2", "section-title", "Implications and open questions"));
  const grid = element("div", "detail-grid");
  appendChildren(grid, [
    section("Strategic significance", finding.strategicSignificance),
    section(
      "Operational implications",
      asArray(finding.operationalImplications).length
        ? textList(finding.operationalImplications)
        : null
    ),
    section(
      "Unresolved questions",
      asArray(finding.unresolvedQuestions).length
        ? textList(finding.unresolvedQuestions)
        : null
    ),
    section(
      "Caveats",
      asArray(finding.caveats).length ? textList(finding.caveats) : null
    ),
  ]);
  implications.appendChild(grid);
  content.appendChild(implications);

  const support = element("section", "overview-section");
  support.appendChild(element("h2", "section-title", "Supporting map entities"));
  support.appendChild(definitionList([
    {
      label: "Meta-clusters",
      value: entityChipList(
        "metaCluster", finding.supportingMetaClusterIds,
        "No supporting meta-cluster IDs."
      ),
    },
    {
      label: "Intermediate clusters",
      value: entityChipList(
        "cluster", finding.supportingClusterIds,
        "No supporting cluster IDs."
      ),
    },
  ], "metadata-list metadata-list--wide"));
  content.appendChild(support);
  viewContent.appendChild(content);
}

function scenarioCard(scenario) {
  const card = cardShell(
    scenario.scenarioId + " · " + sentenceCase(scenario.scenarioType),
    entityLink("scenario", scenario.scenarioId, scenario.name),
    truncate(scenario.coreScenario, 220),
    "scenario"
  );
  card.appendChild(element("p", "scenario-card__timeframe", scenario.timeframe));
  const metrics = element("div", "card-metrics");
  metrics.appendChild(chip("Plausible — not predictive", "scenario"));
  metrics.appendChild(chip("Uncertainty: " + sentenceCase(scenario.uncertaintyLevel), "source"));
  card.appendChild(metrics);
  return card;
}

function renderScenarios(route) {
  const categoryFilter = validCategoryFilter(route, data["scenarios.json"], "scenario");
  const records = sortByName(data["scenarios.json"].filter(function (scenario) {
    return !categoryFilter || asArray(scenario.categoryIds).includes(categoryFilter);
  }));
  setHeader(
    "Plausible futures",
    "Future scenarios",
    "Explore " + formatNumber(indexes.counts.scenarios) + " source scenarios as structured plausibility exercises with pathways, indicators, actions, and alternative outcomes.",
    formatNumber(records.length) + " of " + formatNumber(indexes.counts.scenarios) +
      " scenarios · not forecasts"
  );
  setBreadcrumbs([{ label: "Future scenarios", current: true }]);
  addCategoryViewFilter("scenarios", route, data["scenarios.json"]);
  viewContent.appendChild(cautionBox(
    "Plausible scenarios — not predictions",
    "Scenarios organize uncertainty and support investigation. They do not estimate probability, endorse an outcome, or forecast what will happen.",
    "methodology"
  ));
  const grid = element("div", "map-card-grid");
  records.forEach(function (scenario) { grid.appendChild(scenarioCard(scenario)); });
  viewContent.appendChild(grid);
}

function stringListSection(title, values, className) {
  return asArray(values).length
    ? section(title, textList(values), className)
    : null;
}

function renderScenario(route) {
  const scenario = getEntity("scenario", route.id);
  setHeader(
    "Future scenario · " + scenario.scenarioId,
    scenario.name,
    scenario.timeframe,
    sentenceCase(scenario.scenarioType) + " · " +
      sentenceCase(scenario.uncertaintyLevel) + " uncertainty"
  );
  setBreadcrumbs([
    { label: "Future scenarios", view: "scenarios" },
    { label: scenario.name, current: true },
  ]);

  const content = fragment();
  const disclaimer = element("div", "scenario-disclaimer");
  disclaimer.appendChild(element("strong", null, "Plausibility exercise — not a prediction."));
  disclaimer.appendChild(element(
    "span", null,
    " Use this scenario to examine assumptions, indicators, and possible responses."
  ));
  content.appendChild(disclaimer);

  const core = element("section", "detail-lead");
  core.appendChild(element("h2", "section-title", "Core scenario"));
  core.appendChild(element("p", null, scenario.coreScenario));
  core.appendChild(definitionList([
    { label: "Timeframe", value: scenario.timeframe },
    { label: "Scenario type", value: sentenceCase(scenario.scenarioType) },
    { label: "Uncertainty level", value: sentenceCase(scenario.uncertaintyLevel) },
    { label: "Categories involved", value: entityChipList("category", scenario.categoryIds) },
    { label: "Supporting themes", value: entityChipList("theme", scenario.themeIds) },
    {
      label: "Tensions activated",
      value: entityChipList(
        "tension", scenario.tensionIds,
        "No authoritative tension IDs are present in the current public source."
      ),
    },
  ], "metadata-list metadata-list--wide"));
  content.appendChild(core);

  const forces = element("section", "overview-section");
  forces.appendChild(element("h2", "section-title", "Forces, assumptions, and implications"));
  const grid = element("div", "detail-grid");
  appendChildren(grid, [
    stringListSection("Driving forces", scenario.drivingForces),
    stringListSection("Assumptions", scenario.assumptions),
    stringListSection("Strategic implications", scenario.strategicImplications),
    stringListSection("Operational implications", scenario.operationalImplications),
  ]);
  forces.appendChild(grid);
  content.appendChild(forces);

  const pathway = element("section", "overview-section");
  pathway.appendChild(element("h2", "section-title", "Scenario pathway"));
  pathway.appendChild(element(
    "p", "section-intro",
    "An ordered plausible sequence, not a deterministic causal chain."
  ));
  const timeline = element("ol", "timeline");
  asArray(scenario.pathway).slice().sort(function (left, right) {
    return Number(left.stepNumber) - Number(right.stepNumber);
  }).forEach(function (step) {
    const item = element("li", "timeline__item");
    item.appendChild(element("span", "timeline__step", String(step.stepNumber)));
    const copy = element("div", "timeline__content");
    copy.appendChild(element("p", null, step.step));
    item.appendChild(copy);
    timeline.appendChild(item);
  });
  pathway.appendChild(timeline);
  content.appendChild(pathway);

  const signals = element("section", "overview-section");
  signals.appendChild(element("h2", "section-title", "Indicators and actions"));
  const signalGrid = element("div", "detail-grid");
  appendChildren(signalGrid, [
    stringListSection("Indicators to watch", scenario.indicators),
    stringListSection("Policy or practice actions", scenario.actions),
  ]);
  signals.appendChild(signalGrid);
  content.appendChild(signals);

  const inquiry = element("section", "overview-section");
  inquiry.appendChild(element("h2", "section-title", "Questions and alternative outcomes"));
  const inquiryGrid = element("div", "detail-grid");
  appendChildren(inquiryGrid, [
    stringListSection("Research questions", scenario.researchQuestions),
    stringListSection("Alternative outcomes", scenario.alternativeOutcomes),
  ]);
  inquiry.appendChild(inquiryGrid);
  content.appendChild(inquiry);
  viewContent.appendChild(content);
}

function textMatchesQuery(text, query) {
  if (!query) return true;
  const textTokens = new Set(text.split(/[^a-z0-9]+/).filter(Boolean));
  const queryTokens = query.split(/[^a-z0-9]+/).filter(Boolean);
  if (queryTokens.length === 1 && queryTokens[0].length <= 2) {
    return textTokens.has(queryTokens[0]);
  }
  if (text.includes(query)) return true;
  return queryTokens.length > 0 && queryTokens.every(function (token) {
    return textTokens.has(token);
  });
}

function searchRank(documentRecord, query) {
  if (!query) return 10;
  if (documentRecord.normalizedName === query) return 0;
  if (documentRecord.normalizedName.startsWith(query)) return 1;
  if (textMatchesQuery(documentRecord.normalizedName, query)) return 2;
  if (textMatchesQuery(documentRecord.normalizedText, query)) return 4;
  return Number.POSITIVE_INFINITY;
}

function searchSnippet(documentRecord, query) {
  const field = documentRecord.fields.find(function (value) {
    return !query || textMatchesQuery(normalizeText(value), query);
  }) || documentRecord.fields[0] || "";
  if (!query || !field) return truncate(field, 220);
  const normalized = normalizeText(field);
  const position = normalized.indexOf(query);
  if (position <= 60) return truncate(field, 240);
  const start = Math.max(0, position - 70);
  return "…" + truncate(String(field).slice(start), 235);
}

function searchResultCard(documentRecord, query) {
  const record = documentRecord.record;
  const card = cardShell(
    ENTITY_LABELS[documentRecord.type] + " · " + documentRecord.id,
    entityLink(
      documentRecord.type,
      documentRecord.id,
      documentRecord.name || documentRecord.id
    ),
    searchSnippet(documentRecord, query),
    "search-result"
  );
  const context = element("div", "card-metrics");
  documentRecord.categoryIds.slice(0, 3).forEach(function (categoryId) {
    const category = getEntity("category", categoryId);
    if (category) context.appendChild(chip(category.name, "quiet"));
  });
  if (documentRecord.type === "episode") {
    if (record.podcast) context.appendChild(chip(record.podcast, "quiet"));
    context.appendChild(chip(
      formatNumber(record.originalItemCount) + " original items"
    ));
    context.appendChild(chip(
      formatNumber(record.reconciledSensitivityItemCount) + " sensitivity items",
      "quiet"
    ));
  }
  card.appendChild(context);
  return card;
}

function activeFilterChip(label, value) {
  const item = element("span", "active-filter");
  item.appendChild(element("strong", null, label + ": "));
  item.appendChild(document.createTextNode(value));
  return item;
}

async function copyCurrentLink() {
  const value = window.location.href;
  if (navigator.clipboard && typeof navigator.clipboard.writeText === "function") {
    try {
      await navigator.clipboard.writeText(value);
      return true;
    } catch (_error) {
      // Continue to the synchronous selection fallback below.
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
  try {
    copied = document.execCommand("copy");
  } catch (_error) {
    copied = false;
  }
  field.remove();
  return copied;
}

function renderCopyLinkAction() {
  const existing = viewActions.querySelector("[data-copy-link]");
  if (existing) return;
  const button = element("button", "secondary-button", "Copy Link");
  button.type = "button";
  button.dataset.copyLink = "true";
  button.addEventListener("click", async function () {
    const copied = await copyCurrentLink();
    showNotice(copied ? "Link copied" : "Copy the current URL from the browser address bar.");
  });
  viewActions.appendChild(button);
}

function renderSearchResults(results, query, container) {
  let visible = 60;
  function draw(focusResultIndex) {
    container.replaceChildren();
    results.slice(0, visible).forEach(function (documentRecord) {
      container.appendChild(searchResultCard(documentRecord, query));
    });
    if (visible < results.length) {
      const footer = element("div", "results-footer");
      const button = element(
        "button",
        "secondary-button",
        "Show " + formatNumber(Math.min(60, results.length - visible)) + " more"
      );
      button.type = "button";
      button.addEventListener("click", function () {
        const firstNewResultIndex = visible;
        visible += 60;
        draw(firstNewResultIndex);
      });
      footer.appendChild(button);
      container.appendChild(footer);
    }
    if (Number.isInteger(focusResultIndex)) {
      const links = container.querySelectorAll(".map-card--search-result .entity-link");
      if (links[focusResultIndex]) links[focusResultIndex].focus();
    }
  }
  draw();
}

function renderEpisodes(route) {
  const query = normalizeText(route.q || "");
  const episodes = data["episodes.json"].slice().sort(function (left, right) {
    const leftNumber = left.parsedEpisodeNumber;
    const rightNumber = right.parsedEpisodeNumber;
    if (leftNumber !== null && leftNumber !== undefined &&
        rightNumber !== null && rightNumber !== undefined &&
        Number(leftNumber) !== Number(rightNumber)) {
      return Number(leftNumber) - Number(rightNumber);
    }
    if (leftNumber !== null && leftNumber !== undefined) return -1;
    if (rightNumber !== null && rightNumber !== undefined) return 1;
    return String(left.episodeTitle || "").localeCompare(String(right.episodeTitle || ""));
  }).filter(function (episode) {
    if (!query) return true;
    return textMatchesQuery(normalizeText([
      episode.episodeTitle,
      episode.podcast,
      episode.summary,
      episode.whyItMatters,
      asArray(episode.keyTopics).join(" "),
      hasValue(episode.parsedEpisodeNumber) ? String(episode.parsedEpisodeNumber) : "",
    ].join(" ")), query);
  });
  setHeader(
    "Public episode archive",
    "Episodes",
    "Browse grounded, public-safe summaries for all canonical public-feed releases. Raw items, transcripts, private source identities, and excluded aliases remain outside the public package.",
    query
      ? formatNumber(episodes.length) + " matching releases"
      : formatNumber(indexes.counts.episodes) + " canonical public-feed releases"
  );
  setBreadcrumbs([{ label: "Episodes", current: true }]);

  const form = element("form", "episode-filter");
  form.setAttribute("role", "search");
  const label = element("label", null);
  label.appendChild(element("span", null, "Search episodes"));
  const input = element("input");
  input.type = "search";
  input.name = "q";
  input.value = route.q || "";
  input.placeholder = "Search titles, summaries, or key topics";
  label.appendChild(input);
  form.appendChild(label);
  const submit = element("button", "secondary-button", "Search");
  submit.type = "submit";
  form.appendChild(submit);
  if (query) {
    const clear = viewLink("episodes", "Clear", "text-link");
    form.appendChild(clear);
  }
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    navigate({ view: "episodes", q: input.value.trim() });
  });
  viewContent.appendChild(form);

  const resultStatus = element(
    "p", "section-intro",
    formatNumber(episodes.length) + (episodes.length === 1 ? " release" : " releases") +
      (query ? " match this filter." : " available.")
  );
  resultStatus.setAttribute("role", "status");
  viewContent.appendChild(resultStatus);
  if (!episodes.length) {
    viewContent.appendChild(cautionBox(
      "No episode matches this search",
      "Try a title word, topic, acronym, or a broader phrase.",
      "quiet"
    ));
    return;
  }

  const container = element("div", "map-card-grid");
  const controls = element("div", "load-more-row");
  let visible = 36;
  function draw() {
    container.replaceChildren();
    episodes.slice(0, visible).forEach(function (episode) {
      const numberLabel = hasValue(episode.parsedEpisodeNumber)
        ? "Episode #" + String(episode.parsedEpisodeNumber).padStart(3, "0")
        : "Unnumbered public release";
      const card = cardShell(
        numberLabel,
        entityLink("episode", episode.episodeId, episode.episodeTitle),
        truncate(episode.summary, 220),
        "episode"
      );
      const metrics = element("div", "card-metrics");
      asArray(episode.keyTopics).slice(0, 3).forEach(function (topic) {
        metrics.appendChild(chip(topic, "quiet"));
      });
      card.appendChild(metrics);
      container.appendChild(card);
    });
    controls.replaceChildren();
    if (visible < episodes.length) {
      const more = element(
        "button", "secondary-button",
        "Show more episodes (" + formatNumber(episodes.length - visible) + " remaining)"
      );
      more.type = "button";
      more.addEventListener("click", function () {
        visible += 36;
        draw();
        const nextControl = controls.querySelector("button");
        if (nextControl) nextControl.focus();
        else if (container.lastElementChild) {
          const lastLink = container.lastElementChild.querySelector("a");
          if (lastLink) lastLink.focus();
        }
      });
      controls.appendChild(more);
    }
  }
  draw();
  viewContent.appendChild(container);
  viewContent.appendChild(controls);
}

function renderSearch(route) {
  setHeader(
    "Search the governed public package",
    "Search the discourse map",
    "Search names, definitions, syntheses, findings, scenarios, episode summaries, and episode key topics. Full transcripts and the private item corpus are not searched.",
    "Public map entities and episode catalog only"
  );
  setBreadcrumbs([{ label: "Search", current: true }]);
  searchControls.hidden = false;
  const typeFilter = SEARCH_ENTITY_TYPES.includes(route.type) ? route.type : "";
  const categoryFilter = indexes.category.has(route.category) ? route.category : "";
  const metaFilter = indexes.metaCluster.has(route.meta) ? route.meta : "";
  const clusterFilter = indexes.cluster.has(route.cluster) ? route.cluster : "";
  searchInput.value = route.q;
  searchEntityType.value = typeFilter;
  searchCategory.value = categoryFilter;
  searchMetaCluster.value = metaFilter;
  searchCluster.value = clusterFilter;

  const query = normalizeText(route.q);
  const results = searchDocuments.map(function (documentRecord) {
    return {
      documentRecord: documentRecord,
      rank: searchRank(documentRecord, query),
    };
  }).filter(function (candidate) {
    const doc = candidate.documentRecord;
    if (!Number.isFinite(candidate.rank)) return false;
    if (typeFilter && doc.type !== typeFilter) return false;
    if (categoryFilter && !doc.categoryIds.includes(categoryFilter)) return false;
    if (metaFilter && !doc.metaClusterIds.includes(metaFilter)) return false;
    if (clusterFilter && !doc.clusterIds.includes(clusterFilter)) return false;
    return true;
  }).sort(function (left, right) {
    if (left.rank !== right.rank) return left.rank - right.rank;
    if (left.documentRecord.type !== right.documentRecord.type) {
      return ENTITY_LABELS[left.documentRecord.type].localeCompare(
        ENTITY_LABELS[right.documentRecord.type]
      );
    }
    return left.documentRecord.name.localeCompare(
      right.documentRecord.name,
      undefined,
      { sensitivity: "base", numeric: true }
    );
  }).map(function (candidate) { return candidate.documentRecord; });

  const active = [];
  if (route.q) active.push(activeFilterChip("Search", route.q));
  if (typeFilter) active.push(activeFilterChip("Type", ENTITY_LABELS[typeFilter]));
  if (categoryFilter) {
    active.push(activeFilterChip("Category", indexes.category.get(categoryFilter).name));
  }
  if (metaFilter) {
    active.push(activeFilterChip("Meta-cluster", indexes.metaCluster.get(metaFilter).name));
  }
  if (clusterFilter) {
    active.push(activeFilterChip("Cluster", indexes.cluster.get(clusterFilter).name));
  }
  appendChildren(searchActiveFilters, active);

  viewSummary.textContent = formatNumber(results.length) + " matching public records";
  if (!route.q && !typeFilter && !categoryFilter && !metaFilter && !clusterFilter) {
    const prompt = cautionBox(
      "Search scope",
      "Enter a term or choose one or more facets. With no criteria, the complete public entity and episode catalog is shown. This search never reads full transcripts, private item records, quotations, or review queues.",
      "quiet"
    );
    viewContent.appendChild(prompt);
  }
  if (!results.length) {
    showEmpty(
      "No public records matched",
      "Try a broader phrase, remove a facet, or browse the category hierarchy."
    );
    return;
  }
  const grid = element("div", "map-card-grid search-results");
  renderSearchResults(results, query, grid);
  viewContent.appendChild(grid);
}

function renderEpisode(route) {
  const episode = getEntity("episode", route.id);
  const episodeRelationships = relationshipsFrom("episode", episode.episodeId);
  const byTargetType = function (targetType) {
    return episodeRelationships.filter(function (relationship) {
      return relationship.targetType === targetType;
    });
  };
  const categoryRelationships = byTargetType("category");
  const clusterRelationships = byTargetType("cluster");
  const metaRelationships = byTargetType("metaCluster");
  const themeRelationships = byTargetType("theme");
  const tensionRelationships = byTargetType("tension");
  const episodeLabel = hasValue(episode.parsedEpisodeNumber)
    ? "Episode #" + String(episode.parsedEpisodeNumber).padStart(3, "0")
    : "Unnumbered public release";
  setHeader(
    episodeLabel + " · " + episode.episodeId,
    episode.episodeTitle,
    episode.podcast || "Podcast episode retained in the public corpus catalog.",
    formatNumber(episode.sourceItemCount) + " retained canonical structured items"
  );
  setBreadcrumbs([
    { label: "Episodes", view: "episodes" },
    { label: episode.episodeTitle, current: true },
  ]);
  const content = fragment();
  const lead = element("section", "detail-lead");
  lead.appendChild(definitionList([
    {
      label: "Episode number",
      value: hasValue(episode.parsedEpisodeNumber)
        ? episode.parsedEpisodeNumber
        : "Not available",
    },
    { label: "Episode ID", value: episode.episodeId },
    { label: "Podcast", value: episode.podcast },
    { label: "Historical source identities", value: formatNumber(episode.sourceIdentityCount) },
    { label: "Original analytic item count", value: formatNumber(episode.originalItemCount) },
    { label: "Reconciled sensitivity item count", value: formatNumber(episode.reconciledSensitivityItemCount) },
    { label: "Summary method", value: episode.generationMethod },
  ]));
  content.appendChild(lead);

  const summaryBlock = element("section", "overview-section");
  summaryBlock.appendChild(element("h2", "section-title", "Episode summary"));
  summaryBlock.appendChild(element("p", null, episode.summary));
  content.appendChild(summaryBlock);

  const topics = element("section", "overview-section");
  topics.appendChild(element("h2", "section-title", "Key topics"));
  topics.appendChild(element(
    "p", "section-intro",
    "These topics come from recurring coded clusters and retained canonical relevance tags."
  ));
  const topicList = element("div", "entity-chip-list");
  asArray(episode.keyTopics).forEach(function (topic) {
    topicList.appendChild(chip(topic));
  });
  topics.appendChild(topicList);
  content.appendChild(topics);

  const matters = element("section", "overview-section");
  matters.appendChild(element("h2", "section-title", "Why this episode matters"));
  matters.appendChild(element("p", null, episode.whyItMatters));
  content.appendChild(matters);

  const relationshipBlock = element("section", "overview-section");
  relationshipBlock.appendChild(element("h2", "section-title", "Public-safe analytical relationships"));
  relationshipBlock.appendChild(element(
    "p",
    "section-intro",
    "Category and cluster links aggregate retained canonical items. Meta-cluster and theme links follow governed paths. Tensions appear only where retained items have direct tension-evidence lineage; no stance or endorsement is implied."
  ));
  const relationshipColumns = element("div", "connection-columns");
  const categories = element("div");
  categories.appendChild(element("h3", null, "Categories represented"));
  categories.appendChild(episodeRelationshipList(
    categoryRelationships, "category", "No retained canonical category support."
  ));
  relationshipColumns.appendChild(categories);
  const metas = element("div");
  metas.appendChild(element("h3", null, "Derived meta-clusters"));
  metas.appendChild(episodeRelationshipList(
    metaRelationships, "metaCluster", "No governed meta-cluster path is available."
  ));
  relationshipColumns.appendChild(metas);
  const themes = element("div");
  themes.appendChild(element("h3", null, "Safe themes"));
  themes.appendChild(episodeRelationshipList(
    themeRelationships, "theme", "No direct or governed derived theme path is available."
  ));
  relationshipColumns.appendChild(themes);
  const tensions = element("div");
  tensions.appendChild(element("h3", null, "Safe tensions"));
  tensions.appendChild(episodeRelationshipList(
    tensionRelationships,
    "tension",
    "No retained item from this episode has direct tension-evidence lineage."
  ));
  relationshipColumns.appendChild(tensions);
  relationshipBlock.appendChild(relationshipColumns);
  content.appendChild(relationshipBlock);

  const clusterSection = element("section", "overview-section");
  clusterSection.appendChild(element(
    "h2", "section-title",
    "Actual coded clusters (" + formatNumber(clusterRelationships.length) + ")"
  ));
  clusterSection.appendChild(element(
    "p", "section-intro",
    "Every listed cluster has retained primary or secondary item support. Weighted count uses the governed 2:1 primary-to-secondary rule."
  ));
  clusterSection.appendChild(episodeRelationshipList(
    clusterRelationships,
    "cluster",
    "This episode has no focal cluster assignments."
  ));
  content.appendChild(clusterSection);

  content.appendChild(cautionBox(
    "Public corpus catalog only",
    "This page summarizes one canonical public-feed release from its selected structured historical source. Full transcript search, raw items, source-identity pairings, quotations, speakers, raw model output, and coding rationales remain private. Frequency reflects discourse prevalence within this corpus, not importance, consensus, or evidence strength.",
    "quiet"
  ));
  viewContent.appendChild(content);
}

function methodologyCard(title, text) {
  const card = element("article", "methodology-card");
  card.appendChild(element("h3", null, title));
  if (text instanceof Node) card.appendChild(text);
  else card.appendChild(element("p", null, text));
  return card;
}

function renderMethodology() {
  const qa = data["qa_report.json"];
  const narrativeIssue = data["review_summary.json"].metaNarrativeCountIssue;
  const unmappedClusterLabel = indexes.governedUnmappedClusters.map(function (record) {
    return record.clusterId;
  }).join(", ");
  const emptyMetaLabel = indexes.governedEmptyMetaClusters.map(function (record) {
    return record.metaClusterId;
  }).join(", ");
  const unresolvedThemePlaceholderCount = qa.unresolvedThemeClusterEvidence.length;
  const episodeRelationshipCounts = data["episode_relationships.json"].reduce(
    function (counts, relationship) {
      counts[relationship.relationshipType] =
        Number(counts[relationship.relationshipType] || 0) + 1;
      return counts;
    }, {}
  );
  setHeader(
    "How the map was produced and how to interpret it",
    "Methodology",
    "Understand the corpus, human-guided and AI-assisted synthesis workflow, traceability model, analytical hierarchy, and publication boundaries.",
    "Cognitive Security Map Schema v1.1"
  );
  setBreadcrumbs([{ label: "Methodology", current: true }]);
  const schemaLink = element("a", "secondary-button", "Read the data schema");
  schemaLink.href = "../docs/cognitive-security/COGNITIVE_SECURITY_SCHEMA_V1_1.md";
  viewActions.appendChild(schemaLink);

  const content = fragment();
  content.appendChild(cautionBox(
    "What this product is",
    "An interactive map of recurring concepts, technologies, actors, challenges, recommendations, historical examples, future expectations, cross-cutting themes, unresolved tensions, narratives, and scenarios identified through a human-guided, AI-assisted qualitative synthesis of practitioner discourse.",
    "methodology"
  ));

  const notList = element("section", "overview-section methodology-callout");
  notList.appendChild(element("h2", "section-title", "What it is not"));
  notList.appendChild(textList([
    "A definitive taxonomy",
    "A representative survey of the field",
    "A consensus measure",
    "A causal model",
    "A validated competency framework",
    "A scientific evidence ranking",
    "An extension of the PSYWERX behavioral Driver Ontology",
  ]));
  content.appendChild(notList);

  const corpus = element("section", "overview-section");
  corpus.appendChild(element("h2", "section-title", "Corpus and extraction"));
  corpus.appendChild(element(
    "p",
    "section-intro",
    "The current package represents " + formatNumber(indexes.counts.episodes) +
      " canonical episodes as distinct public feed releases, reconciled from " +
      formatNumber(indexes.counts.sourceIdentities) +
      " historical transcript/source identities. The original analytic release preserves " +
      formatNumber(indexes.counts.items) +
      " extracted interpretive items. The separate reconciled sensitivity dataset contains " +
      formatNumber(indexes.counts.sensitivityItems) +
      " items. Extraction organized material into " +
      formatNumber(indexes.counts.categories) + " categories."
  ));
  corpus.appendChild(cautionBox(
    "Governed corpus reconciliation",
    "The 269 historical source identities include 27 confirmed alias pairs. The canonical count is therefore 242 distinct public feed releases. This is a publication-unit count: a content-equivalent re-release remains a separate feed episode, so the stricter unique-recording count is 241. Episode zero is retained as a feed trailer. Pair-level evidence and filenames remain private.",
    "quiet",
    "h3"
  ));
  const corpusGrid = element("div", "methodology-grid");
  corpusGrid.appendChild(methodologyCard(
    "Research purpose",
    "The project maps recurring practitioner discourse across the corpus and provides a grounded public summary for each canonical release. An episode is a publication and navigation unit, not one statistically independent analytical observation. The higher-order analysis still rests on structured items and governed coding."
  ));
  corpusGrid.appendChild(methodologyCard(
    "Transcript processing and unit of analysis",
    "Transcript files were processed through a structured Python/API workflow. The unit of analysis is an extracted analytic item: an interpretive unit representing one concept, claim, example, actor, technology, challenge, trend, or proposed action. Items are not paragraphs, speakers, episodes, or statistically independent observations."
  ));
  corpusGrid.appendChild(methodologyCard(
    formatNumber(indexes.counts.focalCategories) + " focal categories",
    "Technologies / Tools / Platforms; Organizations / Actors / Communities; Challenges / Risks / Barriers; Key Concepts / Frameworks / Theories; Key Events / Historical Examples; Future Trends / Predictions; and Opportunities / Recommended Actions. These " +
      formatNumber(indexes.counts.focalItems) + " focal items enter the cluster-coding workflow."
  ));
  corpusGrid.appendChild(methodologyCard(
    formatNumber(indexes.counts.contextualCategories) + " contextual categories",
    "Guest Background / Experience, Memorable Insights / Quotes, and Strategic Landscape / Times provide source and episode context. Their " +
      formatNumber(indexes.counts.contextualItems) +
      " items are retained in corpus coverage but intentionally do not have a focal cluster hierarchy."
  ));
  corpus.appendChild(corpusGrid);
  content.appendChild(corpus);

  const coding = element("section", "overview-section");
  coding.appendChild(element("h2", "section-title", "Coding and within-category synthesis"));
  const codingGrid = element("div", "methodology-grid");
  codingGrid.appendChild(methodologyCard(
    "Inductive codebook development",
    "The governed codebook contains " + formatNumber(indexes.counts.clusters) +
      " intermediate clusters developed for the " +
      formatNumber(indexes.counts.focalCategories) +
      " focal categories. Within each category, approximately 100 randomly sampled items were examined in three rounds: candidate-code discovery, merge/split/refinement and boundary clarification, then a saturation-style stability check. This supports practical codebook stability but is not formal proof of saturation. Definitions, inclusion and exclusion criteria, near-neighbor distinctions, and anchor examples preserve cluster boundaries."
  ));
  codingGrid.appendChild(methodologyCard(
    "Primary assignment",
    "Each focal item receives one primary cluster representing its dominant analytical meaning."
  ));
  codingGrid.appendChild(methodologyCard(
    "Secondary assignment",
    "A secondary cluster records substantive conceptual adjacency. It is not a second independent observation and does not create a causal relationship."
  ));
  codingGrid.appendChild(methodologyCard(
    "Cluster synthesis",
    "All material associated with a cluster informed drill-up synthesis. The governed historical method weighted primary assignments 2:1 relative to secondary assignments so dominant meaning carried more influence than adjacency. The weighting describes analytic emphasis, not scientific evidence strength."
  ));
  codingGrid.appendChild(methodologyCard(
    "Meta-clustering",
    formatNumber(indexes.counts.metaClusters) +
      " meta-clusters organize related intermediate clusters within each category. They are within-category families, not cross-category causal mechanisms."
  ));
  codingGrid.appendChild(methodologyCard(
    "Cross-cutting themes",
    formatNumber(indexes.counts.themes) +
      " themes integrate recurring patterns across categories. Unlike meta-clusters, they are cross-category interpretive structures rather than within-category families."
  ));
  codingGrid.appendChild(methodologyCard(
    "Tensions and debates",
    formatNumber(indexes.counts.tensions) +
      " tensions were developed separately to retain tradeoffs, competing assumptions, contradictions, and unresolved differences instead of smoothing them into themes."
  ));
  codingGrid.appendChild(methodologyCard(
    "Meta-narratives",
    formatNumber(indexes.counts.metaNarratives) +
      " source meta-narratives organize higher-level interpretive storylines. Their greater abstraction places them farther from item-level evidence and requires correspondingly cautious interpretation."
  ));
  codingGrid.appendChild(methodologyCard(
    "Future scenarios",
    formatNumber(indexes.counts.scenarios) +
      " scenarios combine mapped forces into structured plausibility exercises. They are not predictions, probability estimates, or forecasts."
  ));
  coding.appendChild(codingGrid);
  content.appendChild(coding);

  const roles = element("section", "overview-section");
  roles.appendChild(element("h2", "section-title", "Human and AI-assisted roles"));
  const roleGrid = element("div", "detail-grid");
  roleGrid.appendChild(section(
    "Human role",
    "The researcher retained responsibility for the research purpose, corpus scope, extraction ontology, category selection, codebook development, code refinement, ambiguity and review handling, interpretation, final claims, governance boundaries, and public/private release decisions."
  ));
  roleGrid.appendChild(section(
    "AI-assisted role",
    "AI systems served as research-assistant and scaling mechanisms for structured extraction, candidate coding, clustering, synthesis, and consistency checks. Model assistance introduces prompt sensitivity, model dependence, semantic smoothing, overgeneralization, and hidden-bias risks; it does not make the corpus representative or the results causal or scientifically validated."
  ));
  roles.appendChild(roleGrid);
  content.appendChild(roles);

  const episodeProducts = element("section", "overview-section");
  episodeProducts.appendChild(element(
    "h2", "section-title", "Grounded episode products"
  ));
  const episodeProductGrid = element("div", "methodology-grid");
  episodeProductGrid.appendChild(methodologyCard(
    "Frozen episode summaries",
    "Each of the 242 public summaries was authored only from the selected canonical source identity’s structured item summaries, categories, primary and secondary clusters, strategic significance, operational implications, relevance tags, and time horizons. Outside knowledge, transcripts, raw item text, and excluded aliases were not inputs. Accepted summaries are frozen; ordinary website builds validate and copy them without making an API call."
  ));
  episodeProductGrid.appendChild(methodologyCard(
    "Direct category and cluster aggregation",
    formatNumber(episodeRelationshipCounts["episode-participates-in-category"] || 0) +
      " episode-category records aggregate retained items by category. " +
      formatNumber(episodeRelationshipCounts["episode-coded-to-cluster"] || 0) +
      " episode-cluster records reproduce every actual retained primary or secondary assignment combination, including exact 2:1 weighted counts."
  ));
  episodeProductGrid.appendChild(methodologyCard(
    "Governed meta-cluster and theme derivation",
    formatNumber(episodeRelationshipCounts["episode-derived-to-meta-cluster"] || 0) +
      " episode-meta-cluster records follow actual supported clusters into governed membership. The " +
      formatNumber(
        Number(episodeRelationshipCounts["episode-derived-to-theme"] || 0) +
        Number(episodeRelationshipCounts["episode-has-theme-lineage"] || 0)
      ) +
      " episode-theme pairs distinguish explicit item lineage from connections derived through governed cluster paths."
  ));
  episodeProductGrid.appendChild(methodologyCard(
    "Conservative tension lineage",
    formatNumber(episodeRelationshipCounts["episode-has-tension-lineage"] || 0) +
      " episode-tension records have retained item evidence lineage. Broader theme/meta-cluster closure would connect every episode to every tension, so those analytically non-discriminating derived links are not published. A direct lineage does not indicate endorsement of either pole."
  ));
  episodeProductGrid.appendChild(methodologyCard(
    "Public/private boundary",
    "Public episode products contain canonical episode IDs, summaries, key topics, why-it-matters statements, public entity IDs, safe aggregate counts, and relationship semantics. They exclude item IDs and text, quotations, transcripts, source filenames, alias records, private notes, raw model output, credentials, review queues, and local paths."
  ));
  episodeProductGrid.appendChild(methodologyCard(
    "Historical release and v2 work",
    "This Explorer preserves the reconciled historical higher-order analysis. A separate full-v2 reanalysis is currently underway in another worktree; unfinished v2 outputs were not consumed by this release and will require their own governance before publication."
  ));
  episodeProducts.appendChild(episodeProductGrid);
  content.appendChild(episodeProducts);

  const distinctions = element("section", "overview-section");
  distinctions.appendChild(element("h2", "section-title", "Four different signals"));
  distinctions.appendChild(element(
    "p", "section-intro",
    "These concepts answer different questions and must not be substituted for one another."
  ));
  const distinctionGrid = element("div", "methodology-grid");
  distinctionGrid.appendChild(methodologyCard(
    "Coding confidence",
    "How confidently an item was assigned during the coding workflow. It is not scientific support for the underlying claim."
  ));
  distinctionGrid.appendChild(methodologyCard(
    "Review status",
    "Whether a record or mapping needs human governance attention. It is a workflow state, not a truth score."
  ));
  distinctionGrid.appendChild(methodologyCard(
    "Corpus coverage",
    "How many extracted items or assignments appear in this corpus. It describes discourse salience, not importance, prevalence, or consensus."
  ));
  distinctionGrid.appendChild(methodologyCard(
    "Scientific evidence strength",
    "The quality and weight of external scientific evidence. This product does not perform that assessment."
  ));
  distinctions.appendChild(distinctionGrid);
  content.appendChild(distinctions);

  const sensitivity = element("section", "overview-section methodology-callout");
  sensitivity.appendChild(element("h2", "section-title", "Reconciliation sensitivity audit"));
  sensitivity.appendChild(element(
    "p", "section-intro",
    "The original analytic release remains unchanged at " +
      formatNumber(indexes.counts.items) + " items. Selecting one canonical source identity for each public-feed episode produces a separate reconciled sensitivity dataset of " +
      formatNumber(indexes.counts.sensitivityItems) + " items (" +
      formatNumber(indexes.counts.sensitivityFocalItems) + " focal and " +
      formatNumber(indexes.counts.sensitivityContextualItems) + " contextual)."
  ));
  const sensitivityGrid = element("div", "methodology-grid");
  sensitivityGrid.appendChild(methodologyCard(
    "Cluster-count sensitivity",
    "All 127 clusters retain primary support. The largest weighted-count changes are OPP-04 (-119; -10.37%), KCFT-06 (-103; -14.23%), KE-03 (-96; -14.26%), ORG-ACT-02 (-90; -11.90%), and ORG-ACT-04 (-86; -11.07%). Count changes describe denominator sensitivity, not substantive validity."
  ));
  sensitivityGrid.appendChild(methodologyCard(
    "Higher-order support sensitivity",
    "Across 132 higher-order records, 44 are stable, 2 mildly sensitive, 18 moderately sensitive, 13 highly sensitive, and 55 cannot be assessed from available item-level provenance. Two tensions lose all of their explicitly linked item support; narratives, category findings, and scenarios lack enough direct item provenance for a support classification."
  ));
  sensitivityGrid.appendChild(methodologyCard(
    "Governed recommendation",
    "A future full pipeline re-analysis is recommended because some higher-order records are materially sensitive to source-identity selection. This release does not regenerate or silently replace the historical synthesis. Loss of traceable support is a reason to reassess, not proof that a claim is invalid."
  ));
  sensitivity.appendChild(sensitivityGrid);
  content.appendChild(sensitivity);

  const unresolved = element("section", "overview-section governed-unresolved");
  unresolved.appendChild(element("h2", "section-title", "Governed unresolved source conditions"));
  unresolved.appendChild(textList([
    unmappedClusterLabel + " are valid clusters with no current meta-cluster assignment. They remain discoverable under their categories.",
    emptyMetaLabel + " is preserved as a strategic synthesis lens with no source cluster-mapping rows. No constituent clusters have been invented.",
    formatNumber(unresolvedThemePlaceholderCount) + " source theme-to-cluster placeholders have null cluster references. They remain in private QA and create no fake public links.",
    "The canonical final synthesis contains " +
      formatNumber(narrativeIssue.currentSourceActual) +
      " meta-narratives, while earlier documentation referenced " +
      formatNumber(narrativeIssue.priorDocumentedExpected) +
      ". The source count is preserved.",
    "Narrative and scenario tension text did not yield authoritative public tension IDs. Empty tension-link arrays are preserved rather than guessed.",
  ]));
  content.appendChild(unresolved);

  const traceability = element("section", "overview-section");
  traceability.appendChild(element("h2", "section-title", "Traceability and semantic relationships"));
  traceability.appendChild(element(
    "p", null,
    "Stable source IDs connect public categories, meta-clusters, clusters, themes, tensions, narratives, findings, and scenarios. The " +
      formatNumber(indexes.counts.relationships) +
      " public graph records are semantic relationships: belongs to, supported by, mapped to, and connected to. They never mean causes, drives, or produces an effect."
  ));
  traceability.appendChild(element(
    "p", null,
    "A separate episode relationship product contains " +
      formatNumber(indexes.counts.episodeRelationships) +
      " public-safe records with explicit direct, derived, and aggregation semantics. Keeping it separate preserves the historical relationships graph byte-for-byte."
  ));
  traceability.appendChild(element(
    "p", null,
    "The intended evidence chain is source identity to extracted item to primary/secondary assignment to cluster and, where source lineage exists, to meta-cluster, theme, tension, narrative, finding, or scenario. The public application joins governed records by stable ID, validates every public endpoint, and never guesses a link from similar wording. Greater abstraction means greater interpretive distance from the source."
  ));
  content.appendChild(traceability);

  const caveats = element("section", "overview-section");
  caveats.appendChild(element("h2", "section-title", "Interpretive cautions"));
  caveats.appendChild(textList([
    "Practitioner discourse is not field consensus.",
    "Frequency is not importance.",
    "Co-occurrence is not causation.",
    "A semantic relationship is not causal influence.",
    "A scenario is not a prediction.",
    "One practitioner-facing podcast corpus is not representative of the entire cognitive-security field.",
    "Counts represent corpus discourse salience, not objective importance, prevalence, or consensus.",
    "Extracted items are interpretive units, not statistically independent observations.",
    "Different extraction categories, prompts, models, codebooks, or coding choices could yield different structures.",
    "Model-assisted analysis is vulnerable to prompt sensitivity, model dependence, semantic smoothing, overgeneralization, and hidden bias.",
    "Transcript wording does not guarantee accurate speaker or quotation attribution; item-level evidence remains private pending a separate review.",
    "Co-occurrence and mappings are semantic, not causal; correlation or proximity does not establish causation.",
    "Coding confidence is a workflow judgment, not scientific evidence strength.",
    "Scenarios are plausible futures, not forecasts.",
    "Discourse clusters are not PSYWERX behavioral Drivers.",
    "Higher abstraction increases interpretive distance from the source material.",
    "Frequency is not consensus, and absence from the map is not evidence that a concept is absent from the field.",
  ]));
  content.appendChild(caveats);

  content.appendChild(cautionBox(
    "Public evidence boundary",
    "Source-linked item and quotation browsing is being held for a separate publication and attribution review. The browser never loads private item text, evidence excerpts, speakers, assignment rationales, local workbooks, or internal review queues.",
    "quiet"
  ));
  viewContent.appendChild(content);
}

function installEventHandlers() {
  document.addEventListener("click", function (event) {
    const entityAnchor = event.target.closest("[data-entity-type][data-entity-id]");
    if (entityAnchor) {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey ||
          event.altKey || (entityAnchor.target && entityAnchor.target !== "_self")) {
        return;
      }
      const type = entityAnchor.dataset.entityType;
      const id = entityAnchor.dataset.entityId;
      if (ENTITY_ROUTES[type] && getEntity(type, id)) {
        event.preventDefault();
        navigate({ view: ENTITY_ROUTES[type], id: id });
      }
      return;
    }
    const routeAnchor = event.target.closest("[data-route-view]");
    if (routeAnchor) {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey ||
          event.altKey || (routeAnchor.target && routeAnchor.target !== "_self")) {
        return;
      }
      event.preventDefault();
      navigate({ view: routeAnchor.dataset.routeView });
      return;
    }
    const viewAnchor = event.target.closest("[data-view-link]");
    if (viewAnchor) {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey ||
          event.altKey || (viewAnchor.target && viewAnchor.target !== "_self")) {
        return;
      }
      event.preventDefault();
      navigate({ view: viewAnchor.dataset.viewLink });
      return;
    }
    const action = event.target.closest("[data-action]");
    if (!action) return;
    if (action.dataset.action === "explore-map") {
      navigate({ view: "browse" });
    } else if (action.dataset.action === "clear-search") {
      navigate({ view: "search" });
    } else if (action.dataset.action === "retry-load") {
      window.location.reload();
    }
  });

  if (searchForm) {
    searchForm.addEventListener("submit", function (event) {
      event.preventDefault();
      navigate({
        view: "search",
        q: searchInput.value.trim(),
        type: searchEntityType.value,
        category: searchCategory.value,
        meta: searchMetaCluster.value,
        cluster: searchCluster.value,
      });
    });
    searchForm.addEventListener("change", function (event) {
      if (!initialized || parseRoute().view !== "search") return;
      // Text queries are committed by the explicit Search submit. Ignoring the
      // search input's blur/change event prevents two identical history entries
      // when a user types and then activates the submit button.
      if (event.target === searchInput) return;
      navigate({
        view: "search",
        q: searchInput.value.trim(),
        type: searchEntityType.value,
        category: searchCategory.value,
        meta: searchMetaCluster.value,
        cluster: searchCluster.value,
      }, { focus: false });
    });
  }

  if (searchClear) {
    searchClear.addEventListener("click", function () {
      navigate({ view: "search" });
    });
  }

  window.addEventListener("popstate", function () {
    renderRoute({ focus: true });
  });

  if (entityDialogClose && entityDialog) {
    entityDialogClose.addEventListener("click", function () { entityDialog.close(); });
  }
  if (copyLinkButton) {
    copyLinkButton.addEventListener("click", async function () {
      const copied = await copyCurrentLink();
      copyStatus.textContent = copied
        ? "Link copied"
        : "Copy the link from the browser address bar.";
    });
  }
}

installEventHandlers();
initialize();
