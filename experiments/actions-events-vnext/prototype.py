"""Read-only scientific inventory. All output is confined to this experiment."""
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
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASELINE = "2636dd9a8b7bad1da3d7dfa21db5fe877f4de4e1"


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT).decode("utf-8").strip()


def output_dir(path):
    destination = Path(path).resolve()
    # Resolve junctions/symlinks before containment; never use string prefixes.
    if not destination.is_relative_to(HERE) or destination == HERE:
        raise ValueError("Output must be an explicitly supplied subdirectory of the experiment")
    destination.mkdir(parents=True, exist_ok=True)
    return destination


def write_json(directory, name, value):
    write_text(directory, name, json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n")


def write_text(directory, name, value):
    destination = (directory / name).resolve()
    if not destination.is_relative_to(HERE) or not destination.is_relative_to(directory.resolve()):
        raise ValueError("Output escapes experimental directory")
    destination.write_text(value, encoding="utf-8", newline="\n")


def protected_hashes():
    paths = git("ls-files", "-z").split("\0")
    result = {}
    for name in paths:
        if name and not name.startswith("experiments/actions-events-vnext/") and name != "docs/governance/ACTIONS_EVENTS_V1_GOVERNANCE_DECISION.md":
            payload = (ROOT / name).read_bytes()
            result[name] = {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}
    return result


def freeze():
    destination = HERE / "PROTECTED_BASELINE.json"
    if destination.exists():
        raise ValueError("Baseline already frozen; refusing to overwrite")
    write_json(HERE, destination.name, {
        "baselineCommit": git("rev-parse", "HEAD"), "lastKnownBaseline": BASELINE,
        "differenceFromLastKnown": git("diff", "--name-status", BASELINE, "HEAD"),
        "remote": git("remote", "get-url", "origin"), "hashMode": "RAW_BYTES",
        "files": protected_hashes(),
    })


def verify_protected():
    baseline = json.loads((HERE / "PROTECTED_BASELINE.json").read_text(encoding="utf-8"))
    actual = protected_hashes()
    differences = sorted(name for name in baseline["files"].keys() | actual.keys()
                         if baseline["files"].get(name) != actual.get(name))
    untracked = [n for n in git("ls-files", "--others", "--exclude-standard").splitlines()
                 if not n.startswith("experiments/actions-events-vnext/") and n != "docs/governance/ACTIONS_EVENTS_V1_GOVERNANCE_DECISION.md"]
    return {"passed": not differences and not untracked, "filesCompared": len(actual), "differences": differences,
            "untrackedOutsideExperiment": untracked,
            "baselineCommit": baseline["baselineCommit"], "hashMode": "RAW_BYTES"}


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
        "protectedComparison": verify_protected(),
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


def emit(family_id, destination):
    data = inventory()
    family = next((r for r in data["families"] if r["id"] == family_id), None)
    if family is None:
        raise ValueError("Unknown canonical Family ID")
    directory = output_dir(destination)
    write_json(directory, "inventory.json", data)
    for key in ("layers", "families", "entities", "matrices", "auditQueue"):
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
    write_json(directory, f"{family_id}_baseline.json", detail)
    write_json(directory, f"{family_id}_research_template.json", {
        "label": "BLANK_NON_PRODUCTION_TEMPLATE", "architectureDecision": "PENDING", "familyId": family_id,
        "baselineCommit": data["summary"]["baselineCommit"], "activationStatus": "NOT_ELIGIBLE", "productionGraphEligible": False,
        "relationships": [], "happeningTypes": [], "occurrences": [], "effectAssertions": [], "evidenceAssessments": [],
        "searchLog": [], "noFindings": [], "unresolved": [], "ownership": [],
        "effectChecklist": ["LEVEL", "VARIABILITY", "RATE", "THRESHOLD", "TIMING", "PERSISTENCE", "RELATIONSHIP_STRENGTH", "RELATIONSHIP_DIRECTION", "ENABLEMENT", "FUNCTIONAL_SHAPE", "STRUCTURE"],
    })
    write_json(directory, "protected-comparison.json", verify_protected())
    return data["summary"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("freeze")
    sub.add_parser("verify-protected")
    inv = sub.add_parser("inventory")
    inv.add_argument("--family", required=True)
    inv.add_argument("--output", required=True)
    demo = sub.add_parser("synthetic-demo")
    demo.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.command == "freeze":
        freeze()
        print("Protected baseline frozen")
    elif args.command == "verify-protected":
        result = verify_protected()
        print(json.dumps(result, indent=2))
        return 0 if result["passed"] else 1
    elif args.command == "synthetic-demo":
        import copy
        import model
        fixture = model.synthetic_fixture()
        before = copy.deepcopy(fixture)
        decisions = [{"objectId": r["id"], "revision": 1,
                      "actorClass": "AUTHORIZED_HUMAN_GOVERNOR", "hypothetical": True,
                      "outcome": "APPROVE"}
                     for collection in ("types", "effects", "evidence") for r in fixture[collection]]
        context = {"actor": "Fictional practitioner", "context": fixture["effects"][0]["scope"]["context"],
                   "prerequisitesCleared": True, "risksReviewed": True,
                   "applicabilityConfirmed": True, "feasibilityConfirmed": True,
                   "legalConstraintsCleared": True, "ethicalConstraintsCleared": True, "label": "SYNTHETIC / NON_PRODUCTION"}
        result = {"label": "SYNTHETIC / NON_PRODUCTION", "architectureDecision": "PENDING",
                  "withoutHypotheticalApproval": model.dry_run(fixture),
                  "hypotheticalScientificReview": model.dry_run(fixture, decisions),
                  "hypotheticalActorUse": model.dry_run(fixture, decisions, context),
                  "inputUnchanged": fixture == before,
                  "note": "Fictional approvals only; no real governance decision or activation."}
        write_json(output_dir(args.output), "synthetic-dry-run.json", result)
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(emit(args.family, args.output), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
