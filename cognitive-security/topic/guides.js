/* Progressive enhancement only: the complete guide is readable without JS. */
(function () {
  "use strict";

  function normalizeSiteHeader() {
    if (document.querySelector(".psywerx-global-header")) return;
    const legacyHeader = document.querySelector(".site-header");
    if (!legacyHeader) return;

    const template = document.createElement("template");
    template.innerHTML = `
      <header class="psywerx-global-header">
        <div class="psywerx-global-header__inner">
          <a class="psywerx-global-brand" href="/" aria-label="PSYWERX home">
            <img src="/assets/wordmark.webp" alt="PSYWERX" width="640" height="130">
          </a>
          <nav class="psywerx-global-nav" aria-label="Main navigation">
            <a href="/">Home</a>
            <details class="psywerx-explore-menu">
              <summary>Explore <span aria-hidden="true">⌄</span></summary>
              <div class="psywerx-explore-panel">
                <a href="/drivers/"><strong>Driver Taxonomy Explorer</strong><span>Browse the behavioral ontology</span></a>
                <a href="/drivers/codebook/"><strong>Driver Codebook</strong><span>Reference fields and governance rules</span></a>
                <a href="/cognitive-security/"><strong>Cognitive Security Explorer</strong><span>Navigate practitioner discourse</span></a>
                <a href="/cognitive-security/topic/"><strong>Topic Guides</strong><span>Start with curated listening paths</span></a>
              </div>
            </details>
            <a href="/#research">Research</a>
            <a href="/#learning-section">Learn</a>
            <a href="/#about">About</a>
            <a class="psywerx-global-live" href="/#live-tools">Live tools <span aria-hidden="true">↗</span></a>
          </nav>
          <details class="psywerx-mobile-menu">
            <summary aria-label="Open navigation"><span aria-hidden="true">☰</span> Menu</summary>
            <nav aria-label="Mobile navigation">
              <a href="/">Home</a>
              <a href="/#platform">Explore</a>
              <a href="/#research">Research</a>
              <a href="/#learning-section">Learn</a>
              <a href="/#about">About</a>
              <a href="/#live-tools">Live tools</a>
            </nav>
          </details>
        </div>
      </header>
      <div class="psywerx-product-bar">
        <div class="psywerx-product-bar__inner">
          <span class="psywerx-product-context">Cognitive Security</span>
          <nav class="psywerx-product-nav" aria-label="Cognitive Security">
            <a href="/cognitive-security/">Explorer</a>
            <a href="/cognitive-security/topic/" aria-current="page">Topic Guides</a>
            <a href="/cognitive-security/?view=methodology">Methodology</a>
          </nav>
        </div>
      </div>`;
    legacyHeader.replaceWith(template.content.cloneNode(true));
  }

  normalizeSiteHeader();

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
