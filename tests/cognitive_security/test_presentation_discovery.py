"""Phase A presentation, icon, metadata, and episode-discovery gates."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest

from scripts.cognitive_security.discovery import (
    DiscoveryError,
    MAIN_TOPIC_DISPLAY_LIMIT,
    PRIMARY_ITEM_MINIMUM,
    PROMINENCE_SHARE_MINIMUM,
    SIMILARITY_MINIMUM,
    SIMILARITY_SHARED_TOPIC_MINIMUM,
    TopicCount,
    boolean_jaccard,
    build_discovery_package,
    freeze_episode_metadata,
    qualified_topics,
    weighted_jaccard,
)


ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "data" / "cognitive-security"
DISCOVERY = ROOT / "data" / "cognitive-security-discovery"
ICONS = ROOT / "cognitive-security" / "assets" / "entry-icons"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class DiscoveryNumericTests(unittest.TestCase):
    def test_weighted_jaccard_known_examples_symmetry_bounds_and_empty(self):
        left = {"a": 0.75, "b": 0.25}
        right = {"a": 0.25, "b": 0.75}
        expected = 0.5 / 1.5
        self.assertAlmostEqual(expected, weighted_jaccard(left, right))
        self.assertAlmostEqual(expected, weighted_jaccard(right, left))
        self.assertEqual(1.0, weighted_jaccard(left, left))
        self.assertIsNone(weighted_jaccard({}, right))
        self.assertIsNone(weighted_jaccard({"a": 0.0}, {"a": 0.0}))
        self.assertEqual(0.0, weighted_jaccard({"a": 1.0}, {"b": 1.0}))

    def test_boolean_baseline_is_explicit_and_handles_empty_profiles(self):
        self.assertAlmostEqual(2 / 3, boolean_jaccard(["a", "b"], ["b", "c", "a"]))
        self.assertIsNone(boolean_jaccard([], ["a"]))

    def test_main_topic_policy_rejects_secondary_only_and_is_deterministic(self):
        counts = {
            "secondary": TopicCount("secondary", 0, 50, 50),
            "primary": TopicCount("primary", 10, 0, 20),
            "too-small": TopicCount("too-small", 1, 100, 102),
        }
        selected = qualified_topics(
            counts,
            share_minimum=PROMINENCE_SHARE_MINIMUM,
            primary_minimum=PRIMARY_ITEM_MINIMUM,
        )
        self.assertEqual(["primary"], [item.topic_id for item in selected])


class EpisodeMetadataMatchingTests(unittest.TestCase):
    def _freeze(
        self,
        *,
        catalog_title,
        official_title,
        parsed_number,
        official_url="https://information-professionals.org/episode/test/",
        official_post_id=9001,
    ):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            core = root / "core"
            cache = root / "cache"
            core.mkdir()
            cache.mkdir()
            (core / "episodes.json").write_text(
                json.dumps(
                    [
                        {
                            "episodeId": "EPI-TEST",
                            "episodeTitle": catalog_title,
                            "parsedEpisodeNumber": parsed_number,
                        }
                    ]
                ),
                encoding="utf-8",
            )
            (cache / "podcasts-page-1.json").write_text(
                json.dumps(
                    [
                        {
                            "id": official_post_id,
                            "date": "2024-01-02T12:00:00",
                            "link": official_url,
                            "title": {"rendered": official_title},
                        }
                    ]
                ),
                encoding="utf-8",
            )
            public_output = root / "episode_metadata.json"
            audit_output = root / "metadata_audit.json"
            audit = freeze_episode_metadata(
                core_dir=core,
                cache_dir=cache,
                public_output=public_output,
                private_audit_output=audit_output,
                retrieved_at="2026-09-04",
            )
            return load(public_output), audit

    def test_number_and_exact_compatible_title_match(self):
        public, audit = self._freeze(
            catalog_title="#12 Tammekänd on Deepfakes",
            official_title="#12 Tammekänd on Deepfakes",
            parsed_number=12,
        )
        self.assertIsNotNone(public[0]["officialEpisodeUrl"])
        self.assertEqual(
            "episode-number-and-exact-normalized-title",
            audit["records"][0]["matchMethod"],
        )

    def test_number_and_compatible_shortened_name_match(self):
        public, audit = self._freeze(
            catalog_title="#65 Sean Guillory on Cognitive Neuroscience Applications",
            official_title="#65 Guillory on Cognitive Neuroscience Applications",
            parsed_number=65,
        )
        self.assertIsNotNone(public[0]["officialEpisodeUrl"])
        self.assertEqual(
            "episode-number-and-compatible-title", audit["records"][0]["matchMethod"]
        )
        self.assertEqual("compatible", audit["records"][0]["titleCompatibility"]["status"])

    def test_number_and_materially_conflicting_title_remain_unresolved(self):
        public, audit = self._freeze(
            catalog_title="#65 Guillory on Cognitive Neuroscience Applications",
            official_title="#65 Different Guest on Unrelated Operations",
            parsed_number=65,
        )
        self.assertIsNone(public[0]["officialEpisodeUrl"])
        self.assertIsNone(audit["records"][0]["matchMethod"])
        self.assertEqual("conflict", audit["records"][0]["titleCompatibility"]["status"])
        self.assertIn("title compatibility", audit["records"][0]["unresolvedReason"])

    def test_normalized_punctuation_difference_matches(self):
        public, audit = self._freeze(
            catalog_title="#12 Tammekänd on “Deepfakes”",
            official_title="#12 Tammekänd on Deepfakes",
            parsed_number=12,
        )
        self.assertIsNotNone(public[0]["officialEpisodeUrl"])
        self.assertEqual(
            "episode-number-and-exact-normalized-title",
            audit["records"][0]["matchMethod"],
        )

    def test_governed_title_exception_is_explicit_and_audited(self):
        public, audit = self._freeze(
            catalog_title="#28 Mushtare and Branch on PSYOP, Manpower, and IO Initiatives",
            official_title="#28 Mushatare and Branch on PSYOP, Manpower, and IO Initiatives",
            parsed_number=28,
            official_post_id=9621,
        )
        self.assertIsNotNone(public[0]["officialEpisodeUrl"])
        record = audit["records"][0]
        self.assertEqual("episode-number-and-governed-title-exception", record["matchMethod"])
        self.assertEqual("governed-title-exception", record["titleCompatibility"]["method"])
        self.assertTrue(record["titleCompatibility"]["exceptionReason"])

    def test_exact_normalized_title_fallback_matches_without_episode_number(self):
        public, audit = self._freeze(
            catalog_title="Arun Seraphin on the SASC and Emerging Technology",
            official_title="#98 Arun Seraphin on the SASC and Emerging Technology",
            parsed_number=None,
        )
        self.assertIsNotNone(public[0]["officialEpisodeUrl"])
        self.assertEqual("exact-normalized-title", audit["records"][0]["matchMethod"])

    def test_unmatched_title_remains_unresolved(self):
        public, audit = self._freeze(
            catalog_title="Unnumbered private event",
            official_title="#77 Lopata on Quantum",
            parsed_number=None,
        )
        self.assertIsNone(public[0]["officialEpisodeUrl"])
        self.assertIsNone(audit["records"][0]["matchMethod"])

    def test_matched_record_rejects_nonofficial_host(self):
        with self.assertRaisesRegex(DiscoveryError, "Unapproved official host"):
            self._freeze(
                catalog_title="#12 Tammekänd on Deepfakes",
                official_title="#12 Tammekänd on Deepfakes",
                parsed_number=12,
                official_url="https://example.com/episode/test/",
            )


class DiscoveryPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load(DISCOVERY / "discovery_manifest.json")
        cls.metadata = load(DISCOVERY / "episode_metadata.json")
        cls.discovery = load(DISCOVERY / "episode_discovery.json")
        cls.topic_index = load(DISCOVERY / "topic_episode_index.json")
        cls.similarity = load(DISCOVERY / "similarity_data.json")
        cls.episodes = load(CORE / "episodes.json")
        cls.provenance = load(CORE / "provenance.json")

    def test_overlay_inventory_counts_and_hashes_are_closed(self):
        expected = [
            "episode_metadata.json",
            "episode_discovery.json",
            "topic_episode_index.json",
            "similarity_data.json",
            "presentation_copy.json",
        ]
        self.assertEqual(expected, self.manifest["publicFiles"])
        self.assertEqual(5, self.manifest["fileCount"])
        self.assertEqual(242, self.manifest["counts"]["publicReleaseCount"])
        self.assertEqual(241, self.manifest["counts"]["contentUnitCount"])
        for entry in self.manifest["files"]:
            payload = (DISCOVERY / entry["file"]).read_bytes()
            self.assertEqual(entry["bytes"], len(payload))
            self.assertEqual(entry["sha256"], hashlib.sha256(payload).hexdigest())

    def test_presentation_copy_omits_the_retained_internal_finding_layer(self):
        copy = load(DISCOVERY / "presentation_copy.json")
        keys = [entry["key"] for entry in copy["entries"]]
        self.assertEqual(10, len(keys))
        self.assertNotIn("findings-open-questions", keys)
        serialized = json.dumps(copy, ensure_ascii=False).casefold()
        self.assertNotIn("findings & open questions", serialized)
        self.assertNotIn("multiple findings", serialized)

    def test_metadata_is_complete_nullable_and_official_only(self):
        self.assertEqual(242, len(self.metadata))
        self.assertEqual({episode["episodeId"] for episode in self.episodes}, {row["episodeId"] for row in self.metadata})
        for row in self.metadata:
            self.assertEqual({"episodeId", "publishedAt", "guests", "officialEpisodeUrl"}, set(row))
            if row["officialEpisodeUrl"]:
                self.assertTrue(row["officialEpisodeUrl"].startswith("https://information-professionals.org/"))
        self.assertEqual(237, sum(bool(row["officialEpisodeUrl"]) for row in self.metadata))
        self.assertEqual(237, sum(bool(row["publishedAt"]) for row in self.metadata))
        self.assertEqual(229, sum(bool(row["guests"]) for row in self.metadata))
        self.assertEqual(5, sum(row["officialEpisodeUrl"] is None for row in self.metadata))

    def test_public_overlay_contains_no_private_paths_files_or_secrets(self):
        forbidden_keys = {
            "itemid", "itemids", "transcripttext", "transcriptpath",
            "localpath", "sourcefilename", "workbookname", "reviewnotes",
            "adjudicationrationale", "prompt", "credential",
        }
        patterns = (
            r"(?i)[a-z]:\\users\\", r"(?i)/users/", r"(?i)\.xlsx\b",
            r"\bgh[pousr]_[A-Za-z0-9]{20,}\b", r"\bAKIA[0-9A-Z]{16}\b",
            r"\bsk-[A-Za-z0-9_-]{20,}\b",
            r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
        )

        def walk(value):
            if isinstance(value, dict):
                for key, nested in value.items():
                    normalized = re.sub(r"[^a-z0-9]", "", key.casefold())
                    self.assertNotIn(normalized, forbidden_keys)
                    walk(nested)
            elif isinstance(value, list):
                for nested in value:
                    walk(nested)

        for path in sorted(DISCOVERY.glob("*.json")):
            text = path.read_text(encoding="utf-8")
            for pattern in patterns:
                self.assertIsNone(re.search(pattern, text), f"{path.name}: {pattern}")
            walk(json.loads(text))

    def test_saved_topic_weights_match_existing_formula(self):
        for links in self.provenance["clusterToReleases"].values():
            for link in links:
                self.assertEqual(
                    2 * link["primaryItemCount"] + link["secondaryItemCount"],
                    link["governedWeightedCount"],
                )

    def test_display_cap_does_not_truncate_similarity_profile(self):
        profiles = {
            row["contentEpisodeId"]: {topic["topicId"] for topic in row["topics"]}
            for row in self.similarity["profiles"]
        }
        for row in self.discovery["records"]:
            self.assertLessEqual(len(row["defaultMainTopicIds"]), MAIN_TOPIC_DISPLAY_LIMIT)
            self.assertEqual(set(row["mainTopicIds"]), profiles[row["contentEpisodeId"]])

    def test_recommendations_are_bounded_explained_and_content_deduplicated(self):
        records = {row["episodeId"]: row for row in self.discovery["records"]}
        for row in records.values():
            seen_content = set()
            for recommendation in row["similarOverall"]:
                target = records[recommendation["episodeId"]]
                self.assertNotEqual(row["contentEpisodeId"], target["contentEpisodeId"])
                self.assertNotIn(target["contentEpisodeId"], seen_content)
                seen_content.add(target["contentEpisodeId"])
                self.assertGreaterEqual(recommendation["score"], SIMILARITY_MINIMUM)
                self.assertLessEqual(recommendation["score"], 1)
                self.assertGreaterEqual(len(recommendation["sharedTopicIds"]), SIMILARITY_SHARED_TOPIC_MINIMUM)

    def test_shared_release_inherits_topics_without_duplicate_recommendations(self):
        shared = [row for row in self.discovery["records"] if row["isSharedContentRelease"]]
        self.assertEqual(1, len(shared))
        alias = shared[0]
        original = next(row for row in self.discovery["records"] if row["episodeId"] == alias["contentEpisodeId"])
        self.assertEqual(original["mainTopicIds"], alias["mainTopicIds"])
        self.assertEqual(original["similarOverall"], alias["similarOverall"])
        self.assertNotIn(original["episodeId"], {row["episodeId"] for row in alias["similarOverall"]})

    def test_builder_is_byte_deterministic_offline(self):
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            outputs = []
            for directory in (Path(first_dir), Path(second_dir)):
                shutil.copyfile(DISCOVERY / "episode_metadata.json", directory / "episode_metadata.json")
                build_discovery_package(core_dir=CORE, output_dir=directory)
                outputs.append({path.name: path.read_bytes() for path in sorted(directory.glob("*.json"))})
            self.assertEqual(outputs[0], outputs[1])


class IconPackageTests(unittest.TestCase):
    def test_all_supplied_icons_are_registered_and_present_in_both_formats(self):
        registry = load(ICONS / "icon_registry.json")
        self.assertEqual("1.0", registry["schemaVersion"])
        self.assertEqual(11, len(registry["icons"]))
        self.assertEqual(11, len({row["key"] for row in registry["icons"]}))
        for row in registry["icons"]:
            self.assertEqual((256, 256), (row["width"], row["height"]))
            png = ICONS / row["png"]
            webp = ICONS / row["webp"]
            self.assertTrue(png.is_file(), png)
            self.assertTrue(webp.is_file(), webp)
            self.assertEqual(b"\x89PNG\r\n\x1a\n", png.read_bytes()[:8])
            self.assertEqual(b"RIFF", webp.read_bytes()[:4])
            self.assertEqual(b"WEBP", webp.read_bytes()[8:12])


if __name__ == "__main__":
    unittest.main()
