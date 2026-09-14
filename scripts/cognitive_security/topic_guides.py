"""Compile curated Topic Guides from the improved canonical public corpus.

This module does not cluster episodes, assign analytical relationships, read raw
transcripts, or call a model/network. Editorial admission is explicit. Existing
canonical labels and field-level selections are resolved and checked at build
 time, so a valid-but-wrong ID cannot silently acquire the wrong label.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlencode, urlparse

METHOD = "deduplicated-canonical-resynthesis"
MEMBERSHIP = "explicit-topic-guide-curation-over-canonical-resynthesis"
PUBLIC = Path("data/cognitive-security-guides")
AUTHORING = Path("content/cognitive-security-guides")
SITE = Path("cognitive-security/topic")
ORIGIN = "https://psywerx.io"
CAVEAT = ("Corpus support reflects recurrence and breadth within this practitioner "
          "discourse corpus. It does not indicate scientific validity, consensus, "
          "importance, prevalence, or real-world effect size.")
SECTIONS = {
    "corpus-findings": ("What the Corpus Says", "Selected existing syntheses, not new findings or a claim that guests agree."),
    "concepts": ("Key Concepts & Frameworks", "Conceptual starting points in the existing topic registry."),
    "challenges": ("Challenges Practitioners Identify", "Constraints and recurring problems described in the corpus."),
    "approaches": ("Approaches Practitioners Recommend", "Practitioner proposals, not independently validated recommendations."),
    "tools-methods": ("Tools, Methods & Techniques", "Methods and capabilities discussed in the corpus; effectiveness is not implied by inclusion."),
    "tensions": ("Tensions & Open Questions", "Both sides are retained. A tension is not an endorsement of either pole."),
    "connections": ("Connections Across the Corpus", "Explicitly selected themes and narratives, with the reason each is relevant here."),
}
FILES = {
    "category": ("categories", "categoryId"), "family": ("families", "familyId"),
    "cluster": ("clusters", "clusterId"), "theme": ("themes", "themeId"),
    "tension": ("tensions", "tensionId"), "narrative": ("narratives", "narrativeId"),
    "finding": ("category_findings", "findingId"), "episode": ("episodes", "episodeId"),
}
CARD_FIELDS = {"type", "id", "field", "scopeNote", "expectedName", "sourceFieldSha256", "heading", "span", "label"}
QUOTE_FIELDS = {"quoteId", "episodeId", "speaker", "text", "sourceUrl", "timestamp", "verificationBasis"}
GUIDE_FIELDS = {"guideId", "slug", "title", "group", "scope", "exclusions", "sourceTopics", "featuredEpisodes", "sections"}
EPISODE_FIELDS = {"episodeId", "expectedEpisodeNumber", "takeaways", "topicIds", "quoteId", "summarySha256"}
SOURCE_TOPIC_FIELDS = {"id", "expectedName", "role"}
TAKEAWAY_FIELDS = {"text", "sourceField"}


class GuideError(ValueError):
    """Invalid, stale, or unsafe guide input. No output is written on failure."""


def require(ok: bool, message: str) -> None:
    if not ok:
        raise GuideError(message)


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def encode(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def field_sha(value: Any) -> str:
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8"))


def name(record: dict[str, Any]) -> str:
    for key in ("name", "title", "episodeTitle"):
        if isinstance(record.get(key), str):
            return record[key]
    raise GuideError("Canonical record has no display name")


def esc(text: Any) -> str:
    return html.escape(str(text), quote=True)


def route(kind: str, identity: str) -> str:
    require(kind in FILES, f"Unroutable entity type: {kind}")
    return "/cognitive-security/?" + urlencode({"view": kind, "id": identity})


def link(url: str, text: str, cls: str = "", **attrs: str) -> str:
    safe = urlparse(url)
    require(not safe.scheme or safe.scheme == "https", "Unsafe hyperlink scheme")
    require(not (safe.netloc and not safe.scheme), "Protocol-relative links are not permitted")
    extras = "".join(f' {esc(k)}="{esc(v)}"' for k, v in attrs.items())
    return f'<a href="{esc(url)}" class="{esc(cls)}"{extras}>{esc(text)}</a>'


class Corpus:
    def __init__(self, root: Path):
        self.root = root
        core = root / "data/cognitive-security"
        self.manifest = load(core / "manifest.json")
        self.records = {}
        for kind, (stem, key) in FILES.items():
            values = load(core / (stem + ".json"))
            self.records[kind] = {value[key]: value for value in values}
            require(len(self.records[kind]) == len(values), f"Duplicate canonical {kind} IDs")
        self.summaries = {x["episodeId"]: x for x in load(core / "episode_summaries.json")}
        self.cluster_summaries = {x["clusterId"]: x for x in load(core / "cluster_summaries.json")}
        self.metadata = {x["episodeId"]: x for x in load(root / "data/cognitive-security-discovery/episode_metadata.json")}
        self.provenance = load(core / "provenance.json")
        self.family_for = {}
        for family in self.records["family"].values():
            for cid in family["memberClusterIds"]:
                require(cid not in self.family_for, f"Multiple primary families for {cid}")
                self.family_for[cid] = family["familyId"]
        self.direct = {(x["episodeId"], cid): x for cid, rows in self.provenance["clusterToReleases"].items() for x in rows}

    def get(self, kind: str, identity: str) -> dict[str, Any]:
        require(kind in self.records and identity in self.records[kind], f"Unknown {kind}: {identity}")
        return self.records[kind][identity]

    def validate_lock(self, lock: dict[str, Any]) -> None:
        require(self.manifest.get("methodVersion") == METHOD, "Initial-pass/noncanonical corpus rejected")
        require(self.manifest.get("contentVersion") == "canonical-resynthesis", "Canonical content version required")
        require(lock.get("methodVersion") == METHOD, "Source lock is not canonical")
        require(lock.get("counts") == self.manifest.get("counts"), "Canonical counts changed; review the source lock")
        require(lock.get("clusterNameById") == {k: name(v) for k, v in self.records["cluster"].items()}, "Canonical ID/name registry changed")
        require(lock.get("primaryFamilyByCluster") == self.family_for, "Improved primary-family assignments changed")
        expected_files = {str(p.relative_to(self.root)) for d in ("data/cognitive-security", "data/cognitive-security-discovery") for p in (self.root / d).glob("*.json")}
        require(set(lock["files"]) == expected_files, "Protected source inventory changed")
        for rel, digest in lock["files"].items():
            require(sha((self.root / rel).read_bytes()) == digest, f"Protected canonical source changed: {rel}")

    def resolve(self, ref: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
        require(set(ref) <= CARD_FIELDS, "Source reference contains non-allowlisted fields")
        rec = self.get(ref["type"], ref["id"])
        selected = self.summaries[ref["id"]] if ref["type"] == "episode" else rec
        require(ref.get("expectedName") == name(selected), f"ID/name mismatch: {ref['id']}")
        field = ref["field"]
        if field == "recurringThemes":
            require(ref["type"] == "cluster", "Patterns must reference an existing cluster synthesis")
            matches = [x for x in self.cluster_summaries[ref["id"]][field] if x["name"] == ref.get("heading")]
            require(len(matches) == 1, f"Missing/ambiguous pattern in {ref['id']}")
            value = matches[0]
            title, text = value["name"], value["description"]
        else:
            allowed = {"cluster": "definition", "family": "definition", "finding": "finding", "theme": "definition", "tension": "definition", "narrative": "shortVersion", "episode": "summary"}
            require(field == allowed.get(ref["type"]), "Unsafe or unsupported source field")
            value = selected[field]
            require(isinstance(value, str), "Source passage must be text")
            title, text = ref.get("label", name(selected)), value
        require(ref.get("sourceFieldSha256") == field_sha(value), f"Stale selected passage: {ref['id']}")
        if "span" in ref:
            bounds = ref["span"]
            require(isinstance(bounds, list) and len(bounds) == 2 and all(type(x) is int for x in bounds), "Invalid excerpt range")
            start, end = bounds
            require(0 <= start < end <= len(text), "Excerpt outside source passage")
            text = text[start:end]
        require(bool(text.strip()), "Empty source passage")
        return title, text, rec


def validate_quotes(corpus: Corpus, quotes: dict[str, Any], approvals: dict[str, Any]) -> dict[str, Any]:
    require(set(quotes) == {"schemaVersion", "quotes"}, "Quote payload is not allowlisted")
    require(set(approvals) == {"schemaVersion", "approved"}, "Quote approval payload is not allowlisted")
    approved = {x["quoteId"]: x["publicExcerptSha256"] for x in approvals["approved"]}
    require(len(approved) == len(approvals["approved"]), "Duplicate quote approval")
    result = {}
    for q in quotes["quotes"]:
        require(set(q) == QUOTE_FIELDS, "Quote contains missing or non-allowlisted fields")
        require(q["quoteId"] not in result, "Duplicate quote ID")
        corpus.get("episode", q["episodeId"])
        require(q["verificationBasis"] == "archived-transcript-text", "Quote must state its actual verification basis")
        require(isinstance(q["speaker"], str) and bool(q["speaker"].strip()), "A verified speaker is required")
        require(isinstance(q["text"], str) and 5 <= len(q["text"].split()) <= 40, "Quote length outside the brief-excerpt policy")
        require(q["timestamp"] is None or re.fullmatch(r"\d{1,2}:\d{2}(?::\d{2})?", q["timestamp"]), "Unverified/invalid timestamp")
        source = corpus.metadata[q["episodeId"]]["officialEpisodeUrl"]
        require(source and q["sourceUrl"] == source, "Quote source must match the episode's verified publisher URL")
        require(approved.get(q["quoteId"]) == field_sha(q), "Quote/speaker/episode changed after excerpt review")
        result[q["quoteId"]] = q
    require(set(result) == set(approved), "Quote approvals and published excerpts differ")
    return result


def validate_guides(corpus: Corpus, payload: dict[str, Any], quotes: dict[str, Any]) -> None:
    require(set(payload) == {"schemaVersion", "membershipMethod", "unmappedAllowed", "guides"}, "Guide payload is not allowlisted")
    require(payload.get("membershipMethod") == MEMBERSHIP, "Explicit canonical curation required")
    require(payload.get("unmappedAllowed") is True, "Guides are not an exhaustive partition")
    seen_ids, seen_slugs = set(), set()
    for g in payload["guides"]:
        require(set(g) == GUIDE_FIELDS, "Guide contains missing/non-allowlisted fields")
        require(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", g["slug"]) is not None, "Invalid guide slug")
        require(g["guideId"] not in seen_ids and g["slug"] not in seen_slugs, "Duplicate guide ID or slug")
        seen_ids.add(g["guideId"]); seen_slugs.add(g["slug"])
        require(set(g["sections"]) == set(SECTIONS), "Unknown or missing guide section")
        source_ids = set()
        for source in g["sourceTopics"]:
            require(set(source) == SOURCE_TOPIC_FIELDS, "Source-topic record is not allowlisted")
            rec = corpus.get("cluster", source["id"])
            require(name(rec) == source["expectedName"], f"ID/name mismatch: {source['id']}")
            require(source["role"] in ("core", "supporting"), "Invalid source-topic role")
            require(source["id"] not in source_ids, "Duplicate source topic")
            source_ids.add(source["id"])
        # sourceTopics are discovery aids, NOT evidence/guide membership edges.
        admitted_clusters = {r["id"] for refs in g["sections"].values() for r in refs if r["type"] == "cluster"}
        for section, refs in g["sections"].items():
            unique = set()
            for ref in refs:
                corpus.resolve(ref)
                key = (ref["type"], ref["id"], ref["field"], ref.get("heading"), str(ref.get("span")))
                require(key not in unique, f"Duplicate card in {g['slug']}/{section}")
                unique.add(key)
                if section == "tensions":
                    require(ref["type"] == "tension", "Tension section requires canonical tension records")
        require(4 <= len(g["featuredEpisodes"]) <= 6, "Starting set must contain 4–6 episodes")
        episodes = set()
        for e in g["featuredEpisodes"]:
            require(set(e) == EPISODE_FIELDS, "Featured episode contains missing/non-allowlisted fields")
            rec = corpus.get("episode", e["episodeId"])
            require(rec["parsedEpisodeNumber"] == e["expectedEpisodeNumber"], "Episode number/ID mismatch")
            require(e["episodeId"] not in episodes, "Duplicate featured episode")
            episodes.add(e["episodeId"])
            summary = corpus.summaries[e["episodeId"]]
            require(summary.get("summaryMethod") == "transcript-grounded-synthesis", "Reviewed public summary required")
            require(e["summarySha256"] == field_sha(summary["summary"]), "Episode summary changed; recheck takeaways")
            require(2 <= len(e["takeaways"]) <= 3, "Each episode needs 2–3 listening takeaways")
            for takeaway in e["takeaways"]:
                require(set(takeaway) == TAKEAWAY_FIELDS and takeaway["sourceField"] == "summary", "Takeaway must cite the reviewed episode summary")
                require(isinstance(takeaway["text"], str) and takeaway["text"].strip(), "Empty takeaway")
            require(len(set(e["topicIds"])) == len(e["topicIds"]), "Duplicate episode topic tag")
            for cid in e["topicIds"]:
                corpus.get("cluster", cid)
                require(cid in admitted_clusters, "Episode tag is not an admitted guide topic")
                edge = corpus.direct.get((e["episodeId"], cid))
                require(edge is not None and edge["primaryItemCount"] > 0, "Episode tag lacks direct primary coded support")
            if e["quoteId"] is not None:
                require(e["quoteId"] in quotes and quotes[e["quoteId"]]["episodeId"] == e["episodeId"], "Quote belongs to a different episode")
    # Intentionally no requirement that all 127 clusters or 242 releases have a guide.


def chips(corpus: Corpus, refs: list[tuple[str, str]]) -> str:
    return '<div class="guide-tags">' + "".join(link(route(k, i), name(corpus.get(k, i)), "guide-tag") for k, i in dict.fromkeys(refs)) + "</div>"


def render_card(corpus: Corpus, ref: dict[str, Any]) -> str:
    title, text, rec = corpus.resolve(ref)
    kind, identity = ref["type"], ref["id"]
    label = "Topic synthesis · recurring pattern" if ref["field"] == "recurringThemes" else {"cluster":"Existing topic", "finding":"Canonical finding", "theme":"Cross-cutting theme", "narrative":"Integrative narrative", "tension":"Canonical tension", "episode":"Episode summary excerpt", "family":"Canonical subcategory"}[kind]
    body = f'<article class="source-card" data-source-type="{esc(kind)}" data-source-id="{esc(identity)}"><p class="eyebrow">{esc(label)}</p><h3>{link(route(kind,identity),title)}</h3><p>{esc(text)}</p>'
    if ref.get("scopeNote"):
        body += '<p class="scope-note"><strong>Why it is here:</strong> ' + esc(ref["scopeNote"]) + '</p>'
    if kind == "tension":
        body += '<div class="tension-poles">'
        for suffix in ("A", "B"):
            body += f'<div><h4>{esc(rec["pole"+suffix+"Label"])}</h4><p>{esc(rec["pole"+suffix+"Assumption"])}</p></div>'
        body += '</div><p class="caveat">' + esc(rec["falseDichotomyCaveat"]) + '</p>'
    body += '<p class="source-citation">Source: ' + link(route(kind,identity),f'{identity} · {name(rec)}') + '</p>'
    tags = []
    if kind == "cluster":
        tags = [("family", corpus.family_for[identity]), ("category", rec["categoryId"])]
    elif kind == "finding":
        tags = [("family", fid) for fid in rec.get("supportingFamilyIds", [])]
    body += chips(corpus, tags) if tags else ""
    return body + '</article>'


def render_episode(corpus: Corpus, e: dict[str, Any], quotes: dict[str, Any], order: int) -> str:
    ep = corpus.get("episode", e["episodeId"]); meta = corpus.metadata[e["episodeId"]]
    url = route("episode", ep["episodeId"])
    head = f'<article class="episode-card" id="episode-{e["expectedEpisodeNumber"]}" data-episode-id="{esc(e["episodeId"])}"><p class="eyebrow">{"Suggested first listen" if order == 0 else "Complementary perspective"}</p><h3>{link(url,name(ep))}</h3>'
    guests = meta.get("guests")
    if guests:
        head += '<p class="guest-line">' + esc(" · ".join(guests)) + '</p>'
    head += '<ul class="takeaways">' + ''.join('<li>' + esc(t["text"]) + '</li>' for t in e["takeaways"]) + '</ul>'
    head += chips(corpus, [("cluster", cid) for cid in e["topicIds"]])
    if e["quoteId"]:
        q = quotes[e["quoteId"]]
        head += f'<figure class="episode-quote"><blockquote><p>“{esc(q["text"])}”</p></blockquote><figcaption>{esc(q["speaker"])} · ' + link(q["sourceUrl"], f'Episode #{e["expectedEpisodeNumber"]}') + '<span class="quote-basis">Transcript excerpt; not independently checked against audio' + (f' · {esc(q["timestamp"])}' if q["timestamp"] else '') + '</span></figcaption></figure>'
    head += '<p class="source-citation">Listening notes: ' + link(url, 'reviewed episode summary') + '.</p><div class="episode-actions">' + link(url, 'Explore episode →', 'text-link')
    if meta.get("officialEpisodeUrl"):
        head += link(meta["officialEpisodeUrl"], 'Listen at The Cognitive Crucible ↗', 'text-link')
    return head + '</div></article>'


def shell(title: str, description: str, path: str, content: str, directory: bool = False) -> str:
    canonical = ORIGIN + path
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | PSYWERX</title><meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(canonical)}"><meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)} | PSYWERX"><meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{esc(canonical)}"><meta property="og:image" content="{ORIGIN}/assets/brand-banner.webp">
<meta property="og:image:alt" content="PSYWERX: applied understanding of human behavior">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)} | PSYWERX">
<meta name="twitter:description" content="{esc(description)}"><meta name="twitter:image" content="{ORIGIN}/assets/brand-banner.webp">
<link rel="icon" href="/assets/favicon.png"><link rel="stylesheet" href="/cognitive-security/topic/guides.css">
<script src="/cognitive-security/topic/guides.js" defer></script></head><body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><div class="header-inner">{link('/', 'PSYWERX', 'wordmark', **{'aria-label':'PSYWERX home'})}<span class="product-name">Cognitive Security<br><strong>Practitioner Discourse Map</strong></span><nav aria-label="Main navigation">{link('/cognitive-security/','Explorer')}{link('/cognitive-security/topic/','Topic Guides','active')}{link('/cognitive-security/?view=methodology','Methodology')}</nav></div></header>
<main id="main" class="guide-main" tabindex="-1">{content}</main>
<footer class="guide-footer"><p>{esc(CAVEAT)}</p><p>Curated entry points, not a complete taxonomy or a ranking of guests. Material describes the podcast discourse; earlier episodes are not current technical or legal guidance.</p><p>{link('/cognitive-security/?view=methodology','Methodology and limitations')} · {link('/cognitive-security/','Cognitive Security Explorer')} · {link('/','PSYWERX home')}</p></footer>
<div class="sr-only" id="guide-status" role="status" aria-live="polite"></div></body></html>\n'''


def render_guide(corpus: Corpus, g: dict[str, Any], quotes: dict[str, Any]) -> str:
    content = f'<nav class="breadcrumbs" aria-label="Breadcrumb">{link("/cognitive-security/","Explorer")} <span>/</span> {link("/cognitive-security/topic/","Topic Guides")} <span>/</span> <span aria-current="page">{esc(g["title"])}</span></nav>'
    content += f'<header class="guide-hero"><p class="eyebrow">Topic Guide · {esc(g["group"])}</p><h1>{esc(g["title"])}</h1><p class="lead">{esc(g["scope"])}</p><p class="curation-note">Curated listening notes and source-linked material from the existing analysis. These guides are starting points, not rankings.</p><div class="hero-actions"><a href="#start-here" class="primary-link">Start listening</a><button type="button" class="copy-link" data-copy-guide>Copy guide link</button></div></header>'
    active = [(k, v) for k, v in SECTIONS.items() if g["sections"][k]]
    content += '<details class="section-jump"><summary>On this page</summary><nav class="section-nav" aria-label="On this page"><a href="#start-here">Start Here</a>' + ''.join(link('#'+key, val[0]) for key,val in active) + '</nav></details>'
    content += f'<section class="guide-section" id="start-here"><div class="section-heading"><p class="eyebrow">Listen & learn</p><h2>Start Here</h2><p>{len(g["featuredEpisodes"])} complementary conversations. The order is a suggested route in, not a score or a claim of agreement.</p></div><div class="episode-list">' + ''.join(render_episode(corpus,e,quotes,i) for i,e in enumerate(g["featuredEpisodes"])) + '</div></section>'
    for key,(heading,description) in active:
        content += f'<section class="guide-section" id="{key}"><div class="section-heading"><h2>{heading}</h2><p>{esc(description)}</p></div><div class="source-grid">' + ''.join(render_card(corpus,ref) for ref in g["sections"][key]) + '</div></section>'
    return shell(g["title"], g["scope"], '/cognitive-security/topic/'+g["slug"]+'/', content)


def render_directory(guides: list[dict[str, Any]]) -> str:
    content = '<header class="guide-hero"><p class="eyebrow">Curated ways into the corpus</p><h1>Topic Guides</h1><p class="lead">Start with a question. Find a few episodes worth listening to, then follow the concepts, findings, and tensions deeper into the Explorer.</p><p class="curation-note">These first 15 guides cover selected interests—not the entire field. Connections are curated around each topic, not generated from whole-episode similarity rankings.</p></header><div class="guide-search"><label for="guide-search">Find a guide</label><input type="search" id="guide-search" placeholder="Assessment, cyber, narrative…" autocomplete="off"><p id="guide-count" role="status">'+str(len(guides))+' guides</p></div>'
    groups = list(dict.fromkeys(g['group'] for g in guides))
    for group in groups:
        content += f'<section class="directory-group" data-guide-group><h2>{esc(group)}</h2><div class="directory-grid">'
        for g in guides:
            if g['group'] != group: continue
            content += f'<article class="directory-card" data-guide-search="{esc((g["title"]+" "+g["scope"]).casefold())}"><p class="eyebrow">{len(g["featuredEpisodes"])} starting episodes</p><h3>{link("/cognitive-security/topic/"+g["slug"]+"/",g["title"])}</h3><p>{esc(g["scope"])}</p>'+link('/cognitive-security/topic/'+g['slug']+'/', 'Open guide →','text-link')+'</article>'
        content += '</div></section>'
    content += '<p id="no-guides" hidden>No guides match that search. Clear the search to see all 15.</p>'
    return shell('Topic Guides', 'Curated listening guides and evidence-linked starting points into the Cognitive Security Practitioner Discourse Map.', '/cognitive-security/topic/', content, True)


def compile_outputs(root: Path, payload: dict[str, Any] | None = None, quote_payload: dict[str, Any] | None = None, approvals: dict[str, Any] | None = None) -> tuple[dict[Path, bytes], dict[str, Any]]:
    corpus = Corpus(root)
    corpus.validate_lock(load(root / AUTHORING / 'source_lock.json'))
    payload = payload if payload is not None else load(root / AUTHORING / 'guides.json')
    quote_payload = quote_payload if quote_payload is not None else load(root / AUTHORING / 'quote_excerpts.json')
    approvals = approvals if approvals is not None else load(root / AUTHORING / 'quote_approvals.json')
    quotes = validate_quotes(corpus, quote_payload, approvals)
    validate_guides(corpus, payload, quotes)
    guides = payload['guides']; out = {}; reverse = defaultdict(set)
    directory = []; quote_missing = []
    for g in guides:
        out[SITE / g['slug'] / 'index.html'] = render_guide(corpus,g,quotes).encode('utf-8')
        directory.append({k:g[k] for k in ('guideId','slug','title','scope','group')})
        # Reverse tags mean 'selected in this guide', never transitive evidence support.
        refs = [(r['type'],r['id']) for rows in g['sections'].values() for r in rows]
        refs += [('episode',e['episodeId']) for e in g['featuredEpisodes']]
        for kind, identity in refs:
            reverse[kind+':'+identity].add(g['guideId'])
        for e in g['featuredEpisodes']:
            if not e['quoteId']:
                quote_missing.append({'guideId':g['guideId'],'episodeNumber':e['expectedEpisodeNumber'],'reason':'No excerpt approved for publication in this build; listening notes are cited separately.'})
    out[SITE / 'index.html'] = render_directory(guides).encode('utf-8')
    out[PUBLIC / 'guide_directory.json'] = encode({'schemaVersion':'1.0','guides':directory})
    out[PUBLIC / 'reverse_index.json'] = encode({'schemaVersion':'1.0','semantics':'explicit-curated-inclusion-not-analytical-support','entities':{k:sorted(v) for k,v in sorted(reverse.items())}})
    out[PUBLIC / 'quote_excerpts.json'] = encode(quote_payload)
    # Public authoring projection: pointers and editorial listening notes only.
    public_guides = []
    for g in guides:
        public_guides.append({'guideId':g['guideId'],'slug':g['slug'],'sections':{key:[{k:v for k,v in r.items() if k not in ('expectedName','sourceFieldSha256')} for r in refs] for key,refs in g['sections'].items()},'featuredEpisodes':[{k:v for k,v in e.items() if k not in ('expectedEpisodeNumber','summarySha256')} for e in g['featuredEpisodes']]})
    out[PUBLIC / 'topic_guides.json'] = encode({'schemaVersion':'1.0','membershipMethod':MEMBERSHIP,'unmappedAllowed':True,'guides':public_guides})
    manifest = {'schemaVersion':'1.0','methodVersion':METHOD,'membershipMethod':MEMBERSHIP,'files':{str(p.relative_to(PUBLIC)):{'sha256':sha(b),'bytes':len(b)} for p,b in out.items() if p.is_relative_to(PUBLIC)},'guideCount':len(guides),'quoteCount':len(quotes)}
    out[PUBLIC / 'manifest.json'] = encode(manifest)
    admitted_clusters = {key.split(':',1)[1] for key in reverse if key.startswith('cluster:')}
    report = {'guideCount':len(guides),'featuredEpisodePlacements':sum(len(g['featuredEpisodes']) for g in guides),'uniqueFeaturedEpisodes':len({e['episodeId'] for g in guides for e in g['featuredEpisodes']}),'selectedSourceCards':sum(len(refs) for g in guides for refs in g['sections'].values()),'approvedQuoteCount':len(quotes),'quoteOmissions':quote_missing,'unmappedClusterCount':len(set(corpus.records['cluster'])-admitted_clusters),'unmappedIsValid':True,'canonicalMethod':METHOD,'protectedFilesUnchanged':True,'outputHashes':{str(p):sha(b) for p,b in sorted(out.items())}}
    out[Path('docs/cognitive-security/topic-guides/BUILD_REPORT.json')] = encode(report)
    return out, report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check existing generated files without changing them')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve()
        out, report = compile_outputs(root)
        stale = [str(p) for p,b in out.items() if not (root/p).is_file() or (root/p).read_bytes()!=b]
        # Detect stale generated guide pages and supplemental JSONs, but never remove them implicitly.
        expected = set(out)
        extras = [str(p.relative_to(root)) for directory, glob in ((SITE,'*/index.html'),(PUBLIC,'*.json')) for p in (root/directory).glob(glob) if p.relative_to(root) not in expected]
        require(not extras, 'Unexpected generated files: '+', '.join(extras))
        if args.check:
            require(not stale, 'Generated files are missing or stale: '+', '.join(stale))
        else:
            for p,b in out.items():
                target = root/p; target.parent.mkdir(parents=True,exist_ok=True)
                tmp = target.with_suffix(target.suffix+'.tmp'); tmp.write_bytes(b);tmp.replace(target)
        print(f"Topic Guides: {report['guideCount']} guides, {report['selectedSourceCards']} selected source cards, {report['approvedQuoteCount']} approved excerpts; canonical sources unchanged.")
        return 0
    except (GuideError, KeyError, OSError, json.JSONDecodeError) as exc:
        print('Topic Guides validation failed: '+str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
