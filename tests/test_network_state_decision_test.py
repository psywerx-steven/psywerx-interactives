import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/governance/post-scale-up/network-state"
DOCS = ROOT / "docs/governance/post-scale-up/network-state"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


class NetworkStateDecisionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, "prototypes/network-state-transition-v1/build_decision_test.py"], cwd=ROOT, check=True, capture_output=True, text=True)
        cls.cases = read(DATA / "network-state-test-cases.json")
        cls.options = read(DATA / "network-state-option-results.json")
        cls.migration = read(DATA / "network-state-migration-classification.json")
        cls.handoffs = read(DATA / "network-state-handoffs.json")

    def test_existing_typed_operations_and_state_safety(self):
        self.assertEqual(set(self.cases["operationsVerified"]), {
            "ADD_NODE", "DEACTIVATE_NODE", "ADD_TIE", "REMOVE_TIE", "UPDATE_TIE_WEIGHT",
            "CHANGE_MEMBERSHIP", "CHANGE_BOUNDARY", "CHANGE_CONTACT_OPPORTUNITY", "CHANGE_ACCESS",
        })
        self.assertTrue(self.cases["rewiring"]["stateChanged"])
        receipt = self.cases["rewiring"]["receipt"]
        self.assertFalse(receipt["causalContribution"])
        self.assertFalse(receipt["empiricalEvidenceProduced"])
        self.assertEqual(receipt["ontologyRelationshipsEdited"], 0)
        self.assertTrue(self.cases["replay"]["exactState"])
        self.assertTrue(self.cases["branching"]["distinct"])

    def test_h12_and_h20_are_recalculation_not_causality(self):
        self.assertNotEqual(self.cases["rewiring"]["beforeDegree"], self.cases["rewiring"]["afterDegree"])
        self.assertEqual(self.cases["rewiring"]["h12Advisory"], "ARCHITECTURALLY_REPRESENTABLE_RECALCULATION_NOT_EMPIRICAL_CAUSAL_EFFECT")
        self.assertNotEqual(self.cases["nodeDeactivation"]["beforeFragmentation"], self.cases["nodeDeactivation"]["afterFragmentation"])
        self.assertEqual(self.cases["nodeDeactivation"]["h20Advisory"], "ARCHITECTURALLY_REPRESENTABLE_RECALCULATION_NOT_EMPIRICAL_CAUSAL_EFFECT")
        self.assertEqual(self.cases["firewalls"]["effectAssertionsCreated"], 0)
        self.assertFalse(self.cases["firewalls"]["causalSourceEligible"])

    def test_boundary_membership_opportunity_weight_and_observation(self):
        self.assertEqual(self.cases["boundary"]["changeClass"], "ANALYTIC_BOUNDARY_ONLY")
        self.assertTrue(self.cases["boundary"]["tieCorpusUnchanged"])
        self.assertTrue(self.cases["membership"]["tiesUnchanged"])
        self.assertTrue(self.cases["membership"]["degreeUnchanged"])
        self.assertTrue(self.cases["opportunityAndAccess"]["tiesUnchanged"])
        self.assertEqual(self.cases["weight"]["binaryMetricStatus"], "UNSUPPORTED_OR_INCOMPLETE")
        self.assertIn("explicitly binary", self.cases["weight"]["binaryMetricReason"])
        self.assertEqual(len(self.cases["observation"]["construction"]), 1)
        self.assertFalse(self.cases["observation"]["assumptions"]["realNetworkTruthClaim"])

    def test_rejections_and_non_effect_operation_reference(self):
        for key in ("staleState", "crossScenario", "retiredTieReuse"):
            self.assertTrue(self.cases["rejections"][key])
        ref = self.cases["operationReference"]
        self.assertEqual(ref["relation"], "REFERENCES_STIPULATED_OPERATION_NOT_EFFECT")
        self.assertFalse(ref["automaticExecution"])
        self.assertFalse(ref["empiricalConsequenceClaim"])

    def test_derivation_positive_control_preserved_and_inactive(self):
        control = self.cases["centralizationPositiveControl"]
        self.assertEqual(control["bindingId"], "DER-V1-SOC-F07-001")
        self.assertEqual(control["before"]["status"], "CALCULATED_SYNTHETIC")
        self.assertEqual(control["governance"]["lifecycleStatus"], "GOVERNED")
        self.assertEqual(control["governance"]["activationStatus"], "INACTIVE")
        self.assertFalse(control["causalSourceAuthorized"])

    def test_option_result_and_migration_accounting(self):
        self.assertEqual(self.options["options"]["B"]["result"], "REJECT_AS_REDUNDANT_FOR_CURRENT_SCOPE")
        self.assertEqual(self.options["options"]["A_PLUS_C"]["result"], "RECOMMENDED_ADVISORY")
        self.assertFalse(self.options["humanDecisionTaken"])
        self.assertEqual(self.migration["recordCount"], 6)
        self.assertEqual(sum(self.migration["counts"].values()), 6)
        self.assertEqual({r["id"] for r in self.migration["records"]}, {
            "HYP-SOC-F07-H12", "HYP-SOC-F07-H20", "ASTRA-SOC-LAYER-003",
            "REL-SOC-017", "REL-SOC-035", "REL-TEC-050",
        })

    def test_cross_level_handoffs_are_exact_and_nonexecuting(self):
        rows = self.handoffs["records"]
        self.assertEqual({r["relationshipId"] for r in rows}, {"REL-SOC-017", "REL-SOC-035", "REL-TEC-050"})
        self.assertTrue(all(r["productionRelationshipChanged"] is False for r in rows))
        self.assertFalse(self.handoffs["productionMutationAuthorized"])
        self.assertIn("causalSourceEligible=false", self.handoffs["wpPsg005"])

    def test_production_counts_and_protected_hashes(self):
        entities = read(ROOT / "data/entities.json")
        drivers = [e for e in entities if e["entityType"] == "DRIVER"]
        rds = [e for e in entities if e["entityType"] == "RELATIONAL_DERIVED_STATE"]
        self.assertEqual((len(drivers), len(rds)), (770, 41))
        protection = read(DATA / "protected-production-hashes.json")
        for relative, expected in protection["hashes"].items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, relative)

    def test_required_artifacts_and_no_production_schema(self):
        for name in (
            "NETWORK_STATE_DECISION_TEST.md", "NETWORK_STATE_OPTION_COMPARISON.md",
            "NETWORK_STATE_REPRESENTATION_CONTRACT.md", "NETWORK_STATE_OPERATION_TAXONOMY.md",
            "NETWORK_STATE_MIGRATION_CLASSIFICATION.md", "NETWORK_STATE_CONSUMER_IMPACT.md",
            "NETWORK_STATE_ARCHITECTURE_DECISION_PACKET.md",
        ):
            self.assertTrue((DOCS / name).is_file(), name)
        self.assertFalse((ROOT / "schemas/network-state-transition.schema.json").exists())
        self.assertFalse((ROOT / "data/network-state-transition-v1").exists())


if __name__ == "__main__":
    unittest.main()
