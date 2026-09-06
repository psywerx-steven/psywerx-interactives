import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "relationship_intervention_v1.py"
SPEC = importlib.util.spec_from_file_location("relationship_intervention_v1", MODULE_PATH)
V1 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = V1
SPEC.loader.exec_module(V1)


def governance(lifecycle="CANDIDATE", activation="NOT_ELIGIBLE", object_id="SYN-OBJECT-1"):
    governed = lifecycle == "GOVERNED"
    transition_record = {
        "fromState": {
            "lifecycleStatus": "REVIEW_READY" if governed else None,
            "activationStatus": "NOT_ELIGIBLE",
        },
        "toState": {
            "lifecycleStatus": lifecycle,
            "activationStatus": activation,
        },
        "actorClass": "AUTHORIZED_HUMAN_GOVERNOR" if governed else "AUTOMATED_PROCESS_OR_AI",
        "rationale": "Synthetic lifecycle provenance.",
        "timestamp": "2026-09-05T12:00:00Z",
        "objectId": object_id,
        "revision": 1,
        "provenance": "synthetic unit test",
        "governanceDecisionRecord": "SYNTHETIC-GOVERNANCE-DECISION" if governed else None,
        "exactDecisionMaterialization": False,
    }
    return {
        "lifecycleStatus": lifecycle,
        "activationStatus": activation,
        "blockStatus": "NONE",
        "decisionOutcome": "APPROVED" if governed else "NOT_DECIDED",
        "authorityBasis": "V1_NATIVE",
        "decisionRecord": "SYNTHETIC-GOVERNANCE-DECISION" if governed else None,
        "authorizedBy": "authorized human governor" if governed else None,
        "decisionDate": "2026-09-05" if governed else None,
        "effectiveVersion": "1.0.0" if governed else None,
        "decisionRationale": "Synthetic test-only authorization." if governed else None,
        "supersedesIds": [],
        "transitionProvenance": [transition_record],
    }


def compatibility(executable="EXECUTABLE"):
    return {
        "sourceSchema": "RELATIONSHIP_V1",
        "authorityStatus": "V1_LIFECYCLE",
        "migrationCompleteness": "COMPLETE",
        "v1Executability": executable,
        "blockedFields": [],
        "legacyRelationFamily": None,
        "legacyScientificFields": None,
        "legacyRecordHash": None,
        "legacyRecord": None,
    }


def safeguards(**overrides):
    value = {
        "derivationVersion": "SYNTHETIC-DERIVATION-V1",
        "derivationInputIds": ["SYN-D-A"],
        "calculationWindow": "Synthetic test window",
        "temporalIndependence": "CONFIRMED",
        "mechanisticIndependence": "CONFIRMED",
        "constituentOverlap": "NONE",
        "sharedDenominatorCheck": "NONE",
        "definitionalEntailment": "ABSENT",
        "duplicatePropagationControl": "Synthetic test-only control.",
        "exogenousUse": "NOT_EXOGENOUS",
    }
    value.update(overrides)
    return value


def relationship(
    identifier="SYN-REL-LOCAL",
    source="SYN-D-A",
    target="SYN-D-B",
    source_type="DRIVER",
    target_type="DRIVER",
    active=False,
    role="MODELED_LOCAL_LINK",
):
    return {
        "schemaVersion": "1.0.0",
        "id": identifier,
        "revision": 1,
        "relationFamily": "CAUSAL",
        "predicate": "CAUSES",
        "symmetry": "DIRECTED",
        "causalClaim": True,
        "sourceEntityId": source,
        "sourceEntityType": source_type,
        "targetEntityId": target,
        "targetEntityType": target_type,
        "causalClaimRole": role,
        "legacyDirectness": None,
        "polarity": "POSITIVE",
        "mechanism": "Synthetic mechanism used only for validation tests.",
        "boundaryConditions": "Synthetic scope only.",
        "applicability": {
            "analyticUnit": "synthetic unit",
            "populationOrSystem": "synthetic population",
            "context": "test context",
        },
        "associationSpecification": None,
        "temporalSpecification": None,
        "moderatedRelationshipId": None,
        "moderatorSpecifications": [],
        "combinationRule": None,
        "moderationDirection": None,
        "causalReviewGate": V1.expected_causal_review_gate(source_type, target_type),
        "rdsSafeguards": safeguards() if "RELATIONAL_DERIVED_STATE" in {source_type, target_type} else None,
        "functionalForm": None,
        "exposurePattern": None,
        "causalLag": None,
        "persistence": None,
        "evidenceAssessmentIds": ["SYN-EVA-1"] if active else [],
        "sourceIds": ["SYN-SRC-1"] if active else [],
        "governance": governance("GOVERNED", "ACTIVE", identifier) if active else governance(object_id=identifier),
        "compatibility": compatibility(),
    }


def noncausal(predicate="ASSOCIATED_WITH"):
    record = relationship(identifier=f"SYN-REL-{predicate}")
    record.update({
        "relationFamily": "EMPIRICAL_NONCAUSAL",
        "predicate": predicate,
        "causalClaim": False,
        "causalClaimRole": None,
        "polarity": None,
        "mechanism": None,
        "causalReviewGate": None,
    })
    if predicate == "ASSOCIATED_WITH":
        record["symmetry"] = "SYMMETRIC"
        record["associationSpecification"] = {
            "temporalScope": "CROSS_SECTIONAL",
            "qualitativeStatement": "Synthetic association.",
            "strengthEstimate": None,
            "constituentOverlapCheck": "Synthetic entities do not overlap.",
        }
    else:
        record["symmetry"] = "DIRECTED"
        record["temporalSpecification"] = {
            "sourceStateDefinition": "synthetic low state" if predicate == "TRANSITIONS_TO" else None,
            "targetStateDefinition": "synthetic high state" if predicate == "TRANSITIONS_TO" else None,
            "observationUnit": "synthetic observation",
            "timeOrigin": "synthetic baseline",
            "horizonOrRiskSet": "synthetic horizon",
            "populationOrSystem": "synthetic population",
            "context": "test context",
            "transitionProbability": None,
        }
    return record


def moderation(combination="INDIVIDUAL"):
    record = relationship(identifier="SYN-MOD-1")
    record.update({
        "relationFamily": "MODERATION",
        "predicate": "MODERATES",
        "causalClaim": False,
        "sourceEntityId": None,
        "sourceEntityType": None,
        "targetEntityId": None,
        "targetEntityType": None,
        "causalClaimRole": None,
        "polarity": None,
        "moderatedRelationshipId": "SYN-LEGACY-A-B",
        "moderatorSpecifications": [{
            "entityId": "SYN-D-M",
            "entityType": "DRIVER",
            "stateOrRange": "synthetic high range",
            "scaleInterpretation": "higher synthetic values",
        }],
        "combinationRule": combination,
        "moderationDirection": "AMPLIFIES",
        "causalReviewGate": None,
    })
    return record


def intervention(identifier, kind="ATOMIC", components=None, active=False, category="TRAINING_OR_SKILL"):
    return {
        "schemaVersion": "1.0.0",
        "id": identifier,
        "revision": 1,
        "canonicalName": f"Synthetic {identifier}",
        "aliases": [],
        "interventionKind": kind,
        "category": category,
        "categorySpecification": "Synthetic category" if category == "OTHER_SPECIFIED" else None,
        "description": "Synthetic test-only manipulation.",
        "componentInterventionIds": components or [],
        "identitySourceIds": ["SYN-SRC-1"] if active else [],
        "externalCrosswalks": [],
        "governance": governance("GOVERNED", "ACTIVE", identifier) if active else governance(object_id=identifier),
    }


def effect(intervention_id="SYN-INT-A", target_kind="DRIVER", active=False):
    identifier = f"SYN-EFF-{intervention_id}-{target_kind}"
    return {
        "schemaVersion": "1.0.0",
        "id": identifier,
        "revision": 1,
        "interventionId": intervention_id,
        "targetKind": target_kind,
        "targetDriverId": "SYN-D-A" if target_kind == "DRIVER" else None,
        "targetRelationshipId": "SYN-LEGACY-A-B" if target_kind == "RELATIONSHIP" else None,
        "mechanisticDriverIds": ["SYN-D-M"] if target_kind == "RELATIONSHIP" else [],
        "effectMode": "MODIFY_RELATIONSHIP" if target_kind == "RELATIONSHIP" else "CHANGE_LEVEL",
        "intendedDirection": "ATTENUATE" if target_kind == "RELATIONSHIP" else "DECREASE",
        "mechanismOfAction": "Synthetic intervention-to-target mechanism.",
        "targetPopulationOrAudience": "synthetic population",
        "populationScope": "SUBGROUP_TARGETED",
        "context": "test context",
        "contextScope": "CONTEXT_DEPENDENT",
        "scale": "PERSON",
        "boundaryConditions": "Synthetic boundaries.",
        "implementers": [],
        "deliveryModalities": ["HUMAN_DELIVERED"],
        "deliveryModalitySpecification": None,
        "channels": [],
        "prerequisites": [],
        "moderatorEntityIds": [],
        "outcomeEntityIds": ["SYN-R-X"],
        "measureOfEffectIds": [],
        "unintendedEffects": [],
        "risks": ["Synthetic risk statement."],
        "ethicalLegalConstraints": [],
        "evidenceAssessmentIds": ["SYN-EVA-1"] if active else [],
        "sourceIds": ["SYN-SRC-1"] if active else [],
        "governance": governance("GOVERNED", "ACTIVE", identifier) if active else governance(object_id=identifier),
    }


def transition(actor, before_lifecycle, after_lifecycle, before_activation="NOT_ELIGIBLE", after_activation="NOT_ELIGIBLE", decision=None, exact=False):
    return {
        "fromState": {"lifecycleStatus": before_lifecycle, "activationStatus": before_activation},
        "toState": {"lifecycleStatus": after_lifecycle, "activationStatus": after_activation},
        "actorClass": actor,
        "rationale": "Synthetic transition test.",
        "timestamp": "2026-09-05T12:00:00Z",
        "objectId": "SYN-OBJECT-1",
        "revision": 1,
        "provenance": "synthetic unit test",
        "governanceDecisionRecord": decision,
        "exactDecisionMaterialization": exact,
    }


class RelationshipInterventionV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schemas = V1.SchemaSet()
        cls.entities = [
            {"id": "SYN-D-A", "entityType": "DRIVER"},
            {"id": "SYN-D-B", "entityType": "DRIVER"},
            {"id": "SYN-D-M", "entityType": "DRIVER"},
            {"id": "SYN-R-X", "entityType": "RELATIONAL_DERIVED_STATE"},
        ]
        cls.legacy_edges = [
            {"schemaVersion": "3.0", "id": "SYN-LEGACY-A-B", "subjectEntityId": "SYN-D-A", "objectEntityId": "SYN-D-B", "relationFamily": "CAUSAL", "governanceStatus": "ACTIVE"},
            {"schemaVersion": "3.0", "id": "SYN-LEGACY-B-R", "subjectEntityId": "SYN-D-B", "objectEntityId": "SYN-R-X", "relationFamily": "CAUSAL", "governanceStatus": "ACTIVE"},
            {"schemaVersion": "3.0", "id": "SYN-LEGACY-NONCAUSAL", "subjectEntityId": "SYN-D-A", "objectEntityId": "SYN-D-B", "relationFamily": "DERIVATIONAL", "governanceStatus": "ACTIVE"},
        ]
        cls.catalog = V1.Catalog.synthetic(cls.entities, cls.legacy_edges, ["SYN-SRC-1"])

    def assertInvalid(self, callable_, text):
        with self.assertRaisesRegex(V1.ArchitectureValidationError, text):
            callable_()

    def test_all_seven_production_schemas_meta_validate(self):
        self.assertEqual(len(self.schemas.schemas), 8)

    def test_family_predicate_compatibility(self):
        invalid = relationship()
        invalid["predicate"] = "ASSOCIATED_WITH"
        self.assertInvalid(lambda: V1.validate_relationship(invalid, self.catalog, self.schemas), "schema violation|incompatible")

    def test_noncausal_records_never_enter_causal_traversal(self):
        record = noncausal()
        record["governance"] = governance("GOVERNED", "ACTIVE", record["id"])
        record["evidenceAssessmentIds"] = ["SYN-EVA-1"]
        record["sourceIds"] = ["SYN-SRC-1"]
        V1.validate_relationship(record, self.catalog, self.schemas)
        self.assertEqual(V1.causal_traversal([record]), [])

    def test_association_is_symmetric_and_canonicalized(self):
        record = noncausal()
        record["sourceEntityId"], record["targetEntityId"] = "SYN-D-B", "SYN-D-A"
        canonical = V1.canonicalize_association(record)
        self.assertEqual((canonical["sourceEntityId"], canonical["targetEntityId"]), ("SYN-D-A", "SYN-D-B"))
        V1.validate_relationship(canonical, self.catalog, self.schemas)
        self.assertInvalid(lambda: V1.validate_relationship(record, self.catalog, self.schemas), "canonically ordered")

    def test_association_may_coexist_with_separate_causal_claim(self):
        causal = relationship()
        association = noncausal()
        V1.validate_relationship(causal, self.catalog, self.schemas)
        V1.validate_relationship(association, self.catalog, self.schemas)
        self.assertNotEqual(causal["id"], association["id"])
        self.assertTrue(causal["causalClaim"])
        self.assertFalse(association["causalClaim"])

    def test_transition_requires_qualified_states(self):
        valid = noncausal("TRANSITIONS_TO")
        V1.validate_relationship(valid, self.catalog, self.schemas)
        invalid = copy.deepcopy(valid)
        invalid["temporalSpecification"]["sourceStateDefinition"] = None
        self.assertInvalid(lambda: V1.validate_relationship(invalid, self.catalog, self.schemas), "schema violation|source state")

    def test_same_entity_transition_requires_different_states(self):
        invalid = noncausal("TRANSITIONS_TO")
        invalid["targetEntityId"] = "SYN-D-A"
        invalid["temporalSpecification"]["targetStateDefinition"] = "synthetic low state"
        self.assertInvalid(lambda: V1.validate_relationship(invalid, self.catalog, self.schemas), "must differ")

    def test_precedes_is_explicitly_noncausal(self):
        record = noncausal("PRECEDES")
        V1.validate_relationship(record, self.catalog, self.schemas)
        self.assertFalse(record["causalClaim"])
        self.assertEqual(V1.causal_traversal([record]), [])

    def test_moderation_targets_one_governed_causal_edge(self):
        V1.validate_relationship(moderation(), self.catalog, self.schemas)
        invalid = moderation()
        invalid["moderatedRelationshipId"] = "SYN-LEGACY-NONCAUSAL"
        self.assertInvalid(lambda: V1.validate_relationship(invalid, self.catalog, self.schemas), "governed causal")

    def test_joint_and_individual_moderation_are_distinct(self):
        invalid_joint = moderation("JOINT")
        self.assertInvalid(lambda: V1.validate_relationship(invalid_joint, self.catalog, self.schemas), "at least two")
        invalid_individual = moderation("INDIVIDUAL")
        invalid_individual["moderatorSpecifications"].append({
            "entityId": "SYN-D-B", "entityType": "DRIVER",
            "stateOrRange": "synthetic state", "scaleInterpretation": "synthetic scale",
        })
        self.assertInvalid(lambda: V1.validate_relationship(invalid_individual, self.catalog, self.schemas), "exactly one")

    def pathway(self):
        return {
            "schemaVersion": "1.0.0", "id": "SYN-CPW-1", "revision": 1,
            "startEntityId": "SYN-D-A", "endEntityId": "SYN-R-X",
            "orderedRelationshipIds": ["SYN-LEGACY-A-B", "SYN-LEGACY-B-R"],
            "intermediateEntities": [{"entityId": "SYN-D-B", "role": "MEDIATOR"}],
            "mediationClassification": "UNDETERMINED",
            "alignedScope": {"analyticUnit": "synthetic unit", "populationOrSystem": "synthetic population", "context": "test context"},
            "temporalOrderRationale": "Synthetic ordered-edge rationale.",
            "evidenceAssessmentIds": [], "sourceIds": [],
            "duplicateCountingControl": {"mode": "PATHWAY_ONLY", "totalEffectRelationshipId": None, "rationale": "No shortcut is counted."},
            "contributesCausalEdge": False, "governance": governance(object_id="SYN-CPW-1"),
        }

    def test_pathway_requires_contiguous_governed_segments(self):
        path = self.pathway()
        relationships = dict(self.catalog.legacy_relationships)
        V1.validate_pathway(path, self.catalog, self.schemas, relationships)
        broken = copy.deepcopy(path)
        broken["orderedRelationshipIds"].reverse()
        self.assertInvalid(lambda: V1.validate_pathway(broken, self.catalog, self.schemas, relationships), "start|contiguous")

    def test_graph_reachability_does_not_create_pathway_or_weight(self):
        path = self.pathway()
        self.assertFalse(path["contributesCausalEdge"])
        invalid = copy.deepcopy(path)
        invalid["graphWeight"] = 1.0
        self.assertInvalid(lambda: self.schemas.validate("pathway", invalid), "Additional properties")

    def test_total_effect_requires_explicit_reconciliation(self):
        path = self.pathway()
        total = relationship("SYN-REL-TOTAL", target="SYN-R-X", target_type="RELATIONAL_DERIVED_STATE", active=True, role="TOTAL_EFFECT")
        relationships = dict(self.catalog.legacy_relationships)
        relationships[total["id"]] = total
        self.assertInvalid(lambda: V1.validate_pathway(path, self.catalog, self.schemas, relationships), "explicit reconciliation")
        path["duplicateCountingControl"] = {"mode": "RECONCILED", "totalEffectRelationshipId": total["id"], "rationale": "Synthetic mutually exclusive execution rule."}
        V1.validate_pathway(path, self.catalog, self.schemas, relationships)

    def test_modeled_local_link_is_not_controlled_by_legacy_directness(self):
        record = relationship(active=True)
        record["legacyDirectness"] = "MEDIATED_PATH"
        V1.validate_relationship(record, self.catalog, self.schemas)
        self.assertEqual([record], V1.causal_traversal([record]))

    def test_driver_target_is_valid_and_rds_target_is_rejected(self):
        interventions = {"SYN-INT-A": intervention("SYN-INT-A")}
        valid = effect()
        V1.validate_intervention_effect(valid, interventions, self.catalog, self.schemas, self.catalog.legacy_relationships)
        invalid = copy.deepcopy(valid)
        invalid["targetDriverId"] = "SYN-R-X"
        self.assertInvalid(lambda: V1.validate_intervention_effect(invalid, interventions, self.catalog, self.schemas, self.catalog.legacy_relationships), "RDS cannot")

    def test_relationship_target_requires_mechanistic_driver_when_active(self):
        interventions = {"SYN-INT-A": intervention("SYN-INT-A", active=True)}
        valid = effect(target_kind="RELATIONSHIP", active=True)
        V1.validate_intervention_effect(valid, interventions, self.catalog, self.schemas, self.catalog.legacy_relationships)
        invalid = copy.deepcopy(valid)
        invalid["mechanisticDriverIds"] = []
        self.assertInvalid(lambda: V1.validate_intervention_effect(invalid, interventions, self.catalog, self.schemas, self.catalog.legacy_relationships), "mechanistic Driver")

    def test_relationship_target_must_be_governed_causal(self):
        interventions = {"SYN-INT-A": intervention("SYN-INT-A")}
        invalid = effect(target_kind="RELATIONSHIP")
        invalid["targetRelationshipId"] = "SYN-LEGACY-NONCAUSAL"
        self.assertInvalid(lambda: V1.validate_intervention_effect(invalid, interventions, self.catalog, self.schemas, self.catalog.legacy_relationships), "governed causal")

    def test_package_requires_two_unique_components_and_rejects_cycles(self):
        a = intervention("SYN-INT-A")
        b = intervention("SYN-INT-B")
        package = intervention("SYN-INT-P", "PACKAGE", ["SYN-INT-A", "SYN-INT-B"])
        V1.validate_intervention_catalog([a, b, package], [], self.catalog, self.schemas, self.catalog.legacy_relationships)
        a["interventionKind"] = "PACKAGE"
        a["componentInterventionIds"] = ["SYN-INT-B", "SYN-INT-P"]
        self.assertInvalid(lambda: V1.validate_intervention_catalog([a, b, package], [], self.catalog, self.schemas, self.catalog.legacy_relationships), "cycle")

    def test_component_effects_do_not_imply_package_effect(self):
        a = intervention("SYN-INT-A", active=True)
        b = intervention("SYN-INT-B")
        package = intervention("SYN-INT-P", "PACKAGE", ["SYN-INT-A", "SYN-INT-B"], active=True)
        component_effect = effect("SYN-INT-A", active=True)
        self.assertInvalid(lambda: V1.validate_intervention_catalog([a, b, package], [component_effect], self.catalog, self.schemas, self.catalog.legacy_relationships), "own active effect")

    def test_other_specified_requires_explanation(self):
        valid = intervention("SYN-INT-A", category="OTHER_SPECIFIED")
        self.schemas.validate("intervention", valid)
        valid["categorySpecification"] = None
        self.assertInvalid(lambda: self.schemas.validate("intervention", valid), "schema violation")
        invalid_effect = effect()
        invalid_effect["deliveryModalities"] = ["OTHER_SPECIFIED"]
        self.assertInvalid(lambda: self.schemas.validate("intervention_effect", invalid_effect), "schema violation")

    def test_context_target_and_alter_context_mode_are_not_v1_vocabulary(self):
        invalid_target = effect()
        invalid_target["targetKind"] = "CONTEXT_CONDITION"
        self.assertInvalid(lambda: self.schemas.validate("intervention_effect", invalid_target), "schema violation")
        invalid_mode = effect()
        invalid_mode["effectMode"] = "ALTER_CONTEXT"
        self.assertInvalid(lambda: self.schemas.validate("intervention_effect", invalid_mode), "schema violation")

    def test_all_driver_rds_combinations_receive_exact_gate(self):
        combinations = [
            ("DRIVER", "DRIVER", "STANDARD_CAUSAL"),
            ("DRIVER", "RELATIONAL_DERIVED_STATE", "HEIGHTENED_CAUSAL"),
            ("RELATIONAL_DERIVED_STATE", "DRIVER", "HEIGHTENED_CAUSAL"),
            ("RELATIONAL_DERIVED_STATE", "RELATIONAL_DERIVED_STATE", "EXCEPTIONAL_CAUSAL"),
        ]
        for source_type, target_type, gate in combinations:
            with self.subTest(source_type=source_type, target_type=target_type):
                self.assertEqual(V1.expected_causal_review_gate(source_type, target_type), gate)

    def test_heightened_causal_claim_requires_completed_safeguards(self):
        record = relationship(target="SYN-R-X", target_type="RELATIONAL_DERIVED_STATE", active=True)
        record["rdsSafeguards"] = None
        self.assertInvalid(lambda: V1.validate_relationship(record, self.catalog, self.schemas), "requires safeguards")

    def test_rds_exogenous_and_constituent_overlap_guards(self):
        record = relationship(source="SYN-R-X", source_type="RELATIONAL_DERIVED_STATE", active=True)
        record["rdsSafeguards"] = safeguards(exogenousUse="UNRESOLVED")
        self.assertInvalid(lambda: V1.validate_relationship(record, self.catalog, self.schemas), "exogenous use")
        record["rdsSafeguards"] = safeguards(constituentOverlap="PRESENT_REQUIRES_RECONCILIATION")
        self.assertInvalid(lambda: V1.validate_relationship(record, self.catalog, self.schemas), "constituent overlap")

    def test_automation_can_manage_only_non_governed_workflow(self):
        for before, after in V1.AUTOMATED_LIFECYCLE_TRANSITIONS:
            V1.validate_governance_transition(transition("AUTOMATED_PROCESS_OR_AI", before, after))

    def test_automation_cannot_govern_or_activate(self):
        govern = transition("AUTOMATED_PROCESS_OR_AI", "REVIEW_READY", "GOVERNED", after_activation="ACTIVE")
        self.assertInvalid(lambda: V1.validate_governance_transition(govern), "not authorized")
        activate = transition("AUTOMATED_PROCESS_OR_AI", "GOVERNED", "GOVERNED", "INACTIVE", "ACTIVE")
        self.assertInvalid(lambda: V1.validate_governance_transition(activate), "not authorized")

    def test_human_governance_requires_decision_provenance(self):
        missing = transition("AUTHORIZED_HUMAN_GOVERNOR", "REVIEW_READY", "GOVERNED", after_activation="ACTIVE")
        self.assertInvalid(lambda: V1.validate_governance_transition(missing), "decision record")
        valid = transition("AUTHORIZED_HUMAN_GOVERNOR", "REVIEW_READY", "GOVERNED", after_activation="ACTIVE", decision="SYN-GOV-1")
        V1.validate_governance_transition(valid)

    def test_exact_human_decision_may_be_materialized_by_automation(self):
        exact = transition("AUTOMATED_PROCESS_OR_AI", "REVIEW_READY", "GOVERNED", after_activation="ACTIVE", decision="SYN-GOV-1", exact=True)
        V1.validate_governance_transition(exact)
        broadened = transition("AUTOMATED_PROCESS_OR_AI", "CANDIDATE", "GOVERNED", after_activation="ACTIVE", decision="SYN-GOV-1", exact=True)
        self.assertInvalid(lambda: V1.validate_governance_transition(broadened), "not governable")

    def test_governed_inactive_is_valid_and_not_traversed(self):
        record = relationship(active=True)
        record["governance"] = governance("GOVERNED", "INACTIVE", record["id"])
        V1.validate_relationship(record, self.catalog, self.schemas)
        self.assertEqual(V1.causal_traversal([record]), [])

    def test_deprecated_record_cannot_reactivate(self):
        invalid = transition("AUTHORIZED_HUMAN_GOVERNOR", "DEPRECATED", "GOVERNED", "INACTIVE", "ACTIVE", "SYN-GOV-1")
        self.assertInvalid(lambda: V1.validate_governance_transition(invalid), "cannot reactivate")

    def test_automation_cannot_substantively_revise_governed_record(self):
        before = relationship(active=True)
        after = copy.deepcopy(before)
        after["revision"] = 2
        record = transition("AUTOMATED_PROCESS_OR_AI", "GOVERNED", "GOVERNED", "ACTIVE", "ACTIVE")
        self.assertInvalid(lambda: V1.validate_governed_revision(before, after, record), "human authorization")

    def test_v3_projection_is_lossless_stable_and_conservative(self):
        catalog = V1.Catalog.from_repository()
        projected = V1.project_current_v3(catalog)
        self.assertEqual(len(projected), 450)
        self.assertEqual(sum(row["relationFamily"] == "CAUSAL" for row in projected), 431)
        self.assertEqual({row["id"] for row in projected}, set(catalog.legacy_relationships))
        for row in projected:
            V1.validate_relationship(row, catalog, self.schemas)
            self.assertEqual(V1.restore_v3_relationship(row), catalog.legacy_relationships[row["id"]])
            self.assertIsNone(row["causalClaimRole"])
            self.assertIsNone(row["boundaryConditions"])
            self.assertEqual(row["evidenceAssessmentIds"], [])
            self.assertEqual(row["compatibility"]["migrationCompleteness"], "INCOMPLETE")
            self.assertEqual(row["compatibility"]["v1Executability"], "LEGACY_ONLY")

    def test_legacy_directness_and_mediated_paths_are_not_reinterpreted(self):
        projected = V1.project_current_v3()
        mediated = [row for row in projected if row["legacyDirectness"] == "MEDIATED_PATH"]
        self.assertEqual(len(mediated), 39)
        self.assertTrue(all(row["causalClaimRole"] is None for row in mediated))
        self.assertTrue(all("causalPathwayAssertion" in row["compatibility"]["blockedFields"] for row in mediated))
        self.assertEqual(V1.causal_traversal(projected), [])

    def test_empty_candidate_workspace_is_valid_and_non_production(self):
        workspace = json.loads(V1.CANDIDATE_WORKSPACE.read_text(encoding="utf-8"))
        V1.validate_candidate_workspace(workspace, V1.Catalog.from_repository(), self.schemas)
        self.assertFalse(workspace["productionGraphEligible"])

    def test_candidate_workspace_rejects_governed_record(self):
        workspace = json.loads(V1.CANDIDATE_WORKSPACE.read_text(encoding="utf-8"))
        workspace["relationships"] = [relationship(active=True)]
        self.assertInvalid(lambda: V1.validate_candidate_workspace(workspace, self.catalog, self.schemas), "cannot contain governed")

    def test_evidence_is_normalized_and_not_a_graph_weight(self):
        evidence = {
            "schemaVersion": "1.0.0", "id": "SYN-EVA-1", "revision": 1,
            "assertion": {"objectType": "RELATIONSHIP", "objectId": "SYN-REL-LOCAL"},
            "sourceIds": ["SYN-SRC-1"], "evidenceRationale": "Synthetic evidence rationale.",
            "evidenceStrength": "LIMITED", "confidence": "LOW", "evidenceDisposition": "SUPPORTS",
            "population": "synthetic population", "context": "test context",
            "studyDesignCharacterizations": [{"designType": "NOT_CHARACTERIZED", "specification": None}],
            "quantitativeEstimate": None, "uncertainty": ["Synthetic uncertainty."],
            "conflictingEvidence": {"sourceIds": [], "summary": None}, "limitations": [],
            "reviewProvenance": {"createdAt": "2026-09-05T12:00:00Z", "createdByActorClass": "AUTOMATED_PROCESS_OR_AI", "reviewedAt": None, "reviewedBy": None, "sourceSchema": "synthetic-test"},
            "governance": governance(object_id="SYN-EVA-1"),
        }
        V1.validate_evidence_assessment(evidence, self.catalog, self.schemas)
        evidence["graphWeight"] = 0.5
        self.assertInvalid(lambda: self.schemas.validate("evidence", evidence), "Additional properties")

    def test_active_evidence_requires_sources_and_rationale(self):
        evidence = {
            "schemaVersion": "1.0.0", "id": "SYN-EVA-2", "revision": 1,
            "assertion": {"objectType": "RELATIONSHIP", "objectId": "SYN-REL-LOCAL"},
            "sourceIds": [], "evidenceRationale": None, "evidenceStrength": "NOT_ASSESSED",
            "confidence": "NOT_ASSESSED", "evidenceDisposition": "NOT_ASSESSED",
            "population": None, "context": None, "studyDesignCharacterizations": [],
            "quantitativeEstimate": None, "uncertainty": [],
            "conflictingEvidence": {"sourceIds": [], "summary": None}, "limitations": [],
            "reviewProvenance": {"createdAt": "2026-09-05T12:00:00Z", "createdByActorClass": "AUTOMATED_PROCESS_OR_AI", "reviewedAt": None, "reviewedBy": None, "sourceSchema": "synthetic-test"},
            "governance": governance("GOVERNED", "ACTIVE", "SYN-EVA-2"),
        }
        self.assertInvalid(lambda: V1.validate_evidence_assessment(evidence, self.catalog, self.schemas), "requires sources")

    def test_repository_validation_preserves_baseline_counts(self):
        counts = V1.validate_repository()
        self.assertEqual(counts["entities"], 811)
        self.assertEqual(counts["legacyActiveRelationships"], 450)
        self.assertEqual(counts["legacyActiveCausalRelationships"], 431)
        self.assertEqual(counts["activeRelationships"], 456)
        self.assertEqual(counts["activeCausalRelationships"], 435)
        self.assertEqual(counts["v1IncompleteRelationships"], 450)


if __name__ == "__main__":
    unittest.main()
