"""Generate the read-only WP-PSG-004 contribution decision-test package."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/governance/post-scale-up/contribution"
DOCS = ROOT / "docs/governance/post-scale-up/contribution"
BASELINE = "24a406468180a35af5beb74df427053cc1536090"
NOTICE = "READ-ONLY / NON-PRODUCTION PRE-GOVERNANCE DECISION TEST"

spec = importlib.util.spec_from_file_location("contribution_control", Path(__file__).with_name("contribution_control.py"))
cc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cc)

PROTECTED = [
    "data/drivers.json", "data/entities.json", "data/relationships.json", "data/sources.json",
    "data/actions-events-v1/catalog.json", "data/relationship-intervention-v1/relationships.json",
    "data/relational-state-v1/catalog.json", "data/rds-computation-v1/profiles.json",
    "data/rds-computation-v1/bindings.json", "data/cross-level-exposure-v1/mappings.json",
    "data/cross-level-exposure-v1/bindings.json", "schemas/actions-events/v1/*.schema.json",
    "schemas/relationship-intervention/v1/*.schema.json", "schemas/relational-state/v1/*.schema.json",
    "schemas/rds-*.schema.json", "schemas/cross-level-exposure-*.schema.json",
    "scripts/actions_events_v1.py", "scripts/relationship_intervention_v1.py",
    "scripts/relational_state_v1.py", "scripts/rds_computation_v1.py",
    "scripts/cross_level_exposure_v1.py", "scripts/build_relationships.py",
    "scenario-service/src/openai-service.js",
]


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def write_json(name, value):
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / name).write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def write_doc(name, value):
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / name).write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def file_hash(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def protected_hashes():
    rows = {}
    for pattern in PROTECTED:
        for path in sorted(ROOT.glob(pattern)):
            rows[path.relative_to(ROOT).as_posix()] = file_hash(path)
    return rows


def member(record_class, record, role, relationship):
    return {
        "recordClass": record_class, "recordId": record["id"],
        "recordVersion": str(record.get("revision", record.get("profileVersion", "1"))),
        "recordHash": digest(record), "memberRole": role,
        "representationRelationship": relationship,
    }


def group(identifier, definition, members, policy, status, scope=None):
    scope = scope or {"population": "TEST_ONLY", "timeWindow": "TEST_ONLY", "causalContrast": "TEST_ONLY", "unitOfAnalysis": "TEST_ONLY"}
    alignment_key = digest({"definition": definition, "scope": scope})
    for item in members:
        item["identityAlignmentKey"] = alignment_key
    return {
        "schemaVersion": "0.1.0-PROTOTYPE", "groupId": identifier, "groupVersion": "1",
        "scientificContributionDefinition": definition,
        "scope": scope,
        "memberRepresentations": members, "consumerPolicy": "EXPLICIT_FAIL_CLOSED",
        "countingPolicy": policy, "propagationPolicy": "NO_IMPLICIT_PROPAGATION",
        "derivationPolicy": "DERIVATION_NEVER_ESTABLISHES_CAUSALITY",
        "causalIndependenceStatus": status, "evidenceOverlapStatus": "SEPARATE_AXIS",
        "constituentOverlapStatus": "EXPLICIT_OR_UNKNOWN", "crossLevelRouteReferences": [],
        "stateRouteReferences": [], "rdsProfileReferences": [],
        "provenance": {"workPackageId": "WP-PSG-004", "baseline": BASELINE, "prototypeOnly": True},
        "governance": {"status": "TEST_ONLY_NOT_GOVERNED", "productionMutationAuthorized": False},
        "causalAuthority": False, "hasWeight": False, "hasPolarity": False,
        "hasActivation": False, "hasScientificLifecycle": False,
    }


def find_record(rows, identifier):
    return next(row for row in rows if row.get("id") == identifier)


def build_tests():
    rels = read("data/relationship-intervention-v1/relationships.json")["relationships"]
    effects = read("data/actions-events-v1/catalog.json")["effectAssertions"]
    relationship = find_record(rels, "REL-V1-PSY-LAYER-001")
    effect = find_record(effects, "EA-V1-PSY-LAYER-001")
    duplicate_group = group(
        "CONTRIB-PSY-LAYER-REPETITION-001",
        "The bounded repeated-claim exposure contribution to specified belief confidence.",
        [member("RELATIONSHIP", relationship, "PRIMARY_CAUSAL_CONTRIBUTION", "SAME_UNDERLYING_CONTRIBUTION"),
         member("EFFECT_ASSERTION", effect, "ALTERNATE_CAUSAL_REPRESENTATION", "SAME_UNDERLYING_CONTRIBUTION")],
        "MUTUALLY_EXCLUSIVE_REPRESENTATIONS", "SAME_CONTRIBUTION_CONFIRMED",
        {"unitOfAnalysis": "Person x specified claim x exposure protocol", "population": relationship["applicability"]["populationOrSystem"], "timeWindow": "Initial exposure before later judgment", "causalContrast": "Repeated versus non-repeated encounter under bounded protocol"},
    )
    cc.validate_group(duplicate_group)

    independent_a = {"id": "SYN-CAUSE-A-X", "revision": 1}
    independent_b = {"id": "SYN-CAUSE-B-X", "revision": 1}
    independent = [
        group("SYN-CONTRIB-A-X", "Cause A to target X", [member("SYNTHETIC_CAUSAL_ROUTE", independent_a, "PRIMARY_CAUSAL_CONTRIBUTION", "PRIMARY")], "INDEPENDENT_CONTRIBUTION", "DISTINCT_CONTRIBUTIONS_CONFIRMED"),
        group("SYN-CONTRIB-B-X", "Cause B to target X", [member("SYNTHETIC_CAUSAL_ROUTE", independent_b, "PRIMARY_CAUSAL_CONTRIBUTION", "PRIMARY")], "INDEPENDENT_CONTRIBUTION", "DISTINCT_CONTRIBUTIONS_CONFIRMED"),
    ]
    for item in independent:
        cc.validate_group(item)

    derivation = {"id": "DER-V1-SOC-F07-001", "revision": 1}
    state_delta = {"id": "SYN-DELTA-WP004-REWIRE", "revision": 1}
    recalc_group = group(
        "CONTRIB-SOC-F07-DEGREE-CENTRALIZATION", "Network state recalculation lineage",
        [member("SCENARIO_STATE_DELTA", state_delta, "STATE_RECALCULATION_ONLY", "PRECEDES_DERIVATION"),
         member("DERIVATION", derivation, "DERIVATION_ONLY", "RECALCULATES_FROM_STATE")],
        "RECALCULATION_ONLY_NO_CAUSAL_SUM", "STATE_RECALCULATION_ONLY",
    )
    cc.validate_group(recalc_group)

    aggregate = {"id": "INS-039::AGGREGATE-ROUTE-PROTOTYPE", "revision": 1}
    constituent = {"id": "INS-039::CONSTITUENT-ROUTE-PROTOTYPE", "revision": 1}
    unresolved_group = group(
        "SYN-CONTRIB-INS-039-OVERLAP", "Potential constituent and Caseload Pressure aggregate overlap",
        [member("SYNTHETIC_CAUSAL_ROUTE", constituent, "CONSTITUENT_CAUSAL_ROUTE", "POTENTIAL_OVERLAP"),
         member("RDS_ROUTE", aggregate, "AGGREGATE_CAUSAL_ROUTE", "POTENTIAL_OVERLAP")],
        "BLOCKED_PENDING_CAUSAL_INDEPENDENCE", "CONSTITUENT_OVERLAP",
    )
    cc.validate_group(unresolved_group)

    duplicate_values = [{"recordId": relationship["id"], "value": .2}, {"recordId": effect["id"], "value": .2}]
    safe_duplicate = cc.duplicate_safe_sum(duplicate_values, [duplicate_group], {duplicate_group["groupId"]: relationship["id"]})
    independent_value = safe_duplicate + .1
    state_value = cc.duplicate_safe_sum([{"recordId": state_delta["id"], "value": .2}, {"recordId": derivation["id"], "value": .2}], [recalc_group])
    try:
        cc.duplicate_safe_sum([{"recordId": constituent["id"], "value": .2}, {"recordId": aggregate["id"], "value": .2}], [unresolved_group])
        aggregate_result = "UNSAFE_ALLOW"
    except cc.ValidationError:
        aggregate_result = "BLOCK_PENDING_INDEPENDENCE"
    try:
        cc.duplicate_safe_sum(duplicate_values, [duplicate_group])
        missing_selection = "UNSAFE_ALLOW"
    except cc.ValidationError:
        missing_selection = "BLOCK_EXPLICIT_SELECTION_REQUIRED"

    same_target_real = [
        {"effectAssertionId": row["id"], "cause": row["typeId"], "target": row["targetId"], "contributionId": row["contribution"]["groupId"]}
        for row in effects if row["targetId"] == "PSY-003"
    ]
    cases = {
        "schemaVersion": "1.0.0", "workPackageId": "WP-PSG-004", "notice": NOTICE,
        "baseline": BASELINE, "productionMutationAuthorized": False, "humanDecisionTaken": False,
        "primaryDuplicateControl": {"relationshipId": relationship["id"], "effectAssertionId": effect["id"], "groupId": duplicate_group["groupId"], "relationshipHasNativeContributionField": False, "effectAssertionHasNativeContributionField": True, "sameContribution": True, "bothInactive": True, "requiredResult": "SELECT_ONE_REPRESENTATION"},
        "negativeControls": {
            "sameInterventionDifferentEffects": {"kind": "SYNTHETIC_ARCHITECTURE_ONLY", "result": "DISTINCT_CONTRIBUTIONS_CONFIRMED"},
            "sameTargetDifferentCauses": {"kind": "REAL_RECORD_SAFE", "records": same_target_real, "result": "DISTINCT_CONTRIBUTIONS_NOT_TARGET_BASED"},
            "sameEvidenceDifferentEffects": {"kind": "SYNTHETIC_ARCHITECTURE_ONLY", "result": "DISTINCT_CONTRIBUTIONS_EVIDENCE_LINEAGE_SEPARATE"},
            "sameMechanismDifferentEffects": {"kind": "SYNTHETIC_ARCHITECTURE_ONLY", "result": "DISTINCT_CONTRIBUTIONS_MECHANISM_NOT_IDENTITY"},
        },
        "numeric": {"naiveDuplicateSum": .4, "duplicateSafeSum": safe_duplicate, "independentAdditionalEffect": .1, "correctIndependentTotal": independent_value, "stateDeltaPlusDerivedMetricCausalSum": state_value, "aggregateUnresolved": aggregate_result, "missingExplicitSelection": missing_selection},
        "groups": [duplicate_group, recalc_group, unresolved_group, *independent],
        "boundaries": {
            "evidenceIdentityIsContributionIdentity": False, "mechanismIdentityIsContributionIdentity": False,
            "crossLevelMappingCountsAsContribution": False, "derivationCreatesCausality": False,
            "stateRecalculationCreatesCausality": False, "graphReachabilityInfersPathwayIdentity": False,
            "totalEffectLocalLinkReconciliation": "EXPLICIT_PATHWAY_RELATION_REQUIRED_NO_GRAPH_INFERENCE",
            "interaction": "SEPARATE_INTERACTION_OR_MODIFIER_SEMANTICS_NEVER_FLATTEN_AUTOMATICALLY",
        },
    }
    return cases


def build_inventory():
    effects = read("data/actions-events-v1/catalog.json")["effectAssertions"]
    relationships = read("data/relationship-intervention-v1/relationships.json")["relationships"]
    groups = Counter(row["contribution"]["groupId"] for row in effects)
    psy_manifest = read("data/actions-events-v1/PSYCHOLOGICAL_LAYER-materialization-manifest.json")
    state = read("data/relational-state-v1/catalog.json")
    profiles = read("data/rds-computation-v1/profiles.json")["profiles"]
    lifecycle = Counter((row["governance"]["lifecycleStatus"], row["governance"]["activationStatus"]) for row in effects)
    current = [
        {"recordClass": "EFFECT_ASSERTION", "field": "contribution.groupId/role/reconciliation/relatedAssertionIds", "recordCount": len(effects), "distinctContributionIds": len(groups), "policy": "CLASS_SPECIFIC_DUPLICATE_VALIDATION", "consumer": "scripts/actions_events_v1.py"},
        {"recordClass": "RELATIONSHIP_V1", "field": "none", "recordCount": len(relationships), "distinctContributionIds": 0, "policy": "NO_NATIVE_CONTRIBUTION_REFERENCE", "consumer": "scripts/relationship_intervention_v1.py"},
        {"recordClass": "MATERIALIZATION_MANIFEST", "field": "sharedContributions", "recordCount": len(psy_manifest.get("sharedContributions", [])), "distinctContributionIds": len({x["id"] for x in psy_manifest.get("sharedContributions", [])}), "policy": "ONE_CONTRIBUTION_NO_ADDITIVE_COUNT", "consumer": "audit/documentation"},
        {"recordClass": "COLLECTION_DERIVATION_BINDING", "field": "sharedContributionIdentity/contributionPolicy", "recordCount": len(state.get("bindings", [])), "distinctContributionIds": len({x.get("sharedContributionIdentity") for x in state.get("bindings", []) if x.get("sharedContributionIdentity")}), "policy": "RECALCULATION_ONLY_NO_CAUSAL_SUM", "consumer": "scripts/relational_state_v1.py"},
        {"recordClass": "RDS_COMPUTATION_PROFILE", "field": "provenance.legacyContributionIdentity/legacyContributionPolicy", "recordCount": len(profiles), "distinctContributionIds": len({p["provenance"].get("legacyContributionIdentity") for p in profiles if p.get("provenance", {}).get("legacyContributionIdentity")}), "policy": "PRESERVE_LEGACY_RECALCULATION_ONLY", "consumer": "scripts/rds_computation_v1.py"},
        {"recordClass": "CROSS_LEVEL_EXPOSURE_MAPPING", "field": "contributionRouteId/intermediateRouteIds/alternateRepresentationIds/constituentRepresentationIds/aggregateRepresentationIds (handoff only)", "recordCount": 0, "distinctContributionIds": 0, "policy": "NONCAUSAL_NO_CONTRIBUTION", "consumer": "scripts/cross_level_exposure_v1.py"},
        {"recordClass": "NETWORK_STATE_RECEIPT", "field": "causalContribution=false/contributionIdentity", "recordCount": 0, "distinctContributionIds": 0, "policy": "STATE_RECALCULATION_ONLY", "consumer": "scripts/relational_state_v1.py"},
    ]
    return {
        "schemaVersion": "1.0.0", "notice": NOTICE, "productionMutationAuthorized": False,
        "mechanisms": current, "totals": {"productionEffectAssertions": len(effects), "effectAssertionsWithContribution": len(effects), "distinctEffectAssertionGroupIds": len(groups), "productionRelationshipV1Records": len(relationships), "relationshipRecordsWithNativeContributionField": 0, "manifestSharedContributionGroups": len(psy_manifest.get("sharedContributions", [])), "governedRecalculationContributionIds": 1},
        "groupIdMultiplicityWithinProductionEffectAssertions": dict(sorted(groups.items())),
        "effectAssertionLifecycleActivationCounts": {f"{key[0]}::{key[1]}": value for key, value in sorted(lifecycle.items())},
        "finding": "Class-specific controls exist and are internally useful, but no single exact cross-class registry/enforcer currently binds Relationship, EffectAssertion, RDS, derivation and state representations.",
    }


def build_collisions():
    return {
        "schemaVersion": "1.0.0", "notice": NOTICE,
        "governanceBlockerIdCollisions": [{
            "identifier": "BLK-PSY-003", "finding": "ACCIDENTAL_HISTORICAL_IDENTIFIER_REUSE_NOT_INTENTIONAL_MERGE",
            "useA": {"planningHandle": "BLK-PSY-003::CONSTRUCT-BOUNDARY", "meaning": "Belief Strength versus Metacognitive Confidence same-proposition boundary", "affected": ["PSY-003", "PSY-116"], "origin": "scripts/build_psychological_layer_governance_recommendations.py and generated Psychological governance recommendations", "authority": "AUTHORITATIVE_FOR_CONSTRUCT_CLASSIFICATION_HISTORY"},
            "useB": {"planningHandle": "BLK-PSY-003::CONTRIBUTION-REPETITION", "meaning": "Relationship and EffectAssertion encode one repetition contribution", "affected": ["REL-V1-PSY-LAYER-001", "EA-V1-PSY-LAYER-001", "CONTRIB-PSY-LAYER-REPETITION-001"], "origin": "scripts/build_psychological_activation_audit_001.py and post-scale-up blocker dependency map", "authority": "AUTHORITATIVE_FOR_WP-PSG-004"},
            "staleness": "NEITHER_MEANING_PROVEN_STALE", "merged": False,
            "normalization": "Use planning-only qualified handles; retain historical BLK-PSY-003 text and IDs unchanged until separate governance-normalization work.",
        }],
        "contributionIdCollisions": [], "collisionCounts": {"governanceBlockerId": 1, "contributionId": 0},
        "productionIdentifiersChanged": False,
    }


def build_duplicates(cases):
    return {
        "schemaVersion": "1.0.0", "notice": NOTICE,
        "groups": [
            {"contributionId": "CONTRIB-PSY-LAYER-REPETITION-001", "classification": "INTENTIONAL_DUPLICATE_REPRESENTATION", "records": ["REL-V1-PSY-LAYER-001", "EA-V1-PSY-LAYER-001"], "currentControl": "Manifest plus EA reconciliation; Relationship has no native field; both inactive", "recommendedControl": "Exact external group membership plus centralized fail-closed enforcement"},
            {"contributionId": "CONTRIB-SOC-F07-DEGREE-CENTRALIZATION", "classification": "DERIVATION_LINEAGE_STATE_RECALCULATION", "records": ["DER-V1-SOC-F07-001", "RDS-PROFILE-V1-SOC-F07-001"], "currentControl": "RECALCULATION_ONLY_NO_CAUSAL_SUM", "recommendedControl": "Preserve native policy and expose it through cross-class reconciliation without causal promotion"},
            {"contributionId": None, "classification": "POTENTIAL_DUPLICATE", "records": ["INS-039", "REL-INS-017", "constituent routes not yet enumerated"], "currentControl": "RESEARCH_NEEDED / RDS causal source false", "recommendedControl": "BLOCKED_PENDING_CAUSAL_INDEPENDENCE for WP-PSG-005"},
            {"contributionId": None, "classification": "POTENTIAL_DUPLICATE", "records": ["INS-103", "REL-INS-036", "constituent routes not yet enumerated"], "currentControl": "RESEARCH_NEEDED / RDS causal source false", "recommendedControl": "BLOCKED_PENDING_CAUSAL_INDEPENDENCE for WP-PSG-005"},
            {"contributionId": None, "classification": "UNKNOWN_NEEDS_REVIEW", "records": ["ASTRA-SOC-LAYER-001", "10 Social RDS causal-source routes"], "currentControl": "RESEARCH_NEEDED_OR_RETYPE_REVIEW_ONLY", "recommendedControl": "Create no group until exact constituent and aggregate routes are known"},
        ],
        "counts": dict(Counter(x["classification"] for x in [
            {"classification": "INTENTIONAL_DUPLICATE_REPRESENTATION"}, {"classification": "DERIVATION_LINEAGE_STATE_RECALCULATION"},
            {"classification": "POTENTIAL_DUPLICATE"}, {"classification": "POTENTIAL_DUPLICATE"}, {"classification": "UNKNOWN_NEEDS_REVIEW"}
        ])), "productionRecordsChanged": False,
    }


def build_consumers():
    rows = [
        ("scripts/actions_events_v1.py", "CLASS_SPECIFIC_AWARENESS", "Validates duplicate EAs within one contribution group; cannot bind a Relationship lacking membership."),
        ("scripts/relationship_intervention_v1.py", "NO_CONTRIBUTION_AWARENESS", "Validates Relationships but has no cross-class contribution identity."),
        ("scripts/build_relationships.py", "NO_CONTRIBUTION_AWARENESS", "Build path does not reconcile EA/RDS/state representations."),
        ("scripts/rds_computation_v1.py", "CLASS_SPECIFIC_AWARENESS", "Preserves the legacy recalculation-only identity and policy; causal-source execution remains false."),
        ("scripts/relational_state_v1.py", "CLASS_SPECIFIC_AWARENESS", "Requires exact derivation contribution identity and emits causalContribution=false."),
        ("scripts/cross_level_exposure_v1.py", "NO_CAUSAL_CONSUMPTION", "Mapping/binding are noncausal and do not count as contributions."),
        ("scenario-service/src/openai-service.js", "NO_CONTRIBUTION_AWARENESS", "No contribution-aware graph assembly found; future causal consumer must fail closed."),
        ("repository FCM/model construction", "UNKNOWN_NO_INTERNAL_ACTIVE_CROSS_CLASS_CONSUMER_FOUND", "No central active graph consumer enforcing cross-class mutual exclusion was found."),
        ("external consumers", "UNKNOWN", "Must consume a centrally validated resolved representation set or fail closed."),
    ]
    return {"schemaVersion": "1.0.0", "notice": NOTICE, "records": [{"consumer": a, "classification": b, "finding": c, "productionChangeRequiredNow": False} for a,b,c in rows], "recommendedEnforcementBoundary": "One central contribution-resolution gate before any future graph/simulation assembly; native subsystem validators remain.", "currentBehaviorChanged": False}


def build_options():
    dimensions = ["scientific fidelity", "duplicate prevention", "false-collapse risk", "cross-class coverage", "runtime enforceability", "central governance clarity", "migration surface", "backward compatibility", "RDS aggregate compatibility", "Network State compatibility", "Cross-level compatibility", "A&E compatibility", "Relationship compatibility", "FCM/simulation safety", "external consumer safety", "rollback"]
    matrix = {
        "A": {"scientific fidelity": "Good if membership is explicitly adjudicated; false-collapse risk otherwise", "duplicate prevention": "Central identity but no enforcement alone", "cross-class coverage": "Strong", "runtime enforceability": "Incomplete alone", "migration and compatibility": "Moderate additive registry; native controls risk duplication", "RDS/Network/Cross-level compatibility": "Can span all while preserving noncausal roles", "FCM/external consumer safety": "Unsafe unless consumers enforce", "rollback": "Registry removal is additive"},
        "B": {"scientific fidelity": "Lineage cannot prove identity", "duplicate prevention": "Inconsistent across consumers", "cross-class coverage": "Theoretical but distributed", "runtime enforceability": "Fragile", "migration and compatibility": "Low initial migration, high consumer burden", "RDS/Network/Cross-level compatibility": "Requires each subsystem to reinterpret links", "FCM/external consumer safety": "High missed-enforcement risk", "rollback": "Simple but safety is not achieved"},
        "C": {"scientific fidelity": "Conservative within classes", "duplicate prevention": "Good only within native subsystem", "cross-class coverage": "Poor", "runtime enforceability": "Fragmented", "migration and compatibility": "Lowest migration and strongest compatibility", "RDS/Network/Cross-level compatibility": "Keeps unresolved cross-class cases blocked", "FCM/external consumer safety": "Cannot reconcile multi-class input", "rollback": "Existing state retained"},
        "A_PLUS_B_PLUS_C": {"scientific fidelity": "Explicit scoped identity with native semantics retained", "duplicate prevention": "Central fail-closed resolver", "cross-class coverage": "Strong only for explicitly grouped cases", "runtime enforceability": "One mandatory boundary plus native validators", "migration and compatibility": "Additive membership; historical records can remain untouched", "RDS/Network/Cross-level compatibility": "Derivation, recalculation and exposure routing stay noncausal; aggregate overlap blocks", "FCM/external consumer safety": "Resolved-set contract or fail closed", "rollback": "Remove registry/resolver integration and retain native controls"},
    }
    return {
        "schemaVersion": "1.0.0", "notice": NOTICE, "humanDecisionTaken": False,
        "dimensions": dimensions,
        "options": {
            "A": {"result": "VIABLE_BUT_INCOMPLETE_ALONE", "worked": "One immutable cross-class identity can reconcile Relationship, EA, RDS, derivation and state representations.", "failed": "A registry without a mandatory enforcement gate remains advisory and risks false grouping."},
            "B": {"result": "REJECT_AS_STANDALONE", "worked": "Small migration surface and existing lineage can inform reconciliation.", "failed": "Every consumer must rediscover semantics; one missed consumer double counts and lineage is not contribution identity."},
            "C": {"result": "SAFE_BUT_FRAGMENTED", "worked": "Existing EA and recalculation controls fail closed within their classes.", "failed": "Cannot resolve Relationship+EA or constituent+aggregate cases across classes."},
            "A_PLUS_B": {"result": "VIABLE_WITH_NATIVE_COMPATIBILITY_GAP", "worked": "Central truth plus consumer enforcement prevents duplicate propagation.", "failed": "Replacing native policies would force needless migration."},
            "A_PLUS_C": {"result": "VIABLE_WITH_ENFORCEMENT_GAP", "worked": "Central cross-class identity supplements native controls and preserves backward compatibility.", "failed": "Metadata alone does not protect consumers."},
            "A_PLUS_B_PLUS_C": {"result": "RECOMMENDED_ADVISORY_BOUNDED", "worked": "Immutable cross-class groups for explicit cases, native class controls retained, and one fail-closed resolution gate before causal consumption.", "failed": "Requires strict scope identity, exact versions/hashes, explicit selection, and no automatic group inference."},
        },
        "qualitativeMatrix": matrix,
        "skepticalReview": [
            "Groups can collapse distinct effects unless exposure/change, target change, contrast, unit, time and pathway scope align.",
            "Total effects and local links require explicit pathway relations; graph reachability is insufficient.",
            "Aggregate routes remain blocked until WP-PSG-005 establishes independence.",
            "External consumers remain unsafe unless they consume only centrally resolved sets.",
            "Historical records can remain untouched because registry membership may be additive and exact-hash bound.",
        ],
        "recommendation": "BOUNDED_A_PLUS_B_PLUS_C_EXPLICIT_CROSS_CLASS_GROUPS_NATIVE_CONTROLS_CENTRAL_FAIL_CLOSED_ENFORCEMENT",
    }


def build_handoffs():
    return {
        "schemaVersion": "1.0.0", "notice": NOTICE,
        "wpPsg005": {"status": "NOT_STARTED", "requiredInputs": ["aggregate RDS ID", "exact profile and binding", "constituent mappings", "constituent contribution IDs", "candidate aggregate contribution ID", "overlap status", "cross-level mapping", "network state/boundary/window when applicable", "temporal alignment", "causalSourceEligible=false", "independenceStatus"], "adjudicationPerformed": False},
        "wpPsg009": {"status": "NOT_STARTED", "dependentReviews": ["Relationships lacking exact external contribution membership where alternate representations exist", "TOTAL_EFFECT versus MODELED_LOCAL_LINK reconciliation", "aggregate-source Relationships with unresolved constituent overlap", "interaction/moderation records requiring separate contribution semantics"]},
        "wpPsg003": {"h12": "NONCAUSAL_STATE_DERIVATION", "h20": "NONCAUSAL_STATE_DERIVATION", "productionStatusChanged": False},
        "wpPsg002": {"crossLevelMappingRole": "EXPOSURE_ROUTING_ONLY", "countsAsContribution": False},
    }


def docs(inventory, options, duplicates, collisions, consumers):
    approval = ("Approve the bounded WP-PSG-004 A+B+C architecture direction tested in DP-PSG-004: use immutable, exact-version ContributionGroups only for explicitly adjudicated cross-class contribution identity; retain existing class-specific contribution and recalculation controls; and require one centralized fail-closed resolution gate before any future graph, simulation, summation, or effect-attribution consumer. Group membership must bind exact record IDs, versions and hashes and align causal exposure/change, target change, contrast, unit of analysis, time scope and pathway scope. Require explicit representation selection for mutually exclusive representations, preserve derivation/state/exposure/evidence records as noncausal, and keep constituent/aggregate overlap blocked pending WP-PSG-005. This authorizes architecture direction and optional non-production prototyping only; it does not authorize production ContributionGroups, record migration, Relationship or EffectAssertion mutation, RDS causal-source use, graph behavior change, lifecycle change, activation, effect magnitude, polarity, or WP-PSG-005 adjudication.")
    common = f"> **{NOTICE}**\n\nBaseline: `{BASELINE}`. No production mutation or governance decision is made.\n"
    write_doc("CONTRIBUTION_DECISION_TEST.md", f"""# WP-PSG-004 contribution identity decision test

{common}
## Finding

The tests support a bounded A+B+C design. An immutable external `ContributionGroup` supplies explicit cross-class identity, existing class-native fields remain authoritative within their subsystems, and a central resolver enforces count-once, select-one, derivation-only, and blocked-pending-independence policies. Groups are created only after explicit scientific identity adjudication; shared sources, targets, interventions, mechanisms, or graph paths never infer membership.

The numeric control rejected naive `0.2 + 0.2 = 0.4` for the Relationship/EA duplicate and returned one `0.2`; adding an independent `0.1` returned `0.3`. State delta plus metric recalculation returned zero causal contribution. An unresolved constituent/aggregate pair failed closed.

## Positive control

`REL-V1-PSY-LAYER-001` and `EA-V1-PSY-LAYER-001` represent `CONTRIB-PSY-LAYER-REPETITION-001`. They remain distinct record classes and inactive. Exact external membership can bind the Relationship without editing it, while the EA's native contribution metadata remains intact.

## Aggregate and state cases

`INS-039`/`REL-INS-017` and `INS-103`/`REL-INS-036` have unresolved constituent overlap and remain `BLOCKED_PENDING_CAUSAL_INDEPENDENCE`. The ten Social RDS sources under `ASTRA-SOC-LAYER-001` remain unknown until exact routes exist. H12/H20 and `DER-V1-SOC-F07-001` are `NONCAUSAL_STATE_DERIVATION`; recalculation never becomes an empirical contribution.

## Safeguards

- Exact immutable group version and member record ID/version/hash.
- No first/latest/active/best automatic selection.
- No group inference from evidence, target, intervention, mechanism, source, or graph reachability.
- Contribution group has no causal authority, evidence, weight, polarity, activation, propagation, or scientific lifecycle.
- Total-effect/local-link and interaction semantics require explicit scientific relations.
- External consumers must accept a centrally resolved set or fail closed.

## Recommendation

`{options['recommendation']}`. Advisory only; human architecture governance remains required.
""")
    write_doc("CONTRIBUTION_OPTION_COMPARISON.md", f"""# Contribution option comparison

{common}
| Design | Result | Main strength | Decisive limit |
|---|---|---|---|
| A | Viable but incomplete alone | Cross-class identity | Registry without enforcement remains advisory |
| B | Rejected standalone | Small migration surface | Distributed consumers can omit exclusion; lineage is not identity |
| C | Safe but fragmented | Preserves native controls | Cannot reconcile cross-class duplicates |
| A+B | Viable | Central truth and enforcement | Replacing native policies causes migration |
| A+C | Viable | Compatibility and cross-class identity | Lacks mandatory consumer gate |
| A+B+C | Recommended advisory | Explicit group, native controls, central enforcement | Must prohibit inferred grouping and fail closed |

The bounded hybrid best preserves scientific distinctions and rollback. It adds only explicit cross-class membership; it does not globalize every native contribution field.
""")
    write_doc("CONTRIBUTION_IDENTITY_CONTRACT.md", f"""# Contribution identity contract

{common}
## Definitions

- **Contribution identity:** one bounded causal change intended to enter a causal accounting context once.
- **Representation identity:** the exact class, ID, version, and hash of one record expressing or supporting a contribution.
- **Evidence lineage:** sources and assessments supporting claims; it never defines contribution identity.
- **Scientific claim identity:** exact proposition, scope, contrast, target, and role; two records can represent one contribution without being the same claim object.
- **Exposure identity:** bounded exposure/change received under a population, unit, window, and contrast.
- **Derivation identity:** exact deterministic/measurement/estimation method and inputs; noncausal by default.
- **State-change identity:** exact scenario delta and before/after lineage; noncausal by itself.
- **Constituent identity:** one input construct/route within an aggregate.
- **Aggregate identity:** the exact aggregate construct/profile/binding; independent causal contribution is unresolved until separately governed.

## Same-group test

Group only when the same causal exposure/change, target change, causal contrast, unit of analysis, time scope, pathway scope, intended contribution, and underlying represented quantity align. Scope differences require a new group identity unless an explicit governed binding proves they are the same bounded contribution. Shared source, intervention, target, or mechanism is insufficient.

Membership changes require a new immutable group version when the same contribution meaning is preserved. Changed exposure, target, contrast, unit, time, pathway, or underlying quantity requires a new group identity and scientific re-adjudication. Exact member hashes prevent silent drift.
""")
    write_doc("CONTRIBUTION_POLICY_CONTRACT.md", f"""# Contribution policy contract

{common}
The prototype recognizes `COUNT_ONCE`, `MUTUALLY_EXCLUSIVE_REPRESENTATIONS`, `RECALCULATION_ONLY_NO_CAUSAL_SUM`, `DERIVATION_ONLY_NO_PROPAGATION`, `ALTERNATE_REPRESENTATION_SELECT_ONE`, `INDEPENDENT_CONTRIBUTION`, `BLOCKED_PENDING_CAUSAL_INDEPENDENCE`, and `BLOCKED_PENDING_IDENTITY_REVIEW`.

Consumer outcomes are `ALLOW_ALL_INDEPENDENT`, `SELECT_ONE_REPRESENTATION`, `NO_CAUSAL_SUM_DERIVATION_ONLY`, `BLOCK_PENDING_IDENTITY`, and `BLOCK_PENDING_INDEPENDENCE`. Select-one requires an explicit governed representation selection. No default, latest, first, active, evidence-ranked, or class-preferred record may be chosen.

Roles distinguish primary and alternate causal representations, mechanistic intermediates, constituent and aggregate routes, derivation/state recalculation, exposure routing, evidence, context, and other noncausal records. Roles never grant causal authority.
""")
    write_doc("CONTRIBUTION_INVENTORY.md", f"""# Contribution control inventory

{common}
Production Actions & Events has {inventory['totals']['productionEffectAssertions']} EffectAssertions and all {inventory['totals']['effectAssertionsWithContribution']} have native contribution objects across {inventory['totals']['distinctEffectAssertionGroupIds']} IDs. The V1 Relationship registry has {inventory['totals']['productionRelationshipV1Records']} records and zero native contribution-reference fields. One Psychological materialization manifest records the cross-class repetition pair. One governed Network State/RDS lineage uses `CONTRIB-SOC-F07-DEGREE-CENTRALIZATION` with `RECALCULATION_ONLY_NO_CAUSAL_SUM`.

The only confirmed cross-class duplicate is the repetition Relationship/EA pair. The RDS centralization entries are derivation lineage, not duplicate causal inputs. Institutional aggregates and Social aggregate sources remain potential/unknown overlap; no production contribution ID is minted.
""")
    write_doc("CONTRIBUTION_CONSUMER_IMPACT.md", f"""# Contribution consumer impact

{common}
Actions & Events and Network State/RDS calculation have class-specific awareness. Relationship validation/building and the scenario service have no cross-class contribution enforcement. Cross-level mappings are noncausal and must remain excluded. No internal active cross-class FCM assembler was found.

A future production design needs one resolver before graph/simulation/summation/effect-attribution assembly. Subsystem validators remain. External consumers must receive only the resolved representation set plus the exact group/policy receipt or fail closed. Installing a registry without this boundary would not prevent double counting.
""")
    write_doc("CONTRIBUTION_ID_COLLISION_AUDIT.md", f"""# Contribution and blocker ID collision audit

{common}
`BLK-PSY-003` is an accidental historical identifier reuse, not an intentional merge. The Psychological governance recommendation generator uses it for the `PSY-003`/`PSY-116` construct boundary. The later activation/post-scale-up chain uses it for the repetition Relationship/EA double-count blocker. Neither meaning is proven stale.

For this work package, the post-scale-up repetition meaning is authoritative. The planning-only handles `BLK-PSY-003::CONSTRUCT-BOUNDARY` and `BLK-PSY-003::CONTRIBUTION-REPETITION` disambiguate references. Historical production/governance records remain unchanged. No contribution-ID collision was found in current production controls.
""")
    write_doc("CONTRIBUTION_ARCHITECTURE_DECISION_PACKET.md", f"""# DP-PSG-004 — contribution identity and double-count control

{common}
## Recommended architecture

Adopt the bounded A+B+C direction: immutable exact-version external ContributionGroups only for explicitly adjudicated cross-class identity; preserve class-native controls; require centralized fail-closed resolution for future causal consumers. Keep unresolved constituent/aggregate routes blocked.

Rejected: A without enforcement, B as distributed lineage-only logic, and C as a permanent fragmented architecture. No production migration is proposed in this decision.

## Known unresolved science

`INS-039`, `INS-103`, the ten Social RDS sources, total-effect/local-link reconciliation, and any aggregate independence remain unadjudicated. WP-PSG-005 receives structured inputs only and is not started.

## Exact bounded approval statement

{approval}
""")
    return approval


def main():
    cases = build_tests()
    inventory = build_inventory()
    collisions = build_collisions()
    duplicates = build_duplicates(cases)
    consumers = build_consumers()
    options = build_options()
    handoffs = build_handoffs()
    approval = docs(inventory, options, duplicates, collisions, consumers)
    write_json("contribution-test-cases.json", cases)
    write_json("contribution-inventory.json", inventory)
    write_json("contribution-duplicate-groups.json", duplicates)
    write_json("contribution-collision-audit.json", collisions)
    write_json("contribution-consumer-impact.json", consumers)
    write_json("contribution-option-results.json", options)
    write_json("contribution-handoffs.json", handoffs)
    write_json("protected-production-hashes.json", {"schemaVersion": "1.0.0", "baseline": BASELINE, "hashAlgorithm": "SHA-256-LF-normalized", "files": protected_hashes(), "productionMutationAuthorized": False})
    print(json.dumps({"workPackageId": "WP-PSG-004", "recommendation": options["recommendation"], "humanDecisionTaken": False, "approvalStatement": approval, "protectedFiles": len(protected_hashes())}, indent=2))


if __name__ == "__main__":
    main()
