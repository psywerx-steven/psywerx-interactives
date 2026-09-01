"""Release gates for the transcript-first public episode summary layer."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLIC_DIR = REPO_ROOT / "data" / "cognitive-security"
PRIVATE_DIR = (
    REPO_ROOT / "analysis" / "cognitive-security" / "transcript-summaries-v1"
)
SUMMARY_FIELDS = {
    "episodeId",
    "episodeNumber",
    "episodeTitle",
    "summary",
    "keyTopics",
    "whyItMatters",
    "summaryMethod",
    "transcriptWordCount",
    "summaryWordCount",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TranscriptSummaryPublicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.episodes = load_json(PUBLIC_DIR / "episodes.json")
        cls.summaries = load_json(PUBLIC_DIR / "episode_summaries.json")

    def test_exact_public_identity_and_schema(self) -> None:
        episodes = {row["episodeId"]: row for row in self.episodes}
        summaries = {row["episodeId"]: row for row in self.summaries}
        self.assertEqual(242, len(self.episodes))
        self.assertEqual(242, len(self.summaries))
        self.assertEqual(set(episodes), set(summaries))
        for episode_id, row in summaries.items():
            with self.subTest(episode_id=episode_id):
                self.assertEqual(SUMMARY_FIELDS, set(row))
                self.assertEqual(
                    episodes[episode_id]["parsedEpisodeNumber"], row["episodeNumber"]
                )
                self.assertEqual(episodes[episode_id]["episodeTitle"], row["episodeTitle"])
                self.assertEqual("transcript-grounded-synthesis-v1", row["summaryMethod"])
                self.assertEqual(len(row["summary"].split()), row["summaryWordCount"])
                self.assertGreaterEqual(row["summaryWordCount"], 100)
                self.assertLessEqual(row["summaryWordCount"], 180)
                self.assertGreater(row["transcriptWordCount"], 0)
                self.assertGreaterEqual(len(row["keyTopics"]), 3)
                self.assertLessEqual(len(row["keyTopics"]), 6)
                self.assertTrue(row["whyItMatters"].strip())
                why_words = len(row["whyItMatters"].split())
                self.assertGreaterEqual(why_words, 10)
                self.assertLessEqual(why_words, 45)
                self.assertEqual(
                    1,
                    len(
                        re.findall(
                            r"[.!?](?:[\"'\u2019\u201d)]*)?(?=\s|$)",
                            row["whyItMatters"],
                        )
                    ),
                    row["whyItMatters"],
                )

    def test_no_duplicate_or_dominant_summary_template(self) -> None:
        normalized = [
            re.sub(r"\W+", " ", row["summary"].casefold()).strip()
            for row in self.summaries
        ]
        self.assertEqual(len(normalized), len(set(normalized)))
        openings = Counter(" ".join(value.split()[:8]) for value in normalized)
        self.assertLessEqual(max(openings.values()), 3)
        mechanical = Counter()
        for row in self.summaries:
            start = row["summary"].casefold().strip()
            for phrase in (
                "this episode discusses",
                "this episode focuses on",
                "the podcast talks about",
                "in this episode",
            ):
                if start.startswith(phrase):
                    mechanical[phrase] += 1
        self.assertLessEqual(sum(mechanical.values()), 6, dict(mechanical))

    def test_public_json_contains_no_private_transcript_details(self) -> None:
        blob = json.dumps(self.summaries, ensure_ascii=False).casefold()
        for forbidden in (
            "selectedtranscriptpath",
            "cleanedtranscriptpath",
            "transcriptsha256",
            "sourcefile",
            "sourceidentityid",
            "c:\\users\\",
            "/users/",
        ):
            self.assertNotIn(forbidden, blob)


@unittest.skipUnless(
    (PRIVATE_DIR / "transcript_manifest.json").is_file(),
    "Private transcript manifest is unavailable.",
)
class TranscriptSummaryPrivateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.episodes = load_json(PUBLIC_DIR / "episodes.json")
        cls.summaries = load_json(PUBLIC_DIR / "episode_summaries.json")
        cls.manifest = load_json(PRIVATE_DIR / "transcript_manifest.json")
        cls.coverage = load_json(PRIVATE_DIR / "chunk_coverage.json")
        cls.classification = load_json(PRIVATE_DIR / "corpus_file_classification.json")
        cls.manifest_report = load_json(PRIVATE_DIR / "manifest_report.json")
        cls.baseline = load_json(PRIVATE_DIR / "analytical_hash_baseline.json")

    def test_manifest_selects_one_canonical_transcript_per_release(self) -> None:
        rows = {row["episodeId"]: row for row in self.manifest}
        self.assertEqual(242, len(rows))
        self.assertEqual({row["episodeId"] for row in self.episodes}, set(rows))
        selected = [row["selectedTranscriptPath"] for row in self.manifest]
        self.assertEqual(242, len(set(selected)))
        self.assertTrue(all(Path(path).is_file() for path in selected))
        self.assertTrue(all(row["selectedFileType"] == "txt" for row in self.manifest))
        self.assertTrue(all(row["transcriptWordCount"] > 0 for row in self.manifest))
        for row in self.manifest:
            with self.subTest(episode_id=row["episodeId"]):
                self.assertRegex(row["transcriptSha256"], r"^[0-9a-f]{64}$")
                variants = row["otherTranscriptVariantsDiscovered"]
                self.assertEqual(4, len(variants))
                self.assertEqual(
                    {"json", "srt", "tsv", "vtt"},
                    {variant["fileType"] for variant in variants},
                )
                self.assertTrue(
                    all(re.fullmatch(r"[0-9a-f]{64}", variant["sha256"]) for variant in variants)
                )
                self.assertTrue(
                    all(
                        variant["contentComparisonStatus"]
                        in {
                            "exact-normalized-text-match",
                            "near-exact-nonmaterial-representation-difference",
                        }
                        for variant in variants
                    )
                )
        self.assertEqual(242, len(self.classification["canonical"]))
        self.assertEqual(27, len(self.classification["excludedAliases"]))
        self.assertEqual(2, len(self.classification["excludedOutsideGovernedCorpus"]))
        self.assertEqual(1_355, self.manifest_report["discoveredTranscriptFileCount"])
        self.assertEqual(968, self.manifest_report["excludedFormatVariantFileCount"])
        self.assertEqual(135, self.manifest_report["excludedAliasFileCount"])
        self.assertEqual(10, self.manifest_report["excludedOutsideGovernedCorpusFileCount"])
        self.assertEqual(968, self.manifest_report["formatVariantComparisonCount"])
        self.assertEqual(
            2,
            self.manifest_report["nearExactNonmaterialFormatVariantDifferences"],
        )
        self.assertEqual(0, self.manifest_report["materialFormatVariantDifferences"])

    def test_alias_and_reuse_edge_cases_are_governed(self) -> None:
        rows = {row["episodeId"]: row for row in self.manifest}
        early = [row for row in self.manifest if row["episodeNumber"] in range(2, 28)]
        self.assertEqual(26, len(early))
        self.assertTrue(
            all(row["duplicateAliasStatus"] == "confirmed-alias-transcripts-excluded" for row in early)
        )
        episode_186 = rows["EPI-72ED08B56161C224"]
        self.assertTrue(Path(episode_186["selectedTranscriptPath"]).name.startswith("#186 "))
        self.assertFalse("Brown Bag" in Path(episode_186["selectedTranscriptPath"]).name)
        original = rows["EPI-72E94D7AF43A4BD3"]
        rerelease = rows["EPI-9960393907F71603"]
        self.assertNotEqual(original["selectedTranscriptPath"], rerelease["selectedTranscriptPath"])
        self.assertEqual(
            "confirmed-content-reuse-distinct-public-release",
            original["contentReuseStatus"]["status"],
        )
        self.assertEqual(
            "confirmed-content-reuse-distinct-public-release",
            rerelease["contentReuseStatus"]["status"],
        )

    def test_complete_beginning_to_end_chunk_coverage(self) -> None:
        self.assertEqual(242, len(self.coverage))
        for row in self.coverage:
            with self.subTest(episode_id=row["episodeId"]):
                self.assertTrue(row["rawBeginningToEndInspected"])
                self.assertTrue(row["cleanedSequentialCoverageComplete"])
                self.assertEqual(row["chunkCount"], len(row["chunks"]))
                self.assertEqual(1, row["chunks"][0]["startWord"])
                self.assertEqual(
                    row["cleanedTranscriptWordCount"], row["chunks"][-1]["endWord"]
                )

    def test_public_transcript_counts_match_private_manifest(self) -> None:
        manifest = {row["episodeId"]: row for row in self.manifest}
        for summary in self.summaries:
            self.assertEqual(
                manifest[summary["episodeId"]]["transcriptWordCount"],
                summary["transcriptWordCount"],
            )

    def test_all_analytical_public_artifacts_are_byte_unchanged(self) -> None:
        for filename, expected in self.baseline.items():
            with self.subTest(filename=filename):
                self.assertEqual(expected, sha256(PUBLIC_DIR / filename))


if __name__ == "__main__":
    unittest.main()
