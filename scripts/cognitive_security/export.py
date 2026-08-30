"""Deterministic private and public exports for the Cognitive Security Map."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_VERSION = "1.0"
PRODUCT_ID = "psywerx-cognitive-security-practitioner-discourse-map"
PRODUCT_NAME = "PSYWERX Cognitive Security Practitioner Discourse Map"

INTERNAL_COLLECTION_ORDER = (
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

PUBLIC_FILE_ORDER = (
    "manifest.json",
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
    "relationships.json",
    "coverage.json",
    "review_summary.json",
    "qa_report.json",
)

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
        target_type = str(row.get("mappedEntityType") or "entity").strip()
        normalized_type = target_type.replace("_", "-").replace(" ", "-").casefold()
        relationships += _relations_from_pairs(
            f"tension-maps-to-{normalized_type}",
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
    item_counts = Counter(
        str(row.get("episodeId"))
        for row in dataset.get("items", ())
        if row.get("episodeId")
    )
    records: list[dict[str, Any]] = []
    for source in dataset.get("episodes", ()):
        record = _project(source, PUBLIC_FIELDS["episodes"])
        record["episodeTitle"] = source.get("episodeTitle") or source.get("title")
        record["itemCount"] = item_counts.get(str(record.get("episodeId")), 0)
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
    return {
        "methodologyCaution": (
            "Counts describe discourse salience in this corpus; they do not measure "
            "importance, consensus, prevalence, or scientific evidence strength."
        ),
        "itemsByCategory": dict(sorted(items_by_category.items())),
        "primaryAssignmentsByCluster": dict(sorted(primary_by_cluster.items())),
        "secondaryAssignmentsByCluster": dict(sorted(secondary_by_cluster.items())),
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


def build_public_payloads(
    dataset: Mapping[str, Sequence[Mapping[str, Any]]],
    qa_report: Mapping[str, Any],
) -> dict[str, Any]:
    """Return the complete conservative public JSON package in memory."""
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
    artifacts = [
        {
            "artifactId": row.get("artifactId"),
            "fileName": row.get("fileName"),
            "sha256": row.get("sha256"),
            "canonicalRole": canonical_roles.get(str(row.get("fileName"))),
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

    return {
        "manifest.json": manifest,
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
        "relationships.json": build_public_relationships(dataset),
        "coverage.json": _coverage(dataset),
        "review_summary.json": _review_summary(dataset, qa_report),
        "qa_report.json": dict(qa_report),
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
