"""Non-production cross-level exposure contract and fail-closed validator."""

from __future__ import annotations

from typing import Any

LEVELS = {
    "PERSON", "DYAD", "EGO_NETWORK", "GROUP", "ORGANIZATION", "INSTITUTION",
    "COMMUNITY", "POPULATION", "NETWORK", "JURISDICTION", "MARKET", "STATE_SYSTEM",
}
ROUTES = {
    "MEMBERSHIP", "ELIGIBILITY", "ASSIGNMENT", "IMPLEMENTATION", "ENFORCEMENT",
    "CONTACT", "INFORMATION_EXPOSURE", "RESOURCE_ACCESS", "SERVICE_DELIVERY",
    "SOCIAL_INTERACTION", "NETWORK_POSITION", "AMBIENT_CONTEXT", "OBSERVATION",
    "MONITORING", "SANCTION_EXPOSURE", "INCENTIVE_EXPOSURE",
}
STATES = {
    "CROSS_LEVEL_READY", "SAME_LEVEL_NOT_APPLICABLE", "BLOCKED_NO_MAPPING",
    "BLOCKED_INCOMPLETE_MAPPING", "BLOCKED_NO_IMPLEMENTATION_ROUTE",
    "BLOCKED_NO_EXPOSURE_ROUTE", "BLOCKED_LEVEL_MISMATCH", "BLOCKED_TEMPORAL_MISMATCH",
    "BLOCKED_PERCEPTION_ROUTE_REQUIRED", "BLOCKED_NETWORK_STATE_DEPENDENCY", "RESEARCH_NEEDED",
}
FORBIDDEN_MAPPING_FIELDS = {
    "polarity", "edgeWeight", "activationValue", "fcmNodeState", "propagationValue",
    "lifecycleStatus", "activationStatus", "causalEffect", "effectMagnitude",
}
FORBIDDEN_VERSION_SELECTORS = {"LATEST", "DEFAULT", "FIRST", "MOST_RECENT", "AUTO_SELECT", "BEST_MATCH"}


class ContractError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def exact_version(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and value.upper() not in FORBIDDEN_VERSION_SELECTORS


def validate_mapping(mapping: dict[str, Any], relationship: dict[str, Any]) -> bool:
    required = {
        "schemaVersion", "mappingId", "mappingVersion", "relationshipId", "sourceEntityId",
        "sourceLevel", "targetEntityId", "targetLevel", "routeType", "exposureDefinition",
        "exposureUnit", "temporalOrder", "evidenceReferences", "scopeLimitations",
        "causalEvidence", "executionAuthority", "provenance", "prototypeStatus",
    }
    require(required <= set(mapping), f"Incomplete mapping fields: {sorted(required - set(mapping))}")
    require(not (FORBIDDEN_MAPPING_FIELDS & set(mapping)), "Mapping cannot become a causal or lifecycle object")
    require(mapping["schemaVersion"] == "0.1.0-PROTOTYPE", "Prototype schema version required")
    require(mapping["prototypeStatus"] == "NON_PRODUCTION_DECISION_TEST", "Production mapping is not authorized")
    require(exact_version(mapping["mappingVersion"]), "Exact mapping version required; no implicit resolution")
    require(mapping["sourceLevel"] in LEVELS and mapping["targetLevel"] in LEVELS, "Unknown level")
    require(mapping["sourceLevel"] != mapping["targetLevel"], "Same-level claims do not require a cross-level mapping")
    require(mapping["routeType"] in ROUTES, "Unknown exposure route")
    require(mapping["relationshipId"] == relationship["id"], "Relationship mismatch")
    require(mapping["sourceEntityId"] == relationship["subjectEntityId"], "Source entity mismatch")
    require(mapping["targetEntityId"] == relationship["objectEntityId"], "Target entity mismatch")
    require(mapping["causalEvidence"] is False, "Mapping existence cannot count as causal evidence")
    require(mapping["executionAuthority"] is False, "Mapping cannot confer execution authority")
    require(bool(mapping["exposureDefinition"].strip()), "Actual exposure must be defined")
    require(mapping["temporalOrder"] == ["SOURCE_STATE", "IMPLEMENTATION_OR_TRANSMISSION", "ACTUAL_EXPOSURE", "PERSON_OR_LOWER_LEVEL_RESPONSE"], "Required temporal stages must be explicit and ordered")
    if mapping.get("perceptionRequired"):
        require(bool(mapping.get("perceptionEntityId")), "Perception-mediated route requires an exact perception entity")
    if mapping["routeType"] == "NETWORK_POSITION":
        require(mapping.get("networkStateDependency") is True, "Network-position route must disclose Network State dependency")
    for field in ("intermediateEntityIds", "happeningTypeIds", "contextRequirements", "evidenceReferences", "scopeLimitations"):
        if field in mapping:
            require(isinstance(mapping[field], list), f"{field} must be a list")
    return True


def assess_eligibility(mapping: dict[str, Any] | None, relationship: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    source_level, target_level = context.get("sourceLevel"), context.get("targetLevel")
    if source_level and source_level == target_level:
        return result("SAME_LEVEL_NOT_APPLICABLE", "The claim is same-level under the tested declarations")
    if mapping is None:
        return result("BLOCKED_NO_MAPPING", "Cross-level claim has no exact mapping")
    try:
        validate_mapping(mapping, relationship)
    except ContractError as error:
        return result("BLOCKED_INCOMPLETE_MAPPING", str(error))
    if source_level != mapping["sourceLevel"] or target_level != mapping["targetLevel"]:
        return result("BLOCKED_LEVEL_MISMATCH", "Claim units do not match the mapping")
    if mapping.get("networkStateDependency") and not context.get("networkStateReference"):
        return result("BLOCKED_NETWORK_STATE_DEPENDENCY", "Exact Network State reference is required")
    if context.get("coverage") == "PARTIAL" and not context.get("coveredTargetSetReference"):
        return result("BLOCKED_INCOMPLETE_MAPPING", "Partial coverage requires an exact included target set or governed selection rule")
    if mapping.get("implementationRequired") and context.get("implementation") != "SATISFIED":
        return result("BLOCKED_NO_IMPLEMENTATION_ROUTE", "Policy/source existence does not establish implementation")
    if mapping.get("actualExposureRequired", True) and context.get("actualExposure") != "SATISFIED":
        return result("BLOCKED_NO_EXPOSURE_ROUTE", "Membership, eligibility or coverage does not establish actual exposure")
    if mapping.get("perceptionRequired") and context.get("perceivedExposure") != "SATISFIED":
        return result("BLOCKED_PERCEPTION_ROUTE_REQUIRED", "The stated mechanism requires perceived exposure")
    order = context.get("observedTemporalOrder", [])
    required_order = mapping["temporalOrder"]
    if order != required_order:
        return result("BLOCKED_TEMPORAL_MISMATCH", "Source, implementation/exposure and response are not temporally aligned")
    if context.get("scientificIdentification") != "ADEQUATE_FOR_TESTED_PROPOSITION":
        return result("RESEARCH_NEEDED", "Mapping completeness does not substitute for causal identification")
    return result("CROSS_LEVEL_READY", "Architecture contract complete; scientific governance and execution remain separate")


def result(state: str, reason: str) -> dict[str, Any]:
    require(state in STATES, "Unknown eligibility state")
    return {
        "state": state,
        "reason": reason,
        "scientificGovernanceConferred": False,
        "executionAuthorized": False,
        "lifecycleChanged": False,
        "causalEvidenceCreated": False,
    }
