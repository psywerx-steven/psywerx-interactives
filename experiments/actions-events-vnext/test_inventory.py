"""Read-only inventory, output boundary, reconciliation and repeatability tests."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import prototype as p


class InventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = p.inventory()

    def test_partition_and_family_reconciliation(self):
        s = self.data["summary"]
        self.assertEqual((s["drivers"], s["rds"], s["entities"], s["families"], s["layers"]), (770, 41, 811, 105, 8))
        self.assertEqual(sum(r["entities"] for r in self.data["families"]), 811)
        self.assertEqual(sum(r["families"] for r in self.data["layers"]), 105)
        ids = [i for f in self.data["families"] for i in f["memberIds"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_projections_are_not_counted_as_science(self):
        s = self.data["summary"]
        self.assertEqual((s["legacy"]["active"], s["projections"]["count"], s["native"]["relationships"]), (450, 450, 6))
        self.assertEqual(s["projections"]["additionalPropositions"], 0)
        self.assertEqual(s["combinedActiveRelationships"], 456)
        self.assertEqual(s["combinedActiveCausal"], 435)
        self.assertEqual(len(self.data["projectionIncompleteFields"]), 450)

    def test_graphs_and_matrices_remain_separate(self):
        s = self.data["summary"]
        for semantic, count in s["combinedBySemantic"].items():
            self.assertEqual(sum(r["count"] for r in self.data["matrices"] if r["semanticType"] == semantic), count)
            self.assertEqual(sum(s["scopeCountsBySemantic"][semantic].values()), count)
        self.assertEqual(sum(e["causalIn"] for e in self.data["entities"]), 435)
        self.assertEqual(sum(e["causalOut"] for e in self.data["entities"]), 435)
        self.assertEqual(s["combinedBySemantic"]["EMPIRICAL_NONCAUSAL"], 1)
        self.assertEqual(s["combinedBySemantic"]["DERIVATIONAL"], 9)

    def test_every_family_has_unadjudicated_queue_entry(self):
        queue = self.data["auditQueue"]
        self.assertEqual(len(queue), 105)
        self.assertEqual({r["familyId"] for r in queue}, {r["id"] for r in self.data["families"]})
        self.assertTrue(all(r["governanceDecision"] == "PENDING" for r in queue))
        self.assertTrue(all(r["priorityScore"] == sum(r["scoreComponents"].values()) for r in queue))

    def test_bio_f01_current_compatibility(self):
        f = next(f for f in self.data["families"] if f["id"] == "BIO-F01")
        self.assertEqual((f["drivers"], f["rds"], f["causalIncident"], f["internal"], f["sameLayerCrossFamily"], f["crossLayer"]), (6, 5, 10, 3, 4, 3))
        self.assertEqual(f["causallyIsolatedEntities"], 6)
        s = self.data["summary"]["native"]
        self.assertEqual(s["interventions"], {"GOVERNED / ACTIVE": 5, "GOVERNED / INACTIVE": 4})
        self.assertEqual(s["effects"], {"GOVERNED / ACTIVE": 5})

    def test_output_canonical_and_prefix_traps_rejected(self):
        for path in (p.ROOT / "data", p.ROOT, p.HERE, p.ROOT / "experiments/actions-events-vnext-escape"):
            with self.assertRaises(ValueError):
                p.output_dir(path)
        with self.assertRaises(ValueError):
            p.write_json(p.HERE, "../../data/forbidden.json", {})

    def test_unknown_family_does_not_create_directory(self):
        with tempfile.TemporaryDirectory(dir=p.HERE) as d:
            dest = Path(d) / "unknown"
            with self.assertRaises(ValueError):
                p.emit("SYN-NO-SUCH-FAMILY", dest)
            self.assertFalse(dest.exists())

    def test_report_generation_is_deterministic_and_template_empty(self):
        before = p.protected_hashes()
        with tempfile.TemporaryDirectory(dir=p.HERE) as d:
            p.emit("BIO-F01", d)
            first = {f.name: f.read_bytes() for f in Path(d).iterdir()}
            p.emit("BIO-F01", d)
            self.assertEqual(first, {f.name: f.read_bytes() for f in Path(d).iterdir()})
            template = json.loads(first["BIO-F01_research_template.json"])
            for key in ("relationships", "happeningTypes", "occurrences", "effectAssertions", "evidenceAssessments"):
                self.assertEqual(template[key], [])
            self.assertFalse(template["productionGraphEligible"])
        self.assertEqual(before, p.protected_hashes())

    def test_statuses_and_original_fields_preserved_in_family_export(self):
        original = p.read("data/relationship-intervention-v1/relationships.json")["relationships"]
        before = copy.deepcopy(original)
        with tempfile.TemporaryDirectory(dir=p.HERE) as d:
            p.emit("BIO-F01", d)
            exported = json.loads((Path(d) / "BIO-F01_baseline.json").read_text(encoding="utf-8"))
            self.assertEqual(exported["nativeIncident"], original)
        self.assertEqual(before, p.read("data/relationship-intervention-v1/relationships.json")["relationships"])

    def test_protected_hash_comparison_passes(self):
        self.assertTrue(p.verify_protected()["passed"])


if __name__ == "__main__":
    unittest.main()
