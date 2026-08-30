"""Normalize extracted workbook tables into governed entity collections."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from copy import deepcopy
from typing import Any, Iterable, Mapping

from .sources import SourceValidationError
from .utils import (
    as_bool,
    as_int,
    as_number,
    deterministic_id,
    embedded_reference_ids,
    identifier,
    literal_list,
    natural_key,
    normalize_text,
    normalized_key,
    sort_records,
    source_ref,
    split_values,
    stable_unique,
)


COLLECTION_KEYS = (
    "artifacts",
    "episodes",
    "items",
    "item_tags",
    "categories",
    "clusters",
    "item_cluster_assignments",
    "cluster_summaries",
    "meta_clusters",
    "cluster_meta_mappings",
    "themes",
    "theme_meta_mappings",
    "theme_cluster_evidence",
    "tensions",
    "tension_mappings",
    "meta_narratives",
    "category_summaries",
    "category_findings",
    "scenarios",
    "scenario_pathways",
    "scenario_indicators",
    "scenario_actions",
    "evidence_links",
    "review_flags",
)

REQUIRED_TABLE_KEYS = (
    "codebook_clusters",
    "master_items",
    "master_focal_items",
    "drill_down_assignments",
    "cluster_summaries",
    "cluster_theme_details",
    "cluster_representative_items",
    "meta_clusters",
    "cluster_meta_mappings",
    "meta_cluster_evidence",
    "meta_review_queue",
    "themes",
    "theme_meta_mappings",
    "theme_cluster_evidence",
    "theme_cooccurrence",
    "theme_representative_items",
    "theme_review_queue",
    "tensions",
    "tension_evidence",
    "tension_mappings",
    "tension_review_queue",
    "meta_narratives",
    "category_summaries",
    "category_findings",
    "scenarios",
    "scenario_pathways",
    "scenario_indicators",
    "scenario_actions",
    "synthesis_review_queue",
)


def _required_id(row: Mapping[str, Any], field: str, entity: str) -> str:
    value = identifier(row.get(field))
    if value is None:
        source = source_ref(row)
        raise SourceValidationError(
            f"{source['fileName']} / {source['sheet']} row {source['rowNumber']}: "
            f"{entity} is missing required source ID field {field!r}."
        )
    return value


def _unique_source_ids(rows: Iterable[Mapping[str, Any]], field: str, entity: str) -> None:
    seen: dict[str, Mapping[str, Any]] = {}
    errors: list[str] = []
    for row in rows:
        value = _required_id(row, field, entity)
        if value in seen:
            first = source_ref(seen[value])
            second = source_ref(row)
            errors.append(
                f"Duplicate {entity} ID {value!r}: {first['fileName']} / "
                f"{first['sheet']} row {first['rowNumber']} and "
                f"{second['fileName']} / {second['sheet']} row {second['rowNumber']}."
            )
        else:
            seen[value] = row
    if errors:
        raise SourceValidationError(errors)


def _known_ids(value: Any, known_ids: Iterable[str]) -> list[str]:
    text = normalize_text(value)
    if text is None:
        return []
    matches: list[tuple[int, str]] = []
    for known_id in known_ids:
        match = re.search(
            rf"(?<![A-Za-z0-9]){re.escape(known_id)}(?![A-Za-z0-9])",
            text,
            flags=re.IGNORECASE,
        )
        if match:
            matches.append((match.start(), known_id))
    return [known_id for _, known_id in sorted(matches, key=lambda item: (item[0], natural_key(item[1])))]


def _category_names(value: Any) -> list[str]:
    return split_values(value, (";",), drop_missing_tokens=True)


def _reference_names(value: Any) -> list[str]:
    return split_values(value, (";",), drop_missing_tokens=True)


def _item_ids(value: Any) -> list[str]:
    """Read numeric canonical item IDs, including malformed legacy list cells."""

    text = normalize_text(value)
    if text is None:
        return []
    # Several synthesis cells mix semicolon lists with fragments such as
    # ``732','1852`` or a trailing comma.  Item IDs are governed numeric IDs,
    # so token extraction is safer and more complete than delimiter guessing.
    return stable_unique(re.findall(r"(?<!\d)\d+(?!\d)", text))


def _portable_artifacts(extracted: Mapping[str, Any]) -> list[dict[str, Any]]:
    canonical_roles = {
        "codebook.xlsx": "canonical-cluster-codebook",
        "master_extractions.xlsx": "canonical-items-and-episode-provenance",
        "drill_down.xlsx": "canonical-item-cluster-assignments",
        "drill_up_cluster_summaries.xlsx": "canonical-cluster-synthesis",
        "drill_up_meta_clusters.xlsx": "canonical-meta-clusters-and-mappings",
        "cross_cutting_themes.xlsx": "canonical-cross-cutting-themes",
        "tensions_debates_rebuilt.xlsx": "canonical-tensions-and-debates",
        "final_synthesis.xlsx": "canonical-narratives-findings-and-scenarios",
    }
    inventory_by_artifact: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for sheet in extracted.get("sheetInventory", []):
        inventory_by_artifact[str(sheet["artifactId"])].append(
            {
                "name": sheet["sheet"],
                "rowCount": sheet["rowCount"],
                "columnCount": sheet["columnCount"],
                "headerRow": sheet["headerRow"],
                "headers": list(sheet["headers"]),
                "canonicalTable": sheet["canonicalTable"],
            }
        )
    artifacts: list[dict[str, Any]] = []
    for source in extracted.get("artifacts", []):
        record = {
            "artifactId": source["artifactId"],
            "fileName": source["fileName"],
            "canonicalRole": canonical_roles[source["fileName"]],
            "sha256": source["sha256"],
            "byteSize": source["byteSize"],
            "sheets": sorted(
                inventory_by_artifact.get(source["artifactId"], []),
                key=lambda sheet: natural_key(sheet["name"]),
            ),
        }
        artifacts.append(record)
    return sort_records(artifacts, "artifactId")


class _Relations:
    def __init__(self) -> None:
        self._evidence: dict[tuple[str, ...], dict[str, Any]] = {}
        self._reviews: dict[tuple[str, ...], dict[str, Any]] = {}

    @staticmethod
    def _append_source(record: dict[str, Any], source: Mapping[str, Any]) -> None:
        portable = dict(source)
        if portable not in record["sources"]:
            record["sources"].append(portable)

    def evidence(
        self,
        source_entity_type: str,
        source_entity_id: str,
        target_entity_type: str,
        target_entity_id: str,
        role: str,
        source: Mapping[str, Any],
        *,
        note: str | None = None,
        rank: int | None = None,
    ) -> None:
        key = (
            source_entity_type,
            source_entity_id,
            target_entity_type,
            target_entity_id,
            role,
        )
        record = self._evidence.get(key)
        if record is None:
            record = {
                "evidenceLinkId": deterministic_id("EVL", *key),
                "sourceEntityType": source_entity_type,
                "sourceEntityId": source_entity_id,
                "targetEntityType": target_entity_type,
                "targetEntityId": target_entity_id,
                "evidenceRole": role,
                "rank": rank,
                "notes": [],
                "sources": [],
            }
            self._evidence[key] = record
        if note and note not in record["notes"]:
            record["notes"].append(note)
        if record["rank"] is None and rank is not None:
            record["rank"] = rank
        self._append_source(record, source)

    def review(
        self,
        entity_type: str,
        entity_id: str,
        flag_type: str,
        source: Mapping[str, Any],
        *,
        reason: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        details: str | None = None,
    ) -> None:
        semantic_reason = reason or details or "Source record requires review."
        key = (entity_type, entity_id, flag_type, normalized_key(semantic_reason))
        record = self._reviews.get(key)
        if record is None:
            record = {
                "reviewFlagId": deterministic_id("RVW", *key),
                "entityType": entity_type,
                "entityId": entity_id,
                "flagType": flag_type,
                "reason": reason,
                "status": status,
                "priority": priority,
                "details": details,
                "sources": [],
            }
            self._reviews[key] = record
        self._append_source(record, source)

    def evidence_records(self, valid_ids: Mapping[str, set[str]]) -> list[dict[str, Any]]:
        records = []
        for record in self._evidence.values():
            candidate = deepcopy(record)
            candidate["targetResolved"] = candidate["targetEntityId"] in valid_ids.get(
                candidate["targetEntityType"], set()
            )
            candidate["sources"] = sorted(
                candidate["sources"],
                key=lambda source: (
                    natural_key(source["artifactId"]),
                    natural_key(source["sheet"]),
                    source["rowNumber"],
                ),
            )
            records.append(candidate)
        return sort_records(records, "evidenceLinkId")

    def review_records(self) -> list[dict[str, Any]]:
        records = []
        for record in self._reviews.values():
            candidate = deepcopy(record)
            candidate["sources"] = sorted(
                candidate["sources"],
                key=lambda source: (
                    natural_key(source["artifactId"]),
                    natural_key(source["sheet"]),
                    source["rowNumber"],
                ),
            )
            records.append(candidate)
        return sort_records(records, "reviewFlagId")


def normalize_sources(extracted: Mapping[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Build deterministic, provenance-bearing normalized entity collections."""

    if not isinstance(extracted, Mapping) or not isinstance(extracted.get("tables"), Mapping):
        raise SourceValidationError("extract_sources output is required.")
    tables = extracted["tables"]
    missing = sorted(set(REQUIRED_TABLE_KEYS) - set(tables))
    if missing:
        raise SourceValidationError(f"Extracted data is missing canonical tables: {missing}.")

    relations = _Relations()

    # Categories are governed by the cluster codebook for focal material and by
    # the canonical item table for contextual material.
    focal_category_rows: dict[str, Mapping[str, Any]] = {}
    for row in tables["codebook_clusters"]:
        name = normalize_text(row.get("Category"))
        if name:
            focal_category_rows.setdefault(normalized_key(name), row)
    master_category_rows: dict[str, Mapping[str, Any]] = {}
    for row in tables["master_items"]:
        name = normalize_text(row.get("category"))
        if name:
            master_category_rows.setdefault(normalized_key(name), row)
    category_names = {
        key: normalize_text(row.get("Category"))
        for key, row in focal_category_rows.items()
    }
    category_names.update(
        {
            key: normalize_text(row.get("category"))
            for key, row in master_category_rows.items()
            if key not in category_names
        }
    )
    category_ids = {
        key: deterministic_id("CAT", name)
        for key, name in category_names.items()
        if name is not None
    }

    # Canonical items and derived episodes.
    _unique_source_ids(tables["master_items"], "ID", "item")
    focal_ids = {_required_id(row, "ID", "focal item") for row in tables["master_focal_items"]}
    canonical_ids = {_required_id(row, "ID", "item") for row in tables["master_items"]}
    missing_focal_ids = sorted(focal_ids - canonical_ids, key=natural_key)
    if missing_focal_ids:
        raise SourceValidationError(
            f"Focal-item sheet contains IDs absent from canonical MASTER: {missing_focal_ids[:20]}."
        )

    episode_accumulator: dict[str, dict[str, Any]] = {}
    items: list[dict[str, Any]] = []
    item_tags: list[dict[str, Any]] = []
    item_by_id: dict[str, dict[str, Any]] = {}
    for row in tables["master_items"]:
        item_id = _required_id(row, "ID", "item")
        category_name = normalize_text(row.get("category"))
        category_key = normalized_key(category_name)
        category_id = category_ids.get(category_key)
        if category_id is None:
            raise SourceValidationError(f"Item {item_id}: category is empty or unregistered.")
        title = normalize_text(row.get("episode_title"))
        source_file = normalize_text(row.get("source_file"))
        podcast = normalize_text(row.get("podcast"))
        if source_file:
            episode_id = deterministic_id("EPI", source_file)
        else:
            episode_id = deterministic_id("EPI", podcast, title)
        scope = "focal" if item_id in focal_ids else "contextual"
        episode = episode_accumulator.get(episode_id)
        if episode is None:
            episode = {
                "episodeId": episode_id,
                "podcast": podcast,
                "episodeTitle": title,
                "sourceFile": source_file,
                "itemCount": 0,
                "focalItemCount": 0,
                "contextualItemCount": 0,
                "source": source_ref(row),
            }
            episode_accumulator[episode_id] = episode
        elif (episode["podcast"], episode["episodeTitle"], episode["sourceFile"]) != (
            podcast,
            title,
            source_file,
        ):
            raise SourceValidationError(
                f"Episode identity collision for {episode_id}: source_file is not unique."
            )
        episode["itemCount"] += 1
        episode[f"{scope}ItemCount"] += 1

        record = {
            "itemId": item_id,
            "episodeId": episode_id,
            "categoryId": category_id,
            "categoryName": category_name,
            "scope": scope,
            "item": normalize_text(row.get("item")),
            "summary": normalize_text(row.get("summary")),
            "strategicSignificance": normalize_text(row.get("strategic_significance")),
            "operationalImplications": normalize_text(row.get("operational_implications")),
            "evidenceExcerpt": normalize_text(row.get("evidence_quote")),
            "speaker": normalize_text(row.get("speaker")),
            "confidence": normalize_text(row.get("confidence")),
            "episodeRelevanceScore": as_number(row.get("episode_relevance_score")),
            "noveltyScore": as_number(row.get("novelty_score")),
            "actionabilityScore": as_number(row.get("actionability_score")),
            "timeHorizon": normalize_text(row.get("time_horizon")),
            "source": source_ref(row),
        }
        items.append(record)
        item_by_id[item_id] = record
        for tag in split_values(row.get("relevance_tags"), (";", ","), drop_missing_tokens=True):
            item_tags.append(
                {
                    "itemTagId": deterministic_id("ITG", item_id, tag),
                    "itemId": item_id,
                    "tag": tag,
                    "normalizedTag": normalized_key(tag),
                    "source": source_ref(row),
                }
            )
    episodes = sort_records(episode_accumulator.values(), "episodeId")
    items = sort_records(items, "itemId")
    item_tags = sort_records(item_tags, "itemTagId")

    # Canonical cluster codebook.
    _unique_source_ids(tables["codebook_clusters"], "ID", "cluster")
    clusters: list[dict[str, Any]] = []
    cluster_by_id: dict[str, dict[str, Any]] = {}
    cluster_ids_by_name: dict[str, list[str]] = defaultdict(list)
    for row in tables["codebook_clusters"]:
        cluster_id = _required_id(row, "ID", "cluster")
        category_name = normalize_text(row.get("Category"))
        category_id = category_ids.get(normalized_key(category_name))
        record = {
            "clusterId": cluster_id,
            "categoryId": category_id,
            "categoryName": category_name,
            "name": normalize_text(row.get("Intermediate Cluster")),
            "definition": normalize_text(row.get("Definition")),
            "inclusionCriteria": normalize_text(row.get("Inclusion Criteria")),
            "exclusionCriteria": normalize_text(row.get("Exclusion Criteria")),
            "nearNeighborDistinctions": normalize_text(row.get("Near-Neighbor Distinctions")),
            "anchorExamples": split_values(row.get("Anchor Examples"), (";",)),
            "source": source_ref(row),
        }
        clusters.append(record)
        cluster_by_id[cluster_id] = record
        if record["name"]:
            cluster_ids_by_name[normalized_key(record["name"])].append(cluster_id)
    clusters = sort_records(clusters, "clusterId")

    item_counts = Counter(record["categoryId"] for record in items)
    cluster_counts = Counter(record["categoryId"] for record in clusters)
    categories: list[dict[str, Any]] = []
    for key, name in category_names.items():
        category_id = category_ids[key]
        source_row = focal_category_rows.get(key) or master_category_rows[key]
        scope = "focal" if key in focal_category_rows else "contextual"
        categories.append(
            {
                "categoryId": category_id,
                "name": name,
                "scope": scope,
                "itemCount": item_counts[category_id],
                "clusterCount": cluster_counts[category_id],
                "source": source_ref(source_row),
            }
        )
    categories = sort_records(categories, "categoryId")

    # Drill-down rows contain copied item text; only their IDs and governed
    # coding fields are retained, resolving to the canonical MASTER item.
    assignments: list[dict[str, Any]] = []
    assignment_ids: set[str] = set()
    for row in tables["drill_down_assignments"]:
        item_id = _required_id(row, "ID", "assignment item")
        canonical_item = item_by_id.get(item_id)
        copied_mismatch = canonical_item is not None and (
            normalize_text(row.get("category")) != canonical_item["categoryName"]
            or normalize_text(row.get("item")) != canonical_item["item"]
        )
        primary_cluster_id = _required_id(
            row, "primary_cluster_id", "primary assignment"
        )
        raw_secondary_cluster_id = identifier(row.get("secondary_cluster_id"))
        secondary_is_none = normalized_key(raw_secondary_cluster_id) == "none"
        secondary_cluster_id = None if secondary_is_none else raw_secondary_cluster_id
        assignment_id = deterministic_id(
            "ICA", item_id, primary_cluster_id, secondary_cluster_id or "NONE"
        )
        if assignment_id in assignment_ids:
            raise SourceValidationError(f"Duplicate assignment row for item {item_id}.")
        assignment_ids.add(assignment_id)
        record = {
            "assignmentId": assignment_id,
            "itemId": item_id,
            "categoryId": canonical_item["categoryId"] if canonical_item else category_ids.get(normalized_key(row.get("category"))),
            "primaryClusterId": primary_cluster_id,
            "primaryClusterName": normalize_text(row.get("primary_cluster_name")),
            "primaryRationale": normalize_text(row.get("primary_rationale")),
            "secondaryClusterId": secondary_cluster_id,
            "secondaryClusterName": None if secondary_is_none else normalize_text(row.get("secondary_cluster_name")),
            "secondaryRationale": None if secondary_is_none else normalize_text(row.get("secondary_rationale")),
            "secondaryIsNone": secondary_is_none,
            "confidence": normalize_text(row.get("confidence")),
            "ambiguityFlag": as_bool(row.get("ambiguity_flag")),
            "ambiguityType": normalize_text(row.get("ambiguity_type")),
            "alternativeClusterIds": split_values(
                row.get("alternative_cluster_ids"), (";",), drop_missing_tokens=True
            ),
            "alternativeClusterNames": split_values(
                row.get("alternative_cluster_names"), (";",), drop_missing_tokens=True
            ),
            "reviewRequired": as_bool(row.get("review_required")),
            "reviewReason": normalize_text(row.get("review_reason")),
            "coder": normalize_text(row.get("coder")),
            "model": normalize_text(row.get("model")),
            "promptVersion": normalize_text(row.get("prompt_version")),
            "codebookVersion": normalize_text(row.get("codebook_version")),
            "codedTimestamp": normalize_text(row.get("coded_timestamp")),
            "source": source_ref(row),
        }
        assignments.append(record)
        if record["reviewRequired"]:
            relations.review(
                "itemClusterAssignment", assignment_id, "reviewRequired", source_ref(row),
                reason=record["reviewReason"], status="pending",
            )
        if record["ambiguityFlag"]:
            relations.review(
                "itemClusterAssignment", assignment_id, "ambiguity", source_ref(row),
                reason=record["ambiguityType"], status="pending",
                details="; ".join(record["alternativeClusterIds"]) or None,
            )
        if canonical_item is None:
            relations.review(
                "item", item_id, "unresolvedCanonicalItem", source_ref(row),
                reason="Assignment source ID does not resolve to canonical MASTER item.",
                status="pending",
            )
        elif copied_mismatch:
            relations.review(
                "item", item_id, "copiedRecordMismatch", source_ref(row),
                reason="Copied drill-down item/category text differs from canonical MASTER; canonical record retained.",
                status="pending",
            )
    assignments = sort_records(assignments, "itemId", "assignmentId")

    # Cluster synthesis with recurring subthemes retained as structured detail.
    themes_by_cluster: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in tables["cluster_theme_details"]:
        cluster_id = _required_id(row, "cluster_id", "cluster theme")
        theme_number = as_int(row.get("theme_number"))
        cluster_theme_id = deterministic_id("CLT", cluster_id, theme_number, row.get("theme_name"))
        evidence_ids = _item_ids(row.get("evidence_item_ids"))
        themes_by_cluster[cluster_id].append(
            {
                "clusterThemeId": cluster_theme_id,
                "themeNumber": theme_number,
                "name": normalize_text(row.get("theme_name")),
                "description": normalize_text(row.get("theme_description")),
                "evidenceItemIds": evidence_ids,
                "primarySupportCountEstimate": as_int(row.get("primary_support_count_estimate")),
                "secondarySupportCountEstimate": as_int(row.get("secondary_support_count_estimate")),
                "importance": normalize_text(row.get("importance")),
                "source": source_ref(row),
            }
        )
        for item_id in evidence_ids:
            relations.evidence(
                "cluster", cluster_id, "item", item_id, "clusterThemeEvidence",
                source_ref(row), note=normalize_text(row.get("theme_name")),
            )
    for value in themes_by_cluster.values():
        value.sort(key=lambda record: (record["themeNumber"] or 0, natural_key(record["clusterThemeId"])))

    cluster_summaries: list[dict[str, Any]] = []
    for row in tables["cluster_summaries"]:
        cluster_id = _required_id(row, "cluster_id", "cluster summary")
        representative_ids = _item_ids(row.get("representative_item_ids"))
        cluster_summaries.append(
            {
                "clusterSummaryId": deterministic_id("CLS", cluster_id),
                "clusterId": cluster_id,
                "categoryId": category_ids.get(normalized_key(row.get("category"))),
                "clusterName": normalize_text(row.get("cluster_name")),
                "primaryCount": as_int(row.get("primary_count")),
                "secondaryCount": as_int(row.get("secondary_count")),
                "weightedCount": as_number(row.get("weighted_count")),
                "summary": normalize_text(row.get("cluster_summary")),
                "strategicSignificance": normalize_text(row.get("strategic_significance_synthesis")),
                "operationalImplications": normalize_text(row.get("operational_implications_synthesis")),
                "primarySecondaryDistinction": normalize_text(row.get("primary_vs_secondary_distinction")),
                "representativeItemIds": representative_ids,
                "edgeCasesOrAmbiguities": normalize_text(row.get("edge_cases_or_ambiguities")),
                "candidateMetaClusterAffinities": split_values(row.get("candidate_meta_cluster_affinities"), (";",)),
                "reviewQuestions": split_values(row.get("review_questions"), ("|",)),
                "summaryConfidence": normalize_text(row.get("summary_confidence")),
                "recurringThemes": themes_by_cluster.get(cluster_id, []),
                "keyThemes": [
                    theme["name"]
                    for theme in themes_by_cluster.get(cluster_id, [])
                    if theme["name"]
                ],
                "source": source_ref(row),
            }
        )
        for rank, item_id in enumerate(representative_ids, 1):
            relations.evidence(
                "cluster", cluster_id, "item", item_id, "representativeItem",
                source_ref(row), rank=rank,
            )
    for row in tables["cluster_representative_items"]:
        cluster_id = _required_id(row, "cluster_id", "cluster representative item")
        item_id = _required_id(row, "item_id", "cluster representative item")
        relations.evidence(
            "cluster", cluster_id, "item", item_id,
            normalize_text(row.get("assignment_role")) or "representativeItem",
            source_ref(row),
            note=normalize_text(row.get("summary")),
        )
    cluster_summaries = sort_records(cluster_summaries, "clusterId")

    # Meta-clusters and their source-authored mappings.
    _unique_source_ids(tables["meta_clusters"], "meta_cluster_id", "meta-cluster")
    meta_clusters: list[dict[str, Any]] = []
    meta_ids: set[str] = set()
    for row in tables["meta_clusters"]:
        meta_id = _required_id(row, "meta_cluster_id", "meta-cluster")
        meta_ids.add(meta_id)
        representative_ids = _item_ids(row.get("representative_item_ids"))
        meta_clusters.append(
            {
                "metaClusterId": meta_id,
                "categoryId": category_ids.get(normalized_key(row.get("category"))),
                "categoryName": normalize_text(row.get("category")),
                "name": normalize_text(row.get("meta_cluster_name")),
                "definition": normalize_text(row.get("definition")),
                "includedClusterIds": split_values(row.get("included_cluster_ids"), (";",), drop_missing_tokens=True),
                "includedClusterNames": split_values(row.get("included_cluster_names"), (";",), drop_missing_tokens=True),
                "rationale": normalize_text(row.get("rationale")),
                "nearNeighborDistinctions": normalize_text(row.get("near_neighbor_distinctions")),
                "representativeItemIds": representative_ids,
                "salience": normalize_text(row.get("salience")),
                "reviewPriority": normalize_text(row.get("review_priority")),
                "categorySynthesis": normalize_text(row.get("category_synthesis")),
                "reviewStatus": normalize_text(row.get("review_status")),
                "humanNotes": normalize_text(row.get("human_notes")),
                "runId": identifier(row.get("run_id")),
                "promptVersion": normalize_text(row.get("prompt_version")),
                "source": source_ref(row),
            }
        )
        for rank, item_id in enumerate(representative_ids, 1):
            relations.evidence(
                "metaCluster", meta_id, "item", item_id, "representativeItem",
                source_ref(row), rank=rank,
            )
    meta_clusters = sort_records(meta_clusters, "metaClusterId")

    cluster_meta_mappings: list[dict[str, Any]] = []
    for row in tables["cluster_meta_mappings"]:
        meta_id = _required_id(row, "meta_cluster_id", "cluster/meta mapping")
        cluster_id = _required_id(row, "cluster_id", "cluster/meta mapping")
        mapping_type = normalize_text(row.get("mapping_type"))
        cluster_meta_mappings.append(
            {
                "clusterMetaMappingId": deterministic_id("CMM", cluster_id, meta_id, mapping_type),
                "clusterId": cluster_id,
                "metaClusterId": meta_id,
                "categoryId": category_ids.get(normalized_key(row.get("category"))),
                "mappingType": mapping_type,
                "mappingRationale": normalize_text(row.get("mapping_rationale")),
                "reviewStatus": normalize_text(row.get("review_status")),
                "humanNotes": normalize_text(row.get("human_notes")),
                "runId": identifier(row.get("run_id")),
                "source": source_ref(row),
            }
        )
    cluster_meta_mappings = sort_records(cluster_meta_mappings, "clusterMetaMappingId")
    for row in tables["meta_cluster_evidence"]:
        meta_id = _required_id(row, "meta_cluster_id", "meta-cluster evidence")
        item_id = _required_id(row, "representative_item_id", "meta-cluster evidence")
        relations.evidence(
            "metaCluster", meta_id, "item", item_id,
            normalize_text(row.get("evidence_role")) or "representativeItem",
            source_ref(row),
        )
    for row in tables["meta_review_queue"]:
        entity_id = identifier(row.get("object_id")) or deterministic_id(
            "UNRES", row.get("object_type"), row.get("object_name")
        )
        relations.review(
            normalize_text(row.get("object_type")) or "metaCluster",
            entity_id,
            "sourceReviewQueue",
            source_ref(row),
            reason=normalize_text(row.get("reason")),
            status=normalize_text(row.get("review_status")),
            details=normalize_text(row.get("human_notes")),
        )

    # Cross-cutting themes and mappings.
    _unique_source_ids(tables["themes"], "theme_id", "theme")
    themes: list[dict[str, Any]] = []
    theme_ids: set[str] = set()
    for row in tables["themes"]:
        theme_id = _required_id(row, "theme_id", "theme")
        theme_ids.add(theme_id)
        linked_names = split_values(row.get("linked_intermediate_clusters"), (";",), drop_missing_tokens=True)
        linked_cluster_ids = stable_unique(
            cluster_ids_by_name[normalized_key(name)][0]
            for name in linked_names
            if len(cluster_ids_by_name.get(normalized_key(name), [])) == 1
        )
        representative_ids = _item_ids(row.get("representative_item_ids"))
        record = {
            "themeId": theme_id,
            "name": normalize_text(row.get("theme_name")),
            "definition": normalize_text(row.get("definition")),
            "categoryNames": _category_names(row.get("categories_present")),
            "categoryIds": [category_ids[normalized_key(name)] for name in _category_names(row.get("categories_present")) if normalized_key(name) in category_ids],
            "categoryCount": as_int(row.get("category_count")),
            "linkedMetaClusterIds": split_values(row.get("linked_meta_cluster_ids"), (";",), drop_missing_tokens=True),
            "linkedMetaClusterNames": split_values(row.get("linked_meta_cluster_names"), (";",), drop_missing_tokens=True),
            "linkedClusterIds": linked_cluster_ids,
            "linkedClusterNames": linked_names,
            "crossCategoryLogic": normalize_text(row.get("cross_category_logic")),
            "cooccurrenceEvidence": normalize_text(row.get("cooccurrence_evidence")),
            "strategicSignificance": normalize_text(row.get("strategic_significance")),
            "operationalImplications": normalize_text(row.get("operational_implications")),
            "boundaryConditions": normalize_text(row.get("boundary_conditions")),
            "relatedTensionNames": _reference_names(row.get("related_tensions_or_debates")),
            "relatedTensionIds": [],
            "representativeItemIds": representative_ids,
            "evidenceStrength": normalize_text(row.get("evidence_strength")),
            "reviewPriority": normalize_text(row.get("review_priority")),
            "reviewRequired": as_bool(row.get("review_required")),
            "reviewNotes": normalize_text(row.get("review_notes")),
            "humanReviewStatus": normalize_text(row.get("human_review_status")),
            "humanThemeName": normalize_text(row.get("human_theme_name")),
            "humanNotes": normalize_text(row.get("human_notes")),
            "source": source_ref(row),
        }
        themes.append(record)
        for rank, item_id in enumerate(representative_ids, 1):
            relations.evidence(
                "theme", theme_id, "item", item_id, "representativeItem",
                source_ref(row), rank=rank,
            )
        if record["reviewRequired"]:
            relations.review(
                "theme", theme_id, "reviewRequired", source_ref(row),
                reason=record["reviewNotes"], status=record["humanReviewStatus"],
                priority=record["reviewPriority"],
            )
    themes = sort_records(themes, "themeId")

    theme_meta_mappings: list[dict[str, Any]] = []
    for row in tables["theme_meta_mappings"]:
        theme_id = _required_id(row, "theme_id", "theme/meta mapping")
        meta_id = _required_id(row, "meta_cluster_id", "theme/meta mapping")
        theme_meta_mappings.append(
            {
                "themeMetaMappingId": deterministic_id("TMM", theme_id, meta_id),
                "themeId": theme_id,
                "metaClusterId": meta_id,
                "categoryId": category_ids.get(normalized_key(row.get("category"))),
                "mappingBasis": normalize_text(row.get("mapping_basis")),
                "humanReviewStatus": normalize_text(row.get("human_review_status")),
                "humanNotes": normalize_text(row.get("human_notes")),
                "source": source_ref(row),
            }
        )
    theme_meta_mappings = sort_records(theme_meta_mappings, "themeMetaMappingId")

    theme_cluster_evidence: list[dict[str, Any]] = []
    for row in tables["theme_cluster_evidence"]:
        theme_id = _required_id(row, "theme_id", "theme/cluster evidence")
        cluster_id = identifier(row.get("cluster_id"))
        evidence_note = normalize_text(row.get("evidence_note"))
        evidence_id = deterministic_id(
            "TCE", theme_id, cluster_id or "UNRESOLVED", evidence_note
        )
        theme_cluster_evidence.append(
            {
                "themeClusterEvidenceId": evidence_id,
                "themeId": theme_id,
                "clusterId": cluster_id,
                "unresolvedReference": cluster_id is None,
                "categoryId": category_ids.get(normalized_key(row.get("category"))),
                "clusterSummary": normalize_text(row.get("cluster_summary")),
                "strategicSignificance": normalize_text(row.get("strategic_significance")),
                "operationalImplications": normalize_text(row.get("operational_implications")),
                "evidenceNote": evidence_note,
                "source": source_ref(row),
            }
        )
        if cluster_id is None:
            relations.review(
                "themeClusterEvidence", evidence_id, "unresolvedClusterReference",
                source_ref(row), reason=evidence_note or (
                    "Theme-to-cluster evidence has no source-authored cluster ID."
                ), status="pending",
            )
    theme_cluster_evidence = sort_records(theme_cluster_evidence, "themeClusterEvidenceId")

    for row in tables["theme_representative_items"]:
        theme_id = _required_id(row, "theme_id", "theme representative item")
        item_id = _required_id(row, "item_id", "theme representative item")
        relations.evidence(
            "theme", theme_id, "item", item_id, "representativeItem",
            source_ref(row), note=normalize_text(row.get("summary")),
            rank=as_int(row.get("score")),
        )
    for row in tables["theme_cooccurrence"]:
        theme_id = _required_id(row, "theme_id", "theme cooccurrence")
        for item_id in _item_ids(row.get("example_item_ids")):
            if item_id:
                relations.evidence(
                    "theme", theme_id, "item", item_id, "cooccurrenceExample",
                    source_ref(row),
                    note=(
                        f"{normalize_text(row.get('primary_cluster_name'))} <-> "
                        f"{normalize_text(row.get('secondary_cluster_name'))}"
                    ),
                )
    for row in tables["theme_review_queue"]:
        theme_id = _required_id(row, "theme_id", "theme review")
        relations.review(
            "theme", theme_id, "sourceReviewQueue", source_ref(row),
            reason=normalize_text(row.get("review_reason")),
            priority=normalize_text(row.get("review_priority")),
            details=normalize_text(row.get("review_notes")) or normalize_text(row.get("suggested_action")),
        )

    # Canonical tensions come only from tensions_debates_rebuilt.xlsx.
    _unique_source_ids(tables["tensions"], "tension_id", "tension")
    tensions: list[dict[str, Any]] = []
    tension_ids: set[str] = set()
    tension_id_by_name: dict[str, str] = {}
    for row in tables["tensions"]:
        tension_id = _required_id(row, "tension_id", "tension")
        tension_ids.add(tension_id)
        name = normalize_text(row.get("tension_name"))
        if name:
            tension_id_by_name[normalized_key(name)] = tension_id
        cluster_names = _reference_names(row.get("clusters_involved"))
        cluster_ids = stable_unique(
            cluster_ids_by_name[normalized_key(cluster_name)][0]
            for cluster_name in cluster_names
            if len(cluster_ids_by_name.get(normalized_key(cluster_name), [])) == 1
        )
        pole_a_ids = _item_ids(row.get("supporting_item_ids_pole_a"))
        pole_b_ids = _item_ids(row.get("supporting_item_ids_pole_b"))
        record = {
            "tensionId": tension_id,
            "name": name,
            "description": normalize_text(row.get("description")),
            "poleALabel": normalize_text(row.get("pole_a_label")),
            "poleBLabel": normalize_text(row.get("pole_b_label")),
            "poleAAssumption": normalize_text(row.get("pole_a_assumption")),
            "poleBAssumption": normalize_text(row.get("pole_b_assumption")),
            "tensionLevel": normalize_text(row.get("tension_level")),
            "categoryNames": _category_names(row.get("categories_involved")),
            "categoryIds": [category_ids[normalized_key(value)] for value in _category_names(row.get("categories_involved")) if normalized_key(value) in category_ids],
            "categoryCount": as_int(row.get("category_count")),
            "clusterNames": cluster_names,
            "clusterIds": cluster_ids,
            "clusterCount": as_int(row.get("cluster_count")),
            "supportingItemIdsPoleA": pole_a_ids,
            "supportingItemIdsPoleB": pole_b_ids,
            "sourceCandidateIds": split_values(row.get("source_candidate_ids"), (";",), drop_missing_tokens=True),
            "candidateCount": as_int(row.get("candidate_count")),
            "evidenceStrength": normalize_text(row.get("evidence_strength")),
            "confidence": normalize_text(row.get("confidence")),
            "reviewPriority": normalize_text(row.get("review_priority")),
            "keyTerms": split_values(row.get("key_terms"), (";", ","), drop_missing_tokens=True),
            "evidenceRationale": normalize_text(row.get("evidence_rationale")),
            "selectionMethod": normalize_text(row.get("selection_method")),
            "reviewRequired": as_bool(row.get("review_required")),
            "humanReviewStatus": normalize_text(row.get("human_review_status")),
            "humanNotes": normalize_text(row.get("human_notes")),
            "source": source_ref(row),
        }
        tensions.append(record)
        for rank, item_id in enumerate(pole_a_ids, 1):
            relations.evidence(
                "tension", tension_id, "item", item_id, "poleAEvidence",
                source_ref(row), rank=rank,
            )
        for rank, item_id in enumerate(pole_b_ids, 1):
            relations.evidence(
                "tension", tension_id, "item", item_id, "poleBEvidence",
                source_ref(row), rank=rank,
            )
        if record["reviewRequired"]:
            relations.review(
                "tension", tension_id, "reviewRequired", source_ref(row),
                reason="Source tension is marked review-required.",
                status=record["humanReviewStatus"], priority=record["reviewPriority"],
            )
    tensions = sort_records(tensions, "tensionId")

    for theme in themes:
        theme["relatedTensionIds"] = stable_unique(
            tension_id_by_name[normalized_key(name)]
            for name in theme["relatedTensionNames"]
            if normalized_key(name) in tension_id_by_name
        )

    tension_mappings: list[dict[str, Any]] = []
    for row in tables["tension_mappings"]:
        tension_id = _required_id(row, "tension_id", "tension mapping")
        mapped_id = _required_id(row, "mapped_id", "tension mapping target")
        mapping_type = normalize_text(row.get("mapping_type"))
        tension_mappings.append(
            {
                "tensionMappingId": deterministic_id("TNM", tension_id, mapping_type, mapped_id),
                "tensionId": tension_id,
                "mappedEntityType": mapping_type,
                "mappedId": mapped_id,
                "mappedName": normalize_text(row.get("mapped_name")),
                "mappingStrength": as_number(row.get("mapping_strength")),
                "mappingBasis": normalize_text(row.get("mapping_basis")),
                "reviewStatus": normalize_text(row.get("review_status")),
                "humanNotes": normalize_text(row.get("human_notes")),
                "source": source_ref(row),
            }
        )
    tension_mappings = sort_records(tension_mappings, "tensionMappingId")
    tensions_by_theme: dict[str, list[str]] = defaultdict(list)
    for mapping in tension_mappings:
        if mapping["mappedEntityType"] == "cross_cutting_theme":
            tensions_by_theme[mapping["mappedId"]].append(mapping["tensionId"])
    for theme in themes:
        theme["relatedTensionIds"] = sorted(
            stable_unique(theme["relatedTensionIds"] + tensions_by_theme[theme["themeId"]]),
            key=natural_key,
        )
    for row in tables["tension_evidence"]:
        tension_id = _required_id(row, "tension_id", "tension evidence")
        rank = as_int(row.get("evidence_rank"))
        for field, role in (
            ("supporting_item_ids_pole_a", "poleAEvidence"),
            ("supporting_item_ids_pole_b", "poleBEvidence"),
        ):
            for item_id in _item_ids(row.get(field)):
                if item_id:
                    relations.evidence(
                        "tension", tension_id, "item", item_id, role,
                        source_ref(row), note=normalize_text(row.get("candidate_description")), rank=rank,
                    )
    for row in tables["tension_review_queue"]:
        tension_id = _required_id(row, "tension_id", "tension review")
        relations.review(
            "tension", tension_id, "sourceReviewQueue", source_ref(row),
            reason=normalize_text(row.get("review_reasons")),
            status=normalize_text(row.get("human_review_status")),
            priority=normalize_text(row.get("review_priority")),
            details=normalize_text(row.get("human_notes")) or normalize_text(row.get("suggested_action")),
        )

    # Final synthesis: preserve seven source narratives without manufacturing a
    # documented-but-absent eighth record.
    _unique_source_ids(tables["meta_narratives"], "narrative_id", "meta-narrative")
    meta_narratives: list[dict[str, Any]] = []
    for row in tables["meta_narratives"]:
        narrative_id = _required_id(row, "narrative_id", "meta-narrative")
        tension_names = _reference_names(row.get("supporting_tensions"))
        record = {
            "narrativeId": narrative_id,
            "name": normalize_text(row.get("narrative_name")),
            "shortVersion": normalize_text(row.get("short_version")),
            "coreClaim": normalize_text(row.get("core_claim")),
            "supportingThemeIds": embedded_reference_ids(row.get("supporting_cross_cutting_themes"), "theme_id") or _known_ids(row.get("supporting_cross_cutting_themes"), theme_ids),
            "supportingTensionNames": tension_names,
            "supportingTensionIds": stable_unique(tension_id_by_name[normalized_key(name)] for name in tension_names if normalized_key(name) in tension_id_by_name),
            "supportingMetaClusterIds": embedded_reference_ids(row.get("supporting_meta_clusters"), "meta_cluster_id") or _known_ids(row.get("supporting_meta_clusters"), meta_ids),
            "categoryNames": _category_names(row.get("categories_connected")),
            "categoryIds": [category_ids[normalized_key(name)] for name in _category_names(row.get("categories_connected")) if normalized_key(name) in category_ids],
            "representativeEvidence": normalize_text(row.get("representative_evidence")),
            "strategicSignificance": normalize_text(row.get("strategic_significance")),
            "operationalImplications": literal_list(row.get("operational_implications")),
            "caveats": normalize_text(row.get("caveats_or_boundary_conditions")),
            "confidence": normalize_text(row.get("confidence")),
            "reviewRequired": as_bool(row.get("review_required")),
            "source": source_ref(row),
        }
        meta_narratives.append(record)
        if record["reviewRequired"]:
            relations.review(
                "metaNarrative", narrative_id, "reviewRequired", source_ref(row),
                reason="Source meta-narrative is marked review-required.", status="pending",
            )
    meta_narratives = sort_records(meta_narratives, "narrativeId")

    category_summaries: list[dict[str, Any]] = []
    for row in tables["category_summaries"]:
        category_name = normalize_text(row.get("category"))
        category_id = category_ids.get(normalized_key(category_name))
        summary_id = deterministic_id("CGS", category_name)
        category_summaries.append(
            {
                "categorySummaryId": summary_id,
                "categoryId": category_id,
                "categoryName": category_name,
                "summary": normalize_text(row.get("category_summary")),
                "soWhat": normalize_text(row.get("category_so_what")),
                "source": source_ref(row),
            }
        )
    category_summaries = sort_records(category_summaries, "categorySummaryId")

    _unique_source_ids(tables["category_findings"], "finding_id", "category finding")
    category_findings: list[dict[str, Any]] = []
    for row in tables["category_findings"]:
        finding_id = _required_id(row, "finding_id", "category finding")
        record = {
            "findingId": finding_id,
            "categoryId": category_ids.get(normalized_key(row.get("category"))),
            "categoryName": normalize_text(row.get("category")),
            "name": normalize_text(row.get("finding_name")),
            "coreFinding": normalize_text(row.get("core_finding")),
            "supportingMetaClusterIds": embedded_reference_ids(row.get("supporting_meta_clusters"), "meta_cluster_id") or _known_ids(row.get("supporting_meta_clusters"), meta_ids),
            "supportingClusterIds": embedded_reference_ids(row.get("supporting_intermediate_clusters"), "cluster_id") or _known_ids(row.get("supporting_intermediate_clusters"), cluster_by_id),
            "strategicSignificance": normalize_text(row.get("strategic_significance")),
            "operationalImplications": literal_list(row.get("operational_implications")),
            "unresolvedQuestions": literal_list(row.get("unresolved_questions")),
            "caveats": literal_list(row.get("caveats")),
            "confidence": normalize_text(row.get("confidence")),
            "reviewRequired": as_bool(row.get("review_required")),
            "source": source_ref(row),
        }
        category_findings.append(record)
        if record["reviewRequired"]:
            relations.review(
                "categoryFinding", finding_id, "reviewRequired", source_ref(row),
                reason="Source category finding is marked review-required.", status="pending",
            )
    category_findings = sort_records(category_findings, "findingId")

    _unique_source_ids(tables["scenarios"], "scenario_id", "scenario")
    scenarios: list[dict[str, Any]] = []
    scenario_ids: set[str] = set()
    for row in tables["scenarios"]:
        scenario_id = _required_id(row, "scenario_id", "scenario")
        scenario_ids.add(scenario_id)
        tension_names = _reference_names(row.get("tensions_activated"))
        record = {
            "scenarioId": scenario_id,
            "name": normalize_text(row.get("scenario_name")),
            "timeframe": normalize_text(row.get("timeframe")),
            "scenarioType": normalize_text(row.get("scenario_type")),
            "coreScenario": normalize_text(row.get("core_scenario")),
            "drivingForces": literal_list(row.get("driving_forces")),
            "categoryNames": _category_names(row.get("categories_meshed")),
            "categoryIds": [category_ids[normalized_key(name)] for name in _category_names(row.get("categories_meshed")) if normalized_key(name) in category_ids],
            "themeIds": _known_ids(row.get("cross_cutting_themes_involved"), theme_ids),
            "tensionNames": tension_names,
            "tensionIds": stable_unique(tension_id_by_name[normalized_key(name)] for name in tension_names if normalized_key(name) in tension_id_by_name),
            "strategicImplications": literal_list(row.get("strategic_implications")),
            "operationalImplications": literal_list(row.get("operational_implications")),
            "researchQuestions": literal_list(row.get("research_questions")),
            "uncertaintyLevel": normalize_text(row.get("uncertainty_level")),
            "assumptions": literal_list(row.get("assumptions")),
            "alternativeOutcomes": literal_list(row.get("alternative_outcomes")),
            "reviewRequired": as_bool(row.get("review_required")),
            "source": source_ref(row),
        }
        scenarios.append(record)
        if record["reviewRequired"]:
            relations.review(
                "scenario", scenario_id, "reviewRequired", source_ref(row),
                reason="Source scenario is marked review-required.", status="pending",
            )
    scenarios = sort_records(scenarios, "scenarioId")

    scenario_pathways: list[dict[str, Any]] = []
    for row in tables["scenario_pathways"]:
        scenario_id = _required_id(row, "scenario_id", "scenario pathway")
        step_number = as_int(row.get("step_number"))
        scenario_pathways.append(
            {
                "pathwayId": deterministic_id("SCP", scenario_id, step_number, row.get("pathway_step")),
                "scenarioId": scenario_id,
                "stepNumber": step_number,
                "pathwayStep": normalize_text(row.get("pathway_step")),
                "source": source_ref(row),
            }
        )
    scenario_pathways = sort_records(scenario_pathways, "scenarioId", "stepNumber", "pathwayId")

    scenario_indicators: list[dict[str, Any]] = []
    indicator_ordinals: Counter[str] = Counter()
    for row in tables["scenario_indicators"]:
        scenario_id = _required_id(row, "scenario_id", "scenario indicator")
        indicator_ordinals[scenario_id] += 1
        indicator_text = normalize_text(row.get("indicator"))
        scenario_indicators.append(
            {
                "indicatorId": deterministic_id("SCI", scenario_id, indicator_text),
                "scenarioId": scenario_id,
                "ordinal": indicator_ordinals[scenario_id],
                "indicator": indicator_text,
                "source": source_ref(row),
            }
        )
    scenario_indicators = sort_records(scenario_indicators, "scenarioId", "ordinal", "indicatorId")

    scenario_actions: list[dict[str, Any]] = []
    action_ordinals: Counter[str] = Counter()
    for row in tables["scenario_actions"]:
        scenario_id = _required_id(row, "scenario_id", "scenario action")
        action_ordinals[scenario_id] += 1
        action_text = normalize_text(row.get("policy_or_practice_action"))
        scenario_actions.append(
            {
                "actionId": deterministic_id("SCA", scenario_id, action_text),
                "scenarioId": scenario_id,
                "ordinal": action_ordinals[scenario_id],
                "policyOrPracticeAction": action_text,
                "source": source_ref(row),
            }
        )
    scenario_actions = sort_records(scenario_actions, "scenarioId", "ordinal", "actionId")

    for row in tables["synthesis_review_queue"]:
        entity_id = identifier(row.get("record_id")) or deterministic_id(
            "UNRES", row.get("source_sheet"), row.get("issue")
        )
        relations.review(
            normalize_text(row.get("source_sheet")) or "finalSynthesis",
            entity_id,
            "sourceReviewQueue",
            source_ref(row),
            reason=normalize_text(row.get("issue")),
            status=normalize_text(row.get("status")),
        )

    # Preserve, but never fill, intermediate clusters absent from the source
    # meta-cluster mapping.
    mapped_cluster_ids = {record["clusterId"] for record in cluster_meta_mappings}
    for cluster in clusters:
        if cluster["clusterId"] not in mapped_cluster_ids:
            relations.review(
                "cluster", cluster["clusterId"], "unmappedMetaCluster",
                cluster["source"],
                reason="No source-authored cluster-to-meta mapping exists.",
                status="pending",
            )

    valid_ids = {
        "item": set(item_by_id),
        "cluster": set(cluster_by_id),
        "metaCluster": meta_ids,
        "theme": theme_ids,
        "tension": tension_ids,
        "scenario": scenario_ids,
    }
    evidence_links = relations.evidence_records(valid_ids)
    for link in evidence_links:
        if not link["targetResolved"]:
            relations.review(
                link["sourceEntityType"], link["sourceEntityId"], "unresolvedEvidenceReference",
                link["sources"][0],
                reason=(
                    f"Evidence target {link['targetEntityType']} "
                    f"{link['targetEntityId']} does not resolve."
                ),
                status="pending",
            )

    result = {
        "artifacts": _portable_artifacts(extracted),
        "episodes": episodes,
        "items": items,
        "item_tags": item_tags,
        "categories": categories,
        "clusters": clusters,
        "item_cluster_assignments": assignments,
        "cluster_summaries": cluster_summaries,
        "meta_clusters": meta_clusters,
        "cluster_meta_mappings": cluster_meta_mappings,
        "themes": themes,
        "theme_meta_mappings": theme_meta_mappings,
        "theme_cluster_evidence": theme_cluster_evidence,
        "tensions": tensions,
        "tension_mappings": tension_mappings,
        "meta_narratives": meta_narratives,
        "category_summaries": category_summaries,
        "category_findings": category_findings,
        "scenarios": scenarios,
        "scenario_pathways": scenario_pathways,
        "scenario_indicators": scenario_indicators,
        "scenario_actions": scenario_actions,
        "evidence_links": evidence_links,
        "review_flags": relations.review_records(),
    }
    if tuple(result) != COLLECTION_KEYS:
        raise AssertionError("Normalized collection contract drifted.")
    return result


__all__ = ("COLLECTION_KEYS", "normalize_sources")
