import { readFileSync } from "node:fs";

const DEFAULT_DATA_URLS = Object.freeze({
  drivers: new URL("../../data/entities.json", import.meta.url),
  families: new URL("../../data/families.json", import.meta.url),
  plainLanguage: new URL("../../data/plain_language.json", import.meta.url),
});

export class CatalogError extends Error {
  constructor(code, publicMessage, status = 422) {
    super(publicMessage);
    this.name = "CatalogError";
    this.code = code;
    this.publicMessage = publicMessage;
    this.status = status;
  }
}

function parseJson(url) {
  try {
    return JSON.parse(readFileSync(url, "utf8"));
  } catch {
    throw new CatalogError(
      "CATALOG_LOAD_FAILED",
      "Required public taxonomy data could not be loaded.",
      503
    );
  }
}

function uniqueMap(records, key, label) {
  const result = new Map();
  for (const record of records) {
    const identifier = record && record[key];
    if (typeof identifier !== "string" || !identifier || result.has(identifier)) {
      throw new CatalogError(
        "CATALOG_INVALID",
        `The public ${label} catalog is invalid.`,
        503
      );
    }
    result.set(identifier, record);
  }
  return result;
}

function familyKey(layer, family) {
  return JSON.stringify([layer, family]);
}

function sameValue(actual, expected) {
  if (Array.isArray(actual) || Array.isArray(expected)) {
    return Array.isArray(actual) && Array.isArray(expected) &&
      actual.length === expected.length &&
      actual.every((value, index) => sameValue(value, expected[index]));
  }
  if (actual && expected && typeof actual === "object" && typeof expected === "object") {
    const actualKeys = Object.keys(actual).sort();
    const expectedKeys = Object.keys(expected).sort();
    return actualKeys.length === expectedKeys.length &&
      actualKeys.every((key, index) => key === expectedKeys[index] &&
        sameValue(actual[key], expected[key]));
  }
  return actual === expected;
}

function rdsContext(entity) {
  return {
    entityType: entity.entityType,
    entitySubtype: entity.entitySubtype ?? null,
    constituentSpecifications: entity.constituentSpecifications || [],
    derivationType: entity.derivationType ?? null,
    derivationLogic: entity.derivationLogic ?? null,
    scopeRequirements: entity.scopeRequirements ?? null,
    directManipulability: entity.directManipulability ?? null,
    recalculationBehavior: entity.recalculationBehavior ?? null,
    uncertaintyPropagation: entity.uncertaintyPropagation ?? null,
    compositeSpecification: entity.compositeSpecification ?? null,
    differenceSpecification: entity.differenceSpecification ?? null,
    networkMetricSpecification: entity.networkMetricSpecification ?? null,
    ratioSpecification: entity.ratioSpecification ?? null,
    temporalSpecification: entity.temporalSpecification ?? null,
  };
}

export function createCatalog(driverData, familyData, plainLanguageData) {
  if (!Array.isArray(driverData)) {
    throw new CatalogError("CATALOG_INVALID", "The public Entity catalog is invalid.", 503);
  }
  if (!familyData || familyData.schemaVersion !== "1.0" || !Array.isArray(familyData.families)) {
    throw new CatalogError("CATALOG_INVALID", "The public Family catalog is invalid.", 503);
  }
  if (
    !plainLanguageData ||
    plainLanguageData.schemaVersion !== "1.0" ||
    !Array.isArray(plainLanguageData.drivers)
  ) {
    throw new CatalogError(
      "CATALOG_INVALID",
      "The public plain-language catalog is invalid.",
      503
    );
  }

  const drivers = uniqueMap(driverData, "id", "Entity");
  const plainLanguage = uniqueMap(
    plainLanguageData.drivers,
    "driverId",
    "plain-language"
  );
  const families = new Map();
  for (const family of familyData.families) {
    const key = familyKey(family && family.layer, family && family.name);
    if (
      !family ||
      typeof family.layer !== "string" ||
      typeof family.name !== "string" ||
      families.has(key)
    ) {
      throw new CatalogError("CATALOG_INVALID", "The public Family catalog is invalid.", 503);
    }
    families.set(key, family);
  }

  for (const plain of plainLanguage.values()) {
    const driver = drivers.get(plain.driverId);
    if (
      !driver ||
      typeof plain.plainLanguageLabel !== "string" ||
      typeof plain.plainLanguageExplanation !== "string" ||
      typeof plain.analyticQuestion !== "string" ||
      (plain.whatThisDoesNotMean !== null &&
        typeof plain.whatThisDoesNotMean !== "string")
    ) {
      throw new CatalogError(
        "CATALOG_INVALID",
        "The public plain-language catalog is invalid.",
        503
      );
    }
  }

  function resolve(request) {
    const supplied = request.driver;
    const driver = drivers.get(supplied.id);
    if (!driver) {
      throw new CatalogError(
        "DRIVER_NOT_AVAILABLE",
        "This Entity is not available for scenario operationalization."
      );
    }
    const plain = plainLanguage.get(driver.id) || null;
    const family = families.get(familyKey(driver.layer, driver.family));
    if (!family) {
      throw new CatalogError(
        "DRIVER_CONTEXT_UNAVAILABLE",
        "The governed Family context for this Entity is unavailable.",
        503
      );
    }

    const expected = {
      id: driver.id,
      ...rdsContext(driver),
      name: driver.name,
      definition: driver.definition,
      plainLanguageExplanation: plain ? plain.plainLanguageExplanation : null,
      analyticQuestion: plain ? plain.analyticQuestion : null,
      whatThisDoesNotMean: plain ? plain.whatThisDoesNotMean : null,
      layer: driver.layer,
      family: driver.family,
      familyDefinition: family.definition,
      familyIncludes: family.includes,
      familyExclusions: family.exclusions,
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
    };
    if (
      Object.keys(expected).some((field) => !sameValue(supplied[field], expected[field]))
    ) {
      throw new CatalogError(
        "STALE_DRIVER_CONTEXT",
        "Entity context is stale or invalid. Reload the Explorer and try again.",
        409
      );
    }

    return {
      driver: {
        id: driver.id,
        ...rdsContext(driver),
        name: driver.name,
        definition: driver.definition,
        layer: driver.layer,
        family: driver.family,
        dataType: driver.dataType,
        mechanism: driver.mechanism,
        moderatorsBoundaryConditions: driver.moderatorsBoundaryConditions,
        indicators: [...driver.indicators],
        measurementAssessmentMethods: driver.measurementAssessmentMethods,
        observability: driver.observability,
        measurementCaveats: driver.measurementCaveats,
        timeScaleOfChange: [...driver.timeScaleOfChange],
        onsetCausalLag: [...driver.onsetCausalLag],
        commonMisinterpretations: driver.commonMisinterpretations,
      },
      family: {
        name: family.name,
        definition: family.definition,
        includes: family.includes,
        exclusions: family.exclusions,
      },
      plainLanguage: {
        label: plain ? plain.plainLanguageLabel : null,
        explanation: plain ? plain.plainLanguageExplanation : null,
        analyticQuestion: plain ? plain.analyticQuestion : null,
        whatThisDoesNotMean: plain ? plain.whatThisDoesNotMean : null,
      },
    };
  }

  return Object.freeze({ resolve });
}

export function loadCatalog(urls = DEFAULT_DATA_URLS) {
  return createCatalog(
    parseJson(urls.drivers),
    parseJson(urls.families),
    parseJson(urls.plainLanguage)
  );
}

export { DEFAULT_DATA_URLS };
