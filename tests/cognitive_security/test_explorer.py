"""Canonical public-data and static Explorer acceptance tests.

The production application is dependency-free. These tests intentionally use
only the Python standard library and validate the shipped projection, browser
contract, privacy boundary, routes, visualizations, and accessibility hooks.
"""

from __future__ import annotations

from collections import Counter
import json
import math
from pathlib import Path
import re
import unittest
from urllib.parse import parse_qs, quote, unquote, urlencode


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPLORER_DIR = REPO_ROOT / "cognitive-security"
PUBLIC_DIR = REPO_ROOT / "data" / "cognitive-security"

SUPPORT_INTERPRETATION = (
    "Corpus support reflects recurrence and breadth within this practitioner "
    "discourse corpus. It does not indicate scientific validity, consensus, "
    "importance, prevalence, or real-world effect size."
)
PUBLIC_FILES = (
    "manifest.json",
    "coverage.json",
    "categories.json",
    "clusters.json",
    "cluster_summaries.json",
    "families.json",
    "themes.json",
    "tensions.json",
    "narratives.json",
    "category_findings.json",
    "scenarios.json",
    "episodes.json",
    "episode_summaries.json",
    "relationships.json",
    "relationship_semantics.json",
    "provenance.json",
    "heatmap.json",
    "qa_report.json",
)
RETIRED_FILES = {
    "corpus_reconciliation.json",
    "meta_clusters.json",
    "meta_narratives.json",
    "episode_relationships.json",
    "review_summary.json",
}
COLLECTIONS = {
    "category": ("categories.json", "categoryId"),
    "cluster": ("clusters.json", "clusterId"),
    "family": ("families.json", "familyId"),
    "theme": ("themes.json", "themeId"),
    "tension": ("tensions.json", "tensionId"),
    "narrative": ("narratives.json", "narrativeId"),
    "finding": ("category_findings.json", "findingId"),
    "scenario": ("scenarios.json", "scenarioId"),
    "episode": ("episodes.json", "episodeId"),
}
ROUTE_TYPES = {
    "category": "category",
    "family": "family",
    "cluster": "cluster",
    "theme": "theme",
    "tension": "tension",
    "narrative": "narrative",
    "scenario": "scenario",
    "episode": "episode",
}
EXPECTED_COUNTS = {
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
EXPECTED_THEME_NAMES = {
    "TH-01": "Institutionalized Information Capability",
    "TH-02": "Epistemic Infrastructure for Contested Reality",
    "TH-03": "Platform Architecture as the Terrain of Influence",
    "TH-04": "AI-Enabled Scale as Both Overmatch and Exposure",
    "TH-05": "Human Reception and Societal Resilience",
    "TH-06": "Datafied Identity as Security Asset and Attack Surface",
    "TH-07": "Multi-Actor Alignment and Networked Execution",
    "TH-08": "Mission Continuity on a Contested Technical Substrate",
    "TH-09": "Knowledge-to-Practice Pipelines for a Professionalizing Field",
    "TH-10": "Asymmetric Tempo, Cost, and Constraint in Gray-Zone Competition",
    "TH-11": "Legitimacy-Preserving Governance of Information Power",
}
REQUIRED_ROLES = {
    "direct-coded-support",
    "primary-family-membership",
    "secondary-family-relationship",
    "primary-theme-support",
    "secondary-theme-support",
    "conceptual-framing",
    "future-extension",
    "tension-evidence-pole-a",
    "tension-evidence-pole-b",
    "activated-tension",
    "contextual-connection",
    "shared-content-inheritance",
}


def load_json(filename: str):
    return json.loads((PUBLIC_DIR / filename).read_text(encoding="utf-8"))


def walk(value, path: tuple[str, ...] = ()):
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk(child, path + (str(key),))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, path + (str(index),))


class ExplorerStaticContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (EXPLORER_DIR / "index.html").read_text(encoding="utf-8")
        cls.javascript = (EXPLORER_DIR / "app.js").read_text(encoding="utf-8")
        cls.css = (EXPLORER_DIR / "styles.css").read_text(encoding="utf-8")
        cls.combined = "\n".join((cls.html, cls.javascript, cls.css))

    def test_required_assets_are_local_and_dependency_free(self):
        for filename in ("index.html", "app.js", "styles.css"):
            self.assertTrue((EXPLORER_DIR / filename).is_file(), filename)
        self.assertIn('href="../shared/psywerx.css"', self.html)
        self.assertIn('src="./app.js"', self.html)
        self.assertIn('src="../shared/assets/psywerx-logo.png"', self.html)
        self.assertNotRegex(
            self.combined,
            r"https?://|cdnjs|unpkg|jsdelivr|googleapis|analytics",
        )

    def test_browser_inventory_matches_the_closed_public_manifest(self):
        for filename in PUBLIC_FILES:
            self.assertIn(f'"{filename}"', self.javascript, filename)
        for filename in RETIRED_FILES:
            self.assertNotIn(filename, self.javascript, filename)
        self.assertIn(
            'const LAZY_PUBLIC_FILES = Object.freeze(["relationships.json", "provenance.json"])',
            self.javascript,
        )
        self.assertIn("PUBLIC_DATA_FILES.filter", self.javascript)
        self.assertIn("EAGER_PUBLIC_FILES.map(fetchPublicJson)", self.javascript)
        self.assertIn("ensureRelationships", self.javascript)
        self.assertIn("ensureProvenance", self.javascript)

    def test_start_here_and_primary_navigation_are_complete(self):
        expected = [
            ("start", "Start Here"),
            ("families", "Categories"),
            ("themes", "Themes"),
            ("tensions", "Tensions"),
            ("narratives", "Narratives"),
            ("scenarios", "Scenarios"),
            ("episodes", "Episodes"),
            ("search", "Search"),
            ("methodology", "Methodology"),
        ]
        for view, label in expected:
            self.assertRegex(
                self.html,
                rf'data-route-view="{re.escape(view)}"[^>]*>{label}</a>',
            )
        for entry in (
            "Choose an entry point",
            "Categories",
            "Subcategories",
            "Topics",
            "How the Explorer fits together",
        ):
            self.assertIn(entry, self.javascript)
        for removed in (
            "Findings & Open Questions",
            "Contextual takeaways",
            "Findings and open questions",
            "Subcategory findings",
            "Integrative category finding",
            "What the corpus says",
        ):
            self.assertNotIn(removed, self.javascript)
        self.assertIn("Explore the ideas, connections, and conversations", self.html)
        self.assertNotIn("approved canonical synthesis", self.html.lower())

    def test_support_display_is_two_layer_noncomposite_and_interpreted(self):
        self.assertIn(SUPPORT_INTERPRETATION, self.javascript)
        self.assertIn("Analytical details", self.javascript)
        self.assertIn("Primary corpus support", self.javascript)
        self.assertIn("Broader traceable reach", self.javascript)
        self.assertIn('"details"', self.javascript)
        self.assertIn("primary subcategories", self.javascript.lower())
        self.assertIn("primary topics", self.javascript.lower())
        self.assertIn("support concentration", self.javascript.lower())
        self.assertIn("primaryContentUnitCount", self.javascript)
        self.assertIn("primary-support content units", self.javascript)
        self.assertNotIn("directContentUnitCount", self.javascript)
        self.assertNotIn("direct content units", self.javascript.lower())
        self.assertIn(
            "Primary support is the evidence designated as primary for this entity. Its path depends on entity type",
            self.javascript,
        )
        for clarification in (
            "retained items directly coded to that cluster",
            "primary support comes from its member topics",
            "primary support comes from primary-support subcategories and topics",
            "evidence directly allocated to Pole A or Pole B",
            "primary evidence is inherited through integrated map constructs",
            "primary evidence is traced through supporting subcategories and topics",
            "primary evidence is traced through relevant map constructs",
        ):
            self.assertIn(clarification, self.javascript)
        for prohibited in (
            "importance score",
            "consensus score",
            "evidence quality score",
            "prevalence score",
        ):
            self.assertNotIn(prohibited, self.combined.lower())
        self.assertNotIn("Frequency reflects discourse prevalence", self.html)

    def test_visualizations_have_complete_controls_and_noncolor_semantics(self):
        self.assertIn("function renderCategoryThemeHeatmap", self.javascript)
        self.assertIn('element("table", "heatmap-table")', self.javascript)
        self.assertIn("normalizedPrimarySupportBreadth", self.javascript)
        self.assertIn("primaryFamilyCount", self.javascript)
        self.assertIn("primaryClusterCount", self.javascript)
        self.assertIn("primaryContentUnitCount", self.javascript)
        self.assertIn("color is only a secondary cue", self.javascript)
        self.assertIn("function renderTensionMatrix", self.javascript)
        for name in ("tensionType", "category", "theme", "scenario", "support"):
            self.assertIn(f'name: "{name}"', self.javascript)
        self.assertIn("function renderEvidenceSlice", self.javascript)
        self.assertIn("one public relationship slice at a time", self.javascript)
        self.assertIn("no arrow or causal direction is asserted", self.javascript)

    def test_entity_details_expose_required_canonical_context(self):
        for token in (
            "Related ideas",
            '{ label: "Themes"',
            '{ label: "Tensions"',
            "Source episodes",
            '{ label: "Narratives"',
            "Related scenarios",
            "Response options are analytical possibilities, not validated recommendations.",
        ):
            self.assertIn(token, self.javascript)
        self.assertIn("Rights and governance safeguards are essential", self.javascript)
        for token in (
            "legal",
            "privacy",
            "civil-liberties",
            "ethics",
            "consent",
            "affected-community",
        ):
            self.assertIn(token, self.javascript.lower())

    def test_routes_history_copy_refresh_and_not_found_contract(self):
        for token in (
            "history.pushState",
            "history.replaceState",
            'window.addEventListener("popstate"',
            "navigator.clipboard.writeText",
            "renderCopyLinkAction",
            "parseRoute",
            "routeHref",
            "canonicalizeRoute",
            "That view is not part of this public map",
        ):
            self.assertIn(token, self.javascript)
        self.assertIn("Copy link", self.javascript)
        self.assertIn("The relevant index is shown", self.javascript)
        self.assertIn("window.location.href", self.javascript)

    def test_legacy_links_are_privacy_safe_and_fail_gracefully(self):
        self.assertIn('crypto.subtle.digest("SHA-256"', self.javascript)
        self.assertIn("LEGACY_SUCCESSOR_HASHES", self.javascript)
        hashes = re.findall(
            r'"([a-f0-9]{64})": Object\.freeze\(\{ view: "(?:theme|tension|narrative|scenario|family)"',
            self.javascript,
        )
        self.assertEqual(68, len(hashes))
        self.assertEqual(68, len(set(hashes)))
        self.assertIn(
            "This link points to content that has been reorganized",
            self.javascript,
        )
        self.assertNotRegex(self.javascript, r"\bTD-\d{3}\b")
        self.assertNotRegex(self.javascript, r"\b[A-Z]{2,6}-M\d{2}\b")

    def test_search_indexes_only_canonical_public_fields(self):
        for field in (
            "definition",
            "poleALabel",
            "poleBLabel",
            "coreClaim",
            "responseOptions",
            "summary",
            "keyTopics",
            "whyItMatters",
        ):
            self.assertIn(f'"{field}"', self.javascript)
        self.assertIn("SEARCH_ENTITY_TYPES", self.javascript)
        self.assertIn("Public map records", self.javascript)
        search_fields = self.javascript.partition("function searchFieldsFor")[2].partition("function familyIdsForRecord")[0]
        self.assertNotIn("categoryFinding", search_fields)
        deep_link_types = self.javascript.partition("const DEEP_LINK_ENTITY_TYPES")[2].partition(");")[0]
        self.assertNotIn("categoryFinding", deep_link_types)
        self.assertNotIn("historicalThemeIds", self.javascript.partition(
            "const FORBIDDEN_PUBLIC_RECORD_KEYS"
        )[0])

    def test_methodology_covers_corpus_process_and_pipeline_boundaries(self):
        for token in (
            "one practitioner podcast corpus",
            "Duplicate-source analytical weight was removed",
            "human-guided, AI-assisted synthesis",
            "Transcript → public episode summary",
            "Structured qualitative analysis → analytical map relationships",
            "Canonical architecture",
            "Private provenance remains preserved and reproducible",
            "Episode discovery",
            "normalized IDF-weighted Jaccard",
        ):
            self.assertIn(token, self.javascript)
        self.assertNotIn("findings and open questions", self.javascript.lower())
        self.assertNotIn("64 findings", self.javascript.lower())

    def test_recurring_patterns_use_a_prose_first_renderer(self):
        renderer = self.javascript.partition("function recurringPatternList")[2].partition("function definitionRows")[0]
        self.assertIn('["description"]', renderer)
        self.assertIn('element("p", null, description)', renderer)
        self.assertNotIn('element("dt"', renderer)
        self.assertIn(
            'detailSection("Recurring patterns", recurringPatternList(cluster.recurringThemes))',
            self.javascript,
        )

    def test_category_hierarchy_does_not_restore_expansion_state(self):
        hierarchy = self.javascript.partition("async function renderFamilies")[2].partition("async function renderCategory")[0]
        self.assertNotIn("localStorage", hierarchy)
        self.assertNotIn("cognitive-security-hierarchy-expanded", hierarchy)
        self.assertIn('route.display === "subcategories"', hierarchy)
        self.assertIn('route.display === "topics"', hierarchy)

    def test_findings_remain_internal_but_have_no_public_renderer(self):
        self.assertIn('"category_findings.json"', self.javascript)
        self.assertIn('categoryFinding: 64', self.javascript)
        self.assertIn('if (route.view === "category-finding")', self.javascript)
        self.assertIn('getEntity("categoryFinding", route.id)', self.javascript)
        self.assertNotIn('"category-finding": renderCategoryFinding', self.javascript)
        self.assertNotIn("function renderCategoryFinding", self.javascript)
        self.assertIn('if (entry.otherType === "categoryFinding") return false;', self.javascript)

    def test_episode_cleanup_keeps_methodology_precise_but_secondary(self):
        self.assertNotIn("episode-card-link__type", self.javascript)
        self.assertEqual(1, self.javascript.count("Listen & show notes"))
        self.assertIn("Main topics in this episode", self.javascript)
        self.assertIn("Source: ", self.javascript)
        self.assertIn("Information Professionals Association", self.javascript)
        for removed_copy in (
            "documented repeated-coding",
            "Recommendations use repeated, eligible topics",
            "meets the documented main-topic threshold",
        ):
            self.assertNotIn(removed_copy, self.javascript)
        for retained_method in (
            "at least two primary coded items",
            "at least a 0.05 share",
            "normalized IDF-weighted Jaccard",
            "at least two shared topics",
            "a 0.15 minimum",
        ):
            self.assertIn(retained_method, self.javascript)

    def test_accessibility_and_mobile_contract_is_explicit(self):
        for token in (
            'class="skip-link"',
            'role="search"',
            'aria-live="polite"',
            'aria-labelledby="view-title"',
            'lang="en"',
        ):
            self.assertIn(token, self.html)
        self.assertIn(":focus-visible", self.css)
        self.assertIn("@media (prefers-reduced-motion: reduce)", self.css)
        self.assertIn("@media (forced-colors: active)", self.css)
        self.assertRegex(self.css, r"@media \(max-width: 31\.25rem\)")
        self.assertRegex(self.css, r"@media \(max-width: 48rem\)")
        self.assertIn("overflow-x: auto", self.css)
        self.assertIn('role", "region"', self.javascript)
        self.assertIn("aria-label", self.javascript)


class PublicCanonicalPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payloads = {name: load_json(name) for name in PUBLIC_FILES}
        cls.manifest = cls.payloads["manifest.json"]
        cls.ids = {
            kind: {row[id_field] for row in cls.payloads[filename]}
            for kind, (filename, id_field) in COLLECTIONS.items()
        }

    def test_exact_inventory_counts_and_performance_partition(self):
        self.assertEqual("canonical-resynthesis", self.manifest["contentVersion"])
        self.assertEqual("deduplicated-canonical-resynthesis", self.manifest["methodVersion"])
        self.assertEqual(list(PUBLIC_FILES), self.manifest["publicFiles"])
        self.assertEqual(["relationships.json", "provenance.json"], self.manifest["lazyFiles"])
        self.assertEqual(len(PUBLIC_FILES), self.manifest["fileCount"])
        self.assertEqual(set(PUBLIC_FILES), {path.name for path in PUBLIC_DIR.glob("*.json")})
        for filename in RETIRED_FILES:
            self.assertFalse((PUBLIC_DIR / filename).exists(), filename)
        for key, expected in EXPECTED_COUNTS.items():
            self.assertEqual(expected, self.manifest["counts"][key], key)
        byte_sizes = {row["name"]: row["bytes"] for row in self.manifest["files"]}
        self.assertLess(sum(byte_sizes.values()), 6_000_000)
        eager_bytes = sum(
            size
            for filename, size in byte_sizes.items()
            if filename not in self.manifest["lazyFiles"]
        )
        self.assertLess(eager_bytes, 3_000_000)

    def test_exact_canonical_collections_and_flat_themes(self):
        self.assertEqual(7, len(self.ids["category"]))
        self.assertEqual(50, len(self.ids["family"]))
        self.assertEqual(127, len(self.ids["cluster"]))
        self.assertEqual(11, len(self.ids["theme"]))
        self.assertEqual(20, len(self.ids["tension"]))
        self.assertEqual(5, len(self.ids["narrative"]))
        self.assertEqual(64, len(self.ids["finding"]))
        self.assertEqual(6, len(self.ids["scenario"]))
        self.assertEqual(242, len(self.ids["episode"]))
        self.assertEqual(
            EXPECTED_THEME_NAMES,
            {row["themeId"]: row["name"] for row in self.payloads["themes.json"]},
        )
        for theme in self.payloads["themes.json"]:
            self.assertNotIn("parentThemeId", theme)
            self.assertNotIn("subthemeIds", theme)
            self.assertNotIn("level", theme)

    def test_family_hierarchy_partitions_all_clusters_without_orphans(self):
        clusters = {row["clusterId"]: row for row in self.payloads["clusters.json"]}
        categories = self.ids["category"]
        membership = []
        for family in self.payloads["families.json"]:
            self.assertIn(family["categoryId"], categories)
            self.assertTrue(family["memberClusterIds"], family["familyId"])
            for cluster_id in family["memberClusterIds"]:
                self.assertIn(cluster_id, clusters)
                self.assertEqual(family["categoryId"], clusters[cluster_id]["categoryId"])
                membership.append(cluster_id)
        self.assertEqual(127, len(membership))
        self.assertEqual(127, len(set(membership)))
        self.assertEqual(set(clusters), set(membership))
        self.assertEqual(
            set(clusters),
            {row["clusterId"] for row in self.payloads["cluster_summaries.json"]},
        )

    def test_findings_narratives_and_scenarios_retain_required_structure(self):
        self.assertEqual(
            Counter({
                "family-finding": 50,
                "integrative-category-finding": 7,
                "open-question": 7,
            }),
            Counter(row["findingType"] for row in self.payloads["category_findings.json"]),
        )
        for narrative in self.payloads["narratives.json"]:
            self.assertGreater(len(narrative["integratesThemeIds"]), 1)
            self.assertTrue(narrative["integratesTensionIds"])
            self.assertTrue(narrative["supportingFamilyIds"])
        for scenario in self.payloads["scenarios.json"]:
            self.assertTrue(scenario["uncertaintyStatement"])
            self.assertTrue(scenario["branchPoints"])
            self.assertTrue(scenario["counterSignposts"])
            self.assertTrue(scenario["mitigatingConditions"])
            self.assertTrue(scenario["researchQuestions"])
            for relation in scenario["relationshipsToOtherScenarios"]:
                self.assertFalse(relation["causalClaim"])
        sc04 = next(
            row for row in self.payloads["scenarios.json"] if row["scenarioId"] == "SC-04"
        )
        for term in (
            "legal",
            "privacy",
            "civil-liberties",
            "ethics",
            "consent",
            "affected-community",
            "not validated recommendations",
        ):
            self.assertIn(term, sc04["publicNotice"].lower())

    def test_support_is_multidimensional_with_broader_reach_subordinate(self):
        support_files = (
            "cluster_summaries.json",
            "families.json",
            "themes.json",
            "tensions.json",
            "narratives.json",
            "category_findings.json",
            "scenarios.json",
        )
        for filename in support_files:
            for record in self.payloads[filename]:
                support = record["support"]
                self.assertEqual(
                    {"primarySupport", "broaderTraceableReach", "interpretation", "limitations"},
                    set(support),
                )
                self.assertEqual(SUPPORT_INTERPRETATION, support["interpretation"])
                primary = support["primarySupport"]
                broader = support["broaderTraceableReach"]
                for key in (
                    "itemCount",
                    "share",
                    "primaryContentUnitCount",
                    "primaryClusterCount",
                    "primaryFamilyCount",
                    "categoryBreadth",
                    "concentration",
                ):
                    self.assertIn(key, primary)
                self.assertLessEqual(primary["itemCount"], broader["itemCount"])
                self.assertLessEqual(
                    primary["primaryContentUnitCount"], broader["contentUnitCount"]
                )
        all_keys = {
            key.lower()
            for payload in self.payloads.values()
            for path, _ in walk(payload)
            for key in path[-1:]
        }
        self.assertFalse(
            any(
                "score" in key
                for key in all_keys
                if key not in {"compositescoreprohibited", "compositescoreabsent"}
            )
        )

    def test_relationship_endpoints_roles_and_noncausal_semantics_resolve(self):
        semantics = {
            row["semanticRole"]: row
            for row in self.payloads["relationship_semantics.json"]
        }
        self.assertTrue(REQUIRED_ROLES.issubset(semantics))
        relationships = self.payloads["relationships.json"]
        self.assertEqual(
            len(relationships),
            len({row["relationshipId"] for row in relationships}),
        )
        for relationship in relationships:
            self.assertIn(relationship["sourceType"], self.ids)
            self.assertIn(
                relationship["sourceId"], self.ids[relationship["sourceType"]]
            )
            self.assertIn(relationship["targetType"], self.ids)
            self.assertIn(
                relationship["targetId"], self.ids[relationship["targetType"]]
            )
            self.assertIn(relationship["semanticRole"], semantics)
            self.assertFalse(relationship["causalClaim"])
            self.assertNotEqual(
                (relationship["sourceType"], relationship["sourceId"]),
                (relationship["targetType"], relationship["targetId"]),
            )
        self.assertEqual(
            50,
            sum(
                row["sourceType"] == "family"
                and row["targetType"] == "category"
                for row in relationships
            ),
        )

    def test_public_provenance_resolves_and_episode_83_has_one_weight(self):
        provenance = self.payloads["provenance.json"]
        self.assertEqual(
            {"semanticRole": "direct-coded-support", "causalClaim": False},
            provenance["clusterRelationship"],
        )
        for cluster_id, links in provenance["clusterToReleases"].items():
            self.assertIn(cluster_id, self.ids["cluster"])
            for link in links:
                self.assertIn(link["episodeId"], self.ids["episode"])
                self.assertNotIn("relationship", link)
        tension_roles = set()
        dual_pole_rows = []
        for tension_id, links in provenance["tensionToReleases"].items():
            self.assertIn(tension_id, self.ids["tension"])
            for link in links:
                self.assertIn(link["episodeId"], self.ids["episode"])
                relationships = link["relationships"]
                self.assertIn(len(relationships), (1, 2))
                roles = [relationship["semanticRole"] for relationship in relationships]
                self.assertEqual(len(roles), len(set(roles)))
                self.assertNotIn("direct-coded-support", roles)
                self.assertTrue(
                    set(roles).issubset(
                        {"tension-evidence-pole-a", "tension-evidence-pole-b"}
                    )
                )
                for relationship in relationships:
                    self.assertGreater(relationship["analyticalWeight"], 0)
                    self.assertFalse(relationship["causalClaim"])
                tension_roles.update(roles)
                if len(roles) == 2:
                    dual_pole_rows.append((tension_id, link["episodeId"], set(roles)))
        self.assertEqual(
            {"tension-evidence-pole-a", "tension-evidence-pole-b"},
            tension_roles,
        )
        self.assertTrue(dual_pole_rows, "Expected at least one dual-pole episode link")
        self.assertTrue(
            all(
                roles == {"tension-evidence-pole-a", "tension-evidence-pole-b"}
                for _, _, roles in dual_pole_rows
            )
        )
        original = "EPI-72E94D7AF43A4BD3"
        inherited = "EPI-9960393907F71603"
        episodes = {
            row["episodeId"]: row for row in self.payloads["episodes.json"]
        }
        self.assertEqual("direct-content-representation", episodes[original]["contentRole"])
        self.assertEqual("shared-content-inheritance", episodes[inherited]["contentRole"])
        self.assertEqual(
            241,
            sum(
                row["contentRole"] == "direct-content-representation"
                for row in episodes.values()
            ),
        )
        self.assertEqual(
            [{
                "relationshipId": provenance["sharedContentRelationships"][0]["relationshipId"],
                "sourceEpisodeId": inherited,
                "targetEpisodeId": original,
                "semanticRole": "shared-content-inheritance",
                "contributesAnalyticalWeight": False,
            }],
            provenance["sharedContentRelationships"],
        )
        direct_episode_ids = {
            link["episodeId"]
            for mapping in (
                provenance["clusterToReleases"],
                provenance["tensionToReleases"],
            )
            for links in mapping.values()
            for link in links
        }
        self.assertIn(original, direct_episode_ids)
        self.assertNotIn(inherited, direct_episode_ids)

    def test_heatmap_is_complete_normalized_and_reconstructable(self):
        cells = self.payloads["heatmap.json"]["cells"]
        self.assertEqual(77, len(cells))
        self.assertEqual(
            {
                (category_id, theme_id)
                for category_id in self.ids["category"]
                for theme_id in self.ids["theme"]
            },
            {(cell["categoryId"], cell["themeId"]) for cell in cells},
        )
        for cell in cells:
            shares = (
                cell["primaryFamilyCount"] / cell["categoryFamilyCount"],
                cell["primaryClusterCount"] / cell["categoryClusterCount"],
                cell["primaryContentUnitCount"] / cell["categoryContentUnitCount"],
            )
            self.assertEqual(round(shares[0], 6), cell["primaryFamilyShare"])
            self.assertEqual(round(shares[1], 6), cell["primaryClusterShare"])
            self.assertEqual(round(shares[2], 6), cell["primaryContentUnitShare"])
            self.assertTrue(
                math.isclose(
                    round(sum(shares) / 3, 6),
                    cell["normalizedPrimarySupportBreadth"],
                    abs_tol=1e-9,
                )
            )

    def test_public_projection_contains_no_private_payload_or_readable_legacy_ids(self):
        prohibited_keys = {
            "itemid",
            "itemids",
            "transcripttext",
            "transcriptpath",
            "localpath",
            "workbookname",
            "workbookhash",
            "sourcefilename",
            "adjudicationid",
            "adjudicationrationale",
            "reviewnotes",
            "reviewflags",
            "evidenceexcerpt",
            "migrationtable",
        }
        secret_patterns = (
            r"(?i)[a-z]:\\users\\",
            r"(?i)/users/",
            r"(?i)\.xlsx\b",
            r"\bTD-\d{3}\b",
            r"\b[A-Z]{2,6}-M\d{2}\b",
            r"\bgh[pousr]_[A-Za-z0-9]{20,}\b",
            r"\bAKIA[0-9A-Z]{16}\b",
            r"\bsk-[A-Za-z0-9_-]{20,}\b",
            r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
        )
        for filename, payload in self.payloads.items():
            serialized = json.dumps(payload, ensure_ascii=False)
            for pattern in secret_patterns:
                self.assertNotRegex(serialized, pattern, filename)
            for path, _ in walk(payload):
                for key in path[-1:]:
                    normalized = re.sub(r"[^a-z0-9]", "", key.lower())
                    self.assertNotIn(normalized, prohibited_keys, f"{filename}: {path}")

    def test_episode_summary_and_deep_link_contract_is_complete(self):
        summaries = self.payloads["episode_summaries.json"]
        self.assertEqual(self.ids["episode"], {row["episodeId"] for row in summaries})
        for summary in summaries:
            self.assertTrue(summary["summary"].strip())
            self.assertTrue(summary["whyItMatters"].strip())
            self.assertTrue(summary["keyTopics"])
        for kind, route_type in ROUTE_TYPES.items():
            ids = self.ids[kind]
            for entity_id in ids:
                query = urlencode({"view": route_type, "id": entity_id})
                parsed = parse_qs(query)
                self.assertEqual(route_type, parsed["view"][0])
                self.assertEqual(entity_id, unquote(quote(parsed["id"][0], safe="")))

    def test_redundancy_and_public_qa_are_closed(self):
        qa = self.payloads["qa_report.json"]
        self.assertEqual("pass", qa["status"])
        self.assertTrue(all(qa["checks"].values()))
        self.assertEqual(0, qa["redundancyResolution"]["unresolvedPairCount"])
        self.assertEqual(
            qa["redundancyResolution"]["flaggedPairCount"],
            qa["redundancyResolution"]["resolvedDistinctPairCount"],
        )


if __name__ == "__main__":
    unittest.main()
