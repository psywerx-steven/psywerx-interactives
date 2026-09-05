"use strict";

(function exposeCausalTools(global) {
  const RELATIONSHIP_KEYS = [
    "id", "sourceDriverId", "sourceDriverName", "targetDriverId",
    "targetDriverName", "causalRole", "polarity", "directness", "mechanism",
    "conditionsModerators", "moderatorDriverIds", "sourceLevel", "targetLevel",
    "levelTransitionMechanism", "lagProfile", "lagLowerBound", "lagUpperBound",
    "lagUnit", "lagNarrative", "exposurePattern", "effectPersistence",
    "evidenceStrength", "confidence", "generalizabilityContext",
    "reciprocalProcessId", "governanceClass", "supportingEvidenceIds",
    "notesCaveats", "source",
  ];
  const ENUMS = {
    causalRole: ["CAUSES", "ENABLES", "CONSTRAINS", "MODERATES"],
    polarity: ["POSITIVE", "NEGATIVE", "NON_MONOTONIC", "CONTEXT_DEPENDENT", "UNSIGNED"],
    directness: ["DIRECT_AT_STATED_RESOLUTION", "MEDIATED_PATH", "UNKNOWN"],
    lagProfile: [
      "IMMEDIATE", "SHORT", "INTERMEDIATE", "DELAYED", "LONG", "STRUCTURAL",
      "INTERGENERATIONAL", "MIXED_CONTEXT_DEPENDENT",
    ],
    exposurePattern: ["PULSE", "SUSTAINED", "CUMULATIVE", "REPEATED", "NOT_SPECIFIED"],
    evidenceStrength: ["Strong", "Moderate", "Mixed", "Limited", "Emerging"],
    confidence: ["HIGH", "MODERATE", "LOW"],
    governanceClass: ["CORE", "CONTEXT_DEPENDENT"],
  };
  const LEVELS = [
    "PERSON", "DYAD_INTERPERSONAL", "SMALL_GROUP", "NETWORK", "COMMUNITY",
    "ORGANIZATION", "INSTITUTIONAL_FIELD", "SOCIETY", "STATE_JURISDICTION",
    "INFORMATION_OBJECT_CORPUS", "INFORMATION_SYSTEM", "TECHNOLOGICAL_SYSTEM",
    "PHYSICAL_SETTING", "ECOLOGICAL_SYSTEM",
  ];
  const SOURCE_KEYS = ["workbook", "worksheet", "row"];
  const PRIVATE_PATH = /(?:[A-Za-z]:[\\/]|file:\/\/|analysis[\\/]|source-data[\\/])/i;

  function sameKeys(record, expected) {
    const actual = Object.keys(record).sort();
    const wanted = [...expected].sort();
    return actual.length === wanted.length &&
      actual.every((key, index) => key === wanted[index]);
  }

  function nonEmptyString(value) {
    return typeof value === "string" && value.trim() !== "";
  }

  function causalEnvelope(envelope) {
    if (!envelope || envelope.schemaVersion !== "3.0") return envelope;
    const relationships = Array.isArray(envelope.relationships)
      ? envelope.relationships.filter((relationship) =>
        relationship.relationFamily === "CAUSAL" &&
        relationship.governanceStatus === "ACTIVE" &&
        relationship.legacyRelationship !== null
      ).map((relationship) => ({
        id: relationship.id,
        sourceDriverId: relationship.subjectEntityId,
        sourceDriverName: relationship.subjectEntityName,
        targetDriverId: relationship.objectEntityId,
        targetDriverName: relationship.objectEntityName,
        causalRole: relationship.predicate,
        polarity: relationship.polarity,
        directness: relationship.directness,
        mechanism: relationship.mechanism,
        conditionsModerators: relationship.conditionsModerators,
        moderatorDriverIds: relationship.moderatorEntityIds,
        sourceLevel: relationship.subjectLevel,
        targetLevel: relationship.objectLevel,
        levelTransitionMechanism: relationship.levelTransitionMechanism,
        lagProfile: relationship.lagProfile,
        lagLowerBound: relationship.lagLowerBound,
        lagUpperBound: relationship.lagUpperBound,
        lagUnit: relationship.lagUnit,
        lagNarrative: relationship.lagNarrative,
        exposurePattern: relationship.exposurePattern,
        effectPersistence: relationship.effectPersistence,
        evidenceStrength: relationship.evidenceStrength,
        confidence: relationship.confidence,
        generalizabilityContext: relationship.generalizabilityContext,
        reciprocalProcessId: relationship.reciprocalProcessId,
        governanceClass: relationship.governanceClass,
        supportingEvidenceIds: relationship.supportingEvidenceIds,
        notesCaveats: relationship.notesCaveats,
        source: relationship.source,
      })) : [];
    return { schemaVersion: "2.0", relationships };
  }

  function validate(envelope, driverById) {
    envelope = causalEnvelope(envelope);
    const errors = [];
    if (!envelope || typeof envelope !== "object" || Array.isArray(envelope)) {
      throw new Error("Relationship data is not an object.");
    }
    if (!sameKeys(envelope, ["schemaVersion", "relationships"])) {
      errors.push("Relationship data has unexpected or missing envelope keys.");
    }
    if (envelope.schemaVersion !== "2.0") {
      errors.push("Relationship data does not use Relationship Schema v2.0.");
    }
    if (!Array.isArray(envelope.relationships)) {
      errors.push("Relationship data does not contain a relationships array.");
    }
    if (errors.length) {
      throw new Error("Relationship data validation failed: " + errors.join(" "));
    }

    const ids = new Set();
    const pairs = new Set();
    const reciprocalGroups = new Map();
    envelope.relationships.forEach((relationship, index) => {
      const label = "Relationship record " + String(index + 1);
      if (!relationship || typeof relationship !== "object" || Array.isArray(relationship)) {
        errors.push(label + " is not an object.");
        return;
      }
      if (!sameKeys(relationship, RELATIONSHIP_KEYS)) {
        errors.push(label + " has unexpected or missing fields.");
      }
      [
        "id", "sourceDriverId", "sourceDriverName", "targetDriverId",
        "targetDriverName", "mechanism", "conditionsModerators", "sourceLevel",
        "targetLevel", "lagNarrative", "evidenceStrength", "generalizabilityContext",
      ].forEach((field) => {
        if (!nonEmptyString(relationship[field])) {
          errors.push(label + " has no valid " + field + ".");
        }
      });
      Object.entries(ENUMS).forEach(([field, allowed]) => {
        const values = field === "lagProfile" ? relationship[field] : [relationship[field]];
        if (!Array.isArray(values) || values.length === 0 ||
            values.some((value) => !allowed.includes(value))) {
          errors.push(label + " has an invalid " + field + ".");
        }
      });
      if (!LEVELS.includes(relationship.sourceLevel) || !LEVELS.includes(relationship.targetLevel)) {
        errors.push(label + " has an invalid endpoint level.");
      }
      ["moderatorDriverIds", "supportingEvidenceIds"].forEach((field) => {
        if (!Array.isArray(relationship[field]) ||
            relationship[field].some((value) => !nonEmptyString(value))) {
          errors.push(label + " has an invalid " + field + " list.");
        }
      });
      [
        "levelTransitionMechanism", "lagUnit", "effectPersistence",
        "reciprocalProcessId", "notesCaveats",
      ].forEach((field) => {
        if (relationship[field] !== null && !nonEmptyString(relationship[field])) {
          errors.push(label + " has an invalid optional " + field + ".");
        }
      });
      if (!Array.isArray(relationship.supportingEvidenceIds) ||
          relationship.supportingEvidenceIds.length === 0) {
        errors.push(label + " has no supporting Evidence IDs.");
      }
      const source = driverById.get(relationship.sourceDriverId);
      const target = driverById.get(relationship.targetDriverId);
      if (!source || source.name !== relationship.sourceDriverName) {
        errors.push(label + " has an unresolved or mismatched source Entity.");
      }
      if (!target || target.name !== relationship.targetDriverName) {
        errors.push(label + " has an unresolved or mismatched target Entity.");
      }
      (Array.isArray(relationship.moderatorDriverIds)
        ? relationship.moderatorDriverIds : []).forEach((driverId) => {
        if (!driverById.has(driverId)) {
          errors.push(label + " references an unknown moderator Entity.");
        }
      });
      if (relationship.sourceDriverId === relationship.targetDriverId) {
        errors.push(label + " is a self-edge.");
      }
      const pair = relationship.sourceDriverId + "\u0000" + relationship.targetDriverId;
      if (ids.has(relationship.id)) errors.push("Duplicate Relationship ID: " + relationship.id + ".");
      if (pairs.has(pair)) errors.push("Duplicate directed endpoint pair: " + pair.replace("\u0000", " -> ") + ".");
      ids.add(relationship.id);
      pairs.add(pair);
      if (relationship.sourceLevel !== relationship.targetLevel &&
          !nonEmptyString(relationship.levelTransitionMechanism)) {
        errors.push(label + " crosses levels without a transition mechanism.");
      }
      const bounds = [relationship.lagLowerBound, relationship.lagUpperBound];
      const hasNumericLag = bounds.some((value) => value !== null);
      if (hasNumericLag &&
          (!bounds.every((value) => typeof value === "number" && Number.isFinite(value)) ||
           !nonEmptyString(relationship.lagUnit))) {
        errors.push(label + " has an incomplete numeric lag profile.");
      }
      if (!hasNumericLag && relationship.lagUnit !== null) {
        errors.push(label + " supplies a lag unit without numeric bounds.");
      }
      if (relationship.directness === "MEDIATED_PATH" &&
          !/mediated-path segment/i.test(relationship.notesCaveats || "")) {
        errors.push(label + " is a mediated path segment without its required disclosure.");
      }
      if (!relationship.source || typeof relationship.source !== "object" ||
          Array.isArray(relationship.source) || !sameKeys(relationship.source, SOURCE_KEYS) ||
          !nonEmptyString(relationship.source.workbook) ||
          relationship.source.worksheet !== "Relationships" ||
          !Number.isInteger(relationship.source.row) || relationship.source.row < 1) {
        errors.push(label + " has invalid generated provenance.");
      }
      if (PRIVATE_PATH.test(JSON.stringify(relationship))) {
        errors.push(label + " exposes a local or private path.");
      }
      if (relationship.reciprocalProcessId !== null) {
        if (!nonEmptyString(relationship.reciprocalProcessId)) {
          errors.push(label + " has an invalid reciprocal-process ID.");
        } else {
          const group = reciprocalGroups.get(relationship.reciprocalProcessId) || [];
          group.push(relationship);
          reciprocalGroups.set(relationship.reciprocalProcessId, group);
        }
      }
    });

    reciprocalGroups.forEach((group, processId) => {
      if (group.length !== 2 ||
          group[0].sourceDriverId !== group[1].targetDriverId ||
          group[0].targetDriverId !== group[1].sourceDriverId) {
        errors.push("Reciprocal process " + processId + " is not an opposite directed pair.");
      }
    });
    if (errors.length) {
      throw new Error(
        "Relationship data validation failed: " + errors.slice(0, 6).join(" ") +
        (errors.length > 6 ? " " + String(errors.length - 6) + " more errors." : "")
      );
    }
    return envelope.relationships;
  }

  function createIndex(relationships) {
    const byId = new Map();
    const upstream = new Map();
    const downstream = new Map();
    relationships.forEach((relationship) => {
      byId.set(relationship.id, relationship);
      if (!downstream.has(relationship.sourceDriverId)) downstream.set(relationship.sourceDriverId, []);
      if (!upstream.has(relationship.targetDriverId)) upstream.set(relationship.targetDriverId, []);
      downstream.get(relationship.sourceDriverId).push(relationship);
      upstream.get(relationship.targetDriverId).push(relationship);
    });
    return { byId, upstream, downstream, relationships };
  }

  function includesFilter(value, selected) {
    return !selected || selected.length === 0 || selected.includes(value);
  }

  function matches(relationship, options, relatedDriver) {
    const filters = options || {};
    return includesFilter(relationship.causalRole, filters.roles) &&
      includesFilter(relationship.polarity, filters.polarities) &&
      includesFilter(relationship.directness, filters.directness) &&
      includesFilter(relationship.confidence, filters.confidence) &&
      includesFilter(relationship.evidenceStrength, filters.evidenceStrength) &&
      includesFilter(relationship.governanceClass, filters.governanceClasses) &&
      (!filters.layer || (relatedDriver && relatedDriver.layer === filters.layer));
  }

  function shortestPaths(index, startId, endId, options, driverById) {
    const maxHops = Math.min(6, Math.max(1, Number(options.maxHops) || 4));
    const maxPaths = Math.min(8, Math.max(1, Number(options.maxPaths) || 5));
    const queue = [{ nodes: [startId], edges: [] }];
    const results = [];
    let foundDepth = null;
    let expansions = 0;
    while (queue.length && results.length < maxPaths && expansions < 5000) {
      const path = queue.shift();
      const current = path.nodes[path.nodes.length - 1];
      if (foundDepth !== null && path.edges.length >= foundDepth) continue;
      if (path.edges.length >= maxHops) continue;
      const outgoing = index.downstream.get(current) || [];
      for (const relationship of outgoing) {
        const next = relationship.targetDriverId;
        if (path.nodes.includes(next) ||
            !matches(relationship, options, driverById.get(next))) continue;
        expansions += 1;
        const candidate = {
          nodes: path.nodes.concat(next),
          edges: path.edges.concat(relationship),
        };
        if (next === endId) {
          if (foundDepth === null) foundDepth = candidate.edges.length;
          if (candidate.edges.length === foundDepth) results.push(candidate);
        } else if (foundDepth === null) {
          queue.push(candidate);
        }
      }
    }
    return { paths: results, truncated: expansions >= 5000, maxHops };
  }

  function boundedNeighborhood(index, centerId, options, driverById) {
    const maxHops = Number(options.maxHops) === 2 ? 2 : 1;
    const direction = ["upstream", "downstream"].includes(options.direction)
      ? options.direction : "both";
    const maxNodes = 25;
    const maxEdges = 40;
    const nodeDepths = new Map([[centerId, 0]]);
    const edges = new Map();
    let truncated = false;

    function walk(kind, sign) {
      const queue = [{ id: centerId, depth: 0 }];
      const seen = new Set([centerId]);
      while (queue.length) {
        const current = queue.shift();
        if (current.depth >= maxHops) continue;
        const candidates = index[kind].get(current.id) || [];
        for (const relationship of candidates) {
          const nextId = kind === "upstream"
            ? relationship.sourceDriverId : relationship.targetDriverId;
          if (!matches(relationship, options, driverById.get(nextId))) continue;
          if (edges.size >= maxEdges || (!nodeDepths.has(nextId) && nodeDepths.size >= maxNodes)) {
            truncated = true;
            continue;
          }
          edges.set(relationship.id, relationship);
          const nextDepth = current.depth + 1;
          const signedDepth = sign * nextDepth;
          if (!nodeDepths.has(nextId) || Math.abs(nodeDepths.get(nextId)) > nextDepth) {
            nodeDepths.set(nextId, signedDepth);
          }
          if (!seen.has(nextId)) {
            seen.add(nextId);
            queue.push({ id: nextId, depth: nextDepth });
          }
        }
      }
    }

    if (direction !== "downstream") walk("upstream", -1);
    if (direction !== "upstream") walk("downstream", 1);
    return { nodeDepths, edges: [...edges.values()], truncated, maxNodes, maxEdges };
  }

  global.PsywerxCausal = Object.freeze({
    ENUMS,
    validate,
    createIndex,
    matches,
    shortestPaths,
    boundedNeighborhood,
  });
})(window);
