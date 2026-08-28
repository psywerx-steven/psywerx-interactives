"use strict";

(function configurePsywerx() {
  const localHost = ["localhost", "127.0.0.1", "[::1]"].includes(
    window.location.hostname
  );

  // Causal relationship features are intentionally disabled in this public
  // taxonomy release pending systematic graph-completeness review.
  const defaults = {
    causalExplorerEnabled: false,
    scenarioAiEnabled: localHost,
    scenarioApiUrl: localHost
      ? "http://localhost:8787/v1/operationalize"
      : "",
  };

  window.PSYWERX_CONFIG = Object.freeze(
    Object.assign(defaults, window.PSYWERX_CONFIG || {})
  );
})();
