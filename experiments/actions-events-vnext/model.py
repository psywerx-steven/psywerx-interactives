"""PENDING synthetic semantic experiment. No production importer or status writer."""
from __future__ import annotations
import copy
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

HERE = Path(__file__).resolve().parent
LAYERS = ("BIO", "PSY", "SOC", "CUL", "ENV", "INS", "INF", "TEC")
PROPERTIES = ("LEVEL", "VARIABILITY", "RATE", "THRESHOLD", "TIMING", "PERSISTENCE",
              "RELATIONSHIP_STRENGTH", "RELATIONSHIP_DIRECTION", "ENABLEMENT",
              "FUNCTIONAL_SHAPE", "STRUCTURE")
SCHEMAS = {"types": "happening-type", "occurrences": "occurrence",
           "effects": "effect-assertion", "evidence": "evidence-assessment"}
CHANGE_COMPATIBILITY = {
    "LEVEL": {"INCREASE", "DECREASE", "CONTEXT_DEPENDENT", "MAINTAIN"},
    "VARIABILITY": {"INCREASE", "DECREASE", "MAINTAIN", "CONTEXT_DEPENDENT"},
    "RATE": {"INCREASE", "DECREASE", "CONTEXT_DEPENDENT"},
    "THRESHOLD": {"INCREASE", "DECREASE", "CONTEXT_DEPENDENT"},
    "TIMING": {"ADVANCE", "DELAY", "CONTEXT_DEPENDENT"},
    "PERSISTENCE": {"INCREASE", "DECREASE", "CONTEXT_DEPENDENT"},
    "RELATIONSHIP_STRENGTH": {"INCREASE", "DECREASE", "DISABLE", "CONTEXT_DEPENDENT"},
    "RELATIONSHIP_DIRECTION": {"REVERSE", "CONTEXT_DEPENDENT"},
    "ENABLEMENT": {"ENABLE", "DISABLE", "CONTEXT_DEPENDENT"},
    "FUNCTIONAL_SHAPE": {"RECONFIGURE", "CONTEXT_DEPENDENT"},
    "STRUCTURE": {"RECONFIGURE", "INCREASE", "DECREASE", "CONTEXT_DEPENDENT"},
}


def schema_validators():
    schemas = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((HERE / "schemas").glob("*.json"))]
    registry = Registry().with_resources((s["$id"], Resource.from_contents(s)) for s in schemas)
    for schema in schemas:
        Draft202012Validator.check_schema(schema)
    return {key: Draft202012Validator(next(s for s in schemas if s["$id"].endswith(name + ".schema.json")),
                                      registry=registry, format_checker=FormatChecker())
            for key, name in SCHEMAS.items()}


def validate_bundle(bundle):
    """Return deterministic schema/reference/semantic errors for SYN-only input."""
    errors = []
    if not isinstance(bundle, dict) or any(not isinstance(bundle.get(key), list)
            for key in (*SCHEMAS, "entities", "relationships", "sources")):
        return ["bundle requires type/occurrence/effect/evidence/reference arrays"]
    if bundle.get("label") != "SYNTHETIC / NON_PRODUCTION":
        errors.append("bundle must be SYNTHETIC / NON_PRODUCTION")
    if any(not isinstance(r, dict) for key in (*SCHEMAS, "entities", "relationships", "sources") for r in bundle[key]):
        return ["every record/reference must be an object"]
    if any(not isinstance(r.get("id"), str) for key in (*SCHEMAS, "entities", "relationships", "sources") for r in bundle[key]):
        return ["every record/reference requires a string identity"]
    validators = schema_validators()
    records = [r for key in SCHEMAS for r in bundle.get(key, [])]
    ids = [r.get("id") for r in records]
    if len(ids) != len(set(ids)):
        errors.append("duplicate record ID/type/occurrence representation")
    for key, validator in validators.items():
        for record in bundle.get(key, []):
            for error in validator.iter_errors(record):
                errors.append(f"{record.get('id')}: {list(error.path)} {error.message}")
    for key in ("entities", "relationships", "sources"):
        reference_ids = [item.get("id") for item in bundle[key]]
        if len(reference_ids) != len(set(reference_ids)):
            errors.append(key + ": duplicate reference identity")
        for item in bundle.get(key, []):
            if not isinstance(item.get("id"), str) or not item["id"].startswith("SYN-") or item.get("label") != "SYNTHETIC / NON_PRODUCTION":
                errors.append(f"{key} contains non-synthetic reference")
    entity_references = {r.get("id"): r for r in bundle["entities"]}
    for item in bundle["entities"]:
        if item.get("entityType") not in ("DRIVER", "RDS") or item.get("layer") not in LAYERS:
            errors.append("entity reference requires valid type and Layer")
    for item in bundle["relationships"]:
        if any(not isinstance(item.get(k), str) or item[k] not in entity_references for k in ("sourceId", "targetId")):
            errors.append("relationship reference has dangling entity endpoint")
        if not isinstance(item.get("governed"), bool) or not isinstance(item.get("family"), str):
            errors.append("relationship reference requires family and fictional governed flag")
    if errors:
        return sorted(errors)
    entities = {r["id"]: r for r in bundle["entities"]}
    relationships = {r["id"]: r for r in bundle["relationships"]}
    types = {r["id"]: r for r in bundle["types"]}
    occurrences = {r["id"]: r for r in bundle["occurrences"]}
    effects = {r["id"]: r for r in bundle["effects"]}
    evidence = {r["id"]: r for r in bundle["evidence"]}
    sources = {r["id"] for r in bundle["sources"]}
    if set(ids) & (set(entities) | set(relationships) | sources):
        errors.append("type/occurrence/effect must not reuse Driver or reference identity")
    for key, field in (("types", "identityKey"), ("occurrences", "episodeKey")):
        values = [r[field] for r in bundle[key]]
        if len(values) != len(set(values)):
            errors.append(f"duplicate {key} {field}")
    for item in types.values():
        if any(cid not in types for cid in item["components"]):
            errors.append(item["id"] + ": missing package component")
    def visit(node, trail):
        if node in trail:
            errors.append(node + ": package composition cycle")
            return
        for child in types.get(node, {}).get("components", []):
            visit(child, trail | {node})
    for key in types:
        visit(key, set())
    for item in occurrences.values():
        if item["typeId"] not in types:
            errors.append(item["id"] + ": missing type")
        for eid in item["occurrenceEvidenceIds"]:
            if eid not in evidence or evidence[eid]["assertionId"] != item["id"]:
                errors.append(item["id"] + ": occurrence evidence must support occurrence only")
        if item["epistemicStatus"] == "OBSERVED" and not item["occurrenceEvidenceIds"]:
            errors.append(item["id"] + ": observed occurrence needs occurrence evidence")
    contributions = {}
    proposition_keys = set()
    for effect in effects.values():
        rid = effect["id"]
        proposition_key = json.dumps([effect[k] for k in
                ("typeId", "occurrenceId", "targetKind", "targetId", "claimSemantics",
                 "property", "change", "scope")], sort_keys=True)
        if proposition_key in proposition_keys:
            errors.append(rid + ": duplicate contextual effect proposition")
        proposition_keys.add(proposition_key)
        if effect["typeId"] not in types:
            errors.append(rid + ": missing type")
        if effect["occurrenceId"] is not None:
            occurrence = occurrences.get(effect["occurrenceId"])
            if occurrence is None or occurrence["typeId"] != effect["typeId"]:
                errors.append(rid + ": occurrence/type mismatch")
        target = entities.get(effect["targetId"]) if effect["targetKind"] == "DRIVER" else relationships.get(effect["targetId"])
        if target is None:
            errors.append(rid + ": missing exact target")
        elif effect["targetKind"] == "DRIVER":
            if target["entityType"] != "DRIVER":
                errors.append(rid + ": RDS direct target forbidden for every happening kind")
            if effect["targetLayers"] != [target["layer"]]:
                errors.append(rid + ": target Layer mismatch")
        else:
            if target["family"] != "CAUSAL" or not target["governed"]:
                errors.append(rid + ": relationship target must be exact governed causal reference")
            target_layers = {entities[target[k]]["layer"] for k in ("sourceId", "targetId")}
            if set(effect["targetLayers"]) != target_layers:
                errors.append(rid + ": relationship target Layer mismatch")
        for did in effect["mechanisticDriverIds"]:
            if entities.get(did, {}).get("entityType") != "DRIVER":
                errors.append(rid + ": invalid mechanistic Driver")
        if effect["property"].startswith("RELATIONSHIP_") and effect["targetKind"] != "RELATIONSHIP":
            errors.append(rid + ": relationship property requires relationship target")
        permitted = CHANGE_COMPATIBILITY[effect["property"]] | {"UNKNOWN", "NO_DETECTED_CHANGE"}
        if effect["change"] not in permitted:
            errors.append(rid + ": incompatible property/change")
        if effect["functionalShape"] in {"CYCLIC", "U_SHAPED", "INVERTED_U", "OTHER_NON_MONOTONIC"} and effect["change"] in {"INCREASE", "DECREASE"}:
            errors.append(rid + ": non-monotonic input cannot have universal sign")
        unknown = effect["knowledgeStatus"] in {"NOT_APPLICABLE", "NOT_INVESTIGATED", "INSUFFICIENT_EVIDENCE"}
        if unknown and effect["change"] != "UNKNOWN":
            errors.append(rid + ": unknown/not-applicable is not zero or an established change")
        if effect["change"] == "NO_DETECTED_CHANGE" and effect["knowledgeStatus"] != "SUPPORTED_NULL":
            errors.append(rid + ": null claim requires supported-null qualification")
        assessments = []
        for eid in effect["evidenceIds"]:
            assessment = evidence.get(eid)
            if not assessment or assessment["assertionId"] != rid:
                errors.append(rid + ": assertion-specific evidence required; occurrence/package evidence cannot transfer")
            else:
                assessments.append(assessment)
        if effect["knowledgeStatus"] in {"SUPPORTED_EFFECT", "SUPPORTED_NULL"} and not assessments:
            errors.append(rid + ": occurrence existence does not establish effect")
        findings = [f for a in assessments for f in a["sourceFindings"]]
        if effect["knowledgeStatus"] == "SUPPORTED_EFFECT":
            if effect["change"] in {"UNKNOWN", "NO_DETECTED_CHANGE"}:
                errors.append(rid + ": supported effect requires a specified non-null change")
            if not findings or not any(f["disposition"] in {"SUPPORTS", "MIXED"} for f in findings):
                errors.append(rid + ": supported effect requires scoped supportive finding; empty/null-only evidence is insufficient")
        if effect["knowledgeStatus"] == "SUPPORTED_NULL" and not any(
                f["disposition"] == "NULL_FINDING" and f["nullInterpretation"]
                and f["nullInterpretation"]["interpretation"] == "EQUIVALENCE_WITHIN_MARGIN"
                and f["nullInterpretation"]["equivalenceMargin"]
                for a in assessments for f in a["sourceFindings"]):
            errors.append(rid + ": supported-null requires source-level null finding with contrast, precision and equivalence margin")
        bases = {basis for a in assessments for f in a["sourceFindings"] for basis in f["basis"]}
        if effect["claimSemantics"] == "CAUSAL" and effect["knowledgeStatus"] == "SUPPORTED_EFFECT" and not bases.intersection({"EXPERIMENT", "QUASI_EXPERIMENT", "MECHANISTIC_THEORY"}):
            errors.append(rid + ": association/model/occurrence alone does not establish causal support")
        if effect["productionMethod"] == "MODEL_INFERENCE":
            provenance = effect["inferenceProvenance"]
            if not provenance or set(provenance["inputEvidenceIds"]) != set(effect["evidenceIds"]):
                errors.append(rid + ": model inference requires model identity, input provenance and assumptions")
            if any(f["inputRole"] != "MODEL_INPUT" for a in assessments for f in a["sourceFindings"]):
                errors.append(rid + ": model inference source findings must be explicitly input evidence")
        elif effect["inferenceProvenance"] is not None:
            errors.append(rid + ": inference provenance only applies to model-produced assertion")
        if effect["claimSemantics"] == "PATHWAY":
            errors.append(rid + ": pathways require separate governed pathway contract; no reachability inference")
        if effect["interaction"]["mode"] != "NONE" and not effect["interaction"]["evidenceIds"]:
            errors.append(rid + ": interaction needs independent evidence")
        for eid in effect["interaction"]["evidenceIds"]:
            if eid not in evidence or evidence[eid]["assertionId"] != rid:
                errors.append(rid + ": interaction evidence must resolve to exact assertion")
        for other in effect["interaction"]["otherEffectIds"]:
            if other not in effects:
                errors.append(rid + ": missing interaction effect")
        contributions.setdefault(effect["contributionKey"], []).append(effect)
    for group in contributions.values():
        if len(group) > 1 and (sum(e["propagationRole"] == "PRIMARY" for e in group) != 1 or any(not e["reconciliation"] for e in group)):
            errors.append("duplicate event/mediator propagation: one primary and explicit reconciliation required")
    for assessment in evidence.values():
        aid = assessment["id"]
        finding_ids = [f["id"] for f in assessment["sourceFindings"]]
        if len(finding_ids) != len(set(finding_ids)) or set(finding_ids) != set(assessment["synthesis"]["sourceFindingIds"]):
            errors.append(aid + ": synthesis must cite every distinct source finding, including contrary findings")
        if assessment["assertionId"] not in effects and assessment["assertionId"] not in occurrences:
            errors.append(aid + ": dangling assertion")
        for finding in assessment["sourceFindings"]:
            if finding["sourceId"] not in sources:
                errors.append(aid + ": unresolved source")
        disposition = assessment["synthesis"]["disposition"]
        contrary = any(f["disposition"] in {"MIXED", "CONTRADICTED", "NULL_FINDING"} for f in assessment["sourceFindings"])
        if contrary and disposition == "SUPPORTS":
            errors.append(aid + ": contrary/null finding requires explicit mixed synthesis in prototype")
        if disposition in {"SUPPORTS", "MIXED"} and assessment["synthesis"]["contraryEvidenceSearch"] != "ASSESSED":
            errors.append(aid + ": contrary evidence not investigated")
    return sorted(set(errors))


def dry_run(bundle, hypothetical_decisions=(), use_context=None):
    """Pure simulation. Never mutates records, authorizes or activates."""
    errors = validate_bundle(bundle)
    approved = {d["objectId"] for d in hypothetical_decisions
                if d.get("hypothetical") is True and d.get("actorClass") == "AUTHORIZED_HUMAN_GOVERNOR"
                and d.get("outcome") == "APPROVE" and d.get("revision") == 1}
    eligible = []
    if not errors:
        for effect in bundle["effects"]:
            type_record = next((t for t in bundle["types"] if t["id"] == effect["typeId"]), None)
            if (effect["id"] in approved and effect["typeId"] in approved
                    and type_record and type_record["governance"]["lifecycleStatus"] == "REVIEW_READY"
                    and effect["claimSemantics"] in {"CAUSAL", "MODERATION"}
                    and effect["knowledgeStatus"] == "SUPPORTED_EFFECT"
                    and effect["productionMethod"] in {"SOURCE_EXTRACTION", "SYNTHESIS"}
                    and effect["propagationRole"] == "PRIMARY"
                    and effect["governance"]["lifecycleStatus"] == "REVIEW_READY"
                    and effect["evidenceIds"] and set(effect["evidenceIds"]).issubset(approved)):
                assessments = [a for a in bundle["evidence"] if a["id"] in effect["evidenceIds"]]
                if all(a["governance"]["lifecycleStatus"] == "REVIEW_READY"
                       and a["sourceFindings"] and a["synthesis"]["disposition"] in {"SUPPORTS", "MIXED"}
                       and "MISSING" not in a["completeness"].values() for a in assessments):
                    eligible.append(effect["id"])
    # Scientific readiness is distinct from an actor's ability to use an action.
    identities = set()
    context = use_context or {}
    occurrences = {o["id"]: o for o in bundle["occurrences"]}
    for effect in bundle["effects"]:
        occurrence = occurrences.get(effect["occurrenceId"])
        intervention = next((t for t in bundle["types"] if t["id"] == effect["typeId"]), None)
        if (effect["id"] in eligible and intervention and intervention["interventionSubset"]
                and occurrence and occurrence["intentionality"] == "DELIBERATE"
                and occurrence["control"]["actor"] == context.get("actor")
                and occurrence["control"]["extent"] in {"FULL", "PARTIAL"}
                and context.get("context") == effect["scope"]["context"]
                and context.get("prerequisitesCleared") is True
                and context.get("risksReviewed") is True
                and context.get("applicabilityConfirmed") is True
                and context.get("label") == "SYNTHETIC / NON_PRODUCTION"):
            identities.add(effect["typeId"])
    return {"label": "SYNTHETIC / NON_PRODUCTION", "productionEligible": False,
            "statusesChanged": 0, "quantitativeModelEligible": False,
            "scientificSimulationEligibleEffectIds": sorted(eligible),
            "actorActionEligibleInterventionIds": sorted(identities),
            "eligibleSimulationEffectIds": sorted(eligible),
            "eligibleSimulationInterventionIds": sorted(identities), "errors": errors}


def synthetic_fixture():
    """Fictional examples, never a scientific dataset."""
    label = "SYNTHETIC / NON_PRODUCTION"
    governance = {"label": label, "architectureDecision": "PENDING", "lifecycleStatus": "REVIEW_READY", "activationStatus": "NOT_ELIGIBLE"}
    scope = {k: "Fictional laboratory system; demonstration only" for k in ("population", "context", "boundaryConditions", "timing", "measurement")}
    bundle = {"label": label, "types": [], "occurrences": [], "effects": [], "evidence": [],
              "entities": [{"id": "SYN-DRIVER-" + l, "entityType": "DRIVER", "layer": l, "label": label} for l in LAYERS]
              + [{"id": "SYN-RDS-BIO", "entityType": "RDS", "layer": "BIO", "label": label}],
              "relationships": [{"id": "SYN-REL-001", "family": "CAUSAL", "governed": True, "sourceId": "SYN-DRIVER-SOC", "targetId": "SYN-DRIVER-PSY", "label": label}],
              "sources": [{"id": "SYN-SOURCE-001", "description": "Fictional source, no real citation", "label": label}]}
    names = ["Scheduling policy", "Environmental shock", "Technology outage", "Informational disclosure", "Network change", "Gradual physiology", "Moderator change", "Conditional reversal", "Access enabling", "Cyclic exposure", "Structural reconfiguration"]
    origins = [["INS"], ["ENV", "SOC"], ["TEC"], ["INF"], ["SOC"], ["BIO"], ["PSY", "CUL"], ["CUL"], ["INS"], ["BIO"], ["TEC", "ENV"]]
    patterns = ["DISCRETE", "REPEATED", "CONTINUOUS", "DISCRETE", "GRADUAL", "CUMULATIVE", "REPEATED", "DISCRETE", "CONTINUOUS", "CYCLIC", "GRADUAL"]
    changes = ["INCREASE", "DECREASE", "DECREASE", "INCREASE", "ADVANCE", "INCREASE", "DECREASE", "REVERSE", "ENABLE", "CONTEXT_DEPENDENT", "RECONFIGURE"]
    for index, prop in enumerate(PROPERTIES):
        suffix = f"{index + 1:03}"
        tid, oid, eid, aid = (f"SYN-{prefix}-{suffix}" for prefix in ("TYPE", "OCC", "EFFECT", "EVIDENCE"))
        action = index in {0, 3, 6, 8}
        bundle["types"].append({"id": tid, "name": "SYNTHETIC " + names[index], "identityKey": names[index], "kindTags": ["ACTION", "PROCESS"] if action else ["EVENT", "EXPOSURE", "PROCESS"], "originLayers": origins[index], "interventionSubset": action, "packageKind": "ATOMIC", "components": [], "componentEnumeration": "NOT_APPLICABLE", "description": "Fictional structural demonstration; no scientific claim", "governance": copy.deepcopy(governance)})
        bundle["occurrences"].append({"id": oid, "typeId": tid, "episodeKey": "fictional-episode-" + suffix, "epistemicStatus": "HYPOTHETICAL", "actorOrSourceSystem": "Fictional source system", "intentionality": "DELIBERATE" if action else "NON_AGENTIC", "control": {"actor": "Fictional practitioner", "extent": "PARTIAL" if action else "NONE", "conditions": "Only under fictional scope"}, "boundary": {"system": "Fictional receiving system", "position": "EXTERNAL", "causalExogeneity": "NOT_INFERRED_FROM_EXTERNALITY"}, "pattern": [patterns[index]], "timing": "Defined synthetic episode", "intensityDose": None, "duration": None, "reach": "Synthetic population only", "scope": copy.deepcopy(scope), "occurrenceEvidenceIds": [], "governance": copy.deepcopy(governance)})
        rel_target = prop.startswith("RELATIONSHIP_")
        bundle["effects"].append({"id": eid, "typeId": tid, "occurrenceId": oid, "targetKind": "RELATIONSHIP" if rel_target else "DRIVER", "targetId": "SYN-REL-001" if rel_target else "SYN-DRIVER-" + LAYERS[index % 8], "targetLayers": ["SOC", "PSY"] if rel_target else [LAYERS[index % 8]], "claimSemantics": "MODERATION" if rel_target else "CAUSAL", "productionMethod": "SOURCE_EXTRACTION", "property": prop, "change": changes[index], "functionalShape": "CYCLIC" if index == 9 else None, "intendedDirection": changes[index] if action else None, "knowledgeStatus": "SUPPORTED_EFFECT", "mechanism": "Fictional mechanism for schema exercise only", "mechanisticDriverIds": ["SYN-DRIVER-PSY"] if rel_target else [], "scope": copy.deepcopy(scope), "evidenceIds": [aid], "contributionKey": "fictional-contribution-" + suffix, "propagationRole": "PRIMARY", "reconciliation": None, "interaction": {"mode": "NONE", "otherEffectIds": [], "evidenceIds": []}, "consequences": {"valence": "NOT_EVALUATED", "unintended": [], "distribution": "Not inferred beyond fictional population", "risks": ["Do not use for real decisions"]}, "governance": copy.deepcopy(governance)})
        bundle["evidence"].append({"id": aid, "assertionId": eid, "sourceFindings": [{"sourceId": "SYN-SOURCE-001", "basis": ["EXPERIMENT"], "finding": "Fictional supportive result", "disposition": "SUPPORTS", "scope": copy.deepcopy(scope), "passage": "Synthetic passage, not a real source", "datasetId": "SYN-DATASET-001", "limitations": ["Fictional evidence; no external validity"]}], "synthesis": {"disposition": "SUPPORTS", "rationale": "Fixture-only synthesis", "contraryEvidenceSearch": "ASSESSED", "datasetOverlap": "All fixtures share one fictional dataset; never independent evidence"}, "confidence": "LOW", "confidenceRationale": "Fictional confidence to exercise distinct field", "completeness": {k: "SPECIFIED" for k in ("target", "direction", "mechanism", "population", "context", "timing", "measurement", "boundaries")}, "uncertainty": ["Entire example is fictional"], "provenance": {"actorClass": "AI_OR_AUTOMATION", "method": "Synthetic fixture construction", "revision": 1, "recordedAt": "2026-09-06T00:00:00Z", "decisionReferences": ["PENDING proposal only"]}, "governance": copy.deepcopy(governance)})
    # Route C: the event changes a moderator Driver; a separate scoped assertion
    # describes that moderator's change to an exact edge. One contribution only.
    driver_effect = copy.deepcopy(bundle["effects"][6])
    driver_effect.update(id="SYN-EFFECT-012", targetKind="DRIVER",
                         targetId="SYN-DRIVER-CUL", targetLayers=["CUL"],
                         claimSemantics="CAUSAL", property="LEVEL", change="INCREASE",
                         mechanism="Fictional action changes moderator Driver; separate moderation evidence is required",
                         mechanisticDriverIds=[], evidenceIds=["SYN-EVIDENCE-012"])
    driver_effect["reconciliation"] = "Primary event-to-moderator contribution; SYN-EFFECT-007 describes the same route, never add a second effect"
    bundle["effects"][6]["propagationRole"] = "MEDIATOR_DESCRIPTION"
    bundle["effects"][6]["mechanisticDriverIds"] = ["SYN-DRIVER-CUL"]
    bundle["effects"][6]["reconciliation"] = "Independent moderation evidence describes SYN-DRIVER-CUL modifying SYN-REL-001; counted through SYN-EFFECT-012 only"
    bundle["effects"].append(driver_effect)
    driver_evidence = copy.deepcopy(bundle["evidence"][6])
    driver_evidence.update(id="SYN-EVIDENCE-012", assertionId="SYN-EFFECT-012")
    driver_evidence["sourceFindings"][0]["sourceId"] = "SYN-SOURCE-002"
    driver_evidence["sourceFindings"][0]["datasetId"] = "SYN-DATASET-002"
    driver_evidence["sourceFindings"][0]["finding"] = "Fictional independently supported action-to-moderator change"
    driver_evidence["synthesis"]["datasetOverlap"] = "Separate fictional dataset for action-to-moderator segment; independent of fictional moderation finding"
    bundle["evidence"].append(driver_evidence)
    bundle["sources"].append({"id": "SYN-SOURCE-002", "description": "Second fictional source for independent route-C segment; no real citation", "label": label})
    for assessment in bundle["evidence"]:
        finding_id = assessment["id"].replace("EVIDENCE", "FINDING")
        assessment["sourceFindings"][0]["id"] = finding_id
        assessment["synthesis"]["sourceFindingIds"] = [finding_id]
        assessment["sourceFindings"][0]["inputRole"] = "DIRECT_FINDING"
        assessment["sourceFindings"][0]["accessDepth"] = "SYNTHETIC"
        assessment["sourceFindings"][0]["nullInterpretation"] = None
    for effect in bundle["effects"]:
        effect["inferenceProvenance"] = None
    return bundle


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-fixture", action="store_true")
    args = parser.parse_args()
    fixture = synthetic_fixture()
    print(json.dumps(fixture if args.emit_fixture else dry_run(fixture), indent=2, sort_keys=True))
