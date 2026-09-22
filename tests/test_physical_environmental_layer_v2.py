"""Exact candidate-only Physical / Environmental Layer V2 tests."""

import json
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from physical_environmental_layer_v2 import DATA, DOCS, read, validate_protection  # noqa: E402


class PhysicalEnvironmentalLayerV2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = read(DATA / "baseline.json")
        cls.coverage = read(DATA / "negative-coverage-registry.json")
        cls.relationships = read(DATA / "relationship-review-registry.json")
        cls.governance = read(DATA / "governance-recommendations.json")
        cls.index = read(DATA / "governance-index.json")

    def test_exact_baseline_and_completion(self):
        counts = self.baseline["mechanicalCounts"]
        self.assertEqual((counts["families"], counts["drivers"], counts["rds"], counts["entities"]), (13, 109, 0, 109))
        self.assertEqual((counts["incidentRelationships"], counts["causalRelationships"], counts["causalIsolates"]), (47, 47, 48))
        self.assertEqual(
            counts["causalScope"],
            {"CROSS_LAYER_INCOMING": 1, "CROSS_LAYER_OUTGOING": 7, "SAME_LAYER_CROSS_FAMILY": 18, "WITHIN_FAMILY": 21},
        )
        self.assertEqual(counts["incidentCausalV1Incomplete"], 46)
        self.assertEqual(counts["blockedEntities"], 0)
        self.assertEqual(set(read(DATA / "progress.json")["families"].values()), {"COMPLETE"})
        self.assertEqual(len(read(DATA / "family-landscapes.json")["families"]), 13)

    def test_coverage_and_relationship_ownership(self):
        self.assertEqual(len(self.coverage), 109)
        self.assertEqual(Counter(row["entityType"] for row in self.coverage.values()), {"DRIVER": 109})
        self.assertTrue(all(row["relationshipStatus"] and row["actionsEventsStatus"] for row in self.coverage.values()))
        self.assertEqual(set(self.relationships), {row["id"] for row in self.baseline["incidentRelationships"]})
        self.assertEqual(len(self.relationships), 47)
        self.assertTrue(all(row["productionChangeAuthorized"] is False for row in self.relationships.values()))
        self.assertEqual(
            Counter(row["disposition"] for row in self.relationships.values()),
            {"RETAIN_AS_IS": 1, "RETAIN_V1_INCOMPLETE": 31, "REVISION_CANDIDATE": 2, "RETYPE_CANDIDATE": 4, "RESEARCH_NEEDED": 9},
        )
        self.assertEqual(sum(bool(row["priorDecisionOrReview"]) for row in self.relationships.values()), 6)

    def test_actions_events_and_evidence_boundaries(self):
        identities = read(DATA / "actions-events-identity-registry.json")
        effects = read(DATA / "candidate-proposition-registry.json")
        assessments = read(DATA / "evidence-assessments.json")
        hypotheses = read(DATA / "actions-events-hypotheses.json")
        self.assertEqual(set(identities), {"HT-CAND-ENV-LAYER-0001"})
        self.assertEqual(set(effects), {"EA-CAND-ENV-LAYER-0001"})
        self.assertEqual([row["id"] for row in assessments], ["EVA-AE-CAND-ENV-LAYER-0001"])
        self.assertEqual(Counter(row["status"] for row in hypotheses), {"RESEARCH_NEEDED": 3, "REVIEW_READY": 1})
        self.assertTrue(all(row["targetKind"] == "DRIVER" for row in hypotheses))
        self.assertTrue(all(row.get("lifecycleStatus", "CANDIDATE") == "CANDIDATE" for row in hypotheses))
        self.assertTrue(all(row.get("activationStatus", "NOT_ELIGIBLE") == "NOT_ELIGIBLE" for row in hypotheses))
        self.assertFalse(identities["HT-CAND-ENV-LAYER-0001"]["efficacyImplied"])
        self.assertEqual(read(DATA / "rds-review.json"), [])
        self.assertEqual(read(DATA / "architecture-escalations.json"), [])
        self.assertEqual(read(DATA / "astra-escalation-queue.json"), [])

    def test_deep_research_and_source_reconciliation(self):
        sources = read(DATA / "candidate-source-registry.json")
        findings = read(DATA / "source-findings.json")
        deep = read(DATA / "deep-research-ledger.json")
        skeptical = read(DATA / "skeptical-review.json")
        overlaps = read(DATA / "source-overlap-registry.json")
        self.assertEqual((len(sources), len(findings), len(deep), len(skeptical), len(overlaps)), (18, 13, 4, 4, 4))
        self.assertEqual(len({row["pmid"] for row in sources.values()}), 18)
        self.assertEqual(len({row["doi"] for row in sources.values()}), 18)
        self.assertTrue(all(row["sourceId"] in sources for row in findings))
        self.assertEqual({row["claimId"] for row in skeptical}, {row["hypothesisId"] for row in deep})
        self.assertEqual(Counter(row["outcome"] for row in deep), {"RESEARCH_NEEDED": 3, "REVIEW_READY_BOUNDED_MIXED": 1})
        registration = read(DATA / "source-registration-recommendations.json")
        required = {sid for sid, row in registration.items() if row["recommendation"].startswith("REQUIRED_IF")}
        self.assertEqual(required, {f"SRC-CAND-ENV-LAYER-{n:03d}" for n in range(14, 18)})
        self.assertTrue(all(row["registrationNowAuthorized"] is False for row in registration.values()))

    def test_governance_compression_and_candidate_isolation(self):
        governance = self.governance
        self.assertEqual(len(self.index), governance["originalGovernanceRows"])
        self.assertEqual(len({row["rowId"] for row in self.index}), len(self.index))
        self.assertEqual(
            (len(governance["groupedHumanDecisions"]), len(governance["individualScientificDecisions"]), len(governance["blockedDecisions"])),
            (4, 9, 0),
        )
        decisions = governance["groupedHumanDecisions"] + governance["individualScientificDecisions"]
        vote_records = [record_id for decision in decisions for record_id in decision["recordIds"]]
        self.assertEqual(len(vote_records), len(set(vote_records)))
        self.assertEqual({row["decisionId"] for row in self.index if row["decisionId"]}, {row["id"] for row in decisions})
        self.assertEqual(governance["futureMaterializationRecommendations"], {"Relationships": 0, "HappeningTypes": 1, "EffectAssertions": 1, "EvidenceAssessments": 1})
        self.assertTrue(governance["consequentialHumanStopRequired"])
        self.assertEqual((governance["newGoverned"], governance["newActive"]), (0, 0))

    def test_protected_science_and_docs(self):
        validate_protection()
        self.assertGreaterEqual(len(list(DOCS.glob("PHYSICAL_ENVIRONMENTAL_LAYER_*.md"))), 15)
        self.assertTrue((DOCS / "PHYSICAL_ENVIRONMENTAL_LAYER_AUDIT_MANIFEST.json").exists())


if __name__ == "__main__":
    unittest.main()
