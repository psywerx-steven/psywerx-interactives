"""Governance tests for the private canonical re-synthesis overlay."""

from __future__ import annotations

import json
import unittest
from collections import Counter
from pathlib import Path

from scripts.cognitive_security.canonical_resynthesis import (
    RELATIONSHIP_SEMANTICS,
    SUPPORT_INTERPRETATION,
    _require_git_ignored_output,
    _support_profile,
    _validated_family_adjudication_index,
    _validated_split_allocation_index,
    _validated_tension_adjudication_index,
    build_canonical_resynthesis,
    build_corpus_selection,
)
from scripts.cognitive_security.reconcile import GOVERNED_DISTINCT_PUBLICATION_REUSES

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "analysis" / "cognitive-security" / "canonical-resynthesis"


class CanonicalSelectionRuleTests(unittest.TestCase):
    def setUp(self) -> None:
        reuse_rule = GOVERNED_DISTINCT_PUBLICATION_REUSES[0]
        self.original = str(reuse_rule["originalSourceIdentityId"])
        self.reuse = str(reuse_rule["reuseSourceIdentityId"])
        self.alias = "EPI-ALIAS"
        self.dataset = {
            "episode_source_identities": [
                {"sourceIdentityId": self.original, "identityKind": "modern-numbered"},
                {"sourceIdentityId": self.reuse, "identityKind": "re-release"},
                {"sourceIdentityId": self.alias, "identityKind": "legacy-numbered"},
            ],
            "episode_source_mappings": [
                {
                    "sourceIdentityId": self.original,
                    "canonicalEpisodeId": self.original,
                    "mappingRole": "canonical",
                    "mappingStatus": "confirmed-alias",
                    "collapseEligible": False,
                },
                {
                    "sourceIdentityId": self.reuse,
                    "canonicalEpisodeId": self.reuse,
                    "mappingRole": "canonical",
                    "mappingStatus": "unique",
                    "collapseEligible": False,
                },
                {
                    "sourceIdentityId": self.alias,
                    "canonicalEpisodeId": self.original,
                    "mappingRole": "alias",
                    "mappingStatus": "confirmed-alias",
                    "collapseEligible": True,
                },
            ],
            "episodes": [
                {
                    "episodeId": self.original,
                    "canonicalSourceIdentityId": self.original,
                },
                {
                    "episodeId": self.reuse,
                    "canonicalSourceIdentityId": self.reuse,
                },
            ],
            "items": [
                {
                    "itemId": "1",
                    "sourceIdentityId": self.original,
                    "scope": "focal",
                    "categoryId": "CAT-1",
                },
                {
                    "itemId": "2",
                    "sourceIdentityId": self.reuse,
                    "scope": "focal",
                    "categoryId": "CAT-1",
                },
                {
                    "itemId": "3",
                    "sourceIdentityId": self.alias,
                    "scope": "contextual",
                    "categoryId": "CAT-2",
                },
            ],
        }

    def test_selection_separates_identity_release_and_content_units(self) -> None:
        selection, report, selected_items, releases = build_corpus_selection(
            self.dataset,
            {
                "status": "pass",
                "coverageComplete": True,
                "strictUniqueContentUnits": 1,
            },
        )
        self.assertEqual({"1"}, selected_items)
        self.assertEqual(2, report["counts"]["publicReleaseCount"])
        self.assertEqual(1, report["counts"]["canonicalAnalyticalContentUnitCount"])
        self.assertEqual({self.original, self.reuse}, releases[self.original])
        reuse_release = next(
            row
            for row in selection["publicReleaseContentMap"]
            if row["publicReleaseId"] == self.reuse
        )
        self.assertFalse(reuse_release["contributesAnalyticalWeight"])
        self.assertEqual(
            "shared-content-inheritance", reuse_release["relationshipRole"]
        )
        self.assertEqual(
            {"direct-content-representation"},
            {
                row["relationshipRole"]
                for row in selection["publicReleaseContentMap"]
                if row["contributesAnalyticalWeight"]
            },
        )

    def test_alias_status_does_not_exclude_canonical_side(self) -> None:
        selection, _, _, _ = build_corpus_selection(self.dataset, {})
        identity = {
            row["sourceIdentityId"]: row
            for row in selection["historicalIdentitySelection"]
        }
        self.assertTrue(identity[self.original]["contributesAnalyticalWeight"])
        self.assertFalse(identity[self.alias]["contributesAnalyticalWeight"])

    def test_support_profile_counts_inherited_release_only_as_discovery(self) -> None:
        item = self.dataset["items"][0]
        profile = _support_profile(
            {"1"},
            historical_item_ids={"1"},
            direct_item_ids={"1"},
            item_by_id={"1": item},
            release_by_content={self.original: {self.original, self.reuse}},
            cluster_ids={"CL-1"},
            family_ids={"F-1"},
            adjudication_status="fixture",
        )
        self.assertEqual(1, profile["uniqueContentUnitSupportCount"])
        self.assertEqual(2, profile["publicReleaseCoverageCount"])
        self.assertEqual(1, profile["inheritedPublicReleaseCoverageCount"])
        self.assertEqual(1, profile["itemSupportCount"])

    def test_support_profile_can_limit_category_breadth_to_direct_evidence(
        self,
    ) -> None:
        items = {
            "1": {
                "itemId": "1",
                "sourceIdentityId": "S-1",
                "scope": "focal",
                "categoryId": "DIRECT",
            },
            "2": {
                "itemId": "2",
                "sourceIdentityId": "S-2",
                "scope": "focal",
                "categoryId": "CONCEPTUAL",
            },
        }
        profile = _support_profile(
            {"1", "2"},
            historical_item_ids={"1", "2"},
            direct_item_ids={"1"},
            category_item_ids={"1"},
            item_by_id=items,
            release_by_content={"S-1": {"R-1"}, "S-2": {"R-2"}},
            cluster_ids={"CL-1", "CL-2"},
            family_ids={"F-1", "F-2"},
            adjudication_status="fixture",
        )
        self.assertEqual(1, profile["categoryBreadth"])
        self.assertEqual(1, profile["directSupportItemCount"])
        self.assertEqual(1, profile["derivedSupportItemCount"])


class CanonicalGovernanceVocabularyTests(unittest.TestCase):
    @staticmethod
    def _tension_validation_fixture():
        seed = {
            "id": "CT-X",
            "name": "Fixture tension",
            "type": "fixture",
            "definition": "Governed definition",
            "poleA": "Pole A",
            "poleB": "Pole B",
            "legacy": ["TD-001"],
        }
        occurrence = {
            "canonicalTensionId": "CT-X",
            "historicalTensionId": "TD-001",
            "analyticalSupportWeight": 1.0,
            "itemId": "I-1",
        }
        item_by_id = {
            "I-1": {
                "sourceIdentityId": "S-1",
                "scope": "focal",
                "categoryId": "CAT-1",
            }
        }
        adjudication = {
            "schemaVersion": "1.0.0",
            "methodVersion": "canonical-tension-construct-adjudication-v1",
            "adjudicationStatus": "analyst-reviewed-private-governed-input",
            "scope": "Fixture governance.",
            "decisionPolicy": {
                "proposedCountIsBinding": False,
                "allowedDecisions": ["retain", "merge", "split", "reject"],
                "retentionRequiresBothPolesAndDistinctBoundaries": True,
                "reviewFlagsAreNonBlockingButRequireHumanConfirmation": True,
            },
            "evidenceAccounting": {
                "occurrenceCountsIncludePositiveWeightLineageRows": True,
                "analyticalWeightsRespectOneUnitPerCanonicalItem": True,
                "uniqueItemsAreGloballySingleUseAcrossTensions": True,
                "sourceConcentrationIsALimitationNotAValidityScore": True,
            },
            "records": [
                {
                    "canonicalTensionId": "CT-X",
                    "name": "Fixture tension",
                    "tensionType": "fixture",
                    "definition": "Governed definition",
                    "poleALabel": "Pole A",
                    "poleBLabel": "Pole B",
                    "decision": "retain",
                    "confidence": "high",
                    "reviewRequired": False,
                    "reviewFlags": [],
                    "rationale": "The fixture rationale is governed.",
                    "historicalTensionIds": ["TD-001"],
                    "proposedHistoricalTensionIds": ["TD-001"],
                }
            ],
        }
        return seed, occurrence, item_by_id, adjudication

    def _empty_tension_validation_fixture(self):
        _, _, _, adjudication = self._tension_validation_fixture()
        adjudication["records"] = []
        adjudication["decisionSummary"] = {
            "candidateCount": 0,
            "retainCount": 0,
            "mergeCount": 0,
            "splitCount": 0,
            "rejectCount": 0,
            "highConfidenceCount": 0,
            "mediumConfidenceCount": 0,
            "reviewConfidenceCount": 0,
            "reviewRequiredCount": 0,
            "unresolvedStructuralDecisionCount": 0,
        }
        adjudication["completenessRequirements"] = {
            "allProposedTensionsReviewed": True,
            "allRetainedTensionsHaveBothPoles": True,
            "allRetainedTensionsHaveDistinctNeighborBoundaries": True,
            "allMediumConfidenceDecisionsHaveReviewFlags": True,
            "noStructuralDecisionUnresolved": True,
        }
        return adjudication

    def test_required_relationship_roles_are_present(self) -> None:
        roles = {role for role, _ in RELATIONSHIP_SEMANTICS}
        self.assertTrue(
            {
                "direct-coded-support",
                "direct-content-representation",
                "primary-family-membership",
                "secondary-family-relationship",
                "primary-theme-support",
                "secondary-theme-support",
                "conceptual-framing",
                "future-extension",
                "tension-evidence-pole-a",
                "tension-evidence-pole-b",
                "integrates",
                "activated-tension",
                "scenario-amplifies",
                "scenario-mitigates",
                "contextual-connection",
                "shared-content-inheritance",
            }
            <= roles
        )

    def test_support_interpretation_rejects_composite_claims(self) -> None:
        self.assertIn("does not indicate scientific validity", SUPPORT_INTERPRETATION)
        self.assertIn("real-world effect size", SUPPORT_INTERPRETATION)

    def test_builder_refuses_output_outside_ignored_private_root(self) -> None:
        unavailable = REPO_ROOT / "not-used-by-this-safety-check"
        with self.assertRaisesRegex(ValueError, "output must remain beneath"):
            build_canonical_resynthesis(
                repo_root=REPO_ROOT,
                normalized_dir=unavailable,
                reconciliation_dir=unavailable,
                transcript_summary_dir=unavailable,
                source_workbook_dir=unavailable,
                design_dir=unavailable,
                output_dir=REPO_ROOT / "data" / "cognitive-security",
            )

    def test_builder_refuses_to_overwrite_private_inputs(self) -> None:
        unavailable = REPO_ROOT / "not-used-by-this-safety-check"
        with self.assertRaisesRegex(ValueError, "cannot overwrite"):
            build_canonical_resynthesis(
                repo_root=REPO_ROOT,
                normalized_dir=unavailable,
                reconciliation_dir=unavailable,
                transcript_summary_dir=unavailable,
                source_workbook_dir=unavailable,
                design_dir=unavailable,
                output_dir=OUTPUT_DIR / "inputs",
            )

    def test_private_output_guard_requires_git_ignore(self) -> None:
        with self.assertRaisesRegex(ValueError, "must be ignored by Git"):
            _require_git_ignored_output(
                REPO_ROOT, REPO_ROOT / "docs" / "not-a-private-output"
            )

    def test_family_adjudication_rejects_failed_substantive_finding(self) -> None:
        dataset = {
            "clusters": [
                {"clusterId": "CL-1", "name": "Cluster one", "categoryId": "CAT-1"}
            ],
            "categories": [{"categoryId": "CAT-1", "name": "Category one"}],
            "items": [
                {
                    "itemId": "I-1",
                    "sourceIdentityId": "S-1",
                    "scope": "focal",
                    "categoryId": "CAT-1",
                }
            ],
            "item_cluster_assignments": [
                {
                    "itemId": "I-1",
                    "primaryClusterId": "CL-1",
                    "secondaryClusterId": None,
                }
            ],
        }
        design = {
            "families": [{"familyId": "F-1", "category": "Category one"}],
            "clusterFamilyMappingsCsv": [
                {
                    "clusterId": "CL-1",
                    "proposedFamilyId": "F-1",
                }
            ],
        }
        adjudication = {
            "records": [
                {
                    "clusterId": "CL-1",
                    "clusterName": "Cluster one",
                    "proposedFamilyId": "F-1",
                    "finalFamilyId": "F-1",
                    "decision": "confirm",
                    "confidence": "high",
                    "proposedMappingConfidence": "high",
                    "evidenceReview": {
                        "support": {
                            "canonicalPrimaryItemCount": 1,
                            "canonicalSecondaryItemCount": 0,
                            "governedWeightedCount": 2,
                        },
                        "breadth": {
                            "canonicalContentUnitCount": 1,
                            "publicReleaseCoverageCount": 1,
                        },
                        "privateRepresentativeItemIds": ["I-1"],
                        "reviewDepth": "boundary-check",
                    },
                    "definitionFinding": {
                        "result": "fail",
                        "finding": "The definition does not fit.",
                    },
                    "inclusionFinding": {"result": "fit", "finding": "Included."},
                    "exclusionFinding": {"result": "pass", "finding": "Passed."},
                    "boundaryFinding": {
                        "result": "resolved",
                        "finding": "Resolved.",
                    },
                }
            ]
        }
        with self.assertRaisesRegex(ValueError, "boundary review is incomplete"):
            _validated_family_adjudication_index(
                dataset,
                design,
                {"CL-1": {"I-1"}},
                {"S-1": {"R-1"}},
                adjudication,
            )

    def test_tension_adjudication_rejects_stale_governed_definition(self) -> None:
        seed = {
            "id": "CT-X",
            "name": "Fixture tension",
            "type": "fixture",
            "definition": "Governed definition",
            "poleA": "Pole A",
            "poleB": "Pole B",
            "legacy": ["TD-001"],
        }
        adjudication = {
            "schemaVersion": "1.0.0",
            "methodVersion": "canonical-tension-construct-adjudication-v1",
            "adjudicationStatus": "analyst-reviewed-private-governed-input",
            "scope": "Fixture governance.",
            "decisionPolicy": {
                "proposedCountIsBinding": False,
                "allowedDecisions": ["retain", "merge", "split", "reject"],
                "retentionRequiresBothPolesAndDistinctBoundaries": True,
                "reviewFlagsAreNonBlockingButRequireHumanConfirmation": True,
            },
            "evidenceAccounting": {
                "occurrenceCountsIncludePositiveWeightLineageRows": True,
                "analyticalWeightsRespectOneUnitPerCanonicalItem": True,
                "uniqueItemsAreGloballySingleUseAcrossTensions": True,
                "sourceConcentrationIsALimitationNotAValidityScore": True,
            },
            "records": [
                {
                    "canonicalTensionId": "CT-X",
                    "name": "Fixture tension",
                    "tensionType": "fixture",
                    "definition": "Stale definition",
                    "poleALabel": "Pole A",
                    "poleBLabel": "Pole B",
                }
            ],
        }
        with self.assertRaisesRegex(ValueError, "definition is stale"):
            _validated_tension_adjudication_index({"CT-X": seed}, [], {}, adjudication)

    def test_tension_adjudication_rejects_unrecognized_governance_header(self) -> None:
        with self.assertRaisesRegex(ValueError, "governance header is invalid"):
            _validated_tension_adjudication_index(
                {}, [], {}, {"schemaVersion": "stale", "records": []}
            )

    def test_tension_adjudication_rejects_numeric_policy_boolean(self) -> None:
        seed, occurrence, item_by_id, adjudication = self._tension_validation_fixture()
        adjudication["decisionPolicy"]["proposedCountIsBinding"] = 0
        with self.assertRaisesRegex(ValueError, "governance header is invalid"):
            _validated_tension_adjudication_index(
                {"CT-X": seed}, [occurrence], item_by_id, adjudication
            )

    def test_tension_adjudication_rejects_boolean_decision_count(self) -> None:
        adjudication = self._empty_tension_validation_fixture()
        adjudication["decisionSummary"]["candidateCount"] = False
        with self.assertRaisesRegex(ValueError, "summary is stale"):
            _validated_tension_adjudication_index({}, [], {}, adjudication)

    def test_tension_adjudication_rejects_numeric_completeness_boolean(self) -> None:
        adjudication = self._empty_tension_validation_fixture()
        adjudication["completenessRequirements"]["allProposedTensionsReviewed"] = 1
        with self.assertRaisesRegex(ValueError, "completeness checks did not pass"):
            _validated_tension_adjudication_index({}, [], {}, adjudication)

    def test_tension_adjudication_rejects_non_string_rationale(self) -> None:
        seed, occurrence, item_by_id, adjudication = self._tension_validation_fixture()
        adjudication["records"][0]["rationale"] = 17
        with self.assertRaisesRegex(ValueError, "rationale is missing"):
            _validated_tension_adjudication_index(
                {"CT-X": seed}, [occurrence], item_by_id, adjudication
            )

    def test_tension_adjudication_rejects_stale_actual_lineage(self) -> None:
        seed, occurrence, item_by_id, adjudication = self._tension_validation_fixture()
        adjudication["records"][0]["historicalTensionIds"] = ["TD-002"]
        with self.assertRaisesRegex(ValueError, "historicalTensionIds"):
            _validated_tension_adjudication_index(
                {"CT-X": seed}, [occurrence], item_by_id, adjudication
            )

    def test_tension_adjudication_rejects_stale_proposed_lineage(self) -> None:
        seed, occurrence, item_by_id, adjudication = self._tension_validation_fixture()
        adjudication["records"][0]["proposedHistoricalTensionIds"] = ["TD-002"]
        with self.assertRaisesRegex(ValueError, "proposedHistoricalTensionIds"):
            _validated_tension_adjudication_index(
                {"CT-X": seed}, [occurrence], item_by_id, adjudication
            )

    def test_tension_adjudication_rejects_null_caveat(self) -> None:
        seed, occurrence, item_by_id, adjudication = self._tension_validation_fixture()
        occurrence.update({"normalizedPole": "A", "primaryClusterId": "CL-1"})
        record = adjudication["records"][0]
        record.update(
            {
                "evidenceSummary": {
                    "poleAOccurrences": 1,
                    "poleBOccurrences": 0,
                    "poleAWeight": 1.0,
                    "poleBWeight": 0.0,
                    "uniqueItems": 1,
                    "contentUnits": 1,
                    "categoryBreadth": 1,
                    "clusterCount": 1,
                    "assessment": "Fixture evidence assessment.",
                },
                "neighborDistinctions": {
                    "CT-Y": "Distinct from fixture Y.",
                    "CT-Z": "Distinct from fixture Z.",
                },
                "poleAAssumption": "Fixture assumption A.",
                "poleBAssumption": "Fixture assumption B.",
                "falseDichotomyCaveat": None,
            }
        )
        other_seeds = {
            tension_id: {
                "id": tension_id,
                "name": tension_id,
                "type": "fixture",
                "definition": tension_id,
                "poleA": "Pole A",
                "poleB": "Pole B",
                "legacy": [historical_id],
            }
            for tension_id, historical_id in (("CT-Y", "TD-002"), ("CT-Z", "TD-003"))
        }
        with self.assertRaisesRegex(ValueError, "pole logic is incomplete"):
            _validated_tension_adjudication_index(
                {"CT-X": seed, **other_seeds},
                [occurrence],
                item_by_id,
                adjudication,
            )

    def test_split_tension_adjudication_rejects_non_boolean_included(self) -> None:
        design = {"tensions": [{"id": "CT-X", "legacy": ["TD-001"]}]}
        adjudication = {
            "records": [
                {
                    "historicalTensionId": "TD-001",
                    "sourceCandidateId": "SC-1",
                    "historicalItemId": "I-1",
                    "historicalPole": "A",
                    "canonicalItemId": "CI-1",
                    "canonicalTensionId": "CT-X",
                    "canonicalPole": "A",
                    "confidence": "high",
                    "allocationRationale": "Fixture allocation.",
                    "included": "false",
                    "exclusionReason": "Fixture exclusion.",
                }
            ]
        }
        with self.assertRaisesRegex(ValueError, "included flag must be Boolean"):
            _validated_split_allocation_index(design, adjudication)


@unittest.skipUnless(
    (OUTPUT_DIR / "canonical_corpus_selection.json").is_file(),
    "Ignored private canonical checkpoint is not present.",
)
class GeneratedCanonicalCheckpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        def load(name: str):
            return json.loads((OUTPUT_DIR / name).read_text(encoding="utf-8"))

        cls.selection = load("canonical_corpus_selection.json")
        cls.clusters = load("cluster_support_recomputed.json")["records"]
        cls.family_adjudication = load("family_adjudication.json")
        cls.families = load("canonical_families_draft.json")["records"]
        cls.theme_adjudication = load("theme_adjudication.json")
        cls.themes = load("canonical_themes_draft.json")["records"]
        cls.allocation = load("tension_evidence_allocation.json")
        cls.counterpart_adjudication = load(
            "inputs/tension_alias_item_counterparts_adjudication.json"
        )
        cls.split_adjudication = load(
            "inputs/tension_split_item_allocation_adjudication.json"
        )
        cls.collision_adjudication = load(
            "inputs/tension_cross_tension_collision_adjudication.json"
        )
        cls.same_tension_adjudication = load(
            "inputs/tension_same_tension_duplicate_adjudication.json"
        )
        cls.tension_adjudication = load("inputs/canonical_tension_adjudication.json")
        cls.tensions = load("canonical_tensions_draft.json")["records"]
        cls.narratives = load("canonical_narratives_draft.json")["records"]
        cls.findings_payload = load("canonical_category_findings_draft.json")
        cls.findings = cls.findings_payload["records"]
        cls.historical_finding_lineage = cls.findings_payload[
            "historicalFindingLineage"
        ]
        cls.scenarios = load("canonical_scenarios_draft.json")["records"]
        cls.review_queue = load("canonicalization_review_queue.json")

    def test_governed_counts(self) -> None:
        counts = self.selection["counts"]
        self.assertEqual(269, counts["historicalSourceIdentityCount"])
        self.assertEqual(242, counts["publicReleaseCount"])
        self.assertEqual(241, counts["canonicalAnalyticalContentUnitCount"])
        self.assertEqual(12933, counts["canonicalItemCount"])
        self.assertEqual(1464, counts["excludedItemCount"])

    def test_selection_lineage_is_complete_and_weightless_exclusions_are_explicit(
        self,
    ) -> None:
        identities = self.selection["historicalIdentitySelection"]
        items = self.selection["historicalItemSelection"]
        content_units = self.selection["canonicalContentUnitSelection"]
        releases = self.selection["publicReleaseContentMap"]
        self.assertEqual(269, len(identities))
        self.assertEqual(14397, len(items))
        self.assertEqual(241, len(content_units))
        self.assertEqual(242, len(releases))
        self.assertEqual(
            {"confirmed-alias-excluded": 27, "shared-content-reuse-excluded": 1},
            {
                status: sum(row["analyticalStatus"] == status for row in identities)
                for status in (
                    "confirmed-alias-excluded",
                    "shared-content-reuse-excluded",
                )
            },
        )
        self.assertEqual(
            12933, sum(row["contributesAnalyticalWeight"] for row in items)
        )
        self.assertTrue(
            all(row["contributesAnalyticalWeight"] for row in content_units)
        )
        inherited = [
            row
            for row in releases
            if row["relationshipRole"] == "shared-content-inheritance"
        ]
        self.assertEqual(1, len(inherited))
        self.assertFalse(inherited[0]["contributesAnalyticalWeight"])
        self.assertEqual("pass", self.selection["transcriptManifestAudit"]["status"])
        self.assertEqual(
            241,
            self.selection["transcriptManifestAudit"]["strictUniqueContentUnits"],
        )

    def test_cluster_and_family_partition(self) -> None:
        self.assertEqual(127, len(self.clusters))
        self.assertEqual(50, len(self.families))
        members = [
            cluster_id
            for family in self.families
            for cluster_id in family["memberClusterIds"]
        ]
        self.assertEqual(127, len(members))
        self.assertEqual(127, len(set(members)))
        self.assertTrue(all(family["memberClusterIds"] for family in self.families))

    def test_every_medium_mapping_has_private_evidence_review(self) -> None:
        medium = [
            row
            for row in self.family_adjudication["mappingDecisions"]
            if row["mappingConfidence"] == "medium"
        ]
        self.assertEqual(33, len(medium))
        self.assertTrue(
            all(
                row["reviewedEvidence"] and row["reviewDepth"] == "deep-item-level"
                for row in medium
            )
        )
        summary = self.family_adjudication["decisionSummary"]
        self.assertEqual(34, summary["deepItemLevelEvidenceReviews"])
        self.assertEqual(119, summary["finalHighConfidenceMappings"])
        self.assertEqual(8, summary["finalModerateConfidenceMappings"])
        self.assertEqual(0, summary["reassignedAfterReview"])
        self.assertTrue(self.family_adjudication["governedValidation"]["passed"])

    def test_themes_are_one_level_and_include_kcf_and_ftp(self) -> None:
        self.assertEqual(11, len(self.themes))
        self.assertEqual({"theme"}, {row["publicLevel"] for row in self.themes})
        for theme in self.themes:
            families = theme["primaryFamilyIds"] + theme["secondaryFamilyIds"]
            self.assertTrue(any(value.startswith("KCF-") for value in families))
            self.assertTrue(any(value.startswith("FTP-") for value in families))
        self.assertEqual(
            {"high": 7, "medium": 4},
            {
                confidence: sum(
                    row["confidence"] == confidence
                    for row in self.theme_adjudication["decisions"]
                )
                for confidence in ("high", "medium")
            },
        )
        self.assertEqual(
            (11, 36, 7, 6),
            (
                len(self.theme_adjudication["historicalThemeLineage"]),
                len(self.theme_adjudication["historicalMetaClusterLineage"]),
                len(self.theme_adjudication["historicalNarrativeLineage"]),
                len(self.theme_adjudication["historicalScenarioLineage"]),
            ),
        )
        self.assertTrue(
            all(
                theme["categoryBreadth"]
                == len(
                    {
                        family_id.split("-", 1)[0]
                        for family_id in (
                            theme["primaryFamilyIds"] + theme["secondaryFamilyIds"]
                        )
                        if not family_id.startswith(("KCF-", "FTP-"))
                    }
                )
                for theme in self.themes
            )
        )

    def test_tension_items_are_globally_unique_and_both_poles_resolve(self) -> None:
        included = [row for row in self.allocation["records"] if row.get("included")]
        by_item = {}
        for row in included:
            by_item.setdefault(row["itemId"], []).append(row)
        self.assertTrue(
            all(
                len({row["canonicalTensionId"] for row in rows}) == 1
                and abs(sum(row["analyticalSupportWeight"] for row in rows) - 1.0)
                < 1e-9
                for rows in by_item.values()
            )
        )
        self.assertTrue(
            all(
                "analyticalSupportWeight" in row
                and isinstance(row["analyticalSupportWeight"], (int, float))
                for row in self.allocation["records"]
            )
        )
        self.assertEqual(20, len(self.tensions))
        self.assertTrue(
            all(
                row["evidenceBalanceAcrossPoles"]["bothPolesDirectlySupported"]
                for row in self.tensions
            )
        )
        self.assertTrue(
            any(
                row.get("orientationTreatment") == "reversed-to-canonical-orientation"
                for row in included
                if row.get("historicalTensionId") == "TD-024"
            )
        )

    def test_tension_constructs_follow_independent_governed_adjudication(self) -> None:
        governed = {
            row["canonicalTensionId"]: row
            for row in self.tension_adjudication["records"]
        }
        self.assertEqual(set(governed), {row["tensionId"] for row in self.tensions})
        self.assertEqual(
            {"retain": 20},
            dict(Counter(row["adjudicationDecision"] for row in self.tensions)),
        )
        self.assertEqual(
            {"high": 10, "medium": 10},
            dict(Counter(row["adjudicationConfidence"] for row in self.tensions)),
        )
        self.assertEqual(10, sum(row["reviewRequired"] for row in self.tensions))
        for tension in self.tensions:
            decision = governed[tension["tensionId"]]
            for field in (
                "name",
                "tensionType",
                "definition",
                "poleALabel",
                "poleBLabel",
                "historicalTensionIds",
                "proposedHistoricalTensionIds",
            ):
                self.assertEqual(decision[field], tension[field])
            self.assertEqual(decision["poleAAssumption"], tension["poleAAssumption"])
            self.assertEqual(decision["poleBAssumption"], tension["poleBAssumption"])
            self.assertEqual(
                decision["neighborDistinctions"], tension["neighborDistinctions"]
            )
            self.assertEqual(decision["reviewFlags"], tension["reviewFlags"])

    def test_alias_counterpart_adjudication_is_exact_and_fail_closed(self) -> None:
        governed = self.counterpart_adjudication["records"]
        substitutions = [
            row
            for row in self.allocation["records"]
            if row.get("lineageTreatment")
            == "governed-canonical-counterpart-substitution"
        ]
        by_lineage = {}
        for row in substitutions:
            by_lineage.setdefault(
                (row["historicalTensionId"], row["historicalItemId"]), []
            ).append(row)

        self.assertEqual(74, len(governed))
        self.assertEqual(74, len({row["historicalItemId"] for row in governed}))
        self.assertEqual(76, len(substitutions))
        self.assertEqual(72, len({row["canonicalItemId"] for row in governed}))
        self.assertEqual(
            {"high": 62, "medium": 11, "review": 1},
            {
                confidence: sum(row["confidence"] == confidence for row in governed)
                for confidence in ("high", "medium", "review")
            },
        )
        self.assertEqual(18, sum(bool(row.get("categoryDrift")) for row in governed))
        self.assertEqual(
            1, sum(bool(row.get("overlapsCanonicalItemIds")) for row in governed)
        )
        self.assertEqual(
            4, sum(bool(row.get("approvedLineageClusterId")) for row in governed)
        )

        for expected in governed:
            key = (
                expected["historicalTensionId"],
                expected["historicalItemId"],
            )
            occurrences = by_lineage[key]
            expected_occurrences = 2 if expected.get("bothPoleBridge") else 1
            self.assertEqual(expected_occurrences, len(occurrences))
            self.assertTrue(
                all(row["itemId"] == expected["canonicalItemId"] for row in occurrences)
            )
            if expected.get("approvedLineageClusterId"):
                self.assertTrue(
                    all(
                        row["primaryClusterId"] == expected["approvedLineageClusterId"]
                        and row["clusterLineageTreatment"]
                        == "governed-alias-proposition-historical-cluster-lineage"
                        and row["clusterLineageRationale"]
                        == expected["approvedLineageRationale"]
                        for row in occurrences
                    )
                )
            self.assertTrue(
                all(
                    row["counterpartMappingConfidence"] == expected["confidence"]
                    and row["counterpartCategoryDrift"]
                    == bool(expected.get("categoryDrift"))
                    for row in occurrences
                )
            )
            expected_overlaps = sorted(expected.get("overlapsCanonicalItemIds", []))
            self.assertTrue(
                all(
                    row["counterpartOverlapCanonicalItemIds"] == expected_overlaps
                    and row["itemId"] not in expected_overlaps
                    for row in occurrences
                )
            )
            if expected.get("bothPoleBridge"):
                self.assertLessEqual(
                    sum(row.get("analyticalSupportWeight", 0.0) for row in occurrences),
                    1.0,
                )

        counts = self.allocation["counts"]
        self.assertEqual(0, counts["unresolvedExcludedSourceIdentityOccurrences"])
        self.assertTrue(
            all(
                row["primaryClusterId"] and row["primaryFamilyId"]
                for row in self.allocation["records"]
                if row.get("included")
            )
        )
        self.assertFalse(
            self.allocation["allocationRules"][
                "lexicalSimilarityUsedForCounterpartIdentity"
            ]
        )

    def test_split_tension_adjudication_covers_every_source_pole_occurrence(
        self,
    ) -> None:
        expected_records = self.split_adjudication["records"]
        actual_records = {
            (
                row["historicalTensionId"],
                row["sourceCandidateId"],
                row["historicalItemId"],
                row["sourcePoleOccurrence"],
            ): row
            for row in self.allocation["records"]
            if row.get("historicalTensionId")
            in {"TD-001", "TD-002", "TD-007", "TD-009"}
        }
        self.assertEqual(98, len(expected_records))
        self.assertEqual(98, len(actual_records))
        for expected in expected_records:
            key = (
                expected["historicalTensionId"],
                expected["sourceCandidateId"],
                expected["historicalItemId"],
                expected["historicalPole"],
            )
            actual = actual_records[key]
            self.assertEqual(expected["canonicalItemId"], actual["itemId"])
            self.assertEqual(
                expected["canonicalTensionId"], actual["canonicalTensionId"]
            )
            self.assertEqual(expected["canonicalPole"], actual["normalizedPole"])
            self.assertEqual(
                expected.get("included", True), actual["splitAdjudicationIncluded"]
            )
            self.assertEqual(
                expected.get("exclusionReason"),
                actual["splitAdjudicationExclusionReason"],
            )
            self.assertEqual(
                "governed-split-item-adjudication", actual["allocationAuthority"]
            )
        self.assertFalse(
            self.allocation["allocationRules"][
                "lexicalOrKeywordRoutingUsedForSplitTensions"
            ]
        )
        counts = self.allocation["counts"]
        self.assertEqual(96, counts["splitOccurrencesIncludedByAdjudication"])
        self.assertEqual(
            2, counts["splitDuplicateBridgeOccurrencesExcludedByAdjudication"]
        )
        self.assertEqual(
            {"high": 87, "medium": 9, "review": 2},
            {
                "high": counts["splitHighConfidenceRecords"],
                "medium": counts["splitMediumConfidenceRecords"],
                "review": counts["splitReviewRecords"],
            },
        )
        self.assertEqual(
            5, counts["splitOccurrencesDepartingFromProposedLegacyTargets"]
        )
        self.assertEqual(4, len(self.allocation["splitDecisionSummary"]))

    def test_td024_counterparts_are_all_inverted(self) -> None:
        records = [
            row
            for row in self.allocation["records"]
            if row.get("historicalTensionId") == "TD-024"
        ]
        self.assertEqual(12, len(records))
        self.assertTrue(
            all(
                row["orientationTreatment"] == "reversed-to-canonical-orientation"
                and row["normalizedPole"]
                == ("B" if row["sourcePoleOccurrence"] == "A" else "A")
                for row in records
            )
        )

    def test_cross_tension_collisions_follow_governed_single_use_decisions(
        self,
    ) -> None:
        governed = self.collision_adjudication["records"]
        summary = self.allocation["crossTensionCollisionDecisionSummary"]
        self.assertEqual(12, len(governed))
        self.assertEqual(12, len(summary))
        self.assertEqual(
            {row["canonicalItemId"] for row in governed},
            {row["canonicalItemId"] for row in summary},
        )
        by_item = {}
        for row in self.allocation["records"]:
            if row.get("crossTensionCollision"):
                by_item.setdefault(str(row["itemId"]), []).append(row)
        self.assertEqual(12, len(by_item))
        self.assertEqual(24, sum(len(rows) for rows in by_item.values()))
        for decision in governed:
            item_id = decision["canonicalItemId"]
            rows = by_item[item_id]
            chosen_key = decision["decision"]["chosenLineageKey"]
            included = [row for row in rows if row.get("included")]
            self.assertEqual(1, len(included))
            actual_key = "|".join(
                (
                    included[0]["historicalTensionId"],
                    included[0]["sourceCandidateId"],
                    included[0]["historicalItemId"],
                    included[0]["sourcePoleOccurrence"],
                    included[0]["canonicalTensionId"],
                    included[0]["normalizedPole"],
                )
            )
            self.assertEqual(chosen_key, actual_key)
            self.assertEqual(1.0, included[0]["analyticalSupportWeight"])
            self.assertTrue(
                all(
                    row["analyticalSupportWeight"]
                    == (1.0 if row.get("included") else 0.0)
                    for row in rows
                )
            )
        counts = self.allocation["counts"]
        self.assertEqual(
            7, counts["crossTensionCollisionDecisionsChangingMechanicalWinner"]
        )
        self.assertEqual(3, counts["crossTensionCollisionReviewRequiredRecords"])

    def test_same_tension_repeated_lineage_uses_one_item_weight_budget(self) -> None:
        governed = self.same_tension_adjudication["records"]
        summary = self.allocation["sameTensionDuplicateDecisionSummary"]
        self.assertEqual(8, len(governed))
        self.assertEqual(8, len(summary))
        self.assertEqual(
            {row["canonicalItemId"] for row in governed},
            {row["canonicalItemId"] for row in summary},
        )
        by_item = {}
        for row in self.allocation["records"]:
            if row.get("sameTensionDuplicate"):
                by_item.setdefault(str(row["itemId"]), []).append(row)
        self.assertEqual(8, len(by_item))
        self.assertEqual(16, sum(len(rows) for rows in by_item.values()))
        for decision in governed:
            rows = by_item[decision["canonicalItemId"]]
            self.assertEqual(
                1.0,
                sum(row["analyticalSupportWeight"] for row in rows),
            )
            self.assertEqual(
                {decision["canonicalTensionId"]},
                {row["canonicalTensionId"] for row in rows},
            )
            expected_weights = {
                row["lineageKey"]: row["occurrenceSupportWeight"]
                for row in decision["occurrences"]
            }
            actual_weights = {
                "|".join(
                    (
                        row["historicalTensionId"],
                        row["sourceCandidateId"],
                        row["historicalItemId"],
                        row["sourcePoleOccurrence"],
                        row["canonicalTensionId"],
                        row["normalizedPole"],
                    )
                ): row["analyticalSupportWeight"]
                for row in rows
            }
            self.assertEqual(expected_weights, actual_weights)
        self.assertEqual(
            4, self.allocation["counts"]["sameTensionDualPoleBridgeRecords"]
        )
        self.assertEqual(
            4, self.allocation["counts"]["sameTensionSharedProvenanceRecords"]
        )

    def test_higher_order_counts_and_traceability(self) -> None:
        self.assertEqual(5, len(self.narratives))
        self.assertEqual(64, len(self.findings))
        self.assertEqual(6, len(self.scenarios))
        self.assertEqual(42, len(self.historical_finding_lineage))
        self.assertEqual(
            0,
            self.review_queue["redundancyAudit"]["unresolvedPotentialRedundancyCount"],
        )
        collections = (
            self.themes,
            self.tensions,
            self.narratives,
            self.findings,
            self.scenarios,
        )
        self.assertTrue(
            all(
                row["corpusSupportProfile"]["itemSupportCount"] > 0
                for records in collections
                for row in records
            )
        )
        self.assertTrue(
            all(
                "plausibility exercise, not a prediction" in row["uncertaintyStatement"]
                for row in self.scenarios
            )
        )
        self.assertEqual(
            {"high": 3, "medium": 2},
            {
                confidence: sum(
                    row["adjudicationConfidence"] == confidence
                    for row in self.narratives
                )
                for confidence in ("high", "medium")
            },
        )
        self.assertEqual(
            {
                "SC-01": (7, 6, 5),
                "SC-02": (6, 6, 4),
                "SC-03": (6, 6, 4),
                "SC-04": (7, 6, 5),
                "SC-05": (7, 6, 5),
                "SC-06": (6, 5, 5),
            },
            {
                row["scenarioId"]: (
                    len(row["plausiblePathways"]),
                    len(row["indicators"]),
                    len(row["responseOptions"]),
                )
                for row in self.scenarios
            },
        )
        self.assertEqual(
            {"SC-04"},
            {row["scenarioId"] for row in self.scenarios if row["reviewRequired"]},
        )
        self.assertTrue(
            all(
                row["corpusSupportProfile"]["historicalToCorrectedSensitivity"][
                    "status"
                ]
                == "unassessable"
                for row in self.scenarios
            )
        )


if __name__ == "__main__":
    unittest.main()
