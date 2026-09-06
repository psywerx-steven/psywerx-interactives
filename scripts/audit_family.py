"""Read-only recorded coverage. Output is confined to explicit reporting paths."""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
from collections import Counter, defaultdict
import actions_events_v1 as ae
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASELINE = "2636dd9a8b7bad1da3d7dfa21db5fe877f4de4e1"


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT).decode("utf-8").strip()


def output_dir(path):
    destination = Path(path).resolve()
    permitted = [ROOT / "reports/actions-events-v1", ROOT / "experiments/actions-events-vnext"]
    if not any(destination.is_relative_to(p.resolve()) and destination != p.resolve() for p in permitted):
        raise ValueError("Output must be a child of reports/actions-events-v1 or experiments/actions-events-vnext")
    destination.mkdir(parents=True, exist_ok=True)
    return destination


def write_text(directory, name, value):
    destination = (directory / name).resolve()
    if not destination.is_relative_to(directory.resolve()):
        raise ValueError("Output file escapes explicit directory")
    destination.write_text(value, encoding="utf-8", newline="\n")


def write_json(directory, name, value):
    write_text(directory, name, json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n")


def scientific_integrity():
    names = git("ls-tree", "-r", "--name-only", BASELINE, "--", "data").splitlines()
    changed, hashes = [], {}
    for name in names:
        frozen = subprocess.check_output(["git", "show", BASELINE + ":" + name], cwd=ROOT)
        current = (ROOT / name).read_bytes()
        hashes[name] = hashlib.sha256(current).hexdigest()
        if frozen.replace(b"\r\n", b"\n") != current.replace(b"\r\n", b"\n"):
            changed.append(name)
    return {"passed": not changed, "filesCompared": len(names), "changed": changed,
            "baselineCommit": BASELINE, "rawCurrentSha256": hashes,
            "comparison": "EXACT_GIT_CONTENT_EXCEPT_CHECKOUT_LINE_ENDINGS"}


def production_module():
    spec = importlib.util.spec_from_file_location("ae_readonly_v1", ROOT / "scripts/relationship_intervention_v1.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    previous = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


def native(filename, key):
    return read(f"data/relationship-intervention-v1/{filename}.json")[key]


def active(record):
    return record.get("governance", {}).get("lifecycleStatus") == "GOVERNED" and record["governance"]["activationStatus"] == "ACTIVE"


def edge(record, origin):
    legacy = origin == "V3"
    family = record["relationFamily"]
    return {
        "id": record["id"], "origin": origin,
        "source": record.get("subjectEntityId" if legacy else "sourceEntityId"),
        "target": record.get("objectEntityId" if legacy else "targetEntityId"),
        "semanticType": "SEMANTIC" if family == "SEMANTIC_MAPPING" else family,
        "originalRelationFamily": family, "predicate": record["predicate"],
        "polarity": record.get("polarity"),
        "authority": record.get("governanceStatus") if legacy else record["governance"]["lifecycleStatus"],
        "activation": record.get("governanceStatus") if legacy else record["governance"]["activationStatus"],
    }


def inventory():
    source_commit = git("rev-parse", "HEAD")
    entities = {r["id"]: r for r in read("data/entities.json")}
    families = {r["id"]: r for r in read("data/families.json")["families"]}
    legacy = read("data/relationships.json")
    relationships = native("relationships", "relationships")
    interventions = native("interventions", "interventions")
    effects = native("intervention-effects", "interventionEffects")
    evidence = native("evidence-assessments", "evidenceAssessments")
    workspace = read("data/candidates/relationship-intervention-v1/workspace.json")
    materialization = read("data/relationship-intervention-v1/materialization-manifest.json")
    v1 = production_module()
    projections = v1.project_current_v3()
    assert {r["id"] for r in projections} == {r["id"] for r in legacy["relationships"]}
    all_edges = [edge(r, "V3") for r in legacy["relationships"]] + [edge(r, "V1_NATIVE") for r in relationships]
    assert len({e["id"] for e in all_edges}) == len(all_edges), "ID collision requires review"
    active_edges = [e for e in all_edges if e["activation"] == "ACTIVE"
                    and (e["origin"] == "V3" or e["authority"] == "GOVERNED")]
    causal = [e for e in active_edges if e["semanticType"] == "CAUSAL"]
    layers = sorted({r["layer"] for r in entities.values()})
    incoming, outgoing = Counter(), Counter()
    for e in causal:
        incoming[e["target"]] += 1
        outgoing[e["source"]] += 1
    effects_by_driver = defaultdict(list)
    intervention_lookup = {r["id"]: r for r in interventions}
    for effect in effects:
        if active(effect) and active(intervention_lookup[effect["interventionId"]]):
            for driver in [effect.get("targetDriverId")] if effect["targetKind"] == "DRIVER" else effect["mechanisticDriverIds"]:
                effects_by_driver[driver].append(effect)
    rds = {r["id"]: r for r in read("data/relational-derived-states.json")}
    entity_rows = []
    for identifier, entity in sorted(entities.items()):
        spec = rds.get(identifier, {})
        dependencies = spec.get("constituentSpecifications", [])
        flags = []
        if identifier in rds:
            for key in ("derivationType", "derivationLogic", "scopeRequirements", "recalculationBehavior", "constituentSpecifications"):
                if not spec.get(key):
                    flags.append("MISSING_" + key)
            if outgoing[identifier]:
                flags.append("RDS_CAUSAL_SOURCE_REVIEW")
            if outgoing[identifier] and not incoming[identifier]:
                flags.append("STRUCTURAL_RDS_ROOT_REVIEW_NOT_EXECUTION_VIOLATION")
            flags.append("NO_PER_RECORD_DERIVATION_VERSION_USE_FROZEN_COMMIT" if not spec.get("derivationVersion") else "VERSION_PRESENT")
        if entity.get("blockedFields"):
            flags.append("ENTITY_BLOCKED_FIELDS")
        entity_rows.append({
            "id": identifier, "name": entity["name"], "entityType": entity["entityType"],
            "layer": entity["layer"], "familyId": entity["primaryFamilyId"],
            "causalIn": incoming[identifier], "causalOut": outgoing[identifier],
            "causalIsolated": incoming[identifier] + outgoing[identifier] == 0,
            "modifiable": entity.get("modifiability"),
            "activeEffectIds": sorted(e["id"] for e in effects_by_driver[identifier]),
            "deliveryModalities": sorted({m for e in effects_by_driver[identifier] for m in e["deliveryModalities"]}),
            "derivationInputs": dependencies, "rdsFlags": flags,
            "blockedFields": entity.get("blockedFields", []),
        })
    projection_flags = {r["id"]: r["compatibility"]["blockedFields"] for r in projections}
    family_rows = []
    for identifier, family in sorted(families.items()):
        members = [e for e in entity_rows if e["familyId"] == identifier]
        ids = {e["id"] for e in members}
        incident = [e for e in causal if e["source"] in ids or e["target"] in ids]
        internal = [e for e in incident if e["source"] in ids and e["target"] in ids]
        cross_family = [e for e in incident if e not in internal]
        cross_layer = [e for e in cross_family if entities[e["source"]]["layer"] != entities[e["target"]]["layer"]]
        legacy_incident = [e for e in incident if e["origin"] == "V3" and projection_flags.get(e["id"])]
        counts = Counter(e["entityType"] for e in members)
        row = {"id": identifier, "name": family["name"], "layer": family["layer"],
               "drivers": counts["DRIVER"], "rds": counts["RELATIONAL_DERIVED_STATE"], "entities": len(members),
               "causalIncident": len(incident), "internal": len(internal),
               "sameLayerCrossFamily": len(cross_family) - len(cross_layer), "crossLayer": len(cross_layer),
               "causallyIsolatedEntities": sum(e["causalIsolated"] for e in members),
               "isolatedFamily": not cross_family, "legacyIncompleteIncident": len(legacy_incident),
               "rdsCausalSourceCount": sum(bool(outgoing[e["id"]]) for e in members if e["entityType"] != "DRIVER"),
               "blockedEntityCount": sum(bool(e["blockedFields"]) for e in members),
               "activeEffectCount": sum(len(e["activeEffectIds"]) for e in members),
               "memberIds": sorted(ids)}
        assert len(members) == family["totalEntityCount"]
        family_rows.append(row)
    layer_rows = []
    for layer in layers:
        members = [e for e in entity_rows if e["layer"] == layer]
        layer_rows.append({"layer": layer, "families": sum(f["layer"] == layer for f in family_rows),
                           "drivers": sum(e["entityType"] == "DRIVER" for e in members),
                           "rds": sum(e["entityType"] != "DRIVER" for e in members), "entities": len(members),
                           "causalIsolatedEntities": sum(e["causalIsolated"] for e in members),
                           "activeEffectCount": sum(len(e["activeEffectIds"]) for e in members)})
    matrices = defaultdict(Counter)
    scope_counts = defaultdict(Counter)
    for e in active_edges:
        source, target = entities[e["source"]], entities[e["target"]]
        matrices[e["semanticType"]][(source["layer"], target["layer"])] += 1
        scope = "withinFamily" if source["primaryFamilyId"] == target["primaryFamilyId"] else "sameLayerCrossFamily" if source["layer"] == target["layer"] else "crossLayer"
        scope_counts[e["semanticType"]][scope] += 1
    queue = []
    for f in family_rows:
        # Deliberately transparent triage rubric, not a scientific impact score.
        parts = {"rdsCausalSources": 5 * f["rdsCausalSourceCount"], "rdsComplexity": 2 * f["rds"],
                 "isolatedFamily": 4 * int(f["isolatedFamily"]), "noCrossLayer": 2 * int(f["crossLayer"] == 0),
                 "isolatedEntities": f["causallyIsolatedEntities"], "blockedEntities": 3 * f["blockedEntityCount"],
                 "legacyReviewBurden": min(10, f["legacyIncompleteIncident"])}
        queue.append({"familyId": f["id"], "name": f["name"], "layer": f["layer"],
                      "priorityScore": sum(parts.values()), "scoreComponents": parts,
                      "status": "EXISTING_PILOT_FOLLOWUP_ONLY" if f["id"] == "BIO-F01" else "NO_AUDIT_STATUS_IN_THIS_INVENTORY",
                      "governanceDecision": "PENDING", "nextAction": "Review recorded membership, RDS inputs and existing incident claims only after separate audit authorization"})
    queue.sort(key=lambda r: (-r["priorityScore"], r["familyId"]))
    for rank, row in enumerate(queue, 1):
        row["rank"] = rank
    counts = lambda rows: dict(sorted(Counter(f"{r['governance']['lifecycleStatus']} / {r['governance']['activationStatus']}" for r in rows).items()))
    candidate_keys = ("relationships", "evidenceAssessments", "causalPathways", "interventions", "interventionEffects")
    candidate_counts = {k: {"records": len(workspace[k]), "lifecycle": counts(workspace[k])} for k in candidate_keys}
    candidate_counts["relationships"]["semanticAndLifecycle"] = dict(Counter(
        f"{r['relationFamily']} / {r['governance']['lifecycleStatus']}" for r in workspace["relationships"]))
    all_native = relationships + interventions + effects + evidence + native("causal-pathways", "causalPathways")
    duplicates = defaultdict(list)
    for e in active_edges:
        duplicates[(e["source"], e["predicate"], e["target"])].append(e["id"])
    polarity_flags = defaultdict(list)
    for e in causal:
        polarity_flags[(e["source"], e["target"])].append(e)
    summary = {
        "label": "READ_ONLY_RECORDED_COVERAGE_NOT_SCIENTIFIC_AUDIT",
        "baselineCommit": source_commit, "lastKnownBaseline": BASELINE,
        "protectedComparison": scientific_integrity(),
        "entities": len(entities), "families": len(families), "layers": len(layers),
        "drivers": sum(e["entityType"] == "DRIVER" for e in entity_rows), "rds": len(rds),
        "legacy": {"active": len(legacy["relationships"]), "causal": sum(e["relationFamily"] == "CAUSAL" for e in legacy["relationships"]),
                   "deprecated": len(legacy["deprecatedRelationships"]), "candidates": len(legacy["relationshipCandidates"]),
                   "bySemanticAndStatus": dict(Counter(f"{r['relationFamily']} / {r.get('governanceStatus')}" for bucket in ("relationships", "deprecatedRelationships", "relationshipCandidates") for r in legacy[bucket]))},
        "projections": {"count": len(projections), "additionalPropositions": 0,
                        "incomplete": sum(r["compatibility"]["migrationCompleteness"] == "INCOMPLETE" for r in projections),
                        "legacyOnly": sum(r["compatibility"]["v1Executability"] == "LEGACY_ONLY" for r in projections)},
        "native": {"relationships": len(relationships), "relationshipLifecycle": counts(relationships),
                   "interventions": counts(interventions), "effects": counts(effects), "evidence": counts(evidence),
                   "allScientificLifecycle": counts(all_native)},
        "combinedActiveRelationships": len(active_edges), "combinedActiveCausal": len(causal),
        "combinedBySemantic": dict(Counter(e["semanticType"] for e in active_edges)),
        "scopeCountsBySemantic": {k: dict(v) for k, v in scope_counts.items()},
        "candidates": candidate_counts,
        "materializedCandidateCopies": {
            "assertionAndIdentity": len(materialization["candidateLineage"]),
            "evidence": len({r["evidenceCandidateId"] for r in materialization["candidateLineage"] if r.get("evidenceCandidateId")}),
            "countedAsAdditionalCanonicalPropositions": 0},
        "causallyIsolatedEntities": sum(e["causalIsolated"] for e in entity_rows),
        "isolatedFamilies": [f["id"] for f in family_rows if f["isolatedFamily"]],
        "familiesWithNoCrossLayerCausal": [f["id"] for f in family_rows if f["crossLayer"] == 0],
        "familiesWithNoIncidentCausal": [f["id"] for f in family_rows if f["causalIncident"] == 0],
        "rdsCausalSourceIds": [e["id"] for e in entity_rows if "RDS_CAUSAL_SOURCE_REVIEW" in e["rdsFlags"]],
        "sharedRdsInputPairs": [
            {"rdsIds": [left, right], "sharedEntityInputs": sorted(
                {s["entityId"] for s in rds[left].get("constituentSpecifications", []) if s.get("entityId")}
                & {s["entityId"] for s in rds[right].get("constituentSpecifications", []) if s.get("entityId")})}
            for left in sorted(rds) for right in sorted(rds) if left < right
            and {s["entityId"] for s in rds[left].get("constituentSpecifications", []) if s.get("entityId")}
            & {s["entityId"] for s in rds[right].get("constituentSpecifications", []) if s.get("entityId")}],
        "endpointDuplicateFlags": [ids for ids in duplicates.values() if len(ids) > 1],
        "oppositePolarityReviewFlags": [[e["id"] for e in rows] for rows in polarity_flags.values() if {e["polarity"] for e in rows} >= {"POSITIVE", "NEGATIVE"}],
        "highDegreeReviewFlags": sorted([{"id": e["id"], "degree": e["causalIn"] + e["causalOut"]} for e in entity_rows], key=lambda e: (-e["degree"], e["id"]))[:9],
        "openGovernanceItems": read("data/migration-manifest.json").get("openGovernanceItems"),
        "warnings": ["Matrix orientation is stored proposition source/target, not causal origin for noncausal graphs.",
                     "Symmetric associations stored once in canonical endpoint order; matrix is not bidirectional influence.",
                     "RDS root flags describe structure, not evidence that a scenario executes RDS exogenously.",
                     "Endpoint/polarity flags require scoped human review; they do not adjudicate duplicates or contradiction.",
                     "High-degree flags are top nine (~1%) by recorded degree, not evidence of invalidity."]}
    return {"summary": summary, "layers": layer_rows, "families": family_rows, "entities": entity_rows,
            "edges": active_edges, "matrices": [{"semanticType": k, "originLayer": a, "targetLayer": b, "count": matrices[k][a,b]}
                         for k in sorted(matrices) for a in layers for b in layers],
            "auditQueue": queue, "projectionIncompleteFields": projection_flags,
            "rdsSpecifications": list(rds.values())}


def ownership(source_id, target_id, semantics, entities, relationship_target_id=None, relationships=None):
    if relationship_target_id:
        edge_record = relationships[relationship_target_id]
        source_id = edge_record.get("sourceEntityId", edge_record.get("subjectEntityId"))
    source_family = entities[source_id]["primaryFamilyId"]
    target_family = entities[target_id]["primaryFamilyId"] if target_id in entities else source_family
    return min(source_family, target_family) if semantics in {"ASSOCIATION", "SYMMETRIC_SEMANTIC"} else source_family


def enriched_inventory():
    data = inventory()
    entities = {r["id"]: r for r in read("data/entities.json")}
    scopes, family_matrix = Counter(), Counter()
    for e in data["edges"]:
        a, b = entities[e["source"]], entities[e["target"]]
        scope = "WITHIN_FAMILY" if a["primaryFamilyId"] == b["primaryFamilyId"] else ("SAME_LAYER_CROSS_FAMILY" if a["layer"] == b["layer"] else "CROSS_LAYER")
        scopes[e["semanticType"], scope, a["layer"], b["layer"]] += 1
        family_matrix[e["semanticType"], a["primaryFamilyId"], b["primaryFamilyId"]] += 1
    data["scopeMatrices"] = [{"semanticType": k, "scope": s, "originLayer": a, "targetLayer": b, "count": n} for (k,s,a,b),n in sorted(scopes.items())]
    data["familyMatrix"] = [{"semanticType": k, "sourceFamily": a, "targetFamily": b, "count": n} for (k,a,b),n in sorted(family_matrix.items())]
    native = ae.read(ae.DATA)
    ae.validate_catalog(native)
    data["summary"]["actionsEvents"] = {k: len(native[k]) for k in ae.COLLECTIONS}
    data["summary"]["actionsEvents"]["sameIdentityCompatibilityViews"] = len(ae.compatibility_catalog())
    data["summary"]["actionsEvents"]["additionalScientificPropositionsFromBridge"] = 0
    type_lookup = {r["id"]: r for r in native["happeningTypes"]}
    native_by_driver = defaultdict(list)
    for effect in native["effectAssertions"]:
        if ae.state_active(effect) and ae.state_active(type_lookup[effect["typeId"]]):
            drivers = [effect["targetId"]] if effect["targetKind"] == "DRIVER" else effect["mechanisticDriverIds"]
            for identifier in drivers:
                native_by_driver[identifier].append(effect["id"])
    for entity in data["entities"]:
        entity["nativeActionsEventsEffectIds"] = sorted(native_by_driver[entity["id"]])
    for family in data["families"]:
        family["nativeActionsEventsEffectIds"] = sorted({i for d in family["memberIds"] for i in native_by_driver[d]})
    for layer in data["layers"]:
        layer["nativeActionsEventsEffectCount"] = len({i for d in data["entities"] if d["layer"] == layer["layer"] for i in d["nativeActionsEventsEffectIds"]})
    data["summary"]["matrixConvention"] = "SPARSE_RECORDED_COUNTS; omitted cells have zero RECORDED edges, not zero real effect"
    families = {f["id"]: f for f in data["families"]}
    for row in data["auditQueue"]:
        family = families[row["familyId"]]
        penalty = 2 if family["activeEffectCount"] == 0 and not family["nativeActionsEventsEffectIds"] else 0
        row["scoreComponents"]["noRecordedActiveEffect"] = penalty
        row["priorityScore"] += penalty
    data["auditQueue"].sort(key=lambda r: (-r["priorityScore"], r["familyId"]))
    for rank,row in enumerate(data["auditQueue"],1):
        row["rank"] = rank
    return data


def emit(family_id, destination):
    data = enriched_inventory()
    family = next((r for r in data["families"] if r["id"] == family_id), None)
    if family is None:
        raise ValueError("Unknown canonical Family ID")
    directory = output_dir(destination)
    write_json(directory, "inventory.json", data)
    for key in ("layers", "families", "entities", "matrices", "auditQueue", "scopeMatrices", "familyMatrix"):
        rows = data[key]
        buffer = io.StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, ensure_ascii=False, sort_keys=True) if isinstance(v, (list, dict)) else v for k, v in row.items()})
        write_text(directory, f"{key}.csv", buffer.getvalue())
    ids = set(family["memberIds"])
    original_entities = read("data/entities.json")
    original_legacy = read("data/relationships.json")
    native_relationships = native("relationships", "relationships")
    incident = lambda r: r.get("subjectEntityId", r.get("sourceEntityId")) in ids or r.get("objectEntityId", r.get("targetEntityId")) in ids
    detail = {"label": "READ_ONLY_BASELINE", "baselineCommit": data["summary"]["baselineCommit"], "family": family,
              "entities": [r for r in original_entities if r["id"] in ids],
              "legacyIncidentByBucket": {k: [r for r in original_legacy[k] if incident(r)] for k in ("relationships", "deprecatedRelationships", "relationshipCandidates")},
              "nativeIncident": [r for r in native_relationships if incident(r)],
              "candidateIncident": [r for r in read("data/candidates/relationship-intervention-v1/workspace.json")["relationships"] if incident(r)],
              "rdsSpecifications": [r for r in data["rdsSpecifications"] if r["id"] in ids]}
    detail["aliases"] = [r for r in read("data/aliases.json")["aliases"] if ids.intersection(r["entityIds"])]
    detail["crosswalks"] = [r for r in read("data/crosswalks.json")["crosswalks"] if r.get("legacyId") in ids or ids.intersection(r.get("successorIds", []))]
    detail["compatibilityViews"] = [r for r in ae.compatibility_catalog() if r["sourceObjectType"] == "INTERVENTION_EFFECT" and r["normalized"]["targetId"] in ids]
    write_json(directory, f"{family_id}_baseline.json", detail)
    write_json(directory, f"{family_id}_research_template.json", ae.empty_workspace(family_id, data["summary"]["baselineCommit"]))
    write_json(directory, "protected-comparison.json", scientific_integrity())
    return data["summary"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    summary = emit(args.family, args.output)
    print(json.dumps({k: summary[k] for k in ("entities", "families", "combinedActiveRelationships", "combinedActiveCausal")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
