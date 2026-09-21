"""Mechanical gates for the post-Biological five-Layer readiness refresh."""

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
        self.assertEqual(len(self.layers), 5)
        self.assertEqual(self.report["excludedCompletedLayers"], ["Psychological", "Informational", "Biological"])
        for row in self.layers.values():
            self.assertEqual(row["uniqueCausalPropositionsTouchingLayer"], row["withinFamilyCausalCount"] + row["sameLayerCrossFamilyCausalCount"] + row["crossLayerCausalCount"])
            self.assertEqual(row["crossLayerCausalCount"], row["incomingCrossLayerCausalCount"] + row["outgoingCrossLayerCausalCount"])

    def test_selection_passes_objective_rule(self):
        cultural = self.layers["Cultural"]
        self.assertEqual(cultural["workload"]["overall"], "MODERATE")
        self.assertEqual(cultural["networkStateBindingCount"], 0)
        self.assertEqual(cultural["blockedEntityCount"], 0)
        self.assertEqual(self.report["selection"]["recommendedNextLayer"], "Cultural")
        self.assertTrue(self.report["selection"]["autonomyRulePassed"])

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
