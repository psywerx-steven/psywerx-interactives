/* Progressive enhancement only: the complete guide is readable without JS. */
(function () {
  "use strict";
  const status = document.getElementById("guide-status");
  function announce(text) { if (status) status.textContent = text; }
  document.querySelectorAll("[data-copy-guide]").forEach(function (button) {
    button.addEventListener("click", async function () {
      const canonical = document.querySelector('link[rel="canonical"]');
      const url = canonical ? canonical.href : window.location.href;
      try {
        if (!navigator.clipboard || !window.isSecureContext) throw new Error("Clipboard unavailable");
        await navigator.clipboard.writeText(url);
        button.textContent = "Link copied";
        announce("Guide link copied to clipboard.");
      } catch (_) {
        let box = document.getElementById("guide-copy-fallback");
        if (!box) {
          box = document.createElement("input"); box.id = "guide-copy-fallback";
          box.readOnly = true; box.setAttribute("aria-label", "Guide link to copy");
          button.insertAdjacentElement("afterend", box);
        }
        box.value = url; box.focus(); box.select();
        announce("Automatic copy is unavailable. The guide link is selected; copy it with your keyboard or device controls.");
      }
    });
  });
  const search = document.getElementById("guide-search");
  if (search) {
    search.addEventListener("input", function () {
      const query = search.value.trim().toLocaleLowerCase(); let count = 0;
      document.querySelectorAll("[data-guide-search]").forEach(function (card) {
        const match = card.dataset.guideSearch.includes(query); card.hidden = !match;
        if (match) count += 1;
      });
      document.querySelectorAll("[data-guide-group]").forEach(function (group) {
        group.hidden = !Array.from(group.querySelectorAll("[data-guide-search]")).some(function (card) { return !card.hidden; });
      });
      document.getElementById("guide-count").textContent = count + (count === 1 ? " guide" : " guides");
      document.getElementById("no-guides").hidden = count !== 0;
    });
  }
})();
