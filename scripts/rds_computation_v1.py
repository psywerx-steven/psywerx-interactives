"""Governed RDS computation-profile contracts and exact execution eligibility.

The service is fail-closed. Computability is separate from lifecycle, simulation,
effect-target, intervention-target, and causal-source authorization.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"
DATA_DIR = ROOT / "data/rds-computation-v1"
PROFILE_TYPES = {"DERIVATION_PROFILE", "MEASUREMENT_PROFILE", "ESTIMATION_PROFILE"}
INPUT_ROLES = {"CONSTITUENT", "MEASUREMENT_INPUT", "PARAMETER", "NORMALIZER", "BOUNDARY_INPUT", "REFERENCE_VALUE", "EXTERNAL_CONTEXT", "DATA_SOURCE"}
FORBIDDEN_SELECTORS = {"LATEST", "DEFAULT", "FIRST", "MOST_RECENT", "ACTIVE_PROFILE", "AUTO_SELECT", "BEST_MATCH"}
ELIGIBILITY_STATES = {"EXECUTABLE", "NON_EXECUTABLE_NO_PROFILE", "NON_EXECUTABLE_NO_ELIGIBLE_PROFILE", "NON_EXECUTABLE_INCOMPLETE_BINDING", "NON_EXECUTABLE_VERSION_MISMATCH", "NON_EXECUTABLE_DEFINITION_MISMATCH", "NON_EXECUTABLE_INPUT_MISMATCH", "NON_EXECUTABLE_PROFILE_TYPE_UNSUPPORTED", "NON_EXECUTABLE_BLOCKED_BY_SCIENCE", "NON_EXECUTABLE_BLOCKED_BY_ONTOLOGY"}


class ValidationError(ValueError):
    pass


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValidationError(reason)


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


@lru_cache(maxsize=1)
def validators() -> dict[str, Draft202012Validator]:
    names = {
        "profile": "rds-computation-profile.schema.json",
        "binding": "rds-application-binding.schema.json",
        "request": "rds-execution-request.schema.json",
        "provenance": "rds-execution-provenance.schema.json",
        "eligibility": "rds-execution-eligibility.schema.json",
    }
    result = {}
    for key, name in names.items():
        value = read(SCHEMA_DIR / name)
        Draft202012Validator.check_schema(value)
        result[key] = Draft202012Validator(value)
    return result


def validate_schema(name: str, record: dict[str, Any]) -> None:
    errors = sorted(validators()[name].iter_errors(record), key=lambda error: str(list(error.path)))
    require(not errors, f"{name}: {errors[0].message}" if errors else "")


def exact_version(value: Any, label: str) -> None:
    require(isinstance(value, str) and bool(value.strip()), f"{label} requires exact non-empty version")
    require(value.upper() not in FORBIDDEN_SELECTORS, f"{label} prohibits implicit selector {value}")


def validate_computation_profile(profile: dict[str, Any]) -> bool:
    validate_schema("profile", profile)
    exact_version(profile["profileVersion"], "profileVersion")
    exact_version(profile["rdsDefinitionVersion"], "rdsDefinitionVersion")
    require(profile["profileType"] in PROFILE_TYPES, "Unsupported profile type")
    require(profile["architectureGovernance"]["status"] == "GOVERNED", "Production profile requires governed architecture record")
    require(profile["causalSourceEligible"] is False, "Causal-source eligibility defaults false")
    require(profile["causalSourceGate"] == "WP-PSG-005_REQUIRED", "Separate WP-PSG-005 governance required")
    require({row["role"] for row in profile["inputContract"]} <= INPUT_ROLES, "Unknown input role")
    kind = profile["profileType"]
    if kind == "DERIVATION_PROFILE":
        require(profile["derivationEntailed"] is True and bool(profile.get("calculationReference")), "Derivation profile requires entailed exact calculation")
        require(not profile.get("measurementProcedure") and not profile.get("estimationProcedure"), "Derivation profile type contradiction")
    elif kind == "MEASUREMENT_PROFILE":
        require(profile["derivationEntailed"] is False and bool(profile.get("measurementProcedure")), "Measurement procedure required without ontology entailment")
        require(not profile.get("calculationReference") and not profile.get("estimationProcedure"), "Measurement profile type contradiction")
    else:
        procedure = profile.get("estimationProcedure") or {}
        require(profile["derivationEntailed"] is False and procedure.get("modelSemantics") and procedure.get("diagnosticExpectations"), "Estimation semantics and diagnostics required")
        require(not profile.get("calculationReference") and not profile.get("measurementProcedure"), "Estimation profile type contradiction")
    return True


def validate_application_binding(binding: dict[str, Any]) -> bool:
    validate_schema("binding", binding)
    exact_version(binding["bindingVersion"], "bindingVersion")
    exact_version(binding["profileVersion"], "profileVersion")
    require(binding["architectureGovernance"]["status"] == "GOVERNED", "Production binding requires governed architecture record")
    require(not ({"calculationReference", "measurementProcedure", "estimationProcedure"} & set(binding)), "Binding cannot redefine computation method")
    return True


def validate_profile_binding_compatibility(profile: dict[str, Any], binding: dict[str, Any]) -> bool:
    validate_computation_profile(profile)
    validate_application_binding(binding)
    for key in ("rdsId", "rdsDefinitionVersion", "rdsDefinitionHash", "profileId", "profileVersion"):
        require(binding[key] == profile[key], f"Profile/binding {key} mismatch")
    require(binding["unitOfAnalysis"] == profile["unitOfAnalysis"], "Unit of analysis mismatch")
    for requirement in profile.get("requiredContext", []):
        require(binding.get("contextContract", {}).get(requirement) is not None, f"Binding omits context contract {requirement}")
    return True


def validate_registry_immutability(rows: list[dict[str, Any]], identity_key: str, version_key: str) -> bool:
    seen: dict[tuple[str, str], str] = {}
    for row in rows:
        identity = (row[identity_key], row[version_key])
        record_hash = digest(row)
        require(identity not in seen or seen[identity] == record_hash, f"Immutable version collision {identity}")
        seen[identity] = record_hash
    return True


def load_registries() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    profiles_payload = read(DATA_DIR / "profiles.json")
    bindings_payload = read(DATA_DIR / "bindings.json")
    require(profiles_payload["schemaVersion"] == "1.0.0" and bindings_payload["schemaVersion"] == "1.0.0", "Registry schema version mismatch")
    profiles, bindings = profiles_payload["profiles"], bindings_payload["bindings"]
    for row in profiles:
        validate_computation_profile(row)
    for row in bindings:
        validate_application_binding(row)
    validate_registry_immutability(profiles, "profileId", "profileVersion")
    validate_registry_immutability(bindings, "bindingId", "bindingVersion")
    require(len({(row["profileId"], row["profileVersion"]) for row in profiles}) == len(profiles), "Duplicate profile identity/version")
    require(len({(row["bindingId"], row["bindingVersion"]) for row in bindings}) == len(bindings), "Duplicate binding identity/version")
    return profiles, bindings


def resolve_execution_eligibility(request: dict[str, Any], current_definition_hash: str) -> dict[str, Any]:
    try:
        validate_schema("request", request)
        for key in ("profileVersion", "bindingVersion"):
            exact_version(request[key], key)
    except ValidationError as error:
        state = "NON_EXECUTABLE_VERSION_MISMATCH" if any(selector in str(error) for selector in FORBIDDEN_SELECTORS) else "NON_EXECUTABLE_INCOMPLETE_BINDING"
        return {"schemaVersion": "1.0.0", "state": state, "reason": str(error), "causalSourceAuthorized": False}
    profiles, bindings = load_registries()
    candidates = [row for row in profiles if row["rdsId"] == request["rdsId"]]
    if not candidates:
        return {"schemaVersion": "1.0.0", "state": "NON_EXECUTABLE_NO_PROFILE", "reason": "No profile for RDS", "causalSourceAuthorized": False}
    eligible = [row for row in candidates if row["executionMode"] == "SHADOW_ONLY"]
    if not eligible:
        return {"schemaVersion": "1.0.0", "state": "NON_EXECUTABLE_NO_ELIGIBLE_PROFILE", "reason": "No execution-eligible profile", "causalSourceAuthorized": False}
    profile = next((row for row in eligible if row["profileId"] == request["profileId"] and row["profileVersion"] == request["profileVersion"]), None)
    if profile is None:
        return {"schemaVersion": "1.0.0", "state": "NON_EXECUTABLE_VERSION_MISMATCH", "reason": "Exact profile/version absent", "causalSourceAuthorized": False}
    binding = next((row for row in bindings if row["bindingId"] == request["bindingId"] and row["bindingVersion"] == request["bindingVersion"]), None)
    if binding is None:
        return {"schemaVersion": "1.0.0", "state": "NON_EXECUTABLE_INCOMPLETE_BINDING", "reason": "Exact binding/version absent", "causalSourceAuthorized": False}
    try:
        validate_profile_binding_compatibility(profile, binding)
    except ValidationError as error:
        return {"schemaVersion": "1.0.0", "state": "NON_EXECUTABLE_INCOMPLETE_BINDING", "reason": str(error), "causalSourceAuthorized": False}
    if profile["rdsDefinitionHash"] != current_definition_hash:
        return {"schemaVersion": "1.0.0", "state": "NON_EXECUTABLE_DEFINITION_MISMATCH", "reason": "RDS definition hash mismatch", "causalSourceAuthorized": False}
    for contract in profile["inputContract"]:
        supplied = request["inputs"].get(contract["inputId"])
        if contract.get("required", True) and supplied is None:
            return {"schemaVersion": "1.0.0", "state": "NON_EXECUTABLE_INPUT_MISMATCH", "reason": f"Missing input {contract['inputId']}", "causalSourceAuthorized": False}
        if supplied is not None and contract.get("definitionHash") and supplied["definitionHash"] != contract["definitionHash"]:
            return {"schemaVersion": "1.0.0", "state": "NON_EXECUTABLE_INPUT_MISMATCH", "reason": f"Input hash mismatch {contract['inputId']}", "causalSourceAuthorized": False}
    result = {"schemaVersion": "1.0.0", "state": "EXECUTABLE", "reason": "Exact governed profile and binding eligible for shadow execution only", "causalSourceAuthorized": False, "profile": profile, "binding": binding}
    validate_schema("eligibility", {key: result[key] for key in ("schemaVersion", "state", "reason", "causalSourceAuthorized")})
    return result


def validate_causal_firewall(profile: dict[str, Any], causal_source_requested: bool) -> bool:
    if causal_source_requested:
        require(profile.get("causalSourceEligible") is True and profile.get("causalSourceAuthorizationId"), "RDS causal-source use requires separate WP-PSG-005 governance")
    return True


def execution_fingerprint(request: dict[str, Any], profile: dict[str, Any], binding: dict[str, Any]) -> str:
    return digest({"rdsDefinitionHash": profile["rdsDefinitionHash"], "profileId": profile["profileId"], "profileVersion": profile["profileVersion"], "bindingId": binding["bindingId"], "bindingVersion": binding["bindingVersion"], "inputHashes": {key: value["valueHash"] for key, value in sorted(request["inputs"].items())}, "parameterHash": digest(request.get("parameters", {}))})


def validate_repository() -> dict[str, Any]:
    validators()
    profiles, bindings = load_registries()
    return {"profiles": len(profiles), "bindings": len(bindings), "causalSourceEligible": sum(row["causalSourceEligible"] is True for row in profiles), "activeSimulationFeeds": sum(row["executionMode"] == "ACTIVE_SIMULATION" for row in profiles), "exactVersionOnly": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-repository", action="store_true", required=True)
    parser.parse_args()
    print(json.dumps(validate_repository(), indent=2))
