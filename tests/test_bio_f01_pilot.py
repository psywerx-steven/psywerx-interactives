import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "data" / "candidates" / "relationship-intervention-v1" / "workspace.json"
PILOT_DIR = ROOT / "docs" / "governance" / "pilots" / "BIO-F01"
MANIFEST = PILOT_DIR / "BIO_F01_AUDIT_MANIFEST.json"
MATERIALIZER = ROOT / "scripts" / "materialize_bio_f01_governance_001.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


V1 = load_module("relationship_intervention_v1_for_bio_f01", ROOT / "scripts" / "relationship_intervention_v1.py")
BUILDER = load_module("build_bio_f01_pilot_for_tests", ROOT / "scripts" / "build_bio_f01_pilot.py")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_lf_sha256(path: Path) -> str:
    payload = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest()


class BioF01PilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace = read_json(WORKSPACE)
        cls.manifest = read_json(MANIFEST)
        cls.catalog = V1.Catalog.from_repository()
        cls.schemas = V1.SchemaSet()

    def test_frozen_family_membership_is_exact(self):
        membership = self.manifest["membership"]
        self.assertEqual(membership["driverCount"], 6)
        self.assertEqual(membership["rdsCount"], 5)
        self.assertEqual(membership["total"], 11)
        actual = {
            row["id"] for row in self.catalog.entities.values()
            if row.get("primaryFamilyId") == "BIO-F01"
        }
        self.assertEqual(actual, set(membership["driverIds"] + membership["rdsIds"]))

    def test_incident_relationship_baseline_is_exact(self):
        ids = set(self.manifest["membership"]["driverIds"] + self.manifest["membership"]["rdsIds"])
        incident = [
            row for row in self.catalog.legacy_relationships.values()
            if row.get("subjectEntityId") in ids or row.get("objectEntityId") in ids
        ]
        self.assertEqual(len(incident), 11)
        self.assertEqual(sum(row["relationFamily"] == "CAUSAL" for row in incident), 6)
        self.assertEqual(sum(row["relationFamily"] == "DERIVATIONAL" for row in incident), 5)
        self.assertEqual({row["id"] for row in incident}, set(self.manifest["incidentRelationshipIds"]))

    def test_every_existing_incident_relationship_has_one_disposition(self):
        dispositions = self.manifest["existingRelationshipAudit"]
        flattened = [identifier for identifiers in dispositions.values() for identifier in identifiers]
        self.assertEqual(len(flattened), 11)
        self.assertEqual(len(set(flattened)), 11)
        self.assertEqual(set(flattened), set(self.manifest["incidentRelationshipIds"]))

    def test_candidate_workspace_validates_and_is_excluded_from_production(self):
        V1.validate_candidate_workspace(self.workspace, self.catalog, self.schemas)
        self.assertFalse(self.workspace["productionGraphEligible"])
        self.assertEqual(V1.causal_traversal(self.workspace["relationships"]), [])

    def test_candidate_counts_and_lifecycle_are_frozen(self):
        expected = {
            "relationships": 9,
            "evidenceAssessments": 18,
            "causalPathways": 0,
            "interventions": 11,
            "interventionEffects": 9,
        }
        self.assertEqual(self.manifest["candidateCounts"], expected)
        all_records = [
            row for key in expected for row in self.workspace[key]
        ]
        self.assertEqual(len(all_records), 47)
        self.assertEqual(sum(row["governance"]["lifecycleStatus"] == "REVIEW_READY" for row in all_records), 30)
        self.assertEqual(sum(row["governance"]["lifecycleStatus"] == "RESEARCH_NEEDED" for row in all_records), 17)
        self.assertTrue(all(row["governance"]["activationStatus"] == "NOT_ELIGIBLE" for row in all_records))
        self.assertTrue(all(row["governance"]["lifecycleStatus"] not in {"GOVERNED", "DEPRECATED", "REJECTED"} for row in all_records))

    def test_no_rds_is_a_direct_intervention_target(self):
        self.assertTrue(self.workspace["interventionEffects"])
        for effect in self.workspace["interventionEffects"]:
            self.assertEqual(effect["targetKind"], "DRIVER")
            target = self.catalog.entities[effect["targetDriverId"]]
            self.assertEqual(target["entityType"], "DRIVER")
        self.assertEqual(self.manifest["interventionResearch"]["rdsDirectTargetViolations"], 0)

    def test_rds_appear_only_as_outcomes_or_noncausal_derivations(self):
        rds_ids = {
            identifier for identifier, row in self.catalog.entities.items()
            if row["entityType"] == "RELATIONAL_DERIVED_STATE"
        }
        for relationship in self.workspace["relationships"]:
            if relationship["relationFamily"] == "CAUSAL":
                self.assertNotIn(relationship["sourceEntityId"], rds_ids)
                self.assertNotIn(relationship["targetEntityId"], rds_ids)
        outcome_ids = {
            identifier
            for effect in self.workspace["interventionEffects"]
            for identifier in effect["outcomeEntityIds"]
            if identifier in rds_ids
        }
        self.assertEqual(outcome_ids, {"BIO-003", "BIO-006", "RDS-0003", "RDS-0004"})

    def test_associations_are_symmetric_and_noncausal(self):
        associations = [row for row in self.workspace["relationships"] if row["predicate"] == "ASSOCIATED_WITH"]
        self.assertEqual(len(associations), 2)
        for row in associations:
            self.assertEqual(row["symmetry"], "SYMMETRIC")
            self.assertFalse(row["causalClaim"])
            self.assertLess(row["sourceEntityId"], row["targetEntityId"])

    def test_moderation_does_not_infer_edges(self):
        moderation = [row for row in self.workspace["relationships"] if row["relationFamily"] == "MODERATION"]
        self.assertEqual(len(moderation), 1)
        self.assertEqual(moderation[0]["moderatedRelationshipId"], "REL-BIO-002")
        self.assertIsNone(moderation[0]["sourceEntityId"])
        self.assertFalse(moderation[0]["causalClaim"])

    def test_temporal_and_pathway_thresholds_are_not_bypassed(self):
        self.assertFalse(any(row["predicate"] in {"PRECEDES", "TRANSITIONS_TO"} for row in self.workspace["relationships"]))
        self.assertEqual(self.workspace["causalPathways"], [])
        self.assertEqual(self.manifest["relationshipResearch"]["temporalCandidates"], 0)
        self.assertEqual(self.manifest["relationshipResearch"]["pathwayCandidates"], 0)

    def test_canonical_baseline_hashes_and_counts_are_unchanged(self):
        baseline = self.manifest["baseline"]
        self.assertEqual(
            canonical_lf_sha256(ROOT / "data" / "entities.json"),
            baseline["entityDatasetCanonicalLfSha256"],
        )
        self.assertEqual(
            canonical_lf_sha256(ROOT / "data" / "relationships.json"),
            baseline["relationshipDatasetCanonicalLfSha256"],
        )
        self.assertEqual(
            canonical_lf_sha256(ROOT / "data" / "sources.json"),
            baseline["sourceRegister"]["canonicalLfSha256"],
        )
        counts = V1.validate_repository()
        self.assertEqual(counts["entities"], 811)
        self.assertEqual(counts["activeRelationships"], 450)
        self.assertEqual(counts["activeCausalRelationships"], 431)

    def test_builder_is_deterministic(self):
        before = (WORKSPACE.read_bytes(), MANIFEST.read_bytes())
        result = subprocess.run(
            [sys.executable, str(MATERIALIZER)],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        self.assertIn("GOV-BIO-F01-001-2026-09-05", result.stdout)
        after = (WORKSPACE.read_bytes(), MANIFEST.read_bytes())
        self.assertEqual(before, after)

    def test_required_review_documents_exist(self):
        for name in self.manifest["documents"]:
            path = PILOT_DIR / name
            self.assertTrue(path.is_file(), name)
            self.assertGreater(path.stat().st_size, 100, name)


if __name__ == "__main__":
    unittest.main()
