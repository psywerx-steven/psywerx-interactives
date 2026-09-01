"""Deterministic private and public exports for the Cognitive Security Map."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .episode_products import (
    episode_relationship_payload,
    validate_frozen_summaries,
)


SCHEMA_VERSION = "1.1"
PRODUCT_ID = "psywerx-cognitive-security-practitioner-discourse-map"
PRODUCT_NAME = "PSYWERX Cognitive Security Practitioner Discourse Map"

# Public source references use stable opaque IDs. Workbook basenames, byte
# fingerprints, and detailed worksheet provenance stay in the ignored
# normalized release; they are not part of the browser data contract.
PUBLIC_ARTIFACT_ROLES = {
    "ART-codebook": "canonical-cluster-codebook",
    "ART-master-extractions": "canonical-items-and-episode-provenance",
    "ART-drill-down": "canonical-item-cluster-assignments",
    "ART-cluster-summaries": "canonical-cluster-synthesis",
    "ART-meta-clusters": "canonical-meta-clusters-and-mappings",
    "ART-cross-cutting-themes": "canonical-cross-cutting-themes",
    "ART-tensions": "canonical-tensions-and-debates",
    "ART-final-synthesis": "canonical-narratives-findings-and-scenarios",
}

INTERNAL_COLLECTION_ORDER = (
    "artifacts",
    "episodes",
    "episode_source_identities",
    "episode_source_mappings",
    "episode_reconciliation_flags",
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

PUBLIC_FILE_ORDER = (
    "manifest.json",
    "corpus_reconciliation.json",
    "categories.json",
    "clusters.json",
    "cluster_summaries.json",
    "meta_clusters.json",
    "themes.json",
    "tensions.json",
    "meta_narratives.json",
    "category_findings.json",
    "scenarios.json",
    "episodes.json",
    "episode_summaries.json",
    "episode_relationships.json",
    "relationships.json",
    "coverage.json",
    "review_summary.json",
    "qa_report.json",
)

# Canonical public graph vocabulary.  Internal source mapping labels remain
# snake_case; public relationship and endpoint types are deliberately stable.
PUBLIC_RELATIONSHIP_SCHEMA: dict[str, tuple[str, str]] = {
    "cluster-belongs-to-category": ("cluster", "category"),
    "meta-cluster-belongs-to-category": ("metaCluster", "category"),
    "cluster-belongs-to-meta-cluster": ("cluster", "metaCluster"),
    "theme-connects-meta-cluster": ("theme", "metaCluster"),
    "theme-supported-by-cluster": ("theme", "cluster"),
    "tension-maps-to-cross-cutting-theme": ("tension", "theme"),
    "tension-maps-to-meta-cluster": ("tension", "metaCluster"),
}

TENSION_MAPPING_PUBLIC_RELATIONSHIPS: dict[str, tuple[str, str]] = {
    "cross_cutting_theme": ("tension-maps-to-cross-cutting-theme", "theme"),
    "meta_cluster": ("tension-maps-to-meta-cluster", "metaCluster"),
}

# Public records are created from these positive allowlists. Adding an internal
# field never makes it public unless it is deliberately added here as well.
PUBLIC_FIELDS: dict[str, tuple[str, ...]] = {
    "categories": (
        "categoryId",
        "name",
        "scope",
        "summary",
        "soWhat",
    ),
    "clusters": (
        "clusterId",
        "categoryId",
        "name",
        "definition",
        "inclusionCriteria",
        "exclusionCriteria",
        "nearNeighborDistinctions",
        "anchorExamples",
    ),
    "cluster_summaries": (
        "clusterId",
        "categoryId",
        "clusterName",
        "primaryCount",
        "secondaryCount",
        "weightedCount",
        "summary",
        "recurringThemes",
        "strategicSignificance",
        "operationalImplications",
        "primarySecondaryDistinction",
    ),
    "meta_clusters": (
        "metaClusterId",
        "categoryId",
        "name",
        "definition",
        "includedClusterIds",
        "nearNeighborDistinctions",
        "salience",
        "categorySynthesis",
    ),
    "themes": (
        "themeId",
        "name",
        "definition",
        "categoryIds",
        "linkedMetaClusterIds",
        "linkedClusterIds",
        "crossCategoryLogic",
        "strategicSignificance",
        "operationalImplications",
        "boundaryConditions",
        "relatedTensionIds",
        "evidenceStrength",
    ),
    "tensions": (
        "tensionId",
        "name",
        "description",
        "poleALabel",
        "poleBLabel",
        "poleAAssumption",
        "poleBAssumption",
        "tensionLevel",
        "categoryIds",
        "clusterIds",
        "evidenceStrength",
        "confidence",
    ),
    "meta_narratives": (
        "narrativeId",
        "name",
        "shortVersion",
        "coreClaim",
        "supportingThemeIds",
        "supportingTensionIds",
        "supportingMetaClusterIds",
        "categoryIds",
        "strategicSignificance",
        "operationalImplications",
        "caveats",
        "confidence",
    ),
    "category_findings": (
        "findingId",
        "categoryId",
        "name",
        "coreFinding",
        "supportingMetaClusterIds",
        "supportingClusterIds",
        "strategicSignificance",
        "operationalImplications",
        "unresolvedQuestions",
        "caveats",
        "confidence",
    ),
    "scenarios": (
        "scenarioId",
        "name",
        "timeframe",
        "scenarioType",
        "coreScenario",
        "drivingForces",
        "categoryIds",
        "themeIds",
        "tensionIds",
        "strategicImplications",
        "operationalImplications",
        "researchQuestions",
        "uncertaintyLevel",
        "assumptions",
        "alternativeOutcomes",
    ),
    "episodes": (
        "episodeId",
        "podcast",
        "episodeTitle",
        "sourceIdentityCount",
        "originalItemCount",
        "reconciledSensitivityItemCount",
        "parsedEpisodeNumber",
    ),
}


def json_bytes(value: Any) -> bytes:
    """Return the canonical UTF-8 representation used by every JSON artifact."""
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def content_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _record_id(record: Mapping[str, Any]) -> str:
    for key in (
        "artifactId",
        "episodeId",
        "itemId",
        "categoryId",
        "clusterId",
        "metaClusterId",
        "themeId",
        "tensionId",
        "narrativeId",
        "findingId",
        "scenarioId",
        "relationshipId",
        "reviewFlagId",
    ):
        value = record.get(key)
        if value not in (None, ""):
            return str(value)
    return json.dumps(record, ensure_ascii=False, sort_keys=True)


def _sorted(records: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [dict(record) for record in sorted(records, key=_record_id)]


def _project(record: Mapping[str, Any], fields: Sequence[str]) -> dict[str, Any]:
    return {field: record.get(field) for field in fields}


def _project_collection(
    dataset: Mapping[str, Sequence[Mapping[str, Any]]], collection: str
) -> list[dict[str, Any]]:
    fields = PUBLIC_FIELDS[collection]
    return _sorted(_project(record, fields) for record in dataset.get(collection, ()))


def _category_records(
    dataset: Mapping[str, Sequence[Mapping[str, Any]]]
) -> list[dict[str, Any]]:
    summaries = {
        str(row.get("categoryId")): row
        for row in dataset.get("category_summaries", ())
        if row.get("categoryId")
    }
    records: list[dict[str, Any]] = []
    for source in dataset.get("categories", ()):
        category_id = str(source.get("categoryId") or "")
        summary = summaries.get(category_id, {})
        records.append(
            {
                "categoryId": source.get("categoryId"),
                "name": source.get("name"),
                "scope": source.get("scope"),
                "summary": summary.get("summary"),
                "soWhat": summary.get("soWhat"),
            }
        )
    return _sorted(records)


def _cluster_summary_records(
    dataset: Mapping[str, Sequence[Mapping[str, Any]]]
) -> list[dict[str, Any]]:
    cluster_names = {
        str(row.get("clusterId")): row.get("name")
        for row in dataset.get("clusters", ())
        if row.get("clusterId")
    }
    records: list[dict[str, Any]] = []
    for source in dataset.get("cluster_summaries", ()):
        record = _project(source, PUBLIC_FIELDS["cluster_summaries"])
        record["clusterName"] = cluster_names.get(str(source.get("clusterId")))
        record["recurringThemes"] = [
            {
                "themeNumber": theme.get("themeNumber"),
                "name": theme.get("name"),
                "description": theme.get("description"),
                "primarySupportCountEstimate": theme.get(
                    "primarySupportCountEstimate"
                ),
                "secondarySupportCountEstimate": theme.get(
                    "secondarySupportCountEstimate"
                ),
                "importance": theme.get("importance"),
            }
            for theme in source.get("recurringThemes", ())
        ]
        records.append(record)
    return _sorted(records)


def _meta_narrative_records(
    dataset: Mapping[str, Sequence[Mapping[str, Any]]]
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for source in dataset.get("meta_narratives", ()):
        record = _project(source, PUBLIC_FIELDS["meta_narratives"])
        record["caveats"] = source.get("caveats") or source.get(
            "caveatsOrBoundaryConditions"
        )
        records.append(record)
    return _sorted(records)


def _relationship_id(relation_type: str, source_id: str, target_id: str) -> str:
    digest = hashlib.sha256(
        f"{relation_type}|{source_id}|{target_id}".encode("utf-8")
    ).hexdigest()[:20]
    return f"CSR-{digest}"


def _relations_from_pairs(
    relation_type: str,
    pairs: Iterable[tuple[Any, Any]],
    source_type: str,
    target_type: str,
) -> list[dict[str, Any]]:
    relationships: list[dict[str, Any]] = []
    for source, target in pairs:
        source_id = str(source or "").strip()
        target_id = str(target or "").strip()
        if not source_id or not target_id:
            continue
        relationships.append(
            {
                "relationshipId": _relationship_id(
                    relation_type, source_id, target_id
                ),
                "relationshipType": relation_type,
                "sourceType": source_type,
                "sourceId": source_id,
                "targetType": target_type,
                "targetId": target_id,
                "interpretation": "semantic",
            }
        )
    return relationships


def build_public_relationships(
    dataset: Mapping[str, Sequence[Mapping[str, Any]]]
) -> list[dict[str, Any]]:
    """Build only explicit, high-level semantic links for the public package."""
    relationships: list[dict[str, Any]] = []
    relationships += _relations_from_pairs(
        "cluster-belongs-to-category",
        ((row.get("clusterId"), row.get("categoryId")) for row in dataset.get("clusters", ())),
        "cluster",
        "category",
    )
    relationships += _relations_from_pairs(
        "meta-cluster-belongs-to-category",
        (
            (row.get("metaClusterId"), row.get("categoryId"))
            for row in dataset.get("meta_clusters", ())
        ),
        "metaCluster",
        "category",
    )
    relationships += _relations_from_pairs(
        "cluster-belongs-to-meta-cluster",
        (
            (row.get("clusterId"), row.get("metaClusterId"))
            for row in dataset.get("cluster_meta_mappings", ())
        ),
        "cluster",
        "metaCluster",
    )
    relationships += _relations_from_pairs(
        "theme-connects-meta-cluster",
        (
            (row.get("themeId"), row.get("metaClusterId"))
            for row in dataset.get("theme_meta_mappings", ())
        ),
        "theme",
        "metaCluster",
    )
    relationships += _relations_from_pairs(
        "theme-supported-by-cluster",
        (
            (row.get("themeId"), row.get("clusterId"))
            for row in dataset.get("theme_cluster_evidence", ())
        ),
        "theme",
        "cluster",
    )
    for row in dataset.get("tension_mappings", ()):
        mapping_type = str(row.get("mappedEntityType") or "").strip().casefold()
        contract = TENSION_MAPPING_PUBLIC_RELATIONSHIPS.get(mapping_type)
        if contract is None:
            raise ValueError(
                f"Unsupported tension mapping type for public export: {mapping_type!r}."
            )
        relationship_type, target_type = contract
        relationships += _relations_from_pairs(
            relationship_type,
            ((row.get("tensionId"), row.get("mappedId")),),
            "tension",
            target_type,
        )

    unique = {row["relationshipId"]: row for row in relationships}
    return _sorted(unique.values())


def _scenario_records(
    dataset: Mapping[str, Sequence[Mapping[str, Any]]]
) -> list[dict[str, Any]]:
    pathways: dict[str, list[dict[str, Any]]] = defaultdict(list)
    indicators: dict[str, list[str]] = defaultdict(list)
    actions: dict[str, list[str]] = defaultdict(list)
    for row in dataset.get("scenario_pathways", ()):
        pathways[str(row.get("scenarioId"))].append(
            {
                "stepNumber": row.get("stepNumber"),
                "step": row.get("pathwayStep"),
            }
        )
    for rows in pathways.values():
        rows.sort(key=lambda row: (row.get("stepNumber") is None, row.get("stepNumber")))
    for row in dataset.get("scenario_indicators", ()):
        value = row.get("indicator")
        if value:
            indicators[str(row.get("scenarioId"))].append(str(value))
    for row in dataset.get("scenario_actions", ()):
        value = row.get("action") or row.get("policyOrPracticeAction")
        if value:
            actions[str(row.get("scenarioId"))].append(str(value))

    fields = PUBLIC_FIELDS["scenarios"]
    records: list[dict[str, Any]] = []
    for source in dataset.get("scenarios", ()):
        record = _project(source, fields)
        scenario_id = str(record.get("scenarioId"))
        record["pathway"] = pathways.get(scenario_id, [])
        record["indicators"] = indicators.get(scenario_id, [])
        record["actions"] = actions.get(scenario_id, [])
        record["forecastDisclaimer"] = "Plausible scenario; not a prediction."
        records.append(record)
    return _sorted(records)


def _episode_records(
    dataset: Mapping[str, Sequence[Mapping[str, Any]]]
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for source in dataset.get("episodes", ()):
        record = _project(source, PUBLIC_FIELDS["episodes"])
        record["episodeTitle"] = source.get("episodeTitle") or source.get("title")
        records.append(record)
    return _sorted(records)


def _coverage(dataset: Mapping[str, Sequence[Mapping[str, Any]]]) -> dict[str, Any]:
    items_by_category = Counter(
        str(row.get("categoryId"))
        for row in dataset.get("items", ())
        if row.get("categoryId")
    )
    primary_by_cluster = Counter(
        str(row.get("primaryClusterId"))
        for row in dataset.get("item_cluster_assignments", ())
        if row.get("primaryClusterId")
    )
    secondary_by_cluster = Counter(
        str(row.get("secondaryClusterId"))
        for row in dataset.get("item_cluster_assignments", ())
        if row.get("secondaryClusterId")
    )
    canonical_source_ids = {
        str(row.get("sourceIdentityId"))
        for row in dataset.get("episode_source_mappings", ())
        if row.get("mappingRole") == "canonical" and row.get("canonicalEpisodeId")
    }
    retained_item_ids = {
        str(row.get("itemId"))
        for row in dataset.get("items", ())
        if row.get("itemId") and str(row.get("sourceIdentityId")) in canonical_source_ids
    }
    reconciled_items_by_category = Counter(
        str(row.get("categoryId"))
        for row in dataset.get("items", ())
        if row.get("categoryId") and str(row.get("itemId")) in retained_item_ids
    )
    reconciled_primary_by_cluster = Counter(
        str(row.get("primaryClusterId"))
        for row in dataset.get("item_cluster_assignments", ())
        if row.get("primaryClusterId") and str(row.get("itemId")) in retained_item_ids
    )
    reconciled_secondary_by_cluster = Counter(
        str(row.get("secondaryClusterId"))
        for row in dataset.get("item_cluster_assignments", ())
        if row.get("secondaryClusterId") and str(row.get("itemId")) in retained_item_ids
    )
    items = list(dataset.get("items", ()))
    focal_items = [row for row in items if row.get("scope") == "focal"]
    contextual_items = [row for row in items if row.get("scope") == "contextual"]
    retained_items = [row for row in items if str(row.get("itemId")) in retained_item_ids]
    retained_focal = [row for row in retained_items if row.get("scope") == "focal"]
    retained_contextual = [row for row in retained_items if row.get("scope") == "contextual"]
    return {
        "methodologyCaution": (
            "Counts describe discourse salience in this corpus; they do not measure "
            "importance, consensus, prevalence, or scientific evidence strength."
        ),
        "itemsByCategory": dict(sorted(items_by_category.items())),
        "reconciledSensitivityItemsByCategory": dict(
            sorted(reconciled_items_by_category.items())
        ),
        "primaryAssignmentsByCluster": dict(sorted(primary_by_cluster.items())),
        "secondaryAssignmentsByCluster": dict(sorted(secondary_by_cluster.items())),
        "reconciledSensitivityPrimaryAssignmentsByCluster": dict(
            sorted(reconciled_primary_by_cluster.items())
        ),
        "reconciledSensitivitySecondaryAssignmentsByCluster": dict(
            sorted(reconciled_secondary_by_cluster.items())
        ),
        "totals": {
            key: len(dataset.get(key, ()))
            for key in (
                "episodes",
                "items",
                "clusters",
                "meta_clusters",
                "themes",
                "tensions",
                "meta_narratives",
                "scenarios",
            )
        },
        "originalAnalyticRelease": {
            "sourceIdentities": len(dataset.get("episode_source_identities", ())),
            "items": len(items),
            "focalItems": len(focal_items),
            "contextualItems": len(contextual_items),
        },
        "reconciledSensitivityDataset": {
            "canonicalEpisodes": len(dataset.get("episodes", ())),
            "retainedSourceIdentities": len(canonical_source_ids),
            "items": len(retained_items),
            "focalItems": len(retained_focal),
            "contextualItems": len(retained_contextual),
        },
    }


def _review_summary(
    dataset: Mapping[str, Sequence[Mapping[str, Any]]], qa_report: Mapping[str, Any]
) -> dict[str, Any]:
    assignments = dataset.get("item_cluster_assignments", ())
    return {
        "assignmentReviewRequiredCount": sum(
            bool(row.get("reviewRequired")) for row in assignments
        ),
        "assignmentAmbiguityCount": sum(
            bool(row.get("ambiguityFlag")) for row in assignments
        ),
        "unresolvedClusterCount": len(qa_report.get("unresolvedMappings", ())),
        "metaNarrativeCountIssue": qa_report.get("narrativeCountMismatch"),
        "detailBoundary": (
            "Detailed review queues, rationales, notes, and evidence remain in the "
            "private normalized release candidate."
        ),
    }


def _public_qa_report(
    dataset: Mapping[str, Sequence[Mapping[str, Any]]],
    qa_report: Mapping[str, Any],
) -> dict[str, Any]:
    """Project private build QA into a filename-free public aggregate.

    The internal QA report remains unchanged and retains the exact source
    hashes and workbook/worksheet inventory needed by maintainers. Public QA
    identifies sources only by stable artifact ID and publishes aggregate
    dimensions that cannot reveal a local or source workbook filename.
    """

    public_report = copy.deepcopy(dict(qa_report))
    source_hashes = public_report.pop("sourceHashes", {})
    source_row_counts = public_report.pop("sourceRowCounts", {})

    source_artifact_qa: list[dict[str, Any]] = []
    for artifact in sorted(
        dataset.get("artifacts", ()), key=lambda row: str(row.get("artifactId", ""))
    ):
        artifact_id = str(artifact.get("artifactId") or "")
        if not artifact_id:
            continue
        # Workbook names are used only for the private in-memory lookup. They
        # never enter the projected record.
        private_file_name = str(artifact.get("fileName") or "")
        worksheet_counts = source_row_counts.get(private_file_name, {})
        numeric_counts = (
            [
                int(value)
                for value in worksheet_counts.values()
                if isinstance(value, (int, float)) and not isinstance(value, bool)
            ]
            if isinstance(worksheet_counts, Mapping)
            else []
        )
        source_artifact_qa.append(
            {
                "artifactId": artifact_id,
                "canonicalRole": PUBLIC_ARTIFACT_ROLES.get(artifact_id),
                "worksheetCount": len(numeric_counts),
                "aggregateRowCount": sum(numeric_counts),
                "integrityVerified": bool(
                    private_file_name
                    and isinstance(source_hashes, Mapping)
                    and source_hashes.get(private_file_name)
                ),
            }
        )
    public_report["sourceArtifactQa"] = source_artifact_qa

    private_decisions = public_report.get("canonicalSourceDecisions", {})
    blank_source_decision = (
        private_decisions.get("blankCopiedSourceTensions")
        if isinstance(private_decisions, Mapping)
        else None
    )
    public_report["canonicalSourceDecisions"] = {
        "tensionsArtifactId": "ART-tensions",
        "blankCopiedSourceTensions": blank_source_decision,
    }
    return public_report


def build_public_payloads(
    dataset: Mapping[str, Sequence[Mapping[str, Any]]],
    qa_report: Mapping[str, Any],
    corpus_reconciliation: Mapping[str, Any],
    frozen_episode_summaries: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return the complete conservative public JSON package in memory."""
    artifacts = [
        {
            "artifactId": row.get("artifactId"),
            "canonicalRole": PUBLIC_ARTIFACT_ROLES.get(str(row.get("artifactId"))),
        }
        for row in dataset.get("artifacts", ())
    ]
    manifest = {
        "schemaVersion": SCHEMA_VERSION,
        "productId": PRODUCT_ID,
        "productName": PRODUCT_NAME,
        "knowledgeProductType": "practitioner-discourse-map",
        "interpretation": (
            "A governed synthesis of practitioner discourse, not a definitive "
            "taxonomy, causal model, prevalence estimate, or consensus measure."
        ),
        "sourceArtifacts": _sorted(artifacts),
        "publicFiles": list(PUBLIC_FILE_ORDER),
    }

    summaries = (
        []
        if frozen_episode_summaries is None
        else validate_frozen_summaries(
            frozen_episode_summaries, dataset.get("episodes", ())
        )
    )

    return {
        "manifest.json": manifest,
        "corpus_reconciliation.json": dict(corpus_reconciliation),
        "categories.json": _category_records(dataset),
        "clusters.json": _project_collection(dataset, "clusters"),
        "cluster_summaries.json": _cluster_summary_records(dataset),
        "meta_clusters.json": _project_collection(dataset, "meta_clusters"),
        "themes.json": _project_collection(dataset, "themes"),
        "tensions.json": _project_collection(dataset, "tensions"),
        "meta_narratives.json": _meta_narrative_records(dataset),
        "category_findings.json": _project_collection(dataset, "category_findings"),
        "scenarios.json": _scenario_records(dataset),
        "episodes.json": _episode_records(dataset),
        "episode_summaries.json": summaries,
        "episode_relationships.json": episode_relationship_payload(dataset),
        "relationships.json": build_public_relationships(dataset),
        "coverage.json": _coverage(dataset),
        "review_summary.json": _review_summary(dataset, qa_report),
        "qa_report.json": _public_qa_report(dataset, qa_report),
    }


def build_internal_payloads(
    dataset: Mapping[str, Sequence[Mapping[str, Any]]],
    qa_report: Mapping[str, Any],
) -> dict[str, Any]:
    payloads = {
        f"{collection}.json": _sorted(dataset.get(collection, ()))
        for collection in INTERNAL_COLLECTION_ORDER
    }
    payloads["qa_report.json"] = dict(qa_report)
    payloads["manifest.json"] = {
        "schemaVersion": SCHEMA_VERSION,
        "productId": PRODUCT_ID,
        "collections": {
            collection: len(dataset.get(collection, ()))
            for collection in INTERNAL_COLLECTION_ORDER
        },
        "privacy": "private-internal-normalized-release-candidate",
    }
    return payloads


def serialize_payloads(payloads: Mapping[str, Any]) -> dict[str, bytes]:
    return {name: json_bytes(payloads[name]) for name in sorted(payloads)}


def write_serialized_files(output_dir: Path, files: Mapping[str, bytes]) -> None:
    """Atomically replace files only after callers have completed validation."""
    output_dir.mkdir(parents=True, exist_ok=True)
    for name in sorted(files):
        target = output_dir / name
        temporary: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb", delete=False, dir=output_dir, prefix=f".{name}.", suffix=".tmp"
            ) as handle:
                handle.write(files[name])
                handle.flush()
                os.fsync(handle.fileno())
                temporary = Path(handle.name)
            temporary.replace(target)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()


def generated_hashes(files: Mapping[str, bytes]) -> dict[str, str]:
    return {name: content_hash(files[name]) for name in sorted(files)}
