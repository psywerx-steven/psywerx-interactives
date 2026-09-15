#!/usr/bin/env python3
"""Connect the generated homepage to the Research & Publications Explorer."""
from __future__ import annotations

import argparse
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise ValueError(f"Expected homepage marker not found: {label}")
    return text.replace(old, new, 1)


def patch(root: Path) -> None:
    index = root / "index.html"
    text = index.read_text(encoding="utf-8")
    text = text.replace('<a href="#research">Research</a>', '<a href="/research/">Research</a>')
    text = text.replace('<a href="#research">Research feed</a>', '<a href="/research/">Research explorer</a>')
    text = text.replace('Owner-selected research, developments, and ideas worth watching.', 'Research, developments, methods, and ideas surfaced through the PSYWERX Daily Brief.')
    text = text.replace('Owner-selected Morning Brief items', 'Verified items from the PSYWERX Daily Brief')
    marker = '<div class="feed-actions">'
    replacement = '<div class="feed-actions"><a class="text-button" href="/research/">Explore full archive →</a>'
    text = replace_once(text, marker, replacement, "research feed actions")
    index.write_text(text, encoding="utf-8", newline="\n")

    sitemap = root / "sitemap.xml"
    if sitemap.exists():
        xml = sitemap.read_text(encoding="utf-8")
        research_url = '  <url><loc>https://psywerx.io/research/</loc></url>\n'
        if research_url not in xml:
            xml = xml.replace('</urlset>', research_url + '</urlset>')
            sitemap.write_text(xml, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    patch(args.root)
