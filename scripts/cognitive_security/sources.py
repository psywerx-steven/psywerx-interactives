"""Governed source-package contract for the Cognitive Security Map."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .utils import file_sha256, normalize_text


class SourceValidationError(RuntimeError):
    """Raised when the eight-workbook source contract is not satisfied."""

    def __init__(self, messages: str | Iterable[str]):
        if isinstance(messages, str):
            self.messages = (messages,)
        else:
            self.messages = tuple(messages)
        super().__init__("\n".join(self.messages))


@dataclass(frozen=True)
class ArtifactSpec:
    artifact_id: str
    file_name: str


@dataclass(frozen=True)
class SheetSpec:
    table_key: str
    artifact_id: str
    sheet_name: str
    required_headers: tuple[str, ...]
    allow_empty: bool = False


ITEM_HEADERS = (
    "ID", "podcast", "episode_title", "source_file", "category", "item",
    "summary", "strategic_significance", "operational_implications",
    "evidence_quote", "speaker", "confidence", "episode_relevance_score",
    "novelty_score", "actionability_score", "time_horizon", "relevance_tags",
)
ASSIGNMENT_HEADERS = ITEM_HEADERS + (
    "primary_cluster_id", "primary_cluster_name", "primary_rationale",
    "secondary_cluster_id", "secondary_cluster_name", "secondary_rationale",
    "ambiguity_flag", "ambiguity_type", "alternative_cluster_ids",
    "alternative_cluster_names", "review_required", "review_reason", "coder",
    "model", "prompt_version", "codebook_version", "coded_timestamp",
)

ARTIFACT_SPECS = (
    ArtifactSpec("ART-codebook", "codebook.xlsx"),
    ArtifactSpec("ART-master-extractions", "master_extractions.xlsx"),
    ArtifactSpec("ART-drill-down", "drill_down.xlsx"),
    ArtifactSpec("ART-cluster-summaries", "drill_up_cluster_summaries.xlsx"),
    ArtifactSpec("ART-meta-clusters", "drill_up_meta_clusters.xlsx"),
    ArtifactSpec("ART-cross-cutting-themes", "cross_cutting_themes.xlsx"),
    ArtifactSpec("ART-tensions", "tensions_debates_rebuilt.xlsx"),
    ArtifactSpec("ART-final-synthesis", "final_synthesis.xlsx"),
)

SHEET_SPECS = (
    SheetSpec(
        "codebook_clusters", "ART-codebook", "Sheet1",
        ("ID", "Category", "Intermediate Cluster", "Definition",
         "Inclusion Criteria", "Exclusion Criteria", "Near-Neighbor Distinctions",
         "Anchor Examples"),
    ),
    SheetSpec("master_items", "ART-master-extractions", "MASTER", ITEM_HEADERS),
    SheetSpec(
        "master_focal_items", "ART-master-extractions",
        "MASTER (only coded cats)", ITEM_HEADERS,
    ),
    SheetSpec("drill_down_assignments", "ART-drill-down", "Drill Down", ASSIGNMENT_HEADERS),
    SheetSpec(
        "cluster_summaries", "ART-cluster-summaries", "Cluster Summaries",
        ("category", "cluster_id", "cluster_name", "primary_count",
         "secondary_count", "weighted_count", "cluster_summary",
         "strategic_significance_synthesis", "operational_implications_synthesis",
         "primary_vs_secondary_distinction", "representative_item_ids",
         "edge_cases_or_ambiguities", "candidate_meta_cluster_affinities",
         "review_questions", "summary_confidence"),
    ),
    SheetSpec(
        "cluster_theme_details", "ART-cluster-summaries", "Theme Details",
        ("category", "cluster_id", "cluster_name", "theme_number", "theme_name",
         "theme_description", "evidence_item_ids", "primary_support_count_estimate",
         "secondary_support_count_estimate", "importance"),
    ),
    SheetSpec(
        "cluster_representative_items", "ART-cluster-summaries", "Representative Items",
        ("category", "cluster_id", "cluster_name", "item_id", "assignment_role",
         "assignment_weight", "episode_title", "item", "summary",
         "strategic_significance", "operational_implications", "evidence_quote"),
    ),
    SheetSpec(
        "meta_clusters", "ART-meta-clusters", "Candidate Meta-Clusters",
        ("meta_cluster_id", "category", "meta_cluster_name", "definition",
         "included_cluster_ids", "included_cluster_names", "rationale",
         "near_neighbor_distinctions", "representative_item_ids", "salience",
         "review_priority", "category_synthesis", "review_status", "human_notes",
         "run_id", "prompt_version"),
    ),
    SheetSpec(
        "cluster_meta_mappings", "ART-meta-clusters", "Cluster-to-Meta Mapping",
        ("category", "meta_cluster_id", "meta_cluster_name", "cluster_id",
         "cluster_name", "mapping_type", "mapping_rationale", "review_status",
         "human_notes", "run_id"),
    ),
    SheetSpec(
        "meta_cluster_evidence", "ART-meta-clusters", "Meta-Cluster Evidence",
        ("category", "meta_cluster_id", "meta_cluster_name",
         "representative_item_id", "evidence_role", "run_id"),
    ),
    SheetSpec(
        "meta_review_queue", "ART-meta-clusters", "Review Queue",
        ("category", "object_type", "object_id", "object_name", "reason",
         "review_status", "human_notes", "run_id"),
    ),
    SheetSpec(
        "themes", "ART-cross-cutting-themes", "Cross-Cutting Themes",
        ("theme_id", "theme_name", "definition", "categories_present",
         "category_count", "linked_meta_cluster_ids", "linked_meta_cluster_names",
         "linked_intermediate_clusters", "cross_category_logic",
         "cooccurrence_evidence", "strategic_significance",
         "operational_implications", "boundary_conditions",
         "related_tensions_or_debates", "representative_item_ids",
         "evidence_strength", "review_priority", "review_required", "review_notes",
         "human_review_status", "human_theme_name", "human_notes"),
    ),
    SheetSpec(
        "theme_meta_mappings", "ART-cross-cutting-themes", "Theme-to-Meta Mapping",
        ("theme_id", "theme_name", "category", "meta_cluster_id",
         "meta_cluster_name", "meta_cluster_definition",
         "included_intermediate_clusters", "mapping_basis",
         "human_review_status", "human_notes"),
    ),
    SheetSpec(
        "theme_cluster_evidence", "ART-cross-cutting-themes",
        "Theme-to-Cluster Evidence",
        ("theme_id", "theme_name", "category", "cluster_id", "cluster_name",
         "cluster_summary", "strategic_significance", "operational_implications",
         "evidence_note"),
    ),
    SheetSpec(
        "theme_cooccurrence", "ART-cross-cutting-themes", "Cooccurrence Evidence",
        ("category", "primary_cluster_name", "secondary_cluster_name",
         "cooccurrence_count", "example_item_ids", "theme_id", "theme_name"),
    ),
    SheetSpec(
        "theme_representative_items", "ART-cross-cutting-themes", "Representative Items",
        ("score", "item_id", "category", "item", "summary",
         "strategic_significance", "operational_implications", "evidence_quote",
         "episode_title", "primary_cluster_name", "secondary_cluster_name",
         "theme_id", "theme_name"),
    ),
    SheetSpec(
        "theme_review_queue", "ART-cross-cutting-themes", "Review Queue",
        ("theme_id", "theme_name", "review_reason", "evidence_strength",
         "category_count", "review_notes", "suggested_action"),
    ),
    SheetSpec(
        "tensions", "ART-tensions", "Tensions Debates",
        ("tension_id", "tension_name", "description", "pole_a_label", "pole_b_label",
         "pole_a_assumption", "pole_b_assumption", "tension_level",
         "categories_involved", "category_count", "clusters_involved", "cluster_count",
         "supporting_item_ids_pole_a", "supporting_item_ids_pole_b",
         "source_candidate_ids", "candidate_count", "evidence_strength", "confidence",
         "review_priority", "key_terms", "evidence_rationale", "selection_method",
         "review_required", "human_review_status", "human_notes"),
    ),
    SheetSpec(
        "tension_evidence", "ART-tensions", "Tension Evidence",
        ("tension_id", "evidence_rank", "source_candidate_id", "source_batch_id",
         "candidate_tension_name", "candidate_description", "pole_a_label",
         "pole_b_label", "supporting_item_ids_pole_a",
         "supporting_item_ids_pole_b", "categories_involved", "clusters_involved",
         "evidence_rationale", "confidence", "review_priority", "candidate_score"),
    ),
    SheetSpec(
        "tension_mappings", "ART-tensions", "Tension Mapping",
        ("tension_id", "mapping_type", "mapped_id", "mapped_name",
         "mapping_strength", "mapping_basis", "review_status", "human_notes"),
    ),
    SheetSpec(
        "tension_review_queue", "ART-tensions", "Review Queue",
        ("tension_id", "tension_name", "review_priority", "review_reasons",
         "suggested_action", "candidate_count", "evidence_strength",
         "categories_involved", "clusters_involved", "human_review_status",
         "human_notes"),
    ),
    SheetSpec(
        "meta_narratives", "ART-final-synthesis", "Corpus Meta-Narratives",
        ("narrative_id", "narrative_name", "short_version", "core_claim",
         "supporting_cross_cutting_themes", "supporting_tensions",
         "supporting_meta_clusters", "categories_connected",
         "representative_evidence", "strategic_significance",
         "operational_implications", "caveats_or_boundary_conditions", "confidence",
         "review_required"),
    ),
    SheetSpec(
        "category_summaries", "ART-final-synthesis", "Category Summaries",
        ("category", "category_summary", "category_so_what"),
    ),
    SheetSpec(
        "category_findings", "ART-final-synthesis", "Category Findings",
        ("finding_id", "category", "finding_name", "core_finding",
         "supporting_meta_clusters", "supporting_intermediate_clusters",
         "strategic_significance", "operational_implications", "unresolved_questions",
         "caveats", "confidence", "review_required"),
    ),
    SheetSpec(
        "scenarios", "ART-final-synthesis", "Future Scenarios",
        ("scenario_id", "scenario_name", "timeframe", "scenario_type", "core_scenario",
         "driving_forces", "categories_meshed", "cross_cutting_themes_involved",
         "tensions_activated", "strategic_implications", "operational_implications",
         "research_questions", "uncertainty_level", "assumptions",
         "alternative_outcomes", "review_required"),
    ),
    SheetSpec(
        "scenario_pathways", "ART-final-synthesis", "Scenario Pathways",
        ("scenario_id", "step_number", "pathway_step"),
    ),
    SheetSpec(
        "scenario_indicators", "ART-final-synthesis", "Scenario Indicators",
        ("scenario_id", "indicator"),
    ),
    SheetSpec(
        "scenario_actions", "ART-final-synthesis", "Scenario Actions",
        ("scenario_id", "policy_or_practice_action"),
    ),
    SheetSpec(
        "synthesis_review_queue", "ART-final-synthesis", "Review Queue",
        ("source_sheet", "record_id", "issue", "status"),
    ),
)

ARTIFACT_BY_ID = {spec.artifact_id: spec for spec in ARTIFACT_SPECS}
SHEETS_BY_ARTIFACT = {
    artifact.artifact_id: tuple(
        spec for spec in SHEET_SPECS if spec.artifact_id == artifact.artifact_id
    )
    for artifact in ARTIFACT_SPECS
}


def resolve_source_paths(source_dir: Path | str) -> dict[str, Path]:
    root = Path(source_dir).expanduser().resolve()
    errors: list[str] = []
    if not root.is_dir():
        raise SourceValidationError(f"Source directory does not exist: {root}")
    paths: dict[str, Path] = {}
    for spec in ARTIFACT_SPECS:
        path = root / spec.file_name
        if not path.is_file():
            errors.append(f"Missing required workbook: {spec.file_name}")
        else:
            paths[spec.artifact_id] = path
    if errors:
        raise SourceValidationError(errors)
    return paths


def normalized_headers(values) -> tuple[str, ...]:
    return tuple(normalize_text(value) or "" for value in values)


def find_header_row(worksheet, spec: SheetSpec, scan_rows: int = 25):
    """Find the unique row containing all governed headers."""

    wanted = set(spec.required_headers)
    matches: list[tuple[int, tuple[str, ...]]] = []
    candidates: list[tuple[int, tuple[str, ...]]] = []
    for row_number, row in enumerate(
        worksheet.iter_rows(min_row=1, max_row=min(worksheet.max_row, scan_rows), values_only=True),
        1,
    ):
        headers = normalized_headers(row)
        while headers and not headers[-1]:
            headers = headers[:-1]
        candidates.append((row_number, headers))
        if wanted.issubset(set(headers)):
            matches.append((row_number, headers))
    if len(matches) != 1:
        discovered = max(candidates, key=lambda item: len([h for h in item[1] if h]), default=(0, ()))
        message = (
            f"{ARTIFACT_BY_ID[spec.artifact_id].file_name} / {spec.sheet_name}: "
            f"expected one header row containing {list(spec.required_headers)!r}; "
            f"best discovered row {discovered[0]} was {list(discovered[1])!r}."
        )
        raise SourceValidationError(message)
    row_number, headers = matches[0]
    nonempty = [header for header in headers if header]
    duplicates = sorted({header for header in nonempty if nonempty.count(header) > 1})
    if duplicates:
        raise SourceValidationError(
            f"{ARTIFACT_BY_ID[spec.artifact_id].file_name} / {spec.sheet_name}: "
            f"duplicate headers: {duplicates}."
        )
    return row_number, headers


def artifact_manifest(paths: dict[str, Path]) -> list[dict]:
    records = []
    for spec in ARTIFACT_SPECS:
        path = paths[spec.artifact_id]
        records.append(
            {
                "artifactId": spec.artifact_id,
                "fileName": spec.file_name,
                "sha256": file_sha256(path),
                "byteSize": path.stat().st_size,
            }
        )
    return records
