"""Synthetic semantic stress tests. Never imports or changes canonical science."""
import copy
import json
import unittest
from pathlib import Path
import model


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.bundle = model.synthetic_fixture()

    def invalid(self, needle):
        errors = model.validate_bundle(self.bundle)
        self.assertTrue(any(needle in e for e in errors), errors)

    def decisions(self):
        return [{"objectId": item["id"], "revision": 1, "hypothetical": True,
                 "actorClass": "AUTHORIZED_HUMAN_GOVERNOR", "outcome": "APPROVE"}
                for key in model.SCHEMAS for item in self.bundle[key]]

    def use_context(self):
        return {"label": "SYNTHETIC / NON_PRODUCTION", "actor": "Fictional practitioner",
                "context": self.bundle["effects"][0]["scope"]["context"],
                "prerequisitesCleared": True, "risksReviewed": True, "applicabilityConfirmed": True}

    def null_finding(self):
        return {"contrast": "Fictional exposure versus fictional comparator",
                "precisionAssessment": "Fictional interval entirely within declared equivalence margin",
                "interpretation": "EQUIVALENCE_WITHIN_MARGIN", "equivalenceMargin": "Fictional prespecified margin"}

    def test_schemas_fixtures_and_determinism(self):
        self.assertEqual(model.validate_bundle(self.bundle), [])
        self.assertEqual(self.bundle, json.loads((Path(__file__).parent / "synthetic.json").read_text()))
        self.assertEqual(model.dry_run(self.bundle), model.dry_run(copy.deepcopy(self.bundle)))

    def test_eleven_properties_and_eight_layers(self):
        self.assertEqual(set(model.PROPERTIES), {e["property"] for e in self.bundle["effects"]})
        self.assertEqual(set(model.LAYERS), {l for t in self.bundle["types"] for l in t["originLayers"]})
        # Independently exercise every target Layer, including relationship target endpoints.
        for layer in model.LAYERS:
            example = copy.deepcopy(self.bundle)
            example["effects"][0]["targetId"] = "SYN-DRIVER-" + layer
            example["effects"][0]["targetLayers"] = [layer]
            self.assertEqual(model.validate_bundle(example), [], layer)
        self.assertTrue(any(len(t["originLayers"]) > 1 for t in self.bundle["types"]))

    def test_property_change_compatibility(self):
        self.bundle["effects"][0]["change"] = "REVERSE"
        self.invalid("incompatible property/change")

    def test_no_production_schema_or_identity(self):
        self.bundle["types"][0]["id"] = "INT-V1-BIO-F01-001"
        self.invalid("does not match")

    def test_duplicate_identity_and_episode(self):
        self.bundle["types"][1]["identityKey"] = self.bundle["types"][0]["identityKey"]
        self.bundle["occurrences"][1]["episodeKey"] = self.bundle["occurrences"][0]["episodeKey"]
        self.invalid("duplicate types")
        self.invalid("duplicate occurrences")

    def test_driver_type_identity_collision(self):
        self.bundle["types"][0]["id"] = "SYN-DRIVER-BIO"
        self.invalid("reuse Driver")

    def test_observed_occurrence_is_not_effect_evidence(self):
        occurrence = self.bundle["occurrences"][0]
        occurrence["epistemicStatus"] = "OBSERVED"
        assessment = self.bundle["evidence"][0]
        assessment["assertionId"] = occurrence["id"]
        occurrence["occurrenceEvidenceIds"] = [assessment["id"]]
        self.invalid("assertion-specific evidence")

    def test_missing_occurrence_evidence(self):
        self.bundle["occurrences"][0]["epistemicStatus"] = "OBSERVED"
        self.invalid("observed occurrence needs")

    def test_high_confidence_association_is_not_causation(self):
        self.bundle["evidence"][0]["confidence"] = "HIGH"
        self.bundle["evidence"][0]["sourceFindings"][0]["basis"] = ["CROSS_SECTIONAL_OBSERVATION"]
        self.invalid("alone does not establish causal")
        self.bundle["effects"][0]["claimSemantics"] = "ASSOCIATION"
        self.assertEqual(model.validate_bundle(self.bundle), [])
        self.assertNotIn(self.bundle["effects"][0]["id"], model.dry_run(self.bundle, self.decisions())["eligibleSimulationEffectIds"])

    def test_context_required(self):
        self.bundle["effects"][0]["scope"]["context"] = ""
        self.invalid("should be non-empty")

    def test_rds_target_forbidden_even_nonintervention(self):
        self.bundle["types"][0]["interventionSubset"] = False
        self.bundle["effects"][0]["targetId"] = "SYN-RDS-BIO"
        self.invalid("RDS direct target forbidden")

    def test_generic_context_target_forbidden(self):
        self.bundle["effects"][0]["targetKind"] = "CONTEXT_CONDITION"
        self.invalid("is not one of")

    def test_mediator_double_count_requires_reconciliation(self):
        first, second = self.bundle["effects"][:2]
        second["contributionKey"] = first["contributionKey"]
        self.invalid("duplicate event/mediator propagation")
        second["propagationRole"] = "MEDIATOR_DESCRIPTION"
        first["reconciliation"] = second["reconciliation"] = "Count only primary; mediator is descriptive, not additive"
        self.assertEqual(model.validate_bundle(self.bundle), [])
        self.assertNotIn(second["id"], model.dry_run(self.bundle, self.decisions())["eligibleSimulationEffectIds"])

    def test_explicit_event_to_moderator_route_c(self):
        primary = next(e for e in self.bundle["effects"] if e["id"] == "SYN-EFFECT-012")
        moderation = next(e for e in self.bundle["effects"] if e["id"] == "SYN-EFFECT-007")
        self.assertEqual(primary["targetKind"], "DRIVER")
        self.assertIn(primary["targetId"], moderation["mechanisticDriverIds"])
        self.assertEqual(moderation["targetId"], "SYN-REL-001")
        self.assertEqual(primary["contributionKey"], moderation["contributionKey"])
        self.assertNotEqual(primary["evidenceIds"], moderation["evidenceIds"])
        self.assertEqual(model.validate_bundle(self.bundle), [])
        report = model.dry_run(self.bundle, self.decisions(), self.use_context())
        self.assertIn(primary["id"], report["scientificSimulationEligibleEffectIds"])
        self.assertNotIn(moderation["id"], report["scientificSimulationEligibleEffectIds"])

    def test_duplicate_proposition_independent_of_id(self):
        duplicate = copy.deepcopy(self.bundle["effects"][0])
        duplicate["id"] = "SYN-EFFECT-DUP"
        duplicate["contributionKey"] = "different-key-does-not-make-new-proposition"
        self.bundle["effects"].append(duplicate)
        self.invalid("duplicate contextual effect proposition")

    def test_missing_bundle_fields_fail_cleanly(self):
        self.assertTrue(model.validate_bundle({}))

    def test_dangling_reference_endpoints_fail_cleanly(self):
        self.bundle["relationships"][0]["sourceId"] = "SYN-MISSING"
        self.invalid("dangling entity endpoint")
        self.assertEqual(model.dry_run(self.bundle, self.decisions())["scientificSimulationEligibleEffectIds"], [])

    def test_malformed_and_duplicate_references_fail_cleanly(self):
        self.bundle["entities"].append(copy.deepcopy(self.bundle["entities"][0]))
        self.invalid("duplicate reference identity")
        self.bundle["entities"].append(None)
        self.invalid("every record/reference must be an object")
        self.bundle["entities"].pop()
        self.bundle["entities"][0]["id"] = []
        self.invalid("requires a string identity")

    def test_supported_null_requires_null_source(self):
        self.bundle["effects"][0]["knowledgeStatus"] = "SUPPORTED_NULL"
        self.bundle["effects"][0]["change"] = "NO_DETECTED_CHANGE"
        self.invalid("source-level null finding")

    def test_cyclic_input_never_universal_sign(self):
        self.bundle["effects"][0]["functionalShape"] = "CYCLIC"
        self.invalid("cannot have universal sign")

    def test_unknown_not_zero(self):
        self.bundle["effects"][0]["knowledgeStatus"] = "INSUFFICIENT_EVIDENCE"
        self.bundle["effects"][0]["change"] = "NO_DETECTED_CHANGE"
        self.invalid("unknown/not-applicable is not zero")

    def test_supported_null_distinct_from_unknown(self):
        self.bundle["effects"][0]["knowledgeStatus"] = "SUPPORTED_NULL"
        self.bundle["effects"][0]["change"] = "NO_DETECTED_CHANGE"
        self.bundle["evidence"][0]["sourceFindings"][0]["disposition"] = "NULL_FINDING"
        self.bundle["evidence"][0]["sourceFindings"][0]["nullInterpretation"] = self.null_finding()
        self.bundle["evidence"][0]["synthesis"]["disposition"] = "MIXED"
        self.assertEqual(model.validate_bundle(self.bundle), [])
        self.assertNotIn("SYN-EFFECT-001", model.dry_run(self.bundle, self.decisions())["eligibleSimulationEffectIds"])

    def test_contrary_evidence_preserved(self):
        contrary = copy.deepcopy(self.bundle["evidence"][0]["sourceFindings"][0])
        contrary["id"] = "SYN-FINDING-CONTRARY"
        contrary["disposition"] = "NULL_FINDING"
        self.bundle["evidence"][0]["sourceFindings"].append(contrary)
        self.bundle["evidence"][0]["synthesis"]["sourceFindingIds"].append(contrary["id"])
        self.invalid("contrary/null")
        self.bundle["evidence"][0]["synthesis"]["disposition"] = "MIXED"
        self.assertEqual(model.validate_bundle(self.bundle), [])

    def test_missing_contrary_search_blocks(self):
        self.bundle["evidence"][0]["synthesis"]["contraryEvidenceSearch"] = "NOT_INVESTIGATED"
        self.invalid("contrary evidence not investigated")

    def test_synthesis_cannot_omit_source_finding(self):
        self.bundle["evidence"][0]["synthesis"]["sourceFindingIds"] = []
        self.invalid("including contrary findings")

    def test_no_graph_weights_or_confidence_numbers(self):
        self.bundle["effects"][0]["weight"] = 0.8
        self.invalid("Additional properties")
        del self.bundle["effects"][0]["weight"]
        self.bundle["evidence"][0]["confidence"] = 0.8
        self.invalid("is not one of")

    def test_model_inference_not_empirical(self):
        self.bundle["effects"][0]["productionMethod"] = "MODEL_INFERENCE"
        self.invalid("model identity")
        self.bundle["effects"][0]["inferenceProvenance"] = {
            "modelId": "SYN-MODEL-001", "inputEvidenceIds": ["SYN-EVIDENCE-001"],
            "assumptions": "Fictional model assumptions; result is inference"}
        self.bundle["evidence"][0]["sourceFindings"][0]["inputRole"] = "MODEL_INPUT"
        self.assertEqual(model.validate_bundle(self.bundle), [])
        self.assertEqual(self.bundle["evidence"][0]["sourceFindings"][0]["basis"], ["EXPERIMENT"])
        self.assertNotIn("SYN-EFFECT-001", model.dry_run(self.bundle, self.decisions())["eligibleSimulationEffectIds"])

    def test_null_only_cannot_support_positive_effect(self):
        self.bundle["evidence"][0]["sourceFindings"][0]["disposition"] = "NULL_FINDING"
        self.bundle["evidence"][0]["synthesis"]["disposition"] = "MIXED"
        self.invalid("null-only evidence")
        self.bundle["effects"][0]["knowledgeStatus"] = "INSUFFICIENT_EVIDENCE"
        self.bundle["effects"][0]["change"] = "UNKNOWN"
        self.assertEqual(model.validate_bundle(self.bundle), [])

    def test_empty_moderation_evidence_blocks(self):
        assessment = self.bundle["evidence"][6]
        assessment["sourceFindings"] = []
        assessment["synthesis"]["sourceFindingIds"] = []
        self.invalid("empty/null-only evidence")
        self.assertEqual(model.dry_run(self.bundle, self.decisions())["eligibleSimulationEffectIds"], [])

    def test_supported_effect_unknown_is_invalid(self):
        self.bundle["effects"][0]["change"] = "UNKNOWN"
        self.invalid("specified non-null change")

    def test_all_supporting_records_must_be_review_ready(self):
        for collection, status in (("types", "CANDIDATE"), ("evidence", "RESEARCH_NEEDED")):
            example = copy.deepcopy(self.bundle)
            example[collection][0]["governance"]["lifecycleStatus"] = status
            self.assertNotIn("SYN-EFFECT-001", model.dry_run(example, self.decisions())["eligibleSimulationEffectIds"])

    def test_actor_action_eligibility_separate_from_scientific(self):
        decisions = self.decisions()
        report = model.dry_run(self.bundle, decisions)
        self.assertIn("SYN-EFFECT-001", report["scientificSimulationEligibleEffectIds"])
        self.assertEqual(report["actorActionEligibleInterventionIds"], [])
        report = model.dry_run(self.bundle, decisions, self.use_context())
        self.assertIn("SYN-TYPE-001", report["actorActionEligibleInterventionIds"])
        self.bundle["occurrences"][0]["control"]["extent"] = "NONE"
        report = model.dry_run(self.bundle, decisions, self.use_context())
        self.assertIn("SYN-EFFECT-001", report["scientificSimulationEligibleEffectIds"])
        self.assertNotIn("SYN-TYPE-001", report["actorActionEligibleInterventionIds"])

    def test_actor_scope_risk_prerequisite_intention_gates(self):
        for key, value in (("actor", "Another actor"), ("context", "Another context"),
                           ("risksReviewed", False), ("prerequisitesCleared", False),
                           ("applicabilityConfirmed", False)):
            context = self.use_context()
            context[key] = value
            self.assertNotIn("SYN-TYPE-001", model.dry_run(self.bundle, self.decisions(), context)["actorActionEligibleInterventionIds"])
        self.bundle["occurrences"][0]["intentionality"] = "UNINTENDED"
        self.assertNotIn("SYN-TYPE-001", model.dry_run(self.bundle, self.decisions(), self.use_context())["actorActionEligibleInterventionIds"])

    def test_reachability_not_pathway(self):
        self.bundle["effects"][0]["claimSemantics"] = "PATHWAY"
        self.invalid("separate governed pathway")

    def test_relationship_target_and_mechanistic_driver(self):
        effect = self.bundle["effects"][6]
        effect["mechanisticDriverIds"] = ["SYN-RDS-BIO"]
        self.invalid("invalid mechanistic Driver")
        effect["mechanisticDriverIds"] = ["SYN-DRIVER-PSY"]
        self.bundle["relationships"][0]["family"] = "EMPIRICAL_NONCAUSAL"
        self.invalid("governed causal reference")

    def test_externality_not_exogeneity(self):
        self.bundle["occurrences"][0]["boundary"]["causalExogeneity"] = "EXOGENOUS"
        self.invalid("NOT_INFERRED_FROM_EXTERNALITY")

    def test_simulation_requires_explicit_hypothetical_human_decisions(self):
        before = copy.deepcopy(self.bundle)
        self.assertEqual(model.dry_run(self.bundle)["eligibleSimulationEffectIds"], [])
        decisions = self.decisions()
        for decision in decisions:
            decision["actorClass"] = "AI_OR_AUTOMATION"
        self.assertEqual(model.dry_run(self.bundle, decisions)["eligibleSimulationEffectIds"], [])
        report = model.dry_run(self.bundle, self.decisions())
        self.assertEqual(len(report["eligibleSimulationEffectIds"]), 11)
        self.assertFalse(report["productionEligible"])
        self.assertFalse(report["quantitativeModelEligible"])
        self.assertEqual(report["statusesChanged"], 0)
        self.assertEqual(before, self.bundle)

    def test_intervention_without_effect_never_eligible(self):
        decisions = [d for d in self.decisions() if d["objectId"] != "SYN-EFFECT-001"]
        report = model.dry_run(self.bundle, decisions)
        self.assertNotIn("SYN-TYPE-001", report["eligibleSimulationInterventionIds"])
        self.assertNotIn("SYN-TYPE-002", report["eligibleSimulationInterventionIds"])  # non-action shock

    def test_package_not_sum_and_components_not_inferred(self):
        package = self.bundle["types"][0]
        package["packageKind"] = "PACKAGE"
        package["components"] = ["SYN-TYPE-004", "SYN-TYPE-007"]
        package["componentEnumeration"] = "NON_EXHAUSTIVE"
        self.assertEqual(model.validate_bundle(self.bundle), [])
        decisions = [d for d in self.decisions() if d["objectId"] != "SYN-EFFECT-001"]
        report = model.dry_run(self.bundle, decisions)
        self.assertNotIn("SYN-TYPE-001", report["eligibleSimulationInterventionIds"])
        decisions = [d for d in self.decisions() if d["objectId"] not in {"SYN-EFFECT-004", "SYN-EFFECT-007"}]
        report = model.dry_run(self.bundle, decisions)
        self.assertNotIn("SYN-EFFECT-004", report["eligibleSimulationEffectIds"])
        self.assertNotIn("SYN-EFFECT-007", report["eligibleSimulationEffectIds"])

    def test_package_cycle(self):
        for i, components in ((0, ["SYN-TYPE-002", "SYN-TYPE-003"]), (1, ["SYN-TYPE-001", "SYN-TYPE-003"])):
            item = self.bundle["types"][i]
            item.update(packageKind="PACKAGE", components=components, componentEnumeration="NON_EXHAUSTIVE")
        self.invalid("composition cycle")

    def test_activation_state_cannot_be_written(self):
        self.bundle["effects"][0]["governance"]["activationStatus"] = "ACTIVE"
        self.invalid("NOT_ELIGIBLE")


if __name__ == "__main__":
    unittest.main()
