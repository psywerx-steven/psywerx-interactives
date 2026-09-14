/* Optional guide tags. No analytical edges, counts, or discovery scores change. */
(function () {
  "use strict";
  let pending = null;
  let revision = 0;
  const supported = new Set(["episode", "cluster", "family", "finding", "theme", "tension", "narrative"]);
  function clear() {
    revision += 1;
    const old = document.getElementById("curated-guide-tags");
    if (old) old.remove();
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
  window.addEventListener("psywerx:route-start", clear);
  window.addEventListener("psywerx:route-ready", async function (event) {
    clear();
    const token = revision;
    const route = event.detail || {};
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
