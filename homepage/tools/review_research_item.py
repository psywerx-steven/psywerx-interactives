#!/usr/bin/env python3
"""Apply one explicit human publishing decision to a research item."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from research_stream import ResearchStreamError, generate_public_feed, review_item

REPO = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE = REPO / "data/research-stream/research_items.jsonl"
DEFAULT_PUBLIC_FEED = REPO / "data/research-stream/public_feed.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("item_id", help="Stable research item ID")
    parser.add_argument("decision", choices=("publish", "hold", "reject"))
    parser.add_argument("--date", default=date.today().isoformat(), help="Decision date in YYYY-MM-DD")
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE, help=argparse.SUPPRESS)
    parser.add_argument("--public-feed", type=Path, default=DEFAULT_PUBLIC_FEED, help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        report = review_item(args.database, args.item_id, args.decision, args.date)
        public = generate_public_feed(args.database, args.public_feed)
        report["publicStreamItems"] = public["totalItems"]
        print(json.dumps(report, indent=2))
        return 0
    except (OSError, ResearchStreamError) as exc:
        print(f"Review failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
