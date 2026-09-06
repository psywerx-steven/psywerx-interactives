"""Exact regression gates for INF-F03 human governance checkpoint 001."""

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import actions_events_v1 as ae
import audit_family as af
import build_inf_f03_pilot as pilot
import relationship_intervention_v1 as ri


RI_DATA = ROOT / "data" / "relationship-intervention-v1"
AE_DATA = ROOT / "data" / "actions-events-v1"
CANDIDATE = ROOT / "data" / "candidates" / "actions-events-v1" / "INF-F03"
DOCS = ROOT / "docs" / "governance" / "pilots" / "INF-F03"
MATERIALIZER = ROOT / "scripts" / "materialize_inf_f03_governance_001.py"
DECISION = "docs/governance/pilots/INF-F03/INF_F03_GOVERNANCE_DECISION_001.md"

RELATIONSHIP_IDS = {"REL-V1-INF-F03-001"}
TYPE_IDS = {
    "HT-V1-INF-F03-001", "HT-V1-INF-F03-002", "HT-V1-INF-F03-004",
    "HT-V1-INF-F03-005", "HT-V1-INF-F03-006", "HT-V1-INF-F03-007",
}
EFFECT_IDS = {"EA-V1-INF-F03-001", "EA-V1-INF-F03-002"}
EVIDENCE_IDS = {
    "EVA-V1-INF-F03-REL-001", "EVA-AE-V1-INF-F03-001", "EVA-AE-V1-INF-F03-002",
}
REGISTERED_SOURCE_IDS = {"SRC-550", "SRC-551", "SRC-552"}


def load(path, key=None):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return payload[key] if key else payload


class InfF03Governance001Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ri_relationships = load(RI_DATA / "relationships.json", "relationships")
        cls.ri_evidence = load(RI_DATA / "evidence-assessments.json", "evidenceAssessments")
        cls.ri_sources = load(RI_DATA / "source-register.json", "sources")
        cls.rel_findings = load(RI_DATA / "relationship-source-findings.json")
        cls.ae_catalog = load(AE_DATA / "catalog.json")
        cls.manifest = load(AE_DATA / "INF-F03-materialization-manifest.json")
        cls.workspace = load(CANDIDATE / "workspace.json")
        cls.research = load(CANDIDATE / "research.json")
        cls.entities = {row["id"]: row for row in load(ROOT / "data/entities.json")}

    def test_exact_human_governance_outcomes_recorded(self):
        decision = (DOCS / "INF_F03_GOVERNANCE_DECISION_001.md").read_text(encoding="utf-8")
        package = (DOCS / "INF_F03_GOVERNANCE_DECISION_PACKAGE.md").read_text(encoding="utf-8")
        self.assertIn("authorized human governor", decision)
        self.assertIn("Activation authorized: **no**", decision)
        self.assertNotIn("PENDING", package)
        for identifier in (
            "REL-RDS-0001", "REL-RDS-0002", "REL-RDS-0003", "REL-RDS-0014", "REL-RDS-0015",
            "REL-INF-023", "REL-INF-029", "REL-TEC-060", "REL-INF-003", "REL-INF-008",
            "REL-INF-006", "REL-INF-041", "REL-INF-046", "REL-INF-048", "REL-INF-007", "REL-INF-009",
        ):
            self.assertIn(identifier, package)
        self.assertEqual(self.manifest["governanceDecisionId"], "GOV-INF-F03-001-2026-09-06")
        self.assertFalse(self.manifest["activationAuthorized"])

    def test_only_exact_approved_records_materialized(self):
        self.assertEqual(
            {row["id"] for row in self.ri_relationships if "INF-F03" in row["id"]},
            RELATIONSHIP_IDS,
        )
        self.assertEqual({row["id"] for row in self.ae_catalog["happeningTypes"]}, TYPE_IDS)
        self.assertEqual({row["id"] for row in self.ae_catalog["effectAssertions"]}, EFFECT_IDS)
        self.assertEqual(
            {row["id"] for row in self.ae_catalog["evidenceAssessments"]},
            {"EVA-AE-V1-INF-F03-001", "EVA-AE-V1-INF-F03-002"},
        )
        self.assertEqual(self.ae_catalog["occurrences"], [])

    def test_relationship_is_mixed_context_dependent_and_not_universal(self):
        relationship = next(row for row in self.ri_relationships if row["id"] == "REL-V1-INF-F03-001")
        evidence = next(row for row in self.ri_evidence if row["id"] == "EVA-V1-INF-F03-REL-001")
        self.assertEqual(relationship["polarity"], "CONTEXT_DEPENDENT")
        self.assertEqual(relationship["functionalForm"]["kind"], "CONTEXT_DEPENDENT_NON_MONOTONIC")
        self.assertIn("no universal positive or negative", relationship["functionalForm"]["specification"])
        self.assertEqual((evidence["evidenceDisposition"], evidence["evidenceStrength"], evidence["confidence"]), ("MIXED", "MODERATE", "MODERATE"))
        text = " ".join([relationship["boundaryConditions"], evidence["evidenceRationale"], *evidence["limitations"]]).casefold()
        for required in ("numeric", "small", "null", "credibility", "calibration", "objective"):
            self.assertIn(required, text)
        self.assertEqual(relationship["governance"]["activationStatus"], "INACTIVE")
        self.assertEqual(relationship["compatibility"]["v1Executability"], "NOT_EXECUTABLE")

    def test_unapproved_relationship_candidates_remain_non_governed(self):
        candidates = {row["id"]: row for row in self.workspace["passA"]["relationshipCandidates"]}
        for identifier in ("REL-CAND-INF-F03-002", "REL-CAND-INF-F03-003", "REL-CAND-INF-F03-004"):
            self.assertEqual(candidates[identifier]["governance"]["lifecycleStatus"], "RESEARCH_NEEDED")
            self.assertEqual(candidates[identifier]["governance"]["activationStatus"], "NOT_ELIGIBLE")

    def test_ea_001_feature_scope_is_machine_readable_and_bounded(self):
        effect = next(row for row in self.ae_catalog["effectAssertions"] if row["id"] == "EA-V1-INF-F03-001")
        measurement = effect["scope"]["measurement"]
        self.assertIn("MANIPULATED_FEATURE_SCOPE_V1", measurement)
        self.assertIn("LEXICAL_LOW_FREQUENCY", measurement)
        self.assertIn("SYNTACTIC_CENTER_EMBEDDED_CLAUSE", measurement)
        self.assertIn("never to all INF-077 dimensions", measurement)
        self.assertEqual((effect["targetId"], effect["property"], effect["change"]), ("INF-077", "LEVEL", "DECREASE"))
        boundaries = (effect["scope"]["boundaryConditions"] + " " + " ".join(effect["qualifiers"]["risks"])).casefold()
        for excluded in ("meaning", "legal-obligation", "comprehension", "readability", "completeness"):
            self.assertIn(excluded, boundaries)

    def test_ea_002_is_disclosure_not_credibility_benefit(self):
        effect = next(row for row in self.ae_catalog["effectAssertions"] if row["id"] == "EA-V1-INF-F03-002")
        evidence = next(row for row in self.ae_catalog["evidenceAssessments"] if row["id"] == "EVA-AE-V1-INF-F03-002")
        self.assertEqual((effect["targetId"], effect["property"], effect["change"]), ("INF-015", "LEVEL", "INCREASE"))
        text = (effect["scope"]["boundaryConditions"] + " " + evidence["synthesis"]["rationale"]).casefold()
        self.assertIn("no fabricated", effect["scope"]["boundaryConditions"].casefold())
        self.assertIn("trust", text)
        self.assertIn("independent", text)
        self.assertEqual((evidence["synthesis"]["evidenceStrength"], evidence["synthesis"]["confidence"]), ("MODERATE", "MODERATE"))

    def test_other_effects_and_ht003_remain_research_needed(self):
        effects = {row["id"]: row for row in self.workspace["passB"]["effectAssertions"]}
        types = {row["id"]: row for row in self.workspace["passB"]["happeningTypes"]}
        for number in range(3, 8):
            row = effects[f"EA-CAND-INF-F03-{number:03d}"]
            self.assertEqual((row["governance"]["lifecycleStatus"], row["governance"]["activationStatus"]), ("RESEARCH_NEEDED", "NOT_ELIGIBLE"))
        self.assertEqual(types["HT-CAND-INF-F03-003"]["governance"]["lifecycleStatus"], "RESEARCH_NEEDED")

    def test_approved_exposure_identities_remain_non_actionable(self):
        types = {row["id"]: row for row in self.ae_catalog["happeningTypes"]}
        for identifier in ("HT-V1-INF-F03-004", "HT-V1-INF-F03-007"):
            row = types[identifier]
            self.assertFalse(row["interventionSubset"])
            self.assertEqual(row["governance"]["activationStatus"], "INACTIVE")
            self.assertFalse(any(effect["typeId"] == identifier for effect in self.ae_catalog["effectAssertions"]))
        self.assertEqual(types["HT-V1-INF-F03-004"]["kindTags"], ["EVENT", "EXPOSURE"])

    def test_no_rds_direct_target_or_new_rds_causal_endpoint(self):
        rds = {identifier for identifier, row in self.entities.items() if row["entityType"] == "RELATIONAL_DERIVED_STATE"}
        for effect in self.ae_catalog["effectAssertions"]:
            self.assertEqual(effect["targetKind"], "DRIVER")
            self.assertNotIn(effect["targetId"], rds)
        for relationship in self.ri_relationships:
            if relationship["id"] in RELATIONSHIP_IDS:
                self.assertNotIn(relationship["sourceEntityId"], rds)
                self.assertNotIn(relationship["targetEntityId"], rds)

    def test_hypothesis_dispositions_are_exact(self):
        hypotheses = {row[0]: row[3] for row in self.research["hypotheses"]}
        rejected = {"H01", "H02", "H03", "H05", "H06", "H10", "H11", "H14", "H15", "H18", "H19"}
        needed = {"H04", "H07", "H08", "H09", "H12", "H13", "H16", "H17"}
        self.assertEqual({identifier for identifier, status in hypotheses.items() if status == "REJECTED_HYPOTHESIS"}, rejected)
        self.assertEqual({identifier for identifier, status in hypotheses.items() if status == "RESEARCH_NEEDED"}, needed)
        self.assertEqual(hypotheses["H20"], "BLOCKED_NEEDS_GOVERNANCE_INPUT")
        self.assertEqual(self.manifest["rejectedHypotheses"], sorted(rejected))

    def test_existing_relationships_and_src_429_444_are_unchanged(self):
        baseline_relationships = subprocess.check_output(
            ["git", "show", "164d938bcd4bbd7e8c48c8128cacd6e64ff0287a:data/relationships.json"], cwd=ROOT
        ).replace(b"\r\n", b"\n")
        self.assertEqual((ROOT / "data/relationships.json").read_bytes().replace(b"\r\n", b"\n"), baseline_relationships)
        baseline_sources = json.loads(subprocess.check_output(
            ["git", "show", "164d938bcd4bbd7e8c48c8128cacd6e64ff0287a:data/sources.json"], cwd=ROOT
        ))
        current_sources = load(ROOT / "data/sources.json")
        before = {row["id"]: row for row in baseline_sources["sources"]}
        after = {row["id"]: row for row in current_sources["sources"]}
        self.assertEqual(after["SRC-429"], before["SRC-429"])
        self.assertEqual(after["SRC-444"], before["SRC-444"])

    def test_source_registration_is_selective_verified_and_deduplicated(self):
        native = [row for row in self.ri_sources if row["auditId"] == "AUD-INF-F03-AE-V1-20260906-001"]
        self.assertEqual({row["id"] for row in native}, REGISTERED_SOURCE_IDS)
        self.assertEqual({row["pmid"] for row in native}, {"35257980", "32205438", "38026007"})
        all_dois = [row["doi"].casefold() for row in self.ri_sources]
        all_pmids = [row["pmid"] for row in self.ri_sources]
        self.assertEqual(len(all_dois), len(set(all_dois)))
        self.assertEqual(len(all_pmids), len(set(all_pmids)))
        manifest = load(DOCS / "INF_F03_SOURCE_REGISTRATION_MANIFEST.json")
        self.assertEqual((manifest["supplementalSourcesEvaluated"], manifest["registeredCount"], manifest["duplicateCount"], manifest["rejectedOrUnverifiedCount"]), (14, 3, 0, 0))
        self.assertEqual(manifest["recordsBlockedBySourceVerification"], [])

    def test_five_governed_source_findings_and_three_assessments(self):
        rel_findings = self.rel_findings["records"][0]["sourceFindings"]
        ae_findings = [finding for assessment in self.ae_catalog["evidenceAssessments"] for finding in assessment["sourceFindings"]]
        findings = rel_findings + ae_findings
        self.assertEqual(len(findings), 5)
        self.assertTrue(all(finding["sourceId"] in REGISTERED_SOURCE_IDS for finding in findings))
        self.assertTrue(all(finding["quantitativeEstimate"] is None for finding in findings))
        self.assertTrue(any(finding["disposition"] == "MIXED" for finding in findings))
        for finding in findings:
            ae.schema_set().validate("source-finding", finding)
        assessments = [row for row in self.ri_evidence if row["id"] == "EVA-V1-INF-F03-REL-001"] + self.ae_catalog["evidenceAssessments"]
        self.assertEqual({row["id"] for row in assessments}, EVIDENCE_IDS)
        self.assertTrue(all(row["governance"]["activationStatus"] == "INACTIVE" for row in assessments))

    def test_all_new_scientific_records_are_governed_inactive(self):
        records = (
            [row for row in self.ri_relationships if row["id"] in RELATIONSHIP_IDS]
            + [row for row in self.ri_evidence if row["id"] == "EVA-V1-INF-F03-REL-001"]
            + ae.all_records(self.ae_catalog)
        )
        self.assertEqual(len(records), 12)
        self.assertTrue(all(row["governance"]["lifecycleStatus"] == "GOVERNED" for row in records))
        self.assertTrue(all(row["governance"]["activationStatus"] == "INACTIVE" for row in records))
        self.assertTrue(all(row["governance"]["decisionRecord"] == DECISION for row in records))
        self.assertTrue(all(row["governance"]["transitionProvenance"][-1]["exactDecisionMaterialization"] for row in records))
        self.assertTrue(all(row["governance"]["transitionProvenance"][-1]["actorClass"] == "AUTOMATED_PROCESS_OR_AI" for row in records))
        self.assertEqual(sum(ri.governed_active(row) for row in records), 0)
        self.assertEqual(len(self.ae_catalog["authorizations"]), 1)

    def test_active_production_counts_and_application_boundary(self):
        counts = ri.validate_repository()
        self.assertEqual((counts["entities"], counts["activeRelationships"], counts["activeCausalRelationships"]), (811, 456, 435))
        self.assertEqual((len(load(ROOT / "data/drivers.json")), len(load(ROOT / "data/relational-derived-states.json"))), (770, 41))
        self.assertEqual(ri.causal_traversal([row for row in self.ri_relationships if row["id"] in RELATIONSHIP_IDS]), [])
        self.assertEqual(ae.validate_catalog(self.ae_catalog)["active"], 0)
        for effect in self.ae_catalog["effectAssertions"]:
            eligibility = ae.use_eligibility(effect["id"], self.ae_catalog)
            self.assertFalse(eligibility["scientificUseEligibility"]["eligible"])
            self.assertFalse(eligibility["practitionerActionEligibility"]["eligible"])

    def test_candidate_to_canonical_lineage_is_exact(self):
        lineage = self.manifest["candidateLineage"]
        self.assertEqual(len(lineage), 9)
        self.assertEqual({row["canonicalId"] for row in lineage}, RELATIONSHIP_IDS | TYPE_IDS | EFFECT_IDS)
        self.assertEqual(self.manifest["governedInactiveCounts"]["totalScientificRecords"], 12)
        self.assertEqual(self.manifest["newActiveRecords"], 0)

    def test_materialization_is_deterministic(self):
        paths = [
            RI_DATA / "source-register.json", RI_DATA / "relationships.json", RI_DATA / "evidence-assessments.json",
            RI_DATA / "relationship-source-findings.json", AE_DATA / "catalog.json",
            AE_DATA / "INF-F03-materialization-manifest.json", CANDIDATE / "source-registration-queue.json",
            DOCS / "INF_F03_AUDIT_MANIFEST.json", DOCS / "INF_F03_GOVERNANCE_DECISION_PACKAGE.md",
            DOCS / "INF_F03_GOVERNANCE_DECISION_001.md", DOCS / "INF_F03_SOURCE_REGISTRATION_MANIFEST.json",
        ]
        before = {path: path.read_bytes() for path in paths}
        result = subprocess.run([sys.executable, str(MATERIALIZER)], cwd=ROOT, check=True, capture_output=True, text=True)
        self.assertIn("GOV-INF-F03-001-2026-09-06", result.stdout)
        self.assertEqual(before, {path: path.read_bytes() for path in paths})


if __name__ == "__main__":
    unittest.main()
