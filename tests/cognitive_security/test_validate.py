from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest

from scripts.cognitive_security.export import PUBLIC_FIELDS
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
                    "mappingType": "cluster",
                    "mappedId": "CL-1",
                }
            ],
            "meta_narratives": [{"narrativeId": "N01", "name": "Narrative"}],
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

    @unittest.skipUnless(PUBLIC_DIR.is_dir(), "public package has not been built")
    def test_real_public_package_has_no_private_fields_or_xlsx_blobs(self) -> None:
        payloads = {
            path.name: json.loads(path.read_text(encoding="utf-8"))
            for path in PUBLIC_DIR.glob("*.json")
        }
        report = validate_public_outputs(payloads)
        self.assertTrue(report.passed, [issue.as_dict() for issue in report.errors])


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
