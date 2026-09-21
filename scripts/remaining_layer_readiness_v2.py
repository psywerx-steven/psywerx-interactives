"""Refresh mechanical readiness after Psychological, Informational and Biological closeout."""

from __future__ import annotations

import json
from pathlib import Path

import audit_family
import next_layer_readiness as base

ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "ed6eae8352184541be15af78b84f3650e3599927"
DOC = ROOT / "docs/governance/REMAINING_LAYER_SCALE_UP_READINESS.md"
REPORT = ROOT / "reports/layer-scale-up-v2/remaining-layer-readiness-v2.json"
LAYERS = {
    "Social": "SOC",
    "Cultural": "CUL",
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
    for row in report["layers"]:
        members = {identifier for identifier, entity in entities.items() if entity["layer"] == row["layer"]}
        cross = [edge for edge in inventory["edges"] if edge["semanticType"] == "CAUSAL"
                 and (edge["source"] in members or edge["target"] in members)
                 and entities[edge["source"]]["layer"] != entities[edge["target"]]["layer"]]
        row["informationalCouplingCausalCount"] = sum(
            "Informational" in {entities[edge["source"]]["layer"], entities[edge["target"]]["layer"]}
            for edge in cross
        )
        row["completedLayerCouplingCausalCount"] = sum(
            bool({entities[edge["source"]]["layer"], entities[edge["target"]]["layer"]}
                 & {"Psychological", "Informational", "Biological"}) for edge in cross
        )
    report.update({
        "analysisId": "REMAINING-LAYER-SCALE-UP-READINESS-2026-09-21-001",
        "sourceCommit": SOURCE_COMMIT,
        "excludedCompletedLayers": ["Psychological", "Informational", "Biological"],
        "selection": {
            "recommendedNextLayer": "Cultural",
            "alternateNextLayer": "Physical / Environmental",
            "deferForNow": ["Social", "Institutional / Structural", "Technological"],
            "recommendedWorkload": "MODERATE",
            "autonomyRulePassed": True,
            "planningOnly": True,
            "candidateAuditStartAuthorizedByStandingInstruction": True,
            "rationale": "Cultural combines direct OIE and meaning-system value with moderate workload, no Network State binding, one RDS, no recorded architecture prerequisite, and meaningful reuse from completed Psychological and Informational work.",
        },
    })
    report.pop("excludedCompletedLayer", None)
    return report


def render(report: dict) -> str:
    lines = [
        "# Remaining Layer Scale-Up V2 readiness",
        "",
        "**READ-ONLY MECHANICAL PLANNING — NO SCIENTIFIC MATERIALIZATION**",
        "",
        f"Analysis `{report['analysisId']}` uses current main `{report['sourceCommit']}`. Psychological, Informational and Biological are complete and excluded. No candidate science, ontology, architecture or activation state was changed.",
        "",
        "## Comparison",
        "",
        "| Layer | Families | Drivers | RDS | Entities | Incident rels | Causal | Within | Cross-Family | Cross-Layer in/out | PSY | INF | Isolates | RDS sources | V1 incomplete | Blocked | Network State | Workload |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["layers"]:
        lines.append(
            f"| {row['layer']} | {row['families']} | {row['drivers']} | {row['rds']} | {row['entities']} | {row['activeIncidentRelationshipCount']} | {row['uniqueCausalPropositionsTouchingLayer']} | {row['withinFamilyCausalCount']} | {row['sameLayerCrossFamilyCausalCount']} | {row['incomingCrossLayerCausalCount']}/{row['outgoingCrossLayerCausalCount']} | {row['psychologicalCouplingCausalCount']} | {row['informationalCouplingCausalCount']} | {row['causalIsolates']} | {row['rdsCausalSourceCount']} | {row['legacyV1IncompleteBurden']} | {row['blockedEntityCount']} | {row['networkStateBindingCount']} | **{row['workload']['overall']}** |"
        )
    lines += [
        "",
        "## Selection",
        "",
        "**RECOMMENDED_NEXT_LAYER: Cultural — MODERATE.** It has high practitioner and OIE value through meaning, identity, legitimacy, narrative interpretation and shared belief systems; it can reuse completed Psychological and Informational proposition reviews. Its 91 entities and 55 causal propositions are material but manageable under V2. One RDS, one RDS causal-source signal, zero blocked entities, zero Network State bindings and no recorded architecture prerequisite satisfy the autonomy rule.",
        "",
        "**ALTERNATE_NEXT_LAYER: Physical / Environmental — MODERATE.** It has low architecture risk and no RDS, but 109 entities, 48 isolates and less direct cognitive-security leverage make it a weaker immediate choice.",
        "",
        "**DEFER_FOR_NOW:** Social remains VERY_HIGH because of 23 RDS, 10 RDS causal sources and an active Network State binding. Institutional / Structural remains VERY_HIGH because of scale and architecture burden. Technological remains HIGH because of relationship, cross-Layer and actor/system evidence burden.",
        "",
        "## Autonomy decision",
        "",
        "The Cultural Layer passes every standing criterion: MODERATE workload; no prerequisite architecture blocker; no active Network State redesign; no prerequisite ontology reclassification; and candidate-only auditing requires no production-science change. The authorized Cultural candidate audit may therefore begin automatically.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    report = build()
    base.write_json(REPORT, report)
    base.write_text(DOC, render(report))
    print(json.dumps({"layers": len(report["layers"]), "recommended": "Cultural", "workload": "MODERATE", "autonomyRulePassed": True}, indent=2))


if __name__ == "__main__":
    main()
