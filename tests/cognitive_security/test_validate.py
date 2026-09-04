from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest

from scripts.cognitive_security.episode_products import validate_frozen_summaries
from scripts.cognitive_security.export import PUBLIC_FIELDS, _public_qa_report
from scripts.cognitive_security.normalize import _exact_name_key
from scripts.cognitive_security.transcript_summaries import (
    is_single_why_sentence,
    validate_public_transcript_summaries,
    why_sentence_count,
)
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


def minimal_public_reconciliation() -> dict[str, object]:
    return {
        "schemaVersion": "1.1",
        "methodVersion": "1.0",
        "status": "complete",
        "counts": {
            "canonicalEpisodes": 0,
            "originalSourceIdentities": 0,
            "confirmedAliasGroups": 0,
            "sourceIdentitiesInConfirmedAliasGroups": 0,
            "excludedConfirmedAliasSourceIdentities": 0,
            "excludedNonEpisodeSourceIdentities": 0,
            "likelyAliasSourceIdentities": 0,
            "ambiguousSourceIdentities": 0,
            "unresolvedSourceIdentities": 0,
            "pendingDecisionRecords": 0,
            "originalItems": 0,
            "reconciledSensitivityItems": 0,
            "originalFocalItems": 0,
            "reconciledSensitivityFocalItems": 0,
            "originalContextualItems": 0,
            "reconciledSensitivityContextualItems": 0,
        },
        "interpretation": "Aggregate fixture.",
        "reanalysisRecommendation": "partial-count-and-coverage-remediation-warranted",
        "automaticRules": [],
        "limitations": [],
    }


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
    def test_public_qa_projection_preserves_private_source_provenance(self) -> None:
        dataset = {
            "artifacts": [
                {
                    "artifactId": "ART-tensions",
                    "fileName": "tensions_debates_rebuilt.xlsx",
                    "sha256": "f" * 64,
                }
            ]
        }
        private_qa = {
            "sourceHashes": {"tensions_debates_rebuilt.xlsx": "f" * 64},
            "sourceRowCounts": {
                "tensions_debates_rebuilt.xlsx": {
                    "Tensions Debates": 31,
                    "Tension Mapping": 301,
                }
            },
            "canonicalSourceDecisions": {
                "tensions": "tensions_debates_rebuilt.xlsx",
                "blankCopiedSourceTensions": "intentionally-not-used",
            },
        }
        before = copy.deepcopy(private_qa)
        public_qa = _public_qa_report(dataset, private_qa)

        self.assertEqual(before, private_qa)
        self.assertNotIn("sourceHashes", public_qa)
        self.assertNotIn("sourceRowCounts", public_qa)
        self.assertEqual(
            [
                {
                    "artifactId": "ART-tensions",
                    "canonicalRole": "canonical-tensions-and-debates",
                    "worksheetCount": 2,
                    "aggregateRowCount": 332,
                    "integrityVerified": True,
                }
            ],
            public_qa["sourceArtifactQa"],
        )
        self.assertEqual(
            "ART-tensions",
            public_qa["canonicalSourceDecisions"]["tensionsArtifactId"],
        )

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
        payloads["corpus_reconciliation.json"] = minimal_public_reconciliation()
        self.assertEqual(validate_public_payloads(payloads), [])

    def test_forbidden_public_fields_and_unknown_fields_fail(self) -> None:
        payloads = {
            "corpus_reconciliation.json": minimal_public_reconciliation(),
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

    def test_public_source_metadata_requires_opaque_ids_and_safe_aggregates(self) -> None:
        payloads = {
            "manifest.json": {
                "sourceArtifacts": [
                    {
                        "artifactId": "ART-tensions",
                        "canonicalRole": "canonical-tensions-and-debates",
                    }
                ]
            },
            "qa_report.json": {
                "sourceArtifactQa": [
                    {
                        "artifactId": "ART-tensions",
                        "canonicalRole": "canonical-tensions-and-debates",
                        "worksheetCount": 8,
                        "aggregateRowCount": 1400,
                        "integrityVerified": True,
                    }
                ]
            },
        }
        report = validate_public_outputs(payloads)
        self.assertTrue(report.passed, [issue.as_dict() for issue in report.errors])

        invalid = copy.deepcopy(payloads)
        invalid["manifest.json"]["sourceArtifacts"][0].update(
            {
                "fileName": "tensions_debates_rebuilt.xlsx",
                "sha256": "f" * 64,
            }
        )
        invalid["qa_report.json"]["sourceHashes"] = {
            "tensions_debates_rebuilt.xlsx": "f" * 64
        }
        invalid["qa_report.json"]["localReference"] = (
            r"C:\private\tensions_debates_rebuilt.xlsx"
        )
        invalid_report = validate_public_outputs(invalid)
        codes = {issue.code for issue in invalid_report.errors}
        self.assertIn("forbidden_public_field", codes)
        self.assertIn("private_source_filename_published", codes)
        self.assertIn("private_source_fingerprint_published", codes)
        self.assertIn("local_path_value_published", codes)
        self.assertIn("public_source_artifact_shape_invalid", codes)
        self.assertIn("private_source_qa_published", codes)

    def test_public_relationship_types_and_endpoints_are_canonical(self) -> None:
        payloads = {
            "corpus_reconciliation.json": minimal_public_reconciliation(),
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

    def test_public_episode_summary_grounding_contract_is_enforced(self) -> None:
        payloads = {
            "episodes.json": [
                {
                    "episodeId": "EP-1",
                    "episodeTitle": "Grounded episode",
                    "parsedEpisodeNumber": 1,
                    "reconciledSensitivityItemCount": 6,
                }
            ],
            "episode_summaries.json": [
                {
                    "episodeId": "EP-1",
                    "episodeNumber": 1,
                    "episodeTitle": "Grounded episode",
                    "summary": " ".join(["grounded"] * 100),
                    "keyTopics": ["Topic one", "Topic two", "Topic three"],
                    "whyItMatters": (
                        "This synthesis explains why the grounded episode discourse matters "
                        "to practitioners."
                    ),
                    "summaryMethod": "transcript-grounded-synthesis-v1",
                    "transcriptWordCount": 6000,
                    "summaryWordCount": 100,
                }
            ],
        }
        report = validate_public_outputs(payloads)
        self.assertTrue(report.passed, [issue.as_dict() for issue in report.errors])

        invalid = copy.deepcopy(payloads)
        summary = invalid["episode_summaries.json"][0]
        summary["summary"] = "Too short."
        summary["keyTopics"] = ["Duplicate", "duplicate", "Third topic"]
        summary["whyItMatters"] = "Too short. It is also two sentences."
        summary["episodeNumber"] = 2
        summary["episodeTitle"] = "Wrong episode"
        summary["transcriptWordCount"] = 0
        summary["summaryMethod"] = "unreviewed-method"
        invalid_report = validate_public_outputs(invalid)
        codes = {issue.code for issue in invalid_report.errors}
        self.assertIn("episode_summary_word_count_invalid", codes)
        self.assertIn("episode_summary_reported_word_count_invalid", codes)
        self.assertIn("episode_summary_topics_duplicate", codes)
        self.assertIn("episode_summary_why_it_matters_invalid", codes)
        self.assertIn("episode_summary_transcript_count_invalid", codes)
        self.assertIn("episode_summary_number_mismatch", codes)
        self.assertIn("episode_summary_title_mismatch", codes)
        self.assertIn("episode_summary_method_invalid", codes)

    def test_public_reconciliation_rejects_pair_level_identity_detail(self) -> None:
        payload = minimal_public_reconciliation()
        payload["sourceIdentityId"] = "EPI-PRIVATE"
        report = validate_public_outputs({"corpus_reconciliation.json": payload})
        codes = {issue.code for issue in report.errors}
        self.assertIn("public_reconciliation_field_not_allowlisted", codes)
        self.assertIn("private_reconciliation_detail_published", codes)

    @unittest.skipUnless(PUBLIC_DIR.is_dir(), "public package has not been built")
    def test_real_public_package_has_no_private_fields_or_xlsx_blobs(self) -> None:
        payloads = {
            path.name: json.loads(path.read_text(encoding="utf-8"))
            for path in PUBLIC_DIR.glob("*.json")
        }
        if payloads.get("manifest.json", {}).get("schemaVersion") == "2.0":
            self.skipTest(
                "Canonical schema 2.0 is validated by test_canonical_public.py."
            )
        report = validate_public_outputs(payloads)
        self.assertTrue(report.passed, [issue.as_dict() for issue in report.errors])
        qa = payloads["qa_report.json"]
        manifest = payloads["manifest.json"]
        self.assertNotIn("sourceHashes", qa)
        self.assertNotIn("sourceRowCounts", qa)
        self.assertEqual(
            {row["artifactId"] for row in manifest["sourceArtifacts"]},
            {row["artifactId"] for row in qa["sourceArtifactQa"]},
        )
        self.assertTrue(
            all(
                set(row) == {"artifactId", "canonicalRole"}
                for row in manifest["sourceArtifacts"]
            )
        )
        serialized = json.dumps(payloads, ensure_ascii=False)
        self.assertNotRegex(serialized, r"(?i)\.xlsx\b")
        self.assertNotRegex(serialized, r"[A-Za-z]:[\\/]")
        self.assertTrue(
            all(
                comparison.get("status") == "pass"
                for comparison in qa["expectedVsActual"].values()
            ),
            qa["expectedVsActual"],
        )
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


class EpisodeSummaryContractTests(unittest.TestCase):
    @staticmethod
    def _fixtures() -> tuple[list[dict], list[dict], dict[str, int]]:
        episodes = []
        summaries = []
        transcript_words_by_id = {}
        for index in range(1, 243):
            episode_id = f"EP-{index:03d}"
            episode_number = index if index < 242 else None
            episode_title = f"Grounded episode {index}"
            transcript_words = 6000 + index
            episodes.append(
                {
                    "episodeId": episode_id,
                    "episodeTitle": episode_title,
                    "parsedEpisodeNumber": episode_number,
                }
            )
            summaries.append(
                {
                    "episodeId": episode_id,
                    "episodeNumber": episode_number,
                    "episodeTitle": episode_title,
                    "summary": " ".join(
                        [f"episode{index}"] + ["grounded"] * 99
                    ),
                    "keyTopics": ["Topic one", "Topic two", "Topic three"],
                    "whyItMatters": (
                        "This U.S. synthesis helps practitioners understand episode risks "
                        "and make careful decisions."
                    ),
                    "summaryMethod": "transcript-grounded-synthesis-v1",
                    "transcriptWordCount": transcript_words,
                    "summaryWordCount": 100,
                }
            )
            transcript_words_by_id[episode_id] = transcript_words
        return episodes, summaries, transcript_words_by_id

    def _assert_rejected_everywhere(
        self,
        mutation,
        central_error_code: str,
        *,
        index: int = 0,
    ) -> None:
        episodes, summaries, transcript_words_by_id = self._fixtures()
        candidate = copy.deepcopy(summaries[index])
        mutation(candidate)

        report = validate_public_outputs(
            {
                "episodes.json": [episodes[index]],
                "episode_summaries.json": [copy.deepcopy(candidate)],
            }
        )
        self.assertIn(
            central_error_code,
            {issue.code for issue in report.errors},
            [issue.as_dict() for issue in report.errors],
        )
        with self.assertRaises(ValueError):
            validate_frozen_summaries(
                [copy.deepcopy(candidate)],
                [episodes[index]],
            )
        summaries[index] = candidate
        with self.assertRaises(ValueError):
            validate_public_transcript_summaries(
                summaries,
                episodes,
                transcript_words_by_id,
            )

    def test_valid_exact_contract_is_accepted_by_all_three_validators(self) -> None:
        episodes, summaries, transcript_words_by_id = self._fixtures()
        public_report = validate_public_outputs(
            {
                "episodes.json": [episodes[0]],
                "episode_summaries.json": [summaries[0]],
            }
        )
        self.assertTrue(
            public_report.passed,
            [issue.as_dict() for issue in public_report.errors],
        )
        self.assertEqual(
            1,
            len(validate_frozen_summaries([summaries[0]], [episodes[0]])),
        )
        self.assertEqual(
            242,
            len(
                validate_public_transcript_summaries(
                    summaries,
                    episodes,
                    transcript_words_by_id,
                )
            ),
        )

    def test_sentence_rule_requires_one_terminal_boundary(self) -> None:
        for value in (
            "This U.S. synthesis helps practitioners understand grounded risks and make careful decisions.",
            "This synthesis helps practitioners understand grounded risks and make careful decisions?!",
            "This synthesis helps practitioners understand grounded risks and make careful decisions.\u201d",
            "This synthesis helps practitioners understand grounded risks and make careful decisions?)",
        ):
            with self.subTest(value=value):
                self.assertTrue(is_single_why_sentence(value))
                self.assertEqual(1, why_sentence_count(value))
        for value in (
            "This synthesis has no terminal boundary",
            "First complete sentence. Second complete sentence.",
            "This synthesis helps practitioners understand operational risks. and make better decisions",
        ):
            with self.subTest(value=value):
                self.assertFalse(is_single_why_sentence(value))
        self._assert_rejected_everywhere(
            lambda row: row.update(
                {
                    "whyItMatters": (
                        "This synthesis helps practitioners understand operational risks. "
                        "and make better decisions"
                    )
                }
            ),
            "episode_summary_why_it_matters_invalid",
        )

    def test_missing_episode_number_on_unnumbered_release_is_rejected(self) -> None:
        self._assert_rejected_everywhere(
            lambda row: row.pop("episodeNumber"),
            "episode_summary_field_set_invalid",
            index=-1,
        )

    def test_topics_must_be_an_array_of_nonblank_strings(self) -> None:
        for invalid_topics in ("ABC", ["One", "Two", "Three", ""], [1, 2, 3]):
            with self.subTest(invalid_topics=invalid_topics):
                self._assert_rejected_everywhere(
                    lambda row, value=invalid_topics: row.update(
                        {"keyTopics": value}
                    ),
                    "episode_summary_topics_type_invalid",
                )

    def test_episode_number_rejects_boolean_and_float_values(self) -> None:
        for invalid_number in (True, 1.0):
            with self.subTest(invalid_number=invalid_number):
                self._assert_rejected_everywhere(
                    lambda row, value=invalid_number: row.update(
                        {"episodeNumber": value}
                    ),
                    "episode_summary_number_type_invalid",
                )

    def test_count_fields_reject_coercible_or_boolean_values(self) -> None:
        cases = (
            ("transcriptWordCount", "6001", "episode_summary_transcript_count_invalid"),
            ("transcriptWordCount", True, "episode_summary_transcript_count_invalid"),
            ("transcriptWordCount", 6001.0, "episode_summary_transcript_count_invalid"),
            ("summaryWordCount", "100", "episode_summary_reported_word_count_invalid"),
            ("summaryWordCount", True, "episode_summary_reported_word_count_invalid"),
            ("summaryWordCount", 100.0, "episode_summary_reported_word_count_invalid"),
        )
        for field, invalid_value, expected_code in cases:
            with self.subTest(field=field, invalid_value=invalid_value):
                self._assert_rejected_everywhere(
                    lambda row, name=field, value=invalid_value: row.update(
                        {name: value}
                    ),
                    expected_code,
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
