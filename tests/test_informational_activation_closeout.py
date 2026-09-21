"""Read-only activation closeout for the one governed Informational identity."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class InformationalActivationCloseoutTests(unittest.TestCase):
    def test_identity_only_kept_inactive(self):
        catalog = json.loads((ROOT / "data/actions-events-v1/catalog.json").read_text(encoding="utf-8"))
        identity = [x for x in catalog["happeningTypes"] if x["id"] == "HT-V1-INF-LAYER-001"]
        self.assertEqual(len(identity), 1)
        self.assertEqual(identity[0]["governance"]["lifecycleStatus"], "GOVERNED")
        self.assertEqual(identity[0]["governance"]["activationStatus"], "INACTIVE")
        self.assertFalse(any(x["typeId"] == identity[0]["id"] for x in catalog["effectAssertions"]))
        doc = (ROOT / "docs/governance/scale-up/INFORMATIONAL_LAYER/INFORMATIONAL_LAYER_ACTIVATION_CLOSEOUT_001.md").read_text(encoding="utf-8")
        self.assertIn("KEEP_INACTIVE", doc)
        self.assertIn("zero records recommended for activation", doc)


if __name__ == "__main__":
    unittest.main()
