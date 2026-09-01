"""Build the private transcript manifest or publish reviewed transcript summaries."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any, Mapping, Sequence

from cognitive_security.transcript_summaries import (
    analytical_file_hashes,
    build_old_new_comparison,
    build_transcript_manifest,
    load_json,
    run_corpus_summary_qa,
    sha256_file,
    validate_public_transcript_summaries,
    write_json,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PRIVATE_DIR = (
    REPO_ROOT / "analysis" / "cognitive-security" / "transcript-summaries-v1"
)
DEFAULT_RECONCILIATION = (
    REPO_ROOT
    / "analysis"
    / "cognitive-security"
    / "corpus-reconciliation"
    / "episode_source_reconciliation.json"
)
DEFAULT_EPISODES = REPO_ROOT / "data" / "cognitive-security" / "episodes.json"
DEFAULT_SUMMARIES = REPO_ROOT / "data" / "cognitive-security" / "episode_summaries.json"
DEFAULT_MANIFEST = DEFAULT_PRIVATE_DIR / "transcript_manifest.json"
DEFAULT_CHUNK_COVERAGE = DEFAULT_PRIVATE_DIR / "chunk_coverage.json"


def _canonical_payload_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _issue_fingerprint(issue: Mapping[str, Any]) -> str:
    return _canonical_payload_sha256(dict(issue))


def _strict_count_map(value: object) -> dict[str, int] | None:
    if type(value) is not dict:
        return None
    result: dict[str, int] = {}
    for key, count in value.items():
        if type(key) is not str or type(count) is not int or count < 0:
            return None
        if count:
            result[key] = count
    return dict(sorted(result.items()))


def _validated_summary_payload(
    summaries: Sequence[Mapping[str, Any]],
    episodes: Sequence[Mapping[str, Any]],
    manifest: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    words_by_id = {
        row["episodeId"]: int(row["transcriptWordCount"])
        for row in manifest
    }
    return validate_public_transcript_summaries(
        summaries,
        episodes,
        words_by_id,
    )


def _load_required_report(path: Path | None, label: str) -> Mapping[str, Any]:
    if path is None or not path.is_file():
        raise ValueError(f"Public summary publication requires {label}.")
    report = load_json(path)
    if not isinstance(report, Mapping):
        raise ValueError(f"{label} must contain one JSON object.")
    return report


def _validate_public_source_authority(args: argparse.Namespace) -> None:
    """Prevent public publication from substituting private or public authorities."""

    if args.output.resolve() != DEFAULT_SUMMARIES.resolve():
        return
    if (
        args.manifest.resolve() != DEFAULT_MANIFEST.resolve()
        or args.episodes.resolve() != DEFAULT_EPISODES.resolve()
    ):
        raise ValueError(
            "Public summary publication requires the canonical transcript manifest "
            "and canonical public episode catalog."
        )


def _validate_public_release_gate(
    args: argparse.Namespace,
    summaries: Sequence[Mapping[str, Any]],
) -> None:
    """Require current automatic, adjudication, and deep QA before public writes."""

    if args.output.resolve() != DEFAULT_SUMMARIES.resolve():
        return
    payload_sha256 = _canonical_payload_sha256(list(summaries))
    automatic = _load_required_report(args.qa_report, "a passing automatic QA report")
    automatic_issues = automatic.get("issues")
    if (
        type(automatic_issues) is not list
        or not all(type(issue) is dict for issue in automatic_issues)
    ):
        raise ValueError("Automatic QA contains an invalid issue collection.")
    severities = [issue.get("severity") for issue in automatic_issues]
    if not all(severity in {"error", "review"} for severity in severities):
        raise ValueError("Automatic QA contains an invalid issue severity.")
    derived_issue_counts = dict(sorted(Counter(severities).items()))
    declared_issue_counts = _strict_count_map(automatic.get("issueCounts"))
    if (
        automatic.get("status") != "pass"
        or type(automatic.get("summaryCount")) is not int
        or automatic.get("summaryCount") != len(summaries)
        or automatic.get("summaryPayloadSha256") != payload_sha256
        or declared_issue_counts != derived_issue_counts
        or derived_issue_counts.get("error", 0) != 0
    ):
        raise ValueError(
            "Automatic QA is failing, stale, or does not match the summaries being published."
        )

    review_fingerprints = {
        _issue_fingerprint(issue)
        for issue in automatic_issues
        if issue.get("severity") == "review"
    }
    if review_fingerprints:
        adjudication = _load_required_report(
            args.adjudication_report,
            "a complete automatic-flag adjudication report",
        )
        if (
            adjudication.get("status") != "pass"
            or adjudication.get("summaryPayloadSha256") != payload_sha256
            or type(adjudication.get("unresolvedIssueCount")) is not int
            or adjudication.get("unresolvedIssueCount") != 0
            or type(adjudication.get("reviewedIssueFingerprints")) is not list
            or len(adjudication.get("reviewedIssueFingerprints"))
            != len(review_fingerprints)
            or set(adjudication.get("reviewedIssueFingerprints")) != review_fingerprints
        ):
            raise ValueError(
                "Automatic QA review flags are unresolved, stale, or incompletely adjudicated."
            )

    deep = _load_required_report(args.deep_qa_report, "a passing deep QA report")
    deep_episodes = deep.get("episodes")
    if type(deep_episodes) is not list or not all(
        type(row) is dict for row in deep_episodes
    ):
        raise ValueError("Deep QA must contain per-episode review records.")
    deep_ids = [row.get("episodeId") for row in deep_episodes]
    valid_classifications = {"SUPPORTED", "MINOR REVISION", "MAJOR REVISION"}
    initial_classifications = [
        row.get("initialClassification") for row in deep_episodes
    ]
    final_classifications = [
        row.get("finalClassification") for row in deep_episodes
    ]
    deep_ids_are_strings = all(
        type(episode_id) is str and episode_id for episode_id in deep_ids
    )
    deep_structure_valid = (
        len(deep_ids) >= 24
        and deep_ids_are_strings
        and len(deep_ids) == len(set(deep_ids))
        and set(deep_ids) <= {row["episodeId"] for row in summaries}
        and all(row.get("allChunksRead") is True for row in deep_episodes)
        and all(
            type(row.get("chunksRead")) is list
            and row.get("chunksRead")
            and all(
                type(filename) is str and filename.strip()
                for filename in row.get("chunksRead")
            )
            for row in deep_episodes
        )
        and all(value in valid_classifications for value in initial_classifications)
        and all(value in valid_classifications for value in final_classifications)
    )
    derived_initial_counts = dict(sorted(Counter(initial_classifications).items()))
    derived_final_counts = dict(sorted(Counter(final_classifications).items()))
    declared_initial_counts = _strict_count_map(deep.get("initialCounts"))
    declared_final_counts = _strict_count_map(deep.get("finalCounts"))
    unresolved_major = derived_final_counts.get("MAJOR REVISION", 0)
    deep_gate_invalid = (
        deep.get("status") != "pass"
        or deep.get("summaryPayloadSha256") != payload_sha256
        or not deep_structure_valid
        or type(deep.get("reviewedEpisodeCount")) is not int
        or deep.get("reviewedEpisodeCount") != len(deep_episodes)
        or declared_initial_counts != derived_initial_counts
        or declared_final_counts != derived_final_counts
        or type(deep.get("unresolvedMajorIssueCount")) is not int
        or deep.get("unresolvedMajorIssueCount") != unresolved_major
        or unresolved_major != 0
    )
    if deep_gate_invalid:
        raise ValueError(
            "Deep transcript-grounding QA is failing, stale, or below the 24-episode gate."
        )

    coverage_path = DEFAULT_CHUNK_COVERAGE
    if not coverage_path.is_file():
        raise ValueError("Public summary publication requires canonical chunk coverage.")
    coverage = load_json(coverage_path)
    if type(coverage) is not list or not all(type(row) is dict for row in coverage):
        raise ValueError("Canonical chunk coverage must contain a JSON record array.")
    coverage_by_id: dict[str, list[str]] = {}
    coverage_valid = True
    chunks_root = (coverage_path.parent / "chunks").resolve()
    for row in coverage:
        episode_id = row.get("episodeId")
        chunks = row.get("chunks")
        if (
            type(episode_id) is not str
            or not episode_id
            or episode_id in coverage_by_id
            or row.get("cleanedSequentialCoverageComplete") is not True
            or type(chunks) is not list
            or not chunks
        ):
            coverage_valid = False
            continue
        chunk_names: list[str] = []
        for index, chunk in enumerate(chunks, 1):
            if (
                type(chunk) is not dict
                or type(chunk.get("chunkNumber")) is not int
                or chunk.get("chunkNumber") != index
                or type(chunk.get("privatePath")) is not str
                or type(chunk.get("sha256")) is not str
            ):
                coverage_valid = False
                break
            chunk_path = Path(chunk["privatePath"])
            expected_name = f"chunk-{index:03d}.txt"
            if (
                chunk_path.name != expected_name
                or not chunk_path.is_file()
                or not chunk_path.resolve().is_relative_to(chunks_root)
                or sha256_file(chunk_path) != chunk["sha256"]
            ):
                coverage_valid = False
                break
            chunk_names.append(chunk_path.name)
        coverage_by_id[episode_id] = chunk_names
    summary_ids = {row["episodeId"] for row in summaries}
    reviewed_chunks_match = all(
        coverage_by_id.get(row["episodeId"]) == row["chunksRead"]
        for row in deep_episodes
    )
    if (
        not coverage_valid
        or set(coverage_by_id) != summary_ids
        or not reviewed_chunks_match
        or deep.get("chunkCoverageSha256")
        != _canonical_payload_sha256(coverage)
    ):
        raise ValueError(
            "Deep QA chunk evidence is incomplete, fictitious, or stale against canonical coverage."
        )


def _write_public_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary.write(
                json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
                + "\n"
            )
            temporary.flush()
            temporary_path = Path(temporary.name)
        temporary_path.replace(path)
        temporary_path = None
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def _manifest(args: argparse.Namespace) -> None:
    public_dir = DEFAULT_EPISODES.parent
    write_json(
        args.private_dir / "analytical_hash_baseline.json",
        analytical_file_hashes(public_dir),
    )
    _, _, report = build_transcript_manifest(
        args.transcript_root,
        load_json(args.reconciliation),
        load_json(args.episodes),
        args.private_dir,
        load_json(args.current_summaries),
        args.chunk_words,
    )
    print(
        "Transcript manifest PASS: "
        f"{report['selectedTranscriptCount']} selected TXT files, "
        f"{report['chunkCount']} complete sequential chunks, "
        f"{report['rawTranscriptWords']} raw words."
    )


def _publish(args: argparse.Namespace) -> None:
    _validate_public_source_authority(args)
    manifest = load_json(args.manifest)
    episodes = load_json(args.episodes)
    supplied = [row for path in args.summaries_from for row in load_json(path)]
    validated = _validated_summary_payload(
        supplied,
        episodes,
        manifest,
    )
    _validate_public_release_gate(args, validated)
    if args.output.resolve() == DEFAULT_SUMMARIES.resolve():
        _write_public_json_atomic(args.output, validated)
    else:
        write_json(args.output, validated)
    print(f"Published {len(validated)} validated transcript-first summaries to {args.output}.")


def _qa(args: argparse.Namespace) -> None:
    supplied = load_json(args.summaries)
    manifest = load_json(args.manifest)
    episodes = load_json(args.episodes)
    summaries = _validated_summary_payload(supplied, episodes, manifest)
    report = run_corpus_summary_qa(summaries, episodes, manifest)
    report["summaryPayloadSha256"] = _canonical_payload_sha256(summaries)
    comparison = build_old_new_comparison(
        load_json(args.old_summaries), summaries, automatic_qa=report
    )
    write_json(args.private_dir / "automatic_qa_report.json", report)
    write_json(args.private_dir / "old_vs_new_comparison.json", comparison)
    print(
        f"Corpus QA {report['status'].upper()}: {report['summaryCount']} summaries; "
        f"issues={report['issueCounts']}."
    )
    if report["status"] != "pass":
        raise SystemExit(1)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    manifest = commands.add_parser("manifest", help="Build and validate private transcript inputs.")
    manifest.add_argument("--transcript-root", type=Path, required=True)
    manifest.add_argument("--reconciliation", type=Path, default=DEFAULT_RECONCILIATION)
    manifest.add_argument("--episodes", type=Path, default=DEFAULT_EPISODES)
    manifest.add_argument("--current-summaries", type=Path, default=DEFAULT_SUMMARIES)
    manifest.add_argument("--private-dir", type=Path, default=DEFAULT_PRIVATE_DIR)
    manifest.add_argument("--chunk-words", type=int, default=4_000)
    manifest.set_defaults(handler=_manifest)

    publish = commands.add_parser("publish", help="Validate and freeze reviewed summaries.")
    publish.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    publish.add_argument("--episodes", type=Path, default=DEFAULT_EPISODES)
    publish.add_argument("--summaries-from", type=Path, nargs="+", required=True)
    publish.add_argument("--output", type=Path, default=DEFAULT_SUMMARIES)
    publish.add_argument(
        "--qa-report",
        type=Path,
        help="Passing automatic QA report required when writing the public summary file.",
    )
    publish.add_argument(
        "--adjudication-report",
        type=Path,
        help="Complete dispositions for every automatic review flag, when any exist.",
    )
    publish.add_argument(
        "--deep-qa-report",
        type=Path,
        help="Passing transcript-grounding review of at least 24 episodes.",
    )
    publish.set_defaults(handler=_publish)

    qa = commands.add_parser("qa", help="Run deterministic full-corpus summary QA.")
    qa.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_PRIVATE_DIR / "transcript_manifest.json",
    )
    qa.add_argument("--episodes", type=Path, default=DEFAULT_EPISODES)
    qa.add_argument("--summaries", type=Path, default=DEFAULT_SUMMARIES)
    qa.add_argument(
        "--old-summaries",
        type=Path,
        default=DEFAULT_PRIVATE_DIR / "published_summary_backup.json",
    )
    qa.add_argument("--private-dir", type=Path, default=DEFAULT_PRIVATE_DIR)
    qa.set_defaults(handler=_qa)
    return root


def main() -> None:
    args = parser().parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
