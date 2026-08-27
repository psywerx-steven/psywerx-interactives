"use strict";

const TERM_QUERY_PARAMETER = "term";
const DATA_URL = "../../data/codebook.json";

const searchInput = document.querySelector("#codebook-search");
const clearSearchButton = document.querySelector("#clear-search");
const termCount = document.querySelector("#term-count");
const categoryCount = document.querySelector("#category-count");
const categoryNavigation = document.querySelector("#category-navigation");
const categorySections = document.querySelector("#category-sections");
const resultSummary = document.querySelector("#result-summary");
const emptyState = document.querySelector("#empty-state");
const loadError = document.querySelector("#load-error");
const linkNotice = document.querySelector("#link-notice");

let terms = [];
let termById = new Map();
let categories = [];
let selectedTermId = null;

function normalizeSearchText(value) {
  return String(value || "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase();
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

function categorySlug(category, index) {
  const slug = normalizeSearchText(category)
    .replace(/&/g, " and ")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
  return "category-" + (slug || String(index + 1));
}

function assertNonemptyString(record, field, label, errors) {
  if (typeof record[field] !== "string" || record[field].trim() === "") {
    errors.push(label + " has no valid " + field + ".");
  }
}

function validateCodebook(envelope) {
  if (!envelope || typeof envelope !== "object" || Array.isArray(envelope)) {
    throw new Error("Codebook data is not an object.");
  }
  if (envelope.schemaVersion !== "1.0") {
    throw new Error("Codebook data does not use Codebook Schema v1.0.");
  }
  if (!Array.isArray(envelope.entries)) {
    throw new Error("Codebook data does not contain an entries array.");
  }

  const errors = [];
  const ids = new Set();
  envelope.entries.forEach((record, index) => {
    const label = "Codebook term " + String(index + 1);
    [
      "id",
      "sheet",
      "field",
      "definition",
      "allowedValuesOrFormat",
      "guidance",
    ].forEach((field) => assertNonemptyString(record, field, label, errors));
    if (typeof record.required !== "boolean") {
      errors.push(label + " has no valid required status.");
    }
    if (!Array.isArray(record.allowedValues)) {
      errors.push(label + " has no valid allowedValues array.");
    }
    if (ids.has(record.id)) {
      errors.push("Duplicate Codebook Term ID: " + record.id + ".");
    }
    ids.add(record.id);
  });

  if (
    envelope.metadata &&
    Number.isInteger(envelope.metadata.termRecords) &&
    envelope.metadata.termRecords !== envelope.entries.length
  ) {
    errors.push("The metadata term count does not match the entries array.");
  }
  if (errors.length) {
    throw new Error(errors.join(" "));
  }
}

function searchableText(term) {
  return normalizeSearchText(
    [
      term.id,
      term.sheet,
      term.field,
      term.definition,
      term.allowedValuesOrFormat,
      term.guidance,
      ...(term.allowedValues || []),
    ].join(" ")
  );
}

function renderAllowedValues(term, body) {
  const section = element("section", "term-card__section");
  section.append(element("h4", null, "Allowed Values / Format"));

  if (term.allowedValues.length) {
    const list = element("ul", "allowed-values");
    term.allowedValues.forEach((value) => {
      list.append(element("li", null, value));
    });
    section.append(list);
    const sourceFormat = element(
      "p",
      "source-format",
      term.allowedValuesOrFormat
    );
    sourceFormat.prepend(element("span", null, "Source format: "));
    section.append(sourceFormat);
  } else {
    section.append(element("p", null, term.allowedValuesOrFormat));
  }
  body.append(section);
}

function createTermCard(term) {
  const card = element("details", "term-card");
  card.id = "term-" + term.id;
  card.dataset.termId = term.id;

  const summary = element("summary", "term-card__summary");
  const identity = element("span", "term-card__identity");
  identity.append(
    element("span", "term-card__field", term.field),
    element("span", "term-card__id", term.id)
  );

  const metadata = element("span", "term-card__metadata");
  metadata.append(
    element(
      "span",
      "requirement-badge " +
        (term.required
          ? "requirement-badge--required"
          : "requirement-badge--optional"),
      term.required ? "Required" : "Optional"
    ),
    element("span", "selected-label", "Selected term"),
    element("span", "term-card__action", "View term")
  );
  summary.append(identity, metadata);

  const body = element("div", "term-card__body");
  const definition = element("section", "term-card__section");
  definition.append(
    element("h4", null, "Definition"),
    element("p", null, term.definition)
  );
  body.append(definition);
  renderAllowedValues(term, body);

  const guidance = element("section", "term-card__section");
  guidance.append(
    element("h4", null, "Rule / Guidance"),
    element("p", null, term.guidance)
  );
  body.append(guidance);
  card.append(summary, body);
  return card;
}

function renderCodebook() {
  categoryNavigation.replaceChildren();
  categorySections.replaceChildren();

  categories.forEach((category, index) => {
    const categoryId = categorySlug(category, index);
    const categoryTerms = terms.filter((term) => term.sheet === category);

    const link = element("a", "category-navigation__link");
    link.href = "#" + categoryId;
    link.dataset.category = category;
    link.append(
      element("span", null, category),
      element("span", "category-navigation__count", String(categoryTerms.length))
    );
    categoryNavigation.append(link);

    const section = element("section", "codebook-category");
    section.id = categoryId;
    section.dataset.category = category;
    section.setAttribute("aria-labelledby", categoryId + "-heading");

    const header = element("div", "codebook-category__heading");
    const heading = element("h3", null, category);
    heading.id = categoryId + "-heading";
    const count = element(
      "p",
      "codebook-category__count",
      categoryTerms.length + (categoryTerms.length === 1 ? " term" : " terms")
    );
    count.dataset.categoryCount = category;
    header.append(heading, count);

    const list = element("div", "term-list");
    categoryTerms.forEach((term) => list.append(createTermCard(term)));
    section.append(header, list);
    categorySections.append(section);
  });
}

function updateSearchResults() {
  const query = normalizeSearchText(searchInput.value.trim());
  let visibleTerms = 0;

  categories.forEach((category) => {
    const section = categorySections.querySelector(
      '[data-category="' + CSS.escape(category) + '"]'
    );
    const navLink = categoryNavigation.querySelector(
      '[data-category="' + CSS.escape(category) + '"]'
    );
    const cards = [...section.querySelectorAll(".term-card")];
    let categoryVisible = 0;

    cards.forEach((card) => {
      const term = termById.get(card.dataset.termId);
      const matches = !query || term._searchText.includes(query);
      card.hidden = !matches;
      if (matches) {
        categoryVisible += 1;
      }
    });

    visibleTerms += categoryVisible;
    section.hidden = categoryVisible === 0;
    navLink.hidden = categoryVisible === 0;
    navLink.querySelector(".category-navigation__count").textContent = query
      ? categoryVisible + "/" + cards.length
      : String(cards.length);
    section.querySelector(".codebook-category__count").textContent =
      categoryVisible + (categoryVisible === 1 ? " term" : " terms");
  });

  resultSummary.textContent = query
    ? visibleTerms + (visibleTerms === 1 ? " matching term" : " matching terms")
    : terms.length + " Codebook terms across " + categories.length + " categories";
  emptyState.hidden = visibleTerms !== 0;
  clearSearchButton.disabled = !searchInput.value;
}

function termUrl(termId) {
  const url = new URL(window.location.href);
  if (termId) {
    url.searchParams.set(TERM_QUERY_PARAMETER, termId);
    url.hash = "term-" + termId;
  } else {
    url.searchParams.delete(TERM_QUERY_PARAMETER);
    url.hash = "";
  }
  return url;
}

function setSelectedTerm(termId, options = {}) {
  const { focus = false, scroll = false } = options;
  selectedTermId = termById.has(termId) ? termId : null;

  categorySections.querySelectorAll(".term-card").forEach((card) => {
    const selected = card.dataset.termId === selectedTermId;
    card.open = selected;
    card.classList.toggle("is-selected", selected);
  });

  if (!selectedTermId) {
    return;
  }
  const selectedCard = document.querySelector("#term-" + CSS.escape(selectedTermId));
  selectedCard.hidden = false;
  selectedCard.closest(".codebook-category").hidden = false;
  if (scroll || focus) {
    window.requestAnimationFrame(() => {
      if (scroll) {
        selectedCard.scrollIntoView({ behavior: "auto", block: "start" });
      }
      if (focus) {
        selectedCard.querySelector("summary").focus({ preventScroll: true });
      }
    });
  }
}

function openTerm(termId, historyMode = null, options = {}) {
  if (!termById.has(termId)) {
    linkNotice.textContent = "The linked Codebook term “" + termId + "” was not found.";
    linkNotice.hidden = false;
    setSelectedTerm(null);
    return;
  }
  linkNotice.hidden = true;
  if (searchInput.value) {
    searchInput.value = "";
    updateSearchResults();
  }
  setSelectedTerm(termId, options);
  if (historyMode === "push") {
    history.pushState({ termId }, "", termUrl(termId));
  } else if (historyMode === "replace") {
    history.replaceState({ termId }, "", termUrl(termId));
  }
}

function closeTerm(historyMode = null) {
  linkNotice.hidden = true;
  setSelectedTerm(null);
  if (historyMode === "push") {
    history.pushState({ termId: null }, "", termUrl(null));
  } else if (historyMode === "replace") {
    history.replaceState({ termId: null }, "", termUrl(null));
  }
}

function applyLocation() {
  const termId = new URL(window.location.href).searchParams.get(
    TERM_QUERY_PARAMETER
  );
  if (termId) {
    openTerm(termId, null, { focus: true, scroll: true });
  } else {
    closeTerm();
  }
}

async function loadCodebook() {
  try {
    const response = await fetch(DATA_URL);
    if (!response.ok) {
      throw new Error("Codebook request failed with status " + response.status + ".");
    }
    const envelope = await response.json();
    validateCodebook(envelope);

    terms = envelope.entries.map((term) =>
      Object.assign({}, term, { _searchText: searchableText(term) })
    );
    termById = new Map(terms.map((term) => [term.id, term]));
    categories = [...new Set(terms.map((term) => term.sheet))];

    termCount.textContent = terms.length.toLocaleString();
    categoryCount.textContent = categories.length.toLocaleString();
    renderCodebook();
    updateSearchResults();
    searchInput.disabled = false;
    clearSearchButton.disabled = true;

    const initialTermId = new URL(window.location.href).searchParams.get(
      TERM_QUERY_PARAMETER
    );
    history.replaceState({ termId: initialTermId }, "", window.location.href);
    applyLocation();
  } catch (error) {
    console.error("Unable to load PSYWERX Codebook:", error);
    resultSummary.textContent = "Codebook unavailable";
    loadError.hidden = false;
  }
}

searchInput.addEventListener("input", updateSearchResults);

clearSearchButton.addEventListener("click", () => {
  searchInput.value = "";
  updateSearchResults();
  searchInput.focus();
});

categorySections.addEventListener("click", (event) => {
  const summary = event.target.closest(".term-card__summary");
  if (!summary) {
    return;
  }
  event.preventDefault();
  const card = summary.closest(".term-card");
  if (selectedTermId === card.dataset.termId) {
    closeTerm("push");
  } else {
    openTerm(card.dataset.termId, "push", { focus: true });
  }
});

window.addEventListener("popstate", applyLocation);

loadCodebook();
