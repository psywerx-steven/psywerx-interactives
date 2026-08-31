"""Corpus reconciliation products and conservative support sensitivity.

This module is intentionally pure: callers supply the normalized dataset and
receive JSON-compatible in-memory products.  It never reads source files,
writes generated output, or changes the supplied records.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from typing import Any, Iterable, Mapping, Sequence

from .reconcile import (
    RECONCILIATION_METHOD_VERSION,
    RECONCILIATION_SCHEMA_VERSION,
    apply_episode_reconciliation,
    build_episode_reconciliation,
)
from .utils import natural_key, normalize_text, normalized_key


NEAR_ITEM_OVERLAP_THRESHOLD = 0.80
WEIGHTING_FORMULA = "2 * primaryCount + secondaryCount"
WEIGHTING_BASIS = (
    "The governed project methodology specifies a 2:1 primary-to-secondary "
    "cluster weighting."
)

_HIGHER_ORDER_COLLECTIONS = (
    ("metaCluster", "meta_clusters", "metaClusterId"),
    ("theme", "themes", "themeId"),
    ("tension", "tensions", "tensionId"),
    ("metaNarrative", "meta_narratives", "narrativeId"),
    ("categoryFinding", "category_findings", "findingId"),
    ("scenario", "scenarios", "scenarioId"),
)
_CANNOT_ASSESS_ENTITY_TYPES = frozenset(
    {"metaNarrative", "categoryFinding", "scenario"}
)


def _identifier(record: Mapping[str, Any], *fields: str) -> str:
    for field in fields:
        value = record.get(field)
        if value not in (None, ""):
            return str(value)
    return ""


def _pct_change(original: int | float, reconciled: int | float) -> float | None:
    if not original:
        return None
    return round(((reconciled - original) / original) * 100.0, 6)


def _pct_loss(original: int | float, reconciled: int | float) -> float | None:
    if not original:
        return None
    return round(((original - reconciled) / original) * 100.0, 6)


def _item_source_identity(item: Mapping[str, Any]) -> str:
    return _identifier(item, "sourceIdentityId", "episodeId")


def _scope_counts(items: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    counter = Counter(str(row.get("scope") or "").strip().casefold() for row in items)
    return {
        "items": sum(counter.values()),
        "focalItems": counter.get("focal", 0),
        "contextualItems": counter.get("contextual", 0),
    }


def _retained_source_identity_ids(
    reconciliation: Mapping[str, Any],
) -> set[str]:
    """Select one governed source identity per nonexcluded canonical episode."""

    return {
        str(row.get("canonicalSourceIdentityId"))
        for row in reconciliation.get("episodes", ())
        if row.get("canonicalSourceIdentityId")
    }


def _category_sensitivity(
    original_items: Sequence[Mapping[str, Any]],
    retained_item_ids: set[str],
    categories: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    category_names = {
        _identifier(row, "categoryId"): row.get("name")
        for row in categories
    }
    original = Counter(
        _identifier(row, "categoryId") for row in original_items if row.get("categoryId")
    )
    reconciled = Counter(
        _identifier(row, "categoryId")
        for row in original_items
        if _identifier(row, "itemId") in retained_item_ids and row.get("categoryId")
    )
    records: list[dict[str, Any]] = []
    for category_id in sorted(set(original) | set(category_names), key=natural_key):
        before = original.get(category_id, 0)
        after = reconciled.get(category_id, 0)
        records.append(
            {
                "categoryId": category_id,
                "categoryName": category_names.get(category_id),
                "originalItemCount": before,
                "reconciledItemCount": after,
                "absoluteChange": after - before,
                "percentChange": _pct_change(before, after),
            }
        )
    return records


def _normalized_exact_item_signature(item: Mapping[str, Any]) -> tuple[str, ...]:
    fields = (
        "categoryId",
        "item",
        "summary",
        "strategicSignificance",
        "operationalImplications",
        "timeHorizon",
    )
    return tuple((normalize_text(item.get(field)) or "").casefold() for field in fields)


def _near_item_tokens(item: Mapping[str, Any]) -> set[str]:
    return set(
        normalized_key(
            " ".join(
                str(item.get(field) or "")
                for field in ("item", "summary", "strategicSignificance")
            )
        ).split()
    )


def _jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def _alias_group_overlap(
    alias_group: Mapping[str, Any],
    items_by_source: Mapping[str, list[Mapping[str, Any]]],
    assignments_by_item: Mapping[str, Mapping[str, Any]],
    category_names: Mapping[str, Any],
) -> dict[str, Any]:
    canonical_id = str(alias_group.get("canonicalSourceIdentityId") or "")
    source_ids = [str(value) for value in alias_group.get("sourceIdentityIds", ())]
    alias_ids = [value for value in source_ids if value != canonical_id]
    canonical_items = list(items_by_source.get(canonical_id, ()))
    alias_items = [
        item for source_id in alias_ids for item in items_by_source.get(source_id, ())
    ]
    combined_items = canonical_items + alias_items
    canonical_item_ids = {
        _identifier(item, "itemId") for item in canonical_items if item.get("itemId")
    }
    combined_item_ids = {
        _identifier(item, "itemId") for item in combined_items if item.get("itemId")
    }

    def assignment_counts(item_ids: set[str]) -> dict[str, int]:
        rows = [assignments_by_item[item_id] for item_id in item_ids if item_id in assignments_by_item]
        return {
            "primaryAssignments": sum(bool(row.get("primaryClusterId")) for row in rows),
            "secondaryAssignments": sum(bool(row.get("secondaryClusterId")) for row in rows),
        }

    category_ids = sorted(
        {
            _identifier(item, "categoryId")
            for item in combined_items
            if item.get("categoryId")
        },
        key=natural_key,
    )

    canonical_signatures: dict[tuple[str, ...], list[int]] = defaultdict(list)
    alias_signatures: dict[tuple[str, ...], list[int]] = defaultdict(list)
    for index, item in enumerate(canonical_items):
        canonical_signatures[_normalized_exact_item_signature(item)].append(index)
    for index, item in enumerate(alias_items):
        alias_signatures[_normalized_exact_item_signature(item)].append(index)

    exact_pairs: list[tuple[int, int]] = []
    for signature in sorted(set(canonical_signatures) & set(alias_signatures)):
        left = canonical_signatures[signature]
        right = alias_signatures[signature]
        exact_pairs.extend(zip(left[: min(len(left), len(right))], right[: min(len(left), len(right))]))
    used_canonical = {pair[0] for pair in exact_pairs}
    used_alias = {pair[1] for pair in exact_pairs}

    candidates: list[tuple[float, int, int]] = []
    canonical_tokens = [_near_item_tokens(item) for item in canonical_items]
    alias_tokens = [_near_item_tokens(item) for item in alias_items]
    for left_index, left_item in enumerate(canonical_items):
        if left_index in used_canonical:
            continue
        for right_index, right_item in enumerate(alias_items):
            if right_index in used_alias:
                continue
            if left_item.get("categoryId") != right_item.get("categoryId"):
                continue
            score = _jaccard(canonical_tokens[left_index], alias_tokens[right_index])
            if score >= NEAR_ITEM_OVERLAP_THRESHOLD:
                candidates.append((score, left_index, right_index))
    near_pairs: list[tuple[float, int, int]] = []
    for score, left_index, right_index in sorted(
        candidates, key=lambda row: (-row[0], row[1], row[2])
    ):
        if left_index in used_canonical or right_index in used_alias:
            continue
        used_canonical.add(left_index)
        used_alias.add(right_index)
        near_pairs.append((score, left_index, right_index))

    return {
        "aliasGroupId": alias_group.get("aliasGroupId"),
        "episodeNumber": alias_group.get("episodeNumber"),
        "canonicalSourceIdentityId": canonical_id,
        "aliasSourceIdentityIds": alias_ids,
        "canonicalSourceItemCount": len(canonical_items),
        "excludedAliasItemCount": len(alias_items),
        "combinedOriginalItemCount": len(canonical_items) + len(alias_items),
        "originalScopeCounts": _scope_counts(combined_items),
        "reconciledScopeCounts": _scope_counts(canonical_items),
        "categoryIds": category_ids,
        "categoryNames": [category_names.get(category_id) for category_id in category_ids],
        "originalAssignmentCounts": assignment_counts(combined_item_ids),
        "reconciledAssignmentCounts": assignment_counts(canonical_item_ids),
        "exactNormalizedRecordMatches": len(exact_pairs),
        "nearHeuristicMatches": len(near_pairs),
        "canonicalItemsWithoutMatch": len(canonical_items) - len(used_canonical),
        "aliasItemsWithoutMatch": len(alias_items) - len(used_alias),
        "nearMatchThreshold": NEAR_ITEM_OVERLAP_THRESHOLD,
        "nearMatchMethod": (
            "Greedy one-to-one token-set Jaccard matching within category; "
            "diagnostic only and never used to deduplicate items."
        ),
    }


def _cluster_sensitivity(
    dataset: Mapping[str, Any],
    reconciliation: Mapping[str, Any],
    retained_item_ids: set[str],
) -> list[dict[str, Any]]:
    items = {
        _identifier(row, "itemId"): row
        for row in dataset.get("items", ())
        if row.get("itemId")
    }
    canonical_by_source = {
        str(row.get("sourceIdentityId")): row.get("canonicalEpisodeId")
        for row in reconciliation.get("mappings", ())
    }
    summary_by_cluster = {
        _identifier(row, "clusterId"): row
        for row in dataset.get("cluster_summaries", ())
        if row.get("clusterId")
    }
    roles: dict[str, dict[str, set[str]]] = defaultdict(
        lambda: {"primary": set(), "secondary": set()}
    )
    for assignment in dataset.get("item_cluster_assignments", ()):
        item_id = _identifier(assignment, "itemId")
        primary_id = _identifier(assignment, "primaryClusterId")
        secondary_id = _identifier(assignment, "secondaryClusterId")
        if primary_id and item_id:
            roles[primary_id]["primary"].add(item_id)
        if secondary_id and item_id:
            roles[secondary_id]["secondary"].add(item_id)

    records: list[dict[str, Any]] = []
    for cluster in sorted(
        dataset.get("clusters", ()), key=lambda row: natural_key(row.get("clusterId"))
    ):
        cluster_id = _identifier(cluster, "clusterId")
        primary_ids = roles[cluster_id]["primary"]
        secondary_ids = roles[cluster_id]["secondary"]
        retained_primary = primary_ids & retained_item_ids
        retained_secondary = secondary_ids & retained_item_ids
        all_ids = primary_ids | secondary_ids
        retained_all = retained_primary | retained_secondary

        def source_ids(item_ids: Iterable[str]) -> set[str]:
            return {
                _item_source_identity(items[item_id])
                for item_id in item_ids
                if item_id in items and _item_source_identity(items[item_id])
            }

        def canonical_ids(item_ids: Iterable[str]) -> set[str]:
            return {
                str(canonical_by_source[source_id])
                for source_id in source_ids(item_ids)
                if canonical_by_source.get(source_id)
            }

        original_primary = len(primary_ids)
        reconciled_primary = len(retained_primary)
        original_secondary = len(secondary_ids)
        reconciled_secondary = len(retained_secondary)
        original_weighted = (
            2 * original_primary + original_secondary
        )
        reconciled_weighted = 2 * reconciled_primary + reconciled_secondary
        source_weighted = summary_by_cluster.get(cluster_id, {}).get("weightedCount")
        records.append(
            {
                "clusterId": cluster_id,
                "clusterName": cluster.get("name"),
                "categoryId": cluster.get("categoryId"),
                "originalPrimaryCount": original_primary,
                "reconciledPrimaryCount": reconciled_primary,
                "primaryAbsoluteChange": reconciled_primary - original_primary,
                "primaryPercentChange": _pct_change(original_primary, reconciled_primary),
                "originalSecondaryCount": original_secondary,
                "reconciledSecondaryCount": reconciled_secondary,
                "secondaryAbsoluteChange": reconciled_secondary - original_secondary,
                "secondaryPercentChange": _pct_change(original_secondary, reconciled_secondary),
                "sourceWorkbookWeightedCount": source_weighted,
                "originalWeightedCount": original_weighted,
                "reconciledWeightedCount": reconciled_weighted,
                "weightedAbsoluteChange": reconciled_weighted - original_weighted,
                "weightedPercentChange": _pct_change(original_weighted, reconciled_weighted),
                "weightingFormula": WEIGHTING_FORMULA,
                "weightingBasis": WEIGHTING_BASIS,
                "sourceWeightedCountMatchesFormula": (
                    source_weighted is None or float(source_weighted) == float(original_weighted)
                ),
                "originalSourceIdentityCoverage": len(source_ids(all_ids)),
                "originalCanonicalEpisodeCoverage": len(canonical_ids(all_ids)),
                "reconciledCanonicalEpisodeCoverage": len(canonical_ids(retained_all)),
                "canonicalEpisodeCoverageAbsoluteChange": (
                    len(canonical_ids(retained_all)) - len(canonical_ids(all_ids))
                ),
                "canonicalEpisodeCoveragePercentChange": _pct_change(
                    len(canonical_ids(all_ids)), len(canonical_ids(retained_all))
                ),
            }
        )
    return records


def _support_classification(
    original_items: int,
    retained_items: int,
    original_episodes: int,
    retained_episodes: int,
    original_categories: int,
    retained_categories: int,
) -> str:
    if original_items == 0:
        return "cannot-assess-from-available-provenance"
    if retained_items == 0 or retained_episodes == 0:
        return "highly-sensitive"
    item_loss = _pct_loss(original_items, retained_items) or 0.0
    episode_loss = _pct_loss(original_episodes, retained_episodes) or 0.0
    category_loss = original_categories - retained_categories
    if episode_loss > 25 or item_loss >= 75 or category_loss >= 2:
        return "highly-sensitive"
    if episode_loss > 10 or category_loss == 1 or (
        original_episodes > 2 and retained_episodes <= 2
    ):
        return "moderately-sensitive"
    if episode_loss > 5 or item_loss > 10:
        return "mildly-sensitive"
    return "stable"


def _role_sensitivity(
    role_items: Mapping[str, set[str]],
    retained_item_ids: set[str],
) -> list[dict[str, Any]]:
    records = []
    for role in sorted(role_items):
        before = role_items[role]
        after = before & retained_item_ids
        records.append(
            {
                "evidenceRole": role,
                "originalItemCount": len(before),
                "reconciledItemCount": len(after),
                "absoluteChange": len(after) - len(before),
                "percentChange": _pct_change(len(before), len(after)),
            }
        )
    return records


def _higher_order_sensitivity(
    dataset: Mapping[str, Any],
    reconciliation: Mapping[str, Any],
    retained_item_ids: set[str],
) -> dict[str, Any]:
    items = {
        _identifier(row, "itemId"): row
        for row in dataset.get("items", ())
        if row.get("itemId")
    }
    canonical_by_source = {
        str(row.get("sourceIdentityId")): row.get("canonicalEpisodeId")
        for row in reconciliation.get("mappings", ())
    }
    direct: dict[tuple[str, str], dict[str, set[str]]] = defaultdict(
        lambda: defaultdict(set)
    )
    for link in dataset.get("evidence_links", ()):
        if str(link.get("targetEntityType") or "") != "item":
            continue
        entity_type = str(link.get("sourceEntityType") or "")
        entity_id = str(link.get("sourceEntityId") or "")
        item_id = str(link.get("targetEntityId") or "")
        if entity_type and entity_id and item_id in items:
            role = str(link.get("evidenceRole") or "directItem")
            direct[(entity_type, entity_id)][role].add(item_id)

    # Explicit record-level item lists are retained even if a future exporter
    # omits a redundant evidence-link row.
    for record in dataset.get("meta_clusters", ()):
        key = ("metaCluster", _identifier(record, "metaClusterId"))
        direct[key]["representativeItem"].update(
            str(value) for value in record.get("representativeItemIds", ()) if str(value) in items
        )
    for record in dataset.get("themes", ()):
        key = ("theme", _identifier(record, "themeId"))
        direct[key]["representativeItem"].update(
            str(value) for value in record.get("representativeItemIds", ()) if str(value) in items
        )
    for record in dataset.get("tensions", ()):
        key = ("tension", _identifier(record, "tensionId"))
        direct[key]["poleAEvidence"].update(
            str(value) for value in record.get("supportingItemIdsPoleA", ()) if str(value) in items
        )
        direct[key]["poleBEvidence"].update(
            str(value) for value in record.get("supportingItemIdsPoleB", ()) if str(value) in items
        )

    records: list[dict[str, Any]] = []
    for entity_type, collection, id_field in _HIGHER_ORDER_COLLECTIONS:
        for entity in sorted(
            dataset.get(collection, ()), key=lambda row: natural_key(row.get(id_field))
        ):
            entity_id = _identifier(entity, id_field)
            role_items = direct.get((entity_type, entity_id), {})
            original_item_ids = set().union(*role_items.values()) if role_items else set()
            reconciled_item_ids = original_item_ids & retained_item_ids

            def source_ids(item_ids: Iterable[str]) -> set[str]:
                return {
                    _item_source_identity(items[item_id])
                    for item_id in item_ids
                    if item_id in items and _item_source_identity(items[item_id])
                }

            def canonical_ids(item_ids: Iterable[str]) -> set[str]:
                return {
                    str(canonical_by_source[source_id])
                    for source_id in source_ids(item_ids)
                    if canonical_by_source.get(source_id)
                }

            def category_ids(item_ids: Iterable[str]) -> set[str]:
                return {
                    _identifier(items[item_id], "categoryId")
                    for item_id in item_ids
                    if item_id in items and items[item_id].get("categoryId")
                }

            original_episodes = canonical_ids(original_item_ids)
            reconciled_episodes = canonical_ids(reconciled_item_ids)
            original_categories = category_ids(original_item_ids)
            reconciled_categories = category_ids(reconciled_item_ids)
            classification = _support_classification(
                len(original_item_ids),
                len(reconciled_item_ids),
                len(original_episodes),
                len(reconciled_episodes),
                len(original_categories),
                len(reconciled_categories),
            )
            assessment_scope = "direct-item-support-sensitivity"
            limitation = (
                "This classification describes survival of explicit item support, "
                "not the validity of the synthesized claim."
            )
            if entity_type in _CANNOT_ASSESS_ENTITY_TYPES:
                classification = "cannot-assess-from-available-provenance"
                assessment_scope = "linked-entity-lineage-only"
                limitation = (
                    "The normalized source provides no direct item-evidence links for "
                    "this entity type; substantive stability cannot be assessed."
                )
            records.append(
                {
                    "entityType": entity_type,
                    "entityId": entity_id,
                    "entityName": entity.get("name"),
                    "assessmentScope": assessment_scope,
                    "supportSensitivity": classification,
                    "originalDirectItemCount": len(original_item_ids),
                    "reconciledDirectItemCount": len(reconciled_item_ids),
                    "directItemAbsoluteChange": len(reconciled_item_ids) - len(original_item_ids),
                    "directItemPercentChange": _pct_change(
                        len(original_item_ids), len(reconciled_item_ids)
                    ),
                    "originalSourceIdentityCoverage": len(source_ids(original_item_ids)),
                    "originalCanonicalEpisodeCoverage": len(original_episodes),
                    "reconciledCanonicalEpisodeCoverage": len(reconciled_episodes),
                    "originalCategoryBreadth": len(original_categories),
                    "reconciledCategoryBreadth": len(reconciled_categories),
                    "roleSensitivity": _role_sensitivity(role_items, retained_item_ids),
                    "interpretationLimit": limitation,
                }
            )
    return {
        "schemaVersion": RECONCILIATION_SCHEMA_VERSION,
        "classificationThresholds": {
            "stable": "No category loss, no more than 5% episode loss, and no more than 10% item loss.",
            "mildlySensitive": "More than 5% episode loss or more than 10% item loss without a category loss.",
            "moderatelySensitive": "More than 10% episode loss, one category lost, or support concentrates in two or fewer episodes.",
            "highlySensitive": "No support, more than 25% episode loss, at least 75% item loss, or two or more categories lost.",
            "cannotAssess": "No sufficiently direct item-level provenance is available.",
        },
        "records": records,
    }


def _status_counts(mappings: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(str(row.get("mappingStatus")) for row in mappings).items()))


def _public_aggregate(
    reconciliation: Mapping[str, Any],
    original_counts: Mapping[str, int],
    reconciled_counts: Mapping[str, int],
) -> dict[str, Any]:
    mappings = list(reconciliation.get("mappings", ()))
    alias_groups = list(reconciliation.get("aliasGroups", ()))
    review_queue = list(reconciliation.get("reviewQueue", ()))
    excluded_aliases = sum(
        row.get("mappingStatus") == "confirmed-alias"
        and row.get("mappingRole") == "alias"
        for row in mappings
    )
    excluded_non_episode = sum(
        row.get("mappingStatus") == "excluded-non-episode" for row in mappings
    )
    status = "complete" if not review_queue else "human-review-required"
    return {
        "schemaVersion": RECONCILIATION_SCHEMA_VERSION,
        "methodVersion": RECONCILIATION_METHOD_VERSION,
        "status": status,
        "counts": {
            "canonicalEpisodes": len(reconciliation.get("episodes", ())),
            "originalSourceIdentities": len(reconciliation.get("sourceIdentities", ())),
            "confirmedAliasGroups": len(alias_groups),
            "sourceIdentitiesInConfirmedAliasGroups": sum(
                len(row.get("sourceIdentityIds", ())) for row in alias_groups
            ),
            "excludedConfirmedAliasSourceIdentities": excluded_aliases,
            "excludedNonEpisodeSourceIdentities": excluded_non_episode,
            "likelyAliasSourceIdentities": sum(
                row.get("mappingStatus") == "likely-alias" for row in mappings
            ),
            "ambiguousSourceIdentities": sum(
                row.get("mappingStatus") == "ambiguous" for row in mappings
            ),
            "unresolvedSourceIdentities": sum(
                row.get("mappingStatus") == "unresolved" for row in mappings
            ),
            "pendingDecisionRecords": len(review_queue),
            "originalItems": int(original_counts.get("items", 0)),
            "reconciledSensitivityItems": int(reconciled_counts.get("items", 0)),
            "originalFocalItems": int(original_counts.get("focalItems", 0)),
            "reconciledSensitivityFocalItems": int(
                reconciled_counts.get("focalItems", 0)
            ),
            "originalContextualItems": int(original_counts.get("contextualItems", 0)),
            "reconciledSensitivityContextualItems": int(
                reconciled_counts.get("contextualItems", 0)
            ),
        },
        "interpretation": (
            "The historical analytical release retains every extracted item. The "
            "reconciled sensitivity dataset selects one canonical source identity "
            "per canonical public-feed release. Distinct releases remain "
            "separate even when their content is reused."
        ),
        "automaticRules": [
            "Preserve every historical source identity and stable EPI identifier.",
            "Retain the episode-zero trailer as a distinct public feed release.",
            "Confirm only modern-versus-legacy pairs numbered 2 through 27 when normalized title tokens corroborate the shared episode number.",
            "Prefer the modern #N source identity as the canonical representative.",
            "Apply separately governed transcript-forensic alias decisions only when explicitly approved.",
            "Retain governed content-equivalent re-releases as distinct public-feed publication units.",
            "Never collapse a fuzzy-title candidate automatically.",
        ],
        "limitations": [
            "Item-overlap similarity is diagnostic and is never used to deduplicate individual items.",
            "Sensitivity counts do not establish the validity of a cluster or higher-order synthesis.",
            "Narrative and scenario stability cannot be assessed directly from the available item-level provenance.",
        ],
    }


def build_reconciliation_products(dataset: Mapping[str, Any]) -> dict[str, Any]:
    """Return the reconciled dataset, private audit files, and public aggregate."""

    reconciliation = build_episode_reconciliation(dataset)
    reconciled_dataset = apply_episode_reconciliation(dataset, reconciliation)
    original_items = [deepcopy(dict(row)) for row in dataset.get("items", ())]
    retained_source_ids = _retained_source_identity_ids(reconciliation)
    retained_item_ids = {
        _identifier(row, "itemId")
        for row in original_items
        if _item_source_identity(row) in retained_source_ids and row.get("itemId")
    }
    retained_items = [
        row for row in original_items if _identifier(row, "itemId") in retained_item_ids
    ]
    original_counts = _scope_counts(original_items)
    reconciled_counts = _scope_counts(retained_items)
    by_category = _category_sensitivity(
        original_items, retained_item_ids, list(dataset.get("categories", ()))
    )
    items_by_source: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for item in original_items:
        items_by_source[_item_source_identity(item)].append(item)
    assignments_by_item = {
        _identifier(row, "itemId"): row
        for row in dataset.get("item_cluster_assignments", ())
        if row.get("itemId")
    }
    category_names = {
        _identifier(row, "categoryId"): row.get("name")
        for row in dataset.get("categories", ())
        if row.get("categoryId")
    }
    alias_item_sensitivity = [
        _alias_group_overlap(
            group, items_by_source, assignments_by_item, category_names
        )
        for group in reconciliation.get("aliasGroups", ())
    ]
    cluster_sensitivity = _cluster_sensitivity(
        dataset, reconciliation, retained_item_ids
    )
    higher_order = _higher_order_sensitivity(
        dataset, reconciliation, retained_item_ids
    )
    public_aggregate = _public_aggregate(
        reconciliation, original_counts, reconciled_counts
    )

    item_summary = {
        "schemaVersion": RECONCILIATION_SCHEMA_VERSION,
        "methodVersion": RECONCILIATION_METHOD_VERSION,
        "datasetLabel": "reconciled sensitivity dataset",
        "original": {
            **original_counts,
            "sourceIdentities": len(reconciliation.get("sourceIdentities", ())),
        },
        "reconciled": {
            **reconciled_counts,
            "retainedSourceIdentities": len(retained_source_ids),
            "canonicalEpisodes": len(reconciliation.get("episodes", ())),
        },
        "absoluteChange": {
            key: int(reconciled_counts[key]) - int(original_counts[key])
            for key in ("items", "focalItems", "contextualItems")
        },
        "percentChange": {
            key: _pct_change(original_counts[key], reconciled_counts[key])
            for key in ("items", "focalItems", "contextualItems")
        },
        "byCategory": by_category,
        "confirmedAliasGroupItemSensitivity": alias_item_sensitivity,
        "nearOverlapBoundary": (
            "Near matches are heuristic diagnostics only. Individual item records "
            "are never automatically merged or deleted."
        ),
    }

    high_cluster_changes = sorted(
        cluster_sensitivity,
        key=lambda row: (
            -abs(int(row.get("weightedAbsoluteChange") or 0)),
            natural_key(row.get("clusterId")),
        ),
    )[:10]
    higher_counts = Counter(
        row["supportSensitivity"] for row in higher_order["records"]
    )
    release_eligible = public_aggregate["status"] == "complete"
    if not release_eligible:
        recommendation = "human-adjudication-required-before-public-count-change"
    elif any(
        row["supportSensitivity"] == "highly-sensitive"
        for row in higher_order["records"]
    ) or any(
        (row.get("weightedPercentChange") or 0) <= -25
        for row in cluster_sensitivity
    ):
        recommendation = "full-pipeline-reanalysis-recommended"
    else:
        recommendation = "partial-count-and-coverage-remediation-warranted"
    public_aggregate["reanalysisRecommendation"] = recommendation

    reconciliation_counts = {
        "sourceIdentities": len(reconciliation.get("sourceIdentities", ())),
        "canonicalEpisodes": len(reconciliation.get("episodes", ())),
        "confirmedAliasGroups": len(reconciliation.get("aliasGroups", ())),
        "reviewQueueRecords": len(reconciliation.get("reviewQueue", ())),
        "mappingStatuses": _status_counts(list(reconciliation.get("mappings", ()))),
    }
    private_payloads = {
        "episode_source_reconciliation.json": {
            "schemaVersion": RECONCILIATION_SCHEMA_VERSION,
            "methodVersion": RECONCILIATION_METHOD_VERSION,
            "counts": reconciliation_counts,
            "episodes": deepcopy(list(reconciliation.get("episodes", ()))),
            "sourceIdentities": deepcopy(
                list(reconciliation.get("sourceIdentities", ()))
            ),
            "mappings": deepcopy(list(reconciliation.get("mappings", ()))),
            "flags": deepcopy(list(reconciliation.get("flags", ()))),
        },
        "alias_groups.json": deepcopy(list(reconciliation.get("aliasGroups", ()))),
        "reconciliation_review_queue.json": deepcopy(
            list(reconciliation.get("reviewQueue", ()))
        ),
        "item_sensitivity_summary.json": item_summary,
        "cluster_sensitivity.json": cluster_sensitivity,
        "higher_order_support_sensitivity.json": higher_order,
        "corpus_reconciliation_report.json": {
            "schemaVersion": RECONCILIATION_SCHEMA_VERSION,
            "methodVersion": RECONCILIATION_METHOD_VERSION,
            "releaseEligible": release_eligible,
            "reconciliationCounts": reconciliation_counts,
            "originalCounts": original_counts,
            "reconciledSensitivityCounts": reconciled_counts,
            "largestWeightedClusterChanges": high_cluster_changes,
            "higherOrderSensitivityCounts": dict(sorted(higher_counts.items())),
            "recommendation": recommendation,
            "interpretiveBoundary": (
                "Count and support changes measure sensitivity to source-identity "
                "selection. They do not by themselves establish substantive instability."
            ),
        },
    }
    return {
        "reconciledDataset": reconciled_dataset,
        "privatePayloads": private_payloads,
        "publicAggregate": public_aggregate,
    }


__all__ = (
    "NEAR_ITEM_OVERLAP_THRESHOLD",
    "WEIGHTING_BASIS",
    "WEIGHTING_FORMULA",
    "build_reconciliation_products",
)
