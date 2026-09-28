"""Build the read-only WP-PSG-005 decision-test package deterministically."""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DOC = ROOT / "docs/governance/post-scale-up/rds-causal-source"
DATA = ROOT / "data/governance/post-scale-up/rds-causal-source"
sys.path.insert(0, str(HERE))
from runtime import evaluate  # noqa: E402

RDS_SOURCES = ["SOC-024", "SOC-041", "SOC-052", "SOC-053", "SOC-054", "SOC-055", "SOC-056", "SOC-074", "SOC-076", "SOC-096"]
ROOT_CASE_SOURCES = {"BIO-003", "CUL-088", "INS-039", "INS-103", *RDS_SOURCES}
DECISION_ID = "DP-PSG-005"


def read(path: str) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def write_json(name: str, value: Any) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def write_doc(name: str, value: str) -> None:
    DOC.mkdir(parents=True, exist_ok=True)
    (DOC / name).write_text(value.strip() + "\n", encoding="utf-8", newline="\n")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


entities_list = read("data/entities.json")
entities = {row["id"]: row for row in entities_list}
rds = {key: row for key, row in entities.items() if row.get("entityType") == "RELATIONAL_DERIVED_STATE"}
rel_payload = read("data/relationships.json")
relationship_rows = []
for collection in ("relationships", "deprecatedRelationships", "relationshipCandidates"):
    for row in rel_payload[collection]:
        relationship_rows.append((collection, row))
relationships = {row["id"]: row for _, row in relationship_rows}
sources = {row["id"]: row for row in read("data/sources.json")["sources"]}
profiles = read("data/rds-computation-v1/profiles.json")["profiles"]
bindings = read("data/rds-computation-v1/bindings.json")["bindings"]
cross_mappings = read("data/cross-level-exposure-v1/mappings.json")["mappings"]
cross_bindings = read("data/cross-level-exposure-v1/bindings.json")["bindings"]
derivation_bindings = read("data/relational-state-v1/catalog.json")["bindings"]
native_contribution_by_rds = {
    row["targetRds"]["id"]: {
        "contributionIdentity": row.get("sharedContributionIdentity"),
        "contributionPolicy": row.get("contributionPolicy"),
        "derivationId": row["id"],
        "derivationRevision": row["revision"],
    }
    for row in derivation_bindings
}


def review_registry(layer: str) -> dict[str, Any]:
    mapping = {
        "Biological": "BIOLOGICAL_LAYER",
        "Cultural": "CULTURAL_LAYER",
        "Social": "SOCIAL_LAYER",
        "Informational": "INFORMATIONAL_LAYER",
        "Institutional / Structural": "INSTITUTIONAL_STRUCTURAL_LAYER",
    }
    folder = mapping.get(layer)
    if not folder:
        return {}
    path = ROOT / f"data/candidates/actions-events-v1/{folder}/relationship-review-registry.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def typology(row: dict[str, Any]) -> str:
    dtype = row.get("derivationType")
    name = row.get("name", "").lower()
    if row.get("networkMetricSpecification") or dtype == "NETWORK_METRIC":
        return "NETWORK_TOPOLOGY_METRIC"
    if dtype == "RATIO":
        return "RATIO_OR_RATE"
    if dtype in {"DISTANCE", "DIFFERENCE", "FIT"}:
        return "DISTANCE_OR_SIMILARITY"
    if any(token in name for token in ("prevalence", "count", "network size")):
        return "AGGREGATE_COUNT_OR_PREVALENCE"
    if any(token in name for token in ("adequacy", "capacity", "pressure")):
        return "CAPACITY_OR_ADEQUACY_INDEX"
    if row.get("layer") in {"Social", "Cultural", "Institutional / Structural"} and row.get("entitySubtype") == "RELATIONAL_STATE":
        return "CONTEXTUAL_GROUP_STATE"
    if dtype in {"COMPOSITE", "INDEX", "WEIGHTED_SUM"}:
        return "DETERMINISTIC_COMPOSITE"
    if dtype in {"LATENT", "ESTIMATED"}:
        return "LATENT_OR_ESTIMATED_CONSTRUCT"
    return "OTHER_DERIVED_SUMMARY"


def profile_for(rds_id: str) -> tuple[list[str], list[str]]:
    p = [f"{row['profileId']}@{row['profileVersion']}" for row in profiles if row.get("rdsId") == rds_id]
    b = [f"{row['bindingId']}@{row['bindingVersion']}" for row in bindings if row.get("rdsId") == rds_id]
    return p, b


def current_review(rel: dict[str, Any]) -> str:
    registry = review_registry(entities[rel["subjectEntityId"]]["layer"])
    return registry.get(rel["id"], {}).get("disposition", "NOT_SEPARATELY_REVIEWED")


ROOT_BLOCKER_BY_SOURCE = {
    "BIO-003": "ASTRA-BIO-LAYER-001",
    "CUL-088": "ASTRA-CUL-LAYER-001",
    "INS-039": "ASTRA-INS-LAYER-001",
    "INS-103": "ASTRA-INS-LAYER-002",
    **{source_id: "ASTRA-SOC-LAYER-001" for source_id in RDS_SOURCES},
}


inventory = []
for collection, rel in relationship_rows:
    source = entities.get(rel.get("subjectEntityId"))
    if not source or source.get("entityType") != "RELATIONAL_DERIVED_STATE":
        continue
    target = entities.get(rel.get("objectEntityId"), {})
    p, b = profile_for(source["id"])
    inventory.append({
        "rdsSourceId": source["id"], "rdsName": source["name"], "layer": source["layer"],
        "rdsTypology": typology(source), "targetId": rel.get("objectEntityId"),
        "targetType": target.get("entityType", rel.get("objectEntityType")),
        "sourceLevel": rel.get("subjectLevel"), "targetLevel": rel.get("objectLevel"), "relationshipId": rel["id"],
        "relationFamily": rel.get("relationFamily"), "predicate": rel.get("predicate"),
        "currentLifecycle": rel.get("governanceStatus"), "currentReviewDisposition": current_review(rel),
        "recordStatus": {"relationships": "PRODUCTION", "deprecatedRelationships": "DEPRECATED_PRODUCTION", "relationshipCandidates": "CANDIDATE"}[collection],
        "d10Gate": "HEIGHTENED_RDS_TO_DRIVER_REVIEW" if rel.get("relationFamily") == "CAUSAL" and target.get("entityType") == "DRIVER" else ("EXCEPTIONAL_RDS_TO_RDS_REVIEW" if rel.get("relationFamily") == "CAUSAL" and target.get("entityType") == "RELATIONAL_DERIVED_STATE" else "NOT_APPLICABLE_NONCAUSAL"),
        "existingContributionControl": native_contribution_by_rds.get(source["id"]),
        "profileReferences": p, "bindingReferences": b,
        "crossLevelDependency": rel.get("subjectLevel") != rel.get("objectLevel") if rel.get("subjectLevel") and rel.get("objectLevel") else None,
        "crossLevelMappingReferences": [f"{m['mappingId']}@{m['mappingVersion']}" for m in cross_mappings if any(x.get("relationshipId") == rel["id"] for x in cross_bindings)],
        "networkStateDependency": bool(source.get("networkMetricSpecification")),
        "evidenceReferences": rel.get("supportingEvidenceIds", []),
        "causalSourceEligible": False,
    })
inventory.sort(key=lambda x: (x["rdsSourceId"], x["relationshipId"]))


def route_case(rel_id: str, status: str, source_assessment: str, evidence: str, planning: list[str], deep: bool = False) -> dict[str, Any]:
    rel = relationships[rel_id]
    source = entities[rel["subjectEntityId"]]
    target = entities[rel["objectEntityId"]]
    p, b = profile_for(source["id"])
    return {
        "relationshipId": rel_id, "sourceId": source["id"], "sourceName": source["name"],
        "rootBlockerId": ROOT_BLOCKER_BY_SOURCE[source["id"]],
        "targetId": target["id"], "targetName": target["name"], "typology": typology(source),
        "sourceLevel": rel.get("subjectLevel"), "targetLevel": rel.get("objectLevel"),
        "currentReviewDisposition": current_review(rel), "architectureFinding": source_assessment,
        "scientificEvidenceFinding": evidence, "executionProfileFinding": "EXACT_PROFILE_AVAILABLE" if p else "NO_EXACT_PROFILE_BINDING",
        "advisoryStatus": status, "planningClassifications": planning, "deepResearch": deep,
        "supportingEvidenceIds": rel.get("supportingEvidenceIds", []), "profileReferences": p, "bindingReferences": b,
        "productionDispositionChanged": False, "causalSourceEligible": False,
    }


case_assessments = [
    route_case("REL-BIO-001", "BLOCKED_MULTIPLE_VERSIONS", "The alignment construct can support a coherent phase/schedule contrast, but the current broad aggregate does not bind one version.", "Forced-desynchrony evidence supports circadian phase effects on sleep propensity and consolidation; current Relationship sources do not isolate the exact BIO-003 to sleep-duration proposition.", ["NEEDS_PROFILE_DEFINITION", "NEEDS_CONTRIBUTION_RECONCILIATION", "NEEDS_TARGETED_CAUSAL_RESEARCH", "MULTIPLE_DEPENDENCIES"], True),
    route_case("REL-CUL-042", "BLOCKED_MULTIPLE_VERSIONS", "Distance is a many-to-one summary; equal distance can encode directionally different profile changes.", "Canonical reviews support cultural dynamics generally, not the exact distance-to-entrenchment causal contrast.", ["NEEDS_PROFILE_DEFINITION", "NEEDS_CONSTITUENT_MAPPING", "NEEDS_TARGETED_CAUSAL_RESEARCH", "MULTIPLE_DEPENDENCIES"], True),
    route_case("REL-INS-017", "BLOCKED_TARGET_CONTAMINATION", "Caseload pressure uses staffing capacity, while the target explicitly includes staffing as part of service-delivery capacity.", "Canonical sources support workload/coping theory, but do not identify an independent aggregate effect at these exact endpoints.", ["NEEDS_CONSTITUENT_MAPPING", "NEEDS_CONTRIBUTION_RECONCILIATION", "NEEDS_TARGETED_CAUSAL_RESEARCH", "MULTIPLE_DEPENDENCIES"], True),
    route_case("REL-INS-036", "BLOCKED_MULTIPLE_VERSIONS", "Equal adequacy ratios can arise from more staff, less workload, or different skill/labor-time composition.", "Staffing interventions can have causal effects, but existing evidence does not identify the broad adequacy-ratio effect on territorial reach.", ["NEEDS_PROFILE_DEFINITION", "NEEDS_CONSTITUENT_MAPPING", "NEEDS_TARGETED_CAUSAL_RESEARCH", "MULTIPLE_DEPENDENCIES"], True),
    route_case("REL-SOC-017", "BLOCKED_TARGET_CONTAMINATION", "Network size and provider availability can share the same alter/provider membership and require exact Network State identity.", "No exact causal contrast separates additional eligible alters from realized support availability.", ["NEEDS_NETWORK_STATE_BINDING", "NEEDS_CONSTITUENT_MAPPING", "NEEDS_TARGETED_CAUSAL_RESEARCH"], False),
    route_case("REL-SOC-029", "BLOCKED_DEFINITIONAL_OVERLAP", "Hierarchy steepness and participation equality can be co-summaries of the same interaction distribution.", "General hierarchy evidence does not identify this exact aggregate-to-aggregate-like participation contrast.", ["NEEDS_CONSTITUENT_MAPPING", "NEEDS_TARGETED_CAUSAL_RESEARCH"], False),
    route_case("REL-SOC-031", "DERIVATION_ONLY", "Density and clustering are same-state topology summaries; changing one statistic is not a state intervention.", "The route is already a retype candidate and lacks an independent causal mechanism.", ["DERIVATION_ONLY", "NEEDS_NETWORK_STATE_BINDING"], False),
    route_case("REL-SOC-035", "BLOCKED_NETWORK_STATE", "Clustering can be a contextual abstraction only after a topology transformation, exposure route, and contribution identity are exact.", "A randomized network experiment supports effects of topology on adoption, but does not isolate the current scalar clustering-to-reinforcement claim.", ["NEEDS_NETWORK_STATE_BINDING", "NEEDS_EXPOSURE_MAPPING", "NEEDS_CONTRIBUTION_RECONCILIATION", "NEEDS_TARGETED_CAUSAL_RESEARCH", "MULTIPLE_DEPENDENCIES"], True),
    route_case("REL-SOC-032", "DERIVATION_ONLY", "Assortativity and segregation reuse a mixing structure and baseline; metric-to-metric causality is not identified.", "Canonical causal-inference review warns selection and influence are confounded.", ["DERIVATION_ONLY", "NEEDS_NETWORK_STATE_BINDING"], False),
    route_case("REL-SOC-033", "DERIVATION_ONLY", "Constraint and cross-cluster ties reuse adjacency/partition information.", "No separately identified aggregate mechanism is present.", ["DERIVATION_ONLY", "NEEDS_NETWORK_STATE_BINDING"], False),
    route_case("REL-SOC-034", "DERIVATION_ONLY", "Cross-cluster tie prevalence and segregation are alternate summaries of the same bounded graph/partition.", "No independent temporal causal proposition is supported.", ["DERIVATION_ONLY", "NEEDS_NETWORK_STATE_BINDING"], False),
    route_case("REL-SOC-046", "INSUFFICIENT_CAUSAL_EVIDENCE", "Goal alignment could be a contextual group state, but its versions, episode, and contribution overlap need binding.", "Team-process reviews and goal experiments support plausibility, not the exact aggregate source claim as currently represented.", ["READY_FOR_SOURCE_GOVERNANCE_REVIEW", "NEEDS_CONSTITUENT_MAPPING", "NEEDS_TARGETED_CAUSAL_RESEARCH"], True),
    route_case("REL-SOC-075", "BLOCKED_DEFINITIONAL_OVERLAP", "Expectation alignment and collective efficacy may share member expectation/judgment content.", "Current review evidence does not separate measurement overlap from causal effect.", ["NEEDS_CONSTITUENT_MAPPING", "NEEDS_TARGETED_CAUSAL_RESEARCH"], False),
    route_case("REL-SOC-060", "INSUFFICIENT_CAUSAL_EVIDENCE", "Status inequality could be contextual, but its difference versions and contact mechanism require exact specification.", "Current reviews support hierarchy/threat broadly, not the exact inequality-to-contact-quality effect.", ["NEEDS_CONSTITUENT_MAPPING", "NEEDS_TARGETED_CAUSAL_RESEARCH"], False),
    route_case("REL-SOC-067", "BLOCKED_EXPOSURE_MAPPING", "Status inequality is group context; person fairness requires actual contextual exposure semantics.", "No exact contextual causal identification or production mapping exists for this route.", ["NEEDS_EXPOSURE_MAPPING", "NEEDS_CONTRIBUTION_RECONCILIATION", "NEEDS_TARGETED_CAUSAL_RESEARCH", "MULTIPLE_DEPENDENCIES"], False),
]


test_cases = [
    {"caseId": "PURE_DERIVATION", "input": {"exactConstruct": True, "derivationOnly": True, "temporalOrder": True, "evidenceClass": "DEFINITIONAL_CALCULATIONAL", "profileAvailable": True}, "expected": "DERIVATION_ONLY"},
    {"caseId": "COMPUTABLE_NOT_CAUSAL", "input": {"exactConstruct": True, "derivationOnly": True, "temporalOrder": True, "evidenceClass": "DEFINITIONAL_CALCULATIONAL", "profileAvailable": True}, "expected": "DERIVATION_ONLY"},
    {"caseId": "PROFILE_ABSENT_SCIENCE_COHERENT", "input": {"exactConstruct": True, "distinctMechanism": True, "independentMechanismClaimed": True, "temporalOrder": True, "evidenceClass": "DIRECT_AGGREGATE_INTERVENTION", "profileAvailable": False}, "expected": "ELIGIBLE_FOR_INDEPENDENT_CAUSAL_REVIEW"},
    {"caseId": "TARGET_CONTAMINATION", "input": {"exactConstruct": True, "targetContaminated": True, "temporalOrder": True, "evidenceClass": "PROSPECTIVE_LONGITUDINAL_WITH_TEMPORAL_ORDER"}, "expected": "BLOCKED_TARGET_CONTAMINATION"},
    {"caseId": "RATIO_MULTIPLE_VERSIONS", "fixture": {"versionA": {"staff": 10, "workload": 100, "ratio": 0.1}, "versionB": {"staff": 20, "workload": 200, "ratio": 0.1}}, "input": {"exactConstruct": True, "multipleVersionsUnresolved": True, "temporalOrder": True, "evidenceClass": "QUASI_EXPERIMENTAL_CONTEXTUAL_EFFECT"}, "expected": "BLOCKED_MULTIPLE_VERSIONS"},
    {"caseId": "DISTANCE_MULTIPLE_VERSIONS", "fixture": {"origin": [0, 0], "profileA": [1, 0], "profileB": [0, 1], "euclideanDistanceA": 1.0, "euclideanDistanceB": 1.0}, "input": {"exactConstruct": True, "multipleVersionsUnresolved": True, "temporalOrder": True, "evidenceClass": "MULTILEVEL_ASSOCIATIONAL"}, "expected": "BLOCKED_MULTIPLE_VERSIONS"},
    {"caseId": "NETWORK_MANY_TO_ONE", "fixture": {"nodes": ["A", "B", "C", "D"], "graphAEdges": [["A", "B"], ["B", "C"], ["A", "C"]], "graphBEdges": [["A", "B"], ["B", "C"], ["C", "D"]], "densityA": 0.5, "densityB": 0.5, "topologyDifference": "TRIANGLE_PLUS_ISOLATE_VS_PATH"}, "input": {"exactConstruct": True, "networkDerived": True, "networkStateBinding": False, "temporalOrder": True, "evidenceClass": "GROUP_OR_CONTEXT_RANDOMIZATION"}, "expected": "BLOCKED_NETWORK_STATE"},
    {"caseId": "CONSTITUENT_DOUBLE_COUNT", "input": {"exactConstruct": True, "contributionOverlap": "UNRESOLVED", "distinctMechanism": True, "independentMechanismClaimed": True, "temporalOrder": True, "evidenceClass": "NATURAL_EXPERIMENT"}, "expected": "BLOCKED_CONTRIBUTION_OVERLAP"},
    {"caseId": "ALTERNATE_ABSTRACTION", "input": {"exactConstruct": True, "alternateAbstraction": True, "contributionOverlap": "RESOLVED_SELECT_ONE", "temporalOrder": True, "evidenceClass": "PROSPECTIVE_LONGITUDINAL_WITH_TEMPORAL_ORDER"}, "expected": "ALTERNATE_ABSTRACTION_ONLY"},
    {"caseId": "CONTEXTUAL_POSITIVE", "input": {"exactConstruct": True, "contextual": True, "distinctMechanism": True, "independentMechanismClaimed": True, "contributionOverlap": "RESOLVED_INDEPENDENT", "temporalOrder": True, "crossLevel": True, "exposureMapping": True, "evidenceClass": "GROUP_OR_CONTEXT_RANDOMIZATION", "profileAvailable": True}, "expected": "ELIGIBLE_FOR_CONTEXTUAL_CAUSAL_REVIEW"},
    {"caseId": "CROSS_LEVEL_NO_MAPPING", "input": {"exactConstruct": True, "contextual": True, "distinctMechanism": True, "independentMechanismClaimed": True, "temporalOrder": True, "crossLevel": True, "exposureMapping": False, "evidenceClass": "GROUP_OR_CONTEXT_RANDOMIZATION"}, "expected": "BLOCKED_EXPOSURE_MAPPING"},
    {"caseId": "TEMPORAL_ORDER_MISSING", "input": {"exactConstruct": True, "distinctMechanism": True, "independentMechanismClaimed": True, "temporalOrder": False, "evidenceClass": "NATURAL_EXPERIMENT"}, "expected": "BLOCKED_TEMPORAL_ORDER"},
    {"caseId": "COHERENT_SOURCE_INSUFFICIENT_RELATIONSHIP_EVIDENCE", "input": {"exactConstruct": True, "distinctMechanism": True, "independentMechanismClaimed": True, "temporalOrder": True, "evidenceClass": "CROSS_SECTIONAL_ASSOCIATIONAL", "profileAvailable": True}, "expected": "INSUFFICIENT_CAUSAL_EVIDENCE"},
]
for case in test_cases:
    case["result"] = evaluate(case["input"])


all_screen = []
for rid, row in sorted(rds.items()):
    outgoing = [item for item in inventory if item["rdsSourceId"] == rid]
    p, b = profile_for(rid)
    all_screen.append({
        "rdsId": rid, "name": row["name"], "layer": row["layer"], "typology": typology(row),
        "exactDefinitionStatus": "DEFINED_CURRENT_ENTITY", "profileStatus": "EXACT_PROFILE_AND_BINDING" if p and b else "NO_EXACT_PROFILE_BINDING",
        "outgoingRouteCount": len(outgoing), "outgoingCausalRouteCount": sum(x["relationFamily"] == "CAUSAL" for x in outgoing),
        "obviousDerivationOnly": bool(outgoing) and all(x["relationFamily"] != "CAUSAL" for x in outgoing),
        "existingContributionControl": native_contribution_by_rds.get(rid),
        "rootProgramRelevance": rid in ROOT_CASE_SOURCES, "causalSourceEligible": False,
    })


decision_tree = {
    "schemaVersion": "1.0.0", "decisionPacket": DECISION_ID, "default": "DERIVATION_ONLY_OR_INELIGIBLE",
    "steps": [
        {"order": 1, "gate": "EXACT_CONSTRUCT", "fail": "BLOCKED_EXACT_CONSTRUCT_UNDEFINED"},
        {"order": 2, "gate": "COMPUTATION_MEASUREMENT_CONTRACT", "fail": "BLOCKED_PROFILE_UNDEFINED_FOR_EXECUTION_ONLY"},
        {"order": 3, "gate": "DEFINITIONAL_TAUTOLOGICAL_OVERLAP", "fail": "BLOCKED_DEFINITIONAL_OVERLAP_OR_TARGET_CONTAMINATION"},
        {"order": 4, "gate": "WELL_DEFINED_CAUSAL_CONTRAST", "fail": "BLOCKED_MULTIPLE_VERSIONS"},
        {"order": 5, "gate": "CONTRIBUTION_INDEPENDENCE", "fail": "BLOCKED_CONTRIBUTION_OVERLAP"},
        {"order": 6, "gate": "MECHANISM_DISTINCTION", "fail": "BLOCKED_NO_DISTINCT_MECHANISM"},
        {"order": 7, "gate": "TEMPORAL_ORDER", "fail": "BLOCKED_TEMPORAL_ORDER"},
        {"order": 8, "gate": "LEVEL_EXPOSURE", "fail": "BLOCKED_EXPOSURE_MAPPING"},
        {"order": 9, "gate": "NETWORK_STATE", "fail": "BLOCKED_NETWORK_STATE"},
        {"order": 10, "gate": "EMPIRICAL_IDENTIFICATION", "fail": "INSUFFICIENT_CAUSAL_EVIDENCE"},
        {"order": 11, "gate": "SCOPE_TRANSPORT", "fail": "BLOCKED_SCOPE_MISMATCH"},
        {"order": 12, "gate": "SPECIFIC_RELATIONSHIP_VALIDITY", "fail": "RELATIONSHIP_NOT_SUPPORTED"},
        {"order": 13, "gate": "EXECUTION_PROFILE", "fail": "NOT_EXECUTABLE_NO_PROFILE"},
        {"order": 14, "gate": "SEPARATE_HUMAN_GOVERNANCE", "fail": "PRODUCTION_AUTHORITY_DENIED"},
    ],
    "invariants": {"causalSourceEligible": False, "autoActivate": False, "relationshipMutation": False},
}


research_ledger = [
    {"referenceId": "PLAN-METHOD-001", "case": "REUSABLE_CONTRACT", "question": "How should multiple aggregate versions be handled?", "title": "Causal Inference Under Multiple Versions of Treatment", "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC4219328/", "design": "AUTHORITATIVE_METHODS", "accessDepth": "FULL_TEXT", "finding": "An aggregate value may conceal versions with different potential outcomes; versions or their assignment distribution must be specified.", "limitations": "Method does not establish case-specific causality."},
    {"referenceId": "PLAN-METHOD-002", "case": "COMPOSITES", "question": "Can constructed measures support causal interpretation?", "title": "Constructed Measures and Causal Inference", "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC8614532/", "design": "AUTHORITATIVE_METHODS", "accessDepth": "FULL_TEXT", "finding": "Composite measures can sometimes receive a causal interpretation through explicit underlying versions, but unknown versions impede intervention and identification.", "limitations": "Does not validate any PSYWERX composite."},
    {"referenceId": "PLAN-METHOD-003", "case": "CAUSAL_ABSTRACTION", "question": "Can macro variables be causal?", "title": "Multi-Level Cause-Effect Systems", "url": "https://proceedings.mlr.press/v51/chalupka16.html", "design": "CAUSAL_METHODS", "accessDepth": "FULL_PAPER", "finding": "Macro causal variables can be coherent when linked to experimental micro-level interventions and stable causal partitions.", "limitations": "The formal result does not establish empirical evidence for repository routes."},
    {"referenceId": "PLAN-METHOD-004", "case": "NETWORK", "question": "What is required for network interventions?", "title": "Causal Inference for Social Network Data", "url": "https://doi.org/10.1080/01621459.2022.2131557", "design": "NETWORK_CAUSAL_METHODS", "accessDepth": "FULL_PAPER", "finding": "Network causal estimands require explicit interventions on treatment or network structure and handling of interference; a scalar metric alone is not the intervention.", "limitations": "No PSYWERX route is identified by this methods paper."},
    {"referenceId": "PLAN-BIO-001", "case": "BIO-003_REL-BIO-001", "question": "Does circadian phase affect sleep propensity independently of time awake?", "title": "Paradoxical timing of the circadian rhythm of sleep propensity serves to consolidate sleep and wakefulness in humans", "url": "https://doi.org/10.1016/0304-3940(94)90841-9", "design": "FORCED_DESYNCHRONY_LAB", "accessDepth": "ABSTRACT", "finding": "Forced desynchrony separates circadian and homeostatic processes and supports a circadian contribution to sleep consolidation.", "limitations": "Eight men; sleep propensity/consolidation is not identical to broad sleep duration."},
    {"referenceId": "PLAN-BIO-002", "case": "BIO-003_REL-BIO-001", "question": "Does homeostatic pressure modify the circadian effect?", "title": "Sleep restriction masks the influence of the circadian process on sleep propensity", "url": "https://pubmed.ncbi.nlm.nih.gov/22621352/", "design": "FORCED_DESYNCHRONY_CONTROLLED", "accessDepth": "ABSTRACT", "finding": "Circadian modulation was pronounced under a normal sleep-wake ratio and masked under severe restriction, demonstrating version and interaction dependence.", "limitations": "Male laboratory sample; does not identify the repository's broad aggregate contrast."},
    {"referenceId": "PLAN-CUL-001", "case": "CUL-088_REL-CUL-042", "question": "Is scalar cultural distance causally interpretable?", "title": "Toward a more in-depth measurement of cultural distance", "url": "https://doi.org/10.1177/14705958221089192", "design": "MEASUREMENT_METHODS", "accessDepth": "ABSTRACT_AND_METHOD_SUMMARY", "finding": "Distance magnitude alone omits dimension, direction, symmetry and context, producing ambiguous interpretations.", "limitations": "Country-level international-business construct, not adjacent-generation norm entrenchment directly."},
    {"referenceId": "PLAN-INS-001", "case": "INS-039_INS-103", "question": "Can staffing ratios identify causal effects?", "title": "How do hospitals respond to input regulation? Evidence from the California nurse staffing mandate", "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC10712346/", "design": "QUASI_EXPERIMENTAL_POLICY", "accessDepth": "FULL_TEXT", "finding": "A defined staffing mandate changed staffing time and multiple organizational margins, including capacity, showing that the intervention version matters beyond a scalar ratio.", "limitations": "Hospital nursing does not establish territorial administrative reach or generic service capacity."},
    {"referenceId": "PLAN-INS-002", "case": "INS-103_REL-INS-036", "question": "Do ratio changes yield uniform outcomes?", "title": "The effect of a hospital nurse staffing mandate on patient health outcomes", "url": "https://doi.org/10.1016/j.jhealeco.2012.01.005", "design": "QUASI_EXPERIMENTAL_POLICY", "accessDepth": "ABSTRACT", "finding": "The mandate changed ratios but did not yield relative improvements in measured safety outcomes, cautioning against treating ratio movement as a uniform mechanism.", "limitations": "Outcome and institutional setting differ from the PSYWERX target."},
    {"referenceId": "PLAN-SOC-001", "case": "SOC-053_REL-SOC-035", "question": "Can topology affect adoption?", "title": "The spread of behavior in an online social network experiment", "url": "https://doi.org/10.1126/science.1185231", "design": "RANDOMIZED_NETWORK_EXPERIMENT", "accessDepth": "CANONICAL_SOURCE_ABSTRACT", "finding": "Randomized network structures can change behavioral diffusion, supporting a topology-level causal question when the exact treatment and exposure are specified.", "limitations": "The manipulation is topology, not an isolated scalar local-clustering intervention."},
    {"referenceId": "PLAN-SOC-002", "case": "SOC-074_REL-SOC-046", "question": "Can a group-level goal condition affect cooperation or performance?", "title": "The effect of group-level performance goals on group performance", "url": "https://doi.org/10.1207/s15327043hup0601_3", "design": "GROUP_LEVEL_EXPERIMENT", "accessDepth": "ABSTRACT", "finding": "Assigned group goals affected performance conditionally through coordination and action planning, supporting a bounded group-context question.", "limitations": "The manipulation is an assigned group goal, not the repository's measured goal-alignment aggregate or cooperation-prevalence endpoint."},
]


deep_case_reviews = [
    {
        "caseId": "BIO-003_REL-BIO-001", "question": "Can circadian alignment independently affect sleep duration rather than only summarize phase and schedule?",
        "sourceRdsId": "BIO-003", "targetId": "BIO-001", "relationshipId": "REL-BIO-001",
        "causalContrast": "A specified shift of sleep opportunity relative to measured circadian phase, holding the sleep-opportunity window and prior wake history explicit.",
        "unitOfAnalysis": "PERSON", "timeScope": "Bounded forced-desynchrony or schedule-shift episode", "sourceLevel": "PERSON", "targetLevel": "PERSON",
        "candidateMechanism": "Circadian phase-dependent sleep propensity and consolidation interacting with homeostatic pressure.",
        "constituents": ["internal circadian phase", "sleep/work/meal/light schedule", "prior wake and sleep opportunity"],
        "currentContributionRoutes": ["REL-BIO-001"], "currentEvidence": ["SRC006", "SRC007", "SRC008"], "newPlanningSources": ["PLAN-BIO-001", "PLAN-BIO-002"],
        "sourceQualityAccessDepth": "Controlled forced-desynchrony studies; abstracts reviewed; small male laboratory samples.", "causalDesignClass": "DIRECT_AGGREGATE_INTERVENTION_APPROXIMATION",
        "supportingFindings": "Circadian phase has an effect separable from elapsed wake time on sleep propensity/consolidation.",
        "nullOrContraryFindings": "Severe sleep restriction masks circadian modulation, so effects are not invariant across versions.",
        "limitations": "The repository aggregate combines several alignment domains and the target is broad sleep duration; no exact executable contrast/profile exists.",
        "remainingUncertainty": "Which alignment component and intervention policy defines the source without overlap or double count.", "decisionTestResult": "BLOCKED_MULTIPLE_VERSIONS",
    },
    {
        "caseId": "CUL-088_REL-CUL-042", "question": "Can scalar adjacent-generation cultural distance act as a causal source for norm entrenchment?",
        "sourceRdsId": "CUL-088", "targetId": "CUL-061", "relationshipId": "REL-CUL-042",
        "causalContrast": "A direction- and dimension-specific change between adjacent generation profiles within one cultural community.",
        "unitOfAnalysis": "COMMUNITY", "timeScope": "Specified adjacent-generation interval", "sourceLevel": "COMMUNITY", "targetLevel": "COMMUNITY",
        "candidateMechanism": "Intergenerational mismatch could alter transmission, contestation, or reinforcement of a focal norm.",
        "constituents": ["values", "norms", "practices", "identity narratives", "distance metric and direction"],
        "currentContributionRoutes": ["REL-CUL-042"], "currentEvidence": ["SRC276", "SRC306"], "newPlanningSources": ["PLAN-CUL-001"],
        "sourceQualityAccessDepth": "Measurement-methods review at abstract/method-summary depth.", "causalDesignClass": "MEASUREMENT_AND_ASSOCIATIONAL",
        "supportingFindings": "Cultural-distance measurement requires dimension, direction, symmetry, and context.",
        "nullOrContraryFindings": "Equal scalar distance does not imply equal profile change or mechanism.",
        "limitations": "No exact derivation or aggregate-level causal identification for the repository route.",
        "remainingUncertainty": "Whether a dimension-specific contrast can be defined without embedding the target norm.", "decisionTestResult": "BLOCKED_MULTIPLE_VERSIONS",
    },
    {
        "caseId": "INS-039_REL-INS-017", "question": "Can caseload pressure independently affect service-delivery capacity?",
        "sourceRdsId": "INS-039", "targetId": "INS-063", "relationshipId": "REL-INS-017",
        "causalContrast": "A specified demand change, staffing/time change, or policy that alters caseload pressure while separately defining service capacity.",
        "unitOfAnalysis": "INSTITUTIONAL_FIELD", "timeScope": "Bounded service-delivery window", "sourceLevel": "INSTITUTIONAL_FIELD", "targetLevel": "INSTITUTIONAL_FIELD",
        "candidateMechanism": "Workload pressure may reduce attention, throughput, quality, or implementation reliability.",
        "constituents": ["service demand", "available actor time", "staffing"],
        "currentContributionRoutes": ["REL-INS-017"], "currentEvidence": ["SRC380", "SRC381", "SRC386"], "newPlanningSources": ["PLAN-INS-001"],
        "sourceQualityAccessDepth": "Quasi-experimental staffing-policy study at full-text depth; canonical repository sources inspected.", "causalDesignClass": "QUASI_EXPERIMENTAL_CONTEXTUAL_EFFECT",
        "supportingFindings": "Defined staffing regulation changes multiple operational margins and demonstrates that input interventions can affect capacity.",
        "nullOrContraryFindings": "The source and target both use staffing/capacity content, creating circular overlap in the current definitions.",
        "limitations": "Evidence does not identify the exact caseload-pressure aggregate independently of its constituents.",
        "remainingUncertainty": "Whether a noncontaminated target and explicit intervention version can be specified.", "decisionTestResult": "BLOCKED_TARGET_CONTAMINATION",
    },
    {
        "caseId": "INS-103_REL-INS-036", "question": "Can staffing adequacy independently enable territorial administrative reach?",
        "sourceRdsId": "INS-103", "targetId": "INS-107", "relationshipId": "REL-INS-036",
        "causalContrast": "A specified staffing intervention, workload intervention, or skill-composition policy producing a bound adequacy change.",
        "unitOfAnalysis": "INSTITUTIONAL_FIELD", "timeScope": "Bounded administrative deployment window", "sourceLevel": "INSTITUTIONAL_FIELD", "targetLevel": "INSTITUTIONAL_FIELD",
        "candidateMechanism": "Qualified deployable labor can extend the institution's consistent geographic administration.",
        "constituents": ["qualified personnel", "deployable labor time", "assigned workload", "skill composition"],
        "currentContributionRoutes": ["REL-INS-036"], "currentEvidence": ["SRC380", "SRC381", "SRC401"], "newPlanningSources": ["PLAN-INS-001", "PLAN-INS-002"],
        "sourceQualityAccessDepth": "Quasi-experimental policy studies at full-text and abstract depth.", "causalDesignClass": "QUASI_EXPERIMENTAL_POLICY",
        "supportingFindings": "Mandates can move staffing ratios and organizational responses.",
        "nullOrContraryFindings": "Ratio changes did not produce uniform downstream outcome improvements.",
        "limitations": "Hospital staffing is not territorial administration; equal ratios can reflect different staff, workload, and skill versions.",
        "remainingUncertainty": "The intervention policy, reference workload, skill mix, and mechanism needed for an invariant contrast.", "decisionTestResult": "BLOCKED_MULTIPLE_VERSIONS",
    },
    {
        "caseId": "SOC-053_REL-SOC-035", "question": "Can local clustering function as a contextual source for social reinforcement multiplicity?",
        "sourceRdsId": "SOC-053", "targetId": "SOC-061", "relationshipId": "REL-SOC-035",
        "causalContrast": "An exact topology transformation on a bound graph that changes neighborhood closure while retaining state, boundary, window, and exposure semantics.",
        "unitOfAnalysis": "SMALL_GROUP", "timeScope": "Specified network-state and behavioral-response windows", "sourceLevel": "SMALL_GROUP", "targetLevel": "SMALL_GROUP",
        "candidateMechanism": "Closed neighborhoods can create redundant independent reinforcement exposures.",
        "constituents": ["node set", "neighbor tie set", "tie type", "boundary", "window"],
        "currentContributionRoutes": ["REL-SOC-035"], "currentEvidence": ["SRC235", "SRC256"], "newPlanningSources": ["PLAN-METHOD-004", "PLAN-SOC-001"],
        "sourceQualityAccessDepth": "Randomized network experiment and network-causal methods literature.", "causalDesignClass": "RANDOMIZED_NETWORK_EXPERIMENT",
        "supportingFindings": "Randomly assigned network topology can alter diffusion behavior.",
        "nullOrContraryFindings": "The experiment does not isolate a scalar local-clustering intervention or the exact reinforcement-multiplicity endpoint.",
        "limitations": "Identical clustering values can hide different topologies and actor exposures.",
        "remainingUncertainty": "Exact state transition, exposure mapping, contribution identity, and route-specific evidence.", "decisionTestResult": "BLOCKED_NETWORK_STATE",
    },
    {
        "caseId": "SOC-074_REL-SOC-046", "question": "Can goal alignment function as a contextual group source for cooperation prevalence?",
        "sourceRdsId": "SOC-074", "targetId": "SOC-034", "relationshipId": "REL-SOC-046",
        "causalContrast": "A specified collective-episode intervention that aligns member goals without defining cooperation as part of alignment.",
        "unitOfAnalysis": "SMALL_GROUP", "timeScope": "Specified collective episode", "sourceLevel": "SMALL_GROUP", "targetLevel": "SMALL_GROUP",
        "candidateMechanism": "Shared goal direction can support coordination and reduce effort conflict.",
        "constituents": ["member stated or revealed goals", "episode definition", "alignment function"],
        "currentContributionRoutes": ["REL-SOC-046"], "currentEvidence": relationships["REL-SOC-046"].get("supportingEvidenceIds", []), "newPlanningSources": ["PLAN-SOC-002"],
        "sourceQualityAccessDepth": "Group-level experiment at abstract depth plus canonical repository evidence.", "causalDesignClass": "GROUP_OR_CONTEXT_RANDOMIZATION_APPROXIMATION",
        "supportingFindings": "Assigned group goals can affect group performance through coordination/action planning.",
        "nullOrContraryFindings": "Effects are conditional; assigned goals are not the same construct as measured goal alignment.",
        "limitations": "The exact alignment aggregate, contribution overlap, and cooperation-prevalence endpoint are not identified.",
        "remainingUncertainty": "Whether an episode-specific contrast and independent contribution can be supported.", "decisionTestResult": "INSUFFICIENT_CAUSAL_EVIDENCE",
    },
]


consumers = [
    {"consumer": "Relationship validation", "futureImpact": "SOURCE_GATE_AWARE", "requirement": "Keep D10; require exact advisory mode/decision record without changing current validity."},
    {"consumer": "Graph assembly / FCM", "futureImpact": "CENTRAL_FAIL_CLOSED_GATE", "requirement": "Require governed source authorization plus contribution resolution before inclusion."},
    {"consumer": "Simulation", "futureImpact": "EXECUTION_AND_PROFILE_AWARE", "requirement": "Require exact profile/binding, source authorization, temporal context and no double count."},
    {"consumer": "Scenario service", "futureImpact": "DISPLAY_ONLY_UNTIL_GOVERNED", "requirement": "May show advisory status; must not infer execution."},
    {"consumer": "RDS computation", "futureImpact": "NO_CAUSAL_BEHAVIOR_CHANGE", "requirement": "Computability remains separate from causal-source eligibility."},
    {"consumer": "Contribution resolver", "futureImpact": "SOURCE_MODE_AWARE", "requirement": "Select one for alternate abstractions; require independent status for additive routes."},
    {"consumer": "Cross-level exposure resolver", "futureImpact": "MAPPING_AWARE", "requirement": "Require exact mapping/binding for contextual cross-level routes."},
    {"consumer": "Network State runtime", "futureImpact": "STATE_REFERENCE_AWARE", "requirement": "Keep state transition/recalculation noncausal; expose exact state identity to a separately governed claim."},
]


option_results = {
    "A": {"result": "INSUFFICIENT_ALONE", "strengths": ["clear contrast and mechanism"], "limitations": ["literal manipulability would reject legitimate contextual causes", "does not itself solve cross-level exposure or double counting"]},
    "B": {"result": "NECESSARY_EXCEPTION_PATH_NOT_DEFAULT", "strengths": ["supports group/network/institutional contexts", "uses exact exposure mappings"], "limitations": ["ecological inference risk", "depends on contribution and actual-exposure controls"]},
    "C": {"result": "SAFE_DEFAULT_INCOMPLETE_AS_BLANKET_RULE", "strengths": ["lowest false-positive risk", "simple rollback"], "limitations": ["would exclude identified higher-level contexts and valid causal abstractions"]},
    "A+B": {"result": "NEEDS_DEFAULT_FIREWALL"}, "A+C": {"result": "MISSES_CONTEXTUAL_PATH"},
    "B+C": {"result": "MISSES_SAME_LEVEL_INDEPENDENT_PATH"}, "A+B+C": {"result": "VIABLE_IF_C_IS_DEFAULT_AND_A_B_ARE_GATED_EXCEPTIONS"},
    "recommended": "C_DEFAULT_WITH_BOUNDED_A_AND_B_EXCEPTION_PATHWAYS",
}


handoffs = {
    "WP-PSG-001": "Exact profile/binding is an execution gate, not a scientific causal gate.",
    "WP-PSG-002": "Contextual cross-level sources require exact mapping/binding and actual exposure.",
    "WP-PSG-003": "Network RDS require state ID/revision/hash, boundary, window, tie definition, and intervention class.",
    "WP-PSG-004": "Alternate abstractions require select-one; independent aggregates require explicit independence resolution.",
    "futureStageE": "Build isolated validator for the governed reusable contract.",
    "futureStageG": ["BIO/Cultural high-information cases", "Institutional ratios/capacity", "Social network/context aggregates"],
}


protected_paths = [
    "data/entities.json", "data/drivers.json", "data/relationships.json", "data/relationship-intervention-v1/relationships.json",
    "data/actions-events-v1/catalog.json", "data/rds-computation-v1/profiles.json", "data/rds-computation-v1/bindings.json",
    "data/contribution-control-v1/groups.json", "data/relational-state-v1/catalog.json",
    "data/cross-level-exposure-v1/mappings.json", "data/cross-level-exposure-v1/bindings.json", "data/sources.json",
    "scripts/build_relationships.py", "scripts/actions_events_v1.py", "scripts/rds_computation_v1.py",
    "scripts/contribution_control_v1.py", "scripts/relational_state_v1.py", "scripts/cross_level_exposure_v1.py",
    "scenario-service/src/openai-service.js",
]
protected = {path: sha(ROOT / path) for path in protected_paths}


write_json("rds-source-inventory.json", {"schemaVersion": "1.0.0", "total": len(inventory), "countsByRelationFamily": dict(sorted(Counter(x["relationFamily"] for x in inventory).items())), "countsByLayer": dict(sorted(Counter(x["layer"] for x in inventory).items())), "routes": inventory})
write_json("rds-source-test-cases.json", {"schemaVersion": "1.0.0", "cases": test_cases, "productionMutationAuthorized": False})
planning_classification_counts = Counter(
    classification for case in case_assessments for classification in case["planningClassifications"]
)
write_json("rds-source-case-assessments.json", {
    "schemaVersion": "1.0.0",
    "caseCount": len(case_assessments),
    "rootBlockers": sorted({case["rootBlockerId"] for case in case_assessments}),
    "planningClassificationCounts": dict(sorted(planning_classification_counts.items())),
    "cases": case_assessments,
})
write_json("rds-source-all-rds-screen.json", {"schemaVersion": "1.0.0", "rdsCount": len(all_screen), "counts": {"withOutgoingRoutes": sum(x["outgoingRouteCount"] > 0 for x in all_screen), "withOutgoingCausalRoutes": sum(x["outgoingCausalRouteCount"] > 0 for x in all_screen), "withExactProfileBinding": sum(x["profileStatus"] == "EXACT_PROFILE_AND_BINDING" for x in all_screen), "obviousDerivationOnlyWithRoutes": sum(x["obviousDerivationOnly"] for x in all_screen), "rootProgramRelevant": sum(x["rootProgramRelevance"] for x in all_screen)}, "records": all_screen})
write_json("rds-source-decision-tree.json", decision_tree)
write_json("rds-source-consumer-impact.json", {"schemaVersion": "1.0.0", "consumers": consumers, "productionIntegrationAuthorized": False})
write_json("rds-source-research-ledger.json", {"schemaVersion": "1.0.0", "references": research_ledger, "caseReviews": deep_case_reviews, "newProductionSourcesRegistered": 0})
write_json("rds-source-handoffs.json", {"schemaVersion": "1.0.0", "handoffs": handoffs, "optionResults": option_results, "protectedHashes": protected, "causalSourceEligibilityChanges": 0})


gates = "\n".join(f"{row['order']}. **{row['gate']}** — fail closed as `{row['fail']}`." for row in decision_tree["steps"])
case_lines = "\n".join(f"- `{x['sourceId']}` → `{x['targetId']}` (`{x['relationshipId']}`): **{x['advisoryStatus']}**. Source class: {x['architectureFinding']} Evidence: {x['scientificEvidenceFinding']} Execution: {x['executionProfileFinding']}." for x in case_assessments)
social_lines = "\n".join(f"- `{sid}`: " + "; ".join(f"`{x['relationshipId']}` → **{x['advisoryStatus']}**" for x in case_assessments if x["sourceId"] == sid) for sid in RDS_SOURCES)
approval = "Approve the bounded WP-PSG-005 reusable RDS causal-source eligibility contract tested in DP-PSG-005: retain DERIVATION_ONLY or INELIGIBLE as the default; permit only separately governed exception review for a well-defined independent aggregate contrast, a contribution-safe alternate causal abstraction selected instead of its constituents, or an explicitly mapped contextual aggregate exposure; and require exact construct, overlap, contrast/version, mechanism, temporal, level/exposure, Network State, aggregate-specific evidence, scope, Relationship, execution-profile, D10, contribution-resolution, and separate human-governance gates. This authorizes architecture direction and optional non-production validator prototyping only. It does not authorize any individual RDS, causalSourceEligible=true, activation, graph or simulation execution, Relationship or RDS mutation, new Relationships or EffectAssertions, production ContributionGroups, source registration, lifecycle change, production migration, or WP-PSG-009 work."

write_doc("RDS_CAUSAL_SOURCE_ELIGIBILITY_CONTRACT.md", f"""
# RDS causal-source eligibility contract

Status: advisory decision-test output; no RDS is authorized.

## Default and source modes

The default is `DERIVATION_ONLY` or `INELIGIBLE`. A boolean remains the correct final production authority firewall, but it is too coarse for review. Advisory decision records need `DERIVATION_ONLY`, `ALTERNATE_CAUSAL_ABSTRACTION`, `INDEPENDENT_AGGREGATE_CAUSAL_SOURCE`, and `CONTEXTUAL_AGGREGATE_CAUSAL_SOURCE`, plus blocked states. None confers execution.

## Gate sequence

{gates}

Source-class coherence, specific-Relationship evidence, computational execution, and governance/activation are four separate determinations. D10 remains additive: RDS-to-Driver is heightened review and RDS-to-RDS is exceptional review. Direct RDS-target EffectAssertions remain prohibited.
""")

write_doc("RDS_CAUSAL_SOURCE_EVIDENCE_STANDARD.md", """
# RDS causal-source evidence standard

Evidence must identify the aggregate or contextual contrast itself. Preferred designs are direct aggregate interventions, group/context randomization, natural experiments, strong quasi-experiments, or prospective longitudinal designs with clear temporal order. Multilevel association, cross-sectional association, prediction, statistical significance, constituent evidence, mechanistic plausibility, and calculation alone are insufficient.

Every assessment separates exact source, target, contrast, unit, time, levels, mechanism, constituents, contribution overlap, evidence design, contrary/null findings, transport limits, profile availability, and production authority. Multiple versions must be bound or assigned by an explicit stochastic policy. Computability never upgrades evidence, and missing profiles affect execution rather than scientific coherence.

Planning references are listed in `rds-source-research-ledger.json`; no new production source was registered.
""")

write_doc("RDS_CAUSAL_SOURCE_CASE_REVIEWS.md", f"""
# RDS causal-source case reviews

These are advisory architecture/evidence findings. Production records and dispositions remain unchanged.

## Blocker and route findings

{case_lines}

## Social ten-source review

{social_lines}

Deep external review was bounded to `BIO-003`, `CUL-088`, `INS-039`, `INS-103`, `SOC-053`, and `SOC-074`. Other Social routes received corpus-grounded gap classification. `SOC-096` has two causal Relationships, so the ten sources produce eleven Social causal routes.
""")

screen_counts = Counter(x["typology"] for x in all_screen)
write_doc("RDS_CAUSAL_SOURCE_ALL_RDS_SCREEN.md", f"""
# All-41 RDS mechanical screen

The corpus contains 41 RDS. {sum(x['outgoingRouteCount'] > 0 for x in all_screen)} have at least one outgoing record, {sum(x['outgoingCausalRouteCount'] > 0 for x in all_screen)} have a causal-source record, {sum(x['profileStatus'] == 'EXACT_PROFILE_AND_BINDING' for x in all_screen)} has an exact production computation profile/binding, and {sum(x['obviousDerivationOnly'] for x in all_screen)} with outgoing records are mechanically noncausal-only.

Typology counts: {', '.join(f'`{k}`={v}' for k, v in sorted(screen_counts.items()))}.

The screen is intentionally cheap. It surfaces route presence, definition, profile, obvious noncausal status, and root-program relevance; it does not adjudicate the 41 constructs.
""")

write_doc("RDS_CAUSAL_SOURCE_OPTION_COMPARISON.md", """
# RDS causal-source option comparison

| Criterion | A: independent contrast | B: contextual exposure | C: prohibit | C default + bounded A/B |
|---|---|---|---|---|
| Scientific fidelity | Strong for exact same-level contrasts | Strong for real higher-level contexts | Rejects all higher-level causal use | Strongest when every exception passes exact gates |
| Causal interpretability | Requires intervention policy and mechanism | Requires context, mechanism, and actual exposure | Simple noncausal interpretation | Explicitly separates independent, contextual, alternate, and derivational modes |
| Constituent double-count prevention | Incomplete alone | Incomplete alone | Prevents by prohibition | Requires WP-PSG-004 independent or select-one resolution |
| Contextual-causality support | Limited | Core strength | None | B-like exception only |
| Network-metric support | Only with exact topology intervention | Only with state and exposure binding | Descriptive/recalculation only | Requires WP-PSG-003 state, transformation, boundary, and window |
| Ratio/composite handling | Good if versions are bound | Possible for contextual ratios | Always derivational | Multiple versions fail closed unless explicitly resolved |
| Cross-level safety | Does not supply exposure semantics | Depends on WP-PSG-002 | Safe by prohibition | Exact mapping and actual exposure required |
| Temporal clarity | Must be specified | Context and response windows required | No causal ordering needed | Mandatory source-before-target gate |
| Execution clarity | Profile still separate | Profile still separate | Computation only | Science, Relationship evidence, execution, and governance remain separate |
| Migration burden | Medium | High | Low | Low default; case-specific exception records only |
| Consumer clarity | Ambiguous without modes | Ambiguous without modes | Simple | Rich advisory mode plus unchanged boolean authority firewall |
| False-positive risk | Medium | High if ecological inference leaks | Lowest | Low through default prohibition and fail-closed gates |
| False-negative risk | High if manipulability is literal | Lower for contexts | Highest | Bounded by exception pathways |
| Rollback safety | Case record removal | Case record/mapping removal | Highest | High because no production behavior changes in this decision test |

“Manipulable” should mean a well-defined causal contrast or intervention policy, not necessarily a literal single treatment. Alternate abstraction is a separate non-additive mode: aggregate or constituents, never both.
""")

write_doc("RDS_CAUSAL_SOURCE_CONSUMER_IMPACT.md", "# RDS causal-source consumer impact\n\n" + "\n".join(f"- **{x['consumer']} — {x['futureImpact']}:** {x['requirement']}" for x in consumers) + "\n\nNo consumer integration is authorized. Minimal future architecture is a versioned eligibility decision record plus existing profile, contribution, exposure, and state references; no RDS schema field is required to govern the reusable contract. The production boolean remains the final execution firewall.\n")

write_doc("RDS_CAUSAL_SOURCE_DECISION_TEST.md", f"""
# Aggregate RDS causal-source independence decision test

Work package `WP-PSG-005`; root `ROOT-RDS-CAUSAL-SOURCE-001`; packet `DP-PSG-005`.

## Mechanical result

The authoritative corpus contains 41 RDS and {len(inventory)} distinct RDS-source records: {dict(sorted(Counter(x['relationFamily'] for x in inventory).items()))}. There are {sum(x['relationFamily'] == 'CAUSAL' for x in inventory)} causal records. The five root blocker families account for {len(case_assessments)} exact causal Relationships across 14 RDS sources; the Social ten-source set has eleven causal routes.

## Scientific result

The test falsifies a single permissive aggregate rule. Ratio, distance, network, composite, and contextual constructs fail for different reasons. A derived aggregate can still be a coherent causal abstraction, but only when its intervention/version semantics, mechanism, evidence, contribution identity, level exposure, and state binding are explicit. Statistical adjustment or predictive value cannot substitute for those conditions.

## Recommendation

Adopt C as the default firewall with bounded A-like independent-aggregate and B-like contextual exceptions. Add an alternate-abstraction path governed by select-one contribution control. Keep `causalSourceEligible=false` until each individual route passes separate scientific and production governance.

## Skeptical review

The recommended rule was challenged with equal ratios from different numerator/denominator states, equal cultural distances from different dimensions, equal network densities from different topologies, target-contaminated indices, aggregate-plus-constituent duplication, and contextual ecological inference. It blocks every unresolved case. It also passes a synthetic group-randomized contextual case with explicit lower-level exposure and independent contribution resolution, so it is not a blanket ban. Computation-profile availability never changes scientific status; a coherent source with weak Relationship evidence remains scientifically distinct from an executable, supported Relationship. External consumers still need an exact governed decision record and the central contribution resolver, so metadata alone cannot make an aggregate additive.

## Protection

All {len(protected)} protected files are hashed in `rds-source-handoffs.json`. No production science, eligibility, lifecycle, activation, graph, simulation, source, ontology, profile, mapping, state, Relationship, EffectAssertion, or ContributionGroup changed.
""")

write_doc("RDS_CAUSAL_SOURCE_ARCHITECTURE_DECISION_PACKET.md", f"""
# RDS causal-source architecture decision packet

Decision packet: `DP-PSG-005`. Human decision status: `REQUIRED_NOT_TAKEN`.

## Recommended architecture

Govern `C_DEFAULT_WITH_BOUNDED_A_AND_B_EXCEPTION_PATHWAYS`, including a non-additive alternate-abstraction path. Preserve the production boolean as the final authority firewall and use richer immutable decision records for review semantics.

## Rejected directions

- A alone: too strict if “manipulable” is literal and incomplete for cross-level contexts.
- B alone: too permissive without default derivational firewall and contribution control.
- C as blanket prohibition: scientifically overbroad.
- A/B/C as peer choices: lacks safe default ordering.

## Safeguards

All fourteen decision gates, D10, direct RDS-target EffectAssertion prohibition, exact-version references, WP-PSG-004 select-one/independence resolution, WP-PSG-002 mapping, WP-PSG-003 state identity, and separate case governance remain mandatory.

## Exact bounded approval statement

{approval}
""")

print(json.dumps({"rds": len(all_screen), "rdsSourceRecords": len(inventory), "causalRecords": sum(x["relationFamily"] == "CAUSAL" for x in inventory), "blockerRoutes": len(case_assessments), "recommendation": option_results["recommended"], "causalEligibilityChanges": 0}, indent=2))
