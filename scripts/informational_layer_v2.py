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

# One row per canonical active incident proposition. These are audit dispositions,
# never production edits. Review-only proposals do not authorize replacement.
REVIEW_TEXT = """
REL-CUL-054|RETAIN_AS_IS|Previously governed euphemism-to-metaphor segment; preserve its specified mediator scope.
REL-INF-001|RESEARCH_NEEDED|Availability and relative prominence differ; encounter probability is an omitted mediator.
REL-INF-002|RESEARCH_NEEDED|Prominent content need not create a prompt cue; cue presence differs from cue detection.
REL-INF-003|RETYPE_CANDIDATE|Pilot found exposure duration qualifies decoding opportunity, not a direct cause of the readability calculation.
REL-INF-004|RETYPE_CANDIDATE|Arrival rate contributes mechanically to window-relative volume; formula dependence is not independent causality.
REL-INF-005|RETYPE_CANDIDATE|Message length is a volume input under a declared window, not an independent causal effect on the calculated ratio.
REL-INF-006|REVISION_CANDIDATE|Pilot approved review-only criticism; INF-013/INF-077 overlap and INF-014 derivation block any implemented replacement; preserve HYP-INF-F03-H20.
REL-INF-007|RESEARCH_NEEDED|Pilot found complete information can remain unambiguously contradictory; no universal sign is supportable.
REL-INF-008|RETYPE_CANDIDATE|Pilot found required uncertainty fields may change completeness by definition under an explicit requirement set.
REL-INF-009|RESEARCH_NEEDED|Pilot found incompatible claims can each be clear; contradiction rule is not ambiguity rule.
REL-INF-010|RETYPE_CANDIDATE|Evidence quality can be one input to argument strength only when inference relevance is specified.
REL-INF-011|RETYPE_CANDIDATE|Citation traceability is a component of process transparency, not an independently observed outcome.
REL-INF-012|RETYPE_CANDIDATE|Including a counterargument is input to possible refutation, but does not prove refutation strength.
REL-INF-013|RETYPE_CANDIDATE|Source identity disclosure can enable provenance reconstruction but disclosure alone is not verified provenance.
REL-INF-014|RESEARCH_NEEDED|Conflict disclosure may reveal a motive but neither completeness nor recipient interpretation is established.
REL-INF-015|RESEARCH_NEEDED|Independent sources can agree or disagree; independence is not a cause of consistency.
REL-INF-016|RESEARCH_NEEDED|Repetition may alter perceived prominence but count, actual encounter, and salience are not aligned.
REL-INF-017|RETYPE_CANDIDATE|Spacing redistributes a fixed count over time; frequency depends on the specified window.
REL-INF-018|RETYPE_CANDIDATE|Correction delay concerns timing after an earlier claim; it does not cause correction presence.
REL-INF-019|RETYPE_CANDIDATE|Narrative coherence and evidence presence are distinct content codings with possible component overlap.
REL-INF-020|RETYPE_CANDIDATE|Causal structure is a component of coherence under a declared coding rule.
REL-INF-021|RESEARCH_NEEDED|Emotional intensity need not produce vividness; bundled wording and imagery prevent a general sign.
REL-INF-022|RESEARCH_NEEDED|Personalization need not add local referents; content alignment and location are distinct.
REL-INF-024|RETYPE_CANDIDATE|Threat-severity content can be part of a warning label but label presence is not a causal effect.
REL-INF-025|RESEARCH_NEEDED|An efficacy claim and complete actionable steps are distinct content components.
REL-INF-026|RESEARCH_NEEDED|Feedback may or may not contain an explicit comparison benchmark.
REL-INF-027|RETYPE_CANDIDATE|A claim of prevalence is not necessarily consensus or endorsement by a relevant group.
REL-INF-028|RESEARCH_NEEDED|Veracity changes only if detected and acted upon; factual status alone does not produce a correction.
REL-INF-030|RETYPE_CANDIDATE|Specificity and detail have overlapping coding components; no independent causal effect identified.
REL-INF-031|RETYPE_CANDIDATE|An alternative explanation contributes correction content under a declared coding rule.
REL-INF-032|RESEARCH_NEEDED|Specific advice can omit an explicit call to action; component identity is unresolved.
REL-INF-033|RETYPE_CANDIDATE|Implementation steps can be one component of guidance completeness, not an independent effect.
REL-INF-034|RETYPE_CANDIDATE|Action-time specification can be one component of guidance completeness, not an independent effect.
REL-INF-035|REVISION_CANDIDATE|Psychological review found no exact trial evidence for universal communicated-to-perceived severity; exposure and appraisal require scope.
REL-INF-036|REVISION_CANDIDATE|Psychological review separates response-efficacy content from belief in efficacy and requires exact exposure evidence.
REL-INF-037|REVISION_CANDIDATE|Psychological review separates objective evidence quality from pretested subjective argument strength.
REL-INF-038|REVISION_CANDIDATE|Psychological review found traceability can reveal poor provenance and need not increase source credibility.
REL-INF-039|RETAIN_V1_INCOMPLETE|Repeated actual encounters can increase familiarity; this does not authorize belief or accuracy inference.
REL-INF-040|RESEARCH_NEEDED|Psychological review found intensity and recipient salience distinct; medium, task and component manipulations remain unresolved.
REL-INF-041|REVISION_CANDIDATE|Pilot found temporary ambiguity may raise task processing demand; generic cognitive-load direction is not established.
REL-INF-042|RESEARCH_NEEDED|Complete guidance does not supply external resources or guarantee perceived behavioral control.
REL-INF-043|REVISION_CANDIDATE|Psychological review found external recommendation detail and formed action-plan specificity are different analytic units.
REL-INF-044|REVISION_CANDIDATE|Psychological review found task framing does not directly change stable loss aversion; endpoint semantics need review.
REL-INF-045|REVISION_CANDIDATE|Psychological review found omitted content and perceived sufficiency differ unless the omission is detected or inferred.
REL-INF-046|REVISION_CANDIDATE|Pilot approved review-only criticism of confidence calibration; Psychological review keeps exact cross-layer evidence research-needed.
REL-INF-047|REVISION_CANDIDATE|Psychological review found objective truth and strength of a person's causal belief are separate without encounter and acceptance.
REL-INF-048|REVISION_CANDIDATE|Prior governed metaphor mediator segment remains active; pilot recommends review of context-dependent ambiguity only.
REL-INF-049|RETAIN_AS_IS|Previously governed viewpoint-diversity mediator segment; preserve path ownership and scope.
REL-INS-049|RETAIN_AS_IS|Previously governed inclusion-to-viewpoint-diversity segment; external owner retained.
REL-RDS-0001|RETAIN_AS_IS|Governed compositional dependency is noncausal and must not traverse as an effect.
REL-RDS-0002|RETAIN_AS_IS|Governed semantic narrower-than relationship is noncausal.
REL-RDS-0003|RETAIN_AS_IS|Governed semantic relation requires aligned requirement universe; no causal sign is inferred.
REL-RDS-0007|RETAIN_AS_IS|Governed realization relation is noncausal; technical prominence does not imply exposure.
REL-RDS-0014|RETAIN_AS_IS|Governed derivational input is noncausal; INF-077 metadata blocker remains.
REL-RDS-0015|RETAIN_AS_IS|Governed derivational input is noncausal; audience fit rule is still required.
REL-TEC-048|RETAIN_V1_INCOMPLETE|Technical amplification can increase selected exposure only if delivery is realized; preserve platform scope.
REL-TEC-051|RETAIN_V1_INCOMPLETE|Recommendation personalization intensity can produce tailored content under implementation conditions.
REL-TEC-052|RETAIN_V1_INCOMPLETE|Reach scaling can expand availability but not actual encounter.
REL-TEC-053|RETAIN_AS_IS|Previously governed reach-scaling mediator segment; do not infer direct behavioral effect.
REL-TEC-057|RESEARCH_NEEDED|Automated feedback capability differs from actual delivered performance feedback.
REL-TEC-060|RETAIN_V1_INCOMPLETE|Pilot retained capability-to-disclosure edge with realized-display conditions; no source repair implied.
REL-TEC-065|RETAIN_V1_INCOMPLETE|Technical provenance signaling can support traceability only when signal authenticity is maintained.
REL-TEC-067|RETAIN_V1_INCOMPLETE|Automated generation can raise content arrival rate under delivery conditions; volume is not load.
REL-V1-INF-F03-001|RETAIN_AS_IS|Pilot-governed bounded uncertainty-to-source-credibility Relationship is reused unchanged.
"""


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


def build_reviews_and_coverage() -> None:
    frozen = read(DATA / "baseline.json")
    landscapes = read(DATA / "family-landscapes.json")["families"]
    decisions = {}
    for line in REVIEW_TEXT.strip().splitlines():
        identifier, disposition, rationale = line.split("|", 2)
        assert identifier not in decisions
        decisions[identifier] = (disposition, rationale)
    ids = {row["id"] for row in frozen["incidentRelationships"]}
    assert ids == set(decisions), (sorted(ids - set(decisions)), sorted(set(decisions) - ids))
    pilot_ids = set(frozen["pilot"]["existingAuditIds"])
    psychological = read(DATA.parent / "PSYCHOLOGICAL_LAYER/relationship-review-registry.json")
    previously_decided_pilot = {
        "REL-INF-003", "REL-INF-006", "REL-INF-007", "REL-INF-008", "REL-INF-009",
        "REL-INF-041", "REL-INF-046", "REL-INF-048", "REL-RDS-0001",
        "REL-RDS-0002", "REL-RDS-0003", "REL-RDS-0014", "REL-RDS-0015",
        "REL-TEC-060", "REL-V1-INF-F03-001",
    }
    reviews = {}
    for row in frozen["incidentRelationships"]:
        identifier = row["id"]
        disposition, rationale = decisions[identifier]
        reviews[identifier] = {
            "id": identifier, "ownerFamilyId": row["ownerFamilyId"],
            "consultedFamilyIds": row["consultedFamilyIds"], "scope": row["scope"],
            "semanticType": row["edge"]["semanticType"], "sourceId": row["edge"]["source"],
            "targetId": row["edge"]["target"], "disposition": disposition,
            "rationale": rationale, "v1IncompleteFields": row["v1IncompleteFields"],
            "priorPilotReviewId": identifier if identifier in pilot_ids else None,
            "priorPsychologicalReviewId": identifier if identifier in psychological else None,
            "priorPsychologicalDisposition": psychological[identifier]["primaryDisposition"] if identifier in psychological else None,
            "priorHumanDecision": ("GOV-INF-F03-001-2026-09-06" if identifier in previously_decided_pilot else
                                   "GOV-PSYCHOLOGICAL-LAYER-001-2026-09-17" if identifier in psychological else None),
            "productionChangeAuthorized": False, "sourceIds": landscapes[row["ownerFamilyId"]]["sourceIds"],
        }
    write(DATA / "relationship-review-registry.json", reviews)

    edges_by_entity = {}
    for row in frozen["incidentRelationships"]:
        if row["edge"]["semanticType"] != "CAUSAL":
            continue
        for endpoint in (row["edge"]["source"], row["edge"]["target"]):
            edges_by_entity.setdefault(endpoint, []).append(row["id"])
    pilot_ae = read(ROOT / "data/candidates/actions-events-v1/INF-F03/workspace.json")["passB"]["effectAssertions"]
    pilot_targets = {row["targetId"] for row in pilot_ae}
    canonical_ae = read(ROOT / "data/actions-events-v1/catalog.json")["effectAssertions"]
    canonical_targets = {row["targetId"] for row in canonical_ae if row["governance"]["lifecycleStatus"] == "GOVERNED"}
    coverage = {}
    for row in frozen["entities"]:
        entity = row["frozenRecord"]
        identifier, family = entity["id"], entity["primaryFamilyId"]
        incident = sorted(edges_by_entity.get(identifier, []))
        if entity["entityType"] != "DRIVER":
            relationship_status = "BLOCKED" if identifier in {"INF-014", "RDS-0001"} else "EXISTING_PROPOSITION_SUFFICIENT" if incident else "NO_PLAUSIBLE_MECHANISM"
            ae_status = "NOT_APPLICABLE"
            reason = "RDS cannot be a direct EffectAssertion target; derivation and causal-source risk are reviewed separately."
        else:
            relationship_status = "CANDIDATE_RESEARCHED" if identifier == "INF-061" else "BLOCKED" if identifier == "INF-077" else "EXISTING_PROPOSITION_SUFFICIENT" if incident else "INSUFFICIENT_PRELIMINARY_SIGNAL"
            if identifier in pilot_targets or identifier == "INF-061":
                ae_status = "CANDIDATE_RESEARCHED"
                reason = "Exact prior pilot candidate or Layer norm-prevalence operation receives bounded review; no inferred efficacy."
            elif identifier in canonical_targets:
                ae_status = "EXISTING_PROPOSITION_SUFFICIENT"
                reason = "Previously governed exact EffectAssertion covers this target; this audit does not duplicate it."
            elif identifier == "INF-041":
                ae_status = "BLOCKED"
                reason = "Psychological repetition shared contribution remains blocked; no duplicate effect is minted."
            else:
                ae_status = "INSUFFICIENT_PRELIMINARY_SIGNAL"
                reason = "Family landscape did not isolate this exact content property as a reusable operation-to-Driver effect; bundled message evidence is insufficient for a formal assertion."
        coverage[identifier] = {
            "id": identifier, "familyId": family, "entityType": entity["entityType"],
            "relationshipStatus": relationship_status, "actionsEventsStatus": ae_status,
            "incidentCausalRelationshipIds": incident, "landscapeSourceIds": landscapes[family]["sourceIds"],
            "reason": reason,
        }
    write(DATA / "negative-coverage-registry.json", coverage)

    rds = []
    all_entity_types = {row["id"]: row["entityType"] for row in read(ROOT / "data/entities.json")}
    for row in frozen["entities"]:
        entity = row["frozenRecord"]
        if entity["entityType"] == "DRIVER":
            continue
        identifier = entity["id"]
        incoming = [r["id"] for r in frozen["incidentRelationships"] if r["edge"]["target"] == identifier and r["edge"]["semanticType"] == "CAUSAL"]
        outgoing = [r["id"] for r in frozen["incidentRelationships"] if r["edge"]["source"] == identifier and r["edge"]["semanticType"] == "CAUSAL"]
        incident_causal = [r for r in frozen["incidentRelationships"] if r["id"] in set(incoming + outgoing)]
        d10_edges = []
        for edge_row in incident_causal:
            edge = edge_row["edge"]
            source_type, target_type = all_entity_types[edge["source"]], all_entity_types[edge["target"]]
            d10_edges.append({"relationshipId": edge_row["id"], "sourceType": source_type,
                              "targetType": target_type,
                              "rule": "EXCEPTIONAL" if source_type != "DRIVER" and target_type != "DRIVER" else "HEIGHTENED"})
        rds.append({
            "id": identifier, "familyId": entity["primaryFamilyId"], "definition": entity["definition"],
            "declaredScale": entity.get("representationScale"), "derivation": "NO_VERSIONED_EXACT_RULE_IN_FROZEN_ENTITY" if identifier != "RDS-0001" else "MULTIDIMENSIONAL_PROFILE_WITH_BLOCKED_METADATA",
            "inputs": "NOT_EXACTLY_DECLARED", "aggregation": "NOT_EXACTLY_DECLARED", "units": "NOT_EXACTLY_DECLARED",
            "window": "NOT_EXACTLY_DECLARED", "baseline": "NOT_EXACTLY_DECLARED", "externalInputs": "NOT_EXACTLY_DECLARED",
            "declaredIndicators": entity.get("indicators"),
            "declaredMeasurementMethods": entity.get("measurementAssessmentMethods"),
            "sharedConstituents": "NOT_IDENTIFIED_FROM_FROZEN_EXACT_RULE",
            "incomingCausalIds": incoming, "outgoingCausalIds": outgoing,
            "d10IncidentCausalEdges": d10_edges,
            "d10": "HEIGHTENED_CAUSAL_SOURCE" if outgoing else "HEIGHTENED_CAUSAL_TARGET" if incoming else "NONCAUSAL_OR_ISOLATED",
            "doubleCountRisk": "YES_REVIEW_CONSTITUENTS" if outgoing else "POSSIBLE_IF_FORMULA_AND_CONSTITUENTS_BOTH_USED" if incoming else "NO_ACTIVE_CAUSAL_EDGE",
            "directEffectTargetAllowed": False, "blockers": ["HYP-INF-F03-H20"] if identifier == "INF-014" else ["BLOCKED_FROZEN_METADATA"] if identifier == "RDS-0001" else [],
            "resolutionAuthorized": False,
        })
    write(DATA / "rds-review.json", rds)

    cross_family = []
    cross_layer = []
    for row in frozen["incidentRelationships"]:
        edge = row["edge"]
        if row["scope"] == "SAME_LAYER_CROSS_FAMILY":
            cross_family.append({"relationshipId": row["id"], "ownerFamilyId": row["ownerFamilyId"],
                                 "consultedFamilyIds": row["consultedFamilyIds"],
                                 "semanticType": edge["semanticType"], "singleReviewId": row["id"],
                                 "issue": reviews[row["id"]]["rationale"]})
        elif row["scope"].startswith("CROSS_LAYER"):
            cross_layer.append({"relationshipId": row["id"], "scope": row["scope"],
                                "externalLayer": "Psychological" if edge["source"].startswith("PSY-") or edge["target"].startswith("PSY-") else "Other",
                                "priorPsychologicalReviewReused": row["id"] in psychological,
                                "priorPsychologicalDisposition": reviews[row["id"]]["priorPsychologicalDisposition"],
                                "newExternalFamilyAuditPerformed": False,
                                "singleReviewId": row["id"]})
    write(DATA / "cross-family-issues.json", cross_family)
    write(DATA / "cross-layer-findings.json", cross_layer)

    pilot_source_rows = []
    for source in frozen["pilot"]["sourceQueue"]:
        is_canonical = source.get("registrationStatus") == "CANONICALIZED_FOR_GOVERNED_INACTIVE_RECORD"
        pilot_source_rows.append({
            "candidateSourceId": source["id"], "existingStatus": source.get("registrationStatus"),
            "canonicalSourceId": source.get("canonicalDuplicateId") if is_canonical else None,
            "classification": ("ALREADY_CANONICAL_FOR_PRIOR_GOVERNED_PILOT" if is_canonical else
                               "UNRESOLVED_IDENTITY_CANDIDATE_ONLY" if not source.get("doi") and not source.get("pmid") else
                               "OLD_CANDIDATE_OR_RESEARCH_NEEDED_ONLY"),
            "priorSupportsAssertionIds": source.get("supportsAssertionIds", []),
            "repairOrRegistrationPerformed": False,
        })
    write(DATA / "pilot-source-queue-review.json", pilot_source_rows)

    write(DATA / "source-overlap-registry.json", [
        {"id": "SO-INF-LAYER-001", "kind": "CANONICAL_PILOT_REUSE", "sourceIds": ["SRC-CAND-INF-F03-002", "SRC-551"], "rule": "One work, one source; prior pilot registration is not new evidence."},
        {"id": "SO-INF-LAYER-002", "kind": "PRIOR_PILOT_CANONICALIZATION", "sourceIds": ["SRC-CAND-INF-F03-001", "SRC-CAND-INF-F03-002", "SRC-CAND-INF-F03-003"], "rule": "Already governed pilot sources are carried by reference, not re-registered."},
        {"id": "SO-INF-LAYER-003", "kind": "INDEPENDENT_PRIMARY_DATASETS", "sourceIds": ["SRC-CAND-INF-LAYER-013", "SRC-CAND-INF-LAYER-014", "SRC-CAND-INF-LAYER-015"], "rule": "Different populations and protocols; directness to the exact endpoint differs, so do not pool as identical replication."},
        {"id": "SO-INF-LAYER-004", "kind": "REVIEW_PRIMARY_DEPENDENCE", "sourceIds": ["SRC-CAND-INF-LAYER-016", "SRC-CAND-INF-LAYER-017"], "rule": "Correction review and included/related primary work cannot be counted as independent replication of an exact new claim."},
        {"id": "SO-INF-LAYER-005", "kind": "SHARED_CAUSAL_CONTRIBUTION", "sourceIds": ["CONTRIB-PSY-LAYER-REPETITION-001"], "rule": "INF-F07 does not mint a second additive repetition-to-belief contribution."},
    ])

    write(DATA / "architecture-escalations.json", [
        {"id": "HYP-INF-F03-H20", "kind": "ONTOLOGY_BOUNDARY_BLOCKER", "issue": "INF-013 conceptual complexity definition overlaps surface-linguistic INF-077 while the latter retains blocked metadata; one measure cannot determine canonical equivalence.", "affectedIds": ["INF-013", "INF-077", "INF-014", "REL-INF-006"], "resolutionAuthorized": False, "candidateDisposition": "BLOCKED_NEEDS_GOVERNANCE_INPUT"},
        {"id": "ARCH-INF-LAYER-0001", "kind": "RDS_DERIVATION_AND_CAUSAL_SOURCE_REVIEW", "issue": "Four Informational RDS are active causal sources but the frozen records lack per-record exact derivation/version rules; constituent and aggregate contributions cannot be safely executed together.", "affectedIds": ["INF-004", "INF-010", "INF-011", "INF-068"], "resolutionAuthorized": False, "candidateDisposition": "BLOCKED_NEEDS_GOVERNANCE_INPUT_FOR_NEW_EXECUTION"},
        {"id": "META-INF-LAYER-0001", "kind": "BLOCKED_ENTITY_METADATA", "issue": "Message Cohesion RDS-0001 retains blocked mechanism, timing, observability and evidence fields; no silent repair.", "affectedIds": ["RDS-0001"], "resolutionAuthorized": False, "candidateDisposition": "BLOCKED_NEEDS_GOVERNANCE_INPUT"},
    ])
    write(DATA / "astra-escalation-queue.json", [
        {"id": "ASTRA-INF-LAYER-001", "recordId": "HYP-INF-F03-H20", "question": "Can conceptual complexity be distinguished from surface-linguistic complexity without redefining INF-013 or repairing blocked INF-077 metadata?", "availableEvidence": "Prior INF-F03 governed pilot audit and its unresolved H20 record; no new exact independent manipulation in this Layer pass.", "interpretations": ["Keep constructs separate with later definition governance", "Treat overlap as unresolved and avoid derived endpoint claims"], "whyNotAutomaticallyResolved": "Either interpretation changes ontology boundaries or feature-scope semantics and exceeds candidate-audit authority.", "consequences": ["Potential future definition/classification governance", "Dependent proposals remain blocked"], "currentDisposition": "BLOCKED_NEEDS_GOVERNANCE_INPUT", "workOnOtherFamiliesContinues": True},
    ])

    progress = read(DATA / "progress.json")
    progress["families"] = {key: "PASS_A_EXISTING" for key in sorted(landscapes)}
    write(DATA / "progress.json", progress)


def build_governance() -> None:
    frozen = read(DATA / "baseline.json")
    reviews = read(DATA / "relationship-review-registry.json")
    coverage = read(DATA / "negative-coverage-registry.json")
    triage = read(DATA / "triage-hypotheses.json")
    identity = read(DATA / "actions-events-identity-registry.json")
    source_findings = read(DATA / "source-findings.json")
    assessments = read(DATA / "evidence-assessments.json")
    rds = read(DATA / "rds-review.json")
    ae_hypotheses = read(DATA / "actions-events-hypotheses.json")
    sources = read(DATA / "candidate-source-registry.json")

    prior = {identifier for identifier, row in reviews.items() if row["priorHumanDecision"]}
    pending = {identifier: row for identifier, row in reviews.items() if identifier not in prior}
    group_specs = [
        ("GRP-INF-001", "APPROVE_RETAIN", [k for k, v in pending.items() if v["disposition"] == "RETAIN_AS_IS"], "The frozen noncausal/prior governed propositions remain unchanged; no new causal traversal."),
        ("GRP-INF-002", "APPROVE_RETAIN_V1_INCOMPLETE", [k for k, v in pending.items() if v["disposition"] == "RETAIN_V1_INCOMPLETE"], "Existing bounded causal mechanisms may remain as V1-incomplete without any claim expansion or execution upgrade."),
        ("GRP-INF-003", "KEEP_RESEARCH_NEEDED", [k for k, v in pending.items() if v["disposition"] == "RESEARCH_NEEDED"], "Exact causal or endpoint alignment is insufficient; each record retains its separate rationale and remains unchanged."),
        ("GRP-INF-004", "ACCEPT_CATEGORY_ERROR_REJECTIONS", [x["id"] for x in triage if x["outcome"] == "REJECT_CATEGORY_ERROR"], "Availability, task framing, threat-message content, correction, and instruction must not be equated with recipient processing, traits, behavior or universal outcomes."),
        ("GRP-INF-005", "KEEP_RESEARCH_NEEDED", [x["id"] for x in triage if x["outcome"] in {"INSUFFICIENT_PRELIMINARY_SIGNAL", "SEARCHED_NO_EXACT_EVIDENCE"}], "Landscape signal or exact component isolation is inadequate; no formal candidate is minted."),
        ("GRP-INF-006", "KEEP_RESEARCH_NEEDED", [x["id"] for x in ae_hypotheses if x["status"] == "RESEARCH_NEEDED"], "The plausible A&E routes lack isolated exact operation-to-target evidence; no EffectAssertion is recommended."),
    ]
    groups = [{"id": key, "recommendation": outcome, "recordIds": sorted(ids), "rationale": reason}
              for key, outcome, ids, reason in group_specs if ids]
    individuals = []
    for identifier, row in sorted(pending.items()):
        if row["disposition"] not in {"REVISION_CANDIDATE", "RETYPE_CANDIDATE", "SPLIT_CANDIDATE"}:
            continue
        outcome = {"REVISION_CANDIDATE": "APPROVE_REVISION_REVIEW_ONLY", "RETYPE_CANDIDATE": "APPROVE_RETYPE_REVIEW_ONLY", "SPLIT_CANDIDATE": "APPROVE_SPLIT_REVIEW_ONLY"}[row["disposition"]]
        individuals.append({"id": f"DEC-{identifier}", "recordIds": [identifier], "recommendation": outcome,
                            "rationale": row["rationale"], "productionChangeAuthorized": False})
    individuals.extend([
        {"id": "DEC-REL-CAND-INF-LAYER-0001", "recordIds": ["REL-CAND-INF-LAYER-0001", "EVA-REL-CAND-INF-LAYER-0001"], "recommendation": "KEEP_RESEARCH_NEEDED", "rationale": "Near-exact referent mismatch and bundled supporting experiments leave the exact content-property edge insufficient; preserve the source findings and null on the separate intention outcome.", "productionChangeAuthorized": False},
        {"id": "DEC-HT-CAND-INF-LAYER-0001", "recordIds": ["HT-CAND-INF-LAYER-0001"], "recommendation": "GOVERN_INACTIVE_IDENTITY", "rationale": "A named-group prevalence statement is a reusable presentation identity distinct from the existing personalized comparison panel. Identity does not imply efficacy or truthful content.", "productionChangeAuthorized": False},
    ])
    blocked = [
        {"id": "DEC-ARCH-INF-LAYER-0001", "recordIds": ["ARCH-INF-LAYER-0001", "INF-004", "INF-010", "INF-011", "INF-068"], "recommendation": "BLOCKED", "rationale": "Exact versioned derivation and constituent/aggregate source use require future architecture/governance review before new execution."},
        {"id": "DEC-META-INF-LAYER-0001", "recordIds": ["META-INF-LAYER-0001", "RDS-0001"], "recommendation": "BLOCKED", "rationale": "Blocked Message Cohesion metadata may not be repaired in this candidate audit."},
    ]
    vote_ids = [identifier for row in groups + individuals + blocked for identifier in row["recordIds"]]
    assert len(vote_ids) == len(set(vote_ids)), "A scientific item appears in multiple proposed votes"

    index = []
    group_by_record = {identifier: group["id"] for group in groups for identifier in group["recordIds"]}
    individual_by_record = {identifier: item["id"] for item in individuals for identifier in item["recordIds"]}
    blocked_by_record = {identifier: item["id"] for item in blocked for identifier in item["recordIds"]}

    def add(registry: str, identifier: str, *, linked: str | None = None) -> None:
        key = linked or identifier
        vote = group_by_record.get(key) or individual_by_record.get(key) or blocked_by_record.get(key)
        index.append({"rowId": f"GI-INF-LAYER-{len(index)+1:04d}", "registry": registry,
                      "recordId": identifier, "decisionId": vote,
                      "rowClass": "SCIENTIFIC_VOTE_REFERENCE" if vote else "NONVOTING_ACKNOWLEDGEMENT",
                      "priorHumanDecision": reviews.get(identifier, {}).get("priorHumanDecision")})

    for identifier in sorted(reviews): add("relationship-review-registry", identifier)
    for identifier in sorted(coverage):
        add("negative-coverage-registry/relationship", identifier + ":PASS_A", linked=identifier)
        add("negative-coverage-registry/actions-events", identifier + ":PASS_B", linked=identifier)
    for row in triage: add("triage-hypotheses", row["id"])
    add("candidate-proposition-registry", "REL-CAND-INF-LAYER-0001")
    for identifier in sorted(identity): add("actions-events-identity-registry", identifier)
    for row in source_findings: add("source-findings", row["id"], linked=row["claimId"])
    for row in assessments: add("evidence-assessments", row["id"])
    for row in rds: add("rds-review", row["id"])
    for row in read(DATA / "cross-family-issues.json"): add("cross-family-issues", "CROSS_FAMILY:" + row["relationshipId"], linked=row["relationshipId"])
    for row in read(DATA / "cross-layer-findings.json"): add("cross-layer-findings", "CROSS_LAYER:" + row["relationshipId"], linked=row["relationshipId"])
    for row in read(DATA / "pilot-source-queue-review.json"): add("pilot-source-queue-review", row["candidateSourceId"])
    for row in read(DATA / "source-overlap-registry.json"): add("source-overlap-registry", row["id"])
    for row in read(DATA / "architecture-escalations.json"): add("architecture-escalations", row["id"])
    for row in read(DATA / "astra-escalation-queue.json"): add("astra-escalation-queue", row["id"])
    for identifier in sorted(sources): add("candidate-source-registry", identifier)
    for row in ae_hypotheses: add("actions-events-hypotheses", row["id"])
    for row in read(DATA / "deep-research-ledger.json"): add("deep-research-ledger", row["id"], linked=row["candidateId"])
    add("skeptical-review", read(DATA / "skeptical-review.json")["reviewId"])
    for identifier in sorted(read(DATA / "family-landscapes.json")["families"]): add("family-landscapes", identifier)
    write(DATA / "governance-index.json", index)

    source_recs = {}
    for identifier, row in sources.items():
        category = ("ALREADY_CANONICAL" if identifier == "SRC-551" else
                    "REQUIRED_IF_IDENTITY_APPROVED" if identifier in {"SRC-CAND-INF-LAYER-013", "SRC-CAND-INF-LAYER-015"} else
                    "RESEARCH_NEEDED_ONLY" if identifier == "SRC-CAND-INF-LAYER-014" else
                    "LANDSCAPE_OR_BACKGROUND_ONLY")
        source_recs[identifier] = {"classification": category, "canonicalRegistrationPerformed": False,
                                   "futureApprovedRecordDependency": ["HT-CAND-INF-LAYER-0001"] if category == "REQUIRED_IF_IDENTITY_APPROVED" else [],
                                   "identityVerification": "PUBMED_OR_PUBLISHER_IDENTIFIER_VERIFIED" if row.get("doi") else "PMCID_AND_TITLE_ONLY",
                                   "accessDepth": row["accessDepth"]}
    write(DATA / "source-registration-recommendations.json", source_recs)

    ack_count = sum(row["rowClass"] == "NONVOTING_ACKNOWLEDGEMENT" for row in index)
    write(DATA / "governance-recommendations.json", {
        "schemaVersion": "1.0.0", "programId": PROGRAM_ID, "advisory": "ADVISORY — HUMAN DECISION REQUIRED",
        "originalGovernanceRows": len(index), "distinctScientificVotesProposed": len(groups) + len(individuals) + len(blocked),
        "groupedHumanDecisions": groups, "individualScientificDecisions": individuals,
        "blockedDecisions": blocked, "nonVotingRowAcknowledgements": ack_count,
        "priorHumanRelationshipDecisionsReferenced": len(prior),
        "futureMaterializationIfApproved": {"Relationships": 0, "HappeningTypes": 1, "EffectAssertions": 0, "EvidenceAssessments": 0},
        "newGoverned": 0, "newActive": 0, "productionScienceChanged": False,
    })

    progress = read(DATA / "progress.json")
    progress["families"] = {key: "SKEPTICAL_REVIEW" for key in sorted(read(DATA / "family-landscapes.json")["families"])}
    write(DATA / "progress.json", progress)


def finalize() -> None:
    validate_protection()
    frozen = read(DATA / "baseline.json")
    reviews = read(DATA / "relationship-review-registry.json")
    coverage = read(DATA / "negative-coverage-registry.json")
    landscapes = read(DATA / "family-landscapes.json")["families"]
    assert len(frozen["families"]) == 13 and len(frozen["entities"]) == 78
    assert len(reviews) == len(frozen["incidentRelationships"]) == 64
    assert set(coverage) == {row["frozenRecord"]["id"] for row in frozen["entities"]}
    assert set(landscapes) == {row["id"] for row in frozen["families"]}
    for identifier in landscapes:
        members = {row["frozenRecord"]["id"] for row in frozen["entities"] if row["frozenRecord"]["primaryFamilyId"] == identifier}
        assert members and members <= set(coverage)
        assert all(row["id"] in reviews for row in frozen["incidentRelationships"] if row["ownerFamilyId"] == identifier)
    assert len(read(DATA / "rds-review.json")) == 7
    assert all(x["governanceDecision"] == "NOT_DECIDED" and x["activationStatus"] == "NOT_ELIGIBLE" for x in read(DATA / "candidate-proposition-registry.json").values())
    assert all(not x["canonicalRegistrationPerformed"] for x in read(DATA / "source-registration-recommendations.json").values())

    progress = read(DATA / "progress.json")
    progress["families"] = {key: "COMPLETE" for key in sorted(landscapes)}
    write(DATA / "progress.json", progress)

    family_issues = {
        "INF-F01": "Availability, encounter and attention separated; prominence RDS reviewed.",
        "INF-F02": "Volume versus cognitive load; formula-like window volume edges require review.",
        "INF-F03": "Governed pilot reused; HYP-INF-F03-H20 and source queue preserved.",
        "INF-F04": "Task framing is not stable loss aversion; metaphor edge retains prior review.",
        "INF-F05": "Evidence quality, amount and audience acceptance separated.",
        "INF-F06": "Source property versus perceived credibility; disclosure components reviewed.",
        "INF-F07": "Repetition contribution linked, not duplicated; delay/spacing distinctions.",
        "INF-F08": "Narrative/vividness/emotion component isolation insufficient.",
        "INF-F09": "Tailoring packages separated from relevance; language-accessibility RDS reviewed.",
        "INF-F10": "Threat and efficacy content kept separate from appraisals and behavior.",
        "INF-F11": "Prevalence-to-perceived-norm candidate deep-researched then downgraded.",
        "INF-F12": "Correction and veracity boundaries; selective-omission RDS reviewed.",
        "INF-F13": "Guidance components are not plans or actions.",
    }
    lines = ["# Informational Layer progress", "", "**ADVISORY — HUMAN DECISION REQUIRED. Candidate science only; new GOVERNED = 0 and ACTIVE = 0.**", "",
             f"Program: `{PROGRAM_ID}`", f"Frozen baseline: `{BASE_COMMIT}`.", "",
             "| Family | Stage | Major issue |", "|---|---|---|"]
    for identifier, issue in family_issues.items():
        lines.append(f"| {identifier} | COMPLETE | {issue} |")
    lines.extend(["", "All Families completed baseline, landscape, triage, existing review, gap and A&E coverage, evidence, skeptical pass and Layer reconciliation. Exact machine statuses are in `progress.json`."])
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "INFORMATIONAL_LAYER_PROGRESS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    triage = read(DATA / "triage-hypotheses.json")
    source_reg = read(DATA / "candidate-source-registry.json")
    telemetry = {
        "driversCovered": sum(row["frozenRecord"]["entityType"] == "DRIVER" for row in frozen["entities"]),
        "actionsEventsCheapNegativeDrivers": sum(row["entityType"] == "DRIVER" and row["actionsEventsStatus"] in {"INSUFFICIENT_PRELIMINARY_SIGNAL", "NO_PLAUSIBLE_MECHANISM", "SEARCHED_NO_EXACT_EVIDENCE", "NOT_APPLICABLE"} for row in coverage.values()),
        "candidateHypothesesGenerated": len(triage) + len(read(DATA / "actions-events-hypotheses.json")),
        "candidatesEnteringDeepResearch": len(read(DATA / "deep-research-ledger.json")),
        "newFormalRelationshipCandidates": len(read(DATA / "candidate-proposition-registry.json")),
        "newFormalHappeningTypeCandidates": sum(row["recordClass"] == "HAPPENING_TYPE_CANDIDATE" for row in read(DATA / "actions-events-identity-registry.json").values()),
        "newFormalEffectAssertionCandidates": 0,
        "formalCandidatesRejectedAfterDeepResearch": 0,
        "newSourceFindings": len(read(DATA / "source-findings.json")),
        "newEvidenceAssessments": len(read(DATA / "evidence-assessments.json")),
        "priorPilotCanonicalSourcesReusedByReference": sum(row["registrationStatus"] == "CANONICALIZED_FOR_GOVERNED_INACTIVE_RECORD" for row in frozen["pilot"]["sourceQueue"]),
        "newCandidateSourceReferences": sum(identifier.startswith("SRC-CAND-INF-LAYER-") for identifier in source_reg),
        "sameLayerCrossFamilyCausalDuplicateReviewsPrevented": sum(row["semanticType"] == "CAUSAL" for row in read(DATA / "cross-family-issues.json")),
        "happeningTypeCanonicalIdentitiesReusedByReference": sum(row["recordClass"] == "IDENTITY_REUSE_REFERENCE" for row in read(DATA / "actions-events-identity-registry.json").values()),
        "astraEscalationsQueued": len(read(DATA / "astra-escalation-queue.json")),
        "elapsedTime": "NOT_MEASURED", "tokenSavings": "NOT_MEASURED", "creditSavings": "NOT_MEASURED",
    }
    write(DATA / "resource-telemetry.json", telemetry)

    gov = read(DATA / "governance-recommendations.json")
    manifest = {
        "advisory": "ADVISORY — HUMAN DECISION REQUIRED",
        "schemaVersion": "1.0.0", "programId": PROGRAM_ID, "auditClass": "CANDIDATE_ONLY_SCIENTIFIC_SCALE_UP_V2",
        "baseCommit": BASE_COMMIT, "familyStatuses": progress["families"],
        "counts": {"families": len(frozen["families"]), "drivers": telemetry["driversCovered"],
                   "rds": sum(row["frozenRecord"]["entityType"] != "DRIVER" for row in frozen["entities"]),
                   "entities": len(frozen["entities"]),
                   "incidentRelationships": len(frozen["incidentRelationships"]),
                   "causalRelationships": sum(row["edge"]["semanticType"] == "CAUSAL" for row in frozen["incidentRelationships"]),
                   "originalGovernanceRows": gov["originalGovernanceRows"],
                   "groupedVotes": len(gov["groupedHumanDecisions"]),
                   "individualVotes": len(gov["individualScientificDecisions"]),
                   "blockedVotes": len(gov["blockedDecisions"]),
                   "nonVotingAcknowledgementRows": gov["nonVotingRowAcknowledgements"]},
        "telemetry": telemetry, "productionHashes": protection(),
        "newGoverned": 0, "newActive": 0, "canonicalSourceRegistrationPerformed": False,
        "governanceHumanAuthorized": False, "productionScienceChanged": False,
        "requiredDataArtifacts": sorted(path.name for path in DATA.glob("*.json") if path.name != "audit-manifest.json"),
    }
    write(DOCS / "INFORMATIONAL_LAYER_AUDIT_MANIFEST.json", manifest)


def validate_protection() -> None:
    expected = read(DATA / "protected-baseline.json")["productionHashes"]
    assert protection() == expected, "Pre-existing production scientific data changed"


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["init", "reviews", "governance", "finalize", "validate"])
    args = parser.parse_args()
    if args.command == "init":
        init()
    elif args.command == "reviews":
        build_reviews_and_coverage()
    elif args.command == "governance":
        build_governance()
    elif args.command == "finalize":
        finalize()
    else:
        validate_protection()
