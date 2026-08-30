"""Human-readable ingestion reporting for the Cognitive Security Map."""

from __future__ import annotations

from collections import Counter
from typing import Any, Mapping, Sequence


EXPECTED_COUNTS = {
    "extractedItems": 14397,
    "focalItems": 10940,
    "contextualItems": 3457,
    "episodes": 269,
    "clusters": 127,
    "primaryAssignments": 10940,
    "secondaryAssignments": 10524,
    "secondaryNone": 416,
    "assignmentReviewRequired": 514,
    "assignmentAmbiguity": 158,
    "metaClusters": 36,
    "clusterMetaMappings": 124,
    "themes": 11,
    "themeMetaMappings": 89,
    "themeClusterEvidence": 302,
    "tensions": 30,
    "metaNarratives": 7,
    "scenarios": 6,
}

KNOWN_UNMAPPED_CLUSTERS = {
    "CRB-10": "Forecasting, Complexity & Uncertainty",
    "FTP-13": "Societal Transformation, Identity, & Social Cohesion",
    "KCFT-20": "Strategic Culture & Ideological Competition",
}


def _value(row: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in row:
            return row[key]
    return default


def actual_counts(
    dataset: Mapping[str, Sequence[Mapping[str, Any]]]
) -> dict[str, int]:
    items = dataset.get("items", ())
    assignments = dataset.get("item_cluster_assignments", ())
    focal_items = [row for row in items if _value(row, "scope", "itemScope") == "focal"]
    contextual_items = [
        row for row in items if _value(row, "scope", "itemScope") == "contextual"
    ]
    return {
        "extractedItems": len(items),
        "focalItems": len(focal_items),
        "contextualItems": len(contextual_items),
        "episodes": len(dataset.get("episodes", ())),
        "clusters": len(dataset.get("clusters", ())),
        "primaryAssignments": sum(
            bool(_value(row, "primaryClusterId")) for row in assignments
        ),
        "secondaryAssignments": sum(
            bool(_value(row, "secondaryClusterId")) for row in assignments
        ),
        "secondaryNone": sum(
            not bool(_value(row, "secondaryClusterId")) for row in assignments
        ),
        "assignmentReviewRequired": sum(
            bool(_value(row, "reviewRequired")) for row in assignments
        ),
        "assignmentAmbiguity": sum(
            bool(_value(row, "ambiguityFlag")) for row in assignments
        ),
        "metaClusters": len(dataset.get("meta_clusters", ())),
        "clusterMetaMappings": len(dataset.get("cluster_meta_mappings", ())),
        "themes": len(dataset.get("themes", ())),
        "themeMetaMappings": len(dataset.get("theme_meta_mappings", ())),
        "themeClusterEvidence": len(dataset.get("theme_cluster_evidence", ())),
        "tensions": len(dataset.get("tensions", ())),
        "metaNarratives": len(dataset.get("meta_narratives", ())),
        "scenarios": len(dataset.get("scenarios", ())),
    }


def _display_metric(metric: str) -> str:
    names = {
        "extractedItems": "Extracted items",
        "focalItems": "Focal items",
        "contextualItems": "Contextual items",
        "episodes": "Distinct episodes/source files",
        "clusters": "Intermediate clusters",
        "primaryAssignments": "Primary focal-item assignments",
        "secondaryAssignments": "Substantive secondary assignments",
        "secondaryNone": "Secondary NONE rows",
        "assignmentReviewRequired": "Review-required assignments",
        "assignmentAmbiguity": "Ambiguity-flagged assignments",
        "metaClusters": "Meta-clusters",
        "clusterMetaMappings": "Cluster-to-meta mappings",
        "themes": "Cross-cutting themes",
        "themeMetaMappings": "Theme-to-meta mappings",
        "themeClusterEvidence": "Theme-to-cluster evidence rows",
        "tensions": "Tensions/debates",
        "metaNarratives": "Meta-narratives in current source",
        "scenarios": "Future scenarios",
    }
    return names.get(metric, metric)


def _status(expected: int, actual: int) -> str:
    return "PASS" if expected == actual else "REVIEW"


def _escape(value: Any) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace(
        "\n", " "
    )


def render_ingestion_report(
    dataset: Mapping[str, Sequence[Mapping[str, Any]]],
    extracted: Mapping[str, Any],
    qa_report: Mapping[str, Any],
    public_hashes: Mapping[str, str],
    deterministic: bool,
) -> str:
    counts = actual_counts(dataset)
    artifacts = dataset.get("artifacts", ())
    inventory = extracted.get("sheetInventory", ())
    entity_counts = {
        key: len(value)
        for key, value in dataset.items()
        if isinstance(value, (list, tuple))
    }

    lines = [
        "# Cognitive Security Map Phase 1 Ingestion Report",
        "",
        "## Release conclusion",
        "",
        (
            "Phase 1 passed its governed ingestion and publication-boundary gate."
            if not qa_report.get("errors") and deterministic
            else "Phase 1 did not pass all governed release checks."
        ),
        "",
        "This release builds the data foundation only. It does not add a public user interface.",
        "",
        "## Source package manifest",
        "",
        "| Artifact | Canonical role | SHA-256 |",
        "|---|---|---|",
    ]
    for artifact in sorted(artifacts, key=lambda row: str(row.get("fileName", ""))):
        lines.append(
            "| {file} | {role} | `{sha}` |".format(
                file=_escape(artifact.get("fileName")),
                role=_escape(artifact.get("canonicalRole")),
                sha=_escape(artifact.get("sha256")),
            )
        )

    lines += [
        "",
        "All source files are local, ignored XLSX artifacts. Public JSON contains filenames and integrity hashes, never local paths or workbook binaries.",
        "",
        "## Workbook and worksheet inventory",
        "",
        "| Workbook | Worksheet | Rows | Columns |",
        "|---|---|---:|---:|",
    ]
    for sheet in sorted(
        inventory,
        key=lambda row: (
            str(_value(row, "fileName", "workbook", default="")),
            str(_value(row, "sheetName", "sheet", default="")),
        ),
    ):
        lines.append(
            "| {file} | {sheet} | {rows} | {columns} |".format(
                file=_escape(_value(sheet, "fileName", "workbook")),
                sheet=_escape(_value(sheet, "sheetName", "sheet")),
                rows=_escape(_value(sheet, "rowCount", "rows")),
                columns=_escape(_value(sheet, "columnCount", "columns")),
            )
        )

    lines += [
        "",
        "## Expected versus actual baseline",
        "",
        "Expected values are validation baselines, not targets that the importer forces the source to match.",
        "",
        "| Metric | Expected | Actual | Result |",
        "|---|---:|---:|---|",
    ]
    for metric, expected in EXPECTED_COUNTS.items():
        actual = counts.get(metric, 0)
        lines.append(
            f"| {_display_metric(metric)} | {expected:,} | {actual:,} | {_status(expected, actual)} |"
        )

    lines += [
        "",
        "## Normalized entity counts",
        "",
        "| Collection | Records |",
        "|---|---:|",
    ]
    for collection, count in sorted(entity_counts.items()):
        lines.append(f"| `{collection}` | {count:,} |")

    lines += [
        "",
        "## Governance discrepancies retained",
        "",
        "### Unmapped intermediate clusters",
        "",
        "The following clusters are preserved without invented meta-cluster assignments:",
        "",
    ]
    unresolved = qa_report.get("unresolvedMappings") or [
        {"clusterId": key, "clusterName": value}
        for key, value in KNOWN_UNMAPPED_CLUSTERS.items()
    ]
    for row in unresolved:
        if isinstance(row, str):
            lines.append(f"- `{_escape(row)}`")
        else:
            lines.append(
                f"- `{_escape(_value(row, 'clusterId', 'cluster_id'))}` — "
                f"{_escape(_value(row, 'clusterName', 'cluster_name'))}"
            )

    lines += [
        "",
        "### Meta-narrative count",
        "",
        "The canonical worksheet contains seven records (`N01`–`N07`). Earlier project documentation described eight. The build preserves seven, creates no replacement record, and reports the discrepancy for human adjudication.",
        "",
        "### Canonical tension source",
        "",
        "`final_synthesis.xlsx` contains a blank copied `Source Tensions` worksheet. The 30 governed tension records come from `tensions_debates_rebuilt.xlsx`.",
        "",
        "### Unresolved theme-to-cluster evidence",
        "",
        "Three source-authored placeholder rows for `XTHEME-007`, `XTHEME-008`, and `XTHEME-010` contain no category or cluster ID. They remain in the 302-record evidence collection with null references, portable provenance, explicit unresolved markers, and private review flags. No cluster was invented.",
        "",
        "### Additional source observations",
        "",
        "- Meta-cluster `CRB-M05` exists but has no rows in the cluster-to-meta mapping table.",
        "- Category-specific worksheets omit canonical MASTER item IDs `14368`–`14373`; the build uses `MASTER` and retains all six.",
        "- Drill-down and current MASTER confidence values differ for 4,229 focal items. Item confidence remains canonical from MASTER, while coding confidence is preserved separately on assignments.",
        "- All 865 Batch Candidate rows have blank `batch_id` but populated `source_batch_id`; explicit candidate/source identifiers are retained through tension lineage where referenced.",
        "",
        "## Validation",
        "",
        f"- Structural errors: {len(qa_report.get('errors', ()))}",
        f"- Warnings/review findings: {len(qa_report.get('warnings', ()))}",
        f"- Deterministic in-memory serialization: {'PASS' if deterministic else 'FAIL'}",
        f"- Public files generated: {len(public_hashes)}",
        "",
    ]
    if qa_report.get("errors"):
        lines.append("Errors:")
        lines.append("")
        lines.extend(f"- {_escape(error)}" for error in qa_report["errors"])
        lines.append("")
    if qa_report.get("warnings"):
        lines.append("Warnings and review findings:")
        lines.append("")
        lines.extend(f"- {_escape(warning)}" for warning in qa_report["warnings"])
        lines.append("")

    lines += [
        "## Generated public-file hashes",
        "",
        "| File | SHA-256 |",
        "|---|---|",
    ]
    for name, sha256 in sorted(public_hashes.items()):
        lines.append(f"| `{_escape(name)}` | `{_escape(sha256)}` |")
    lines.append("")

    lines += [
        "## Public/private boundary",
        "",
        "Public export uses positive field allowlists. It includes governed high-level entities, semantic mappings, aggregate coverage, source integrity hashes, and aggregate QA. It excludes item text, evidence quotations, detailed rationales, internal notes, detailed review queues, hidden source metadata, and all workbook content blobs.",
        "",
        "The complete normalized QA layer—including item records, evidence excerpts, rationales, ambiguity details, and review flags—is written only to ignored `analysis/cognitive-security/normalized/`.",
        "",
        "## Methodology cautions",
        "",
        "- This is a practitioner-discourse map, not a definitive taxonomy.",
        "- Counts indicate corpus discourse salience, not objective importance, prevalence, scientific support, or consensus.",
        "- Extracted items are interpretive units, not independent statistical observations.",
        "- Primary assignment represents dominant analytic meaning.",
        "- Secondary assignment represents substantive conceptual adjacency.",
        "- Primary-secondary co-occurrence is semantic, not causal.",
        "- Discourse clusters are not automatically PSYWERX behavioral Drivers.",
        "- A meta-cluster is a within-category family.",
        "- A cross-cutting theme connects patterns across categories.",
        "- A tension is an unresolved tradeoff, disagreement, or competing assumption.",
        "- A meta-narrative is a high-level interpretive storyline.",
        "- Scenarios are plausibility exercises, not forecasts.",
        "- Model coding confidence is not scientific evidence strength.",
        "- Frequency is not consensus.",
        "- Higher-order synthesis remains traceable to lower-level source IDs where the source supports the relationship.",
        "",
        "## Recommended human adjudications",
        "",
        "1. Decide whether and where to map `CRB-10`, `FTP-13`, and `KCFT-20` within the meta-cluster layer.",
        "2. Reconcile the prior eight-narrative expectation with the seven canonical source records.",
        "3. Establish an explicit evidence and quotation publication allowlist before any evidence-browser release.",
        "4. Review speaker attribution and episode-link publication rules before Phase 3 evidence browsing.",
        "",
        "## Known limitations",
        "",
        "Phase 1 does not adjudicate source review queues, infer causal relationships, publish evidence excerpts, or implement the explorer interface. Those are intentionally deferred to governed follow-on phases.",
        "",
    ]
    return "\n".join(lines)
