"""Governed cross-level exposure architecture with shadow-only eligibility.

This subsystem does not alter Relationships, graph construction, simulation, or
lifecycle. A mapping describes routing semantics; a binding anchors those
semantics to an exact Relationship. Neither object supplies causal evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, RefResolver

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"
DATA_DIR = ROOT / "data/cross-level-exposure-v1"

LEVELS = {"PERSON", "DYAD", "EGO_NETWORK", "GROUP", "ORGANIZATION", "INSTITUTION", "COMMUNITY", "POPULATION", "NETWORK", "JURISDICTION", "MARKET", "STATE_SYSTEM"}
ROUTES = {"MEMBERSHIP", "ELIGIBILITY", "ASSIGNMENT", "IMPLEMENTATION", "ENFORCEMENT", "CONTACT", "INFORMATION_EXPOSURE", "RESOURCE_ACCESS", "SERVICE_DELIVERY", "SOCIAL_INTERACTION", "NETWORK_POSITION", "AMBIENT_CONTEXT", "OBSERVATION", "MONITORING", "SANCTION_EXPOSURE", "INCENTIVE_EXPOSURE"}
IMPLICIT_SELECTORS = {"LATEST", "DEFAULT", "FIRST", "ONLY", "MOST_RECENT", "ACTIVE", "BEST_MATCH", "AUTO_SELECT"}
FORBIDDEN_MAPPING_FIELDS = {"polarity", "weight", "edgeWeight", "fcmState", "fcmNodeState", "activationValue", "lifecycleStatus", "propagationValue", "causalAuthority", "scientificApproval", "relationshipApproval"}


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


def exact_version(value: Any, label: str) -> None:
    require(isinstance(value, str) and bool(value.strip()), f"{label} requires exact version")
    require(value.upper() not in IMPLICIT_SELECTORS, f"{label} prohibits implicit selector {value}")


@lru_cache(maxsize=1)
def validators() -> dict[str, Draft202012Validator]:
    names = {
        "mapping": "cross-level-exposure-mapping.schema.json",
        "binding": "cross-level-exposure-binding.schema.json",
        "eligibility": "cross-level-exposure-eligibility.schema.json",
        "provenance": "cross-level-exposure-provenance.schema.json",
    }
    store = {}
    for name in names.values():
        schema = read(SCHEMA_DIR / name)
        Draft202012Validator.check_schema(schema)
        store[schema["$id"]] = schema
    return {key: Draft202012Validator(store[f"https://psywerx.org/schemas/{name}"], resolver=RefResolver.from_schema(store[f"https://psywerx.org/schemas/{name}"], store=store)) for key, name in names.items()}


def validate_schema(kind: str, record: dict[str, Any]) -> None:
    errors = sorted(validators()[kind].iter_errors(record), key=lambda e: str(list(e.path)))
    require(not errors, f"{kind}: {errors[0].message}" if errors else "")


def validate_mapping(mapping: dict[str, Any]) -> bool:
    validate_schema("mapping", mapping)
    exact_version(mapping["mappingVersion"], "mappingVersion")
    require(mapping["sourceLevel"] != mapping["targetLevel"], "Cross-level mapping requires distinct levels")
    require(mapping["routeType"] in ROUTES, "Unknown route")
    require(mapping["routeStages"][0] == "SOURCE_STATE" and mapping["routeStages"][-1] == "TARGET_RESPONSE", "Route must preserve source-to-response order")
    require(mapping["temporalOrder"] == mapping["routeStages"], "Temporal order must match route stages")
    require(not (FORBIDDEN_MAPPING_FIELDS & set(mapping)), "Mapping cannot carry causal, lifecycle, weight, polarity, or propagation authority")
    require(mapping["causalEvidence"] is False and mapping["executionAuthority"] is False, "Mapping is noncausal and nonexecuting")
    require(mapping["hasWeight"] is False and mapping["hasLifecycle"] is False and mapping["hasPropagationState"] is False, "Mapping cannot become a graph object")
    if mapping["routeType"] == "NETWORK_POSITION":
        require(mapping["networkStateRequirements"]["required"] is True, "Network-position routes require governed Network State semantics")
    return True


def validate_binding(binding: dict[str, Any]) -> bool:
    validate_schema("binding", binding)
    exact_version(binding["bindingVersion"], "bindingVersion")
    exact_version(binding["mappingVersion"], "mappingVersion")
    require(binding["shadowEligibilityOnly"] is True, "Binding must remain shadow-only")
    require(binding["feedsGraphConstruction"] is False and binding["feedsSimulation"] is False and binding["executionAuthorized"] is False, "Binding cannot change execution")
    return True


def _relationships() -> dict[str, dict[str, Any]]:
    return {row["id"]: row for row in read(ROOT / "data/relationships.json")["relationships"]}


def _entity_ids() -> set[str]:
    return {row["id"] for row in read(ROOT / "data/entities.json")}


def _happening_type_ids() -> set[str]:
    payload = read(ROOT / "data/actions-events-v1/catalog.json")
    return {row["id"] for row in payload.get("happeningTypes", [])}


def validate_attachment(mapping: dict[str, Any], binding: dict[str, Any], relationship: dict[str, Any]) -> bool:
    validate_mapping(mapping)
    validate_binding(binding)
    require(binding["mappingId"] == mapping["mappingId"] and binding["mappingVersion"] == mapping["mappingVersion"], "Exact mapping reference mismatch")
    require(binding["relationshipId"] == relationship["id"], "Relationship mismatch")
    require(binding["relationshipRevisionOrHash"] == digest(relationship), "Relationship hash mismatch")
    require(binding["sourceEntityId"] == relationship["subjectEntityId"], "Source mismatch")
    require(binding["targetEntityId"] == relationship["objectEntityId"], "Target mismatch")
    require(binding["sourceLevel"] == mapping["sourceLevel"] and binding["targetLevel"] == mapping["targetLevel"], "Level mismatch")
    require(set(binding["intermediateEntityIds"]) <= _entity_ids(), "Intermediate entity reference unresolved")
    require(set(binding["happeningTypeIds"]) <= _happening_type_ids(), "HappeningType reference unresolved")
    return True


def load_registries() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    mapping_payload = read(DATA_DIR / "mappings.json")
    binding_payload = read(DATA_DIR / "bindings.json")
    require(mapping_payload["schemaVersion"] == "1.0.0" and binding_payload["schemaVersion"] == "1.0.0", "Registry schema mismatch")
    mappings, bindings = mapping_payload["mappings"], binding_payload["bindings"]
    relationships = _relationships()
    mapping_index: dict[tuple[str, str], dict[str, Any]] = {}
    for mapping in mappings:
        validate_mapping(mapping)
        key = (mapping["mappingId"], mapping["mappingVersion"])
        require(key not in mapping_index, f"Immutable mapping collision {key}")
        mapping_index[key] = mapping
    seen_bindings = set()
    for binding in bindings:
        key = (binding["bindingId"], binding["bindingVersion"])
        require(key not in seen_bindings, f"Immutable binding collision {key}")
        seen_bindings.add(key)
        mapping_key = (binding["mappingId"], binding["mappingVersion"])
        require(mapping_key in mapping_index, "Exact mapping version absent")
        require(binding["relationshipId"] in relationships, "Bound Relationship absent")
        validate_attachment(mapping_index[mapping_key], binding, relationships[binding["relationshipId"]])
    return mappings, bindings


def _receipt(state: str, reason: str, relationship: dict[str, Any], mapping: dict[str, Any] | None, binding: dict[str, Any] | None, context: dict[str, Any]) -> dict[str, Any]:
    identity = {
        "relationshipId": relationship["id"],
        "relationshipRevisionOrHash": digest(relationship),
        "mappingId": mapping.get("mappingId") if mapping else None,
        "mappingVersion": mapping.get("mappingVersion") if mapping else None,
        "bindingId": binding.get("bindingId") if binding else None,
        "bindingVersion": binding.get("bindingVersion") if binding else None,
        "sourceEntityId": relationship["subjectEntityId"],
        "targetEntityId": relationship["objectEntityId"],
        "sourceLevel": binding.get("sourceLevel") if binding else context.get("sourceLevel"),
        "targetLevel": binding.get("targetLevel") if binding else context.get("targetLevel"),
        "routeType": mapping.get("routeType") if mapping else None,
        "routeStages": mapping.get("routeStages", []) if mapping else [],
        "intermediateEntityIds": binding.get("intermediateEntityIds", []) if binding else [],
        "happeningTypeIds": binding.get("happeningTypeIds", []) if binding else [],
        "implementationRequirement": binding.get("implementationRequirement") if binding else None,
        "actualExposureRequirement": binding.get("actualExposureRule") if binding else None,
        "perceptionRequired": binding.get("perceptionRequired") if binding else False,
        "coverageRule": binding.get("coverageRule") if binding else None,
        "temporalOrder": binding.get("temporalAlignment", []) if binding else [],
        "networkStateDependency": bool(mapping and mapping["networkStateRequirements"]["required"]),
        "eligibilityState": state,
        "reason": reason,
        "contextFingerprint": digest(context),
        "causalEvidence": False,
        "executionAuthority": False,
        "feedsGraphConstruction": False,
        "feedsSimulation": False,
        "activationAuthorized": False,
    }
    identity["deterministicFingerprint"] = digest(identity)
    validate_schema("eligibility", {
        "schemaVersion": "1.0.0", "eligibilityState": state, "reason": reason,
        "causalEvidence": False, "executionAuthority": False,
        "feedsGraphConstruction": False, "feedsSimulation": False,
        "activationAuthorized": False,
    })
    receipt = {"schemaVersion": "1.0.0", **identity}
    validate_schema("provenance", receipt)
    return receipt


def resolve_shadow_eligibility(relationship_id: str, mapping_id: str, mapping_version: str, binding_id: str, binding_version: str, context: dict[str, Any]) -> dict[str, Any]:
    for value, label in ((mapping_version, "mappingVersion"), (binding_version, "bindingVersion")):
        try:
            exact_version(value, label)
        except ValidationError as error:
            rel = _relationships().get(relationship_id) or {"id": relationship_id, "subjectEntityId": "UNKNOWN", "objectEntityId": "UNKNOWN"}
            return _receipt("BLOCKED_MAPPING_VERSION_MISMATCH", str(error), rel, None, None, context)
    relationships = _relationships()
    require(relationship_id in relationships, "Relationship absent")
    relationship = relationships[relationship_id]
    mappings, bindings = load_registries()
    mapping = next((row for row in mappings if row["mappingId"] == mapping_id and row["mappingVersion"] == mapping_version), None)
    binding = next((row for row in bindings if row["bindingId"] == binding_id and row["bindingVersion"] == binding_version), None)
    if mapping is None or binding is None:
        version_mismatch = (mapping is None and any(row["mappingId"] == mapping_id for row in mappings)) or (binding is None and any(row["bindingId"] == binding_id for row in bindings))
        state = "BLOCKED_MAPPING_VERSION_MISMATCH" if version_mismatch else "BLOCKED_NO_MAPPING"
        return _receipt(state, "Exact mapping and binding version are absent", relationship, mapping, binding, context)
    try:
        validate_attachment(mapping, binding, relationship)
    except ValidationError as error:
        state = "BLOCKED_MAPPING_VERSION_MISMATCH" if "version" in str(error).lower() else "BLOCKED_INCOMPLETE_MAPPING"
        return _receipt(state, str(error), relationship, mapping, binding, context)
    if context.get("sourceEntityId", binding["sourceEntityId"]) != binding["sourceEntityId"] or context.get("targetEntityId", binding["targetEntityId"]) != binding["targetEntityId"]:
        return _receipt("BLOCKED_INCOMPLETE_MAPPING", "Context source/target does not match binding", relationship, mapping, binding, context)
    if context.get("sourceLevel") != binding["sourceLevel"] or context.get("targetLevel") != binding["targetLevel"]:
        return _receipt("BLOCKED_LEVEL_MISMATCH", "Context levels do not match reviewed levels", relationship, mapping, binding, context)
    if mapping["networkStateRequirements"]["required"] and not context.get("networkStateSatisfied"):
        return _receipt("BLOCKED_NETWORK_STATE_DEPENDENCY", "Exact Network State semantics unresolved", relationship, mapping, binding, context)
    if context.get("ontologyDependency"):
        return _receipt("BLOCKED_ONTOLOGY_DEPENDENCY", "Ontology dependency unresolved", relationship, mapping, binding, context)
    if binding["implementationRequirement"]["required"] and not context.get("implementationSatisfied"):
        return _receipt("BLOCKED_NO_IMPLEMENTATION_ROUTE", "Implementation not established for target", relationship, mapping, binding, context)
    if context.get("coverage") == "PARTIAL" and not context.get("coverageRuleSatisfied"):
        return _receipt("BLOCKED_PARTIAL_COVERAGE_UNBOUND", "Partial coverage lacks exact target rule", relationship, mapping, binding, context)
    if binding["actualExposureRule"]["required"] and not context.get("actualExposureSatisfied"):
        return _receipt("BLOCKED_NO_EXPOSURE_ROUTE", "Membership, eligibility, assignment, or implementation alone is insufficient", relationship, mapping, binding, context)
    if binding["perceptionRequired"] and not context.get("perceptionSatisfied"):
        return _receipt("BLOCKED_PERCEPTION_ROUTE_REQUIRED", "Required perception route not established", relationship, mapping, binding, context)
    if context.get("observedTemporalOrder") != binding["temporalAlignment"]:
        return _receipt("BLOCKED_TEMPORAL_MISMATCH", "Observed order does not match binding", relationship, mapping, binding, context)
    if context.get("rdsSource") and not context.get("wpPsg005CausalSourceAuthorized", False):
        return _receipt("RESEARCH_NEEDED_BEFORE_MAPPING", "RDS causal source requires WP-PSG-005", relationship, mapping, binding, context)
    return _receipt("CROSS_LEVEL_READY_FOR_REVIEW", "Routing contract satisfied in shadow review only", relationship, mapping, binding, context)


def rel_ins_040_shadow_receipts() -> dict[str, Any]:
    """Return deterministic Phase 1 controls without feeding graph/simulation."""
    mapping_id = "XLEM-V1-INSTITUTION-IMPLEMENTATION-PERCEPTION-001"
    binding_id = "XLEB-V1-REL-INS-040-001"
    _, bindings = load_registries()
    require(len(bindings) == 1 and bindings[0]["relationshipId"] == "REL-INS-040", "Phase 1 is bounded to REL-INS-040")
    binding = bindings[0]
    base = {
        "sourceEntityId": "INS-051", "targetEntityId": "PSY-022",
        "sourceLevel": "INSTITUTION", "targetLevel": "PERSON",
        "implementationSatisfied": True, "actualExposureSatisfied": True,
        "perceptionSatisfied": True, "coverage": "COMPLETE",
        "coverageRuleSatisfied": True,
        "observedTemporalOrder": binding["temporalAlignment"],
    }
    cases = [
        ("COMPLETE_ROUTE", base, "1.0.0", "1.0.0"),
        ("MEMBERSHIP_ONLY", {**base, "actualExposureSatisfied": False, "membershipOnly": True}, "1.0.0", "1.0.0"),
        ("ELIGIBILITY_ONLY", {**base, "actualExposureSatisfied": False, "eligibilityOnly": True}, "1.0.0", "1.0.0"),
        ("IMPLEMENTED_NOT_EXPOSED", {**base, "actualExposureSatisfied": False}, "1.0.0", "1.0.0"),
        ("WRONG_TARGET_PERSON", {**base, "targetEntityId": "PSY-023"}, "1.0.0", "1.0.0"),
        ("PERCEPTION_REQUIREMENT_OMITTED", {**base, "perceptionSatisfied": False}, "1.0.0", "1.0.0"),
        ("TEMPORAL_REVERSAL", {**base, "observedTemporalOrder": list(reversed(binding["temporalAlignment"]))}, "1.0.0", "1.0.0"),
        ("WRONG_MAPPING_VERSION", base, "2.0.0", "1.0.0"),
    ]
    receipts = []
    for case_id, context, mapping_version, binding_version in cases:
        receipt = resolve_shadow_eligibility("REL-INS-040", mapping_id, mapping_version, binding_id, binding_version, context)
        receipts.append({"caseId": case_id, "context": context, "receipt": receipt})
    bad_binding = dict(binding)
    bad_binding["relationshipRevisionOrHash"] = "0" * 64
    relationship = _relationships()["REL-INS-040"]
    mapping = load_registries()[0][0]
    try:
        validate_attachment(mapping, bad_binding, relationship)
        hash_state, reason = "CROSS_LEVEL_READY_FOR_REVIEW", "unexpected"
    except ValidationError as error:
        hash_state, reason = "BLOCKED_INCOMPLETE_MAPPING", str(error)
    receipts.append({"caseId": "WRONG_RELATIONSHIP_HASH", "context": base, "receipt": _receipt(hash_state, reason, relationship, mapping, bad_binding, base)})
    return {
        "schemaVersion": "1.0.0", "relationshipId": "REL-INS-040",
        "mode": "SHADOW_VALIDATION_ONLY", "receipts": receipts,
        "feedsGraphConstruction": False, "feedsSimulation": False,
        "causalEvidence": False, "executionAuthority": False,
        "activationAuthorized": False,
    }


def validate_repository() -> dict[str, Any]:
    validators()
    mappings, bindings = load_registries()
    return {"mappings": len(mappings), "bindings": len(bindings), "relationshipMigrations": 0, "graphBehaviorChanges": 0, "simulationBehaviorChanges": 0, "causalAuthorizations": 0, "activations": 0}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-repository", action="store_true")
    parser.add_argument("--write-shadow-receipts", action="store_true")
    args = parser.parse_args()
    if args.validate_repository:
        print(json.dumps(validate_repository(), sort_keys=True))
    if args.write_shadow_receipts:
        output = DATA_DIR / "rel-ins-040-shadow-receipts.json"
        output.write_text(json.dumps(rel_ins_040_shadow_receipts(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        print(output.relative_to(ROOT))
