"""Exact candidate-only Cultural Layer V2 coverage and protection tests."""

import json
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from cultural_layer_v2 import DATA, DOCS, read, validate_protection  # noqa: E402


class CulturalLayerV2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b = read(DATA / "baseline.json")
        cls.coverage = read(DATA / "negative-coverage-registry.json")
        cls.relationships = read(DATA / "relationship-review-registry.json")
        cls.rds = read(DATA / "rds-review.json")
        cls.governance = read(DATA / "governance-recommendations.json")
        cls.index = read(DATA / "governance-index.json")

    def test_exact_baseline_and_completion(self):
        c = self.b["mechanicalCounts"]
        self.assertEqual((c["families"], c["drivers"], c["rds"], c["entities"]), (13, 90, 1, 91))
        self.assertEqual((c["incidentRelationships"], c["causalRelationships"], c["causalIsolates"]), (55, 55, 28))
        self.assertEqual(c["causalScope"], {"WITHIN_FAMILY":23, "SAME_LAYER_CROSS_FAMILY":21, "CROSS_LAYER_OUTGOING":11})
        self.assertEqual(c["rdsCausalSources"], ["CUL-088"])
        self.assertEqual(set(read(DATA / "progress.json")["families"].values()), {"COMPLETE"})
        self.assertEqual(len(read(DATA / "family-landscapes.json")["families"]), 13)

    def test_coverage_and_relationship_ownership(self):
        self.assertEqual(len(self.coverage), 91)
        self.assertEqual(Counter(x["entityType"] for x in self.coverage.values()), {"DRIVER":90, "RELATIONAL_DERIVED_STATE":1})
        self.assertEqual(set(self.relationships), {x["id"] for x in self.b["incidentRelationships"]})
        self.assertEqual(len(self.relationships), 55)
        self.assertTrue(all(x["relationshipStatus"] and x["actionsEventsStatus"] for x in self.coverage.values()))
        self.assertTrue(all(v["productionChangeAuthorized"] is False for v in self.relationships.values()))
        self.assertEqual(sum(bool(v["priorDecisionOrReview"]) for v in self.relationships.values()), 7)

    def test_rds_and_actions_events_boundaries(self):
        self.assertEqual(len(self.rds), 1)
        self.assertEqual(self.rds[0]["id"], "CUL-088")
        self.assertEqual(self.rds[0]["outgoingCausalIds"], ["REL-CUL-042"])
        self.assertFalse(self.rds[0]["directEffectTargetAllowed"])
        effects = read(DATA / "actions-events-hypotheses.json")
        self.assertEqual(len(effects), 4)
        self.assertTrue(all(x["status"] == "RESEARCH_NEEDED" for x in effects))
        self.assertTrue(all(x["targetKind"] == "DRIVER" and x["targetId"] != "CUL-088" for x in effects))
        self.assertEqual(read(DATA / "actions-events-identity-registry.json"), {})
        self.assertEqual(read(DATA / "candidate-proposition-registry.json"), {})
        self.assertEqual(read(DATA / "evidence-assessments.json"), [])

    def test_evidence_and_skeptical_review(self):
        sources = read(DATA / "candidate-source-registry.json")
        findings = read(DATA / "source-findings.json")
        deep = read(DATA / "deep-research-ledger.json")
        skeptical = read(DATA / "skeptical-review.json")
        self.assertEqual((len(sources), len(findings), len(deep), len(skeptical)), (15, 8, 4, 4))
        self.assertTrue(all(x["sourceId"] in sources for x in findings))
        self.assertEqual({x["claimId"] for x in skeptical}, {x["hypothesisId"] for x in deep})
        self.assertEqual(len(read(DATA / "astra-escalation-queue.json")), 1)

    def test_governance_compression(self):
        g = self.governance
        self.assertEqual(len(self.index), g["originalGovernanceRows"])
        self.assertEqual(len({x["rowId"] for x in self.index}), len(self.index))
        self.assertEqual((len(g["groupedHumanDecisions"]), len(g["individualScientificDecisions"]), len(g["blockedDecisions"])), (4, 9, 1))
        decisions = g["groupedHumanDecisions"] + g["individualScientificDecisions"] + g["blockedDecisions"]
        votes = [rid for unit in decisions for rid in unit["recordIds"]]
        self.assertEqual(len(votes), len(set(votes)))
        self.assertEqual({x["decisionId"] for x in self.index if x["decisionId"]}, {x["id"] for x in decisions})
        self.assertEqual(g["futureMaterializationRecommendations"], {"Relationships":0,"HappeningTypes":0,"EffectAssertions":0,"EvidenceAssessments":0})
        self.assertEqual((g["newGoverned"], g["newActive"]), (0,0))

    def test_protected_science_and_docs(self):
        validate_protection()
        self.assertGreaterEqual(len(list(DOCS.glob("CULTURAL_LAYER_*.md"))), 15)
        self.assertTrue((DOCS / "CULTURAL_LAYER_AUDIT_MANIFEST.json").exists())


if __name__ == "__main__":
    unittest.main()
