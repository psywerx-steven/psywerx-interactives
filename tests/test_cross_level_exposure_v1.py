"""Production cross-level exposure Phase 0/1 safety and shadow tests."""

import copy
import hashlib
import json
import sys
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import cross_level_exposure_v1 as xle


def read(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class CrossLevelExposureProductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.relationship = next(row for row in read("data/relationships.json")["relationships"] if row["id"] == "REL-INS-040")

    def mapping(self):
        stages = ["SOURCE_STATE", "IMPLEMENTATION_OR_TRANSMISSION", "ACTUAL_EXPOSURE", "PERCEIVED_EXPOSURE", "TARGET_RESPONSE"]
        return {
            "schemaVersion": "1.0.0", "mappingId": "XLEM-V1-INSTITUTION-IMPLEMENTATION-PERCEPTION-001", "mappingVersion": "1.0.0",
            "objectKind": "SCIENTIFIC_ROUTING_ELIGIBILITY_CONTRACT", "sourceLevel": "INSTITUTION", "targetLevel": "PERSON", "routeType": "IMPLEMENTATION",
            "routeStages": stages, "exposureDefinition": "Implemented procedure actually encountered by a covered person", "exposureUnit": "PERSON_ENCOUNTER",
            "temporalOrder": stages, "membershipSemantics": "Membership alone is insufficient", "eligibilitySemantics": "Eligibility alone is insufficient",
            "implementationSemantics": "The institutional procedure must be realized in practice", "assignmentSemantics": "Assignment alone is insufficient",
            "actualExposureSemantics": "The target person must encounter the implemented procedure", "perceivedExposureSemantics": "Perception is the bounded person-level target",
            "coverageSemantics": "Only explicitly covered and exposed persons qualify", "partialCoverageAllowed": True, "ambientContextAllowed": False,
            "networkStateRequirements": {"required": False, "description": "No Network State dependency"},
            "intermediateReferenceRules": ["Reference only scientifically substantive existing entities"], "evidenceBindingRules": ["Mapping references do not create causal evidence"],
            "scopeLimitations": ["Shadow validation only"], "causalEvidence": False, "executionAuthority": False, "hasWeight": False, "hasLifecycle": False, "hasPropagationState": False,
            "provenance": {"architectureDecisionId": "GOV-CROSS-LEVEL-IMPLEMENTATION-001-2026-09-26"},
        }

    def binding(self):
        return {
            "schemaVersion": "1.0.0", "bindingId": "XLEB-V1-REL-INS-040-001", "bindingVersion": "1.0.0", "relationshipId": "REL-INS-040",
            "relationshipRevisionOrHash": xle.digest(self.relationship), "sourceEntityId": "INS-051", "sourceLevel": "INSTITUTION", "targetEntityId": "PSY-022", "targetLevel": "PERSON",
            "mappingId": self.mapping()["mappingId"], "mappingVersion": "1.0.0", "claimSpecificQualifiers": ["No scientific disposition change"],
            "intermediateEntityIds": [], "happeningTypeIds": [], "networkStateReferences": [],
            "implementationRequirement": {"required": True, "definition": "Procedure realized in practice"}, "membershipRule": "Insufficient alone", "eligibilityRule": "Insufficient alone", "assignmentRule": "Insufficient alone",
            "actualExposureRule": {"required": True, "definition": "Person actually encounters procedure"}, "perceptionRequired": True, "perceptionEntityId": "PSY-022",
            "exposureWindow": "Bounded before target measurement", "coverageRule": "Exact applicable target set required", "temporalAlignment": self.mapping()["temporalOrder"],
            "evidenceReferences": [], "scope": "REL-INS-040 shadow eligibility", "provenance": {"architectureDecisionId": "GOV-CROSS-LEVEL-IMPLEMENTATION-001-2026-09-26"},
            "shadowEligibilityOnly": True, "feedsGraphConstruction": False, "feedsSimulation": False, "executionAuthorized": False,
        }

    def test_repository_phase_state_is_bounded(self):
        state = xle.validate_repository()
        self.assertIn(state, [
            {"mappings": 0, "bindings": 0, "relationshipMigrations": 0, "graphBehaviorChanges": 0, "simulationBehaviorChanges": 0, "causalAuthorizations": 0, "activations": 0},
            {"mappings": 1, "bindings": 1, "relationshipMigrations": 0, "graphBehaviorChanges": 0, "simulationBehaviorChanges": 0, "causalAuthorizations": 0, "activations": 0},
        ])

    def test_mapping_and_binding_schema_and_exactness(self):
        mapping, binding = self.mapping(), self.binding()
        self.assertTrue(xle.validate_mapping(mapping))
        self.assertTrue(xle.validate_attachment(mapping, binding, self.relationship))
        for selector in xle.IMPLICIT_SELECTORS:
            invalid = copy.deepcopy(mapping); invalid["mappingVersion"] = selector
            with self.assertRaises(xle.ValidationError): xle.validate_mapping(invalid)

    def test_mapping_cannot_be_graph_or_lifecycle_object(self):
        for field, value in (("weight", 1), ("polarity", "POSITIVE"), ("lifecycleStatus", "ACTIVE"), ("propagationValue", 1)):
            invalid = copy.deepcopy(self.mapping()); invalid[field] = value
            with self.assertRaises(xle.ValidationError): xle.validate_mapping(invalid)
        for field in ("causalEvidence", "executionAuthority", "hasWeight", "hasLifecycle", "hasPropagationState"):
            invalid = copy.deepcopy(self.mapping()); invalid[field] = True
            with self.assertRaises(xle.ValidationError): xle.validate_mapping(invalid)

    def test_binding_exact_relationship_source_target_and_levels(self):
        for field, value in (("relationshipId", "REL-INS-041"), ("relationshipRevisionOrHash", "0" * 64), ("sourceEntityId", "INS-052"), ("targetEntityId", "PSY-023"), ("sourceLevel", "GROUP"), ("targetLevel", "GROUP")):
            invalid = copy.deepcopy(self.binding()); invalid[field] = value
            with self.assertRaises(xle.ValidationError): xle.validate_attachment(self.mapping(), invalid, self.relationship)

    def test_protected_science_hashes_unchanged(self):
        manifest = read("data/governance/post-scale-up/cross-level/cross-level-stage-e-protected-hashes.json")
        for relative, expected in manifest["files"].items():
            actual = hashlib.sha256((ROOT / relative).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
            self.assertEqual(actual, expected, relative)
        self.assertEqual(len(read("data/drivers.json")), 770)
        entities = read("data/entities.json")
        self.assertEqual(sum(row["entityType"] == "RELATIONAL_DERIVED_STATE" for row in entities), 41)

    def test_legacy_relationships_are_not_required_to_have_bindings(self):
        relationships = read("data/relationships.json")["relationships"]
        _, bindings = xle.load_registries()
        bound = {row["relationshipId"] for row in bindings}
        self.assertEqual(len(relationships), 450)
        self.assertTrue(all(row["id"] not in bound or row["id"] == "REL-INS-040" for row in relationships))

    def test_shadow_gates_fail_closed_without_changing_authority(self):
        mapping, binding = self.mapping(), self.binding()
        base = {"sourceEntityId": "INS-051", "targetEntityId": "PSY-022", "sourceLevel": "INSTITUTION", "targetLevel": "PERSON", "implementationSatisfied": True, "actualExposureSatisfied": True, "perceptionSatisfied": True, "coverage": "COMPLETE", "coverageRuleSatisfied": True, "observedTemporalOrder": binding["temporalAlignment"]}
        with patch.object(xle, "load_registries", return_value=([mapping], [binding])):
            ready = xle.resolve_shadow_eligibility("REL-INS-040", mapping["mappingId"], "1.0.0", binding["bindingId"], "1.0.0", base)
            self.assertEqual(ready["eligibilityState"], "CROSS_LEVEL_READY_FOR_REVIEW")
            self.assertFalse(ready["causalEvidence"] or ready["executionAuthority"] or ready["feedsGraphConstruction"] or ready["feedsSimulation"] or ready["activationAuthorized"])
            self.assertEqual(ready["deterministicFingerprint"], xle.resolve_shadow_eligibility("REL-INS-040", mapping["mappingId"], "1.0.0", binding["bindingId"], "1.0.0", base)["deterministicFingerprint"])
            cases = [
                ({**base, "actualExposureSatisfied": False}, "BLOCKED_NO_EXPOSURE_ROUTE"),
                ({**base, "perceptionSatisfied": False}, "BLOCKED_PERCEPTION_ROUTE_REQUIRED"),
                ({**base, "coverage": "PARTIAL", "coverageRuleSatisfied": False}, "BLOCKED_PARTIAL_COVERAGE_UNBOUND"),
                ({**base, "observedTemporalOrder": list(reversed(binding["temporalAlignment"]))}, "BLOCKED_TEMPORAL_MISMATCH"),
                ({**base, "rdsSource": True}, "RESEARCH_NEEDED_BEFORE_MAPPING"),
            ]
            for context, state in cases:
                self.assertEqual(xle.resolve_shadow_eligibility("REL-INS-040", mapping["mappingId"], "1.0.0", binding["bindingId"], "1.0.0", context)["eligibilityState"], state)

        network = copy.deepcopy(mapping)
        network["routeType"] = "NETWORK_POSITION"
        network["networkStateRequirements"] = {"required": True, "description": "Exact governed state required"}
        with patch.object(xle, "load_registries", return_value=([network], [binding])):
            self.assertEqual(xle.resolve_shadow_eligibility("REL-INS-040", network["mappingId"], "1.0.0", binding["bindingId"], "1.0.0", base)["eligibilityState"], "BLOCKED_NETWORK_STATE_DEPENDENCY")


if __name__ == "__main__":
    unittest.main()
