"""Governed additive Actions & Events contracts. No scientific writes or activation.

Existing RI records are read through SAME_IDENTITY views; native stores are empty.
Synthetic evaluation is explicit and never eligible for real production use.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from functools import lru_cache
from dataclasses import dataclass
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
import relationship_intervention_v1 as ri

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas/actions-events/v1"
DATA = ROOT / "data/actions-events-v1/catalog.json"
WORKSPACE = ROOT / "data/candidates/actions-events-v1/workspace.json"
BASELINE = "2636dd9a8b7bad1da3d7dfa21db5fe877f4de4e1"
SYNTHETIC = "SYNTHETIC / NON_PRODUCTION"
COLLECTIONS = {"happeningTypes": "happening-type", "occurrences": "occurrence",
               "effectAssertions": "effect-assertion", "evidenceAssessments": "evidence-assessment"}
VOCAB = json.loads((SCHEMAS / "vocabulary.json").read_text(encoding="utf-8"))


class ValidationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ValidationError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":")).encode()).hexdigest()


class SchemaSet:
    def __init__(self):
        paths = sorted(SCHEMAS.glob("*-v1.schema.json")) + sorted(ri.SCHEMA_DIR.glob("*.schema.json"))
        schemas = [read(p) for p in paths]
        registry = Registry().with_resources((s["$id"], Resource.from_contents(s)) for s in schemas)
        self.validators = {}
        for path, schema in zip(paths, schemas):
            Draft202012Validator.check_schema(schema)
            if path.parent == SCHEMAS:
                self.validators[path.name.removesuffix("-v1.schema.json")] = Draft202012Validator(
                    schema, registry=registry, format_checker=FormatChecker())

    def validate(self, name, value):
        errors = sorted(self.validators[name].iter_errors(value), key=lambda e: str(list(e.path)))
        if errors:
            raise ValidationError(f"{name} {list(errors[0].path)}: {errors[0].message}")


@lru_cache(maxsize=1)
def schema_set():
    return SchemaSet()


@dataclass
class Context:
    entities: dict
    relationships: dict
    source_ids: set
    synthetic: bool = False

    @classmethod
    def repository(cls):
        catalog = ri.Catalog.from_repository()
        relationships = dict(catalog.legacy_relationships)
        for record in read(ROOT / "data/relationship-intervention-v1/relationships.json")["relationships"]:
            require(record["id"] not in relationships, "Legacy/native relationship identity collision")
            relationships[record["id"]] = record
        return cls(dict(catalog.entities), relationships, set(catalog.source_ids))

    def driver(self, identifier):
        return self.entities.get(identifier, {}).get("entityType") == "DRIVER"

    def layer(self, identifier):
        entity = self.entities[identifier]
        return entity["primaryFamilyId"].split("-")[0] if entity.get("primaryFamilyId") else entity.get("layerId", entity.get("layer"))

    def governed_causal(self, identifier, active=False):
        row = self.relationships.get(identifier, {})
        if row.get("schemaVersion") == "3.0" or "subjectEntityId" in row:
            return row.get("relationFamily") == "CAUSAL" and row.get("governanceStatus") == "ACTIVE"
        g = row.get("governance", {})
        return row.get("relationFamily") == "CAUSAL" and g.get("lifecycleStatus") == "GOVERNED" and (
            not active or g.get("activationStatus") == "ACTIVE")

    def endpoints(self, identifier):
        row = self.relationships[identifier]
        return (row.get("sourceEntityId", row.get("subjectEntityId")),
                row.get("targetEntityId", row.get("objectEntityId")))


def state_active(record):
    return ri.governed_active(record) and record["governance"]["blockStatus"] == "NONE"


def all_records(catalog):
    return [r for key in COLLECTIONS for r in catalog[key]]


def empty_catalog():
    return {"schemaVersion": "1.0.0", **{key: [] for key in COLLECTIONS}, "authorizations": []}


def empty_workspace(family_id=None, baseline_commit=None):
    return {"schemaVersion": "1.0.0", "workspaceClass": "NON_GOVERNED_RESEARCH",
            "activationStatus": "NOT_ELIGIBLE", "productionEligible": False,
            "familyId": family_id, "baselineCommit": baseline_commit,
            "passA": {k: [] for k in ("existingDispositions", "gapQuestions", "sourceQueue",
                                     "relationshipCandidates", "evidence", "ownership", "unresolved")},
            "passB": empty_catalog(), "readiness": {k: False for k in (
                "membershipDefinitions", "incidentDispositions", "rdsDerivations",
                "relationshipScope", "gapsAndDeferrals")}, "noFindings": [], "handoffs": []}


def validate_lifecycle(record, authorizations, context):
    """D12 remains authoritative; a scientific approval needs exact independent scope."""
    g = record["governance"]
    require(g["authorityBasis"] == "V1_NATIVE", "Native AE object cannot claim preserved V3 authority")
    ri.validate_governance_record(record)
    previous = {"lifecycleStatus": None, "activationStatus": "NOT_ELIGIBLE"}
    for transition in g["transitionProvenance"]:
        require(transition["fromState"] == previous, "Transition chain is not contiguous")
        previous = transition["toState"]
    if g["lifecycleStatus"] in {"GOVERNED", "DEPRECATED", "REJECTED"}:
        authorized = False
        for decision in authorizations:
            if decision["decisionRecord"] != g["decisionRecord"]:
                continue
            require("ACTIONS_EVENTS_V1_GOVERNANCE_DECISION" not in decision["decisionRecord"],
                    "Architecture authorization cannot govern scientific records")
            if not context.synthetic:
                path = (ROOT / decision["decisionRecord"]).resolve()
                require(path.is_relative_to((ROOT / "docs/governance").resolve()) and path.is_file(),
                        "Scientific decision record must resolve in governance hierarchy")
            authorized |= any(a["id"] == record["id"] and a["revision"] == record["revision"]
                              and a["recordHash"] == digest(record) for a in decision["authorizedObjects"])
        require(authorized, "Exact human scientific authorization missing for record/revision/hash")


def validate_catalog(catalog, context=None, candidate=False):
    context = context or Context.repository()
    schemas = schema_set()
    schemas.validate("catalog", catalog)
    records = all_records(catalog)
    require(len({r["id"] for r in records}) == len(records), "Duplicate scientific identity")
    reference_ids = set(context.entities) | set(context.relationships) | context.source_ids
    if not context.synthetic:
        reference_ids.update(r["id"] for rows in source_catalog().values() for r in rows)
    require(not reference_ids.intersection(r["id"] for r in records), "Happening/Driver/reference identity collision")
    for row in records:
        if context.synthetic:
            require(row["recordClass"] == SYNTHETIC and row["id"].startswith("SYN-"), "Synthetic labels/IDs required")
        else:
            require(row["recordClass"] == "SCIENTIFIC_RECORD" and not row["id"].startswith("SYN-"),
                    "Synthetic content cannot enter production/canonical workspace")
        if candidate:
            require(row["governance"]["lifecycleStatus"] in ri.NON_GOVERNED_LIFECYCLES
                    and row["governance"]["activationStatus"] == "NOT_ELIGIBLE", "Candidate workspace cannot govern or activate")
        validate_lifecycle(row, catalog["authorizations"], context)
    if candidate:
        require(not catalog["authorizations"], "Research workspace cannot supply scientific authority")
    for decision in catalog["authorizations"]:
        require((decision["recordClass"] == SYNTHETIC) == context.synthetic, "Authorization environment mismatch")
    types = {r["id"]: r for r in catalog["happeningTypes"]}
    occurrences = {r["id"]: r for r in catalog["occurrences"]}
    effects = {r["id"]: r for r in catalog["effectAssertions"]}
    assessments = {r["id"]: r for r in catalog["evidenceAssessments"]}
    identities = [r["identityKey"] for r in types.values()]
    episodes = [r["episodeKey"] for r in occurrences.values()]
    require(len(identities) == len(set(identities)), "Duplicate reusable identity")
    require(len(episodes) == len(set(episodes)), "Duplicate occurrence episode")
    def visit(identifier, trail):
        require(identifier not in trail, "Package composition cycle")
        require(identifier in types, "Package component does not resolve")
        for component in types[identifier]["components"]:
            visit(component, trail | {identifier})
    for row in types.values():
        visit(row["id"], set())
        require(set(row["identitySourceIds"]) <= context.source_ids, "Identity source unresolved")
        if row["interventionSubset"]:
            require(row["intentionality"] == "DELIBERATE", "Intervention subset must describe deliberate action")
    findings_seen = set()
    for row in assessments.values():
        assertion_id = row["assertion"]["objectId"]
        lookup = {"HAPPENING_TYPE": types, "OCCURRENCE": occurrences, "EFFECT_ASSERTION": effects}
        require(assertion_id in lookup[row["assertion"]["objectType"]], "Evidence target does not resolve")
        finding_ids = [f["id"] for f in row["sourceFindings"]]
        require(len(set(finding_ids)) == len(finding_ids) and not findings_seen.intersection(finding_ids), "Finding identity is duplicated")
        findings_seen.update(finding_ids)
        require(not reference_ids.intersection(finding_ids) and not {r["id"] for r in records}.intersection(finding_ids), "Finding identity collides with scientific/reference identity")
        synthesis = row["synthesis"]
        require(set(finding_ids) == set(synthesis["sourceFindingIds"]), "Synthesis must preserve every source finding")
        contrary = {f["id"] for f in row["sourceFindings"] if f["disposition"] in {"NULL_FINDING", "MIXED", "CONTRADICTED"}}
        require({c["findingId"] for c in synthesis["conflicts"]} == contrary, "Null/mixed/contrary findings require explicit synthesis disposition")
        if contrary and synthesis["disposition"] == "SUPPORTS":
            require(all(c["dispositionRationale"] for c in synthesis["conflicts"]), "Contrary evidence cannot be erased")
        for finding in row["sourceFindings"]:
            require(finding["sourceId"] in context.source_ids, "Finding source unresolved")
            require((finding["accessDepth"] == "SYNTHETIC") == context.synthetic, "Source access cannot imply synthetic is empirical")
        dataset_ids = [d for f in row["sourceFindings"] for d in f["datasetIds"]]
        if len(dataset_ids) != len(set(dataset_ids)):
            require(synthesis["datasetOverlap"], "Shared datasets require an overlap synthesis note")
        if state_active(row):
            require(bool(row["sourceFindings"]) and synthesis["rationale"] and synthesis["confidenceRationale"], "Active evidence needs findings and rationale")
            require(synthesis["evidenceStrength"] != "NOT_ASSESSED" and synthesis["confidence"] != "NOT_ASSESSED"
                    and synthesis["disposition"] != "NOT_ASSESSED", "Active evidence needs assessed synthesis")
    def evidence_for(row, key, expected):
        result = []
        for identifier in row[key]:
            require(identifier in assessments, "EvidenceAssessment unresolved")
            evidence = assessments[identifier]
            require(evidence["assertion"] == {"objectType": expected, "objectId": row["id"]},
                    "Occurrence/package/other assertion evidence cannot transfer to an effect")
            if state_active(row):
                require(state_active(evidence), "Active assertion needs active supporting EvidenceAssessment")
            result.append(evidence)
        return result
    for row in occurrences.values():
        require(row["typeId"] in types, "Occurrence type unresolved")
        ev = evidence_for(row, "evidenceAssessmentIds", "OCCURRENCE")
        if row["epistemicStatus"] == "OBSERVED":
            require(any("OCCURRENCE" in f["supportedSemantics"] and f["disposition"] in {"SUPPORTS", "MIXED"}
                        for e in ev for f in e["sourceFindings"]), "Observed occurrence requires occurrence-specific evidence")
            require(row["timeWindow"] and row["placeOrSystem"] and row["populationOrSystem"],
                    "Observed occurrence needs time, place/system and affected population/system")
    signatures, groups = set(), {}
    for row in effects.values():
        require(row["typeId"] in types, "Effect type unresolved")
        if row["occurrenceId"]:
            require(row["occurrenceId"] in occurrences and occurrences[row["occurrenceId"]]["typeId"] == row["typeId"], "Occurrence/type mismatch")
        signature = digest({k: row[k] for k in ("typeId", "occurrenceId", "targetKind", "targetId", "property", "change", "scope", "claimSemantics")})
        require(signature not in signatures, "Duplicate contextual proposition")
        signatures.add(signature)
        target = row["targetId"]
        if row["targetKind"] == "DRIVER":
            require(context.driver(target), "No direct RDS target; exact canonical Driver required")
            require(row["targetLayers"] == [context.layer(target)], "Target Layer must resolve independently of origin")
        else:
            require(context.governed_causal(target), "Exact governed causal relationship target required")
            require(set(row["targetLayers"]) == {context.layer(e) for e in context.endpoints(target)}, "Edge target Layer mismatch")
            if state_active(row):
                require(bool(row["mechanisticDriverIds"]), "Active relationship target needs mechanistic Driver linkage")
                require(context.governed_causal(target, active=True), "Active effect cannot modify inactive edge")
        for identifier in row["mechanisticDriverIds"]:
            require(context.driver(identifier), "Mechanistic linkage must be a Driver")
        if row["property"].startswith("RELATIONSHIP_"):
            require(row["targetKind"] == "RELATIONSHIP", "Relationship property needs exact edge target")
        if row["change"] in {"CYCLIC", "U_SHAPED", "INVERTED_U", "NON_MONOTONIC", "STATE_DEPENDENT"}:
            require(row["observedChange"] not in {"INCREASE", "DECREASE"}, "Cyclic/nonmonotonic claim cannot carry universal observed sign")
        unknown = row["knowledgeStatus"] in {"NOT_INVESTIGATED", "NOT_APPLICABLE", "INSUFFICIENT_EVIDENCE"}
        require(not unknown or row["change"] == "UNKNOWN", "Unknown effect is not zero or established direction")
        require(row["change"] != "NO_DETECTED_CHANGE" or row["knowledgeStatus"] == "SUPPORTED_NULL", "Null requires explicit bounded support")
        require(row["claimSemantics"] != "PATHWAY", "Pathways require separate governed CausalPathway; no reachability inference")
        ev = evidence_for(row, "evidenceAssessmentIds", "EFFECT_ASSERTION")
        findings = [f for a in ev for f in a["sourceFindings"]]
        if row["knowledgeStatus"] == "SUPPORTED_EFFECT":
            require(row["change"] not in {"UNKNOWN", "NO_DETECTED_CHANGE"}, "Supported effect must specify change")
            require(any(row["claimSemantics"] in f["supportedSemantics"] and f["disposition"] in {"SUPPORTS", "MIXED"}
                        for f in findings), "Association/occurrence/null evidence cannot establish a causal effect")
        if row["knowledgeStatus"] == "SUPPORTED_NULL":
            require(any(f["nullInterpretation"] and f["nullInterpretation"]["interpretation"] == "BOUNDED_NULL_SUPPORTED"
                        and f["disposition"] == "NULL_FINDING" for f in findings), "Nonsignificance alone is not supported null")
        if row["productionMethod"] == "MODEL_INFERENCE":
            require(row["inferenceProvenance"] and set(row["inferenceProvenance"]["inputEvidenceIds"]) == set(row["evidenceAssessmentIds"]), "Model inference requires explicit inputs/assumptions")
            require(all(f["inputRole"] == "MODEL_INPUT" for f in findings), "Model inputs must not masquerade as direct empirical findings")
        else:
            require(row["inferenceProvenance"] is None, "Inference provenance conflicts with production method")
        if row["productionMethod"] == "HYPOTHESIS":
            require(row["knowledgeStatus"] == "INSUFFICIENT_EVIDENCE", "Untested hypothesis is not supported empirical knowledge")
        if row["claimSemantics"] == "CAUSAL":
            require(row["grounding"]["derivationEntailed"] != "YES", "Formula-derived causal claim prohibited")
            if state_active(row):
                require(row["grounding"]["derivationEntailed"] == "NO" and row["grounding"]["causalIdentificationRationale"], "Active causal grounding incomplete")
        if row["grounding"]["representedDriverId"]:
            require(context.driver(row["grounding"]["representedDriverId"]) and row["grounding"]["duplicatePropagationControl"], "Event/Driver representation requires single-contribution control")
        for outcome in row["outcomes"]:
            require(outcome["entityId"] in context.entities, "Outcome entity unresolved")
        for subgroup in row["qualifiers"]["subgroups"]:
            require(set(subgroup["evidenceAssessmentIds"]) <= set(row["evidenceAssessmentIds"]),
                    "Subgroup difference requires this assertion's evidence")
        if row["qualifiers"]["evaluation"]["valence"] != "NOT_EVALUATED":
            evaluation = row["qualifiers"]["evaluation"]
            require(evaluation["stakeholder"] and evaluation["criterion"], "Valence needs stakeholder and criterion")
        for link in row["moderatorLinks"]:
            require(context.driver(link["driverId"]), "Moderator route requires Driver")
            if link["driverEffectId"]:
                other = effects.get(link["driverEffectId"], {})
                require(other.get("targetKind") == "DRIVER" and other.get("targetId") == link["driverId"], "Moderator direct effect mismatch")
                require(other["contribution"]["groupId"] == row["contribution"]["groupId"], "Moderator/direct routes must share contribution identity")
                require(set(other["evidenceAssessmentIds"]).isdisjoint(row["evidenceAssessmentIds"]), "Moderator segments need independent assertion evidence")
            if link["moderationRelationshipId"]:
                moderation = context.relationships.get(link["moderationRelationshipId"], {})
                require(moderation.get("relationFamily") == "MODERATION" and moderation.get("moderatedRelationshipId") == target, "Moderation must identify the exact modified edge")
        if row["interaction"]["mode"] != "NONE":
            require(row["interaction"]["otherEffectIds"] and row["interaction"]["evidenceAssessmentIds"], "Joint interaction cannot be inferred from separate effects")
        require(set(row["interaction"]["otherEffectIds"]) <= effects.keys(), "Interaction effect unresolved")
        require(set(row["interaction"]["evidenceAssessmentIds"]) <= set(row["evidenceAssessmentIds"]), "Interaction needs assertion-specific evidence")
        groups.setdefault(row["contribution"]["groupId"], []).append(row)
        if state_active(row):
            require(state_active(types[row["typeId"]]), "Active effect requires active type identity")
            require(ev and all(row["scope"].values()) and row["mechanism"] and row["mechanismStatus"] != "UNKNOWN", "Active effect scope/mechanism/evidence incomplete")
            require(row["knowledgeStatus"] in {"SUPPORTED_EFFECT", "SUPPORTED_NULL"}, "Uninvestigated effect cannot activate")
    for group in groups.values():
        if len(group) > 1:
            require(sum(r["contribution"]["role"] == "PRIMARY" for r in group) == 1
                    and all(r["contribution"]["reconciliation"] for r in group), "Duplicate contribution: select one primary, never sum routes")
        for row in group:
            require(set(row["contribution"]["relatedAssertionIds"]) <= effects.keys(), "Contribution linkage unresolved")
    for row in types.values():
        if state_active(row) and row["interventionSubset"]:
            require(any(e["typeId"] == row["id"] and state_active(e) for e in effects.values()), "Active Intervention identity requires own active effect, not component inference")
    return {"records": len(records), "synthetic": context.synthetic,
            "active": sum(state_active(r) for r in records), "statusChanges": 0}


def validate_workspace(workspace, context=None):
    schema_set().validate("candidate-workspace", workspace)
    context = context or Context.repository()
    validate_catalog(workspace["passB"], context, candidate=True)
    for row in workspace["passA"]["relationshipCandidates"] + workspace["passA"]["evidence"]:
        require(row["governance"]["lifecycleStatus"] in ri.NON_GOVERNED_LIFECYCLES
                and row["governance"]["activationStatus"] == "NOT_ELIGIBLE", "Pass A candidates cannot govern")
        ri.validate_governance_record(row)
    catalog = ri.Catalog(context.entities, context.relationships, frozenset(context.source_ids))
    schemas = ri.SchemaSet()
    relationships = {**context.relationships, **{r["id"]: r for r in workspace["passA"]["relationshipCandidates"]}}
    evidence = {r["id"]: r for r in workspace["passA"]["evidence"]}
    require(len(evidence) == len(workspace["passA"]["evidence"]), "Duplicate Pass A evidence")
    candidate_ids = [r["id"] for r in workspace["passA"]["relationshipCandidates"]]
    require(len(candidate_ids) == len(set(candidate_ids)) and not set(candidate_ids) & context.relationships.keys(),
            "Pass A revisions must not overwrite existing relationship IDs")
    for row in workspace["passA"]["relationshipCandidates"]:
        ri.validate_relationship(row, catalog, schemas, relationships)
        require(set(row["evidenceAssessmentIds"]) <= evidence.keys(), "Pass A evidence does not resolve")
    for row in evidence.values():
        ri.validate_evidence_assessment(row, catalog, schemas)
        require(row["assertion"]["objectId"] in relationships, "Pass A evidence assertion does not resolve")
    return {"passBReady": all(workspace["readiness"].values()), "productionEligible": False}


def validate_repository():
    legacy = ri.validate_repository()
    native = validate_catalog(read(DATA))
    candidates = validate_workspace(read(WORKSPACE))
    views = compatibility_catalog()
    for view in views:
        validate_compatibility(view)
    return {"existingV1": legacy, "nativeActionsEvents": native,
            "candidateWorkspace": candidates, "sameIdentityViews": len(views),
            "additionalScientificPropositions": 0}


# Compatibility and calculated-use functions follow; no production importer exists.

def source_catalog():
    base = ROOT / "data/relationship-intervention-v1"
    return {"INTERVENTION": read(base / "interventions.json")["interventions"],
            "INTERVENTION_EFFECT": read(base / "intervention-effects.json")["interventionEffects"],
            "EVIDENCE_ASSESSMENT": read(base / "evidence-assessments.json")["evidenceAssessments"]}


def compatibility_view(record, object_type, context=None):
    """Same proposition, same revision. Unsupported fields stay unassessed.

No source-specific finding, origin Layer, actor control, observed result or
new estimand is inferred from a legacy synthesis or target Layer.
"""
    context = context or Context.repository()
    original = copy.deepcopy(record)
    if object_type == "INTERVENTION":
        view_type = "HAPPENING_TYPE"
        normalized = {"name": original["canonicalName"], "kindTags": ["ACTION"],
                      "interventionSubset": True, "originLayers": [],
                      "intentionality": "DELIBERATE", "controlProfiles": [],
                      "packageKind": original["interventionKind"],
                      "components": copy.deepcopy(original["componentInterventionIds"]),
                      "packageSpecification": copy.deepcopy(original.get("packageSpecification")),
                      "description": original["description"],
                      "componentEnumeration": "SOURCE_SPECIFICATION_CONTROLS"}
        incomplete = ["originLayers", "controlProfiles", "domainTags"]
    elif object_type == "INTERVENTION_EFFECT":
        view_type = "EFFECT_ASSERTION"
        target = original["targetDriverId"] or original["targetRelationshipId"]
        # Only the unambiguous CHANGE_LEVEL mapping is normalized. Other old
        # modes are retained verbatim, never guessed into an eleven-property slot.
        mode = original["effectMode"]
        change = {"CONTEXT_DEPENDENT": "STATE_DEPENDENT"}.get(original["intendedDirection"], original["intendedDirection"])
        normalized = {"typeId": original["interventionId"], "occurrenceId": None,
                      "targetKind": original["targetKind"], "targetId": target,
                      "targetLayers": [context.layer(target)] if original["targetKind"] == "DRIVER" else sorted({context.layer(e) for e in context.endpoints(target)}),
                      "property": "LEVEL" if mode == "CHANGE_LEVEL" else None,
                      "change": change if mode == "CHANGE_LEVEL" else None,
                      "intendedChange": original["intendedDirection"], "observedChange": None,
                      "legacyEffectMode": mode, "mechanism": original["mechanismOfAction"],
                      "mechanisticDriverIds": copy.deepcopy(original["mechanisticDriverIds"]),
                      "scope": {"population": original["targetPopulationOrAudience"], "context": original["context"],
                                "boundaryConditions": original["boundaryConditions"], "timing": None, "measurement": None},
                      "evidenceAssessmentIds": copy.deepcopy(original["evidenceAssessmentIds"]),
                      "outcomeEntityIds": copy.deepcopy(original["outcomeEntityIds"]),
                      "risks": copy.deepcopy(original["risks"]),
                      "ethicalLegalConstraints": copy.deepcopy(original["ethicalLegalConstraints"])}
        incomplete = ["sourceFindingNormalization", "observedChange", "scope.timing", "scope.measurement", "controlProfiles"]
        if mode != "CHANGE_LEVEL":
            incomplete += ["property", "change"]
    elif object_type == "EVIDENCE_ASSESSMENT":
        view_type = object_type
        normalized = {"assertion": copy.deepcopy(original["assertion"]), "sourceFindings": [],
                      "synthesis": {"disposition": original["evidenceDisposition"],
                                    "evidenceStrength": original["evidenceStrength"],
                                    "confidence": original["confidence"],
                                    "rationale": original["evidenceRationale"],
                                    "conflicts": copy.deepcopy(original["conflictingEvidence"]),
                                    "generalizationLimits": copy.deepcopy(original["limitations"])},
                      "sourceIds": copy.deepcopy(original["sourceIds"]),
                      "normalizationStatus": "LEGACY_SYNTHESIS_PRESERVED_FINDINGS_NOT_INFERRED"}
        incomplete = ["sourceFindings"]
    else:
        raise ValidationError("Unsupported compatibility source type")
    return {"schemaVersion": "1.0.0", "id": original["id"], "revision": original["revision"],
            "viewType": view_type, "sourceObjectType": object_type,
            "identitySemantics": "SAME_IDENTITY", "additionalScientificPropositions": 0,
            "sourceRecordHash": digest(original), "sourceRecord": original,
            "normalized": normalized, "incompleteFields": incomplete,
            "governance": copy.deepcopy(original["governance"])}


def compatibility_catalog():
    context = Context.repository()
    return [compatibility_view(r, kind, context) for kind, records in source_catalog().items() for r in records]


def validate_compatibility(view):
    schema_set().validate("compatibility", view)
    sources = source_catalog()[view["sourceObjectType"]]
    current = next((r for r in sources if r["id"] == view["id"]), None)
    require(current is not None, "Compatibility source ID does not resolve")
    require(view == compatibility_view(current, view["sourceObjectType"]), "Compatibility view changed authority/content or is stale")
    return True


def restore_compatibility(view):
    validate_compatibility(view)
    return copy.deepcopy(view["sourceRecord"])


def deduplicate_scientific_views(records):
    result = {}
    for record in records:
        if record.get("identitySemantics") == "SAME_IDENTITY":
            original = restore_compatibility(record)
        else:
            original = record
        identifier = original["id"]
        require(identifier not in result or result[identifier] == original, "Same ID has conflicting scientific representations")
        result[identifier] = copy.deepcopy(original)
    return list(result.values())


def use_eligibility(effect_id, catalog=None, context=None, use_context=None):
    """Derived readiness, not recommendations/ranking, activation or a model.

The caller supplies an explicit actor-use assessment scoped to this effect's
revision. Unknown/missing constraints fail closed. Synthetic would-qualify flags
never confer production eligibility. Existing status is preserved in bridge views.
"""
    context = context or Context.repository()
    legacy = catalog is None
    if legacy:
        ri.validate_repository()
        source = source_catalog()
        effect = next((r for r in source["INTERVENTION_EFFECT"] if r["id"] == effect_id), None)
        require(effect, "Unknown existing effect")
        identity = next(r for r in source["INTERVENTION"] if r["id"] == effect["interventionId"])
        evidence = {r["id"]: r for r in source["EVIDENCE_ASSESSMENT"]}
        scope = {"population": effect["targetPopulationOrAudience"], "context": effect["context"]}
        active_evidence = all(state_active(evidence[e]) for e in effect["evidenceAssessmentIds"])
        scientifically_ready = state_active(effect) and state_active(identity) and active_evidence
        actionable_claim = scientifically_ready and all(
            evidence[e]["evidenceDisposition"] in {"SUPPORTS", "MIXED"}
            for e in effect["evidenceAssessmentIds"])
        deliberate = True
    else:
        validate_catalog(catalog, context)
        effect = next((r for r in catalog["effectAssertions"] if r["id"] == effect_id), None)
        require(effect, "Unknown native effect")
        identity = next(r for r in catalog["happeningTypes"] if r["id"] == effect["typeId"])
        scientifically_ready = state_active(effect) and state_active(identity)
        scope = effect["scope"]
        deliberate = identity["interventionSubset"] and identity["intentionality"] == "DELIBERATE"
        actionable_claim = (scientifically_ready and effect["claimSemantics"] == "CAUSAL"
                            and effect["knowledgeStatus"] == "SUPPORTED_EFFECT"
                            and effect["productionMethod"] in {"SOURCE_EXTRACTION", "SYNTHESIS"}
                            and effect["contribution"]["role"] == "PRIMARY")
        # Documented edge modulation can inform action, never an ordinary edge.
        if effect["claimSemantics"] == "MODERATION":
            actionable_claim = scientifically_ready and effect["knowledgeStatus"] == "SUPPORTED_EFFECT" and effect["productionMethod"] in {"SOURCE_EXTRACTION", "SYNTHESIS"} and effect["contribution"]["role"] == "PRIMARY"
        evidence = {r["id"]: r for r in catalog["evidenceAssessments"]}
        actionable_claim = actionable_claim and all(
            evidence[e]["synthesis"]["disposition"] in {"SUPPORTS", "MIXED"}
            for e in effect["evidenceAssessmentIds"])
    request = use_context or {}
    reasons = []
    if not deliberate:
        reasons.append("Not a deliberate Intervention/action subset")
    if not actionable_claim:
        reasons.append("No independently eligible governed-active effect")
    if request.get("effectId") != effect_id or request.get("revision") != effect["revision"]:
        reasons.append("Use assessment does not identify exact effect/revision")
    if request.get("population") != scope["population"] or request.get("context") != scope["context"]:
        reasons.append("Population/context applicability not established for exact scope")
    control = request.get("control", {})
    if (not request.get("actorId") or control.get("actorId") != request.get("actorId")
            or control.get("extent") not in {"FULL", "PARTIAL"}
            or not control.get("capabilities") or not control.get("provenance")):
        reasons.append("Actor-specific controllability not established")
    if not legacy:
        profiles = list(identity["controlProfiles"])
        if effect["occurrenceId"]:
            occurrence = next(r for r in catalog["occurrences"] if r["id"] == effect["occurrenceId"])
            profiles += occurrence["controlProfiles"]
        for profile in profiles:
            if (profile["actorId"] == request.get("actorId") and profile["population"] == scope["population"]
                    and profile["context"] == scope["context"] and profile["extent"] in {"NONE", "UNKNOWN", "INFLUENCE_ONLY"}):
                reasons.append("Recorded actor control profile does not permit this action")
    for check in ("prerequisites", "feasibility", "legalConstraints", "ethicalRiskConstraints", "applicability"):
        assessment = request.get("checks", {}).get(check, {})
        if assessment.get("status") != "ASSESSED_PASS" or not assessment.get("rationale") or not assessment.get("provenance"):
            reasons.append(check + " not explicitly assessed")
    action_ready = not reasons
    synthetic = context.synthetic
    result = {"schemaVersion": "1.0.0", "objectId": effect_id, "revision": effect["revision"],
              "scientificUseEligibility": {"eligible": bool(scientifically_ready and not synthetic),
                  "reasons": ["Synthetic only"] if synthetic else ([] if scientifically_ready else ["Not governed-active with required dependencies"])},
              "modelEligibility": {"eligible": False, "reasons": ["No quantitative execution/model contract authorized; no weights inferred"]},
              "practitionerActionEligibility": {"eligible": bool(action_ready and not synthetic), "reasons": reasons + (["Synthetic only"] if synthetic else [])},
              "syntheticSimulation": {"scientificWouldQualify": bool(scientifically_ready), "actionWouldQualify": bool(action_ready)} if synthetic else None,
              "statusChanges": 0}
    schema_set().validate("use-eligibility", result)
    return result


def source_identity_keys(source):
    """Identifiers deduplicate; title/year is a human-review flag, never a merge."""
    keys = set()
    for field in ("doi", "DOI"):
        value = source.get(field)
        if value:
            keys.add("doi:" + re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", str(value).strip(), flags=re.I).lower().rstrip("."))
    for field in ("pmid", "PMID"):
        if source.get(field):
            keys.add("pmid:" + str(source[field]).strip())
    return keys


def source_registration_triage(proposed, registered):
    keys = source_identity_keys(proposed)
    exact = sorted(r["id"] for r in registered if keys & source_identity_keys(r))
    if exact:
        return {"status": "EXACT_IDENTIFIER_MATCH", "sourceIds": exact, "registrationPerformed": False}
    title = lambda r: re.sub(r"\W+", " ", str(r.get("title", "")).casefold()).strip()
    possible = sorted(r["id"] for r in registered if title(proposed) and title(proposed) == title(r) and proposed.get("year") == r.get("year"))
    return {"status": "TITLE_YEAR_REVIEW" if possible else "NEW_UNVERIFIED", "sourceIds": possible, "registrationPerformed": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-repository", action="store_true")
    parser.add_argument("--compatibility-summary", action="store_true")
    args = parser.parse_args()
    if args.compatibility_summary:
        views = compatibility_catalog()
        result = {"views": len(views), "additionalScientificPropositions": 0,
                  "incomplete": {r["id"]: r["incompleteFields"] for r in views}}
    else:
        result = validate_repository()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
