"""Release acceptance tests for grounded, navigable episode products."""

from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import subprocess
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLIC_DIR = REPO_ROOT / "data" / "cognitive-security"
EXPLORER_DIR = REPO_ROOT / "cognitive-security"

EXPECTED_RELATIONSHIP_COUNTS = {
    "episode-participates-in-category": 2_410,
    "episode-coded-to-cluster": 10_757,
    "episode-derived-to-meta-cluster": 5_864,
    "episode-derived-to-theme": 2_625,
    "episode-has-theme-lineage": 34,
    "episode-has-tension-lineage": 165,
}
EXPECTED_SEMANTICS = {
    "episode-participates-in-category": ("category", "direct-item-aggregation"),
    "episode-coded-to-cluster": ("cluster", "direct-coded-relationship"),
    "episode-derived-to-meta-cluster": (
        "metaCluster",
        "derived-through-cluster-membership",
    ),
    "episode-derived-to-theme": ("theme", "derived-analytical-connection"),
    "episode-has-theme-lineage": ("theme", "direct-item-lineage"),
    "episode-has-tension-lineage": ("tension", "direct-item-lineage"),
}


def load_json(filename: str):
    return json.loads((PUBLIC_DIR / filename).read_text(encoding="utf-8"))


class EpisodeAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.episodes = load_json("episodes.json")
        cls.summaries = load_json("episode_summaries.json")
        cls.episode_relationships = load_json("episode_relationships.json")
        cls.historical_relationships = load_json("relationships.json")
        cls.manifest = load_json("manifest.json")
        cls.index_html = (EXPLORER_DIR / "index.html").read_text(encoding="utf-8")
        cls.app_js = (EXPLORER_DIR / "app.js").read_text(encoding="utf-8")

        cls.ids_by_type = {
            "episode": {row["episodeId"] for row in cls.episodes},
            "category": {row["categoryId"] for row in load_json("categories.json")},
            "cluster": {row["clusterId"] for row in load_json("clusters.json")},
            "metaCluster": {
                row["metaClusterId"] for row in load_json("meta_clusters.json")
            },
            "theme": {row["themeId"] for row in load_json("themes.json")},
            "tension": {row["tensionId"] for row in load_json("tensions.json")},
        }

    def test_episode_summaries_are_complete_grounded_and_frozen(self):
        self.assertEqual(242, len(self.episodes))
        self.assertEqual(242, len(self.summaries))
        self.assertEqual(
            self.ids_by_type["episode"],
            {row["episodeId"] for row in self.summaries},
        )
        self.assertEqual(242, len({row["episodeId"] for row in self.summaries}))

        episodes_by_id = {row["episodeId"]: row for row in self.episodes}
        for row in self.summaries:
            with self.subTest(episode_id=row["episodeId"]):
                self.assertEqual(
                    {
                        "episodeId",
                        "summary",
                        "keyTopics",
                        "whyItMatters",
                        "sourceItemCount",
                        "focalItemCount",
                        "contextualItemCount",
                        "generationMethod",
                    },
                    set(row),
                )
                self.assertLessEqual(100, len(row["summary"].split()))
                self.assertLessEqual(len(row["summary"].split()), 180)
                self.assertGreaterEqual(len(row["keyTopics"]), 3)
                self.assertLessEqual(len(row["keyTopics"]), 6)
                self.assertTrue(all(topic.strip() for topic in row["keyTopics"]))
                self.assertGreaterEqual(len(row["whyItMatters"].split()), 12)
                self.assertEqual("codex-grounded-synthesis-v1", row["generationMethod"])
                self.assertEqual(
                    row["sourceItemCount"],
                    row["focalItemCount"] + row["contextualItemCount"],
                )
                self.assertEqual(
                    episodes_by_id[row["episodeId"]]["reconciledSensitivityItemCount"],
                    row["sourceItemCount"],
                )

    def test_summaries_are_not_a_repeated_template(self):
        normalized = [
            re.sub(r"\W+", " ", row["summary"].casefold()).strip()
            for row in self.summaries
        ]
        self.assertEqual(len(normalized), len(set(normalized)))
        opening_phrases = Counter(" ".join(text.split()[:8]) for text in normalized)
        self.assertLessEqual(max(opening_phrases.values()), 3)
        combined = "\n".join(normalized)
        for forbidden in (
            "this episode explores the complex landscape",
            "in today s rapidly evolving world",
            "the discussion underscores the importance of leveraging",
        ):
            self.assertNotIn(forbidden, combined)

    def test_standalone_relationship_counts_and_semantics(self):
        self.assertEqual(21_855, len(self.episode_relationships))
        self.assertEqual(
            EXPECTED_RELATIONSHIP_COUNTS,
            dict(Counter(row["relationshipType"] for row in self.episode_relationships)),
        )
        relationship_ids = [row["relationshipId"] for row in self.episode_relationships]
        self.assertEqual(len(relationship_ids), len(set(relationship_ids)))

        for row in self.episode_relationships:
            with self.subTest(relationship_id=row["relationshipId"]):
                expected_target, expected_semantics = EXPECTED_SEMANTICS[
                    row["relationshipType"]
                ]
                self.assertEqual("episode", row["sourceType"])
                self.assertEqual(expected_target, row["targetType"])
                self.assertEqual(expected_semantics, row["relationshipSemantics"])
                self.assertIn(row["sourceId"], self.ids_by_type["episode"])
                self.assertIn(row["targetId"], self.ids_by_type[expected_target])

    def test_direct_counts_are_consistent(self):
        category_totals = defaultdict(lambda: {"focal": 0, "contextual": 0})
        cluster_totals = defaultdict(lambda: {"primary": 0, "secondary": 0})
        for row in self.episode_relationships:
            if row["relationshipType"] == "episode-participates-in-category":
                self.assertEqual(
                    row["itemCount"],
                    row["focalItemCount"] + row["contextualItemCount"],
                )
                category_totals[row["sourceId"]]["focal"] += row["focalItemCount"]
                category_totals[row["sourceId"]]["contextual"] += row[
                    "contextualItemCount"
                ]
            elif row["relationshipType"] == "episode-coded-to-cluster":
                self.assertEqual(
                    row["weightedCount"],
                    2 * row["primaryCount"] + row["secondaryCount"],
                )
                cluster_totals[row["sourceId"]]["primary"] += row["primaryCount"]
                cluster_totals[row["sourceId"]]["secondary"] += row["secondaryCount"]

        summaries_by_id = {row["episodeId"]: row for row in self.summaries}
        for episode_id, summary in summaries_by_id.items():
            self.assertEqual(summary["focalItemCount"], category_totals[episode_id]["focal"])
            self.assertEqual(
                summary["contextualItemCount"],
                category_totals[episode_id]["contextual"],
            )
        self.assertEqual(9_855, sum(row["primary"] for row in cluster_totals.values()))
        self.assertEqual(9_473, sum(row["secondary"] for row in cluster_totals.values()))

    def test_tension_links_are_direct_lineage_only(self):
        tension_rows = [
            row for row in self.episode_relationships if row["targetType"] == "tension"
        ]
        self.assertEqual(165, len(tension_rows))
        for row in tension_rows:
            self.assertEqual("episode-has-tension-lineage", row["relationshipType"])
            self.assertEqual("direct-item-lineage", row["relationshipSemantics"])
            self.assertGreater(row["itemCount"], 0)
            self.assertGreaterEqual(
                row["itemCount"],
                max(row["poleASupportCount"], row["poleBSupportCount"]),
            )
            self.assertLessEqual(
                row["itemCount"],
                row["poleASupportCount"] + row["poleBSupportCount"],
            )
            self.assertIn("does not mean", row["interpretiveCaveat"])

    def test_historical_graph_contains_no_episode_edges_and_is_unchanged(self):
        self.assertEqual(975, len(self.historical_relationships))
        self.assertFalse(
            [
                row
                for row in self.historical_relationships
                if row.get("sourceType") == "episode" or row.get("targetType") == "episode"
            ]
        )
        result = subprocess.run(
            [
                "git",
                "diff",
                "--exit-code",
                "origin/main",
                "--",
                "data/cognitive-security/relationships.json",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_manifest_and_browser_load_separate_episode_products(self):
        manifest_files = set(self.manifest["publicFiles"])
        self.assertIn("episode_summaries.json", manifest_files)
        self.assertIn("episode_relationships.json", manifest_files)
        self.assertRegex(self.app_js, r'["\']episode_summaries\.json["\']')
        self.assertRegex(self.app_js, r'["\']episode_relationships\.json["\']')

    def test_navigation_route_search_breadcrumb_and_copy_contract(self):
        expected_labels = (
            "Overview",
            "Browse",
            "Cross-Cutting Themes",
            "Tensions &amp; Debates",
            "Meta-Narratives",
            "Future Scenarios",
            "Episodes",
            "Search",
            "Methodology",
        )
        positions = [self.index_html.index(label) for label in expected_labels]
        self.assertEqual(sorted(positions), positions)
        for token in (
            'view: "episodes"',
            'episode: "episode"',
            "parsedEpisodeNumber",
            "episodeSummary",
            "episodeRelationships",
            "history.pushState",
            "popstate",
            "navigator.clipboard.writeText",
            "document.execCommand(\"copy\")",
            "Cognitive Security Map",
            "No episode matches",
        ):
            with self.subTest(token=token):
                self.assertIn(token, self.app_js)

    def test_required_detail_language_is_explicit(self):
        for token in (
            'element("h2", "section-title", "Intermediate clusters")',
            'element("h2", "section-title", "Theme summary")',
            'section("Why this matters", theme.strategicSignificance)',
            'element("h2", "section-title", "Strategic significance")',
            "has no separate strategic-significance field",
            "Plausibility exercise — not a prediction.",
        ):
            with self.subTest(token=token):
                self.assertIn(token, self.app_js)

    def test_search_filter_is_governed_and_does_not_expose_private_records(self):
        for label in (
            "Categories",
            "Meta-clusters",
            "Clusters",
            "Themes",
            "Tensions",
            "Meta-narratives",
            "Scenarios",
            "Episodes",
        ):
            self.assertIn(label, self.app_js)
        public_blob = json.dumps(
            {"summaries": self.summaries, "relationships": self.episode_relationships}
        ).casefold()
        for forbidden in (
            "sourceidentityid",
            "itemid",
            "speakername",
            "reviewernotes",
            "assignmentrationale",
        ):
            self.assertNotIn(forbidden, public_blob)

    def test_no_arbitrary_assignment_implementation(self):
        implementation = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (
                REPO_ROOT / "scripts" / "cognitive_security" / "episode_products.py",
                REPO_ROOT / "scripts" / "build_episode_products.py",
            )
        ).casefold()
        for forbidden in (
            "round-robin",
            "round robin",
            "index %",
            "episode_number %",
            "title-derived assignment",
            "fixed topic bank",
        ):
            self.assertNotIn(forbidden, implementation)


if __name__ == "__main__":
    unittest.main()
