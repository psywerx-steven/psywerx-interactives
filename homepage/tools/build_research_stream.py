#!/usr/bin/env python3
"""Build the deterministic public research stream from canonical JSONL."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from research_stream import ResearchStreamError, generate_public_feed

REPO = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE = REPO / "data/research-stream/research_items.jsonl"
DEFAULT_PUBLIC_FEED = REPO / "data/research-stream/public_feed.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--output", type=Path, default=DEFAULT_PUBLIC_FEED)
    parser.add_argument("--page-size", type=int, default=24)
    args = parser.parse_args()
    try:
        report = generate_public_feed(args.database, args.output, page_size=args.page_size)
        print(json.dumps({key: report[key] for key in ("schemaVersion", "pageSize", "totalItems")}, indent=2))
        return 0
    except (OSError, ResearchStreamError) as exc:
        print(f"Public stream build failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
