"""Read-only, lifecycle-aware activation audit for the Technological bundle."""

import hashlib
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "b12364aa1bbf1ff5a97ab2f5fd9bbd15889eba2f"
IDS = {
    "EVA-AE-V1-TEC-LAYER-001",
    "HT-V1-TEC-LAYER-001",
    "EA-V1-TEC-LAYER-001",
}


def read(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def frozen(relative):
    return subprocess.check_output(["git", "show", f"{BASE}:{relative}"], cwd=ROOT).replace(b"\r\n", b"\n")


class TechnologicalActivationAudit001Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = read("data/candidates/actions-events-v1/TECHNOLOGICAL_LAYER/activation-audit-001.json")
        cls.catalog = read("data/actions-events-v1/catalog.json")
        cls.records = {
            row["id"]: row
            for key in ("happeningTypes", "effectAssertions", "evidenceAssessments")
            for row in cls.catalog[key]
            if row["id"] in IDS
        }

    def test_exact_bundle_is_blocked_and_inactive(self):
        self.assertEqual(self.audit["classification"], "BLOCKED")
        self.assertEqual(self.audit["blockerId"], "BLK-TEC-ACTIVATION-001")
        self.assertEqual({x["id"] for x in self.audit["records"]}, IDS)
        self.assertFalse(self.audit["activationAuthorized"])
        self.assertFalse(self.audit["activationPerformed"])
        self.assertEqual(self.audit["activationChanges"], 0)
        for record in self.records.values():
            self.assertEqual(
                (record["governance"]["lifecycleStatus"], record["governance"]["activationStatus"]),
                ("GOVERNED", "INACTIVE"),
            )

    def test_mechanism_contract_checked_before_activation(self):
        effect = self.records["EA-V1-TEC-LAYER-001"]
        self.assertEqual(effect["mechanismStatus"], "UNKNOWN")
        self.assertEqual(effect["knowledgeStatus"], "SUPPORTED_EFFECT")
        self.assertEqual(self.audit["checks"]["activeMechanismContract"], "mechanismStatus != UNKNOWN")
        self.assertEqual(self.audit["checks"]["architectureDependency"], "ACTIVE_MECHANISM_CONTRACT")
        self.assertIn("No recipient-level mechanism is identified", effect["mechanism"])

    def test_scope_evidence_and_dependency_checks_are_explicit(self):
        checks = self.audit["checks"]
        for key in (
            "exactPropositionReferent", "exactVisualMediaScope", "adjacentAiProcessLabel",
            "immediateTiming", "adultSurveyPopulation", "governedEvidence",
            "sourceIdentityResolved", "mediumPlatformInterfaceTaskQualifiers",
            "policyTextNullExplicit", "typeDependency", "contributionControl",
        ):
            self.assertEqual(checks[key], "PASS", key)
        evidence = self.records["EVA-AE-V1-TEC-LAYER-001"]
        self.assertEqual(evidence["synthesis"]["disposition"], "MIXED")
        self.assertIn("policy-text", json.dumps(evidence).lower())

    def test_production_science_validator_and_sources_unchanged(self):
        for relative in (
            "data/actions-events-v1/catalog.json",
            "data/relationship-intervention-v1/source-register.json",
            "data/relationship-intervention-v1/relationships.json",
            "data/entities.json", "data/drivers.json", "data/relationships.json",
            "data/relational-state-v1/catalog.json", "scripts/actions_events_v1.py",
        ):
            current = (ROOT / relative).read_bytes().replace(b"\r\n", b"\n")
            self.assertEqual(current, frozen(relative), relative)
            self.assertEqual(hashlib.sha256(current).hexdigest(), hashlib.sha256(frozen(relative)).hexdigest())


if __name__ == "__main__":
    unittest.main()
