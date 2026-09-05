import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { loadCatalog } from "../src/catalog.js";
import { validateOperationalizationRequest } from "../src/contracts.js";

const DATA_URLS = Object.freeze({
  drivers: new URL("../../data/entities.json", import.meta.url),
  families: new URL("../../data/families.json", import.meta.url),
  plainLanguage: new URL("../../data/plain_language.json", import.meta.url),
});

function readJson(url) {
  return JSON.parse(readFileSync(url, "utf8"));
}

test("every current canonical Entity resolves against the exact browser contract", () => {
  const drivers = readJson(DATA_URLS.drivers);
  const familyData = readJson(DATA_URLS.families);
  const plainLanguageData = readJson(DATA_URLS.plainLanguage);
  const families = new Map(
    familyData.families.map((family) => [
      JSON.stringify([family.layer, family.name]),
      family,
    ])
  );
  const plainLanguage = new Map(
    plainLanguageData.drivers.map((record) => [record.driverId, record])
  );
  const catalog = loadCatalog();
  let protectedDriverCount = 0;

  for (const driver of drivers) {
    const family = families.get(JSON.stringify([driver.layer, driver.family]));
    const plain = plainLanguage.get(driver.id) || null;
    if (!plain) protectedDriverCount += 1;
    const request = {
      actor: "A bounded actor",
      behaviorObjective: "A bounded behavior or objective",
      context: "A bounded scenario context",
      clarificationAnswer: null,
      driver: {
        id: driver.id,
        entityType: driver.entityType,
        entitySubtype: driver.entitySubtype ?? null,
        name: driver.name,
        definition: driver.definition,
        plainLanguageExplanation: plain ? plain.plainLanguageExplanation : null,
        analyticQuestion: plain ? plain.analyticQuestion : null,
        whatThisDoesNotMean: plain ? plain.whatThisDoesNotMean : null,
        layer: driver.layer,
        family: driver.family,
        familyDefinition: family ? family.definition : null,
        familyIncludes: family ? family.includes : null,
        familyExclusions: family ? family.exclusions : null,
        mechanism: driver.mechanism,
        moderatorsBoundaryConditions: driver.moderatorsBoundaryConditions,
        indicators: driver.indicators,
        measurementAssessmentMethods: driver.measurementAssessmentMethods,
        observability: driver.observability,
        measurementCaveats: driver.measurementCaveats,
        dataType: driver.dataType,
        timeScaleOfChange: driver.timeScaleOfChange,
        onsetCausalLag: driver.onsetCausalLag,
        commonMisinterpretations: driver.commonMisinterpretations,
        evidenceNotes: driver.evidenceNotes,
        constituentSpecifications: driver.constituentSpecifications || [],
        derivationType: driver.derivationType ?? null,
        derivationLogic: driver.derivationLogic ?? null,
        scopeRequirements: driver.scopeRequirements ?? null,
        directManipulability: driver.directManipulability ?? null,
        recalculationBehavior: driver.recalculationBehavior ?? null,
        uncertaintyPropagation: driver.uncertaintyPropagation ?? null,
        compositeSpecification: driver.compositeSpecification ?? null,
        differenceSpecification: driver.differenceSpecification ?? null,
        networkMetricSpecification: driver.networkMetricSpecification ?? null,
        ratioSpecification: driver.ratioSpecification ?? null,
        temporalSpecification: driver.temporalSpecification ?? null,
      },
    };
    validateOperationalizationRequest(request);
    assert.equal(catalog.resolve(request).driver.id, driver.id);
  }

  assert.equal(drivers.length, 811);
  assert.equal(protectedDriverCount, 43);
});
