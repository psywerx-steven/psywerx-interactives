import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/governance/post-scale-up/contribution"
DOCS = ROOT / "docs/governance/post-scale-up/contribution"
MODULE = ROOT / "prototypes/contribution-identity-v1/contribution_control.py"
spec = importlib.util.spec_from_file_location("contribution_control_test", MODULE)
cc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cc)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


class ContributionIdentityDecisionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, "prototypes/contribution-identity-v1/build_decision_test.py"], cwd=ROOT, check=True, capture_output=True, text=True)
        cls.cases = read(DATA / "contribution-test-cases.json")
        cls.inventory = read(DATA / "contribution-inventory.json")
        cls.duplicates = read(DATA / "contribution-duplicate-groups.json")
        cls.collisions = read(DATA / "contribution-collision-audit.json")
        cls.consumers = read(DATA / "contribution-consumer-impact.json")
        cls.options = read(DATA / "contribution-option-results.json")
        cls.handoffs = read(DATA / "contribution-handoffs.json")

    def test_required_artifacts_exist(self):
        docs = {
            "CONTRIBUTION_DECISION_TEST.md", "CONTRIBUTION_OPTION_COMPARISON.md",
            "CONTRIBUTION_IDENTITY_CONTRACT.md", "CONTRIBUTION_POLICY_CONTRACT.md",
            "CONTRIBUTION_INVENTORY.md", "CONTRIBUTION_CONSUMER_IMPACT.md",
            "CONTRIBUTION_ID_COLLISION_AUDIT.md", "CONTRIBUTION_ARCHITECTURE_DECISION_PACKET.md",
        }
        data = {
            "contribution-test-cases.json", "contribution-inventory.json",
            "contribution-duplicate-groups.json", "contribution-collision-audit.json",
            "contribution-consumer-impact.json", "contribution-option-results.json",
            "contribution-handoffs.json", "protected-production-hashes.json",
        }
        self.assertTrue(all((DOCS / x).exists() for x in docs))
        self.assertTrue(all((DATA / x).exists() for x in data))

    def test_relationship_effect_assertion_same_contribution(self):
        primary = self.cases["primaryDuplicateControl"]
        self.assertEqual(primary["groupId"], "CONTRIB-PSY-LAYER-REPETITION-001")
        self.assertTrue(primary["sameContribution"])
        self.assertTrue(primary["bothInactive"])
        self.assertFalse(primary["relationshipHasNativeContributionField"])
        self.assertEqual(primary["requiredResult"], "SELECT_ONE_REPRESENTATION")
        self.assertEqual(self.cases["numeric"]["naiveDuplicateSum"], .4)
        self.assertEqual(self.cases["numeric"]["duplicateSafeSum"], .2)
        self.assertAlmostEqual(self.cases["numeric"]["correctIndependentTotal"], .3)

    def test_negative_controls_do_not_overcollapse(self):
        controls = self.cases["negativeControls"]
        self.assertEqual(controls["sameInterventionDifferentEffects"]["result"], "DISTINCT_CONTRIBUTIONS_CONFIRMED")
        self.assertEqual(controls["sameEvidenceDifferentEffects"]["result"], "DISTINCT_CONTRIBUTIONS_EVIDENCE_LINEAGE_SEPARATE")
        self.assertGreaterEqual(len(controls["sameTargetDifferentCauses"]["records"]), 3)
        self.assertGreaterEqual(len({x["contributionId"] for x in controls["sameTargetDifferentCauses"]["records"]}), 3)

    def test_aggregate_and_state_fail_closed(self):
        self.assertEqual(self.cases["numeric"]["aggregateUnresolved"], "BLOCK_PENDING_INDEPENDENCE")
        self.assertEqual(self.cases["numeric"]["stateDeltaPlusDerivedMetricCausalSum"], 0)
        self.assertFalse(self.cases["boundaries"]["derivationCreatesCausality"])
        self.assertFalse(self.cases["boundaries"]["stateRecalculationCreatesCausality"])
        self.assertFalse(self.cases["boundaries"]["crossLevelMappingCountsAsContribution"])
        classes = {x["classification"] for x in self.duplicates["groups"]}
        self.assertIn("POTENTIAL_DUPLICATE", classes)
        self.assertIn("DERIVATION_LINEAGE_STATE_RECALCULATION", classes)

    def test_no_silent_selection_or_floating_membership(self):
        group = copy.deepcopy(self.cases["groups"][0])
        with self.assertRaises(cc.ValidationError):
            cc.resolve_contribution_policy([group])
        self.assertEqual(self.cases["numeric"]["missingExplicitSelection"], "BLOCK_EXPLICIT_SELECTION_REQUIRED")
        group["groupVersion"] = "LATEST"
        with self.assertRaises(cc.ValidationError):
            cc.validate_group(group)

    def test_version_hash_and_registry_collision_validation(self):
        group = copy.deepcopy(self.cases["groups"][0])
        records = {(m["recordClass"], m["recordId"], m["recordVersion"]): m["recordHash"] for m in group["memberRepresentations"]}
        self.assertTrue(cc.validate_registry([group], records))
        wrong = dict(records)
        key = next(iter(wrong))
        wrong[key] = "0" * 64
        with self.assertRaises(cc.ValidationError):
            cc.validate_registry([group], wrong)
        with self.assertRaises(cc.ValidationError):
            cc.validate_registry([group, group], records)

        contradictory = copy.deepcopy(group)
        contradictory["memberRepresentations"][1]["identityAlignmentKey"] = "different-scope"
        with self.assertRaises(cc.ValidationError):
            cc.validate_group(contradictory)

    def test_group_has_no_causal_or_lifecycle_authority(self):
        group = copy.deepcopy(self.cases["groups"][0])
        for field in ("causalAuthority", "hasWeight", "hasPolarity", "hasActivation", "hasScientificLifecycle"):
            changed = copy.deepcopy(group)
            changed[field] = True
            with self.assertRaises(cc.ValidationError):
                cc.validate_group(changed)

    def test_blocker_collision_is_disambiguated_without_rewrite(self):
        row = self.collisions["governanceBlockerIdCollisions"][0]
        self.assertEqual(row["identifier"], "BLK-PSY-003")
        self.assertEqual(row["finding"], "ACCIDENTAL_HISTORICAL_IDENTIFIER_REUSE_NOT_INTENTIONAL_MERGE")
        self.assertNotEqual(row["useA"]["planningHandle"], row["useB"]["planningHandle"])
        self.assertEqual(row["useB"]["authority"], "AUTHORITATIVE_FOR_WP-PSG-004")
        self.assertFalse(self.collisions["productionIdentifiersChanged"])

    def test_inventory_and_consumer_findings(self):
        totals = self.inventory["totals"]
        self.assertEqual(totals["productionEffectAssertions"], 11)
        self.assertEqual(totals["effectAssertionsWithContribution"], 11)
        self.assertEqual(totals["productionRelationshipV1Records"], 8)
        self.assertEqual(totals["relationshipRecordsWithNativeContributionField"], 0)
        classes = {x["classification"] for x in self.consumers["records"]}
        self.assertIn("CLASS_SPECIFIC_AWARENESS", classes)
        self.assertIn("NO_CONTRIBUTION_AWARENESS", classes)
        self.assertIn("UNKNOWN", classes)

    def test_option_result_is_advisory_and_wp5_not_started(self):
        self.assertEqual(self.options["options"]["A_PLUS_B_PLUS_C"]["result"], "RECOMMENDED_ADVISORY_BOUNDED")
        self.assertFalse(self.options["humanDecisionTaken"])
        self.assertEqual(self.handoffs["wpPsg005"]["status"], "NOT_STARTED")
        self.assertFalse(self.handoffs["wpPsg005"]["adjudicationPerformed"])
        self.assertEqual(self.cases["boundaries"]["totalEffectLocalLinkReconciliation"], "EXPLICIT_PATHWAY_RELATION_REQUIRED_NO_GRAPH_INFERENCE")
        self.assertIn("NEVER_FLATTEN", self.cases["boundaries"]["interaction"])

    def test_production_counts_and_hashes_unchanged(self):
        entities = read(ROOT / "data/entities.json")
        self.assertEqual(sum(x.get("entityType") == "DRIVER" for x in entities), 770)
        self.assertEqual(len(read(ROOT / "data/relational-derived-states.json")), 41)
        protected = read(DATA / "protected-production-hashes.json")
        self.assertEqual(protected["baseline"], "24a406468180a35af5beb74df427053cc1536090")
        for relative, expected in protected["files"].items():
            self.assertEqual(file_hash(ROOT / relative), expected, relative)
        self.assertFalse(protected["productionMutationAuthorized"])


if __name__ == "__main__":
    unittest.main()
