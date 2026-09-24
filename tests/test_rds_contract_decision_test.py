"""WP-PSG-001 Stage C read-only RDS contract decision-test validation."""

import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/governance/post-scale-up/rds"
DOCS = ROOT / "docs/governance/post-scale-up/rds"
SCRIPT = ROOT / "scripts/rds_contract_decision_test.py"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


class RdsContractDecisionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = read(DATA / "rds-contract-test-cases.json")
        cls.prototype = read(DATA / "rds-profile-prototype.json")
        cls.migration = read(DATA / "rds-migration-classification.json")
        spec = importlib.util.spec_from_file_location("rds_contract_decision_test", SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_authoritative_scope_and_real_exemplars(self):
        self.assertEqual(self.cases["workPackageId"], "WP-PSG-001")
        self.assertEqual(self.cases["decisionPacketId"], "DP-PSG-001")
        self.assertEqual(self.cases["rootIssueId"], "ROOT-RDS-DEFINITION-DERIVATION-001")
        self.assertEqual({row["rdsId"] for row in self.cases["exemplars"]}, {
            "RDS-0006", "BIO-003", "CUL-088", "INS-039", "INS-103", "INF-010", "PSY-078",
        })
        self.assertTrue(all(not row["productionRecordChanged"] for row in self.cases["exemplars"]))

    def test_options_remain_advisory_and_hybrid_is_recommended(self):
        results = {row["option"]: row["result"] for row in self.cases["optionResults"]}
        self.assertEqual(results["A"], "REJECT_AS_UNIVERSAL_ARCHITECTURE")
        self.assertEqual(results["B"], "VIABLE_BUT_INCOMPLETE_ALONE")
        self.assertEqual(results["C"], "SAFE_FALLBACK_NOT_SUFFICIENT_ALONE")
        self.assertEqual(results["B_PLUS_C"], "RECOMMENDED_ADVISORY")
        self.assertEqual(self.prototype["governanceStatus"], "ADVISORY_NOT_GOVERNED")
        self.assertFalse(self.prototype["productionMutationAuthorized"])

    def test_positive_and_negative_cases_observe_expected_results(self):
        self.assertEqual(self.cases["summary"]["positiveCases"], 5)
        self.assertEqual(self.cases["summary"]["negativeCases"], 14)
        self.assertTrue(self.cases["summary"]["allExpectedOutcomesObserved"])
        for case in self.cases["testCases"]:
            observed = self.module.validate_request(self.prototype, case["request"])
            self.assertEqual(observed, case["result"], case["id"])
            self.assertEqual(observed["executableInPrototype"], case["expected"]["executableInPrototype"], case["id"])
            self.assertTrue(set(case["expected"]["requiredErrors"]).issubset(observed["errors"]), case["id"])

    def test_exact_network_metric_and_version_reproducibility(self):
        self.assertEqual(self.module.degree_centralization([3, 1, 1, 1]), 1.0)
        positives = {row["id"]: row for row in self.cases["testCases"]}
        self.assertTrue(positives["POS-001"]["result"]["executableInPrototype"])
        self.assertTrue(positives["POS-003"]["observation"]["sameRdsId"])
        self.assertTrue(positives["POS-003"]["observation"]["differentBindingId"])
        self.assertTrue(positives["POS-004"]["observation"]["version2NotSelected"])

    def test_consumer_contract_has_no_silent_resolution(self):
        contract = self.prototype["consumerContract"]
        self.assertEqual(set(contract["required"]), {
            "rdsId", "derivationProfileId", "derivationProfileVersion",
            "applicationBindingId", "applicationBindingVersion",
        })
        self.assertEqual(contract["zeroProfileBehavior"], "RDS_EXISTS_NON_EXECUTABLE")
        self.assertIn("LATEST_PROFILE", contract["prohibitedResolution"])
        negatives = {row["id"]: row for row in self.cases["testCases"]}
        self.assertIn("SILENT_LATEST_SELECTION_PROHIBITED", negatives["NEG-012"]["result"]["errors"])
        self.assertIn("NARRATIVE_OR_UNDERDEFINED_RDS_NON_EXECUTABLE", negatives["NEG-013"]["result"]["errors"])

    def test_profile_types_and_input_roles_preserve_scientific_distinctions(self):
        self.assertEqual(set(self.prototype["profileTypes"]), {
            "DERIVATION_PROFILE", "MEASUREMENT_PROFILE", "ESTIMATION_PROFILE",
        })
        allowed = {"CONSTITUENTS", "MEASUREMENT_INPUTS", "PARAMETERS", "NORMALIZERS", "BOUNDARY_INPUTS", "REFERENCE_VALUES", "EXTERNAL_CONTEXT"}
        for profile in self.prototype["profiles"]:
            for mapping in profile["constituentMapping"]:
                self.assertIn(mapping["role"], allowed)

    def test_definition_gate_is_firewalled_from_causal_source_gate(self):
        firewall = self.prototype["causalFirewall"]
        self.assertEqual(firewall["definitionGate"], "WP-PSG-001")
        self.assertEqual(firewall["causalSourceGate"], "WP-PSG-005")
        self.assertFalse(firewall["defaultCausalSourceEligible"])
        self.assertTrue(all(not row["causalSemantics"]["causalSourceEligible"] for row in self.prototype["profiles"]))
        negative = next(row for row in self.cases["testCases"] if row["id"] == "NEG-014")
        self.assertIn("CAUSAL_SOURCE_NOT_AUTHORIZED_BY_DERIVATION", negative["result"]["errors"])

    def test_all_41_rds_have_one_conservative_migration_classification(self):
        self.assertEqual(self.migration["totalRds"], 41)
        self.assertEqual(len(self.migration["records"]), 41)
        self.assertEqual(len({row["rdsId"] for row in self.migration["records"]}), 41)
        expected = {
            "READY_FOR_PROFILE_MATERIALIZATION": 1,
            "PROFILE_DEFINITION_REQUIRED": 13,
            "MULTIPLE_PROFILE_REVIEW_REQUIRED": 12,
            "LATENT_ESTIMATION_DESIGN_REQUIRED": 0,
            "NON_EXECUTABLE_PENDING_SCIENCE": 13,
            "BLOCKED_BY_ONTOLOGY": 2,
        }
        self.assertEqual(self.migration["counts"], expected)
        self.assertEqual(Counter(row["migrationCategory"] for row in self.migration["records"]), Counter({k:v for k,v in expected.items() if v}))
        self.assertFalse(self.migration["migrationAuthorized"])

    def test_existing_derivation_is_preserved_by_additive_mapping(self):
        compatibility = self.prototype["existingDerivationCompatibility"]
        self.assertEqual(compatibility["sourceId"], "DER-V1-SOC-F07-001")
        self.assertEqual(compatibility["strategy"], "ADDITIVE_PROFILE_WRAPPER_PRESERVE_ID_AND_LINEAGE")
        self.assertFalse(compatibility["rewriteRequired"])

    def test_protected_science_ontology_architecture_lifecycle_sources_and_validators(self):
        protected = self.cases["protection"]["productionHashes"]
        for relative, expected in protected.items():
            self.assertEqual(digest(ROOT / relative), expected, relative)
        self.assertFalse(self.cases["protection"]["productionMutationAuthorized"])

    def test_documents_and_structured_artifacts_exist(self):
        for name in ["rds-contract-test-cases.json", "rds-profile-prototype.json", "rds-migration-classification.json"]:
            self.assertTrue((DATA / name).is_file())
        for name in ["RDS_CONTRACT_DECISION_TEST.md", "RDS_CONTRACT_OPTION_COMPARISON.md", "RDS_PROFILE_IDENTITY_RULES.md", "RDS_MIGRATION_CLASSIFICATION.md"]:
            self.assertTrue((DOCS / name).is_file())

    def test_generator_is_deterministic(self):
        paths = sorted(DATA.glob("*.json")) + sorted(DOCS.glob("*.md"))
        before = {path: path.read_bytes().replace(b"\r\n", b"\n") for path in paths}
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
        after = {path: path.read_bytes().replace(b"\r\n", b"\n") for path in paths}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
