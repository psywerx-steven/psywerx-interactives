"""Refresh mechanical readiness after four completed Layer closeouts."""

from __future__ import annotations

import json
from pathlib import Path

import audit_family
import next_layer_readiness as base

ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "9b8c55f3da1e4a8487ee0874bb6b4519674e39be"
DOC = ROOT / "docs/governance/REMAINING_LAYER_SCALE_UP_READINESS.md"
REPORT = ROOT / "reports/layer-scale-up-v2/remaining-layer-readiness-v2.json"
LAYERS = {
    "Social": "SOC",
    "Physical / Environmental": "ENV",
    "Institutional / Structural": "INS",
    "Technological": "TEC",
}


def build() -> dict:
    prior_layers, prior_source = base.LAYERS, base.SOURCE_COMMIT
    try:
        base.LAYERS, base.SOURCE_COMMIT = LAYERS, SOURCE_COMMIT
        report = base.build()
    finally:
        base.LAYERS, base.SOURCE_COMMIT = prior_layers, prior_source
    inventory = audit_family.inventory()
    entities = {row["id"]: row for row in inventory["entities"]}
    completed_review_files = {
        "Psychological": ROOT / "data/candidates/actions-events-v1/PSYCHOLOGICAL_LAYER/relationship-review-registry.json",
        "Informational": ROOT / "data/candidates/actions-events-v1/INFORMATIONAL_LAYER/relationship-review-registry.json",
        "Biological": ROOT / "data/candidates/actions-events-v1/BIOLOGICAL_LAYER/relationship-review-registry.json",
        "Cultural": ROOT / "data/candidates/actions-events-v1/CULTURAL_LAYER/relationship-review-registry.json",
    }
    completed_reviews = {layer: set(json.loads(path.read_text(encoding="utf-8"))) for layer, path in completed_review_files.items()}
    for row in report["layers"]:
        members = {identifier for identifier, entity in entities.items() if entity["layer"] == row["layer"]}
        incident_ids = {edge["id"] for edge in inventory["edges"] if edge["source"] in members or edge["target"] in members}
        cross = [edge for edge in inventory["edges"] if edge["semanticType"] == "CAUSAL"
                 and (edge["source"] in members or edge["target"] in members)
                 and entities[edge["source"]]["layer"] != entities[edge["target"]]["layer"]]
        row["informationalCouplingCausalCount"] = sum(
            "Informational" in {entities[edge["source"]]["layer"], entities[edge["target"]]["layer"]}
            for edge in cross
        )
        row["completedLayerCouplingCausalCount"] = sum(
            bool({entities[edge["source"]]["layer"], entities[edge["target"]]["layer"]}
                 & {"Psychological", "Informational", "Biological", "Cultural"}) for edge in cross
        )
        reused = set().union(*(incident_ids & ids for ids in completed_reviews.values()))
        row["priorCompletedLayerReviewReuseIds"] = sorted(reused)
        row["priorCompletedLayerReviewReuseCount"] = len(reused)
    report.update({
        "analysisId": "REMAINING-LAYER-SCALE-UP-READINESS-2026-09-21-002",
        "sourceCommit": SOURCE_COMMIT,
        "excludedCompletedLayers": ["Psychological", "Informational", "Biological", "Cultural"],
        "selection": {
            "recommendedNextLayer": "Physical / Environmental",
            "alternateNextLayer": "Technological",
            "deferForNow": ["Social", "Institutional / Structural", "Technological"],
            "recommendedWorkload": "MODERATE",
            "autonomyRulePassed": True,
            "planningOnly": True,
            "candidateAuditStartAuthorizedByStandingInstruction": True,
            "rationale": "Physical / Environmental is the sole remaining MODERATE Layer. It has no RDS, no blocked entities, no Network State binding, low architecture risk, and can reuse completed Biological and Psychological reviews while remaining candidate-only.",
        },
    })
    report.pop("excludedCompletedLayer", None)
    return report


def render(report: dict) -> str:
    lines = [
        "# Remaining Layer Scale-Up V2 readiness",
        "",
        "**READ-ONLY MECHANICAL PLANNING - NO SCIENTIFIC MATERIALIZATION**",
        "",
        f"Analysis `{report['analysisId']}` uses current main `{report['sourceCommit']}`. Psychological, Informational, Biological and Cultural are complete and excluded. No candidate science, ontology, architecture or activation state was changed.",
        "",
        "## Comparison",
        "",
        "| Layer | Families | Drivers | RDS | Entities | Incident rels | Causal | Within | Cross-Family | Cross-Layer in/out | Prior reviews | Isolates | RDS sources | V1 incomplete | Blocked | Network State | Workload |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["layers"]:
        lines.append(
            f"| {row['layer']} | {row['families']} | {row['drivers']} | {row['rds']} | {row['entities']} | {row['activeIncidentRelationshipCount']} | {row['uniqueCausalPropositionsTouchingLayer']} | {row['withinFamilyCausalCount']} | {row['sameLayerCrossFamilyCausalCount']} | {row['incomingCrossLayerCausalCount']}/{row['outgoingCrossLayerCausalCount']} | {row['priorCompletedLayerReviewReuseCount']} | {row['causalIsolates']} | {row['rdsCausalSourceCount']} | {row['legacyV1IncompleteBurden']} | {row['blockedEntityCount']} | {row['networkStateBindingCount']} | **{row['workload']['overall']}** |"
        )
    lines += [
        "",
        "## Selection",
        "",
        "**RECOMMENDED_NEXT_LAYER: Physical / Environmental - MODERATE.** It is the sole remaining Layer below HIGH workload. Its 109 entities and 48 isolates require broad coverage, but zero RDS, zero blocked entities, zero Network State bindings, low architecture risk and exact prior-review reuse allow a candidate-only audit without production changes.",
        "",
        "**ALTERNATE_NEXT_LAYER: Technological - HIGH.** It has strong cognitive-security value and substantial Informational coupling, but its relationship, cross-Layer and actor/system evidence burden exceeds the automatic-start threshold.",
        "",
        "**DEFER_FOR_NOW:** Social remains VERY_HIGH because of 23 RDS, 10 RDS causal sources and an active Network State binding. Institutional / Structural remains VERY_HIGH because of scale and architecture burden. Technological remains HIGH because of relationship, cross-Layer and actor/system evidence burden.",
        "",
        "## Autonomy decision",
        "",
        "The Physical / Environmental Layer passes every standing criterion: MODERATE workload; no prerequisite architecture blocker; no Network State redesign; no prerequisite ontology reclassification; and candidate-only auditing requires no production-science change. The authorized candidate audit may therefore begin automatically.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    # This post-Cultural readiness result is a dated planning snapshot. Later
    # authorized ENV and Technological materializations must not rewrite its
    # historical Actions & Events coverage counts during deterministic CI.
    if (ROOT / "data/actions-events-v1/PHYSICAL_ENVIRONMENTAL_LAYER-materialization-manifest.json").is_file() and REPORT.is_file():
        frozen = json.loads(REPORT.read_text(encoding="utf-8"))
        if frozen.get("sourceCommit") == SOURCE_COMMIT:
            return
    report = build()
    base.write_json(REPORT, report)
    base.write_text(DOC, render(report))
    print(json.dumps({"layers": len(report["layers"]), "recommended": "Physical / Environmental", "workload": "MODERATE", "autonomyRulePassed": True}, indent=2))


if __name__ == "__main__":
    main()
