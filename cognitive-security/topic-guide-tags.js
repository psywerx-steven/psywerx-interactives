/* Optional guide tags plus Start Here entry points. No analytical edges, counts, or discovery scores change. */
(function () {
  "use strict";
  let pending = null;
  let revision = 0;
  const supported = new Set(["episode", "cluster", "family", "finding", "theme", "tension", "narrative"]);

  function removeById(id) {
    const node = document.getElementById(id);
    if (node) node.remove();
  }

  function clear() {
    revision += 1;
    removeById("curated-guide-tags");
    removeById("topic-guides-entry-card");
    removeById("topic-guides-overview-node");
  }

  async function readJson(name) {
    const response = await fetch("../data/cognitive-security-guides/" + name, { credentials: "same-origin" });
    if (!response.ok) throw new Error("Optional Topic Guides unavailable");
    return response.json();
  }

  async function data() {
    if (!pending) pending = Promise.all([readJson("guide_directory.json"), readJson("reverse_index.json")])
      .then(function (values) {
        if (values[0].schemaVersion !== "1.0" || values[1].schemaVersion !== "1.0" || values[1].semantics !== "explicit-curated-inclusion-not-analytical-support") throw new Error("Invalid Topic Guides data");
        const guides = new Map();
        if (!Array.isArray(values[0].guides)) throw new Error("Invalid guide directory");
        values[0].guides.forEach(function (guide) {
          if (typeof guide.guideId !== "string" || typeof guide.title !== "string" || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(guide.slug) || guides.has(guide.guideId)) throw new Error("Invalid guide");
          guides.set(guide.guideId, guide);
        });
        if (!values[1].entities || typeof values[1].entities !== "object") throw new Error("Invalid reverse index");
        return { guides: guides, entities: values[1].entities };
      }).catch(function (error) { pending = null; throw error; });
    return pending;
  }

  function cloneIcon(selector) {
    const icon = document.querySelector(selector);
    return icon ? icon.cloneNode(true) : null;
  }

  function renderStartExplanation() {
    const count = document.getElementById("total-episode-count");
    const episodeCount = count ? count.textContent.trim() : "";
    const lede = document.querySelector("#landing-hero .hero__lede");
    if (lede) {
      lede.textContent = "An AI-enabled qualitative analysis of " + (episodeCount ? episodeCount + " " : "") + "public Cognitive Crucible episodes, mapping recurring topics, cross-cutting themes, enduring tensions, narratives, scenarios, and the source conversations behind them.";
    }
    const description = document.getElementById("view-description");
    if (description) {
      description.textContent = "See how practitioner discourse is organized, then choose a curated Topic Guide or explore the analytical layers directly.";
    }
  }

  function renderStartEntry(guideCount) {
    const grid = document.querySelector("#view-content .entry-grid");
    if (!grid) return;
    let card = document.getElementById("topic-guides-entry-card");
    if (!card) {
      const topicsCard = Array.from(grid.querySelectorAll(".entry-card")).find(function (candidate) {
        const title = candidate.querySelector(".entry-card__title");
        return title && title.textContent.trim() === "Topics";
      });
      card = document.createElement("a");
      card.id = "topic-guides-entry-card";
      card.className = "entry-card";
      card.href = "./topic/";
      const icon = topicsCard ? topicsCard.querySelector(".entry-icon") : null;
      if (icon) card.appendChild(icon.cloneNode(true));
      const copy = document.createElement("span");
      copy.className = "entry-card__copy";
      const title = document.createElement("strong");
      title.className = "entry-card__title";
      title.textContent = "Topic Guides";
      const description = document.createElement("span");
      description.className = "entry-card__description";
      description.textContent = "Curated starting points that connect selected episodes with cross-cutting takeaways, concepts, challenges, approaches, tools, tensions, and the wider discourse map.";
      copy.appendChild(title);
      copy.appendChild(description);
      card.appendChild(copy);
      if (topicsCard) topicsCard.insertAdjacentElement("afterend", card);
      else grid.appendChild(card);
    }
    if (Number.isInteger(guideCount)) {
      let count = card.querySelector(".entry-card__count");
      if (!count) {
        count = document.createElement("span");
        count.className = "entry-card__count";
        card.querySelector(".entry-card__copy").appendChild(count);
      }
      count.textContent = String(guideCount);
      count.setAttribute("aria-label", guideCount + " Topic Guides");
    }
  }

  function renderStartOverviewNode() {
    const synthesis = document.querySelector("#view-content .overview-group--synthesis");
    if (!synthesis || document.getElementById("topic-guides-overview-node")) return;
    const link = document.createElement("a");
    link.id = "topic-guides-overview-node";
    link.className = "overview-node overview-node--topic-guides";
    link.href = "./topic/";
    link.setAttribute("aria-label", "Topic Guides — curated entry points into the discourse map");
    const icon = cloneIcon("#view-content .overview-node--topics .entry-icon");
    if (icon) link.appendChild(icon);
    const label = document.createElement("span");
    label.textContent = "Topic Guides";
    link.appendChild(label);
    synthesis.appendChild(link);
  }

  function renderStart(guideCount) {
    renderStartExplanation();
    renderStartEntry(guideCount);
    renderStartOverviewNode();
  }

  window.addEventListener("psywerx:route-start", clear);
  window.addEventListener("psywerx:route-ready", async function (event) {
    clear();
    const token = revision;
    const route = event.detail || {};

    if (route.view === "start") {
      renderStart();
      try {
        const payload = await data();
        if (revision === token) renderStart(payload.guides.size);
      } catch (_) {
        // Topic Guides remain discoverable even if optional guide data is unavailable.
      }
      return;
    }

    if (!supported.has(route.view) || !route.id) return;
    try {
      const payload = await data();
      if (revision !== token) return;
      const ids = payload.entities[route.view + ":" + route.id];
      if (!Array.isArray(ids) || ids.length === 0) return;
      const panel = document.createElement("aside"); panel.id = "curated-guide-tags";
      panel.className = "curated-guide-tags"; panel.setAttribute("aria-label", "Selected in Topic Guides");
      const label = document.createElement("span"); label.textContent = "Selected in Topic Guides:"; panel.appendChild(label);
      ids.forEach(function (id) {
        const guide = payload.guides.get(id); if (!guide) throw new Error("Unknown guide relationship");
        const anchor = document.createElement("a"); anchor.className = "entity-chip";
        anchor.href = "./topic/" + guide.slug + "/"; anchor.textContent = guide.title;
        panel.appendChild(anchor);
      });
      const header = document.getElementById("view-header");
      if (header && revision === token) header.insertAdjacentElement("afterend", panel);
    } catch (_) {
      // Guide tagging is optional. Never fail the canonical Explorer because the overlay failed.
    }
  });
})();
