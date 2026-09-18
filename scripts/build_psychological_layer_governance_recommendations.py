#!/usr/bin/env python3
"""Build the advisory Psychological Layer governance decision package.

This builder consumes the completed audit package.  It does not search for new
evidence, mutate candidate lifecycle, or touch production science.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/candidates/actions-events-v1/PSYCHOLOGICAL_LAYER"
DOCS = ROOT / "docs/governance/scale-up/PSYCHOLOGICAL_LAYER"
NOTICE = "ADVISORY — HUMAN DECISION REQUIRED"

APPROVED_EFFECT_NUMBERS = {1, 2, 3, 5, 7, 12, 23}

IDENTITY_GROUPS = {
    "GRP-ID-01": ({1, 2, 5, 22, 26, 27}, "Information exposure, corrective, norm, health-message and forewarning identities"),
    "GRP-ID-02": ({3, 4, 8, 21}, "Aversive, exclusion, affective-media and shared-crisis exposure identities"),
    "GRP-ID-03": ({9, 10, 11, 16}, "Cueing, working-memory, retrieval and inhibition-practice identities"),
    "GRP-ID-04": ({13, 14, 15}, "Repeated behavior, if-then planning and progress-monitoring identities"),
    "GRP-ID-05": ({6, 17, 18}, "Bounded choice, future-cue and default-option identities"),
    "GRP-ID-06": ({19, 20, 24}, "Values, counterattitudinal-writing and perspective-taking identities"),
    "GRP-ID-07": ({12, 23, 25}, "Feedback, delay and calibration-feedback identities"),
    "GRP-ID-08": ({7, 28, 29}, "Breathing, uncertainty-testing and outgoing-behavior protocol identities"),
}

BLOCK_ROWS = {
    "BLK-PSY-001": {
        "title": "Normalized feature/dimension-specific scope",
        "rows": {"ARCH-PSY-LAYER-0001", "H-PSY-F03-22", "H-PSY-F07-10", "H-PSY-F08-04", "H-PSY-F08-19"},
        "issue": "Whole-profile candidates cannot represent a normalized feature- or dimension-specific exposure without an approved representation rule.",
        "affected": ["PSY-021", "PSY-048", "PSY-049", "PSY-085", "PSY-086", "PSY-087", "PSY-130"],
        "blocks": "Blocks materialization of claims whose meaning depends on a selected component or dimension.",
        "safe": "Target an already-defined exact Driver/measurement where it is scientifically identical; otherwise retain RESEARCH_NEEDED.",
        "future": "Human ontology governance should select a normalized feature/dimension representation and migration rule before materialization.",
    },
    "BLK-PSY-002": {
        "title": "PSY-130 situational/enduring meaning versus trait-only timing metadata",
        "rows": {"ARCH-PSY-LAYER-0002", "CF-PSY-LAYER-0056", "H-PSY-F14-22"},
        "issue": "PSY-130's definition permits situational and enduring meaning while its timing metadata is trait-only.",
        "affected": ["PSY-130"],
        "blocks": "Blocks state-to-trait materialization and any candidate that assumes one timescale.",
        "safe": "Leave PSY-130 unchanged and keep state-sensitive claims at RESEARCH_NEEDED.",
        "future": "Definition/timing governance must decide whether to revise timing metadata, split the construct, or constrain candidate use.",
    },
    "BLK-PSY-003": {
        "title": "Belief Strength versus Metacognitive Confidence for the same proposition",
        "rows": {"CF-PSY-LAYER-0003", "H-PSY-F01-06"},
        "issue": "The same-proposition boundary between PSY-003 Belief Strength and PSY-116 Metacognitive Confidence is not sufficiently normalized for duplicate-safe governance.",
        "affected": ["PSY-003", "PSY-116"],
        "blocks": "Blocks aliasing, merging, or materializing a claim whose confidence referent is not explicit.",
        "safe": "Name the proposition and confidence referent explicitly and preserve a single shared contribution; otherwise retain RESEARCH_NEEDED.",
        "future": "Classification governance should define referent tests and duplicate-control rules for belief and metacognitive confidence.",
    },
}

CONSTRUCT_QUESTIONS = [
    ("Component measurements versus multidimensional Drivers", "ARCHITECTURE_GOVERNANCE_NEEDED", "A component or profile score cannot silently stand for the whole Driver; use exact existing endpoints where available and defer feature-scoped materialization."),
    ("Belief confidence versus memory confidence, judgment confidence, and calibration", "CLASSIFICATION_GOVERNANCE_NEEDED", "The confidence referent and judged object must be explicit; PSY-003/PSY-116 same-proposition cases remain blocked."),
    ("Actual versus perceived norms", "NO_ACTION", "The completed audit consistently treats perceived norm reports as distinct from actual prevalence or behavior."),
    ("Knowledge versus recall", "RESEARCH_CLARIFICATION", "Task recall is an observation and does not by itself establish durable knowledge."),
    ("Frequency versus habit/automaticity", "NO_ACTION", "The audit correctly rejects frequency as an identity for automaticity and keeps exact habit claims separate."),
    ("Temporary state versus stable disposition", "RESEARCH_CLARIFICATION", "State manipulations do not establish trait change; timing must remain part of every candidate scope."),
    ("PSY-130 situational/enduring definition versus trait-only timing metadata", "ARCHITECTURE_GOVERNANCE_NEEDED", "The discrepancy is preserved as BLK-PSY-002 and must be resolved before state-sensitive materialization."),
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def num(record_id: str) -> int:
    return int(record_id.rsplit("-", 1)[1])


def text_of(row: dict) -> str:
    values = [row.get(k) for k in ("proposition", "support", "boundaries", "nullContrary", "humanDecision")]
    return " ".join(str(v) for v in values if v).lower()


def choose_group(text: str, rules: list[tuple[str, tuple[str, ...]]], fallback: str) -> str:
    for group_id, needles in rules:
        if any(needle in text for needle in needles):
            return group_id
    return fallback


REJECTION_RULES = [
    ("GRP-REJ-10", ("bundled", "multi-component", "package", "co-intervention", "cannot attribute")),
    ("GRP-REJ-01", ("measure != construct", "measurement does not", "measure is not", "scale score", "operationalization")),
    ("GRP-REJ-02", ("correlation", "cross-sectional", "association", "predictive model", "causal direction")),
    ("GRP-REJ-03", ("state != trait", "state does not", "temporary", "trait change", "stable disposition")),
    ("GRP-REJ-04", ("perceived norm", "actual norm", "perceived prevalence", "reported norm", "perceived descriptive", "actual behavioral prevalence", "perceived sufficiency", "actual information")),
    ("GRP-REJ-05", ("confidence", "accuracy", "calibration", "correctness")),
    ("GRP-REJ-06", ("frequency", "habit", "automaticity", "repetition alone")),
    ("GRP-REJ-07", ("task performance", "task score", "reaction time", "latent construct", "proxy")),
    ("GRP-REJ-08", ("intention", "behavior", "action", "willingness")),
    ("GRP-REJ-09", ("component", "part-whole", "definitional", "circular", "subscale")),
    ("GRP-REJ-11", ("mediat", "moderat", "pathway", "reciprocal", "mechanism")),
]

REJECTION_TITLES = {
    "GRP-REJ-01": "Measure is not the construct",
    "GRP-REJ-02": "Association or prediction is not causal identification",
    "GRP-REJ-03": "Temporary state is not stable trait change",
    "GRP-REJ-04": "Perceived norm is not actual norm",
    "GRP-REJ-05": "Confidence is not accuracy or calibration",
    "GRP-REJ-06": "Frequency is not habit or automaticity",
    "GRP-REJ-07": "Task performance is not the latent construct",
    "GRP-REJ-08": "Intention or willingness is not action",
    "GRP-REJ-09": "Part-whole, definitional, or circular inference",
    "GRP-REJ-10": "Bundled operation cannot identify a component effect",
    "GRP-REJ-11": "Mediation, moderation, reciprocity, or pathway not identified",
    "GRP-REJ-12": "Wrong entity level or semantic non-equivalence",
}

RESEARCH_RULES = [
    ("GRP-RN-01", ("causal", "random", "intervention", "directionality", "observational")),
    ("GRP-RN-02", ("construct", "endpoint", "semantic", "definition", "alignment")),
    ("GRP-RN-03", ("temporal", "timing", "state", "trait", "lag", "durab")),
    ("GRP-RN-04", ("task", "proxy", "measure", "performance", "scale")),
    ("GRP-RN-05", ("population", "transfer", "generaliz", "context", "sample")),
    ("GRP-RN-06", ("bundled", "component", "package", "co-intervention", "isolate")),
    ("GRP-RN-07", ("mixed", "null", "conflict", "contrary", "heterogen")),
    ("GRP-RN-08", ("exact", "unavailable", "no source", "not located", "insufficient source")),
    ("GRP-RN-09", ("mediat", "moderat", "recipro", "pathway", "mechanism")),
]

RESEARCH_TITLES = {
    "GRP-RN-01": "Insufficient causal identification",
    "GRP-RN-02": "Construct or endpoint mismatch",
    "GRP-RN-03": "Temporal or state/trait ambiguity",
    "GRP-RN-04": "Task, proxy, or measurement mismatch",
    "GRP-RN-05": "Population or context transfer not established",
    "GRP-RN-06": "Bundled manipulation or component attribution",
    "GRP-RN-07": "Conflicting, null, or heterogeneous evidence",
    "GRP-RN-08": "Exact endpoint or operation evidence unavailable",
    "GRP-RN-09": "Pathway, moderation, or reciprocity unproven",
    "GRP-RN-10": "Source alignment, access, or precision insufficient",
}

EXISTING_RN_GROUPS = {
    "GRP-ER-RN-01": ({"REL-INF-046"}, "Existing edge tied to unresolved prior-review/source alignment"),
    "GRP-ER-RN-02": ({"REL-BIO-019", "REL-INF-040", "REL-INF-042", "REL-PSY-007", "REL-PSY-015", "REL-PSY-033", "REL-PSY-051", "REL-PSY-064", "REL-SOC-068", "REL-TEC-064"}, "Existing edges supported only by task, proxy, or mismatched measurements"),
    "GRP-ER-RN-03": ({"REL-ENV-044", "REL-PSY-060", "REL-PSY-067", "REL-SOC-067", "REL-SOC-069"}, "Existing cross-level, aggregation, or population-transfer edges"),
    "GRP-ER-RN-04": ({"REL-PSY-030", "REL-PSY-040", "REL-PSY-041", "REL-PSY-042", "REL-PSY-044", "REL-PSY-056"}, "Existing edges with state/trait, timing, or durable-change ambiguity"),
    "GRP-ER-RN-05": ({"REL-BIO-020", "REL-INS-043", "REL-PSY-011", "REL-PSY-016", "REL-PSY-057", "REL-PSY-058", "REL-PSY-059", "REL-PSY-066", "REL-SOC-063", "REL-SOC-066"}, "Existing edges with construct or exact-endpoint mismatch"),
    "GRP-ER-RN-06": ({"REL-INS-042", "REL-PSY-023", "REL-PSY-054", "REL-TEC-062"}, "Existing edges without sufficient causal identification"),
}

SHARED_TITLES = {
    "GRP-SH-01": "Single-primary-review ownership and shared-contribution control",
    "GRP-SH-02": "Confidence and epistemic-referent boundaries",
    "GRP-SH-03": "Norms, trust, perceived/actual, and cross-level boundaries",
    "GRP-SH-04": "State, trait, and timescale coordination",
    "GRP-SH-05": "Component, profile, and measurement overlap",
    "GRP-SH-06": "Operation, package, and proxy boundaries",
    "GRP-SH-07": "RDS and representation questions",
    "GRP-SH-08": "Reciprocal, pathway, and moderator coordination",
    "GRP-SH-09": "Source alignment and duplicate-source control",
    "GRP-SH-10": "Evidence overlap and EvidenceAssessment dependency control",
}

SHARED_GROUPS = {
    "GRP-SH-01": {"CF-PSY-LAYER-0024", "CF-PSY-LAYER-0031"},
    "GRP-SH-02": {"CF-PSY-LAYER-0008", "CF-PSY-LAYER-0010", "CF-PSY-LAYER-0026", "CF-PSY-LAYER-0029", "CF-PSY-LAYER-0051"},
    "GRP-SH-03": {"CF-PSY-LAYER-0012", "CF-PSY-LAYER-0013", "CF-PSY-LAYER-0052"},
    "GRP-SH-04": {"CF-PSY-LAYER-0018", "CF-PSY-LAYER-0021", "CF-PSY-LAYER-0046", "CF-PSY-LAYER-0048", "CF-PSY-LAYER-0053", "CF-PSY-LAYER-0055"},
    "GRP-SH-05": {"CF-PSY-LAYER-0002", "CF-PSY-LAYER-0007", "CF-PSY-LAYER-0017", "CF-PSY-LAYER-0030", "CF-PSY-LAYER-0032", "CF-PSY-LAYER-0037", "CF-PSY-LAYER-0043"},
    "GRP-SH-06": {"CF-PSY-LAYER-0034", "CF-PSY-LAYER-0036", "CF-PSY-LAYER-0038", "CF-PSY-LAYER-0044", "CF-PSY-LAYER-0050"},
    "GRP-SH-07": {"CF-PSY-LAYER-0015", "CF-PSY-LAYER-0027", "CF-PSY-LAYER-0035", "CF-PSY-LAYER-0040", "CF-PSY-LAYER-0054"},
    "GRP-SH-08": {"CF-PSY-LAYER-0001", "CF-PSY-LAYER-0004", "CF-PSY-LAYER-0022", "CF-PSY-LAYER-0033", "CF-PSY-LAYER-0039", "CF-PSY-LAYER-0041", "CF-PSY-LAYER-0042", "CF-PSY-LAYER-0045", "CF-PSY-LAYER-0049"},
    "GRP-SH-09": {"CF-PSY-LAYER-0006", "CF-PSY-LAYER-0009", "CF-PSY-LAYER-0016", "CF-PSY-LAYER-0023", "CF-PSY-LAYER-0028"},
    "GRP-SH-10": {"CF-PSY-LAYER-0011", "CF-PSY-LAYER-0014", "CF-PSY-LAYER-0019", "CF-PSY-LAYER-0020", "CF-PSY-LAYER-0025", "CF-PSY-LAYER-0047"},
}


def shared_group(row: dict) -> str:
    t = text_of(row) + " " + " ".join(row.get("issueIds", []))
    if any(x in t for x in ("source", "duplicate", "registration", "alignment")):
        return "GRP-SH-09"
    if any(x in t for x in ("evidenceassessment", "shared dataset", "independent replication", "review and included")):
        return "GRP-SH-10"
    if any(x in t for x in ("owner", "ownership", "shared contribution", "primary review")):
        return "GRP-SH-01"
    if any(x in t for x in ("confidence", "belief strength", "calibration", "metacognitive")):
        return "GRP-SH-02"
    if any(x in t for x in ("norm", "trust", "perceived", "actual", "cross-level")):
        return "GRP-SH-03"
    if any(x in t for x in ("state", "trait", "timing", "timescale")):
        return "GRP-SH-04"
    if any(x in t for x in ("component", "profile", "dimension", "measurement overlap")):
        return "GRP-SH-05"
    if any(x in t for x in ("operation", "package", "proxy", "manipulation")):
        return "GRP-SH-06"
    if any(x in t for x in ("rds", "representation", "ontology")):
        return "GRP-SH-07"
    return "GRP-SH-08"


def collect_formal_records():
    relationships, identities, effects, assessments = [], [], [], []
    for family in sorted(DATA.glob("PSY-F*")):
        workspace = load(family / "workspace.json")
        relationships.extend(workspace["passA"].get("relationshipCandidates", []))
        assessments.extend(workspace["passA"].get("evidence", []))
        identities.extend(workspace["passB"].get("happeningTypes", []))
        effects.extend(workspace["passB"].get("effectAssertions", []))
        assessments.extend(workspace["passB"].get("evidenceAssessments", []))
    return relationships, identities, effects, assessments


def candidate_summary(record: dict) -> dict:
    governance = record.get("governance", {})
    return {
        "id": record["id"],
        "lifecycleStatus": governance.get("lifecycleStatus"),
        "activationStatus": governance.get("activationStatus"),
        "targetId": record.get("targetId"),
        "targetKind": record.get("targetKind"),
        "typeId": record.get("typeId"),
        "property": record.get("property"),
        "change": record.get("change"),
        "scope": record.get("scope"),
    }


def main() -> None:
    rows = load(DATA / "governance-index.json")
    row_by_id = {row["id"]: row for row in rows}
    relationships, identities, effects, assessments = collect_formal_records()
    identity_registry = {x["id"]: x for x in load(DATA / "actions-events-identity-registry.json")}
    existing_registry = load(DATA / "relationship-review-registry.json")

    decision_units: dict[str, dict] = {}
    row_to_unit: dict[str, str] = {}

    def unit(unit_id: str, tier: int, title: str, outcome: str, rationale: str, row_ids: list[str], kind: str = "SCIENTIFIC_VOTE"):
        assert unit_id not in decision_units
        decision_units[unit_id] = {
            "id": unit_id,
            "tier": tier,
            "title": title,
            "advisoryRecommendation": outcome,
            "rationale": rationale,
            "humanActionType": kind,
            "rowIds": sorted(row_ids),
        }
        for row_id in row_ids:
            assert row_id in row_by_id, row_id
            assert row_id not in row_to_unit, row_id
            row_to_unit[row_id] = unit_id

    # Tier 1: existing retains.
    retain = [r["id"] for r in rows if r["type"] == "EXISTING_RELATIONSHIP_REVIEW" and r["recommendation"] == "RETAIN_AS_IS"]
    incomplete = [r["id"] for r in rows if r["type"] == "EXISTING_RELATIONSHIP_REVIEW" and r["recommendation"] == "RETAIN_V1_INCOMPLETE"]
    unit("GRP-ER-RETAIN", 1, "Straightforward existing Relationship retention", "APPROVE_RETAIN", "The completed review found no scientific change warranting a proposal.", retain)
    unit("GRP-ER-INCOMPLETE", 1, "Retain existing V1-incomplete Relationships", "APPROVE_RETAIN_V1_INCOMPLETE", "The science does not justify replacement semantics; retain the current record and its incomplete status.", incomplete)

    # Tier 1: existing Relationship research-needed groups.
    expected_existing_rn = {r["id"] for r in rows if r["type"] == "EXISTING_RELATIONSHIP_REVIEW" and r["recommendation"] == "RESEARCH_NEEDED"}
    grouped_existing_rn = set().union(*(ids for ids, _ in EXISTING_RN_GROUPS.values()))
    assert grouped_existing_rn == expected_existing_rn
    for gid, (ids, title) in EXISTING_RN_GROUPS.items():
        unit(gid, 1, title, "KEEP_RESEARCH_NEEDED", "The review identifies a plausible issue, but exact replacement semantics and evidence remain insufficient.", list(ids))

    # Tier 1: identities are coherent reusable operation identities. Identity governance implies no efficacy.
    identity_rows = {r["id"]: r for r in rows if r["type"] == "HAPPENING_TYPE_IDENTITY"}
    identity_recommendations = []
    for gid, (numbers, title) in IDENTITY_GROUPS.items():
        ids = [f"HT-CAND-PSY-LAYER-{n:04d}" for n in sorted(numbers)]
        unit(gid, 1, title, "GOVERN_INACTIVE_IDENTITY", "Each operation is reusable, intentionally scoped, provenance-bearing, and distinct from compared production identities. This recommendation confers no efficacy.", ids)
        for record_id in ids:
            reg = identity_registry[record_id]
            row = identity_rows[record_id]
            identity_recommendations.append({
                "id": record_id,
                "name": reg["name"],
                "recommendation": "GOVERN_INACTIVE_IDENTITY",
                "decisionUnitId": gid,
                "lifecycleStatus": row.get("lifecycle"),
                "activationStatus": reg.get("activationStatus"),
                "identityOnly": True,
                "efficacyImplied": False,
                "productionDuplicatesReviewed": reg.get("comparedProductionIdentityIds", []),
                "rationale": "Reusable operation identity is coherent at the recorded intentionality, origin, population-neutral scope, and provenance. Effect claims remain separate.",
            })

    # Tier 1: rejected hypotheses, preserving each proposition and rationale in rowAccounts.
    rejected_groups = defaultdict(list)
    for row in rows:
        if row["type"] == "HYPOTHESIS_LEDGER" and row["recommendation"] == "REJECTED_HYPOTHESIS":
            gid = choose_group(text_of(row), REJECTION_RULES, "GRP-REJ-12")
            rejected_groups[gid].append(row["id"])
    for gid, title in REJECTION_TITLES.items():
        if rejected_groups[gid]:
            unit(gid, 1, title, "REJECT_HYPOTHESIS", "Sample-check confirmed the category error or unsupported inference. The original row rationale remains controlling for every member.", rejected_groups[gid])

    # Tier 1: research-needed hypothesis groups.
    rn_groups = defaultdict(list)
    for row in rows:
        if row["type"] == "HYPOTHESIS_LEDGER" and row["recommendation"] == "RESEARCH_NEEDED":
            gid = choose_group(text_of(row), RESEARCH_RULES, "GRP-RN-10")
            rn_groups[gid].append(row["id"])
    for gid, title in RESEARCH_TITLES.items():
        if rn_groups[gid]:
            unit(gid, 1, title, "KEEP_RESEARCH_NEEDED", "The proposition remains plausible enough to preserve, but the completed package does not support an exact governed scientific record.", rn_groups[gid])

    # Tier 2: every revision/retype/split proposal is an individual review-only decision.
    existing_recommendations = []
    outcome_map = {
        "RETAIN_AS_IS": "APPROVE_RETAIN",
        "RETAIN_V1_INCOMPLETE": "APPROVE_RETAIN_V1_INCOMPLETE",
        "REVISION_CANDIDATE": "APPROVE_REVISION_REVIEW_ONLY",
        "RETYPE_CANDIDATE": "APPROVE_RETYPE_REVIEW_ONLY",
        "SPLIT_CANDIDATE": "APPROVE_SPLIT_REVIEW_ONLY",
        "RESEARCH_NEEDED": "KEEP_RESEARCH_NEEDED",
    }
    for row in (r for r in rows if r["type"] == "EXISTING_RELATIONSHIP_REVIEW"):
        outcome = outcome_map[row["recommendation"]]
        if row["recommendation"] in {"REVISION_CANDIDATE", "RETYPE_CANDIDATE", "SPLIT_CANDIDATE"}:
            uid = "IND-" + row["id"]
            unit(uid, 2, f"Individual review-only proposal for {row['id']}", outcome, "The criticism is scientifically meaningful, but this pass does not establish implementation-ready replacement semantics or authorize production change.", [row["id"]])
        else:
            uid = row_to_unit[row["id"]]
        review = existing_registry[row["id"]]["review"]
        existing_recommendations.append({
            "id": row["id"], "recommendation": outcome, "decisionUnitId": uid,
            "currentDisposition": row["recommendation"], "rationale": review.get("rationale"),
            "proposal": review.get("proposal"), "nullContrary": review.get("nullContrary"),
            "productionChangeAuthorized": False,
        })

    # Tier 2: new Relationship.
    relationship = relationships[0]
    relationship_row = row_by_id[relationship["id"]]
    unit("IND-REL-CAND-PSY-LAYER-0001", 2, "INF-041 Message Exposure Frequency → PSY-003 Belief Strength", "APPROVE_AS_IS", "The bounded claim identifies repeated encounter before later belief-confidence rating, preserves context-dependent direction and null/counterexample findings, and disclaims accuracy, behavior, universal dose-response, and transfer. It shares one contribution with EA-CAND-PSY-LAYER-0001 and must never be counted additively.", [relationship["id"]])
    new_relationship = {
        "id": relationship["id"],
        "recommendation": "APPROVE_AS_IS",
        "sourceId": relationship.get("sourceEntityId"),
        "targetId": relationship.get("targetEntityId"),
        "exactBoundedSemantics": relationship_row["proposition"],
        "boundaries": relationship_row.get("boundaries"),
        "nullContrary": relationship_row.get("nullContrary"),
        "sharedContributionId": relationship.get("sharedContributionId") or "CONTRIB-PSY-LAYER-REPETITION-001",
        "relatedEffectAssertionId": "EA-CAND-PSY-LAYER-0001",
        "duplicateProductionEdgeFound": False,
        "additiveCountingAuthorized": False,
        "productionChangeAuthorized": False,
        "candidateLifecycle": candidate_summary(relationship),
    }

    # Tier 2: every EffectAssertion is individual; REVIEW_READY is not automatic approval.
    effect_recommendations = []
    effect_by_id = {x["id"]: x for x in effects}
    assessment_by_object = {x["assertion"]["objectId"]: x for x in assessments}
    for effect_id in sorted(effect_by_id, key=num):
        effect = effect_by_id[effect_id]
        assessment = assessment_by_object[effect_id]
        synthesis = assessment.get("synthesis", {})
        approved = num(effect_id) in APPROVED_EFFECT_NUMBERS
        recommendation = "GOVERN_INACTIVE_AS_IS" if approved else "KEEP_RESEARCH_NEEDED"
        rationale = ("The exact operation, Driver target, property, direction/timing scope, manipulation alignment, and explicit null/contrary boundaries are sufficiently bounded for inactive scientific governance."
                     if approved else
                     "The exact claim remains insufficient at its recorded endpoint, causal, timing, transfer, or attribution boundary; statistical significance elsewhere does not cure that gap.")
        unit("IND-" + effect_id, 2, f"Individual EffectAssertion review: {effect_id}", recommendation, rationale, [effect_id])
        effect_recommendations.append({
            "id": effect_id,
            "recommendation": recommendation,
            "decisionUnitId": "IND-" + effect_id,
            "typeId": effect.get("typeId"),
            "targetId": effect.get("targetId"),
            "targetKind": effect.get("targetKind"),
            "property": effect.get("property"),
            "change": effect.get("change"),
            "scope": effect.get("scope"),
            "sharedContributionId": effect.get("contribution", {}).get("groupId"),
            "evidenceAssessmentId": assessment["id"],
            "evidenceDisposition": assessment.get("evidenceDisposition") or synthesis.get("disposition"),
            "evidenceStrength": assessment.get("evidenceStrength") or synthesis.get("evidenceStrength"),
            "nullContrary": row_by_id[effect_id].get("nullContrary"),
            "rationale": rationale,
            "candidateLifecycle": candidate_summary(effect),
        })

    # Tier 3: ten blocked rows collapse to three indivisible architecture/classification decisions.
    architecture_blockers = []
    for block_id, info in BLOCK_ROWS.items():
        unit(block_id, 3, info["title"], "BLOCKED", info["issue"], list(info["rows"]))
        architecture_blockers.append({
            "id": block_id, "recommendation": "BLOCKED", "sourceRowIds": sorted(info["rows"]),
            "exactIssue": info["issue"], "affectedCandidatesOrEntities": info["affected"],
            "materializationImpact": info["blocks"], "safeCurrentRepresentation": info["safe"],
            "recommendedFutureGovernanceAction": info["future"], "architectureChangeAuthorized": False,
        })

    # Remaining shared rows are coordination votes, compressed by scientific question.
    shared_groups = defaultdict(list)
    explicit_shared_group = {row_id: gid for gid, ids in SHARED_GROUPS.items() for row_id in ids}
    assert len(explicit_shared_group) == sum(len(ids) for ids in SHARED_GROUPS.values())
    for row in rows:
        if row["type"] != "SHARED_ISSUE_NOT_SCIENTIFIC_RECORD" or row["id"] in row_to_unit:
            continue
        # CF-0005 is a dependency of the Relationship/Effect shared contribution.
        if row["id"] == "CF-PSY-LAYER-0005":
            decision_units["IND-REL-CAND-PSY-LAYER-0001"]["rowIds"].append(row["id"])
            row_to_unit[row["id"]] = "IND-REL-CAND-PSY-LAYER-0001"
            continue
        assert row["id"] in explicit_shared_group, row["id"]
        shared_groups[explicit_shared_group[row["id"]]].append(row["id"])
    for gid, title in SHARED_TITLES.items():
        outcome = "ACKNOWLEDGE_COORDINATION_REQUIREMENT"
        unit(gid, 1, title, outcome, "Treat these rows as one coordination decision. They do not create a scientific record, alias, source registration, or production change.", shared_groups[gid])

    assert len(row_to_unit) == 595, sorted(set(row_by_id) - set(row_to_unit))
    assert set(row_to_unit) == set(row_by_id)
    tier_counts = Counter(x["tier"] for x in decision_units.values())
    assert tier_counts == {1: 48, 2: 95, 3: 3}, tier_counts

    row_accounts = []
    for row in rows:
        uid = row_to_unit[row["id"]]
        row_accounts.append({
            "rowId": row["id"], "originalType": row["type"],
            "originalRecommendation": row["recommendation"], "originalLifecycle": row.get("lifecycle"),
            "priority": row.get("priority"), "proposition": row.get("proposition"),
            "originalRationale": row.get("support") or row.get("humanDecision"),
            "decisionUnitId": uid, "tier": decision_units[uid]["tier"],
            "advisoryRecommendation": decision_units[uid]["advisoryRecommendation"],
            "candidateLifecycleChanged": False,
        })

    evidence_dependencies = []
    approved_record_ids = {new_relationship["id"]} | {x["id"] for x in identity_recommendations} | {
        x["id"] for x in effect_recommendations if x["recommendation"].startswith("GOVERN_INACTIVE")
    }
    for assessment in sorted(assessments, key=lambda x: x["id"]):
        object_id = assessment["assertion"]["objectId"]
        synthesis = assessment.get("synthesis", {})
        evidence_dependencies.append({
            "id": assessment["id"], "objectId": object_id,
            "recommendation": "INCLUDE_WITH_FUTURE_GOVERNED_RECORD" if object_id in approved_record_ids else "RETAIN_WITH_RESEARCH_NEEDED_CANDIDATE",
            "disposition": assessment.get("evidenceDisposition") or synthesis.get("disposition"),
            "strength": assessment.get("evidenceStrength") or synthesis.get("evidenceStrength"),
            "sourceIds": assessment.get("sourceIds") or sorted({x["sourceId"] for x in assessment.get("sourceFindings", [])}),
            "nullContraryPreserved": True,
            "independentReplicationInflationAllowed": False, "theoryAsExperimentAllowed": False,
            "candidateLifecycle": candidate_summary(assessment),
        })

    baseline = load(DATA / "baseline.json")
    workflow_acknowledgements = []
    for family in baseline["familyInventory"]:
        workflow_acknowledgements.append({
            "id": "ACK-" + family["id"], "familyId": family["id"],
            "recommendation": "ACKNOWLEDGE_COMPLETE_SEARCH_LEDGER",
            "humanActionType": "WORKFLOW_LEDGER_ACKNOWLEDGEMENT",
            "scientificVote": False,
        })

    existing_counts = Counter(x["recommendation"] for x in existing_recommendations)
    effect_counts = Counter(x["recommendation"] for x in effect_recommendations)
    identity_counts = Counter(x["recommendation"] for x in identity_recommendations)
    package = {
        "notice": NOTICE,
        "schemaVersion": "1.0.0",
        "packageType": "ADVISORY_GOVERNANCE_RECOMMENDATIONS",
        "authority": {"humanDecisionRequired": True, "governancePerformed": False, "activationAuthorized": False, "materializationAuthorized": False},
        "compression": {
            "originalGovernanceRows": 595,
            "distinctScientificDecisions": 534,
            "groupedHumanDecisions": 48,
            "individualScientificDecisions": 95,
            "blockedDecisions": 3,
            "totalHumanDecisionUnits": 146,
            "workflowLedgerAcknowledgements": 14,
            "explanation": "Distinct scientific decisions count the 111 existing Relationship reviews, one new Relationship, 29 identities, 30 effects, 151 rejected hypotheses, 209 research-needed hypotheses, and three deduplicated blocked questions. Shared rows are dependencies/coordination questions; Family completion ledgers are non-voting acknowledgements.",
        },
        "decisionUnits": sorted(decision_units.values(), key=lambda x: (x["tier"], x["id"])),
        "rowAccounts": row_accounts,
        "workflowLedgerAcknowledgements": workflow_acknowledgements,
        "existingRelationshipRecommendations": existing_recommendations,
        "existingRelationshipCounts": dict(sorted(existing_counts.items())),
        "newRelationshipRecommendation": new_relationship,
        "happeningTypeIdentityRecommendations": sorted(identity_recommendations, key=lambda x: num(x["id"])),
        "happeningTypeIdentityCounts": dict(identity_counts),
        "effectAssertionRecommendations": sorted(effect_recommendations, key=lambda x: num(x["id"])),
        "effectAssertionCounts": dict(effect_counts),
        "evidenceAssessmentDependencies": evidence_dependencies,
        "constructOntologyQuestions": [{"issue": x, "classification": y, "recommendation": z} for x, y, z in CONSTRUCT_QUESTIONS],
        "architectureBlockers": architecture_blockers,
        "proposedFutureMaterialization": {"Relationships": 1, "HappeningTypes": 29, "EffectAssertions": 7, "EvidenceAssessments": 8},
        "validationAssertions": {
            "allGovernanceRowsAccountedFor": True,
            "reviewReadyRecordsAdjudicated": 45,
            "candidateLifecycleChanged": False,
            "productionScienceChanged": False,
            "familiesComplete": 14,
            "newGoverned": 0,
            "newActive": 0,
        },
    }
    decision_path = DATA / "governance-decision-001.json"
    materialization_path = ROOT / "data/actions-events-v1/PSYCHOLOGICAL_LAYER-materialization-manifest.json"
    if decision_path.exists() and materialization_path.exists():
        decision = load(decision_path)
        materialization = load(materialization_path)
        package["postRecommendationStatus"] = {
            "recommended": "HISTORICAL_ADVISORY_PRESERVED",
            "humanApproved": True,
            "humanDecisionId": decision["decisionId"],
            "humanDecisionRecord": decision["decisionRecord"],
            "materialized": True,
            "materializationId": materialization["materializationId"],
            "materializationManifest": "data/actions-events-v1/PSYCHOLOGICAL_LAYER-materialization-manifest.json",
            "materializedCounts": materialization["counts"],
            "activationAuthorized": False,
        }
    dump(DATA / "governance-recommendations.json", package)
    build_sources(approved_record_ids)
    build_markdown(package)


def build_sources(approved_record_ids: set[str]) -> None:
    registry = load(DATA / "candidate-source-registry.json")
    queue = load(DATA / "source-registration-candidate-queue.json")
    overlaps = load(DATA / "source-overlap-registry.json")
    queue_by_id = {x["candidateSourceId"]: x for x in queue}
    overlap_by_source = defaultdict(list)
    for issue in overlaps:
        for source_id in issue.get("sourceIds", []):
            overlap_by_source[source_id].append(issue["id"])

    hypothesis_usage = defaultdict(set)
    for family in sorted(DATA.glob("PSY-F*")):
        research = load(family / "research.json")
        for hypothesis in research.get("hypotheses", []):
            for source_id in hypothesis.get("sources", []):
                hypothesis_usage[source_id].add(hypothesis.get("status"))

    recommendations = []
    for source in registry:
        source_id = source["id"]
        if source.get("canonicalDuplicate"):
            classification = "ALREADY_CANONICAL"
            mapped = []
        else:
            q = queue_by_id[source_id]
            mapped = q.get("candidateAssertionOrIdentityIds", [])
            if any(x in approved_record_ids for x in mapped):
                classification = "REQUIRED_FOR_GOVERNED_RECORD"
            elif mapped:
                classification = "RESEARCH_NEEDED_ONLY"
            else:
                usage = hypothesis_usage.get(source_id, set())
                if usage and usage <= {"REJECTED_HYPOTHESIS"}:
                    classification = "REJECTION_BACKGROUND_ONLY"
                elif not source.get("verifiedAt"):
                    classification = "UNVERIFIED"
                elif overlap_by_source[source_id] and not usage:
                    classification = "DUPLICATE_OVERLAPPING"
                else:
                    classification = "RESEARCH_NEEDED_ONLY"
        recommendations.append({
            "sourceId": source_id, "classification": classification,
            "mappedCandidateRecordIds": mapped,
            "requiredForRecommendedRecordIds": sorted(set(mapped) & approved_record_ids),
            "canonicalDuplicate": source.get("canonicalDuplicate"),
            "accessDepth": source.get("accessDepth"), "verifiedAt": source.get("verifiedAt"),
            "overlapIssueIds": sorted(overlap_by_source[source_id]),
            "canonicalRegistrationAuthorized": False,
        })

    counts = Counter(x["classification"] for x in recommendations)
    required = [x for x in recommendations if x["classification"] == "REQUIRED_FOR_GOVERNED_RECORD"]
    assert len(required) == 44, len(required)
    assert all(x["requiredForRecommendedRecordIds"] for x in required)
    source_package = {
        "notice": NOTICE,
        "schemaVersion": "1.0.0",
        "packageType": "FUTURE_SOURCE_REGISTRATION_RECOMMENDATIONS",
        "authority": {"humanDecisionRequired": True, "sourceRegistrationPerformed": False, "canonicalRegistrationAuthorized": False},
        "counts": dict(sorted(counts.items())),
        "requiredFutureRegistrationCount": len(required),
        "futureRegistrationManifest": required,
        "recommendations": recommendations,
        "alignmentCaveats": [
            "The 64 source-overlap records remain controlling; reviews and included studies must not be counted twice.",
            "Shared datasets, preprint/publication pairs, and component reports are not independent replication.",
            "Theoretical and framework sources are not experimental evidence.",
            "Recorded access depth must remain explicit; abstract or selected-text access is not full-text extraction.",
            "Registration is conditional on later human approval of the mapped scientific record and is not authorized by this package.",
        ],
    }
    registered_manifest = DOCS / "PSYCHOLOGICAL_LAYER_SOURCE_REGISTRATION_MANIFEST.json"
    if registered_manifest.exists():
        registered = load(registered_manifest)
        source_package["postRecommendationStatus"] = {
            "recommended": "HISTORICAL_ADVISORY_PRESERVED",
            "humanApprovedRequiredOnly": True,
            "materialized": True,
            "registeredCount": registered["registeredCount"],
            "registrationManifest": "docs/governance/scale-up/PSYCHOLOGICAL_LAYER/PSYCHOLOGICAL_LAYER_SOURCE_REGISTRATION_MANIFEST.json",
            "activationAuthorized": False,
        }
    dump(DATA / "source-registration-recommendations.json", source_package)


def md_table(headers: list[str], rows: list[list[object]]) -> str:
    def clean(value):
        return str(value if value is not None else "—").replace("|", "\\|").replace("\n", " ")
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    out.extend("| " + " | ".join(clean(v) for v in row) + " |" for row in rows)
    return "\n".join(out)


def build_markdown(package: dict) -> None:
    sources = load(DATA / "source-registration-recommendations.json")
    c = package["compression"]
    decisions = {x["id"]: x for x in package["decisionUnits"]}
    grouped = [x for x in package["decisionUnits"] if x["tier"] == 1]
    rejections = [x for x in grouped if x["id"].startswith("GRP-REJ")]
    research = [x for x in grouped if x["id"].startswith("GRP-RN") or x["id"].startswith("GRP-ER-RN")]
    identities = package["happeningTypeIdentityRecommendations"]
    effects = package["effectAssertionRecommendations"]
    existing = package["existingRelationshipRecommendations"]

    lines = [
        "# Psychological Layer Governance Recommendations", "", f"> **{NOTICE}**", "",
        "This package recommends human decisions from the completed Psychological Layer audit. It performs no governance, activation, source registration, materialization, ontology edit, or production change.", "",
    ]
    if package.get("postRecommendationStatus"):
        status = package["postRecommendationStatus"]
        lines += [
            "## Recommendation lifecycle status", "",
            "| Stage | Status | Authority |", "| --- | --- | --- |",
            "| RECOMMENDED | Historical advisory preserved | This document and `governance-recommendations.json` |",
            f"| HUMAN APPROVED | Approved | `{status['humanDecisionId']}` / `PSYCHOLOGICAL_LAYER_GOVERNANCE_DECISION_001.md` |",
            f"| MATERIALIZED | 45 governed inactive records; 44 selectively registered sources | `{status['materializationId']}` |",
            "| ACTIVATED | No | Activation explicitly withheld |", "",
            "The present document remains the advisory rationale. The later decision record supplies human authority, and the materialization manifest records implementation. No advisory text has been retroactively converted into authority.", "",
        ]
    lines += [
        "## Executive summary", "",
        f"**595 original rows → {c['groupedHumanDecisions']} grouped human decisions + {c['individualScientificDecisions']} individual scientific decisions + {c['blockedDecisions']} blocked decisions.**", "",
        f"The package reconstructs **{c['distinctScientificDecisions']} distinct scientific decisions** and **{c['workflowLedgerAcknowledgements']} workflow/ledger acknowledgements**. The acknowledgements confirm completed Family search coverage and do not count as scientific votes. Every governance-index row maps to exactly one decision unit; repeated Family appearances and evidence dependencies do not create duplicate votes.", "",
        "Recommended future materialization, only after human authorization, is 1 Relationship, 29 HappeningTypes, 7 EffectAssertions, and 8 EvidenceAssessments. New GOVERNED remains 0; new ACTIVE remains 0; every current candidate remains NOT_ELIGIBLE.", "",
        "## Grouped approvals recommended", "",
        md_table(["Decision", "Recommendation", "Rows", "Basis"], [[x["id"], x["advisoryRecommendation"], len(x["rowIds"]), x["title"]] for x in grouped if x["advisoryRecommendation"] not in {"REJECT_HYPOTHESIS", "KEEP_RESEARCH_NEEDED"}]), "",
        "Identity approvals govern reusable operation identities only. They do not approve efficacy, implementation, activation, or practitioner use.", "",
        "## Grouped rejection recommendations", "",
        md_table(["Decision", "Rationale group", "Rows", "Sample checked"], [[x["id"], x["title"], len(x["rowIds"]), ", ".join(x["rowIds"][:3])] for x in rejections]), "",
        "All 151 rejected hypotheses retain their row-specific proposition and rationale in `governance-recommendations.json`. Any future change to a proposition or evidence base requires a new review rather than inheriting this grouped rejection.", "",
        "## Grouped research-needed recommendations", "",
        md_table(["Decision", "Rationale group", "Rows", "Recommendation"], [[x["id"], x["title"], len(x["rowIds"]), x["advisoryRecommendation"]] for x in research]), "",
        "These groups preserve 209 hypothesis-ledger conclusions and 36 existing-Relationship research-needed reviews. They do not create formal candidate records.", "",
        "## Existing Relationship proposals", "",
        md_table(["Recommendation", "Count"], [[k, v] for k, v in sorted(package["existingRelationshipCounts"].items())]), "",
        "Every revision, retype, and split proposal remains an individual Tier 2 decision. Approval means review the criticism and proposed direction; it does not mean the replacement is implementation-ready. No production Relationship changes in this package.", "",
        md_table(["Relationship", "Recommendation", "Current audit disposition"], [[x["id"], x["recommendation"], x["currentDisposition"]] for x in existing if "REVIEW_ONLY" in x["recommendation"]]), "",
        "## New Relationship candidate", "",
        "**REL-CAND-PSY-LAYER-0001 — APPROVE_AS_IS (future inactive governance only).**", "",
        package["newRelationshipRecommendation"]["exactBoundedSemantics"], "",
        "The exact endpoint is PSY-003 Belief Strength: confidence or commitment attached to the specified proposition. It is not objective truth, calibration, memory confidence, arbitrary persuasion, or behavior. Repetition is encounter with the same factual statement/headline before the later rating. Direction is context dependent rather than universally positive or monotonic. Population, timing, implausibility, task instruction, veracity-cue, and initial accuracy-focus boundaries remain explicit. The candidate and EA-CAND-PSY-LAYER-0001 are one shared contribution and must never be added as two effects. No duplicate production edge was found.", "",
        "## HappeningType identities", "",
        md_table(["Candidate", "Identity", "Recommendation", "Group"], [[x["id"], x["name"], x["recommendation"], x["decisionUnitId"]] for x in identities]), "",
        "Counts: 29 GOVERN_INACTIVE_IDENTITY; 0 merges; 0 research-needed; 0 rejects; 0 blocked. Population/context constraints remain with effects unless they define the reusable operation itself. Every identity retains source provenance and NOT_ELIGIBLE activation status.", "",
        "## EffectAssertions", "",
        md_table(["Candidate", "Operation", "Target", "Property/change", "Evidence", "Recommendation"], [[x["id"], x["typeId"], x["targetId"], f"{x['property']} / {x['change']}", f"{x['evidenceDisposition']} / {x['evidenceStrength']}", x["recommendation"]] for x in effects]), "",
        "The seven inactive-governance recommendations survive individual review because each has an exact Driver target, operation, property, direction/timing scope, manipulation alignment, and explicit null/contrary boundary. The other 23 remain research-needed. None directly targets an RDS or RelationalState. Statistical significance alone was not used as an approval rule.", "",
        "## EvidenceAssessment dependencies", "",
        "All 31 EvidenceAssessments remain dependencies rather than separate votes. Eight would accompany the one recommended Relationship and seven recommended EffectAssertions; 23 remain attached to research-needed effects. Synthesis remains 23 INSUFFICIENT, 7 MIXED, and 1 SUPPORTS. MIXED, null, contrary, access-depth, shared-dataset, review/component, and theory-versus-experiment qualifications remain explicit.", "",
        "## Construct/ontology questions", "",
        md_table(["Issue", "Classification", "Recommendation"], [[x["issue"], x["classification"], x["recommendation"]] for x in package["constructOntologyQuestions"]]), "",
        "## Architecture blockers", "",
    ]
    for block in package["architectureBlockers"]:
        lines += [f"### {block['id']} — {decisions[block['id']]['title']}", "", f"- **Exact issue:** {block['exactIssue']}", f"- **Affected candidates/entities:** {', '.join(block['affectedCandidatesOrEntities'])}", f"- **Materialization impact:** {block['materializationImpact']}", f"- **Safe current representation:** {block['safeCurrentRepresentation']}", f"- **Future governance:** {block['recommendedFutureGovernanceAction']}", ""]
    lines += [
        "## Future source registrations", "",
        f"Future registration manifest: **{sources['requiredFutureRegistrationCount']} candidate sources**, conditional on later human approval of the mapped records. Registration is not performed or authorized here. Ten registry entries are already canonical/reused. The 64 overlap issues remain controlling: reviews and included studies, shared datasets, and preprint/publication pairs are not independent replications; theoretical sources are not experiments; recorded access depth remains truthful.", "",
        "## Proposed future materialization set", "",
        md_table(["Record class", "Recommended future count"], [[k, v] for k, v in package["proposedFutureMaterialization"].items()]), "",
        "These are recommendations only. The set is conditional on human approval and the source-registration prerequisites. The Relationship and its related EffectAssertion share one contribution.", "",
        "## Explicit exclusions", "",
        "- No candidate was governed or activated.",
        "- No source was registered canonically.",
        "- No production Relationship, Driver, RDS, alias, crosswalk, definition, or architecture content changed.",
        "- No revision, retype, split, blocker resolution, or materialization was implemented.",
        "- No literature search, Family audit, or Actions & Events search ledger was rerun.", "",
        "## Activation boundary", "",
        "**NO ACTIVATION recommendation is authorized by this review.** All candidates remain NOT_ELIGIBLE. Human approval of inactive scientific governance would still require a separate, explicit materialization step; activation requires its own governed decision and is outside this package.", "",
    ]
    (DOCS / "PSYCHOLOGICAL_LAYER_GOVERNANCE_RECOMMENDATIONS.md").write_text("\n".join(lines), encoding="utf-8")

    priority = ["REL-CAND-PSY-LAYER-0001"] + [f"EA-CAND-PSY-LAYER-{n:04d}" for n in sorted(APPROVED_EFFECT_NUMBERS)] + [
        "IND-REL-PSY-002", "IND-REL-PSY-037", "IND-REL-PSY-052", "IND-REL-PSY-065",
        "BLK-PSY-001", "BLK-PSY-002", "BLK-PSY-003",
    ]
    summary = [
        "# Psychological Layer Governance Review Summary", "", f"> **{NOTICE}**", "",
        "This is an independent recommendation pass over the completed audit package. It does not enact any decision.", "",
    ]
    if package.get("postRecommendationStatus"):
        status = package["postRecommendationStatus"]
        summary += [
            "## Recommendation lifecycle status", "",
            f"RECOMMENDED is preserved as this historical advisory; HUMAN APPROVED is recorded by `{status['humanDecisionId']}`; MATERIALIZED is recorded by `{status['materializationId']}` as 45 governed inactive records. ACTIVATED remains no.", "",
        ]
    summary += [
        "## Compression result", "",
        f"**595 original rows → {c['groupedHumanDecisions']} grouped human decisions + {c['individualScientificDecisions']} individual scientific decisions + {c['blockedDecisions']} blocked decisions.**", "",
        md_table(["Measure", "Count"], [["Original governance rows", 595], ["Distinct scientific decisions", c["distinctScientificDecisions"]], ["Grouped human decisions", c["groupedHumanDecisions"]], ["Individual scientific decisions", c["individualScientificDecisions"]], ["Blocked decisions", c["blockedDecisions"]], ["Workflow/ledger acknowledgements", c["workflowLedgerAcknowledgements"]]]), "",
        "Scientific votes are the 148 grouped, individual, and blocked decision units. The 14 Family ledger acknowledgements only confirm completed search coverage and require no scientific vote.", "",
        "## Recommendation totals", "",
        md_table(["Area", "Recommendations"], [
            ["Existing Relationships", ", ".join(f"{k}={v}" for k, v in sorted(package["existingRelationshipCounts"].items()))],
            ["New Relationship", "REL-CAND-PSY-LAYER-0001 = APPROVE_AS_IS"],
            ["HappeningType identities", "29 govern inactive; 0 merge; 0 research-needed; 0 reject; 0 blocked"],
            ["EffectAssertions", "7 govern inactive as-is; 0 modify; 23 research-needed; 0 reject; 0 blocked"],
            ["EvidenceAssessments", "8 future dependencies; 23 retained with research-needed effects"],
            ["Sources", f"{sources['requiredFutureRegistrationCount']} conditional future registrations; none registered"],
        ]), "",
        "## Human priorities", "",
        "Read these individual decisions most closely:", "",
    ]
    priority_labels = {
        "REL-CAND-PSY-LAYER-0001": "Repeated exposure → Belief Strength, including the shared-contribution rule",
        "EA-CAND-PSY-LAYER-0001": "Repeated-claim effect; mixed evidence and same contribution as the Relationship",
        "EA-CAND-PSY-LAYER-0002": "Explanatory refutation → Belief Strength",
        "EA-CAND-PSY-LAYER-0003": "Response-contingent noise termination → perceived task control",
        "EA-CAND-PSY-LAYER-0005": "Virtual exclusion → immediate perceived exclusion",
        "EA-CAND-PSY-LAYER-0007": "Bounded homework choice → task interest",
        "EA-CAND-PSY-LAYER-0012": "Delayed retrieval practice → recall, preserving the five-minute contrary result",
        "EA-CAND-PSY-LAYER-0023": "High-control health recommendation → perceived freedom threat",
        "IND-REL-PSY-002": "Retype review involving semantically consequential endpoint classification",
        "IND-REL-PSY-037": "Split review whose component claims require separate evidence allocation",
        "IND-REL-PSY-052": "Split review whose component claims require separate evidence allocation",
        "IND-REL-PSY-065": "Retype review involving semantically consequential endpoint classification",
        "BLK-PSY-001": "Feature/dimension representation architecture",
        "BLK-PSY-002": "PSY-130 state/trait definition-timing discrepancy",
        "BLK-PSY-003": "Belief Strength versus Metacognitive Confidence boundary",
    }
    summary.extend([f"{i}. **{pid}:** {priority_labels[pid]}" for i, pid in enumerate(priority, 1)])
    summary += ["", "## Validation boundary", "", "The structured package contains one account for each governance-index row, all 45 REVIEW_READY lifecycle-bearing records, every high-priority row, the three blocked questions, and a source manifest whose required entries map only to recommended future governed records. Focused integrity and protected-science checks must pass after generation. Linux and Windows CI must pass after commit.", "", "## Authority boundary", "", "New GOVERNED = 0. New ACTIVE = 0. Production remains unchanged. Candidate lifecycle remains unchanged. PR #24 remains open and unmerged. Human authorization is required before any governance, registration, materialization, or activation.", ""]
    (DOCS / "PSYCHOLOGICAL_LAYER_GOVERNANCE_REVIEW_SUMMARY.md").write_text("\n".join(summary), encoding="utf-8")


if __name__ == "__main__":
    main()
