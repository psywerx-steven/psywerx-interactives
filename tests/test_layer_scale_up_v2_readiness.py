"""Mechanical and scope gates for the seven-Layer readiness analysis."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import next_layer_readiness as readiness


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class LayerScaleUpV2ReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = read(readiness.REPORT)
        cls.layers = {row["layer"]: row for row in cls.report["layers"]}

    def test_exact_remaining_layer_inventory(self):
        self.assertEqual(set(self.layers), set(readiness.LAYERS))
        self.assertEqual(len(self.layers), 7)
        self.assertEqual(sum(row["families"] for row in self.layers.values()), 91)
        self.assertEqual(sum(row["drivers"] for row in self.layers.values()), 636)
        self.assertEqual(sum(row["rds"] for row in self.layers.values()), 40)
        self.assertEqual(sum(row["entities"] for row in self.layers.values()), 676)
        expected = {
            "Biological": (14, 72, 5, 77),
            "Social": (12, 83, 23, 106),
            "Cultural": (13, 90, 1, 91),
            "Physical / Environmental": (13, 109, 0, 109),
            "Institutional / Structural": (13, 112, 4, 116),
            "Informational": (13, 71, 7, 78),
            "Technological": (13, 99, 0, 99),
        }
        self.assertEqual({name: (row["families"], row["drivers"], row["rds"], row["entities"]) for name, row in self.layers.items()}, expected)

    def test_causal_scope_accounting_is_closed(self):
        for row in self.layers.values():
            self.assertEqual(
                row["uniqueCausalPropositionsTouchingLayer"],
                row["withinFamilyCausalCount"] + row["sameLayerCrossFamilyCausalCount"] + row["crossLayerCausalCount"],
            )
            self.assertEqual(row["crossLayerCausalCount"], row["incomingCrossLayerCausalCount"] + row["outgoingCrossLayerCausalCount"])
            self.assertGreaterEqual(row["activeIncidentRelationshipCount"], row["uniqueCausalPropositionsTouchingLayer"])
            self.assertGreaterEqual(row["entities"], row["causalIsolates"])
        self.assertEqual(self.layers["Informational"]["psychologicalCouplingCausalCount"], 14)
        self.assertEqual(self.layers["Social"]["uniqueCausalPropositionsTouchingLayer"], 92)
        self.assertEqual(self.layers["Biological"]["uniqueCausalPropositionsTouchingLayer"], 32)

    def test_rds_legacy_and_network_signals_are_mechanical(self):
        self.assertEqual((self.layers["Social"]["rds"], self.layers["Social"]["rdsCausalSourceCount"]), (23, 10))
        self.assertEqual(self.layers["Social"]["networkStateBindingCount"], 1)
        self.assertEqual(self.layers["Informational"]["rdsCausalSourceCount"], 4)
        self.assertEqual(self.layers["Physical / Environmental"]["rds"], 0)
        for row in self.layers.values():
            self.assertEqual(row["blockedOrIncompleteMetadataCount"], row["blockedEntityCount"] + row["legacyV1IncompleteBurden"])

    def test_prior_pilots_actions_events_and_source_queues_are_explicit(self):
        self.assertEqual(self.layers["Biological"]["priorPilotCoverage"], ["BIO-F01"])
        self.assertEqual(self.layers["Informational"]["priorPilotCoverage"], ["INF-F03"])
        self.assertEqual(self.layers["Social"]["priorPilotCoverage"], ["SOC-F07"])
        self.assertEqual(self.layers["Informational"]["actionsEventsCoverage"], {
            "governedHappeningTypesWithOriginLayer": 29,
            "activeHappeningTypesWithOriginLayer": 5,
            "governedEffectAssertionsTargetingLayer": 2,
            "activeEffectAssertionsTargetingLayer": 1,
            "priorPilotCandidateRecords": 21,
        })
        self.assertEqual(self.layers["Informational"]["unresolvedPilotSourceQueueCount"], 11)
        self.assertEqual(self.layers["Social"]["unresolvedPilotSourceQueueCount"], 1)
        self.assertEqual(self.layers["Cultural"]["sourceGovernanceQueueBasis"], "NO_STRUCTURED_PRIOR_PILOT_QUEUE")

    def test_workload_proxy_has_all_eight_factors_and_no_cost_fiction(self):
        expected = {
            "entityVolume", "existingRelationshipVolume", "crossLayerCoordination",
            "rdsComplexity", "constructBoundaryAmbiguity", "sourceEvidenceBurden",
            "architectureRisk", "actionsEventsSearchComplexity",
        }
        for row in self.layers.values():
            self.assertEqual(set(row["workload"]["factors"]), expected)
            self.assertTrue(set(row["workload"]["factors"].values()) <= set(readiness.LEVEL))
            self.assertIn(row["workload"]["overall"], readiness.LEVEL)
        serialized = json.dumps(self.report).lower()
        self.assertNotIn("token estimate", serialized)
        self.assertNotIn("credit estimate", serialized)

    def test_selection_is_planning_only(self):
        selection = self.report["selection"]
        self.assertEqual(selection["recommendedNextLayer"], "Informational")
        self.assertEqual(selection["alternateNextLayer"], "Biological")
        self.assertTrue(selection["planningOnly"])
        self.assertFalse(selection["nextLayerStartAuthorized"])
        self.assertFalse(self.report["scienceResearchPerformed"])
        self.assertFalse(self.report["candidateGenerationPerformed"])

    def test_no_scientific_or_candidate_data_changed(self):
        changed = subprocess.check_output([
            "git", "diff", "--name-only", readiness.SOURCE_COMMIT, "--", "data", "schemas",
        ], cwd=ROOT, text=True).strip()
        self.assertEqual(changed, "")
        candidate_branches = subprocess.check_output([
            "git", "branch", "--format=%(refname:short)",
        ], cwd=ROOT, text=True).splitlines()
        self.assertNotIn("scale-up/informational-layer-v1", candidate_branches)

    def test_output_is_deterministic(self):
        before_report = readiness.REPORT.read_bytes().replace(b"\r\n", b"\n")
        before_doc = readiness.DOC.read_bytes().replace(b"\r\n", b"\n")
        readiness.main()
        self.assertEqual(before_report, readiness.REPORT.read_bytes().replace(b"\r\n", b"\n"))
        self.assertEqual(before_doc, readiness.DOC.read_bytes().replace(b"\r\n", b"\n"))

    def test_document_contains_required_decision_sections(self):
        text = readiness.DOC.read_text(encoding="utf-8")
        for heading in ("RECOMMENDED_NEXT_LAYER", "ALTERNATE_NEXT_LAYER", "DEFER_FOR_NOW", "Selection boundary"):
            self.assertIn(heading, text)
        self.assertIn("READ-ONLY MECHANICAL PLANNING", text)
        self.assertIn("Starting another full Layer remains the next consequential human decision", text)


if __name__ == "__main__":
    unittest.main()
