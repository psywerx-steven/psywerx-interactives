import test from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { createHttpHandler } from "../src/http-app.js";
import { validRequest, validResponse } from "./fixtures.js";

const config = Object.freeze({
  allowedOrigins: new Set(["http://localhost:8000"]),
  maxRequestBytes: 32768,
  rateLimitWindowMs: 60000,
  rateLimitMaxRequests: 2,
  rateLimitMaxKeys: 100,
  trustProxy: false,
});

async function withServer(run, overrides = {}) {
  const handler = createHttpHandler({
    config: { ...config, ...overrides },
    catalog: { resolve: () => ({ driver: { id: "BIO-001" } }) },
    operationalize: async () => ({ result: validResponse(), attempts: 1 }),
    logger: () => {},
  });
  const server = createServer(handler);
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const address = server.address();
  try {
    await run(`http://127.0.0.1:${address.port}`);
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
}

test("health endpoint returns minimal status", async () => {
  await withServer(async (base) => {
    const response = await fetch(`${base}/health`);
    assert.equal(response.status, 200);
    assert.deepEqual(await response.json(), { status: "ok" });
  });
});

test("operationalization endpoint returns the exact success object", async () => {
  await withServer(async (base) => {
    const response = await fetch(`${base}/v1/operationalize`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Origin: "http://localhost:8000",
      },
      body: JSON.stringify(validRequest()),
    });
    assert.equal(response.status, 200);
    assert.deepEqual(await response.json(), validResponse());
    assert.equal(response.headers.get("access-control-allow-origin"), "http://localhost:8000");
  });
});

test("unlisted origins are rejected", async () => {
  await withServer(async (base) => {
    const response = await fetch(`${base}/v1/operationalize`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Origin: "https://example.invalid" },
      body: JSON.stringify(validRequest()),
    });
    assert.equal(response.status, 403);
    assert.equal((await response.json()).code, "ORIGIN_NOT_ALLOWED");
  });
});

test("request-size and in-memory rate limits fail clearly", async () => {
  await withServer(
    async (base) => {
      const oversized = await fetch(`${base}/v1/operationalize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(validRequest()),
      });
      assert.equal(oversized.status, 413);
    },
    { maxRequestBytes: 100 }
  );

  await withServer(async (base) => {
    const options = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(validRequest()),
    };
    assert.equal((await fetch(`${base}/v1/operationalize`, options)).status, 200);
    assert.equal((await fetch(`${base}/v1/operationalize`, options)).status, 200);
    const limited = await fetch(`${base}/v1/operationalize`, options);
    assert.equal(limited.status, 429);
    assert.equal((await limited.json()).code, "RATE_LIMITED");
  });
});
