"""Private-data release gates for episode summaries and relationships.

These tests intentionally read the ignored normalized release when it is
available locally.  CI installations that do not possess the governed private
package skip this module; the end-of-day release process must run it locally.
"""

from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
import re
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLIC_DIR = REPO_ROOT / "data" / "cognitive-security"
sys.path.insert(0, str(REPO_ROOT))

from scripts.cognitive_security.episode_products import (  # noqa: E402
    build_episode_relationships,
    build_private_source_packages,
    build_summary_authoring_inputs,
    canonical_episode_sources,
    retained_canonical_items,
)
from scripts.cognitive_security.transcript_summaries import word_count  # noqa: E402


REQUIRED_COLLECTIONS = (
    "episodes",
    "episode_source_mappings",
    "items",
    "item_tags",
    "categories",
    "clusters",
    "item_cluster_assignments",
    "cluster_meta_mappings",
    "meta_clusters",
    "themes",
    "theme_cluster_evidence",
    "theme_meta_mappings",
    "tensions",
    "tension_mappings",
)


def _private_normalized_dir() -> Path | None:
    candidates = (
        REPO_ROOT / "analysis" / "cognitive-security" / "normalized",
        REPO_ROOT.parent
        / "psywerx-interactives"
        / "analysis"
        / "cognitive-security"
        / "normalized",
    )
    for candidate in candidates:
        if all((candidate / f"{name}.json").is_file() for name in REQUIRED_COLLECTIONS):
            return candidate
    return None


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _normalized_words(value: object) -> tuple[str, ...]:
    return tuple(re.findall(r"[a-z0-9]+", str(value or "").casefold()))


def _ngrams(words: tuple[str, ...], size: int) -> set[tuple[str, ...]]:
    return {words[index : index + size] for index in range(len(words) - size + 1)}


class EpisodeGroundingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.normalized_dir = _private_normalized_dir()
        if cls.normalized_dir is None:
            raise unittest.SkipTest("Governed private normalized release is unavailable.")
        cls.dataset = {
            name: _load_json(cls.normalized_dir / f"{name}.json")
            for name in REQUIRED_COLLECTIONS
        }
        cls.public_summaries = _load_json(PUBLIC_DIR / "episode_summaries.json")
        legacy_relationships = PUBLIC_DIR / "episode_relationships.json"
        cls.public_relationships = (
            _load_json(legacy_relationships) if legacy_relationships.is_file() else []
        )
        cls.packages = build_private_source_packages(cls.dataset)
        cls.authoring_inputs = build_summary_authoring_inputs(cls.packages)

    def test_canonical_selection_excludes_all_alias_items(self):
        selected_sources = canonical_episode_sources(self.dataset)
        alias_sources = {
            row["sourceIdentityId"]
            for row in self.dataset["episode_source_mappings"]
            if row["mappingRole"] == "alias"
        }
        self.assertEqual(242, len(selected_sources))
        self.assertEqual(27, len(alias_sources))
        self.assertTrue(alias_sources.isdisjoint(selected_sources.values()))

        retained_by_episode, item_episode = retained_canonical_items(self.dataset)
        self.assertEqual(12_978, len(item_episode))
        self.assertEqual(242, len(retained_by_episode))
        self.assertTrue(all(retained_by_episode.values()))
        retained_source_ids = {
            item["sourceIdentityId"]
            for items in retained_by_episode.values()
            for item in items
        }
        self.assertTrue(alias_sources.isdisjoint(retained_source_ids))
        for episode_id, items in retained_by_episode.items():
            self.assertEqual(
                {selected_sources[episode_id]},
                {item["sourceIdentityId"] for item in items},
            )

    def test_every_public_summary_resolves_to_canonical_episode(self):
        package_by_id = {row["episodeId"]: row for row in self.packages}
        self.assertEqual(242, len(package_by_id))
        self.assertEqual(set(package_by_id), {row["episodeId"] for row in self.public_summaries})

        for summary in self.public_summaries:
            episode_id = summary["episodeId"]
            package = package_by_id[episode_id]
            with self.subTest(episode_id=episode_id):
                self.assertGreater(package["itemCount"], 0)
                self.assertEqual(package["itemCount"], len(package["structuredItems"]))
                self.assertEqual(
                    0,
                    package["summaryGenerationProvenance"][
                        "excludedAliasContribution"
                    ],
                )

    def test_every_public_summary_matches_private_transcript_manifest(self):
        private_dir = (
            REPO_ROOT
            / "analysis"
            / "cognitive-security"
            / "transcript-summaries-v1"
        )
        manifest_path = private_dir / "transcript_manifest.json"
        coverage_path = private_dir / "chunk_coverage.json"
        if not manifest_path.is_file() or not coverage_path.is_file():
            self.skipTest("Private transcript-summary manifest is unavailable.")
        manifest = _load_json(manifest_path)
        coverage = _load_json(coverage_path)
        manifest_by_id = {row["episodeId"]: row for row in manifest}
        self.assertEqual(242, len(manifest_by_id))
        self.assertEqual(
            set(manifest_by_id), {row["episodeId"] for row in self.public_summaries}
        )
        self.assertEqual(242, len(coverage))
        self.assertTrue(all(row["cleanedSequentialCoverageComplete"] for row in coverage))
        for summary in self.public_summaries:
            source = manifest_by_id[summary["episodeId"]]
            transcript_path = Path(source["selectedTranscriptPath"])
            with self.subTest(episode_id=summary["episodeId"]):
                self.assertTrue(transcript_path.is_file())
                self.assertEqual(
                    word_count(transcript_path.read_text(encoding="utf-8")),
                    summary["transcriptWordCount"],
                )
                self.assertNotIn("selectedTranscriptPath", summary)
                self.assertNotIn("transcriptSha256", summary)

    def test_published_relationships_equal_full_private_recomputation(self):
        if not self.public_relationships:
            self.skipTest(
                "Superseded legacy graph; canonical provenance has separate gates."
            )
        recomputed = build_episode_relationships(self.dataset)
        self.assertEqual(recomputed, self.public_relationships)

    def test_meta_and_theme_derivations_have_governed_paths(self):
        if not self.public_relationships:
            self.skipTest(
                "Superseded legacy graph; canonical provenance has separate gates."
            )
        cluster_rows = {
            (row["sourceId"], row["targetId"]): row
            for row in self.public_relationships
            if row["relationshipType"] == "episode-coded-to-cluster"
        }
        meta_by_cluster = defaultdict(set)
        for row in self.dataset["cluster_meta_mappings"]:
            meta_by_cluster[row["clusterId"]].add(row["metaClusterId"])
        themes_by_cluster = defaultdict(set)
        for row in self.dataset["theme_cluster_evidence"]:
            if not row.get("unresolvedReference"):
                themes_by_cluster[row["clusterId"]].add(row["themeId"])
        themes_by_meta = defaultdict(set)
        for row in self.dataset["theme_meta_mappings"]:
            themes_by_meta[row["metaClusterId"]].add(row["themeId"])

        for row in self.public_relationships:
            relationship_type = row["relationshipType"]
            if relationship_type == "episode-derived-to-meta-cluster":
                for cluster_id in row["supportingClusterIds"]:
                    self.assertIn((row["sourceId"], cluster_id), cluster_rows)
                    self.assertIn(row["targetId"], meta_by_cluster[cluster_id])
            elif relationship_type in {
                "episode-derived-to-theme",
                "episode-has-theme-lineage",
            }:
                for cluster_id in row["supportingClusterIds"]:
                    self.assertIn((row["sourceId"], cluster_id), cluster_rows)
                valid_cluster_path = any(
                    row["targetId"] in themes_by_cluster[cluster_id]
                    for cluster_id in row["supportingClusterIds"]
                )
                valid_meta_path = any(
                    row["targetId"] in themes_by_meta[meta_id]
                    for meta_id in row["supportingMetaClusterIds"]
                )
                self.assertTrue(valid_cluster_path or valid_meta_path)

    def test_direct_theme_and_tension_lineage_resolves_to_retained_items(self):
        if not self.public_relationships:
            self.skipTest(
                "Superseded legacy graph; canonical provenance has separate gates."
            )
        retained_by_episode, _ = retained_canonical_items(self.dataset)
        retained_ids = {
            episode_id: {row["itemId"] for row in items}
            for episode_id, items in retained_by_episode.items()
        }
        theme_evidence = {
            row["themeId"]: set(row.get("representativeItemIds", ()))
            for row in self.dataset["themes"]
        }
        tension_evidence = {
            row["tensionId"]: (
                set(row.get("supportingItemIdsPoleA", ())),
                set(row.get("supportingItemIdsPoleB", ())),
            )
            for row in self.dataset["tensions"]
        }

        for row in self.public_relationships:
            episode_items = retained_ids[row["sourceId"]]
            if row["relationshipType"] == "episode-has-theme-lineage":
                direct = episode_items & theme_evidence[row["targetId"]]
                self.assertEqual(len(direct), row["itemCount"])
                self.assertTrue(direct)
            elif row["relationshipType"] == "episode-has-tension-lineage":
                pole_a, pole_b = tension_evidence[row["targetId"]]
                self.assertEqual(len(episode_items & pole_a), row["poleASupportCount"])
                self.assertEqual(len(episode_items & pole_b), row["poleBSupportCount"])
                self.assertEqual(
                    len(episode_items & (pole_a | pole_b)), row["itemCount"]
                )

    def test_public_summary_text_is_not_raw_private_item_text(self):
        package_by_id = {row["episodeId"]: row for row in self.packages}
        for summary in self.public_summaries:
            public_words = _normalized_words(
                f"{summary['summary']} {summary['whyItMatters']}"
            )
            public_ngrams = _ngrams(public_words, 18)
            private_ngrams: set[tuple[str, ...]] = set()
            for item in package_by_id[summary["episodeId"]]["structuredItems"]:
                for field in (
                    "summary",
                    "strategicSignificance",
                    "operationalImplications",
                ):
                    private_ngrams.update(_ngrams(_normalized_words(item.get(field)), 18))
            with self.subTest(episode_id=summary["episodeId"]):
                self.assertFalse(
                    public_ngrams & private_ngrams,
                    "Public synthesis contains an 18-word private-source sequence.",
                )

    def test_public_products_contain_no_private_identifiers_or_paths(self):
        public_blob = json.dumps(
            {
                "summaries": self.public_summaries,
                "relationships": self.public_relationships,
            },
            ensure_ascii=False,
        ).casefold()
        for forbidden in (
            "sourceidentityid",
            "canonicalsourceidentityid",
            "itemid",
            "evidenceexcerpt",
            "sourcefilename",
            "reviewernotes",
            "assignmentrationale",
            "c:\\users\\",
            "/users/",
        ):
            self.assertNotIn(forbidden, public_blob)


if __name__ == "__main__":
    unittest.main()
