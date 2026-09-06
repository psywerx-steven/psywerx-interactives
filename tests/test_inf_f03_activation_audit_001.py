"""Independent INF-F03 activation-readiness audit; performs no activation."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import actions_events_v1 as ae
import relationship_intervention_v1 as ri

DOCS = ROOT / "docs/governance/pilots/INF-F03"
AE_DATA = ROOT / "data/actions-events-v1"
RI_DATA = ROOT / "data/relationship-intervention-v1"
CANDIDATE = ROOT / "data/candidates/actions-events-v1/INF-F03"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class InfF03ActivationAudit001Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = read(DOCS / "INF_F03_ACTIVATION_AUDIT_001.json")
        cls.catalog = read(AE_DATA / "catalog.json")
        cls.relationships = read(RI_DATA / "relationships.json")["relationships"]
        cls.ri_evidence = read(RI_DATA / "evidence-assessments.json")["evidenceAssessments"]
        cls.rel_findings = read(RI_DATA / "relationship-source-findings.json")["records"][0]["sourceFindings"]
        cls.sources = {r["id"]: r for r in read(RI_DATA / "source-register.json")["sources"]}
        cls.entities = {r["id"]: r for r in read(ROOT / "data/entities.json")}
        cls.workspace = read(CANDIDATE / "workspace.json")
        cls.by_recommendation = {}
        for row in cls.audit["recommendations"]:
            cls.by_recommendation.setdefault(row["recommendation"], set()).add(row["id"])

    def test_exact_current_governed_inactive_set(self):
        records = (
            [r for r in self.relationships if r["id"] == "REL-V1-INF-F03-001"]
            + [r for r in self.ri_evidence if r["id"] == "EVA-V1-INF-F03-REL-001"]
            + ae.all_records(self.catalog)
        )
        self.assertEqual(len(records), 12)
        self.assertTrue(all(r["governance"]["lifecycleStatus"] == "GOVERNED" for r in records))
        self.assertTrue(all(r["governance"]["activationStatus"] == "INACTIVE" for r in records))
        self.assertEqual(sum(ri.governed_active(r) for r in records), 0)
        self.assertTrue(self.audit["auditOnly"])
        self.assertFalse(self.audit["activationAuthorized"])
        self.assertEqual(self.audit["statusChanges"], 0)

    def test_recommendation_partition_is_exact(self):
        self.assertEqual(self.by_recommendation["ACTIVATE_RECOMMENDED"], {
            "EVA-V1-INF-F03-REL-001", "REL-V1-INF-F03-001",
            "EVA-AE-V1-INF-F03-002", "EA-V1-INF-F03-002", "HT-V1-INF-F03-002",
        })
        self.assertEqual(self.by_recommendation["KEEP_INACTIVE"], {
            "HT-V1-INF-F03-004", "HT-V1-INF-F03-005", "HT-V1-INF-F03-006", "HT-V1-INF-F03-007",
        })
        self.assertEqual(self.by_recommendation["BLOCKED_PENDING_CORRECTION"], {
            "EVA-AE-V1-INF-F03-001", "EA-V1-INF-F03-001", "HT-V1-INF-F03-001",
        })
        self.assertNotIn("NEEDS_NEW_HUMAN_SCIENTIFIC_DECISION", self.by_recommendation)

    def test_relationship_exact_semantics_and_no_duplicate(self):
        relationship = next(r for r in self.relationships if r["id"] == "REL-V1-INF-F03-001")
        self.assertEqual((relationship["sourceEntityId"], relationship["targetEntityId"]), ("INF-015", "PSY-113"))
        self.assertEqual((self.entities["INF-015"]["entityType"], self.entities["PSY-113"]["entityType"]), ("DRIVER", "DRIVER"))
        self.assertEqual(relationship["polarity"], "CONTEXT_DEPENDENT")
        self.assertEqual(relationship["functionalForm"]["kind"], "CONTEXT_DEPENDENT_NON_MONOTONIC")
        self.assertIn("no universal positive or negative", relationship["functionalForm"]["specification"])
        self.assertNotIn("calibrat", relationship["mechanism"].casefold())
        self.assertEqual(relationship["compatibility"]["v1Executability"], "NOT_EXECUTABLE")
        self.assertIn("activationNotAuthorized", relationship["compatibility"]["blockedFields"])
        legacy = read(ROOT / "data/relationships.json")
        duplicates = [r for bucket in ("relationships", "deprecatedRelationships", "relationshipCandidates")
                      for r in legacy[bucket]
                      if r.get("subjectEntityId") == "INF-015" and r.get("objectEntityId") == "PSY-113"]
        self.assertEqual(duplicates, [])

    def test_relationship_evidence_scope_and_construct_alignment(self):
        evidence = next(r for r in self.ri_evidence if r["id"] == "EVA-V1-INF-F03-REL-001")
        self.assertEqual((evidence["evidenceDisposition"], evidence["evidenceStrength"], evidence["confidence"]),
                         ("MIXED", "MODERATE", "MODERATE"))
        text = " ".join([evidence["evidenceRationale"], evidence["conflictingEvidence"]["summary"], *evidence["limitations"]]).casefold()
        for term in ("small", "null", "trust", "calibration", "objective", "not counted as independent"):
            self.assertIn(term, text)
        self.assertIn("trustworthy", self.entities["PSY-113"]["definition"])
        self.assertEqual(evidence["sourceIds"], ["SRC-551", "SRC-552"])

    def test_ea001_is_bounded_but_not_structurally_dimension_scoped(self):
        effect = next(r for r in self.catalog["effectAssertions"] if r["id"] == "EA-V1-INF-F03-001")
        self.assertEqual((effect["targetId"], effect["targetKind"], effect["property"], effect["change"]),
                         ("INF-077", "DRIVER", "LEVEL", "DECREASE"))
        measurement = effect["scope"]["measurement"]
        self.assertIn("MANIPULATED_FEATURE_SCOPE_V1", measurement)
        self.assertIn("LEXICAL_LOW_FREQUENCY", measurement)
        self.assertIn("SYNTACTIC_CENTER_EMBEDDED_CLAUSE", measurement)
        self.assertIsInstance(measurement, str)
        schema_text = (ROOT / "schemas/actions-events/v1/effect-assertion-v1.schema.json").read_text(encoding="utf-8")
        self.assertNotIn("targetDimensions", schema_text)
        boundaries = (effect["scope"]["boundaryConditions"] + " " + " ".join(effect["qualifiers"]["risks"])).casefold()
        for term in ("comprehension", "readability", "completeness", "contradiction", "fidelity"):
            self.assertIn(term, boundaries)

    def test_ea002_exact_disclosure_target_and_no_downstream_inference(self):
        effect = next(r for r in self.catalog["effectAssertions"] if r["id"] == "EA-V1-INF-F03-002")
        evidence = next(r for r in self.catalog["evidenceAssessments"] if r["id"] == "EVA-AE-V1-INF-F03-002")
        self.assertEqual((effect["targetId"], effect["targetKind"], effect["property"], effect["change"]),
                         ("INF-015", "DRIVER", "LEVEL", "INCREASE"))
        text = " ".join([effect["scope"]["measurement"], effect["scope"]["boundaryConditions"],
                         evidence["synthesis"]["rationale"], *evidence["synthesis"]["generalizationLimits"]]).casefold()
        for term in ("justified", "disclosure", "no downstream", "trust", "calibration"):
            self.assertIn(term, text)
        self.assertEqual((evidence["synthesis"]["disposition"], evidence["synthesis"]["evidenceStrength"],
                          evidence["synthesis"]["confidence"]), ("SUPPORTS", "MODERATE", "MODERATE"))

    def test_sources_and_all_five_findings_resolve(self):
        expected = {
            "SRC-550": ("10.1016/j.cognition.2022.105070", "35257980", 2022),
            "SRC-551": ("10.1073/pnas.1913678117", "32205438", 2020),
            "SRC-552": ("10.1098/rsos.230604", "38026007", 2023),
        }
        for identifier, values in expected.items():
            source = self.sources[identifier]
            self.assertEqual((source["doi"], source["pmid"], source["year"]), values)
            self.assertEqual(source["verification"]["status"], "VERIFIED")
        ae_findings = [f for assessment in self.catalog["evidenceAssessments"] for f in assessment["sourceFindings"]]
        findings = self.rel_findings + ae_findings
        self.assertEqual({f["id"] for f in findings}, set(self.audit["sourceAudit"]["sourceFindingIds"]))
        self.assertEqual(len(findings), 5)
        self.assertTrue(all(f["sourceId"] in expected for f in findings))
        self.assertTrue(all(f["disposition"] == "MIXED" for f in findings))
        self.assertTrue(all(f["quantitativeEstimate"] is None for f in findings))
        self.assertTrue(all(f["locator"] and f["accessDepth"] in {"ABSTRACT", "SELECTED_FULL_TEXT"} for f in findings))
        for finding in findings:
            ae.schema_set().validate("source-finding", finding)

    def test_evidence_synthesis_preserves_findings_and_overlap(self):
        for evidence in self.catalog["evidenceAssessments"]:
            ids = {f["id"] for f in evidence["sourceFindings"]}
            synthesis = evidence["synthesis"]
            self.assertEqual(ids, set(synthesis["sourceFindingIds"]))
            self.assertEqual(ids, {c["findingId"] for c in synthesis["conflicts"]})
            self.assertTrue(synthesis["datasetOverlap"])
            self.assertNotEqual(synthesis["evidenceStrength"], "NOT_ASSESSED")
            self.assertNotEqual(synthesis["confidence"], "NOT_ASSESSED")

    def test_authorization_hashes_and_lineage_resolve(self):
        authorization = self.catalog["authorizations"][0]
        hashes = {r["id"]: r["recordHash"] for r in authorization["authorizedObjects"]}
        for record in ae.all_records(self.catalog):
            self.assertEqual(hashes[record["id"]], ae.digest(record))
        manifest = read(AE_DATA / "INF-F03-materialization-manifest.json")
        self.assertEqual(len(manifest["candidateLineage"]), 9)
        self.assertTrue(all(row["candidateId"] and row["canonicalId"] for row in manifest["candidateLineage"]))
        decision = ROOT / "docs/governance/pilots/INF-F03/INF_F03_GOVERNANCE_DECISION_001.md"
        self.assertTrue(decision.is_file())

    def test_dependency_order_and_deliberate_identity_rule(self):
        order = self.audit["activationOrder"]
        self.assertEqual(order[0]["ids"], ["EVA-V1-INF-F03-REL-001", "EVA-AE-V1-INF-F03-002"])
        self.assertEqual(order[2]["mode"], "ATOMIC_BUNDLE_AFTER_EFFECT_EVIDENCE")
        types = {r["id"]: r for r in self.catalog["happeningTypes"]}
        effects = {r["typeId"]: r["id"] for r in self.catalog["effectAssertions"]}
        self.assertEqual(effects["HT-V1-INF-F03-002"], "EA-V1-INF-F03-002")
        for identifier in ("HT-V1-INF-F03-001", "HT-V1-INF-F03-002", "HT-V1-INF-F03-005", "HT-V1-INF-F03-006"):
            self.assertTrue(types[identifier]["interventionSubset"])
        for identifier in ("HT-V1-INF-F03-004", "HT-V1-INF-F03-007"):
            self.assertFalse(types[identifier]["interventionSubset"])

    def test_practitioner_and_model_eligibility_fail_closed(self):
        for effect_id in ("EA-V1-INF-F03-001", "EA-V1-INF-F03-002"):
            result = ae.use_eligibility(effect_id, self.catalog)
            self.assertFalse(result["scientificUseEligibility"]["eligible"])
            self.assertFalse(result["modelEligibility"]["eligible"])
            self.assertFalse(result["practitionerActionEligibility"]["eligible"])
            reasons = " ".join(result["practitionerActionEligibility"]["reasons"])
            for required in ("controllability", "prerequisites", "feasibility", "legalConstraints",
                             "ethicalRiskConstraints", "applicability"):
                self.assertIn(required, reasons)

    def test_excluded_candidates_and_hypotheses_remain_excluded(self):
        records = self.workspace["passA"]["relationshipCandidates"] + ae.all_records(self.workspace["passB"])
        by_id = {r["id"]: r for r in records}
        for identifier in self.audit["excludedCandidateIds"]:
            self.assertIn(identifier, by_id)
            self.assertIn(by_id[identifier]["governance"]["lifecycleStatus"], {"CANDIDATE", "RESEARCH_NEEDED", "REVIEW_READY"})
            self.assertEqual(by_id[identifier]["governance"]["activationStatus"], "NOT_ELIGIBLE")
        research = read(CANDIDATE / "research.json")
        hypotheses = {r[0]: r[3] for r in research["hypotheses"]}
        for identifier in ("H04", "H07", "H08", "H09", "H12", "H13", "H16", "H17"):
            self.assertEqual(hypotheses[identifier], "RESEARCH_NEEDED")
        self.assertEqual(hypotheses["H20"], "BLOCKED_NEEDS_GOVERNANCE_INPUT")
        for identifier in ("H01", "H02", "H03", "H05", "H06", "H10", "H11", "H14", "H15", "H18", "H19"):
            self.assertEqual(hypotheses[identifier], "REJECTED_HYPOTHESIS")

    def test_rds_safety_and_production_counts(self):
        for identifier in ("INF-010", "INF-011", "INF-014", "RDS-0001"):
            entity = self.entities[identifier]
            self.assertEqual(entity["entityType"], "RELATIONAL_DERIVED_STATE")
            self.assertEqual(entity["directManipulability"], "VIA_CONSTITUENTS")
            self.assertTrue(entity["derivationLogic"])
        self.assertTrue(all(e["targetId"] not in {"INF-010", "INF-011", "INF-014", "RDS-0001"}
                            for e in self.catalog["effectAssertions"]))
        relationship = next(r for r in self.relationships if r["id"] == "REL-V1-INF-F03-001")
        self.assertNotIn("RELATIONAL_DERIVED_STATE", {relationship["sourceEntityType"], relationship["targetEntityType"]})
        counts = ri.validate_repository()
        self.assertEqual((counts["entities"], counts["activeRelationships"], counts["activeCausalRelationships"]),
                         (811, 456, 435))
        self.assertEqual((len(read(ROOT / "data/drivers.json")), len(read(ROOT / "data/relational-derived-states.json"))),
                         (770, 41))

    def test_audit_document_has_all_required_groups(self):
        text = (DOCS / "INF_F03_ACTIVATION_AUDIT_001.md").read_text(encoding="utf-8")
        for heading in ("Recommend ACTIVATE", "Recommend KEEP INACTIVE", "Blocked pending mechanical correction",
                        "Requires new human scientific decision", "Exact dependency order", "RDS safety"):
            self.assertIn(heading, text)
        self.assertIn("not an activation decision", text)


if __name__ == "__main__":
    unittest.main()
