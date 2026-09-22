"""Deterministic final Social / Institutional readiness and program checkpoint."""

from __future__ import annotations

import json
from pathlib import Path

import audit_family
import next_layer_readiness as readiness

ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "5513a3e352da1938e9fdefc6473a3864ccf552da"
ANALYSIS_ID = "FINAL-TWO-LAYER-READINESS-2026-09-22-001"
LAYERS = {"Social": "SOC", "Institutional / Structural": "INS"}
REPORT = ROOT / "reports/layer-scale-up-v2/final-two-layer-readiness.json"
DOC = ROOT / "docs/governance/FINAL_TWO_LAYER_READINESS.md"
STATUS_DOC = ROOT / "docs/governance/LAYER_SCALE_UP_PROGRAM_STATUS.md"
STATUS_REPORT = ROOT / "reports/layer-scale-up-v2/layer-scale-up-program-status.json"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def build_readiness() -> dict:
    prior_layers, prior_source = readiness.LAYERS, readiness.SOURCE_COMMIT
    try:
        readiness.LAYERS, readiness.SOURCE_COMMIT = LAYERS, SOURCE_COMMIT
        report = readiness.build()
    finally:
        readiness.LAYERS, readiness.SOURCE_COMMIT = prior_layers, prior_source

    inventory = audit_family.inventory()
    entities = {row["id"]: row for row in inventory["entities"]}
    review_files = sorted((ROOT / "data/candidates/actions-events-v1").glob("*_LAYER/relationship-review-registry.json"))
    completed_reviews = {path.parent.name: set(read(path)) for path in review_files}
    for row in report["layers"]:
        members = {identifier for identifier, entity in entities.items() if entity["layer"] == row["layer"]}
        incident_ids = {edge["id"] for edge in inventory["edges"] if edge["source"] in members or edge["target"] in members}
        cross = [
            edge for edge in inventory["edges"]
            if edge["semanticType"] == "CAUSAL"
            and (edge["source"] in members or edge["target"] in members)
            and entities[edge["source"]]["layer"] != entities[edge["target"]]["layer"]
        ]
        row["informationalCouplingCausalCount"] = sum(
            "Informational" in {entities[edge["source"]]["layer"], entities[edge["target"]]["layer"]}
            for edge in cross
        )
        row["technologicalCouplingCausalCount"] = sum(
            "Technological" in {entities[edge["source"]]["layer"], entities[edge["target"]]["layer"]}
            for edge in cross
        )
        reuse_by_layer = {name: len(incident_ids & ids) for name, ids in completed_reviews.items()}
        row["priorCompletedLayerReviewReuseByLayer"] = reuse_by_layer
        row["priorCompletedLayerReviewReuseCount"] = len(set().union(*(incident_ids & ids for ids in completed_reviews.values())))

    report.update({
        "analysisId": ANALYSIS_ID,
        "sourceCommit": SOURCE_COMMIT,
        "excludedCompletedLayers": [
            "Psychological", "Informational", "Biological", "Cultural",
            "Physical / Environmental", "Technological",
        ],
        "scienceResearchPerformed": False,
        "candidateGenerationPerformed": False,
        "productionScienceChanged": False,
        "selection": {
            "recommendedNextLayer": "Social",
            "finalLayer": "Institutional / Structural",
            "startAuthorized": False,
            "rationale": (
                "Social has the greater architecture burden but also the stronger immediate OIE leverage, "
                "13 Psychological couplings, five Technological couplings, 25 reusable completed-Layer reviews, "
                "and the SOC-F07 pilot. Auditing it next exposes Network State, aggregation, actual/perceived norm, "
                "and individual/group boundaries before the final institutional audit. Institutional / Structural "
                "then closes the program with the largest inventory and the broad policy/implementation and "
                "institution/person-level reconciliation burden."
            ),
        },
    })
    return report


def build_status() -> dict:
    rows = [
        {"layer": "Biological", "candidateAudit": "COMPLETE", "humanGovernance": "COMPLETE",
         "materialization": "1 HT GOVERNED/INACTIVE", "activationAudit": "KEEP_INACTIVE",
         "newActiveScience": "0", "majorBlocker": "ARCH-BIO-LAYER-0001 / BLK-BIO-RDS-001; ASTRA-BIO-LAYER-001"},
        {"layer": "Psychological", "candidateAudit": "COMPLETE", "humanGovernance": "COMPLETE",
         "materialization": "1 Relationship, 29 HT, 7 EA, 8 EVA governed", "activationAudit": "6 bundles activated",
         "newActiveScience": "18 records (6 HT / 6 EA / 6 EVA)", "majorBlocker": "BLK-PSY-001, BLK-PSY-002, BLK-PSY-003; repetition contribution inactive"},
        {"layer": "Social", "candidateAudit": "NOT_STARTED (SOC-F07 PILOT COMPLETE)", "humanGovernance": "FULL LAYER PENDING",
         "materialization": "Prior SOC-F07 pilot only", "activationAudit": "FULL LAYER PENDING",
         "newActiveScience": "No full-Layer additions", "majorBlocker": "23 RDS; 10 RDS sources; Network State binding; HYP-SOC-F07-H12/H20"},
        {"layer": "Cultural", "candidateAudit": "COMPLETE", "humanGovernance": "COMPLETE",
         "materialization": "NONE", "activationAudit": "NOT REQUIRED",
         "newActiveScience": "0", "majorBlocker": "ARCH-CUL-LAYER-0001 / BLK-CUL-RDS-001; ASTRA-CUL-LAYER-001"},
        {"layer": "Physical / Environmental", "candidateAudit": "COMPLETE", "humanGovernance": "COMPLETE",
         "materialization": "1 HT / 1 EA / 1 EVA GOVERNED/INACTIVE", "activationAudit": "BLOCKED",
         "newActiveScience": "0", "majorBlocker": "BLK-ENV-ACTIVATION-001; mechanismStatus UNKNOWN required by science"},
        {"layer": "Institutional / Structural", "candidateAudit": "NOT_STARTED", "humanGovernance": "PENDING",
         "materialization": "NONE", "activationAudit": "PENDING",
         "newActiveScience": "0", "majorBlocker": "4 RDS; multi-level policy/implementation and authority/legitimacy boundaries"},
        {"layer": "Informational", "candidateAudit": "COMPLETE", "humanGovernance": "COMPLETE",
         "materialization": "1 HT GOVERNED/INACTIVE", "activationAudit": "KEEP_INACTIVE",
         "newActiveScience": "0 from full-Layer closeout", "majorBlocker": "HYP-INF-F03-H20; ARCH/META-INF-LAYER-0001; ASTRA-INF-LAYER-001"},
        {"layer": "Technological", "candidateAudit": "COMPLETE", "humanGovernance": "COMPLETE",
         "materialization": "1 HT / 1 EA / 1 EVA GOVERNED/INACTIVE", "activationAudit": "BLOCKED",
         "newActiveScience": "0", "majorBlocker": "BLK-TEC-ACTIVATION-001; mechanismStatus UNKNOWN; TEC-097/098/099 metadata"},
    ]
    return {
        "schemaVersion": "1.0.0", "checkpointId": "LAYER-SCALE-UP-PROGRAM-STATUS-2026-09-22-001",
        "sourceCommit": SOURCE_COMMIT, "layers": rows,
        "completedCandidateAudits": 6, "fullLayerAuditsRemaining": ["Social", "Institutional / Structural"],
        "activationChangesInThisCloseout": 0,
    }


def render_readiness(report: dict) -> str:
    lines = [
        "# Final two-Layer Scale-Up V2 readiness",
        "",
        "**READ-ONLY MECHANICAL PLANNING - HUMAN LAYER-START DECISION REQUIRED**",
        "",
        f"Analysis `{ANALYSIS_ID}` uses main `{SOURCE_COMMIT}` after Technological governance and activation closeout. No literature research, candidate generation, scientific materialization, activation, ontology change, or architecture change was performed.",
        "",
        "## Mechanical comparison",
        "",
        "| Layer | Families | Drivers | RDS | Entities | Incident rels | Causal | Within | Cross-Family | Cross-Layer in/out | Isolates | RDS sources | V1 incomplete | Blocked | Network State | A&E HT gov/active | A&E EA gov/active | Prior reviews | Workload |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["layers"]:
        ae = row["actionsEventsCoverage"]
        lines.append(
            f"| {row['layer']} | {row['families']} | {row['drivers']} | {row['rds']} | {row['entities']} | "
            f"{row['activeIncidentRelationshipCount']} | {row['uniqueCausalPropositionsTouchingLayer']} | "
            f"{row['withinFamilyCausalCount']} | {row['sameLayerCrossFamilyCausalCount']} | "
            f"{row['incomingCrossLayerCausalCount']}/{row['outgoingCrossLayerCausalCount']} | {row['causalIsolates']} | "
            f"{row['rdsCausalSourceCount']} | {row['legacyV1IncompleteBurden']} | {row['blockedEntityCount']} | "
            f"{row['networkStateBindingCount']} | {ae['governedHappeningTypesWithOriginLayer']}/{ae['activeHappeningTypesWithOriginLayer']} | "
            f"{ae['governedEffectAssertionsTargetingLayer']}/{ae['activeEffectAssertionsTargetingLayer']} | "
            f"{row['priorCompletedLayerReviewReuseCount']} | **{row['workload']['overall']}** |"
        )
    social = next(x for x in report["layers"] if x["layer"] == "Social")
    institutional = next(x for x in report["layers"] if x["layer"] == "Institutional / Structural")
    lines += [
        "", "## Social readiness", "",
        f"Social has {social['rds']} RDS, {social['rdsCausalSourceCount']} RDS causal sources, {social['networkStateBindingCount']} Network State binding, {social['blockedEntityCount']} blocked entities, and {social['legacyV1IncompleteBurden']} V1-incomplete incident causal Relationships. SOC-F07 contributes {social['actionsEventsCoverage']['priorPilotCandidateRecords']} prior candidate records, one unresolved structured source-queue row, and blockers `HYP-SOC-F07-H12` and `HYP-SOC-F07-H20`. Actual versus perceived norms, node versus aggregate properties, group versus individual constructs, and constituent/aggregate double counting are mandatory review surfaces.",
        "", "## Institutional / Structural readiness", "",
        f"Institutional / Structural has the larger inventory ({institutional['entities']} entities), {institutional['rds']} RDS, {institutional['rdsCausalSourceCount']} RDS causal sources, {institutional['blockedEntityCount']} blocked entities, {institutional['causalIsolates']} isolates, and {institutional['legacyV1IncompleteBurden']} V1-incomplete incident causal Relationships. It has no current Network State binding and no structured pilot queue. Objective institution versus perceived institution, policy versus implementation, capacity versus experienced access, rule versus compliance, authority versus legitimacy, and institution-level versus person-level targets dominate the expected reconciliation burden.",
        "", "## Recommended sequence", "",
        "**RECOMMENDED_NEXT_LAYER: Social.** Its OIE value and leverage over completed Psychological, Informational, Cultural, Biological, and Technological reviews are highest. The SOC-F07 pilot supplies tested identity, source, RDS, and Network State infrastructure. Its greater architecture burden is also programmatically useful: resolving the scientific review surface around network topology, aggregation, norms, and group/person levels before Institutional work should expose shared representation questions early. This recommendation does not authorize starting the Layer or resolving those questions.",
        "",
        "**FINAL_LAYER: Institutional / Structural.** It closes the program with the largest remaining inventory and broadest policy/implementation and institution/person-level reconciliation burden. Deferring it until after Social allows any reusable network, aggregate, legitimacy, coordination, and multi-level governance lessons to be carried into the final audit.",
    ]
    return "\n".join(lines) + "\n"


def render_status(status: dict) -> str:
    lines = [
        "# PSYWERX Layer Scale-Up program status",
        "",
        "**PROGRAM CHECKPOINT - PROCESS AND GOVERNANCE STATUS ONLY**",
        "",
        f"Checkpoint `{status['checkpointId']}` uses main `{SOURCE_COMMIT}`. It does not alter scientific records.",
        "",
        "| Layer | Candidate audit | Human governance | Materialization | Activation audit | New active science | Major unresolved blocker |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in status["layers"]:
        lines.append(f"| {row['layer']} | {row['candidateAudit']} | {row['humanGovernance']} | {row['materialization']} | {row['activationAudit']} | {row['newActiveScience']} | {row['majorBlocker']} |")
    lines += [
        "", "Six full-Layer candidate audits are complete. Social and Institutional / Structural remain. ENV and Technological governed bundles remain inactive because the current ACTIVE contract requires non-UNKNOWN mechanism status; neither bounded effect is scientifically rejected.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    report, status = build_readiness(), build_status()
    write_json(REPORT, report)
    write_json(STATUS_REPORT, status)
    write_text(DOC, render_readiness(report))
    write_text(STATUS_DOC, render_status(status))
    print(json.dumps({"analysisId": ANALYSIS_ID, "next": "Social", "final": "Institutional / Structural", "scienceChanges": 0}, indent=2))


if __name__ == "__main__":
    main()
