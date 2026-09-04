"""Data-contract tests for the canonical Cognitive Security public projection."""

from __future__ import annotations

from collections import Counter, defaultdict
import json
import math
import os
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from scripts.build_cognitive_security import (
    ValidationError,
    _guard_against_canonical_public_overwrite,
)
from scripts.cognitive_security.canonical_public import (
    APPROVED_CHECKPOINT_COMMIT,
    CONTENT_VERSION,
    EXPECTED_COUNTS,
    NORMALIZED_FILES,
    PUBLIC_FILE_ORDER,
    SC04_NOTICE,
    SUPPORT_INTERPRETATION,
    PublicProjectionError,
    build_and_serialize,
    load_projection_inputs,
    validate_public_payloads,
    verify_approved_checkpoint_commit,
)


CHECKPOINT_DIR = (
    REPO_ROOT / "analysis" / "cognitive-security" / "canonical-resynthesis"
)
PUBLIC_DIR = REPO_ROOT / "data" / "cognitive-security"
EPISODE_SUMMARIES_PATH = PUBLIC_DIR / "episode_summaries.json"
ORIGINAL_EPISODE_83 = "EPI-72E94D7AF43A4BD3"
INHERITED_EPISODE_83 = "EPI-9960393907F71603"

SUPPORT_FILES = (
    "cluster_summaries.json",
    "families.json",
    "themes.json",
    "tensions.json",
    "narratives.json",
    "category_findings.json",
    "scenarios.json",
)
PRIMARY_SUPPORT_KEYS = {
    "itemCount",
    "share",
    "primaryContentUnitCount",
    "primaryClusterCount",
    "primaryFamilyCount",
    "categoryBreadth",
    "concentration",
}
BROADER_REACH_KEYS = {
    "itemCount",
    "derivedItemCount",
    "contentUnitCount",
    "publicReleaseCount",
    "inheritedPublicReleaseCount",
    "clusterCount",
    "familyCount",
    "categoryBreadth",
    "secondaryOrDerivedClusterCount",
    "secondaryOrDerivedFamilyCount",
    "concentration",
}
CONCENTRATION_KEYS = {
    "topOneContentUnitShare",
    "topTwoContentUnitShare",
    "topFiveContentUnitShare",
    "effectiveContentUnitCount",
}
HEATMAP_CELL_KEYS = {
    "categoryId",
    "themeId",
    "primaryFamilyCount",
    "categoryFamilyCount",
    "primaryClusterCount",
    "categoryClusterCount",
    "primaryContentUnitCount",
    "categoryContentUnitCount",
    "primaryFamilyShare",
    "primaryClusterShare",
    "primaryContentUnitShare",
    "normalizedPrimarySupportBreadth",
}


def _records(document: Any) -> list[dict[str, Any]]:
    if isinstance(document, list):
        return document
    if isinstance(document, dict) and isinstance(document.get("records"), list):
        return document["records"]
    raise AssertionError("Expected an array or an object containing records")


def _candidate_normalized_directories() -> Iterable[Path]:
    configured = os.environ.get("COGNITIVE_SECURITY_NORMALIZED_DIR")
    if configured:
        yield Path(configured).expanduser()
    yield REPO_ROOT / "analysis" / "cognitive-security" / "normalized"
    yield (
        REPO_ROOT.parent
        / "psywerx-interactives"
        / "analysis"
        / "cognitive-security"
        / "normalized"
    )


def _find_normalized_directory() -> Path | None:
    required = tuple(NORMALIZED_FILES.values())
    for candidate in _candidate_normalized_directories():
        if all((candidate / name).is_file() for name in required):
            return candidate
    return None


def _load_public_package() -> dict[str, Any] | None:
    manifest_path = PUBLIC_DIR / "manifest.json"
    if not manifest_path.is_file():
        return None
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("contentVersion") != CONTENT_VERSION:
        return None
    if not all((PUBLIC_DIR / name).is_file() for name in PUBLIC_FILE_ORDER):
        return None
    return {
        name: json.loads((PUBLIC_DIR / name).read_text(encoding="utf-8"))
        for name in PUBLIC_FILE_ORDER
    }


def _iter_keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _iter_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_keys(child)


class CanonicalPublicProjectionTests(unittest.TestCase):
    """Exercise the complete package using governed inputs when they are present."""

    inputs: dict[str, Any] | None = None
    payloads: dict[str, Any]
    serialized: dict[str, bytes]
    normalized_dir: Path | None = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.normalized_dir = _find_normalized_directory()
        checkpoint_available = all(
            (CHECKPOINT_DIR / name).is_file()
            for name in (
                "canonical_corpus_selection.json",
                "canonical_families_draft.json",
                "canonical_themes_draft.json",
                "canonical_tensions_draft.json",
                "canonical_narratives_draft.json",
                "canonical_category_findings_draft.json",
                "canonical_scenarios_draft.json",
                "cluster_support_recomputed.json",
                "tension_evidence_allocation.json",
                "relationship_semantics.json",
                "canonicalization_review_queue.json",
            )
        )
        if (
            checkpoint_available
            and cls.normalized_dir is not None
            and EPISODE_SUMMARIES_PATH.is_file()
        ):
            cls.inputs = load_projection_inputs(
                CHECKPOINT_DIR,
                cls.normalized_dir,
                EPISODE_SUMMARIES_PATH,
            )
            cls.payloads, cls.serialized = build_and_serialize(cls.inputs)
            return

        published = _load_public_package()
        if published is None:
            raise unittest.SkipTest(
                "Canonical public data and the governed private build inputs are unavailable"
            )
        validate_public_payloads(published)
        cls.payloads = published
        cls.serialized = {
            name: (PUBLIC_DIR / name).read_bytes() for name in PUBLIC_FILE_ORDER
        }

    def test_recursive_allowlist_and_privacy_guard_fail_closed(self) -> None:
        validate_public_payloads(self.payloads)

        unknown = dict(self.payloads)
        unknown_themes = list(self.payloads["themes.json"])
        unknown_theme = dict(unknown_themes[0])
        unknown_support = dict(unknown_theme["support"])
        unknown_primary = dict(unknown_support["primarySupport"])
        unknown_primary["sourceItemIds"] = ["private-item"]
        unknown_support["primarySupport"] = unknown_primary
        unknown_theme["support"] = unknown_support
        unknown_themes[0] = unknown_theme
        unknown["themes.json"] = unknown_themes
        with self.assertRaisesRegex(PublicProjectionError, "keys differ from allowlist"):
            validate_public_payloads(unknown)

        private_path = dict(self.payloads)
        private_categories = list(self.payloads["categories.json"])
        private_category = dict(private_categories[0])
        private_category["summary"] = r"C:\Users\analyst\private\source.xlsx"
        private_categories[0] = private_category
        private_path["categories.json"] = private_categories
        with self.assertRaisesRegex(PublicProjectionError, "Private filesystem reference"):
            validate_public_payloads(private_path)

    def test_build_is_byte_deterministic_and_does_not_mutate_inputs(self) -> None:
        if self.inputs is None:
            self.skipTest("Governed private build inputs are unavailable")
        selection_before = json.dumps(
            self.inputs["selection"], ensure_ascii=False, sort_keys=True
        )
        rebuilt_payloads, rebuilt_bytes = build_and_serialize(self.inputs)
        self.assertEqual(self.serialized, rebuilt_bytes)
        self.assertEqual(self.payloads, rebuilt_payloads)
        self.assertEqual(
            selection_before,
            json.dumps(self.inputs["selection"], ensure_ascii=False, sort_keys=True),
        )
        self.assertNotIn("_support_metrics", self.inputs)
        for name, content in rebuilt_bytes.items():
            self.assertTrue(content.endswith(b"\n"), name)
            self.assertEqual(rebuilt_payloads[name], json.loads(content), name)
            self.assertEqual((PUBLIC_DIR / name).read_bytes(), content, name)

    def test_approved_checkpoint_is_fixed_and_verifiable(self) -> None:
        self.assertEqual(
            APPROVED_CHECKPOINT_COMMIT,
            "99e6732ac01a7b6f06b2eaf6490efb05093b97ea",
        )
        if self.inputs is None:
            self.skipTest("Governed checkpoint is unavailable")
        verify_approved_checkpoint_commit(REPO_ROOT, CHECKPOINT_DIR)

    def test_exact_canonical_counts(self) -> None:
        expected = {
            "categoryCount": 7,
            "familyCount": 50,
            "clusterCount": 127,
            "clusterSummaryCount": 127,
            "themeCount": 11,
            "tensionCount": 20,
            "narrativeCount": 5,
            "categoryFindingCount": 64,
            "scenarioCount": 6,
            "publicReleaseCount": 242,
            "episodeSummaryCount": 242,
            "canonicalContentUnitCount": 241,
            "canonicalItemCount": 12933,
            "canonicalFocalItemCount": 9822,
            "canonicalContextualItemCount": 3111,
            "heatmapCellCount": 77,
        }
        self.assertEqual(expected, EXPECTED_COUNTS)
        counts = self.payloads["manifest.json"]["counts"]
        for key, value in expected.items():
            self.assertEqual(value, counts[key], key)
        self.assertEqual(7, len(self.payloads["categories.json"]))
        self.assertEqual(50, len(self.payloads["families.json"]))
        self.assertEqual(127, len(self.payloads["clusters.json"]))
        self.assertEqual(127, len(self.payloads["cluster_summaries.json"]))
        self.assertEqual(11, len(self.payloads["themes.json"]))
        self.assertEqual(20, len(self.payloads["tensions.json"]))
        self.assertEqual(5, len(self.payloads["narratives.json"]))
        self.assertEqual(64, len(self.payloads["category_findings.json"]))
        self.assertEqual(6, len(self.payloads["scenarios.json"]))
        self.assertEqual(242, len(self.payloads["episodes.json"]))

    def test_heatmap_is_complete_and_reconstructable_from_primary_support(self) -> None:
        heatmap = self.payloads["heatmap.json"]
        cells = heatmap["cells"]
        categories = self.payloads["categories.json"]
        families = self.payloads["families.json"]
        themes = self.payloads["themes.json"]
        provenance = self.payloads["provenance.json"]
        family_by_id = {row["familyId"]: row for row in families}
        category_families = {
            category["categoryId"]: {
                family["familyId"]
                for family in families
                if family["categoryId"] == category["categoryId"]
            }
            for category in categories
        }
        cluster_releases = {
            cluster_id: {row["episodeId"] for row in rows}
            for cluster_id, rows in provenance["clusterToReleases"].items()
        }

        self.assertEqual(77, len(cells))
        self.assertEqual(
            {
                (category["categoryId"], theme["themeId"])
                for category in categories
                for theme in themes
            },
            {(cell["categoryId"], cell["themeId"]) for cell in cells},
        )
        theme_by_id = {theme["themeId"]: theme for theme in themes}
        for cell in cells:
            with self.subTest(category=cell["categoryId"], theme=cell["themeId"]):
                self.assertEqual(HEATMAP_CELL_KEYS, set(cell))
                category_family_ids = category_families[cell["categoryId"]]
                category_cluster_ids = {
                    cluster_id
                    for family_id in category_family_ids
                    for cluster_id in family_by_id[family_id]["memberClusterIds"]
                }
                category_content_ids = {
                    episode_id
                    for cluster_id in category_cluster_ids
                    for episode_id in cluster_releases.get(cluster_id, set())
                }
                theme = theme_by_id[cell["themeId"]]
                primary_family_ids = {
                    relation["familyId"]
                    for relation in theme["familyRelationships"]
                    if relation["semanticRole"] == "primary-theme-support"
                } & category_family_ids
                primary_cluster_ids = {
                    cluster_id
                    for family_id in primary_family_ids
                    for cluster_id in family_by_id[family_id]["memberClusterIds"]
                }
                primary_content_ids = {
                    episode_id
                    for cluster_id in primary_cluster_ids
                    for episode_id in cluster_releases.get(cluster_id, set())
                }
                expected_counts = (
                    len(primary_family_ids),
                    len(category_family_ids),
                    len(primary_cluster_ids),
                    len(category_cluster_ids),
                    len(primary_content_ids),
                    len(category_content_ids),
                )
                self.assertEqual(
                    expected_counts,
                    (
                        cell["primaryFamilyCount"],
                        cell["categoryFamilyCount"],
                        cell["primaryClusterCount"],
                        cell["categoryClusterCount"],
                        cell["primaryContentUnitCount"],
                        cell["categoryContentUnitCount"],
                    ),
                )
                shares = tuple(
                    round(numerator / denominator, 6)
                    for numerator, denominator in zip(
                        expected_counts[::2], expected_counts[1::2]
                    )
                )
                self.assertEqual(
                    shares,
                    (
                        cell["primaryFamilyShare"],
                        cell["primaryClusterShare"],
                        cell["primaryContentUnitShare"],
                    ),
                )
                expected_breadth = round(
                    sum(
                        numerator / denominator
                        for numerator, denominator in zip(
                            expected_counts[::2], expected_counts[1::2]
                        )
                    )
                    / 3,
                    6,
                )
                self.assertTrue(
                    math.isclose(
                        expected_breadth,
                        cell["normalizedPrimarySupportBreadth"],
                        abs_tol=1e-9,
                    )
                )

    def test_support_is_two_layer_interpreted_and_has_no_score(self) -> None:
        coverage = self.payloads["coverage.json"]
        self.assertEqual(
            ["primarySupport", "broaderTraceableReach"],
            coverage["supportModel"]["layers"],
        )
        self.assertTrue(coverage["supportModel"]["compositeScoreProhibited"])
        self.assertEqual(
            SUPPORT_INTERPRETATION,
            coverage["supportModel"]["interpretation"],
        )
        primary_meaning = coverage["supportModel"]["primaryMeaning"]
        self.assertIn("evidence path depends on entity type", primary_meaning)
        self.assertNotRegex(primary_meaning, r"(?i)\bdirect(?:ly)?\b")
        for filename in SUPPORT_FILES:
            for record in self.payloads[filename]:
                support = record["support"]
                with self.subTest(filename=filename, entity=next(iter(record.values()))):
                    self.assertEqual(
                        {
                            "primarySupport",
                            "broaderTraceableReach",
                            "interpretation",
                            "limitations",
                        },
                        set(support),
                    )
                    self.assertEqual(SUPPORT_INTERPRETATION, support["interpretation"])
                    self.assertEqual(PRIMARY_SUPPORT_KEYS, set(support["primarySupport"]))
                    self.assertEqual(
                        BROADER_REACH_KEYS,
                        set(support["broaderTraceableReach"]),
                    )
                    self.assertEqual(
                        CONCENTRATION_KEYS,
                        set(support["primarySupport"]["concentration"]),
                    )
                    self.assertEqual(
                        CONCENTRATION_KEYS,
                        set(support["broaderTraceableReach"]["concentration"]),
                    )
                    primary = support["primarySupport"]
                    broader = support["broaderTraceableReach"]
                    self.assertEqual(
                        primary["itemCount"] + broader["derivedItemCount"],
                        broader["itemCount"],
                    )
                    expected_share = (
                        round(primary["itemCount"] / broader["itemCount"], 6)
                        if broader["itemCount"]
                        else 0.0
                    )
                    self.assertEqual(expected_share, primary["share"])
                    self.assertNotIn("directContentUnitCount", primary)

        allowed_score_flags = {"compositeScoreProhibited", "compositeScoreAbsent"}
        score_keys = {
            key
            for key in _iter_keys(self.payloads)
            if "score" in "".join(character for character in key if character.isalnum()).lower()
        }
        self.assertLessEqual(score_keys, allowed_score_flags)

    def test_tension_evidence_paths_never_use_direct_coded_support(self) -> None:
        provenance = self.payloads["provenance.json"]
        relationships = [
            relationship
            for links in provenance["tensionToReleases"].values()
            for link in links
            for relationship in link["relationships"]
        ]
        self.assertTrue(relationships)
        self.assertNotIn(
            "direct-coded-support",
            {relationship["semanticRole"] for relationship in relationships},
        )
        self.assertTrue(all(relationship["causalClaim"] is False for relationship in relationships))

    def test_tension_pole_a_evidence_uses_governed_pole_a_role(self) -> None:
        relationships = [
            relationship
            for links in self.payloads["provenance.json"]["tensionToReleases"].values()
            for link in links
            for relationship in link["relationships"]
            if relationship["semanticRole"] == "tension-evidence-pole-a"
        ]
        self.assertTrue(relationships)
        self.assertTrue(all(relationship["analyticalWeight"] > 0 for relationship in relationships))

    def test_tension_pole_b_evidence_uses_governed_pole_b_role(self) -> None:
        relationships = [
            relationship
            for links in self.payloads["provenance.json"]["tensionToReleases"].values()
            for link in links
            for relationship in link["relationships"]
            if relationship["semanticRole"] == "tension-evidence-pole-b"
        ]
        self.assertTrue(relationships)
        self.assertTrue(all(relationship["analyticalWeight"] > 0 for relationship in relationships))

    def test_dual_pole_episode_support_exposes_both_roles(self) -> None:
        dual_pole_links = [
            link
            for links in self.payloads["provenance.json"]["tensionToReleases"].values()
            for link in links
            if len(link["relationships"]) == 2
        ]
        self.assertTrue(dual_pole_links)
        for link in dual_pole_links:
            self.assertEqual(
                {"tension-evidence-pole-a", "tension-evidence-pole-b"},
                {relationship["semanticRole"] for relationship in link["relationships"]},
            )

    def test_tension_provenance_matches_governed_pole_allocations(self) -> None:
        if self.inputs is None:
            self.skipTest("Governed private build inputs are unavailable")
        release_by_content = {
            str(row["canonicalContentUnitId"]): str(row["selectedRepresentationId"])
            for row in self.inputs["selection"]["canonicalContentUnitSelection"]
            if row["contributesAnalyticalWeight"]
        }
        expected: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
        roles = {
            "A": "tension-evidence-pole-a",
            "B": "tension-evidence-pole-b",
        }
        for row in _records(self.inputs["tension_allocation"]):
            weight = float(row.get("analyticalSupportWeight") or 0)
            if not row.get("included") or weight <= 0:
                continue
            expected[
                (
                    str(row["canonicalTensionId"]),
                    release_by_content[str(row["canonicalContentUnitId"])],
                )
            ][roles[str(row["normalizedPole"])]] += weight
        expected_normalized = {
            key: {role: round(weight, 6) for role, weight in weights.items()}
            for key, weights in expected.items()
        }
        actual = {
            (tension_id, link["episodeId"]): {
                relationship["semanticRole"]: relationship["analyticalWeight"]
                for relationship in link["relationships"]
            }
            for tension_id, links in self.payloads["provenance.json"][
                "tensionToReleases"
            ].items()
            for link in links
        }
        self.assertEqual(expected_normalized, actual)

    def test_cluster_provenance_still_uses_direct_coded_support(self) -> None:
        provenance = self.payloads["provenance.json"]
        self.assertEqual(
            {"semanticRole": "direct-coded-support", "causalClaim": False},
            provenance["clusterRelationship"],
        )
        links = [
            link
            for cluster_links in provenance["clusterToReleases"].values()
            for link in cluster_links
        ]
        self.assertTrue(links)
        self.assertTrue(all("relationship" not in link for link in links))

    def test_episode_83_has_two_releases_one_weight_and_one_inheritance_edge(self) -> None:
        episodes = {row["episodeId"]: row for row in self.payloads["episodes.json"]}
        self.assertEqual(
            "direct-content-representation",
            episodes[ORIGINAL_EPISODE_83]["contentRole"],
        )
        self.assertEqual(
            "shared-content-inheritance",
            episodes[INHERITED_EPISODE_83]["contentRole"],
        )
        self.assertEqual(
            241,
            sum(
                row["contentRole"] == "direct-content-representation"
                for row in episodes.values()
            ),
        )
        self.assertEqual(
            1,
            sum(
                row["contentRole"] == "shared-content-inheritance"
                for row in episodes.values()
            ),
        )

        provenance = self.payloads["provenance.json"]
        self.assertEqual(
            [
                {
                    "relationshipId": provenance["sharedContentRelationships"][0][
                        "relationshipId"
                    ],
                    "sourceEpisodeId": INHERITED_EPISODE_83,
                    "targetEpisodeId": ORIGINAL_EPISODE_83,
                    "semanticRole": "shared-content-inheritance",
                    "contributesAnalyticalWeight": False,
                }
            ],
            provenance["sharedContentRelationships"],
        )
        directly_weighted = {
            row["episodeId"]
            for mapping in (
                provenance["clusterToReleases"],
                provenance["tensionToReleases"],
            )
            for rows in mapping.values()
            for row in rows
        }
        self.assertIn(ORIGINAL_EPISODE_83, directly_weighted)
        self.assertNotIn(INHERITED_EPISODE_83, directly_weighted)
        matching_edges = [
            edge
            for edge in self.payloads["relationships.json"]
            if edge["sourceType"] == "episode"
            and edge["sourceId"] == INHERITED_EPISODE_83
            and edge["targetType"] == "episode"
            and edge["targetId"] == ORIGINAL_EPISODE_83
        ]
        self.assertEqual(1, len(matching_edges))
        self.assertEqual("shared-content-inheritance", matching_edges[0]["semanticRole"])
        self.assertFalse(matching_edges[0]["causalClaim"])

    def test_sc04_has_all_required_public_safeguards(self) -> None:
        scenarios = {
            row["scenarioId"]: row for row in self.payloads["scenarios.json"]
        }
        self.assertEqual(SC04_NOTICE, scenarios["SC-04"]["publicNotice"])
        notice = scenarios["SC-04"]["publicNotice"].lower()
        for safeguard in (
            "legal",
            "privacy",
            "civil-liberties",
            "ethics",
            "consent",
            "affected-community",
            "not validated recommendations",
            "not a recommendation",
        ):
            self.assertIn(safeguard, notice)
        self.assertTrue(scenarios["SC-04"]["responseOptions"])
        self.assertTrue(
            all(
                row["publicNotice"] is None
                for scenario_id, row in scenarios.items()
                if scenario_id != "SC-04"
            )
        )

    def test_relationship_endpoints_roles_category_edges_and_theme_roles(self) -> None:
        payloads = self.payloads
        ids = {
            "category": {row["categoryId"] for row in payloads["categories.json"]},
            "cluster": {row["clusterId"] for row in payloads["clusters.json"]},
            "family": {row["familyId"] for row in payloads["families.json"]},
            "theme": {row["themeId"] for row in payloads["themes.json"]},
            "tension": {row["tensionId"] for row in payloads["tensions.json"]},
            "narrative": {
                row["narrativeId"] for row in payloads["narratives.json"]
            },
            "finding": {
                row["findingId"] for row in payloads["category_findings.json"]
            },
            "scenario": {row["scenarioId"] for row in payloads["scenarios.json"]},
            "episode": {row["episodeId"] for row in payloads["episodes.json"]},
        }
        semantics = {
            row["semanticRole"] for row in payloads["relationship_semantics.json"]
        }
        relationships = payloads["relationships.json"]
        self.assertEqual(
            len(relationships),
            len({row["relationshipId"] for row in relationships}),
        )
        for relationship in relationships:
            with self.subTest(relationship=relationship["relationshipId"]):
                self.assertIn(relationship["sourceType"], ids)
                self.assertIn(
                    relationship["sourceId"], ids[relationship["sourceType"]]
                )
                self.assertIn(relationship["targetType"], ids)
                self.assertIn(
                    relationship["targetId"], ids[relationship["targetType"]]
                )
                self.assertIn(relationship["semanticRole"], semantics)
                self.assertFalse(relationship["causalClaim"])

        families = payloads["families.json"]
        category_edges = [
            row
            for row in relationships
            if row["sourceType"] == "family" and row["targetType"] == "category"
        ]
        self.assertEqual(50, len(category_edges))
        self.assertEqual(
            {(row["familyId"], row["categoryId"]) for row in families},
            {(row["sourceId"], row["targetId"]) for row in category_edges},
        )
        self.assertTrue(
            all(
                row["semanticRole"] == "contextual-connection"
                and row["qualifier"] == "within-category"
                for row in category_edges
            )
        )

        theme_family_edges = {
            (
                row["sourceId"],
                row["targetId"],
                row["semanticRole"],
                row["qualifier"],
            )
            for row in relationships
            if row["sourceType"] == "theme" and row["targetType"] == "family"
        }
        expected_theme_family_edges = {
            (
                theme["themeId"],
                relation["familyId"],
                relation["semanticRole"],
                relation["analyticalWeight"],
            )
            for theme in payloads["themes.json"]
            for relation in theme["familyRelationships"]
        }
        self.assertEqual(expected_theme_family_edges, theme_family_edges)
        theme_roles = {row[2] for row in theme_family_edges}
        self.assertEqual(
            {
                "primary-theme-support",
                "secondary-theme-support",
                "conceptual-framing",
                "future-extension",
            },
            theme_roles,
        )

        derived_tension_theme_edges = [
            row
            for row in relationships
            if row["sourceType"] == "tension" and row["targetType"] == "theme"
        ]
        self.assertTrue(derived_tension_theme_edges)
        self.assertTrue(
            all(
                row["semanticRole"] == "contextual-connection"
                and row["qualifier"] == "shared-governed-cluster-support"
                for row in derived_tension_theme_edges
            )
        )

    def test_manifest_has_only_the_canonical_inventory_and_no_private_hashes(self) -> None:
        manifest = self.payloads["manifest.json"]
        self.assertEqual(18, manifest["fileCount"])
        self.assertEqual(list(PUBLIC_FILE_ORDER), manifest["publicFiles"])
        self.assertEqual(
            ["relationships.json", "provenance.json"], manifest["lazyFiles"]
        )
        self.assertEqual(
            [name for name in PUBLIC_FILE_ORDER if name != "manifest.json"],
            [row["name"] for row in manifest["files"]],
        )
        for row in manifest["files"]:
            self.assertEqual(len(self.serialized[row["name"]]), row["bytes"])
            self.assertEqual({"name", "bytes"}, set(row))

        manifest_text = json.dumps(manifest, sort_keys=True).lower()
        self.assertNotIn("sha256", manifest_text)
        self.assertNotIn("checkpoint", manifest_text)
        self.assertNotIn(APPROVED_CHECKPOINT_COMMIT, manifest_text)
        self.assertFalse(
            any("hash" in key.lower() for key in _iter_keys(manifest)),
            "Manifest must not publish private-input hashes",
        )


class LegacyBuilderGuardTests(unittest.TestCase):
    def test_legacy_builder_refuses_to_overwrite_canonical_package(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo_root = Path(temporary_directory)
            manifest_path = repo_root / "data" / "cognitive-security" / "manifest.json"
            manifest_path.parent.mkdir(parents=True)
            manifest_path.write_text(
                json.dumps({"contentVersion": CONTENT_VERSION}), encoding="utf-8"
            )
            with self.assertRaisesRegex(ValidationError, "cannot overwrite"):
                _guard_against_canonical_public_overwrite(repo_root)

    def test_legacy_builder_fails_closed_for_unreadable_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo_root = Path(temporary_directory)
            manifest_path = repo_root / "data" / "cognitive-security" / "manifest.json"
            manifest_path.parent.mkdir(parents=True)
            manifest_path.write_text("not JSON", encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "Cannot safely identify"):
                _guard_against_canonical_public_overwrite(repo_root)


if __name__ == "__main__":
    unittest.main()
