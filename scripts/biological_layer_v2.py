"""Deterministic, candidate-only Biological Layer V2 inventory and validation."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import audit_family

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/candidates/actions-events-v1/BIOLOGICAL_LAYER"
DOCS = ROOT / "docs/governance/scale-up/BIOLOGICAL_LAYER"
BASE_COMMIT = "85645e46b8c61b883ba5cf91674e6ffcbb90fb7b"
PROGRAM_ID = "AUD-BIOLOGICAL-LAYER-AE-V1-20260920-001"
PROTECTED = (
    "data/entities.json", "data/families.json", "data/relationships.json",
    "data/relationship-intervention-v1/relationships.json",
    "data/relationship-intervention-v1/evidence-assessments.json",
    "data/relationship-intervention-v1/interventions.json",
    "data/relationship-intervention-v1/intervention-effects.json",
    "data/relationship-intervention-v1/source-register.json",
    "data/actions-events-v1/catalog.json", "data/relational-state-v1/catalog.json",
)


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_doc(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def hashes() -> dict[str, str]:
    return {path: hashlib.sha256((ROOT / path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
            for path in PROTECTED}


def baseline() -> dict:
    inventory = audit_family.inventory()
    raw_entities = {row["id"]: row for row in read(ROOT / "data/entities.json") if row["layer"] == "Biological"}
    entities = {row["id"]: row for row in inventory["entities"]}
    families = [row for row in read(ROOT / "data/families.json")["families"] if row["layer"] == "Biological"]
    legacy = {row["id"]: row for row in read(ROOT / "data/relationships.json")["relationships"]}
    native = {row["id"]: row for row in read(ROOT / "data/relationship-intervention-v1/relationships.json")["relationships"]}
    relationships = []
    for edge in inventory["edges"]:
        source_in, target_in = edge["source"] in raw_entities, edge["target"] in raw_entities
        if not (source_in or target_in):
            continue
        source, target = entities[edge["source"]], entities[edge["target"]]
        scope = ("WITHIN_FAMILY" if source_in and target_in and source["familyId"] == target["familyId"]
                 else "SAME_LAYER_CROSS_FAMILY" if source_in and target_in else "CROSS_LAYER_INCOMING" if target_in else "CROSS_LAYER_OUTGOING")
        owner = source["familyId"] if source_in else target["familyId"]
        relationships.append({
            "id": edge["id"], "edge": edge, "frozenRecord": legacy.get(edge["id"]) or native[edge["id"]],
            "scope": scope, "ownerFamilyId": owner,
            "consultedFamilyIds": sorted({source["familyId"], target["familyId"]} - {owner}),
            "v1IncompleteFields": inventory["projectionIncompleteFields"].get(edge["id"], []),
        })
    causal = [x for x in relationships if x["edge"]["semanticType"] == "CAUSAL"]
    incident_ids = {x["edge"]["source"] for x in causal} | {x["edge"]["target"] for x in causal}
    return {
        "schemaVersion": "1.0.0", "programId": PROGRAM_ID,
        "class": "FROZEN_CANDIDATE_AUDIT_BASELINE", "baseCommit": BASE_COMMIT,
        "hashNormalization": "CRLF_TO_LF", "productionHashes": hashes(),
        "families": sorted(families, key=lambda x: x["id"]),
        "entities": [{"frozenRecord": raw_entities[k], "mechanical": entities[k]} for k in sorted(raw_entities)],
        "incidentRelationships": sorted(relationships, key=lambda x: x["id"]),
        "mechanicalCounts": {
            "families": len(families), "drivers": sum(x["entityType"] == "DRIVER" for x in raw_entities.values()),
            "rds": sum(x["entityType"] != "DRIVER" for x in raw_entities.values()),
            "entities": len(raw_entities), "incidentRelationships": len(relationships),
            "causalRelationships": len(causal), "causalScope": dict(sorted(Counter(x["scope"] for x in causal).items())),
            "causalIsolates": len(set(raw_entities) - incident_ids),
            "rdsCausalSources": sorted({x["edge"]["source"] for x in causal if raw_entities.get(x["edge"]["source"], {}).get("entityType") == "RELATIONAL_DERIVED_STATE"}),
            "incidentCausalV1Incomplete": sum(bool(x["v1IncompleteFields"]) for x in causal),
            "blockedEntities": sum(bool(x["frozenRecord"].get("blockedFields")) for x in [{"frozenRecord": row} for row in raw_entities.values()]),
        },
        "pilot": {"familyId": "BIO-F01", "governanceDecision": "GOV-BIO-F01-001-2026-09-05",
                  "governanceDocument": "docs/governance/pilots/BIO-F01/BIO_F01_GOVERNANCE_DECISION_001.md",
                  "revisionProposalIds": [f"REL-REV-BIO-F01-B{i:02d}" for i in range(1, 6)]},
    }


def validate_protection() -> None:
    expected = read(DATA / "protected-baseline.json")["productionHashes"]
    actual = hashes()
    assert expected == actual, "Biological candidate audit changed protected production science"


def init() -> None:
    if (DATA / "baseline.json").exists():
        raise ValueError("Biological baseline already frozen; do not refreeze")
    value = baseline()
    write(DATA / "baseline.json", value)
    write(DATA / "protected-baseline.json", {"baseCommit": BASE_COMMIT, "hashNormalization": "CRLF_TO_LF", "productionHashes": value["productionHashes"]})
    empty = {
        "relationship-review-registry.json": {}, "candidate-proposition-registry.json": {},
        "cross-family-issues.json": [], "cross-layer-findings.json": [],
        "actions-events-identity-registry.json": {}, "actions-events-hypotheses.json": [],
        "candidate-source-registry.json": {}, "source-overlap-registry.json": [],
        "architecture-escalations.json": [], "astra-escalation-queue.json": [],
        "negative-coverage-registry.json": {}, "deep-research-ledger.json": [],
        "source-findings.json": [], "evidence-assessments.json": [],
        "rds-review.json": [], "triage-hypotheses.json": [],
        "family-landscapes.json": {"families": {}}, "governance-index.json": [],
        "governance-recommendations.json": {}, "resource-telemetry.json": {},
    }
    for name, contents in empty.items():
        write(DATA / name, contents)
    write(DATA / "progress.json", {"programId": PROGRAM_ID, "baseCommit": BASE_COMMIT,
        "families": {row["id"]: "BASELINE" for row in value["families"]}})
    c = value["mechanicalCounts"]
    write_doc(DOCS / "BIOLOGICAL_LAYER_PLAN.md", f"""# Biological Layer Scale-Up V2 plan

**ADVISORY — HUMAN DECISION REQUIRED. Candidate-only science; new GOVERNED = 0 and ACTIVE = 0.**

Program `{PROGRAM_ID}` freezes main `{BASE_COMMIT}`. All 14 Families receive membership, existing-edge, Driver and A&E coverage. BIO-F01 governed pilot science and B01–B05 review proposals are reused without revision. V2 proceeds through Family landscape, cheap triage, bounded deep research, structured evidence, skeptical pass, Layer reconciliation and governance compression. A Family need not yield a candidate. No production proposition, ontology, architecture, canonical source or activation state may change.

The structured Layer registries are authoritative. Checkpoints are committed after coherent Family groups. Hard construct/RDS questions enter the Astra escalation queue and remain blocked or research-needed while independent work continues.
""")
    write_doc(DOCS / "BIOLOGICAL_LAYER_PROGRESS.md", "# Biological Layer progress\n\n**ADVISORY — HUMAN DECISION REQUIRED. New GOVERNED = 0 and ACTIVE = 0.**\n\n" +
              f"Program `{PROGRAM_ID}`; frozen main `{BASE_COMMIT}`.\n\n" +
              "| Family | Stage |\n|---|---|\n" + "\n".join(f"| {row['id']} | BASELINE |" for row in value["families"]) + "\n")
    write_doc(DOCS / "BIOLOGICAL_LAYER_BASELINE.md", f"""# Biological Layer frozen baseline

**ADVISORY — HUMAN DECISION REQUIRED. No production science changed.**

Program `{PROGRAM_ID}`; source main `{BASE_COMMIT}`. The full object-level snapshot is `baseline.json`.

| Measure | Frozen count |
|---|---:|
| Families | {c['families']} |
| Drivers | {c['drivers']} |
| RDS | {c['rds']} |
| Entities | {c['entities']} |
| Incident Relationships | {c['incidentRelationships']} |
| Unique causal propositions | {c['causalRelationships']} |
| Causal isolates | {c['causalIsolates']} |

Causal scope: {c['causalScope']}. RDS causal sources: {c['rdsCausalSources']}. The prior BIO-F01 pilot is reused, not re-audited.
""")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["init", "validate"])
    args = parser.parse_args()
    init() if args.command == "init" else validate_protection()
