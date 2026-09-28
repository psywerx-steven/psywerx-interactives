"""Governed contribution identity control plane.

The service is additive and shadow-only.  It reconciles exact representations
without granting causal, graph, simulation, lifecycle, or activation authority.
"""
from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"
DATA_DIR = ROOT / "data/contribution-control-v1"
DECISION_ID = "GOV-CONTRIBUTION-IMPLEMENTATION-001-2026-09-27"
IMPLICIT_SELECTORS = {"LATEST", "DEFAULT", "FIRST", "ONLY", "ACTIVE", "BEST", "PREFERRED", "MOST_RECENT", "AUTO_SELECT"}
NONCAUSAL_ROLES = {"DERIVATION_ONLY", "STATE_RECALCULATION_ONLY", "EXPOSURE_ROUTING_ONLY", "EVIDENCE_ONLY", "CONTEXT_ONLY", "NONCAUSAL_REPRESENTATION"}
FORBIDDEN_FIELDS = {"weight", "edgeWeight", "magnitude", "polarity", "lifecycleStatus", "activationStatus", "propagationState", "fcmState"}


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
    require(isinstance(value, str) and bool(value.strip()), f"{label} requires an exact version")
    require(value.upper() not in IMPLICIT_SELECTORS, f"{label} prohibits implicit selector {value}")


@lru_cache(maxsize=1)
def validators() -> dict[str, Draft202012Validator]:
    files = {
        "group": "contribution-group.schema.json",
        "request": "contribution-resolution-request.schema.json",
        "receipt": "contribution-resolution-receipt.schema.json",
    }
    result = {}
    for kind, name in files.items():
        schema = read(SCHEMA_DIR / name)
        Draft202012Validator.check_schema(schema)
        result[kind] = Draft202012Validator(schema)
    return result


def validate_schema(kind: str, value: dict[str, Any]) -> None:
    errors = sorted(validators()[kind].iter_errors(value), key=lambda error: str(list(error.path)))
    require(not errors, f"{kind}: {errors[0].message}" if errors else "")


def validate_group(group: dict[str, Any]) -> bool:
    validate_schema("group", group)
    exact_version(group["groupVersion"], "groupVersion")
    require(not (FORBIDDEN_FIELDS & set(group)), "ContributionGroup cannot carry magnitude, polarity, lifecycle, activation, or propagation")
    for field in ("causalEvidence", "executionAuthority", "hasWeight", "hasPolarity", "hasLifecycle", "hasActivation", "hasPropagationState"):
        require(group[field] is False, f"{field} must remain false")
    require(group["shadowOnly"] is True, "Production groups are shadow-only in the authorized phase")
    member_keys = set()
    for member in group["memberRepresentations"]:
        exact_version(str(member["recordRevision"]), "member recordRevision")
        key = (member["recordClass"], member["recordId"], str(member["recordRevision"]))
        require(key not in member_keys, "Duplicate exact group member")
        member_keys.add(key)
    if group["causalIndependenceStatus"] == "SAME_CONTRIBUTION_CONFIRMED":
        require(group["countingPolicy"] in {"COUNT_ONCE", "MUTUALLY_EXCLUSIVE_REPRESENTATIONS"}, "Confirmed shared contribution must count once")
        require(group["selectionPolicy"] == "EXACT_EXPLICIT_REPRESENTATION_REQUIRED", "Mutually exclusive representations require exact selection")
    return True


def _find(rows: list[dict[str, Any]], identifier: str) -> dict[str, Any]:
    record = next((row for row in rows if row.get("id") == identifier), None)
    require(record is not None, f"Unknown production record {identifier}")
    return record


def native_record(record_class: str, record_id: str) -> dict[str, Any]:
    if record_class == "RELATIONSHIP":
        return _find(read(ROOT / "data/relationship-intervention-v1/relationships.json")["relationships"], record_id)
    if record_class == "EFFECT_ASSERTION":
        return _find(read(ROOT / "data/actions-events-v1/catalog.json")["effectAssertions"], record_id)
    if record_class == "DERIVATION":
        return _find(read(ROOT / "data/relational-state-v1/catalog.json")["bindings"], record_id)
    if record_class == "RDS_PROFILE":
        return next(row for row in read(ROOT / "data/rds-computation-v1/profiles.json")["profiles"] if row["profileId"] == record_id)
    if record_class == "CROSS_LEVEL_MAPPING":
        return next(row for row in read(ROOT / "data/cross-level-exposure-v1/mappings.json")["mappings"] if row["mappingId"] == record_id)
    raise ValidationError(f"No production native adapter for {record_class}")


def native_control(record_class: str, record_id: str) -> dict[str, Any]:
    record = native_record(record_class, record_id)
    base = {"recordClass": record_class, "recordId": record_id, "recordRevision": record.get("revision", record.get("profileVersion", record.get("mappingVersion"))), "recordHash": digest(record), "sourceRecordMutated": False}
    if record_class == "RELATIONSHIP":
        return {**base, "nativeContributionId": None, "nativeContributionPolicy": None, "causalContribution": bool(record.get("causalClaim"))}
    if record_class == "EFFECT_ASSERTION":
        contribution = record.get("contribution") or {}
        return {**base, "nativeContributionId": contribution.get("groupId"), "nativeContributionPolicy": contribution.get("reconciliation"), "nativeRole": contribution.get("role"), "relatedAssertionIds": contribution.get("relatedAssertionIds", []), "causalContribution": record.get("claimSemantics") == "CAUSAL"}
    if record_class == "DERIVATION":
        return {**base, "nativeContributionId": record.get("sharedContributionIdentity"), "nativeContributionPolicy": record.get("contributionPolicy"), "causalContribution": False}
    if record_class == "RDS_PROFILE":
        return {**base, "nativeContributionId": record.get("provenance", {}).get("legacyContributionIdentity"), "nativeContributionPolicy": record.get("provenance", {}).get("legacyContributionPolicy"), "causalContribution": bool(record.get("causalSourceEligible", False))}
    if record_class == "CROSS_LEVEL_MAPPING":
        return {**base, "nativeContributionId": None, "nativeContributionPolicy": "EXPOSURE_ROUTING_ONLY", "causalContribution": False}
    raise ValidationError(f"Unsupported native control {record_class}")


def network_state_control(record_id: str = "SCENARIO_STATE_DELTA") -> dict[str, Any]:
    return {"recordClass": "SCENARIO_STATE_DELTA", "recordId": record_id, "nativeContributionPolicy": "STATE_RECALCULATION_ONLY", "causalContribution": False, "empiricalEvidenceProduced": False, "ontologyRelationshipsEdited": 0}


def validate_group_members(group: dict[str, Any]) -> bool:
    validate_group(group)
    for member in group["memberRepresentations"]:
        native = native_control(member["recordClass"], member["recordId"])
        require(str(native["recordRevision"]) == str(member["recordRevision"]), "Native member revision mismatch")
        require(native["recordHash"] == member["recordHash"], "Native member hash mismatch")
        if member["recordClass"] == "EFFECT_ASSERTION":
            require(native["nativeContributionId"] == member["nativeContributionId"] == group["groupId"], "Native EA contribution identity mismatch")
            require(native["nativeContributionPolicy"] == member["nativeContributionPolicy"], "Native EA reconciliation mismatch")
    return True


class ContributionRegistry:
    def __init__(self, groups: list[dict[str, Any]]):
        self._groups: dict[tuple[str, str], dict[str, Any]] = {}
        member_memberships: dict[tuple[str, str, str], str] = {}
        for group in groups:
            validate_group_members(group)
            key = (group["groupId"], group["groupVersion"])
            require(key not in self._groups, "Immutable group version collision")
            for member in group["memberRepresentations"]:
                mkey = (member["recordClass"], member["recordId"], str(member["recordRevision"]))
                prior = member_memberships.get(mkey)
                require(prior is None or prior == group["groupId"], "Record belongs to contradictory ContributionGroups")
                member_memberships[mkey] = group["groupId"]
            self._groups[key] = json.loads(json.dumps(group))

    def get(self, group_id: str, group_version: str) -> dict[str, Any]:
        exact_version(group_version, "groupVersion")
        require((group_id, group_version) in self._groups, "Exact ContributionGroup version not found")
        return json.loads(json.dumps(self._groups[(group_id, group_version)]))

    def all(self) -> list[dict[str, Any]]:
        return [json.loads(json.dumps(self._groups[key])) for key in sorted(self._groups)]


def load_registry() -> ContributionRegistry:
    payload = read(DATA_DIR / "groups.json")
    require(payload["schemaVersion"] == "1.0.0" and payload["registryId"] == "CONTRIBUTION-GROUPS-V1", "Registry identity mismatch")
    return ContributionRegistry(payload["groups"])


def _receipt(request: dict[str, Any], groups: list[dict[str, Any]], included: list[str], excluded: list[str], blocked: list[str], outcome: str) -> dict[str, Any]:
    identity = {
        "schemaVersion": "1.0.0", "requestHash": digest(request),
        "candidateRepresentations": sorted(request["candidateRepresentations"], key=lambda row: (row["recordClass"], row["recordId"])),
        "groupReferences": sorted(request["groupReferences"], key=lambda row: (row["groupId"], row["groupVersion"])),
        "explicitSelections": dict(sorted(request["explicitSelections"].items())),
        "includedRepresentations": sorted(set(included)), "excludedRepresentations": sorted(set(excluded)), "blockedRepresentations": sorted(set(blocked)),
        "resolutionOutcome": outcome,
        "countingPolicies": sorted({g["countingPolicy"] for g in groups}), "propagationPolicies": sorted({g["propagationPolicy"] for g in groups}),
        "independenceStatuses": sorted({g["causalIndependenceStatus"] for g in groups}),
        "causalAuthorityGranted": False, "activationAuthorityGranted": False, "graphAuthorityGranted": False, "simulationAuthorityGranted": False,
    }
    identity["deterministicFingerprint"] = digest(identity)
    validate_schema("receipt", identity)
    return identity


def resolve_for_causal_consumption(request: dict[str, Any]) -> dict[str, Any]:
    validate_schema("request", request)
    candidates = request["candidateRepresentations"]
    exact = {(row["recordClass"], row["recordId"], str(row["recordRevision"])): row for row in candidates}
    require(len(exact) == len(candidates), "Duplicate candidate representation")
    registry = load_registry()
    groups = [registry.get(ref["groupId"], ref["groupVersion"]) for ref in request["groupReferences"]]
    included, excluded, blocked, covered = [], [], [], set()
    outcomes: list[str] = []
    for group in groups:
        members = [member for member in group["memberRepresentations"] if (member["recordClass"], member["recordId"], str(member["recordRevision"])) in exact]
        for member in members:
            candidate = exact[(member["recordClass"], member["recordId"], str(member["recordRevision"]))]
            require(candidate["recordHash"] == member["recordHash"], "Candidate/member hash mismatch")
            covered.add((member["recordClass"], member["recordId"], str(member["recordRevision"])))
        if group["countingPolicy"] in {"RECALCULATION_ONLY_NO_CAUSAL_SUM", "DERIVATION_ONLY_NO_PROPAGATION"}:
            excluded.extend(member["recordId"] for member in members); outcomes.append("DERIVATION_ONLY_NO_CAUSAL_SUM"); continue
        if group["countingPolicy"] in {"BLOCKED_PENDING_CAUSAL_INDEPENDENCE", "BLOCKED_PENDING_IDENTITY_REVIEW"}:
            blocked.extend(member["recordId"] for member in members); outcomes.append("BLOCK_PENDING_CAUSAL_INDEPENDENCE" if group["countingPolicy"].endswith("CAUSAL_INDEPENDENCE") else "BLOCK_PENDING_IDENTITY"); continue
        causal_members = [member for member in members if member["memberRole"] not in NONCAUSAL_ROLES]
        if group["countingPolicy"] in {"COUNT_ONCE", "MUTUALLY_EXCLUSIVE_REPRESENTATIONS"} and len(causal_members) > 1:
            selected = request["explicitSelections"].get(group["groupId"])
            if selected is None:
                return _receipt(request, groups, [], [], [member["recordId"] for member in causal_members], "SELECT_ONE_REQUIRED")
            require(isinstance(selected, str), "Exactly one representation must be selected")
            allowed = {member["recordId"] for member in causal_members}
            require(selected in allowed, "Explicit selection is not an exact group member")
            included.append(selected); excluded.extend(allowed - {selected}); outcomes.append("COUNT_ONCE")
        else:
            included.extend(member["recordId"] for member in causal_members); excluded.extend(member["recordId"] for member in members if member["memberRole"] in NONCAUSAL_ROLES)
    for key, candidate in exact.items():
        if key in covered:
            continue
        adapter = request["context"].get("nativeControls", {}).get(candidate["recordId"])
        if adapter and adapter.get("causalContribution") is False:
            excluded.append(candidate["recordId"])
        else:
            included.append(candidate["recordId"])
    if blocked:
        outcome = "BLOCK_PENDING_CAUSAL_INDEPENDENCE" if "BLOCK_PENDING_CAUSAL_INDEPENDENCE" in outcomes else "BLOCK_PENDING_IDENTITY"
    elif "COUNT_ONCE" in outcomes:
        outcome = "COUNT_ONCE"
    elif not included:
        outcome = "DERIVATION_ONLY_NO_CAUSAL_SUM" if "DERIVATION_ONLY_NO_CAUSAL_SUM" in outcomes else "NO_CAUSAL_CONTRIBUTION"
    else:
        outcome = "ALLOW_ALL_INDEPENDENT"
    return _receipt(request, groups, included, excluded, blocked, outcome)


def validate_repository() -> dict[str, int]:
    groups = load_registry().all()
    return {"groups": len(groups), "recordMigrations": 0, "relationshipChanges": 0, "effectAssertionChanges": 0, "graphBehaviorChanges": 0, "simulationBehaviorChanges": 0, "lifecycleChanges": 0, "activationChanges": 0, "rdsCausalSourceChanges": 0}
