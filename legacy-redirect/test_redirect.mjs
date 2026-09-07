import assert from "node:assert/strict";
import test from "node:test";
import { redirectLegacyRequest } from "./worker.mjs";

async function location(path) {
  const response = redirectLegacyRequest(new Request(`https://drivers.psywerx.io${path}`));
  assert.equal(response.status, 308);
  return response.headers.get("location");
}

test("legacy root goes to the Driver Explorer", async () => {
  assert.equal(await location("/"), "https://psywerx.io/drivers/");
});

test("Driver paths and queries are preserved", async () => {
  assert.equal(
    await location("/drivers/?q=motivation&layer=individual"),
    "https://psywerx.io/drivers/?q=motivation&layer=individual",
  );
});

test("Cognitive Security paths and queries are preserved", async () => {
  assert.equal(
    await location("/cognitive-security/?view=themes&q=trust"),
    "https://psywerx.io/cognitive-security/?view=themes&q=trust",
  );
});

test("static asset and future deep paths are preserved", async () => {
  assert.equal(await location("/drivers/app.js?v=1"), "https://psywerx.io/drivers/app.js?v=1");
});

test("other hosts fail closed", () => {
  const response = redirectLegacyRequest(new Request("https://example.com/drivers/"));
  assert.equal(response.status, 421);
});
