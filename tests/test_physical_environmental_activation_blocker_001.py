"""Regression gates for the cancelled ENV activation and durable blocker."""

import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = "aee96af9c988ca9f169798e447ded1437f1edd63"
DATA = ROOT / "data/candidates/actions-events-v1/PHYSICAL_ENVIRONMENTAL_LAYER/activation-blocker-001.json"
DOC = ROOT / "docs/governance/scale-up/PHYSICAL_ENVIRONMENTAL_LAYER/PHYSICAL_ENVIRONMENTAL_LAYER_ACTIVATION_BLOCKER_001.md"
IDS = {
    "EVA-AE-V1-ENV-LAYER-001",
    "HT-V1-ENV-LAYER-001",
    "EA-V1-ENV-LAYER-001",
}


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def frozen_bytes(relative):
    return subprocess.check_output(["git", "show", f"{BASE}:{relative}"], cwd=ROOT).replace(b"\r\n", b"\n")


class PhysicalEnvironmentalActivationBlocker001Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blocker = read(DATA)
        cls.catalog = read(ROOT / "data/actions-events-v1/catalog.json")
        cls.records = {
            row["id"]: row
            for key in ("happeningTypes", "effectAssertions", "evidenceAssessments")
            for row in cls.catalog[key]
            if row["id"] in IDS
        }

    def test_exact_blocker_and_no_activation(self):
        self.assertEqual(self.blocker["blockerId"], "BLK-ENV-ACTIVATION-001")
        self.assertEqual(self.blocker["classification"], "BLOCKED_FOR_ACTIVATION")
        self.assertFalse(self.blocker["activationAuthorized"])
        self.assertEqual(self.blocker["activationChanges"], 0)
        self.assertEqual(set(self.blocker["affectedIds"]), IDS)
        for row in self.records.values():
            self.assertEqual((row["governance"]["lifecycleStatus"], row["governance"]["activationStatus"]), ("GOVERNED", "INACTIVE"))

    def test_unknown_mechanism_preserved(self):
        effect = self.records["EA-V1-ENV-LAYER-001"]
        self.assertEqual(effect["mechanismStatus"], "UNKNOWN")
        self.assertIn("No component mechanism is identified", effect["mechanism"])
        self.assertEqual(self.blocker["requiredEffectField"]["scientificallyCorrectValue"], "UNKNOWN")
        self.assertEqual(self.blocker["requiredEffectField"]["activeContract"], "mechanismStatus != UNKNOWN")

    def test_catalog_and_production_science_byte_identical(self):
        paths = (
            "data/actions-events-v1/catalog.json",
            "data/relationship-intervention-v1/source-register.json",
            "data/relationship-intervention-v1/relationships.json",
            "data/entities.json", "data/drivers.json", "data/relationships.json",
            "data/relational-state-v1/catalog.json",
        )
        for relative in paths:
            current, prior = (ROOT / relative).read_bytes().replace(b"\r\n", b"\n"), frozen_bytes(relative)
            if relative == "data/actions-events-v1/catalog.json":
                current_json, prior_json = json.loads(current), json.loads(prior)
                for key, identifier in (
                    ("happeningTypes", "HT-V1-TEC-LAYER-001"),
                    ("effectAssertions", "EA-V1-TEC-LAYER-001"),
                    ("evidenceAssessments", "EVA-AE-V1-TEC-LAYER-001"),
                ):
                    current_json[key] = [row for row in current_json[key] if row["id"] != identifier]
                current_json["authorizations"] = [row for row in current_json["authorizations"] if row["decisionId"] != "GOV-TECHNOLOGICAL-LAYER-001-2026-09-22"]
                self.assertEqual(current_json, prior_json, relative)
            elif relative == "data/relationship-intervention-v1/source-register.json":
                current_json, prior_json = json.loads(current), json.loads(prior)
                current_json["sources"] = [row for row in current_json["sources"] if row["id"] not in {"SRC-613", "SRC-614", "SRC-615", "SRC-616"}]
                self.assertEqual(current_json, prior_json, relative)
            else:
                self.assertEqual(current, prior, relative)

    def test_validator_is_byte_identical(self):
        relative = "scripts/actions_events_v1.py"
        current = (ROOT / relative).read_bytes().replace(b"\r\n", b"\n")
        self.assertEqual(current, frozen_bytes(relative))
        self.assertEqual(hashlib.sha256(current).hexdigest(), hashlib.sha256(frozen_bytes(relative)).hexdigest())

    def test_historical_audit_preserved(self):
        for relative in (
            "docs/governance/scale-up/PHYSICAL_ENVIRONMENTAL_LAYER/PHYSICAL_ENVIRONMENTAL_LAYER_ACTIVATION_AUDIT_001.md",
            "data/candidates/actions-events-v1/PHYSICAL_ENVIRONMENTAL_LAYER/activation-audit-001.json",
        ):
            self.assertEqual((ROOT / relative).read_bytes().replace(b"\r\n", b"\n"), frozen_bytes(relative))

    def test_bounded_science_and_sources_preserved(self):
        evidence = self.records["EVA-AE-V1-ENV-LAYER-001"]
        effect = self.records["EA-V1-ENV-LAYER-001"]
        self.assertEqual(evidence["synthesis"]["disposition"], "MIXED")
        self.assertIn("MIXED_SUPPORTS_BOUNDED", evidence["synthesis"]["rationale"])
        self.assertEqual((effect["targetKind"], effect["targetId"], effect["property"]), ("DRIVER", "PSY-050", "LEVEL"))
        self.assertTrue(all(value is False for key, value in self.blocker.items() if key.endswith("Changed")))

    def test_document_records_non_rejection_and_future_options(self):
        text = DOC.read_text(encoding="utf-8")
        for value in ("BLOCKED_FOR_ACTIVATION", "mechanismStatus = UNKNOWN", "does not reject", "chooses none"):
            self.assertIn(value, text)


if __name__ == "__main__":
    unittest.main()
