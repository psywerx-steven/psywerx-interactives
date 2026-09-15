#!/usr/bin/env python3
"""Canonical PSYWERX research database, brief manifests, and public projections."""
from __future__ import annotations

import hashlib
import ipaddress
import json
import os
import re
import tempfile
from datetime import date
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

HANDOFF_SCHEMA = "psywerx-research-items-v1"
PUBLIC_SCHEMA = "psywerx-public-research-stream-v1"
BRIEF_MANIFEST_SCHEMA = "psywerx-brief-manifest-v1"
EXPLORER_SCHEMA = "psywerx-research-explorer-v1"
CATEGORIES = ("behavioral-science", "technology-modeling", "operations-strategy", "application-analysis")
DECISIONS = ("publish", "hold", "reject")
HANDOFF_TOP_FIELDS = {"schemaVersion", "briefDate", "briefType", "items"}
HANDOFF_ITEM_FIELDS = {
    "sourceItemNumber", "primaryCategory", "categories", "questionAndWhy", "whatTheyDid",
    "whatTheyFound", "whatItMeans", "streamTitle", "streamSummary", "attribution",
    "sourceUrl", "sourcePublishedAt", "sourceKey", "sourceVerified", "briefDate",
    "briefType", "streamDecision",
}
CANONICAL_FIELDS = (
    "itemId", "sourceKey", "firstSeenBriefDate", "latestSeenBriefDate", "sourcePublishedAt",
    "primaryCategory", "categories", "questionAndWhy", "whatTheyDid", "whatTheyFound",
    "whatItMeans", "streamTitle", "streamSummary", "attribution", "sourceUrl",
    "sourceVerified", "streamDecision", "decisionDate", "publishedAt", "reviewRequired",
)
CONTENT_FIELDS = (
    "sourcePublishedAt", "primaryCategory", "categories", "questionAndWhy", "whatTheyDid",
    "whatTheyFound", "whatItMeans", "streamTitle", "streamSummary", "attribution",
    "sourceUrl", "sourceVerified",
)
PUBLIC_FIELDS = (
    "itemId", "streamTitle", "streamSummary", "attribution", "sourceUrl", "categories",
    "sourcePublishedAt", "dateAdded",
)
EXPLORER_FIELDS = (
    "itemId", "streamTitle", "streamSummary", "attribution", "sourceUrl", "sourcePublishedAt",
    "dateAdded", "latestSeenBriefDate", "primaryCategory", "categories", "questionAndWhy",
    "whatTheyDid", "whatTheyFound", "whatItMeans",
)
DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.I)
ITEM_ID_RE = re.compile(r"research-[0-9a-f]{20}")
TRACKING = {"fbclid", "gclid", "mc_cid", "mc_eid"}
SENSITIVE = {"api_key", "apikey", "key", "password", "secret", "signature", "token"}
NON_SOURCE = {"docs.google.com", "drive.google.com", "localhost"}


class ResearchStreamError(ValueError):
    pass


def _exact(value, expected, label):
    if not isinstance(value, dict):
        raise ResearchStreamError(f"{label} must be an object")
    if set(value) != set(expected):
        raise ResearchStreamError(
            f"{label} fields differ; missing={sorted(set(expected)-set(value))}, "
            f"extra={sorted(set(value)-set(expected))}"
        )


def _date(value, label, nullable=False):
    if value is None and nullable:
        return None
    if not isinstance(value, str):
        raise ResearchStreamError(f"{label} must be an ISO date string")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ResearchStreamError(f"{label} must be YYYY-MM-DD") from exc
    if parsed.isoformat() != value:
        raise ResearchStreamError(f"{label} must be canonical YYYY-MM-DD")
    return value


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ResearchStreamError(f"{label} must be non-empty text")
    value = " ".join(value.split())
    if len(value) > 4000:
        raise ResearchStreamError(f"{label} is unexpectedly long")
    return value


def normalize_doi(value):
    if not isinstance(value, str):
        return None
    candidate = value.strip()
    low = candidate.lower()
    if low.startswith("doi:"):
        candidate = candidate[4:].strip()
    else:
        try:
            parsed = urlsplit(candidate)
        except ValueError:
            parsed = None
        if parsed and parsed.scheme.lower() in ("http", "https") and (parsed.hostname or "").lower() in ("doi.org", "dx.doi.org"):
            candidate = parsed.path.lstrip("/")
        elif not low.startswith("10."):
            return None
    candidate = candidate.strip().lower()
    return candidate if DOI_RE.fullmatch(candidate) else None


def normalize_url(value):
    if not isinstance(value, str):
        raise ResearchStreamError("source URL must be text")
    try:
        parsed = urlsplit(value.strip())
        port = parsed.port
    except ValueError as exc:
        raise ResearchStreamError("source URL is invalid") from exc
    if parsed.scheme.lower() != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ResearchStreamError("source URL must be public HTTPS without credentials")
    host = parsed.hostname.lower()
    if host in NON_SOURCE or host.endswith(".local"):
        raise ResearchStreamError("source URL cannot be a private document or local host")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address is not None and not address.is_global:
        raise ResearchStreamError("source URL cannot use a non-public IP address")
    netloc = host if port in (None, 443) else f"{host}:{port}"
    path = re.sub(r"/{2,}", "/", parsed.path or "/")
    if path != "/":
        path = path.rstrip("/")
    query = [
        (key, val)
        for key, val in parse_qsl(parsed.query, keep_blank_values=True)
        if not key.lower().startswith("utm_") and key.lower() not in TRACKING
    ]
    if any(key.lower() in SENSITIVE or key.lower().startswith("x-amz-") for key, _ in query):
        raise ResearchStreamError("source URL query appears to contain credentials")
    query.sort()
    return urlunsplit(("https", netloc, path, urlencode(query, doseq=True), ""))


def normalize_source_identity(key, url):
    key_doi, url_doi = normalize_doi(key), normalize_doi(url)
    if key_doi or url_doi:
        if key_doi and url_doi and key_doi != url_doi:
            raise ResearchStreamError("sourceKey DOI does not match sourceUrl DOI")
        doi = key_doi or url_doi
        return f"doi:{doi}", f"https://doi.org/{doi}" if url_doi else normalize_url(url)
    return normalize_url(key), normalize_url(url)


def item_id_for(key):
    return "research-" + hashlib.sha256(key.encode()).hexdigest()[:20]


def validate_handoff(payload):
    _exact(payload, HANDOFF_TOP_FIELDS, "handoff")
    if payload["schemaVersion"] != HANDOFF_SCHEMA:
        raise ResearchStreamError(f"schemaVersion must be {HANDOFF_SCHEMA}")
    brief_date = _date(payload["briefDate"], "briefDate")
    if payload["briefType"] != "daily":
        raise ResearchStreamError("briefType must be daily")
    if not isinstance(payload["items"], list) or not payload["items"]:
        raise ResearchStreamError("items must be a non-empty array")

    numbers, keys, items = set(), set(), []
    for index, raw in enumerate(payload["items"]):
        label = f"items[{index}]"
        _exact(raw, HANDOFF_ITEM_FIELDS, label)
        source_number = raw["sourceItemNumber"]
        if isinstance(source_number, bool) or not isinstance(source_number, int) or source_number < 1 or source_number in numbers:
            raise ResearchStreamError(f"{label}.sourceItemNumber must be a unique positive integer")
        numbers.add(source_number)
        primary, categories = raw["primaryCategory"], raw["categories"]
        if (
            primary not in CATEGORIES or not isinstance(categories, list) or not categories
            or primary not in categories or len(categories) != len(set(categories))
            or any(category not in CATEGORIES for category in categories)
        ):
            raise ResearchStreamError(f"{label}.categories are invalid")
        if raw["briefDate"] != brief_date or raw["briefType"] != "daily":
            raise ResearchStreamError(f"{label} brief provenance must match the handoff")
        if raw["streamDecision"] not in ("pending", "publish"):
            raise ResearchStreamError(f"{label}.streamDecision must be publish (legacy pending is accepted for archived handoffs)")
        if not isinstance(raw["sourceVerified"], bool):
            raise ResearchStreamError(f"{label}.sourceVerified must be boolean")

        source_key, source_url = normalize_source_identity(raw["sourceKey"], raw["sourceUrl"])
        if source_key in keys:
            raise ResearchStreamError(f"handoff repeats normalized sourceKey {source_key}")
        keys.add(source_key)
        item = {field: raw[field] for field in HANDOFF_ITEM_FIELDS}
        item.update(sourceKey=source_key, sourceUrl=source_url)
        for field in ("questionAndWhy", "whatTheyDid", "whatTheyFound", "whatItMeans", "streamTitle", "streamSummary", "attribution"):
            item[field] = _text(item[field], f"{label}.{field}")
        item["streamDecision"] = "publish"
        item["sourcePublishedAt"] = _date(item["sourcePublishedAt"], f"{label}.sourcePublishedAt", True)
        item["categories"] = list(categories)
        items.append(item)
    return {"schemaVersion": HANDOFF_SCHEMA, "briefDate": brief_date, "briefType": "daily", "items": items}


def extract_handoff(text):
    if not isinstance(text, str) or not text.strip():
        raise ResearchStreamError("input is empty")
    try:
        raw = json.loads(text.strip())
    except json.JSONDecodeError:
        raw = None
    if raw is not None:
        return validate_handoff(raw)
    matches, malformed = [], False
    for block in re.findall(r"```(?:json)?\s*\r?\n(.*?)```", text, flags=re.I | re.S):
        if HANDOFF_SCHEMA not in block:
            continue
        try:
            candidate = json.loads(block.strip())
        except json.JSONDecodeError:
            malformed = True
            continue
        if isinstance(candidate, dict) and candidate.get("schemaVersion") == HANDOFF_SCHEMA:
            matches.append(candidate)
    if len(matches) > 1:
        raise ResearchStreamError(f"multiple fenced {HANDOFF_SCHEMA} objects found")
    if not matches:
        raise ResearchStreamError("research-items fenced JSON is malformed" if malformed else f"no fenced {HANDOFF_SCHEMA} JSON object found")
    return validate_handoff(matches[0])


def validate_record(record):
    _exact(record, CANONICAL_FIELDS, "research item")
    key, url = normalize_source_identity(record["sourceKey"], record["sourceUrl"])
    if key != record["sourceKey"] or url != record["sourceUrl"]:
        raise ResearchStreamError("source identity is not canonical")
    if not isinstance(record["itemId"], str) or not ITEM_ID_RE.fullmatch(record["itemId"]):
        raise ResearchStreamError("itemId is invalid")
    first = _date(record["firstSeenBriefDate"], "firstSeenBriefDate")
    latest = _date(record["latestSeenBriefDate"], "latestSeenBriefDate")
    if first > latest:
        raise ResearchStreamError("firstSeenBriefDate cannot follow latestSeenBriefDate")
    _date(record["sourcePublishedAt"], "sourcePublishedAt", True)
    primary, categories = record["primaryCategory"], record["categories"]
    if (
        primary not in CATEGORIES or not isinstance(categories, list) or not categories
        or primary not in categories or len(categories) != len(set(categories))
        or any(category not in CATEGORIES for category in categories)
    ):
        raise ResearchStreamError("categories are invalid")
    for field in ("questionAndWhy", "whatTheyDid", "whatTheyFound", "whatItMeans", "streamTitle", "streamSummary", "attribution"):
        if _text(record[field], field) != record[field]:
            raise ResearchStreamError(f"{field} is not normalized")
    if not isinstance(record["sourceVerified"], bool):
        raise ResearchStreamError("sourceVerified must be boolean")
    decision = record["streamDecision"]
    if decision not in DECISIONS:
        raise ResearchStreamError("streamDecision is invalid")
    if decision == "publish" and record["sourceVerified"] is not True:
        raise ResearchStreamError("publish records require sourceVerified: true")
    decision_date = _date(record["decisionDate"], "decisionDate", True)
    published_at = _date(record["publishedAt"], "publishedAt", True)
    if decision == "publish" and (decision_date is None or published_at is None):
        raise ResearchStreamError("publish records require decisionDate and publishedAt")
    if decision in ("hold", "reject") and (decision_date is None or published_at is not None):
        raise ResearchStreamError(f"{decision} records require decisionDate and no publishedAt")
    if not isinstance(record["reviewRequired"], bool):
        raise ResearchStreamError("reviewRequired must be boolean")
    return record


def _read(path):
    if not path.exists():
        return []
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            raise ResearchStreamError(f"blank JSONL line in {path.name} at {line_number}")
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ResearchStreamError(f"invalid JSON in {path.name} line {line_number}: {exc.msg}") from exc
        records.append(validate_record(record))
    return records


def database_files(path):
    archive = path.parent / "archive"
    return [path] + (sorted(archive.glob("*.jsonl")) if archive.exists() else [])


def load_database(path):
    records, keys, ids = [], set(), set()
    for source in database_files(path):
        for record in _read(source):
            if record["sourceKey"] in keys or record["itemId"] in ids:
                raise ResearchStreamError(f"duplicate source identity across research database shards: {record['sourceKey']}")
            keys.add(record["sourceKey"])
            ids.add(record["itemId"])
            records.append(record)
    return records


def _atomic(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def write_database(path, records):
    archive = path.parent / "archive"
    origins = {}
    shards = sorted(archive.glob("*.jsonl")) if archive.exists() else []
    for shard in shards:
        for record in _read(shard):
            origins[record["sourceKey"]] = shard
    groups = {path: []}
    groups.update({shard: [] for shard in shards})
    for record in records:
        validate_record(record)
        groups.setdefault(origins.get(record["sourceKey"], path), []).append(record)
    for target, group in groups.items():
        lines = [
            json.dumps({field: record[field] for field in CANONICAL_FIELDS}, ensure_ascii=False, separators=(",", ":"))
            for record in sorted(group, key=lambda value: value["itemId"])
        ]
        _atomic(target, "\n".join(lines) + ("\n" if lines else ""))


def _incoming_record(item):
    return {
        "itemId": item_id_for(item["sourceKey"]),
        "sourceKey": item["sourceKey"],
        "firstSeenBriefDate": item["briefDate"],
        "latestSeenBriefDate": item["briefDate"],
        "sourcePublishedAt": item["sourcePublishedAt"],
        "primaryCategory": item["primaryCategory"],
        "categories": item["categories"],
        "questionAndWhy": item["questionAndWhy"],
        "whatTheyDid": item["whatTheyDid"],
        "whatTheyFound": item["whatTheyFound"],
        "whatItMeans": item["whatItMeans"],
        "streamTitle": item["streamTitle"],
        "streamSummary": item["streamSummary"],
        "attribution": item["attribution"],
        "sourceUrl": item["sourceUrl"],
        "sourceVerified": item["sourceVerified"],
        "streamDecision": "publish" if item["sourceVerified"] else "hold",
        "decisionDate": item["briefDate"],
        "publishedAt": item["briefDate"] if item["sourceVerified"] else None,
        "reviewRequired": False,
    }


def _manifest_for(payload, by_key):
    item_ids = [by_key[item["sourceKey"]]["itemId"] for item in payload["items"]]
    category_counts = {category: 0 for category in CATEGORIES}
    for item in payload["items"]:
        category_counts[item["primaryCategory"]] += 1
    return {
        "schemaVersion": BRIEF_MANIFEST_SCHEMA,
        "briefDate": payload["briefDate"],
        "briefType": "daily",
        "totalItems": len(item_ids),
        "categoryCounts": category_counts,
        "itemIds": item_ids,
    }


def ingest_handoff(payload, database_path, *, dry_run=False):
    payload = validate_handoff(payload)
    records = load_database(database_path)
    by_key = {record["sourceKey"]: record for record in records}
    report = {"added": [], "updated": [], "unchanged": [], "conflicts": [], "rejected": []}

    for item in payload["items"]:
        incoming = _incoming_record(item)
        existing = by_key.get(incoming["sourceKey"])
        if existing is None:
            records.append(incoming)
            by_key[incoming["sourceKey"]] = incoming
            report["added"].append(incoming["itemId"])
            continue

        changed = [field for field in CONTENT_FIELDS if existing[field] != incoming[field]]
        old_latest = existing["latestSeenBriefDate"]
        first = min(existing["firstSeenBriefDate"], item["briefDate"])
        latest = max(old_latest, item["briefDate"])
        provenance_changed = first != existing["firstSeenBriefDate"] or latest != old_latest
        existing["firstSeenBriefDate"] = first
        existing["latestSeenBriefDate"] = latest

        if not changed:
            report["updated" if provenance_changed else "unchanged"].append(existing["itemId"])
            continue
        if existing["streamDecision"] in ("hold", "reject"):
            existing["reviewRequired"] = True
            report["conflicts"].append({
                "itemId": existing["itemId"],
                "sourceKey": existing["sourceKey"],
                "preservedDecision": existing["streamDecision"],
                "changedFields": changed,
            })
            continue
        if item["briefDate"] < old_latest:
            report["updated" if provenance_changed else "unchanged"].append(existing["itemId"])
            continue
        for field in CONTENT_FIELDS:
            if field == "sourceVerified":
                existing[field] = existing[field] or incoming[field]
            elif field == "sourcePublishedAt" and incoming[field] is None and existing[field] is not None:
                continue
            else:
                existing[field] = incoming[field]
        report["updated"].append(existing["itemId"])

    for record in records:
        validate_record(record)
    manifest = _manifest_for(payload, by_key)
    if not dry_run:
        write_database(database_path, records)
        manifest_path = database_path.parent / "briefs" / f"{payload['briefDate']}.json"
        _atomic(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

    return {
        "schemaVersion": HANDOFF_SCHEMA,
        "briefDate": payload["briefDate"],
        "dryRun": dry_run,
        **{key: len(value) for key, value in report.items()},
        "manifest": manifest,
        "details": report,
    }


def is_public(record):
    validate_record(record)
    return record["sourceVerified"] is True and record["streamDecision"] == "publish"


def public_item(record):
    return {
        "itemId": record["itemId"],
        "streamTitle": record["streamTitle"],
        "streamSummary": record["streamSummary"],
        "attribution": record["attribution"],
        "sourceUrl": record["sourceUrl"],
        "categories": record["categories"],
        "sourcePublishedAt": record["sourcePublishedAt"],
        "dateAdded": record["firstSeenBriefDate"],
    }


def explorer_item(record):
    return {
        "itemId": record["itemId"],
        "streamTitle": record["streamTitle"],
        "streamSummary": record["streamSummary"],
        "attribution": record["attribution"],
        "sourceUrl": record["sourceUrl"],
        "sourcePublishedAt": record["sourcePublishedAt"],
        "dateAdded": record["firstSeenBriefDate"],
        "latestSeenBriefDate": record["latestSeenBriefDate"],
        "primaryCategory": record["primaryCategory"],
        "categories": record["categories"],
        "questionAndWhy": record["questionAndWhy"],
        "whatTheyDid": record["whatTheyDid"],
        "whatTheyFound": record["whatTheyFound"],
        "whatItMeans": record["whatItMeans"],
    }


def generate_public_feed(database_path, output_path, *, page_size=24):
    if isinstance(page_size, bool) or not isinstance(page_size, int) or not 1 <= page_size <= 100:
        raise ResearchStreamError("page_size must be between 1 and 100")
    records = [record for record in load_database(database_path) if is_public(record)]
    records.sort(key=lambda record: (record["firstSeenBriefDate"], record["sourcePublishedAt"] or "", record["itemId"]), reverse=True)
    items = [public_item(record) for record in records]
    pages = [items[index:index + page_size] for index in range(0, len(items), page_size)] or [[]]
    page_dir = output_path.parent / "public_feed_pages"
    expected = set()

    def envelope(number, values):
        return {
            "schemaVersion": PUBLIC_SCHEMA,
            "page": number,
            "pageSize": page_size,
            "totalItems": len(items),
            "items": values,
            "nextPage": f"public_feed_pages/page-{number + 1:04d}.json" if number < len(pages) else None,
        }

    _atomic(output_path, json.dumps(envelope(1, pages[0]), ensure_ascii=False, indent=2) + "\n")
    for number, values in enumerate(pages[1:], 2):
        target = page_dir / f"page-{number:04d}.json"
        expected.add(target)
        _atomic(target, json.dumps(envelope(number, values), ensure_ascii=False, indent=2) + "\n")
    if page_dir.exists():
        for target in page_dir.glob("page-*.json"):
            if target not in expected:
                target.unlink()
        try:
            page_dir.rmdir()
        except OSError:
            pass
    return envelope(1, pages[0])


def generate_explorer_data(database_path, output_path):
    records = [record for record in load_database(database_path) if is_public(record)]
    records.sort(key=lambda record: (record["firstSeenBriefDate"], record["sourcePublishedAt"] or "", record["itemId"]), reverse=True)
    items = [explorer_item(record) for record in records]
    visible_ids = {item["itemId"] for item in items}
    manifests = []
    brief_dir = database_path.parent / "briefs"
    if brief_dir.exists():
        for path in sorted(brief_dir.glob("*.json"), reverse=True):
            raw = json.loads(path.read_text(encoding="utf-8"))
            if raw.get("schemaVersion") != BRIEF_MANIFEST_SCHEMA:
                raise ResearchStreamError(f"unexpected brief manifest schema in {path.name}")
            item_ids = [item_id for item_id in raw.get("itemIds", []) if item_id in visible_ids]
            if not item_ids:
                continue
            counts = {category: 0 for category in CATEGORIES}
            lookup = {item["itemId"]: item for item in items}
            for item_id in item_ids:
                counts[lookup[item_id]["primaryCategory"]] += 1
            manifests.append({
                "briefDate": raw["briefDate"],
                "briefType": "daily",
                "totalItems": len(item_ids),
                "categoryCounts": counts,
                "itemIds": item_ids,
            })
    payload = {
        "schemaVersion": EXPLORER_SCHEMA,
        "generatedAt": date.today().isoformat(),
        "totalItems": len(items),
        "items": items,
        "briefs": manifests,
    }
    _atomic(output_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return payload


def review_item(database_path, item_id, decision, decision_date):
    if decision not in ("publish", "hold", "reject"):
        raise ResearchStreamError("decision must be publish, hold, or reject")
    _date(decision_date, "decision date")
    records = load_database(database_path)
    matches = [record for record in records if record["itemId"] == item_id]
    if not matches:
        raise ResearchStreamError(f"unknown itemId: {item_id}")
    record = matches[0]
    if decision == "publish" and record["sourceVerified"] is not True:
        raise ResearchStreamError("sourceVerified must be true before publish")
    previous = record["streamDecision"]
    record["streamDecision"] = decision
    record["decisionDate"] = decision_date
    record["publishedAt"] = decision_date if decision == "publish" else None
    record["reviewRequired"] = False
    write_database(database_path, records)
    return {
        "itemId": item_id,
        "previousDecision": previous,
        "streamDecision": decision,
        "decisionDate": decision_date,
    }
