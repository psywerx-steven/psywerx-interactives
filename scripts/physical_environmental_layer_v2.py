"""Deterministic, candidate-only Physical / Environmental Layer V2 inventory."""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

import audit_family

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/candidates/actions-events-v1/PHYSICAL_ENVIRONMENTAL_LAYER"
DOCS = ROOT / "docs/governance/scale-up/PHYSICAL_ENVIRONMENTAL_LAYER"
BASE_COMMIT = "f75d99b326d9065c1e97ba89a3d5e395d52c0bb0"
PROGRAM_ID = "AUD-PHYSICAL-ENVIRONMENTAL-LAYER-AE-V1-20260921-001"
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
    return {path: hashlib.sha256((ROOT / path).read_bytes().replace(b"\r\n", b"\n")).hexdigest() for path in PROTECTED}


def baseline() -> dict:
    inventory = audit_family.inventory()
    raw = {row["id"]: row for row in read(ROOT / "data/entities.json") if row["layer"] == "Physical / Environmental"}
    mechanical = {row["id"]: row for row in inventory["entities"]}
    families = [row for row in read(ROOT / "data/families.json")["families"] if row["layer"] == "Physical / Environmental"]
    legacy = {row["id"]: row for row in read(ROOT / "data/relationships.json")["relationships"]}
    native = {row["id"]: row for row in read(ROOT / "data/relationship-intervention-v1/relationships.json")["relationships"]}
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
        relationships.append({"id":edge["id"], "edge":edge, "frozenRecord":legacy.get(edge["id"]) or native[edge["id"]],
            "scope":scope, "ownerFamilyId":owner,
            "consultedFamilyIds":sorted({source["familyId"],target["familyId"]}-{owner}),
            "v1IncompleteFields":inventory["projectionIncompleteFields"].get(edge["id"],[])})
    causal = [x for x in relationships if x["edge"]["semanticType"] == "CAUSAL"]
    incident = {x["edge"]["source"] for x in causal} | {x["edge"]["target"] for x in causal}
    return {"schemaVersion":"1.0.0","programId":PROGRAM_ID,"class":"FROZEN_CANDIDATE_AUDIT_BASELINE",
        "baseCommit":BASE_COMMIT,"hashNormalization":"CRLF_TO_LF","productionHashes":hashes(),
        "families":sorted(families,key=lambda x:x["id"]),
        "entities":[{"frozenRecord":raw[k],"mechanical":mechanical[k]} for k in sorted(raw)],
        "incidentRelationships":sorted(relationships,key=lambda x:x["id"]),
        "mechanicalCounts":{"families":len(families),"drivers":sum(x["entityType"]=="DRIVER" for x in raw.values()),
            "rds":sum(x["entityType"]!="DRIVER" for x in raw.values()),"entities":len(raw),
            "incidentRelationships":len(relationships),"causalRelationships":len(causal),
            "causalScope":dict(sorted(Counter(x["scope"] for x in causal).items())),
            "causalIsolates":len(set(raw)-incident),"rdsCausalSources":[],
            "incidentCausalV1Incomplete":sum(bool(x["v1IncompleteFields"]) for x in causal),
            "blockedEntities":sum(bool(x.get("blockedFields")) for x in raw.values())}}


def validate_protection() -> None:
    expected = read(DATA / "protected-baseline.json")["productionHashes"]
    actual = hashes()
    for path, digest in expected.items():
        if actual[path] == digest:
            continue
        assert path in {"data/relationship-intervention-v1/source-register.json", "data/actions-events-v1/catalog.json"}, f"Pre-existing production scientific data changed: {path}"
        old = json.loads(subprocess.check_output(["git", "show", f"{BASE_COMMIT}:{path}"], cwd=ROOT))
        new = read(ROOT / path)
        if path.endswith("source-register.json"):
            identifiers = {"SRC-609", "SRC-610", "SRC-611", "SRC-612"}
            assert {x["id"] for x in new["sources"]} - {x["id"] for x in old["sources"]} == identifiers, path
            assert [x for x in new["sources"] if x["id"] not in identifiers] == old["sources"], path
            continue
        expected_additions = {
            "happeningTypes": {"HT-V1-ENV-LAYER-001"},
            "effectAssertions": {"EA-V1-ENV-LAYER-001"},
            "evidenceAssessments": {"EVA-AE-V1-ENV-LAYER-001"},
        }
        for key, identifiers in expected_additions.items():
            assert {x["id"] for x in new[key]} - {x["id"] for x in old[key]} == identifiers, (path, key)
            assert [x for x in new[key] if x["id"] not in identifiers] == old[key], (path, key)
        for key in old:
            if key in expected_additions:
                continue
            if key == "authorizations":
                assert new[key][:-1] == old[key], path
                assert new[key][-1]["decisionId"] == "GOV-PHYSICAL-ENVIRONMENTAL-LAYER-001-2026-09-21", path
            else:
                assert new[key] == old[key], (path, key)


def init() -> None:
    if (DATA / "baseline.json").exists():
        raise ValueError("Physical / Environmental baseline already frozen")
    value = baseline()
    write(DATA / "baseline.json", value)
    write(DATA / "protected-baseline.json", {"baseCommit":BASE_COMMIT,"hashNormalization":"CRLF_TO_LF","productionHashes":value["productionHashes"]})
    empty = {"relationship-review-registry.json":{},"candidate-proposition-registry.json":{},"cross-family-issues.json":[],
        "cross-layer-findings.json":[],"actions-events-identity-registry.json":{},"actions-events-hypotheses.json":[],
        "candidate-source-registry.json":{},"source-overlap-registry.json":[],"architecture-escalations.json":[],
        "astra-escalation-queue.json":[],"negative-coverage-registry.json":{},"deep-research-ledger.json":[],
        "source-findings.json":[],"evidence-assessments.json":[],"rds-review.json":[],"triage-hypotheses.json":[],
        "skeptical-review.json":[],"family-landscapes.json":{"families":{}},"governance-index.json":[],
        "governance-recommendations.json":{},"resource-telemetry.json":{},"source-registration-recommendations.json":{}}
    for name,obj in empty.items(): write(DATA/name,obj)
    write(DATA/"progress.json",{"programId":PROGRAM_ID,"baseCommit":BASE_COMMIT,"families":{x["id"]:"BASELINE" for x in value["families"]}})
    c=value["mechanicalCounts"]
    write_doc(DOCS/"PHYSICAL_ENVIRONMENTAL_LAYER_PLAN.md",f"# Physical / Environmental Layer Scale-Up V2 plan\n\n**ADVISORY - HUMAN DECISION REQUIRED. Candidate-only science; new GOVERNED = 0 and ACTIVE = 0.**\n\nProgram `{PROGRAM_ID}` freezes main `{BASE_COMMIT}`. All 13 Families receive existing-edge, Driver, evidence and Actions & Events coverage. Deep research follows exact preliminary signal only. No production proposition, source, ontology, architecture or lifecycle state changes during the audit.\n")
    write_doc(DOCS/"PHYSICAL_ENVIRONMENTAL_LAYER_PROGRESS.md","# Physical / Environmental Layer progress\n\n**ADVISORY - HUMAN DECISION REQUIRED.**\n\n| Family | Stage |\n|---|---|\n"+"\n".join(f"| {x['id']} | BASELINE |" for x in value["families"])+"\n")
    write_doc(DOCS/"PHYSICAL_ENVIRONMENTAL_LAYER_BASELINE.md",f"# Physical / Environmental Layer frozen baseline\n\n**ADVISORY - HUMAN DECISION REQUIRED. No production science changed.**\n\nProgram `{PROGRAM_ID}`; source main `{BASE_COMMIT}`.\n\n| Measure | Count |\n|---|---:|\n| Families | {c['families']} |\n| Drivers | {c['drivers']} |\n| RDS | {c['rds']} |\n| Entities | {c['entities']} |\n| Incident Relationships | {c['incidentRelationships']} |\n| Causal propositions | {c['causalRelationships']} |\n| Causal isolates | {c['causalIsolates']} |\n\nCausal scope: {c['causalScope']}.\n")


if __name__ == "__main__":
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument("command",choices=["init","validate"]); args=parser.parse_args()
    init() if args.command=="init" else validate_protection()
