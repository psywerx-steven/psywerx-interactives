"use strict";

/*
 * Source Explorer projection
 * --------------------------
 * data/sources.json remains the governed bibliographic registry. This module
 * creates a read-only presentation index from canonical Entity.keySources.
 * Driver backlinks are explicit provenance; Family and Layer IDs are always
 * derived through Driver -> Family -> Layer. RDS backlinks are retained in
 * rdsIds and never participate in Driver, Family, or Layer facets.
 *
 * Governed source IDs are stable identities. Locator/citation collisions are
 * reported as suspected duplicates, not merged automatically: the registry
 * contains known cases where a shared URL and conflicting citation text make
 * identity uncertain. That conservative rule prevents scientific records from
 * being collapsed merely to improve bibliography metrics.
 */
(function exposeSourceIndex(root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.PSYWERX_SOURCE_INDEX = Object.freeze(api);
})(typeof globalThis !== "undefined" ? globalThis : this, function sourceIndexFactory() {
  const DRIVER_TYPE = "DRIVER";
  const RDS_TYPE = "RELATIONAL_DERIVED_STATE";
  const FUTURE_ANNOTATION_FIELDS = Object.freeze([
    "summary", "evidenceNotes", "studyType", "methodology",
    "populationContext", "relevantFindings", "limitations",
    "evidenceQuality", "relevantMechanisms",
  ]);

  function hasText(value) {
    return typeof value === "string" && value.trim() !== "";
  }

  function normalizedText(value) {
    return String(value || "").normalize("NFKD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLocaleLowerCase()
      .replace(/[^\p{L}\p{N}]+/gu, " ")
      .trim();
  }

  function normalizedDoi(value) {
    if (!hasText(value)) return null;
    let candidate = value.trim().replace(/^doi:\s*/i, "");
    candidate = candidate.replace(/^https?:\/\/(?:dx\.)?doi\.org\//i, "");
    try { candidate = decodeURIComponent(candidate); } catch (_error) { /* keep source text */ }
    candidate = candidate.replace(/[\s.,;]+$/g, "").toLocaleLowerCase();
    return /^10\.\d{4,9}\/[\S]+$/i.test(candidate) ? candidate : null;
  }

  function sourceDoi(source) {
    const candidates = [source.doi, source.resolvedIdentifier, source.sourceUrl, source.href];
    for (const candidate of candidates) {
      const doi = normalizedDoi(candidate);
      if (doi) return doi;
      if (hasText(candidate)) {
        const match = candidate.match(/(?:doi\.org\/)?(10\.\d{4,9}\/[^\s?#]+)/i);
        const embedded = match && normalizedDoi(match[1]);
        if (embedded) return embedded;
      }
    }
    return null;
  }

  function canonicalUrl(value) {
    if (!hasText(value)) return null;
    try {
      const parsed = new URL(value);
      if (!['https:', 'http:'].includes(parsed.protocol)) return null;
      parsed.hash = "";
      parsed.hostname = parsed.hostname.toLocaleLowerCase();
      if ((parsed.protocol === "https:" && parsed.port === "443") ||
          (parsed.protocol === "http:" && parsed.port === "80")) parsed.port = "";
      if (parsed.pathname !== "/") parsed.pathname = parsed.pathname.replace(/\/+$/, "");
      return parsed.href;
    } catch (_error) { return null; }
  }

  function parseCitation(source) {
    const citation = source.citationText.trim();
    const canonicalYear = Number.isInteger(source.year) ? source.year : null;
    let authors = null;
    let title = null;
    let publisherOrJournal = null;
    let parsedYear = canonicalYear;
    let match = citation.match(/^(.+?)\s+\((\d{4})\)\s+(?:\u2014|\u00e2\u20ac\u201d)\s+(.+)$/u);
    if (match) {
      authors = match[1].trim() || null;
      parsedYear = canonicalYear || Number(match[2]);
      title = match[3].trim() || null;
    } else {
      match = citation.match(/^(.+?)\s+\((\d{4})\)\.\s+(.+)$/u);
      if (match) {
        authors = match[1].trim() || null;
        parsedYear = canonicalYear || Number(match[2]);
        const segments = match[3].split(/\.\s+(?=[A-Z0-9])/u);
        title = segments.shift().trim() || null;
        publisherOrJournal = segments.join(". ").trim() || null;
      } else {
        match = citation.match(/^(.+?)\s*\((\d{4})\)\.?$/u);
        if (match) {
          title = match[1].trim() || null;
          parsedYear = canonicalYear || Number(match[2]);
        }
      }
    }
    return { authors, title, year: parsedYear, publisherOrJournal };
  }

  function bibliographicIdentity(source, parsed) {
    const doi = sourceDoi(source);
    if (doi) return "doi:" + doi;
    const url = canonicalUrl(source.sourceUrl);
    if (url) return "url:" + url;
    if (parsed.title && parsed.year) {
      return "bibliographic:" + [parsed.authors, parsed.title, parsed.year]
        .map(normalizedText).join("|");
    }
    return "citation:" + normalizedText(source.citationText);
  }

  function sortedUnique(values) {
    return [...new Set(values)].sort((a, b) => String(a).localeCompare(
      String(b), undefined, { sensitivity: "base", numeric: true }
    ));
  }

  function assertEnvelope(sourceEnvelope) {
    if (!sourceEnvelope || sourceEnvelope.schemaVersion !== "1.0" ||
        !Array.isArray(sourceEnvelope.sources)) {
      throw new Error("Source data does not use Source Schema v1.0.");
    }
  }

  function filterSources(sources, query, selections = {}) {
    const normalizedQuery = normalizedText(query);
    const facets = ["layerIds", "familyIds", "driverIds"];
    return sources.filter((source) => {
      if (normalizedQuery && !source.searchText.includes(normalizedQuery)) return false;
      return facets.every((field) => {
        const selected = selections[field] instanceof Set
          ? selections[field] : new Set(selections[field] || []);
        return selected.size === 0 || source[field].some((value) => selected.has(value));
      });
    });
  }

  function buildSourceIndex(sourceEnvelope, entities, families) {
    assertEnvelope(sourceEnvelope);
    if (!Array.isArray(entities) || !Array.isArray(families)) {
      throw new Error("Source projection requires canonical Entity and Family arrays.");
    }
    const familyById = new Map(families.map((family) => [family.id, family]));
    const sourceRecords = new Map();
    sourceEnvelope.sources.forEach((source) => {
      if (!source || !hasText(source.id) || !hasText(source.citationText)) {
        throw new Error("Source data contains an invalid record.");
      }
      if (sourceRecords.has(source.id)) throw new Error("Duplicate Source ID: " + source.id + ".");
      sourceRecords.set(source.id, source);
    });

    const driverRefs = new Map();
    const rdsRefs = new Map();
    const entityById = new Map();
    let rawSourceReferences = 0;
    entities.forEach((entity) => {
      entityById.set(entity.id, entity);
      const target = entity.entityType === DRIVER_TYPE ? driverRefs
        : entity.entityType === RDS_TYPE ? rdsRefs : null;
      if (!target) return;
      const references = Array.isArray(entity.keySources) ? entity.keySources : [];
      rawSourceReferences += references.length;
      references.forEach((sourceId) => {
        if (!sourceRecords.has(sourceId)) {
          throw new Error("Entity " + entity.id + " cites missing Source " + sourceId + ".");
        }
        if (!target.has(sourceId)) target.set(sourceId, new Set());
        target.get(sourceId).add(entity.id);
      });
    });

    const usedSourceIds = sortedUnique([...driverRefs.keys(), ...rdsRefs.keys()]);
    const normalizedSources = usedSourceIds.map((sourceId) => {
      const source = sourceRecords.get(sourceId);
      const parsed = parseCitation(source);
      const driverIds = sortedUnique([...(driverRefs.get(sourceId) || [])]);
      const rdsIds = sortedUnique([...(rdsRefs.get(sourceId) || [])]);
      const familyIds = sortedUnique(driverIds.map((driverId) => {
        const driver = entityById.get(driverId);
        return driver && driver.primaryFamilyId;
      }).filter(Boolean));
      const layerIds = sortedUnique(familyIds.map((familyId) => {
        const family = familyById.get(familyId);
        if (!family) throw new Error("Source " + sourceId + " derives an unknown Family " + familyId + ".");
        return family.layer;
      }));
      const doi = sourceDoi(source);
      const url = canonicalUrl(source.sourceUrl) ||
        (source.resolutionType === "SEARCH" ? null : canonicalUrl(source.href));
      const normalized = {
        sourceId,
        citation: source.citationText,
        title: parsed.title,
        authors: parsed.authors,
        year: parsed.year,
        sourceType: hasText(source.evidenceType) ? source.evidenceType : null,
        publisherOrJournal: parsed.publisherOrJournal,
        doi,
        url,
        externalUrl: canonicalUrl(source.href) || url,
        externalLinkLabel: hasText(source.linkLabel) ? source.linkLabel : null,
        driverIds,
        rdsIds,
        familyIds,
        layerIds,
        evidenceStrength: hasText(source.evidenceStrength) ? source.evidenceStrength : null,
        summary: hasText(source.summary) ? source.summary : null,
        evidenceNotes: null,
        studyType: null,
        methodology: null,
        populationContext: null,
        relevantFindings: null,
        limitations: null,
        evidenceQuality: null,
        relevantMechanisms: null,
        identityKey: bibliographicIdentity(source, parsed),
      };
      normalized.searchText = normalizedText([
        normalized.sourceId, normalized.citation, normalized.title, normalized.authors,
        normalized.year, normalized.sourceType, normalized.publisherOrJournal,
        normalized.doi, normalized.url,
      ].filter((value) => value !== null).join(" "));
      return Object.freeze(normalized);
    });

    const identityGroups = new Map();
    normalizedSources.forEach((source) => {
      if (!identityGroups.has(source.identityKey)) identityGroups.set(source.identityKey, []);
      identityGroups.get(source.identityKey).push(source);
    });
    const suspectedDuplicateGroups = [...identityGroups.entries()]
      .filter(([, group]) => group.length > 1)
      .map(([identityKey, group]) => Object.freeze({
        identityKey,
        sourceIds: group.map((source) => source.sourceId),
        citations: group.map((source) => source.citation),
      }))
      .sort((a, b) => a.identityKey.localeCompare(b.identityKey));

    const audit = Object.freeze({
      totalRawSourceReferences: rawSourceReferences,
      totalNormalizedUniqueSources: normalizedSources.length,
      linkedToExactlyOneDriver: normalizedSources.filter((source) => source.driverIds.length === 1).length,
      linkedToMultipleDrivers: normalizedSources.filter((source) => source.driverIds.length > 1).length,
      linkedOnlyToRds: normalizedSources.filter((source) =>
        source.driverIds.length === 0 && source.rdsIds.length > 0).length,
      withDoi: normalizedSources.filter((source) => source.doi).length,
      withUrl: normalizedSources.filter((source) => source.url).length,
      withParsedTitle: normalizedSources.filter((source) => source.title).length,
      withIncompleteStructuredMetadata: normalizedSources.filter((source) =>
        !source.title || !source.authors || !source.year || !source.publisherOrJournal).length,
      unreferencedRegistryRecords: sourceEnvelope.sources.length - normalizedSources.length,
      suspectedDuplicateGroupCount: suspectedDuplicateGroups.length,
    });

    return Object.freeze({
      sources: Object.freeze(normalizedSources),
      sourceById: new Map(normalizedSources.map((source) => [source.sourceId, source])),
      suspectedDuplicateGroups: Object.freeze(suspectedDuplicateGroups),
      futureAnnotationFields: FUTURE_ANNOTATION_FIELDS,
      audit,
    });
  }

  return Object.freeze({
    FUTURE_ANNOTATION_FIELDS,
    normalizedText,
    normalizedDoi,
    canonicalUrl,
    parseCitation,
    bibliographicIdentity,
    filterSources,
    buildSourceIndex,
  });
});
