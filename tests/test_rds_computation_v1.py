"""Bounded production RDS computation architecture and RDS-0006 shadow tests."""

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import rds_computation_v1 as rds
import relational_state_fixtures as fixtures
import relational_state_v1 as legacy_runtime
import materialize_soc_f07_completion as completion


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


class RdsComputationProductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.legacy_binding = completion.binding()
        cls.authorizations = [completion.authorization([cls.legacy_binding])]

    def shadow_request(self, state=None):
        state = state or fixtures.state()
        legacy_request = fixtures.request(state, "FREEMAN_DEGREE_CENTRALIZATION", self.legacy_binding)
        values = legacy_request["collection"]["values"]
        request = {
            "schemaVersion": "1.0.0", "requestId": "SHADOW-RDS-0006-TEST", "rdsId": "RDS-0006",
            "profileId": rds.RDS_0006_PROFILE_ID, "profileVersion": "1.0.0",
            "bindingId": rds.RDS_0006_BINDING_ID, "bindingVersion": "1.0.0",
            "inputs": {"SOC-049": {"definitionHash": self.legacy_binding["inputContract"]["inputEntity"]["definitionHash"], "valueHash": rds.digest(values), "value": values}},
            "parameters": {"metricVariant": self.legacy_binding["metricVariant"], "normalization": self.legacy_binding["normalization"]},
            "causalSourceRequested": False, "simulationFeedRequested": False,
        }
        return state, legacy_request, request

    def test_phase1_repository_has_only_bounded_wrapper(self):
        status = rds.validate_repository()
        self.assertEqual(status, {"profiles": 1, "bindings": 1, "causalSourceEligible": 0, "activeSimulationFeeds": 0, "exactVersionOnly": True})
        profiles, bindings = rds.load_registries()
        self.assertEqual({row["rdsId"] for row in profiles + bindings}, {"RDS-0006"})
        self.assertEqual(profiles[0]["executionMode"], "SHADOW_ONLY")

    def test_five_production_schemas_validate(self):
        self.assertEqual(set(rds.validators()), {"profile", "binding", "request", "provenance", "eligibility"})

    def test_zero_profile_means_non_executable(self):
        request = {"schemaVersion": "1.0.0", "requestId": "TEST", "rdsId": "CUL-088", "profileId": "NONE", "profileVersion": "1.0.0", "bindingId": "NONE", "bindingVersion": "1.0.0", "inputs": {}, "parameters": {}, "causalSourceRequested": False, "simulationFeedRequested": False}
        self.assertEqual(rds.resolve_execution_eligibility(request, "0" * 64)["state"], "NON_EXECUTABLE_NO_PROFILE")

    def test_implicit_version_selectors_fail_closed(self):
        base = {"schemaVersion": "1.0.0", "requestId": "TEST", "rdsId": "RDS-0006", "profileId": "NONE", "profileVersion": "1.0.0", "bindingId": "NONE", "bindingVersion": "1.0.0", "inputs": {}, "parameters": {}, "causalSourceRequested": False, "simulationFeedRequested": False}
        for selector in rds.FORBIDDEN_SELECTORS:
            request = {**base, "profileVersion": selector}
            self.assertEqual(rds.resolve_execution_eligibility(request, "0" * 64)["state"], "NON_EXECUTABLE_VERSION_MISMATCH")

    def test_causal_firewall_has_no_bypass(self):
        with self.assertRaises(rds.ValidationError):
            rds.validate_causal_firewall({"causalSourceEligible": False}, True)

    def test_human_decision_is_bounded(self):
        decision = read(ROOT / "data/governance/post-scale-up/rds/rds-production-implementation-decision-001.json")
        self.assertEqual(decision["phase1RdsIds"], ["RDS-0006"])
        self.assertEqual(decision["remainingRdsAuthorized"], 0)
        self.assertFalse(decision["causalSourceAuthorization"])
        self.assertFalse(decision["activeSimulationFeedAuthorization"])

    def test_rds0006_shadow_numeric_provenance_and_lineage_equivalence(self):
        state, legacy_request, request = self.shadow_request()
        receipt = rds.shadow_execute_rds0006(request, legacy_request, state, self.legacy_binding, self.authorizations)
        legacy = legacy_runtime.calculate(legacy_request, state, self.legacy_binding, self.authorizations)
        self.assertAlmostEqual(receipt["output"], 2 / 3)
        self.assertEqual(receipt["output"], legacy["value"])
        self.assertEqual(receipt["legacyReceiptHash"], legacy["receiptHash"])
        self.assertEqual(receipt["legacyDerivationId"], "DER-V1-SOC-F07-001")
        self.assertTrue(all(receipt["equivalence"].values()))
        self.assertFalse(receipt["feedsActiveSimulation"])
        self.assertFalse(receipt["causalSourceAuthorized"])

    def test_shadow_fingerprint_is_deterministic(self):
        state, legacy_request, request = self.shadow_request()
        first = rds.shadow_execute_rds0006(request, legacy_request, state, self.legacy_binding, self.authorizations)
        second = rds.shadow_execute_rds0006(copy.deepcopy(request), copy.deepcopy(legacy_request), copy.deepcopy(state), copy.deepcopy(self.legacy_binding), copy.deepcopy(self.authorizations))
        self.assertEqual(first, second)

    def test_shadow_rejects_input_or_legacy_drift(self):
        state, legacy_request, request = self.shadow_request()
        bad_input = copy.deepcopy(request)
        bad_input["inputs"]["SOC-049"]["valueHash"] = "0" * 64
        with self.assertRaises(rds.ValidationError):
            rds.shadow_execute_rds0006(bad_input, legacy_request, state, self.legacy_binding, self.authorizations)
        bad_legacy = copy.deepcopy(self.legacy_binding)
        bad_legacy["scopeLimitations"].append("unauthorized drift")
        with self.assertRaises(rds.ValidationError):
            rds.shadow_execute_rds0006(request, legacy_request, state, bad_legacy, self.authorizations)

    def test_wrapper_preserves_exact_legacy_record(self):
        catalog = read(ROOT / "data/relational-state-v1/catalog.json")
        legacy = next(row for row in catalog["bindings"] if row["id"] == "DER-V1-SOC-F07-001")
        self.assertEqual(rds.digest(legacy), "609f164d5bcd45cb7372f51374961f365780f2ebce7693e83f7b2db7d6e2dfbf")
        profile = rds.load_registries()[0][0]
        self.assertEqual(profile["provenance"]["legacyRecordHash"], rds.digest(legacy))
        self.assertEqual(profile["provenance"]["legacyContributionPolicy"], "RECALCULATION_ONLY_NO_CAUSAL_SUM")

    def test_other_forty_rds_remain_unprofiled(self):
        migration = read(ROOT / "data/governance/post-scale-up/rds/rds-migration-dry-run.json")
        rds_ids = {row["rdsId"] for row in migration["records"]}
        self.assertEqual(len(rds_ids), 41)
        profiled = {row["rdsId"] for row in rds.load_registries()[0]}
        self.assertEqual(profiled, {"RDS-0006"})
        self.assertEqual(len(rds_ids - profiled), 40)
        closeout = read(ROOT / "data/governance/post-scale-up/rds/rds-0006-phase1-compatibility.json")
        self.assertEqual(closeout["remainingRdsChanged"], 0)
        self.assertEqual(closeout["rollbackState"], "UNCHANGED_LEGACY_DERIVATION_ONLY")


if __name__ == "__main__":
    unittest.main()
