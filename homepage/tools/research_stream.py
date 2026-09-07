#!/usr/bin/env python3
"""Canonical PSYWERX research-item storage and public-stream projection.

Standard library only. The JSONL database is the source of truth; generated
public pages contain a deliberately small allowlist and never change editorial
decisions.
"""
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
CATEGORIES = (
    "behavioral-science",
    "technology-modeling",
    "operations-strategy",
    "application-analysis",
)
DECISIONS = ("pending", "publish", "hold", "reject")
HANDOFF_TOP_FIELDS = {"schemaVersion", "briefDate", "briefType", "items"}
HANDOFF_ITEM_FIELDS = {
    "sourceItemNumber",
    "primaryCategory",
    "categories",
    "questionAndWhy",
    "whatTheyDid",
    "whatTheyFound",
    "whatItMeans",
    "streamTitle",
    "streamSummary",
    "attribution",
    "sourceUrl",
    "sourcePublishedAt",
    "sourceKey",
    "sourceVerified",
    "briefDate",
    "briefType",
    "streamDecision",
}
CANONICAL_FIELDS = (
    "itemId",
    "sourceKey",
    "firstSeenBriefDate",
    "latestSeenBriefDate",
    "sourcePublishedAt",
    "primaryCategory",
    "categories",
    "questionAndWhy",
    "whatTheyDid",
    "whatTheyFound",
    "whatItMeans",
    "streamTitle",
    "streamSummary",
    "attribution",
    "sourceUrl",
    "sourceVerified",
    "streamDecision",
    "decisionDate",
    "publishedAt",
    "reviewRequired",
)
CONTENT_FIELDS = (
    "sourcePublishedAt",
    "primaryCategory",
    "categories",
    "questionAndWhy",
    "whatTheyDid",
    "whatTheyFound",
    "whatItMeans",
    "streamTitle",
    "streamSummary",
    "attribution",
    "sourceUrl",
    "sourceVerified",
)
PUBLIC_FIELDS = (
    "itemId",
    "streamTitle",
    "streamSummary",
    "attribution",
    "sourceUrl",
    "categories",
    "publishedAt",
)
DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
ITEM_ID_RE = re.compile(r"research-[0-9a-f]{20}")
TRACKING_QUERY_KEYS = {"fbclid", "gclid", "mc_cid", "mc_eid"}
SENSITIVE_QUERY_KEYS = {"api_key", "apikey", "key", "password", "secret", "signature", "token"}
NON_SOURCE_HOSTS = {"docs.google.com", "drive.google.com", "localhost"}


class ResearchStreamError(ValueError):
    """A validation or deterministic-update failure."""


def _require_exact_keys(value: dict, expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ResearchStreamError(f"{label} fields differ; missing={missing}, extra={extra}")


def _iso_date(value, label: str, *, nullable: bool = False):
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


def _text(value, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ResearchStreamError(f"{label} must be non-empty text")
    normalized = " ".join(value.split())
    if len(normalized) > 4000:
        raise ResearchStreamError(f"{label} is unexpectedly long")
    return normalized


def normalize_doi(value: str | None) -> str | None:
    """Return a lower-case bare DOI, or None when value is not a DOI form."""
    if not isinstance(value, str):
        return None
    candidate = value.strip()
    lowered = candidate.lower()
    if lowered.startswith("doi:"):
        candidate = candidate[4:].strip()
    else:
        try:
            parsed = urlsplit(candidate)
        except ValueError:
            parsed = None
        if parsed and parsed.scheme.lower() in ("http", "https") and (parsed.hostname or "").lower() in (
            "doi.org",
            "dx.doi.org",
        ):
            candidate = parsed.path.lstrip("/")
        elif lowered.startswith("10."):
            candidate = candidate
        else:
            return None
    candidate = candidate.strip().lower()
    return candidate if DOI_RE.fullmatch(candidate) else None


def normalize_url(value: str) -> str:
    """Normalize a public HTTPS source URL for stable identity comparisons."""
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
    if host in NON_SOURCE_HOSTS or host.endswith(".local"):
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
        if not key.lower().startswith("utm_") and key.lower() not in TRACKING_QUERY_KEYS
    ]
    if any(key.lower() in SENSITIVE_QUERY_KEYS or key.lower().startswith("x-amz-") for key, _ in query):
        raise ResearchStreamError("source URL query appears to contain credentials")
    query.sort()
    return urlunsplit(("https", netloc, path, urlencode(query, doseq=True), ""))


def normalize_source_identity(source_key: str, source_url: str) -> tuple[str, str]:
    """Normalize sourceKey and sourceUrl, preferring DOI identity when present."""
    url_doi = normalize_doi(source_url)
    key_doi = normalize_doi(source_key)
    if key_doi or url_doi:
        if key_doi and url_doi and key_doi != url_doi:
            raise ResearchStreamError("sourceKey DOI does not match sourceUrl DOI")
        doi = key_doi or url_doi
        normalized_url = f"https://doi.org/{doi}" if url_doi else normalize_url(source_url)
        return f"doi:{doi}", normalized_url
    normalized_url = normalize_url(source_url)
    normalized_key = normalize_url(source_key)
    return normalized_key, normalized_url


def item_id_for(source_key: str) -> str:
    digest = hashlib.sha256(source_key.encode("utf-8")).hexdigest()[:20]
    return f"research-{digest}"


def validate_handoff(payload) -> dict:
    """Strictly validate and normalize one Morning Brief machine handoff."""
    if not isinstance(payload, dict):
        raise ResearchStreamError("handoff must be one JSON object")
    _require_exact_keys(payload, HANDOFF_TOP_FIELDS, "handoff")
    if payload["schemaVersion"] != HANDOFF_SCHEMA:
        raise ResearchStreamError(f"schemaVersion must be {HANDOFF_SCHEMA}")
    brief_date = _iso_date(payload["briefDate"], "briefDate")
    if payload["briefType"] != "daily":
        raise ResearchStreamError("briefType must be daily")
    if not isinstance(payload["items"], list) or not payload["items"]:
        raise ResearchStreamError("items must be a non-empty array")

    numbers: set[int] = set()
    source_keys: set[str] = set()
    normalized_items = []
    for index, raw in enumerate(payload["items"], start=1):
        label = f"items[{index - 1}]"
        if not isinstance(raw, dict):
            raise ResearchStreamError(f"{label} must be an object")
        _require_exact_keys(raw, HANDOFF_ITEM_FIELDS, label)
        number = raw["sourceItemNumber"]
        if isinstance(number, bool) or not isinstance(number, int) or number < 1 or number in numbers:
            raise ResearchStreamError(f"{label}.sourceItemNumber must be a unique positive integer")
        numbers.add(number)
        primary = raw["primaryCategory"]
        categories = raw["categories"]
        if primary not in CATEGORIES:
            raise ResearchStreamError(f"{label}.primaryCategory is invalid")
        if (
            not isinstance(categories, list)
            or not categories
            or any(category not in CATEGORIES for category in categories)
            or len(categories) != len(set(categories))
            or primary not in categories
        ):
            raise ResearchStreamError(f"{label}.categories must be unique allowed IDs including primaryCategory")
        if raw["briefDate"] != brief_date or raw["briefType"] != "daily":
            raise ResearchStreamError(f"{label} brief provenance must match the handoff")
        if raw["streamDecision"] != "pending":
            raise ResearchStreamError(f"{label}.streamDecision must be pending")
        if not isinstance(raw["sourceVerified"], bool):
            raise ResearchStreamError(f"{label}.sourceVerified must be boolean")
        source_key, source_url = normalize_source_identity(raw["sourceKey"], raw["sourceUrl"])
        if source_key in source_keys:
            raise ResearchStreamError(f"handoff repeats normalized sourceKey {source_key}")
        source_keys.add(source_key)
        normalized_items.append(
            {
                "sourceItemNumber": number,
                "primaryCategory": primary,
                "categories": list(categories),
                "questionAndWhy": _text(raw["questionAndWhy"], f"{label}.questionAndWhy"),
                "whatTheyDid": _text(raw["whatTheyDid"], f"{label}.whatTheyDid"),
                "whatTheyFound": _text(raw["whatTheyFound"], f"{label}.whatTheyFound"),
                "whatItMeans": _text(raw["whatItMeans"], f"{label}.whatItMeans"),
                "streamTitle": _text(raw["streamTitle"], f"{label}.streamTitle"),
                "streamSummary": _text(raw["streamSummary"], f"{label}.streamSummary"),
                "attribution": _text(raw["attribution"], f"{label}.attribution"),
                "sourceUrl": source_url,
                "sourcePublishedAt": _iso_date(
                    raw["sourcePublishedAt"], f"{label}.sourcePublishedAt", nullable=True
                ),
                "sourceKey": source_key,
                "sourceVerified": raw["sourceVerified"],
                "briefDate": brief_date,
                "briefType": "daily",
                "streamDecision": "pending",
            }
        )
    return {
        "schemaVersion": HANDOFF_SCHEMA,
        "briefDate": brief_date,
        "briefType": "daily",
        "items": normalized_items,
    }


def extract_handoff(text: str) -> dict:
    """Read raw JSON or the final matching fenced JSON block from Markdown."""
    if not isinstance(text, str) or not text.strip():
        raise ResearchStreamError("input is empty")
    stripped = text.strip()
    try:
        raw = json.loads(stripped)
    except json.JSONDecodeError:
        raw = None
    if raw is not None:
        return validate_handoff(raw)

    fences = re.findall(r"```(?:json)?\s*\r?\n(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    matching = []
    parse_error = None
    for block in fences:
        if HANDOFF_SCHEMA not in block:
            continue
        try:
            candidate = json.loads(block.strip())
        except json.JSONDecodeError as exc:
            parse_error = exc
            continue
        if isinstance(candidate, dict) and candidate.get("schemaVersion") == HANDOFF_SCHEMA:
            matching.append(candidate)
    if not matching:
        if parse_error:
            raise ResearchStreamError(f"research-items fenced JSON is malformed: {parse_error.msg}")
        raise ResearchStreamError(f"no fenced {HANDOFF_SCHEMA} JSON object found")
    if len(matching) > 1:
        raise ResearchStreamError(f"multiple fenced {HANDOFF_SCHEMA} objects found")
    return validate_handoff(matching[0])


def validate_record(record: dict) -> dict:
    if not isinstance(record, dict):
        raise ResearchStreamError("database line must contain one object")
    _require_exact_keys(record, set(CANONICAL_FIELDS), "research item")
    if not isinstance(record["itemId"], str) or not ITEM_ID_RE.fullmatch(record["itemId"]):
        raise ResearchStreamError("itemId is invalid")
    source_key, source_url = normalize_source_identity(record["sourceKey"], record["sourceUrl"])
    if source_key != record["sourceKey"] or source_url != record["sourceUrl"]:
        raise ResearchStreamError("source identity is not canonical")
    if item_id_for(source_key) != record["itemId"]:
        raise ResearchStreamError("itemId does not match sourceKey")
    first = _iso_date(record["firstSeenBriefDate"], "firstSeenBriefDate")
    latest = _iso_date(record["latestSeenBriefDate"], "latestSeenBriefDate")
    if first > latest:
        raise ResearchStreamError("firstSeenBriefDate cannot follow latestSeenBriefDate")
    _iso_date(record["sourcePublishedAt"], "sourcePublishedAt", nullable=True)
    primary = record["primaryCategory"]
    categories = record["categories"]
    if primary not in CATEGORIES:
        raise ResearchStreamError("primaryCategory is invalid")
    if (
        not isinstance(categories, list)
        or not categories
        or any(category not in CATEGORIES for category in categories)
        or len(categories) != len(set(categories))
        or primary not in categories
    ):
        raise ResearchStreamError("categories are invalid")
    for field in (
        "questionAndWhy",
        "whatTheyDid",
        "whatTheyFound",
        "whatItMeans",
        "streamTitle",
        "streamSummary",
        "attribution",
    ):
        if _text(record[field], field) != record[field]:
            raise ResearchStreamError(f"{field} is not normalized")
    if not isinstance(record["sourceVerified"], bool):
        raise ResearchStreamError("sourceVerified must be boolean")
    decision = record["streamDecision"]
    if decision not in DECISIONS:
        raise ResearchStreamError("streamDecision is invalid")
    decision_date = _iso_date(record["decisionDate"], "decisionDate", nullable=True)
    published = _iso_date(record["publishedAt"], "publishedAt", nullable=True)
    if decision == "pending" and (decision_date is not None or published is not None):
        raise ResearchStreamError("pending records cannot have decisionDate or publishedAt")
    if decision == "publish" and (decision_date is None or published is None):
        raise ResearchStreamError("publish records require decisionDate and publishedAt")
    if decision in ("hold", "reject") and (decision_date is None or published is not None):
        raise ResearchStreamError(f"{decision} records require decisionDate and no publishedAt")
    if not isinstance(record["reviewRequired"], bool):
        raise ResearchStreamError("reviewRequired must be boolean")
    return record


def load_database(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records = []
    seen_keys = set()
    seen_ids = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            raise ResearchStreamError(f"blank JSONL line at {line_number}")
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ResearchStreamError(f"invalid JSON on database line {line_number}: {exc.msg}") from exc
        validate_record(record)
        if record["sourceKey"] in seen_keys or record["itemId"] in seen_ids:
            raise ResearchStreamError(f"duplicate source identity on database line {line_number}")
        seen_keys.add(record["sourceKey"])
        seen_ids.add(record["itemId"])
        records.append(record)
    return records


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def write_database(path: Path, records: list[dict]) -> None:
    ordered = sorted(records, key=lambda record: record["itemId"])
    for record in ordered:
        validate_record(record)
    lines = [
        json.dumps({field: record[field] for field in CANONICAL_FIELDS}, ensure_ascii=False, separators=(",", ":"))
        for record in ordered
    ]
    _atomic_write(path, "\n".join(lines) + ("\n" if lines else ""))


def _incoming_record(item: dict) -> dict:
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
        "streamDecision": "pending",
        "decisionDate": None,
        "publishedAt": None,
        "reviewRequired": False,
    }


def ingest_handoff(payload: dict, database_path: Path, *, dry_run: bool = False) -> dict:
    normalized = validate_handoff(payload)
    records = load_database(database_path)
    by_key = {record["sourceKey"]: record for record in records}
    report = {"added": [], "updated": [], "unchanged": [], "conflicts": [], "rejected": []}

    for item in normalized["items"]:
        incoming = _incoming_record(item)
        existing = by_key.get(incoming["sourceKey"])
        if existing is None:
            records.append(incoming)
            by_key[incoming["sourceKey"]] = incoming
            report["added"].append(incoming["itemId"])
            continue

        changed_fields = [field for field in CONTENT_FIELDS if existing[field] != incoming[field]]
        provenance_changed = False
        first_seen = min(existing["firstSeenBriefDate"], incoming["firstSeenBriefDate"])
        latest_seen = max(existing["latestSeenBriefDate"], incoming["latestSeenBriefDate"])
        if first_seen != existing["firstSeenBriefDate"] or latest_seen != existing["latestSeenBriefDate"]:
            existing["firstSeenBriefDate"] = first_seen
            existing["latestSeenBriefDate"] = latest_seen
            provenance_changed = True

        if not changed_fields:
            bucket = "updated" if provenance_changed else "unchanged"
            report[bucket].append(existing["itemId"])
            continue

        if existing["streamDecision"] != "pending":
            existing["reviewRequired"] = True
            report["conflicts"].append(
                {
                    "itemId": existing["itemId"],
                    "sourceKey": existing["sourceKey"],
                    "preservedDecision": existing["streamDecision"],
                    "changedFields": changed_fields,
                }
            )
            continue

        if incoming["latestSeenBriefDate"] < existing["latestSeenBriefDate"]:
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
    if not dry_run:
        write_database(database_path, records)
    return {
        "schemaVersion": HANDOFF_SCHEMA,
        "briefDate": normalized["briefDate"],
        "dryRun": dry_run,
        **{key: len(value) for key, value in report.items()},
        "details": report,
    }


def public_item(record: dict) -> dict:
    validate_record(record)
    return {field: record[field] for field in PUBLIC_FIELDS}


def generate_public_feed(database_path: Path, output_path: Path, *, page_size: int = 24) -> dict:
    if isinstance(page_size, bool) or not isinstance(page_size, int) or page_size < 1 or page_size > 100:
        raise ResearchStreamError("page_size must be between 1 and 100")
    records = [record for record in load_database(database_path) if record["streamDecision"] == "publish"]
    records.sort(key=lambda record: (record["publishedAt"], record["itemId"]), reverse=True)
    items = [public_item(record) for record in records]
    pages = [items[index : index + page_size] for index in range(0, len(items), page_size)] or [[]]
    page_dir = output_path.parent / "public_feed_pages"
    expected_page_files = set()

    def envelope(page_number: int, page_items: list[dict]) -> dict:
        has_next = page_number < len(pages)
        return {
            "schemaVersion": PUBLIC_SCHEMA,
            "page": page_number,
            "pageSize": page_size,
            "totalItems": len(items),
            "items": page_items,
            "nextPage": f"public_feed_pages/page-{page_number + 1:04d}.json" if has_next else None,
        }

    _atomic_write(output_path, json.dumps(envelope(1, pages[0]), ensure_ascii=False, indent=2) + "\n")
    for page_number, page_items in enumerate(pages[1:], start=2):
        path = page_dir / f"page-{page_number:04d}.json"
        expected_page_files.add(path)
        _atomic_write(path, json.dumps(envelope(page_number, page_items), ensure_ascii=False, indent=2) + "\n")
    if page_dir.exists():
        for path in page_dir.glob("page-*.json"):
            if path not in expected_page_files:
                path.unlink()
        try:
            page_dir.rmdir()
        except OSError:
            pass
    return envelope(1, pages[0])


def review_item(database_path: Path, item_id: str, decision: str, decision_date: str) -> dict:
    if decision not in ("publish", "hold", "reject"):
        raise ResearchStreamError("decision must be publish, hold, or reject")
    _iso_date(decision_date, "decision date")
    records = load_database(database_path)
    matches = [record for record in records if record["itemId"] == item_id]
    if not matches:
        raise ResearchStreamError(f"unknown itemId: {item_id}")
    record = matches[0]
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
