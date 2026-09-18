"""Exact Psychological Layer governance-materialization gates."""

import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = "5675780b7c36c788f222617810bfd07ee64ebfba"
DATA = ROOT / "data/candidates/actions-events-v1/PSYCHOLOGICAL_LAYER"
sys.path.insert(0, str(ROOT / "scripts"))

import actions_events_v1 as ae
import materialize_psychological_layer_governance_001 as materialize
import materialize_psychological_layer_activation_001 as activation
import relationship_intervention_v1 as ri
import source_verification_v1 as sv


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def frozen(path):
    return json.loads(subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT))


class PsychologicalLayerMaterializationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = read(ROOT / "data/actions-events-v1/catalog.json")
        cls.relationships = read(ROOT / "data/relationship-intervention-v1/relationships.json")["relationships"]
        cls.ri_evidence = read(ROOT / "data/relationship-intervention-v1/evidence-assessments.json")["evidenceAssessments"]
        cls.sources = read(ROOT / "data/relationship-intervention-v1/source-register.json")["sources"]
        cls.manifest = read(ROOT / "data/actions-events-v1/PSYCHOLOGICAL_LAYER-materialization-manifest.json")
        cls.decision = read(DATA / "governance-decision-001.json")

    def test_exact_governed_counts_after_partial_activation(self):
        groups = {
            "relationships": [x for x in self.relationships if x["id"].startswith("REL-V1-PSY-LAYER-")],
            "happeningTypes": [x for x in self.catalog["happeningTypes"] if x["id"].startswith("HT-V1-PSY-LAYER-")],
            "effectAssertions": [x for x in self.catalog["effectAssertions"] if x["id"].startswith("EA-V1-PSY-LAYER-")],
            "evidenceAssessments": [x for x in self.ri_evidence if x["id"].startswith("EVA-V1-PSY-LAYER-")] + [x for x in self.catalog["evidenceAssessments"] if x["id"].startswith("EVA-AE-V1-PSY-LAYER-")],
        }
        self.assertEqual({k: len(v) for k, v in groups.items()}, {"relationships": 1, "happeningTypes": 29, "effectAssertions": 7, "evidenceAssessments": 8})
        records = [x for values in groups.values() for x in values]
        self.assertEqual(len(records), 45)
        self.assertTrue(all(x["governance"]["lifecycleStatus"] == "GOVERNED" for x in records))
        self.assertEqual(sum(x["governance"]["activationStatus"] == "ACTIVE" for x in records), 18)
        self.assertEqual(sum(x["governance"]["activationStatus"] == "INACTIVE" for x in records), 27)

    def test_canonical_ids_and_lineage_are_exact(self):
        ids = self.manifest["canonicalIds"]
        self.assertEqual(ids["relationship"], {"REL-CAND-PSY-LAYER-0001": "REL-V1-PSY-LAYER-001"})
        self.assertEqual(len(ids["happeningTypes"]), 29)
        self.assertEqual(set(ids["effectAssertions"].values()), {f"EA-V1-PSY-LAYER-{n:03d}" for n in materialize.APPROVED_EFFECT_NUMBERS})
        self.assertEqual(len(ids["evidenceAssessments"]), 8)
        self.assertEqual(len(ids["sources"]), 44)
        self.assertEqual(len(self.manifest["candidateLineage"]), 45)
        self.assertTrue(all(not x["scientificSemanticsBroadened"] and x["activationStatus"] == "INACTIVE" for x in self.manifest["candidateLineage"]))

    def test_relationship_bounds_and_shared_contribution(self):
        relationship = next(x for x in self.relationships if x["id"] == "REL-V1-PSY-LAYER-001")
        self.assertEqual((relationship["sourceEntityId"], relationship["targetEntityId"], relationship["polarity"]), ("INF-041", "PSY-003", "CONTEXT_DEPENDENT"))
        self.assertEqual(relationship["compatibility"]["v1Executability"], "NOT_EXECUTABLE")
        self.assertIn("numericalExecutionNotAuthorized", relationship["compatibility"]["blockedFields"])
        contribution = self.manifest["sharedContributions"]
        self.assertEqual(contribution, [{"id": "CONTRIB-PSY-LAYER-REPETITION-001", "relationshipId": "REL-V1-PSY-LAYER-001", "effectAssertionId": "EA-V1-PSY-LAYER-001", "policy": "ONE_CONTRIBUTION_NO_ADDITIVE_COUNT"}])
        effect = next(x for x in self.catalog["effectAssertions"] if x["id"] == "EA-V1-PSY-LAYER-001")
        self.assertEqual(effect["contribution"]["groupId"], contribution[0]["id"])
        self.assertIn("never sum", effect["contribution"]["reconciliation"])

    def test_effect_targets_are_exact_drivers_and_not_rds(self):
        effects = [x for x in self.catalog["effectAssertions"] if x["id"].startswith("EA-V1-PSY-LAYER-")]
        self.assertTrue(all(x["targetKind"] == "DRIVER" for x in effects))
        self.assertTrue(all(x["targetId"] != "PSY-078" for x in effects))
        self.assertEqual({x["id"] for x in effects}, {f"EA-V1-PSY-LAYER-{n:03d}" for n in materialize.APPROVED_EFFECT_NUMBERS})

    def test_evidence_semantics_and_findings_preserved(self):
        assessments = [x for x in self.catalog["evidenceAssessments"] if x["id"].startswith("EVA-AE-V1-PSY-LAYER-")]
        self.assertEqual(Counter(x["synthesis"]["disposition"] for x in assessments), {"MIXED": 6, "SUPPORTS": 1})
        self.assertTrue(any(f["disposition"] == "NULL_FINDING" for x in assessments for f in x["sourceFindings"]))
        self.assertTrue(any(f["disposition"] == "CONTRADICTED" for x in assessments for f in x["sourceFindings"]))
        relationship_evidence = next(x for x in self.ri_evidence if x["id"] == "EVA-V1-PSY-LAYER-REL-001")
        self.assertEqual((relationship_evidence["evidenceDisposition"], relationship_evidence["evidenceStrength"], relationship_evidence["confidence"]), ("MIXED", "MODERATE", "MODERATE"))

    def test_selective_sources_registered_and_verified(self):
        sources = [x for x in self.sources if x["id"] in set(materialize.SOURCE_MAP.values())]
        self.assertEqual(len(sources), 44)
        self.assertEqual({x["id"] for x in sources}, {f"SRC-{n}" for n in range(560, 604)})
        self.assertEqual(Counter(x["verification"]["system"] for x in sources), {"PUBMED_NCBI_EUTILITIES": 29, "AUTHORITATIVE_BIBLIOGRAPHIC": 15})
        for source in sources:
            ri.SchemaSet().validate("source", source)
            self.assertTrue(sv.validate_source(source))
        registration = read(materialize.SOURCE_MANIFEST)
        self.assertEqual((registration["registeredCount"], registration["recordsBlockedBySourceVerification"]), (44, []))
        self.assertTrue(all(x["approvedRecordDependencies"] for x in registration["registrations"]))

    def test_deferred_candidates_and_proposals_unchanged(self):
        effects = []
        for family in sorted(DATA.glob("PSY-F*")):
            effects.extend(read(family / "workspace.json")["passB"]["effectAssertions"])
        remaining = [x for x in effects if int(x["id"].rsplit("-", 1)[1]) not in materialize.APPROVED_EFFECT_NUMBERS]
        self.assertEqual(len(remaining), 23)
        self.assertTrue(all(x["governance"]["lifecycleStatus"] == "RESEARCH_NEEDED" and x["governance"]["activationStatus"] == "NOT_ELIGIBLE" for x in remaining))
        self.assertEqual(self.manifest["remainingNonGoverned"], {
            "effectAssertions": [f"EA-CAND-PSY-LAYER-{n:04d}" for n in range(1, 31) if n not in materialize.APPROVED_EFFECT_NUMBERS],
            "existingRelationshipResearchNeeded": 36, "revisionProposals": 57, "retypeProposals": 5,
            "splitProposals": 2, "researchNeededHypotheses": 209,
        })
        self.assertEqual(self.manifest["rejectedHypotheses"], 151)
        self.assertEqual(self.manifest["preservedBlockers"], ["BLK-PSY-001", "BLK-PSY-002", "BLK-PSY-003"])

    def test_all_families_remain_complete(self):
        summary = read(DATA / "layer-summary.json")
        self.assertEqual(summary["familiesCompleted"], 14)
        self.assertEqual(len(summary["families"]), 14)
        self.assertTrue(all(x["localComplete"] and x["layerReconciliation"] == "COMPLETE" for x in summary["families"]))

    def test_no_preexisting_production_record_changed(self):
        comparisons = [
            ("data/actions-events-v1/catalog.json", ("happeningTypes", "effectAssertions", "evidenceAssessments")),
            ("data/relationship-intervention-v1/relationships.json", ("relationships",)),
            ("data/relationship-intervention-v1/evidence-assessments.json", ("evidenceAssessments",)),
            ("data/relationship-intervention-v1/source-register.json", ("sources",)),
        ]
        current_by_path = {
            "data/actions-events-v1/catalog.json": self.catalog,
            "data/relationship-intervention-v1/relationships.json": read(ROOT / "data/relationship-intervention-v1/relationships.json"),
            "data/relationship-intervention-v1/evidence-assessments.json": read(ROOT / "data/relationship-intervention-v1/evidence-assessments.json"),
            "data/relationship-intervention-v1/source-register.json": read(ROOT / "data/relationship-intervention-v1/source-register.json"),
        }
        for path, keys in comparisons:
            old, new = frozen(path), current_by_path[path]
            for key in keys:
                current = {x["id"]: x for x in new[key]}
                for record in old[key]:
                    self.assertEqual(current[record["id"]], record, f"pre-existing record changed: {record['id']}")

    def test_prior_pilots_and_network_state_unchanged(self):
        changed = subprocess.check_output([
            "git", "diff", "--name-only", BASE, "--",
            "data/relational-state-v1", "schemas/relational-state-v1", "scripts/relational_state_v1.py",
            "docs/governance/pilots/BIO-F01", "docs/governance/pilots/INF-F03", "docs/governance/pilots/SOC-F07",
        ], cwd=ROOT, text=True).strip()
        self.assertEqual(changed, "")

    def test_authority_and_advisory_status_are_explicit(self):
        self.assertEqual(self.decision["actorClass"], "AUTHORIZED_HUMAN_GOVERNOR")
        self.assertFalse(self.decision["activationAuthorized"])
        self.assertEqual(self.decision["materialized"]["newActive"], 0)
        advisory = read(DATA / "governance-recommendations.json")
        self.assertEqual(advisory["postRecommendationStatus"]["recommended"], "HISTORICAL_ADVISORY_PRESERVED")
        self.assertTrue(advisory["postRecommendationStatus"]["humanApproved"])
        self.assertTrue(advisory["postRecommendationStatus"]["materialized"])
        self.assertFalse(advisory["postRecommendationStatus"]["activationAuthorized"])

    def test_repository_schema_validation_and_active_counts(self):
        result = ri.validate_repository()
        self.assertEqual((result["activeRelationships"], result["activeCausalRelationships"]), (457, 436))
        context = ae.Context.repository()
        validated = ae.validate_catalog(self.catalog, context)
        self.assertEqual(validated["statusChanges"], 0)
        psychological = [x for key in ("happeningTypes", "effectAssertions", "evidenceAssessments") for x in self.catalog[key] if "-PSY-LAYER-" in x["id"]]
        self.assertEqual(sum(x["governance"]["activationStatus"] == "ACTIVE" for x in psychological), 18)

    def test_activation_materializer_is_deterministic(self):
        outputs = [
            activation.CATALOG_PATH, activation.MANIFEST_PATH,
            activation.DECISION_DATA_PATH, activation.DECISION_DOC,
        ]
        normalized = lambda path: path.read_bytes().replace(b"\r\n", b"\n")
        before = {path: normalized(path) for path in outputs}
        activation.materialize()
        self.assertEqual(before, {path: normalized(path) for path in outputs})


if __name__ == "__main__":
    unittest.main()
