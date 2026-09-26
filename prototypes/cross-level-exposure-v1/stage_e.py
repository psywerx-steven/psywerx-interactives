"""Non-production WP-PSG-002 Stage E reference implementation."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any

SCHEMA_VERSION = "0.2.0-PROTOTYPE"
OBJECT_KIND = "SCIENTIFIC_ROUTING_ELIGIBILITY_CONTRACT"
PROTOTYPE_STATUS = "PROTOTYPE_ONLY_NON_PRODUCTION"

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
    "CROSS_LEVEL_READY_FOR_REVIEW", "SAME_LEVEL_NOT_APPLICABLE", "NONCAUSAL_NOT_APPLICABLE",
    "BLOCKED_NO_MAPPING", "BLOCKED_MAPPING_VERSION_MISMATCH", "BLOCKED_INCOMPLETE_MAPPING",
    "BLOCKED_LEVEL_UNDECLARED", "BLOCKED_LEVEL_MISMATCH", "BLOCKED_NO_IMPLEMENTATION_ROUTE",
    "BLOCKED_NO_EXPOSURE_ROUTE", "BLOCKED_PARTIAL_COVERAGE_UNBOUND",
    "BLOCKED_PERCEPTION_ROUTE_REQUIRED", "BLOCKED_TEMPORAL_MISMATCH",
    "BLOCKED_NETWORK_STATE_DEPENDENCY", "BLOCKED_ONTOLOGY_DEPENDENCY",
    "RESEARCH_NEEDED_BEFORE_MAPPING",
}
IMPLICIT_SELECTORS = {"LATEST", "DEFAULT", "FIRST", "AUTO_SELECT", "BEST_MATCH", "ONLY_MAPPING", "ACTIVE"}
FORBIDDEN_MAPPING_FIELDS = {
    "polarity", "weight", "edgeWeight", "fcmState", "fcmNodeState", "activationValue",
    "lifecycleStatus", "propagationValue", "causalAuthority", "effectMagnitude",
}


class PrototypeValidationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PrototypeValidationError(message)


def exact_version(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and value.upper() not in IMPLICIT_SELECTORS


def canonical_fingerprint(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate_mapping(mapping: dict[str, Any]) -> bool:
    required = {
        "schemaVersion", "mappingId", "mappingVersion", "objectKind", "sourceLevel", "targetLevel",
        "routeType", "routeStages", "exposureDefinition", "exposureUnit", "temporalOrder",
        "membershipSemantics", "eligibilitySemantics", "implementationSemantics", "assignmentSemantics",
        "actualExposureSemantics", "perceivedExposureSemantics", "coverageSemantics",
        "partialCoverageAllowed", "ambientContextAllowed", "networkStateRequirements",
        "intermediateReferenceRules", "evidenceBindingRules", "scopeLimitations", "causalEvidence",
        "executionAuthority", "hasWeight", "hasLifecycle", "hasPropagationState", "provenance",
        "prototypeStatus",
    }
    require(required <= set(mapping), f"Incomplete mapping: {sorted(required - set(mapping))}")
    require(not (FORBIDDEN_MAPPING_FIELDS & set(mapping)), "Mapping cannot contain causal, lifecycle, or propagation fields")
    require(mapping["schemaVersion"] == SCHEMA_VERSION, "Wrong prototype schema version")
    require(mapping["objectKind"] == OBJECT_KIND, "Wrong object kind")
    require(mapping["prototypeStatus"] == PROTOTYPE_STATUS, "Production materialization is not authorized")
    require(exact_version(mapping["mappingVersion"]), "Exact mapping version required")
    require(mapping["sourceLevel"] in LEVELS and mapping["targetLevel"] in LEVELS, "Exact reviewed levels required")
    require(mapping["sourceLevel"] != mapping["targetLevel"], "Same-level route does not use a cross-level mapping")
    require(mapping["routeType"] in ROUTES, "Unknown route type")
    require(mapping["causalEvidence"] is False and mapping["executionAuthority"] is False, "Mapping cannot confer evidence or execution")
    require(mapping["hasWeight"] is False and mapping["hasLifecycle"] is False and mapping["hasPropagationState"] is False, "Mapping cannot become a causal graph object")
    require(bool(mapping["exposureDefinition"]), "Exposure semantics must be explicit")
    require(mapping["routeStages"][0] == "SOURCE_STATE" and mapping["routeStages"][-1] == "TARGET_RESPONSE", "Route stages must preserve source-to-response order")
    require(mapping["temporalOrder"] == mapping["routeStages"], "Temporal order must match route stages")
    if mapping["routeType"] == "NETWORK_POSITION":
        require(mapping["networkStateRequirements"]["required"] is True, "Network position requires exact Network State semantics")
    return True


def validate_mapping_identity(existing: dict[str, Any], candidate: dict[str, Any]) -> str:
    """Classify a candidate difference without mutating immutable versions."""
    validate_mapping(existing)
    validate_mapping(candidate)
    identity_fields = {
        "sourceLevel", "targetLevel", "routeType", "routeStages", "exposureDefinition",
        "perceivedExposureSemantics", "implementationSemantics", "coverageSemantics",
        "partialCoverageAllowed", "ambientContextAllowed",
    }
    if existing["mappingId"] == candidate["mappingId"] and existing["mappingVersion"] == candidate["mappingVersion"]:
        require(canonical_fingerprint(existing) == canonical_fingerprint(candidate), "Immutable mapping version changed")
        return "IDENTICAL_IMMUTABLE_VERSION"
    if any(existing.get(field) != candidate.get(field) for field in identity_fields):
        return "NEW_MAPPING_IDENTITY_REQUIRED"
    return "NEW_MAPPING_VERSION_OR_BINDING_REVIEW"


def validate_relationship_attachment(binding: dict[str, Any], mapping: dict[str, Any], relationship: dict[str, Any]) -> bool:
    required = {
        "schemaVersion", "bindingId", "bindingVersion", "relationshipId", "relationshipHash",
        "sourceEntityId", "sourceLevel", "targetEntityId", "targetLevel", "mappingId", "mappingVersion",
        "claimSpecificQualifiers", "intermediateEntityIds", "happeningTypeIds", "networkStateReferences",
        "implementationRequirement", "membershipRule", "eligibilityRule", "assignmentRule",
        "actualExposureRule", "perceptionRequired", "perceptionEntityId", "exposureWindow",
        "coverageRule", "temporalAlignment", "evidenceReferences", "scope", "provenance",
        "prototypeStatus",
    }
    require(required <= set(binding), f"Incomplete binding: {sorted(required - set(binding))}")
    require(binding["schemaVersion"] == SCHEMA_VERSION and binding["prototypeStatus"] == PROTOTYPE_STATUS, "Prototype-only binding required")
    require(exact_version(binding["bindingVersion"]) and exact_version(binding["mappingVersion"]), "Exact binding and mapping versions required")
    require(binding["mappingId"] == mapping["mappingId"] and binding["mappingVersion"] == mapping["mappingVersion"], "Mapping reference mismatch")
    require(binding["relationshipId"] == relationship["id"], "Relationship mismatch")
    require(binding["relationshipHash"] == canonical_fingerprint(relationship), "Relationship hash mismatch")
    require(binding["sourceEntityId"] == relationship["subjectEntityId"], "Source entity mismatch")
    require(binding["targetEntityId"] == relationship["objectEntityId"], "Target entity mismatch")
    require(binding["sourceLevel"] == mapping["sourceLevel"] and binding["targetLevel"] == mapping["targetLevel"], "Level mismatch")
    require(binding["sourceLevel"] in LEVELS and binding["targetLevel"] in LEVELS, "Reviewed levels required")
    require(binding.get("artificialPlumbingEntityRequired") is not True, "Architecture plumbing entities are prohibited")
    return True


def resolve_cross_level_eligibility(mapping: dict[str, Any] | None, binding: dict[str, Any] | None,
                                     relationship: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    if context.get("noncausal"):
        return receipt("NONCAUSAL_NOT_APPLICABLE", relationship, mapping, binding, "Noncausal semantic/derivational record")
    if context.get("sourceLevel") == context.get("targetLevel") and context.get("sourceLevel"):
        return receipt("SAME_LEVEL_NOT_APPLICABLE", relationship, mapping, binding, "Same-level record")
    if not context.get("sourceLevel") or not context.get("targetLevel"):
        return receipt("BLOCKED_LEVEL_UNDECLARED", relationship, mapping, binding, "Exact reviewed levels are unavailable")
    if mapping is None or binding is None:
        return receipt("BLOCKED_NO_MAPPING", relationship, mapping, binding, "Exact mapping and binding are required")
    try:
        validate_mapping(mapping)
        validate_relationship_attachment(binding, mapping, relationship)
    except PrototypeValidationError as error:
        state = "BLOCKED_MAPPING_VERSION_MISMATCH" if "version" in str(error).lower() or "reference mismatch" in str(error).lower() else "BLOCKED_INCOMPLETE_MAPPING"
        return receipt(state, relationship, mapping, binding, str(error))
    if context["sourceLevel"] != binding["sourceLevel"] or context["targetLevel"] != binding["targetLevel"]:
        return receipt("BLOCKED_LEVEL_MISMATCH", relationship, mapping, binding, "Context levels do not match reviewed binding levels")
    if mapping["networkStateRequirements"]["required"] and not context.get("networkStateSatisfied"):
        return receipt("BLOCKED_NETWORK_STATE_DEPENDENCY", relationship, mapping, binding, "Exact Network State identity and boundary are unavailable")
    if context.get("ontologyDependency"):
        return receipt("BLOCKED_ONTOLOGY_DEPENDENCY", relationship, mapping, binding, "A genuine construct is missing; WP-PSG-007 required")
    if binding["implementationRequirement"]["required"] and not context.get("implementationSatisfied"):
        return receipt("BLOCKED_NO_IMPLEMENTATION_ROUTE", relationship, mapping, binding, "Source state or policy was not implemented for the target")
    if context.get("coverage") == "PARTIAL" and not context.get("coverageRuleSatisfied"):
        return receipt("BLOCKED_PARTIAL_COVERAGE_UNBOUND", relationship, mapping, binding, "Partial coverage lacks an exact set or rule")
    if binding["actualExposureRule"]["required"] and not context.get("actualExposureSatisfied"):
        return receipt("BLOCKED_NO_EXPOSURE_ROUTE", relationship, mapping, binding, "Membership, eligibility, assignment, or availability did not establish exposure")
    if binding["perceptionRequired"] and not context.get("perceptionSatisfied"):
        return receipt("BLOCKED_PERCEPTION_ROUTE_REQUIRED", relationship, mapping, binding, "Perception is required but not established")
    if context.get("observedTemporalOrder") != binding["temporalAlignment"]:
        return receipt("BLOCKED_TEMPORAL_MISMATCH", relationship, mapping, binding, "Observed order does not match the bounded route")
    if not context.get("mappingEvidenceSufficient"):
        return receipt("RESEARCH_NEEDED_BEFORE_MAPPING", relationship, mapping, binding, "Routing evidence is insufficient; no generic mapping substituted")
    return receipt("CROSS_LEVEL_READY_FOR_REVIEW", relationship, mapping, binding, "Routing semantics are representable; science, execution, and lifecycle remain separate")


def receipt(state: str, relationship: dict[str, Any], mapping: dict[str, Any] | None,
            binding: dict[str, Any] | None, reason: str) -> dict[str, Any]:
    require(state in STATES, "Unknown eligibility state")
    identity = {
        "relationshipId": relationship["id"],
        "relationshipHash": canonical_fingerprint(relationship),
        "mappingId": mapping.get("mappingId") if mapping else None,
        "mappingVersion": mapping.get("mappingVersion") if mapping else None,
        "bindingId": binding.get("bindingId") if binding else None,
        "bindingVersion": binding.get("bindingVersion") if binding else None,
        "sourceEntityId": relationship["subjectEntityId"],
        "targetEntityId": relationship["objectEntityId"],
        "routeType": mapping.get("routeType") if mapping else None,
        "evaluationResult": state,
    }
    return {
        **identity, "reason": reason, "fingerprint": canonical_fingerprint(identity),
        "mappingCausalEvidence": False, "mappingExecutionAuthority": False,
        "relationshipDispositionChanged": False, "graphInclusionChanged": False,
        "simulationBehaviorChanged": False, "lifecycleChanged": False,
    }


class PrototypeRegistry:
    def __init__(self) -> None:
        self._mappings: dict[tuple[str, str], dict[str, Any]] = {}
        self._bindings: dict[tuple[str, str], dict[str, Any]] = {}

    def add_mapping(self, mapping: dict[str, Any]) -> None:
        validate_mapping(mapping)
        key = (mapping["mappingId"], mapping["mappingVersion"])
        require(key not in self._mappings, "Immutable mapping version already exists")
        self._mappings[key] = deepcopy(mapping)

    def add_binding(self, binding: dict[str, Any], relationship: dict[str, Any]) -> None:
        key = (binding["mappingId"], binding["mappingVersion"])
        require(key in self._mappings, "Exact mapping version not found")
        validate_relationship_attachment(binding, self._mappings[key], relationship)
        binding_key = (binding["bindingId"], binding["bindingVersion"])
        require(binding_key not in self._bindings, "Immutable binding version already exists")
        self._bindings[binding_key] = deepcopy(binding)

    def mapping(self, mapping_id: str, mapping_version: str) -> dict[str, Any]:
        require(exact_version(mapping_version), "Implicit mapping selection prohibited")
        require((mapping_id, mapping_version) in self._mappings, "Exact mapping version not found")
        return deepcopy(self._mappings[(mapping_id, mapping_version)])

    def binding(self, binding_id: str, binding_version: str) -> dict[str, Any]:
        require(exact_version(binding_version), "Implicit binding selection prohibited")
        require((binding_id, binding_version) in self._bindings, "Exact binding version not found")
        return deepcopy(self._bindings[(binding_id, binding_version)])
