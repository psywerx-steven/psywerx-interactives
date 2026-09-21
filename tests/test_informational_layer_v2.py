"""Integrity gates for the candidate-only Informational Layer V2 package."""

from __future__ import annotations

import json
import hashlib
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import informational_layer_v2 as inf


def load(name: str):
    return json.loads((inf.DATA / name).read_text(encoding="utf-8"))


class InformationalLayerV2Tests(unittest.TestCase):
    def test_frozen_baseline_and_production_protection(self):
        frozen = load("baseline.json")
        live = inf.baseline()
        self.assertEqual(frozen, live)
        inf.validate_protection()
        self.assertEqual(frozen["hashNormalization"], "CRLF_TO_LF")
        for path, expected in frozen["productionHashes"].items():
            blob = subprocess.check_output(["git", "show", f"{inf.BASE_COMMIT}:{path}"], cwd=ROOT)
            self.assertEqual(hashlib.sha256(blob.replace(b"\r\n", b"\n")).hexdigest(), expected, path)
        self.assertEqual(len(frozen["families"]), 13)
        entities = [x["frozenRecord"] for x in frozen["entities"]]
        self.assertEqual(len(entities), 78)
        self.assertEqual(Counter(x["entityType"] for x in entities),
                         {"DRIVER": 71, "RELATIONAL_DERIVED_STATE": 7})
        rels = frozen["incidentRelationships"]
        self.assertEqual(len(rels), 64)
        self.assertEqual(len({x["id"] for x in rels}), 64)
        causal = [x for x in rels if x["edge"]["semanticType"] == "CAUSAL"]
        self.assertEqual(len(causal), 58)
        self.assertEqual(Counter(x["scope"] for x in causal),
                         {"WITHIN_FAMILY": 26, "SAME_LAYER_CROSS_FAMILY": 7,
                          "CROSS_LAYER_INCOMING": 10, "CROSS_LAYER_OUTGOING": 15})

    def test_all_family_entity_and_existing_edge_coverage(self):
        frozen = load("baseline.json")
        progress = load("progress.json")
        self.assertEqual(set(progress["families"]), {x["id"] for x in frozen["families"]})
        self.assertEqual(set(progress["families"].values()), {"COMPLETE"})
        landscapes = load("family-landscapes.json")["families"]
        self.assertEqual(set(landscapes), set(progress["families"]))
        for landscape in landscapes.values():
            self.assertTrue(landscape["mechanisms"])
            self.assertTrue(landscape["sourceIds"])
        coverage = load("negative-coverage-registry.json")
        self.assertEqual(set(coverage), {x["frozenRecord"]["id"] for x in frozen["entities"]})
        for row in coverage.values():
            self.assertTrue(row["relationshipStatus"])
            self.assertTrue(row["actionsEventsStatus"])
            self.assertTrue(row["reason"])
        reviews = load("relationship-review-registry.json")
        self.assertEqual(set(reviews), {x["id"] for x in frozen["incidentRelationships"]})
        self.assertEqual(len(reviews), 64)
        rds = load("rds-review.json")
        self.assertEqual(len(rds), 7)
        self.assertEqual(sum(bool(x["outgoingCausalIds"]) for x in rds), 4)
        self.assertTrue(all(not x["directEffectTargetAllowed"] for x in rds))
        self.assertEqual(sum(len(x["d10IncidentCausalEdges"]) for x in rds), 9)
        self.assertTrue(all(edge["rule"] == "HEIGHTENED" for row in rds for edge in row["d10IncidentCausalEdges"]))

    def test_prior_pilot_and_cross_layer_reuse(self):
        reviews = load("relationship-review-registry.json")
        psych = load("cross-layer-findings.json")
        psych = [x for x in psych if x["externalLayer"] == "Psychological" and
                 reviews[x["relationshipId"]]["semanticType"] == "CAUSAL"]
        self.assertEqual(len(psych), 14)
        self.assertTrue(all(x["priorPsychologicalReviewReused"] for x in psych))
        self.assertEqual(len([x for x in load("cross-family-issues.json") if x["semanticType"] == "CAUSAL"]), 7)
        pilot = load("pilot-source-queue-review.json")
        self.assertEqual(len(pilot), 14)
        self.assertEqual(sum(x["existingStatus"] == "CANDIDATE_ONLY" for x in pilot), 11)
        self.assertTrue(all(not x["repairOrRegistrationPerformed"] for x in pilot))
        escalations = load("architecture-escalations.json")
        self.assertIn("HYP-INF-F03-H20", {x["id"] for x in escalations})
        self.assertTrue(all(not x["resolutionAuthorized"] for x in escalations))

    def test_candidate_science_and_source_traceability(self):
        candidates = load("candidate-proposition-registry.json")
        identity = load("actions-events-identity-registry.json")
        assessments = load("evidence-assessments.json")
        findings = load("source-findings.json")
        sources = load("candidate-source-registry.json")
        deep = load("deep-research-ledger.json")
        self.assertEqual(len(deep), 1)
        self.assertEqual(set(candidates), {"REL-CAND-INF-LAYER-0001"})
        self.assertEqual(len(assessments), 1)
        self.assertEqual(len(findings), 3)
        self.assertEqual({x["id"] for x in findings}, set(deep[0]["sourceFindingIds"]))
        self.assertEqual({x["sourceId"] for x in findings}, set(deep[0]["sourceIdsReviewed"]))
        self.assertTrue(all(x["sourceId"] in sources for x in findings))
        self.assertEqual(assessments[0]["synthesis"], "INSUFFICIENT")
        self.assertEqual(candidates["REL-CAND-INF-LAYER-0001"]["lifecycleStatus"], "RESEARCH_NEEDED")
        self.assertEqual(identity["HT-CAND-INF-LAYER-0001"]["lifecycleStatus"], "REVIEW_READY")
        self.assertTrue(all(x["activationStatus"] == "NOT_ELIGIBLE" for x in candidates.values()))
        self.assertTrue(all(x["activationStatus"] == "NOT_ELIGIBLE" for x in assessments))
        self.assertTrue(all(x["targetKind"] == "DRIVER" for x in load("actions-events-hypotheses.json")))
        self.assertEqual(sum(x["status"] == "RESEARCH_NEEDED" for x in load("actions-events-hypotheses.json")), 4)
        self.assertEqual(sum(x["status"] == "BLOCKED_NEEDS_GOVERNANCE_INPUT" for x in load("actions-events-hypotheses.json")), 1)
        self.assertEqual(len(load("skeptical-review.json")["reviewReadyCandidates"]), 1)
        self.assertEqual({x["candidateId"] for x in deep}, set(candidates))

    def test_governance_compression_and_no_duplicate_votes(self):
        recommendations = load("governance-recommendations.json")
        index = load("governance-index.json")
        self.assertEqual(len(index), recommendations["originalGovernanceRows"])
        self.assertEqual(len({x["rowId"] for x in index}), len(index))
        groups = recommendations["groupedHumanDecisions"]
        individuals = recommendations["individualScientificDecisions"]
        blocked = recommendations["blockedDecisions"]
        self.assertEqual((len(groups), len(individuals), len(blocked)), (6, 18, 2))
        self.assertEqual(len(groups) + len(individuals) + len(blocked), recommendations["distinctScientificVotesProposed"])
        voted = [identifier for row in groups + individuals + blocked for identifier in row["recordIds"]]
        self.assertEqual(len(voted), len(set(voted)))
        decision_ids = {row["id"] for row in groups + individuals + blocked}
        self.assertTrue(all(row["decisionId"] in decision_ids for row in index if row["decisionId"]))
        self.assertEqual(recommendations["futureMaterializationIfApproved"],
                         {"Relationships": 0, "HappeningTypes": 1, "EffectAssertions": 0, "EvidenceAssessments": 0})
        source_recs = load("source-registration-recommendations.json")
        required = {key for key, row in source_recs.items() if row["classification"] == "REQUIRED_IF_IDENTITY_APPROVED"}
        self.assertEqual(required, {"SRC-CAND-INF-LAYER-013", "SRC-CAND-INF-LAYER-015"})
        self.assertTrue(all(x["futureApprovedRecordDependency"] == ["HT-CAND-INF-LAYER-0001"] for key, x in source_recs.items() if key in required))
        self.assertTrue(all(not x["canonicalRegistrationPerformed"] for x in source_recs.values()))
        self.assertEqual((recommendations["newGoverned"], recommendations["newActive"]), (0, 0))


if __name__ == "__main__":
    unittest.main()
