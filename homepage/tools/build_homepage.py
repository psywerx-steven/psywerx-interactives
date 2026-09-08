#!/usr/bin/env python3
"""Build PSYWERX's static homepage from validated public projections.

Standard library only. No network, API keys, source transcripts, or account data.
The canonical research database is projected through a strict public allowlist;
pending, held, and rejected records never enter either homepage build.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from research_stream import PUBLIC_FIELDS as PUBLIC_FEED_FIELDS
from research_stream import generate_public_feed

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SITE = ROOT.parent / "homepage-preview"
EXPECTED_AREAS = ["foundations", "methods", "application", "assessment", "inquiry", "learning"]
EXPECTED_FEED = [
    "behavioral-science",
    "technology-modeling",
    "operations-strategy",
    "application-analysis",
]
STATUS_LABELS = {"live": "Live", "progress": "Work in progress", "soon": "Coming soon"}
STATIC_ASSETS = ["brain-mark.webp", "brand-banner.webp", "favicon.png", "home.css", "home.js", "wordmark.webp"]
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
ICONS = {
    "nodes": '<circle cx="12" cy="12" r="3"/><circle cx="5" cy="5" r="2"/><circle cx="19" cy="5" r="2"/><circle cx="5" cy="19" r="2"/><circle cx="19" cy="19" r="2"/><path d="m7 7 3 3m4 4 3 3M17 7l-3 3m-4 4-3 3"/>',
    "change": '<path d="M4 8h13l-3-3m3 3-3 3M20 16H7l3-3m-3 3 3 3"/><circle cx="4" cy="8" r="1"/><circle cx="20" cy="16" r="1"/>',
    "framework": '<rect x="3" y="3" width="7" height="7" rx="1.4"/><rect x="14" y="3" width="7" height="7" rx="1.4"/><rect x="3" y="14" width="7" height="7" rx="1.4"/><rect x="14" y="14" width="7" height="7" rx="1.4"/><path d="M10 6.5h4M6.5 10v4m11-4v4M10 17.5h4"/>',
    "measure": '<path d="M4 3v17h17M8 16v-5m5 5V8m5 8V5"/><path d="m7 7 5-3 6-1"/>',
    "inquiry": '<circle cx="10" cy="10" r="6"/><path d="m14.5 14.5 6 6M7 10h6m-3-3v6"/>',
    "book": '<path d="M12 5c-3-2-6-2-9-1v15c3-1 6-1 9 1 3-2 6-2 9-1V4c-3-1-6-1-9 1Zm0 0v15M6 8h3m-3 4h3m6-4h3m-3 4h3"/>',
}


def icon(name: str) -> str:
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>'


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def display_date(value: str | None) -> str:
    if value is None:
        return "date unavailable"
    parsed = date.fromisoformat(value)
    return f"{MONTHS[parsed.month - 1]} {parsed.day}, {parsed.year}"


def feed_date_meta(item: dict) -> str:
    published = f'Published {display_date(item["sourcePublishedAt"])}'
    added = f'Added {display_date(item["dateAdded"])}'
    return f'<div class="feed-meta"><span>{esc(published)}</span><span>{esc(added)}</span></div>'


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding="utf-8", newline="\n")


def https_url(value) -> bool:
    try:
        parsed = urlparse(value)
        return parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and not parsed.password
    except (TypeError, ValueError):
        return False


def validate(site, platform) -> bool:
    if [area["id"] for area in platform] != EXPECTED_AREAS:
        raise ValueError("Six approved platform areas required, in order.")
    if [category["id"] for category in site["feedCategories"]] != EXPECTED_FEED:
        raise ValueError("Feed taxonomy differs from approved taxonomy.")
    if site["brandLine"] != "exploring the human condition from theory to practice":
        raise ValueError("Brand line changed.")
    for key in ("currentToolsOrigin", "targetOrigin"):
        if not https_url(site[key]):
            raise ValueError(f"Invalid URL: {key}")
    for key in ("newsletterAction", "linkedinUrl"):
        if site.get(key) is not None and not https_url(site[key]):
            raise ValueError(f"Invalid URL: {key}")
    newsletter = urlparse(site["newsletterAction"])
    if newsletter.hostname != "assets.mailerlite.com" or not re.fullmatch(
        r"/jsonp/\d+/forms/\d+/subscribe", newsletter.path
    ):
        raise ValueError("Newsletter action must be the verified public MailerLite form endpoint")
    for area in platform:
        for tool in area["tools"]:
            if tool["status"] not in STATUS_LABELS:
                raise ValueError("Unknown tool status")
            if tool["status"] == "live" and tool.get("path") not in ("/drivers/", "/cognitive-security/"):
                raise ValueError("Live destination requires verification")
    return True


def build(mode="preview", tool_links="preview", root=ROOT, output=None):
    site_dir = Path(output) if output else (DEFAULT_SITE if root == ROOT else root / "site")
    site = read_json(root / "content/site.json")
    platform = read_json(root / "content/platform.json")
    validate(site, platform)

    research_dir = (root.parent / "data/research-stream") if root == ROOT else (root / "data/research-stream")
    public_page = generate_public_feed(
        research_dir / "research_items.jsonl",
        research_dir / "public_feed.json",
    )
    selected = public_page["items"]

    def tool_url(path: str) -> str:
        return site["currentToolsOrigin"].rstrip("/") + path if tool_links == "preview" else "." + path

    def area_tools(area: dict) -> str:
        output_tools = []
        for tool in area["tools"]:
            name = (
                f'<a href="{esc(tool_url(tool["path"]))}">{esc(tool["name"])} ↗</a>'
                if tool["status"] == "live"
                else esc(tool["name"])
            )
            local_link = (
                f'<a class="tool-link" href="#{esc(tool["localAnchor"])}">View research stream →</a>'
                if tool.get("localAnchor")
                else ""
            )
            output_tools.append(
                f'<li><h4>{name}</h4><span class="status {tool["status"]}">{STATUS_LABELS[tool["status"]]}</span>'
                f'<p>{esc(tool["description"])}</p>{local_link}</li>'
            )
        return "".join(output_tools)

    cards = []
    mega = []
    nodes = []
    for area in platform:
        has_live = any(tool["status"] == "live" for tool in area["tools"])
        footer = "Live & in development" if has_live else ("Coming soon" if area["id"] == "learning" else "Work in progress")
        cards.append(
            f'<details class="area-card" id="area-{area["id"]}"><summary aria-label="{esc(area["label"] + ": " + area["domain"] + " — view tools")}">'
            f'<div class="area-top"><span class="area-icon">{icon(area["icon"])}</span><span class="area-number">{area["number"]}</span></div>'
            f'<span class="area-label">{esc(area["label"])}</span><h3>{esc(area["domain"])}</h3><p class="area-description">{esc(area["description"])}</p>'
            f'<span class="area-open"><span>{footer}</span><span class="area-plus" aria-hidden="true">+</span></span></summary>'
            f'<ul class="area-tools">{area_tools(area)}</ul></details>'
        )
        mega.append(
            f'<a class="mega-link" href="#area-{area["id"]}">{icon(area["icon"])}<div><strong>{esc(area["label"])}</strong>'
            f'<span>{esc(area["domain"])}</span></div></a>'
        )
        nodes.append(
            f'<button type="button" class="map-node map-node-{area["id"]}" data-area="{area["id"]}" '
            f'aria-pressed="{str(area["id"] == "foundations").lower()}" aria-controls="map-detail"><div>'
            f'<strong>{esc(area["label"])}</strong><small>{esc(area["domain"])}</small></div><span aria-hidden="true">↗</span></button>'
        )

    filters = "".join(
        f'<button type="button" class="filter-chip" data-filter="{category["id"]}" aria-pressed="false" '
        f'title="{esc(category["description"])}">{esc(category["label"])}</button>'
        for category in site["feedCategories"]
    )
    feed_html = [
        f'<article class="feed-item" data-categories="{esc(" ".join(item["categories"]))}" data-feed-id="{esc(item["itemId"])}">'
        f'{feed_date_meta(item)}<h3>{esc(item["streamTitle"])}</h3><p>{esc(item["streamSummary"])}</p><div class="feed-source">'
        f'<a href="{esc(item["sourceUrl"])}" target="_blank" rel="noopener noreferrer">{esc(item["attribution"])}</a>'
        f'<span class="arrow" aria-hidden="true">↗</span></div></article>'
        for item in selected
    ]
    if not feed_html:
        feed_html = [
            '<div class="feed-empty"><h3>Research selections are on the way.</h3>'
            '<p>Items selected from the Morning Brief will appear here after owner review.</p></div>'
        ]
    next_page = None
    if public_page["nextPage"]:
        prefix = "../data/research-stream/" if tool_links == "preview" else "./data/research-stream/"
        next_page = prefix + public_page["nextPage"]
    home_url = site["targetOrigin"].rstrip("/") + "/"

    replacements = {
        "HOME_URL": esc(home_url),
        "HOME_CURRENT": ' aria-current="page"' if mode == "release" else "",
        "ROBOTS": '<meta name="robots" content="noindex,nofollow">' if mode == "preview" else '<meta name="robots" content="index,follow">',
        "PRODUCTION_METADATA": "" if mode == "preview" else '''<link rel="canonical" href="https://psywerx.io/">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="PSYWERX">
  <meta property="og:title" content="PSYWERX | Behavioral &amp; Social Science in Practice">
  <meta property="og:description" content="PSYWERX is a nonprofit initiative connecting behavioral and social science with practical tools, research, and education.">
  <meta property="og:url" content="https://psywerx.io/">
  <meta property="og:image" content="https://psywerx.io/assets/brand-banner.webp">
  <meta property="og:image:alt" content="PSYWERX — exploring the human condition from theory to practice">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="PSYWERX | Behavioral &amp; Social Science in Practice">
  <meta name="twitter:description" content="A nonprofit initiative connecting behavioral and social science with practical tools, research, and education.">
  <meta name="twitter:image" content="https://psywerx.io/assets/brand-banner.webp">
  <meta name="twitter:image:alt" content="PSYWERX — exploring the human condition from theory to practice">''',
        "MISSION": esc(site["mission"]),
        "DRIVERS_URL": esc(tool_url("/drivers/")),
        "COGNITIVE_URL": esc(tool_url("/cognitive-security/")),
        "MEGA_LINKS": "".join(mega),
        "AREA_CARDS": "".join(cards),
        "MAP_NODES": "".join(nodes),
        "FILTERS": filters,
        "FEED_COUNT": str(len(selected)),
        "FEED_ITEMS": "".join(feed_html),
        "FEED_SNAPSHOT": "Owner-selected Morning Brief items",
        "PREVIEW_BADGE": '<span class="preview-badge">Preview</span>' if mode == "preview" else "",
        "YEAR": "2026",
        "FOOTER_STATUS": "Homepage design preview · not yet deployed" if mode == "preview" else "Behavioral & social science · Tools · Research · Learning",
        "NEWSLETTER_ACTION": esc(site["newsletterAction"]),
        "LINKEDIN_URL": esc(site["linkedinUrl"]),
        "BOOK_ICON": icon("book"),
        "FRAMEWORK_ICON": icon("framework"),
        "CHANGE_ICON": icon("change"),
    }
    template = (root / "src/homepage.template.html").read_text(encoding="utf-8")
    for key, value in replacements.items():
        template = template.replace("{{" + key + "}}", value)
    if re.search(r"{{[A-Z_]+}}", template):
        raise ValueError("Unresolved template marker")

    assets_dir = site_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    for asset in STATIC_ASSETS:
        source = root / "src/assets" / asset
        destination = assets_dir / asset
        if source.suffix in (".css", ".js"):
            write(destination, source.read_text(encoding="utf-8"))
        else:
            shutil.copy2(source, destination)
    write(site_dir / "index.html", template)
    data = {
        "mode": mode,
        "platform": platform,
        "feed": selected,
        "feedCategories": site["feedCategories"],
        "feedPagination": {"totalItems": public_page["totalItems"], "nextPage": next_page},
        "links": {"linkedinUrl": site["linkedinUrl"]},
    }
    javascript = "window.PSYWERX_HOME = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + ";\n"
    write(site_dir / "assets/home-data.js", javascript)

    managed = [site_dir / "index.html", site_dir / "assets/home-data.js"] + [site_dir / "assets" / asset for asset in STATIC_ASSETS]
    if mode == "release":
        write(site_dir / "robots.txt", "User-agent: *\nAllow: /\nSitemap: https://psywerx.io/sitemap.xml\n")
        write(
            site_dir / "sitemap.xml",
            '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://psywerx.io/</loc></url>
  <url><loc>https://psywerx.io/drivers/</loc></url>
  <url><loc>https://psywerx.io/drivers/codebook/</loc></url>
  <url><loc>https://psywerx.io/cognitive-security/</loc></url>
</urlset>
''',
        )
        managed += [site_dir / "robots.txt", site_dir / "sitemap.xml"]
    manifest = {
        path.relative_to(site_dir).as_posix(): {
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for path in sorted(managed)
    }
    write(
        root / "docs/BUILD_MANIFEST.json",
        json.dumps(
            {
                "mode": mode,
                "toolLinks": tool_links,
                "feedCount": len(selected),
                "feedTotal": public_page["totalItems"],
                "files": manifest,
            },
            indent=2,
        )
        + "\n",
    )
    return {
        "mode": mode,
        "feedCount": len(selected),
        "feedTotal": public_page["totalItems"],
        "totalBytes": sum(item["bytes"] for item in manifest.values()),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["preview", "release"], default="preview")
    parser.add_argument("--tool-links", choices=["preview", "local"], default="preview")
    parser.add_argument("--output", help="Output directory; use the repository root for the launch build")
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.mode, args.tool_links, output=args.output), indent=2))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
