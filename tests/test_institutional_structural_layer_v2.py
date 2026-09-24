"""Completeness, RDS, evidence and protection gates for the final Layer audit."""

import json
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/candidates/actions-events-v1/INSTITUTIONAL_STRUCTURAL_LAYER"
DOCS = ROOT / "docs/governance/scale-up/INSTITUTIONAL_STRUCTURAL_LAYER"
sys.path.insert(0, str(ROOT / "scripts"))
import institutional_structural_layer_v2 as institutional


def read(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


class InstitutionalStructuralLayerV2Tests(unittest.TestCase):
    def test_mechanical_baseline(self):
        c = read("baseline.json")["mechanicalCounts"]
        self.assertEqual((c["families"], c["drivers"], c["rds"], c["entities"]), (13, 112, 4, 116))
        self.assertEqual((c["incidentRelationships"], c["causalRelationships"], c["causalIsolates"]), (62, 61, 49))
        self.assertEqual(c["causalScope"], {"CROSS_LAYER_INCOMING": 4, "CROSS_LAYER_OUTGOING": 16, "SAME_LAYER_CROSS_FAMILY": 19, "WITHIN_FAMILY": 22})
        self.assertEqual(c["rdsCausalSources"], ["INS-039", "INS-103"])
        self.assertEqual((c["incidentCausalV1Incomplete"], c["blockedEntities"], c["networkStateBindings"]), (61, 2, 0))

    def test_all_families_entities_and_relationships_accounted(self):
        progress = read("progress.json")["families"]
        self.assertEqual(len(progress), 13)
        self.assertEqual(set(progress.values()), {"COMPLETE"})
        self.assertEqual(len(read("negative-coverage-registry.json")), 112)
        reviews = read("relationship-review-registry.json")
        self.assertEqual(len(reviews), 62)
        self.assertEqual(set(reviews), {x["id"] for x in read("baseline.json")["incidentRelationships"]})
        self.assertTrue(all(not x["productionChangeAuthorized"] for x in reviews.values()))

    def test_existing_relationship_dispositions_and_prior_reuse(self):
        rows = read("relationship-review-registry.json")
        self.assertEqual(Counter(x["disposition"] for x in rows.values()), Counter({
            "RESEARCH_NEEDED": 26, "RETAIN_V1_INCOMPLETE": 23, "REVISION_CANDIDATE": 8,
            "RETYPE_CANDIDATE": 3, "RETAIN_AS_IS": 2,
        }))
        self.assertEqual(sum(x["priorLayerReviewReused"] for x in rows.values()), 21)

    def test_all_rds_and_both_sources_reviewed(self):
        rows = read("rds-review.json")
        self.assertEqual({x["id"] for x in rows}, {"INS-024", "INS-039", "INS-103", "INS-113"})
        self.assertEqual(sum(x["causalSource"] for x in rows), 2)
        self.assertEqual(Counter(x["recommendedDisposition"] for x in rows), Counter({"RESEARCH_NEEDED": 2, "BLOCKED": 2}))
        self.assertTrue(all(x["doubleCountRisk"] == "HIGH" for x in rows if x["causalSource"]))
        self.assertTrue(all(not x["networkStateDependency"] for x in rows))

    def test_blocked_entities_and_architecture_preserved(self):
        rows = read("architecture-escalations.json")
        metadata = next(x for x in rows if x["id"] == "BLK-INS-METADATA-001")
        self.assertEqual({x["id"] for x in metadata["blockedEntities"]}, {"INS-115", "INS-116"})
        self.assertTrue(all(x["materializationBlocked"] and x["safeReviewContinues"] for x in metadata["blockedEntities"]))
        self.assertEqual(len(read("astra-escalation-queue.json")), 3)

    def test_deep_research_findings_and_skeptical_review(self):
        routes = read("deep-research-ledger.json")
        self.assertEqual(len(routes), 8)
        self.assertTrue(all(x["closed"] and x["deepResearchComplete"] and x["skepticalReviewComplete"] for x in routes))
        hypotheses = read("actions-events-hypotheses.json")
        effects = [x for x in hypotheses if x.get("recordClass") == "EFFECT_ASSERTION"]
        self.assertEqual(len(effects), 3)
        self.assertTrue(all(x["statusBeforeSkepticalReview"] == "REVIEW_READY" and x["status"] == "RESEARCH_NEEDED" for x in effects))
        self.assertTrue(all(x["targetKind"] == "DRIVER" for x in effects))
        self.assertEqual(len(read("skeptical-review.json")), 3)
        self.assertEqual(len(read("source-findings.json")), 16)
        self.assertEqual(len(read("evidence-assessments.json")), 3)

    def test_negative_coverage_is_complete(self):
        rows = read("negative-coverage-registry.json")
        allowed = {"NOT_APPLICABLE", "NO_PLAUSIBLE_MECHANISM", "INSUFFICIENT_PRELIMINARY_SIGNAL", "SEARCHED_NO_EXACT_EVIDENCE", "EXISTING_PROPOSITION_SUFFICIENT", "CANDIDATE_RESEARCHED", "BLOCKED", "ASTRA_ESCALATION_NEEDED"}
        self.assertTrue(all(x["actionsEventsCoverage"] in allowed for x in rows.values()))
        self.assertEqual(sum(x["deepResearchRequired"] for x in rows.values()), 8)

    def test_governance_compression_and_conservative_closeout(self):
        rec = read("governance-recommendations.json")
        self.assertEqual(rec["originalGovernanceRows"], 204)
        self.assertEqual(rec["compression"], {"groupedHumanDecisions": 3, "individualScientificDecisions": 12, "blockedDecisions": 2, "nonVotingAcknowledgements": 149, "distinctScientificDecisions": 17, "priorDecisionsReused": 21})
        self.assertEqual(rec["recommendedFutureMaterialization"], {"relationships": 0, "happeningTypes": 0, "effectAssertions": 0, "evidenceAssessments": 0})
        self.assertTrue(rec["automaticCloseoutCriteriaSatisfied"])
        self.assertEqual((rec["newGoverned"], rec["newActive"]), (0, 0))

    def test_production_science_is_unchanged(self):
        institutional.validate_protection()
        manifest = read("INSTITUTIONAL_STRUCTURAL_LAYER_AUDIT_MANIFEST.json")
        self.assertFalse(manifest["productionScienceChanged"])
        self.assertEqual((manifest["newGoverned"], manifest["newActive"]), (0, 0))
        self.assertEqual(manifest["materializationOutcome"], "NONE")
        self.assertFalse(manifest["activationAuditRequired"])

    def test_required_documents_exist(self):
        names = ["PLAN", "PROGRESS", "BASELINE", "RELATIONSHIP_SUMMARY", "RDS_REVIEW", "CONSTRUCT_BOUNDARIES", "CROSS_FAMILY_ISSUES", "CROSS_LAYER_FINDINGS", "ACTIONS_EVENTS_SUMMARY", "EVIDENCE_SUMMARY", "REJECTIONS", "ARCHITECTURE_ESCALATIONS", "COMPLETENESS_REPORT", "GOVERNANCE_RECOMMENDATIONS", "GOVERNANCE_REVIEW_SUMMARY", "HANDOFF", "GOVERNANCE_DECISION_001", "CLOSEOUT_001"]
        for name in names:
            self.assertTrue((DOCS / f"INSTITUTIONAL_STRUCTURAL_LAYER_{name}.md").is_file(), name)


if __name__ == "__main__":
    unittest.main()
