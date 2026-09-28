import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTO = ROOT / "prototypes/rds-causal-source-v1"
sys.path.insert(0, str(PROTO))
from runtime import evaluate


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class RdsCausalSourceDecisionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = read("data/governance/post-scale-up/rds-causal-source/rds-source-inventory.json")
        cls.cases = read("data/governance/post-scale-up/rds-causal-source/rds-source-test-cases.json")
        cls.assessments = read("data/governance/post-scale-up/rds-causal-source/rds-source-case-assessments.json")
        cls.screen = read("data/governance/post-scale-up/rds-causal-source/rds-source-all-rds-screen.json")
        cls.handoffs = read("data/governance/post-scale-up/rds-causal-source/rds-source-handoffs.json")
        cls.research = read("data/governance/post-scale-up/rds-causal-source/rds-source-research-ledger.json")

    def test_inventory_is_deduplicated_and_mechanical(self):
        rows = self.inventory["routes"]
        self.assertEqual(len(rows), 38)
        self.assertEqual(len({x["relationshipId"] for x in rows}), 38)
        self.assertEqual(self.inventory["countsByRelationFamily"], {"CAUSAL": 23, "COMPOSITIONAL": 1, "DERIVATIONAL": 8, "SEMANTIC_MAPPING": 6})

    def test_all_41_rds_screened_once(self):
        rows = self.screen["records"]
        self.assertEqual(len(rows), 41)
        self.assertEqual(len({x["rdsId"] for x in rows}), 41)
        self.assertTrue(all(x["causalSourceEligible"] is False for x in rows))

    def test_root_blockers_and_social_sources_accounted_for(self):
        rows = self.assessments["cases"]
        self.assertEqual(len(rows), 15)
        self.assertEqual({"REL-BIO-001", "REL-CUL-042", "REL-INS-017", "REL-INS-036"} - {x["relationshipId"] for x in rows}, set())
        social = {"SOC-024", "SOC-041", "SOC-052", "SOC-053", "SOC-054", "SOC-055", "SOC-056", "SOC-074", "SOC-076", "SOC-096"}
        self.assertEqual(social, {x["sourceId"] for x in rows if x["sourceId"].startswith("SOC-")})
        self.assertEqual(sum(x["sourceId"] == "SOC-096" for x in rows), 2)
        self.assertEqual(set(self.assessments["rootBlockers"]), {
            "ASTRA-BIO-LAYER-001", "ASTRA-CUL-LAYER-001", "ASTRA-INS-LAYER-001",
            "ASTRA-INS-LAYER-002", "ASTRA-SOC-LAYER-001",
        })

    def test_reusable_gate_controls(self):
        for case in self.cases["cases"]:
            self.assertEqual(evaluate(case["input"])["advisoryStatus"], case["expected"], case["caseId"])
            self.assertFalse(case["result"]["causalSourceEligible"])
            self.assertFalse(case["result"]["executionAuthorized"])
            self.assertFalse(case["result"]["activationAuthorized"])

    def test_derivation_and_profile_firewalls(self):
        by_id = {x["caseId"]: x for x in self.cases["cases"]}
        self.assertEqual(by_id["PURE_DERIVATION"]["result"]["advisoryStatus"], "DERIVATION_ONLY")
        self.assertEqual(by_id["COMPUTABLE_NOT_CAUSAL"]["result"]["advisoryStatus"], "DERIVATION_ONLY")
        self.assertEqual(by_id["PROFILE_ABSENT_SCIENCE_COHERENT"]["result"]["advisoryStatus"], "ELIGIBLE_FOR_INDEPENDENT_CAUSAL_REVIEW")
        self.assertFalse(by_id["PROFILE_ABSENT_SCIENCE_COHERENT"]["result"]["computationallyExecutable"])

    def test_multiple_versions_and_target_contamination(self):
        by_id = {x["caseId"]: x for x in self.cases["cases"]}
        expected = {key: value["result"]["advisoryStatus"] for key, value in by_id.items()}
        self.assertEqual(expected["RATIO_MULTIPLE_VERSIONS"], "BLOCKED_MULTIPLE_VERSIONS")
        self.assertEqual(expected["DISTANCE_MULTIPLE_VERSIONS"], "BLOCKED_MULTIPLE_VERSIONS")
        self.assertEqual(expected["TARGET_CONTAMINATION"], "BLOCKED_TARGET_CONTAMINATION")
        ratio = by_id["RATIO_MULTIPLE_VERSIONS"]["fixture"]
        self.assertEqual(ratio["versionA"]["ratio"], ratio["versionB"]["ratio"])
        self.assertNotEqual(ratio["versionA"]["staff"], ratio["versionB"]["staff"])
        distance = by_id["DISTANCE_MULTIPLE_VERSIONS"]["fixture"]
        self.assertEqual(distance["euclideanDistanceA"], distance["euclideanDistanceB"])
        self.assertNotEqual(distance["profileA"], distance["profileB"])

    def test_network_contribution_cross_level_and_time_fail_closed(self):
        by_id = {x["caseId"]: x for x in self.cases["cases"]}
        expected = {key: value["result"]["advisoryStatus"] for key, value in by_id.items()}
        self.assertEqual(expected["NETWORK_MANY_TO_ONE"], "BLOCKED_NETWORK_STATE")
        self.assertEqual(expected["CONSTITUENT_DOUBLE_COUNT"], "BLOCKED_CONTRIBUTION_OVERLAP")
        self.assertEqual(expected["CROSS_LEVEL_NO_MAPPING"], "BLOCKED_EXPOSURE_MAPPING")
        self.assertEqual(expected["TEMPORAL_ORDER_MISSING"], "BLOCKED_TEMPORAL_ORDER")
        network = by_id["NETWORK_MANY_TO_ONE"]["fixture"]
        self.assertEqual(network["densityA"], network["densityB"])
        self.assertNotEqual(network["graphAEdges"], network["graphBEdges"])

    def test_source_class_relationship_evidence_and_execution_are_separate(self):
        by_id = {x["caseId"]: x for x in self.cases["cases"]}
        result = by_id["COHERENT_SOURCE_INSUFFICIENT_RELATIONSHIP_EVIDENCE"]["result"]
        self.assertTrue(result["scientificSourceClassCoherent"])
        self.assertFalse(result["relationshipEvidenceAdequate"])
        self.assertTrue(result["computationallyExecutable"])
        self.assertFalse(result["causalSourceEligible"])

    def test_deep_research_ledger_is_complete_and_planning_only(self):
        reviews = self.research["caseReviews"]
        self.assertEqual({x["caseId"] for x in reviews}, {
            "BIO-003_REL-BIO-001", "CUL-088_REL-CUL-042", "INS-039_REL-INS-017",
            "INS-103_REL-INS-036", "SOC-053_REL-SOC-035", "SOC-074_REL-SOC-046",
        })
        required = {
            "question", "sourceRdsId", "targetId", "causalContrast", "unitOfAnalysis",
            "timeScope", "sourceLevel", "targetLevel", "candidateMechanism", "constituents",
            "currentContributionRoutes", "currentEvidence", "newPlanningSources",
            "sourceQualityAccessDepth", "causalDesignClass", "supportingFindings",
            "nullOrContraryFindings", "limitations", "remainingUncertainty", "decisionTestResult",
        }
        self.assertTrue(all(required <= set(review) for review in reviews))
        self.assertEqual(self.research["newProductionSourcesRegistered"], 0)

    def test_native_derivation_contribution_control_is_mechanically_inventoried(self):
        row = next(x for x in self.screen["records"] if x["rdsId"] == "RDS-0006")
        self.assertEqual(row["existingContributionControl"]["contributionIdentity"], "CONTRIB-SOC-F07-DEGREE-CENTRALIZATION")
        self.assertEqual(row["existingContributionControl"]["contributionPolicy"], "RECALCULATION_ONLY_NO_CAUSAL_SUM")

    def test_positive_context_and_alternate_abstraction(self):
        expected = {x["caseId"]: x["result"]["advisoryStatus"] for x in self.cases["cases"]}
        self.assertEqual(expected["CONTEXTUAL_POSITIVE"], "ELIGIBLE_FOR_CONTEXTUAL_CAUSAL_REVIEW")
        self.assertEqual(expected["ALTERNATE_ABSTRACTION"], "ALTERNATE_ABSTRACTION_ONLY")

    def test_d10_and_effectassertion_firewalls(self):
        causal = [x for x in self.inventory["routes"] if x["relationFamily"] == "CAUSAL"]
        self.assertTrue(all(x["d10Gate"] in {"HEIGHTENED_RDS_TO_DRIVER_REVIEW", "EXCEPTIONAL_RDS_TO_RDS_REVIEW"} for x in causal))
        catalog = read("data/actions-events-v1/catalog.json")
        entity = {x["id"]: x for x in read("data/entities.json")}
        self.assertFalse(any(entity.get(x.get("targetId"), {}).get("entityType") == "RELATIONAL_DERIVED_STATE" for x in catalog["effectAssertions"]))

    def test_protected_hashes_and_counts(self):
        for path, expected in self.handoffs["protectedHashes"].items():
            actual = hashlib.sha256((ROOT / path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
            self.assertEqual(actual, expected, path)
        entities = read("data/entities.json")
        self.assertEqual(sum(x.get("entityType") == "DRIVER" for x in entities), 770)
        self.assertEqual(sum(x.get("entityType") == "RELATIONAL_DERIVED_STATE" for x in entities), 41)
        self.assertEqual(self.handoffs["causalSourceEligibilityChanges"], 0)

    def test_deterministic_regeneration(self):
        tracked = ["data/governance/post-scale-up/rds-causal-source", "docs/governance/post-scale-up/rds-causal-source"]
        subprocess.run([sys.executable, str(PROTO / "build_decision_test.py")], cwd=ROOT, check=True, capture_output=True)
        result = subprocess.run(["git", "diff", "--exit-code", "--", *tracked], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
