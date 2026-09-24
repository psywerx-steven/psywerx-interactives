"""Deterministic, candidate-only Institutional / Structural Layer V2 inventory and protection gates."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import audit_family

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/candidates/actions-events-v1/INSTITUTIONAL_STRUCTURAL_LAYER"
DOCS = ROOT / "docs/governance/scale-up/INSTITUTIONAL_STRUCTURAL_LAYER"
BASE_COMMIT = "a2632555588ed34a0a5a7ebe7ed4e70e9df6f327"
PROGRAM_ID = "AUD-INSTITUTIONAL-STRUCTURAL-LAYER-AE-V1-20260923-001"
PROTECTED = (
    "data/entities.json", "data/drivers.json", "data/families.json",
    "data/aliases.json", "data/sources.json", "data/relationships.json",
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
    return {p: hashlib.sha256((ROOT / p).read_bytes().replace(b"\r\n", b"\n")).hexdigest() for p in PROTECTED}


def baseline() -> dict:
    inventory = audit_family.inventory()
    raw = {r["id"]: r for r in read(ROOT / "data/entities.json") if r["layer"] == "Institutional / Structural"}
    mechanical = {r["id"]: r for r in inventory["entities"]}
    families = [r for r in read(ROOT / "data/families.json")["families"] if r["layer"] == "Institutional / Structural"]
    legacy = {r["id"]: r for r in read(ROOT / "data/relationships.json")["relationships"]}
    native = {r["id"]: r for r in read(ROOT / "data/relationship-intervention-v1/relationships.json")["relationships"]}
    relationships = []
    for edge in inventory["edges"]:
        source_in, target_in = edge["source"] in raw, edge["target"] in raw
        if not (source_in or target_in):
            continue
        source, target = mechanical[edge["source"]], mechanical[edge["target"]]
        scope = ("WITHIN_FAMILY" if source_in and target_in and source["familyId"] == target["familyId"]
                 else "SAME_LAYER_CROSS_FAMILY" if source_in and target_in
                 else "CROSS_LAYER_INCOMING" if target_in else "CROSS_LAYER_OUTGOING")
        owner = source["familyId"] if source_in else target["familyId"]
        relationships.append({"id": edge["id"], "edge": edge,
            "frozenRecord": legacy.get(edge["id"]) or native[edge["id"]], "scope": scope,
            "ownerFamilyId": owner, "consultedFamilyIds": sorted({source["familyId"], target["familyId"]} - {owner}),
            "v1IncompleteFields": inventory["projectionIncompleteFields"].get(edge["id"], [])})
    causal = [r for r in relationships if r["edge"]["semanticType"] == "CAUSAL"]
    incident = {r["edge"]["source"] for r in causal} | {r["edge"]["target"] for r in causal}
    rds_sources = sorted({r["edge"]["source"] for r in causal
                          if r["edge"]["source"] in raw and raw[r["edge"]["source"]]["entityType"] != "DRIVER"})
    return {"schemaVersion": "1.0.0", "programId": PROGRAM_ID,
        "class": "FROZEN_CANDIDATE_AUDIT_BASELINE", "baseCommit": BASE_COMMIT,
        "hashNormalization": "CRLF_TO_LF", "productionHashes": hashes(),
        "families": sorted(families, key=lambda x: x["id"]),
        "entities": [{"frozenRecord": raw[k], "mechanical": mechanical[k]} for k in sorted(raw)],
        "incidentRelationships": sorted(relationships, key=lambda x: x["id"]),
        "mechanicalCounts": {"families": len(families),
            "drivers": sum(r["entityType"] == "DRIVER" for r in raw.values()),
            "rds": sum(r["entityType"] != "DRIVER" for r in raw.values()), "entities": len(raw),
            "incidentRelationships": len(relationships), "causalRelationships": len(causal),
            "causalScope": dict(sorted(Counter(r["scope"] for r in causal).items())),
            "causalIsolates": len(set(raw) - incident), "rdsCausalSources": rds_sources,
            "incidentCausalV1Incomplete": sum(bool(r["v1IncompleteFields"]) for r in causal),
            "blockedEntities": sum(bool(r.get("blockedFields")) for r in raw.values()),
            "networkStateBindings": 0}}


def validate_protection() -> None:
    expected = read(DATA / "protected-baseline.json")["productionHashes"]
    assert hashes() == expected, "Production science changed after Institutional / Structural baseline"


def init() -> None:
    if (DATA / "baseline.json").exists():
        raise ValueError("Institutional / Structural baseline already frozen")
    value = baseline()
    write(DATA / "baseline.json", value)
    write(DATA / "protected-baseline.json", {"baseCommit": BASE_COMMIT,
        "hashNormalization": "CRLF_TO_LF", "productionHashes": value["productionHashes"]})
    for name, obj in {
        "relationship-review-registry.json": {}, "candidate-proposition-registry.json": {},
        "cross-family-issues.json": [], "cross-layer-findings.json": [], "rds-review.json": [],
        "network-state-reconciliation.json": {}, "actions-events-identity-registry.json": {},
        "actions-events-hypotheses.json": [], "candidate-source-registry.json": {},
        "source-overlap-registry.json": [], "architecture-escalations.json": [],
        "astra-escalation-queue.json": [], "negative-coverage-registry.json": {},
        "deep-research-ledger.json": [], "source-findings.json": [], "evidence-assessments.json": [],
        "triage-hypotheses.json": [], "skeptical-review.json": [], "family-landscapes.json": {"families": {}},
        "governance-index.json": [], "governance-recommendations.json": {},
        "source-registration-recommendations.json": {}, "resource-telemetry.json": {},
    }.items():
        write(DATA / name, obj)
    write(DATA / "progress.json", {"programId": PROGRAM_ID, "baseCommit": BASE_COMMIT,
        "families": {r["id"]: "BASELINE" for r in value["families"]}})
    c = value["mechanicalCounts"]
    notice = "**ADVISORY — HUMAN DECISION REQUIRED. Candidate-only science; new GOVERNED = 0 and ACTIVE = 0.**"
    write_doc(DOCS / "INSTITUTIONAL_STRUCTURAL_LAYER_PLAN.md", f"# Institutional / Structural Layer Scale-Up V2 plan\n\n{notice}\n\nProgram `{PROGRAM_ID}` freezes main `{BASE_COMMIT}`. All 13 Families receive existing-edge, Driver, RDS, evidence, Network State and Actions & Events coverage. Deep research follows exact preliminary signal only. No production proposition, source, ontology, architecture or lifecycle state changes.\n")
    write_doc(DOCS / "INSTITUTIONAL_STRUCTURAL_LAYER_PROGRESS.md", "# Institutional / Structural Layer progress\n\n" + notice + "\n\n| Family | Stage |\n|---|---|\n" + "\n".join(f"| {r['id']} | BASELINE |" for r in value["families"]))
    write_doc(DOCS / "INSTITUTIONAL_STRUCTURAL_LAYER_BASELINE.md", f"# Institutional / Structural Layer frozen baseline\n\n{notice}\n\nProgram `{PROGRAM_ID}`; source main `{BASE_COMMIT}`.\n\n| Measure | Count |\n|---|---:|\n| Families | {c['families']} |\n| Drivers | {c['drivers']} |\n| RDS | {c['rds']} |\n| Entities | {c['entities']} |\n| Incident Relationships | {c['incidentRelationships']} |\n| Causal propositions | {c['causalRelationships']} |\n| Causal isolates | {c['causalIsolates']} |\n| RDS causal sources | {len(c['rdsCausalSources'])} |\n| V1-incomplete causal | {c['incidentCausalV1Incomplete']} |\n| Blocked entities | {c['blockedEntities']} |\n| Network State bindings | 0 |\n\nCausal scope: `{c['causalScope']}`.\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=["init", "validate"]); args = parser.parse_args()
    init() if args.command == "init" else validate_protection()
