"""Generate isolated WP-PSG-001 Stage E and Stage F dry-run artifacts."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "runtime"))
import rds_runtime as rt  # noqa: E402

DOC = ROOT / "docs/governance/post-scale-up/rds"
DATA = ROOT / "data/governance/post-scale-up/rds"
SCHEMAS = HERE / "schemas"
REGISTRY = HERE / "registry"
MIGRATION = HERE / "migration"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_doc(name: str, text: str) -> None:
    DOC.mkdir(parents=True, exist_ok=True)
    (DOC / name).write_text(text.rstrip() + "\n", encoding="utf-8")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def semantic_hash(entity: dict) -> str:
    keys = ["id", "entityType", "entitySubtype", "name", "definition", "dataType", "representationScale", "polarityDirection", "constituentSpecifications", "derivationType", "derivationLogic", "scopeRequirements", "recalculationBehavior", "networkMetricSpecification", "ratioSpecification", "compositeSpecification"]
    return rt.digest({key: entity.get(key) for key in keys if key in entity})


def schema(title: str, required: list[str], properties: dict) -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"urn:psywerx:prototype:rds-computation-v1:{title.lower().replace(' ', '-')}",
        "title": title, "type": "object", "additionalProperties": True,
        "required": required, "properties": properties,
        "$comment": "NON-PRODUCTION WP-PSG-001 prototype only",
    }


def build_schemas() -> None:
    string = {"type": "string", "minLength": 1}
    profile = schema("RDS Computation Profile Prototype", ["schemaVersion", "profileId", "profileVersion", "rdsId", "rdsDefinitionVersion", "rdsDefinitionHash", "profileType", "inputContract", "outputScale", "outputInterpretation", "derivationEntailed", "causalSourceEligible", "causalSourceGate", "governance"], {
        "profileId": string, "profileVersion": string, "rdsId": string,
        "profileType": {"enum": sorted(rt.PROFILE_TYPES)},
        "inputContract": {"type": "array", "items": {"type": "object", "required": ["inputId", "role"], "properties": {"inputId": string, "role": {"enum": sorted(rt.INPUT_ROLES)}}}},
        "derivationEntailed": {"type": "boolean"}, "causalSourceEligible": {"const": False},
        "causalSourceGate": {"const": "WP-PSG-005_REQUIRED"},
    })
    binding = schema("RDS Application Binding Prototype", ["schemaVersion", "bindingId", "bindingVersion", "rdsId", "rdsDefinitionVersion", "rdsDefinitionHash", "profileId", "profileVersion", "unitOfAnalysis", "contextParameters", "governance"], {
        "bindingId": string, "bindingVersion": string, "rdsId": string,
        "profileId": string, "profileVersion": string, "contextParameters": {"type": "object"},
    })
    request = schema("RDS Execution Request Prototype", ["rdsId", "profileId", "profileVersion", "bindingId", "bindingVersion", "inputs"], {key: string for key in ("rdsId", "profileId", "profileVersion", "bindingId", "bindingVersion")})
    provenance = schema("RDS Execution Provenance Prototype", ["rdsId", "rdsDefinitionHash", "profileId", "profileVersion", "bindingId", "bindingVersion", "inputHashes", "output", "executionFingerprint", "causalSourceAuthorized"], {"causalSourceAuthorized": {"const": False}, "executionFingerprint": string})
    eligibility = schema("RDS Execution Eligibility Prototype", ["state"], {"state": {"enum": sorted(rt.EXECUTION_STATES)}})
    for name, value in {
        "rds-computation-profile.schema.json": profile,
        "rds-application-binding.schema.json": binding,
        "rds-execution-request.schema.json": request,
        "rds-execution-provenance.schema.json": provenance,
        "rds-execution-eligibility.schema.json": eligibility,
    }.items():
        write_json(SCHEMAS / name, value)


def build_registry():
    catalog = read(ROOT / "data/relational-state-v1/catalog.json")
    legacy = next(row for row in catalog["bindings"] if row["id"] == "DER-V1-SOC-F07-001")
    target = legacy["targetRds"]
    input_entity = legacy["inputContract"]["inputEntity"]
    gov = {"status": "PROTOTYPE_ONLY", "executionEligibleInPrototype": True, "productionMaterialization": False}
    profile = {
        "schemaVersion": "1.0.0-PROTOTYPE", "profileId": "PROTO-DER-V1-SOC-F07-001", "profileVersion": "1.0.0",
        "rdsId": "RDS-0006", "rdsDefinitionVersion": target["definitionVersion"], "rdsDefinitionHash": target["definitionHash"],
        "profileType": "DERIVATION_PROFILE", "displayName": "Additive compatibility wrapper for Freeman degree centralization",
        "scientificPurpose": "Represent the exact governed legacy calculation without changing its identity or scope.",
        "inputContract": [{"inputId": "SOC-049", "role": "CONSTITUENT", "required": True, "definitionVersion": input_entity["definitionVersion"], "definitionHash": input_entity["definitionHash"], "collectionSubject": legacy["inputContract"]["collectionSubject"], "completenessRule": legacy["inputContract"]["completenessRule"]}],
        "minimumInputRequirements": [{"minimumNodes": legacy["minimumNodes"], "completeAlignedCollection": True}],
        "constituentMapping": [{"inputId": "SOC-049", "role": "CONSTITUENT", "causalConstituentInference": False}],
        "requiredContext": ["networkBoundary", "nodeSet", "tieRelation", "timeWindow"],
        "aggregationFunction": "FREEMAN_DEGREE_CENTRALIZATION",
        "calculationReference": legacy["calculationReference"], "metricVariant": legacy["metricVariant"], "normalization": legacy["normalization"],
        "missingnessPolicy": "EXACT_SET_EQUALITY_NO_MISSING_NO_EXTRA", "unitOfAnalysis": "NETWORK",
        "outputScale": "NORMALIZED_NETWORK_CENTRALIZATION", "outputInterpretation": "Degree centralization for the exact bound simple undirected network.",
        "scopeLimitations": legacy["scopeLimitations"], "derivationEntailed": True,
        "causalSemantics": "DEFINITIONAL_CALCULATIONAL_RECALCULATION_ONLY_NO_CAUSAL_SUM",
        "causalSourceEligible": False, "causalSourceGate": "WP-PSG-005_REQUIRED",
        "provenance": {"compatibilityWrapperFor": legacy["id"], "preservesLegacyId": True, "legacyRecordHash": next(a["authorizedObjects"][0]["recordHash"] for a in catalog["authorizations"]), "lineage": legacy["lineage"]},
        "governance": gov,
    }
    synthetic_measurement = {
        "schemaVersion": "1.0.0-PROTOTYPE", "profileId": "PROTO-SYNTHETIC-MEASUREMENT-001", "profileVersion": "1.0.0",
        "rdsId": "TEST-RDS-MEASUREMENT-001", "rdsDefinitionVersion": "TEST-ONLY-1", "rdsDefinitionHash": rt.digest("TEST-RDS-MEASUREMENT-001"),
        "profileType": "MEASUREMENT_PROFILE", "displayName": "Synthetic measurement architecture example", "scientificPurpose": "Test measurement-specific contract; not PSYWERX science.",
        "inputContract": [{"inputId": "TEST-INSTRUMENT-RESPONSES", "role": "MEASUREMENT_INPUT", "required": True}, {"inputId": "TEST-INSTRUMENT-VERSION", "role": "PARAMETER", "required": True}],
        "minimumInputRequirements": [{"completeRequiredItems": True}], "constituentMapping": [], "requiredContext": ["measurementInstrument", "population"],
        "measurementProcedure": {"instrumentId": "TEST-INSTRUMENT-V1", "instrumentVersionRequired": True, "scoringRule": "TEST_ONLY_DECLARED_RULE", "missingItemRules": "TEST_ONLY_EXPLICIT", "reliabilityInformation": "OUTPUT_METADATA_WHEN_AVAILABLE", "validityScope": "BOUND_POPULATION_ONLY"},
        "unitOfAnalysis": "INDIVIDUAL", "outputScale": "TEST_SCORE", "outputInterpretation": "Synthetic score only", "scopeLimitations": ["NOT SCIENTIFICALLY GOVERNED"],
        "derivationEntailed": False, "causalSemantics": "NONE", "causalSourceEligible": False, "causalSourceGate": "WP-PSG-005_REQUIRED", "provenance": {"synthetic": True}, "governance": gov,
    }
    synthetic_estimation = {
        "schemaVersion": "1.0.0-PROTOTYPE", "profileId": "PROTO-CUL-088-ESTIMATION-COUNTEREXAMPLE", "profileVersion": "1.0.0",
        "rdsId": "CUL-088", "rdsDefinitionVersion": "TEST-ONLY-NOT-CANONICAL", "rdsDefinitionHash": rt.digest("CUL-088-TEST-ONLY-COUNTEREXAMPLE"),
        "profileType": "ESTIMATION_PROFILE", "displayName": "CUL-088 latent estimation counterexample", "scientificPurpose": "Exercise estimator validation only; not a proposed measurement model.",
        "inputContract": [{"inputId": "SYNTHETIC-INDICATORS", "role": "MEASUREMENT_INPUT", "required": True}, {"inputId": "SYNTHETIC-COHORT", "role": "REFERENCE_VALUE", "required": True}],
        "minimumInputRequirements": [{"sampleAdequacy": "ESTIMATOR_SPECIFIC"}], "constituentMapping": [], "requiredContext": ["population", "timeWindow"],
        "estimationProcedure": {"modelSemantics": "TEST_ONLY_LATENT_DISTANCE_MODEL", "modelVersion": "TEST-1", "diagnosticExpectations": ["CONVERGENCE_STATUS", "FIT_DIAGNOSTICS", "UNCERTAINTY_METHOD"], "outputUncertainty": ["POINT_ESTIMATE", "STANDARD_ERROR_OR_INTERVAL_WHEN_APPROPRIATE"]},
        "unitOfAnalysis": "GROUP", "outputScale": "TEST_LATENT_DISTANCE", "outputInterpretation": "Architecture counterexample only", "scopeLimitations": ["NOT SCIENTIFICALLY GOVERNED", "NOT A PROPOSED CUL-088 MEASUREMENT MODEL"],
        "derivationEntailed": False, "causalSemantics": "NONE", "causalSourceEligible": False, "causalSourceGate": "WP-PSG-005_REQUIRED", "provenance": {"syntheticArchitectureCounterexample": True},
        "governance": {**gov, "executionEligibleInPrototype": False},
    }
    binding = {
        "schemaVersion": "1.0.0-PROTOTYPE", "bindingId": "PROTO-BIND-RDS-0006-STAR-4", "bindingVersion": "1.0.0",
        "rdsId": "RDS-0006", "rdsDefinitionVersion": target["definitionVersion"], "rdsDefinitionHash": target["definitionHash"],
        "profileId": profile["profileId"], "profileVersion": profile["profileVersion"],
        "inputDefinitionVersions": {"SOC-049": input_entity["definitionVersion"]}, "inputDefinitionHashes": {"SOC-049": input_entity["definitionHash"]},
        "population": "FOUR_SYNTHETIC_NODES", "networkBoundary": "EXACT_FOUR_NODE_STAR", "nodeSet": ["A", "B", "C", "D"], "tieRelation": "SIMPLE_UNDIRECTED_LOOPLESS",
        "dataSource": "TEST_FIXTURE", "timeWindow": "SINGLE_TEST_STATE", "observationWindow": "SINGLE_TEST_STATE", "unitOfAnalysis": "NETWORK", "scenarioStateReference": "SYNTHETIC_STAR_STATE_V1",
        "contextParameters": {"metricVariant": legacy["metricVariant"], "normalization": legacy["normalization"]}, "provenance": {"prototypeOnly": True, "legacySource": legacy["id"]}, "governance": gov,
    }
    binding_b = {**binding, "bindingId": "PROTO-BIND-RDS-0006-STAR-4-B", "bindingVersion": "1.0.0", "population": "SECOND_SYNTHETIC_FOUR_NODE_CONTEXT", "scenarioStateReference": "SYNTHETIC_STAR_STATE_V1_B"}
    measurement_v2 = json.loads(json.dumps(synthetic_measurement))
    measurement_v2["profileVersion"] = "1.0.1"
    measurement_v2["displayName"] = "Synthetic measurement architecture example, corrected prototype version"
    measurement_alternative = json.loads(json.dumps(synthetic_measurement))
    measurement_alternative["profileId"] = "PROTO-SYNTHETIC-MEASUREMENT-ALT-001"
    measurement_alternative["measurementProcedure"]["scoringRule"] = "TEST_ONLY_ALTERNATIVE_RULE"
    measurement_alternative["outputInterpretation"] = "Alternative synthetic score semantics only"
    measurement_binding = {
        "schemaVersion": "1.0.0-PROTOTYPE", "bindingId": "PROTO-BIND-SYNTHETIC-MEASUREMENT-001", "bindingVersion": "1.0.0",
        "rdsId": synthetic_measurement["rdsId"], "rdsDefinitionVersion": synthetic_measurement["rdsDefinitionVersion"], "rdsDefinitionHash": synthetic_measurement["rdsDefinitionHash"],
        "profileId": synthetic_measurement["profileId"], "profileVersion": synthetic_measurement["profileVersion"], "population": "SYNTHETIC_RESPONDENTS",
        "measurementInstrument": "TEST-INSTRUMENT-V1", "dataSource": "SYNTHETIC_RESPONSES", "unitOfAnalysis": "INDIVIDUAL", "contextParameters": {}, "provenance": {"synthetic": True}, "governance": gov,
    }
    estimation_binding = {
        "schemaVersion": "1.0.0-PROTOTYPE", "bindingId": "PROTO-BIND-CUL-088-ESTIMATION-COUNTEREXAMPLE", "bindingVersion": "1.0.0",
        "rdsId": synthetic_estimation["rdsId"], "rdsDefinitionVersion": synthetic_estimation["rdsDefinitionVersion"], "rdsDefinitionHash": synthetic_estimation["rdsDefinitionHash"],
        "profileId": synthetic_estimation["profileId"], "profileVersion": synthetic_estimation["profileVersion"], "population": "SYNTHETIC_COHORTS", "timeWindow": "SYNTHETIC_WINDOW",
        "unitOfAnalysis": "GROUP", "contextParameters": {"modelVersion": "TEST-1"}, "provenance": {"synthetic": True, "notScience": True}, "governance": {**gov, "executionEligibleInPrototype": False},
    }
    profiles = [profile, synthetic_measurement, measurement_v2, measurement_alternative, synthetic_estimation]
    bindings = [binding, binding_b, measurement_binding, estimation_binding]
    for row in profiles: rt.validate_computation_profile(row)
    for row in bindings: rt.validate_application_binding(row)
    rt.validate_registry_immutability(profiles)
    rt.validate_registry_immutability(bindings)
    write_json(REGISTRY / "profiles.json", {"schemaVersion": "1.0.0-PROTOTYPE", "namespace": "NON_PRODUCTION", "profiles": profiles})
    write_json(REGISTRY / "bindings.json", {"schemaVersion": "1.0.0-PROTOTYPE", "namespace": "NON_PRODUCTION", "bindings": bindings})
    role_descriptions = {
        "CONSTITUENT": (True, "Ontology constituent used to define or calculate the output."),
        "MEASUREMENT_INPUT": (False, "Observed response or indicator used by a measurement/estimation method."),
        "PARAMETER": (False, "Declared computation parameter."),
        "NORMALIZER": (False, "Reference denominator or benchmark used for normalization."),
        "BOUNDARY_INPUT": (False, "Population, node-set, jurisdiction or other scope boundary."),
        "REFERENCE_VALUE": (False, "Comparison or baseline value."),
        "EXTERNAL_CONTEXT": (False, "Context required for application but not an ontology constituent."),
        "DATA_SOURCE": (False, "Bound source or instrument supplying observations."),
    }
    write_json(REGISTRY / "input-role-taxonomy.json", {"schemaVersion": "1.0.0-PROTOTYPE", "roles": [{"role": role, "causalConstituentByRole": causal, "meaning": meaning} for role, (causal, meaning) in role_descriptions.items()]})
    request = {"rdsId": "RDS-0006", "profileId": profile["profileId"], "profileVersion": profile["profileVersion"], "bindingId": binding["bindingId"], "bindingVersion": binding["bindingVersion"], "inputs": {"SOC-049": {"value": [3, 1, 1, 1], "definitionHash": input_entity["definitionHash"], "valueHash": rt.digest([3, 1, 1, 1])}}, "parameters": {}, "causalSourceRequested": False}
    result = rt.execute_reference(request, profiles, bindings, target["definitionHash"])
    write_json(HERE / "runtime/reference-execution.json", {"request": request, "result": result})
    return legacy, profile, binding, result


def migration_dry_run(legacy, profile, binding):
    classification = read(DATA / "rds-migration-classification.json")
    entities = {row["id"]: row for row in read(ROOT / "data/entities.json") if row["entityType"] == "RELATIONAL_DERIVED_STATE"}
    assert len(entities) == 41
    rows = []
    for source in classification["records"]:
        entity = entities[source["rdsId"]]
        category = source["migrationCategory"]
        row = {
            "rdsId": source["rdsId"], "currentLayer": source["layer"], "currentDefinitionHash": semantic_hash(entity),
            "currentMigrationCategory": category, "proposedExecutionState": "NON_EXECUTABLE_NO_ELIGIBLE_PROFILE",
            "existingGovernedDerivationIds": [legacy["id"]] if source["rdsId"] == "RDS-0006" else [],
            "proposedProfileRecords": [], "proposedBindingRequirements": [], "profileIdentityReviewItems": [],
            "scientificGaps": [], "ontologyDependencies": [], "architectureDependencies": ["GOV-RDS-CONTRACT-001-2026-09-25", "WP-PSG-001_PRODUCTION_NOT_AUTHORIZED"],
            "causalSourceEligible": False, "causalSourceGate": "WP-PSG-005_REQUIRED", "productionMutationAuthorized": False,
            "migrationAction": "NO_PRODUCTION_ACTION", "rollbackState": "CURRENT_PRODUCTION_RDS_AND_LEGACY_DERIVATION_UNCHANGED",
        }
        if category == "READY_FOR_PROFILE_MATERIALIZATION":
            row.update({"proposedExecutionState": "EXECUTABLE_IN_PROTOTYPE_ONLY", "proposedProfileRecords": [{"profileId": profile["profileId"], "profileVersion": profile["profileVersion"], "profileType": profile["profileType"], "compatibilityWrapperFor": legacy["id"], "productionStatus": "PROPOSED_ONLY"}], "proposedBindingRequirements": profile["requiredContext"], "migrationAction": "FUTURE_ADDITIVE_WRAPPER_PHASE_1_ONLY", "lineageMap": {"legacyId": legacy["id"], "strategy": "PRESERVE_ID_AND_LINEAGE_ADDITIVE_WRAPPER", "legacyDefinitionHash": legacy["targetRds"]["definitionHash"]}})
        elif category == "PROFILE_DEFINITION_REQUIRED":
            row["scientificGaps"] = ["EXACT_PROFILE_TYPE", "EXACT_METHOD", "INPUT_VERSIONS_AND_HASHES", "MISSINGNESS_POLICY", "OUTPUT_INTERPRETATION"]
            row["knownCandidateInputs"] = entity.get("constituentSpecifications", [])
            row["likelyProfileType"] = "REQUIRES_SCIENTIFIC_CLASSIFICATION"
            row["proposedBindingRequirements"] = ["REFERENCE_POPULATION_OR_APPLICATION_SCOPE", "TIME_WINDOW", "UNIT_OF_ANALYSIS"]
            row["migrationAction"] = "CREATE_SCIENTIFIC_DEFINITION_WORK_ITEM_ONLY"
        elif category == "MULTIPLE_PROFILE_REVIEW_REQUIRED":
            row["profileIdentityReviewItems"] = ["DIRECTION_DIRECTED_OR_UNDIRECTED", "WEIGHT_BINARY_OR_VALUED", "LOCAL_OR_GLOBAL", "NORMALIZATION_VARIANT", "CONSTITUENT_SET", "AGGREGATION_RULE", "MISSINGNESS_POLICY", "UNIT_OF_ANALYSIS", "NETWORK_OR_POPULATION_BOUNDARY", "TIME_WINDOW"]
            row["scientificGaps"] = ["PROFILE_IDENTITY_REVIEW_REQUIRED"]
            row["migrationAction"] = "PROFILE_IDENTITY_REVIEW_ONLY"
        elif category == "NON_EXECUTABLE_PENDING_SCIENCE":
            row["proposedExecutionState"] = "NON_EXECUTABLE_BLOCKED_BY_SCIENCE"
            row["scientificGaps"] = ["EXACT_COMPUTATION_OR_MEASUREMENT_SEMANTICS", "VERSIONED_INPUT_CONTRACT", "APPLICATION_SCOPE"]
            row["migrationAction"] = "RETAIN_CONSTRUCT_NON_EXECUTABLE_PENDING_SCIENCE"
        elif category == "BLOCKED_BY_ONTOLOGY":
            row["proposedExecutionState"] = "NON_EXECUTABLE_BLOCKED_BY_ONTOLOGY"
            row["ontologyDependencies"] = ["WP-PSG-007_CONSTRUCT_ONTOLOGY_GOVERNANCE"]
            row["scientificGaps"] = ["ROOT_CONSTRUCT_OR_METADATA_BLOCKER"]
            row["migrationAction"] = "PRESERVE_ONTOLOGY_BLOCKER_NO_PROFILE"
        rows.append(row)
    observed = Counter(row["currentMigrationCategory"] for row in rows)
    counts = {key: observed.get(key, 0) for key in classification["counts"]}
    assert counts == classification["counts"]
    assert len(rows) == 41 and len({row["rdsId"] for row in rows}) == 41
    manifest = {"schemaVersion": "1.0.0-PROTOTYPE", "dryRunId": "WP-PSG-001-STAGE-F-DRY-RUN-20260925-001", "decisionId": "GOV-RDS-CONTRACT-001-2026-09-25", "productionMigrationAuthorized": False, "rootBlockerResolved": False, "counts": counts, "totalRds": len(rows), "records": rows}
    write_json(DATA / "rds-migration-dry-run.json", manifest)
    write_json(MIGRATION / "rds-migration-dry-run.json", manifest)
    return manifest


def consumer_and_delta(legacy, result):
    consumers = {
        "schemaVersion": "1.0.0-PROTOTYPE", "analysisType": "READ_ONLY_CONSUMER_IMPACT", "productionMutationAuthorized": False,
        "summary": {"NO_RDS_EXECUTION_DEPENDENCY": 2, "USES_RDS_AS_ENTITY_ONLY": 3, "USES_LEGACY_DERIVATION": 2, "WOULD_REQUIRE_PROFILE_AWARENESS": 1, "WOULD_REQUIRE_MIGRATION": 0, "UNKNOWN_REQUIRES_REVIEW": 0},
        "consumers": [
            {"consumer": "scripts/relational_state_v1.py", "classification": "USES_LEGACY_DERIVATION", "currentBehavior": "Validates and evaluates DER-V1-SOC-F07-001", "futurePath": "Keep legacy path; shadow adapter invokes prototype-equivalent profile engine only after Phase 1 authorization."},
            {"consumer": "scripts/relational_state_fixtures.py", "classification": "USES_LEGACY_DERIVATION", "currentBehavior": "Builds deterministic network fixtures", "futurePath": "Reuse fixtures for byte/numeric shadow comparison."},
            {"consumer": "scripts/social_layer_v2_package.py", "classification": "USES_RDS_AS_ENTITY_ONLY", "currentBehavior": "Reads derivation for audit/reporting", "futurePath": "No execution migration required."},
            {"consumer": "scripts/next_layer_readiness.py", "classification": "USES_RDS_AS_ENTITY_ONLY", "currentBehavior": "Reads catalog inventory", "futurePath": "No execution migration required."},
            {"consumer": "scripts/rds_contract_decision_test.py", "classification": "NO_RDS_EXECUTION_DEPENDENCY", "currentBehavior": "Stage C planning prototype", "futurePath": "Historical decision-test retained."},
            {"consumer": "scripts/actions_events_v1.py", "classification": "NO_RDS_EXECUTION_DEPENDENCY", "currentBehavior": "Rejects direct RDS EffectAssertion targets", "futurePath": "Rule remains unchanged."},
            {"consumer": "future RDS computation service", "classification": "WOULD_REQUIRE_PROFILE_AWARENESS", "currentBehavior": "Does not exist", "futurePath": "Require exact rds/profile/version/binding/version; never infer latest/default."},
            {"consumer": "data/relationships.json", "classification": "USES_RDS_AS_ENTITY_ONLY", "currentBehavior": "Stores current propositions", "futurePath": "No mutation in Phase 0 or Phase 1."},
        ],
        "rds0006Compatibility": {"semanticEquivalent": True, "numericEquivalentForFourNodeStar": result["output"] == 1.0, "lineagePreserving": True, "causallyNeutral": result["causalSourceAuthorized"] is False, "rollbackSafe": True, "consumerCompatibleAdditively": True},
    }
    write_json(DATA / "rds-consumer-impact.json", consumers)
    delta = {
        "schemaVersion": "1.0.0-PROTOTYPE", "decisionPacketId": "DP-PSG-001-IMPLEMENTATION", "status": "HUMAN_GOVERNANCE_REQUIRED", "productionMutationAuthorized": False,
        "phase0": {"scope": "Install schemas, empty registries, validators, eligibility service and causal firewall with zero migrated RDS.", "proposedPaths": ["schemas/rds-computation-profile.schema.json", "schemas/rds-application-binding.schema.json", "schemas/rds-execution-request.schema.json", "schemas/rds-execution-provenance.schema.json", "schemas/rds-execution-eligibility.schema.json", "data/rds-computation-v1/profiles.json", "data/rds-computation-v1/bindings.json", "scripts/rds_computation_v1.py"], "migratedRds": []},
        "phase1": {"scope": "Add one compatibility wrapper and binding for RDS-0006 only, run shadow equivalence, do not feed active simulation.", "migratedRds": ["RDS-0006"], "legacyPreserved": [legacy["id"]], "shadowGate": "NUMERIC_AND_PROVENANCE_EQUIVALENCE", "causalSourceEligible": False},
        "excluded": {"remainingRds": 40, "causalSourceAuthorization": "EXCLUDED", "lifecycleOrActivation": "EXCLUDED", "relationshipMutation": "EXCLUDED"},
        "futureValidatorFunctions": ["validate_computation_profile", "validate_application_binding", "validate_profile_binding_compatibility", "resolve_execution_eligibility", "validate_rds_execution_request", "validate_causal_firewall"],
        "rollback": "Remove profile/binding registry integration and profile-aware service routing; retain all RDS IDs and DER-V1-SOC-F07-001 unchanged; empty registries restore ontology-only/legacy behavior.",
        "protectedScienceGates": ["41 production RDS hashes unchanged", "Relationship corpus unchanged", "Actions & Events unchanged", "Network State unchanged", "source registry unchanged", "lifecycle unchanged", "causal firewall false"],
    }
    write_json(DATA / "rds-production-delta-preview.json", delta)
    packet = {
        "schemaVersion": "1.0.0", "decisionPacketId": "DP-PSG-001-IMPLEMENTATION", "workPackageId": "WP-PSG-001",
        "status": "HUMAN_ARCHITECTURE_GOVERNANCE_REQUIRED", "recommendedScope": "PHASE_0_THEN_SEPARATELY_GATED_RDS_0006_PHASE_1",
        "phase0": delta["phase0"], "phase1": delta["phase1"], "explicitExclusions": delta["excluded"],
        "shadowModeRequired": True, "rollback": delta["rollback"], "causalFirewall": "WP-PSG-005_REQUIRED_AND_FALSE_BY_DEFAULT",
        "exactApprovalStatement": "Approve DP-PSG-001-IMPLEMENTATION for a bounded production Phase 0 that installs the governed RDS computation-profile schemas, empty registries, exact-version validators, execution-eligibility service, provenance/fingerprint contract, and mandatory WP-PSG-005 causal firewall with zero RDS migrations; then authorize a separately gated Phase 1 compatibility wrapper for RDS-0006 only, preserving DER-V1-SOC-F07-001 and its lineage, requiring shadow-mode numeric and provenance equivalence, rollback to legacy-only behavior, no active simulation feed, and causalSourceEligible=false. All other 40 RDS, production Relationships, lifecycle states, ontology, Network State, Actions & Events, sources, and activation remain unchanged and unauthorized.",
    }
    write_json(DATA / "rds-production-implementation-decision-packet.json", packet)
    return consumers, delta


def protected_hashes():
    paths = [
        "data/entities.json", "data/drivers.json", "data/relational-derived-states.json", "data/relationships.json",
        "data/actions-events-v1/catalog.json", "data/relational-state-v1/catalog.json", "data/network-state-v1/catalog.json",
        "data/sources.json", "scripts/actions_events_v1.py", "scripts/relational_state_v1.py", "schemas/actions-events-v1.schema.json",
    ]
    rows = {path: file_hash(ROOT / path) for path in paths if (ROOT / path).exists()}
    payload = {"schemaVersion": "1.0.0-PROTOTYPE", "capturedFromMain": "a11ad927fdb58fb947404287dc620a4f79cd9497", "purpose": "Assert Stage E/F changes no production science, architecture, validator, lifecycle, or source file.", "sha256": rows}
    write_json(MIGRATION / "protected-production-hashes.json", payload)
    return payload


def docs(manifest, consumers, delta, result):
    c = manifest["counts"]
    write_doc("RDS_REFERENCE_IMPLEMENTATION.md", f"""# RDS computation-profile reference implementation

**Decision:** `GOV-RDS-CONTRACT-001-2026-09-25`
**Scope:** non-production Stage E prototype and Stage F dry run only

The isolated implementation in `prototypes/rds-computation-v1/` separates RDS construct, typed immutable computation profile, versioned application binding, execution request/provenance and causal authorization. It supports `DERIVATION_PROFILE`, `MEASUREMENT_PROFILE` and `ESTIMATION_PROFILE` without collapsing their semantics. Every prototype object is `PROTOTYPE_ONLY`; no production registry imports this package.

RDS-0006 is the only exact positive control. Its additive wrapper references `DER-V1-SOC-F07-001`, retains the governed definition hash and recalculation-only semantics, and produces `1.0` for the four-node star. The deterministic fingerprint is `{result['executionFingerprint']}`. Causal authorization remains false.

Stage E is complete in the authorized non-production scope. Stage F is complete only as a dry run; production migration is not started or authorized.
""")
    write_doc("RDS_PROFILE_SCHEMA_SPEC.md", """# RDS computation profile schema specification

Profiles are typed and immutable at `profileId + profileVersion`. Universal fields anchor exact RDS identity/version/hash, input roles, output meaning, provenance, prototype governance and the causal firewall. Derivation profiles require an exact calculation and entailment. Measurement profiles require instrument/procedure and scoring semantics without claiming ontology entailment. Estimation profiles require model semantics, version, diagnostics and estimator-appropriate uncertainty.

Input roles are `CONSTITUENT`, `MEASUREMENT_INPUT`, `PARAMETER`, `NORMALIZER`, `BOUNDARY_INPUT`, `REFERENCE_VALUE`, `EXTERNAL_CONTEXT` and `DATA_SOURCE`. Context-only changes belong in bindings. Changes to method, normalization, metric variant, constituents, aggregation, missingness, unit, instrument/model or output semantics require a new profile identity; compatible corrections require a new profile version. Presentation-only changes are metadata.
""")
    write_doc("RDS_BINDING_SCHEMA_SPEC.md", """# RDS application binding schema specification

A binding fixes application context without redefining construct or method. Its immutable identity is `bindingId + bindingVersion`, and it anchors the exact RDS and profile versions/hashes. Applicable dimensions include population, jurisdiction, organization, network boundary, node set, tie relation, instrument, source, windows, unit, scenario state and parameters. Different context with the same computation uses a new or revised binding; method changes are prohibited in bindings.
""")
    write_doc("RDS_EXECUTION_CONTRACT.md", """# RDS prototype execution contract

An execution request must explicitly name `rdsId`, `profileId`, `profileVersion`, `bindingId` and `bindingVersion`. `LATEST`, `DEFAULT`, `FIRST`, `MOST_RECENT`, `ACTIVE_PROFILE`, `AUTO_SELECT` and `BEST_MATCH` are rejected. The runtime returns explicit executability states and never interprets missing profile/binding as zero or null.

Definition and input hashes, units, boundaries, metric variant and normalization must match. Provenance records method, context, inputs, output and a deterministic fingerprint. Computability does not imply active status, causal source eligibility, simulation-node eligibility, intervention eligibility or effect-target eligibility. Every prototype profile carries `causalSourceEligible=false` and `WP-PSG-005_REQUIRED`.
""")
    write_doc("RDS_MIGRATION_DRY_RUN.md", f"""# 41-RDS migration dry run

All 41 production RDS appear exactly once. No row authorizes production mutation.

| Category | Count |
|---|---:|
| READY_FOR_PROFILE_MATERIALIZATION | {c['READY_FOR_PROFILE_MATERIALIZATION']} |
| PROFILE_DEFINITION_REQUIRED | {c['PROFILE_DEFINITION_REQUIRED']} |
| MULTIPLE_PROFILE_REVIEW_REQUIRED | {c['MULTIPLE_PROFILE_REVIEW_REQUIRED']} |
| LATENT_ESTIMATION_DESIGN_REQUIRED | {c['LATENT_ESTIMATION_DESIGN_REQUIRED']} |
| NON_EXECUTABLE_PENDING_SCIENCE | {c['NON_EXECUTABLE_PENDING_SCIENCE']} |
| BLOCKED_BY_ONTOLOGY | {c['BLOCKED_BY_ONTOLOGY']} |

No classifications changed. RDS-0006 receives a proposed additive wrapper preview. Thirteen definition tasks receive gaps rather than formulas. Twelve multiple-profile cases receive identity-review dimensions. Thirteen science-pending and two ontology-blocked RDS remain non-executable.
""")
    rows = "\n".join(f"| `{r['consumer']}` | {r['classification']} | {r['futurePath']} |" for r in consumers["consumers"])
    write_doc("RDS_CONSUMER_IMPACT_ANALYSIS.md", f"""# RDS consumer impact analysis

| Consumer | Classification | Backward-compatible path |
|---|---|---|
{rows}

The legacy derivation remains the only exact governed executable calculation. No current consumer must migrate in Phase 0. Phase 1 can shadow RDS-0006 beside the legacy evaluator without feeding active simulation.
""")
    write_doc("RDS_PRODUCTION_IMPLEMENTATION_PLAN.md", """# RDS production implementation plan

This is a design preview, not authorization.

1. **Phase 0:** add production schemas, empty registries, exact validators, eligibility service and causal firewall; migrate zero RDS.
2. **Phase 1:** add only the RDS-0006 compatibility wrapper and binding; preserve `DER-V1-SOC-F07-001`; run numeric/provenance shadow equivalence; do not feed active simulation.
3. **Later batches:** require separate scientific governance. The remaining 40 RDS stay unchanged.

Rollback removes profile-aware integration and empty/new registries while leaving every RDS identity and legacy derivation untouched. Shadow failure returns to legacy-only behavior. WP-PSG-005 receives exact profile/binding/input-role/constituent/output semantics with causal eligibility still false.
""")
    approval = "Approve `DP-PSG-001-IMPLEMENTATION` for a bounded production Phase 0 that installs the governed RDS computation-profile schemas, empty registries, exact-version validators, execution-eligibility service, provenance/fingerprint contract, and mandatory `WP-PSG-005` causal firewall with zero RDS migrations; then authorize a separately gated Phase 1 compatibility wrapper for `RDS-0006` only, preserving `DER-V1-SOC-F07-001` and its lineage, requiring shadow-mode numeric and provenance equivalence, rollback to legacy-only behavior, no active simulation feed, and `causalSourceEligible=false`. All other 40 RDS, production Relationships, lifecycle states, ontology, Network State, Actions & Events, sources, and activation remain unchanged and unauthorized."
    write_doc("RDS_PRODUCTION_IMPLEMENTATION_DECISION_PACKET.md", f"""# DP-PSG-001-IMPLEMENTATION — bounded production implementation

**Status:** HUMAN ARCHITECTURE GOVERNANCE REQUIRED

The prototype validates the B+C contract and RDS-0006 equivalence. The next consequential step is narrow: Phase 0 installs empty architecture; Phase 1 may wrap RDS-0006 only after Phase 0 gates pass. The remaining 40 RDS and all causal-source questions are excluded.

## Required gates

- exact immutable versions and no silent resolution;
- empty registries in Phase 0;
- protected-science hashes and rollback;
- shadow numeric/provenance equivalence for Phase 1;
- legacy ID/lineage preservation;
- causal eligibility false and separate WP-PSG-005 governance;
- no lifecycle, activation, Relationship or source changes.

## Exact bounded approval statement

> {approval}
""")


def update_roadmap():
    path = ROOT / "data/governance/post-scale-up/work-packages.json"
    implementation_decision = ROOT / "data/governance/post-scale-up/rds/rds-production-implementation-decision-001.json"
    if implementation_decision.exists():
        # The historical prototype generator must not roll back a later,
        # governed production implementation state.
        return
    payload = read(path)
    wp = next(row for row in payload["workPackages"] if row["workPackageId"] == "WP-PSG-001")
    wp["stages"]["E_implementation"] = "COMPLETE_NON_PRODUCTION_REFERENCE_PROTOTYPE"
    wp["stages"]["F_migrationRevalidation"] = "DRY_RUN_ONLY_COMPLETE_PRODUCTION_MIGRATION_NOT_AUTHORIZED"
    wp["productionImplementationStatus"] = "HUMAN_GOVERNANCE_REQUIRED_NOT_STARTED"
    wp["rootIssueResolutionStatus"] = "NOT_RESOLVED_PROTOTYPE_ONLY"
    wp["nextDecisionPacketId"] = "DP-PSG-001-IMPLEMENTATION"
    write_json(path, payload)


def main():
    build_schemas()
    legacy, profile, binding, result = build_registry()
    manifest = migration_dry_run(legacy, profile, binding)
    consumers, delta = consumer_and_delta(legacy, result)
    protected_hashes()
    docs(manifest, consumers, delta, result)
    update_roadmap()
    (HERE / "README.md").write_text("# Non-production RDS computation prototype\n\nThis namespace is isolated from production runtime and schema paths. It is authorized by `GOV-RDS-CONTRACT-001-2026-09-25` for prototype and dry-run use only.\n", encoding="utf-8")


if __name__ == "__main__":
    main()
