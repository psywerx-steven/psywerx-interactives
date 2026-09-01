"""Grounded, public-safe episode products for the Cognitive Security Explorer.

This module deliberately keeps episode relationships separate from the frozen
historical ``relationships.json`` graph.  Every aggregate starts with the one
governed canonical source identity selected for a public-feed episode.  Alias
items therefore cannot enter an episode summary package or relationship.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from copy import deepcopy
from typing import Any, Iterable, Mapping, Sequence


EPISODE_PRODUCT_SCHEMA_VERSION = "1.0"
SUMMARY_METHOD = "deterministic-grounded-extractive-synthesis-v1"
REVIEWED_SUMMARY_METHOD = "codex-grounded-synthesis-v1"

EPISODE_RELATIONSHIP_SCHEMA: dict[str, tuple[str, str, str]] = {
    "episode-participates-in-category": (
        "category",
        "direct-item-aggregation",
        "Actual retained canonical items aggregated by their coded category.",
    ),
    "episode-coded-to-cluster": (
        "cluster",
        "direct-coded-relationship",
        "Actual retained canonical item-to-cluster assignments.",
    ),
    "episode-derived-to-meta-cluster": (
        "metaCluster",
        "derived-through-cluster-membership",
        "Actual episode cluster support followed through the governed cluster-to-meta-cluster mapping.",
    ),
    "episode-derived-to-theme": (
        "theme",
        "derived-analytical-connection",
        "Actual episode cluster support followed through a governed cluster/theme or cluster/meta-cluster/theme path.",
    ),
    "episode-has-theme-lineage": (
        "theme",
        "direct-item-lineage",
        "Actual retained canonical items listed as representative evidence for the theme.",
    ),
    "episode-has-tension-lineage": (
        "tension",
        "direct-item-lineage",
        "Actual retained canonical items listed as source evidence for a tension pole.",
    ),
}


_SPACE_RE = re.compile(r"\s+")
_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9'-]*")
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
_STOP_WORDS = {
    "a", "about", "across", "after", "again", "against", "all", "also", "an",
    "and", "any", "are", "as", "at", "be", "because", "been", "before", "being",
    "between", "both", "but", "by", "can", "could", "did", "do", "does", "during",
    "each", "for", "from", "further", "had", "has", "have", "having", "how", "if",
    "in", "into", "is", "it", "its", "may", "more", "most", "not", "of", "on",
    "or", "other", "our", "out", "over", "same", "should", "so", "some", "such",
    "than", "that", "the", "their", "them", "then", "there", "these", "they", "this",
    "those", "through", "to", "under", "up", "very", "was", "we", "were", "what",
    "when", "where", "which", "while", "who", "why", "will", "with", "would", "you",
}


def _text(value: Any) -> str:
    return _SPACE_RE.sub(" ", str(value or "")).strip()


def _identifier(record: Mapping[str, Any], field: str) -> str:
    return _text(record.get(field))


def _words(value: Any) -> list[str]:
    return _WORD_RE.findall(_text(value))


def _content_tokens(value: Any) -> set[str]:
    return {
        word.casefold()
        for word in _words(value)
        if len(word) > 2 and word.casefold() not in _STOP_WORDS
    }


def _first_sentence(value: Any) -> str:
    text = _text(value)
    if not text:
        return ""
    return _SENTENCE_RE.split(text, maxsplit=1)[0].strip()


def _trim_words(value: Any, maximum: int) -> str:
    text = _text(value)
    words = text.split()
    if len(words) <= maximum:
        return text
    shortened = " ".join(words[:maximum]).rstrip(" ,;:-")
    return shortened + "."


def _stable_relationship_id(
    relationship_type: str,
    episode_id: str,
    target_id: str,
) -> str:
    prefix = {
        "episode-participates-in-category": "CAT",
        "episode-coded-to-cluster": "CLU",
        "episode-derived-to-meta-cluster": "MET",
        "episode-derived-to-theme": "THM",
        "episode-has-theme-lineage": "THD",
        "episode-has-tension-lineage": "TND",
    }[relationship_type]
    return f"EPR-{prefix}-{episode_id}-{target_id}"


def canonical_episode_sources(
    dataset: Mapping[str, Sequence[Mapping[str, Any]]],
) -> dict[str, str]:
    """Return the governed episode -> selected source identity mapping.

    The reconciled episode record is authoritative.  Mapping-table roles are
    cross-checked when present so an alias can never silently be selected.
    """

    canonical_mapping_rows = {
        _identifier(row, "canonicalEpisodeId"): _identifier(row, "sourceIdentityId")
        for row in dataset.get("episode_source_mappings", ())
        if row.get("mappingRole") == "canonical"
        and row.get("canonicalEpisodeId")
        and row.get("sourceIdentityId")
    }
    selected: dict[str, str] = {}
    for episode in dataset.get("episodes", ()):
        episode_id = _identifier(episode, "episodeId")
        source_id = _identifier(episode, "canonicalSourceIdentityId")
        if not episode_id or not source_id:
            raise ValueError("Every canonical episode must identify its selected source identity.")
        mapped_source = canonical_mapping_rows.get(episode_id)
        if mapped_source and mapped_source != source_id:
            raise ValueError(
                f"Canonical source disagreement for {episode_id}: "
                f"episode={source_id}, mapping={mapped_source}."
            )
        if episode_id in selected:
            raise ValueError(f"Duplicate canonical episode ID: {episode_id}.")
        selected[episode_id] = source_id
    return selected


def retained_canonical_items(
    dataset: Mapping[str, Sequence[Mapping[str, Any]]],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, str]]:
    """Group items by episode only when their source identity was retained."""

    selected_sources = canonical_episode_sources(dataset)
    episode_by_source = {source_id: episode_id for episode_id, source_id in selected_sources.items()}
    grouped: dict[str, list[dict[str, Any]]] = {episode_id: [] for episode_id in selected_sources}
    item_episode: dict[str, str] = {}
    for source in dataset.get("items", ()):
        source_id = _identifier(source, "sourceIdentityId")
        episode_id = episode_by_source.get(source_id)
        if episode_id is None:
            continue
        item_id = _identifier(source, "itemId")
        if not item_id:
            raise ValueError(f"A retained item for {episode_id} has no itemId.")
        if item_id in item_episode:
            raise ValueError(f"Duplicate retained item ID: {item_id}.")
        item_episode[item_id] = episode_id
        grouped[episode_id].append(dict(source))
    missing = [episode_id for episode_id, rows in grouped.items() if not rows]
    if missing:
        raise ValueError(
            "Every public episode must have nonzero canonical structured input; missing: "
            + ", ".join(sorted(missing))
        )
    return grouped, item_episode


def _base_relationship(
    relationship_type: str,
    episode_id: str,
    target_id: str,
) -> dict[str, Any]:
    target_type, semantics, _ = EPISODE_RELATIONSHIP_SCHEMA[relationship_type]
    return {
        "relationshipId": _stable_relationship_id(
            relationship_type, episode_id, target_id
        ),
        "relationshipType": relationship_type,
        "sourceType": "episode",
        "sourceId": episode_id,
        "targetType": target_type,
        "targetId": target_id,
        "relationshipSemantics": semantics,
    }


def build_episode_relationships(
    dataset: Mapping[str, Sequence[Mapping[str, Any]]],
) -> list[dict[str, Any]]:
    """Build all public-safe episode relationships from governed lineage."""

    items_by_episode, item_episode = retained_canonical_items(dataset)
    relationships: list[dict[str, Any]] = []

    # Episode -> category: aggregate every actual retained item.
    for episode_id, items in items_by_episode.items():
        by_category: dict[str, Counter[str]] = defaultdict(Counter)
        for item in items:
            category_id = _identifier(item, "categoryId")
            scope = _text(item.get("scope")).casefold()
            if category_id:
                by_category[category_id][scope] += 1
        for category_id, counts in by_category.items():
            record = _base_relationship(
                "episode-participates-in-category", episode_id, category_id
            )
            record.update(
                {
                    "itemCount": sum(counts.values()),
                    "focalItemCount": counts.get("focal", 0),
                    "contextualItemCount": counts.get("contextual", 0),
                }
            )
            relationships.append(record)

    # Episode -> cluster: count every actual retained primary/secondary code.
    cluster_counts: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for assignment in dataset.get("item_cluster_assignments", ()):
        item_id = _identifier(assignment, "itemId")
        episode_id = item_episode.get(item_id)
        if not episode_id:
            continue
        primary_id = _identifier(assignment, "primaryClusterId")
        secondary_id = _identifier(assignment, "secondaryClusterId")
        if primary_id:
            cluster_counts[(episode_id, primary_id)]["primary"] += 1
        if secondary_id:
            cluster_counts[(episode_id, secondary_id)]["secondary"] += 1

    cluster_records: dict[tuple[str, str], dict[str, Any]] = {}
    for (episode_id, cluster_id), counts in cluster_counts.items():
        primary = counts.get("primary", 0)
        secondary = counts.get("secondary", 0)
        record = _base_relationship(
            "episode-coded-to-cluster", episode_id, cluster_id
        )
        record.update(
            {
                "primaryCount": primary,
                "secondaryCount": secondary,
                "weightedCount": 2 * primary + secondary,
            }
        )
        relationships.append(record)
        cluster_records[(episode_id, cluster_id)] = record

    # Episode -> meta-cluster: only through actual supported clusters.
    meta_by_cluster: dict[str, set[str]] = defaultdict(set)
    for mapping in dataset.get("cluster_meta_mappings", ()):
        cluster_id = _identifier(mapping, "clusterId")
        meta_id = _identifier(mapping, "metaClusterId")
        if cluster_id and meta_id:
            meta_by_cluster[cluster_id].add(meta_id)

    meta_support: dict[tuple[str, str], dict[str, Any]] = defaultdict(
        lambda: {
            "primaryCount": 0,
            "secondaryCount": 0,
            "supportingClusterIds": set(),
        }
    )
    for (episode_id, cluster_id), cluster_record in cluster_records.items():
        for meta_id in meta_by_cluster.get(cluster_id, ()):
            support = meta_support[(episode_id, meta_id)]
            support["primaryCount"] += cluster_record["primaryCount"]
            support["secondaryCount"] += cluster_record["secondaryCount"]
            support["supportingClusterIds"].add(cluster_id)

    meta_records: dict[tuple[str, str], dict[str, Any]] = {}
    for (episode_id, meta_id), support in meta_support.items():
        primary = int(support["primaryCount"])
        secondary = int(support["secondaryCount"])
        record = _base_relationship(
            "episode-derived-to-meta-cluster", episode_id, meta_id
        )
        record.update(
            {
                "primaryCount": primary,
                "secondaryCount": secondary,
                "weightedCount": 2 * primary + secondary,
                "supportingClusterIds": sorted(support["supportingClusterIds"]),
            }
        )
        relationships.append(record)
        meta_records[(episode_id, meta_id)] = record

    # Episode -> theme: follow either governed cluster evidence or a governed
    # cluster -> meta-cluster -> theme chain.  A supporting cluster contributes
    # counts once even if both governed paths exist.
    themes_by_cluster: dict[str, set[str]] = defaultdict(set)
    for evidence in dataset.get("theme_cluster_evidence", ()):
        cluster_id = _identifier(evidence, "clusterId")
        theme_id = _identifier(evidence, "themeId")
        if cluster_id and theme_id and not evidence.get("unresolvedReference"):
            themes_by_cluster[cluster_id].add(theme_id)
    themes_by_meta: dict[str, set[str]] = defaultdict(set)
    for mapping in dataset.get("theme_meta_mappings", ()):
        meta_id = _identifier(mapping, "metaClusterId")
        theme_id = _identifier(mapping, "themeId")
        if meta_id and theme_id:
            themes_by_meta[meta_id].add(theme_id)

    theme_paths: dict[tuple[str, str], dict[str, set[str]]] = defaultdict(
        lambda: {
            "clusters": set(),
            "metaClusters": set(),
            "pathTypes": set(),
        }
    )
    for (episode_id, cluster_id), _cluster_record in cluster_records.items():
        for theme_id in themes_by_cluster.get(cluster_id, ()):
            path = theme_paths[(episode_id, theme_id)]
            path["clusters"].add(cluster_id)
            path["pathTypes"].add("through-cluster-evidence")
        for meta_id in meta_by_cluster.get(cluster_id, ()):
            for theme_id in themes_by_meta.get(meta_id, ()):
                path = theme_paths[(episode_id, theme_id)]
                path["clusters"].add(cluster_id)
                path["metaClusters"].add(meta_id)
                path["pathTypes"].add("through-meta-cluster")

    direct_theme_items: dict[str, set[str]] = {
        _identifier(theme, "themeId"): {
            _text(item_id)
            for item_id in theme.get("representativeItemIds", ())
            if _text(item_id)
        }
        for theme in dataset.get("themes", ())
        if _identifier(theme, "themeId")
    }
    retained_ids_by_episode = {
        episode_id: {_identifier(item, "itemId") for item in items}
        for episode_id, items in items_by_episode.items()
    }

    theme_records: dict[tuple[str, str], dict[str, Any]] = {}
    for (episode_id, theme_id), path in theme_paths.items():
        supporting_clusters = sorted(path["clusters"])
        primary = sum(
            cluster_records[(episode_id, cluster_id)]["primaryCount"]
            for cluster_id in supporting_clusters
        )
        secondary = sum(
            cluster_records[(episode_id, cluster_id)]["secondaryCount"]
            for cluster_id in supporting_clusters
        )
        direct_item_count = len(
            retained_ids_by_episode[episode_id]
            & direct_theme_items.get(theme_id, set())
        )
        relationship_type = (
            "episode-has-theme-lineage"
            if direct_item_count
            else "episode-derived-to-theme"
        )
        record = _base_relationship(relationship_type, episode_id, theme_id)
        record.update(
            {
                "primaryCount": primary,
                "secondaryCount": secondary,
                "weightedCount": 2 * primary + secondary,
                "supportingClusterIds": supporting_clusters,
                "supportingMetaClusterIds": sorted(path["metaClusters"]),
                "derivationPaths": sorted(path["pathTypes"]),
            }
        )
        if direct_item_count:
            record["itemCount"] = direct_item_count
        relationships.append(record)
        theme_records[(episode_id, theme_id)] = record

    # Episode -> tension direct lineage: tension pole evidence is the strongest
    # available trace.  Pole counts describe lineage only, never endorsement.
    for tension in dataset.get("tensions", ()):
        tension_id = _identifier(tension, "tensionId")
        pole_a_ids = {_text(value) for value in tension.get("supportingItemIdsPoleA", ()) if _text(value)}
        pole_b_ids = {_text(value) for value in tension.get("supportingItemIdsPoleB", ()) if _text(value)}
        if not tension_id:
            continue
        for episode_id, retained_ids in retained_ids_by_episode.items():
            pole_a_count = len(retained_ids & pole_a_ids)
            pole_b_count = len(retained_ids & pole_b_ids)
            if not pole_a_count and not pole_b_count:
                continue
            record = _base_relationship(
                "episode-has-tension-lineage", episode_id, tension_id
            )
            record.update(
                {
                    "itemCount": len(retained_ids & (pole_a_ids | pole_b_ids)),
                    "poleASupportCount": pole_a_count,
                    "poleBSupportCount": pole_b_count,
                    "interpretiveCaveat": (
                        "Evidence lineage does not mean the episode or speaker endorses either pole."
                    ),
                }
            )
            relationships.append(record)

    relationship_ids = [record["relationshipId"] for record in relationships]
    if len(relationship_ids) != len(set(relationship_ids)):
        raise ValueError("Episode relationship IDs are not unique.")
    return sorted(
        relationships,
        key=lambda record: (
            str(record["sourceId"]),
            str(record["targetType"]),
            str(record["targetId"]),
            str(record["relationshipType"]),
        ),
    )


def episode_relationship_payload(
    dataset: Mapping[str, Sequence[Mapping[str, Any]]],
) -> list[dict[str, Any]]:
    """Return the standalone public relationship record list."""

    return build_episode_relationships(dataset)


def build_private_source_packages(
    dataset: Mapping[str, Sequence[Mapping[str, Any]]],
) -> list[dict[str, Any]]:
    """Build ignored source packages used for grounded summary authoring."""

    items_by_episode, item_episode = retained_canonical_items(dataset)
    episodes = {
        _identifier(row, "episodeId"): row for row in dataset.get("episodes", ())
    }
    categories = {
        _identifier(row, "categoryId"): _text(row.get("name"))
        for row in dataset.get("categories", ())
    }
    clusters = {
        _identifier(row, "clusterId"): _text(row.get("name"))
        for row in dataset.get("clusters", ())
    }
    assignments_by_item = {
        _identifier(row, "itemId"): row
        for row in dataset.get("item_cluster_assignments", ())
        if _identifier(row, "itemId") in item_episode
    }
    tags_by_item: dict[str, list[str]] = defaultdict(list)
    for row in dataset.get("item_tags", ()):
        item_id = _identifier(row, "itemId")
        if item_id in item_episode:
            tag = _text(row.get("normalizedTag") or row.get("tag"))
            if tag:
                tags_by_item[item_id].append(tag)

    packages: list[dict[str, Any]] = []
    for episode_id in sorted(episodes):
        episode = episodes[episode_id]
        rows = items_by_episode[episode_id]
        category_counts: dict[str, Counter[str]] = defaultdict(Counter)
        primary_counts: Counter[str] = Counter()
        secondary_counts: Counter[str] = Counter()
        public_items: list[dict[str, Any]] = []
        all_tags: Counter[str] = Counter()
        for row in rows:
            item_id = _identifier(row, "itemId")
            category_id = _identifier(row, "categoryId")
            scope = _text(row.get("scope")).casefold()
            if category_id:
                category_counts[category_id][scope] += 1
            assignment = assignments_by_item.get(item_id, {})
            primary_id = _identifier(assignment, "primaryClusterId")
            secondary_id = _identifier(assignment, "secondaryClusterId")
            if primary_id:
                primary_counts[primary_id] += 1
            if secondary_id:
                secondary_counts[secondary_id] += 1
            item_tags = sorted(set(tags_by_item.get(item_id, ())))
            all_tags.update(item_tags)
            public_items.append(
                {
                    "summary": _text(row.get("summary")),
                    "categoryId": category_id,
                    "categoryName": categories.get(category_id, _text(row.get("categoryName"))),
                    "scope": scope,
                    "primaryClusterId": primary_id or None,
                    "primaryClusterName": clusters.get(primary_id) or None,
                    "secondaryClusterId": secondary_id or None,
                    "secondaryClusterName": clusters.get(secondary_id) or None,
                    "strategicSignificance": _text(row.get("strategicSignificance")),
                    "operationalImplications": _text(row.get("operationalImplications")),
                    "relevanceTags": item_tags,
                    "timeHorizon": _text(row.get("timeHorizon")) or None,
                    "episodeRelevanceScore": row.get("episodeRelevanceScore"),
                    "actionabilityScore": row.get("actionabilityScore"),
                }
            )

        category_distribution = [
            {
                "categoryId": category_id,
                "categoryName": categories.get(category_id, category_id),
                "itemCount": sum(counts.values()),
                "focalItemCount": counts.get("focal", 0),
                "contextualItemCount": counts.get("contextual", 0),
            }
            for category_id, counts in sorted(category_counts.items())
        ]
        cluster_distribution = [
            {
                "clusterId": cluster_id,
                "clusterName": clusters.get(cluster_id, cluster_id),
                "primaryCount": primary_counts.get(cluster_id, 0),
                "secondaryCount": secondary_counts.get(cluster_id, 0),
                "weightedCount": 2 * primary_counts.get(cluster_id, 0)
                + secondary_counts.get(cluster_id, 0),
            }
            for cluster_id in sorted(set(primary_counts) | set(secondary_counts))
        ]
        cluster_distribution.sort(
            key=lambda row: (-row["weightedCount"], row["clusterId"])
        )
        packages.append(
            {
                "episodeId": episode_id,
                "canonicalSourceIdentityId": _identifier(
                    episode, "canonicalSourceIdentityId"
                ),
                "episodeTitle": _text(episode.get("episodeTitle")),
                "episodeNumber": episode.get("parsedEpisodeNumber"),
                "itemCount": len(rows),
                "focalItemCount": sum(
                    1 for row in rows if _text(row.get("scope")).casefold() == "focal"
                ),
                "contextualItemCount": sum(
                    1
                    for row in rows
                    if _text(row.get("scope")).casefold() == "contextual"
                ),
                "categoriesRepresented": category_distribution,
                "primaryClusterDistribution": [
                    {
                        "clusterId": row["clusterId"],
                        "clusterName": row["clusterName"],
                        "count": row["primaryCount"],
                    }
                    for row in cluster_distribution
                    if row["primaryCount"]
                ],
                "secondaryClusterDistribution": [
                    {
                        "clusterId": row["clusterId"],
                        "clusterName": row["clusterName"],
                        "count": row["secondaryCount"],
                    }
                    for row in cluster_distribution
                    if row["secondaryCount"]
                ],
                "clusterDistribution": cluster_distribution,
                "relevanceTags": [
                    {"tag": tag, "count": count}
                    for tag, count in sorted(
                        all_tags.items(), key=lambda pair: (-pair[1], pair[0])
                    )
                ],
                "structuredItems": public_items,
                "summaryGenerationProvenance": {
                    "selectionRule": (
                        "Only items whose sourceIdentityId equals the episode's governed canonicalSourceIdentityId."
                    ),
                    "excludedAliasContribution": 0,
                    "allowedInputs": [
                        "structured item summary",
                        "category",
                        "primary cluster",
                        "secondary cluster",
                        "strategic significance",
                        "operational implications",
                        "relevance tags",
                        "time horizon",
                    ],
                },
            }
        )
    return packages


def _candidate_score(item: Mapping[str, Any], token_frequency: Counter[str]) -> float:
    summary = _text(item.get("summary"))
    tokens = _content_tokens(summary)
    centrality = sum(token_frequency[token] for token in tokens) / max(len(tokens), 1)
    relevance = float(item.get("episodeRelevanceScore") or 0)
    actionability = float(item.get("actionabilityScore") or 0)
    focal_bonus = 2.0 if item.get("scope") == "focal" else 0.0
    significance_bonus = 1.0 if _text(item.get("strategicSignificance")) else 0.0
    implication_bonus = 1.0 if _text(item.get("operationalImplications")) else 0.0
    length = len(_words(summary))
    length_bonus = 2.0 if 14 <= length <= 42 else 0.0
    return (
        centrality
        + relevance
        + actionability * 0.5
        + focal_bonus
        + significance_bonus
        + implication_bonus
        + length_bonus
    )


def _representative_items(package: Mapping[str, Any], maximum: int = 6) -> list[dict[str, Any]]:
    items = [
        dict(row)
        for row in package.get("structuredItems", ())
        if _text(row.get("summary"))
    ]
    token_frequency: Counter[str] = Counter()
    for item in items:
        token_frequency.update(_content_tokens(item.get("summary")))
    ranked = sorted(
        items,
        key=lambda row: (
            -_candidate_score(row, token_frequency),
            _text(row.get("categoryId")),
            _text(row.get("summary")),
        ),
    )
    chosen: list[dict[str, Any]] = []
    chosen_tokens: list[set[str]] = []
    represented_categories: set[str] = set()
    for candidate in ranked:
        tokens = _content_tokens(candidate.get("summary"))
        if not tokens:
            continue
        overlap = max(
            (
                len(tokens & prior) / max(len(tokens | prior), 1)
                for prior in chosen_tokens
            ),
            default=0.0,
        )
        category_id = _text(candidate.get("categoryId"))
        if overlap > 0.58 and category_id in represented_categories:
            continue
        chosen.append(candidate)
        chosen_tokens.append(tokens)
        represented_categories.add(category_id)
        if len(chosen) >= maximum:
            break
    return chosen or ranked[:maximum]


def _public_key_topics(package: Mapping[str, Any]) -> list[str]:
    topics: list[str] = []
    for cluster in package.get("clusterDistribution", ()):
        name = _text(cluster.get("clusterName"))
        if name and name.casefold() not in {topic.casefold() for topic in topics}:
            topics.append(name)
        if len(topics) >= 4:
            break
    for tag_record in package.get("relevanceTags", ()):
        tag = _text(tag_record.get("tag"))
        count = int(tag_record.get("count") or 0)
        if (
            tag
            and 2 <= len(_words(tag)) <= 7
            and (count >= 2 or int(package.get("itemCount") or 0) < 6)
            and tag.casefold() not in {topic.casefold() for topic in topics}
        ):
            topics.append(tag)
        if len(topics) >= 6:
            break
    for category in package.get("categoriesRepresented", ()):
        name = _text(category.get("categoryName"))
        if name and name.casefold() not in {topic.casefold() for topic in topics}:
            topics.append(name)
        if len(topics) >= 3:
            break
    return topics[:6]


def _extractive_summary(package: Mapping[str, Any]) -> str:
    representatives = _representative_items(package)
    sentences: list[str] = []
    seen: set[str] = set()
    for item in representatives:
        sentence = _trim_words(_first_sentence(item.get("summary")), 38)
        normalized = sentence.casefold()
        if sentence and normalized not in seen:
            sentences.append(sentence)
            seen.add(normalized)
        word_count = len(" ".join(sentences).split())
        if word_count >= 118:
            break

    if len(" ".join(sentences).split()) < 100:
        for item in representatives:
            sentence = _trim_words(_first_sentence(item.get("strategicSignificance")), 32)
            normalized = sentence.casefold()
            if sentence and normalized not in seen:
                sentences.append(sentence)
                seen.add(normalized)
            if len(" ".join(sentences).split()) >= 105:
                break
    if len(" ".join(sentences).split()) < 100:
        for item in representatives:
            sentence = _trim_words(_first_sentence(item.get("operationalImplications")), 30)
            normalized = sentence.casefold()
            if sentence and normalized not in seen:
                sentences.append(sentence)
                seen.add(normalized)
            if len(" ".join(sentences).split()) >= 105:
                break

    output: list[str] = []
    word_count = 0
    for sentence in sentences:
        sentence_words = len(sentence.split())
        if output and word_count + sentence_words > 180:
            break
        output.append(sentence.rstrip() if sentence.endswith(('.', '!', '?')) else sentence + ".")
        word_count += sentence_words
    summary = " ".join(output)
    if not summary:
        raise ValueError(f"Episode {package.get('episodeId')} has no structured summary input.")
    if len(summary.split()) < 90:
        # Very small episodes are allowed to be shorter than the preferred
        # range, but they still use only their actual structured material.
        return summary
    return summary


def _why_it_matters(package: Mapping[str, Any]) -> str:
    representatives = _representative_items(package)
    strategic = next(
        (
            _trim_words(_first_sentence(row.get("strategicSignificance")), 34)
            for row in representatives
            if _text(row.get("strategicSignificance"))
        ),
        "",
    )
    operational = next(
        (
            _trim_words(_first_sentence(row.get("operationalImplications")), 24)
            for row in representatives
            if _text(row.get("operationalImplications"))
        ),
        "",
    )
    if strategic and operational and strategic.casefold() != operational.casefold():
        return _trim_words(
            strategic.rstrip(".") + "; " + operational[:1].lower() + operational[1:],
            52,
        )
    return strategic or operational or _trim_words(_first_sentence(package.get("episodeTitle")), 30)


def build_grounded_summary(package: Mapping[str, Any]) -> dict[str, Any]:
    """Create a deterministic fallback summary using only structured inputs."""

    summary = _extractive_summary(package)
    topics = _public_key_topics(package)
    why_it_matters = _why_it_matters(package)
    if not topics:
        raise ValueError(f"Episode {package.get('episodeId')} has no grounded key topics.")
    if not why_it_matters:
        raise ValueError(f"Episode {package.get('episodeId')} has no grounded why-it-matters material.")
    return {
        "episodeId": _identifier(package, "episodeId"),
        "summary": summary,
        "keyTopics": topics,
        "whyItMatters": why_it_matters,
        "sourceItemCount": int(package.get("itemCount") or 0),
        "focalItemCount": int(package.get("focalItemCount") or 0),
        "contextualItemCount": int(package.get("contextualItemCount") or 0),
        "generationMethod": SUMMARY_METHOD,
    }


def build_grounded_summaries(
    packages: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    summaries = [build_grounded_summary(package) for package in packages]
    episode_ids = [row["episodeId"] for row in summaries]
    if len(episode_ids) != len(set(episode_ids)):
        raise ValueError("Grounded summary episode IDs are not unique.")
    return sorted(summaries, key=lambda row: row["episodeId"])


def build_summary_authoring_inputs(
    packages: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Return compact private inputs for human/agent grounded synthesis review."""

    inputs: list[dict[str, Any]] = []
    for package in packages:
        representatives = _representative_items(package, maximum=8)
        inputs.append(
            {
                "episodeId": _identifier(package, "episodeId"),
                "episodeTitle": _text(package.get("episodeTitle")),
                "episodeNumber": package.get("episodeNumber"),
                "itemCount": int(package.get("itemCount") or 0),
                "focalItemCount": int(package.get("focalItemCount") or 0),
                "contextualItemCount": int(package.get("contextualItemCount") or 0),
                "categoriesRepresented": deepcopy(
                    list(package.get("categoriesRepresented", ()))
                ),
                "clusterDistribution": deepcopy(
                    list(package.get("clusterDistribution", ()))[:12]
                ),
                "topicCandidates": _public_key_topics(package),
                "sourceMaterials": [
                    {
                        "summary": _text(row.get("summary")),
                        "categoryName": _text(row.get("categoryName")),
                        "primaryClusterName": _text(row.get("primaryClusterName")) or None,
                        "secondaryClusterName": _text(row.get("secondaryClusterName")) or None,
                        "strategicSignificance": _text(row.get("strategicSignificance")),
                        "operationalImplications": _text(row.get("operationalImplications")),
                        "relevanceTags": deepcopy(list(row.get("relevanceTags", ()))),
                        "timeHorizon": row.get("timeHorizon"),
                    }
                    for row in representatives
                ],
            }
        )
    return sorted(inputs, key=lambda row: row["episodeId"])


def select_representative_pilot(
    packages: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Select ten documented, non-position-based QA cases by governed traits."""

    by_number: dict[int, Mapping[str, Any]] = {
        int(row["episodeNumber"]): row
        for row in packages
        if row.get("episodeNumber") is not None
    }
    selected: list[tuple[str, Mapping[str, Any]]] = []

    def add(reason: str, row: Mapping[str, Any] | None) -> None:
        if row is None:
            return
        episode_id = _identifier(row, "episodeId")
        if episode_id and all(_identifier(existing, "episodeId") != episode_id for _, existing in selected):
            selected.append((reason, row))

    add("trailer", by_number.get(0))
    positive_numbers = sorted(number for number in by_number if number > 0)
    add("early episode", by_number.get(positive_numbers[0]) if positive_numbers else None)
    add("middle episode", by_number.get(120) or by_number.get(121))
    add("recent episode", by_number.get(positive_numbers[-1]) if positive_numbers else None)
    add("governed public-feed re-release", by_number.get(83))

    def content_score(row: Mapping[str, Any], patterns: Sequence[str]) -> int:
        content = " ".join(
            [
                _text(row.get("episodeTitle")),
                *(
                    _text(item.get("summary"))
                    for item in row.get("structuredItems", ())
                ),
            ]
        ).casefold()
        return sum(content.count(pattern.casefold()) for pattern in patterns)

    unselected = lambda: [
        row
        for row in packages
        if all(_identifier(row, "episodeId") != _identifier(existing, "episodeId") for _, existing in selected)
    ]

    for reason, patterns in (
        ("technical episode", ("cyber", "network", "technical", "infrastructure")),
        ("institutional episode", ("institution", "governance", "organization", "military")),
        ("influence episode", ("influence", "propaganda", "disinformation", "information operation")),
        ("AI-related episode", ("artificial intelligence", "machine learning", " ai ")),
    ):
        candidates = sorted(
            unselected(),
            key=lambda row: (
                -content_score(row, patterns),
                _identifier(row, "episodeId"),
            ),
        )
        add(reason, candidates[0] if candidates and content_score(candidates[0], patterns) else None)

    low_item_candidates = sorted(
        unselected(),
        key=lambda row: (int(row.get("itemCount") or 0), _identifier(row, "episodeId")),
    )
    add("unusual low-item episode", low_item_candidates[0] if low_item_candidates else None)

    if len(selected) < 10:
        for row in sorted(unselected(), key=lambda value: _identifier(value, "episodeId")):
            add("additional coverage case", row)
            if len(selected) >= 10:
                break
    if len(selected) != 10:
        raise ValueError(f"Representative pilot must contain 10 episodes; found {len(selected)}.")
    return [
        {
            "selectionReason": reason,
            **build_grounded_summary(package),
            "episodeTitle": _text(package.get("episodeTitle")),
        }
        for reason, package in selected
    ]


def validate_frozen_summaries(
    summaries: Sequence[Mapping[str, Any]],
    episodes: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Validate and copy the frozen public summary product."""

    episodes_by_id = {
        _identifier(row, "episodeId"): row
        for row in episodes
    }
    episode_ids = set(episodes_by_id)
    summary_ids = [_identifier(row, "episodeId") for row in summaries]
    if len(summaries) != len(episodes) or set(summary_ids) != episode_ids:
        raise ValueError("Frozen summaries must cover every canonical episode exactly once.")
    if len(summary_ids) != len(set(summary_ids)):
        raise ValueError("Frozen episode summary IDs must be unique.")
    allowed_fields = {
        "episodeId",
        "summary",
        "keyTopics",
        "whyItMatters",
        "sourceItemCount",
        "focalItemCount",
        "contextualItemCount",
        "generationMethod",
    }
    validated: list[dict[str, Any]] = []
    for source in summaries:
        missing = allowed_fields - set(source)
        unexpected = set(source) - allowed_fields
        if missing or unexpected:
            raise ValueError(
                f"Frozen summary {_identifier(source, 'episodeId')} has an invalid field set; "
                f"missing: {', '.join(sorted(missing)) or 'none'}; "
                f"unexpected: {', '.join(sorted(unexpected)) or 'none'}."
            )
        episode_id = _identifier(source, "episodeId")
        summary = _text(source.get("summary"))
        topics = [_text(value) for value in source.get("keyTopics", ()) if _text(value)]
        why_it_matters = _text(source.get("whyItMatters"))
        source_item_count = int(source.get("sourceItemCount") or 0)
        focal_item_count = int(source.get("focalItemCount") or 0)
        contextual_item_count = int(source.get("contextualItemCount") or 0)
        generation_method = _text(source.get("generationMethod"))
        if not summary or not topics or not why_it_matters or source_item_count <= 0:
            raise ValueError(
                f"Frozen summary {episode_id} is incomplete or ungrounded."
            )
        word_count = len(summary.split())
        if not 100 <= word_count <= 180:
            raise ValueError(
                f"Frozen summary {episode_id} must contain 100-180 words; found {word_count}."
            )
        if not 3 <= len(topics) <= 6:
            raise ValueError(
                f"Frozen summary {episode_id} must have 3-6 key topics."
            )
        if len({topic.casefold() for topic in topics}) != len(topics):
            raise ValueError(f"Frozen summary {episode_id} contains duplicate key topics.")
        if (
            focal_item_count < 0
            or contextual_item_count < 0
            or source_item_count != focal_item_count + contextual_item_count
        ):
            raise ValueError(
                f"Frozen summary {episode_id} has inconsistent grounding counts."
            )
        expected_item_count = int(
            episodes_by_id[episode_id].get("reconciledSensitivityItemCount") or 0
        )
        if source_item_count != expected_item_count:
            raise ValueError(
                f"Frozen summary {episode_id} grounding count does not match its canonical episode."
            )
        if generation_method != REVIEWED_SUMMARY_METHOD:
            raise ValueError(
                f"Frozen summary {episode_id} must use generation method "
                f"{REVIEWED_SUMMARY_METHOD}."
            )
        validated.append(
            {
                "episodeId": episode_id,
                "summary": summary,
                "keyTopics": topics,
                "whyItMatters": why_it_matters,
                "sourceItemCount": source_item_count,
                "focalItemCount": focal_item_count,
                "contextualItemCount": contextual_item_count,
                "generationMethod": generation_method,
            }
        )
    return sorted(validated, key=lambda row: row["episodeId"])


def private_package_without_copy(
    package: Mapping[str, Any],
) -> dict[str, Any]:
    """Small helper used by QA tooling to avoid mutating shared package data."""

    return deepcopy(dict(package))


__all__ = [
    "EPISODE_PRODUCT_SCHEMA_VERSION",
    "EPISODE_RELATIONSHIP_SCHEMA",
    "REVIEWED_SUMMARY_METHOD",
    "SUMMARY_METHOD",
    "build_episode_relationships",
    "build_grounded_summaries",
    "build_grounded_summary",
    "build_private_source_packages",
    "build_summary_authoring_inputs",
    "canonical_episode_sources",
    "episode_relationship_payload",
    "retained_canonical_items",
    "select_representative_pilot",
    "validate_frozen_summaries",
]
