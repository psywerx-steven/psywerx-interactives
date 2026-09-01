"""Adversarial tests for transcript-summary publication gates."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from typing import Any
import unittest
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_episode_products  # noqa: E402
import build_transcript_summaries as release  # noqa: E402


def write_report(path: Path, value: Any) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


class TranscriptSummaryReleaseGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.summaries = [
            {"episodeId": f"EPI-{index:03d}", "summary": f"grounded {index}"}
            for index in range(24)
        ]
        self.payload_hash = release._canonical_payload_sha256(self.summaries)

    def coverage(self, root: Path | None = None) -> list[dict]:
        records = []
        base = root if root is not None else Path("C:/private")
        for row in self.summaries:
            chunk_path = base / "chunks" / row["episodeId"] / "chunk-001.txt"
            if root is not None:
                chunk_path.parent.mkdir(parents=True, exist_ok=True)
                chunk_path.write_text(
                    f"grounded chunk for {row['episodeId']}\n", encoding="utf-8"
                )
                digest = hashlib.sha256(chunk_path.read_bytes()).hexdigest()
            else:
                digest = "0" * 64
            records.append(
                {
                    "episodeId": row["episodeId"],
                    "cleanedSequentialCoverageComplete": True,
                    "chunks": [
                        {
                            "chunkNumber": 1,
                            "privatePath": str(chunk_path),
                            "sha256": digest,
                        }
                    ],
                }
            )
        return records

    def deep_report(self, coverage: list[dict] | None = None) -> dict:
        coverage = self.coverage() if coverage is None else coverage
        episodes = [
            {
                "episodeId": row["episodeId"],
                "chunksRead": ["chunk-001.txt"],
                "allChunksRead": True,
                "initialClassification": "SUPPORTED",
                "finalClassification": "SUPPORTED",
            }
            for row in self.summaries
        ]
        return {
            "status": "pass",
            "summaryPayloadSha256": self.payload_hash,
            "chunkCoverageSha256": release._canonical_payload_sha256(coverage),
            "reviewedEpisodeCount": len(episodes),
            "initialCounts": {"SUPPORTED": len(episodes)},
            "finalCounts": {"SUPPORTED": len(episodes)},
            "unresolvedMajorIssueCount": 0,
            "episodes": episodes,
        }

    @staticmethod
    def args(output: Path, **overrides):
        values = {
            "output": output,
            "qa_report": None,
            "adjudication_report": None,
            "deep_qa_report": None,
        }
        values.update(overrides)
        return SimpleNamespace(**values)

    def test_private_candidate_does_not_claim_release_qa(self) -> None:
        with TemporaryDirectory() as directory:
            args = self.args(Path(directory) / "candidate.json")
            release._validate_public_release_gate(args, self.summaries)

    def test_public_write_rejects_missing_or_stale_automatic_qa(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(ValueError, "automatic QA report"):
                release._validate_public_release_gate(
                    self.args(release.DEFAULT_SUMMARIES), self.summaries
                )
            stale = write_report(
                root / "automatic.json",
                {
                    "status": "pass",
                    "summaryCount": len(self.summaries),
                    "summaryPayloadSha256": "0" * 64,
                    "issueCounts": {},
                    "issues": [],
                },
            )
            with self.assertRaisesRegex(ValueError, "failing, stale"):
                release._validate_public_release_gate(
                    self.args(release.DEFAULT_SUMMARIES, qa_report=stale),
                    self.summaries,
                )

    def test_public_write_requires_exact_review_dispositions_and_deep_qa(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            issue = {
                "severity": "review",
                "code": "possible-transcript-identity-mismatch",
                "episodeIds": [self.summaries[0]["episodeId"]],
                "detail": "reviewed fixture",
            }
            automatic = write_report(
                root / "automatic.json",
                {
                    "status": "pass",
                    "summaryCount": len(self.summaries),
                    "summaryPayloadSha256": self.payload_hash,
                    "issueCounts": {"review": 1},
                    "issues": [issue],
                },
            )
            coverage_payload = self.coverage(root)
            coverage = write_report(root / "coverage.json", coverage_payload)
            deep = write_report(
                root / "deep.json", self.deep_report(coverage_payload)
            )
            without_disposition = self.args(
                release.DEFAULT_SUMMARIES,
                qa_report=automatic,
                deep_qa_report=deep,
            )
            with self.assertRaisesRegex(ValueError, "adjudication report"):
                release._validate_public_release_gate(
                    without_disposition, self.summaries
                )

            adjudication = write_report(
                root / "adjudication.json",
                {
                    "status": "pass",
                    "summaryPayloadSha256": self.payload_hash,
                    "unresolvedIssueCount": 0,
                    "reviewedIssueFingerprints": [
                        release._issue_fingerprint(issue)
                    ],
                },
            )
            complete = self.args(
                release.DEFAULT_SUMMARIES,
                qa_report=automatic,
                adjudication_report=adjudication,
                deep_qa_report=deep,
            )
            with patch.object(release, "DEFAULT_CHUNK_COVERAGE", coverage):
                release._validate_public_release_gate(complete, self.summaries)

            deep_payload = json.loads(deep.read_text(encoding="utf-8"))
            deep_payload["reviewedEpisodeCount"] = 23
            write_report(deep, deep_payload)
            with self.assertRaisesRegex(ValueError, "24-episode gate"):
                release._validate_public_release_gate(complete, self.summaries)

    def test_automatic_issue_counts_cannot_contradict_embedded_issues(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            deep = write_report(root / "deep.json", self.deep_report())
            embedded_error = write_report(
                root / "embedded-error.json",
                {
                    "status": "pass",
                    "summaryCount": len(self.summaries),
                    "summaryPayloadSha256": self.payload_hash,
                    "issueCounts": {},
                    "issues": [
                        {
                            "severity": "error",
                            "code": "unsupported-numerical-claim",
                            "episodeIds": [self.summaries[0]["episodeId"]],
                        }
                    ],
                },
            )
            with self.assertRaisesRegex(ValueError, "failing, stale"):
                release._validate_public_release_gate(
                    self.args(
                        release.DEFAULT_SUMMARIES,
                        qa_report=embedded_error,
                        deep_qa_report=deep,
                    ),
                    self.summaries,
                )

            missing_review = write_report(
                root / "missing-review.json",
                {
                    "status": "pass",
                    "summaryCount": len(self.summaries),
                    "summaryPayloadSha256": self.payload_hash,
                    "issueCounts": {"review": 1},
                    "issues": [],
                },
            )
            with self.assertRaisesRegex(ValueError, "failing, stale"):
                release._validate_public_release_gate(
                    self.args(
                        release.DEFAULT_SUMMARIES,
                        qa_report=missing_review,
                        deep_qa_report=deep,
                    ),
                    self.summaries,
                )

    def test_deep_gate_requires_distinct_episode_evidence_and_exact_counts(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            automatic = write_report(
                root / "automatic.json",
                {
                    "status": "pass",
                    "summaryCount": len(self.summaries),
                    "summaryPayloadSha256": self.payload_hash,
                    "issueCounts": {},
                    "issues": [],
                },
            )
            scalar_only = write_report(
                root / "scalar-only.json",
                {
                    "status": "pass",
                    "summaryPayloadSha256": self.payload_hash,
                    "reviewedEpisodeCount": 24,
                    "unresolvedMajorIssueCount": 0,
                },
            )
            with self.assertRaisesRegex(ValueError, "per-episode"):
                release._validate_public_release_gate(
                    self.args(
                        release.DEFAULT_SUMMARIES,
                        qa_report=automatic,
                        deep_qa_report=scalar_only,
                    ),
                    self.summaries,
                )

            invalid = self.deep_report()
            invalid["episodes"][1]["episodeId"] = invalid["episodes"][0]["episodeId"]
            invalid["episodes"][2]["allChunksRead"] = False
            invalid_report = write_report(root / "invalid-deep.json", invalid)
            with self.assertRaisesRegex(ValueError, "24-episode gate"):
                release._validate_public_release_gate(
                    self.args(
                        release.DEFAULT_SUMMARIES,
                        qa_report=automatic,
                        deep_qa_report=invalid_report,
                    ),
                    self.summaries,
                )

            coverage_payload = self.coverage(root)
            coverage = write_report(root / "coverage.json", coverage_payload)
            fictitious = self.deep_report(coverage_payload)
            for episode in fictitious["episodes"]:
                episode["chunksRead"] = ["not-a-real-chunk.txt"]
            fictitious_report = write_report(root / "fictitious.json", fictitious)
            with patch.object(release, "DEFAULT_CHUNK_COVERAGE", coverage):
                with self.assertRaisesRegex(ValueError, "fictitious"):
                    release._validate_public_release_gate(
                        self.args(
                            release.DEFAULT_SUMMARIES,
                            qa_report=automatic,
                            deep_qa_report=fictitious_report,
                        ),
                        self.summaries,
                    )

    def test_public_write_cannot_override_canonical_source_authorities(self) -> None:
        canonical = SimpleNamespace(
            output=release.DEFAULT_SUMMARIES,
            manifest=release.DEFAULT_MANIFEST,
            episodes=release.DEFAULT_EPISODES,
        )
        release._validate_public_source_authority(canonical)
        for field, value in (
            ("manifest", Path("fabricated-manifest.json")),
            ("episodes", Path("fabricated-episodes.json")),
        ):
            with self.subTest(field=field):
                overridden = SimpleNamespace(**vars(canonical))
                setattr(overridden, field, value)
                with self.assertRaisesRegex(ValueError, "canonical"):
                    release._validate_public_source_authority(overridden)

    def test_validated_payload_hash_is_independent_of_fragment_order(self) -> None:
        episodes = []
        manifest = []
        summaries = []
        for index in range(242):
            episode_id = f"EPI-FIXTURE-{index:03d}"
            episode_number = index if index < 241 else None
            episode_title = f"Fixture episode {index}"
            transcript_words = 6_000 + index
            episodes.append(
                {
                    "episodeId": episode_id,
                    "parsedEpisodeNumber": episode_number,
                    "episodeTitle": episode_title,
                }
            )
            manifest.append(
                {
                    "episodeId": episode_id,
                    "transcriptWordCount": transcript_words,
                }
            )
            summaries.append(
                {
                    "episodeId": episode_id,
                    "episodeNumber": episode_number,
                    "episodeTitle": episode_title,
                    "summary": " ".join(
                        [f"fixture{index}"] + ["grounded"] * 99
                    ),
                    "keyTopics": ["Topic one", "Topic two", "Topic three"],
                    "whyItMatters": (
                        "This grounded synthesis helps practitioners understand risks "
                        "and make careful decisions."
                    ),
                    "summaryMethod": "transcript-grounded-synthesis-v1",
                    "transcriptWordCount": transcript_words,
                    "summaryWordCount": 100,
                }
            )
        forward = release._validated_summary_payload(summaries, episodes, manifest)
        reverse = release._validated_summary_payload(
            list(reversed(summaries)), episodes, manifest
        )
        self.assertEqual(forward, reverse)
        self.assertEqual(
            release._canonical_payload_sha256(forward),
            release._canonical_payload_sha256(reverse),
        )

    def test_legacy_structured_item_cli_cannot_publish_summaries(self) -> None:
        args = SimpleNamespace(summaries_from=[Path("reviewed.json")])
        with self.assertRaisesRegex(ValueError, "not supported by this legacy"):
            build_episode_products.build(args)

    def test_ordinary_build_recovery_points_to_transcript_workflow(self) -> None:
        source = (REPO_ROOT / "scripts" / "build_cognitive_security.py").read_text(
            encoding="utf-8"
        )
        recovery = source[source.index("Frozen episode summary product is missing.") :]
        self.assertIn("build_transcript_summaries.py", recovery)
        self.assertNotIn("Run scripts/build_episode_products.py", recovery)


if __name__ == "__main__":
    unittest.main()
