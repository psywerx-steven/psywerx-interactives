"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const sourceIndex = require("../drivers/source-index.js");

const ROOT = path.resolve(__dirname, "..");
const readJson = (relativePath) => JSON.parse(
  fs.readFileSync(path.join(ROOT, relativePath), "utf8")
);

function fixture() {
  const families = [
    { id: "A-F1", name: "Alpha family", layer: "Psychological" },
    { id: "B-F1", name: "Beta family", layer: "Social" },
  ];
  const entities = [
    { id: "A-1", entityType: "DRIVER", primaryFamilyId: "A-F1", keySources: ["S-1", "S-1"] },
    { id: "A-2", entityType: "DRIVER", primaryFamilyId: "A-F1", keySources: ["S-1"] },
    { id: "B-1", entityType: "DRIVER", primaryFamilyId: "B-F1", keySources: ["S-1"] },
    { id: "RDS-1", entityType: "RELATIONAL_DERIVED_STATE", primaryFamilyId: "B-F1", keySources: ["S-1", "S-RDS"] },
  ];
  const sources = {
    schemaVersion: "1.0",
    sources: [
      {
        id: "S-1", citationText: "Example & Example (2020) — A useful source",
        year: 2020, evidenceType: "Review", evidenceStrength: "Moderate",
        sourceUrl: "https://doi.org/10.1234/EXAMPLE", href: "https://doi.org/10.1234/EXAMPLE",
        resolvedIdentifier: "10.1234/EXAMPLE", linkLabel: "Open source",
      },
      {
        id: "S-RDS", citationText: "RDS-only source", year: null,
        evidenceType: null, evidenceStrength: null, sourceUrl: null,
        href: "https://example.org/rds", resolvedIdentifier: null, linkLabel: "Open source",
      },
      {
        id: "S-MIN", citationText: "Minimal unreferenced citation", year: null,
        evidenceType: null, evidenceStrength: null, sourceUrl: null,
        href: null, resolvedIdentifier: null, linkLabel: null,
      },
    ],
  };
  return { families, entities, sources };
}

test("canonical projection is deterministic and preserves governed source IDs/citations", () => {
  const registry = readJson("data/sources.json");
  const entities = readJson("data/entities.json");
  const families = readJson("data/families.json").families;
  const first = sourceIndex.buildSourceIndex(registry, entities, families);
  const second = sourceIndex.buildSourceIndex(registry, entities, families);
  assert.deepEqual(first.sources, second.sources);
  assert.equal(first.audit.totalRawSourceReferences, 1893);
  assert.equal(first.audit.totalNormalizedUniqueSources, 510);
  assert.deepEqual(first.audit, {
    totalRawSourceReferences: 1893,
    totalNormalizedUniqueSources: 510,
    linkedToExactlyOneDriver: 168,
    linkedToMultipleDrivers: 334,
    linkedOnlyToRds: 8,
    withDoi: 226,
    withUrl: 509,
    withParsedTitle: 469,
    withIncompleteStructuredMetadata: 366,
    unreferencedRegistryRecords: 19,
    suspectedDuplicateGroupCount: 8,
  });
  for (const source of first.sources) {
    assert.equal(source.citation, registry.sources.find((row) => row.id === source.sourceId).citationText);
  }
});

test("one source record collects unique explicit Driver backlinks across Families and Layers", () => {
  const data = fixture();
  const projection = sourceIndex.buildSourceIndex(data.sources, data.entities, data.families);
  const source = projection.sourceById.get("S-1");
  assert.deepEqual(source.driverIds, ["A-1", "A-2", "B-1"]);
  assert.deepEqual(source.familyIds, ["A-F1", "B-F1"]);
  assert.deepEqual(source.layerIds, ["Psychological", "Social"]);
  assert.deepEqual(source.rdsIds, ["RDS-1"]);
  assert.equal(source.doi, "10.1234/example");
  assert.equal(source.citation, "Example & Example (2020) — A useful source");
});

test("RDS citations remain separate and never become Driver or taxonomy facet relationships", () => {
  const data = fixture();
  const source = sourceIndex.buildSourceIndex(data.sources, data.entities, data.families)
    .sourceById.get("S-RDS");
  assert.deepEqual(source.driverIds, []);
  assert.deepEqual(source.familyIds, []);
  assert.deepEqual(source.layerIds, []);
  assert.deepEqual(source.rdsIds, ["RDS-1"]);
});

test("minimal citations preserve source text without invented structured metadata", () => {
  const data = fixture();
  data.entities.push({
    id: "A-3", entityType: "DRIVER", primaryFamilyId: "A-F1", keySources: ["S-MIN"],
  });
  const source = sourceIndex.buildSourceIndex(data.sources, data.entities, data.families)
    .sourceById.get("S-MIN");
  assert.equal(source.citation, "Minimal unreferenced citation");
  for (const field of ["title", "authors", "year", "publisherOrJournal", "doi", "url", "summary"]) {
    assert.equal(source[field], null, field);
  }
});

test("keyword and facets implement OR within facets and AND across facets", () => {
  const data = fixture();
  const projection = sourceIndex.buildSourceIndex(data.sources, data.entities, data.families);
  const sources = projection.sources;
  assert.deepEqual(sourceIndex.filterSources(sources, "useful", {
    layerIds: new Set(["Psychological", "Institutional / Structural"]),
    familyIds: new Set(["A-F1", "missing-family"]),
    driverIds: new Set(["A-2", "missing-driver"]),
  }).map((source) => source.sourceId), ["S-1"]);
  assert.equal(sourceIndex.filterSources(sources, "no match", {}).length, 0);
  assert.equal(sourceIndex.filterSources(sources, "", {}).length, 2);
});

test("identity normalization follows DOI then URL and reports collisions without merging", () => {
  const data = fixture();
  const copy = { ...data.sources.sources[0], id: "S-2", citationText: "Conflicting citation" };
  data.sources.sources.push(copy);
  data.entities[0].keySources.push("S-2");
  const projection = sourceIndex.buildSourceIndex(data.sources, data.entities, data.families);
  assert.equal(projection.sources.length, 3);
  assert.deepEqual(projection.suspectedDuplicateGroups[0].sourceIds, ["S-1", "S-2"]);
  assert.match(projection.suspectedDuplicateGroups[0].identityKey, /^doi:/);
});
