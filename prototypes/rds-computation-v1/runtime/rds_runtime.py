"""Isolated WP-PSG-001 RDS computation-profile reference runtime.

This module is intentionally outside production runtime paths. It implements the
governed B+C contract for tests and migration rehearsal only.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Iterable


PROFILE_TYPES = {"DERIVATION_PROFILE", "MEASUREMENT_PROFILE", "ESTIMATION_PROFILE"}
INPUT_ROLES = {
    "CONSTITUENT", "MEASUREMENT_INPUT", "PARAMETER", "NORMALIZER",
    "BOUNDARY_INPUT", "REFERENCE_VALUE", "EXTERNAL_CONTEXT", "DATA_SOURCE",
}
FORBIDDEN_SELECTORS = {"LATEST", "DEFAULT", "FIRST", "MOST_RECENT", "ACTIVE_PROFILE", "AUTO_SELECT", "BEST_MATCH"}
EXECUTION_STATES = {
    "EXECUTABLE",
    "NON_EXECUTABLE_NO_PROFILE",
    "NON_EXECUTABLE_NO_ELIGIBLE_PROFILE",
    "NON_EXECUTABLE_INCOMPLETE_BINDING",
    "NON_EXECUTABLE_VERSION_MISMATCH",
    "NON_EXECUTABLE_DEFINITION_MISMATCH",
    "NON_EXECUTABLE_INPUT_MISMATCH",
    "NON_EXECUTABLE_PROFILE_TYPE_UNSUPPORTED",
    "NON_EXECUTABLE_BLOCKED_BY_SCIENCE",
    "NON_EXECUTABLE_BLOCKED_BY_ONTOLOGY",
}


class ContractError(ValueError):
    """Raised when a prototype contract is violated."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def _exact_version(value: Any, label: str) -> None:
    _require(isinstance(value, str) and bool(value.strip()), f"{label} must be an exact non-empty string")
    _require(value.upper() not in FORBIDDEN_SELECTORS, f"{label} cannot use implicit selector {value}")


def validate_computation_profile(profile: dict[str, Any]) -> None:
    required = [
        "schemaVersion", "profileId", "profileVersion", "rdsId",
        "rdsDefinitionVersion", "rdsDefinitionHash", "profileType",
        "scientificPurpose", "inputContract", "outputScale",
        "outputInterpretation", "derivationEntailed", "causalSemantics",
        "governance",
    ]
    for key in required:
        _require(key in profile, f"profile missing {key}")
    _exact_version(profile["profileVersion"], "profileVersion")
    _exact_version(profile["rdsDefinitionVersion"], "rdsDefinitionVersion")
    _require(profile["profileType"] in PROFILE_TYPES, "unsupported profileType")
    _require(profile["governance"].get("status") == "PROTOTYPE_ONLY", "prototype governance status required")
    _require(profile.get("causalSourceEligible") is False, "causalSourceEligible must default false")
    _require(profile.get("causalSourceGate") == "WP-PSG-005_REQUIRED", "WP-PSG-005 causal firewall required")
    roles = {row.get("role") for row in profile["inputContract"]}
    _require(roles <= INPUT_ROLES, "unknown input role")

    kind = profile["profileType"]
    if kind == "DERIVATION_PROFILE":
        _require(profile["derivationEntailed"] is True, "derivation profile must be entailed")
        _require(bool(profile.get("calculationReference")), "derivation profile needs calculationReference")
        _require(not profile.get("measurementProcedure") and not profile.get("estimationProcedure"), "derivation profile cannot carry measurement/estimation procedure")
    elif kind == "MEASUREMENT_PROFILE":
        _require(profile["derivationEntailed"] is False, "measurement output is not ontology-entailed")
        _require(bool(profile.get("measurementProcedure")), "measurement profile needs measurementProcedure")
        _require(not profile.get("calculationReference") and not profile.get("estimationProcedure"), "measurement type contradiction")
    else:
        _require(profile["derivationEntailed"] is False, "estimated output is not ontology-entailed")
        procedure = profile.get("estimationProcedure") or {}
        _require(bool(procedure.get("modelSemantics")), "estimation profile needs modelSemantics")
        _require(bool(procedure.get("diagnosticExpectations")), "estimation profile needs diagnostic expectations")
        _require(not profile.get("calculationReference") and not profile.get("measurementProcedure"), "estimation type contradiction")


def validate_application_binding(binding: dict[str, Any]) -> None:
    required = [
        "schemaVersion", "bindingId", "bindingVersion", "rdsId",
        "rdsDefinitionVersion", "rdsDefinitionHash", "profileId",
        "profileVersion", "unitOfAnalysis", "contextParameters", "governance",
    ]
    for key in required:
        _require(key in binding, f"binding missing {key}")
    _exact_version(binding["bindingVersion"], "bindingVersion")
    _exact_version(binding["profileVersion"], "profileVersion")
    _require(binding["governance"].get("status") == "PROTOTYPE_ONLY", "prototype binding status required")
    _require("calculationReference" not in binding and "measurementProcedure" not in binding and "estimationProcedure" not in binding, "binding cannot redefine method")


def validate_profile_binding_compatibility(profile: dict[str, Any], binding: dict[str, Any]) -> None:
    validate_computation_profile(profile)
    validate_application_binding(binding)
    for key in ("rdsId", "rdsDefinitionVersion", "rdsDefinitionHash", "profileId", "profileVersion"):
        _require(binding[key] == profile[key], f"binding/profile {key} mismatch")
    expected_unit = profile.get("unitOfAnalysis")
    _require(not expected_unit or binding["unitOfAnalysis"] == expected_unit, "incompatible unit of analysis")
    for requirement in profile.get("requiredContext", []):
        _require(binding.get(requirement) not in (None, "", [], {}), f"binding missing required context {requirement}")
    metric = profile.get("metricVariant")
    if metric:
        _require(binding.get("contextParameters", {}).get("metricVariant") == metric, "wrong metric variant")
    normalization = profile.get("normalization")
    if normalization:
        _require(binding.get("contextParameters", {}).get("normalization") == normalization, "unknown normalization")
    if profile["profileType"] == "MEASUREMENT_PROFILE":
        instrument = profile["measurementProcedure"].get("instrumentId")
        _require(not instrument or binding.get("measurementInstrument") == instrument, "incompatible measurement instrument")


def validate_registry_immutability(records: Iterable[dict[str, Any]]) -> None:
    seen: dict[tuple[str, str], str] = {}
    for record in records:
        if "bindingId" in record:
            identity = (record["bindingId"], record["bindingVersion"])
        else:
            identity = (record["profileId"], record["profileVersion"])
        value = digest(record)
        _require(identity not in seen or seen[identity] == value, f"immutable identity collision: {identity}")
        seen[identity] = value


def classify_profile_change(existing: dict[str, Any], proposed: dict[str, Any]) -> str:
    identity_fields = {
        "profileType", "inputContract", "constituentMapping", "aggregationFunction",
        "calculationReference", "measurementProcedure", "estimationProcedure",
        "metricVariant", "normalization", "missingnessPolicy", "unitOfAnalysis",
        "outputScale", "outputInterpretation",
    }
    if any(existing.get(k) != proposed.get(k) for k in identity_fields):
        return "NEW_PROFILE_IDENTITY"
    if any(existing.get(k) != proposed.get(k) for k in ("displayName", "scopeLimitations")):
        return "METADATA_ONLY"
    return "NEW_OR_REVISED_BINDING"


def resolve_execution_eligibility(
    request: dict[str, Any], profiles: list[dict[str, Any]], bindings: list[dict[str, Any]],
    current_definition_hash: str,
) -> dict[str, Any]:
    for key in ("rdsId", "profileId", "profileVersion", "bindingId", "bindingVersion"):
        if key not in request:
            return {"state": "NON_EXECUTABLE_INCOMPLETE_BINDING", "reason": f"missing exact {key}"}
        try:
            _exact_version(request[key], key)
        except ContractError as error:
            return {"state": "NON_EXECUTABLE_VERSION_MISMATCH", "reason": str(error)}

    candidates = [p for p in profiles if p["rdsId"] == request["rdsId"]]
    if not candidates:
        return {"state": "NON_EXECUTABLE_NO_PROFILE", "reason": "construct has zero profiles"}
    eligible = [p for p in candidates if p["governance"].get("executionEligibleInPrototype") is True]
    if not eligible:
        return {"state": "NON_EXECUTABLE_NO_ELIGIBLE_PROFILE", "reason": "no eligible prototype profile"}
    profile = next((p for p in eligible if p["profileId"] == request["profileId"] and p["profileVersion"] == request["profileVersion"]), None)
    if profile is None:
        return {"state": "NON_EXECUTABLE_VERSION_MISMATCH", "reason": "exact profile/version absent"}
    binding = next((b for b in bindings if b["bindingId"] == request["bindingId"] and b["bindingVersion"] == request["bindingVersion"]), None)
    if binding is None:
        return {"state": "NON_EXECUTABLE_INCOMPLETE_BINDING", "reason": "exact binding/version absent"}
    if profile["rdsDefinitionHash"] != current_definition_hash or binding["rdsDefinitionHash"] != current_definition_hash:
        return {"state": "NON_EXECUTABLE_DEFINITION_MISMATCH", "reason": "RDS semantic definition hash changed"}
    try:
        validate_profile_binding_compatibility(profile, binding)
    except ContractError as error:
        return {"state": "NON_EXECUTABLE_INCOMPLETE_BINDING", "reason": str(error)}
    supplied = request.get("inputs", {})
    for spec in profile["inputContract"]:
        if spec.get("required", True) and spec["inputId"] not in supplied:
            return {"state": "NON_EXECUTABLE_INPUT_MISMATCH", "reason": f"missing input {spec['inputId']}"}
        if spec["inputId"] in supplied and spec.get("definitionHash"):
            if supplied[spec["inputId"]].get("definitionHash") != spec["definitionHash"]:
                return {"state": "NON_EXECUTABLE_INPUT_MISMATCH", "reason": f"stale input definition hash for {spec['inputId']}"}
    return {"state": "EXECUTABLE", "profile": profile, "binding": binding}


def validate_causal_firewall(profile: dict[str, Any], causal_source_requested: bool) -> None:
    if causal_source_requested:
        _require(profile.get("causalSourceEligible") is True and profile.get("causalSourceAuthorizationId"), "causal-source use requires separate WP-PSG-005 authorization")


def execution_fingerprint(request: dict[str, Any], profile: dict[str, Any], binding: dict[str, Any]) -> str:
    identity = {
        "rdsId": request["rdsId"],
        "definitionHash": profile["rdsDefinitionHash"],
        "profileId": profile["profileId"], "profileVersion": profile["profileVersion"],
        "bindingId": binding["bindingId"], "bindingVersion": binding["bindingVersion"],
        "inputHashes": {key: value.get("valueHash") for key, value in sorted(request.get("inputs", {}).items())},
        "parameterHash": digest(request.get("parameters", {})),
    }
    return digest(identity)


def execute_reference(request: dict[str, Any], profiles: list[dict[str, Any]], bindings: list[dict[str, Any]], current_definition_hash: str) -> dict[str, Any]:
    eligibility = resolve_execution_eligibility(request, profiles, bindings, current_definition_hash)
    _require(eligibility["state"] == "EXECUTABLE", eligibility["reason"] if "reason" in eligibility else eligibility["state"])
    profile, binding = eligibility["profile"], eligibility["binding"]
    validate_causal_firewall(profile, request.get("causalSourceRequested", False))
    _require(profile["profileType"] == "DERIVATION_PROFILE", "reference executor only executes deterministic derivation profiles")
    _require(profile["calculationReference"] == "SUM_MAX_DEGREE_MINUS_DEGREES_DIVIDED_BY_N_MINUS_1_TIMES_N_MINUS_2", "unsupported calculation")
    degrees = request["inputs"]["SOC-049"]["value"]
    n = len(degrees)
    _require(n >= 3, "minimum three nodes")
    numerator = sum(max(degrees) - value for value in degrees)
    output = numerator / ((n - 1) * (n - 2))
    fingerprint = execution_fingerprint(request, profile, binding)
    return {
        "schemaVersion": "1.0.0-PROTOTYPE", "executionState": "EXECUTABLE",
        "rdsId": request["rdsId"], "rdsDefinitionHash": current_definition_hash,
        "profileId": profile["profileId"], "profileVersion": profile["profileVersion"],
        "bindingId": binding["bindingId"], "bindingVersion": binding["bindingVersion"],
        "inputHashes": {k: v["valueHash"] for k, v in sorted(request["inputs"].items())},
        "calculationReference": profile["calculationReference"], "output": output,
        "executionFingerprint": fingerprint, "deterministicRunMarker": fingerprint[:16],
        "causalSourceAuthorized": False, "causalSourceGate": "WP-PSG-005_REQUIRED",
        "governance": {"status": "PROTOTYPE_ONLY", "productionOutput": False},
    }
