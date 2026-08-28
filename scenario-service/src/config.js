const DEFAULTS = Object.freeze({
  host: "127.0.0.1",
  port: 8787,
  maxRequestBytes: 32768,
  rateLimitWindowMs: 60000,
  rateLimitMaxRequests: 10,
  rateLimitMaxKeys: 10000,
  openAiTimeoutMs: 14000,
  openAiMaxOutputTokens: 1800,
  serverRequestTimeoutMs: 32000,
  trustProxy: false,
});

export class ConfigurationError extends Error {
  constructor(message) {
    super(message);
    this.name = "ConfigurationError";
  }
}

function required(env, name) {
  const value = String(env[name] || "").trim();
  if (!value) {
    throw new ConfigurationError(`${name} is required.`);
  }
  return value;
}

function integer(env, name, fallback, minimum, maximum) {
  const raw = String(env[name] || "").trim();
  if (!raw) return fallback;
  if (!/^\d+$/.test(raw)) {
    throw new ConfigurationError(`${name} must be an integer.`);
  }
  const value = Number(raw);
  if (!Number.isSafeInteger(value) || value < minimum || value > maximum) {
    throw new ConfigurationError(
      `${name} must be between ${minimum} and ${maximum}.`
    );
  }
  return value;
}

function boolean(env, name, fallback) {
  const raw = String(env[name] || "").trim().toLowerCase();
  if (!raw) return fallback;
  if (raw === "true") return true;
  if (raw === "false") return false;
  throw new ConfigurationError(`${name} must be true or false.`);
}

function originSet(raw) {
  const origins = String(raw || "")
    .split(",")
    .map((origin) => origin.trim())
    .filter(Boolean);
  if (origins.length === 0) {
    throw new ConfigurationError("ALLOWED_ORIGINS must name at least one origin.");
  }
  const validated = new Set();
  for (const origin of origins) {
    if (origin === "*") {
      throw new ConfigurationError("ALLOWED_ORIGINS cannot contain a wildcard.");
    }
    let parsed;
    try {
      parsed = new URL(origin);
    } catch {
      throw new ConfigurationError("ALLOWED_ORIGINS contains an invalid origin.");
    }
    if (
      !["http:", "https:"].includes(parsed.protocol) ||
      parsed.username ||
      parsed.password ||
      parsed.pathname !== "/" ||
      parsed.search ||
      parsed.hash ||
      parsed.origin !== origin
    ) {
      throw new ConfigurationError(
        "ALLOWED_ORIGINS entries must be exact HTTP(S) origins without paths."
      );
    }
    validated.add(origin);
  }
  return validated;
}

export function loadConfig(env = process.env) {
  const config = {
    openAiApiKey: required(env, "OPENAI_API_KEY"),
    openAiModel: required(env, "OPENAI_MODEL"),
    host: String(env.HOST || DEFAULTS.host).trim(),
    port: integer(env, "PORT", DEFAULTS.port, 1, 65535),
    allowedOrigins: originSet(required(env, "ALLOWED_ORIGINS")),
    maxRequestBytes: integer(
      env,
      "MAX_REQUEST_BYTES",
      DEFAULTS.maxRequestBytes,
      1024,
      262144
    ),
    rateLimitWindowMs: integer(
      env,
      "RATE_LIMIT_WINDOW_MS",
      DEFAULTS.rateLimitWindowMs,
      1000,
      3600000
    ),
    rateLimitMaxRequests: integer(
      env,
      "RATE_LIMIT_MAX_REQUESTS",
      DEFAULTS.rateLimitMaxRequests,
      1,
      1000
    ),
    rateLimitMaxKeys: integer(
      env,
      "RATE_LIMIT_MAX_KEYS",
      DEFAULTS.rateLimitMaxKeys,
      100,
      100000
    ),
    openAiTimeoutMs: integer(
      env,
      "OPENAI_TIMEOUT_MS",
      DEFAULTS.openAiTimeoutMs,
      1000,
      60000
    ),
    openAiMaxOutputTokens: integer(
      env,
      "OPENAI_MAX_OUTPUT_TOKENS",
      DEFAULTS.openAiMaxOutputTokens,
      500,
      5000
    ),
    serverRequestTimeoutMs: integer(
      env,
      "SERVER_REQUEST_TIMEOUT_MS",
      DEFAULTS.serverRequestTimeoutMs,
      5000,
      120000
    ),
    trustProxy: boolean(env, "TRUST_PROXY", DEFAULTS.trustProxy),
  };
  if (!config.host) {
    throw new ConfigurationError("HOST cannot be empty.");
  }
  return Object.freeze(config);
}

export { DEFAULTS };
