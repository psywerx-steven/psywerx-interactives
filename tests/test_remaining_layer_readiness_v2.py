"""Mechanical gates for the post-Cultural four-Layer readiness refresh."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import sys
sys.path.insert(0, str(ROOT / "scripts"))
import remaining_layer_readiness_v2 as readiness


class RemainingLayerReadinessV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(readiness.REPORT.read_text(encoding="utf-8"))
        cls.layers = {x["layer"]: x for x in cls.report["layers"]}

    def test_exact_remaining_layers_and_accounting(self):
        self.assertEqual(set(self.layers), set(readiness.LAYERS))
        self.assertEqual(len(self.layers), 4)
        self.assertEqual(self.report["excludedCompletedLayers"], ["Psychological", "Informational", "Biological", "Cultural"])
        for row in self.layers.values():
            self.assertEqual(row["uniqueCausalPropositionsTouchingLayer"], row["withinFamilyCausalCount"] + row["sameLayerCrossFamilyCausalCount"] + row["crossLayerCausalCount"])
            self.assertEqual(row["crossLayerCausalCount"], row["incomingCrossLayerCausalCount"] + row["outgoingCrossLayerCausalCount"])

    def test_selection_passes_objective_rule(self):
        physical = self.layers["Physical / Environmental"]
        self.assertEqual(physical["workload"]["overall"], "MODERATE")
        self.assertEqual(physical["networkStateBindingCount"], 0)
        self.assertEqual(physical["blockedEntityCount"], 0)
        self.assertEqual(physical["rds"], 0)
        self.assertEqual(self.report["selection"]["recommendedNextLayer"], "Physical / Environmental")
        self.assertTrue(self.report["selection"]["autonomyRulePassed"])

    def test_prior_review_reuse_is_mechanical(self):
        physical = self.layers["Physical / Environmental"]
        self.assertEqual(physical["priorCompletedLayerReviewReuseCount"], 6)
        self.assertEqual(set(physical["priorCompletedLayerReviewReuseIds"]), {
            "REL-ENV-039", "REL-ENV-040", "REL-ENV-041", "REL-ENV-044", "REL-ENV-045", "REL-V1-BIO-F01-004",
        })

    def test_output_is_deterministic_and_read_only(self):
        before_report = readiness.REPORT.read_bytes().replace(b"\r\n", b"\n")
        before_doc = readiness.DOC.read_bytes().replace(b"\r\n", b"\n")
        readiness.main()
        self.assertEqual(before_report, readiness.REPORT.read_bytes().replace(b"\r\n", b"\n"))
        self.assertEqual(before_doc, readiness.DOC.read_bytes().replace(b"\r\n", b"\n"))
        self.assertFalse(self.report["scienceResearchPerformed"])
        self.assertFalse(self.report["candidateGenerationPerformed"])


if __name__ == "__main__":
    unittest.main()
