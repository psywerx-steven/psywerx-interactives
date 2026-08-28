import { randomUUID } from "node:crypto";
import { CatalogError } from "./catalog.js";
import { ContractError, validateOperationalizationRequest } from "./contracts.js";
import { ScenarioServiceError } from "./openai-service.js";
import { createRateLimiter } from "./rate-limit.js";

class HttpError extends Error {
  constructor(status, code, publicMessage, headers = {}) {
    super(publicMessage);
    this.name = "HttpError";
    this.status = status;
    this.code = code;
    this.publicMessage = publicMessage;
    this.headers = headers;
  }
}

function contentHeaders(origin) {
  const headers = {
    "Cache-Control": "no-store",
    "Content-Type": "application/json; charset=utf-8",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
  };
  if (origin) {
    headers["Access-Control-Allow-Origin"] = origin;
    headers.Vary = "Origin";
  }
  return headers;
}

function writeJson(response, status, body, headers = {}, origin = null) {
  if (response.writableEnded) return;
  response.writeHead(status, { ...contentHeaders(origin), ...headers });
  response.end(JSON.stringify(body));
}

function validateOrigin(request, allowedOrigins) {
  const origin = request.headers.origin;
  if (origin === undefined) return null;
  if (typeof origin !== "string" || !allowedOrigins.has(origin)) {
    throw new HttpError(403, "ORIGIN_NOT_ALLOWED", "This request origin is not allowed.");
  }
  return origin;
}

function clientKey(request, trustProxy) {
  if (trustProxy) {
    const forwarded = request.headers["x-forwarded-for"];
    if (typeof forwarded === "string") {
      const first = forwarded.split(",", 1)[0].trim();
      if (first) return first.slice(0, 128);
    }
  }
  return String(request.socket.remoteAddress || "unknown").slice(0, 128);
}

function contentLength(request) {
  const raw = request.headers["content-length"];
  if (raw === undefined) return null;
  if (typeof raw !== "string" || !/^\d+$/.test(raw)) {
    throw new HttpError(400, "INVALID_CONTENT_LENGTH", "Content-Length is invalid.");
  }
  const value = Number(raw);
  if (!Number.isSafeInteger(value)) {
    throw new HttpError(400, "INVALID_CONTENT_LENGTH", "Content-Length is invalid.");
  }
  return value;
}

function readJsonBody(request, maximumBytes) {
  const declaredLength = contentLength(request);
  if (declaredLength !== null && declaredLength > maximumBytes) {
    request.resume();
    throw new HttpError(413, "REQUEST_TOO_LARGE", "The request body is too large.");
  }
  return new Promise((resolve, reject) => {
    let size = 0;
    let tooLarge = false;
    const chunks = [];
    request.on("data", (chunk) => {
      size += chunk.length;
      if (size > maximumBytes) {
        tooLarge = true;
        chunks.length = 0;
      } else if (!tooLarge) {
        chunks.push(chunk);
      }
    });
    request.on("end", () => {
      if (tooLarge) {
        reject(new HttpError(413, "REQUEST_TOO_LARGE", "The request body is too large."));
        return;
      }
      if (size === 0) {
        reject(new HttpError(400, "INVALID_JSON", "A JSON request body is required."));
        return;
      }
      try {
        resolve(JSON.parse(Buffer.concat(chunks).toString("utf8")));
      } catch {
        reject(new HttpError(400, "INVALID_JSON", "The request body is not valid JSON."));
      }
    });
    request.on("error", () =>
      reject(new HttpError(400, "REQUEST_READ_FAILED", "The request body could not be read."))
    );
  });
}

function publicError(error) {
  if (error instanceof HttpError) return error;
  if (error instanceof ContractError) {
    return new HttpError(400, error.code || "INVALID_REQUEST", error.message);
  }
  if (error instanceof CatalogError || error instanceof ScenarioServiceError) {
    return new HttpError(error.status, error.code, error.publicMessage);
  }
  return new HttpError(
    500,
    "INTERNAL_ERROR",
    "Scenario operationalization is temporarily unavailable."
  );
}

function defaultLogger(event) {
  console.info(JSON.stringify(event));
}

export function createHttpHandler({
  config,
  catalog,
  operationalize,
  logger = defaultLogger,
  now = Date.now,
}) {
  const rateLimiter = createRateLimiter({
    windowMs: config.rateLimitWindowMs,
    maxRequests: config.rateLimitMaxRequests,
    maxKeys: config.rateLimitMaxKeys,
    now,
  });

  return async function handle(request, response) {
    const startedAt = now();
    const requestId = randomUUID();
    response.setHeader("X-Request-Id", requestId);
    let status = 500;
    let errorCode = null;
    let route = "unknown";
    let origin = null;
    try {
      const url = new URL(request.url || "/", "http://service.invalid");
      const pathname = url.pathname;
      route = pathname === "/health"
        ? "/health"
        : pathname === "/v1/operationalize"
          ? "/v1/operationalize"
          : "other";
      if (url.search) {
        throw new HttpError(400, "QUERY_NOT_ALLOWED", "Query parameters are not allowed.");
      }
      origin = validateOrigin(request, config.allowedOrigins);

      if (request.method === "GET" && pathname === "/health") {
        status = 200;
        writeJson(response, status, { status: "ok" }, {}, origin);
        return;
      }

      if (request.method === "OPTIONS" && pathname === "/v1/operationalize") {
        if (!origin) {
          throw new HttpError(
            400,
            "ORIGIN_REQUIRED",
            "A permitted Origin header is required for preflight requests."
          );
        }
        status = 204;
        response.writeHead(status, {
          ...contentHeaders(origin),
          "Access-Control-Allow-Headers": "Content-Type",
          "Access-Control-Allow-Methods": "POST",
          "Access-Control-Max-Age": "600",
        });
        response.end();
        return;
      }

      if (pathname !== "/v1/operationalize") {
        throw new HttpError(404, "NOT_FOUND", "The requested endpoint was not found.");
      }
      if (request.method !== "POST") {
        throw new HttpError(405, "METHOD_NOT_ALLOWED", "Only POST is allowed.", {
          Allow: "POST, OPTIONS",
        });
      }
      const mediaType = String(request.headers["content-type"] || "")
        .split(";", 1)[0]
        .trim()
        .toLowerCase();
      if (mediaType !== "application/json") {
        throw new HttpError(
          415,
          "UNSUPPORTED_MEDIA_TYPE",
          "Content-Type must be application/json."
        );
      }
      const contentEncoding = String(request.headers["content-encoding"] || "identity")
        .trim()
        .toLowerCase();
      if (contentEncoding !== "identity") {
        throw new HttpError(
          415,
          "UNSUPPORTED_CONTENT_ENCODING",
          "Compressed request bodies are not supported."
        );
      }

      const rate = rateLimiter.consume(clientKey(request, config.trustProxy));
      const rateHeaders = {
        "RateLimit-Limit": String(config.rateLimitMaxRequests),
        "RateLimit-Remaining": String(rate.remaining),
        "RateLimit-Reset": String(Math.ceil(rate.resetMs / 1000)),
      };
      if (!rate.allowed) {
        throw new HttpError(
          429,
          "RATE_LIMITED",
          "Too many scenario requests. Please try again later.",
          { ...rateHeaders, "Retry-After": String(Math.ceil(rate.resetMs / 1000)) }
        );
      }

      const body = await readJsonBody(request, config.maxRequestBytes);
      validateOperationalizationRequest(body);
      const context = catalog.resolve(body);
      const generated = await operationalize(context, body);
      status = 200;
      writeJson(response, status, generated.result, rateHeaders, origin);
    } catch (error) {
      const safe = publicError(error);
      status = safe.status;
      errorCode = safe.code;
      writeJson(
        response,
        status,
        { error: safe.publicMessage, code: safe.code },
        safe.headers,
        origin
      );
    } finally {
      logger({
        event: "request_complete",
        requestId,
        method: request.method || "UNKNOWN",
        route,
        status,
        durationMs: Math.max(0, now() - startedAt),
        ...(errorCode ? { errorCode } : {}),
      });
    }
  };
}
