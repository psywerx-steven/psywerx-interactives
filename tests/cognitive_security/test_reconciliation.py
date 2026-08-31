"""Governance and regression tests for Cognitive Security corpus reconciliation.

The fixture tests exercise the pure reconciliation functions without access to
the private corpus.  Corpus-level tests run when the ignored normalized release
and source workbooks are present in the maintainer workspace.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import random
import unittest
from unittest.mock import patch

from scripts.cognitive_security.reconcile import (
    MAPPING_STATUSES,
    apply_episode_reconciliation,
    build_episode_reconciliation,
)
from scripts.cognitive_security.sensitivity import build_reconciliation_products
from scripts.cognitive_security.validate import validate_reconciliation_dataset


REPO_ROOT = Path(__file__).resolve().parents[2]
NORMALIZED_DIR = REPO_ROOT / "analysis" / "cognitive-security" / "normalized"
RECONCILIATION_DIR = (
    REPO_ROOT / "analysis" / "cognitive-security" / "corpus-reconciliation"
)
SOURCE_DIR = REPO_ROOT / "source-data" / "ipa-podcast"
PUBLIC_DIR = REPO_ROOT / "data" / "cognitive-security"

EXPECTED_SOURCE_HASHES = {
    "codebook.xlsx": "a578d408c6bbaa42b0cde5738418b86f73fa51bf75646e4462a452f12d09af1e",
    "cross_cutting_themes.xlsx": "cd9540c3b2b780088d64a9b463cea3773e946cad33d42641f69aafc190f2cc17",
    "drill_down.xlsx": "e85a038144e2ffc3ed65061490bb25e006c6205e3a88be07edd08cf706eff8df",
    "drill_up_cluster_summaries.xlsx": "6e806e87a1f50f7ca57367865ee0148abdbde24c15b3669b96352ca1e0c5a737",
    "drill_up_meta_clusters.xlsx": "a7b436c18f5d1a40ef664da87c5b5e9f92f145cfd76972a9947a538e9c7f0afa",
    "final_synthesis.xlsx": "9e1a39755fe5397f4395c1019203db80ebe0123e25fea70a4e88001eec8f4ff2",
    "master_extractions.xlsx": "974aa0b8b83371681b3a921d6f2bface2befa680db1f0b68954a6c48487f4d0f",
    "tensions_debates_rebuilt.xlsx": "60b3ce533852fda1e47afee687e7e9b5f5838c2691006e28c3477b25dea65394",
}


def _source(row: int) -> dict[str, object]:
    return {
        "artifactId": "ART-fixture",
        "sheet": "Master",
        "rowNumber": row,
    }


def _episode(
    identity_id: str,
    title: str,
    source_file: str,
    row: int,
) -> dict[str, object]:
    return {
        "episodeId": identity_id,
        "podcast": "Fixture podcast",
        "episodeTitle": title,
        "sourceFile": source_file,
        "source": _source(row),
    }


def _item(item_id: str, identity_id: str, scope: str = "focal") -> dict[str, object]:
    return {
        "itemId": item_id,
        "episodeId": identity_id,
        "categoryId": "CAT-1",
        "scope": scope,
        "item": f"Fixture item {item_id}",
        "source": _source(int(item_id.rsplit("-", 1)[-1])),
    }


def _load_private_dataset() -> dict[str, object]:
    payloads: dict[str, object] = {}
    for path in sorted(NORMALIZED_DIR.glob("*.json")):
        if path.stem in {"manifest", "qa_report"}:
            continue
        payloads[path.stem] = json.loads(path.read_text(encoding="utf-8"))
    return payloads


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class ReconciliationRuleTests(unittest.TestCase):
    def test_ambiguous_identity_is_never_collapsed(self) -> None:
        dataset = {
            "episodes": [
                _episode("EPI-CONFLICT", "#2 Alpha topic", "#3 Alpha topic.txt", 2)
            ],
            "items": [_item("ITEM-1", "EPI-CONFLICT")],
        }
        with patch(
            "scripts.cognitive_security.reconcile.GOVERNED_EDITED_RELEASE_ALIASES",
            (),
        ), patch(
            "scripts.cognitive_security.reconcile.GOVERNED_DISTINCT_PUBLICATION_REUSES",
            (),
        ):
            reconciliation = build_episode_reconciliation(dataset)

        self.assertEqual(1, len(reconciliation["mappings"]))
        mapping = reconciliation["mappings"][0]
        self.assertEqual("ambiguous", mapping["mappingStatus"])
        self.assertEqual("candidate", mapping["mappingRole"])
        self.assertEqual(
            ["conflicting-episode-number-evidence"], mapping["mappingBasis"]
        )
        self.assertFalse(mapping["collapseEligible"])
        self.assertEqual("EPI-CONFLICT", mapping["canonicalEpisodeId"])
        self.assertEqual(
            ["EPI-CONFLICT"],
            [record["episodeId"] for record in reconciliation["episodes"]],
        )
        self.assertGreaterEqual(len(reconciliation["reviewQueue"]), 1)

    def test_numbered_pair_cardinality_failure_uses_candidate_semantics(self) -> None:
        dataset = {
            "episodes": [
                _episode("EPI-MODERN", "#2 Alpha topic", "#2 Alpha topic.txt", 2)
            ],
            "items": [_item("ITEM-1", "EPI-MODERN")],
        }
        with patch(
            "scripts.cognitive_security.reconcile.GOVERNED_EDITED_RELEASE_ALIASES",
            (),
        ), patch(
            "scripts.cognitive_security.reconcile.GOVERNED_DISTINCT_PUBLICATION_REUSES",
            (),
        ):
            reconciliation = build_episode_reconciliation(dataset)

        mapping = reconciliation["mappings"][0]
        self.assertEqual("ambiguous", mapping["mappingStatus"])
        self.assertEqual("candidate", mapping["mappingRole"])
        self.assertIsNone(mapping["candidateCanonicalEpisodeId"])
        self.assertEqual(
            ["governed-episode-number-cardinality-unresolved"],
            mapping["mappingBasis"],
        )

    def test_conflicting_number_identity_cannot_leave_peer_collapse_eligible(self) -> None:
        dataset = {
            "episodes": [
                _episode("EPI-MODERN", "#2 Alpha topic", "#3 Alpha topic.txt", 2),
                _episode(
                    "EPI-LEGACY",
                    "The Cognitive Crucible Episode 003: Alpha topic",
                    "The Cognitive Crucible Episode 003 Alpha topic.txt",
                    3,
                ),
            ],
            "items": [
                _item("ITEM-1", "EPI-MODERN"),
                _item("ITEM-2", "EPI-LEGACY"),
            ],
        }
        with patch(
            "scripts.cognitive_security.reconcile.GOVERNED_EDITED_RELEASE_ALIASES",
            (),
        ), patch(
            "scripts.cognitive_security.reconcile.GOVERNED_DISTINCT_PUBLICATION_REUSES",
            (),
        ):
            reconciliation = build_episode_reconciliation(dataset)
            products = build_reconciliation_products(dataset)

        self.assertEqual([], reconciliation["aliasGroups"])
        self.assertEqual(
            {"ambiguous"},
            {mapping["mappingStatus"] for mapping in reconciliation["mappings"]},
        )
        self.assertTrue(
            all(
                mapping["mappingRole"] == "candidate"
                and not mapping["collapseEligible"]
                for mapping in reconciliation["mappings"]
            )
        )
        self.assertEqual(2, len(reconciliation["episodes"]))
        self.assertEqual(
            [],
            validate_reconciliation_dataset(
                dataset,
                products["reconciledDataset"],
                products["privatePayloads"],
                products["publicAggregate"],
            ),
        )
        tampered_private = copy.deepcopy(products["privatePayloads"])
        tampered_private["reconciliation_review_queue.json"][0]["reason"] = (
            "Tampered review rationale"
        )
        self.assertIn(
            "The reconciliation review queue does not exactly preserve pending flags.",
            validate_reconciliation_dataset(
                dataset,
                products["reconciledDataset"],
                tampered_private,
                products["publicAggregate"],
            ),
        )

    def test_likely_aliases_remain_distinct_without_title_corroboration(self) -> None:
        dataset = {
            "episodes": [
                _episode("EPI-MODERN", "#2 Alpha topic", "#2 Alpha topic.txt", 2),
                _episode(
                    "EPI-LEGACY",
                    "The Cognitive Crucible Episode 002: Completely different subject",
                    "The Cognitive Crucible Episode 002 Completely different subject.txt",
                    3,
                ),
            ],
            "items": [
                _item("ITEM-1", "EPI-MODERN"),
                _item("ITEM-2", "EPI-LEGACY"),
            ],
        }
        with patch(
            "scripts.cognitive_security.reconcile.GOVERNED_EDITED_RELEASE_ALIASES",
            (),
        ), patch(
            "scripts.cognitive_security.reconcile.GOVERNED_DISTINCT_PUBLICATION_REUSES",
            (),
        ):
            reconciliation = build_episode_reconciliation(dataset)

        self.assertEqual(
            {"likely-alias"},
            {record["mappingStatus"] for record in reconciliation["mappings"]},
        )
        self.assertEqual(2, len(reconciliation["episodes"]))
        self.assertTrue(
            all(not record["collapseEligible"] for record in reconciliation["mappings"])
        )

    def test_reconciliation_is_deterministic_and_does_not_mutate_input(self) -> None:
        dataset = {
            "episodes": [
                _episode("EPI-MODERN", "#2 Alice on trust", "#2 Alice on trust.txt", 2),
                _episode(
                    "EPI-LEGACY",
                    "The Cognitive Crucible Episode 002: Alice on trust",
                    "The Cognitive Crucible Episode 002 Alice on trust.txt",
                    3,
                ),
                _episode("EPI-UNIQUE", "#40 Unique topic", "#40 Unique topic.txt", 4),
            ],
            "items": [
                _item("ITEM-1", "EPI-MODERN"),
                _item("ITEM-2", "EPI-LEGACY"),
                _item("ITEM-3", "EPI-UNIQUE", "contextual"),
            ],
        }
        historical = copy.deepcopy(dataset)
        shuffled = copy.deepcopy(dataset)
        random.Random(1451).shuffle(shuffled["episodes"])
        random.Random(1452).shuffle(shuffled["items"])

        with patch(
            "scripts.cognitive_security.reconcile.GOVERNED_EDITED_RELEASE_ALIASES",
            (),
        ), patch(
            "scripts.cognitive_security.reconcile.GOVERNED_DISTINCT_PUBLICATION_REUSES",
            (),
        ):
            first = build_episode_reconciliation(dataset)
            second = build_episode_reconciliation(shuffled)
            reconciled = apply_episode_reconciliation(dataset, first)

        self.assertEqual(historical, dataset, "Historical input was mutated in memory.")
        self.assertEqual(_canonical_json(first), _canonical_json(second))
        self.assertEqual(
            [record["episodeId"] for record in first["episodes"]],
            [record["episodeId"] for record in second["episodes"]],
        )
        self.assertEqual(
            [record["episodeSourceMappingId"] for record in first["mappings"]],
            [record["episodeSourceMappingId"] for record in second["mappings"]],
        )

        old_episode_by_item = {
            record["itemId"]: record["episodeId"] for record in historical["items"]
        }
        for item in reconciled["items"]:
            self.assertEqual(old_episode_by_item[item["itemId"]], item["sourceIdentityId"])
            self.assertIsNotNone(item["episodeId"])


@unittest.skipUnless(
    (NORMALIZED_DIR / "episode_source_mappings.json").is_file()
    and (RECONCILIATION_DIR / "corpus_reconciliation_report.json").is_file(),
    "private reconciled release has not been built",
)
class GovernedCorpusReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dataset = _load_private_dataset()
        cls.identities = cls.dataset["episode_source_identities"]
        cls.mappings = cls.dataset["episode_source_mappings"]
        cls.episodes = cls.dataset["episodes"]
        cls.items = cls.dataset["items"]
        cls.alias_groups = json.loads(
            (RECONCILIATION_DIR / "alias_groups.json").read_text(encoding="utf-8")
        )
        cls.report = json.loads(
            (RECONCILIATION_DIR / "corpus_reconciliation_report.json").read_text(
                encoding="utf-8"
            )
        )

    def test_every_source_identity_has_exactly_one_status_and_no_identity_is_dropped(self) -> None:
        identity_ids = [row["sourceIdentityId"] for row in self.identities]
        mapped_ids = [row["sourceIdentityId"] for row in self.mappings]
        self.assertEqual(269, len(identity_ids))
        self.assertEqual(len(identity_ids), len(set(identity_ids)))
        self.assertEqual(len(mapped_ids), len(set(mapped_ids)))
        self.assertEqual(set(identity_ids), set(mapped_ids))
        for mapping in self.mappings:
            self.assertIn(mapping["mappingStatus"], MAPPING_STATUSES)
            self.assertIsInstance(mapping["mappingStatus"], str)
            self.assertTrue(mapping["mappingStatus"])

    def test_27_confirmed_alias_groups_have_one_canonical_source_each(self) -> None:
        mapping_by_source = {row["sourceIdentityId"]: row for row in self.mappings}
        self.assertEqual(27, len(self.alias_groups))
        grouped_members: set[str] = set()
        for group in self.alias_groups:
            members = group["sourceIdentityIds"]
            self.assertGreaterEqual(len(members), 2)
            self.assertEqual(len(members), len(set(members)))
            self.assertIn(group["canonicalSourceIdentityId"], members)
            member_mappings = [mapping_by_source[source_id] for source_id in members]
            self.assertEqual(
                1,
                sum(row["mappingRole"] == "canonical" for row in member_mappings),
            )
            self.assertTrue(
                all(row["mappingStatus"] == "confirmed-alias" for row in member_mappings)
            )
            self.assertTrue(
                all(
                    row["collapseEligible"] == (row["mappingRole"] == "alias")
                    for row in member_mappings
                )
            )
            self.assertFalse(grouped_members.intersection(members))
            grouped_members.update(members)
            if group["aliasGroupId"] == "EAG-186":
                self.assertTrue(
                    all(
                        row["decisionSource"]
                        == "governed-transcript-forensic-decision"
                        for row in member_mappings
                    )
                )

        confirmed_members = {
            row["sourceIdentityId"]
            for row in self.mappings
            if row["mappingStatus"] == "confirmed-alias"
        }
        self.assertEqual(confirmed_members, grouped_members)

    def test_episode_membership_is_bidirectionally_complete(self) -> None:
        membership_counts: dict[str, int] = {}
        episode_by_source: dict[str, str] = {}
        for episode in self.episodes:
            for source_id in episode["sourceIdentityIds"]:
                membership_counts[source_id] = membership_counts.get(source_id, 0) + 1
                episode_by_source[source_id] = episode["episodeId"]

        self.assertEqual(
            {row["sourceIdentityId"] for row in self.mappings},
            set(membership_counts),
        )
        self.assertTrue(all(count == 1 for count in membership_counts.values()))
        for mapping in self.mappings:
            self.assertEqual(
                mapping["canonicalEpisodeId"],
                episode_by_source[mapping["sourceIdentityId"]],
            )

    def test_canonical_episode_and_sensitivity_counts_reproduce_exactly(self) -> None:
        self.assertEqual(242, len(self.episodes))
        original_scopes = {"focal": 0, "contextual": 0}
        retained_scopes = {"focal": 0, "contextual": 0}
        identity_ids = {row["sourceIdentityId"] for row in self.identities}
        mapping_by_source = {row["sourceIdentityId"]: row for row in self.mappings}
        canonical_sources = {
            row["sourceIdentityId"]
            for row in self.mappings
            if row["mappingRole"] == "canonical"
            and row["mappingStatus"] in {"unique", "confirmed-alias"}
        }
        self.assertEqual(242, len(canonical_sources))
        for item in self.items:
            scope = item["scope"]
            original_scopes[scope] += 1
            self.assertIn(item["sourceIdentityId"], identity_ids)
            self.assertEqual(
                mapping_by_source[item["sourceIdentityId"]]["canonicalEpisodeId"],
                item["episodeId"],
            )
            if item["sourceIdentityId"] in canonical_sources:
                retained_scopes[scope] += 1

        self.assertEqual({"focal": 10_940, "contextual": 3_457}, original_scopes)
        self.assertEqual({"focal": 9_855, "contextual": 3_123}, retained_scopes)
        self.assertEqual(14_397, sum(original_scopes.values()))
        self.assertEqual(12_978, sum(retained_scopes.values()))
        self.assertEqual(
            {"items": 14_397, "focalItems": 10_940, "contextualItems": 3_457},
            self.report["originalCounts"],
        )
        self.assertEqual(
            {"items": 12_978, "focalItems": 9_855, "contextualItems": 3_123},
            self.report["reconciledSensitivityCounts"],
        )

    def test_governed_reconciliation_products_are_byte_deterministic(self) -> None:
        # This re-runs the pure analysis from a historical v1.0-shaped view,
        # reconstructed from preserved source identities and item provenance.
        historical = copy.deepcopy(self.dataset)
        historical["episodes"] = [
            {
                "episodeId": row["sourceIdentityId"],
                "podcast": row.get("podcast"),
                "episodeTitle": row.get("sourceEpisodeTitle"),
                "sourceFile": row.get("sourceFile"),
                "source": row.get("source"),
            }
            for row in self.identities
        ]
        for item in historical["items"]:
            item["episodeId"] = item["sourceIdentityId"]
        first = build_reconciliation_products(historical)
        second = build_reconciliation_products(copy.deepcopy(historical))
        self.assertEqual(_canonical_json(first), _canonical_json(second))
        self.assertEqual(
            12_978,
            first["privatePayloads"]["item_sensitivity_summary.json"]["reconciled"]["items"],
        )


class PublicReconciliationBoundaryTests(unittest.TestCase):
    @unittest.skipUnless(
        (PUBLIC_DIR / "corpus_reconciliation.json").is_file(),
        "public reconciliation aggregate has not been built",
    )
    def test_public_aggregate_is_counts_only_and_has_no_identity_details(self) -> None:
        payload = json.loads(
            (PUBLIC_DIR / "corpus_reconciliation.json").read_text(encoding="utf-8")
        )
        self.assertEqual(242, payload["counts"]["canonicalEpisodes"])
        self.assertEqual(269, payload["counts"]["originalSourceIdentities"])
        self.assertEqual(27, payload["counts"]["confirmedAliasGroups"])
        self.assertEqual(
            54, payload["counts"]["sourceIdentitiesInConfirmedAliasGroups"]
        )
        self.assertEqual(
            27, payload["counts"]["excludedConfirmedAliasSourceIdentities"]
        )
        self.assertEqual(0, payload["counts"]["pendingDecisionRecords"])
        self.assertEqual(14_397, payload["counts"]["originalItems"])
        self.assertEqual(12_978, payload["counts"]["reconciledSensitivityItems"])
        self.assertIn(
            payload["reanalysisRecommendation"],
            {
                "human-adjudication-required-before-public-count-change",
                "partial-count-and-coverage-remediation-warranted",
                "full-pipeline-reanalysis-recommended",
            },
        )

        serialized = _canonical_json(payload).casefold()
        for prohibited in (
            "sourcefile",
            "sourceidentityid",
            "canonicalsourceidentityid",
            "aliasgroupid",
            "sourceidentityids",
            "normalizedtitle",
            "normalizedsourcefilename",
            "transcripttext",
            "transcripthash",
            ".txt",
            ".xlsx",
            "analysis/",
            "source-data/",
        ):
            with self.subTest(prohibited=prohibited):
                self.assertNotIn(prohibited, serialized)

    @unittest.skipUnless(
        (PUBLIC_DIR / "episodes.json").is_file(),
        "public episode feed has not been built",
    )
    def test_public_episode_feed_uses_canonical_count_not_source_identity_count(self) -> None:
        episodes = json.loads(
            (PUBLIC_DIR / "episodes.json").read_text(encoding="utf-8")
        )
        self.assertEqual(242, len(episodes))
        self.assertNotEqual(269, len(episodes))
        self.assertEqual(len(episodes), len({row["episodeId"] for row in episodes}))
        for row in episodes:
            self.assertNotIn("sourceFile", row)
            self.assertNotIn("sourceIdentityIds", row)
            self.assertNotIn("canonicalSourceIdentityId", row)


@unittest.skipUnless(SOURCE_DIR.is_dir(), "ignored source package is not present")
class ImmutableSourceRegressionTests(unittest.TestCase):
    def test_all_eight_source_workbook_hashes_are_unchanged(self) -> None:
        self.assertEqual(
            set(EXPECTED_SOURCE_HASHES),
            {path.name for path in SOURCE_DIR.glob("*.xlsx")},
        )
        for filename, expected in EXPECTED_SOURCE_HASHES.items():
            with self.subTest(filename=filename):
                actual = hashlib.sha256((SOURCE_DIR / filename).read_bytes()).hexdigest()
                self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
