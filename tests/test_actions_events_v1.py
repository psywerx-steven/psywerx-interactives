"""Governed infrastructure tests; all new scientific examples are fictional."""
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import actions_events_v1 as ae
import actions_events_synthetic as syn
import relationship_intervention_v1 as ri


class ActionsEventsTests(unittest.TestCase):
    def setUp(self):
        self.catalog, self.context = syn.fixture()

    def invalid(self, text):
        with self.assertRaisesRegex((ae.ValidationError, ri.ArchitectureValidationError), text):
            ae.validate_catalog(self.catalog, self.context)

    def test_meta_and_synthetic_contracts(self):
        self.assertEqual(len(ae.SchemaSet().validators), 11)
        self.assertEqual(ae.validate_catalog(self.catalog, self.context, candidate=True)["records"], 46)

    def test_all_origins_and_domains(self):
        self.assertEqual({l for r in self.catalog["happeningTypes"] for l in r["originLayers"]}, {"BIO","PSY","SOC","CUL","ENV","INS","INF","TEC"})
        self.assertEqual({d for r in self.catalog["happeningTypes"] for d in r["domainTags"]}, set(ae.VOCAB["domainTags"]))
        self.assertTrue(any(len(r["originLayers"]) > 1 for r in self.catalog["happeningTypes"]))

    def test_every_property_and_change_descriptor(self):
        rows = {r["property"]: r for r in self.catalog["effectAssertions"]}
        self.assertEqual(set(rows), set(ae.VOCAB["propertyChanges"]))
        schemas = ae.schema_set()
        for prop, values in ae.VOCAB["propertyChanges"].items():
            for value in values:
                with self.subTest(property=prop, change=value):
                    row = copy.deepcopy(rows[prop]); row["change"] = value
                    if value == "OTHER_SPECIFIED": row["otherSpecified"] = "Fictional shape definition"
                    schemas.validate("effect-assertion", row)

    def test_wrong_property_descriptor(self):
        self.catalog["effectAssertions"][0]["change"] = "DECELERATE"
        self.invalid("is not one of")

    def test_other_specified_requires_detail(self):
        self.catalog["effectAssertions"][9]["change"] = "OTHER_SPECIFIED"
        self.invalid("string")

    def test_origin_is_not_target(self):
        row = self.catalog["effectAssertions"][0]
        self.assertEqual(row["targetLayers"], ["BIO"])
        self.assertEqual(self.catalog["happeningTypes"][0]["originLayers"], ["INS"])
        row["targetLayers"] = ["INS"]
        self.invalid("independently")

    def test_all_target_layers(self):
        for layer in ("BIO","PSY","SOC","CUL","ENV","INS","INF","TEC"):
            self.catalog["effectAssertions"][0].update(targetId="SYN-DRIVER-"+layer,targetLayers=[layer])
            ae.validate_catalog(self.catalog, self.context)

    def test_rds_direct_target_even_natural_event(self):
        self.catalog["effectAssertions"][1]["targetId"] = "SYN-RDS"
        self.invalid("No direct RDS")

    def test_context_target_and_mode_absent(self):
        self.catalog["effectAssertions"][0]["targetKind"] = "CONTEXT_CONDITION"
        self.invalid("is not one of")
        self.catalog["effectAssertions"][0]["targetKind"] = "DRIVER"
        self.catalog["effectAssertions"][0]["effectMode"] = "ALTER_CONTEXT"
        self.invalid("Additional properties")

    def test_exact_relationship_resolution(self):
        self.catalog["effectAssertions"][4]["targetId"] = "SYN-UNKNOWN"
        self.invalid("Exact governed causal")

    def test_noncausal_relationship_not_modification_target(self):
        self.context.relationships["SYN-REL-001"]["relationFamily"] = "EMPIRICAL_NONCAUSAL"
        self.invalid("Exact governed causal")

    def test_relationship_property_needs_edge(self):
        self.catalog["effectAssertions"][4].update(targetKind="DRIVER",targetId="SYN-DRIVER-SOC")
        self.invalid("Relationship property|RELATIONSHIP")

    def test_mechanistic_driver_linkage_active(self):
        self.catalog = syn.make_active(self.catalog)
        self.catalog["effectAssertions"][4]["mechanisticDriverIds"] = []
        syn.refresh_authorization(self.catalog)
        self.invalid("mechanistic Driver")

    def test_rds_mechanistic_link_rejected(self):
        self.catalog["effectAssertions"][4]["mechanisticDriverIds"] = ["SYN-RDS"]
        self.invalid("must be a Driver")

    def test_occurrence_is_optional(self):
        self.catalog["effectAssertions"][0]["occurrenceId"] = None
        ae.validate_catalog(self.catalog,self.context)

    def test_observed_occurrence_needs_evidence(self):
        self.catalog["occurrences"][0]["epistemicStatus"] = "OBSERVED"
        self.invalid("non-empty")

    def test_occurrence_evidence_cannot_support_effect(self):
        occurrence = self.catalog["occurrences"][0]
        occurrence.update(epistemicStatus="OBSERVED",evidenceAssessmentIds=["SYN-EVIDENCE-001"])
        evidence = self.catalog["evidenceAssessments"][0]
        evidence["assertion"] = {"objectType":"OCCURRENCE","objectId":occurrence["id"]}
        evidence["sourceFindings"][0]["supportedSemantics"] = ["OCCURRENCE"]
        self.invalid("cannot transfer")

    def test_externality_not_exogeneity(self):
        self.catalog["occurrences"][0]["boundary"]["causalExogeneity"] = "UNCONFOUNDED"
        self.invalid("NOT_INFERRED_FROM_EXTERNALITY")

    def test_high_confidence_association_not_causal(self):
        evidence = self.catalog["evidenceAssessments"][0]
        evidence["synthesis"]["confidence"] = "HIGH"
        finding = evidence["sourceFindings"][0]
        finding.update(basis=["OBSERVATIONAL_CROSS_SECTIONAL"], supportedSemantics=["ASSOCIATION"])
        self.invalid("cannot establish a causal")
        self.catalog["effectAssertions"][0]["claimSemantics"] = "ASSOCIATION"
        ae.validate_catalog(self.catalog,self.context)

    def test_model_inputs_not_observations(self):
        effect = self.catalog["effectAssertions"][0]
        effect["productionMethod"] = "MODEL_INFERENCE"
        self.invalid("explicit inputs")
        effect["inferenceProvenance"] = {"modelOrPathwayId":"SYN-MODEL","inputEvidenceIds":effect["evidenceAssessmentIds"],"assumptions":"Fictional"}
        self.invalid("direct empirical")
        self.catalog["evidenceAssessments"][0]["sourceFindings"][0]["inputRole"] = "MODEL_INPUT"
        ae.validate_catalog(self.catalog,self.context)

    def test_hypothesis_not_supported_fact(self):
        self.catalog["effectAssertions"][0]["productionMethod"] = "HYPOTHESIS"
        self.invalid("Untested hypothesis")

    def test_unknown_not_zero(self):
        self.catalog["effectAssertions"][0].update(knowledgeStatus="INSUFFICIENT_EVIDENCE",change="NO_DETECTED_CHANGE")
        self.invalid("Unknown effect is not zero")

    def test_supported_null_needs_precision_not_nonsignificance(self):
        self.catalog["effectAssertions"][0].update(knowledgeStatus="SUPPORTED_NULL",change="NO_DETECTED_CHANGE")
        finding = self.catalog["evidenceAssessments"][0]["sourceFindings"][0]
        finding["disposition"] = "NULL_FINDING"
        self.catalog["evidenceAssessments"][0]["synthesis"]["conflicts"] = [{"findingId":finding["id"],"dispositionRationale":"Scoped null"}]
        self.invalid("Nonsignificance")
        finding["nullInterpretation"] = {"contrast":"Fictional contrast","precisionAssessment":"Fictional bounded precision","interpretation":"BOUNDED_NULL_SUPPORTED","rationale":"Fictional null assessment, not p-value alone"}
        ae.validate_catalog(self.catalog,self.context)

    def test_contrary_findings_cannot_disappear(self):
        evidence = self.catalog["evidenceAssessments"][0]
        finding = copy.deepcopy(evidence["sourceFindings"][0])
        finding.update(id="SYN-FINDING-NULL",disposition="NULL_FINDING")
        evidence["sourceFindings"].append(finding)
        self.invalid("preserve every source")
        evidence["synthesis"]["sourceFindingIds"].append(finding["id"])
        self.invalid("explicit synthesis disposition")
        evidence["synthesis"]["conflicts"].append({"findingId":finding["id"],"dispositionRationale":"Null contrast preserved"})
        evidence["synthesis"]["disposition"] = "MIXED"
        ae.validate_catalog(self.catalog,self.context)

    def test_source_resolution(self):
        self.catalog["evidenceAssessments"][0]["sourceFindings"][0]["sourceId"] = "SYN-MISSING"
        self.invalid("source unresolved")

    def test_numeric_estimate_optional_confidence_not_number(self):
        self.assertIsNone(self.catalog["evidenceAssessments"][0]["sourceFindings"][0]["quantitativeEstimate"])
        self.catalog["evidenceAssessments"][0]["synthesis"]["confidence"] = 0.9
        self.invalid("is not one of")

    def test_no_graph_weights(self):
        self.catalog["effectAssertions"][0]["weight"] = 0.5
        self.invalid("Additional properties")

    def test_cyclic_cannot_be_universal_monotonic(self):
        self.catalog["effectAssertions"][9]["observedChange"] = "INCREASE"
        self.invalid("universal observed sign")

    def test_formula_and_duplicate_driver_representation(self):
        self.catalog["effectAssertions"][0]["grounding"]["derivationEntailed"] = "YES"
        self.invalid("Formula-derived")
        self.catalog["effectAssertions"][0]["grounding"].update(derivationEntailed="NO",representedDriverId="SYN-DRIVER-BIO")
        self.invalid("single-contribution")

    def test_duplicate_proposition(self):
        duplicate = copy.deepcopy(self.catalog["effectAssertions"][0]); duplicate.update(syn.base("SYN-DUPLICATE"))
        self.catalog["effectAssertions"].append(duplicate)
        self.invalid("Duplicate contextual")

    def test_moderator_direct_route_double_count(self):
        modifier = self.catalog["effectAssertions"][7]
        modifier["contribution"]["role"] = "PRIMARY"
        self.invalid("Duplicate contribution")

    def test_moderator_requires_shared_identity(self):
        self.catalog["effectAssertions"][7]["contribution"]["groupId"] = "SYN-DIFFERENT"
        self.invalid("share contribution")

    def test_pathway_never_inferred(self):
        self.catalog["effectAssertions"][0]["claimSemantics"] = "PATHWAY"
        self.invalid("separate governed CausalPathway")

    def test_package_cycle(self):
        for i, components in ((0,["SYN-TYPE-002","SYN-TYPE-003"]),(1,["SYN-TYPE-001","SYN-TYPE-003"])):
            self.catalog["happeningTypes"][i].update(packageKind="PACKAGE",components=components,componentEnumeration="NON_EXHAUSTIVE")
        self.invalid("Package composition cycle")

    def test_package_non_exhaustive_and_no_effect_inference(self):
        self.catalog["happeningTypes"][0].update(packageKind="PACKAGE",components=["SYN-TYPE-004","SYN-TYPE-009"],componentEnumeration="NON_EXHAUSTIVE")
        self.catalog["effectAssertions"] = [r for r in self.catalog["effectAssertions"] if r["id"] != "SYN-EFFECT-001"]
        self.catalog["evidenceAssessments"] = [r for r in self.catalog["evidenceAssessments"] if r["id"] != "SYN-EVIDENCE-001"]
        self.catalog = syn.make_active(self.catalog)
        self.invalid("own active effect")

    def test_governance_requires_exact_authorization(self):
        self.catalog = syn.make_active(self.catalog)
        self.catalog["effectAssertions"][0]["mechanism"] += " changed"
        self.invalid("Exact human scientific authorization")

    def test_ai_cannot_govern(self):
        self.catalog = syn.make_active(self.catalog)
        self.catalog["effectAssertions"][0]["governance"]["transitionProvenance"][-2]["actorClass"] = "AUTOMATED_PROCESS_OR_AI"
        syn.refresh_authorization(self.catalog)
        self.invalid("Non-governor transition")

    def test_ai_cannot_activate(self):
        self.catalog = syn.make_active(self.catalog)
        self.catalog["effectAssertions"][0]["governance"]["transitionProvenance"][-1]["actorClass"] = "AUTOMATED_PROCESS_OR_AI"
        syn.refresh_authorization(self.catalog)
        self.invalid("Non-governor transition")

    def test_architecture_decision_is_not_scientific_authority(self):
        self.catalog = syn.make_active(self.catalog)
        record = self.catalog["effectAssertions"][0]
        record["governance"]["decisionRecord"] = "docs/governance/ACTIONS_EVENTS_V1_GOVERNANCE_DECISION.md"
        syn.refresh_authorization(self.catalog)
        self.catalog["authorizations"][0]["decisionRecord"] = record["governance"]["decisionRecord"]
        self.invalid("Exact human scientific authorization|Architecture authorization")

    def test_candidate_cannot_supply_authority(self):
        self.catalog = syn.make_active(self.catalog)
        with self.assertRaisesRegex(ae.ValidationError,"cannot govern"):
            ae.validate_catalog(self.catalog,self.context,candidate=True)

    def test_synthetic_rejected_in_production(self):
        with self.assertRaisesRegex(ae.ValidationError,"Synthetic content"):
            ae.validate_catalog(self.catalog,ae.Context.repository())

    def test_eligibility_three_dimensions_no_state_changes(self):
        active = syn.make_active(self.catalog); before = copy.deepcopy(active)
        effect = active["effectAssertions"][0]
        result = ae.use_eligibility(effect["id"],active,self.context,syn.actor_context(effect))
        self.assertTrue(result["syntheticSimulation"]["actionWouldQualify"])
        self.assertFalse(result["scientificUseEligibility"]["eligible"])
        self.assertFalse(result["modelEligibility"]["eligible"])
        self.assertFalse(result["practitionerActionEligibility"]["eligible"])
        self.assertEqual(before,active); self.assertEqual(result["statusChanges"],0)

    def test_uncontrolled_disaster_not_actionable(self):
        active = syn.make_active(self.catalog); effect=active["effectAssertions"][1]
        result = ae.use_eligibility(effect["id"],active,self.context,syn.actor_context(effect))
        self.assertTrue(result["syntheticSimulation"]["scientificWouldQualify"])
        self.assertFalse(result["syntheticSimulation"]["actionWouldQualify"])

    def test_each_actor_use_constraint_fails_closed(self):
        active = syn.make_active(self.catalog); effect=active["effectAssertions"][0]
        for key in ("prerequisites","feasibility","legalConstraints","ethicalRiskConstraints","applicability"):
            request = syn.actor_context(effect); request["checks"][key]["status"] = "UNKNOWN"
            result = ae.use_eligibility(effect["id"],active,self.context,request)
            self.assertFalse(result["syntheticSimulation"]["actionWouldQualify"], key)
        request=syn.actor_context(effect);request["control"]["extent"]="NONE"
        self.assertFalse(ae.use_eligibility(effect["id"],active,self.context,request)["syntheticSimulation"]["actionWouldQualify"])

    def test_inactive_candidate_not_actionable(self):
        effect=self.catalog["effectAssertions"][0]
        result=ae.use_eligibility(effect["id"],self.catalog,self.context,syn.actor_context(effect))
        self.assertFalse(result["syntheticSimulation"]["actionWouldQualify"])

    def test_identity_alone_never_effect(self):
        self.catalog["effectAssertions"]=[];self.catalog["evidenceAssessments"]=[]
        with self.assertRaisesRegex(ae.ValidationError,"Unknown native effect"):
            ae.use_eligibility("SYN-NONE",self.catalog,self.context)

    def test_blank_workspace_and_local_readiness(self):
        workspace=ae.empty_workspace("PSY-F03",ae.BASELINE)
        self.assertFalse(ae.validate_workspace(workspace)["passBReady"])
        workspace["readiness"]={k:True for k in workspace["readiness"]}
        self.assertTrue(ae.validate_workspace(workspace)["passBReady"])
        self.assertFalse(workspace["productionEligible"])

    def test_source_identifier_dedup_not_registration(self):
        source={"id":"SYN-SOURCE","doi":"10.1234/ABC","title":"Fictional Title","year":2000}
        r=ae.source_registration_triage({"doi":"https://doi.org/10.1234/abc"},[source])
        self.assertEqual(r["status"],"EXACT_IDENTIFIER_MATCH");self.assertFalse(r["registrationPerformed"])
        self.assertEqual(ae.source_registration_triage({"title":"Fictional title","year":2000},[source])["status"],"TITLE_YEAR_REVIEW")

    def test_recorded_uncontrollable_cannot_be_overridden_by_request(self):
        active=syn.make_active(self.catalog);effect=active["effectAssertions"][0]
        request=syn.actor_context(effect)
        profile={**request["control"], "extent":"NONE", "population":effect["scope"]["population"],
                 "context":effect["scope"]["context"], "conditions":"SYN fictional constraint", "provenance":syn.provenance()}
        active["happeningTypes"][0]["controlProfiles"]=[profile]
        syn.refresh_authorization(active)
        result=ae.use_eligibility(effect["id"],active,self.context,request)
        self.assertFalse(result["syntheticSimulation"]["actionWouldQualify"])

    def test_governed_inactive_valid_but_not_eligible(self):
        inactive=syn.make_active(self.catalog)
        for row in ae.all_records(inactive):
            row["governance"]["transitionProvenance"].pop()
            row["governance"]["activationStatus"]="INACTIVE"
        syn.refresh_authorization(inactive)
        ae.validate_catalog(inactive,self.context)
        result=ae.use_eligibility("SYN-EFFECT-001",inactive,self.context)
        self.assertFalse(result["syntheticSimulation"]["scientificWouldQualify"])

    def test_component_cannot_reuse_package_evidence(self):
        self.catalog["happeningTypes"][0].update(packageKind="PACKAGE",components=["SYN-TYPE-004","SYN-TYPE-009"],componentEnumeration="NON_EXHAUSTIVE")
        self.catalog["effectAssertions"][3]["evidenceAssessmentIds"]=["SYN-EVIDENCE-001"]
        self.invalid("evidence cannot transfer")

    def test_subgroup_evidence_must_belong_to_assertion(self):
        self.catalog["effectAssertions"][0]["qualifiers"]["subgroups"]=[{"population":"SYN subgroup","description":"SYN difference","evidenceAssessmentIds":["SYN-MISSING"]}]
        self.invalid("Subgroup difference")

    def test_shared_dataset_note_required(self):
        ev=self.catalog["evidenceAssessments"][0]
        finding=copy.deepcopy(ev["sourceFindings"][0]);finding["id"]="SYN-FINDING-REUSED-DATA"
        ev["sourceFindings"][0]["datasetIds"]=["SYN-DATASET"]
        finding["datasetIds"]=["SYN-DATASET"]
        ev["sourceFindings"].append(finding);ev["synthesis"]["sourceFindingIds"].append(finding["id"])
        ev["synthesis"]["datasetOverlap"]=None
        self.invalid("Shared datasets")
        ev["synthesis"]["datasetOverlap"]="SYN same dataset, not independent replication"
        ae.validate_catalog(self.catalog,self.context)

    def test_observed_occurrence_has_own_evidence_not_effect_transfer(self):
        occurrence=self.catalog["occurrences"][0]
        ev=copy.deepcopy(self.catalog["evidenceAssessments"][0])
        ev.update(id="SYN-OCCURRENCE-EVIDENCE",governance=syn.governance("SYN-OCCURRENCE-EVIDENCE"))
        ev["assertion"]={"objectType":"OCCURRENCE","objectId":occurrence["id"]}
        ev["sourceFindings"][0].update(id="SYN-OCCURRENCE-FINDING",supportedSemantics=["OCCURRENCE"])
        ev["synthesis"]["sourceFindingIds"]=["SYN-OCCURRENCE-FINDING"]
        self.catalog["evidenceAssessments"].append(ev)
        occurrence.update(epistemicStatus="OBSERVED",evidenceAssessmentIds=[ev["id"]])
        ae.validate_catalog(self.catalog,self.context)
        occurrence["timeWindow"]=None
        self.invalid("Observed occurrence needs time")

    def test_each_copy_ready_prompt_is_complete(self):
        import re
        text=(ae.ROOT/"docs/governance/ACTIONS_EVENTS_RESEARCH_PROMPTS_V1.md").read_text(encoding="utf-8")
        blocks=re.findall(r"```text\n([\s\S]*?)```",text)
        self.assertEqual(len(blocks),5)
        required=list(ae.VOCAB["propertyChanges"])+["Biological","Psychological","Social","Cultural","Physical/Environmental",
            "Institutional/Structural","Informational","Technological","routine/unintended","external events/shocks",
            "environmental exposures","institutional/structural","technological change","social/network",
            "informational exposures","biological/physiological","confidence","clarity","provenance","governance",
            "mixed","null","contrary","NO FINDINGS","UNRESOLVED"]
        for index,block in enumerate(blocks,1):
            for term in required:self.assertIn(term.casefold(),block.casefold(),(index,term))

    def test_contradicted_synthesis_not_practitioner_eligible(self):
        active=syn.make_active(self.catalog);effect=active["effectAssertions"][0]
        for disposition in ("CONTRADICTED","INSUFFICIENT"):
            active["evidenceAssessments"][0]["synthesis"]["disposition"]=disposition
            syn.refresh_authorization(active)
            result=ae.use_eligibility(effect["id"],active,self.context,syn.actor_context(effect))
            self.assertTrue(result["syntheticSimulation"]["scientificWouldQualify"])
            self.assertFalse(result["syntheticSimulation"]["actionWouldQualify"])

    def test_native_record_cannot_duplicate_existing_intervention_identity(self):
        self.catalog["happeningTypes"][0]["id"]="INT-V1-BIO-F01-001"
        with self.assertRaisesRegex(ae.ValidationError,"identity collision"):
            ae.validate_catalog(self.catalog,ae.Context.repository())


class CompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.views=ae.compatibility_catalog()

    def test_lossless_same_identity_views(self):
        self.assertEqual(len(self.views),26)
        for view in self.views:
            self.assertEqual(ae.restore_compatibility(view),view["sourceRecord"])
            self.assertEqual(view["id"],view["sourceRecord"]["id"])
            self.assertEqual(view["governance"],view["sourceRecord"]["governance"])
            self.assertEqual(view["additionalScientificPropositions"],0)

    def test_compatibility_not_new_propositions(self):
        original=[r for rows in ae.source_catalog().values() for r in rows]
        self.assertEqual(len(ae.deduplicate_scientific_views(original+self.views)),26)

    def test_missing_scientific_metadata_not_invented(self):
        for view in self.views:
            if view["viewType"]=="HAPPENING_TYPE": self.assertEqual(view["normalized"]["originLayers"],[])
            if view["viewType"]=="EVIDENCE_ASSESSMENT": self.assertEqual(view["normalized"]["sourceFindings"],[])
            if view["viewType"]=="EFFECT_ASSERTION": self.assertIsNone(view["normalized"]["observedChange"])

    def test_modified_or_stale_view_rejected(self):
        view=copy.deepcopy(self.views[0]);view["normalized"]["name"]="Changed scientific identity"
        with self.assertRaisesRegex(ae.ValidationError,"changed authority/content"):
            ae.validate_compatibility(view)

    def test_mixed_light_and_melatonin_preserved(self):
        for suffix in ("005","006"):
            view=next(r for r in self.views if r["id"]=="EVA-V1-BIO-F01-IE-"+suffix)
            self.assertEqual(view["normalized"]["synthesis"]["disposition"],"MIXED")
            self.assertTrue(view["normalized"]["synthesis"]["conflicts"]["sourceIds"])

    def test_bio_states_and_cyclic_direction_preserved(self):
        types=[r for r in self.views if r["viewType"]=="HAPPENING_TYPE"]
        self.assertEqual(sum(ae.state_active(r) for r in types),5)
        self.assertEqual(sum(r["governance"]["activationStatus"]=="INACTIVE" for r in types),4)
        for suffix in ("005","006"):
            row=next(r for r in self.views if r["id"]=="IE-V1-BIO-F01-"+suffix)
            self.assertEqual(row["normalized"]["change"],"STATE_DEPENDENT")
            self.assertEqual(row["sourceRecord"]["intendedDirection"],"CONTEXT_DEPENDENT")

    def test_bio_package_exact_nonexhaustive_semantics(self):
        row=next(r for r in self.views if r["id"]=="INT-V1-BIO-F01-006")
        self.assertEqual(row["normalized"]["components"],row["sourceRecord"]["componentInterventionIds"])
        self.assertIn("not as an exhaustive scientific definition",row["sourceRecord"]["description"])

    def test_preserved_active_science_not_automatic_action_or_model(self):
        result=ae.use_eligibility("IE-V1-BIO-F01-005")
        self.assertTrue(result["scientificUseEligibility"]["eligible"])
        self.assertFalse(result["modelEligibility"]["eligible"])
        self.assertFalse(result["practitionerActionEligibility"]["eligible"])


if __name__=="__main__":
    unittest.main()
