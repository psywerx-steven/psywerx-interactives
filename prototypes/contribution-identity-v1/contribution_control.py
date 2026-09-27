"""Non-production WP-PSG-004 contribution identity prototype.

This module reconciles representations for test-only consumers.  It never
authorizes causality, activation, weights, polarity, or lifecycle changes.
"""
from __future__ import annotations

import hashlib
import json


class ValidationError(ValueError):
    pass


ROLES = {
    "PRIMARY_CAUSAL_CONTRIBUTION", "ALTERNATE_CAUSAL_REPRESENTATION",
    "MECHANISTIC_INTERMEDIATE", "CONSTITUENT_CAUSAL_ROUTE",
    "AGGREGATE_CAUSAL_ROUTE", "DERIVATION_ONLY", "STATE_RECALCULATION_ONLY",
    "EXPOSURE_ROUTING_ONLY", "EVIDENCE_ONLY", "CONTEXT_ONLY",
    "NONCAUSAL_REPRESENTATION",
}
POLICIES = {
    "COUNT_ONCE", "MUTUALLY_EXCLUSIVE_REPRESENTATIONS",
    "RECALCULATION_ONLY_NO_CAUSAL_SUM", "DERIVATION_ONLY_NO_PROPAGATION",
    "ALTERNATE_REPRESENTATION_SELECT_ONE", "INDEPENDENT_CONTRIBUTION",
    "BLOCKED_PENDING_CAUSAL_INDEPENDENCE", "BLOCKED_PENDING_IDENTITY_REVIEW",
}
STATUSES = {
    "NOT_APPLICABLE_NONCAUSAL", "SAME_CONTRIBUTION_CONFIRMED",
    "DISTINCT_CONTRIBUTIONS_CONFIRMED", "POTENTIAL_OVERLAP",
    "CONSTITUENT_OVERLAP", "DERIVATIONAL_OVERLAP",
    "STATE_RECALCULATION_ONLY", "INDEPENDENCE_NOT_ESTABLISHED",
    "BLOCKED_PENDING_GOVERNANCE",
}
CLASSES = {
    "RELATIONSHIP", "EFFECT_ASSERTION", "RDS_ROUTE", "RDS_PROFILE",
    "SCENARIO_STATE_DELTA", "DERIVATION", "CROSS_LEVEL_MAPPING",
    "EVIDENCE_ASSESSMENT", "INTERACTION_EFFECT", "SYNTHETIC_CAUSAL_ROUTE",
}
RESULTS = {
    "ALLOW_ALL_INDEPENDENT", "SELECT_ONE_REPRESENTATION",
    "NO_CAUSAL_SUM_DERIVATION_ONLY", "BLOCK_PENDING_IDENTITY",
    "BLOCK_PENDING_INDEPENDENCE",
}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValidationError(message)


def validate_member(member):
    required = {"recordClass", "recordId", "recordVersion", "recordHash", "memberRole", "representationRelationship", "identityAlignmentKey"}
    require(required <= member.keys(), "Contribution member is incomplete")
    require(member["recordClass"] in CLASSES, "Unsupported representation class")
    require(member["memberRole"] in ROLES, "Unsupported contribution role")
    require(member["recordVersion"] not in {"LATEST", "DEFAULT", "FIRST", "ACTIVE", "AUTO_SELECT", None}, "Exact member version required")
    require(isinstance(member["recordHash"], str) and len(member["recordHash"]) == 64, "Exact member hash required")


def validate_group(group):
    required = {
        "schemaVersion", "groupId", "groupVersion", "scientificContributionDefinition",
        "scope", "memberRepresentations", "consumerPolicy", "countingPolicy",
        "propagationPolicy", "derivationPolicy", "causalIndependenceStatus",
        "evidenceOverlapStatus", "constituentOverlapStatus", "provenance",
        "governance", "causalAuthority", "hasWeight", "hasPolarity",
        "hasActivation", "hasScientificLifecycle",
    }
    require(required <= group.keys(), "Contribution group is incomplete")
    require(group["groupVersion"] not in {"LATEST", "DEFAULT", "FIRST", "ACTIVE", "AUTO_SELECT", None}, "Exact group version required")
    require(group["countingPolicy"] in POLICIES, "Unsupported counting policy")
    require(group["causalIndependenceStatus"] in STATUSES, "Unsupported independence status")
    require(group["causalAuthority"] is False, "Contribution group cannot authorize causality")
    require(group["hasWeight"] is False and group["hasPolarity"] is False, "Contribution group cannot carry weight or polarity")
    require(group["hasActivation"] is False and group["hasScientificLifecycle"] is False, "Contribution group cannot carry activation or scientific lifecycle")
    require(len(group["memberRepresentations"]) >= 1, "Contribution group requires members")
    for member in group["memberRepresentations"]:
        validate_member(member)
    refs = [(m["recordClass"], m["recordId"], m["recordVersion"]) for m in group["memberRepresentations"]]
    require(len(refs) == len(set(refs)), "Duplicate exact member reference")
    if group["causalIndependenceStatus"] == "SAME_CONTRIBUTION_CONFIRMED":
        require(group["countingPolicy"] in {"COUNT_ONCE", "MUTUALLY_EXCLUSIVE_REPRESENTATIONS", "ALTERNATE_REPRESENTATION_SELECT_ONE"}, "Same contribution must count once")
        causal_members = [m for m in group["memberRepresentations"] if m["memberRole"] in {"PRIMARY_CAUSAL_CONTRIBUTION", "ALTERNATE_CAUSAL_REPRESENTATION"}]
        require(len({m["identityAlignmentKey"] for m in causal_members}) == 1, "Contradictory contribution identity dimensions")
    if group["causalIndependenceStatus"] in {"INDEPENDENCE_NOT_ESTABLISHED", "BLOCKED_PENDING_GOVERNANCE", "POTENTIAL_OVERLAP", "CONSTITUENT_OVERLAP"}:
        require(group["countingPolicy"] in {"BLOCKED_PENDING_CAUSAL_INDEPENDENCE", "BLOCKED_PENDING_IDENTITY_REVIEW"}, "Unresolved identity must fail closed")
    return True


def validate_registry(groups, exact_records):
    seen = set()
    for group in groups:
        validate_group(group)
        key = (group["groupId"], group["groupVersion"])
        require(key not in seen, "Duplicate immutable group version")
        seen.add(key)
        for member in group["memberRepresentations"]:
            record_key = (member["recordClass"], member["recordId"], member["recordVersion"])
            require(record_key in exact_records, "Contribution group references nonexistent record")
            require(exact_records[record_key] == member["recordHash"], "Contribution member version/hash mismatch")
    return True


def resolve_contribution_policy(groups, selected_representations=None):
    """Return a fail-closed policy result; never picks first/latest/best."""
    selected_representations = selected_representations or {}
    for group in groups:
        validate_group(group)
        status = group["causalIndependenceStatus"]
        policy = group["countingPolicy"]
        if policy in {"RECALCULATION_ONLY_NO_CAUSAL_SUM", "DERIVATION_ONLY_NO_PROPAGATION"}:
            return {"result": "NO_CAUSAL_SUM_DERIVATION_ONLY", "selected": [], "groupId": group["groupId"]}
        if status in {"INDEPENDENCE_NOT_ESTABLISHED", "BLOCKED_PENDING_GOVERNANCE", "POTENTIAL_OVERLAP", "CONSTITUENT_OVERLAP"}:
            return {"result": "BLOCK_PENDING_INDEPENDENCE", "selected": [], "groupId": group["groupId"]}
        if policy in {"COUNT_ONCE", "MUTUALLY_EXCLUSIVE_REPRESENTATIONS", "ALTERNATE_REPRESENTATION_SELECT_ONE"}:
            selected = selected_representations.get(group["groupId"])
            ids = {m["recordId"] for m in group["memberRepresentations"] if m["memberRole"] not in {"EVIDENCE_ONLY", "EXPOSURE_ROUTING_ONLY", "DERIVATION_ONLY", "STATE_RECALCULATION_ONLY"}}
            require(selected in ids, "Explicit governed representation selection required")
            return {"result": "SELECT_ONE_REPRESENTATION", "selected": [selected], "groupId": group["groupId"]}
    return {"result": "ALLOW_ALL_INDEPENDENT", "selected": [], "groupId": None}


def duplicate_safe_sum(contributions, groups, selections=None):
    selections = selections or {}
    by_id = {c["recordId"]: c for c in contributions}
    used = set()
    total = 0.0
    for group in groups:
        result = resolve_contribution_policy([group], selections)
        if result["result"] == "BLOCK_PENDING_INDEPENDENCE":
            raise ValidationError("Unresolved contribution independence")
        if result["result"] == "NO_CAUSAL_SUM_DERIVATION_ONLY":
            used.update(m["recordId"] for m in group["memberRepresentations"])
            continue
        if result["result"] == "SELECT_ONE_REPRESENTATION":
            identifier = result["selected"][0]
            require(identifier in by_id, "Selected representation is not supplied")
            total += by_id[identifier]["value"]
            used.update(m["recordId"] for m in group["memberRepresentations"])
    for contribution in contributions:
        if contribution["recordId"] not in used:
            total += contribution["value"]
    return total
