"""Exact regression gates for INF-F03 partial activation decision 001."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import actions_events_v1 as ae
import relationship_intervention_v1 as ri


RI_DATA = ROOT / "data/relationship-intervention-v1"
AE_DATA = ROOT / "data/actions-events-v1"
CANDIDATE = ROOT / "data/candidates/actions-events-v1/INF-F03"
DOCS = ROOT / "docs/governance/pilots/INF-F03"
MATERIALIZER = ROOT / "scripts/materialize_inf_f03_governance_001.py"
AUDITED_HEAD = "8ecf60775a5ae35b31010c301490dfd3c439623c"
ACTIVATION_DECISION = "docs/governance/pilots/INF-F03/INF_F03_ACTIVATION_DECISION_001.md"

ACTIVE_IDS = {
    "EVA-V1-INF-F03-REL-001",
    "REL-V1-INF-F03-001",
    "EVA-AE-V1-INF-F03-002",
    "HT-V1-INF-F03-002",
    "EA-V1-INF-F03-002",
}
INACTIVE_IDS = {
    "HT-V1-INF-F03-001",
    "HT-V1-INF-F03-004",
    "HT-V1-INF-F03-005",
    "HT-V1-INF-F03-006",
    "HT-V1-INF-F03-007",
    "EA-V1-INF-F03-001",
    "EVA-AE-V1-INF-F03-001",
}


def load(path: Path, key: str | None = None):
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload[key] if key else payload


def show_json(commit: str, path: str):
    return json.loads(subprocess.check_output(
        ["git", "show", f"{commit}:{path}"], cwd=ROOT
    ).decode("utf-8"))


class InfF03Activation001Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.relationships = load(RI_DATA / "relationships.json", "relationships")
        cls.ri_evidence = load(RI_DATA / "evidence-assessments.json", "evidenceAssessments")
        cls.catalog = load(AE_DATA / "catalog.json")
        cls.manifest = load(AE_DATA / "INF-F03-materialization-manifest.json")
        cls.workspace = load(CANDIDATE / "workspace.json")
        cls.research = load(CANDIDATE / "research.json")
        cls.entities = {row["id"]: row for row in load(ROOT / "data/entities.json")}
        cls.inf_records = (
            [row for row in cls.relationships if row["id"] == "REL-V1-INF-F03-001"]
            + [row for row in cls.ri_evidence if row["id"] == "EVA-V1-INF-F03-REL-001"]
            + ae.all_records(cls.catalog)
        )

    def test_exact_five_records_are_active(self):
        self.assertEqual(len(self.inf_records), 12)
        self.assertEqual(
            {row["id"] for row in self.inf_records if ri.governed_active(row)},
            ACTIVE_IDS,
        )
        self.assertEqual(
            {row["id"] for row in self.inf_records if row["governance"]["activationStatus"] == "INACTIVE"},
            INACTIVE_IDS,
        )
        self.assertTrue(all(row["governance"]["lifecycleStatus"] == "GOVERNED" for row in self.inf_records))

    def test_activation_transition_is_exact_and_human_authorized(self):
        for record in self.inf_records:
            transitions = record["governance"]["transitionProvenance"]
            if record["id"] in ACTIVE_IDS:
                transition = transitions[-1]
                self.assertEqual(transition["fromState"], {"lifecycleStatus": "GOVERNED", "activationStatus": "INACTIVE"})
                self.assertEqual(transition["toState"], {"lifecycleStatus": "GOVERNED", "activationStatus": "ACTIVE"})
                self.assertEqual(transition["actorClass"], "AUTOMATED_PROCESS_OR_AI")
                self.assertTrue(transition["exactDecisionMaterialization"])
                self.assertEqual(transition["governanceDecisionRecord"], ACTIVATION_DECISION)
                self.assertEqual(record["governance"]["authorizedBy"], "authorized human governor")
            else:
                self.assertNotEqual(transitions[-1]["toState"]["activationStatus"], "ACTIVE")

    def test_relationship_activation_order_and_semantics(self):
        relationship = next(row for row in self.relationships if row["id"] == "REL-V1-INF-F03-001")
        evidence = next(row for row in self.ri_evidence if row["id"] == "EVA-V1-INF-F03-REL-001")
        self.assertTrue(ri.governed_active(evidence))
        self.assertTrue(ri.governed_active(relationship))
        self.assertEqual((relationship["sourceEntityId"], relationship["targetEntityId"]), ("INF-015", "PSY-113"))
        self.assertEqual(relationship["polarity"], "CONTEXT_DEPENDENT")
        self.assertEqual(relationship["functionalForm"]["kind"], "CONTEXT_DEPENDENT_NON_MONOTONIC")
        self.assertIn("no universal positive or negative", relationship["functionalForm"]["specification"])
        self.assertEqual(relationship["compatibility"]["v1Executability"], "EXECUTABLE")
        self.assertEqual(relationship["compatibility"]["blockedFields"], ["quantitativeExecutionNotAuthorized"])
        self.assertEqual(
            (evidence["evidenceDisposition"], evidence["evidenceStrength"], evidence["confidence"]),
            ("MIXED", "MODERATE", "MODERATE"),
        )
        text = " ".join([relationship["boundaryConditions"], evidence["evidenceRationale"]]).casefold()
        for forbidden_inference in ("calibration", "objective"):
            self.assertIn(forbidden_inference, text)

    def test_ea002_and_type_are_atomic_and_exact(self):
        typ = next(row for row in self.catalog["happeningTypes"] if row["id"] == "HT-V1-INF-F03-002")
        effect = next(row for row in self.catalog["effectAssertions"] if row["id"] == "EA-V1-INF-F03-002")
        evidence = next(row for row in self.catalog["evidenceAssessments"] if row["id"] == "EVA-AE-V1-INF-F03-002")
        self.assertTrue(all(ri.governed_active(row) for row in (evidence, typ, effect)))
        self.assertEqual((effect["typeId"], effect["targetId"], effect["targetKind"]), (typ["id"], "INF-015", "DRIVER"))
        self.assertEqual((effect["property"], effect["change"]), ("LEVEL", "INCREASE"))
        text = " ".join([
            effect["scope"]["measurement"], effect["scope"]["boundaryConditions"],
            evidence["synthesis"]["rationale"], *evidence["synthesis"]["generalizationLimits"],
        ]).casefold()
        for required in ("justified", "disclosure", "no downstream", "trust", "calibration", "no fabricated"):
            self.assertIn(required, text)
        self.assertEqual(
            (evidence["synthesis"]["disposition"], evidence["synthesis"]["evidenceStrength"], evidence["synthesis"]["confidence"]),
            ("SUPPORTS", "MODERATE", "MODERATE"),
        )

    def test_ea001_bundle_and_other_types_remain_inactive(self):
        for identifier in INACTIVE_IDS:
            record = next(row for row in self.inf_records if row["id"] == identifier)
            self.assertEqual(record["governance"]["activationStatus"], "INACTIVE")
        audit = load(DOCS / "INF_F03_ACTIVATION_AUDIT_001.json")
        blocked = {row["id"] for row in audit["recommendations"] if row["recommendation"] == "BLOCKED_PENDING_CORRECTION"}
        self.assertEqual(blocked, {"HT-V1-INF-F03-001", "EA-V1-INF-F03-001", "EVA-AE-V1-INF-F03-001"})

    def test_non_governed_candidates_remain_not_eligible(self):
        records = self.workspace["passA"]["relationshipCandidates"] + ae.all_records(self.workspace["passB"])
        by_id = {row["id"]: row for row in records}
        excluded = {
            "REL-CAND-INF-F03-002", "REL-CAND-INF-F03-003", "REL-CAND-INF-F03-004",
            "HT-CAND-INF-F03-003", "EA-CAND-INF-F03-003", "EA-CAND-INF-F03-004",
            "EA-CAND-INF-F03-005", "EA-CAND-INF-F03-006", "EA-CAND-INF-F03-007",
        }
        for identifier in excluded:
            self.assertEqual(by_id[identifier]["governance"]["activationStatus"], "NOT_ELIGIBLE")
            self.assertNotEqual(by_id[identifier]["governance"]["lifecycleStatus"], "GOVERNED")

    def test_hypotheses_and_existing_proposals_remain_unchanged(self):
        hypotheses = {row[0]: row[3] for row in self.research["hypotheses"]}
        for identifier in ("H04", "H07", "H08", "H09", "H12", "H13", "H16", "H17"):
            self.assertEqual(hypotheses[identifier], "RESEARCH_NEEDED")
        self.assertEqual(hypotheses["H20"], "BLOCKED_NEEDS_GOVERNANCE_INPUT")
        for identifier in ("H01", "H02", "H03", "H05", "H06", "H10", "H11", "H14", "H15", "H18", "H19"):
            self.assertEqual(hypotheses[identifier], "REJECTED_HYPOTHESIS")
        self.assertEqual(
            set(self.manifest["remainingNonGoverned"]["revisionAndRetypeProposals"]),
            {"REL-INF-003", "REL-INF-006", "REL-INF-008", "REL-INF-041", "REL-INF-046", "REL-INF-048"},
        )

    def test_no_rds_endpoint_or_direct_target(self):
        rds_ids = {identifier for identifier, row in self.entities.items() if row["entityType"] == "RELATIONAL_DERIVED_STATE"}
        relationship = next(row for row in self.relationships if row["id"] == "REL-V1-INF-F03-001")
        self.assertNotIn(relationship["sourceEntityId"], rds_ids)
        self.assertNotIn(relationship["targetEntityId"], rds_ids)
        self.assertTrue(all(effect["targetId"] not in rds_ids for effect in self.catalog["effectAssertions"]))
        for identifier in ("INF-010", "INF-011", "INF-014", "RDS-0001"):
            self.assertEqual(self.entities[identifier]["directManipulability"], "VIA_CONSTITUENTS")
            self.assertTrue(self.entities[identifier]["derivationLogic"])

    def test_scientific_model_and_practitioner_eligibility_are_separate(self):
        eligible = ae.use_eligibility("EA-V1-INF-F03-002", self.catalog)
        self.assertTrue(eligible["scientificUseEligibility"]["eligible"])
        self.assertFalse(eligible["modelEligibility"]["eligible"])
        self.assertFalse(eligible["practitionerActionEligibility"]["eligible"])
        reasons = " ".join(eligible["practitionerActionEligibility"]["reasons"])
        for required in ("controllability", "prerequisites", "feasibility", "legalConstraints", "ethicalRiskConstraints", "applicability"):
            self.assertIn(required, reasons)

    def test_active_counts_are_exact(self):
        counts = ri.validate_repository()
        self.assertEqual((counts["entities"], counts["activeRelationships"], counts["activeCausalRelationships"]), (811, 457, 436))
        self.assertEqual((len(load(ROOT / "data/drivers.json")), len(load(ROOT / "data/relational-derived-states.json"))), (770, 41))
        self.assertEqual(ae.validate_catalog(self.catalog)["active"], 3)
        self.assertEqual(self.manifest["newActiveRecords"], 5)

    def test_activation_authorization_hashes_are_exact(self):
        decision = next(row for row in self.catalog["authorizations"] if row["decisionId"] == "GOV-INF-F03-ACTIVATION-001-2026-09-06")
        active_ae = {row["id"]: row for row in ae.all_records(self.catalog) if row["id"] in ACTIVE_IDS}
        self.assertEqual({row["id"] for row in decision["authorizedObjects"]}, set(active_ae))
        for authorization in decision["authorizedObjects"]:
            self.assertEqual(authorization["recordHash"], ae.digest(active_ae[authorization["id"]]))
        text = (DOCS / "INF_F03_ACTIVATION_DECISION_001.md").read_text(encoding="utf-8")
        all_active = {row["id"]: row for row in self.inf_records if row["id"] in ACTIVE_IDS}
        for identifier, record in all_active.items():
            self.assertIn(f"`{identifier}` revision 1: `{ae.digest(record)}`", text)

    def test_bio_f01_and_legacy_science_are_unchanged(self):
        baseline_ri = show_json(AUDITED_HEAD, "data/relationship-intervention-v1/relationships.json")["relationships"]
        baseline_ev = show_json(AUDITED_HEAD, "data/relationship-intervention-v1/evidence-assessments.json")["evidenceAssessments"]
        before_bio = [row for row in baseline_ri + baseline_ev if "BIO-F01" in row["id"]]
        after_bio = [row for row in self.relationships + self.ri_evidence if "BIO-F01" in row["id"]]
        self.assertEqual(after_bio, before_bio)
        self.assertEqual(
            (ROOT / "data/relationships.json").read_bytes().replace(b"\r\n", b"\n"),
            subprocess.check_output(["git", "show", f"{AUDITED_HEAD}:data/relationships.json"], cwd=ROOT).replace(b"\r\n", b"\n"),
        )

    def test_only_authorized_scientific_records_changed_from_audited_head(self):
        before_rel = {row["id"]: row for row in show_json(AUDITED_HEAD, "data/relationship-intervention-v1/relationships.json")["relationships"]}
        after_rel = {row["id"]: row for row in self.relationships}
        self.assertEqual({identifier for identifier in after_rel if after_rel[identifier] != before_rel[identifier]}, {"REL-V1-INF-F03-001"})
        before_ev = {row["id"]: row for row in show_json(AUDITED_HEAD, "data/relationship-intervention-v1/evidence-assessments.json")["evidenceAssessments"]}
        after_ev = {row["id"]: row for row in self.ri_evidence}
        self.assertEqual({identifier for identifier in after_ev if after_ev[identifier] != before_ev[identifier]}, {"EVA-V1-INF-F03-REL-001"})
        before_catalog = show_json(AUDITED_HEAD, "data/actions-events-v1/catalog.json")
        before_records = {row["id"]: row for row in ae.all_records(before_catalog)}
        after_records = {row["id"]: row for row in ae.all_records(self.catalog)}
        self.assertEqual({identifier for identifier in after_records if after_records[identifier] != before_records[identifier]}, ACTIVE_IDS & set(after_records))

    def test_materialization_is_deterministic(self):
        paths = [
            RI_DATA / "relationships.json", RI_DATA / "evidence-assessments.json",
            AE_DATA / "catalog.json", AE_DATA / "INF-F03-materialization-manifest.json",
            DOCS / "INF_F03_AUDIT_MANIFEST.json", DOCS / "INF_F03_GOVERNANCE_DECISION_PACKAGE.md",
            DOCS / "INF_F03_GOVERNANCE_DECISION_001.md", DOCS / "INF_F03_ACTIVATION_DECISION_001.md",
        ]
        normalized = lambda path: path.read_bytes().replace(b"\r\n", b"\n")
        before = {path: normalized(path) for path in paths}
        subprocess.run([sys.executable, str(MATERIALIZER)], cwd=ROOT, check=True, capture_output=True, text=True)
        self.assertEqual(before, {path: normalized(path) for path in paths})


if __name__ == "__main__":
    unittest.main()
