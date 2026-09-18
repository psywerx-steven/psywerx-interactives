"""Advisory-governance compression and conservation gates."""

import json
import sys
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/candidates/actions-events-v1/PSYCHOLOGICAL_LAYER"
DOCS = ROOT / "docs/governance/scale-up/PSYCHOLOGICAL_LAYER"
sys.path.insert(0, str(ROOT / "scripts"))

import build_psychological_layer_governance_recommendations as builder
import closeout_psychological_layer_v1 as closeout


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


class PsychologicalGovernanceRecommendationsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = read(DATA / "governance-index.json")
        cls.package = read(DATA / "governance-recommendations.json")
        cls.sources = read(DATA / "source-registration-recommendations.json")

    def test_advisory_authority_boundary(self):
        self.assertEqual(self.package["notice"], builder.NOTICE)
        self.assertFalse(self.package["authority"]["governancePerformed"])
        self.assertFalse(self.package["authority"]["activationAuthorized"])
        self.assertFalse(self.package["authority"]["materializationAuthorized"])
        self.assertEqual(self.package["validationAssertions"]["newGoverned"], 0)
        self.assertEqual(self.package["validationAssertions"]["newActive"], 0)
        self.assertFalse(self.sources["authority"]["sourceRegistrationPerformed"])
        self.assertFalse(self.sources["authority"]["canonicalRegistrationAuthorized"])

    def test_every_governance_row_accounted_once(self):
        accounts = self.package["rowAccounts"]
        self.assertEqual(len(accounts), 595)
        self.assertEqual({x["rowId"] for x in accounts}, {x["id"] for x in self.index})
        self.assertEqual(len({x["rowId"] for x in accounts}), 595)
        units = {x["id"] for x in self.package["decisionUnits"]}
        self.assertTrue(all(x["decisionUnitId"] in units for x in accounts))
        self.assertTrue(all(not x["candidateLifecycleChanged"] for x in accounts))

    def test_compression_counts_and_no_duplicate_votes(self):
        compression = self.package["compression"]
        self.assertEqual(
            (
                compression["originalGovernanceRows"],
                compression["distinctScientificDecisions"],
                compression["groupedHumanDecisions"],
                compression["individualScientificDecisions"],
                compression["blockedDecisions"],
                compression["workflowLedgerAcknowledgements"],
            ),
            (595, 534, 48, 95, 3, 14),
        )
        units = self.package["decisionUnits"]
        self.assertEqual(len(units), len({x["id"] for x in units}))
        self.assertEqual(Counter(x["tier"] for x in units), {1: 48, 2: 95, 3: 3})
        voted_rows = [row for unit in units for row in unit["rowIds"]]
        self.assertEqual(len(voted_rows), len(set(voted_rows)))

    def test_existing_relationship_recommendations(self):
        self.assertEqual(
            self.package["existingRelationshipCounts"],
            {
                "APPROVE_RETAIN": 1,
                "APPROVE_RETAIN_V1_INCOMPLETE": 10,
                "APPROVE_RETYPE_REVIEW_ONLY": 5,
                "APPROVE_REVISION_REVIEW_ONLY": 57,
                "APPROVE_SPLIT_REVIEW_ONLY": 2,
                "KEEP_RESEARCH_NEEDED": 36,
            },
        )
        self.assertTrue(all(not x["productionChangeAuthorized"] for x in self.package["existingRelationshipRecommendations"]))

    def test_new_relationship_is_bounded_and_nonadditive(self):
        record = self.package["newRelationshipRecommendation"]
        self.assertEqual((record["id"], record["recommendation"]), ("REL-CAND-PSY-LAYER-0001", "APPROVE_AS_IS"))
        self.assertEqual((record["sourceId"], record["targetId"]), ("INF-041", "PSY-003"))
        self.assertEqual(record["relatedEffectAssertionId"], "EA-CAND-PSY-LAYER-0001")
        self.assertFalse(record["duplicateProductionEdgeFound"])
        self.assertFalse(record["additiveCountingAuthorized"])
        self.assertEqual(record["candidateLifecycle"]["activationStatus"], "NOT_ELIGIBLE")

    def test_all_identities_and_effects_individually_accounted(self):
        identities = self.package["happeningTypeIdentityRecommendations"]
        effects = self.package["effectAssertionRecommendations"]
        self.assertEqual((len(identities), len(effects)), (29, 30))
        self.assertEqual(Counter(x["recommendation"] for x in identities), {"GOVERN_INACTIVE_IDENTITY": 29})
        self.assertEqual(Counter(x["recommendation"] for x in effects), {"GOVERN_INACTIVE_AS_IS": 7, "KEEP_RESEARCH_NEEDED": 23})
        self.assertTrue(all(x["candidateLifecycle"]["activationStatus"] == "NOT_ELIGIBLE" for x in effects))
        self.assertTrue(all(x["targetKind"] == "DRIVER" and x["targetId"] != "PSY-078" for x in effects))

    def test_every_review_ready_formal_record_adjudicated(self):
        review_ready = []
        for family in sorted(DATA.glob("PSY-F*")):
            workspace = read(family / "workspace.json")
            for record in workspace["passA"].get("relationshipCandidates", []):
                if record["governance"]["lifecycleStatus"] == "REVIEW_READY":
                    review_ready.append(record["id"])
            for bucket in ("happeningTypes", "effectAssertions", "evidenceAssessments"):
                for record in workspace["passB"].get(bucket, []):
                    if record["governance"]["lifecycleStatus"] == "REVIEW_READY":
                        review_ready.append(record["id"])
            for record in workspace["passA"].get("evidence", []):
                if record["governance"]["lifecycleStatus"] == "REVIEW_READY":
                    review_ready.append(record["id"])
        self.assertEqual(len(review_ready), 45)
        adjudicated = {self.package["newRelationshipRecommendation"]["id"]}
        adjudicated |= {x["id"] for x in self.package["happeningTypeIdentityRecommendations"]}
        adjudicated |= {x["id"] for x in self.package["effectAssertionRecommendations"]}
        adjudicated |= {x["id"] for x in self.package["evidenceAssessmentDependencies"]}
        self.assertTrue(set(review_ready) <= adjudicated)

    def test_evidence_dispositions_and_dependencies_preserved(self):
        dependencies = self.package["evidenceAssessmentDependencies"]
        self.assertEqual(len(dependencies), 31)
        self.assertEqual(Counter(x["disposition"] for x in dependencies), {"INSUFFICIENT": 23, "MIXED": 7, "SUPPORTS": 1})
        self.assertEqual(Counter(x["recommendation"] for x in dependencies), {"INCLUDE_WITH_FUTURE_GOVERNED_RECORD": 8, "RETAIN_WITH_RESEARCH_NEEDED_CANDIDATE": 23})
        self.assertTrue(all(x["nullContraryPreserved"] for x in dependencies))
        self.assertTrue(all(not x["independentReplicationInflationAllowed"] for x in dependencies))
        self.assertTrue(all(not x["theoryAsExperimentAllowed"] for x in dependencies))

    def test_blocked_questions_preserved(self):
        blockers = self.package["architectureBlockers"]
        self.assertEqual({x["id"] for x in blockers}, {"BLK-PSY-001", "BLK-PSY-002", "BLK-PSY-003"})
        self.assertEqual(sum(len(x["sourceRowIds"]) for x in blockers), 10)
        self.assertTrue(all(x["recommendation"] == "BLOCKED" and not x["architectureChangeAuthorized"] for x in blockers))

    def test_future_materialization_and_source_manifest(self):
        self.assertEqual(self.package["proposedFutureMaterialization"], {"Relationships": 1, "HappeningTypes": 29, "EffectAssertions": 7, "EvidenceAssessments": 8})
        manifest = self.sources["futureRegistrationManifest"]
        self.assertEqual(len(manifest), 44)
        recommended = {self.package["newRelationshipRecommendation"]["id"]}
        recommended |= {x["id"] for x in self.package["happeningTypeIdentityRecommendations"]}
        recommended |= {x["id"] for x in self.package["effectAssertionRecommendations"] if x["recommendation"] == "GOVERN_INACTIVE_AS_IS"}
        self.assertTrue(all(set(x["requiredForRecommendedRecordIds"]) <= recommended for x in manifest))
        self.assertTrue(all(x["requiredForRecommendedRecordIds"] for x in manifest))
        self.assertTrue(all(not x["canonicalRegistrationAuthorized"] for x in self.sources["recommendations"]))

    def test_all_families_complete_and_production_protected(self):
        summary = closeout.validate()
        self.assertEqual(summary["familiesCompleted"], 14)
        self.assertEqual((summary["newGoverned"], summary["newActive"]), (0, 0))
        self.assertEqual(summary["formalScientificLifecycle"], {"RESEARCH_NEEDED": 46, "REVIEW_READY": 45})
        self.assertEqual(closeout.p.check_protected(), {"filesCompared": 191, "changed": [], "passed": True})
        self.assertEqual(summary["productionCounts"], {"drivers": 770, "rds": 41, "entities": 811, "combinedActiveRelationships": 457, "combinedActiveCausal": 436})

    def test_required_human_documents_and_headings(self):
        primary = (DOCS / "PSYCHOLOGICAL_LAYER_GOVERNANCE_RECOMMENDATIONS.md").read_text(encoding="utf-8")
        review = (DOCS / "PSYCHOLOGICAL_LAYER_GOVERNANCE_REVIEW_SUMMARY.md").read_text(encoding="utf-8")
        self.assertIn(builder.NOTICE, primary)
        self.assertIn(builder.NOTICE, review)
        for heading in (
            "Executive summary", "Grouped approvals recommended", "Grouped rejection recommendations",
            "Grouped research-needed recommendations", "Existing Relationship proposals", "New Relationship candidate",
            "HappeningType identities", "EffectAssertions", "EvidenceAssessment dependencies",
            "Construct/ontology questions", "Architecture blockers", "Future source registrations",
            "Proposed future materialization set", "Explicit exclusions", "Activation boundary",
        ):
            self.assertIn(f"## {heading}", primary)
        self.assertIn("NO ACTIVATION recommendation is authorized by this review", primary)

    def test_builder_is_deterministic(self):
        outputs = [
            DATA / "governance-recommendations.json",
            DATA / "source-registration-recommendations.json",
            DOCS / "PSYCHOLOGICAL_LAYER_GOVERNANCE_RECOMMENDATIONS.md",
            DOCS / "PSYCHOLOGICAL_LAYER_GOVERNANCE_REVIEW_SUMMARY.md",
        ]
        before = {path: path.read_bytes() for path in outputs}
        builder.main()
        self.assertEqual(before, {path: path.read_bytes() for path in outputs})


if __name__ == "__main__":
    unittest.main()
