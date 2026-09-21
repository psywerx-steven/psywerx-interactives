"""Read-only activation closeout for the governed Biological identity."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class BiologicalActivationCloseoutTests(unittest.TestCase):
    def test_identity_only_kept_inactive(self):
        catalog = json.loads((ROOT / "data/actions-events-v1/catalog.json").read_text(encoding="utf-8"))
        identity = [x for x in catalog["happeningTypes"] if x["id"] == "HT-V1-BIO-LAYER-001"]
        self.assertEqual(len(identity), 1)
        self.assertEqual(identity[0]["governance"]["lifecycleStatus"], "GOVERNED")
        self.assertEqual(identity[0]["governance"]["activationStatus"], "INACTIVE")
        self.assertFalse(any(x["typeId"] == identity[0]["id"] for x in catalog["effectAssertions"]))

    def test_closeout_is_read_only_and_preserves_deferred_science(self):
        audit = json.loads((ROOT / "data/candidates/actions-events-v1/BIOLOGICAL_LAYER/activation-closeout-001.json").read_text(encoding="utf-8"))
        self.assertEqual(audit["classification"], "KEEP_INACTIVE")
        self.assertFalse(audit["activationPerformed"])
        self.assertEqual(audit["recommendedForActivation"], [])
        effects = json.loads((ROOT / "data/candidates/actions-events-v1/BIOLOGICAL_LAYER/actions-events-hypotheses.json").read_text(encoding="utf-8"))
        evidence = json.loads((ROOT / "data/candidates/actions-events-v1/BIOLOGICAL_LAYER/evidence-assessments.json").read_text(encoding="utf-8"))
        self.assertEqual((effects[0]["status"], effects[0]["activationStatus"]), ("RESEARCH_NEEDED", "NOT_ELIGIBLE"))
        self.assertEqual((evidence[0]["disposition"], evidence[0]["activationStatus"]), ("MIXED", "NOT_ELIGIBLE"))
        self.assertEqual(set(audit["preservedBlockers"]), {"ARCH-BIO-LAYER-0001", "BLK-BIO-RDS-001", "ASTRA-BIO-LAYER-001"})


if __name__ == "__main__":
    unittest.main()
