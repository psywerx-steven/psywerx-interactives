#!/usr/bin/env python3
"""Build the PSYWERX Research & Publications Explorer from the canonical research stream."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from research_stream import ResearchStreamError, generate_explorer_data

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "homepage" / "src" / "research"
DATABASE = REPO / "data" / "research-stream" / "research_items.jsonl"
EXPLORER_DATA = REPO / "data" / "research-stream" / "explorer.json"
DEFAULT_OUTPUT = REPO / "research"


def build(output: Path = DEFAULT_OUTPUT) -> dict:
    payload = generate_explorer_data(DATABASE, EXPLORER_DATA)
    output.mkdir(parents=True, exist_ok=True)
    assets = output / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE / "research.css", assets / "research.css")
    shutil.copy2(SOURCE / "research.js", assets / "research.js")
    shutil.copy2(SOURCE / "research.template.html", output / "index.html")
    javascript = "window.PSYWERX_RESEARCH = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + ";\n"
    (assets / "research-data.js").write_text(javascript, encoding="utf-8", newline="\n")
    return {"items": payload["totalItems"], "briefs": len(payload["briefs"]), "output": str(output)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.output), indent=2))
    except (OSError, ResearchStreamError, ValueError) as exc:
        print(f"Research explorer build failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
