"""Read-only activation audit for the governed ENV bundle."""

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "72eda41e261d23b69b8cb61e0de9b6801882a3e1"


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class PhysicalEnvironmentalActivationAuditTests(unittest.TestCase):
    def test_atomic_bundle_ready_but_inactive(self):
        audit = read("data/candidates/actions-events-v1/PHYSICAL_ENVIRONMENTAL_LAYER/activation-audit-001.json")
        self.assertEqual(audit["bundleClassification"], "READY_FOR_ACTIVATION_REVIEW")
        self.assertFalse(audit["activationPerformed"])
        self.assertTrue(audit["humanActivationAuthorizationRequired"])
        identifiers = {x["id"] for x in audit["records"]}
        self.assertEqual(identifiers, {"EVA-AE-V1-ENV-LAYER-001", "HT-V1-ENV-LAYER-001", "EA-V1-ENV-LAYER-001"})
        catalog = read("data/actions-events-v1/catalog.json")
        records = {x["id"]: x for key in ("happeningTypes", "effectAssertions", "evidenceAssessments") for x in catalog[key]}
        for identifier in identifiers:
            self.assertEqual((records[identifier]["governance"]["lifecycleStatus"],
                              records[identifier]["governance"]["activationStatus"]), ("GOVERNED", "INACTIVE"))

    def test_read_only_against_post_governance_main(self):
        for path in ("data/actions-events-v1/catalog.json", "data/relationship-intervention-v1/source-register.json",
                     "data/entities.json", "data/relationships.json", "data/relational-state-v1/catalog.json"):
            before = subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT).replace(b"\r\n", b"\n")
            after = (ROOT / path).read_bytes().replace(b"\r\n", b"\n")
            self.assertEqual(before, after, path)


if __name__ == "__main__":
    unittest.main()
