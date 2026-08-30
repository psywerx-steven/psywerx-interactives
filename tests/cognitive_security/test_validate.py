from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest

from scripts.cognitive_security.export import PUBLIC_FIELDS
from scripts.cognitive_security.normalize import _exact_name_key
from scripts.cognitive_security.validate import (
    KNOWN_UNMAPPED_CLUSTERS,
    REQUIRED_COLLECTIONS,
    REQUIRED_WORKBOOKS,
    ValidationError,
    canonical_json_bytes,
    validate_dataset,
    validate_normalized_dataset,
    validate_public_outputs,
    validate_public_payloads,
    validate_source_protection,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = REPO_ROOT / "source-data" / "ipa-podcast"
PUBLIC_DIR = REPO_ROOT / "data" / "cognitive-security"


def minimal_dataset() -> dict[str, list[dict]]:
    dataset = {collection: [] for collection in REQUIRED_COLLECTIONS}
    dataset.update(
        {
            "artifacts": [
                {
                    "artifactId": "ART-tensions",
                    "fileName": "tensions_debates_rebuilt.xlsx",
                }
            ],
            "episodes": [
                {"episodeId": "EP-1", "artifactId": "ART-tensions"}
            ],
            "categories": [
                {"categoryId": "CAT-F", "name": "Focal", "scope": "focal"},
                {
                    "categoryId": "CAT-C",
                    "name": "Contextual",
                    "scope": "contextual",
                },
            ],
            "items": [
                {
                    "itemId": "ITEM-1",
                    "episodeId": "EP-1",
                    "categoryId": "CAT-F",
                    "scope": "focal",
                },
                {
                    "itemId": "ITEM-2",
                    "episodeId": "EP-1",
                    "categoryId": "CAT-C",
                    "scope": "contextual",
                },
            ],
            "item_tags": [
                {"itemTagId": "IT-1", "itemId": "ITEM-1", "tag": "example"}
            ],
            "clusters": [
                {
                    "clusterId": "CL-1",
                    "categoryId": "CAT-F",
                    "name": "Example cluster",
                    "definition": "A retained definition.",
                    "inclusionCriteria": "Included material.",
                    "exclusionCriteria": "Excluded material.",
                }
            ],
            "item_cluster_assignments": [
                {
                    "assignmentId": "AS-1",
                    "itemId": "ITEM-1",
                    "primaryClusterId": "CL-1",
                    "secondaryClusterId": None,
                    "reviewRequired": True,
                    "ambiguityFlag": True,
                }
            ],
            "cluster_summaries": [
                {
                    "clusterSummaryId": "CS-1",
                    "clusterId": "CL-1",
                    "summary": "Summary",
                }
            ],
            "meta_clusters": [
                {
                    "metaClusterId": "MC-1",
                    "categoryId": "CAT-F",
                    "name": "Example meta-cluster",
                }
            ],
            "cluster_meta_mappings": [
                {
                    "clusterMetaMappingId": "CMM-1",
                    "clusterId": "CL-1",
                    "metaClusterId": "MC-1",
                }
            ],
            "themes": [{"themeId": "TH-1", "name": "Theme"}],
            "theme_meta_mappings": [
                {
                    "themeMetaMappingId": "TMM-1",
                    "themeId": "TH-1",
                    "metaClusterId": "MC-1",
                }
            ],
            "theme_cluster_evidence": [
                {
                    "themeClusterEvidenceId": "TCE-1",
                    "themeId": "TH-1",
                    "clusterId": "CL-1",
                    "representativeItemIds": ["ITEM-1"],
                }
            ],
            "tensions": [
                {
                    "tensionId": "TN-1",
                    "name": "Tension",
                    "poleALabel": "Pole A",
                    "poleBLabel": "Pole B",
                    "sourceArtifactId": "ART-tensions",
                }
            ],
            "tension_mappings": [
                {
                    "tensionMappingId": "TNM-1",
                    "tensionId": "TN-1",
                    "mappedEntityType": "meta_cluster",
                    "mappedId": "MC-1",
                }
            ],
            "meta_narratives": [{"narrativeId": "N01", "name": "Narrative"}],
            "category_summaries": [
                {
                    "categorySummaryId": "CGS-1",
                    "categoryId": "CAT-F",
                    "summary": "Focal category summary.",
                    "soWhat": "Why this focal category matters.",
                }
            ],
            "category_findings": [
                {
                    "findingId": "F-1",
                    "categoryId": "CAT-F",
                    "name": "Finding",
                }
            ],
            "scenarios": [{"scenarioId": "SC-1", "name": "Scenario"}],
            "scenario_pathways": [
                {"pathwayId": "P-1", "scenarioId": "SC-1", "pathwayStep": "Step"}
            ],
            "scenario_indicators": [
                {
                    "indicatorId": "IND-1",
                    "scenarioId": "SC-1",
                    "pathwayId": "P-1",
                    "indicator": "Indicator",
                }
            ],
            "scenario_actions": [
                {
                    "actionId": "ACT-1",
                    "scenarioId": "SC-1",
                    "pathwayId": "P-1",
                    "action": "Action",
                }
            ],
            "evidence_links": [{"evidenceLinkId": "EL-1"}],
            "review_flags": [{"reviewFlagId": "RF-1"}],
        }
    )
    return dataset


class NormalizedValidationTests(unittest.TestCase):
    def test_related_tension_name_matching_is_exact_not_fuzzy(self) -> None:
        self.assertEqual(_exact_name_key("  Rights   vs Restraint  "), "rights vs restraint")
        self.assertEqual(_exact_name_key("RIGHTS VS RESTRAINT"), "rights vs restraint")
        self.assertNotEqual(_exact_name_key("Rights-vs-Restraint"), "rights vs restraint")

    def test_valid_camel_case_contract(self) -> None:
        report = validate_normalized_dataset(minimal_dataset(), expected_counts={})
        self.assertTrue(report.passed, [issue.as_dict() for issue in report.errors])
        self.assertEqual(report.counts["review_required_assignments"], 1)
        self.assertEqual(report.counts["ambiguity_flagged_assignments"], 1)
        self.assertEqual(report.counts["secondary_none"], 1)

    def test_duplicate_and_blank_ids_are_errors(self) -> None:
        dataset = minimal_dataset()
        duplicate = copy.deepcopy(dataset["items"][0])
        dataset["items"].append(duplicate)
        dataset["themes"].append({"themeId": "", "name": "Blank"})
        report = validate_normalized_dataset(dataset, expected_counts={})
        codes = {issue.code for issue in report.errors}
        self.assertIn("duplicate_id", codes)
        self.assertIn("blank_id", codes)

    def test_foreign_key_failure_is_structural(self) -> None:
        dataset = minimal_dataset()
        dataset["theme_meta_mappings"][0]["metaClusterId"] = "MISSING"
        report = validate_normalized_dataset(dataset, expected_counts={})
        self.assertTrue(any(issue.code == "missing_foreign_key" for issue in report.errors))
        with self.assertRaises(ValidationError) as caught:
            validate_dataset(dataset)
        self.assertFalse(caught.exception.report["passed"])

    def test_focal_assignment_cardinality_and_contextual_separation(self) -> None:
        dataset = minimal_dataset()
        dataset["item_cluster_assignments"].append(
            {
                "assignmentId": "AS-2",
                "itemId": "ITEM-2",
                "primaryClusterId": "CL-1",
                "secondaryClusterId": None,
            }
        )
        dataset["item_cluster_assignments"][0]["primaryClusterId"] = ""
        report = validate_normalized_dataset(dataset, expected_counts={})
        codes = {issue.code for issue in report.errors}
        self.assertIn("contextual_item_assigned_as_focal", codes)
        self.assertIn("blank_primary_assignment", codes)

    def test_secondary_none_must_be_null(self) -> None:
        dataset = minimal_dataset()
        dataset["item_cluster_assignments"][0]["secondaryClusterId"] = "NONE"
        report = validate_normalized_dataset(dataset, expected_counts={})
        self.assertTrue(
            any(issue.code == "secondary_none_not_normalized" for issue in report.errors)
        )

    def test_three_governance_known_unmapped_clusters_are_reported_not_failed(self) -> None:
        dataset = minimal_dataset()
        dataset["clusters"] = []
        dataset["cluster_summaries"] = []
        dataset["cluster_meta_mappings"] = []
        dataset["meta_clusters"] = []
        dataset["theme_meta_mappings"] = []
        dataset["item_cluster_assignments"] = []
        dataset["items"] = dataset["items"][1:]
        dataset["item_tags"] = []
        dataset["theme_cluster_evidence"] = []
        dataset["tension_mappings"] = []
        for cluster_id, name in KNOWN_UNMAPPED_CLUSTERS.items():
            dataset["clusters"].append(
                {
                    "clusterId": cluster_id,
                    "categoryId": "CAT-F",
                    "name": name,
                    "definition": "Definition",
                    "inclusionCriteria": "Inclusion",
                    "exclusionCriteria": "Exclusion",
                }
            )
        report = validate_normalized_dataset(dataset, expected_counts={})
        self.assertTrue(report.passed, [issue.as_dict() for issue in report.errors])
        self.assertEqual(
            {row["cluster_id"] for row in report.unresolved_mappings},
            set(KNOWN_UNMAPPED_CLUSTERS),
        )
        self.assertEqual(
            sum(issue.code == "known_unmapped_cluster" for issue in report.warnings), 3
        )

    def test_unresolved_reference_requires_marker_review_flag_and_provenance(self) -> None:
        dataset = minimal_dataset()
        evidence = dataset["theme_cluster_evidence"][0]
        evidence.update(
            {
                "clusterId": None,
                "unresolvedReference": True,
                "source": {
                    "artifactId": "ART-tensions",
                    "fileName": "cross_cutting_themes.xlsx",
                    "sheet": "Theme-to-Cluster Evidence",
                    "rowNumber": 164,
                },
            }
        )
        dataset["review_flags"].append(
            {
                "reviewFlagId": "RF-2",
                "entityId": "TCE-1",
                "entityType": "themeClusterEvidence",
                "flagType": "unresolvedClusterReference",
            }
        )
        report = validate_normalized_dataset(dataset, expected_counts={})
        self.assertTrue(report.passed, [issue.as_dict() for issue in report.errors])
        self.assertTrue(
            any(issue.code == "explicit_unresolved_reference" for issue in report.warnings)
        )

        without_review = copy.deepcopy(dataset)
        without_review["review_flags"] = without_review["review_flags"][:1]
        failed = validate_normalized_dataset(without_review, expected_counts={})
        self.assertTrue(
            any(issue.code == "missing_required_reference" for issue in failed.errors)
        )

    def test_count_mismatches_are_reported_without_forcing_source(self) -> None:
        report = validate_normalized_dataset(
            minimal_dataset(), expected_counts={"items": 999}
        )
        self.assertTrue(report.passed)
        self.assertEqual(report.comparisons["items"]["status"], "mismatch")
        self.assertTrue(any(issue.code == "expected_count_mismatch" for issue in report.warnings))

    def test_category_summaries_are_required_unique_and_category_bound(self) -> None:
        absent = minimal_dataset()
        absent.pop("category_summaries")
        absent_report = validate_normalized_dataset(absent, expected_counts={})
        self.assertTrue(
            any(
                issue.code == "missing_collection"
                and issue.context.get("collection") == "category_summaries"
                for issue in absent_report.errors
            )
        )

        missing = minimal_dataset()
        missing["category_summaries"] = []
        missing_report = validate_normalized_dataset(missing, expected_counts={})
        self.assertTrue(
            any(issue.code == "missing_focal_category_summary" for issue in missing_report.errors)
        )

        duplicate = minimal_dataset()
        duplicate["category_summaries"].append(
            {
                "categorySummaryId": "CGS-2",
                "categoryId": "CAT-F",
                "summary": "Duplicate",
                "soWhat": "Duplicate",
            }
        )
        duplicate_report = validate_normalized_dataset(duplicate, expected_counts={})
        self.assertTrue(
            any(
                issue.code == "duplicate_category_summary_assignment"
                for issue in duplicate_report.errors
            )
        )

        invalid_fk = minimal_dataset()
        invalid_fk["category_summaries"][0]["categoryId"] = "CAT-MISSING"
        invalid_report = validate_normalized_dataset(invalid_fk, expected_counts={})
        self.assertTrue(
            any(issue.code == "missing_foreign_key" for issue in invalid_report.errors)
        )

    def test_tension_mapping_polymorphic_targets_and_types_are_strict(self) -> None:
        valid = minimal_dataset()
        valid["tension_mappings"].append(
            {
                "tensionMappingId": "TNM-2",
                "tensionId": "TN-1",
                "mappedEntityType": "cross_cutting_theme",
                "mappedId": "TH-1",
            }
        )
        valid_report = validate_normalized_dataset(valid, expected_counts={})
        self.assertTrue(valid_report.passed, [issue.as_dict() for issue in valid_report.errors])

        unsupported = minimal_dataset()
        unsupported["tension_mappings"][0]["mappedEntityType"] = "cluster"
        unsupported_report = validate_normalized_dataset(unsupported, expected_counts={})
        self.assertTrue(
            any(
                issue.code == "unsupported_tension_mapping_type"
                for issue in unsupported_report.errors
            )
        )

        unresolved = minimal_dataset()
        unresolved["tension_mappings"][0]["mappedId"] = "MC-MISSING"
        unresolved_report = validate_normalized_dataset(unresolved, expected_counts={})
        self.assertTrue(
            any(issue.code == "missing_foreign_key" for issue in unresolved_report.errors)
        )

        missing_theme = minimal_dataset()
        missing_theme["tension_mappings"][0].update(
            {"mappedEntityType": "cross_cutting_theme", "mappedId": "XTHEME-MISSING"}
        )
        missing_theme_report = validate_normalized_dataset(
            missing_theme, expected_counts={}
        )
        self.assertTrue(
            any(issue.code == "missing_foreign_key" for issue in missing_theme_report.errors)
        )

    def test_crb_m05_empty_membership_is_explicit_governance_warning(self) -> None:
        dataset = minimal_dataset()
        dataset["meta_clusters"].append(
            {
                "metaClusterId": "CRB-M05",
                "categoryId": "CAT-F",
                "name": "Strategic synthesis lens",
            }
        )
        report = validate_normalized_dataset(dataset, expected_counts={})
        self.assertTrue(report.passed, [issue.as_dict() for issue in report.errors])
        self.assertTrue(
            any(issue.code == "known_empty_meta_cluster" for issue in report.warnings)
        )
        self.assertTrue(
            any(
                row.get("meta_cluster_id") == "CRB-M05"
                for row in report.unresolved_mappings
            )
        )


class PublicationBoundaryTests(unittest.TestCase):
    def test_exporter_projection_fields_match_validator_allowlists(self) -> None:
        filenames = {
            "categories": "categories.json",
            "clusters": "clusters.json",
            "cluster_summaries": "cluster_summaries.json",
            "meta_clusters": "meta_clusters.json",
            "themes": "themes.json",
            "tensions": "tensions.json",
            "meta_narratives": "meta_narratives.json",
            "category_findings": "category_findings.json",
            "scenarios": "scenarios.json",
            "episodes": "episodes.json",
        }
        payloads = {
            filenames[collection]: [{field: None for field in fields}]
            for collection, fields in PUBLIC_FIELDS.items()
        }
        self.assertEqual(validate_public_payloads(payloads), [])

    def test_forbidden_public_fields_and_unknown_fields_fail(self) -> None:
        payloads = {
            "clusters.json": [
                {
                    "clusterId": "CL-1",
                    "definition": "Safe",
                    "evidenceQuote": "Private quotation",
                    "modelRationale": "Private rationale",
                    "unexpectedField": "not allowlisted",
                }
            ]
        }
        report = validate_public_outputs(payloads)
        codes = {issue.code for issue in report.errors}
        self.assertIn("forbidden_public_field", codes)
        self.assertIn("public_field_not_allowlisted", codes)

    def test_public_relationship_types_and_endpoints_are_canonical(self) -> None:
        payloads = {
            "categories.json": [{"categoryId": "CAT-1", "name": "Category"}],
            "clusters.json": [
                {
                    "clusterId": "CL-1", "categoryId": "CAT-1",
                    "name": "Cluster", "definition": "Definition",
                }
            ],
            "meta_clusters.json": [
                {"metaClusterId": "MC-1", "categoryId": "CAT-1", "name": "Meta"}
            ],
            "themes.json": [{"themeId": "TH-1", "name": "Theme"}],
            "tensions.json": [
                {
                    "tensionId": "TN-1", "name": "Tension",
                    "poleALabel": "A", "poleBLabel": "B",
                }
            ],
            "relationships.json": [
                {
                    "relationshipId": "REL-1",
                    "relationshipType": "tension-maps-to-cross-cutting-theme",
                    "sourceType": "tension",
                    "sourceId": "TN-1",
                    "targetType": "theme",
                    "targetId": "TH-1",
                    "interpretation": "semantic",
                },
                {
                    "relationshipId": "REL-2",
                    "relationshipType": "tension-maps-to-meta-cluster",
                    "sourceType": "tension",
                    "sourceId": "TN-1",
                    "targetType": "metaCluster",
                    "targetId": "MC-1",
                    "interpretation": "semantic",
                },
            ],
        }
        report = validate_public_outputs(payloads)
        self.assertTrue(report.passed, [issue.as_dict() for issue in report.errors])

        invalid = copy.deepcopy(payloads)
        invalid["relationships.json"][0]["relationshipType"] = "tension-links-entity"
        invalid["relationships.json"][1]["targetId"] = "MC-MISSING"
        invalid["relationships.json"][1]["interpretation"] = "causal"
        invalid_report = validate_public_outputs(invalid)
        codes = {issue.code for issue in invalid_report.errors}
        self.assertIn("unsupported_public_relationship_type", codes)
        self.assertIn("public_relationship_endpoint_unresolved", codes)
        self.assertIn("public_relationship_not_semantic", codes)

    @unittest.skipUnless(PUBLIC_DIR.is_dir(), "public package has not been built")
    def test_real_public_package_has_no_private_fields_or_xlsx_blobs(self) -> None:
        payloads = {
            path.name: json.loads(path.read_text(encoding="utf-8"))
            for path in PUBLIC_DIR.glob("*.json")
        }
        report = validate_public_outputs(payloads)
        self.assertTrue(report.passed, [issue.as_dict() for issue in report.errors])
        qa = payloads["qa_report.json"]
        self.assertTrue(
            any("known_empty_meta_cluster" in warning for warning in qa["warnings"])
        )
        self.assertTrue(
            any(
                row.get("metaClusterId") == "CRB-M05"
                and row.get("governanceStatus") == "known-empty-source-membership"
                for row in qa["unresolvedMappings"]
            )
        )


class SourceProtectionAndDeterminismTests(unittest.TestCase):
    @unittest.skipUnless(SOURCE_DIR.is_dir(), "ignored source package is not present")
    def test_required_workbooks_present_hashed_and_untracked(self) -> None:
        report = validate_source_protection(REPO_ROOT, SOURCE_DIR)
        self.assertTrue(report.passed, [issue.as_dict() for issue in report.errors])
        self.assertEqual(report.counts["present_workbooks"], len(REQUIRED_WORKBOOKS))
        self.assertEqual(report.counts["tracked_xlsx_files"], 0)
        for filename in REQUIRED_WORKBOOKS:
            digest = hashlib.sha256((SOURCE_DIR / filename).read_bytes()).hexdigest()
            self.assertRegex(digest, r"^[0-9a-f]{64}$")

    def test_canonical_serialization_is_byte_deterministic(self) -> None:
        first = {"z": [3, 2, 1], "a": {"y": "café", "x": 1}}
        second = {"a": {"x": 1, "y": "café"}, "z": [3, 2, 1]}
        self.assertEqual(canonical_json_bytes(first), canonical_json_bytes(second))
        self.assertTrue(canonical_json_bytes(first).endswith(b"\n"))


if __name__ == "__main__":
    unittest.main()
