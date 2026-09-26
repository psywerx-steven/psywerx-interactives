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


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


class RdsComputationPhase0Tests(unittest.TestCase):
    def test_phase0_repository_is_empty_and_valid(self):
        status = rds.validate_repository()
        self.assertEqual(status, {"profiles": 0, "bindings": 0, "causalSourceEligible": 0, "activeSimulationFeeds": 0, "exactVersionOnly": True})

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


if __name__ == "__main__":
    unittest.main()
