"""Generate the read-only Layer Scale-Up V2 next-Layer readiness inventory."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import actions_events_v1 as ae
import audit_family


DOC = ROOT / "docs/governance/NEXT_LAYER_SCALE_UP_READINESS.md"
REPORT = ROOT / "reports/layer-scale-up-v2/next-layer-readiness.json"

LAYERS = {
    "Biological": "BIO",
    "Social": "SOC",
    "Cultural": "CUL",
    "Physical / Environmental": "ENV",
    "Institutional / Structural": "INS",
    "Informational": "INF",
    "Technological": "TEC",
}
PILOTS = {"BIO": "BIO-F01", "INF": "INF-F03", "SOC": "SOC-F07"}
LEVEL = {"LOW": 1, "MODERATE": 2, "HIGH": 3, "VERY_HIGH": 4}


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def threshold(value: int, low: int, moderate: int, high: int) -> str:
    if value <= low:
        return "LOW"
    if value <= moderate:
        return "MODERATE"
    if value <= high:
        return "HIGH"
    return "VERY_HIGH"


def candidate_workspace(prefix: str):
    path = ROOT / "data/candidates/actions-events-v1" / PILOTS.get(prefix, "") / "workspace.json"
    return read(path) if path.is_file() else None


def pilot_blockers(prefix: str) -> list[str]:
    workspace = candidate_workspace(prefix)
    if not workspace:
        return []
    blocked = []
    for value in workspace.get("passA", {}).values():
        if not isinstance(value, list):
            continue
        for row in value:
            if row.get("status") == "BLOCKED_NEEDS_GOVERNANCE_INPUT" or row.get("governance", {}).get("blockStatus") == "NEEDS_GOVERNANCE_INPUT":
                blocked.append(row["id"])
    return sorted(set(blocked))


def source_queue(prefix: str) -> tuple[str, int]:
    pilot = PILOTS.get(prefix)
    if not pilot:
        return "NO_STRUCTURED_PRIOR_PILOT_QUEUE", 0
    path = ROOT / "data/candidates/actions-events-v1" / pilot / "source-registration-queue.json"
    if not path.is_file():
        return "NO_STRUCTURED_PRIOR_PILOT_QUEUE", 0
    rows = read(path)
    unresolved = 0
    for row in rows:
        status = row.get("registrationStatus") or row.get("canonicalRegistration")
        if status in {"CANDIDATE_ONLY", "BLOCKED_PENDING_SOURCE_REGISTRATION_CONTRACT"}:
            unresolved += 1
    return "STRUCTURED_PRIOR_PILOT_QUEUE", unresolved


def workload(metrics: dict) -> dict:
    architecture_signal = (
        metrics["blockedEntityCount"]
        + 2 * metrics["rdsCausalSourceCount"]
        + metrics["knownArchitectureEscalationCount"]
        + 3 * metrics["networkStateBindingCount"]
    )
    search_signal = (
        metrics["entities"]
        + 3 * metrics["families"]
        + 2 * metrics["crossLayerCausalCount"]
        + metrics["causalIsolates"]
    )
    factors = {
        "entityVolume": threshold(metrics["entities"], 80, 100, 110),
        "existingRelationshipVolume": threshold(metrics["uniqueCausalPropositionsTouchingLayer"], 35, 55, 70),
        "crossLayerCoordination": threshold(metrics["crossLayerCausalCount"], 10, 15, 25),
        "rdsComplexity": threshold(metrics["rds"] + 2 * metrics["rdsCausalSourceCount"], 0, 4, 12),
        "constructBoundaryAmbiguity": threshold(metrics["blockedEntityCount"] + metrics["rds"], 1, 4, 9),
        "sourceEvidenceBurden": threshold(
        metrics["uniqueCausalPropositionsTouchingLayer"]
            + metrics["legacyV1IncompleteBurden"]
            + metrics["activeCausalWithoutStructuredEvidenceCount"]
            + metrics["unresolvedPilotSourceQueueCount"],
            75, 120, 170,
        ),
        "architectureRisk": threshold(architecture_signal, 0, 4, 9),
        "actionsEventsSearchComplexity": threshold(search_signal, 140, 180, 230),
    }
    average = sum(LEVEL[value] for value in factors.values()) / len(factors)
    overall = "LOW" if average <= 1.5 else "MODERATE" if average <= 2.25 else "HIGH" if average <= 3 else "VERY_HIGH"
    return {
        "factors": factors,
        "overall": overall,
        "observableSignals": {
            "architectureSignal": architecture_signal,
            "actionsEventsSearchSignal": search_signal,
            "averageOrdinal": round(average, 3),
        },
    }


def build() -> dict:
    inventory = audit_family.inventory()
    entities = {row["id"]: row for row in inventory["entities"]}
    catalog = read(ROOT / "data/actions-events-v1/catalog.json")
    all_effects = {row["id"]: row for row in catalog["effectAssertions"]}
    assessments = {row["id"]: row for row in catalog["evidenceAssessments"]}
    network = read(ROOT / "data/relational-state-v1/catalog.json")
    family_rows = inventory["families"]
    projection_incomplete = inventory["projectionIncompleteFields"]
    legacy_relationships = {row["id"]: row for row in read(ROOT / "data/relationships.json")["relationships"]}
    native_relationships = {row["id"]: row for row in read(ROOT / "data/relationship-intervention-v1/relationships.json")["relationships"]}

    rows = []
    for layer, prefix in LAYERS.items():
        members = {identifier for identifier, row in entities.items() if row["layer"] == layer}
        families = {row["familyId"] for row in entities.values() if row["layer"] == layer}
        active_incident = [edge for edge in inventory["edges"] if edge["source"] in members or edge["target"] in members]
        causal = [edge for edge in active_incident if edge["semanticType"] == "CAUSAL"]
        within = [edge for edge in causal if edge["source"] in members and edge["target"] in members and entities[edge["source"]]["familyId"] == entities[edge["target"]]["familyId"]]
        same_layer = [edge for edge in causal if edge["source"] in members and edge["target"] in members and entities[edge["source"]]["familyId"] != entities[edge["target"]]["familyId"]]
        cross = [edge for edge in causal if entities[edge["source"]]["layer"] != entities[edge["target"]]["layer"]]
        incoming = [edge for edge in cross if edge["target"] in members]
        outgoing = [edge for edge in cross if edge["source"] in members]
        psych = [edge for edge in cross if "Psychological" in {entities[edge["source"]]["layer"], entities[edge["target"]]["layer"]}]
        layer_entities = [row for row in entities.values() if row["layer"] == layer]
        rds_rows = [row for row in layer_entities if row["entityType"] != "DRIVER"]
        incomplete_legacy = {
            edge["id"] for edge in causal
            if edge["origin"] == "V3" and projection_incomplete.get(edge["id"])
        }
        missing_structured_evidence = {
            edge["id"] for edge in causal
            if not (
                legacy_relationships.get(edge["id"], {}).get("supportingEvidenceIds")
                or native_relationships.get(edge["id"], {}).get("evidenceAssessmentIds")
            )
        }
        blocked_entities = sum(bool(row["blockedFields"]) for row in layer_entities)
        rds_sources = sum("RDS_CAUSAL_SOURCE_REVIEW" in row["rdsFlags"] for row in rds_rows)
        network_bindings = sum(binding["targetRds"]["id"] in members for binding in network["bindings"])

        governed_types = [row for row in catalog["happeningTypes"] if prefix in row["originLayers"] and row["governance"]["lifecycleStatus"] == "GOVERNED"]
        governed_effects = [row for row in catalog["effectAssertions"] if prefix in row["targetLayers"] and row["governance"]["lifecycleStatus"] == "GOVERNED"]
        evidence_ids = {identifier for row in governed_effects for identifier in row["evidenceAssessmentIds"]}
        canonical_sources = {
            source_id for row in governed_types for source_id in row["identitySourceIds"]
        } | {
            finding["sourceId"] for identifier in evidence_ids for finding in assessments[identifier]["sourceFindings"]
        }
        queue_kind, unresolved_sources = source_queue(prefix)
        blockers = pilot_blockers(prefix)
        workspace = candidate_workspace(prefix)
        candidate_ae = 0
        if workspace:
            candidate_ae = sum(len(workspace["passB"][key]) for key in ("happeningTypes", "effectAssertions", "evidenceAssessments"))
        pilot = PILOTS.get(prefix)
        pilot_present = bool(pilot and (ROOT / "docs/governance/pilots" / pilot).is_dir())

        metrics = {
            "layer": layer,
            "prefix": prefix,
            "families": len(families),
            "drivers": sum(row["entityType"] == "DRIVER" for row in layer_entities),
            "rds": len(rds_rows),
            "entities": len(layer_entities),
            "activeIncidentRelationshipCount": len(active_incident),
            "uniqueCausalPropositionsTouchingLayer": len(causal),
            "withinFamilyCausalCount": len(within),
            "sameLayerCrossFamilyCausalCount": len(same_layer),
            "crossLayerCausalCount": len(cross),
            "incomingCrossLayerCausalCount": len(incoming),
            "outgoingCrossLayerCausalCount": len(outgoing),
            "psychologicalCouplingCausalCount": len(psych),
            "causalIsolates": sum(row["causalIsolated"] for row in layer_entities),
            "rdsCausalSourceCount": rds_sources,
            "blockedEntityCount": blocked_entities,
            "legacyV1IncompleteBurden": len(incomplete_legacy),
            "activeCausalWithoutStructuredEvidenceCount": len(missing_structured_evidence),
            "blockedOrIncompleteMetadataCount": blocked_entities + len(incomplete_legacy),
            "actionsEventsCoverage": {
                "governedHappeningTypesWithOriginLayer": len(governed_types),
                "activeHappeningTypesWithOriginLayer": sum(row["governance"]["activationStatus"] == "ACTIVE" for row in governed_types),
                "governedEffectAssertionsTargetingLayer": len(governed_effects),
                "activeEffectAssertionsTargetingLayer": sum(row["governance"]["activationStatus"] == "ACTIVE" for row in governed_effects),
                "priorPilotCandidateRecords": candidate_ae,
            },
            "priorPilotCoverage": [pilot] if pilot_present else [],
            "canonicalSourcesInGovernedActionsEventsCoverage": len(canonical_sources),
            "sourceGovernanceQueueBasis": queue_kind,
            "unresolvedPilotSourceQueueCount": unresolved_sources,
            "knownArchitectureEscalationIds": blockers,
            "knownArchitectureEscalationCount": len(blockers),
            "networkStateBindingCount": network_bindings,
            "networkStateRelevance": threshold(len(rds_rows) + 2 * rds_sources + 3 * network_bindings, 0, 4, 12),
        }
        metrics["workload"] = workload(metrics)
        rows.append(metrics)

    return {
        "schemaVersion": "1.0.0",
        "analysisId": "NEXT-LAYER-SCALE-UP-READINESS-2026-09-18-001",
        "analysisClass": "READ_ONLY_MECHANICAL_PLANNING",
        "sourceCommit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "workflow": "LAYER_SCALE_UP_V2",
        "excludedCompletedLayer": "Psychological",
        "scienceResearchPerformed": False,
        "candidateGenerationPerformed": False,
        "layers": rows,
        "selection": {
            "recommendedNextLayer": "Informational",
            "alternateNextLayer": "Biological",
            "deferForNow": ["Social", "Cultural", "Physical / Environmental", "Institutional / Structural", "Technological"],
            "planningOnly": True,
            "nextLayerStartAuthorized": False,
        },
        "metricDefinitions": {
            "activeIncidentRelationshipCount": "Unique active legacy/native Relationships of any semantic family with at least one endpoint in the Layer.",
            "uniqueCausalPropositionsTouchingLayer": "Unique active causal Relationships with at least one endpoint in the Layer; a cross-Layer edge is counted once within each touched Layer.",
            "causalIsolates": "Layer entities with zero active causal in-degree and out-degree.",
            "blockedOrIncompleteMetadataCount": "Blocked entities plus unique incident legacy causal Relationships whose V1 compatibility projection has incomplete fields.",
            "sourceGovernanceQueue": "Only unresolved rows in an existing structured prior-pilot source queue; zero with NO_STRUCTURED_PRIOR_PILOT_QUEUE means no recorded queue, not proof of no issue.",
            "architectureEscalations": "Only structured BLOCKED_NEEDS_GOVERNANCE_INPUT rows from an existing Actions & Events pilot; RDS and blocked-entity signals are reported separately.",
            "workload": "Ordinal proxy derived only from recorded counts; no token, credit, duration, or scientific-yield estimate.",
        },
    }


def render(report: dict) -> str:
    lines = [
        "# Next Layer Scale-Up readiness",
        "",
        "**READ-ONLY MECHANICAL PLANNING — HUMAN LAYER-SELECTION DECISION REQUIRED**",
        "",
        f"Analysis `{report['analysisId']}` applies Layer Scale-Up V2 to the seven remaining Layers at `{report['sourceCommit']}`. Psychological is complete and excluded. No literature search, candidate generation, scientific adjudication, governance, activation, ontology work, or architecture change was performed.",
        "",
        "## Compact comparison",
        "",
        "| Layer | Families | Drivers | RDS | Entities | Active incident rels | Causal propositions | Within family | Same-Layer cross-Family | Cross-Layer (in/out) | Isolates | RDS sources | V1 incomplete | A&E governed/active | Prior pilot | RDS complexity | Cross-Layer burden | Overall V2 workload |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- |",
    ]
    for row in report["layers"]:
        ae_cov = row["actionsEventsCoverage"]
        ae_text = f"HT {ae_cov['governedHappeningTypesWithOriginLayer']}/{ae_cov['activeHappeningTypesWithOriginLayer']}; EA {ae_cov['governedEffectAssertionsTargetingLayer']}/{ae_cov['activeEffectAssertionsTargetingLayer']}"
        lines.append(
            f"| {row['layer']} | {row['families']} | {row['drivers']} | {row['rds']} | {row['entities']} | {row['activeIncidentRelationshipCount']} | {row['uniqueCausalPropositionsTouchingLayer']} | {row['withinFamilyCausalCount']} | {row['sameLayerCrossFamilyCausalCount']} | {row['crossLayerCausalCount']} ({row['incomingCrossLayerCausalCount']}/{row['outgoingCrossLayerCausalCount']}) | {row['causalIsolates']} | {row['rdsCausalSourceCount']} | {row['legacyV1IncompleteBurden']} | {ae_text} | {', '.join(row['priorPilotCoverage']) or 'none'} | {row['workload']['factors']['rdsComplexity']} | {row['workload']['factors']['crossLayerCoordination']} | {row['workload']['overall']} |"
        )

    lines += [
        "",
        "A&E cells show governed/active HappeningTypes by origin Layer and governed/active EffectAssertions by target Layer. The count is current coverage, not efficacy breadth or search completeness.",
        "",
        "## Workload proxies",
        "",
        "| Layer | Entity volume | Relationship volume | Cross-Layer coordination | RDS complexity | Construct ambiguity | Source/evidence | Architecture risk | A&E search | Overall |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in report["layers"]:
        f = row["workload"]["factors"]
        lines.append(f"| {row['layer']} | {f['entityVolume']} | {f['existingRelationshipVolume']} | {f['crossLayerCoordination']} | {f['rdsComplexity']} | {f['constructBoundaryAmbiguity']} | {f['sourceEvidenceBurden']} | {f['architectureRisk']} | {f['actionsEventsSearchComplexity']} | **{row['workload']['overall']}** |")

    lines += [
        "",
        "Ratings use only entity, causal-edge, cross-Layer, RDS, blocked-field, legacy-incomplete, prior-pilot queue, and Network State binding counts. They are relative planning signals; they do not estimate tokens, credits, calendar time, evidence quality, or candidate yield.",
        "",
        "## Existing coverage and recorded risk signals",
        "",
    ]
    for row in report["layers"]:
        ae_cov = row["actionsEventsCoverage"]
        lines += [
            f"### {row['layer']}",
            "",
            f"- Psychological causal coupling: {row['psychologicalCouplingCausalCount']} active cross-Layer propositions.",
            f"- Blocked/incomplete metadata proxy: {row['blockedOrIncompleteMetadataCount']} ({row['blockedEntityCount']} blocked entities; {row['legacyV1IncompleteBurden']} unique V1-incomplete incident causal Relationships).",
            f"- Source-governance signals: {row['activeCausalWithoutStructuredEvidenceCount']} active incident causal Relationships lack structured evidence IDs; unresolved structured pilot source-queue rows: {row['unresolvedPilotSourceQueueCount']} ({row['sourceGovernanceQueueBasis']}).",
            f"- Prior-pilot A&E candidate records: {ae_cov['priorPilotCandidateRecords']}.",
            f"- Governed A&E coverage references {row['canonicalSourcesInGovernedActionsEventsCoverage']} unique canonical sources for this Layer's origin/target routes.",
            f"- Structured pilot blockers: {', '.join(f'`{x}`' for x in row['knownArchitectureEscalationIds']) or 'none recorded'}; Network State bindings: {row['networkStateBindingCount']}; Network State relevance: {row['networkStateRelevance']}.",
            "",
        ]

    lines += [
        "## RECOMMENDED_NEXT_LAYER",
        "",
        "**Informational.** It has the strongest direct strategic fit for cognitive security and OIE, the largest recorded coupling to completed Psychological science among the manageable candidates (14 active cross-Layer causal propositions), and an existing INF-F03 pilot with reusable governance, source, and Actions & Events infrastructure. Its 78 entities are the smallest remaining inventory after Biological, while 58 incident causal propositions, 25 cross-Layer causal links, seven RDS, and four RDS causal sources make it substantial enough to exercise the V2 funnel. The workload proxy is HIGH rather than trivial: one unique structured pilot blocker and 11 unresolved pilot source-queue rows require explicit Stage 0/2 routing. Those are recorded constraints that V2 can surface early; the analysis does not authorize resolving them or starting research.",
        "",
        "## ALTERNATE_NEXT_LAYER",
        "",
        "**Biological.** BIO-F01 provides prior pilot infrastructure and scientific diversity from Psychological work. It has the lowest active causal volume (32) and only 11 cross-Layer causal links, making it a controlled second exercise of V2. Five RDS, one RDS causal source, five blocked entities, and 48 causal isolates still give the funnel meaningful RDS and negative-coverage work. It ranks behind Informational because its recorded Psychological coupling is lower (5) and its immediate cognitive-security/OIE leverage is less direct.",
        "",
        "## DEFER_FOR_NOW",
        "",
        "- **Social:** strategically valuable and tightly coupled to Psychological work, but 92 incident causal propositions, 31 cross-Layer links, 23 RDS, 10 RDS causal sources, 92 V1-incomplete incident edges, two unique structured pilot blockers, and the current Network State binding make it the highest architecture/co-ordination burden. It should follow an earlier V2 application unless the human explicitly prioritizes network architecture work.",
        "- **Institutional / Structural:** largest remaining entity inventory (116), 49 isolates, 61 V1-incomplete incident causal Relationships, and HIGH architecture/RDS signals create a broad first-pass burden.",
        "- **Physical / Environmental:** 109 entities and 48 isolates imply extensive negative-coverage accounting despite low RDS risk; its direct Psychological coupling is only two recorded causal propositions.",
        "- **Technological:** 70 incident causal propositions and 23 cross-Layer links create HIGH evidence and Actions & Events search burden; actor/system feasibility boundaries would require careful later handling.",
        "- **Cultural:** moderate entity volume but 55 incident causal propositions and 55 V1-incomplete incident edges indicate substantial construct and evidence reconciliation before exact candidate work.",
        "",
        "## Selection boundary",
        "",
        "This is planning advice only. No next-Layer branch, Family landscape, literature search, source extraction, candidate, governance record, or activation has been created. Starting another full Layer remains the next consequential human decision.",
    ]
    return "\n".join(lines)


def main() -> None:
    report = build()
    write_json(REPORT, report)
    write_text(DOC, render(report))
    print(json.dumps({
        "layers": len(report["layers"]),
        "recommended": report["selection"]["recommendedNextLayer"],
        "alternate": report["selection"]["alternateNextLayer"],
        "scienceChanges": 0,
    }, indent=2))


if __name__ == "__main__":
    main()
