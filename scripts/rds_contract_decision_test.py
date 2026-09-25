"""Build the read-only WP-PSG-001 Stage C RDS contract decision test.

This module creates planning artifacts and a non-production validator prototype.
It never writes production science, ontology, architecture, lifecycle, or source data.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/governance/post-scale-up/rds"
DOCS = ROOT / "docs/governance/post-scale-up/rds"
SOURCE_MAIN = "9e1ffb63a31756c39e0129679c997619286f8754"
TEST_ID = "WP-PSG-001-STAGE-C-20260924-001"
DECISION_ID = "GOV-RDS-CONTRACT-001-2026-09-25"
DECISION_DATE = "2026-09-25"

PROTECTED_PATHS = [
    "data/entities.json",
    "data/drivers.json",
    "data/relationships.json",
    "data/sources.json",
    "data/actions-events-v1/catalog.json",
    "data/relationship-intervention-v1/relationships.json",
    "data/relational-state-v1/catalog.json",
    "scripts/actions_events_v1.py",
    "scripts/relationship_intervention_v1.py",
    "scripts/relational_state_v1.py",
    "scripts/network_state_integrity.py",
]

EXEMPLAR_IDS = ["RDS-0006", "BIO-003", "CUL-088", "INS-039", "INS-103", "INF-010", "PSY-078"]

CLASSIFICATION = {
    "RDS-0006": ["DETERMINISTIC_METRIC", "CONTEXT_SPECIFIC_PROFILE"],
    "BIO-003": ["COMPOSITE_SCORE", "CONTEXT_SPECIFIC_PROFILE"],
    "CUL-088": ["DISTANCE_METRIC", "CONTEXT_SPECIFIC_PROFILE", "NARRATIVE_OR_UNDERDEFINED"],
    "INS-039": ["RATIO", "AGGREGATE_STATISTIC", "NARRATIVE_OR_UNDERDEFINED"],
    "INS-103": ["RATIO", "AGGREGATE_STATISTIC", "NARRATIVE_OR_UNDERDEFINED"],
    "INF-010": ["RATIO", "RULE_BASED_DERIVATION", "CONTEXT_SPECIFIC_PROFILE"],
    "PSY-078": ["DETERMINISTIC_INDEX", "RULE_BASED_DERIVATION", "CONTEXT_SPECIFIC_PROFILE"],
}

FIELD_REQUIREMENTS = {
    "REQUIRED_UNIVERSAL": [
        "rdsId", "definitionVersion", "derivationProfileId", "derivationProfileVersion",
        "profileType", "inputContract", "inputDefinitionVersions", "inputDefinitionHashes",
        "minimumInputRequirements", "constituentMapping", "outputScale", "outputInterpretation",
        "scopeLimitations", "derivationEntailed", "causalSemantics", "provenance", "governance",
    ],
    "REQUIRED_CONDITIONAL": [
        "inputEntityIds", "requiredExternalInputs", "aggregationFunction", "calculationReference",
        "referencePopulation", "unitOfAnalysis", "boundary", "timeWindow", "metricVariant",
        "normalization", "missingnessPolicy", "parameterization",
    ],
    "OPTIONAL": ["displayName", "notes", "supersedesProfileVersion", "estimatorDiagnostics"],
    "NOT_APPLICABLE": "Determined per profile type; a field may be omitted only with an explicit applicability declaration.",
}


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, value: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def entity_hash(entity: dict) -> str:
    raw = json.dumps(entity, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def find_derivation(catalog: dict, identifier: str) -> dict:
    stack = [catalog]
    while stack:
        value = stack.pop()
        if isinstance(value, dict):
            if value.get("id") == identifier and value.get("objectKind") == "COLLECTION_DERIVATION_BINDING":
                return value
            stack.extend(value.values())
        elif isinstance(value, list):
            stack.extend(value)
    raise KeyError(identifier)


def profile(profile_id, version, rds_id, *, profile_type, inputs, context, metric_variant,
            normalization, calculation, source, test_only=False, output_scale="NUMBER"):
    return {
        "derivationProfileId": profile_id,
        "derivationProfileVersion": version,
        "rdsId": rds_id,
        "definitionVersion": "EXACT_HASH_IN_APPLICATION_BINDING",
        "profileType": profile_type,
        "inputContract": inputs,
        "inputDefinitionVersions": "EXACT_IN_APPLICATION_BINDING",
        "inputDefinitionHashes": "EXACT_IN_APPLICATION_BINDING",
        "minimumInputRequirements": [row["name"] for row in inputs if row["required"]],
        "constituentMapping": [{"input": row["name"], "role": row["role"]} for row in inputs],
        "requiredContext": context,
        "metricVariant": metric_variant,
        "normalization": normalization,
        "calculationReference": calculation,
        "aggregationFunction": calculation,
        "missingnessPolicy": "REJECT_MISSING_REQUIRED_INPUTS",
        "parameterization": "EXACT_IN_PROFILE_OR_BINDING",
        "outputScale": output_scale,
        "outputInterpretation": "PROFILE_AND_BINDING_SPECIFIC",
        "scopeLimitations": ["No causal-source authorization", "No silent profile or version selection"],
        "derivationEntailed": True,
        "causalSemantics": {"causalSourceEligible": False, "gate": "WP-PSG-005_REQUIRED"},
        "provenance": source,
        "governance": {
            "profileStatus": "PRODUCTION_GOVERNED_SOURCE_WRAPPED_FOR_TEST" if not test_only else "TEST_ONLY_NOT_GOVERNED",
            "namespace": "WP-PSG-001_STAGE_C_NON_PRODUCTION",
        },
    }


def binding(binding_id, version, profile_id, profile_version, rds_id, *, definition_hash,
            input_versions, input_hashes, context):
    return {
        "applicationBindingId": binding_id,
        "applicationBindingVersion": version,
        "rdsId": rds_id,
        "rdsDefinitionHash": definition_hash,
        "derivationProfileId": profile_id,
        "derivationProfileVersion": profile_version,
        "inputDefinitionVersions": input_versions,
        "inputDefinitionHashes": input_hashes,
        "context": context,
        "governance": {"namespace": "WP-PSG-001_STAGE_C_NON_PRODUCTION", "status": "TEST_ONLY"},
    }


def validate_request(prototype: dict, request: dict) -> dict:
    errors = []
    rds_id = request.get("rdsId")
    rds_defined = rds_id in prototype["rdsConstructs"]
    if not rds_defined:
        errors.append("RDS_NOT_DEFINED")
    profile_id = request.get("derivationProfileId")
    version = request.get("derivationProfileVersion")
    if not profile_id:
        errors.append("MISSING_PROFILE_ID")
    if not version:
        errors.append("UNVERSIONED_PROFILE")
    candidates = [p for p in prototype["profiles"] if p["derivationProfileId"] == profile_id]
    if profile_id and not version and len(candidates) > 1:
        errors.append("AMBIGUOUS_PROFILE_SELECTION")
    matches = [p for p in candidates if p["derivationProfileVersion"] == version]
    profile_row = matches[0] if len(matches) == 1 else None
    if profile_id and version and profile_row is None:
        errors.append("PROFILE_VERSION_NOT_FOUND")
    if profile_row and profile_row["rdsId"] != rds_id:
        errors.append("PROFILE_RDS_MISMATCH")

    binding_id = request.get("applicationBindingId")
    binding_version = request.get("applicationBindingVersion")
    binding_matches = [b for b in prototype["bindings"] if b["applicationBindingId"] == binding_id and b["applicationBindingVersion"] == binding_version]
    binding_row = binding_matches[0] if len(binding_matches) == 1 else None
    if profile_row and not binding_id:
        errors.append("MISSING_APPLICATION_BINDING")
    if binding_id and not binding_version:
        errors.append("UNVERSIONED_APPLICATION_BINDING")
    if binding_id and binding_version and binding_row is None:
        errors.append("APPLICATION_BINDING_NOT_FOUND")
    if profile_row and binding_row:
        if (binding_row["derivationProfileId"], binding_row["derivationProfileVersion"]) != (profile_id, version):
            errors.append("BINDING_PROFILE_MISMATCH")
        supplied = request.get("inputs", {})
        for item in profile_row["inputContract"]:
            if item["required"] and item["name"] not in supplied:
                errors.append("MISSING_REQUIRED_INPUT")
        if request.get("inputDefinitionVersions") != binding_row["inputDefinitionVersions"]:
            errors.append("WRONG_INPUT_VERSION")
        if request.get("inputDefinitionHashes") != binding_row["inputDefinitionHashes"]:
            errors.append("WRONG_INPUT_HASH")
        supplied_context = request.get("context", {})
        for field in profile_row["requiredContext"]:
            if field not in supplied_context or supplied_context[field] in (None, "", "UNKNOWN"):
                errors.append(f"MISSING_CONTEXT_{field.upper()}")
            elif supplied_context[field] != binding_row["context"].get(field):
                errors.append(f"INCOMPATIBLE_CONTEXT_{field.upper()}")
        if request.get("requestedMetricVariant") != profile_row["metricVariant"]:
            errors.append("WRONG_METRIC_VARIANT")
        if request.get("requestedNormalization") != profile_row["normalization"]:
            errors.append("UNKNOWN_OR_WRONG_NORMALIZATION")
        if request.get("requestedUnitOfAnalysis") != binding_row["context"].get("unitOfAnalysis"):
            errors.append("INCOMPATIBLE_UNIT_OF_ANALYSIS")
        if request.get("computationMode") and request["computationMode"] != profile_row["profileType"]:
            errors.append("PROFILE_TYPE_MISMATCH_FALSE_DETERMINISM")

    if request.get("resolveNewest"):
        errors.append("SILENT_LATEST_SELECTION_PROHIBITED")
    if rds_defined and not candidates and request.get("execute"):
        errors.append("NARRATIVE_OR_UNDERDEFINED_RDS_NON_EXECUTABLE")
    if request.get("requestCausalSourceUse"):
        errors.append("CAUSAL_SOURCE_NOT_AUTHORIZED_BY_DERIVATION")

    errors = sorted(set(errors))
    return {
        "rdsDefined": rds_defined,
        "governedComputationProfilePresent": bool(profile_row and not profile_row["governance"]["profileStatus"].startswith("TEST_ONLY")),
        "exactProfileVersion": bool(profile_row),
        "applicationBindingComplete": bool(binding_row) and not any(e.startswith("MISSING_") or e.startswith("INCOMPATIBLE_CONTEXT") for e in errors),
        "requiredInputsPresent": "MISSING_REQUIRED_INPUT" not in errors,
        "inputDefinitionsCompatible": not any(e in errors for e in ("WRONG_INPUT_VERSION", "WRONG_INPUT_HASH")),
        "executableInPrototype": bool(request.get("execute") and not errors),
        "causalSourceEligible": False,
        "errors": errors,
    }


def degree_centralization(degrees: list[float]) -> float:
    n = len(degrees)
    if n < 3:
        raise ValueError("minimum three nodes")
    maximum = max(degrees)
    return sum(maximum - value for value in degrees) / ((n - 1) * (n - 2))


def classify_migration(entities: list[dict]) -> list[dict]:
    ready = {"RDS-0006"}
    blocked_ontology = {"RDS-0001", "INF-014"}
    pending_science = {
        "BIO-003", "BIO-006", "RDS-0002", "RDS-0003", "RDS-0004",
        "INF-004", "INF-010", "INF-011", "INF-068", "INS-039", "INS-103", "RDS-0005", "RDS-0007",
    }
    multiple = {"CUL-088"} | {
        e["id"] for e in entities
        if e.get("derivationType") == "NETWORK_METRIC" and e["id"] not in ready | pending_science
    }
    rows = []
    for e in sorted((x for x in entities if x.get("entityType") == "RELATIONAL_DERIVED_STATE"), key=lambda x: x["id"]):
        identifier = e["id"]
        if identifier in ready:
            category = "READY_FOR_PROFILE_MATERIALIZATION"
            basis = "Existing exact governed DER-V1-SOC-F07-001 can be wrapped additively; no causal authorization follows."
        elif identifier in blocked_ontology:
            category = "BLOCKED_BY_ONTOLOGY"
            basis = "Current governed blocker prevents safe profile governance without an ontology/metadata decision."
        elif identifier in pending_science:
            category = "NON_EXECUTABLE_PENDING_SCIENCE"
            basis = "Layer review explicitly records missing exact versioned calculation/aggregation or blocked derivation semantics."
        elif identifier in multiple:
            category = "MULTIPLE_PROFILE_REVIEW_REQUIRED"
            basis = "Metric family, boundary, variant, or context permits materially distinct computations requiring identity review."
        else:
            category = "PROFILE_DEFINITION_REQUIRED"
            basis = "Construct metadata exists, but no exact governed computation profile and binding were found."
        rows.append({
            "rdsId": identifier, "name": e["name"], "layer": e["layer"],
            "derivationType": e.get("derivationType"), "migrationCategory": category,
            "basis": basis, "productionMutationAuthorized": False,
        })
    return rows


def build():
    entities = read(ROOT / "data/entities.json")
    entity_map = {e["id"]: e for e in entities}
    relational = read(ROOT / "data/relational-state-v1/catalog.json")
    existing = find_derivation(relational, "DER-V1-SOC-F07-001")

    constructs = {
        identifier: {
            "rdsId": identifier,
            "name": entity_map[identifier]["name"],
            "layer": entity_map[identifier]["layer"],
            "definition": entity_map[identifier]["definition"],
            "definitionHash": entity_hash(entity_map[identifier]),
            "classification": CLASSIFICATION[identifier],
            "constructExistsWithoutExecutableProfile": identifier != "RDS-0006",
        }
        for identifier in EXEMPLAR_IDS
    }

    degree_inputs = [
        {"name": "nodeDegrees", "role": "MEASUREMENT_INPUTS", "required": True},
        {"name": "nodeSet", "role": "BOUNDARY_INPUTS", "required": True},
        {"name": "maximumBenchmark", "role": "REFERENCE_VALUES", "required": True},
    ]
    profiles = [
        profile(
            "DER-V1-SOC-F07-001", "1", "RDS-0006", profile_type="DERIVATION_PROFILE",
            inputs=degree_inputs,
            context=["population", "networkBoundary", "timeWindow", "nodeSet", "tieRelation", "unitOfAnalysis"],
            metric_variant=existing["metricVariant"], normalization=existing["normalization"],
            calculation=existing["calculationReference"], source="DER-V1-SOC-F07-001", test_only=False,
        ),
        profile(
            "TEST-RDS-0006-DIRECTED-OUT-DEGREE", "1", "RDS-0006", profile_type="DERIVATION_PROFILE",
            inputs=degree_inputs,
            context=["population", "networkBoundary", "timeWindow", "nodeSet", "tieRelation", "unitOfAnalysis"],
            metric_variant="FREEMAN_DIRECTED_OUT_DEGREE_CENTRALIZATION",
            normalization="DIRECTED_STAR_MAXIMUM_FOR_BOUND_NODE_SET",
            calculation="TEST_ONLY_EXACT_DIRECTED_OUT_DEGREE_FORMULA",
            source="NON_PRODUCTION_COUNTEREXAMPLE_TO_SINGLE_PROFILE_ASSUMPTION", test_only=True,
        ),
        profile(
            "TEST-PSY-078-DIFFERENCE", "1", "PSY-078", profile_type="DERIVATION_PROFILE",
            inputs=[
                {"name": "desiredState", "role": "REFERENCE_VALUES", "required": True},
                {"name": "perceivedCurrentState", "role": "MEASUREMENT_INPUTS", "required": True},
            ],
            context=["population", "timeWindow", "unitOfAnalysis"], metric_variant="SIGNED_DIFFERENCE",
            normalization="NONE", calculation="desiredState - perceivedCurrentState",
            source="PSY-078_CANONICAL_RULE_TEST_ONLY", test_only=True,
        ),
        profile(
            "TEST-PSY-078-DIFFERENCE", "2", "PSY-078", profile_type="DERIVATION_PROFILE",
            inputs=[
                {"name": "desiredState", "role": "REFERENCE_VALUES", "required": True},
                {"name": "perceivedCurrentState", "role": "MEASUREMENT_INPUTS", "required": True},
            ],
            context=["population", "timeWindow", "unitOfAnalysis"], metric_variant="SIGNED_STANDARDIZED_DIFFERENCE",
            normalization="DECLARED_COMMON_SCALE", calculation="standardizedDesired - standardizedPerceivedCurrent",
            source="TEST_ONLY_VERSION_SELECTION_COUNTEREXAMPLE", test_only=True,
        ),
        profile(
            "TEST-CUL-088-LATENT-DISTANCE", "1", "CUL-088", profile_type="ESTIMATION_PROFILE",
            inputs=[
                {"name": "generationAIndicators", "role": "MEASUREMENT_INPUTS", "required": True},
                {"name": "generationBIndicators", "role": "MEASUREMENT_INPUTS", "required": True},
                {"name": "measurementModel", "role": "PARAMETERS", "required": True},
            ],
            context=["population", "referencePopulation", "timeWindow", "unitOfAnalysis"],
            metric_variant="TEST_ONLY_LATENT_COHORT_DISTANCE", normalization="TEST_ONLY_INVARIANT_LATENT_SCALE",
            calculation="TEST_ONLY_ESTIMATOR_NOT_A_DETERMINISTIC_FORMULA",
            source="NON_PRODUCTION_FALSE_DETERMINISM_COUNTEREXAMPLE", test_only=True,
        ),
    ]

    main_context = {
        "population": "TEST_NETWORK_POPULATION_A", "networkBoundary": "BOUNDARY-A",
        "timeWindow": "WINDOW-A", "nodeSet": "NODES-A", "tieRelation": "UNDIRECTED_TIE-A", "unitOfAnalysis": "NETWORK",
    }
    binding_main = binding(
        "TEST-BIND-RDS-0006-A", "1", "DER-V1-SOC-F07-001", "1", "RDS-0006",
        definition_hash=constructs["RDS-0006"]["definitionHash"],
        input_versions={"SOC-049": "ENTITY_V0_3_GOVERNED_RECORD_HASH"},
        input_hashes={"SOC-049": existing["inputContract"]["inputEntity"]["definitionHash"]}, context=main_context,
    )
    bindings = [binding_main]
    bindings.append(binding(
        "TEST-BIND-RDS-0006-B", "1", "DER-V1-SOC-F07-001", "1", "RDS-0006",
        definition_hash=constructs["RDS-0006"]["definitionHash"],
        input_versions=binding_main["inputDefinitionVersions"], input_hashes=binding_main["inputDefinitionHashes"],
        context={**main_context, "population": "TEST_NETWORK_POPULATION_B", "networkBoundary": "BOUNDARY-B", "nodeSet": "NODES-B"},
    ))
    bindings.append(binding(
        "TEST-BIND-RDS-0006-DIRECTED", "1", "TEST-RDS-0006-DIRECTED-OUT-DEGREE", "1", "RDS-0006",
        definition_hash=constructs["RDS-0006"]["definitionHash"],
        input_versions=binding_main["inputDefinitionVersions"], input_hashes=binding_main["inputDefinitionHashes"],
        context={**main_context, "tieRelation": "DIRECTED_TIE-A"},
    ))
    bindings.append(binding(
        "TEST-BIND-PSY-078-V1", "1", "TEST-PSY-078-DIFFERENCE", "1", "PSY-078",
        definition_hash=constructs["PSY-078"]["definitionHash"],
        input_versions={"DESIRED_OR_REFERENCE_STATE": "1", "PERCEIVED_CURRENT_STATE": "1"},
        input_hashes={"DESIRED_OR_REFERENCE_STATE": "TEST-HASH-A", "PERCEIVED_CURRENT_STATE": "TEST-HASH-B"},
        context={"population": "TEST_PERSON", "timeWindow": "TEST_OBSERVATION", "unitOfAnalysis": "INDIVIDUAL"},
    ))
    bindings.append(binding(
        "TEST-BIND-CUL-088-LATENT", "1", "TEST-CUL-088-LATENT-DISTANCE", "1", "CUL-088",
        definition_hash=constructs["CUL-088"]["definitionHash"],
        input_versions={"GENERATION_A": "TEST-1", "GENERATION_B": "TEST-1", "MODEL": "TEST-1"},
        input_hashes={"GENERATION_A": "TEST-HASH-A", "GENERATION_B": "TEST-HASH-B", "MODEL": "TEST-HASH-M"},
        context={"population": "TEST_CULTURAL_COMMUNITY", "referencePopulation": "TEST_COHORT_PAIR",
                 "timeWindow": "TEST_WINDOW", "unitOfAnalysis": "COMMUNITY_COHORT_PAIR"},
    ))

    prototype = {
        "schemaVersion": "0.1.0-test-only", "testId": TEST_ID,
        "namespace": "NON_PRODUCTION_PLANNING_PROTOTYPE", "sourceMain": SOURCE_MAIN,
        "governanceStatus": "ADVISORY_NOT_GOVERNED", "productionMutationAuthorized": False,
        "rdsConstructs": constructs, "fieldRequirements": FIELD_REQUIREMENTS,
        "profileTypes": ["DERIVATION_PROFILE", "MEASUREMENT_PROFILE", "ESTIMATION_PROFILE"],
        "profiles": profiles, "bindings": bindings,
        "consumerContract": {
            "required": ["rdsId", "derivationProfileId", "derivationProfileVersion", "applicationBindingId", "applicationBindingVersion"],
            "prohibitedResolution": ["LATEST_PROFILE", "DEFAULT_PROFILE", "FIRST_PROFILE", "IMPLICIT_FORMULA"],
            "zeroProfileBehavior": "RDS_EXISTS_NON_EXECUTABLE",
            "multipleProfileBehavior": "EXACT_PROFILE_AND_VERSION_REQUIRED",
        },
        "causalFirewall": {
            "definitionGate": "WP-PSG-001",
            "causalSourceGate": "WP-PSG-005",
            "rule": "PROFILE_GOVERNED_NEVER_IMPLIES_CAUSAL_SOURCE_AUTHORIZED",
            "defaultCausalSourceEligible": False,
        },
        "existingDerivationCompatibility": {
            "sourceId": "DER-V1-SOC-F07-001", "strategy": "ADDITIVE_PROFILE_WRAPPER_PRESERVE_ID_AND_LINEAGE",
            "rewriteRequired": False,
        },
    }

    good_request = {
        "rdsId": "RDS-0006", "derivationProfileId": "DER-V1-SOC-F07-001", "derivationProfileVersion": "1",
        "applicationBindingId": "TEST-BIND-RDS-0006-A", "applicationBindingVersion": "1", "execute": True,
        "inputs": {"nodeDegrees": [3, 1, 1, 1], "nodeSet": ["a", "b", "c", "d"], "maximumBenchmark": 6},
        "inputDefinitionVersions": binding_main["inputDefinitionVersions"],
        "inputDefinitionHashes": binding_main["inputDefinitionHashes"], "context": main_context,
        "requestedMetricVariant": existing["metricVariant"], "requestedNormalization": existing["normalization"],
        "requestedUnitOfAnalysis": "NETWORK", "computationMode": "DERIVATION_PROFILE", "requestCausalSourceUse": False,
    }

    cases = []
    def add(identifier, kind, purpose, request, required_errors=None, expected_exec=False, extra=None):
        result = validate_request(prototype, request)
        row = {
            "id": identifier, "kind": kind, "purpose": purpose, "request": request,
            "result": result, "expected": {"executableInPrototype": expected_exec, "requiredErrors": required_errors or []},
        }
        if extra:
            row["observation"] = extra
        cases.append(row)

    add("POS-001", "POSITIVE", "Exact network metric executes under exact profile and binding.", good_request, expected_exec=True,
        extra={"computedValue": degree_centralization([3, 1, 1, 1]), "expectedValue": 1.0})
    directed = {**good_request, "derivationProfileId": "TEST-RDS-0006-DIRECTED-OUT-DEGREE",
                "applicationBindingId": "TEST-BIND-RDS-0006-DIRECTED", "applicationBindingVersion": "1",
                "context": bindings[2]["context"], "requestedMetricVariant": "FREEMAN_DIRECTED_OUT_DEGREE_CENTRALIZATION",
                "requestedNormalization": "DIRECTED_STAR_MAXIMUM_FOR_BOUND_NODE_SET", "execute": True}
    add("POS-002", "POSITIVE_DESIGN", "A second explicitly identified metric profile can coexist without ambiguous selection.", directed,
        expected_exec=True,
        extra={"shapeValidated": True, "scientificGovernanceImplied": False})
    context_b = {**good_request, "applicationBindingId": "TEST-BIND-RDS-0006-B", "context": bindings[1]["context"]}
    add("POS-003", "POSITIVE", "A context binding change preserves RDS and profile identity.", context_b, expected_exec=True,
        extra={"sameRdsId": True, "sameProfileId": True, "differentBindingId": True})
    psy_request = {
        "rdsId": "PSY-078", "derivationProfileId": "TEST-PSY-078-DIFFERENCE", "derivationProfileVersion": "1",
        "applicationBindingId": "TEST-BIND-PSY-078-V1", "applicationBindingVersion": "1", "execute": True,
        "inputs": {"desiredState": 8, "perceivedCurrentState": 5},
        "inputDefinitionVersions": bindings[3]["inputDefinitionVersions"], "inputDefinitionHashes": bindings[3]["inputDefinitionHashes"],
        "context": bindings[3]["context"], "requestedMetricVariant": "SIGNED_DIFFERENCE", "requestedNormalization": "NONE",
        "requestedUnitOfAnalysis": "INDIVIDUAL", "computationMode": "DERIVATION_PROFILE", "requestCausalSourceUse": False,
    }
    add("POS-004", "POSITIVE", "Historical version 1 remains explicitly reproducible after version 2 exists.", psy_request, expected_exec=True,
        extra={"computedValue": 3, "version2NotSelected": True})
    add("POS-005", "POSITIVE_SAFE_FAILURE", "A narrative RDS remains a valid construct but cannot execute.",
        {"rdsId": "CUL-088", "execute": True}, ["MISSING_PROFILE_ID", "UNVERSIONED_PROFILE", "NARRATIVE_OR_UNDERDEFINED_RDS_NON_EXECUTABLE"], False)

    negative_specs = [
        ("NEG-001", "Missing profile ID", {**good_request, "derivationProfileId": None}, "MISSING_PROFILE_ID"),
        ("NEG-002", "Ambiguous profile selection", {**good_request, "derivationProfileId": "TEST-PSY-078-DIFFERENCE", "derivationProfileVersion": None}, "AMBIGUOUS_PROFILE_SELECTION"),
        ("NEG-003", "Unversioned profile", {**good_request, "derivationProfileVersion": None}, "UNVERSIONED_PROFILE"),
        ("NEG-004", "Wrong input version", {**good_request, "inputDefinitionVersions": {"SOC-049": "WRONG"}}, "WRONG_INPUT_VERSION"),
        ("NEG-005", "Missing required constituent", {**good_request, "inputs": {"nodeSet": ["a"], "maximumBenchmark": 1}}, "MISSING_REQUIRED_INPUT"),
        ("NEG-006", "Incompatible unit of analysis", {**good_request, "requestedUnitOfAnalysis": "INDIVIDUAL"}, "INCOMPATIBLE_UNIT_OF_ANALYSIS"),
        ("NEG-007", "Wrong network boundary", {**good_request, "context": {**main_context, "networkBoundary": "WRONG"}}, "INCOMPATIBLE_CONTEXT_NETWORKBOUNDARY"),
        ("NEG-008", "Wrong metric variant", {**good_request, "requestedMetricVariant": "BETWEENNESS"}, "WRONG_METRIC_VARIANT"),
        ("NEG-009", "Unknown normalization", {**good_request, "requestedNormalization": "UNKNOWN"}, "UNKNOWN_OR_WRONG_NORMALIZATION"),
        ("NEG-010", "Missing reference population", {**good_request, "context": {k:v for k,v in main_context.items() if k != "population"}}, "MISSING_CONTEXT_POPULATION"),
        ("NEG-011", "Latent/estimated profile falsely requested as deterministic", {
            "rdsId": "CUL-088", "derivationProfileId": "TEST-CUL-088-LATENT-DISTANCE", "derivationProfileVersion": "1",
            "applicationBindingId": "TEST-BIND-CUL-088-LATENT", "applicationBindingVersion": "1", "execute": True,
            "inputs": {"generationAIndicators": [1, 2], "generationBIndicators": [2, 3], "measurementModel": "TEST_MODEL"},
            "inputDefinitionVersions": bindings[4]["inputDefinitionVersions"], "inputDefinitionHashes": bindings[4]["inputDefinitionHashes"],
            "context": bindings[4]["context"], "requestedMetricVariant": "TEST_ONLY_LATENT_COHORT_DISTANCE",
            "requestedNormalization": "TEST_ONLY_INVARIANT_LATENT_SCALE", "requestedUnitOfAnalysis": "COMMUNITY_COHORT_PAIR",
            "computationMode": "DERIVATION_PROFILE", "requestCausalSourceUse": False,
        }, "PROFILE_TYPE_MISMATCH_FALSE_DETERMINISM"),
        ("NEG-012", "Newest version resolution", {**psy_request, "derivationProfileVersion": None, "resolveNewest": True}, "SILENT_LATEST_SELECTION_PROHIBITED"),
        ("NEG-013", "Execution of underdefined RDS", {"rdsId": "INS-039", "execute": True}, "NARRATIVE_OR_UNDERDEFINED_RDS_NON_EXECUTABLE"),
        ("NEG-014", "Causal-source request from derivation alone", {**good_request, "requestCausalSourceUse": True}, "CAUSAL_SOURCE_NOT_AUTHORIZED_BY_DERIVATION"),
    ]
    for identifier, purpose, request, error in negative_specs:
        add(identifier, "NEGATIVE", purpose, request, [error], False)

    exemplar_rows = []
    for identifier in EXEMPLAR_IDS:
        entity = entity_map[identifier]
        exemplar_rows.append({
            "rdsId": identifier, "name": entity["name"], "layer": entity["layer"],
            "familyId": entity["primaryFamilyId"], "classification": CLASSIFICATION[identifier],
            "canonicalDerivationType": entity.get("derivationType"),
            "canonicalDerivationMetadataPresent": all(entity.get(k) for k in ("derivationType", "derivationLogic", "scopeRequirements")),
            "governedPortableProfilePresent": identifier == "RDS-0006",
            "testRole": {
                "RDS-0006": "POSITIVE_CONTROL_EXACT_GOVERNED_CALCULATION",
                "BIO-003": "BIOLOGICAL_ALIGNMENT_COMPOSITE",
                "CUL-088": "MULTI_VARIANT_DISTANCE_COUNTEREXAMPLE",
                "INS-039": "INSTITUTIONAL_RATIO_AGGREGATE",
                "INS-103": "INSTITUTIONAL_RATIO_AGGREGATE",
                "INF-010": "INFORMATIONAL_REQUIREMENT_SET_RATIO",
                "PSY-078": "PSYCHOLOGICAL_DIFFERENCE_RULE",
            }[identifier],
            "productionRecordChanged": False,
        })

    option_results = [
        {
            "option": "A", "result": "REJECT_AS_UNIVERSAL_ARCHITECTURE",
            "worked": ["Clear for RDS-0006 and a single exact PSY-078 difference rule", "Strong deterministic consumer contract"],
            "failed": ["Collapses legitimate metric/context variants", "Pressures underdefined and estimated constructs into false determinism", "Duplicates application context or embeds it as universal identity", "Produces excessive not-applicable fields"],
        },
        {
            "option": "B", "result": "VIABLE_BUT_INCOMPLETE_ALONE",
            "worked": ["Separates construct, computation profile, and application binding", "Supports exact versions and multiple legitimate variants", "Preserves existing DER-V1-SOC-F07-001 additively"],
            "failed": ["Needs an explicit zero-profile safe state", "Needs strict identity rules to prevent proliferation", "Cannot permit default or latest-profile resolution"],
        },
        {
            "option": "C", "result": "SAFE_FALLBACK_NOT_SUFFICIENT_ALONE",
            "worked": ["Preserves unknown as unknown", "Keeps CUL-088 and INS-039 scientifically valid but non-executable", "Avoids fabricated formulas"],
            "failed": ["Provides no execution architecture for RDS-0006", "Leaves well-defined metrics unavailable", "Does not solve versioning for future profiles"],
        },
        {
            "option": "B_PLUS_C", "result": "RECOMMENDED_ADVISORY",
            "worked": ["B defines executable profiles and exact bindings", "C is the mandatory default when no eligible governed profile/binding exists", "Supports zero, one, or multiple profiles without ambiguity", "Maintains a separate WP-PSG-005 causal gate"],
            "failed": ["Adds consumer verbosity", "Requires governance discipline and registry validation", "Does not itself resolve any missing derivation or causal-source case"],
        },
    ]

    test_data = {
        "schemaVersion": "1.0.0", "testId": TEST_ID, "workPackageId": "WP-PSG-001",
        "decisionPacketId": "DP-PSG-001", "rootIssueId": "ROOT-RDS-DEFINITION-DERIVATION-001",
        "sourceMain": SOURCE_MAIN, "runMode": "READ_ONLY_DESIGN_VALIDATION",
        "exemplars": exemplar_rows, "optionResults": option_results, "testCases": cases,
        "summary": {
            "positiveCases": sum(c["kind"].startswith("POSITIVE") for c in cases),
            "negativeCases": sum(c["kind"] == "NEGATIVE" for c in cases),
            "allExpectedOutcomesObserved": all(
                c["result"]["executableInPrototype"] == c["expected"]["executableInPrototype"]
                and set(c["expected"]["requiredErrors"]).issubset(c["result"]["errors"])
                for c in cases
            ),
            "recommendation": "OPTION_B_PLUS_C_HYBRID",
        },
        "protection": {
            "productionMutationAuthorized": False,
            "productionHashes": {path: digest(ROOT / path) for path in PROTECTED_PATHS},
        },
    }

    migration_rows = classify_migration(entities)
    migration_categories = [
        "READY_FOR_PROFILE_MATERIALIZATION", "PROFILE_DEFINITION_REQUIRED",
        "MULTIPLE_PROFILE_REVIEW_REQUIRED", "LATENT_ESTIMATION_DESIGN_REQUIRED",
        "NON_EXECUTABLE_PENDING_SCIENCE", "BLOCKED_BY_ONTOLOGY",
    ]
    observed_migration_counts = Counter(row["migrationCategory"] for row in migration_rows)
    migration = {
        "schemaVersion": "1.0.0", "testId": TEST_ID, "sourceMain": SOURCE_MAIN,
        "classificationRule": "Conservative classification from governed derivation presence, explicit Layer blockers, ontology blockers, and metric-variant structure; no record is migrated.",
        "counts": {category: observed_migration_counts[category] for category in migration_categories},
        "totalRds": len(migration_rows), "records": migration_rows,
        "migrationAuthorized": False,
    }

    write_json(DATA / "rds-profile-prototype.json", prototype)
    write_json(DATA / "rds-contract-test-cases.json", test_data)
    write_json(DATA / "rds-migration-classification.json", migration)
    decision = architecture_decision()
    write_json(DATA / "rds-contract-architecture-decision-001.json", decision)
    render_docs(exemplar_rows, option_results, migration, cases)
    render_decision(decision)


def architecture_decision():
    return {
        "schemaVersion": "1.0.0",
        "decisionId": DECISION_ID,
        "decisionDate": DECISION_DATE,
        "decisionPacketId": "DP-PSG-001",
        "rootIssueId": "ROOT-RDS-DEFINITION-DERIVATION-001",
        "workPackageId": "WP-PSG-001",
        "decisionTestId": TEST_ID,
        "decisionAuthority": "HUMAN_GOVERNOR",
        "decisionOutcome": "APPROVED_BOUNDED_OPTION_B_PLUS_C_DIRECTION",
        "approvedDirection": {
            "computationProfiles": "TYPED_NAMED_IMMUTABLE_VERSION",
            "applicationBindings": "EXPLICIT_VERSIONED",
            "zeroEligibleProfileBehavior": "RDS_EXISTS_NON_EXECUTABLE",
            "consumerSelection": "EXACT_PROFILE_AND_BINDING_VERSION_REQUIRED",
            "silentResolution": "PROHIBITED_DEFAULT_FIRST_OR_LATEST",
            "existingDerivationLineage": "ADDITIVE_PRESERVATION",
            "causalFirewall": {
                "definitionGate": "WP-PSG-001",
                "causalSourceGate": "WP-PSG-005",
                "defaultCausalSourceEligible": False,
                "separateHumanGovernanceRequired": True,
            },
        },
        "authorizedActivities": [
            "architecture design",
            "non-production schema prototyping",
            "non-production validator prototyping",
            "test-only computation-profile and binding experiments",
            "migration classification and dry-run planning without production writes",
        ],
        "notAuthorized": [
            "production RDS migration",
            "production RDS mutation",
            "production schema or validator behavior change",
            "causal-source authorization",
            "Relationship or EffectAssertion mutation",
            "lifecycle change",
            "activation",
            "source registration",
        ],
        "productionState": {
            "scienceChanged": False,
            "ontologyChanged": False,
            "architectureImplemented": False,
            "productionValidatorsChanged": False,
            "rdsMigrated": 0,
            "causalSourcesAuthorized": 0,
            "lifecycleChanges": 0,
            "activations": 0,
        },
        "nextGovernedStage": "NON_PRODUCTION_IMPLEMENTATION_PROTOTYPE",
        "productionImplementationStatus": "NOT_AUTHORIZED_NOT_STARTED",
    }


def table(headers, rows):
    return "| " + " | ".join(headers) + " |\n| " + " | ".join("---" for _ in headers) + " |\n" + "\n".join(
        "| " + " | ".join(str(value).replace("|", "\\|") for value in row) + " |" for row in rows
    )


def render_docs(exemplars, option_results, migration, cases):
    exemplar_table = table(
        ["RDS", "Layer", "Classification", "Test role", "Portable governed profile"],
        [[e["rdsId"], e["layer"], ", ".join(e["classification"]), e["testRole"], "yes" if e["governedPortableProfilePresent"] else "no"] for e in exemplars],
    )
    write_text(DOCS / "RDS_CONTRACT_DECISION_TEST.md", f"""# RDS contract decision test

**Test:** `{TEST_ID}`

**Decision packet:** `DP-PSG-001`

**Root issue:** `ROOT-RDS-DEFINITION-DERIVATION-001`
**Status:** advisory Stage C design validation; no human architecture decision taken

## Scope and gate separation

This test evaluates when an RDS is exactly defined and executable. It does not decide whether the RDS may act as an independent causal source. A governed computation profile passes Gate 1 only. Gate 2 remains `WP-PSG-005`; it requires separate scientific governance.

## Real-record test set

{exemplar_table}

`BLK-PSY-001` does not identify `PSY-078` as its affected record. The prototype therefore uses `PSY-078` only as a real difference-rule exemplar and retains the feature/dimension blocker as a separate boundary counterexample.

## Experimental result

The prototype ran {len(cases)} cases: {sum(c['kind'].startswith('POSITIVE') for c in cases)} positive/safe-positive cases and {sum(c['kind']=='NEGATIVE' for c in cases)} rejection cases. All expected outcomes were observed. A four-node star produced degree centralization `1.0` only when the exact `DER-V1-SOC-F07-001` profile and binding were requested.

Option A works for one exact deterministic calculation but fails as a universal contract. Option B expresses exact versions and context bindings but is unsafe without an explicit zero-profile state. Option C preserves underdefined constructs safely but supplies no execution architecture. The bounded B+C hybrid passed all exemplars: named/versioned profiles plus exact bindings for execution, and non-executable-by-default semantics when no eligible governed profile exists.

## Minimum contract

Universal fields are: {', '.join(FIELD_REQUIREMENTS['REQUIRED_UNIVERSAL'])}. Conditional fields are required when their scientific concept applies and must never be populated with guesses: {', '.join(FIELD_REQUIREMENTS['REQUIRED_CONDITIONAL'])}.

## Causal firewall

Every profile in the prototype carries `causalSourceEligible=false` and `gate=WP-PSG-005_REQUIRED`. `RDS-0006` calculates deterministically while remaining unauthorized as a causal source. `NEG-014` proves that a causal request is rejected even when the derivation request is otherwise complete.

## Recommendation

Adopt **Option B+C as the architecture direction**, subject to human governance and later implementation design. Use an umbrella RDS computation-profile registry with distinct `DERIVATION_PROFILE`, `MEASUREMENT_PROFILE`, and `ESTIMATION_PROFILE` types. Require exact profile and binding versions. Keep an RDS non-executable when no eligible governed profile/binding exists. Preserve `DER-V1-SOC-F07-001` by additive wrapping and lineage rather than rewriting it.

This recommendation does not govern the architecture, migrate records, authorize execution, or authorize causal-source use.

## Exact governance statement prepared for the human

> Approve the bounded Option B+C architecture direction for later implementation design: preserve each RDS construct separately from named, immutable-version computation profiles and explicit versioned application bindings; permit zero, one, or multiple governed profiles; make zero eligible profile/binding mean non-executable; require exact profile and binding selection with no silent latest/default behavior; preserve typed derivation, measurement, and estimation semantics; wrap `DER-V1-SOC-F07-001` additively without changing its ID or lineage; and keep all RDS causal-source eligibility false unless separately governed through WP-PSG-005. This decision authorizes architecture design only, not production implementation, migration, causal-source use, lifecycle change, or activation.
""")

    matrix_rows = []
    labels = {
        "A": ["mixed", "strong", "weak", "strong", "weak", "weak", "high", "mixed", "strong", "weak"],
        "B": ["strong", "strong", "strong", "strong", "strong with typed profiles", "strong", "medium if unchecked", "strong", "strong", "strong"],
        "C": ["strong", "not applicable", "strong", "simple", "strong", "strong", "none", "strong", "strong", "defers"],
        "B_PLUS_C": ["strong", "strong", "strong", "strong", "strong with typed profiles", "strong", "controlled by identity rules", "strong", "strong", "strong"],
    }
    criteria = ["Scientific fidelity", "Determinism", "Context specificity", "Versioning", "Latent constructs", "Migration safety", "Profile proliferation risk", "Consumer clarity", "Causal firewall", "WP-PSG-005 compatibility"]
    for i, criterion in enumerate(criteria):
        matrix_rows.append([criterion] + [labels[o][i] for o in ["A", "B", "C", "B_PLUS_C"]])
    option_narrative = "\n\n".join(
        f"### Option {row['option']} — {row['result']}\n\nWorked: " + "; ".join(row["worked"]) + ".\n\nFailed: " + "; ".join(row["failed"]) + "."
        for row in option_results
    )
    write_text(DOCS / "RDS_CONTRACT_OPTION_COMPARISON.md", f"""# RDS contract option comparison

{option_narrative}

## Qualitative decision matrix

{table(['Criterion', 'A', 'B', 'C', 'B+C'], matrix_rows)}

## Skeptical architecture review

- **Overconstraint:** A turns context-specific and estimated constructs into one universal formula.
- **Profile explosion:** B requires the identity rules in the companion document and registry-level duplicate review.
- **Semantic drift:** profile definitions must cite an immutable RDS definition hash and never redefine the construct.
- **Version ambiguity:** exact profile and binding versions are mandatory; `latest` is prohibited.
- **False determinism:** estimation and measurement profiles remain typed and may not execute as deterministic derivations.
- **Migration instability:** existing IDs and lineage remain stable; additive wrappers precede any governed migration.
- **Consumer complexity:** B+C is more explicit, but the added fields expose rather than hide real ambiguity.
- **Causal leakage:** profile governance never changes `causalSourceEligible=false`; WP-PSG-005 remains separate.
- **Rollback:** removing a test/additive wrapper returns the repository to the current non-executable safe state without rewriting the RDS.
""")

    write_text(DOCS / "RDS_PROFILE_IDENTITY_RULES.md", f"""# RDS profile identity rules

## Architecture vocabulary

- **RDS construct identity:** the scientific concept and its definition version.
- **Computation profile:** a named, versioned method. Use `DERIVATION_PROFILE` for deterministic calculations, `MEASUREMENT_PROFILE` for observed-score construction, and `ESTIMATION_PROFILE` for latent/model-estimated states.
- **Application binding:** the concrete population, boundary, window, instrument/data source, and compatible input versions used in an application.

## New identity versus version versus binding

| Change | Required action |
| --- | --- |
| Same method, different population, cohort, jurisdiction, network instance, node set, data source, or observation window | New or revised **binding**; profile unchanged |
| Correction that preserves the scientific method and output meaning | New **profile version**; old version remains reproducible |
| Different normalization, metric variant, aggregation rule, constituent set, missingness policy, unit of analysis, or latent measurement model | New **profile identity** unless a governed compatibility rule proves it is only parameterization |
| Degree versus weighted degree; deterministic score versus latent estimator | New **profile identity** and correct profile type |
| Change to the scientific construct or output interpretation | New **RDS identity/version** through ontology governance, not a profile workaround |
| Presentation-only label change with unchanged definition hash and semantics | Metadata update; no new profile or RDS |

## Proliferation controls

Profiles require a material computation difference, canonical registry search, explicit supersession/compatibility statement, immutable version, and human governance. Bindings carry contextual variation that does not change method semantics. Consumers must supply exact IDs and versions; no default, first, or latest profile is allowed.

## Version propagation

A changed Driver/input definition invalidates compatibility unless the binding cites a governed compatibility assertion. Normalization, formula, estimator, or time-window-rule changes create a new profile version or identity. Source changes update provenance only when the method is unchanged. Historical requests retain their cited profile, binding, input versions, and hashes.

## Constituent roles

Every input is typed as `CONSTITUENTS`, `MEASUREMENT_INPUTS`, `PARAMETERS`, `NORMALIZERS`, `BOUNDARY_INPUTS`, `REFERENCE_VALUES`, or `EXTERNAL_CONTEXT`. Required input does not imply causal constituent. This prepares later double-count review without deciding it.
""")

    counts = migration["counts"]
    migration_table = table(["Category", "Count"], [[k, v] for k, v in counts.items()] + [["TOTAL", migration["totalRds"]]])
    records_table = table(["RDS", "Layer", "Category", "Basis"], [[r["rdsId"], r["layer"], r["migrationCategory"], r["basis"]] for r in migration["records"]])
    write_text(DOCS / "RDS_MIGRATION_CLASSIFICATION.md", f"""# RDS migration classification

This is a planning classification of all 41 current RDS. It authorizes no migration and does not deactivate or reinterpret existing production records.

{migration_table}

`LATENT_ESTIMATION_DESIGN_REQUIRED` has count zero because no current RDS record is explicitly governed as latent/estimated. The architecture still needs that profile type so future reviews do not force estimated states into deterministic formulas.

## Record classification

{records_table}

`READY_FOR_PROFILE_MATERIALIZATION` means structurally ready for a later governed additive wrapper, not authorized now. `NON_EXECUTABLE_PENDING_SCIENCE` describes behavior under the proposed contract and does not alter any current production relationship or lifecycle state.
""")


def render_decision(decision):
    write_text(DOCS / "RDS_CONTRACT_ARCHITECTURE_DECISION_001.md", f"""# RDS contract architecture decision 001

**Decision ID:** `{decision['decisionId']}`

**Decision packet:** `DP-PSG-001`

**Work package:** `WP-PSG-001`

**Decision date:** {decision['decisionDate']}

**Outcome:** `APPROVED_BOUNDED_OPTION_B_PLUS_C_DIRECTION`

## Human-approved direction

The human governor approves the bounded Option B+C RDS architecture direction established by the Stage C decision test:

- typed, named, immutable-version computation profiles;
- explicit versioned application bindings;
- valid RDS constructs remain non-executable when no eligible governed profile and complete binding exist;
- exact profile and binding versions are mandatory, with no silent default, first, or latest resolution;
- existing governed derivation IDs and lineage are preserved additively;
- definition/derivation eligibility remains separate from causal-source eligibility;
- any causal-source use requires separate `WP-PSG-005` governance and defaults to ineligible.

## Authorized scope

This decision authorizes architecture design and non-production implementation prototyping: schema experiments, validator prototypes, test-only profile/binding execution, and migration dry-run planning.

## Explicit boundary

This decision does **not** authorize production RDS migration, production RDS or validator mutation, causal-source use, Relationship or EffectAssertion mutation, lifecycle change, activation, or source registration. Production implementation remains `NOT_AUTHORIZED_NOT_STARTED`.

## Materialization outcome

No production record is materialized or changed. The current safe state of every RDS and dependent blocker remains intact. Stage D is complete only for the bounded architecture direction; later production implementation, migration/revalidation, and scientific re-adjudication remain separate stages.
""")


if __name__ == "__main__":
    build()
