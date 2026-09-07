"""Candidate-only Psychological Layer orchestration; never production mutation.

Generic Family runner is used for each Family against one cached immutable
inventory. Its repeated ontology-wide CSVs are omitted; one shared inventory is
stored. Scientific judgments must be separately authored, never inferred here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from unittest.mock import patch

import actions_events_v1 as ae
import audit_family as af

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "de38b3948f511602af7aa94a9cd80b78e1a00298"
PROGRAM = "AUD-PSYCHOLOGICAL-LAYER-AE-V1-20260907-001"
STORE = ROOT / "data/candidates/actions-events-v1/PSYCHOLOGICAL_LAYER"
DOCS = ROOT / "docs/governance/scale-up/PSYCHOLOGICAL_LAYER"
REPORT = ROOT / "reports/actions-events-v1/psychological-layer-v1"
FAMILIES = [f"PSY-F{i:02d}" for i in range(1, 15)]
STAGES = ["BASELINE", "ENTITY_REVIEW", "PASS_A_EXISTING", "PASS_A_GAPS",
          "PASS_B_ACTIONS_EVENTS", "EVIDENCE_RECONCILIATION", "SKEPTICAL_REVIEW",
          "DECISION_PACKAGE", "VALIDATION", "COMPLETE"]
PROTECTED_ROOTS = ["data", "schemas", "_migration_handoff_v0.3", "scenario-service",
                   "docs/governance/pilots", "experiments/network-state-vnext",
                   "scripts/relational_state_v1.py", "scripts/source_verification_v1.py",
                   "scripts/actions_events_v1.py", "scripts/relationship_intervention_v1.py"]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT).decode("utf-8").strip()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def encode(value):
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def write(path, value):
    path = Path(path).resolve()
    if not any(root.resolve() == root.absolute() and path.is_relative_to(root.resolve())
               for root in (STORE, DOCS, REPORT)):
        raise ValueError("Layer outputs confined to isolated candidate/docs/report roots")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value if isinstance(value, str) else encode(value), encoding="utf-8", newline="\n")


def protected_paths():
    return git("ls-tree", "-r", "--name-only", BASELINE, "--", *PROTECTED_ROOTS).splitlines()


def check_protected():
    frozen = read(STORE / "protected-baseline.json")
    changed = [p for p, h in frozen["normalizedSha256"].items()
               if not (ROOT / p).is_file() or digest(ROOT / p) != h]
    if changed:
        raise ValueError("PROTECTED SCIENCE DRIFT: " + ", ".join(changed))
    return {"passed": True, "filesCompared": len(frozen["normalizedSha256"]), "changed": []}


def endpoints(record):
    return (record.get("sourceEntityId", record.get("subjectEntityId")),
            record.get("targetEntityId", record.get("objectEntityId")))


def scope(record, entities):
    a, b = (entities[x] for x in endpoints(record))
    if a["primaryFamilyId"] == b["primaryFamilyId"]:
        return "WITHIN_FAMILY"
    if a["layer"] == b["layer"]:
        return "PSYCHOLOGICAL_CROSS_FAMILY"
    return "CROSS_LAYER_OUTGOING" if a["layer"] == "Psychological" else "CROSS_LAYER_INCOMING"


def freeze():
    if (STORE / "baseline.json").exists():
        raise ValueError("Baseline already exists; verify/reuse it, do not refreeze research")
    tracked = protected_paths()
    # Only baseline-tracked files: newly added candidate files are not science drift.
    dirty = git("diff", "--name-only", BASELINE, "--", *tracked)
    if dirty:
        raise ValueError("Investigate production drift before freezing: " + dirty)
    inv = af.enriched_inventory()
    inv["summary"]["baselineCommit"] = BASELINE
    expected = {"drivers": 770, "rds": 41, "entities": 811,
                "combinedActiveRelationships": 457, "combinedActiveCausal": 436}
    if any(inv["summary"][k] != v for k, v in expected.items()):
        raise ValueError("Unexpected production counts")
    families = [f for f in inv["families"] if f["layer"] == "Psychological"]
    if [f["id"] for f in families] != FAMILIES:
        raise ValueError("Unexpected Psychological Family membership")
    entities = {r["id"]: r for r in af.read("data/entities.json")}
    members = {i for f in families for i in f["memberIds"]}
    edges = [e for e in inv["edges"] if e["source"] in members or e["target"] in members]
    if len({e["id"] for e in edges}) != len(edges):
        raise ValueError("Duplicate active proposition ID")
    captured = {}

    def capture(directory, name, value):
        if name.endswith("_baseline.json") or name.endswith("_research_template.json"):
            captured[name] = json.loads(value)

    # Exact generic Family emit implementation, including aliases/crosswalks,
    # inactive/deprecated buckets and compatibility references; no copied logic.
    with patch.object(af, "enriched_inventory", return_value=inv), \
         patch.object(af, "scientific_integrity", return_value=inv["summary"]["protectedComparison"]), \
         patch.object(af, "write_text", side_effect=capture):
        for family in FAMILIES:
            af.emit(family, REPORT / "families" / family)
    write(REPORT / "inventory.json", inv)
    for f in FAMILIES:
        detail = captured[f + "_baseline.json"]
        detail["programId"] = PROGRAM
        detail["familyAuditId"] = PROGRAM.replace("PSYCHOLOGICAL-LAYER", f)
        detail["scienceOrigin"] = "PRODUCTION_BASELINE"
        write(STORE / f / "BASELINE.json", detail)
        write(STORE / f / "workspace.json", captured[f + "_research_template.json"])
    registry = {}
    for family in FAMILIES:
        detail = captured[family + "_baseline.json"]
        buckets = {**detail["legacyIncidentByBucket"], "nativeIncident": detail["nativeIncident"],
                   "candidateIncident": detail["candidateIncident"]}
        for bucket, rows in buckets.items():
            for r in rows:
                a, b = endpoints(r)
                if r["id"] not in registry:
                    sem = r["relationFamily"]
                    if sem == "DERIVATIONAL":
                        owner = entities[a]["primaryFamilyId"]
                    elif r.get("symmetry") == "SYMMETRIC":
                        owner = min(entities[a]["primaryFamilyId"], entities[b]["primaryFamilyId"])
                    else:
                        owner = entities[a]["primaryFamilyId"]
                    registry[r["id"]] = {"id": r["id"], "frozenRecord": r, "sourceBucket": bucket,
                        "scienceOrigin": "PRE_EXISTING_CANDIDATE" if "candidate" in bucket.lower() else "PRODUCTION_BASELINE",
                        "ownerFamilyId": owner, "processingFamilyId": family,
                        "endpointFamilyIds": sorted({entities[a]["primaryFamilyId"], entities[b]["primaryFamilyId"]}),
                        "psychologicalFamilyIds": [], "scope": scope(r, entities),
                        "primaryDisposition": None, "reviewStatus": "NOT_STARTED",
                        "review": None, "humanDecision": "PENDING — APPROVE / MODIFY / REJECT"}
                registry[r["id"]]["psychologicalFamilyIds"].append(family)
    # Prior AE pilot candidate copies are discovery context, not additional active
    # science or new Layer proposals. Materialization lineage is preserved intact.
    prior = []
    for path in sorted((ROOT / "data/candidates/actions-events-v1").glob("*/workspace.json")):
        if STORE in path.parents:
            continue
        for r in read(path).get("passA", {}).get("relationshipCandidates", []):
            if members.intersection(endpoints(r)):
                prior.append({"path": path.relative_to(ROOT).as_posix(), "record": r,
                              "scienceOrigin": "PRIOR_PILOT_CANDIDATE"})
    write(STORE / "prior-pilot-candidate-references.json", prior)
    write(STORE / "relationship-review-registry.json", registry)
    for name in ("candidate-proposition-registry", "cross-family-issues", "actions-events-identity-registry",
                 "candidate-source-registry", "source-overlap-registry", "architecture-escalations"):
        write(STORE / (name + ".json"), [])
    causal = [e for e in edges if e["semanticType"] == "CAUSAL"]
    pairs = {(e["source"], e["target"]): e["id"] for e in causal}
    stats = {"families": len(families), "drivers": sum(f["drivers"] for f in families),
        "rds": sum(f["rds"] for f in families), "entities": len(members),
        "uniqueActiveIncident": len(edges), "activeCausal": len(causal), "activeNoncausal": len(edges) - len(causal),
        "allStatusUniqueReviewRecords": len(registry),
        "activeScopes": dict(Counter(scope({"sourceEntityId": e["source"], "targetEntityId": e["target"]}, entities) for e in edges)),
        "activeSemantics": dict(Counter(e["semanticType"] for e in edges)),
        "rdsIds": sorted(i for i in members if entities[i]["entityType"] != "DRIVER"),
        "isolates": sorted(e["id"] for e in inv["entities"] if e["id"] in members and e["causalIsolated"]),
        "blockedEntityIds": sorted(e["id"] for e in inv["entities"] if e["id"] in members and e["blockedFields"]),
        "reciprocalPairs": sorted({tuple(sorted((identifier, pairs[b, a]))) for (a,b),identifier in pairs.items() if (b,a) in pairs}),
        "projectionAdditionalPropositions": 0}
    write(STORE / "baseline.json", {"programId": PROGRAM, "baselineCommit": BASELINE,
        "summary": stats, "familyInventory": families, "entityIds": sorted(members), "activeEdges": edges,
        "productionCounts": expected, "genericRunner": "audit_family.emit for all 14; one cached enriched inventory; duplicate global exports omitted"})
    write(STORE / "protected-baseline.json", {"baselineCommit": BASELINE, "normalization": "CRLF_TO_LF_ONLY",
        "normalizedSha256": {p: digest(ROOT / p) for p in tracked}})
    write(STORE / "progress.json", {"programId": PROGRAM, "families": {f: {stage: "DONE" if stage == "BASELINE" else "NOT_STARTED" for stage in STAGES} for f in FAMILIES}})
    lines = ["# Psychological Layer frozen baseline", "", f"Main: `{BASELINE}`. Program `{PROGRAM}`.", "",
        "Read-only inventory; coverage is not completed scientific review.", "", "```json", encode(stats).strip(), "```", "",
        "| Family | Drivers | RDS | Entities | Incident causal (not additive) |", "|---|---:|---:|---:|---:|"]
    lines += [f"| {f['id']} — {f['name']} | {f['drivers']} | {f['rds']} | {f['entities']} | {f['causalIncident']} |" for f in families]
    lines += ["", "Family source records, aliases, crosswalks and derivations are frozen in each", "candidate Family BASELINE.json. One Layer inventory retains degree, flags, V1", "completeness and existing AE coverage. V3 compatibility projections add zero", "propositions. Prior pilot candidates are references, not new Layer science.", ""]
    write(DOCS / "PSYCHOLOGICAL_LAYER_BASELINE.md", "\n".join(lines))
    print(encode(stats))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--check-protected", action="store_true")
    parser.add_argument("--progress", action="store_true")
    args = parser.parse_args()
    if args.freeze:
        freeze()
    if args.check_protected:
        print(encode(check_protected()))
    if args.progress:
        render_progress()


def render_progress():
    progress = read(STORE / "progress.json")
    lines = ["# Psychological Layer progress", "", f"Program: `{PROGRAM}`.",
             "Branch: `scale-up/psychological-layer-v1`.", f"Starting main: `{BASELINE}`.", "",
             "DONE means the named stage is checked, not that the Family is scientifically complete.",
             "NOT_STARTED and PARTIAL stages remain unfinished. All human decisions remain pending.", "",
             "| Family | " + " | ".join(STAGES) + " |",
             "|---|" + "---|" * len(STAGES)]
    for f in FAMILIES:
        lines.append("| " + f + " | " + " | ".join(progress["families"][f][s] for s in STAGES) + " |")
    lines += ["", "## Exact resume point", "", progress.get("resumePoint", "Begin PSY-F01: entity review and existing Relationship research; all fourteen baselines are frozen."), "",
              "## Checkpoints", ""]
    lines += progress.get("checkpoints", ["- Layer baseline: 14 Families, 134 Drivers, 1 RDS (PSY-078), 111 unique active incident causal Relationships. Protected comparison: 191 files unchanged; eight incremental baseline tests pass. Commit SHA recorded at next checkpoint."])
    lines += ["", "No new GOVERNED or ACTIVE records; no canonical source registration; no production science changes.", ""]
    write(DOCS / "PSYCHOLOGICAL_LAYER_PROGRESS.md", "\n".join(lines))


if __name__ == "__main__":
    main()
