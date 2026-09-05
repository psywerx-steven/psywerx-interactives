"""Deterministic presentation and episode-discovery overlays.

The functions in this module consume only the shipped public Cognitive Security
aggregates and a frozen public metadata projection.  They do not read transcript
text, item-level evidence, or network resources.
"""

from __future__ import annotations

import hashlib
import html
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import urlparse


SCHEMA_VERSION = "1.0"
PRIMARY_ITEM_MINIMUM = 2
PROMINENCE_SHARE_MINIMUM = 0.05
MAIN_TOPIC_DISPLAY_LIMIT = 6
SIMILARITY_MINIMUM = 0.15
SIMILARITY_SHARED_TOPIC_MINIMUM = 2
SIMILARITY_RESULT_LIMIT = 6
OFFICIAL_HOST = "information-professionals.org"
DISCOVERY_FILES = (
    "episode_metadata.json",
    "episode_discovery.json",
    "topic_episode_index.json",
    "similarity_data.json",
    "presentation_copy.json",
)
CORE_COUNT_INVARIANTS = {
    "categoryCount": 7,
    "familyCount": 50,
    "clusterCount": 127,
    "themeCount": 11,
    "tensionCount": 20,
    "narrativeCount": 5,
    "categoryFindingCount": 64,
    "scenarioCount": 6,
    "publicReleaseCount": 242,
    "canonicalContentUnitCount": 241,
    "canonicalItemCount": 12933,
    "canonicalFocalItemCount": 9822,
    "canonicalContextualItemCount": 3111,
}
METADATA_FIELDS = frozenset(
    {"episodeId", "publishedAt", "guests", "officialEpisodeUrl"}
)
GOVERNED_TITLE_EXCEPTIONS = {
    (28, 9621): "The catalog and publisher spell the guest surname Mushtare/Mushatare differently; the remaining title is exact.",
    (131, 13574): "The catalog contains the one-character Ghost Tean/Team transcription error; the remaining title is exact.",
    (159, 14768): "The catalog and publisher spell the guest surname Schiovani/Schiavoni differently; the remaining title is exact.",
}


class DiscoveryError(ValueError):
    """Raised when an input or generated discovery artifact is invalid."""


@dataclass(frozen=True)
class TopicCount:
    topic_id: str
    primary: int
    secondary: int
    weighted: int


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def json_bytes(payload: Any) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
        + "\n"
    ).encode("utf-8")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json_bytes(payload))


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise DiscoveryError(message)


def _normalized_title(value: str) -> str:
    value = html.unescape(value).replace("：", ":").replace("／", "/")
    value = re.sub(r"^#?\d+\s*[:\-–—]?\s*", "", value.strip())
    value = value.casefold()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def _token_prefix(left: tuple[str, ...], right: tuple[str, ...]) -> bool:
    shorter, longer = (left, right) if len(left) <= len(right) else (right, left)
    return len(shorter) >= 2 and longer[: len(shorter)] == shorter


def _split_on(tokens: tuple[str, ...]) -> tuple[tuple[str, ...], tuple[str, ...]] | None:
    try:
        index = tokens.index("on")
    except ValueError:
        return None
    if index == 0 or index == len(tokens) - 1:
        return None
    return tokens[:index], tokens[index + 1 :]


def _guest_names_compatible(left: tuple[str, ...], right: tuple[str, ...]) -> bool:
    if left == right:
        return True
    left_set = set(left)
    right_set = set(right)
    if left_set <= right_set or right_set <= left_set:
        return True
    return bool(
        len(left) == 2
        and len(right) == 2
        and left[-1] == right[-1]
        and left[0][0] == right[0][0]
    )


def _title_compatibility(catalog_title: str, official_title: str) -> dict[str, Any]:
    catalog_normalized = _normalized_title(catalog_title)
    official_normalized = _normalized_title(official_title)
    result = {
        "status": "conflict",
        "method": "material-title-conflict",
        "catalogNormalizedTitle": catalog_normalized,
        "officialNormalizedTitle": official_normalized,
    }
    if not catalog_normalized or not official_normalized:
        return result
    if catalog_normalized == official_normalized:
        result.update(status="compatible", method="exact-normalized-title")
        return result

    catalog_tokens = tuple(catalog_normalized.split())
    official_tokens = tuple(official_normalized.split())
    if _token_prefix(catalog_tokens, official_tokens):
        result.update(status="compatible", method="normalized-title-prefix")
        return result

    catalog_parts = _split_on(catalog_tokens)
    official_parts = _split_on(official_tokens)
    if catalog_parts and official_parts:
        catalog_guests, catalog_topic = catalog_parts
        official_guests, official_topic = official_parts
        topic_compatible = catalog_topic == official_topic or _token_prefix(
            catalog_topic, official_topic
        )
        if topic_compatible and _guest_names_compatible(catalog_guests, official_guests):
            result.update(status="compatible", method="structured-guest-and-topic")
    return result


def _official_number(title: str) -> int | None:
    match = re.match(r"^#(\d+)\b", html.unescape(title).strip())
    return int(match.group(1)) if match else None


def _guest_line(title: str) -> list[str] | None:
    match = re.match(r"^#\d+\s+(.+?)\s+on\s+.+$", html.unescape(title).strip())
    if not match:
        return None
    candidate = re.sub(r"\s+", " ", match.group(1)).strip(" :-")
    if not candidate or candidate.casefold().startswith(("bonus", "the cognitive")):
        return None
    return [candidate]


def _official_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and parsed.hostname == OFFICIAL_HOST


def freeze_episode_metadata(
    *,
    core_dir: Path,
    cache_dir: Path,
    public_output: Path,
    private_audit_output: Path,
    retrieved_at: str,
) -> dict[str, Any]:
    """Match cached official WordPress records to the public release catalog.

    This intentionally does not perform HTTP requests.  Acquisition stays a
    separate, explicit step; this function freezes and audits an existing cache.
    """

    try:
        date.fromisoformat(retrieved_at)
    except ValueError as exc:
        raise DiscoveryError("retrieved_at must be an ISO date") from exc

    episodes = load_json(core_dir / "episodes.json")
    pages = sorted(cache_dir.glob("podcasts-page-*.json"))
    _assert(bool(pages), "No cached official publisher pages were found.")
    posts: list[dict[str, Any]] = []
    for page in pages:
        payload = load_json(page)
        _assert(isinstance(payload, list), f"{page.name} is not a record list")
        posts.extend(payload)

    by_number: dict[int, dict[str, Any]] = {}
    by_normalized_title: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for post in posts:
        official_title = html.unescape(post.get("title", {}).get("rendered", "")).strip()
        number = _official_number(official_title)
        if number is not None:
            _assert(number not in by_number, f"Duplicate official episode number {number}")
            by_number[number] = post
        by_normalized_title[_normalized_title(official_title)].append(post)

    public_records: list[dict[str, Any]] = []
    audit_records: list[dict[str, Any]] = []
    matched_post_ids: set[int] = set()
    for episode in sorted(episodes, key=lambda item: item["episodeId"]):
        episode_id = episode["episodeId"]
        number = episode.get("parsedEpisodeNumber")
        match: dict[str, Any] | None = None
        method: str | None = None
        number_candidate: dict[str, Any] | None = None
        title_compatibility: dict[str, Any] | None = None
        unresolved_reason = "No unique official publisher record matched without guessing."
        if isinstance(number, int) and number > 0:
            number_candidate = by_number.get(number)
            if number_candidate is not None:
                candidate_title = html.unescape(
                    number_candidate.get("title", {}).get("rendered", "")
                ).strip()
                title_compatibility = _title_compatibility(
                    episode["episodeTitle"], candidate_title
                )
                exception_reason = GOVERNED_TITLE_EXCEPTIONS.get(
                    (number, number_candidate.get("id"))
                )
                if title_compatibility["status"] == "compatible":
                    match = number_candidate
                    method = (
                        "episode-number-and-exact-normalized-title"
                        if title_compatibility["method"] == "exact-normalized-title"
                        else "episode-number-and-compatible-title"
                    )
                elif exception_reason:
                    title_compatibility.update(
                        status="compatible",
                        method="governed-title-exception",
                        exceptionReason=exception_reason,
                    )
                    match = number_candidate
                    method = "episode-number-and-governed-title-exception"
                else:
                    unresolved_reason = (
                        "Official episode number matched, but title compatibility "
                        "was not established; no metadata was published."
                    )
        if match is None and number_candidate is None:
            candidates = by_normalized_title.get(_normalized_title(episode["episodeTitle"]), [])
            candidates = [item for item in candidates if item["id"] not in matched_post_ids]
            if len(candidates) == 1:
                match = candidates[0]
                method = "exact-normalized-title"
                title_compatibility = _title_compatibility(
                    episode["episodeTitle"],
                    html.unescape(match.get("title", {}).get("rendered", "")).strip(),
                )

        if match is None:
            public_records.append(
                {
                    "episodeId": episode_id,
                    "publishedAt": None,
                    "guests": None,
                    "officialEpisodeUrl": None,
                }
            )
            audit_record = {
                "episodeId": episode_id,
                "episodeTitle": episode["episodeTitle"],
                "matchMethod": None,
                "titleCompatibility": title_compatibility,
                "retrievedAt": retrieved_at,
                "sourceFields": {},
                "unresolvedReason": unresolved_reason,
            }
            if number_candidate is not None:
                audit_record.update(
                    officialCandidatePostId=number_candidate.get("id"),
                    officialCandidateTitle=html.unescape(
                        number_candidate.get("title", {}).get("rendered", "")
                    ).strip(),
                )
            audit_records.append(audit_record)
            continue

        matched_post_ids.add(match["id"])
        official_title = html.unescape(match["title"]["rendered"]).strip()
        link = match.get("link", "")
        _assert(_official_url(link), f"Unapproved official host for {episode_id}")
        published_at = str(match.get("date", ""))[:10] or None
        if published_at:
            date.fromisoformat(published_at)
        guests = _guest_line(official_title)
        public_records.append(
            {
                "episodeId": episode_id,
                "publishedAt": published_at,
                "guests": guests,
                "officialEpisodeUrl": link,
            }
        )
        audit_records.append(
            {
                "episodeId": episode_id,
                "episodeTitle": episode["episodeTitle"],
                "matchMethod": method,
                "titleCompatibility": title_compatibility,
                "officialPostId": match["id"],
                "officialTitle": official_title,
                "retrievedAt": retrieved_at,
                "sourceFields": {
                    "publishedAt": "official WordPress post date",
                    "guests": "official title before the 'on' delimiter" if guests else None,
                    "officialEpisodeUrl": "official WordPress post canonical link",
                },
                "sourceUrl": link,
                "unresolvedReason": None,
            }
        )

    validate_episode_metadata(public_records, episodes)
    write_json(public_output, public_records)
    private_audit = {
        "schemaVersion": SCHEMA_VERSION,
        "retrievedAt": retrieved_at,
        "source": "Information Professionals Association public WordPress API",
        "sourceHost": OFFICIAL_HOST,
        "cachedPageCount": len(pages),
        "cachedPostCount": len(posts),
        "matchedReleaseCount": sum(bool(item["officialEpisodeUrl"]) for item in public_records),
        "unmatchedReleaseCount": sum(not item["officialEpisodeUrl"] for item in public_records),
        "records": audit_records,
    }
    write_json(private_audit_output, private_audit)
    return private_audit


def validate_episode_metadata(
    records: list[dict[str, Any]], episodes: list[dict[str, Any]]
) -> None:
    _assert(len(records) == len(episodes), "Metadata must cover every public release")
    episode_ids = {item["episodeId"] for item in episodes}
    seen: set[str] = set()
    for record in records:
        _assert(set(record) == METADATA_FIELDS, "Metadata record field allowlist mismatch")
        episode_id = record.get("episodeId")
        _assert(episode_id in episode_ids, f"Unknown metadata episodeId {episode_id}")
        _assert(episode_id not in seen, f"Duplicate metadata episodeId {episode_id}")
        seen.add(episode_id)
        published = record.get("publishedAt")
        if published is not None:
            _assert(isinstance(published, str), "publishedAt must be a string or null")
            date.fromisoformat(published)
        guests = record.get("guests")
        _assert(
            guests is None
            or (isinstance(guests, list) and guests and all(isinstance(x, str) and x.strip() for x in guests)),
            "guests must be a nonempty string list or null",
        )
        url = record.get("officialEpisodeUrl")
        _assert(url is None or _official_url(url), "Unapproved officialEpisodeUrl")
    _assert(seen == episode_ids, "Metadata release IDs are incomplete")


def _episode_sort_key(episode: Mapping[str, Any]) -> tuple[Any, ...]:
    number = episode.get("parsedEpisodeNumber")
    return (
        number is None or number == 0,
        number if isinstance(number, int) else math.inf,
        str(episode.get("episodeTitle", "")).casefold(),
        str(episode.get("episodeId", "")),
    )


def _content_mapping(
    episodes: list[dict[str, Any]], provenance: Mapping[str, Any]
) -> tuple[dict[str, str], dict[str, str]]:
    episode_by_id = {item["episodeId"]: item for item in episodes}
    content_for_release = {episode_id: episode_id for episode_id in episode_by_id}
    preferred_release = {episode_id: episode_id for episode_id in episode_by_id}
    for relation in provenance.get("sharedContentRelationships", []):
        _assert(relation.get("semanticRole") == "shared-content-inheritance", "Unexpected shared-content role")
        _assert(relation.get("contributesAnalyticalWeight") is False, "Shared content must add zero weight")
        alias_id = relation["sourceEpisodeId"]
        original_id = relation["targetEpisodeId"]
        _assert(alias_id in episode_by_id and original_id in episode_by_id, "Unknown shared release")
        content_for_release[alias_id] = original_id
        preferred_release.pop(alias_id, None)
        preferred_release[original_id] = original_id
    return content_for_release, preferred_release


def build_topic_counts(
    episodes: list[dict[str, Any]], provenance: Mapping[str, Any]
) -> dict[str, dict[str, TopicCount]]:
    episode_ids = {item["episodeId"] for item in episodes}
    counts: dict[str, dict[str, TopicCount]] = {episode_id: {} for episode_id in episode_ids}
    for topic_id, links in provenance["clusterToReleases"].items():
        for link in links:
            episode_id = link["episodeId"]
            _assert(episode_id in episode_ids, f"Unknown provenance episode {episode_id}")
            primary = link["primaryItemCount"]
            secondary = link["secondaryItemCount"]
            weighted = link["governedWeightedCount"]
            _assert(weighted == 2 * primary + secondary, "Saved governed weight formula mismatch")
            _assert(topic_id not in counts[episode_id], "Duplicate episode/topic aggregate")
            counts[episode_id][topic_id] = TopicCount(topic_id, primary, secondary, weighted)
    return counts


def qualified_topics(
    counts: Mapping[str, TopicCount],
    *,
    share_minimum: float = PROMINENCE_SHARE_MINIMUM,
    primary_minimum: int = PRIMARY_ITEM_MINIMUM,
) -> list[TopicCount]:
    total = sum(item.weighted for item in counts.values())
    if total <= 0:
        return []
    result = [
        item
        for item in counts.values()
        if item.primary >= primary_minimum and item.weighted / total >= share_minimum
    ]
    return sorted(result, key=lambda item: (-item.weighted, -item.primary, item.topic_id))


def weighted_jaccard(
    left: Mapping[str, float], right: Mapping[str, float]
) -> float | None:
    if not left or not right:
        return None
    keys = set(left) | set(right)
    denominator = sum(max(left.get(key, 0.0), right.get(key, 0.0)) for key in keys)
    if denominator <= 0:
        return None
    numerator = sum(min(left.get(key, 0.0), right.get(key, 0.0)) for key in keys)
    return numerator / denominator


def boolean_jaccard(left: Iterable[str], right: Iterable[str]) -> float | None:
    left_set = set(left)
    right_set = set(right)
    if not left_set or not right_set:
        return None
    return len(left_set & right_set) / len(left_set | right_set)


def _normalize_vector(values: Mapping[str, float]) -> dict[str, float]:
    total = sum(values.values())
    if total <= 0:
        return {}
    return {key: value / total for key, value in values.items()}


def _shared_contributions(
    left: Mapping[str, float], right: Mapping[str, float]
) -> list[tuple[str, float]]:
    shared = set(left) & set(right)
    return sorted(
        ((topic_id, min(left[topic_id], right[topic_id])) for topic_id in shared),
        key=lambda item: (-item[1], item[0]),
    )


def _build_similarity_profiles(
    content_ids: Iterable[str], qualified: Mapping[str, list[TopicCount]]
) -> tuple[dict[str, dict[str, float]], dict[str, int]]:
    content_ids = list(content_ids)
    frequency: Counter[str] = Counter()
    for episode_id in content_ids:
        frequency.update(item.topic_id for item in qualified[episode_id])
    total_units = len(content_ids)
    vectors: dict[str, dict[str, float]] = {}
    for episode_id in content_ids:
        adjusted = {
            item.topic_id: item.weighted
            * (1.0 + math.log((total_units + 1) / (frequency[item.topic_id] + 1)))
            for item in qualified[episode_id]
        }
        vectors[episode_id] = _normalize_vector(adjusted)
    return vectors, dict(frequency)


def _presentation_copy() -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "landing": {
            "title": "Cognitive Security Explorer",
            "description": "Explore recurring subjects, cross-cutting interpretations, possible futures, and the conversations behind the map.",
            "overviewNote": "These links show how the parts of the Explorer fit together. Connections organize browsing; they do not assert causation.",
        },
        "entries": [
            {"key": "categories", "description": "Broad areas of the analysis."},
            {"key": "subcategories", "description": "Related subjects grouped inside a category."},
            {"key": "topics", "description": "Specific recurring subjects."},
            {"key": "themes", "description": "Patterns spanning different areas."},
            {"key": "tensions", "description": "Competing priorities, assumptions, or approaches."},
            {"key": "narratives", "description": "Broader interpretations integrating multiple analytical threads."},
            {"key": "scenarios", "description": "Possible future situations for exploration."},
            {"key": "episodes", "description": "Individual conversations and original sources."},
            {"key": "search", "description": "Find subjects across the entire map."},
            {"key": "methodology", "description": "Understand the process, evidence, and limits."},
        ],
    }


def _threshold_distribution(
    topic_counts: Mapping[str, Mapping[str, TopicCount]], content_ids: Iterable[str]
) -> dict[str, dict[str, int]]:
    output: dict[str, dict[str, int]] = {}
    for threshold in (0.03, 0.05, 0.075, 0.10):
        counter = Counter(
            len(qualified_topics(topic_counts[episode_id], share_minimum=threshold))
            for episode_id in content_ids
        )
        output[f"{threshold:.3f}"] = {
            str(topic_count): release_count
            for topic_count, release_count in sorted(counter.items())
        }
    return output


def build_discovery_package(
    *,
    core_dir: Path,
    output_dir: Path,
    calibration_output: Path | None = None,
) -> dict[str, Any]:
    manifest = load_json(core_dir / "manifest.json")
    for key, expected in CORE_COUNT_INVARIANTS.items():
        _assert(manifest["counts"].get(key) == expected, f"Protected count changed: {key}")

    episodes = load_json(core_dir / "episodes.json")
    summaries = load_json(core_dir / "episode_summaries.json")
    clusters = load_json(core_dir / "clusters.json")
    provenance = load_json(core_dir / "provenance.json")
    metadata_path = output_dir / "episode_metadata.json"
    _assert(metadata_path.exists(), "Freeze episode_metadata.json before building discovery")
    metadata = load_json(metadata_path)
    validate_episode_metadata(metadata, episodes)
    write_json(metadata_path, metadata)

    episode_by_id = {item["episodeId"]: item for item in episodes}
    summary_by_id = {item["episodeId"]: item for item in summaries}
    topic_names = {item["clusterId"]: item["name"] for item in clusters}
    _assert(len(topic_names) == CORE_COUNT_INVARIANTS["clusterCount"], "Topic count changed")
    content_for_release, preferred_releases = _content_mapping(episodes, provenance)
    content_ids = sorted(preferred_releases)
    _assert(len(content_ids) == CORE_COUNT_INVARIANTS["canonicalContentUnitCount"], "Content-unit count changed")

    topic_counts = build_topic_counts(episodes, provenance)
    qualified = {episode_id: qualified_topics(topic_counts[episode_id]) for episode_id in content_ids}
    vectors, document_frequency = _build_similarity_profiles(content_ids, qualified)

    pair_scores: dict[tuple[str, str], float | None] = {}
    recommendations: dict[str, list[dict[str, Any]]] = {episode_id: [] for episode_id in content_ids}
    for index, left_id in enumerate(content_ids):
        for right_id in content_ids[index + 1 :]:
            score = weighted_jaccard(vectors[left_id], vectors[right_id])
            pair_scores[(left_id, right_id)] = score
            shared = _shared_contributions(vectors[left_id], vectors[right_id])
            if (
                score is not None
                and score >= SIMILARITY_MINIMUM
                and len(shared) >= SIMILARITY_SHARED_TOPIC_MINIMUM
            ):
                left_entry = {
                    "episodeId": preferred_releases[right_id],
                    "score": round(score, 8),
                    "sharedTopicIds": [item[0] for item in shared[:3]],
                }
                right_entry = {
                    "episodeId": preferred_releases[left_id],
                    "score": round(score, 8),
                    "sharedTopicIds": [item[0] for item in shared[:3]],
                }
                recommendations[left_id].append(left_entry)
                recommendations[right_id].append(right_entry)

    for episode_id in content_ids:
        recommendations[episode_id].sort(
            key=lambda item: (
                -item["score"],
                _episode_sort_key(episode_by_id[item["episodeId"]]),
            )
        )
        recommendations[episode_id] = recommendations[episode_id][:SIMILARITY_RESULT_LIMIT]

    discovery_records: list[dict[str, Any]] = []
    for episode in sorted(episodes, key=lambda item: item["episodeId"]):
        episode_id = episode["episodeId"]
        content_id = content_for_release[episode_id]
        all_topics = [item.topic_id for item in qualified[content_id]]
        discovery_records.append(
            {
                "episodeId": episode_id,
                "contentEpisodeId": content_id,
                "isSharedContentRelease": episode_id != content_id,
                "mainTopicIds": all_topics,
                "defaultMainTopicIds": all_topics[:MAIN_TOPIC_DISPLAY_LIMIT],
                "similarOverall": recommendations[content_id],
            }
        )

    topic_index = []
    for topic_id in sorted(topic_names):
        qualifying_ids = [
            preferred_releases[episode_id]
            for episode_id in content_ids
            if topic_id in vectors[episode_id]
        ]
        qualifying_ids.sort(key=lambda episode_id: _episode_sort_key(episode_by_id[episode_id]))
        topic_index.append({"topicId": topic_id, "episodeIds": qualifying_ids})

    similarity_profiles = [
        {
            "contentEpisodeId": episode_id,
            "topics": [
                {"topicId": topic_id, "normalizedWeight": round(weight, 12)}
                for topic_id, weight in sorted(vectors[episode_id].items())
            ],
        }
        for episode_id in content_ids
    ]

    discovery_payload = {
        "schemaVersion": SCHEMA_VERSION,
        "method": {
            "name": "normalized IDF-weighted Jaccard",
            "primaryItemMinimum": PRIMARY_ITEM_MINIMUM,
            "prominenceShareMinimum": PROMINENCE_SHARE_MINIMUM,
            "defaultMainTopicLimit": MAIN_TOPIC_DISPLAY_LIMIT,
            "similarityMinimum": SIMILARITY_MINIMUM,
            "sharedTopicMinimum": SIMILARITY_SHARED_TOPIC_MINIMUM,
            "recommendationLimit": SIMILARITY_RESULT_LIMIT,
            "interpretation": "A transparent browsing aid based on repeated coded topics; it is not an evidence relationship or a claim that guests agree.",
        },
        "records": discovery_records,
    }
    topic_payload = {
        "schemaVersion": SCHEMA_VERSION,
        "interpretation": "Topic-specific navigation uses the same qualified topic profiles as episode discovery.",
        "records": topic_index,
    }
    similarity_payload = {
        "schemaVersion": SCHEMA_VERSION,
        "method": discovery_payload["method"],
        "contentUnitCount": len(content_ids),
        "topicDocumentFrequency": [
            {"topicId": topic_id, "contentUnitCount": document_frequency.get(topic_id, 0)}
            for topic_id in sorted(topic_names)
        ],
        "profiles": similarity_profiles,
    }
    outputs = {
        "episode_discovery.json": discovery_payload,
        "topic_episode_index.json": topic_payload,
        "similarity_data.json": similarity_payload,
        "presentation_copy.json": _presentation_copy(),
    }
    for file_name, payload in outputs.items():
        write_json(output_dir / file_name, payload)

    file_entries = []
    for file_name in DISCOVERY_FILES:
        payload = (output_dir / file_name).read_bytes()
        file_entries.append(
            {"file": file_name, "bytes": len(payload), "sha256": sha256_bytes(payload)}
        )
    package_manifest = {
        "schemaVersion": SCHEMA_VERSION,
        "publicFiles": list(DISCOVERY_FILES),
        "fileCount": len(DISCOVERY_FILES),
        "files": file_entries,
        "counts": {
            "publicReleaseCount": len(episodes),
            "metadataRecordCount": len(metadata),
            "discoveryRecordCount": len(discovery_records),
            "contentUnitCount": len(content_ids),
            "topicIndexCount": len(topic_index),
            "qualifiedTopicAssignmentCount": sum(len(items) for items in qualified.values()),
            "releaseWithMainTopicsCount": sum(bool(item["mainTopicIds"]) for item in discovery_records),
            "releaseWithSimilarEpisodesCount": sum(bool(item["similarOverall"]) for item in discovery_records),
            "verifiedSourceUrlCount": sum(bool(item["officialEpisodeUrl"]) for item in metadata),
            "verifiedPublishedDateCount": sum(bool(item["publishedAt"]) for item in metadata),
            "verifiedGuestLineCount": sum(bool(item["guests"]) for item in metadata),
        },
        "corePackageRelationship": "Presentation and discovery overlay only; no new analytical evidence relationships.",
    }
    write_json(output_dir / "discovery_manifest.json", package_manifest)

    if calibration_output is not None:
        summary_words = {
            episode_id: summary_by_id[episode_id].get("summaryWordCount", 0)
            for episode_id in content_ids
        }
        weighted_totals = {
            episode_id: sum(item.weighted for item in topic_counts[episode_id].values())
            for episode_id in content_ids
        }
        ordered = sorted(content_ids, key=lambda eid: _episode_sort_key(episode_by_id[eid]))
        requested_numbers = (0, 1, 15, 29, 83, 100, 145, 180, 200, 220, 244, 245)
        sample_ids = []
        for number in requested_numbers:
            match = next(
                (eid for eid in ordered if episode_by_id[eid].get("parsedEpisodeNumber") == number),
                None,
            )
            if match and match not in sample_ids:
                sample_ids.append(match)
        for candidate in (
            min(content_ids, key=lambda eid: (weighted_totals[eid], eid)),
            max(content_ids, key=lambda eid: (weighted_totals[eid], eid)),
            min(content_ids, key=lambda eid: (summary_words[eid], eid)),
            max(content_ids, key=lambda eid: (summary_words[eid], eid)),
        ):
            if candidate not in sample_ids:
                sample_ids.append(candidate)

        idf_only_vectors = {
            episode_id: _normalize_vector(
                {
                    item.topic_id: 1.0
                    + math.log((len(content_ids) + 1) / (document_frequency[item.topic_id] + 1))
                    for item in qualified[episode_id]
                }
            )
            for episode_id in content_ids
        }

        def comparison_neighbors(episode_id: str, method: str) -> list[dict[str, Any]]:
            candidates = []
            for other_id in content_ids:
                if other_id == episode_id:
                    continue
                shared_ids = sorted(
                    set(item.topic_id for item in qualified[episode_id])
                    & set(item.topic_id for item in qualified[other_id])
                )
                if len(shared_ids) < SIMILARITY_SHARED_TOPIC_MINIMUM:
                    continue
                if method == "boolean Jaccard":
                    score = boolean_jaccard(
                        (item.topic_id for item in qualified[episode_id]),
                        (item.topic_id for item in qualified[other_id]),
                    )
                elif method == "normalized IDF-only Jaccard":
                    score = weighted_jaccard(
                        idf_only_vectors[episode_id], idf_only_vectors[other_id]
                    )
                else:
                    score = weighted_jaccard(vectors[episode_id], vectors[other_id])
                if score is not None:
                    candidates.append((score, other_id, shared_ids))
            candidates.sort(
                key=lambda item: (-item[0], _episode_sort_key(episode_by_id[item[1]]))
            )
            return [
                {
                    "episodeId": other_id,
                    "title": episode_by_id[other_id]["episodeTitle"],
                    "score": round(score, 8),
                    "sharedTopics": [topic_names[topic_id] for topic_id in shared_ids[:3]],
                }
                for score, other_id, shared_ids in candidates[:3]
            ]

        eligible_pairs = []
        for (left_id, right_id), score in pair_scores.items():
            if score is None:
                continue
            if len(set(vectors[left_id]) & set(vectors[right_id])) < SIMILARITY_SHARED_TOPIC_MINIMUM:
                continue
            eligible_pairs.append((score, left_id, right_id))
        sorted_scores = sorted(score for score, _, _ in eligible_pairs)

        def percentile(fraction: float) -> float | None:
            if not sorted_scores:
                return None
            index = min(len(sorted_scores) - 1, math.floor(fraction * (len(sorted_scores) - 1)))
            return round(sorted_scores[index], 8)

        cutoff_distribution = {}
        for cutoff in (0.05, 0.08, 0.10, 0.15, 0.20):
            selected = [item for item in eligible_pairs if item[0] >= cutoff]
            represented = {episode_id for _, left_id, right_id in selected for episode_id in (left_id, right_id)}
            cutoff_distribution[f"{cutoff:.2f}"] = {
                "eligiblePairCount": len(selected),
                "contentUnitWithNeighborCount": len(represented),
            }
        calibration = {
            "schemaVersion": SCHEMA_VERSION,
            "selectedProminencePolicy": {
                "primaryItemMinimum": PRIMARY_ITEM_MINIMUM,
                "prominenceShareMinimum": PROMINENCE_SHARE_MINIMUM,
                "rationale": "Requires repeated primary coding while retaining focused topics that reach five percent of an episode's saved weighted coding profile.",
            },
            "thresholdDistributions": _threshold_distribution(topic_counts, content_ids),
            "selectedSimilarityPolicy": {
                "method": "normalized IDF-weighted Jaccard",
                "similarityMinimum": SIMILARITY_MINIMUM,
                "sharedTopicMinimum": SIMILARITY_SHARED_TOPIC_MINIMUM,
                "rationale": "The two-topic gate supplies meaningful overlap; 0.15 removes roughly the weakest tenth of eligible normalized overlaps while retaining the same set of content units with at least one genuine neighbor.",
            },
            "similarityScoreDistribution": {
                "eligiblePairCount": len(eligible_pairs),
                "minimum": round(sorted_scores[0], 8) if sorted_scores else None,
                "p10": percentile(0.10),
                "median": percentile(0.50),
                "p90": percentile(0.90),
                "maximum": round(sorted_scores[-1], 8) if sorted_scores else None,
            },
            "similarityCutoffDistribution": cutoff_distribution,
            "sample": [
                {
                    "episodeId": episode_id,
                    "episodeNumber": episode_by_id[episode_id].get("parsedEpisodeNumber"),
                    "episodeTitle": episode_by_id[episode_id]["episodeTitle"],
                    "summaryWordCount": summary_words[episode_id],
                    "weightedTopicTotal": weighted_totals[episode_id],
                    "qualifiedByThreshold": {
                        f"{threshold:.3f}": [
                            item.topic_id
                            for item in qualified_topics(topic_counts[episode_id], share_minimum=threshold)
                        ]
                        for threshold in (0.03, 0.05, 0.075, 0.10)
                    },
                    "selectedTopicNames": [topic_names[item.topic_id] for item in qualified[episode_id]],
                    "neighbors": [
                        {
                            "episodeId": item["episodeId"],
                            "title": episode_by_id[item["episodeId"]]["episodeTitle"],
                            "score": item["score"],
                            "sharedTopics": [topic_names[topic_id] for topic_id in item["sharedTopicIds"]],
                        }
                        for item in recommendations[episode_id]
                    ],
                    "methodComparison": {
                        method: comparison_neighbors(episode_id, method)
                        for method in (
                            "boolean Jaccard",
                            "normalized IDF-only Jaccard",
                            "normalized IDF-weighted Jaccard",
                        )
                    },
                }
                for episode_id in sample_ids
            ],
        }
        write_json(calibration_output, calibration)

    validate_discovery_package(core_dir=core_dir, output_dir=output_dir)
    return package_manifest


def validate_discovery_package(*, core_dir: Path, output_dir: Path) -> None:
    episodes = load_json(core_dir / "episodes.json")
    metadata = load_json(output_dir / "episode_metadata.json")
    validate_episode_metadata(metadata, episodes)
    package_manifest = load_json(output_dir / "discovery_manifest.json")
    _assert(package_manifest["publicFiles"] == list(DISCOVERY_FILES), "Discovery allowlist mismatch")
    _assert(package_manifest["fileCount"] == len(DISCOVERY_FILES), "Discovery file count mismatch")
    for entry in package_manifest["files"]:
        _assert(entry["file"] in DISCOVERY_FILES, "Unexpected discovery file")
        payload = (output_dir / entry["file"]).read_bytes()
        _assert(len(payload) == entry["bytes"], f"Byte count mismatch for {entry['file']}")
        _assert(sha256_bytes(payload) == entry["sha256"], f"Hash mismatch for {entry['file']}")

    discovery = load_json(output_dir / "episode_discovery.json")
    topic_index = load_json(output_dir / "topic_episode_index.json")
    similarity = load_json(output_dir / "similarity_data.json")
    episode_ids = {item["episodeId"] for item in episodes}
    records = discovery["records"]
    _assert(len(records) == len(episode_ids), "Discovery release count mismatch")
    _assert({item["episodeId"] for item in records} == episode_ids, "Discovery IDs mismatch")
    topic_ids = {item["topicId"] for item in topic_index["records"]}
    _assert(len(topic_ids) == CORE_COUNT_INVARIANTS["clusterCount"], "Topic index count mismatch")
    profiles = {item["contentEpisodeId"]: item["topics"] for item in similarity["profiles"]}
    _assert(len(profiles) == CORE_COUNT_INVARIANTS["canonicalContentUnitCount"], "Similarity profile count mismatch")
    for record in records:
        _assert(set(record["defaultMainTopicIds"]).issubset(record["mainTopicIds"]), "Display topics escaped full profile")
        _assert(len(record["defaultMainTopicIds"]) <= MAIN_TOPIC_DISPLAY_LIMIT, "Display topic cap exceeded")
        _assert(len(record["similarOverall"]) <= SIMILARITY_RESULT_LIMIT, "Recommendation cap exceeded")
        for recommendation in record["similarOverall"]:
            _assert(recommendation["episodeId"] in episode_ids, "Unknown recommended episode")
            _assert(recommendation["episodeId"] != record["episodeId"], "Self recommendation")
            _assert(len(recommendation["sharedTopicIds"]) >= SIMILARITY_SHARED_TOPIC_MINIMUM, "Weak recommendation")
            _assert(SIMILARITY_MINIMUM <= recommendation["score"] <= 1, "Recommendation score out of bounds")


__all__ = [
    "DiscoveryError",
    "build_discovery_package",
    "build_topic_counts",
    "boolean_jaccard",
    "freeze_episode_metadata",
    "json_bytes",
    "qualified_topics",
    "validate_discovery_package",
    "validate_episode_metadata",
    "weighted_jaccard",
]
