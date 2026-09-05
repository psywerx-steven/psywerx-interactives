import test from "node:test";
import assert from "node:assert/strict";
import { CatalogError, createCatalog } from "../src/catalog.js";
import { fixtureData, rdsFixtureData, validRequest } from "./fixtures.js";

test("catalog verifies the browser snapshot and returns bounded server context", () => {
  const data = fixtureData();
  const catalog = createCatalog(data.drivers, data.families, data.plainLanguage);
  const context = catalog.resolve(validRequest(data));
  assert.equal(context.driver.id, "BIO-001");
  assert.equal(context.plainLanguage.label, data.plain.plainLanguageLabel);
  assert.equal(Object.hasOwn(context.driver, "evidenceNotes"), false);
  assert.equal(Object.hasOwn(context.driver, "source"), false);
});

test("catalog rejects a stale or tampered Driver snapshot", () => {
  const data = fixtureData();
  const request = validRequest(data);
  request.driver.definition = "A replacement supplied by the browser.";
  const catalog = createCatalog(data.drivers, data.families, data.plainLanguage);
  assert.throws(() => catalog.resolve(request), CatalogError);
});

test("canonical Drivers without public plain language remain eligible", () => {
  const data = fixtureData({ includePlainLanguage: false });
  const catalog = createCatalog(data.drivers, data.families, data.plainLanguage);
  const context = catalog.resolve(validRequest(data));
  assert.equal(context.plainLanguage.label, null);
  assert.equal(context.plainLanguage.explanation, null);
});

test("catalog preserves governed RDS identity and derivation context", () => {
  const data = rdsFixtureData();
  const catalog = createCatalog(data.drivers, data.families, data.plainLanguage);
  const context = catalog.resolve(validRequest(data));
  assert.equal(context.driver.id, "RDS-0001");
  assert.equal(context.driver.entityType, "RELATIONAL_DERIVED_STATE");
  assert.equal(context.driver.derivationType, "COMPOSITE");
  assert.equal(context.driver.mechanism, null);
  assert.equal(context.driver.constituentSpecifications[0].entityId, "INF-013");
});
