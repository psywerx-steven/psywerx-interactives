"""Exact candidate-only Biological Layer V2 coverage and protection tests."""

import json
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from biological_layer_v2 import DATA, DOCS, hashes, read  # noqa: E402


class BiologicalLayerV2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b = read(DATA / "baseline.json")
        cls.coverage = read(DATA / "negative-coverage-registry.json")
        cls.relationships = read(DATA / "relationship-review-registry.json")
        cls.rds = read(DATA / "rds-review.json")
        cls.governance = read(DATA / "governance-recommendations.json")
        cls.index = read(DATA / "governance-index.json")

    def test_exact_baseline_and_family_completion(self):
        c = self.b["mechanicalCounts"]
        self.assertEqual((c["families"], c["drivers"], c["rds"], c["entities"]), (14, 72, 5, 77))
        self.assertEqual((c["incidentRelationships"], c["causalRelationships"], c["causalIsolates"]), (39, 32, 48))
        self.assertEqual(c["causalScope"], {"WITHIN_FAMILY": 7, "SAME_LAYER_CROSS_FAMILY": 14,
                                            "CROSS_LAYER_INCOMING": 6, "CROSS_LAYER_OUTGOING": 5})
        self.assertEqual(set(read(DATA / "progress.json")["families"].values()), {"COMPLETE"})
        self.assertEqual(len(read(DATA / "family-landscapes.json")["families"]), 14)

    def test_all_entities_and_incident_propositions_owned_once(self):
        self.assertEqual(len(self.coverage), 77)
        self.assertEqual(Counter(x["entityType"] for x in self.coverage.values()),
                         {"DRIVER": 72, "RELATIONAL_DERIVED_STATE": 5})
        self.assertEqual(set(self.relationships), {x["id"] for x in self.b["incidentRelationships"]})
        self.assertEqual(len(self.relationships), 39)
        self.assertTrue(all(x["relationshipStatus"] and x["actionsEventsStatus"] for x in self.coverage.values()))
        self.assertTrue(all(x["entityType"] == "DRIVER" for x in self.coverage.values()
                            if x["relationshipStatus"] == "CANDIDATE_RESEARCHED"))
        self.assertEqual(set(self.rds[0].keys()) >= {"id", "d10Disposition", "directEffectTargetAllowed"}, True)
        self.assertEqual({x["id"] for x in self.rds}, {"BIO-003", "BIO-006", "RDS-0002", "RDS-0003", "RDS-0004"})
        self.assertEqual([x["id"] for x in self.rds if x["outgoingCausalIds"]], ["BIO-003"])
        self.assertTrue(all(not x["directEffectTargetAllowed"] for x in self.rds))

    def test_pilot_and_cross_layer_reuse(self):
        reused = {k for k,v in self.relationships.items() if v["priorDecisionOrReview"]}
        self.assertEqual(len(reused), 21)
        self.assertEqual(len({k for k in reused if k.startswith("REL-V1-BIO-F01-")}), 6)
        self.assertEqual({"REL-BIO-019", "REL-BIO-020", "REL-PSY-057", "REL-PSY-058"} <= reused, True)
        self.assertEqual(len(read(DATA / "cross-family-issues.json")), 4)
        self.assertTrue(all(v["productionChangeAuthorized"] is False for v in self.relationships.values()))

    def test_candidate_isolation_and_evidence(self):
        identities = read(DATA / "actions-events-identity-registry.json")
        effects = read(DATA / "actions-events-hypotheses.json")
        eva = read(DATA / "evidence-assessments.json")
        findings = read(DATA / "source-findings.json")
        sources = read(DATA / "candidate-source-registry.json")
        self.assertEqual(len(identities), 1)
        self.assertEqual(len([x for x in effects if x["id"].startswith("EA-CAND-")]), 1)
        self.assertEqual(len(eva), 1)
        self.assertEqual(len(findings), 10)
        self.assertEqual(len(sources), 35)
        self.assertTrue(all(x["sourceId"] in sources for x in findings))
        self.assertTrue(all(x["targetKind"] == "DRIVER" for x in effects))
        self.assertTrue(all(x["targetId"] not in {r["id"] for r in self.rds} for x in effects))
        self.assertEqual(effects[0]["status"], "RESEARCH_NEEDED")
        self.assertEqual(eva[0]["disposition"], "MIXED")
        self.assertEqual(eva[0]["sourceFindingIds"], [x["id"] for x in findings[-3:]])
        self.assertTrue(all(x.get("lifecycleStatus", "CANDIDATE") != "GOVERNED" for x in effects))
        self.assertTrue(all(x.get("activationStatus", "NOT_ELIGIBLE") != "ACTIVE" for x in effects))
        self.assertEqual(len(read(DATA / "deep-research-ledger.json")), 4)
        self.assertEqual(len(read(DATA / "skeptical-review.json")), 4)

    def test_governance_index_and_blocker(self):
        g = self.governance
        self.assertEqual(len(self.index), g["originalGovernanceRows"])
        self.assertEqual(len({x["rowId"] for x in self.index}), len(self.index))
        self.assertEqual((len(g["groupedHumanDecisions"]), len(g["individualScientificDecisions"]),
                          len(g["blockedDecisions"])), (4, 5, 1))
        decisions = g["groupedHumanDecisions"] + g["individualScientificDecisions"] + g["blockedDecisions"]
        self.assertEqual(len({x["id"] for x in decisions}), len(decisions))
        record_votes = [r for x in decisions for r in x["recordIds"]]
        self.assertEqual(len(record_votes), len(set(record_votes)))
        self.assertEqual({x["decisionId"] for x in self.index if x["decisionId"]}, {x["id"] for x in decisions})
        self.assertEqual(g["futureMaterializationRecommendations"],
                         {"Relationships":0,"HappeningTypes":1,"EffectAssertions":0,"EvidenceAssessments":0})
        self.assertEqual((g["newGoverned"],g["newActive"]),(0,0))
        self.assertEqual(len(read(DATA / "astra-escalation-queue.json")), 1)

    def test_protected_science_and_docs(self):
        from biological_layer_v2 import validate_protection
        validate_protection()
        self.assertGreaterEqual(len(list(DOCS.glob("BIOLOGICAL_LAYER_*.md"))), 15)
        self.assertTrue((DOCS / "BIOLOGICAL_LAYER_AUDIT_MANIFEST.json").exists())


if __name__ == "__main__": unittest.main()
