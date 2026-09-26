"""Read-only WP-PSG-002 decision-test and protected-science gates."""

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTO = ROOT / "prototypes/cross-level-exposure-v1"
sys.path.insert(0, str(PROTO))
import contract

DATA = ROOT / "data/governance/post-scale-up/cross-level"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


class CrossLevelDecisionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = read(DATA / "cross-level-test-cases.json")
        cls.prototype = read(DATA / "cross-level-mapping-prototype.json")
        cls.migration = read(DATA / "cross-level-migration-classification.json")
        cls.consumers = read(DATA / "cross-level-consumer-impact.json")
        cls.protected = read(DATA / "protected-production-hashes.json")
        cls.relationships = {row["id"]: row for row in read(ROOT / "data/relationships.json")["relationships"]}

    def test_authoritative_queue_reconciliation(self):
        social = next(row for row in read(ROOT / "data/candidates/actions-events-v1/SOCIAL_LAYER/astra-escalation-queue.json") if row["id"] == "ASTRA-SOC-LAYER-002")["affectedRecords"]
        institutional = next(row for row in read(ROOT / "data/candidates/actions-events-v1/INSTITUTIONAL_STRUCTURAL_LAYER/astra-escalation-queue.json") if row["id"] == "ASTRA-INS-LAYER-003")["affectedRecords"]
        self.assertEqual((len(social), len(institutional), len(set(social) & set(institutional)), len(set(social) | set(institutional))), (20, 21, 3, 38))
        self.assertEqual({row["relationshipId"] for row in self.migration["records"]}, set(social) | set(institutional))

    def test_every_affected_record_classified_once_without_mutation(self):
        rows = self.migration["records"]
        self.assertEqual(len(rows), 38)
        self.assertEqual(len({row["relationshipId"] for row in rows}), 38)
        self.assertTrue(all(not row["productionMutationAuthorized"] for row in rows))
        self.assertEqual(sum(self.migration["counts"].values()), 38)
        self.assertEqual(self.migration["counts"], {
            "EXISTING_BRIDGE_SUFFICIENT": 5, "MAPPING_LIKELY_REQUIRED": 13,
            "METADATA_ONLY_MAY_SUFFICE": 2, "NETWORK_STATE_DEPENDENCY": 3,
            "CONSTRUCT_ONTOLOGY_DEPENDENCY": 0,
            "NO_CROSS_LEVEL_PROBLEM_AFTER_REVIEW": 13, "RESEARCH_NEEDED_BEFORE_MAPPING": 2,
        })

    def test_all_architecture_cases_fail_or_pass_as_declared(self):
        self.assertEqual(len(self.cases["cases"]), 15)
        for row in self.cases["cases"]:
            with self.subTest(row["caseId"]):
                self.assertEqual(row["actualResult"]["state"], row["expectedState"])
                self.assertFalse(row["actualResult"]["scientificGovernanceConferred"])
                self.assertFalse(row["actualResult"]["executionAuthorized"])
                self.assertFalse(row["actualResult"]["lifecycleChanged"])
                self.assertFalse(row["actualResult"]["causalEvidenceCreated"])

    def test_required_positive_and_negative_patterns_present(self):
        states = {row["caseId"]: row["actualResult"]["state"] for row in self.cases["cases"]}
        self.assertEqual(states["NEG-POLICY-NOT-IMPLEMENTED"], "BLOCKED_NO_IMPLEMENTATION_ROUTE")
        self.assertEqual(states["NEG-ELIGIBLE-NO-RECEIPT"], "BLOCKED_NO_EXPOSURE_ROUTE")
        self.assertEqual(states["NEG-PERCEPTION-REQUIRED"], "BLOCKED_PERCEPTION_ROUTE_REQUIRED")
        self.assertEqual(states["NEG-ECOLOGICAL-CORRELATION"], "RESEARCH_NEEDED")
        self.assertEqual(states["SYN-NETWORK-MISSING-STATE"], "BLOCKED_NETWORK_STATE_DEPENDENCY")
        self.assertEqual(states["REAL-SAME-LEVEL-CONTROL"], "SAME_LEVEL_NOT_APPLICABLE")
        self.assertEqual(states["SYN-OBJECTIVE-NO-PERCEPTION"], "CROSS_LEVEL_READY")
        self.assertEqual(states["NEG-PARTIAL-COVERAGE-UNBOUND"], "BLOCKED_INCOMPLETE_MAPPING")
        self.assertEqual(states["SYN-PARTIAL-COVERAGE-BOUND"], "CROSS_LEVEL_READY")
        self.assertEqual(states["SYN-DISCRETE-ASSIGNMENT"], "CROSS_LEVEL_READY")

    def test_mapping_is_neither_causal_node_nor_evidence(self):
        semantics = self.prototype["mappingSemantics"]
        self.assertFalse(semantics["isCausalNode"])
        self.assertFalse(semantics["isEvidence"])
        self.assertFalse(semantics["hasWeight"])
        self.assertFalse(semantics["hasLifecycle"])
        for row in self.prototype["mappings"]:
            self.assertFalse(row["causalEvidence"])
            self.assertFalse(row["executionAuthority"])
            self.assertFalse(contract.FORBIDDEN_MAPPING_FIELDS & set(row))

    def test_exact_versions_and_identity_mismatches_fail(self):
        mapping = copy.deepcopy(self.prototype["mappings"][0])
        relationship = self.relationships[mapping["relationshipId"]]
        self.assertTrue(contract.validate_mapping(mapping, relationship))
        mapping["mappingVersion"] = "LATEST"
        with self.assertRaises(contract.ContractError):
            contract.validate_mapping(mapping, relationship)
        mapping = copy.deepcopy(self.prototype["mappings"][0])
        mapping["sourceEntityId"] = "WRONG"
        with self.assertRaises(contract.ContractError):
            contract.validate_mapping(mapping, relationship)
        mapping = copy.deepcopy(self.prototype["mappings"][0])
        mapping["edgeWeight"] = 0.5
        with self.assertRaises(contract.ContractError):
            contract.validate_mapping(mapping, relationship)

    def test_level_and_route_taxonomies_are_bounded(self):
        self.assertEqual(set(self.prototype["levels"]), contract.LEVELS)
        self.assertEqual(set(self.prototype["routes"]), contract.ROUTES)
        self.assertIn("AMBIENT_CONTEXT", contract.ROUTES)
        self.assertIn("NETWORK_POSITION", contract.ROUTES)
        self.assertIn("PERSON", contract.LEVELS)
        self.assertIn("INSTITUTION", contract.LEVELS)
        finding = self.prototype["levelDeclarationFinding"]
        self.assertEqual(finding["legacyRelationshipLevelsPresent"] + finding["legacyRelationshipLevelsMissing"], 38)
        self.assertFalse(finding["entityMetadataSupportsSafeInference"])

    def test_bounded_direction_is_governed_without_production_authority(self):
        options = {row["option"]: row["result"] for row in self.prototype["optionResults"]}
        self.assertEqual(options["A+B+C"], "RECOMMENDED_BOUNDED_HYBRID")
        self.assertEqual(options["B"], "REJECT_AS_UNIVERSAL_REQUIREMENT")
        decision = read(DATA / "cross-level-architecture-decision-001.json")
        self.assertEqual(decision["decisionId"], "GOV-CROSS-LEVEL-EXPOSURE-001-2026-09-26")
        self.assertEqual(decision["decisionOutcome"], "APPROVED_BOUNDED_A_PLUS_B_PLUS_C_DIRECTION")
        self.assertEqual(decision["authorizedActivities"], [
            "architecture direction",
            "non-production schema prototyping",
            "non-production validator prototyping",
            "test-only mapping and eligibility experiments",
            "read-only migration and consumer-impact planning",
        ])
        self.assertFalse(any(decision["approvedDirection"]["mappingConveys"].values()))
        self.assertEqual(decision["productionImplementationStatus"], "NOT_AUTHORIZED_NOT_STARTED")
        self.assertFalse(decision["productionState"]["architectureImplemented"])
        self.assertEqual(decision["productionState"]["relationshipsChanged"], 0)
        packets = read(ROOT / "data/governance/post-scale-up/decision-packets.json")
        packet = next(row for row in packets["decisionPackets"] if row["decisionPacketId"] == "DP-PSG-002")
        self.assertEqual(packet["humanDecisionStatus"], "HUMAN_APPROVED_BOUNDED_DIRECTION")
        self.assertEqual(packet["stageCDecisionTestStatus"], "COMPLETE_READ_ONLY_RECOMMENDATION")
        self.assertEqual(packet["humanDecisionId"], "GOV-CROSS-LEVEL-EXPOSURE-001-2026-09-26")
        self.assertEqual(packet["approvedOption"], "BOUNDED_A_PLUS_B_PLUS_C")
        self.assertIn("production migration", packet["authorizationBoundary"])
        packages = read(ROOT / "data/governance/post-scale-up/work-packages.json")
        package = next(row for row in packages["workPackages"] if row["workPackageId"] == "WP-PSG-002")
        self.assertEqual(package["stages"]["D_humanGovernanceDecision"], "COMPLETE_BOUNDED_DIRECTION_APPROVED")
        self.assertEqual(package["prototypeImplementationAuthorization"], "AUTHORIZED_NON_PRODUCTION_ONLY")
        self.assertEqual(package["productionImplementationStatus"], "NOT_AUTHORIZED_NOT_STARTED")
        self.assertEqual(package["stages"]["E_implementation"], "COMPLETE_NON_PRODUCTION_REFERENCE_PROTOTYPE")
        self.assertEqual(package["stages"]["F_migrationRevalidation"], "DRY_RUN_ONLY_COMPLETE_PRODUCTION_MIGRATION_NOT_AUTHORIZED")

    def test_consumers_remain_unintegrated(self):
        self.assertFalse(self.consumers["productionIntegrationAuthorized"])
        self.assertTrue(all(row["classification"] in {"NO_CURRENT_EXECUTION_IMPACT", "DISPLAY_ONLY", "VALIDATION_AWARE", "VALIDATION_AWARE_AND_MIGRATION_REQUIRED", "MIGRATION_REQUIRED", "UNKNOWN_REQUIRES_REVIEW"} for row in self.consumers["consumers"]))
        self.assertFalse((ROOT / "schemas/cross-level-exposure-mapping.schema.json").exists())
        self.assertFalse((ROOT / "data/cross-level-exposure-v1").exists())

    def test_protected_production_hashes_unchanged(self):
        for relative, expected in self.protected["files"].items():
            with self.subTest(relative):
                canonical = (ROOT / relative).read_bytes().replace(b"\r\n", b"\n")
                actual = hashlib.sha256(canonical).hexdigest()
                self.assertEqual(actual, expected)

    def test_rds_causal_firewall_unchanged(self):
        profiles = read(ROOT / "data/rds-computation-v1/profiles.json")["profiles"]
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0]["rdsId"], "RDS-0006")
        self.assertFalse(profiles[0]["causalSourceEligible"])
        self.assertEqual(profiles[0]["causalSourceGate"], "WP-PSG-005_REQUIRED")


if __name__ == "__main__":
    unittest.main()
