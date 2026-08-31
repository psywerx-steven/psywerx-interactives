"""Validation primitives for the Cognitive Security Phase 1 data contract.

The validator operates on the normalized, in-memory dataset rather than on
workbook rows.  This keeps source-specific parsing out of the governance layer
and gives the private and public exporters one shared set of integrity checks.

Normalized dataset contract
---------------------------
``validate_normalized_dataset`` expects a mapping whose values are lists under
the collection names in ``REQUIRED_COLLECTIONS``.  Canonical record fields use
camelCase identifiers (``itemId``, ``clusterId``, and so on); snake_case aliases
are accepted defensively at the validator boundary.  An exporter
may wrap a list in a mapping under the collection name, ``records``,
``entries``, or ``relationships``; ``collection_records`` unwraps those forms.

An item/cluster assignment is one record per focal item and has ``itemId``,
``primaryClusterId``, nullable ``secondaryClusterId``, ``reviewRequired``, and
``ambiguityFlag``.  The source sentinel ``NONE`` must
be normalized to ``None`` before validation.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any, Iterable, Mapping, Sequence

from .export import PUBLIC_RELATIONSHIP_SCHEMA


REQUIRED_WORKBOOKS = (
    "codebook.xlsx",
    "master_extractions.xlsx",
    "drill_down.xlsx",
    "drill_up_cluster_summaries.xlsx",
    "drill_up_meta_clusters.xlsx",
    "cross_cutting_themes.xlsx",
    "tensions_debates_rebuilt.xlsx",
    "final_synthesis.xlsx",
)

REQUIRED_COLLECTIONS = (
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

# These are comparisons, not coercive targets.  Unexpected differences are
# reported as warnings so source truth is never changed merely to hit a count.
EXPECTED_BASELINE_COUNTS = {
    "items": 14_397,
    "focal_items": 10_940,
    "contextual_items": 3_457,
    "episodes": 269,
    "clusters": 127,
    "primary_assignments": 10_940,
    "substantive_secondary_assignments": 10_524,
    "secondary_none": 416,
    "review_required_assignments": 514,
    "ambiguity_flagged_assignments": 158,
    "meta_clusters": 36,
    "cluster_meta_mappings": 124,
    "themes": 11,
    "theme_meta_mappings": 89,
    "theme_cluster_evidence": 302,
    "tensions": 30,
    "meta_narratives": 7,
    "category_summaries": 7,
    "scenarios": 6,
}

KNOWN_UNMAPPED_CLUSTERS = {
    "CRB-10": "Forecasting, Complexity & Uncertainty",
    "FTP-13": "Societal Transformation, Identity, & Social Cohesion",
    "KCFT-20": "Strategic Culture & Ideological Competition",
}

KNOWN_EMPTY_META_CLUSTERS = {
    "CRB-M05": "Strategic synthesis lens without source cluster-mapping rows",
}

ENTITY_ID_FIELDS = {
    "artifacts": ("artifact_id", "id"),
    "episodes": ("episode_id", "id"),
    "items": ("item_id", "source_item_id", "id"),
    "item_tags": ("item_tag_id", "id"),
    "categories": ("category_id", "id"),
    "clusters": ("cluster_id", "id"),
    "item_cluster_assignments": ("assignment_id", "id"),
    "cluster_summaries": ("cluster_summary_id", "id"),
    "meta_clusters": ("meta_cluster_id", "id"),
    "cluster_meta_mappings": ("cluster_meta_mapping_id", "id"),
    "themes": ("theme_id", "id"),
    "theme_meta_mappings": ("theme_meta_mapping_id", "id"),
    "theme_cluster_evidence": ("theme_cluster_evidence_id", "id"),
    "tensions": ("tension_id", "id"),
    "tension_mappings": ("tension_mapping_id", "id"),
    "meta_narratives": ("meta_narrative_id", "narrative_id", "id"),
    "category_summaries": ("category_summary_id", "id"),
    "category_findings": ("finding_id", "category_finding_id", "id"),
    "scenarios": ("scenario_id", "id"),
    "scenario_pathways": ("pathway_id", "scenario_pathway_id", "id"),
    "scenario_indicators": ("indicator_id", "scenario_indicator_id", "id"),
    "scenario_actions": ("action_id", "scenario_action_id", "id"),
    "evidence_links": ("evidence_link_id", "id"),
    "review_flags": ("review_flag_id", "id"),
}

# Mapping-like entities may use a deterministic generated ID or the documented
# composite key.  Either representation is acceptable, but duplicates are not.
COMPOSITE_KEYS = {
    "item_tags": (("item_id", "tag"), ("item_id", "tag_id")),
    "item_cluster_assignments": (("item_id",),),
    "cluster_summaries": (("cluster_id",),),
    "cluster_meta_mappings": (("cluster_id", "meta_cluster_id"),),
    "theme_meta_mappings": (("theme_id", "meta_cluster_id"),),
    "theme_cluster_evidence": (("theme_id", "cluster_id"),),
    "tension_mappings": (("tension_id", "mapping_type", "mapped_id"),),
}

PUBLIC_FILE_COLLECTIONS = {
    "categories.json": "categories",
    "clusters.json": "clusters",
    "cluster_summaries.json": "cluster_summaries",
    "meta_clusters.json": "meta_clusters",
    "themes.json": "themes",
    "tensions.json": "tensions",
    "meta_narratives.json": "meta_narratives",
    "category_findings.json": "category_findings",
    "scenarios.json": "scenarios",
    "episodes.json": "episodes",
    "relationships.json": "relationships",
}

# Explicit conservative public record allowlists.  They intentionally omit raw
# item text, evidence quotations, model rationales, and detailed review data.
PUBLIC_RECORD_ALLOWLISTS = {
    "categories": {
        "id", "category_id", "name", "category_name", "description",
        "summary", "so_what",
        "category_type", "scope", "is_focal", "item_count", "cluster_count",
        "meta_cluster_count", "source_artifact_id",
    },
    "clusters": {
        "id", "cluster_id", "category_id", "name", "cluster_name",
        "definition", "inclusion_criteria", "exclusion_criteria",
        "near_neighbor_distinctions", "anchor_examples", "primary_count",
        "secondary_count", "total_count", "meta_cluster_ids",
        "is_meta_mapped", "source_artifact_id",
    },
    "cluster_summaries": {
        "id", "cluster_id", "category_id", "cluster_name", "summary", "cluster_summary", "key_themes",
        "subthemes", "recurring_themes", "strategic_significance", "operational_implications",
        "primary_count", "secondary_count", "weighted_count",
        "primary_vs_secondary_distinction", "primary_secondary_distinction", "conceptual_bridges",
        "representative_item_ids", "summary_confidence",
    },
    "meta_clusters": {
        "id", "meta_cluster_id", "category_id", "name", "meta_cluster_name",
        "definition", "cluster_ids", "included_cluster_ids", "cluster_count", "primary_count_total",
        "secondary_count_total", "salience", "category_synthesis",
        "representative_item_ids", "near_neighbor_distinctions", "source_artifact_id",
    },
    "themes": {
        "id", "theme_id", "name", "theme_name", "definition",
        "category_ids", "categories_present", "category_count",
        "meta_cluster_ids", "linked_meta_cluster_ids", "cluster_ids", "linked_cluster_ids", "cross_category_logic",
        "strategic_significance", "operational_implications",
        "boundary_conditions", "related_tension_ids", "representative_item_ids", "evidence_strength",
        "source_artifact_id",
    },
    "tensions": {
        "id", "tension_id", "name", "tension_name", "description",
        "pole_a_label", "pole_b_label", "pole_a_assumption",
        "pole_b_assumption", "tension_level", "category_ids",
        "categories_involved", "category_count", "cluster_ids",
        "cluster_count", "evidence_strength", "confidence", "key_terms",
        "source_artifact_id",
    },
    "meta_narratives": {
        "id", "meta_narrative_id", "narrative_id", "name", "title",
        "description", "summary", "definition", "short_version", "core_claim",
        "theme_ids", "supporting_theme_ids", "tension_ids", "supporting_tension_ids",
        "meta_cluster_ids", "cluster_ids", "category_ids",
        "strategic_significance", "operational_implications",
        "supporting_meta_cluster_ids", "representative_item_ids", "caveats",
        "confidence", "source_artifact_id",
    },
    "category_findings": {
        "id", "category_finding_id", "finding_id", "category_id", "name",
        "title", "summary", "finding", "core_finding", "key_patterns", "cluster_ids",
        "supporting_cluster_ids", "meta_cluster_ids", "supporting_meta_cluster_ids",
        "theme_ids", "tension_ids",
        "strategic_significance", "operational_implications",
        "unresolved_questions", "caveats", "confidence", "source_artifact_id",
    },
    "scenarios": {
        "id", "scenario_id", "name", "title", "description", "summary",
        "time_horizon", "timeframe", "scenario_type", "core_scenario",
        "driving_forces", "assumptions", "pathways", "indicators", "actions",
        "pathway_ids", "indicator_ids", "action_ids", "category_ids",
        "cluster_ids", "meta_cluster_ids", "theme_ids", "tension_ids",
        "strategic_implications", "operational_implications", "research_questions", "uncertainty_level",
        "alternative_outcomes",
        "source_artifact_id",
    },
    "episodes": {
        "id", "episode_id", "podcast", "episode_title", "title",
        "source_identity_count", "original_item_count",
        "reconciled_sensitivity_item_count",
    },
    "relationships": {
        "id", "relationship_id", "source_type", "source_id", "target_type",
        "target_id", "relationship_type", "weight", "count", "category_id",
        "source_artifact_id",
    },
}

# Fields added by the public exporter while assembling derived records.  These
# are allowlisted explicitly alongside the projection fields above.
PUBLIC_DERIVED_RECORD_FIELDS = {
    "scenarios": {"pathway", "indicators", "actions", "forecastDisclaimer"},
    "episodes": set(),
    "relationships": {
        "relationshipId", "relationshipType", "sourceId", "targetId",
        "interpretation",
    },
}

PUBLIC_RECONCILIATION_FIELDS = {
    "schemaVersion",
    "methodVersion",
    "status",
    "counts",
    "interpretation",
    "automaticRules",
    "limitations",
    "reanalysisRecommendation",
}

PUBLIC_RECONCILIATION_COUNT_FIELDS = {
    "canonicalEpisodes",
    "originalSourceIdentities",
    "confirmedAliasGroups",
    "sourceIdentitiesInConfirmedAliasGroups",
    "excludedConfirmedAliasSourceIdentities",
    "excludedNonEpisodeSourceIdentities",
    "likelyAliasSourceIdentities",
    "ambiguousSourceIdentities",
    "unresolvedSourceIdentities",
    "pendingDecisionRecords",
    "originalItems",
    "reconciledSensitivityItems",
    "originalFocalItems",
    "reconciledSensitivityFocalItems",
    "originalContextualItems",
    "reconciledSensitivityContextualItems",
}

PUBLIC_WRAPPER_KEYS = {
    "schemaVersion", "schema_version", "contentVersion", "content_version",
    "product", "title", "description", "methodology", "cautions", "counts",
    "summary", "records", "entries", "relationships", "categories", "clusters",
    "cluster_summaries", "meta_clusters", "themes", "tensions",
    "meta_narratives", "category_findings", "scenarios", "episodes", "coverage",
    "review_summary", "qa_report", "manifest", "files", "source_hashes",
    "source_row_counts", "normalized_entity_counts", "expected_vs_actual",
    "missing_references", "duplicate_ids", "unresolved_mappings",
    "review_counts", "ambiguity_counts", "narrative_count_mismatch",
    "public_export_checks", "deterministic_build", "status", "passed",
    "warnings", "errors", "notes", "known_limitations",
}

FORBIDDEN_PUBLIC_KEY_PATTERNS = (
    re.compile(r"transcript", re.I),
    re.compile(r"(?:^|_)evidence_(?:quote|excerpt)(?:$|_)", re.I),
    re.compile(r"(?:^|_)(?:full_text|item_text|raw_text)(?:$|_)", re.I),
    re.compile(r"rationale", re.I),
    re.compile(r"(?:^|_)(?:human|internal|reviewer|model)_notes?(?:$|_)", re.I),
    re.compile(r"review_queue", re.I),
    re.compile(r"(?:^|_)(?:coder|prompt_version|coded_timestamp)(?:$|_)", re.I),
    re.compile(r"(?:^|_)(?:source_file|local_path|workbook_path)(?:$|_)", re.I),
)


@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    code: str
    message: str
    context: Mapping[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "context": dict(sorted(self.context.items())),
        }


@dataclass
class ValidationReport:
    issues: list[ValidationIssue] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)
    comparisons: dict[str, dict[str, Any]] = field(default_factory=dict)
    missing_references: list[dict[str, Any]] = field(default_factory=list)
    duplicate_ids: list[dict[str, Any]] = field(default_factory=list)
    unresolved_mappings: list[dict[str, Any]] = field(default_factory=list)
    public_export_checks: dict[str, Any] = field(default_factory=dict)

    def add(
        self,
        severity: str,
        code: str,
        message: str,
        **context: Any,
    ) -> None:
        self.issues.append(ValidationIssue(severity, code, message, context))

    @property
    def errors(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "warning"]

    @property
    def passed(self) -> bool:
        return not self.errors

    def as_dict(self) -> dict[str, Any]:
        ordered_issues = sorted(
            (issue.as_dict() for issue in self.issues),
            key=lambda issue: (
                issue["severity"], issue["code"],
                json.dumps(issue["context"], sort_keys=True, default=str),
            ),
        )
        return {
            "passed": self.passed,
            "errors": sum(issue["severity"] == "error" for issue in ordered_issues),
            "warnings": sum(issue["severity"] == "warning" for issue in ordered_issues),
            "counts": dict(sorted(self.counts.items())),
            "expected_vs_actual": dict(sorted(self.comparisons.items())),
            "missing_references": sorted(
                self.missing_references,
                key=lambda row: json.dumps(row, sort_keys=True, default=str),
            ),
            "duplicate_ids": sorted(
                self.duplicate_ids,
                key=lambda row: json.dumps(row, sort_keys=True, default=str),
            ),
            "unresolved_mappings": sorted(
                self.unresolved_mappings,
                key=lambda row: json.dumps(row, sort_keys=True, default=str),
            ),
            "public_export_checks": dict(sorted(self.public_export_checks.items())),
            "issues": ordered_issues,
        }


class ValidationError(ValueError):
    """Raised when structural validation fails without hiding the QA report."""

    def __init__(self, message: str, report: Mapping[str, Any]):
        super().__init__(message)
        self.report = dict(report)


def canonical_json_bytes(payload: Any) -> bytes:
    """Return the repository's stable, UTF-8, pretty-printed JSON form."""

    return (
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


_CAMEL_BOUNDARY = re.compile(r"(?<!^)(?=[A-Z])")


def _snake_key(key: str) -> str:
    """Normalize a public camelCase field to the validator's internal spelling."""

    return _CAMEL_BOUNDARY.sub("_", key).replace("-", "_").casefold()


def _canonicalize_record(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            _snake_key(str(key)): _canonicalize_record(child)
            for key, child in value.items()
        }
    if isinstance(value, list):
        return [_canonicalize_record(child) for child in value]
    return value


def _canonicalize_dataset(dataset: Mapping[str, Any]) -> dict[str, Any]:
    # Collection names are governed snake_case names; only record/wrapper field
    # names are canonicalized so dataset routing remains explicit.
    return {
        str(collection): _canonicalize_record(value)
        for collection, value in dataset.items()
    }


def collection_records(dataset: Mapping[str, Any], name: str) -> list[dict[str, Any]]:
    """Get a normalized collection, accepting the documented wrapper forms."""

    value = dataset.get(name, [])
    if isinstance(value, list):
        return [record for record in value if isinstance(record, dict)]
    if isinstance(value, dict):
        for key in (name, "records", "entries", "relationships"):
            records = value.get(key)
            if isinstance(records, list):
                return [record for record in records if isinstance(record, dict)]
    return []


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return _text(value).casefold() in {"1", "true", "yes", "y", "required", "flagged"}


def _values(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [_text(item) for item in value if _text(item)]
    text = _text(value)
    if not text:
        return []
    return [part.strip() for part in re.split(r"[;,]", text) if part.strip()]


def _first(record: Mapping[str, Any], fields: Iterable[str]) -> tuple[str | None, str]:
    for field_name in fields:
        if field_name in record:
            return field_name, _text(record.get(field_name))
    return None, ""


def _record_key(collection: str, record: Mapping[str, Any]) -> tuple[Any, ...] | None:
    id_fields = ENTITY_ID_FIELDS.get(collection, ())
    field_name, value = _first(record, id_fields)
    if field_name:
        return (field_name, value)
    for fields in COMPOSITE_KEYS.get(collection, ()):
        if all(field_name in record for field_name in fields):
            return ("composite",) + tuple(_text(record.get(field_name)) for field_name in fields)
    return None


def _validate_collection_ids(
    dataset: Mapping[str, Any], report: ValidationReport
) -> None:
    for collection in REQUIRED_COLLECTIONS:
        records = collection_records(dataset, collection)
        seen: dict[tuple[Any, ...], int] = {}
        for index, record in enumerate(records):
            key = _record_key(collection, record)
            if key is None:
                # A small number of auxiliary collections can be empty or use a
                # source-defined shape; nonempty records still require a key.
                report.add(
                    "error", "missing_record_key",
                    f"{collection} record has no supported stable key.",
                    collection=collection, row=index + 1,
                )
                continue
            if any(not _text(part) for part in key[1:] if len(key) > 1) or (
                len(key) == 1 and not _text(key[0])
            ):
                report.add(
                    "error", "blank_id", f"{collection} record has a blank key.",
                    collection=collection, row=index + 1,
                )
                continue
            if key in seen:
                duplicate = {
                    "collection": collection,
                    "key": list(key),
                    "first_row": seen[key],
                    "duplicate_row": index + 1,
                }
                report.duplicate_ids.append(duplicate)
                report.add(
                    "error", "duplicate_id",
                    f"Duplicate stable key in {collection}.", **duplicate,
                )
            else:
                seen[key] = index + 1


def _id_set(dataset: Mapping[str, Any], collection: str) -> set[str]:
    fields = ENTITY_ID_FIELDS.get(collection, ())
    result: set[str] = set()
    for record in collection_records(dataset, collection):
        _, value = _first(record, fields)
        if value:
            result.add(value)
    return result


def _check_fk(
    report: ValidationReport,
    collection: str,
    row: int,
    field_name: str,
    value: Any,
    valid_ids: set[str],
    *,
    required: bool = False,
    explicitly_unresolved: bool = False,
) -> None:
    values = _values(value)
    if required and not values:
        if explicitly_unresolved:
            unresolved = {
                "collection": collection,
                "row": row,
                "field": field_name,
                "governance_known": False,
                "status": "explicitly-unresolved-source-reference",
            }
            report.unresolved_mappings.append(unresolved)
            report.add(
                "warning", "explicit_unresolved_reference",
                f"{collection}.{field_name} is unresolved in the source and was preserved without invention.",
                **unresolved,
            )
            return
        report.add(
            "error", "missing_required_reference",
            f"{collection}.{field_name} is required.",
            collection=collection, row=row, field=field_name,
        )
    for foreign_id in values:
        if foreign_id not in valid_ids:
            missing = {
                "collection": collection,
                "row": row,
                "field": field_name,
                "missing_id": foreign_id,
            }
            report.missing_references.append(missing)
            report.add(
                "error", "missing_foreign_key",
                f"{collection}.{field_name} references unknown ID {foreign_id!r}.",
                **missing,
            )


def _validate_foreign_keys(dataset: Mapping[str, Any], report: ValidationReport) -> None:
    ids = {name: _id_set(dataset, name) for name in ENTITY_ID_FIELDS}
    direct_rules = {
        "episodes": (("artifact_id", "artifacts", False),),
        "items": (
            ("episode_id", "episodes", True),
            ("category_id", "categories", True),
            ("source_artifact_id", "artifacts", False),
        ),
        "item_tags": (("item_id", "items", True),),
        "clusters": (
            ("category_id", "categories", True),
            ("source_artifact_id", "artifacts", False),
        ),
        "item_cluster_assignments": (
            ("item_id", "items", True),
            ("cluster_id", "clusters", False),
            ("primary_cluster_id", "clusters", False),
            ("secondary_cluster_id", "clusters", False),
        ),
        "cluster_summaries": (("cluster_id", "clusters", True),),
        "meta_clusters": (
            ("category_id", "categories", True),
            ("source_artifact_id", "artifacts", False),
        ),
        "cluster_meta_mappings": (
            ("cluster_id", "clusters", True),
            ("meta_cluster_id", "meta_clusters", True),
        ),
        "theme_meta_mappings": (
            ("theme_id", "themes", True),
            ("meta_cluster_id", "meta_clusters", True),
        ),
        "theme_cluster_evidence": (
            ("theme_id", "themes", True),
            ("cluster_id", "clusters", True),
            ("representative_item_ids", "items", False),
        ),
        "tension_mappings": (("tension_id", "tensions", True),),
        "category_findings": (("category_id", "categories", True),),
        "category_summaries": (("category_id", "categories", True),),
        "scenario_pathways": (("scenario_id", "scenarios", True),),
        "scenario_indicators": (
            ("scenario_id", "scenarios", True),
            ("pathway_id", "scenario_pathways", False),
        ),
        "scenario_actions": (
            ("scenario_id", "scenarios", True),
            ("pathway_id", "scenario_pathways", False),
        ),
    }
    unresolved_entity_ids = {
        _text(flag.get("entity_id"))
        for flag in collection_records(dataset, "review_flags")
        if "unresolved" in _text(flag.get("flag_type")).casefold()
        and _text(flag.get("entity_id"))
    }
    for collection, rules in direct_rules.items():
        for row, record in enumerate(collection_records(dataset, collection), 1):
            record_key = _record_key(collection, record)
            stable_id = _text(record_key[1]) if record_key and len(record_key) == 2 else ""
            unresolved_marker = _truthy(record.get("unresolved_reference")) or _text(
                record.get("resolution_status")
            ).casefold() in {"unresolved", "unmapped", "source-unresolved"}
            source = record.get("source") if isinstance(record.get("source"), Mapping) else {}
            has_portable_provenance = bool(
                _text(source.get("artifact_id") or source.get("file_name"))
                and _text(source.get("sheet"))
                and _text(source.get("row_number"))
            )
            explicitly_unresolved = bool(
                unresolved_marker
                and stable_id in unresolved_entity_ids
                and has_portable_provenance
            )
            for field_name, target, required in rules:
                if field_name in record or required:
                    _check_fk(
                        report, collection, row, field_name,
                        record.get(field_name), ids.get(target, set()),
                        required=required,
                        explicitly_unresolved=explicitly_unresolved,
                    )

    # Optional higher-synthesis link lists remain traceable when populated.
    synthesis_rules = {
        "themes": {
            "meta_cluster_ids": "meta_clusters",
            "linked_meta_cluster_ids": "meta_clusters",
            "cluster_ids": "clusters",
            "linked_cluster_ids": "clusters",
            "related_tension_ids": "tensions",
            "representative_item_ids": "items",
        },
        "tensions": {
            "cluster_ids": "clusters",
            "supporting_item_ids_pole_a": "items",
            "supporting_item_ids_pole_b": "items",
        },
        "meta_narratives": {
            "theme_ids": "themes", "supporting_theme_ids": "themes",
            "tension_ids": "tensions", "supporting_tension_ids": "tensions",
            "meta_cluster_ids": "meta_clusters", "supporting_meta_cluster_ids": "meta_clusters",
            "cluster_ids": "clusters",
            "category_ids": "categories", "representative_item_ids": "items",
        },
        "category_findings": {
            "theme_ids": "themes", "tension_ids": "tensions",
            "meta_cluster_ids": "meta_clusters", "supporting_meta_cluster_ids": "meta_clusters",
            "cluster_ids": "clusters", "supporting_cluster_ids": "clusters",
        },
        "scenarios": {
            "theme_ids": "themes", "tension_ids": "tensions",
            "meta_cluster_ids": "meta_clusters", "cluster_ids": "clusters",
            "category_ids": "categories",
        },
    }
    for collection, rules in synthesis_rules.items():
        for row, record in enumerate(collection_records(dataset, collection), 1):
            for field_name, target in rules.items():
                if field_name in record:
                    _check_fk(
                        report, collection, row, field_name, record.get(field_name),
                        ids.get(target, set()),
                    )

    mapping_targets = {
        "cross_cutting_theme": ids.get("themes", set()),
        "meta_cluster": ids.get("meta_clusters", set()),
    }
    for row, record in enumerate(collection_records(dataset, "tension_mappings"), 1):
        mapping_type = _text(
            record.get("mapped_entity_type", record.get("mapping_type"))
        ).casefold().replace("-", "_").replace(" ", "_")
        mapped_id = record.get("mapped_id")
        target_ids = mapping_targets.get(mapping_type)
        if target_ids is None:
            report.add(
                "error", "unsupported_tension_mapping_type",
                "Tension mapping type must be cross_cutting_theme or meta_cluster.",
                row=row, mapping_type=mapping_type,
                tension_id=_text(record.get("tension_id")),
            )
            continue
        _check_fk(
            report, "tension_mappings", row, "mapped_id", mapped_id,
            target_ids, required=True,
        )


def _item_is_focal(record: Mapping[str, Any]) -> bool:
    if "is_focal" in record:
        return _truthy(record.get("is_focal"))
    item_type = _text(
        record.get(
            "scope",
            record.get("item_scope", record.get("item_type", record.get("category_type"))),
        )
    ).casefold()
    return item_type not in {"contextual", "context", "background"}


def _validate_assignments(dataset: Mapping[str, Any], report: ValidationReport) -> None:
    items = collection_records(dataset, "items")
    assignments = collection_records(dataset, "item_cluster_assignments")
    item_ids = {
        _first(item, ENTITY_ID_FIELDS["items"])[1]: item
        for item in items
        if _first(item, ENTITY_ID_FIELDS["items"])[1]
    }
    category_scope = {
        _first(category, ENTITY_ID_FIELDS["categories"])[1]: _text(
            category.get("scope", category.get("category_type"))
        ).casefold()
        for category in collection_records(dataset, "categories")
    }

    def is_focal(item: Mapping[str, Any]) -> bool:
        if any(
            field_name in item
            for field_name in ("is_focal", "scope", "item_scope", "item_type", "category_type")
        ):
            return _item_is_focal(item)
        scope = category_scope.get(_text(item.get("category_id")), "")
        if scope:
            return scope not in {"contextual", "context", "background"}
        return True

    focal_ids = {item_id for item_id, item in item_ids.items() if is_focal(item)}
    contextual_ids = set(item_ids) - focal_ids
    role_based = any("assignment_role" in row or "cluster_id" in row for row in assignments)
    if role_based:
        primary_rows = [
            row for row in assignments
            if _text(row.get("assignment_role")).casefold() == "primary"
        ]
        secondary_rows = [
            row for row in assignments
            if _text(row.get("assignment_role")).casefold() == "secondary"
        ]
    else:
        primary_rows = assignments
        secondary_rows = assignments
    assignment_counts = Counter(_text(row.get("item_id")) for row in primary_rows)

    for item_id in sorted(focal_ids):
        count = assignment_counts.get(item_id, 0)
        if count != 1:
            report.add(
                "error", "focal_primary_assignment_cardinality",
                "Every focal item must have exactly one assignment record.",
                item_id=item_id, assignment_count=count,
            )
    incorrectly_assigned = sorted(
        contextual_ids
        & {_text(row.get("item_id")) for row in assignments if _text(row.get("item_id"))}
    )
    for item_id in incorrectly_assigned:
        report.add(
            "error", "contextual_item_assigned_as_focal",
            "Contextual item appears in the focal assignment collection.",
            item_id=item_id,
        )

    if role_based:
        valid_roles = {"primary", "secondary"}
        secondary_counts = Counter(_text(row.get("item_id")) for row in secondary_rows)
        for item_id in sorted(focal_ids):
            if secondary_counts.get(item_id, 0) != 1:
                report.add(
                    "error", "focal_secondary_assignment_cardinality",
                    "Every focal item must retain exactly one normalized secondary row, including NONE.",
                    item_id=item_id, assignment_count=secondary_counts.get(item_id, 0),
                )
        for row, assignment in enumerate(assignments, 1):
            role = _text(assignment.get("assignment_role")).casefold()
            cluster_id = _text(assignment.get("cluster_id"))
            is_none = _truthy(assignment.get("is_none"))
            if role not in valid_roles:
                report.add(
                    "error", "invalid_assignment_role",
                    "Assignment role must be primary or secondary.", row=row, role=role,
                )
            if role == "primary" and (not cluster_id or is_none):
                report.add(
                    "error", "blank_primary_assignment",
                    "Primary assignment has no substantive cluster.", row=row,
                    item_id=_text(assignment.get("item_id")),
                )
            if cluster_id.casefold() in {"none", "n/a", "na", "null"}:
                report.add(
                    "error", "secondary_none_not_normalized",
                    "Secondary assignment sentinel must be normalized to null.",
                    row=row, item_id=_text(assignment.get("item_id")), value=cluster_id,
                )
            if role == "secondary" and is_none != (not cluster_id):
                report.add(
                    "error", "secondary_none_state_inconsistent",
                    "Secondary isNone must be true exactly when clusterId is null.",
                    row=row, item_id=_text(assignment.get("item_id")),
                )
    else:
        for row, assignment in enumerate(assignments, 1):
            primary = _text(assignment.get("primary_cluster_id"))
            if not primary:
                report.add(
                    "error", "blank_primary_assignment",
                    "Assignment has no primary cluster.", row=row,
                    item_id=_text(assignment.get("item_id")),
                )
            secondary = assignment.get("secondary_cluster_id")
            if _text(secondary).casefold() in {"none", "n/a", "na", "null"}:
                report.add(
                    "error", "secondary_none_not_normalized",
                    "Secondary assignment sentinel must be normalized to null.",
                    row=row, item_id=_text(assignment.get("item_id")),
                    value=_text(secondary),
                )

    review_item_ids = {
        _text(row.get("item_id")) for row in assignments
        if _truthy(row.get("review_required")) and _text(row.get("item_id"))
    }
    ambiguity_item_ids = {
        _text(row.get("item_id")) for row in assignments
        if _truthy(row.get("ambiguity_flag")) and _text(row.get("item_id"))
    }
    if role_based:
        substantive_secondary = sum(bool(_text(row.get("cluster_id"))) for row in secondary_rows)
        secondary_none = sum(not _text(row.get("cluster_id")) for row in secondary_rows)
    else:
        substantive_secondary = sum(
            bool(_text(row.get("secondary_cluster_id")))
            and _text(row.get("secondary_cluster_id")).casefold() not in {"none", "n/a", "na", "null"}
            for row in secondary_rows
        )
        secondary_none = sum(
            not _text(row.get("secondary_cluster_id"))
            or _text(row.get("secondary_cluster_id")).casefold() in {"none", "n/a", "na", "null"}
            for row in secondary_rows
        )

    report.counts.update({
        "focal_items": len(focal_ids),
        "contextual_items": len(contextual_ids),
        "primary_assignments": sum(
            bool(_text(row.get("cluster_id"))) for row in primary_rows
        ) if role_based else sum(bool(_text(row.get("primary_cluster_id"))) for row in primary_rows),
        "substantive_secondary_assignments": substantive_secondary,
        "secondary_none": secondary_none,
        "review_required_assignments": len(review_item_ids),
        "ambiguity_flagged_assignments": len(ambiguity_item_ids),
    })


def _validate_cluster_content(dataset: Mapping[str, Any], report: ValidationReport) -> None:
    for row, cluster in enumerate(collection_records(dataset, "clusters"), 1):
        if not _text(cluster.get("definition")):
            report.add(
                "error", "cluster_definition_missing",
                "Cluster definition was not retained.", row=row,
                cluster_id=_first(cluster, ENTITY_ID_FIELDS["clusters"])[1],
            )
        # Fields must be present even if the source value is null; their absence
        # indicates the source schema was accidentally narrowed.
        for field_name in ("inclusion_criteria", "exclusion_criteria"):
            if field_name not in cluster:
                report.add(
                    "error", "cluster_governance_field_missing",
                    f"Cluster is missing retained field {field_name}.", row=row,
                    cluster_id=_first(cluster, ENTITY_ID_FIELDS["clusters"])[1],
                    field=field_name,
                )


def _validate_category_summaries(
    dataset: Mapping[str, Any], report: ValidationReport
) -> None:
    categories = collection_records(dataset, "categories")
    summaries = collection_records(dataset, "category_summaries")
    focal_category_ids = {
        _first(category, ENTITY_ID_FIELDS["categories"])[1]
        for category in categories
        if _text(category.get("scope")).casefold() == "focal"
        and _first(category, ENTITY_ID_FIELDS["categories"])[1]
    }
    summary_counts = Counter(
        _text(summary.get("category_id")) for summary in summaries
        if _text(summary.get("category_id"))
    )
    for category_id, count in sorted(summary_counts.items()):
        if count > 1:
            report.add(
                "error", "duplicate_category_summary_assignment",
                "A category may have at most one canonical category summary.",
                category_id=category_id, summary_count=count,
            )
    for category_id in sorted(focal_category_ids):
        if summary_counts.get(category_id, 0) != 1:
            report.add(
                "error", "missing_focal_category_summary",
                "Every focal category must have exactly one category summary.",
                category_id=category_id,
                summary_count=summary_counts.get(category_id, 0),
            )
    for row, summary in enumerate(summaries, 1):
        summary_id = _first(summary, ENTITY_ID_FIELDS["category_summaries"])[1]
        for field_name in ("summary", "so_what"):
            if not _text(summary.get(field_name)):
                report.add(
                    "error", "category_summary_content_missing",
                    f"Category summary must retain nonblank {field_name}.",
                    row=row, category_summary_id=summary_id, field=field_name,
                )


def _validate_meta_coverage(dataset: Mapping[str, Any], report: ValidationReport) -> None:
    cluster_ids = _id_set(dataset, "clusters")
    mapped_ids = {
        _text(row.get("cluster_id"))
        for row in collection_records(dataset, "cluster_meta_mappings")
        if _text(row.get("cluster_id"))
    }
    unmapped = cluster_ids - mapped_ids
    for cluster_id in sorted(unmapped):
        known = cluster_id in KNOWN_UNMAPPED_CLUSTERS
        record = {
            "cluster_id": cluster_id,
            "cluster_name": KNOWN_UNMAPPED_CLUSTERS.get(cluster_id),
            "governance_known": known,
        }
        report.unresolved_mappings.append(record)
        report.add(
            "warning" if known else "error",
            "known_unmapped_cluster" if known else "unexpected_unmapped_cluster",
            "Intermediate cluster has no meta-cluster assignment.", **record,
        )

    meta_records = {
        _first(meta_cluster, ENTITY_ID_FIELDS["meta_clusters"])[1]: meta_cluster
        for meta_cluster in collection_records(dataset, "meta_clusters")
        if _first(meta_cluster, ENTITY_ID_FIELDS["meta_clusters"])[1]
    }
    mapped_meta_ids = {
        _text(row.get("meta_cluster_id"))
        for row in collection_records(dataset, "cluster_meta_mappings")
        if _text(row.get("meta_cluster_id"))
    }
    for meta_cluster_id in sorted(set(meta_records) - mapped_meta_ids):
        known = meta_cluster_id in KNOWN_EMPTY_META_CLUSTERS
        record = {
            "entity_type": "meta_cluster",
            "meta_cluster_id": meta_cluster_id,
            "meta_cluster_name": _text(meta_records[meta_cluster_id].get("name")),
            "governance_known": known,
            "governance_note": KNOWN_EMPTY_META_CLUSTERS.get(meta_cluster_id),
        }
        report.unresolved_mappings.append(record)
        report.add(
            "warning" if known else "error",
            "known_empty_meta_cluster" if known else "unexpected_empty_meta_cluster",
            "Meta-cluster has no source cluster-mapping rows; membership was not invented.",
            **record,
        )


def _validate_tensions(dataset: Mapping[str, Any], report: ValidationReport) -> None:
    artifact_files = {
        _first(artifact, ENTITY_ID_FIELDS["artifacts"])[1]: _text(
            artifact.get("file_name")
        )
        for artifact in collection_records(dataset, "artifacts")
    }
    for row, tension in enumerate(collection_records(dataset, "tensions"), 1):
        tension_id = _first(tension, ENTITY_ID_FIELDS["tensions"])[1]
        for field_name in ("pole_a_label", "pole_b_label"):
            if not _text(tension.get(field_name)):
                report.add(
                    "error", "tension_pole_missing",
                    f"Tension must retain {field_name}.", row=row,
                    tension_id=tension_id, field=field_name,
                )
        source = tension.get("source") if isinstance(tension.get("source"), Mapping) else {}
        artifact_id = _text(tension.get("source_artifact_id") or source.get("artifact_id"))
        artifact = _text(
            tension.get("source_workbook") or source.get("file_name")
            or artifact_files.get(artifact_id) or artifact_id
        ).casefold()
        if artifact and "tensions_debates_rebuilt" not in artifact and artifact not in {
            "art-tensions", "artifact-tensions", "tensions-debates-rebuilt"
        }:
            report.add(
                "error", "noncanonical_tension_provenance",
                "Canonical tension provenance must identify tensions_debates_rebuilt.xlsx.",
                row=row, tension_id=tension_id,
                source_artifact=_text(tension.get("source_artifact_id", tension.get("source_workbook"))),
            )


def _populate_counts(dataset: Mapping[str, Any], report: ValidationReport) -> None:
    for collection in REQUIRED_COLLECTIONS:
        report.counts.setdefault(collection, len(collection_records(dataset, collection)))


def _compare_expected(
    report: ValidationReport,
    expected_counts: Mapping[str, int],
) -> None:
    for metric, expected in expected_counts.items():
        actual = report.counts.get(metric, 0)
        status = "match" if actual == expected else "mismatch"
        report.comparisons[metric] = {
            "expected": expected, "actual": actual, "status": status,
            "governance_known": False,
        }
        if actual != expected:
            report.add(
                "warning", "expected_count_mismatch",
                "Actual source-derived count differs from the validation expectation; source data was not altered.",
                metric=metric, expected=expected, actual=actual,
            )

    # The source has N01-N07 while earlier project documentation expected eight.
    actual_narratives = report.counts.get("meta_narratives", 0)
    report.comparisons["documented_meta_narratives"] = {
        "expected": 8,
        "actual": actual_narratives,
        "status": "governance_known_mismatch" if actual_narratives == 7 else (
            "match" if actual_narratives == 8 else "mismatch"
        ),
        "governance_known": actual_narratives == 7,
    }
    if actual_narratives == 7:
        report.add(
            "warning", "known_meta_narrative_count_mismatch",
            "Source contains seven meta-narratives (N01-N07); prior project documentation expected eight.",
            expected=8, actual=7,
        )


def validate_normalized_dataset(
    dataset: Mapping[str, Any],
    *,
    expected_counts: Mapping[str, int] | None = None,
) -> ValidationReport:
    """Validate normalized entities and return a stable structured report."""

    dataset = _canonicalize_dataset(dataset)
    report = ValidationReport()
    for collection in REQUIRED_COLLECTIONS:
        if collection not in dataset:
            report.add(
                "error", "missing_collection",
                f"Normalized dataset is missing collection {collection!r}.",
                collection=collection,
            )
    _populate_counts(dataset, report)
    _validate_collection_ids(dataset, report)
    _validate_foreign_keys(dataset, report)
    _validate_assignments(dataset, report)
    _validate_cluster_content(dataset, report)
    _validate_category_summaries(dataset, report)
    _validate_meta_coverage(dataset, report)
    _validate_tensions(dataset, report)
    _compare_expected(
        report,
        EXPECTED_BASELINE_COUNTS if expected_counts is None else expected_counts,
    )
    return report


def _walk_keys(value: Any, path: tuple[str, ...] = ()) -> Iterable[tuple[tuple[str, ...], str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            yield path, key_text, child
            yield from _walk_keys(child, path + (key_text,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_keys(child, path + (str(index),))


def _public_record_list(payload: Any, collection: str) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if not isinstance(payload, dict):
        return []
    for key in (collection, "records", "entries", "relationships"):
        rows = payload.get(key)
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


PUBLIC_ENDPOINT_COLLECTIONS = {
    "category": ("categories.json", "categories", "categoryId"),
    "cluster": ("clusters.json", "clusters", "clusterId"),
    "metaCluster": ("meta_clusters.json", "meta_clusters", "metaClusterId"),
    "theme": ("themes.json", "themes", "themeId"),
    "tension": ("tensions.json", "tensions", "tensionId"),
}


def _payload_by_basename(public_outputs: Mapping[str, Any], filename: str) -> Any:
    for supplied_name, payload in public_outputs.items():
        if Path(str(supplied_name)).name == filename:
            return payload
    return None


def _validate_public_relationships(
    public_outputs: Mapping[str, Any], report: ValidationReport
) -> int:
    payload = _payload_by_basename(public_outputs, "relationships.json")
    if payload is None:
        return 0
    relationships = _public_record_list(payload, "relationships")
    endpoint_ids: dict[str, set[str]] = {}
    for entity_type, (filename, collection, id_field) in PUBLIC_ENDPOINT_COLLECTIONS.items():
        entity_payload = _payload_by_basename(public_outputs, filename)
        endpoint_ids[entity_type] = {
            _text(record.get(id_field))
            for record in _public_record_list(entity_payload, collection)
            if _text(record.get(id_field))
        }

    errors_before = len(report.errors)
    relationship_ids: dict[str, int] = {}
    for row, relationship in enumerate(relationships, 1):
        relationship_id = _text(relationship.get("relationshipId"))
        if not relationship_id:
            report.add(
                "error", "public_relationship_id_missing",
                "Public relationship must have a stable nonblank relationshipId.",
                row=row,
            )
        elif relationship_id in relationship_ids:
            report.add(
                "error", "duplicate_public_relationship_id",
                "Public relationshipId must be unique.", row=row,
                relationship_id=relationship_id,
                first_row=relationship_ids[relationship_id],
            )
        else:
            relationship_ids[relationship_id] = row

        relationship_type = _text(relationship.get("relationshipType"))
        contract = PUBLIC_RELATIONSHIP_SCHEMA.get(relationship_type)
        if contract is None:
            report.add(
                "error", "unsupported_public_relationship_type",
                "Public relationshipType is outside the canonical vocabulary.",
                row=row, relationship_id=relationship_id,
                relationship_type=relationship_type,
            )
            continue
        expected_source_type, expected_target_type = contract
        source_type = _text(relationship.get("sourceType"))
        target_type = _text(relationship.get("targetType"))
        if (source_type, target_type) != contract:
            report.add(
                "error", "public_relationship_endpoint_type_mismatch",
                "Relationship endpoint types do not match relationshipType.",
                row=row, relationship_id=relationship_id,
                relationship_type=relationship_type,
                expected_source_type=expected_source_type,
                actual_source_type=source_type,
                expected_target_type=expected_target_type,
                actual_target_type=target_type,
            )
            continue
        interpretation = _text(relationship.get("interpretation")).casefold()
        if interpretation != "semantic":
            report.add(
                "error", "public_relationship_not_semantic",
                "Public relationships must be explicitly labeled semantic, never causal.",
                row=row, relationship_id=relationship_id,
                interpretation=interpretation,
            )
        for endpoint, entity_type in (
            ("source", source_type), ("target", target_type)
        ):
            endpoint_id = _text(relationship.get(f"{endpoint}Id"))
            if not endpoint_id:
                report.add(
                    "error", "public_relationship_endpoint_missing",
                    "Public relationship endpoint ID is blank.",
                    row=row, relationship_id=relationship_id, endpoint=endpoint,
                    entity_type=entity_type,
                )
            elif endpoint_id not in endpoint_ids.get(entity_type, set()):
                report.add(
                    "error", "public_relationship_endpoint_unresolved",
                    "Public relationship endpoint does not resolve to a public entity.",
                    row=row, relationship_id=relationship_id, endpoint=endpoint,
                    entity_type=entity_type, endpoint_id=endpoint_id,
                )
    return len(report.errors) - errors_before


def _validate_public_corpus_reconciliation(
    payload: Any, report: ValidationReport
) -> int:
    """Validate the deliberately small public reconciliation aggregate."""

    errors_before = len(report.errors)
    if not isinstance(payload, Mapping):
        report.add(
            "error",
            "public_reconciliation_not_object",
            "corpus_reconciliation.json must contain one aggregate object.",
        )
        return len(report.errors) - errors_before

    unexpected = sorted(set(payload) - PUBLIC_RECONCILIATION_FIELDS)
    missing = sorted(PUBLIC_RECONCILIATION_FIELDS - set(payload))
    for field_name in unexpected:
        report.add(
            "error",
            "public_reconciliation_field_not_allowlisted",
            "Public reconciliation aggregate contains an unexpected field.",
            field=field_name,
        )
    for field_name in missing:
        report.add(
            "error",
            "public_reconciliation_field_missing",
            "Public reconciliation aggregate is missing a required field.",
            field=field_name,
        )

    counts = payload.get("counts")
    if not isinstance(counts, Mapping):
        report.add(
            "error",
            "public_reconciliation_counts_not_object",
            "Public reconciliation counts must be an object.",
        )
    else:
        unexpected_counts = sorted(
            set(counts) - PUBLIC_RECONCILIATION_COUNT_FIELDS
        )
        missing_counts = sorted(
            PUBLIC_RECONCILIATION_COUNT_FIELDS - set(counts)
        )
        for field_name in unexpected_counts:
            report.add(
                "error",
                "public_reconciliation_count_not_allowlisted",
                "Public reconciliation counts contain an unexpected field.",
                field=field_name,
            )
        for field_name in missing_counts:
            report.add(
                "error",
                "public_reconciliation_count_missing",
                "Public reconciliation counts are missing a required field.",
                field=field_name,
            )
        for field_name, value in counts.items():
            if field_name in PUBLIC_RECONCILIATION_COUNT_FIELDS and (
                isinstance(value, bool) or not isinstance(value, int) or value < 0
            ):
                report.add(
                    "error",
                    "public_reconciliation_count_invalid",
                    "Public reconciliation counts must be non-negative integers.",
                    field=field_name,
                )

    if payload.get("schemaVersion") != "1.1":
        report.add(
            "error",
            "public_reconciliation_schema_mismatch",
            "Public reconciliation aggregate must use Schema v1.1.",
        )
    if payload.get("status") not in {"complete", "human-review-required"}:
        report.add(
            "error",
            "public_reconciliation_status_invalid",
            "Public reconciliation status is not governed.",
        )
    if payload.get("reanalysisRecommendation") not in {
        "full-pipeline-reanalysis-recommended",
        "partial-count-and-coverage-remediation-warranted",
        "human-adjudication-required-before-public-count-change",
    }:
        report.add(
            "error",
            "public_reanalysis_recommendation_invalid",
            "Public reconciliation re-analysis recommendation is not governed.",
        )

    private_tokens = {
        "sourceIdentityId",
        "sourceFile",
        "candidateCanonicalEpisodeId",
        "mappingBasis",
        "confidence",
        "aliasGroupId",
    }
    for path, key, _value in _walk_keys(payload):
        if key in private_tokens:
            report.add(
                "error",
                "private_reconciliation_detail_published",
                "Public reconciliation aggregate exposes private pair-level detail.",
                path=".".join(path + (key,)),
            )
    return len(report.errors) - errors_before


def validate_public_outputs(public_outputs: Mapping[str, Any]) -> ValidationReport:
    """Validate public JSON payloads against the conservative publication boundary."""

    report = ValidationReport()
    forbidden_hits: list[dict[str, Any]] = []
    allowlist_hits: list[dict[str, Any]] = []
    xlsx_blob_hits: list[dict[str, Any]] = []
    for supplied_name, payload in sorted(public_outputs.items()):
        filename = Path(str(supplied_name)).name
        for path, key, value in _walk_keys(payload):
            normalized_key = _snake_key(key)
            if any(pattern.search(normalized_key) for pattern in FORBIDDEN_PUBLIC_KEY_PATTERNS):
                hit = {"file": filename, "path": ".".join(path + (key,))}
                forbidden_hits.append(hit)
                report.add(
                    "error", "forbidden_public_field",
                    "Public output contains a private/internal field.", **hit,
                )
            if isinstance(value, str) and value.startswith("PK\x03\x04"):
                hit = {"file": filename, "path": ".".join(path + (key,))}
                xlsx_blob_hits.append(hit)
                report.add(
                    "error", "xlsx_blob_in_public_output",
                    "Public output appears to contain an XLSX/ZIP data blob.", **hit,
                )

        collection = PUBLIC_FILE_COLLECTIONS.get(filename)
        if not collection:
            continue
        allowlist = PUBLIC_RECORD_ALLOWLISTS[collection] | PUBLIC_DERIVED_RECORD_FIELDS.get(collection, set())
        normalized_allowlist = {_snake_key(field_name) for field_name in allowlist}
        for row, record in enumerate(_public_record_list(payload, collection), 1):
            unexpected = sorted(
                field_name for field_name in record
                if _snake_key(field_name) not in normalized_allowlist
            )
            for field_name in unexpected:
                hit = {"file": filename, "row": row, "field": field_name}
                allowlist_hits.append(hit)
                report.add(
                    "error", "public_field_not_allowlisted",
                    "Public record contains a field outside its explicit allowlist.",
                    **hit,
                )

    relationship_errors = _validate_public_relationships(public_outputs, report)
    reconciliation_errors = 0
    if "corpus_reconciliation.json" in public_outputs:
        reconciliation_errors = _validate_public_corpus_reconciliation(
            public_outputs["corpus_reconciliation.json"], report
        )
    report.public_export_checks = {
        "files_checked": len(public_outputs),
        "forbidden_field_hits": len(forbidden_hits),
        "allowlist_violations": len(allowlist_hits),
        "xlsx_blob_hits": len(xlsx_blob_hits),
        "relationship_errors": relationship_errors,
        "reconciliation_errors": reconciliation_errors,
        "passed": not (
            forbidden_hits
            or allowlist_hits
            or xlsx_blob_hits
            or relationship_errors
            or reconciliation_errors
        ),
    }
    return report


def merge_reports(*reports: ValidationReport) -> ValidationReport:
    """Combine normalized/public reports without losing machine-readable detail."""

    merged = ValidationReport()
    for report in reports:
        merged.issues.extend(report.issues)
        merged.counts.update(report.counts)
        merged.comparisons.update(report.comparisons)
        merged.missing_references.extend(report.missing_references)
        merged.duplicate_ids.extend(report.duplicate_ids)
        merged.unresolved_mappings.extend(report.unresolved_mappings)
        merged.public_export_checks.update(report.public_export_checks)
    return merged


def validate_reconciliation_dataset(
    historical_dataset: Mapping[str, Any],
    reconciled_dataset: Mapping[str, Any],
    private_payloads: Mapping[str, Any],
    public_aggregate: Mapping[str, Any],
) -> list[str]:
    """Validate Schema v1.1 reconciliation without rewriting v1.0 history."""

    errors: list[str] = []

    def fail(message: str) -> None:
        errors.append(message)

    historical_episodes = list(historical_dataset.get("episodes", ()))
    source_identities = list(
        reconciled_dataset.get("episode_source_identities", ())
    )
    mappings = list(reconciled_dataset.get("episode_source_mappings", ()))
    episodes = list(reconciled_dataset.get("episodes", ()))
    flags = list(reconciled_dataset.get("episode_reconciliation_flags", ()))

    historical_source_ids = [
        str(row.get("episodeId") or "") for row in historical_episodes
    ]
    source_ids = [
        str(row.get("sourceIdentityId") or "") for row in source_identities
    ]
    mapping_source_ids = [
        str(row.get("sourceIdentityId") or "") for row in mappings
    ]
    episode_ids = [str(row.get("episodeId") or "") for row in episodes]

    for label, values in (
        ("historical source identity", historical_source_ids),
        ("source identity", source_ids),
        ("source mapping", mapping_source_ids),
        ("canonical episode", episode_ids),
    ):
        if any(not value for value in values):
            fail(f"A {label} has a blank stable ID.")
        if len(values) != len(set(values)):
            fail(f"Duplicate {label} IDs were generated.")

    if set(source_ids) != set(historical_source_ids):
        fail("Source-identity reconciliation dropped or invented a historical identity.")
    if set(mapping_source_ids) != set(source_ids):
        fail("Every source identity must have exactly one reconciliation mapping.")

    allowed_statuses = {
        "unique", "confirmed-alias", "likely-alias", "ambiguous",
        "unresolved", "excluded-non-episode",
    }
    episode_id_set = set(episode_ids)
    mapping_by_source = {
        str(row.get("sourceIdentityId")): row for row in mappings
    }
    for row in mappings:
        source_id = str(row.get("sourceIdentityId") or "")
        status = str(row.get("mappingStatus") or "")
        canonical_id = row.get("canonicalEpisodeId")
        if status not in allowed_statuses:
            fail(f"Source identity {source_id} has unsupported status {status!r}.")
        if status in {"likely-alias", "ambiguous", "unresolved"} and row.get(
            "collapseEligible"
        ):
            fail(f"Unconfirmed source identity {source_id} is collapse-eligible.")
        if canonical_id and str(canonical_id) not in episode_id_set:
            fail(f"Source identity {source_id} maps to an unknown canonical episode.")

    source_membership_counts: Counter[str] = Counter()
    for episode in episodes:
        episode_id = str(episode.get("episodeId") or "")
        canonical_source = str(episode.get("canonicalSourceIdentityId") or "")
        source_members = [str(value) for value in episode.get("sourceIdentityIds", ())]
        if canonical_source != episode_id:
            fail(f"Canonical episode {episode_id} does not preserve its selected EPI ID.")
        if canonical_source not in source_members or not source_members:
            fail(f"Canonical episode {episode_id} has no canonical source member.")
        if len(source_members) != len(set(source_members)):
            fail(f"Canonical episode {episode_id} repeats a source identity.")
        for source_id in source_members:
            source_membership_counts[source_id] += 1
            mapping = mapping_by_source.get(source_id)
            if not mapping or str(mapping.get("canonicalEpisodeId") or "") != episode_id:
                fail(
                    f"Canonical episode {episode_id} has an inconsistent source mapping."
                )
        canonical_mapping = mapping_by_source.get(canonical_source, {})
        episode_status = str(episode.get("reconciliationStatus") or "")
        expected_role = (
            "candidate"
            if episode_status in {"likely-alias", "ambiguous", "unresolved"}
            else "canonical"
        )
        if canonical_mapping.get("mappingRole") != expected_role:
            fail(
                f"Episode {episode_id} requires {expected_role!r} mapping role "
                f"for reconciliation status {episode_status!r}."
            )

    for mapping in mappings:
        source_id = str(mapping.get("sourceIdentityId") or "")
        status = str(mapping.get("mappingStatus") or "")
        if status == "excluded-non-episode":
            if source_membership_counts[source_id]:
                fail(f"Excluded source identity {source_id} appears in an episode.")
            continue
        if source_membership_counts[source_id] != 1:
            fail(
                f"Source identity {source_id} must appear exactly once in canonical "
                "episode membership."
            )
        if status in {"likely-alias", "ambiguous", "unresolved"} and mapping.get(
            "mappingRole"
        ) != "candidate":
            fail(f"Unconfirmed source identity {source_id} must have candidate role.")

    historical_items = {
        str(row.get("itemId")): row for row in historical_dataset.get("items", ())
    }
    reconciled_items = {
        str(row.get("itemId")): row for row in reconciled_dataset.get("items", ())
    }
    if set(historical_items) != set(reconciled_items):
        fail("Reconciliation changed the historical item ID set.")
    for item_id, historical in historical_items.items():
        reconciled = reconciled_items.get(item_id, {})
        source_id = str(reconciled.get("sourceIdentityId") or "")
        if source_id != str(historical.get("episodeId") or ""):
            fail(f"Item {item_id} lost its historical source-identity provenance.")
            continue
        mapping = mapping_by_source.get(source_id)
        if not mapping or reconciled.get("episodeId") != mapping.get(
            "canonicalEpisodeId"
        ):
            fail(f"Item {item_id} has an inconsistent canonical episode mapping.")

    required_private_files = {
        "episode_source_reconciliation.json",
        "alias_groups.json",
        "reconciliation_review_queue.json",
        "item_sensitivity_summary.json",
        "cluster_sensitivity.json",
        "higher_order_support_sensitivity.json",
        "corpus_reconciliation_report.json",
    }
    if set(private_payloads) != required_private_files:
        fail("Private reconciliation output set does not match the governed contract.")

    alias_groups = private_payloads.get("alias_groups.json", [])
    if not isinstance(alias_groups, list):
        fail("alias_groups.json must contain a list.")
        alias_groups = []
    alias_group_ids = [str(group.get("aliasGroupId") or "") for group in alias_groups]
    if any(not alias_group_id for alias_group_id in alias_group_ids):
        fail("A confirmed alias group has a blank stable ID.")
    if len(alias_group_ids) != len(set(alias_group_ids)):
        fail("Duplicate confirmed alias-group IDs were generated.")
    grouped_source_ids: set[str] = set()
    for group in alias_groups:
        alias_group_id = str(group.get("aliasGroupId") or "")
        members = [str(member) for member in group.get("sourceIdentityIds", ())]
        canonical_source = str(group.get("canonicalSourceIdentityId") or "")
        if len(members) < 2:
            fail("A confirmed alias group has fewer than two source identities.")
        if len(members) != len(set(members)):
            fail(f"Confirmed alias group {alias_group_id} repeats a source identity.")
        overlapping = sorted(set(members) & grouped_source_ids)
        if overlapping:
            fail(
                f"Confirmed alias groups overlap on source identities: "
                f"{', '.join(overlapping)}."
            )
        grouped_source_ids.update(members)
        if members.count(canonical_source) != 1:
            fail("A confirmed alias group does not have exactly one canonical source.")
        member_mappings = [mapping_by_source.get(member, {}) for member in members]
        if any(row.get("mappingStatus") != "confirmed-alias" for row in member_mappings):
            fail(f"Alias-group {alias_group_id} member lacks confirmed-alias status.")
        if any(str(row.get("aliasGroupId") or "") != alias_group_id for row in member_mappings):
            fail(f"Alias-group {alias_group_id} membership disagrees with its mappings.")
        if sum(row.get("mappingRole") == "canonical" for row in member_mappings) != 1:
            fail(f"Alias-group {alias_group_id} does not have one canonical mapping role.")
        canonical_episode = str(group.get("canonicalEpisodeId") or "")
        if any(
            str(row.get("canonicalEpisodeId") or "") != canonical_episode
            for row in member_mappings
        ):
            fail(f"Alias-group {alias_group_id} mappings target different episodes.")

    confirmed_mapping_ids = {
        str(row.get("sourceIdentityId") or "")
        for row in mappings
        if row.get("mappingStatus") == "confirmed-alias"
    }
    if grouped_source_ids != confirmed_mapping_ids:
        fail("Confirmed-alias mappings and alias-group membership are not equivalent.")

    review_queue = private_payloads.get("reconciliation_review_queue.json", [])
    if not isinstance(review_queue, list):
        fail("reconciliation_review_queue.json must contain a list.")
        review_queue = []
    pending_flags = [row for row in flags if row.get("status") == "pending"]
    review_ids = [
        str(row.get("episodeReconciliationFlagId") or "") for row in review_queue
    ]
    pending_ids = [
        str(row.get("episodeReconciliationFlagId") or "") for row in pending_flags
    ]
    if any(not flag_id for flag_id in review_ids + pending_ids):
        fail("A pending reconciliation flag or review record has a blank stable ID.")
    if len(review_ids) != len(set(review_ids)) or len(pending_ids) != len(set(pending_ids)):
        fail("Duplicate pending reconciliation flag IDs were generated.")
    if set(review_ids) != set(pending_ids):
        fail("The reconciliation review queue does not match pending flags.")
    elif (
        {str(row.get("episodeReconciliationFlagId") or ""): row for row in review_queue}
        != {
            str(row.get("episodeReconciliationFlagId") or ""): row
            for row in pending_flags
        }
    ):
        fail("The reconciliation review queue does not exactly preserve pending flags.")

    counts = public_aggregate.get("counts", {})
    if not isinstance(counts, Mapping):
        fail("Public reconciliation aggregate has no counts object.")
        counts = {}
    expected_counts = {
        "canonicalEpisodes": len(episodes),
        "originalSourceIdentities": len(source_identities),
        "confirmedAliasGroups": len(alias_groups),
        "pendingDecisionRecords": len(review_queue),
        "originalItems": len(historical_items),
    }
    for key, expected in expected_counts.items():
        if counts.get(key) != expected:
            fail(f"Public reconciliation count {key} does not reproduce exactly.")

    item_summary = private_payloads.get("item_sensitivity_summary.json", {})
    original_summary = item_summary.get("original", {}) if isinstance(
        item_summary, Mapping
    ) else {}
    reconciled_summary = item_summary.get("reconciled", {}) if isinstance(
        item_summary, Mapping
    ) else {}
    for key, public_key in (
        ("items", "Items"),
        ("focalItems", "FocalItems"),
        ("contextualItems", "ContextualItems"),
    ):
        if counts.get(f"original{public_key}") != original_summary.get(key):
            fail(f"Original sensitivity count {key} does not match the public aggregate.")
        if counts.get(f"reconciledSensitivity{public_key}") != reconciled_summary.get(key):
            fail(f"Reconciled sensitivity count {key} does not match the public aggregate.")

    cluster_rows = private_payloads.get("cluster_sensitivity.json", [])
    if isinstance(cluster_rows, list):
        for row in cluster_rows:
            primary = int(row.get("reconciledPrimaryCount") or 0)
            secondary = int(row.get("reconciledSecondaryCount") or 0)
            if row.get("reconciledWeightedCount") != 2 * primary + secondary:
                fail(
                    f"Cluster {row.get('clusterId')} does not reproduce the governed 2:1 weight."
                )

    if len(historical_source_ids) == 269:
        governed = {
            "canonicalEpisodes": 242,
            "confirmedAliasGroups": 27,
            "originalItems": 14397,
            "reconciledSensitivityItems": 12978,
            "originalFocalItems": 10940,
            "reconciledSensitivityFocalItems": 9855,
            "originalContextualItems": 3457,
            "reconciledSensitivityContextualItems": 3123,
        }
        for key, expected in governed.items():
            if counts.get(key) != expected:
                fail(
                    f"Governed corpus reconciliation expectation failed for {key}: "
                    f"expected {expected}, got {counts.get(key)!r}."
                )

    return sorted(set(errors))


def tracked_xlsx_files(repo_root: Path) -> list[str]:
    """Return Git-tracked XLSX paths, or raise when Git cannot perform the check."""

    git = shutil.which("git")
    if git is None:
        windows_git = Path("C:/Program Files/Git/cmd/git.exe")
        git = str(windows_git) if windows_git.is_file() else None
    if git is None:
        raise OSError("Git executable was not found.")
    completed = subprocess.run(
        [git, "ls-files", "--", "*.xlsx"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return sorted(line.strip() for line in completed.stdout.splitlines() if line.strip())


def validate_source_protection(repo_root: Path, source_dir: Path) -> ValidationReport:
    """Check package presence and confirm raw XLSX files are not Git-tracked."""

    report = ValidationReport()
    present = {path.name for path in source_dir.glob("*.xlsx") if path.is_file()}
    missing = sorted(set(REQUIRED_WORKBOOKS) - present)
    extra = sorted(present - set(REQUIRED_WORKBOOKS))
    for filename in missing:
        report.add(
            "error", "required_workbook_missing",
            "Required source workbook is missing.", filename=filename,
        )
    for filename in extra:
        report.add(
            "warning", "unexpected_source_workbook",
            "Unexpected XLSX workbook is present in the governed source package.",
            filename=filename,
        )
    try:
        tracked = tracked_xlsx_files(repo_root)
    except (OSError, subprocess.CalledProcessError) as exc:
        report.add(
            "error", "git_tracking_check_failed",
            "Could not verify that raw XLSX files are untracked.", error=str(exc),
        )
        tracked = []
    for path in tracked:
        report.add(
            "error", "xlsx_tracked_by_git",
            "Raw XLSX file is tracked by Git.", path=path,
        )
    report.counts.update({
        "required_workbooks": len(REQUIRED_WORKBOOKS),
        "present_workbooks": len(present & set(REQUIRED_WORKBOOKS)),
        "tracked_xlsx_files": len(tracked),
    })
    return report


def validate_dataset(
    dataset: Mapping[str, Any],
    repo_root: Path | str | None = None,
) -> dict[str, Any]:
    """Orchestrator API: validate and return a machine-readable QA report.

    Count differences and the two known governance discrepancies remain visible
    warnings.  Structural integrity or source-protection failures raise
    ``ValidationError`` and retain the complete report on ``error.report``.
    """

    reports = [validate_normalized_dataset(dataset)]
    if repo_root is not None:
        root = Path(repo_root).resolve()
        reports.append(
            validate_source_protection(root, root / "source-data" / "ipa-podcast")
        )
    report = merge_reports(*reports)
    detailed = report.as_dict()

    def issue_text(issue: ValidationIssue) -> str:
        suffix = (
            f" ({json.dumps(dict(issue.context), sort_keys=True, default=str)})"
            if issue.context else ""
        )
        return f"{issue.code}: {issue.message}{suffix}"

    payload: dict[str, Any] = {
        "schemaVersion": "1.0",
        "passed": report.passed,
        "normalizedEntityCounts": dict(sorted(report.counts.items())),
        "expectedVsActual": dict(sorted(report.comparisons.items())),
        "missingReferences": detailed["missing_references"],
        "duplicateIds": detailed["duplicate_ids"],
        "unresolvedMappings": detailed["unresolved_mappings"],
        "publicExportChecks": {},
        "deterministicBuild": {"status": "pending"},
        "errors": [issue_text(issue) for issue in report.errors],
        "warnings": [issue_text(issue) for issue in report.warnings],
        "validationIssues": detailed["issues"],
    }
    payload["reviewCounts"] = {
        "assignmentRows": report.counts.get("review_required_assignments", 0),
        "reviewFlags": report.counts.get("review_flags", 0),
    }
    payload["ambiguityCounts"] = {
        "assignmentRows": report.counts.get("ambiguity_flagged_assignments", 0),
    }
    payload["narrativeCountMismatch"] = report.comparisons.get(
        "documented_meta_narratives"
    )
    if not report.passed:
        raise ValidationError(
            f"Cognitive Security validation failed with {len(report.errors)} error(s).",
            payload,
        )
    return payload


def validate_public_payloads(public_payloads: Mapping[str, Any]) -> list[str]:
    """Orchestrator API: return publication-boundary errors; empty means pass."""

    report = validate_public_outputs(public_payloads)
    return [
        f"{issue.code}: {issue.message}"
        + (f" ({json.dumps(dict(issue.context), sort_keys=True)})" if issue.context else "")
        for issue in report.errors
    ]
