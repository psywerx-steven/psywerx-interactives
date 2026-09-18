#!/usr/bin/env python3
"""Ingest a PSYWERX Morning Brief JSON handoff into canonical JSONL."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from research_stream import ResearchStreamError, extract_handoff, generate_public_feed, ingest_handoff

REPO = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE = REPO / "data/research-stream/research_items.jsonl"
DEFAULT_PUBLIC_FEED = REPO / "data/research-stream/public_feed.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Raw JSON or Morning Brief Markdown/text export")
    parser.add_argument("--dry-run", action="store_true", help="Validate and report without writing files")
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE, help=argparse.SUPPRESS)
    parser.add_argument("--public-feed", type=Path, default=DEFAULT_PUBLIC_FEED, help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        text = Path(args.input).read_text(encoding="utf-8-sig")
        payload = extract_handoff(text)
        report = ingest_handoff(payload, args.database, dry_run=args.dry_run)
        if not args.dry_run:
            generate_public_feed(args.database, args.public_feed)
        print(json.dumps(report, indent=2))
        return 2 if report["conflicts"] else 0
    except (OSError, ResearchStreamError) as exc:
        print(
            json.dumps(
                {
                    "added": 0,
                    "updated": 0,
                    "unchanged": 0,
                    "conflicts": 0,
                    "rejected": 1,
                    "error": str(exc),
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
