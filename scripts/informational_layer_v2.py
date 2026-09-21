"""Deterministic baseline and validation helpers for the candidate-only INF audit."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_family

DATA = ROOT / "data/candidates/actions-events-v1/INFORMATIONAL_LAYER"
DOCS = ROOT / "docs/governance/scale-up/INFORMATIONAL_LAYER"
BASE_COMMIT = "236b9c6bd0642a4704f3a845454846bb13a09def"
PROGRAM_ID = "AUD-INFORMATIONAL-LAYER-AE-V1-20260920-001"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def protection() -> dict[str, str]:
    paths = (
        "data/entities.json", "data/families.json", "data/relationships.json",
        "data/relationship-intervention-v1/relationships.json",
        "data/relationship-intervention-v1/evidence-assessments.json",
        "data/relationship-intervention-v1/source-register.json",
        "data/actions-events-v1/catalog.json", "data/relational-state-v1/catalog.json",
    )
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}


def baseline() -> dict:
    inv = audit_family.inventory()
    rows = read(ROOT / "data/entities.json")
    entities = {row["id"]: row for row in rows if row["layer"] == "Informational"}
    summarized = {row["id"]: row for row in inv["entities"]}
    families = [row for row in read(ROOT / "data/families.json")["families"] if row["layer"] == "Informational"]
    legacy = {row["id"]: row for row in read(ROOT / "data/relationships.json")["relationships"]}
    native = {row["id"]: row for row in read(ROOT / "data/relationship-intervention-v1/relationships.json")["relationships"]}
    edges = [row for row in inv["edges"] if row["source"] in entities or row["target"] in entities]
    relationships = []
    for edge in edges:
        source, target = summarized[edge["source"]], summarized[edge["target"]]
        source_in, target_in = edge["source"] in entities, edge["target"] in entities
        scope = ("WITHIN_FAMILY" if source_in and target_in and source["familyId"] == target["familyId"]
                 else "SAME_LAYER_CROSS_FAMILY" if source_in and target_in else "CROSS_LAYER_INCOMING" if target_in else "CROSS_LAYER_OUTGOING")
        relationships.append({
            "id": edge["id"], "edge": edge, "frozenRecord": legacy.get(edge["id"]) or native[edge["id"]],
            "scope": scope, "ownerFamilyId": source["familyId"] if source_in else target["familyId"],
            "consultedFamilyIds": sorted({source["familyId"], target["familyId"]} - {source["familyId"] if source_in else target["familyId"]}),
            "v1IncompleteFields": inv["projectionIncompleteFields"].get(edge["id"], []),
        })
    pilot = read(ROOT / "data/candidates/actions-events-v1/INF-F03/workspace.json")
    pilot_queue = read(ROOT / "data/candidates/actions-events-v1/INF-F03/source-registration-queue.json")
    return {
        "schemaVersion": "1.0.0", "programId": PROGRAM_ID, "class": "FROZEN_CANDIDATE_AUDIT_BASELINE",
        "baseCommit": BASE_COMMIT, "productionHashes": protection(),
        "families": sorted(families, key=lambda x: x["id"]),
        "entities": [{"frozenRecord": entities[k], "mechanical": summarized[k]} for k in sorted(entities)],
        "incidentRelationships": sorted(relationships, key=lambda x: x["id"]),
        "pilot": {"familyId": "INF-F03", "baselineCommit": pilot.get("baselineCommit"),
                  "existingAuditIds": sorted({x["currentRecord"]["id"] for x in read(ROOT / "data/candidates/actions-events-v1/INF-F03/existing-relationship-audit.json")}),
                  "sourceQueue": pilot_queue, "blockerId": "HYP-INF-F03-H20"},
    }


def init() -> None:
    value = baseline()
    write(DATA / "baseline.json", value)
    write(DATA / "protected-baseline.json", {"baseCommit": BASE_COMMIT, "productionHashes": value["productionHashes"]})
    for filename, content in {
        "relationship-review-registry.json": {}, "candidate-proposition-registry.json": {},
        "cross-family-issues.json": [], "actions-events-identity-registry.json": {},
        "candidate-source-registry.json": {}, "source-overlap-registry.json": [],
        "architecture-escalations.json": [], "astra-escalation-queue.json": [],
        "negative-coverage-registry.json": {}, "deep-research-ledger.json": [],
        "source-findings.json": [], "evidence-assessments.json": [],
    }.items():
        path = DATA / filename
        if not path.exists():
            write(path, content)
    write(DATA / "progress.json", {"programId": PROGRAM_ID, "baseCommit": BASE_COMMIT,
         "families": {row["id"]: "BASELINE" for row in value["families"]}})


def validate_protection() -> None:
    expected = read(DATA / "protected-baseline.json")["productionHashes"]
    assert protection() == expected, "Pre-existing production scientific data changed"


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["init", "validate"])
    args = parser.parse_args()
    if args.command == "init":
        init()
    else:
        validate_protection()
