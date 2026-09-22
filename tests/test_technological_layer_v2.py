"""Conservation and completeness gates for Technological Layer V2."""

import json
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data/candidates/actions-events-v1/TECHNOLOGICAL_LAYER"
DOCS=ROOT/"docs/governance/scale-up/TECHNOLOGICAL_LAYER"
sys.path.insert(0,str(ROOT/"scripts"))
import technological_layer_v2 as tech


def read(name): return json.loads((DATA/name).read_text(encoding="utf-8"))


class TechnologicalLayerV2Tests(unittest.TestCase):
    def test_baseline_and_family_completion(self):
        b=read("baseline.json"); c=b["mechanicalCounts"]
        self.assertEqual((c["families"],c["drivers"],c["rds"],c["entities"]),(13,99,0,99))
        self.assertEqual((c["incidentRelationships"],c["causalRelationships"],c["causalIsolates"]),(72,70,16))
        self.assertEqual(c["causalScope"],{"CROSS_LAYER_INCOMING":4,"CROSS_LAYER_OUTGOING":19,"SAME_LAYER_CROSS_FAMILY":4,"WITHIN_FAMILY":43})
        progress=read("progress.json")["families"]
        self.assertEqual(len(progress),13); self.assertEqual(set(progress.values()),{"COMPLETE"})

    def test_every_entity_and_relationship_accounted_once(self):
        coverage=read("negative-coverage-registry.json"); reviews=read("relationship-review-registry.json")
        self.assertEqual(len(coverage),99); self.assertEqual(len(reviews),72)
        self.assertEqual(set(reviews),{x["id"] for x in read("baseline.json")["incidentRelationships"]})
        allowed={"NOT_APPLICABLE","NO_PLAUSIBLE_MECHANISM","INSUFFICIENT_PRELIMINARY_SIGNAL","SEARCHED_NO_EXACT_EVIDENCE","EXISTING_PROPOSITION_SUFFICIENT","CANDIDATE_RESEARCHED","BLOCKED","ASTRA_ESCALATION_NEEDED"}
        self.assertTrue(all(x["actionsEventsCoverage"] in allowed for x in coverage.values()))

    def test_relationship_dispositions_and_prior_reuse(self):
        rows=read("relationship-review-registry.json"); counts=Counter(x["disposition"] for x in rows.values())
        self.assertEqual(counts,Counter({"RETYPE_CANDIDATE":31,"RESEARCH_NEEDED":22,"RETAIN_V1_INCOMPLETE":13,"RETAIN_AS_IS":3,"REVISION_CANDIDATE":3}))
        self.assertEqual(sum(x["priorLayerReviewReused"] for x in rows.values()),13)
        self.assertTrue(all(not x["productionChangeAuthorized"] for x in rows.values()))

    def test_deep_research_and_skeptical_review(self):
        routes=read("deep-research-ledger.json")
        self.assertEqual(len(routes),6); self.assertTrue(all(x["opened"] and x["closed"] and x["deepResearchComplete"] for x in routes))
        effects=read("actions-events-hypotheses.json")
        self.assertEqual(len(effects),6); self.assertEqual(sum(x["status"]=="REVIEW_READY" for x in effects),1)
        self.assertEqual(len(read("skeptical-review.json")),1)
        self.assertEqual(len(read("source-findings.json")),9)
        eva=read("evidence-assessments.json")[0]
        self.assertEqual((eva["disposition"],eva["activationStatus"]),("MIXED_SUPPORTS_BOUNDED","NOT_ELIGIBLE"))

    def test_effect_target_and_identity_dedup(self):
        effect=read("actions-events-hypotheses.json")[0]
        self.assertEqual((effect["targetKind"],effect["targetId"]),("DRIVER","PSY-003"))
        self.assertNotIn(effect["targetKind"],{"RDS","RELATIONAL_STATE","CONTEXT"})
        identities=read("actions-events-identity-registry.json")
        self.assertEqual(identities["HT-REUSE-TEC-LAYER-0001"]["canonicalId"],"HT-V1-PSY-LAYER-018")
        self.assertTrue(identities["HT-CAND-TEC-LAYER-0001"]["effectFreeIdentity"])

    def test_governance_compression_and_boundary(self):
        rec=read("governance-recommendations.json")
        self.assertEqual(rec["originalGovernanceRows"],193)
        self.assertEqual(rec["compression"],{"groupedHumanDecisions":4,"individualScientificDecisions":36,"blockedDecisions":0,"nonVotingAcknowledgements":114,"distinctScientificDecisions":40})
        self.assertEqual(rec["recommendedFutureMaterialization"],{"relationships":0,"happeningTypes":1,"effectAssertions":1,"evidenceAssessments":1})
        self.assertEqual((rec["newGoverned"],rec["newActive"]),(0,0))
        self.assertTrue(rec["humanAuthorizationRequired"])

    def test_no_rds_network_or_production_mutation(self):
        self.assertEqual(read("rds-review.json"),[])
        self.assertEqual(read("architecture-escalations.json"),[])
        self.assertEqual(read("astra-escalation-queue.json"),[])
        tech.validate_protection()

    def test_required_documents_exist(self):
        names=["PLAN","PROGRESS","BASELINE","RELATIONSHIP_SUMMARY","CONSTRUCT_BOUNDARIES","CROSS_FAMILY_ISSUES","CROSS_LAYER_FINDINGS","ACTIONS_EVENTS_SUMMARY","EVIDENCE_SUMMARY","REJECTIONS","ARCHITECTURE_ESCALATIONS","COMPLETENESS_REPORT","GOVERNANCE_RECOMMENDATIONS","GOVERNANCE_REVIEW_SUMMARY","HANDOFF"]
        for name in names:self.assertTrue((DOCS/f"TECHNOLOGICAL_LAYER_{name}.md").is_file(),name)
        self.assertTrue((DOCS/"TECHNOLOGICAL_LAYER_AUDIT_MANIFEST.json").is_file())


if __name__=="__main__": unittest.main()
