"""Conservation, completeness, RDS and governance gates for Social Layer V2."""

import json
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/candidates/actions-events-v1/SOCIAL_LAYER"
DOCS = ROOT / "docs/governance/scale-up/SOCIAL_LAYER"
sys.path.insert(0, str(ROOT / "scripts"))
import social_layer_v2 as social


def read(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


class SocialLayerV2Tests(unittest.TestCase):
    def test_mechanical_baseline(self):
        c = read("baseline.json")["mechanicalCounts"]
        self.assertEqual((c["families"], c["drivers"], c["rds"], c["entities"]), (12, 83, 23, 106))
        self.assertEqual((c["incidentRelationships"], c["causalRelationships"], c["causalIsolates"]), (99, 92, 34))
        self.assertEqual(c["causalScope"], {"CROSS_LAYER_INCOMING": 21, "CROSS_LAYER_OUTGOING": 10, "SAME_LAYER_CROSS_FAMILY": 22, "WITHIN_FAMILY": 39})
        self.assertEqual((len(c["rdsCausalSources"]), c["incidentCausalV1Incomplete"], c["blockedEntities"], c["networkStateBindings"]), (10, 92, 6, 1))

    def test_all_families_entities_and_relationships_accounted(self):
        progress = read("progress.json")["families"]
        self.assertEqual(len(progress), 12); self.assertEqual(set(progress.values()), {"COMPLETE"})
        self.assertEqual(len(read("negative-coverage-registry.json")), 83)
        reviews = read("relationship-review-registry.json")
        self.assertEqual(len(reviews), 99)
        self.assertEqual(set(reviews), {x["id"] for x in read("baseline.json")["incidentRelationships"]})
        self.assertTrue(all(not x["productionChangeAuthorized"] for x in reviews.values()))

    def test_existing_relationship_dispositions_and_reuse(self):
        rows = read("relationship-review-registry.json")
        self.assertEqual(Counter(x["disposition"] for x in rows.values()), Counter({
            "RETAIN_V1_INCOMPLETE": 50, "RESEARCH_NEEDED": 30, "RETAIN_AS_IS": 8,
            "REVISION_CANDIDATE": 7, "RETYPE_CANDIDATE": 4}))
        self.assertEqual(sum(x["priorLayerReviewReused"] for x in rows.values()), 34)

    def test_all_rds_and_causal_sources_individually_reviewed(self):
        rows = read("rds-review.json")
        self.assertEqual(len(rows), 23); self.assertEqual(len({x["id"] for x in rows}), 23)
        self.assertEqual(sum(x["causalSource"] for x in rows), 10)
        self.assertEqual(Counter(x["recommendedDisposition"] for x in rows), Counter({
            "RESEARCH_NEEDED": 15, "RETYPE_REVIEW_ONLY": 5, "BLOCKED": 2, "SAFE_DERIVATIONAL": 1}))
        self.assertTrue(all(x["doubleCountRisk"] == "HIGH" for x in rows if x["causalSource"]))

    def test_network_state_and_pilot_are_preserved(self):
        n = read("network-state-reconciliation.json")
        self.assertEqual((n["bindingId"], n["status"]), ("DER-V1-SOC-F07-001", "GOVERNED_INACTIVE_UNCHANGED"))
        self.assertEqual({x["id"] for x in n["blockers"]}, {"HYP-SOC-F07-H12", "HYP-SOC-F07-H20"})
        self.assertFalse(n["newBindingCreated"]); self.assertFalse(n["networkStateMutated"])
        queue = json.loads((ROOT / "data/candidates/actions-events-v1/SOC-F07/source-registration-queue.json").read_text(encoding="utf-8"))
        row = next(x for x in queue if x["sourceId"] == "SRC-CAND-SOC-F07-010")
        self.assertEqual(row["canonicalRegistration"], "BLOCKED_PENDING_SOURCE_REGISTRATION_CONTRACT")
        self.assertIn("non-PubMed", row["condition"])

    def test_deep_research_skeptical_review_and_targets(self):
        routes = read("deep-research-ledger.json")
        self.assertEqual(len(routes), 6); self.assertTrue(all(x["closed"] and x["skepticalReviewComplete"] for x in routes))
        hypotheses = read("actions-events-hypotheses.json")
        effects = [x for x in hypotheses if x.get("recordClass") == "EFFECT_ASSERTION"]
        self.assertEqual(len(effects), 2); self.assertTrue(all(x["status"] == "RESEARCH_NEEDED" for x in effects))
        self.assertTrue(all(x["targetKind"] == "DRIVER" for x in effects))
        self.assertEqual({x["targetId"] for x in effects}, {"SOC-034", "SOC-100"})
        self.assertEqual(len(read("skeptical-review.json")), 2)
        self.assertEqual(len(read("source-findings.json")), 12)
        self.assertEqual(len(read("evidence-assessments.json")), 2)

    def test_governance_compression_and_zero_materialization(self):
        rec = read("governance-recommendations.json")
        self.assertEqual(rec["originalGovernanceRows"], 229)
        self.assertEqual(rec["compression"], {"groupedHumanDecisions": 4, "individualScientificDecisions": 17,
            "blockedDecisions": 2, "nonVotingAcknowledgements": 144, "distinctScientificDecisions": 23,
            "priorDecisionsReused": 34})
        self.assertEqual(rec["recommendedFutureMaterialization"], {"relationships": 0, "happeningTypes": 0, "effectAssertions": 0, "evidenceAssessments": 0})
        self.assertEqual((rec["newGoverned"], rec["newActive"]), (0, 0))

    def test_production_science_is_unchanged(self):
        social.validate_protection()
        self.assertEqual(read("architecture-escalations.json")[0]["id"], "HYP-SOC-F07-H12")
        self.assertEqual(len(read("astra-escalation-queue.json")), 3)

    def test_required_documents_exist(self):
        names = ["PLAN", "PROGRESS", "BASELINE", "RELATIONSHIP_SUMMARY", "RDS_REVIEW",
            "NETWORK_STATE_RECONCILIATION", "CONSTRUCT_BOUNDARIES", "CROSS_FAMILY_ISSUES",
            "CROSS_LAYER_FINDINGS", "ACTIONS_EVENTS_SUMMARY", "EVIDENCE_SUMMARY", "REJECTIONS",
            "ARCHITECTURE_ESCALATIONS", "COMPLETENESS_REPORT", "GOVERNANCE_RECOMMENDATIONS",
            "GOVERNANCE_REVIEW_SUMMARY", "HANDOFF"]
        for name in names:
            self.assertTrue((DOCS / f"SOCIAL_LAYER_{name}.md").is_file(), name)
        self.assertTrue((DOCS / "SOCIAL_LAYER_AUDIT_MANIFEST.json").is_file())


if __name__ == "__main__":
    unittest.main()
