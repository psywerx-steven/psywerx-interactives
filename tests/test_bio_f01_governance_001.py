import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "relationship-intervention-v1"
CANDIDATES = ROOT / "data" / "candidates" / "relationship-intervention-v1" / "workspace.json"
PILOT = ROOT / "docs" / "governance" / "pilots" / "BIO-F01"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load(path: Path, key: str):
    return json.loads(path.read_text(encoding="utf-8"))[key]


V1 = load_module(
    "relationship_intervention_v1_for_bio_f01_governance",
    ROOT / "scripts" / "relationship_intervention_v1.py",
)


class BioF01Governance001Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schemas = V1.SchemaSet()
        cls.catalog = V1.Catalog.from_repository()
        cls.relationships = load(DATA / "relationships.json", "relationships")
        cls.evidence = load(DATA / "evidence-assessments.json", "evidenceAssessments")
        cls.pathways = load(DATA / "causal-pathways.json", "causalPathways")
        cls.interventions = load(DATA / "interventions.json", "interventions")
        cls.effects = load(DATA / "intervention-effects.json", "interventionEffects")
        cls.sources = load(DATA / "source-register.json", "sources")
        cls.materialization = json.loads((DATA / "materialization-manifest.json").read_text(encoding="utf-8"))
        cls.workspace = json.loads(CANDIDATES.read_text(encoding="utf-8"))

    def test_native_store_validates_and_exact_counts_are_frozen(self):
        counts = V1.validate_repository()
        self.assertEqual(counts["nativeSources"], 20)
        self.assertEqual(counts["nativeRelationships"], 6)
        self.assertEqual(counts["nativeCausalRelationships"], 4)
        self.assertEqual(counts["nativeInterventions"], 9)
        self.assertEqual(counts["nativeInterventionEffects"], 5)
        self.assertEqual(counts["nativeEvidenceAssessments"], 11)
        self.assertEqual(counts["nativeActiveRecords"], 27)
        self.assertEqual(counts["nativeActiveRelationships"], 6)
        self.assertEqual(counts["nativeActiveCausalRelationships"], 4)
        self.assertEqual(counts["nativeActiveInterventions"], 5)
        self.assertEqual(counts["nativeActiveInterventionEffects"], 5)
        self.assertEqual(counts["nativeActiveEvidenceAssessments"], 11)

    def test_all_new_scientific_records_are_governed_with_exact_activation_split(self):
        all_records = self.relationships + self.evidence + self.pathways + self.interventions + self.effects
        self.assertEqual(len(all_records), 31)
        self.assertTrue(all(row["governance"]["lifecycleStatus"] == "GOVERNED" for row in all_records))
        self.assertEqual(sum(row["governance"]["activationStatus"] == "ACTIVE" for row in all_records), 27)
        self.assertEqual(sum(row["governance"]["activationStatus"] == "INACTIVE" for row in all_records), 4)
        self.assertTrue(all(row["governance"]["authorizedBy"] == "authorized human governor" for row in all_records))

    def test_only_active_causal_records_enter_traversal(self):
        causal = [row for row in self.relationships if row["relationFamily"] == "CAUSAL"]
        self.assertEqual(len(causal), 4)
        self.assertEqual({row["id"] for row in V1.causal_traversal(self.relationships)}, {row["id"] for row in causal})
        self.assertTrue(all(row["compatibility"]["v1Executability"] == "EXECUTABLE" for row in causal))
        self.assertNotIn("REL-V1-BIO-F01-005", {row["id"] for row in V1.causal_traversal(self.relationships)})
        self.assertNotIn("REL-V1-BIO-F01-006", {row["id"] for row in V1.causal_traversal(self.relationships)})

    def test_required_relationship_candidates_remain_non_governed(self):
        by_id = {row["id"]: row for row in self.workspace["relationships"]}
        expected = {
            "REL-CAND-BIO-F01-005",
            "REL-CAND-BIO-F01-007",
            "REL-CAND-BIO-F01-008",
        }
        self.assertEqual(
            {identifier for identifier in expected if by_id[identifier]["governance"]["lifecycleStatus"] == "RESEARCH_NEEDED"},
            expected,
        )
        self.assertTrue(all(by_id[identifier]["governance"]["activationStatus"] == "NOT_ELIGIBLE" for identifier in expected))

    def test_required_effect_candidates_remain_non_governed(self):
        by_id = {row["id"]: row for row in self.workspace["interventionEffects"]}
        expected = {
            "IE-CAND-BIO-F01-002",
            "IE-CAND-BIO-F01-007",
            "IE-CAND-BIO-F01-008",
            "IE-CAND-BIO-F01-009",
        }
        self.assertTrue(all(by_id[identifier]["governance"]["lifecycleStatus"] == "RESEARCH_NEEDED" for identifier in expected))
        self.assertTrue(all(by_id[identifier]["governance"]["activationStatus"] == "NOT_ELIGIBLE" for identifier in expected))

    def test_acoustic_umbrella_cannot_be_governed(self):
        by_id = {row["id"]: row for row in self.workspace["interventions"]}
        self.assertEqual(by_id["INT-CAND-BIO-F01-009"]["governance"]["lifecycleStatus"], "RESEARCH_NEEDED")
        self.assertIn("umbrella", by_id["INT-CAND-BIO-F01-009"]["description"].casefold())
        self.assertEqual(by_id["INT-CAND-BIO-F01-011"]["governance"]["lifecycleStatus"], "RESEARCH_NEEDED")
        effect = next(row for row in self.workspace["interventionEffects"] if row["id"] == "IE-CAND-BIO-F01-007")
        self.assertEqual(effect["interventionId"], "INT-CAND-BIO-F01-011")
        self.assertNotIn("INT-V1-BIO-F01-009", {row["id"] for row in self.interventions})

    def test_cbti_package_is_explicitly_non_exhaustive(self):
        by_id = {row["id"]: row for row in self.interventions}
        package = by_id["INT-V1-BIO-F01-006"]
        self.assertEqual(package["interventionKind"], "PACKAGE")
        self.assertEqual(package["componentInterventionIds"], ["INT-V1-BIO-F01-004", "INT-V1-BIO-F01-005"])
        folded = package["description"].casefold()
        self.assertIn("not as an exhaustive", folded)
        self.assertIn("package effects require separate evidence", folded)

    def test_circadian_relationship_is_not_universal_monotonic(self):
        record = next(row for row in self.relationships if row["id"] == "REL-V1-BIO-F01-002")
        self.assertEqual(record["polarity"], "CONTEXT_DEPENDENT")
        self.assertEqual(record["functionalForm"]["kind"], "CYCLIC_STATE_DEPENDENT")
        text = (record["mechanism"] + " " + record["boundaryConditions"]).casefold()
        self.assertIn("cyclic", text)
        self.assertIn("not wall-clock time", text)
        self.assertIn("no global monotonic", record["functionalForm"]["specification"].casefold())

    def test_rds_direct_intervention_target_remains_impossible(self):
        for effect in self.effects + self.workspace["interventionEffects"]:
            self.assertEqual(effect["targetKind"], "DRIVER")
            entity = self.catalog.entities[effect["targetDriverId"]]
            self.assertEqual(entity["entityType"], "DRIVER")

    def test_no_unapproved_rds_causal_edge_or_pathway_was_created(self):
        rds = {identifier for identifier, row in self.catalog.entities.items() if row["entityType"] == "RELATIONAL_DERIVED_STATE"}
        causal = [row for row in self.relationships if row["relationFamily"] == "CAUSAL"]
        self.assertTrue(all(row["sourceEntityId"] not in rds and row["targetEntityId"] not in rds for row in causal))
        self.assertEqual(self.pathways, [])
        self.assertFalse(any(row["relationFamily"] == "MODERATION" for row in self.relationships))

    def test_rejected_hypotheses_are_not_regenerated(self):
        records = self.relationships + self.workspace["relationships"]
        forbidden_causal = {
            ("BIO-001", "RDS-0003"),
            ("BIO-001", "RDS-0004"),
            ("BIO-074", "RDS-0003"),
            ("BIO-074", "RDS-0004"),
        }
        self.assertFalse(any(row["relationFamily"] == "CAUSAL" and (row["sourceEntityId"], row["targetEntityId"]) in forbidden_causal for row in records))
        self.assertFalse(any(row["predicate"] == "TRANSITIONS_TO" and {row["sourceEntityId"], row["targetEntityId"]} == {"BIO-001", "BIO-005"} for row in records))
        self.assertFalse(any(row["sourceEntityId"] == "BIO-003" and row["targetEntityId"] == "BIO-001" for row in self.relationships))
        rejected = self.materialization["rejectedHypotheses"]
        self.assertEqual([row["decisionId"] for row in rejected], [f"BIOF01-D-H0{i}" for i in range(1, 6)])

    def test_sources_are_verified_unique_and_resolvable(self):
        self.assertEqual(len(self.sources), 20)
        self.assertEqual(len({row["id"] for row in self.sources}), 20)
        self.assertEqual(len({row["pmid"] for row in self.sources}), 20)
        self.assertEqual(len({row["doi"].casefold() for row in self.sources}), 20)
        for source in self.sources:
            self.schemas.validate("source", source)
            self.assertIn(source["id"], self.catalog.source_ids)
            self.assertEqual(source["verification"]["status"], "VERIFIED")

    def test_candidate_to_canonical_lineage_is_exact(self):
        lineage = self.materialization["candidateLineage"]
        self.assertEqual(len(lineage), 20)
        candidates = {
            row["id"]
            for key in ("relationships", "interventions", "interventionEffects")
            for row in self.workspace[key]
        }
        canonical = {row["id"] for row in self.relationships + self.interventions + self.effects}
        self.assertTrue(all(row["candidateId"] in candidates for row in lineage))
        self.assertTrue(all(row["canonicalId"] in canonical for row in lineage))
        statuses = {row["canonicalId"]: row["status"] for row in lineage}
        inactive = {"INT-V1-BIO-F01-002", "INT-V1-BIO-F01-004", "INT-V1-BIO-F01-005", "INT-V1-BIO-F01-010"}
        self.assertTrue(all(statuses[identifier] == "MATERIALIZED_AS_GOVERNED_INACTIVE" for identifier in inactive))
        self.assertTrue(all(status == "MATERIALIZED_AS_GOVERNED_ACTIVE" for identifier, status in statuses.items() if identifier not in inactive))

    def test_existing_production_baseline_is_unchanged(self):
        counts = V1.validate_repository()
        self.assertEqual(counts["entities"], 811)
        self.assertEqual(counts["legacyActiveRelationships"], 450)
        self.assertEqual(counts["legacyActiveCausalRelationships"], 431)
        self.assertEqual(counts["activeRelationships"], 456)
        self.assertEqual(counts["activeCausalRelationships"], 435)

    def test_revision_proposals_are_review_only(self):
        text = (PILOT / "BIO_F01_EXISTING_RELATIONSHIP_REVISION_PROPOSALS.md").read_text(encoding="utf-8")
        for suffix in range(1, 6):
            self.assertIn(f"REL-REV-BIO-F01-B0{suffix}", text)
        self.assertIn("Nothing in this document mutates, supersedes, or deactivates", text)


if __name__ == "__main__":
    unittest.main()
