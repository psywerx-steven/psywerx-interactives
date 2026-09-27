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

IMPLICIT = {"LATEST", "DEFAULT", "FIRST", "ONLY", "MOST_RECENT", "ACTIVE", "BEST", "PREFERRED", "AUTO_SELECT"}


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


class ContributionRegistry:
    """Exact-version, immutable, in-memory prototype registry."""
    def __init__(self, groups=()):
        self._groups = {}
        for item in groups:
            self.add(item)

    def add(self, group):
        validate_group(group)
        key = (group["groupId"], group["groupVersion"])
        require(key not in self._groups, "Immutable group version already exists")
        self._groups[key] = json.loads(json.dumps(group))

    def get(self, group_id, group_version):
        require(group_version not in IMPLICIT and group_version is not None, "Exact group version required; implicit resolution forbidden")
        require((group_id, group_version) in self._groups, "Exact contribution group not found")
        return json.loads(json.dumps(self._groups[(group_id, group_version)]))

    def versions(self, group_id):
        return sorted(version for identifier, version in self._groups if identifier == group_id)


def resolution_fingerprint(receipt):
    identity = {key: value for key, value in receipt.items() if key != "deterministicFingerprint"}
    return digest(identity)


IDENTITY_DIMENSIONS = ("causalExposureOrChange", "targetChange", "causalContrast", "unitOfAnalysis", "timeScope", "pathwayScope", "intendedContribution", "underlyingRepresentedQuantity")


def same_identity_dimensions(left, right):
    """All governed dimensions must match; superficial metadata is ignored."""
    require(all(key in left and key in right for key in IDENTITY_DIMENSIONS), "Identity dimensions incomplete")
    return all(left[key] == right[key] for key in IDENTITY_DIMENSIONS)


def classify_group_change(before, after):
    if not same_identity_dimensions(before["identityDimensions"], after["identityDimensions"]):
        return "NEW_GROUP_IDENTITY_AND_SCIENTIFIC_READJUDICATION"
    if before["memberRepresentations"] != after["memberRepresentations"]:
        return "NEW_IMMUTABLE_GROUP_VERSION"
    return "NO_SEMANTIC_CHANGE"


def validate_native_controls(group, native_records):
    for member in group["memberRepresentations"]:
        native = native_records.get((member["recordClass"], member["recordId"]))
        require(native is not None, "Native record unavailable")
        require(str(native["revision"]) == str(member["recordRevision"]), "Native revision mismatch")
        require(native["recordHash"] == member["recordHash"], "Native record hash mismatch")
        if member["recordClass"] == "EFFECT_ASSERTION":
            require(native["nativeContributionId"] == member["nativeContributionId"] == group["groupId"], "EA native/external contribution identity mismatch")
    return True


def resolve_contribution_set(candidate_records, explicit_selection, contribution_groups, context=None):
    """Resolve candidate representations without granting causal authority.

    Candidate records must carry exact class/id/version/hash and a synthetic test
    value only when a numeric rehearsal is requested.
    """
    context = context or {}
    require(isinstance(explicit_selection, dict), "Explicit selection map required")
    exact = {(r["recordClass"], r["recordId"], r["recordVersion"]): r for r in candidate_records}
    require(len(exact) == len(candidate_records), "Duplicate candidate representation")
    for record in candidate_records:
        require(record["recordVersion"] not in IMPLICIT, "Exact candidate version required")
        require(isinstance(record["recordHash"], str) and len(record["recordHash"]) == 64, "Exact candidate hash required")
    membership = {}
    for group in contribution_groups:
        validate_group(group)
        for member in group["memberRepresentations"]:
            key = (member["recordClass"], member["recordId"], member["recordVersion"])
            if key in exact:
                require(exact[key]["recordHash"] == member["recordHash"], "Candidate/member hash mismatch")
                membership.setdefault(key, []).append(group)
    for key, groups in membership.items():
        mutually_exclusive = {(g["groupId"], g["groupVersion"], g["scientificContributionDefinition"]) for g in groups if g["countingPolicy"] in {"COUNT_ONCE", "MUTUALLY_EXCLUSIVE_REPRESENTATIONS"}}
        require(len(mutually_exclusive) <= 1, "Record belongs to contradictory contribution groups")

    included, excluded, blocked = [], [], []
    seen = set()
    outcomes = []
    for group in contribution_groups:
        members = [m for m in group["memberRepresentations"] if (m["recordClass"], m["recordId"], m["recordVersion"]) in exact]
        if not members:
            continue
        seen.update((m["recordClass"], m["recordId"], m["recordVersion"]) for m in members)
        policy = group["countingPolicy"]
        if policy in {"RECALCULATION_ONLY_NO_CAUSAL_SUM", "DERIVATION_ONLY_NO_PROPAGATION"}:
            excluded.extend(m["recordId"] for m in members)
            outcomes.append("DERIVATION_ONLY_NO_CAUSAL_SUM")
            continue
        if policy in {"BLOCKED_PENDING_CAUSAL_INDEPENDENCE", "BLOCKED_PENDING_IDENTITY_REVIEW"}:
            blocked.extend(m["recordId"] for m in members)
            outcomes.append("BLOCK_PENDING_CAUSAL_INDEPENDENCE" if policy.endswith("CAUSAL_INDEPENDENCE") else "BLOCK_PENDING_IDENTITY")
            continue
        if policy in {"COUNT_ONCE", "MUTUALLY_EXCLUSIVE_REPRESENTATIONS", "ALTERNATE_REPRESENTATION_SELECT_ONE"} and len(members) > 1:
            selected = explicit_selection.get(group["groupId"])
            require(selected is not None, "SELECT_ONE_REQUIRED")
            require(not isinstance(selected, list), "Exactly one representation must be selected")
            allowed = {m["recordId"] for m in members}
            require(selected in allowed, "Explicit selection is not an exact group member")
            included.append(selected)
            excluded.extend(sorted(allowed - {selected}))
            outcomes.append("COUNT_ONCE")
        else:
            included.extend(m["recordId"] for m in members if m["memberRole"] not in {"DERIVATION_ONLY", "STATE_RECALCULATION_ONLY", "EXPOSURE_ROUTING_ONLY", "EVIDENCE_ONLY", "CONTEXT_ONLY", "NONCAUSAL_REPRESENTATION"})
            excluded.extend(m["recordId"] for m in members if m["memberRole"] in {"DERIVATION_ONLY", "STATE_RECALCULATION_ONLY", "EXPOSURE_ROUTING_ONLY", "EVIDENCE_ONLY", "CONTEXT_ONLY", "NONCAUSAL_REPRESENTATION"})
            outcomes.append("ALLOW_ALL_INDEPENDENT" if included else "NO_CAUSAL_CONTRIBUTION")
    for key, record in exact.items():
        if key not in seen:
            included.append(record["recordId"])
    outcome = "BLOCK_PENDING_CAUSAL_INDEPENDENCE" if blocked else ("COUNT_ONCE" if "COUNT_ONCE" in outcomes else ("DERIVATION_ONLY_NO_CAUSAL_SUM" if outcomes and all(x in {"DERIVATION_ONLY_NO_CAUSAL_SUM", "NO_CAUSAL_CONTRIBUTION"} for x in outcomes) else "ALLOW_ALL_INDEPENDENT"))
    receipt = {
        "candidateRecords": sorted([{k: r[k] for k in ("recordClass", "recordId", "recordVersion", "recordHash")} for r in candidate_records], key=lambda x: (x["recordClass"], x["recordId"])),
        "groupRefs": sorted([{"groupId": g["groupId"], "groupVersion": g["groupVersion"], "countingPolicy": g["countingPolicy"], "propagationPolicy": g["propagationPolicy"], "independenceStatus": g["causalIndependenceStatus"]} for g in contribution_groups], key=lambda x: (x["groupId"], x["groupVersion"])),
        "explicitSelection": dict(sorted(explicit_selection.items())), "includedRepresentations": sorted(set(included)),
        "excludedRepresentations": sorted(set(excluded)), "blockedRepresentations": sorted(set(blocked)),
        "resolutionOutcome": outcome, "contextHash": digest(context),
        "causalAuthorityGranted": False, "activationAuthorityGranted": False, "graphAuthorityGranted": False,
    }
    receipt["deterministicFingerprint"] = resolution_fingerprint(receipt)
    return receipt
