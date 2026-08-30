"""Static and public-data contract tests for the Cognitive Security Explorer.

The Explorer is intentionally dependency-free, so these tests use only the
Python standard library.  They validate the publication boundary as well as
the relationships and identifiers that the browser application navigates.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import unittest
from urllib.parse import parse_qs, quote, unquote, urlencode


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPLORER_DIR = REPO_ROOT / "cognitive-security"
PUBLIC_DIR = REPO_ROOT / "data" / "cognitive-security"

REQUIRED_EXPLORER_FILES = ("index.html", "app.js", "styles.css")
REQUIRED_CONTENT_FILES = {
    "corpus_reconciliation.json",
    "categories.json",
    "clusters.json",
    "cluster_summaries.json",
    "meta_clusters.json",
    "themes.json",
    "tensions.json",
    "meta_narratives.json",
    "category_findings.json",
    "scenarios.json",
    "episodes.json",
    "relationships.json",
    "coverage.json",
}
EXPECTED_PUBLIC_FILES = {
    "manifest.json",
    "corpus_reconciliation.json",
    "categories.json",
    "clusters.json",
    "cluster_summaries.json",
    "meta_clusters.json",
    "themes.json",
    "tensions.json",
    "meta_narratives.json",
    "category_findings.json",
    "scenarios.json",
    "episodes.json",
    "relationships.json",
    "coverage.json",
    "review_summary.json",
    "qa_report.json",
}

EXPECTED_COUNTS = {
    "categories": 10,
    "clusters": 127,
    "cluster_summaries": 127,
    "meta_clusters": 36,
    "themes": 11,
    "tensions": 30,
    "meta_narratives": 7,
    "category_findings": 42,
    "scenarios": 6,
    "episodes": 242,
    "relationships": 975,
}
EXPECTED_RELATIONSHIP_COUNTS = {
    "cluster-belongs-to-category": 127,
    "cluster-belongs-to-meta-cluster": 124,
    "meta-cluster-belongs-to-category": 36,
    "theme-connects-meta-cluster": 89,
    "theme-supported-by-cluster": 299,
    "tension-maps-to-cross-cutting-theme": 120,
    "tension-maps-to-meta-cluster": 180,
}
RELATIONSHIP_ENDPOINT_TYPES = {
    "cluster-belongs-to-category": ("cluster", "category"),
    "cluster-belongs-to-meta-cluster": ("cluster", "metaCluster"),
    "meta-cluster-belongs-to-category": ("metaCluster", "category"),
    "theme-connects-meta-cluster": ("theme", "metaCluster"),
    "theme-supported-by-cluster": ("theme", "cluster"),
    "tension-maps-to-cross-cutting-theme": ("tension", "theme"),
    "tension-maps-to-meta-cluster": ("tension", "metaCluster"),
}
UNMAPPED_CLUSTER_IDS = {"CRB-10", "FTP-13", "KCFT-20"}
KNOWN_EMPTY_META_CLUSTER_ID = "CRB-M05"

# Exact positive allowlists for entity records.  Aggregate release metadata has
# separate shapes and is checked for prohibited detail below.
PUBLIC_RECORD_FIELDS = {
    "categories.json": {
        "categoryId", "name", "scope", "summary", "soWhat",
    },
    "clusters.json": {
        "clusterId", "categoryId", "name", "definition",
        "inclusionCriteria", "exclusionCriteria", "nearNeighborDistinctions",
        "anchorExamples",
    },
    "cluster_summaries.json": {
        "clusterId", "categoryId", "clusterName", "primaryCount",
        "secondaryCount", "weightedCount", "summary", "recurringThemes",
        "strategicSignificance", "operationalImplications",
        "primarySecondaryDistinction",
    },
    "meta_clusters.json": {
        "metaClusterId", "categoryId", "name", "definition",
        "includedClusterIds", "nearNeighborDistinctions", "salience",
        "categorySynthesis",
    },
    "themes.json": {
        "themeId", "name", "definition", "categoryIds",
        "linkedMetaClusterIds", "linkedClusterIds", "crossCategoryLogic",
        "strategicSignificance", "operationalImplications",
        "boundaryConditions", "relatedTensionIds", "evidenceStrength",
    },
    "tensions.json": {
        "tensionId", "name", "description", "poleALabel", "poleBLabel",
        "poleAAssumption", "poleBAssumption", "tensionLevel", "categoryIds",
        "clusterIds", "evidenceStrength", "confidence",
    },
    "meta_narratives.json": {
        "narrativeId", "name", "shortVersion", "coreClaim",
        "supportingThemeIds", "supportingTensionIds",
        "supportingMetaClusterIds", "categoryIds", "strategicSignificance",
        "operationalImplications", "caveats", "confidence",
    },
    "category_findings.json": {
        "findingId", "categoryId", "name", "coreFinding",
        "supportingMetaClusterIds", "supportingClusterIds",
        "strategicSignificance", "operationalImplications",
        "unresolvedQuestions", "caveats", "confidence",
    },
    "scenarios.json": {
        "scenarioId", "name", "timeframe", "scenarioType", "coreScenario",
        "drivingForces", "categoryIds", "themeIds", "tensionIds",
        "strategicImplications", "operationalImplications",
        "researchQuestions", "uncertaintyLevel", "assumptions",
        "alternativeOutcomes", "pathway", "indicators", "actions",
        "forecastDisclaimer",
    },
    "episodes.json": {
        "episodeId", "podcast", "episodeTitle", "sourceIdentityCount",
        "originalItemCount", "reconciledSensitivityItemCount",
    },
    "relationships.json": {
        "relationshipId", "relationshipType", "sourceId", "sourceType",
        "targetId", "targetType", "interpretation",
    },
}

DETAIL_ROUTES = {
    "category": ("categories.json", "categoryId"),
    "meta-cluster": ("meta_clusters.json", "metaClusterId"),
    "cluster": ("clusters.json", "clusterId"),
    "theme": ("themes.json", "themeId"),
    "tension": ("tensions.json", "tensionId"),
    "meta-narrative": ("meta_narratives.json", "narrativeId"),
    "category-finding": ("category_findings.json", "findingId"),
    "scenario": ("scenarios.json", "scenarioId"),
}
EXPECTED_DEEP_LINK_ENTITY_TYPES = [
    "category", "metaCluster", "cluster", "theme", "tension",
    "metaNarrative", "categoryFinding", "scenario",
]


def load_json(filename: str):
    return json.loads((PUBLIC_DIR / filename).read_text(encoding="utf-8"))


def recursively_walk(value, path: tuple[str, ...] = ()):
    """Yield ``(path, value)`` for every node in a JSON-compatible value."""
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from recursively_walk(child, path + (str(key),))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from recursively_walk(child, path + (str(index),))


class ExplorerStaticContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load_json("manifest.json")
        cls.html = (EXPLORER_DIR / "index.html").read_text(encoding="utf-8")
        cls.javascript = (EXPLORER_DIR / "app.js").read_text(encoding="utf-8")
        cls.css = (EXPLORER_DIR / "styles.css").read_text(encoding="utf-8")

    def test_required_explorer_files_and_shared_assets_exist(self):
        for filename in REQUIRED_EXPLORER_FILES:
            with self.subTest(filename=filename):
                path = EXPLORER_DIR / filename
                self.assertTrue(path.is_file(), f"Missing Explorer file: {path}")

        self.assertRegex(
            self.html,
            r"href=[\"']\.\./shared/psywerx\.css[\"']",
            "Explorer must reuse the shared PSYWERX stylesheet.",
        )
        self.assertRegex(self.html, r"href=[\"']\./styles\.css[\"']")
        self.assertRegex(self.html, r"src=[\"']\./app\.js[\"']")

        asset_references = re.findall(
            r"(?:src|href)=[\"']([^\"']+\.(?:css|js|png|svg|webp|ico))[\"']",
            self.html,
            flags=re.IGNORECASE,
        )
        self.assertTrue(asset_references, "Expected local Explorer asset references.")
        for reference in asset_references:
            with self.subTest(asset=reference):
                self.assertFalse(re.match(r"(?:https?:)?//", reference))
                target = (EXPLORER_DIR / reference.split("?", 1)[0]).resolve()
                self.assertTrue(target.is_file(), f"Missing referenced asset: {reference}")

    def test_explorer_has_no_private_or_third_party_references(self):
        combined = "\n".join((self.html, self.javascript, self.css))
        lowered = combined.casefold().replace("\\", "/")
        for prohibited_path in (
            "analysis/",
            "source-data/",
            "ipa-podcast/",
            "master_extractions.xlsx",
            "items.json",
            "item_tags.json",
            "item_cluster_assignments.json",
            "evidence_links.json",
            "review_flags.json",
        ):
            with self.subTest(path=prohibited_path):
                self.assertNotIn(prohibited_path, lowered)

        external_urls = re.findall(r"(?:https?:)?//[^\s\"')]+", combined)
        self.assertEqual([], external_urls, "Explorer must not use third-party URLs.")

    def test_explorer_json_references_are_public_allowlisted_files(self):
        manifest_files = set(self.manifest["publicFiles"])
        self.assertEqual(EXPECTED_PUBLIC_FILES, manifest_files)

        references = {
            Path(match).name
            for match in re.findall(
                r"[\"']([^\"']+\.json(?:\?[^\"']*)?)[\"']",
                self.javascript,
                flags=re.IGNORECASE,
            )
        }
        self.assertTrue(
            REQUIRED_CONTENT_FILES <= references,
            "Explorer must load every governed content dataset needed by its views; "
            f"missing {sorted(REQUIRED_CONTENT_FILES - references)}",
        )
        self.assertFalse(
            references - manifest_files,
            f"Explorer references non-public JSON: {sorted(references - manifest_files)}",
        )

    def test_deep_link_contract_and_history_support_are_explicit(self):
        constant_match = re.search(
            r"const\s+DEEP_LINK_ENTITY_TYPES\s*=\s*Object\.freeze\(\s*(\[[^;]+?\])\s*\)\s*;",
            self.javascript,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(
            constant_match,
            "app.js must expose the governed DEEP_LINK_ENTITY_TYPES constant.",
        )
        self.assertEqual(
            EXPECTED_DEEP_LINK_ENTITY_TYPES,
            json.loads(constant_match.group(1)),
        )

        for token in (
            "URLSearchParams",
            "history.pushState",
            "history.replaceState",
            "popstate",
        ):
            with self.subTest(token=token):
                self.assertIn(token, self.javascript)

        for parameter in ("view", "id", "q", "type", "category", "meta", "cluster"):
            with self.subTest(query_parameter=parameter):
                self.assertRegex(
                    self.javascript,
                    rf"[\"']{re.escape(parameter)}[\"']",
                    f"Missing query-state token {parameter!r}.",
                )
        for route in DETAIL_ROUTES:
            with self.subTest(route=route):
                self.assertRegex(self.javascript, rf"[\"']{re.escape(route)}[\"']")

    def test_governed_unresolved_states_and_not_found_routes_are_data_driven(self):
        for token in (
            'data["qa_report.json"]',
            "unresolvedMappings",
            "metaClustersWithoutMappingRows",
            "renderMissingEntity",
            "No record has been inferred or substituted.",
        ):
            with self.subTest(token=token):
                self.assertIn(token, self.javascript)
        self.assertNotIn("UNMAPPED_CLUSTER_IDS", self.javascript)
        self.assertNotIn("EMPTY_META_CLUSTER_ID", self.javascript)

    def test_search_has_an_explicit_submit_and_filter_changes_add_history(self):
        self.assertRegex(
            self.html,
            r'<button[^>]*class="primary-button search-form__submit"[^>]*type="submit"',
        )
        change_handler = re.search(
            r'searchForm\.addEventListener\("change".*?\n\s*}\);',
            self.javascript,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(change_handler)
        self.assertNotIn("replace: true", change_handler.group(0))
        self.assertIn("firstNewResultIndex", self.javascript)

    def test_browser_initialization_enforces_governed_release_metadata(self):
        for token in (
            "qa.passed !== true",
            "qa.deterministicBuild.status",
            "qa.publicExportChecks.status",
            "Governed count mismatch",
            "Missing public semantic relationship",
            "Coverage keys do not match",
        ):
            with self.subTest(token=token):
                self.assertIn(token, self.javascript)

    def test_corpus_language_distinguishes_analysis_from_reconciliation(self):
        public_copy = "\n".join((self.html, self.javascript)).casefold()
        for term in (
            "original analytic release",
            "reconciled sensitivity dataset",
            "source identities",
            "canonical episodes",
        ):
            with self.subTest(term=term):
                self.assertIn(term, public_copy)
        for misleading in (
            "269 episodes",
            "269 podcast episodes",
            "269 canonical episodes",
        ):
            with self.subTest(misleading=misleading):
                self.assertNotIn(misleading, public_copy)
        self.assertIn("originalItemCount", self.javascript)
        self.assertIn("reconciledSensitivityItemCount", self.javascript)
        self.assertNotRegex(self.javascript, r"\b(?:episode|record)\.itemCount\b")
        self.assertNotIn("schema v1.0", public_copy)
        self.assertIn(
            "../docs/cognitive-security/COGNITIVE_SECURITY_SCHEMA_V1_1.md",
            self.javascript,
        )


class PublicDataContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payloads = {
            filename: load_json(filename) for filename in EXPECTED_PUBLIC_FILES
        }
        cls.categories = cls.payloads["categories.json"]
        cls.clusters = cls.payloads["clusters.json"]
        cls.cluster_summaries = cls.payloads["cluster_summaries.json"]
        cls.meta_clusters = cls.payloads["meta_clusters.json"]
        cls.themes = cls.payloads["themes.json"]
        cls.tensions = cls.payloads["tensions.json"]
        cls.narratives = cls.payloads["meta_narratives.json"]
        cls.findings = cls.payloads["category_findings.json"]
        cls.scenarios = cls.payloads["scenarios.json"]
        cls.relationships = cls.payloads["relationships.json"]

        cls.ids_by_type = {
            "category": {row["categoryId"] for row in cls.categories},
            "cluster": {row["clusterId"] for row in cls.clusters},
            "metaCluster": {row["metaClusterId"] for row in cls.meta_clusters},
            "theme": {row["themeId"] for row in cls.themes},
            "tension": {row["tensionId"] for row in cls.tensions},
            "metaNarrative": {row["narrativeId"] for row in cls.narratives},
            "categoryFinding": {row["findingId"] for row in cls.findings},
            "scenario": {row["scenarioId"] for row in cls.scenarios},
            "episode": {
                row["episodeId"] for row in cls.payloads["episodes.json"]
            },
        }

    def assert_ids_resolve(self, records, field, valid_ids, record_id_field):
        for record in records:
            values = record.get(field)
            self.assertIsInstance(
                values,
                list,
                f"{record_id_field}={record.get(record_id_field)}: {field} must be a list",
            )
            missing = set(values) - valid_ids
            self.assertFalse(
                missing,
                f"{record_id_field}={record.get(record_id_field)}: "
                f"{field} has missing IDs {sorted(missing)}",
            )

    def test_governed_entity_counts_and_corpus_totals(self):
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
            "relationships": "relationships.json",
        }
        for entity, expected in EXPECTED_COUNTS.items():
            with self.subTest(entity=entity):
                self.assertEqual(expected, len(self.payloads[filenames[entity]]))

        scopes = Counter(row["scope"] for row in self.categories)
        self.assertEqual({"focal": 7, "contextual": 3}, dict(scopes))
        governed_summaries = [
            row for row in self.categories
            if row.get("summary") not in (None, "") and row.get("soWhat") not in (None, "")
        ]
        self.assertEqual(7, len(governed_summaries))

        coverage = self.payloads["coverage.json"]
        self.assertEqual(14_397, coverage["totals"]["items"])
        self.assertEqual(242, coverage["totals"]["episodes"])
        self.assertEqual(
            {
                "sourceIdentities": 269,
                "items": 14_397,
                "focalItems": 10_940,
                "contextualItems": 3_457,
            },
            coverage["originalAnalyticRelease"],
        )
        self.assertEqual(
            {
                "canonicalEpisodes": 242,
                "retainedSourceIdentities": 242,
                "items": 12_978,
                "focalItems": 9_855,
                "contextualItems": 3_123,
            },
            coverage["reconciledSensitivityDataset"],
        )
        focal_ids = {
            row["categoryId"] for row in self.categories if row["scope"] == "focal"
        }
        focal_item_count = sum(
            count for category_id, count in coverage["itemsByCategory"].items()
            if category_id in focal_ids
        )
        self.assertEqual(10_940, focal_item_count)

    def test_category_meta_cluster_cluster_hierarchy_resolves(self):
        categories = self.ids_by_type["category"]
        clusters = self.ids_by_type["cluster"]
        cluster_category = {
            row["clusterId"]: row["categoryId"] for row in self.clusters
        }
        meta_by_id = {row["metaClusterId"]: row for row in self.meta_clusters}

        for cluster in self.clusters:
            self.assertIn(cluster["categoryId"], categories)
        for meta_cluster in self.meta_clusters:
            self.assertIn(meta_cluster["categoryId"], categories)
            included = meta_cluster["includedClusterIds"]
            self.assertEqual(len(included), len(set(included)))
            self.assertFalse(set(included) - clusters)
            for cluster_id in included:
                self.assertEqual(
                    meta_cluster["categoryId"],
                    cluster_category[cluster_id],
                    f"Cross-category hierarchy mapping for {cluster_id}",
                )

        parent_relationships = [
            row for row in self.relationships
            if row["relationshipType"] == "cluster-belongs-to-meta-cluster"
        ]
        parents_by_cluster = defaultdict(list)
        for relationship in parent_relationships:
            parents_by_cluster[relationship["sourceId"]].append(
                relationship["targetId"]
            )
        self.assertEqual(
            UNMAPPED_CLUSTER_IDS,
            clusters - set(parents_by_cluster),
        )
        for cluster_id, parent_ids in parents_by_cluster.items():
            self.assertEqual(1, len(parent_ids), f"Multiple parents for {cluster_id}")
            parent = meta_by_id[parent_ids[0]]
            self.assertIn(cluster_id, parent["includedClusterIds"])

    def test_unmapped_clusters_and_crb_m05_are_preserved(self):
        cluster_ids = self.ids_by_type["cluster"]
        self.assertTrue(UNMAPPED_CLUSTER_IDS <= cluster_ids)

        meta = next(
            row for row in self.meta_clusters
            if row["metaClusterId"] == KNOWN_EMPTY_META_CLUSTER_ID
        )
        self.assertEqual([], meta["includedClusterIds"])
        mapped_targets = {
            row["targetId"] for row in self.relationships
            if row["relationshipType"] == "cluster-belongs-to-meta-cluster"
        }
        self.assertNotIn(KNOWN_EMPTY_META_CLUSTER_ID, mapped_targets)

        qa_report = self.payloads["qa_report.json"]
        issue_codes = {
            issue.get("code") for issue in qa_report.get("validationIssues", [])
        }
        self.assertIn("known_empty_meta_cluster", issue_codes)
        unresolved = qa_report.get("unresolvedMappings", [])
        self.assertTrue(
            any(row.get("metaClusterId") == KNOWN_EMPTY_META_CLUSTER_ID for row in unresolved)
        )
        unresolved_cluster_ids = {
            row.get("clusterId") for row in unresolved if row.get("clusterId")
        }
        self.assertEqual(UNMAPPED_CLUSTER_IDS, unresolved_cluster_ids)

    def test_cluster_summaries_resolve_and_match_cluster_categories(self):
        clusters = {row["clusterId"]: row for row in self.clusters}
        seen = set()
        for summary in self.cluster_summaries:
            cluster_id = summary["clusterId"]
            self.assertIn(cluster_id, clusters)
            self.assertNotIn(cluster_id, seen)
            seen.add(cluster_id)
            self.assertEqual(clusters[cluster_id]["categoryId"], summary["categoryId"])
        self.assertEqual(set(clusters), seen)

    def test_synthesis_embedded_foreign_keys_resolve(self):
        categories = self.ids_by_type["category"]
        clusters = self.ids_by_type["cluster"]
        meta_clusters = self.ids_by_type["metaCluster"]
        themes = self.ids_by_type["theme"]
        tensions = self.ids_by_type["tension"]

        for field, valid_ids in (
            ("categoryIds", categories),
            ("linkedMetaClusterIds", meta_clusters),
            ("linkedClusterIds", clusters),
            ("relatedTensionIds", tensions),
        ):
            self.assert_ids_resolve(self.themes, field, valid_ids, "themeId")

        self.assert_ids_resolve(self.tensions, "categoryIds", categories, "tensionId")
        self.assert_ids_resolve(self.tensions, "clusterIds", clusters, "tensionId")

        for field, valid_ids in (
            ("supportingThemeIds", themes),
            ("supportingTensionIds", tensions),
            ("supportingMetaClusterIds", meta_clusters),
            ("categoryIds", categories),
        ):
            self.assert_ids_resolve(self.narratives, field, valid_ids, "narrativeId")

        for finding in self.findings:
            self.assertIn(finding["categoryId"], categories)
        self.assert_ids_resolve(
            self.findings, "supportingMetaClusterIds", meta_clusters, "findingId"
        )
        self.assert_ids_resolve(
            self.findings, "supportingClusterIds", clusters, "findingId"
        )

        for field, valid_ids in (
            ("categoryIds", categories),
            ("themeIds", themes),
            ("tensionIds", tensions),
        ):
            self.assert_ids_resolve(self.scenarios, field, valid_ids, "scenarioId")

    def test_all_975_semantic_relationships_and_endpoints_resolve(self):
        relationship_ids = [row["relationshipId"] for row in self.relationships]
        self.assertEqual(len(relationship_ids), len(set(relationship_ids)))
        self.assertEqual(
            EXPECTED_RELATIONSHIP_COUNTS,
            dict(Counter(row["relationshipType"] for row in self.relationships)),
        )

        for relationship in self.relationships:
            relationship_type = relationship["relationshipType"]
            with self.subTest(relationshipId=relationship["relationshipId"]):
                self.assertIn(relationship_type, RELATIONSHIP_ENDPOINT_TYPES)
                expected_source_type, expected_target_type = (
                    RELATIONSHIP_ENDPOINT_TYPES[relationship_type]
                )
                self.assertEqual(expected_source_type, relationship["sourceType"])
                self.assertEqual(expected_target_type, relationship["targetType"])
                self.assertEqual("semantic", relationship["interpretation"])
                self.assertIn(
                    relationship["sourceId"],
                    self.ids_by_type[expected_source_type],
                )
                self.assertIn(
                    relationship["targetId"],
                    self.ids_by_type[expected_target_type],
                )

        theme_meta = {
            (row["sourceId"], row["targetId"])
            for row in self.relationships
            if row["relationshipType"] == "theme-connects-meta-cluster"
        }
        embedded_theme_meta = {
            (row["themeId"], meta_id)
            for row in self.themes for meta_id in row["linkedMetaClusterIds"]
        }
        self.assertEqual(embedded_theme_meta, theme_meta)

        theme_cluster = {
            (row["sourceId"], row["targetId"])
            for row in self.relationships
            if row["relationshipType"] == "theme-supported-by-cluster"
        }
        embedded_theme_cluster = {
            (row["themeId"], cluster_id)
            for row in self.themes for cluster_id in row["linkedClusterIds"]
        }
        self.assertEqual(embedded_theme_cluster, theme_cluster)

    def test_public_entity_allowlists_and_no_item_or_quote_payloads(self):
        for filename, allowed_fields in PUBLIC_RECORD_FIELDS.items():
            for index, record in enumerate(self.payloads[filename]):
                with self.subTest(filename=filename, index=index):
                    self.assertEqual(allowed_fields, set(record))

        prohibited_public_files = {
            "items.json",
            "item_tags.json",
            "item_cluster_assignments.json",
            "evidence_links.json",
            "review_flags.json",
            "review_queue.json",
            "quotations.json",
            "evidence_quotes.json",
        }
        existing_files = {path.name for path in PUBLIC_DIR.glob("*.json")}
        self.assertFalse(prohibited_public_files & existing_files)

        prohibited_key_fragments = (
            "quote",
            "quotation",
            "excerpt",
            "transcript",
            "speaker",
            "assignmentrationale",
            "reviewernotes",
            "reviewqueue",
            "modelrationale",
            "rawtext",
            "fulltext",
        )
        violations = []
        for filename, payload in self.payloads.items():
            for path, _value in recursively_walk(payload):
                if not path:
                    continue
                # The QA report exposes aggregate source worksheet row counts.
                # Worksheet titles such as "Review Queue" and "Memorable
                # Quotes" describe what was withheld; their numeric counts are
                # not review-queue records, items, or quotation content.
                if filename == "qa_report.json" and path[0] == "sourceRowCounts":
                    if len(path) >= 3:
                        self.assertIsInstance(_value, int)
                    continue
                key = re.sub(r"[^a-z]", "", path[-1].casefold())
                if any(fragment in key for fragment in prohibited_key_fragments):
                    violations.append(f"{filename}:{'.'.join(path)}")
        self.assertEqual([], violations, "Private/detail keys escaped: " + repr(violations))

    def test_all_detail_route_ids_are_url_safe_and_round_trip(self):
        for route, (filename, id_field) in DETAIL_ROUTES.items():
            records = self.payloads[filename]
            ids = [record[id_field] for record in records]
            self.assertEqual(len(ids), len(set(ids)), f"Duplicate IDs for {route}")
            for entity_id in ids:
                with self.subTest(route=route, entity_id=entity_id):
                    self.assertIsInstance(entity_id, str)
                    self.assertTrue(entity_id.strip())
                    self.assertEqual(entity_id, unquote(quote(entity_id, safe="")))
                    query = urlencode({"view": route, "id": entity_id})
                    parsed = parse_qs(query, strict_parsing=True)
                    self.assertEqual([route], parsed["view"])
                    self.assertEqual([entity_id], parsed["id"])
                    self.assertRegex(entity_id, r"^[A-Za-z0-9][A-Za-z0-9._~-]*$")


if __name__ == "__main__":
    unittest.main()
