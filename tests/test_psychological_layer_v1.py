"""Incremental audit gates. An unfinished program must not pass closeout."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import psychological_layer_v1 as p


class PsychologicalBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = p.read(p.STORE / "baseline.json")
        cls.registry = p.read(p.STORE / "relationship-review-registry.json")

    def test_actual_membership_and_rds(self):
        b = self.baseline
        entities = p.read(p.ROOT / "data/entities.json")
        members = [e for e in entities if e["layer"] == "Psychological"]
        self.assertEqual(set(b["entityIds"]), {e["id"] for e in members})
        self.assertEqual((len(members), sum(e["entityType"] == "DRIVER" for e in members)), (135, 134))
        self.assertEqual(b["summary"]["rdsIds"], ["PSY-078"])
        self.assertEqual([f["id"] for f in b["familyInventory"]], p.FAMILIES)

    def test_each_family_uses_generic_frozen_membership(self):
        for family in self.baseline["familyInventory"]:
            d = p.read(p.STORE / family["id"] / "BASELINE.json")
            self.assertEqual(set(family["memberIds"]), {e["id"] for e in d["entities"]})
            self.assertEqual(d["baselineCommit"], p.BASELINE)
            self.assertEqual(d["scienceOrigin"], "PRODUCTION_BASELINE")

    def test_unique_relationship_registry_not_incident_sum(self):
        edges = self.baseline["activeEdges"]
        self.assertEqual(len(edges), 111)
        self.assertEqual(len({r["id"] for r in edges}), 111)
        self.assertEqual({e["id"] for e in edges}, set(self.registry))
        self.assertGreater(sum(len(r["psychologicalFamilyIds"]) for r in self.registry.values()), len(self.registry))
        self.assertEqual(self.baseline["summary"]["projectionAdditionalPropositions"], 0)

    def test_no_baseline_scaffold_claims_research_complete(self):
        progress = p.read(p.STORE / "progress.json")
        for family, stages in progress["families"].items():
            if stages["COMPLETE"] == "DONE":
                self.assertTrue(all(s == "DONE" for s in stages.values()), family)
                self.assertTrue((p.STORE / family / "research.json").exists(), family)
            else:
                self.assertEqual(stages["BASELINE"], "DONE")

    def test_candidate_workspaces_remain_isolated(self):
        for family in p.FAMILIES:
            w = p.read(p.STORE / family / "workspace.json")
            self.assertEqual(w["activationStatus"], "NOT_ELIGIBLE")
            self.assertFalse(w["productionEligible"])
            for row in w["passB"]["effectAssertions"]:
                self.assertIn(row["targetKind"], ("DRIVER", "RELATIONSHIP"))
                if row["targetKind"] == "DRIVER":
                    self.assertNotEqual(row["targetId"], "PSY-078")
            for bucket in p.ae.COLLECTIONS:
                for row in w["passB"][bucket]:
                    self.assertIn(row["governance"]["lifecycleStatus"], ("CANDIDATE", "RESEARCH_NEEDED", "REVIEW_READY"))
                    self.assertEqual(row["governance"]["activationStatus"], "NOT_ELIGIBLE")

    def test_protected_science(self):
        self.assertTrue(p.check_protected()["passed"])
        counts = self.baseline["productionCounts"]
        self.assertEqual((counts["combinedActiveRelationships"], counts["combinedActiveCausal"]), (457, 436))

    def test_output_guard(self):
        with self.assertRaises(ValueError):
            p.write(p.ROOT / "data/entities.json", [])

    def test_cannot_accidentally_refreeze(self):
        with self.assertRaisesRegex(ValueError, "already exists"):
            p.freeze()


if __name__ == "__main__":
    unittest.main()
