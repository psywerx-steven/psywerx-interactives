"""Build the read-only WP-PSG-002 architecture decision-test package."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from contract import LEVELS, ROUTES, assess_eligibility, validate_mapping

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/governance/post-scale-up/cross-level"
DOCS = ROOT / "docs/governance/post-scale-up/cross-level"
SOC_QUEUE = ROOT / "data/candidates/actions-events-v1/SOCIAL_LAYER/astra-escalation-queue.json"
INS_QUEUE = ROOT / "data/candidates/actions-events-v1/INSTITUTIONAL_STRUCTURAL_LAYER/astra-escalation-queue.json"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def write_doc(name: str, text: str) -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / name).write_text(text.strip() + "\n", encoding="utf-8", newline="\n")


def file_hash(path: Path) -> str:
    # Git may materialize text with CRLF on Windows and LF on Linux. The
    # protection gate compares scientific content, so canonicalize line endings
    # before hashing rather than treating checkout policy as a mutation.
    canonical = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(canonical).hexdigest()


def mapping(identifier, relationship, source_level, target_level, route, exposure, *, implementation=True, perception=False, perception_entity=None, network=False, intermediates=None, happenings=None):
    return {
        "schemaVersion": "0.1.0-PROTOTYPE",
        "mappingId": identifier,
        "mappingVersion": "1.0.0-TEST",
        "relationshipId": relationship["id"],
        "sourceEntityId": relationship["subjectEntityId"],
        "sourceLevel": source_level,
        "targetEntityId": relationship["objectEntityId"],
        "targetLevel": target_level,
        "routeType": route,
        "membershipRule": "Membership identifies a possible risk set only; it never establishes exposure.",
        "eligibilityRule": "Eligibility identifies possible coverage only; receipt/exposure must be established separately.",
        "implementationRequired": implementation,
        "implementationRequirement": "Specified source state must be realized in practice for the bounded target unit." if implementation else "Persistent source context; no discrete implementation event required.",
        "exposureDefinition": exposure,
        "exposureUnit": "DEFINED_TARGET_UNIT",
        "exposureWindow": "BOUNDED_TO_THE_RELATIONSHIP_EVIDENCE_WINDOW",
        "coverageRule": "PARTIAL_COVERAGE_ALLOWED_ONLY_WITH_EXPLICIT_INCLUDED_TARGET_SET_OR_RULE",
        "perceptionRequired": perception,
        "perceptionEntityId": perception_entity,
        "intermediateEntityIds": intermediates or [],
        "happeningTypeIds": happenings or [],
        "contextRequirements": ["SOURCE_SCOPE", "TARGET_SCOPE", "IMPLEMENTATION_OR_CONTEXT", "ACTUAL_EXPOSURE", "TIME_ALIGNMENT"],
        "temporalOrder": ["SOURCE_STATE", "IMPLEMENTATION_OR_TRANSMISSION", "ACTUAL_EXPOSURE", "PERSON_OR_LOWER_LEVEL_RESPONSE"],
        "evidenceReferences": relationship.get("supportingEvidenceIds", []),
        "scopeLimitations": ["Architecture routing only", "No ecological or atomistic inference", "No lifecycle, weight, activation or causal authority"],
        "networkStateDependency": network,
        "causalEvidence": False,
        "executionAuthority": False,
        "provenance": {"workPackageId": "WP-PSG-002", "decisionPacketId": "DP-PSG-002", "sourceRelationshipReviewOnly": True},
        "prototypeStatus": "NON_PRODUCTION_DECISION_TEST",
    }


def main() -> None:
    social = next(row for row in read(SOC_QUEUE) if row["id"] == "ASTRA-SOC-LAYER-002")
    institutional = next(row for row in read(INS_QUEUE) if row["id"] == "ASTRA-INS-LAYER-003")
    assert len(social["affectedRecords"]) == 20 and len(institutional["affectedRecords"]) == 21
    affected_ids = sorted(set(social["affectedRecords"]) | set(institutional["affectedRecords"]))
    assert len(affected_ids) == 38 and sorted(set(social["affectedRecords"]) & set(institutional["affectedRecords"])) == ["REL-INS-046", "REL-INS-047", "REL-INS-048"]
    relationships = read(ROOT / "data/relationships.json")["relationships"]
    by_id = {row["id"]: row for row in relationships}
    assert set(affected_ids) <= set(by_id)
    social_reviews = read(ROOT / "data/candidates/actions-events-v1/SOCIAL_LAYER/relationship-review-registry.json")
    institutional_reviews = read(ROOT / "data/candidates/actions-events-v1/INSTITUTIONAL_STRUCTURAL_LAYER/relationship-review-registry.json")

    categories = {
        "MAPPING_LIKELY_REQUIRED": {"REL-INS-040", "REL-INS-041", "REL-INS-042", "REL-INS-043", "REL-INS-044", "REL-INS-045", "REL-INS-046", "REL-INS-047", "REL-INS-048", "REL-INS-050", "REL-SOC-067", "REL-SOC-073", "REL-SOC-074"},
        "EXISTING_BRIDGE_SUFFICIENT": {"REL-ENV-042", "REL-INS-051", "REL-INS-052", "REL-INS-053", "REL-INS-054"},
        "METADATA_ONLY_MAY_SUFFICE": {"REL-INS-049", "REL-RDS-0008"},
        "NETWORK_STATE_DEPENDENCY": {"REL-SOC-017", "REL-SOC-035", "REL-TEC-050"},
        "CONSTRUCT_ONTOLOGY_DEPENDENCY": set(),
        "RESEARCH_NEEDED_BEFORE_MAPPING": {"REL-INS-056", "REL-TEC-063"},
        "NO_CROSS_LEVEL_PROBLEM_AFTER_REVIEW": {"REL-RDS-0005", "REL-RDS-0010", "REL-RDS-0011", "REL-RDS-0012", "REL-SOC-029", "REL-SOC-030", "REL-SOC-045", "REL-SOC-046", "REL-SOC-054", "REL-SOC-055", "REL-SOC-060", "REL-SOC-072", "REL-SOC-075"},
    }
    flat = set().union(*categories.values())
    assert flat == set(affected_ids) and sum(len(rows) for rows in categories.values()) == 38
    reasons = {
        "MAPPING_LIKELY_REQUIRED": "A genuine level transition needs bounded implementation/context and target-exposure semantics before later re-adjudication.",
        "EXISTING_BRIDGE_SUFFICIENT": "The current target Driver already names the system-level realized state; retain it and require claim-specific route metadata rather than inventing plumbing entities.",
        "METADATA_ONLY_MAY_SUFFICE": "The proposition is realization/corpus scope rather than person exposure; bounded Relationship metadata may be enough.",
        "NETWORK_STATE_DEPENDENCY": "Network structure or a network-derived state cannot establish personal exposure without exact Network State and later WP-PSG-003/005 handling.",
        "CONSTRUCT_ONTOLOGY_DEPENDENCY": "A construct identity decision would be prerequisite; none of the 38 is assigned here after review.",
        "RESEARCH_NEEDED_BEFORE_MAPPING": "The exact causal route remains too weak or reciprocal to specify a truthful mapping.",
        "NO_CROSS_LEVEL_PROBLEM_AFTER_REVIEW": "The record is same-level or noncausal semantic/derivational; the root queue must not force a cross-level migration.",
    }
    category_by_id = {identifier: category for category, identifiers in categories.items() for identifier in identifiers}
    migration_rows = []
    for identifier in affected_ids:
        row = by_id[identifier]
        review = social_reviews.get(identifier) or institutional_reviews.get(identifier) or {}
        migration_rows.append({
            "relationshipId": identifier,
            "subjectEntityId": row["subjectEntityId"],
            "objectEntityId": row["objectEntityId"],
            "currentSubjectLevel": row.get("subjectLevel"),
            "currentObjectLevel": row.get("objectLevel"),
            "relationFamily": row.get("relationFamily"),
            "currentReviewDisposition": review.get("disposition", "NOT_REVIEWED_IN_LAYER_REGISTRY"),
            "classification": category_by_id[identifier],
            "reason": reasons[category_by_id[identifier]],
            "productionMutationAuthorized": False,
        })
    migration_counter = Counter(row["classification"] for row in migration_rows)
    migration = {
        "schemaVersion": "0.1.0-PROTOTYPE", "workPackageId": "WP-PSG-002", "rootIssueId": "ROOT-CROSS-LEVEL-EXPOSURE-001",
        "sourceQueueCounts": {"ASTRA-SOC-LAYER-002": 20, "ASTRA-INS-LAYER-003": 21, "overlap": 3, "distinct": 38},
        "counts": {category: migration_counter.get(category, 0) for category in categories}, "records": migration_rows,
    }

    def real(identifier):
        return by_id[identifier]

    synthetic_network = {"id": "SYN-REL-NETWORK-PERSON-001", "subjectEntityId": "RDS-0006", "objectEntityId": "SYN-PERSON-OPPORTUNITY", "supportingEvidenceIds": []}
    synthetic_objective = {"id": "SYN-REL-SANCTION-PERSON-001", "subjectEntityId": "SYN-GROUP-SANCTION-CLIMATE", "objectEntityId": "SYN-PERSON-RESOURCE-LOSS", "supportingEvidenceIds": []}
    synthetic_ecological = {"id": "SYN-REL-INSTITUTION-AVERAGE-001", "subjectEntityId": "SYN-INSTITUTION-SCORE", "objectEntityId": "SYN-PERSON-OUTCOME", "supportingEvidenceIds": []}
    synthetic_assignment = {"id": "SYN-REL-ASSIGNMENT-PERSON-001", "subjectEntityId": "SYN-INSTITUTION-ASSIGNMENT", "objectEntityId": "SYN-PERSON-CONTACT-STATE", "supportingEvidenceIds": []}
    mappings = [
        mapping("XLEM-TEST-INS-040", real("REL-INS-040"), "INSTITUTION", "PERSON", "IMPLEMENTATION", "The specified person encounters the implemented impartial procedure and evaluates that process.", perception=True, perception_entity="PSY-022"),
        mapping("XLEM-TEST-INS-046", real("REL-INS-046"), "INSTITUTION", "GROUP", "RESOURCE_ACCESS", "The specified groups receive institutionally allocated resources within the bounded field.", perception=False),
        mapping("XLEM-TEST-SOC-067", real("REL-SOC-067"), "GROUP", "PERSON", "AMBIENT_CONTEXT", "The specified member experiences the bounded intergroup status context relevant to the fairness judgment.", implementation=False, perception=True, perception_entity="PSY-022"),
        mapping("XLEM-TEST-NETWORK-001", synthetic_network, "NETWORK", "PERSON", "NETWORK_POSITION", "The specified person's position in the exact Network State changes their opportunity set.", implementation=False, network=True),
        mapping("XLEM-TEST-INS-044", real("REL-INS-044"), "INSTITUTION", "PERSON", "MONITORING", "The surveillance mandate is implemented and the specified person is actually subject to monitoring.", perception=True, perception_entity="PSY-108"),
        mapping("XLEM-TEST-INS-050", real("REL-INS-050"), "INSTITUTION", "GROUP", "ELIGIBILITY", "Eligible members receive and can use the implemented formal voice opportunity."),
        mapping("XLEM-TEST-OBJECTIVE-001", synthetic_objective, "GROUP", "PERSON", "SANCTION_EXPOSURE", "The specified person receives an objective sanction consequence.", perception=False),
        mapping("XLEM-TEST-ECOLOGICAL-001", synthetic_ecological, "INSTITUTION", "PERSON", "AMBIENT_CONTEXT", "The person is demonstrably exposed to the bounded institution-level context.", implementation=False),
        mapping("XLEM-TEST-ASSIGNMENT-001", synthetic_assignment, "INSTITUTION", "PERSON", "ASSIGNMENT", "The specified person is assigned to and receives the bounded contact condition.", happenings=["HT-SYN-ASSIGNMENT-TEST"]),
    ]
    map_by_id = {row["mappingId"]: row for row in mappings}
    for row in mappings:
        rel = by_id.get(row["relationshipId"], {"id": row["relationshipId"], "subjectEntityId": row["sourceEntityId"], "objectEntityId": row["targetEntityId"]})
        validate_mapping(row, rel)
    order = ["SOURCE_STATE", "IMPLEMENTATION_OR_TRANSMISSION", "ACTUAL_EXPOSURE", "PERSON_OR_LOWER_LEVEL_RESPONSE"]
    cases = [
        ("REAL-INSTITUTION-PERCEPTION", "REL-INS-040", "XLEM-TEST-INS-040", {"sourceLevel": "INSTITUTION", "targetLevel": "PERSON", "implementation": "SATISFIED", "actualExposure": "SATISFIED", "perceivedExposure": "SATISFIED", "observedTemporalOrder": order, "scientificIdentification": "ADEQUATE_FOR_TESTED_PROPOSITION"}, "CROSS_LEVEL_READY", "Institutional rule/process to a perception target"),
        ("REAL-INSTITUTION-GROUP", "REL-INS-046", "XLEM-TEST-INS-046", {"sourceLevel": "INSTITUTION", "targetLevel": "GROUP", "implementation": "SATISFIED", "actualExposure": "SATISFIED", "observedTemporalOrder": order, "scientificIdentification": "ADEQUATE_FOR_TESTED_PROPOSITION"}, "CROSS_LEVEL_READY", "Institutional resource process to group state"),
        ("REAL-GROUP-AMBIENT-PERCEPTION", "REL-SOC-067", "XLEM-TEST-SOC-067", {"sourceLevel": "GROUP", "targetLevel": "PERSON", "actualExposure": "SATISFIED", "perceivedExposure": "SATISFIED", "observedTemporalOrder": order, "scientificIdentification": "ADEQUATE_FOR_TESTED_PROPOSITION"}, "CROSS_LEVEL_READY", "Persistent ambient group context without fabricated HappeningType"),
        ("SYN-NETWORK-MISSING-STATE", synthetic_network["id"], "XLEM-TEST-NETWORK-001", {"sourceLevel": "NETWORK", "targetLevel": "PERSON", "actualExposure": "SATISFIED", "observedTemporalOrder": order, "scientificIdentification": "ADEQUATE_FOR_TESTED_PROPOSITION"}, "BLOCKED_NETWORK_STATE_DEPENDENCY", "Network metric existence is not personal exposure"),
        ("SYN-NETWORK-WITH-STATE", synthetic_network["id"], "XLEM-TEST-NETWORK-001", {"sourceLevel": "NETWORK", "targetLevel": "PERSON", "networkStateReference": "SYN-NETWORK-STATE-EXACT", "actualExposure": "SATISFIED", "observedTemporalOrder": order, "scientificIdentification": "ADEQUATE_FOR_TESTED_PROPOSITION"}, "CROSS_LEVEL_READY", "Exact state plus defined opportunity route"),
        ("NEG-POLICY-NOT-IMPLEMENTED", "REL-INS-044", "XLEM-TEST-INS-044", {"sourceLevel": "INSTITUTION", "targetLevel": "PERSON", "implementation": "NOT_SATISFIED", "actualExposure": "NOT_SATISFIED", "perceivedExposure": "NOT_SATISFIED", "observedTemporalOrder": order, "scientificIdentification": "ADEQUATE_FOR_TESTED_PROPOSITION"}, "BLOCKED_NO_IMPLEMENTATION_ROUTE", "Policy existence and formal coverage are insufficient"),
        ("NEG-ELIGIBLE-NO-RECEIPT", "REL-INS-050", "XLEM-TEST-INS-050", {"sourceLevel": "INSTITUTION", "targetLevel": "GROUP", "implementation": "SATISFIED", "actualExposure": "NOT_SATISFIED", "observedTemporalOrder": order, "scientificIdentification": "ADEQUATE_FOR_TESTED_PROPOSITION"}, "BLOCKED_NO_EXPOSURE_ROUTE", "Eligibility is not receipt or use"),
        ("SYN-OBJECTIVE-NO-PERCEPTION", synthetic_objective["id"], "XLEM-TEST-OBJECTIVE-001", {"sourceLevel": "GROUP", "targetLevel": "PERSON", "implementation": "SATISFIED", "actualExposure": "SATISFIED", "observedTemporalOrder": order, "scientificIdentification": "ADEQUATE_FOR_TESTED_PROPOSITION"}, "CROSS_LEVEL_READY", "Objective consequence route does not fabricate perception mediation"),
        ("NEG-PERCEPTION-REQUIRED", "REL-INS-040", "XLEM-TEST-INS-040", {"sourceLevel": "INSTITUTION", "targetLevel": "PERSON", "implementation": "SATISFIED", "actualExposure": "SATISFIED", "perceivedExposure": "NOT_SATISFIED", "observedTemporalOrder": order, "scientificIdentification": "ADEQUATE_FOR_TESTED_PROPOSITION"}, "BLOCKED_PERCEPTION_ROUTE_REQUIRED", "Objective procedure alone does not establish perceived fairness"),
        ("REAL-SAME-LEVEL-CONTROL", "REL-BIO-001", None, {"sourceLevel": "PERSON", "targetLevel": "PERSON", "observedTemporalOrder": order, "scientificIdentification": "ADEQUATE_FOR_TESTED_PROPOSITION"}, "SAME_LEVEL_NOT_APPLICABLE", "Person-level control requires no cross-level mapping"),
        ("NEG-ECOLOGICAL-CORRELATION", synthetic_ecological["id"], "XLEM-TEST-ECOLOGICAL-001", {"sourceLevel": "INSTITUTION", "targetLevel": "PERSON", "actualExposure": "SATISFIED", "observedTemporalOrder": order, "scientificIdentification": "ECOLOGICAL_ASSOCIATION_ONLY"}, "RESEARCH_NEEDED", "Complete metadata cannot manufacture individual causal identification"),
        ("NEG-TEMPORAL-ORDER", "REL-INS-040", "XLEM-TEST-INS-040", {"sourceLevel": "INSTITUTION", "targetLevel": "PERSON", "implementation": "SATISFIED", "actualExposure": "SATISFIED", "perceivedExposure": "SATISFIED", "observedTemporalOrder": ["PERSON_OR_LOWER_LEVEL_RESPONSE", "SOURCE_STATE", "IMPLEMENTATION_OR_TRANSMISSION", "ACTUAL_EXPOSURE"], "scientificIdentification": "ADEQUATE_FOR_TESTED_PROPOSITION"}, "BLOCKED_TEMPORAL_MISMATCH", "Policy adopted after response measurement cannot support the claim"),
        ("NEG-PARTIAL-COVERAGE-UNBOUND", "REL-INS-046", "XLEM-TEST-INS-046", {"sourceLevel": "INSTITUTION", "targetLevel": "GROUP", "coverage": "PARTIAL", "implementation": "SATISFIED", "actualExposure": "SATISFIED", "observedTemporalOrder": order, "scientificIdentification": "ADEQUATE_FOR_TESTED_PROPOSITION"}, "BLOCKED_INCOMPLETE_MAPPING", "Partial coverage cannot silently become universal exposure"),
        ("SYN-PARTIAL-COVERAGE-BOUND", "REL-INS-046", "XLEM-TEST-INS-046", {"sourceLevel": "INSTITUTION", "targetLevel": "GROUP", "coverage": "PARTIAL", "coveredTargetSetReference": "SYN-DEFINED-GROUP-SUBSET", "implementation": "SATISFIED", "actualExposure": "SATISFIED", "observedTemporalOrder": order, "scientificIdentification": "ADEQUATE_FOR_TESTED_PROPOSITION"}, "CROSS_LEVEL_READY", "Exact included subset preserves partial coverage"),
        ("SYN-DISCRETE-ASSIGNMENT", synthetic_assignment["id"], "XLEM-TEST-ASSIGNMENT-001", {"sourceLevel": "INSTITUTION", "targetLevel": "PERSON", "implementation": "SATISFIED", "actualExposure": "SATISFIED", "observedTemporalOrder": order, "scientificIdentification": "ADEQUATE_FOR_TESTED_PROPOSITION"}, "CROSS_LEVEL_READY", "Discrete assignment may reference a substantive HappeningType"),
    ]
    test_rows = []
    for case_id, rel_id, map_id, context, expected, purpose in cases:
        rel = by_id.get(rel_id, synthetic_network if rel_id == synthetic_network["id"] else synthetic_objective if rel_id == synthetic_objective["id"] else synthetic_assignment if rel_id == synthetic_assignment["id"] else synthetic_ecological)
        actual = assess_eligibility(map_by_id.get(map_id), rel, context)
        assert actual["state"] == expected, (case_id, actual, expected)
        test_rows.append({"caseId": case_id, "recordClass": "REAL_RELATIONSHIP" if rel_id in by_id else "SYNTHETIC_ARCHITECTURE_CONTROL", "relationshipId": rel_id, "mappingId": map_id, "purpose": purpose, "context": context, "expectedState": expected, "actualResult": actual})

    field_contract = {
        "REQUIRED_UNIVERSAL": ["mappingId", "mappingVersion", "relationshipId", "sourceEntityId", "sourceLevel", "targetEntityId", "targetLevel", "routeType", "exposureDefinition", "exposureUnit", "temporalOrder", "evidenceReferences", "scopeLimitations", "causalEvidence=false", "executionAuthority=false", "provenance"],
        "REQUIRED_CONDITIONAL": ["membershipRule", "eligibilityRule", "implementationRequirement", "assignmentRule", "exposureWindow", "exposureIntensity", "coverageRule", "contactRule", "transmissionRule", "perceptionRequired", "perceptionEntityId", "intermediateEntityIds", "happeningTypeIds", "networkStateDependency"],
        "OPTIONAL": ["contextRequirements", "claimSpecificQualifiers", "implementationEvidenceReferences", "exposureEvidenceReferences"],
        "NOT_APPLICABLE_OR_PROHIBITED": sorted(["polarity", "edgeWeight", "activationValue", "fcmNodeState", "propagationValue", "lifecycleStatus", "activationStatus"]),
    }
    route_taxonomy = {
        "MEMBERSHIP": "Defines risk set only; never sufficient exposure.", "ELIGIBILITY": "Defines possible coverage only.", "ASSIGNMENT": "Assigns target unit to condition; receipt/contact still explicit.",
        "IMPLEMENTATION": "Formal state is realized in practice.", "ENFORCEMENT": "Rule is applied through a specified enforcement process.", "CONTACT": "Target unit encounters specified actor/context.",
        "INFORMATION_EXPOSURE": "Specified information is delivered or displayed; attention/perception separate.", "RESOURCE_ACCESS": "Resource becomes actually accessible to target unit.", "SERVICE_DELIVERY": "Specified service is delivered.",
        "SOCIAL_INTERACTION": "Bounded interaction constitutes exposure.", "NETWORK_POSITION": "Exact Network State creates a bounded opportunity/context; metric alone insufficient.", "AMBIENT_CONTEXT": "Persistent context applies without fabricating a discrete event.",
        "OBSERVATION": "Target can observe a specified condition.", "MONITORING": "Target is actually subject to monitoring.", "SANCTION_EXPOSURE": "Target receives or faces a specified applied sanction.", "INCENTIVE_EXPOSURE": "Target receives or faces a specified implemented incentive.",
    }
    options = [
        {"option": "A", "result": "VIABLE_BUT_INCOMPLETE_ALONE", "worked": ["Reusable typed contract", "Runtime validation", "Ambient and discrete routes", "Separation from causal evidence"], "failed": ["Needs exact Relationship attachment", "Can proliferate without identity rules", "May look causal unless prohibited semantics are enforced"]},
        {"option": "B", "result": "REJECT_AS_UNIVERSAL_REQUIREMENT", "worked": ["Uses real intermediate constructs when scientifically present", "Keeps substantive mechanisms in ontology"], "failed": ["Missing bridge constructs", "Artificial plumbing Drivers", "Long paths", "HappeningType/state confusion", "Ontology bloat"]},
        {"option": "C", "result": "REJECT_AS_COMPLETE_SOLUTION", "worked": ["Small additive migration", "Relationship-local clarity", "Backward-compatible display"], "failed": ["Duplicates route content", "Weak reuse", "Metadata may be ignored", "Cannot centrally version shared mappings"]},
        {"option": "A+B", "result": "VIABLE_WITH_ATTACHMENT_GAP", "worked": ["Typed route plus real bridges only when warranted"], "failed": ["Relationship still needs exact versioned reference"]},
        {"option": "A+C", "result": "VIABLE_CORE", "worked": ["Reusable mapping plus exact mapping reference and claim qualifiers"], "failed": ["Does not by itself state when bridge entities are scientifically required"]},
        {"option": "A+B+C", "result": "RECOMMENDED_BOUNDED_HYBRID", "worked": ["Reusable contract", "Exact Relationship reference", "Conditional real bridge references", "Fail-closed validation", "Ambient and discrete exposure"], "failed": ["Requires migration and consumer awareness", "Needs strict identity/proliferation governance"]},
    ]
    matrix = [
        {"criterion": "Scientific fidelity", "A": "High if noncausal", "B": "High only for real intermediates", "C": "Moderate", "A+B+C": "High with conditional B"},
        {"criterion": "Cross-level explicitness", "A": "High", "B": "Path-dependent", "C": "Relationship-local", "A+B+C": "High and claim-bound"},
        {"criterion": "Ontology burden", "A": "One new contract class", "B": "Potentially high", "C": "Low", "A+B+C": "Bounded by no-plumbing rule"},
        {"criterion": "Runtime enforceability", "A": "High", "B": "Incomplete when bridges absent", "C": "Moderate", "A+B+C": "High"},
        {"criterion": "Reuse", "A": "High", "B": "Varies", "C": "Low", "A+B+C": "High"},
        {"criterion": "Migration safety", "A": "Additive registry", "B": "Potential ontology migration", "C": "Additive fields", "A+B+C": "Additive but consumer-aware"},
        {"criterion": "Ambient context", "A": "Supported", "B": "May fabricate state/event", "C": "Displayable", "A+B+C": "Supported without fake event"},
        {"criterion": "Discrete exposure", "A": "Supported", "B": "Supported via real HT", "C": "Displayable", "A+B+C": "Supported with optional HT ref"},
        {"criterion": "Perception mediation", "A": "Conditional explicit", "B": "Requires real perception Driver", "C": "Easy to omit", "A+B+C": "Explicit and optionally entity-bound"},
        {"criterion": "Network State compatibility", "A": "Can require exact reference", "B": "Cannot replace state", "C": "Weak alone", "A+B+C": "Fail-closed dependency"},
        {"criterion": "WP-PSG-005 compatibility", "A": "Supplies route contract", "B": "Supplies real intermediates", "C": "Attaches exact mapping", "A+B+C": "Complete handoff; no authorization"},
        {"criterion": "Contribution-control compatibility", "A": "Can expose alternate routes", "B": "May reveal duplicate paths", "C": "Claim-local qualifier", "A+B+C": "Best handoff to WP-PSG-004"},
        {"criterion": "Consumer clarity / rollback", "A": "Central and removable", "B": "Harder if ontology added", "C": "Simple but duplicative", "A+B+C": "Exact ref; remove integration to rollback"},
    ]
    skeptical = [
        {"challenge": "Hidden causal entity", "finding": "Prevented only if the mapping schema prohibits polarity, weights, lifecycle, node state, propagation and execution authority."},
        {"challenge": "Relationship or Actions & Events duplication", "finding": "Avoided by storing only an exact mapping reference on the Relationship and referencing, rather than copying, real intermediate entities/events."},
        {"challenge": "Metadata-only causal shortcut", "finding": "Prevented because complete mapping still returns RESEARCH_NEEDED when identification is ecological or otherwise inadequate."},
        {"challenge": "Partial exposure", "finding": "Unbound partial coverage fails; an exact included target set or governed selection rule is required."},
        {"challenge": "Ambient context", "finding": "Representable through AMBIENT_CONTEXT without fabricating a HappeningType."},
        {"challenge": "Multi-stage implementation", "finding": "The core four-stage temporal contract is enforceable; claim-specific intermediate references remain optional/conditional."},
        {"challenge": "Ontology bloat", "finding": "Conditional B rejects Drivers or HappeningTypes created solely as plumbing."},
        {"challenge": "Too generic to validate", "finding": "Route-specific requirements, exact levels, exposure definition, coverage and temporal checks keep the contract bounded."},
        {"challenge": "Ignored by consumers", "finding": "Future validators and execution consumers must fail closed; display-only handling is insufficient for execution."},
        {"challenge": "Impossible migration", "finding": "13 of 38 rows need no cross-level migration; blocked/research/network-dependent rows remain safely unmigrated."},
    ]
    explicit_levels = sum(bool(by_id[row]["subjectLevel"] and by_id[row]["objectLevel"]) for row in affected_ids)
    prototype = {
        "schemaVersion": "0.1.0-PROTOTYPE", "prototypeId": "WP-PSG-002-STAGE-C-20260926-001", "productionArchitecture": False,
        "levels": sorted(LEVELS), "routes": route_taxonomy, "fieldApplicability": field_contract,
        "identityRule": "A mapping identity represents one reusable level transition and exposure contract. Claim-specific scope stays on the Relationship reference; substantive pathway changes require a new mapping identity; compatible clarification requires a new immutable version.",
        "levelDeclarationFinding": {"affectedRelationships": 38, "legacyRelationshipLevelsPresent": explicit_levels, "legacyRelationshipLevelsMissing": 38 - explicit_levels, "entityMetadataSupportsSafeInference": False, "decision": "Future mappings require explicit governed source/target level declarations; legacy labels may inform review but cannot be silently normalized."},
        "relationshipAttachment": {"requiredFutureFields": ["crossLevelMappingId", "crossLevelMappingVersion"], "claimSpecificQualifiersAllowed": True, "fullMappingDuplicationProhibited": True},
        "bridgeRule": "Reference an existing Driver or HappeningType only when it is a scientifically meaningful intermediate state or operation. Never create one solely as routing plumbing.",
        "happeningTypeRule": "Use for discrete or patterned operations/exposures; persistent ambient context does not require a fabricated HappeningType.",
        "mappingSemantics": {"objectKind": "SCIENTIFIC_ROUTING_ELIGIBILITY_CONTRACT", "isCausalNode": False, "isEvidence": False, "hasWeight": False, "hasLifecycle": False, "executionAuthority": False},
        "optionBBridgeChainExamples": [
            {"relationshipId": "REL-INS-040", "conceptualChain": ["INS-051", "IMPLEMENTED_PROCEDURE", "ACTUAL_PROCEDURAL_EXPOSURE", "PSY-022"], "result": "Existing ontology does not contain every bridge; do not mint plumbing Drivers."},
            {"relationshipId": "REL-SOC-067", "conceptualChain": ["SOC-096", "MEMBER_CONTEXT_EXPOSURE", "PSY-022"], "result": "Ambient mapping is possible without a discrete HappeningType."},
        ],
        "optionCRelationshipMetadataExample": {"relationshipId": "REL-INS-040", "crossLevel": True, "sourceLevel": "INSTITUTION", "targetLevel": "PERSON", "exposureRouteType": "IMPLEMENTATION", "actualExposureRequired": True, "perceivedExposureRequired": True, "finding": "Useful claim metadata but duplicative and weak without a reusable exact mapping."},
        "hybridRelationshipReferenceExample": {"relationshipId": "REL-INS-040", "crossLevelMappingId": "XLEM-TEST-INS-040", "crossLevelMappingVersion": "1.0.0-TEST", "claimSpecificQualifiers": ["target is immediate perceived fairness", "specified implemented procedure only"]},
        "handoffs": {
            "WP-PSG-003": ["exact Network State identity", "state/boundary transition dependency", "no metric-to-exposure inference"],
            "WP-PSG-004": ["underlying contribution source", "intermediate route IDs", "alternate aggregate/constituent representations"],
            "WP-PSG-005": ["exact source RDS/profile", "source/target levels", "mapping ID/version", "constituent mapping", "exposure route", "temporal alignment", "causalSourceEligible remains false"],
            "WP-PSG-007": ["only genuine missing construct identities", "no plumbing entities", "explicit actual/perceived construct boundary"],
        },
        "mappings": mappings, "optionResults": options, "decisionMatrix": matrix, "skepticalReview": skeptical,
    }
    tests = {"schemaVersion": "0.1.0-PROTOTYPE", "testSetId": "WP-PSG-002-STAGE-C-20260926-001", "counts": dict(Counter(row["actualResult"]["state"] for row in test_rows)), "cases": test_rows}

    consumers = [
        {"consumer": "scripts/relationship_intervention_v1.py", "classification": "VALIDATION_AWARE_AND_MIGRATION_REQUIRED", "futureChange": "Validate exact mapping/version references for cross-level Relationships; preserve lifecycle separation."},
        {"consumer": "scripts/build_relationships.py", "classification": "MIGRATION_REQUIRED", "futureChange": "Emit optional exact mapping references only after production governance."},
        {"consumer": "scripts/actions_events_v1.py", "classification": "VALIDATION_AWARE", "futureChange": "Resolve referenced HappeningTypes when a mapping names a real discrete operation; no universal HT requirement."},
        {"consumer": "scripts/relational_state_v1.py", "classification": "VALIDATION_AWARE", "futureChange": "Validate exact Network State reference for network-dependent mappings; do not infer exposure from metrics."},
        {"consumer": "scripts/rds_computation_v1.py", "classification": "NO_CURRENT_EXECUTION_IMPACT", "futureChange": "Later provide exact profile/binding and mapping reference to WP-PSG-005; causal eligibility remains false."},
        {"consumer": "scenario-service/src/openai-service.js", "classification": "DISPLAY_ONLY", "futureChange": "May display bounded route context later; must not infer execution or causality."},
        {"consumer": "repository FCM/model construction", "classification": "UNKNOWN_REQUIRES_REVIEW", "futureChange": "No active cross-level propagation consumer was located; external consumers must fail closed until mapping-aware."},
    ]
    consumer_payload = {"schemaVersion": "0.1.0-PROTOTYPE", "consumers": consumers, "productionIntegrationAuthorized": False}

    protected_paths = [
        "data/drivers.json", "data/relational-derived-states.json", "data/entities.json", "data/relationships.json",
        "data/relationship-intervention-v1/relationships.json", "data/relationship-intervention-v1/evidence-assessments.json",
        "data/actions-events-v1/catalog.json", "data/relational-state-v1/catalog.json", "data/rds-computation-v1/profiles.json",
        "data/rds-computation-v1/bindings.json", "data/sources.json", "data/relationship-intervention-v1/source-register.json", "scripts/relationship_intervention_v1.py",
        "scripts/actions_events_v1.py", "scripts/relational_state_v1.py", "scripts/rds_computation_v1.py",
    ]
    protected_paths += sorted(path.relative_to(ROOT).as_posix() for path in (ROOT / "schemas").rglob("*.json"))
    protected_paths += sorted(path.relative_to(ROOT).as_posix() for path in (ROOT / "scenario-service/src").rglob("*.js"))
    protected_paths = sorted(set(protected_paths))
    protected = {"schemaVersion": "1.0.0", "baseMain": "86d136141111fc41832f6b1021d0f4863c1bf204", "hashAlgorithm": "SHA256_CANONICAL_LF_TEXT", "files": {path: file_hash(ROOT / path) for path in protected_paths}}
    write_json(DATA / "cross-level-test-cases.json", tests)
    write_json(DATA / "cross-level-mapping-prototype.json", prototype)
    write_json(DATA / "cross-level-migration-classification.json", migration)
    write_json(DATA / "cross-level-consumer-impact.json", consumer_payload)
    write_json(DATA / "protected-production-hashes.json", protected)

    counts = migration["counts"]
    write_doc("CROSS_LEVEL_DECISION_TEST.md", f"""
# WP-PSG-002 cross-level exposure decision test

This read-only Stage C test reconciles `ASTRA-SOC-LAYER-002` (20 rows) and `ASTRA-INS-LAYER-003` (21 rows). Three rows overlap, producing 38 distinct current records. No disposition or production record changes.

{len(test_rows)} real/synthetic cases test implemented and unimplemented policy, eligibility without receipt, partial coverage, discrete assignment, institutional-to-person perception, institution-to-group allocation, ambient group context, network-state dependency, objective exposure without perception, ecological association, temporal reversal and a same-level control. All expected fail-closed states were reproduced.

The test supports a bounded A+B+C hybrid: a separate immutable typed mapping is the reusable contract; each cross-level Relationship carries only its exact mapping ID/version plus claim qualifiers; existing Drivers/HappeningTypes are referenced only when they are scientifically real intermediates. The mapping is routing/eligibility metadata, never a causal node or evidence.

Migration rehearsal: `{json.dumps(counts, sort_keys=True)}`. The 38-row queue is not 38 production migrations: 13 rows have no cross-level problem after review and several others first depend on Network State or research.
""")
    option_lines = "\n".join(f"| {row['option']} | {row['result']} | {'; '.join(row['worked'])} | {'; '.join(row['failed'])} |" for row in options)
    matrix_lines = "\n".join(f"| {row['criterion']} | {row['A']} | {row['B']} | {row['C']} | {row['A+B+C']} |" for row in matrix)
    skeptical_lines = "\n".join(f"- **{row['challenge']}:** {row['finding']}" for row in skeptical)
    write_doc("CROSS_LEVEL_OPTION_COMPARISON.md", f"""
# Cross-level architecture option comparison

| Option | Result | What worked | What failed |
|---|---|---|---|
{option_lines}

The recommended bounded hybrid is A+B+C with A+C as the required architecture and B conditional on scientific meaning. Option B is rejected as a universal bridge requirement; Option C is rejected as a complete solution; Option A alone lacks an exact claim attachment.

## Decision matrix

| Criterion | A | B | C | Bounded A+B+C |
|---|---|---|---|---|
{matrix_lines}

## Skeptical architecture review

{skeptical_lines}
""")
    route_lines = "\n".join(f"| `{key}` | {value} |" for key, value in route_taxonomy.items())
    write_doc("CROSS_LEVEL_EXPOSURE_CONTRACT.md", f"""
# Cross-level exposure contract

The proposed object is a versioned `SCIENTIFIC_ROUTING_ELIGIBILITY_CONTRACT`. It is not a Driver, RDS, HappeningType, EffectAssertion, Relationship or Network State. It has no polarity, weight, activation value, lifecycle or propagation state. Mapping existence is not evidence.

## Field applicability

- Required universally: {', '.join(field_contract['REQUIRED_UNIVERSAL'])}.
- Required conditionally: {', '.join(field_contract['REQUIRED_CONDITIONAL'])}.
- Optional: {', '.join(field_contract['OPTIONAL'])}.
- Prohibited/not applicable: {', '.join(field_contract['NOT_APPLICABLE_OR_PROHIBITED'])}.

## Routes

| Route | Meaning |
|---|---|
{route_lines}

Perception is required only when it is part of the stated mechanism or target. Membership, eligibility, assignment and implementation cannot substitute for actual exposure. Ambient contexts need bounded membership/exposure windows but no fabricated event. Discrete operations may reference an existing HappeningType. Exact source, implementation/transmission, exposure and response order is mandatory.

## Actual and perceived exposure patterns

| Pattern | Contract treatment |
|---|---|
| Objective exposure directly affects target | `perceptionRequired=false`; actual exposure remains mandatory. |
| Objective exposure must be interpreted | `perceptionRequired=true` with an exact perception entity/reference. |
| Target is perception of context | Actual encounter/observation and the perception target are both explicit; objective state alone cannot satisfy the target. |

## Dependencies

- `WP-PSG-003`: exact Network State identity and state/boundary transition; metric recalculation is not exposure.
- `WP-PSG-004`: underlying contribution identity, intermediate route IDs and alternate aggregate/constituent representations.
- `WP-PSG-005`: exact RDS/profile, mapping ID/version, constituent mapping, exposure route and temporal alignment; causal eligibility stays false.
- `WP-PSG-007`: genuine missing construct identities only; no architecture-plumbing Drivers or HappeningTypes.
""")
    migration_lines = "\n".join(f"| `{key}` | {counts.get(key, 0)} | {reasons[key]} |" for key in categories)
    write_doc("CROSS_LEVEL_MIGRATION_CLASSIFICATION.md", f"""
# Cross-level migration classification

| Category | Count | Meaning |
|---|---:|---|
{migration_lines}

Every authoritative affected Relationship appears exactly once. This is planning classification only; current Layer dispositions remain unchanged.
""")
    consumer_lines = "\n".join(f"| `{row['consumer']}` | {row['classification']} | {row['futureChange']} |" for row in consumers)
    write_doc("CROSS_LEVEL_CONSUMER_IMPACT.md", f"""
# Cross-level consumer impact

| Consumer | Classification | Future bounded change |
|---|---|---|
{consumer_lines}

No current consumer is modified. Future execution-aware consumers must fail closed on absent, incomplete or wrong-version mappings and must keep scientific governance and lifecycle separate from routing eligibility.
""")
    approval = "Approve the bounded WP-PSG-002 architecture direction tested in DP-PSG-002: use an immutable, versioned CrossLevelExposureMapping as a separate noncausal scientific routing/eligibility contract; require each governed cross-level Relationship to reference an exact mapping ID/version with claim-specific qualifiers; and require references to existing Driver or HappeningType intermediates only when they are scientifically substantive parts of the pathway. The mapping must distinguish source state, implementation/transmission, eligibility or membership, actual exposure, optional perceived exposure, temporal order and target response; mapping existence must confer no causal evidence, lifecycle, weight, propagation or execution authority. This approval authorizes architecture direction and later non-production prototyping only. It does not authorize Relationship reclassification, cross-level edge execution or activation, new Drivers, new HappeningTypes, Network State changes, RDS causal-source eligibility, production migration, ontology mutation, lifecycle change, source registration or activation; each requires separate governance."
    write_doc("CROSS_LEVEL_ARCHITECTURE_DECISION_PACKET.md", f"""
# DP-PSG-002 - cross-level exposure architecture decision packet

**Status:** HUMAN ARCHITECTURE GOVERNANCE REQUIRED

## Recommendation

Adopt the bounded A+B+C hybrid. A typed reusable mapping carries the level-transition/exposure contract. C becomes an exact ID/version reference plus claim-specific qualifiers on a Relationship. B is conditional: reference real bridge Drivers/HappeningTypes when the science requires them, and never mint plumbing constructs.

## Required safeguards

- Mapping is noncausal, non-evidentiary and non-executable by itself.
- Exact immutable versions; no default/latest selection.
- Actual and perceived exposure stay distinct.
- Membership, eligibility, policy adoption and implementation remain insufficient alone.
- Network routes depend on WP-PSG-003; aggregate causal-source authority remains WP-PSG-005.
- WP-PSG-004 receives contribution/alternate-route references; WP-PSG-007 governs genuine construct gaps.
- Existing science and dispositions remain unchanged until separate re-adjudication.

## Exact bounded approval statement

> {approval}
""")
    print(json.dumps({"distinctAffectedRecords": 38, "testCases": len(test_rows), "migrationCounts": counts, "recommendedOption": "BOUNDED_A_PLUS_B_PLUS_C", "productionMutations": 0}, indent=2))


if __name__ == "__main__":
    main()
