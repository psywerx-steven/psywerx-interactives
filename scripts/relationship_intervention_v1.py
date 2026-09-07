"""Production validators and V3 compatibility adapter for PSYWERX V1.

This module contains infrastructure only. It does not generate, govern, or
activate scientific assertions. The canonical V3 corpus remains untouched.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from functools import lru_cache
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas" / "relationship-intervention" / "v1"
DATA = ROOT / "data"
CANDIDATE_WORKSPACE = DATA / "candidates" / "relationship-intervention-v1" / "workspace.json"
GOVERNED_V1_DIR = DATA / "relationship-intervention-v1"


@lru_cache(maxsize=1)
def source_verification_module():
    # Existing consumers load this module by absolute file path, without adding
    # scripts/ to sys.path. Resolve the additive sibling the same way.
    spec = importlib.util.spec_from_file_location("psywerx_source_verification_v1", ROOT / "scripts/source_verification_v1.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

SCHEMA_FILES = {
    "governance": "governance-v1.schema.json",
    "evidence": "evidence-assessment-v1.schema.json",
    "relationship": "relationship-v1.schema.json",
    "pathway": "causal-pathway-v1.schema.json",
    "intervention": "intervention-v1.schema.json",
    "intervention_effect": "intervention-effect-v1.schema.json",
    "candidate_workspace": "candidate-workspace-v1.schema.json",
    "source": "source-record-v1.schema.json",
}

CAUSAL_PREDICATES = {"CAUSES", "ENABLES", "CONSTRAINS"}
FAMILY_PREDICATES = {
    "CAUSAL": CAUSAL_PREDICATES,
    "EMPIRICAL_NONCAUSAL": {"ASSOCIATED_WITH", "PRECEDES", "TRANSITIONS_TO"},
    "MODERATION": {"MODERATES"},
    "DERIVATIONAL": {"DERIVED_FROM"},
    "COMPOSITIONAL": {"CONSTITUENT_OF", "MEMBER_OF"},
    "REALIZATION": {"REALIZES"},
    "SEMANTIC": {
        "NARROWER_THAN", "BROADER_THAN", "OVERLAPS_WITH",
        "EQUIVALENT_UNDER_CONDITIONS", "INVERSE_UNDER_ALIGNED_SCOPE",
        "RELATED_METRIC",
    },
}
SYMMETRIC_SEMANTIC_PREDICATES = {
    "OVERLAPS_WITH", "EQUIVALENT_UNDER_CONDITIONS",
    "INVERSE_UNDER_ALIGNED_SCOPE", "RELATED_METRIC",
}
NON_GOVERNED_LIFECYCLES = {"CANDIDATE", "RESEARCH_NEEDED", "REVIEW_READY"}
AUTOMATED_LIFECYCLE_TRANSITIONS = {
    (None, "CANDIDATE"),
    ("CANDIDATE", "RESEARCH_NEEDED"),
    ("RESEARCH_NEEDED", "CANDIDATE"),
    ("RESEARCH_NEEDED", "REVIEW_READY"),
    ("REVIEW_READY", "RESEARCH_NEEDED"),
}


class ArchitectureValidationError(ValueError):
    """Raised when a cross-record governed V1 rule is violated."""


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ArchitectureValidationError(message)


class SchemaSet:
    """Load and validate the modular production JSON Schemas."""

    def __init__(self, schema_dir: Path = SCHEMA_DIR) -> None:
        self.schemas = {
            name: _load_json(schema_dir / filename)
            for name, filename in SCHEMA_FILES.items()
        }
        registry = Registry().with_resources(
            (schema["$id"], Resource.from_contents(schema))
            for schema in self.schemas.values()
        )
        self.validators: dict[str, Draft202012Validator] = {}
        for name, schema in self.schemas.items():
            Draft202012Validator.check_schema(schema)
            self.validators[name] = Draft202012Validator(
                schema, registry=registry, format_checker=FormatChecker()
            )

    def validate(self, schema_name: str, record: Any) -> None:
        errors = sorted(
            self.validators[schema_name].iter_errors(record),
            key=lambda error: tuple(str(part) for part in error.absolute_path),
        )
        if errors:
            error = errors[0]
            location = ".".join(str(part) for part in error.absolute_path) or "$"
            raise ArchitectureValidationError(
                f"{schema_name} schema violation at {location}: {error.message}"
            )


@dataclass(frozen=True)
class Catalog:
    entities: Mapping[str, Mapping[str, Any]]
    legacy_relationships: Mapping[str, Mapping[str, Any]]
    source_ids: frozenset[str]

    @classmethod
    def from_repository(cls) -> "Catalog":
        entities = {row["id"]: row for row in _load_json(DATA / "entities.json")}
        envelope = _load_json(DATA / "relationships.json")
        active = {row["id"]: row for row in envelope["relationships"]}
        source_ids = {
            row["id"] for row in _load_json(DATA / "sources.json")["sources"]
        }
        native_sources = GOVERNED_V1_DIR / "source-register.json"
        if native_sources.exists():
            source_ids.update(
                row["id"] for row in _load_json(native_sources)["sources"]
            )
        return cls(
            entities=entities,
            legacy_relationships=active,
            source_ids=frozenset(source_ids),
        )

    @classmethod
    def synthetic(
        cls,
        entities: Iterable[Mapping[str, Any]],
        relationships: Iterable[Mapping[str, Any]] = (),
        source_ids: Iterable[str] = (),
    ) -> "Catalog":
        return cls(
            entities={row["id"]: row for row in entities},
            legacy_relationships={row["id"]: row for row in relationships},
            source_ids=frozenset(source_ids),
        )


def governed_active(record: Mapping[str, Any]) -> bool:
    governance = record.get("governance") or {}
    return (
        governance.get("lifecycleStatus") == "GOVERNED"
        and governance.get("activationStatus") == "ACTIVE"
    )


def expected_causal_review_gate(source_type: str, target_type: str) -> str:
    if source_type == "DRIVER" and target_type == "DRIVER":
        return "STANDARD_CAUSAL"
    if source_type == "RELATIONAL_DERIVED_STATE" and target_type == "RELATIONAL_DERIVED_STATE":
        return "EXCEPTIONAL_CAUSAL"
    return "HEIGHTENED_CAUSAL"


def _relationship_endpoints(record: Mapping[str, Any]) -> tuple[str | None, str | None]:
    if record.get("schemaVersion") == "3.0":
        return record.get("subjectEntityId"), record.get("objectEntityId")
    return record.get("sourceEntityId"), record.get("targetEntityId")


def _is_governed_causal(
    record: Mapping[str, Any], catalog: Catalog
) -> bool:
    identifier = record.get("id")
    if identifier in catalog.legacy_relationships:
        legacy = catalog.legacy_relationships[identifier]
        return (
            legacy.get("relationFamily") == "CAUSAL"
            and legacy.get("governanceStatus") == "ACTIVE"
        )
    compatibility = record.get("compatibility") or {}
    return (
        record.get("relationFamily") == "CAUSAL"
        and governed_active(record)
        and compatibility.get("v1Executability") == "EXECUTABLE"
    )


def canonicalize_association(record: Mapping[str, Any]) -> dict[str, Any]:
    """Return the single ID-ordered representation of a symmetric association."""
    result = copy.deepcopy(record)
    _require(
        result.get("relationFamily") == "EMPIRICAL_NONCAUSAL"
        and result.get("predicate") == "ASSOCIATED_WITH",
        "Only ASSOCIATED_WITH records can be canonicalized as associations",
    )
    source = result.get("sourceEntityId")
    target = result.get("targetEntityId")
    _require(bool(source and target), "Association endpoints are required")
    if source > target:
        result["sourceEntityId"], result["targetEntityId"] = target, source
        result["sourceEntityType"], result["targetEntityType"] = (
            result.get("targetEntityType"), result.get("sourceEntityType")
        )
    return result


def validate_governance_transition(transition: Mapping[str, Any]) -> None:
    """Enforce D12 across lifecycle and activation dimensions."""
    required = {
        "fromState", "toState", "actorClass", "rationale", "timestamp",
        "objectId", "revision", "provenance", "governanceDecisionRecord",
        "exactDecisionMaterialization",
    }
    _require(required <= transition.keys(), "Transition provenance is incomplete")
    before = transition["fromState"]
    after = transition["toState"]
    actor = transition["actorClass"]
    pair = (before.get("lifecycleStatus"), after.get("lifecycleStatus"))
    exact = transition["exactDecisionMaterialization"]
    decision = transition["governanceDecisionRecord"]
    human_lifecycle = AUTOMATED_LIFECYCLE_TRANSITIONS | {
        ("REVIEW_READY", "GOVERNED"),
        ("REVIEW_READY", "REJECTED"),
        ("GOVERNED", "DEPRECATED"),
    }
    activation_change = (
        pair == ("GOVERNED", "GOVERNED")
        and before.get("activationStatus") in {"ACTIVE", "INACTIVE"}
        and after.get("activationStatus") in {"ACTIVE", "INACTIVE"}
        and before.get("activationStatus") != after.get("activationStatus")
    )

    _require(before.get("lifecycleStatus") != "DEPRECATED", "Deprecated records cannot reactivate")
    if exact:
        _require(actor == "AUTOMATED_PROCESS_OR_AI", "Exact decision materialization is an automation action")
        _require(bool(decision), "Exact decision materialization requires a governance decision")
        _require(pair in human_lifecycle or activation_change, "Exact materialization transition is not governable")
        return

    if actor in {"AUTOMATED_PROCESS_OR_AI", "RESEARCHER_REVIEWER"}:
        _require(pair in AUTOMATED_LIFECYCLE_TRANSITIONS, "Non-governor transition is not authorized")
        _require(
            before.get("activationStatus") == "NOT_ELIGIBLE"
            and after.get("activationStatus") == "NOT_ELIGIBLE",
            "Non-governed workflow must remain NOT_ELIGIBLE",
        )
        return

    _require(actor == "AUTHORIZED_HUMAN_GOVERNOR", "Unknown transition actor class")
    _require(pair in human_lifecycle or activation_change, "Human transition is not valid")
    if pair in {("REVIEW_READY", "GOVERNED"), ("REVIEW_READY", "REJECTED"), ("GOVERNED", "DEPRECATED")} or activation_change:
        _require(bool(decision), "Governance transition requires a decision record")


def validate_governed_revision(
    previous: Mapping[str, Any], current: Mapping[str, Any], transition: Mapping[str, Any]
) -> None:
    _require(previous.get("id") == current.get("id"), "Revision cannot change object identity")
    _require(
        current.get("revision") == previous.get("revision", 0) + 1,
        "Governed revision must increment revision by one",
    )
    _require(governed_active(previous), "Substantive governed revision requires a governed source")
    actor = transition.get("actorClass")
    exact = transition.get("exactDecisionMaterialization")
    _require(
        actor == "AUTHORIZED_HUMAN_GOVERNOR" or exact is True,
        "Substantive governed revision requires human authorization",
    )
    _require(bool(transition.get("governanceDecisionRecord")), "Governed revision requires a decision record")


def validate_governance_record(record: Mapping[str, Any]) -> None:
    governance = record["governance"]
    transitions = governance["transitionProvenance"]
    if governance["authorityBasis"] == "PRESERVED_V3":
        _require(not transitions, "V3 preservation must not invent V1 transitions")
        return
    _require(bool(transitions), "Native V1 record requires transition provenance")
    for item in transitions:
        validate_governance_transition(item)
        _require(item["objectId"] == record["id"], "Transition object ID does not match record")
        _require(item["revision"] <= record["revision"], "Transition revision exceeds record revision")
    final_state = transitions[-1]["toState"]
    _require(final_state["lifecycleStatus"] == governance["lifecycleStatus"], "Final transition lifecycle does not match record")
    _require(final_state["activationStatus"] == governance["activationStatus"], "Final transition activation does not match record")


def _validate_entity_endpoint(
    identifier: str | None, declared_type: str | None, catalog: Catalog, label: str
) -> None:
    _require(bool(identifier), f"{label} entity ID is required")
    _require(identifier in catalog.entities, f"{label} entity does not resolve: {identifier}")
    actual = catalog.entities[identifier].get("entityType")
    _require(actual == declared_type, f"{label} entity type does not match catalog")


def _validate_rds_safeguards(safeguards: Mapping[str, Any] | None) -> None:
    _require(bool(safeguards), "Governed active RDS causal claim requires safeguards")
    assert safeguards is not None
    _require(bool(safeguards.get("derivationVersion")), "RDS derivationVersion is required")
    _require(bool(safeguards.get("calculationWindow")), "RDS calculationWindow is required")
    _require(safeguards.get("temporalIndependence") == "CONFIRMED", "RDS temporal independence is not confirmed")
    _require(safeguards.get("mechanisticIndependence") == "CONFIRMED", "RDS mechanistic independence is not confirmed")
    _require(safeguards.get("constituentOverlap") in {"NONE", "ASSESSED_AND_CONTROLLED"}, "RDS constituent overlap is unresolved")
    _require(safeguards.get("sharedDenominatorCheck") in {"NONE", "ASSESSED_AND_CONTROLLED"}, "RDS shared denominator is unresolved")
    _require(safeguards.get("definitionalEntailment") == "ABSENT", "Definitionally entailed claim cannot be causal")
    _require(bool(safeguards.get("duplicatePropagationControl")), "RDS duplicate propagation control is required")
    _require(safeguards.get("exogenousUse") != "UNRESOLVED", "RDS exogenous use is unresolved")


def validate_relationship(
    record: Mapping[str, Any], catalog: Catalog, schemas: SchemaSet,
    related_relationships: Mapping[str, Mapping[str, Any]] | None = None,
) -> None:
    schemas.validate("relationship", record)
    validate_governance_record(record)
    _require(set(record["sourceIds"]) <= catalog.source_ids, "Relationship source does not resolve")
    family = record["relationFamily"]
    _require(record["predicate"] in FAMILY_PREDICATES[family], "Predicate is incompatible with relation family")
    _require(record["causalClaim"] is (family == "CAUSAL"), "causalClaim flag is incompatible with relation family")
    if family != "CAUSAL":
        for field in (
            "causalClaimRole", "polarity", "causalReviewGate", "rdsSafeguards",
            "functionalForm", "exposurePattern", "causalLag", "persistence",
        ):
            _require(record[field] is None, f"Noncausal relationship cannot carry {field}")

    if record["predicate"] in SYMMETRIC_SEMANTIC_PREDICATES | {"ASSOCIATED_WITH"}:
        _require(record["symmetry"] == "SYMMETRIC", "Symmetric predicate must be stored symmetrically")
    else:
        _require(record["symmetry"] == "DIRECTED", "Directed predicate must be stored directionally")

    if family == "MODERATION":
        target_id = record["moderatedRelationshipId"]
        relationships = dict(catalog.legacy_relationships)
        relationships.update(related_relationships or {})
        _require(target_id in relationships, "Moderated relationship does not resolve")
        _require(_is_governed_causal(relationships[target_id], catalog), "Moderation must target one governed causal relationship")
        moderators = record["moderatorSpecifications"]
        for moderator in moderators:
            _validate_entity_endpoint(moderator["entityId"], moderator["entityType"], catalog, "Moderator")
        if record["combinationRule"] == "INDIVIDUAL":
            _require(len(moderators) == 1, "INDIVIDUAL moderation requires exactly one moderator")
        else:
            _require(len(moderators) >= 2, "JOINT moderation requires at least two moderators")
    else:
        _validate_entity_endpoint(record["sourceEntityId"], record["sourceEntityType"], catalog, "Source")
        _validate_entity_endpoint(record["targetEntityId"], record["targetEntityType"], catalog, "Target")

    if record["predicate"] == "ASSOCIATED_WITH":
        _require(record["sourceEntityId"] < record["targetEntityId"], "Association endpoints are not canonically ordered")
        _require(record["associationSpecification"] is not None, "Association specification is required")

    if record["predicate"] in {"PRECEDES", "TRANSITIONS_TO"}:
        _require(record["temporalSpecification"] is not None, "Temporal specification is required")
    if record["predicate"] == "TRANSITIONS_TO":
        temporal = record["temporalSpecification"]
        _require(bool(temporal["sourceStateDefinition"]), "Transition source state is required")
        _require(bool(temporal["targetStateDefinition"]), "Transition target state is required")
        if record["sourceEntityId"] == record["targetEntityId"]:
            _require(temporal["sourceStateDefinition"] != temporal["targetStateDefinition"], "Same-entity transition states must differ")

    if family == "CAUSAL":
        expected = expected_causal_review_gate(record["sourceEntityType"], record["targetEntityType"])
        _require(record["causalReviewGate"] == expected, f"Causal review gate must be {expected}")
        if governed_active(record):
            _require(record["causalClaimRole"] is not None, "Active causal claim requires causalClaimRole")
            _require(record["polarity"] is not None, "Active causal claim requires polarity")
            _require(bool(record["mechanism"]), "Active causal claim requires mechanism")
            _require(bool(record["boundaryConditions"]), "Active causal claim requires boundary conditions")
            _require(record["applicability"] is not None, "Active causal claim requires applicability")
            if "RELATIONAL_DERIVED_STATE" in {record["sourceEntityType"], record["targetEntityType"]}:
                _validate_rds_safeguards(record["rdsSafeguards"])

    if governed_active(record):
        compatibility = record["compatibility"]
        _require(compatibility["sourceSchema"] == "RELATIONSHIP_V1", "Preserved V3 record cannot silently become V1-active")
        _require(compatibility["migrationCompleteness"] == "COMPLETE", "Active V1 relationship must be complete")
        _require(compatibility["v1Executability"] == "EXECUTABLE", "Active V1 relationship must be executable")
        _require(bool(record["evidenceAssessmentIds"]), "Active relationship requires evidence assessment")
        _require(bool(record["sourceIds"]), "Active relationship requires sources")


def causal_traversal(records: Iterable[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    """Return only governed-active executable V1 causal edges."""
    return [
        record for record in records
        if record.get("relationFamily") == "CAUSAL"
        and governed_active(record)
        and (record.get("compatibility") or {}).get("v1Executability") == "EXECUTABLE"
    ]


def validate_pathway(
    pathway: Mapping[str, Any], catalog: Catalog, schemas: SchemaSet,
    relationships: Mapping[str, Mapping[str, Any]],
) -> None:
    schemas.validate("pathway", pathway)
    validate_governance_record(pathway)
    _require(set(pathway["sourceIds"]) <= catalog.source_ids, "CausalPathway source does not resolve")
    _require(pathway["startEntityId"] in catalog.entities, "Pathway start entity does not resolve")
    _require(pathway["endEntityId"] in catalog.entities, "Pathway end entity does not resolve")
    for intermediate in pathway["intermediateEntities"]:
        _require(intermediate["entityId"] in catalog.entities, "Pathway intermediate entity does not resolve")
    ordered = pathway["orderedRelationshipIds"]
    segments: list[Mapping[str, Any]] = []
    for identifier in ordered:
        _require(identifier in relationships, f"Pathway relationship does not resolve: {identifier}")
        segment = relationships[identifier]
        _require(_is_governed_causal(segment, catalog), "Pathway segments must be governed causal relationships")
        segments.append(segment)
    endpoints = [_relationship_endpoints(segment) for segment in segments]
    _require(endpoints[0][0] == pathway["startEntityId"], "Pathway start does not match first edge")
    _require(endpoints[-1][1] == pathway["endEntityId"], "Pathway end does not match final edge")
    for left, right in zip(endpoints, endpoints[1:]):
        _require(left[1] == right[0], "Pathway causal segments are not contiguous")
    expected_intermediates = [target for _, target in endpoints[:-1]]
    actual_intermediates = [row["entityId"] for row in pathway["intermediateEntities"]]
    _require(actual_intermediates == expected_intermediates, "Pathway intermediate roles do not match segment order")

    total_effects = [
        record for record in relationships.values()
        if record.get("causalClaimRole") == "TOTAL_EFFECT"
        and _relationship_endpoints(record) == (pathway["startEntityId"], pathway["endEntityId"])
        and _is_governed_causal(record, catalog)
    ]
    control = pathway["duplicateCountingControl"]
    if total_effects:
        _require(control["mode"] == "RECONCILED", "Total effect and pathway require explicit reconciliation")
        _require(control["totalEffectRelationshipId"] in {row["id"] for row in total_effects}, "Reconciliation does not name the matching total effect")
    if governed_active(pathway):
        _require(bool(pathway["evidenceAssessmentIds"]), "Active pathway requires pathway-specific evidence")
        _require(bool(pathway["sourceIds"]), "Active pathway requires sources")


def validate_intervention_catalog(
    interventions: Sequence[Mapping[str, Any]],
    effects: Sequence[Mapping[str, Any]],
    catalog: Catalog,
    schemas: SchemaSet,
    relationships: Mapping[str, Mapping[str, Any]],
) -> None:
    by_id: dict[str, Mapping[str, Any]] = {}
    for intervention in interventions:
        schemas.validate("intervention", intervention)
        validate_governance_record(intervention)
        _require(set(intervention["identitySourceIds"]) <= catalog.source_ids, "Intervention identity source does not resolve")
        _require(intervention["id"] not in by_id, "Duplicate Intervention ID")
        by_id[intervention["id"]] = intervention
    for intervention in interventions:
        for component in intervention["componentInterventionIds"]:
            _require(component in by_id, f"Package component does not resolve: {component}")
            _require(component != intervention["id"], "Package cannot contain itself")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(identifier: str) -> None:
        if identifier in visiting:
            raise ArchitectureValidationError("Intervention package composition cycle")
        if identifier in visited:
            return
        visiting.add(identifier)
        for component in by_id[identifier]["componentInterventionIds"]:
            visit(component)
        visiting.remove(identifier)
        visited.add(identifier)

    for identifier in by_id:
        visit(identifier)

    active_effect_interventions: set[str] = set()
    for effect in effects:
        validate_intervention_effect(effect, by_id, catalog, schemas, relationships)
        if governed_active(effect):
            active_effect_interventions.add(effect["interventionId"])
    for intervention in interventions:
        if governed_active(intervention):
            _require(bool(intervention["identitySourceIds"]), "Active Intervention requires an identity source")
            _require(intervention["id"] in active_effect_interventions, "Active Intervention requires its own active effect")


def validate_evidence_assessment(
    evidence: Mapping[str, Any], catalog: Catalog, schemas: SchemaSet
) -> None:
    schemas.validate("evidence", evidence)
    validate_governance_record(evidence)
    _require(set(evidence["sourceIds"]) <= catalog.source_ids, "Evidence source does not resolve")
    _require(
        set(evidence["conflictingEvidence"]["sourceIds"]) <= catalog.source_ids,
        "Conflicting/null evidence source does not resolve",
    )
    if governed_active(evidence):
        _require(bool(evidence["sourceIds"]), "Active EvidenceAssessment requires sources")
        _require(bool(evidence["evidenceRationale"]), "Active EvidenceAssessment requires rationale")
        _require(evidence["evidenceStrength"] != "NOT_ASSESSED", "Active evidence strength must be assessed")
        _require(evidence["confidence"] != "NOT_ASSESSED", "Active evidence confidence must be assessed")
        _require(evidence["evidenceDisposition"] != "NOT_ASSESSED", "Active evidence disposition must be assessed")


def recommendation_eligible_effects(
    interventions: Iterable[Mapping[str, Any]],
    effects: Iterable[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    """Return active effects whose reusable Intervention identity is also active."""
    active_intervention_ids = {
        record["id"] for record in interventions if governed_active(record)
    }
    return [
        effect for effect in effects
        if governed_active(effect) and effect.get("interventionId") in active_intervention_ids
    ]


def validate_intervention_effect(
    effect: Mapping[str, Any],
    interventions: Mapping[str, Mapping[str, Any]],
    catalog: Catalog,
    schemas: SchemaSet,
    relationships: Mapping[str, Mapping[str, Any]],
) -> None:
    schemas.validate("intervention_effect", effect)
    validate_governance_record(effect)
    _require(set(effect["sourceIds"]) <= catalog.source_ids, "InterventionEffect source does not resolve")
    _require(effect["interventionId"] in interventions, "InterventionEffect Intervention does not resolve")
    if governed_active(effect):
        _require(governed_active(interventions[effect["interventionId"]]), "Active InterventionEffect requires a governed-active Intervention")
    mechanistic = effect["mechanisticDriverIds"]
    for identifier in mechanistic:
        _require(identifier in catalog.entities, f"Mechanistic Driver does not resolve: {identifier}")
        _require(catalog.entities[identifier]["entityType"] == "DRIVER", "Mechanistic linkage must name a Driver")

    if effect["targetKind"] == "DRIVER":
        identifier = effect["targetDriverId"]
        _require(identifier in catalog.entities, "Driver target does not resolve")
        _require(catalog.entities[identifier]["entityType"] == "DRIVER", "RDS cannot be a direct InterventionEffect target")
    else:
        identifier = effect["targetRelationshipId"]
        _require(identifier in relationships, "Relationship target does not resolve")
        _require(_is_governed_causal(relationships[identifier], catalog), "InterventionEffect must target a governed causal Relationship")
        if governed_active(effect):
            _require(bool(mechanistic), "Active relationship-targeted effect requires a mechanistic Driver")

    for identifier in effect["moderatorEntityIds"] + effect["outcomeEntityIds"]:
        _require(identifier in catalog.entities, f"Effect entity reference does not resolve: {identifier}")
    if governed_active(effect):
        _require(bool(effect["evidenceAssessmentIds"]), "Active InterventionEffect requires evidence")
        _require(bool(effect["sourceIds"]), "Active InterventionEffect requires sources")


def validate_candidate_workspace(
    workspace: Mapping[str, Any], catalog: Catalog, schemas: SchemaSet
) -> None:
    schemas.validate("candidate_workspace", workspace)
    record_groups = (
        workspace["relationships"], workspace["evidenceAssessments"],
        workspace["causalPathways"], workspace["interventions"],
        workspace["interventionEffects"],
    )
    for group in record_groups:
        for record in group:
            governance = record["governance"]
            _require(governance["lifecycleStatus"] in NON_GOVERNED_LIFECYCLES, "Candidate workspace cannot contain governed/rejected/deprecated records")
            _require(governance["activationStatus"] == "NOT_ELIGIBLE", "Candidate workspace records must be NOT_ELIGIBLE")

    object_groups = {
        "RELATIONSHIP": workspace["relationships"],
        "CAUSAL_PATHWAY": workspace["causalPathways"],
        "INTERVENTION": workspace["interventions"],
        "INTERVENTION_EFFECT": workspace["interventionEffects"],
    }
    object_ids: dict[str, set[str]] = {
        kind: {record["id"] for record in records}
        for kind, records in object_groups.items()
    }
    for kind, records in object_groups.items():
        _require(len(object_ids[kind]) == len(records), f"Duplicate {kind} ID")
    evidence_by_id = {row["id"]: row for row in workspace["evidenceAssessments"]}
    _require(len(evidence_by_id) == len(workspace["evidenceAssessments"]), "Duplicate EvidenceAssessment ID")

    relationship_map = dict(catalog.legacy_relationships)
    relationship_map.update({row["id"]: row for row in workspace["relationships"]})
    for relationship in workspace["relationships"]:
        validate_relationship(relationship, catalog, schemas, relationship_map)
    for evidence in workspace["evidenceAssessments"]:
        validate_evidence_assessment(evidence, catalog, schemas)
        assertion = evidence["assertion"]
        assertion_type = assertion["objectType"]
        target_kind = "RELATIONSHIP" if assertion_type == "MODERATION" else assertion_type
        if target_kind == "INTERVENTION_IDENTITY":
            target_kind = "INTERVENTION"
        _require(
            assertion["objectId"] in object_ids.get(target_kind, set()),
            "Evidence assertion target does not resolve in candidate workspace",
        )
    for pathway in workspace["causalPathways"]:
        validate_pathway(pathway, catalog, schemas, relationship_map)
    validate_intervention_catalog(
        workspace["interventions"], workspace["interventionEffects"], catalog,
        schemas, relationship_map,
    )
    evidence_references = (
        list(workspace["relationships"])
        + list(workspace["causalPathways"])
        + list(workspace["interventionEffects"])
    )
    for record in evidence_references:
        for evidence_id in record["evidenceAssessmentIds"]:
            _require(evidence_id in evidence_by_id, f"EvidenceAssessment reference does not resolve for {record['id']}")
            assertion = evidence_by_id[evidence_id]["assertion"]
            expected_types = {"RELATIONSHIP"}
            if record.get("relationFamily") == "MODERATION":
                expected_types.add("MODERATION")
            elif "orderedRelationshipIds" in record:
                expected_types = {"CAUSAL_PATHWAY"}
            elif "interventionId" in record:
                expected_types = {"INTERVENTION_EFFECT"}
            _require(
                assertion["objectId"] == record["id"]
                and assertion["objectType"] in expected_types,
                f"EvidenceAssessment assertion does not match {record['id']}",
            )
    _require(not causal_traversal(workspace["relationships"]), "Candidate workspace entered causal traversal")


def project_v3_relationship(record: Mapping[str, Any]) -> dict[str, Any]:
    """Create a lossless, conservative V1 compatibility projection."""
    legacy = copy.deepcopy(record)
    family = "SEMANTIC" if record["relationFamily"] == "SEMANTIC_MAPPING" else record["relationFamily"]
    predicate = record["predicate"]
    symmetry = "SYMMETRIC" if predicate in SYMMETRIC_SEMANTIC_PREDICATES else "DIRECTED"
    blocked = {
        "normalizedEvidenceAssessment",
        "evidenceRationale",
        "governanceTransitionProvenance",
        "boundaryConditions",
        "applicability",
    }
    if family == "CAUSAL":
        blocked.add("causalClaimRole")
        if record.get("functionalForm") in {None, "UNSPECIFIED"}:
            blocked.add("functionalForm")
        if record.get("exposurePattern") in {None, "NOT_SPECIFIED"}:
            blocked.add("exposurePattern")
        if record.get("lagLowerBound") is None or record.get("lagUpperBound") is None:
            blocked.add("numericCausalLag")
        if record.get("effectPersistence") is None:
            blocked.add("persistence")
        if "RELATIONAL_DERIVED_STATE" in {record["subjectEntityType"], record["objectEntityType"]}:
            blocked.add("rdsSafeguards")
        if record.get("directness") == "MEDIATED_PATH":
            blocked.add("causalPathwayAssertion")
    if record.get("moderatorEntityIds"):
        blocked.add("normalizedModerationAssertion")

    legacy_scientific = {
        key: copy.deepcopy(record.get(key))
        for key in (
            "conditionsModerators", "moderatorEntityIds", "functionalForm",
            "functionalFormNotes", "lagProfile", "lagLowerBound", "lagUpperBound",
            "lagUnit", "lagNarrative", "exposurePattern", "effectPersistence",
            "evidenceStrength", "confidence", "generalizabilityContext",
            "governanceClass", "notesCaveats", "source", "legacyRelationship",
        )
    }
    causal_gate = None
    if family == "CAUSAL":
        causal_gate = expected_causal_review_gate(
            record["subjectEntityType"], record["objectEntityType"]
        )
    return {
        "schemaVersion": "1.0.0",
        "id": record["id"],
        "revision": 1,
        "relationFamily": family,
        "predicate": predicate,
        "symmetry": symmetry,
        "causalClaim": family == "CAUSAL",
        "sourceEntityId": record["subjectEntityId"],
        "sourceEntityType": record["subjectEntityType"],
        "targetEntityId": record["objectEntityId"],
        "targetEntityType": record["objectEntityType"],
        "causalClaimRole": None,
        "legacyDirectness": record.get("directness"),
        "polarity": record.get("polarity") if family == "CAUSAL" else None,
        "mechanism": record.get("mechanism"),
        "boundaryConditions": None,
        "applicability": None,
        "associationSpecification": None,
        "temporalSpecification": None,
        "moderatedRelationshipId": None,
        "moderatorSpecifications": [],
        "combinationRule": None,
        "moderationDirection": None,
        "causalReviewGate": causal_gate,
        "rdsSafeguards": None,
        "functionalForm": None,
        "exposurePattern": None,
        "causalLag": None,
        "persistence": None,
        "evidenceAssessmentIds": [],
        "sourceIds": copy.deepcopy(record.get("supportingEvidenceIds") or []),
        "governance": {
            "lifecycleStatus": "RESEARCH_NEEDED",
            "activationStatus": "NOT_ELIGIBLE",
            "blockStatus": "NEEDS_GOVERNANCE_INPUT",
            "decisionOutcome": "NOT_DECIDED",
            "authorityBasis": "PRESERVED_V3",
            "decisionRecord": None,
            "authorizedBy": None,
            "decisionDate": None,
            "effectiveVersion": None,
            "decisionRationale": None,
            "supersedesIds": [],
            "transitionProvenance": [],
        },
        "compatibility": {
            "sourceSchema": "RELATIONSHIP_SCHEMA_V3",
            "authorityStatus": "PRESERVED_V3_GOVERNED_ACTIVE",
            "migrationCompleteness": "INCOMPLETE",
            "v1Executability": "LEGACY_ONLY",
            "blockedFields": sorted(blocked),
            "legacyRelationFamily": record["relationFamily"],
            "legacyScientificFields": legacy_scientific,
            "legacyRecordHash": _canonical_hash(legacy),
            "legacyRecord": legacy,
        },
    }


def project_current_v3(catalog: Catalog | None = None) -> list[dict[str, Any]]:
    catalog = catalog or Catalog.from_repository()
    return [project_v3_relationship(record) for record in catalog.legacy_relationships.values()]


def restore_v3_relationship(projected: Mapping[str, Any]) -> dict[str, Any]:
    compatibility = projected.get("compatibility") or {}
    _require(compatibility.get("sourceSchema") == "RELATIONSHIP_SCHEMA_V3", "Record is not a V3 projection")
    legacy = copy.deepcopy(compatibility.get("legacyRecord"))
    _require(bool(legacy), "Lossless V3 record is missing")
    _require(_canonical_hash(legacy) == compatibility.get("legacyRecordHash"), "Lossless V3 payload hash mismatch")
    return legacy


def _native_records(filename: str, key: str) -> list[dict[str, Any]]:
    path = GOVERNED_V1_DIR / filename
    if not path.exists():
        return []
    envelope = _load_json(path)
    _require(
        set(envelope) == {"schemaVersion", key}
        and envelope["schemaVersion"] == "1.0.0"
        and isinstance(envelope[key], list),
        f"Invalid native V1 store envelope: {filename}",
    )
    return envelope[key]


def validate_native_source_register(schemas: SchemaSet) -> list[dict[str, Any]]:
    """Validate governed V1 sources and reject duplicates across both registries."""
    records = _native_records("source-register.json", "sources")
    if not records:
        return []
    legacy = _load_json(DATA / "sources.json")["sources"]
    legacy_ids = {row["id"] for row in legacy}
    seen_ids: set[str] = set()
    seen_pmids: set[str] = set()
    seen_dois: set[str] = set()
    seen_titles: set[str] = set()
    legacy_text = json.dumps(legacy, ensure_ascii=False).casefold()
    legacy_titles = {
        str(row.get("citationText") or "").strip().rstrip(".").casefold()
        for row in legacy
    }
    for record in records:
        schemas.validate("source", record)
        # Additive authoritative non-PubMed route; existing PubMed records are
        # preserved and checked exactly, not silently remigrated.
        verification = source_verification_module()
        try:
            verification.validate_source(record)
        except verification.VerificationError as error:
            raise ArchitectureValidationError(str(error)) from error
        identifier = record["id"]
        _require(identifier not in legacy_ids, f"Native source ID duplicates legacy source: {identifier}")
        _require(identifier not in seen_ids, f"Duplicate native source ID: {identifier}")
        seen_ids.add(identifier)
        pmid = record.get("pmid")
        doi = (record.get("doi") or "").casefold()
        title = record["title"].rstrip(".").casefold()
        if pmid:
            _require(pmid not in seen_pmids, f"Duplicate native PMID: {pmid}")
            _require(f"pubmed.ncbi.nlm.nih.gov/{pmid}" not in legacy_text, f"PMID already exists in legacy source register: {pmid}")
            seen_pmids.add(pmid)
        if doi:
            _require(doi not in seen_dois, f"Duplicate native DOI: {doi}")
            _require(doi not in legacy_text, f"DOI already exists in legacy source register: {doi}")
            seen_dois.add(doi)
        _require(title not in seen_titles, f"Duplicate native source title: {record['title']}")
        _require(title not in legacy_titles, f"Source title already exists in legacy register: {record['title']}")
        seen_titles.add(title)
    return records


def validate_governed_v1_store(
    catalog: Catalog, schemas: SchemaSet
) -> dict[str, int]:
    """Validate native governed scientific stores and cross-record provenance."""
    relationships = _native_records("relationships.json", "relationships")
    evidence = _native_records("evidence-assessments.json", "evidenceAssessments")
    pathways = _native_records("causal-pathways.json", "causalPathways")
    interventions = _native_records("interventions.json", "interventions")
    effects = _native_records("intervention-effects.json", "interventionEffects")
    if not any((relationships, evidence, pathways, interventions, effects)):
        return {
            "nativeRelationships": 0,
            "nativeCausalRelationships": 0,
            "nativeInterventions": 0,
            "nativeInterventionEffects": 0,
            "nativeEvidenceAssessments": 0,
            "nativeActiveRecords": 0,
            "nativeActiveRelationships": 0,
            "nativeActiveCausalRelationships": 0,
            "nativeActiveInterventions": 0,
            "nativeActiveInterventionEffects": 0,
            "nativeActiveEvidenceAssessments": 0,
        }

    groups = (relationships, evidence, pathways, interventions, effects)
    all_records = [record for group in groups for record in group]
    all_ids = [record["id"] for record in all_records]
    _require(len(all_ids) == len(set(all_ids)), "Duplicate native V1 scientific object ID")
    for record in all_records:
        governance = record["governance"]
        _require(governance["lifecycleStatus"] == "GOVERNED", "Native production store contains a non-governed record")
        _require(governance["activationStatus"] in {"ACTIVE", "INACTIVE"}, "Governed native record has invalid activation")

    relationship_map = dict(catalog.legacy_relationships)
    relationship_map.update({row["id"]: row for row in relationships})
    for relationship in relationships:
        validate_relationship(relationship, catalog, schemas, relationship_map)
        _require(bool(relationship["sourceIds"]), "Governed native Relationship requires sources")
        _require(bool(relationship["evidenceAssessmentIds"]), "Governed native Relationship requires evidence")
    for assessment in evidence:
        validate_evidence_assessment(assessment, catalog, schemas)
        _require(bool(assessment["sourceIds"]), "Governed native EvidenceAssessment requires sources")
        _require(bool(assessment["evidenceRationale"]), "Governed native EvidenceAssessment requires rationale")
    for pathway in pathways:
        validate_pathway(pathway, catalog, schemas, relationship_map)
    validate_intervention_catalog(
        interventions, effects, catalog, schemas, relationship_map
    )
    for intervention in interventions:
        _require(bool(intervention["identitySourceIds"]), "Governed native Intervention requires identity sources")
    for effect in effects:
        _require(bool(effect["sourceIds"]), "Governed native InterventionEffect requires sources")
        _require(bool(effect["evidenceAssessmentIds"]), "Governed native InterventionEffect requires evidence")

    by_evidence_id = {row["id"]: row for row in evidence}
    assertion_targets = {
        "RELATIONSHIP": {row["id"] for row in relationships},
        "MODERATION": {row["id"] for row in relationships if row["relationFamily"] == "MODERATION"},
        "CAUSAL_PATHWAY": {row["id"] for row in pathways},
        "INTERVENTION_EFFECT": {row["id"] for row in effects},
        "INTERVENTION_IDENTITY": {row["id"] for row in interventions},
    }
    for assessment in evidence:
        assertion = assessment["assertion"]
        _require(
            assertion["objectId"] in assertion_targets[assertion["objectType"]],
            f"Governed evidence assertion does not resolve: {assessment['id']}",
        )
    for record in relationships + pathways + effects:
        for evidence_id in record["evidenceAssessmentIds"]:
            _require(evidence_id in by_evidence_id, f"Governed EvidenceAssessment does not resolve: {evidence_id}")
            assertion = by_evidence_id[evidence_id]["assertion"]
            expected_type = "RELATIONSHIP"
            if record.get("relationFamily") == "MODERATION":
                expected_type = "MODERATION"
            elif "orderedRelationshipIds" in record:
                expected_type = "CAUSAL_PATHWAY"
            elif "interventionId" in record:
                expected_type = "INTERVENTION_EFFECT"
            _require(
                assertion == {"objectType": expected_type, "objectId": record["id"]},
                f"Governed evidence assertion does not match {record['id']}",
            )

    return {
        "nativeRelationships": len(relationships),
        "nativeCausalRelationships": sum(row["relationFamily"] == "CAUSAL" for row in relationships),
        "nativeInterventions": len(interventions),
        "nativeInterventionEffects": len(effects),
        "nativeEvidenceAssessments": len(evidence),
        "nativeActiveRecords": sum(governed_active(row) for row in all_records),
        "nativeActiveRelationships": sum(governed_active(row) for row in relationships),
        "nativeActiveCausalRelationships": sum(
            governed_active(row) and row["relationFamily"] == "CAUSAL"
            for row in relationships
        ),
        "nativeActiveInterventions": sum(governed_active(row) for row in interventions),
        "nativeActiveInterventionEffects": sum(governed_active(row) for row in effects),
        "nativeActiveEvidenceAssessments": sum(governed_active(row) for row in evidence),
    }


def validate_repository() -> dict[str, int]:
    schemas = SchemaSet()
    native_sources = validate_native_source_register(schemas)
    catalog = Catalog.from_repository()
    workspace = _load_json(CANDIDATE_WORKSPACE)
    validate_candidate_workspace(workspace, catalog, schemas)
    projected = project_current_v3(catalog)
    for record in projected:
        validate_relationship(record, catalog, schemas)
        _require(restore_v3_relationship(record) == catalog.legacy_relationships[record["id"]], "V3 round-trip mismatch")
    causal = sum(
        record["relationFamily"] == "CAUSAL"
        for record in catalog.legacy_relationships.values()
    )
    mediated = sum(record.get("directness") == "MEDIATED_PATH" for record in catalog.legacy_relationships.values())
    native_counts = validate_governed_v1_store(catalog, schemas)
    result = {
        "entities": len(catalog.entities),
        "legacyActiveRelationships": len(projected),
        "legacyActiveCausalRelationships": causal,
        "activeRelationships": len(projected) + native_counts["nativeActiveRelationships"],
        "activeCausalRelationships": causal + native_counts["nativeActiveCausalRelationships"],
        "v1IncompleteRelationships": sum(record["compatibility"]["migrationCompleteness"] == "INCOMPLETE" for record in projected),
        "v1LegacyOnlyRelationships": sum(record["compatibility"]["v1Executability"] == "LEGACY_ONLY" for record in projected),
        "legacyMediatedPathRecords": mediated,
        "nativeSources": len(native_sources),
    }
    result.update(native_counts)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-repository", action="store_true")
    args = parser.parse_args()
    if not args.validate_repository:
        parser.error("Use --validate-repository")
    counts = validate_repository()
    print("Relationship + Intervention V1 infrastructure validated")
    for name, value in counts.items():
        print(f"  {name}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
