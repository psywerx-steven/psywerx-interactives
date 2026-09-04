"""Build the private Cognitive Security canonical re-synthesis checkpoint."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from cognitive_security.canonical_resynthesis import build_canonical_resynthesis


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build the ignored, deduplicated canonical analytical overlay without "
            "changing the live Cognitive Security Explorer."
        )
    )
    repo_root = Path(__file__).resolve().parent.parent
    parser.add_argument("--repo-root", type=Path, default=repo_root)
    parser.add_argument("--normalized-dir", type=Path, required=True)
    parser.add_argument("--reconciliation-dir", type=Path, required=True)
    parser.add_argument("--transcript-summary-dir", type=Path, required=True)
    parser.add_argument("--source-workbook-dir", type=Path, required=True)
    parser.add_argument(
        "--design-dir",
        type=Path,
        default=repo_root
        / "analysis"
        / "cognitive-security"
        / "canonical-resynthesis"
        / "inputs",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=repo_root / "analysis" / "cognitive-security" / "canonical-resynthesis",
    )
    return parser


def main() -> int:
    arguments = _parser().parse_args()
    try:
        result = build_canonical_resynthesis(
            repo_root=arguments.repo_root.resolve(),
            normalized_dir=arguments.normalized_dir.resolve(),
            reconciliation_dir=arguments.reconciliation_dir.resolve(),
            transcript_summary_dir=arguments.transcript_summary_dir.resolve(),
            source_workbook_dir=arguments.source_workbook_dir.resolve(),
            design_dir=arguments.design_dir.resolve(),
            output_dir=arguments.output_dir.resolve(),
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
