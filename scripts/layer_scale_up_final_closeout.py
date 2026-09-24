"""Build the deterministic eight-Layer completion checkpoint and unresolved backlog."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports/layer-scale-up-v2"
STATUS_DOC = ROOT / "docs/governance/LAYER_SCALE_UP_PROGRAM_STATUS.md"
COMPLETE_DOC = ROOT / "docs/governance/LAYER_SCALE_UP_FINAL_COMPLETENESS.md"
BACKLOG_DOC = ROOT / "docs/governance/POST_SCALE_UP_BLOCKER_BACKLOG.md"
CHECKPOINT_ID = "LAYER-SCALE-UP-FINAL-COMPLETENESS-2026-09-24-001"
SOURCE_BASE = "a2632555588ed34a0a5a7ebe7ed4e70e9df6f327"

LAYER_DIRS = {
    "Biological": "BIOLOGICAL_LAYER",
    "Psychological": "PSYCHOLOGICAL_LAYER",
    "Social": "SOCIAL_LAYER",
    "Cultural": "CULTURAL_LAYER",
    "Physical / Environmental": "PHYSICAL_ENVIRONMENTAL_LAYER",
    "Institutional / Structural": "INSTITUTIONAL_STRUCTURAL_LAYER",
    "Informational": "INFORMATIONAL_LAYER",
    "Technological": "TECHNOLOGICAL_LAYER",
}


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def write_text(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def item(identifier, category, layer, affected, science, architecture, safe, consequence, blocks, work):
    return {"id": identifier, "category": category, "layer": layer, "affectedRecords": affected,
            "scientificProblem": science, "architectureProblem": architecture, "currentSafeState": safe,
            "consequenceOfLeavingUnresolved": consequence, "blocksActiveExecution": blocks,
            "recommendedFutureWorkType": work}


def build_backlog():
    rows = [
        item("BLK-PSY-001", "A_RDS_DEFINITION_DERIVATION", "Psychological", ["PSY relational derived-state route"], "The target construct and derivation are not exact enough for governed causal use.", "Current target semantics cannot safely carry the proposed effect.", "Preserve governed records and blocker; no new causal use.", "The affected route remains unavailable to active consumers.", True, "DEDICATED_RDS_AND_TARGET_GOVERNANCE"),
        item("BLK-PSY-002", "F_CONSTRUCT_CLASSIFICATION_ONTOLOGY", "Psychological", ["PSY construct-classification route"], "A candidate cannot be classified without changing its scientific meaning.", "A classification decision would alter ontology semantics.", "Leave the candidate blocked and production unchanged.", "One candidate route remains unavailable.", True, "ONTOLOGY_GOVERNANCE"),
        item("BLK-PSY-003", "D_NETWORK_STATE_OR_CONTRIBUTION_REPRESENTATION", "Psychological", ["REL-V1-PSY-LAYER-001", "EA-V1-PSY-LAYER-001", "CONTRIB-PSY-LAYER-REPETITION-001"], "Relationship and EffectAssertion encode one repetition contribution.", "Active contribution deduplication is not defined.", "Keep both representations inactive and preserve shared lineage.", "The repetition contribution cannot activate safely.", True, "CONTRIBUTION_DEDUP_ARCHITECTURE"),
        item("HYP-INF-F03-H20", "F_CONSTRUCT_CLASSIFICATION_ONTOLOGY", "Informational", ["INF-013", "INF-077"], "Conceptual and surface-definition overlap cannot be resolved by selecting one measure.", "No governed identity, merge or feature-scope rule resolves the boundary.", "Preserve both definitions and blocked metadata.", "Dependent candidates remain research-needed or blocked.", True, "CONSTRUCT_BOUNDARY_GOVERNANCE"),
        item("ARCH-INF-LAYER-0001", "A_RDS_DEFINITION_DERIVATION", "Informational", ["7 Informational RDS"], "Portable derivations and constituent overlap remain incomplete for broader causal use.", "RDS causal-source semantics require dedicated review.", "No new RDS target, source authorization or Network State binding.", "Aggregate routes remain conservative and inactive.", True, "RDS_ARCHITECTURE_REVIEW"),
        item("META-INF-LAYER-0001", "G_SOURCE_GOVERNANCE", "Informational", ["11 INF-F03 source-queue rows"], "Candidate provenance includes unresolved work/version and source-identity rows.", "Canonical registration contract is not satisfied for every row.", "Keep the queue candidate-only and truthful.", "Some deferred candidates lack canonical provenance.", False, "SOURCE_IDENTITY_RESOLUTION"),
        item("BLK-BIO-RDS-001", "A_RDS_DEFINITION_DERIVATION", "Biological", ["BIO-F01 five RDS", "BIO-003"], "Exact versioned calculation and aggregation definitions are insufficient, especially for BIO-003 constituent overlap.", "Current RDS architecture cannot establish independent causal-source use.", "Keep RDS definitions and causal-source semantics unchanged.", "Broader Biological RDS execution remains blocked.", True, "RDS_DERIVATION_GOVERNANCE"),
        item("ASTRA-BIO-LAYER-001", "B_RDS_CAUSAL_SOURCE_INDEPENDENCE", "Biological", ["BIO-003 outgoing route"], "It is unresolved whether the source is independent of sleep-duration constituents.", "Aggregate contribution control is undefined.", "No new causal authorization.", "Potential double counting remains avoided by deferral.", True, "CAUSAL_SOURCE_ADJUDICATION"),
        item("BLK-CUL-RDS-001", "A_RDS_DEFINITION_DERIVATION", "Cultural", ["CUL-088", "REL-CUL-042", "CUL-061"], "Generational Cultural Distance lacks a governed metric, aggregation and reference window.", "RDS causal-source architecture is not versioned for this route.", "Keep REL-CUL-042 unchanged and the review disposition blocked.", "The distance route cannot support new active execution.", True, "RDS_METRIC_GOVERNANCE"),
        item("ASTRA-CUL-LAYER-001", "B_RDS_CAUSAL_SOURCE_INDEPENDENCE", "Cultural", ["CUL-088", "REL-CUL-042"], "Aggregate distance may share constituents with its target or contextual inputs.", "Independent aggregate causal semantics are unresolved.", "No causal-source authorization.", "Possible contextual effects remain unavailable.", True, "AGGREGATE_CAUSAL_REVIEW"),
        item("BLK-ENV-ACTIVATION-001", "E_MECHANISMSTATUS_ACTIVATION_CONTRACT", "Physical / Environmental", ["EVA-AE-V1-ENV-LAYER-001", "HT-V1-ENV-LAYER-001", "EA-V1-ENV-LAYER-001"], "The bounded natural-walk effect is supported, but the multisensory package does not identify a component mechanism.", "ACTIVE EffectAssertions currently require mechanismStatus other than UNKNOWN.", "Preserve the governed bundle inactive and mechanismStatus UNKNOWN.", "The bounded bundle cannot activate under the current contract.", True, "ACTIVATION_LIFECYCLE_GOVERNANCE"),
        item("BLK-TEC-ACTIVATION-001", "E_MECHANISMSTATUS_ACTIVATION_CONTRACT", "Technological", ["EVA-AE-V1-TEC-LAYER-001", "HT-V1-TEC-LAYER-001", "EA-V1-TEC-LAYER-001"], "The bounded AI-label effect does not identify a sufficiently exact mechanism across media and interface boundaries.", "ACTIVE EffectAssertions require a non-UNKNOWN mechanismStatus.", "Preserve the governed bundle inactive and scientific qualifiers intact.", "The Tech bundle cannot activate under the current contract.", True, "ACTIVATION_LIFECYCLE_GOVERNANCE"),
        item("BLK-TEC-METADATA-001", "F_CONSTRUCT_CLASSIFICATION_ONTOLOGY", "Technological", ["TEC-097", "TEC-098", "TEC-099"], "Blocked scientific metadata remains unresolved.", "Repair could imply an unauthorized construct or architecture decision.", "Preserve blocked fields.", "Dependent candidates remain unavailable.", True, "METADATA_AND_ONTOLOGY_GOVERNANCE"),
        item("HYP-SOC-F07-H12", "D_NETWORK_STATE_OR_CONTRIBUTION_REPRESENTATION", "Social", ["network adjacency", "degree RDS"], "Network rewiring changes adjacency and derived metrics but does not prove an empirical causal effect.", "No complete canonical adjacency-state Driver target exists.", "Use ScenarioStateDelta plus recalculation only.", "The proposed causal effect remains blocked.", True, "NETWORK_STATE_ARCHITECTURE"),
        item("HYP-SOC-F07-H20", "D_NETWORK_STATE_OR_CONTRIBUTION_REPRESENTATION", "Social", ["node deletion", "fragmentation RDS"], "Node deletion changes state and recalculates fragmentation.", "No ordinary Driver represents the node/boundary transformation.", "Preserve blocked derivation metadata and recalculation-only semantics.", "The proposed causal effect remains blocked.", True, "NETWORK_STATE_ARCHITECTURE"),
        item("ASTRA-SOC-LAYER-001", "B_RDS_CAUSAL_SOURCE_INDEPENDENCE", "Social", ["10 Social RDS causal sources"], "Independent aggregate mechanisms and constituent double counting remain unresolved.", "Current RDS source semantics do not encode contribution independence.", "Keep advisory dispositions and production unchanged.", "Ten aggregate-source routes need dedicated review before broader use.", True, "RDS_CAUSAL_SOURCE_PROGRAM"),
        item("ASTRA-SOC-LAYER-002", "C_CROSS_LEVEL_GROUP_PERSON_CAUSALITY", "Social", ["group-to-person Relationships"], "Group states do not automatically expose individual actors.", "No generic exposure mapping bridges group and person levels.", "Keep affected edges research-needed or review-only.", "Cross-level active execution remains scientifically constrained.", True, "CROSS_LEVEL_EXPOSURE_ARCHITECTURE"),
        item("ASTRA-SOC-LAYER-003", "D_NETWORK_STATE_OR_CONTRIBUTION_REPRESENTATION", "Social", ["HYP-SOC-F07-H12", "HYP-SOC-F07-H20", "DER-V1-SOC-F07-001"], "Adjacency and membership operations mix empirical interventions, state changes and metric recalculation.", "A future cross-level state object may be needed.", "Preserve the governed derivation inactive and recalculation-only.", "Some network operations cannot be represented as causal Effects.", True, "NETWORK_STATE_R_AND_D"),
        item("SRC-CAND-SOC-F07-010", "G_SOURCE_GOVERNANCE", "Social", ["HT-CAND-SOC-F07-008"], "A verified non-PubMed source binding lacks a satisfied canonical registration route.", "The source contract must preserve truthful non-PubMed provenance.", "Keep the candidate source queue intact.", "One candidate identity remains provenance-constrained.", False, "NON_PUBMED_SOURCE_REGISTRATION"),
        item("BLK-INS-METADATA-001", "F_CONSTRUCT_CLASSIFICATION_ONTOLOGY", "Institutional / Structural", ["INS-115", "INS-116"], "Scientific mechanism, time, observability, evidence and source fields remain blocked.", "Repair would require separate scientific governance.", "Keep both Drivers blocked and terminate dependent routes conservatively.", "No current incident edge is lost, but future materialization is blocked.", True, "DRIVER_METADATA_GOVERNANCE"),
        item("BLK-INS-RDS-001", "A_RDS_DEFINITION_DERIVATION", "Institutional / Structural", ["INS-039", "INS-103", "REL-INS-017", "REL-INS-036"], "The two causal-source RDS lack exact versioned inputs, aggregation and independent aggregate mechanisms.", "Current architecture cannot control constituent overlap safely.", "No new RDS definition, retype or causal-source authorization.", "Both aggregate-source routes remain blocked for future active use.", True, "RDS_DERIVATION_AND_CAUSAL_GOVERNANCE"),
        item("ASTRA-INS-LAYER-001", "B_RDS_CAUSAL_SOURCE_INDEPENDENCE", "Institutional / Structural", ["INS-039", "REL-INS-017", "INS-063"], "Caseload Pressure may summarize workload/staffing constituents that also define or cause capacity.", "Independent aggregate contribution is unresolved.", "Keep the edge unchanged and advisory review blocked.", "Potential double counting remains avoided by deferral.", True, "AGGREGATE_CAUSAL_ADJUDICATION"),
        item("ASTRA-INS-LAYER-002", "B_RDS_CAUSAL_SOURCE_INDEPENDENCE", "Institutional / Structural", ["INS-103", "REL-INS-036", "INS-107"], "Staffing Adequacy is a ratio whose independent effect on territorial reach is not established.", "Ratio constituents, unit and temporal order are not bound.", "Keep production unchanged and block new authorization.", "The route cannot be broadened or numerically executed.", True, "AGGREGATE_CAUSAL_ADJUDICATION"),
        item("ASTRA-INS-LAYER-003", "C_CROSS_LEVEL_GROUP_PERSON_CAUSALITY", "Institutional / Structural", ["20 Institutional cross-Layer causal propositions"], "Institution-level policies and procedures need explicit implementation and exposure routes before targeting person-level states.", "Current metadata lacks a generic cross-level bridge.", "Reuse prior conservative reviews; no new bridge or edge.", "Cross-level claims remain limited to existing governed scope.", True, "CROSS_LEVEL_EXPOSURE_ARCHITECTURE"),
    ]
    review_counts = {
        "Psychological": {"revision": 57, "retype": 5, "split": 2, "researchNeeded": 36},
        "Informational": {"revision": 12, "retype": 18, "split": 0, "researchNeeded": 16},
        "Biological": {"revision": 5, "retype": 0, "split": 0, "researchNeeded": 14},
        "Cultural": {"revision": 6, "retype": 5, "split": 0, "researchNeeded": 36},
        "Physical / Environmental": {"revision": 2, "retype": 4, "split": 0, "researchNeeded": 9},
        "Technological": {"revision": 3, "retype": 31, "split": 0, "researchNeeded": 22},
        "Social": {"revision": 7, "retype": 4, "split": 0, "researchNeeded": 30},
        "Institutional / Structural": {"revision": 8, "retype": 3, "split": 0, "researchNeeded": 26},
    }
    for layer_name, counts in review_counts.items():
        rows.append(item(
            "BACKLOG-REL-" + LAYER_DIRS[layer_name], "H_PRODUCTION_RELATIONSHIP_REVIEW_PROPOSALS", layer_name,
            [f"{counts['revision']} revision", f"{counts['retype']} retype", f"{counts['split']} split"],
            "Full-Layer review found bounded revision, retype or split proposals that remain advisory.",
            "No architecture change is implied until each proposition is separately governed.",
            "Keep every production Relationship unchanged.",
            "Known semantic debt remains visible without destabilizing production.", False, "RELATIONSHIP_PROPOSITION_GOVERNANCE"))
        rows.append(item(
            "BACKLOG-RN-" + LAYER_DIRS[layer_name], "I_CANDIDATE_SCIENCE_RESEARCH_NEEDED", layer_name,
            [f"{counts['researchNeeded']} existing Relationship reviews plus Layer candidate routes"],
            "Exact causal identification, target alignment, scope or evidence remains insufficient.",
            "No architecture decision is required merely to retain research-needed status.",
            "Keep candidate and advisory records non-governed or inactive as recorded.",
            "Potential science remains unavailable for new production use.", False, "TARGETED_EVIDENCE_RESEARCH"))
    rows.extend([
        item("INACTIVE-BIO-IDENTITY-001", "J_INACTIVE_GOVERNED_BUNDLES", "Biological", ["HT-V1-BIO-LAYER-001"], "A coherent caffeine-cessation identity has no governed eligible effect.", "No independent active meaning is required.", "GOVERNED / INACTIVE; KEEP_INACTIVE.", "Identity remains reusable for future evidence work.", False, "EFFECT_EVIDENCE_RESEARCH"),
        item("INACTIVE-INF-IDENTITY-001", "J_INACTIVE_GOVERNED_BUNDLES", "Informational", ["HT-V1-INF-LAYER-001"], "A reference-group prevalence-display identity has no governed eligible effect.", "No independent active meaning is required.", "GOVERNED / INACTIVE; KEEP_INACTIVE.", "Identity remains reusable for future evidence work.", False, "EFFECT_EVIDENCE_RESEARCH"),
        item("INACTIVE-ENV-BUNDLE-001", "J_INACTIVE_GOVERNED_BUNDLES", "Physical / Environmental", ["EVA-AE-V1-ENV-LAYER-001", "HT-V1-ENV-LAYER-001", "EA-V1-ENV-LAYER-001"], "Bounded evidence/effect bundle remains scientifically valid but activation-blocked.", "See BLK-ENV-ACTIVATION-001.", "GOVERNED / INACTIVE.", "No active production participation.", True, "ACTIVATION_CONTRACT_GOVERNANCE"),
        item("INACTIVE-TEC-BUNDLE-001", "J_INACTIVE_GOVERNED_BUNDLES", "Technological", ["EVA-AE-V1-TEC-LAYER-001", "HT-V1-TEC-LAYER-001", "EA-V1-TEC-LAYER-001"], "Bounded evidence/effect bundle remains scientifically valid but activation-blocked.", "See BLK-TEC-ACTIVATION-001.", "GOVERNED / INACTIVE.", "No active production participation.", True, "ACTIVATION_CONTRACT_GOVERNANCE"),
    ])
    return rows


def build():
    entities = read(ROOT / "data/entities.json")
    families = read(ROOT / "data/families.json")["families"]
    layer_rows = []
    status_detail = {
        "Biological": ("COMPLETE", "COMPLETE", "1 HT GOVERNED/INACTIVE", "KEEP_INACTIVE", "0", "BLK-BIO-RDS-001; ASTRA-BIO-LAYER-001"),
        "Psychological": ("COMPLETE", "COMPLETE", "1 Relationship, 29 HT, 7 EA, 8 EVA governed", "6 bundles ACTIVE", "18 records", "BLK-PSY-001/002/003; repetition contribution inactive"),
        "Social": ("COMPLETE", "COMPLETE", "NONE", "NOT REQUIRED", "0", "23 RDS; H12/H20; ASTRA-SOC-LAYER-001/002/003"),
        "Cultural": ("COMPLETE", "COMPLETE", "NONE", "NOT REQUIRED", "0", "BLK-CUL-RDS-001; ASTRA-CUL-LAYER-001"),
        "Physical / Environmental": ("COMPLETE", "COMPLETE", "1 HT / 1 EA / 1 EVA GOVERNED/INACTIVE", "BLOCKED", "0", "BLK-ENV-ACTIVATION-001"),
        "Institutional / Structural": ("COMPLETE", "COMPLETE", "NONE", "NOT REQUIRED", "0", "BLK-INS-METADATA-001; BLK-INS-RDS-001; three Astra questions"),
        "Informational": ("COMPLETE", "COMPLETE", "1 HT GOVERNED/INACTIVE", "KEEP_INACTIVE", "0", "HYP-INF-F03-H20; ARCH/META-INF-LAYER-0001"),
        "Technological": ("COMPLETE", "COMPLETE", "1 HT / 1 EA / 1 EVA GOVERNED/INACTIVE", "BLOCKED", "0", "BLK-TEC-ACTIVATION-001; TEC-097/098/099"),
    }
    for name, directory in LAYER_DIRS.items():
        members = [x for x in entities if x["layer"] == name]
        fs = [x for x in families if x["layer"] == name]
        audit_dir = ROOT / "data/candidates/actions-events-v1" / directory
        assert audit_dir.is_dir(), directory
        audit, governance, materialization, activation, active, blocker = status_detail[name]
        layer_rows.append({"layer": name, "families": len(fs), "drivers": sum(x["entityType"] == "DRIVER" for x in members),
            "rds": sum(x["entityType"] != "DRIVER" for x in members), "entities": len(members),
            "candidateAudit": audit, "humanGovernance": governance, "materialization": materialization,
            "activationStatus": activation, "newActiveScience": active, "majorUnresolvedBlocker": blocker})
    backlog = build_backlog()
    report = {"schemaVersion": "1.0.0", "checkpointId": CHECKPOINT_ID, "sourceBaseline": SOURCE_BASE,
              "layers": layer_rows, "totals": {"layers": len(layer_rows), "families": len(families),
              "drivers": sum(x["entityType"] == "DRIVER" for x in entities),
              "rds": sum(x["entityType"] != "DRIVER" for x in entities), "entities": len(entities)},
              "completedCandidateAudits": 8, "completedHumanGovernance": 8,
              "openCandidateLayerPRsAfterCloseout": 0, "productionScienceChangedByFinalCloseout": False}
    backlog_report = {"schemaVersion": "1.0.0", "checkpointId": CHECKPOINT_ID,
                      "items": backlog, "countsByCategory": dict(sorted(Counter(x["category"] for x in backlog).items())),
                      "blockingActiveExecutionCount": sum(x["blocksActiveExecution"] for x in backlog)}
    return report, backlog_report


def render_status(report):
    lines = ["# PSYWERX Layer Scale-Up program status", "", "**FINAL EIGHT-LAYER CHECKPOINT — PROCESS AND GOVERNANCE STATUS**", "",
             f"Checkpoint `{CHECKPOINT_ID}`. No scientific record is changed by this checkpoint.", "",
             "| Layer | Candidate audit | Human governance | Materialization | Activation status | New active science | Major unresolved blocker |",
             "|---|---|---|---|---|---|---|"]
    for row in report["layers"]:
        lines.append(f"| {row['layer']} | {row['candidateAudit']} | {row['humanGovernance']} | {row['materialization']} | {row['activationStatus']} | {row['newActiveScience']} | {row['majorUnresolvedBlocker']} |")
    lines += ["", "All eight full-Layer candidate audits and human-governance checkpoints are complete. The program covers 105 Families, 770 Drivers, 41 RDS and 811 entities. Remaining work is consolidated in `POST_SCALE_UP_BLOCKER_BACKLOG.md`; it is not resolved here."]
    return "\n".join(lines)


def render_completeness(report, backlog):
    lines = ["# Layer Scale-Up final completeness", "", "## Mechanical scope", "",
             "| Layer | Families | Drivers | RDS | Entities | Audit | Governance |",
             "|---|---:|---:|---:|---:|---|---|"]
    for row in report["layers"]:
        lines.append(f"| {row['layer']} | {row['families']} | {row['drivers']} | {row['rds']} | {row['entities']} | {row['candidateAudit']} | {row['humanGovernance']} |")
    t = report["totals"]
    lines += [f"| **Total** | **{t['families']}** | **{t['drivers']}** | **{t['rds']}** | **{t['entities']}** | **8 complete** | **8 complete** |", "",
              "## Completion finding", "", "All 105 Families and every current Driver/RDS are represented. All eight Layer packages contain a final audit state and governance state. The only full-Layer active additions are the six Psychological evidence-first bundles (18 records). ENV and Technological bundles remain governed/inactive and activation-blocked; Biological and Informational identity-only records remain governed/inactive. Social, Cultural and Institutional close with zero materialization.", "",
              f"The backlog contains {len(backlog['items'])} bounded items across {len(backlog['countsByCategory'])} required classes. This audit does not resolve any of them."]
    return "\n".join(lines)


def render_backlog(backlog):
    lines = ["# Post-Scale-Up blocker backlog", "", "This is the consolidated planning backlog after all eight full-Layer audits. It records safe current states and future work; it does not change science, architecture, ontology or activation.", "", "## Counts", "", "| Class | Items |", "|---|---:|"]
    for key, value in backlog["countsByCategory"].items():
        lines.append(f"| {key} | {value} |")
    lines += ["", "## Items", ""]
    for row in backlog["items"]:
        lines += [f"### {row['id']} — {row['layer']}", "", f"- Class: `{row['category']}`", f"- Affected records: {', '.join(row['affectedRecords'])}", f"- Scientific problem: {row['scientificProblem']}", f"- Architecture problem: {row['architectureProblem']}", f"- Current safe state: {row['currentSafeState']}", f"- Consequence if unresolved: {row['consequenceOfLeavingUnresolved']}", f"- Blocks active execution: **{'YES' if row['blocksActiveExecution'] else 'NO'}**", f"- Recommended future work: `{row['recommendedFutureWorkType']}`", ""]
    return "\n".join(lines)


def main():
    report, backlog = build()
    write_json(REPORTS / "layer-scale-up-program-status.json", report)
    write_json(REPORTS / "layer-scale-up-final-completeness.json", report)
    write_json(REPORTS / "post-scale-up-blocker-backlog.json", backlog)
    write_text(STATUS_DOC, render_status(report))
    write_text(COMPLETE_DOC, render_completeness(report, backlog))
    write_text(BACKLOG_DOC, render_backlog(backlog))
    print(json.dumps({"checkpointId": CHECKPOINT_ID, "layers": report["totals"]["layers"], "families": report["totals"]["families"], "backlogItems": len(backlog["items"])}, indent=2))


if __name__ == "__main__":
    main()
