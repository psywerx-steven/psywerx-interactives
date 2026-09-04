"""Build the approved canonical Cognitive Security public package."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from cognitive_security.canonical_public import (
    PublicProjectionError,
    build_and_serialize,
    load_projection_inputs,
    verify_approved_checkpoint_commit,
    write_package_atomic,
)


DEFAULT_REPO_ROOT = Path(__file__).resolve().parent.parent
CANONICAL_OUTPUT_RELATIVE = Path("data") / "cognitive-security"
CHECKPOINT_RELATIVE = (
    Path("analysis") / "cognitive-security" / "canonical-resynthesis"
)
EPISODE_SUMMARIES_RELATIVE = CANONICAL_OUTPUT_RELATIVE / "episode_summaries.json"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate and atomically publish the approved, deduplicated canonical "
            "Cognitive Security public projection."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_REPO_ROOT)
    parser.add_argument(
        "--checkpoint-dir",
        type=Path,
        help="Approved checkpoint directory (default: <repo>/analysis/cognitive-security/canonical-resynthesis).",
    )
    parser.add_argument(
        "--normalized-dir",
        type=Path,
        required=True,
        help="Explicit path to the read-only private normalized inputs.",
    )
    parser.add_argument(
        "--episode-summaries-path",
        type=Path,
        help="Safe episode summaries JSON (default: current public episode_summaries.json).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Publication directory (must resolve to <repo>/data/cognitive-security).",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Run commit, projection, privacy, invariant, and determinism checks without writing.",
    )
    return parser


def _resolved_paths(arguments: argparse.Namespace) -> dict[str, Path]:
    repo_root = arguments.repo_root.resolve()
    return {
        "repo_root": repo_root,
        "checkpoint_dir": (
            arguments.checkpoint_dir or repo_root / CHECKPOINT_RELATIVE
        ).resolve(),
        "normalized_dir": arguments.normalized_dir.resolve(),
        "episode_summaries_path": (
            arguments.episode_summaries_path
            or repo_root / EPISODE_SUMMARIES_RELATIVE
        ).resolve(),
        "output_dir": (
            arguments.output_dir or repo_root / CANONICAL_OUTPUT_RELATIVE
        ).resolve(),
    }


def _report(
    payloads: dict[str, object],
    serialized: dict[str, bytes],
    *,
    check_only: bool,
    output_dir: Path,
) -> dict[str, object]:
    manifest = payloads.get("manifest.json")
    if not isinstance(manifest, dict):
        raise PublicProjectionError("Projected manifest.json is missing or invalid.")
    return {
        "status": "pass",
        "mode": "check-only" if check_only else "published",
        "contentVersion": manifest.get("contentVersion"),
        "schemaVersion": manifest.get("schemaVersion"),
        "counts": manifest.get("counts", {}),
        "fileCount": len(serialized),
        "files": [
            {"name": name, "bytes": len(content)}
            for name, content in sorted(serialized.items())
        ],
        **({} if check_only else {"outputDirectory": str(output_dir)}),
    }


def main() -> int:
    arguments = _parser().parse_args()
    paths = _resolved_paths(arguments)
    canonical_output = (paths["repo_root"] / CANONICAL_OUTPUT_RELATIVE).resolve()
    try:
        if not arguments.check_only and paths["output_dir"] != canonical_output:
            raise PublicProjectionError(
                "Publication output must resolve to the repository's "
                "data/cognitive-security directory."
            )
        verify_approved_checkpoint_commit(
            paths["repo_root"], paths["checkpoint_dir"]
        )
        inputs = load_projection_inputs(
            paths["checkpoint_dir"],
            paths["normalized_dir"],
            paths["episode_summaries_path"],
        )
        payloads, serialized = build_and_serialize(inputs)
        if not arguments.check_only:
            write_package_atomic(paths["output_dir"], payloads, serialized)
        report = _report(
            payloads,
            serialized,
            check_only=arguments.check_only,
            output_dir=paths["output_dir"],
        )
    except (OSError, PublicProjectionError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
