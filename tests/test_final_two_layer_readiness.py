"""Mechanical final-two-Layer readiness and eight-Layer status checkpoint."""

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import final_two_layer_readiness as readiness


class FinalTwoLayerReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(readiness.REPORT.read_text(encoding="utf-8"))
        cls.layers = {row["layer"]: row for row in cls.report["layers"]}
        cls.status = json.loads(readiness.STATUS_REPORT.read_text(encoding="utf-8"))

    def test_exact_mechanical_counts(self):
        self.assertEqual(set(self.layers), {"Social", "Institutional / Structural"})
        social = self.layers["Social"]
        institutional = self.layers["Institutional / Structural"]
        self.assertEqual(
            [social[key] for key in (
                "families", "drivers", "rds", "entities", "activeIncidentRelationshipCount",
                "uniqueCausalPropositionsTouchingLayer", "withinFamilyCausalCount",
                "sameLayerCrossFamilyCausalCount", "incomingCrossLayerCausalCount",
                "outgoingCrossLayerCausalCount", "causalIsolates", "rdsCausalSourceCount",
                "legacyV1IncompleteBurden", "blockedEntityCount", "networkStateBindingCount",
            )],
            [12, 83, 23, 106, 99, 92, 39, 22, 21, 10, 34, 10, 92, 6, 1],
        )
        self.assertEqual(
            [institutional[key] for key in (
                "families", "drivers", "rds", "entities", "activeIncidentRelationshipCount",
                "uniqueCausalPropositionsTouchingLayer", "withinFamilyCausalCount",
                "sameLayerCrossFamilyCausalCount", "incomingCrossLayerCausalCount",
                "outgoingCrossLayerCausalCount", "causalIsolates", "rdsCausalSourceCount",
                "legacyV1IncompleteBurden", "blockedEntityCount", "networkStateBindingCount",
            )],
            [13, 112, 4, 116, 62, 61, 22, 19, 4, 16, 49, 2, 61, 2, 0],
        )
        for row in self.layers.values():
            self.assertEqual(
                row["uniqueCausalPropositionsTouchingLayer"],
                row["withinFamilyCausalCount"] + row["sameLayerCrossFamilyCausalCount"] + row["crossLayerCausalCount"],
            )
            self.assertEqual(row["workload"]["overall"], "VERY_HIGH")

    def test_reuse_pilot_and_architecture_burdens(self):
        social, institutional = self.layers["Social"], self.layers["Institutional / Structural"]
        self.assertEqual(social["priorCompletedLayerReviewReuseCount"], 25)
        self.assertEqual(institutional["priorCompletedLayerReviewReuseCount"], 21)
        self.assertEqual(social["priorPilotCoverage"], ["SOC-F07"])
        self.assertEqual(social["knownArchitectureEscalationIds"], ["HYP-SOC-F07-H12", "HYP-SOC-F07-H20"])
        self.assertEqual(social["unresolvedPilotSourceQueueCount"], 1)
        self.assertEqual(institutional["priorPilotCoverage"], [])
        self.assertEqual(institutional["unresolvedPilotSourceQueueCount"], 0)
        self.assertEqual((social["informationalCouplingCausalCount"], social["technologicalCouplingCausalCount"]), (1, 5))
        self.assertEqual((institutional["informationalCouplingCausalCount"], institutional["technologicalCouplingCausalCount"]), (1, 5))

    def test_sequence_and_all_eight_status_rows(self):
        self.assertEqual(self.report["selection"]["recommendedNextLayer"], "Institutional / Structural")
        self.assertEqual(self.report["selection"]["finalLayer"], "Institutional / Structural")
        self.assertFalse(self.report["selection"]["startAuthorized"])
        self.assertEqual(len(self.status["layers"]), 8)
        self.assertEqual(self.status["completedCandidateAudits"], 7)
        self.assertEqual(self.status["fullLayerAuditsRemaining"], ["Institutional / Structural"])
        self.assertEqual({row["layer"] for row in self.status["layers"]}, {
            "Biological", "Psychological", "Social", "Cultural", "Physical / Environmental",
            "Institutional / Structural", "Informational", "Technological",
        })
        env = next(row for row in self.status["layers"] if row["layer"] == "Physical / Environmental")
        tech = next(row for row in self.status["layers"] if row["layer"] == "Technological")
        social = next(row for row in self.status["layers"] if row["layer"] == "Social")
        self.assertEqual((social["candidateAudit"], social["humanGovernance"]), ("COMPLETE", "PENDING"))
        self.assertEqual(env["activationAudit"], "BLOCKED")
        self.assertIn("mechanismStatus UNKNOWN", env["majorBlocker"])
        self.assertEqual(tech["activationAudit"], "BLOCKED")
        self.assertIn("BLK-TEC-ACTIVATION-001", tech["majorBlocker"])

    def test_deterministic_and_production_read_only(self):
        outputs = (readiness.REPORT, readiness.STATUS_REPORT, readiness.DOC, readiness.STATUS_DOC)
        before = {path: path.read_bytes().replace(b"\r\n", b"\n") for path in outputs}
        protected = (
            "data/actions-events-v1/catalog.json", "data/relationship-intervention-v1/source-register.json",
            "data/relationship-intervention-v1/relationships.json", "data/entities.json",
            "data/drivers.json", "data/relationships.json", "data/relational-state-v1/catalog.json",
        )
        hashes = {path: hashlib.sha256((ROOT / path).read_bytes().replace(b"\r\n", b"\n")).hexdigest() for path in protected}
        readiness.main()
        self.assertEqual(before, {path: path.read_bytes().replace(b"\r\n", b"\n") for path in outputs})
        self.assertEqual(hashes, {path: hashlib.sha256((ROOT / path).read_bytes().replace(b"\r\n", b"\n")).hexdigest() for path in protected})
        self.assertFalse(self.report["scienceResearchPerformed"])
        self.assertFalse(self.report["candidateGenerationPerformed"])
        self.assertFalse(self.report["productionScienceChanged"])


if __name__ == "__main__":
    unittest.main()
