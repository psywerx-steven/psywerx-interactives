"""Build the governed Cognitive Security Practitioner Discourse Map data."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

from cognitive_security import SourceValidationError, extract_sources, normalize_sources
from cognitive_security.export import (
    build_internal_payloads,
    build_public_payloads,
    generated_hashes,
    serialize_payloads,
    write_serialized_files,
)
from cognitive_security.report import EXPECTED_COUNTS, actual_counts, render_ingestion_report
from cognitive_security.sensitivity import build_reconciliation_products
from cognitive_security.validate import (
    ValidationError,
    validate_dataset,
    validate_public_payloads,
    validate_reconciliation_dataset,
)


SOURCE_DIR = Path("source-data") / "ipa-podcast"
PUBLIC_DIR = Path("data") / "cognitive-security"
PRIVATE_DIR = Path("analysis") / "cognitive-security" / "normalized"
RECONCILIATION_DIR = (
    Path("analysis") / "cognitive-security" / "corpus-reconciliation"
)
REPORT_PATH = Path("docs") / "cognitive-security" / "INGESTION_REPORT.md"
FROZEN_EPISODE_SUMMARIES_PATH = (
    Path("data") / "cognitive-security" / "episode_summaries.json"
)
CANONICAL_PUBLIC_CONTENT_VERSION = "canonical-resynthesis"
RETIRED_CANONICAL_PUBLIC_CONTENT_VERSIONS = {"canonical-resynthesis-v1"}


def _guard_against_canonical_public_overwrite(repo_root: Path) -> None:
    """Refuse to let the legacy builder replace the canonical public package."""

    manifest_path = repo_root / PUBLIC_DIR / "manifest.json"
    if not manifest_path.exists():
        return
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(
            "Cannot safely identify the existing public Cognitive Security package.",
            {
                "errors": [
                    f"Refusing legacy overwrite because {manifest_path} could not "
                    f"be read as JSON: {exc}"
                ]
            },
        ) from exc
    if not isinstance(manifest, Mapping):
        raise ValidationError(
            "Cannot safely identify the existing public Cognitive Security package.",
            {
                "errors": [
                    f"Refusing legacy overwrite because {manifest_path} is not a "
                    "JSON object."
                ]
            },
        )
    if manifest.get("contentVersion") in {
        CANONICAL_PUBLIC_CONTENT_VERSION,
        *RETIRED_CANONICAL_PUBLIC_CONTENT_VERSIONS,
    }:
        raise ValidationError(
            "The legacy Cognitive Security builder cannot overwrite the canonical "
            "public package.",
            {
                "errors": [
                    "Use scripts/build_canonical_public.py to rebuild "
                    f"{CANONICAL_PUBLIC_CONTENT_VERSION}."
                ]
            },
        )


def _normalized_counts(
    dataset: Mapping[str, Sequence[Mapping[str, Any]]]
) -> dict[str, int]:
    return {
        key: len(value)
        for key, value in sorted(dataset.items())
        if isinstance(value, (list, tuple))
    }


def _private_source_hashes(
    dataset: Mapping[str, Sequence[Mapping[str, Any]]]
) -> dict[str, str]:
    return {
        str(row.get("fileName")): str(row.get("sha256"))
        for row in sorted(
            dataset.get("artifacts", ()), key=lambda value: str(value.get("fileName", ""))
        )
    }


def _private_source_row_counts(
    extracted: Mapping[str, Any]
) -> dict[str, dict[str, int]]:
    output: dict[str, dict[str, int]] = {}
    for row in extracted.get("sheetInventory", ()):
        file_name = str(row.get("fileName") or row.get("workbook") or "")
        sheet_name = str(row.get("sheetName") or row.get("sheet") or "")
        row_count = row.get("rowCount", row.get("rows", 0))
        if file_name and sheet_name:
            output.setdefault(file_name, {})[sheet_name] = int(row_count or 0)
    return {
        file_name: dict(sorted(sheets.items()))
        for file_name, sheets in sorted(output.items())
    }


def _unresolved_mappings(
    dataset: Mapping[str, Sequence[Mapping[str, Any]]]
) -> list[dict[str, str]]:
    mapped = {
        str(row.get("clusterId"))
        for row in dataset.get("cluster_meta_mappings", ())
        if row.get("clusterId")
    }
    unresolved = [
        {
            "clusterId": str(row.get("clusterId")),
            "clusterName": str(row.get("name") or row.get("clusterName") or ""),
            "categoryId": str(row.get("categoryId") or ""),
        }
        for row in dataset.get("clusters", ())
        if row.get("clusterId") and str(row.get("clusterId")) not in mapped
    ]
    mapped_meta_clusters = {
        str(row.get("metaClusterId"))
        for row in dataset.get("cluster_meta_mappings", ())
        if row.get("metaClusterId")
    }
    for meta_cluster in dataset.get("meta_clusters", ()):
        meta_cluster_id = str(meta_cluster.get("metaClusterId") or "")
        if meta_cluster_id == "CRB-M05" and meta_cluster_id not in mapped_meta_clusters:
            unresolved.append(
                {
                    "metaClusterId": meta_cluster_id,
                    "metaClusterName": str(meta_cluster.get("name") or ""),
                    "governanceStatus": "known-empty-source-membership",
                }
            )
    return sorted(
        unresolved,
        key=lambda row: row.get("clusterId") or row.get("metaClusterId") or "",
    )


def _expected_actual(dataset: Mapping[str, Sequence[Mapping[str, Any]]]) -> dict[str, Any]:
    actual = actual_counts(dataset)
    return {
        metric: {
            "expected": expected,
            "actual": actual.get(metric, 0),
            "status": "pass" if expected == actual.get(metric, 0) else "review",
        }
        for metric, expected in EXPECTED_COUNTS.items()
    }


def _enrich_qa_report(
    base: Mapping[str, Any],
    dataset: Mapping[str, Sequence[Mapping[str, Any]]],
    extracted: Mapping[str, Any],
    corpus_reconciliation: Mapping[str, Any],
) -> dict[str, Any]:
    # This is the complete maintainer QA record. The public exporter projects
    # it to opaque artifact IDs and aggregate counts before browser publication.
    assignments = dataset.get("item_cluster_assignments", ())
    meta_narratives = dataset.get("meta_narratives", ())
    issues = list(base.get("validationIssues", base.get("issues", ())))
    base_errors = base.get("errors", ())
    base_warnings = base.get("warnings", ())
    report: dict[str, Any] = {
        "schemaVersion": "1.1",
        "passed": bool(base.get("passed", False)),
        "errors": list(base_errors) if isinstance(base_errors, (list, tuple)) else [],
        "warnings": (
            list(base_warnings) if isinstance(base_warnings, (list, tuple)) else []
        ),
        "counts": dict(
            base.get("normalizedEntityCounts", base.get("counts", {}))
        ),
        "validationIssues": issues,
    }
    report["sourceHashes"] = _private_source_hashes(dataset)
    report["sourceRowCounts"] = _private_source_row_counts(extracted)
    report["normalizedEntityCounts"] = _normalized_counts(dataset)
    governed_counts = dict(
        base.get("normalizedEntityCounts", base.get("counts", {}))
    )
    governed_counts.update(report["normalizedEntityCounts"])
    report["counts"] = governed_counts
    # Schema v1.1 expectations include canonical releases, source identities,
    # and sensitivity counts that exist only after reconciliation. Compare the
    # governed reconciled dataset, never the historical v1.0 normalization.
    report["expectedVsActual"] = _expected_actual(dataset)
    report["missingReferences"] = list(
        base.get("missingReferences", base.get("missing_references", ()))
    )
    report["duplicateIds"] = list(
        base.get("duplicateIds", base.get("duplicate_ids", ()))
    )
    report["unresolvedMappings"] = _unresolved_mappings(dataset)
    report["unresolvedThemeClusterEvidence"] = [
        {
            "themeClusterEvidenceId": row.get("themeClusterEvidenceId"),
            "themeId": row.get("themeId"),
            "clusterId": None,
            "status": "source-placeholder-retained",
        }
        for row in dataset.get("theme_cluster_evidence", ())
        if row.get("unresolvedReference")
    ]
    mapped_meta_ids = {
        row.get("metaClusterId")
        for row in dataset.get("cluster_meta_mappings", ())
        if row.get("metaClusterId")
    }
    report["metaClustersWithoutMappingRows"] = [
        {
            "metaClusterId": row.get("metaClusterId"),
            "name": row.get("name"),
        }
        for row in dataset.get("meta_clusters", ())
        if row.get("metaClusterId") not in mapped_meta_ids
    ]
    report["reviewCounts"] = {
        "assignmentRows": sum(bool(row.get("reviewRequired")) for row in assignments),
        "normalizedReviewFlags": len(dataset.get("review_flags", ())),
    }
    report["ambiguityCounts"] = {
        "assignmentRows": sum(bool(row.get("ambiguityFlag")) for row in assignments)
    }
    report["narrativeCountMismatch"] = {
        "priorDocumentedExpected": 8,
        "currentSourceActual": len(meta_narratives),
        "sourceRecordIds": [
            row.get("narrativeId") for row in meta_narratives if row.get("narrativeId")
        ],
        "status": "human-adjudication-required",
        "action": "preserved-source-records-without-invention",
    }
    report["canonicalSourceDecisions"] = {
        "tensions": "tensions_debates_rebuilt.xlsx",
        "blankCopiedSourceTensions": "intentionally-not-used",
    }
    report["corpusReconciliation"] = {
        "status": corpus_reconciliation.get("status"),
        "methodVersion": corpus_reconciliation.get("methodVersion"),
        "counts": dict(corpus_reconciliation.get("counts", {})),
    }
    report["additionalSourceAnomalies"] = [
        {
            "code": "category-sheet-id-omission",
            "description": (
                "Category-specific source sheets omit MASTER item IDs "
                "14368-14373; canonical MASTER retains all six records."
            ),
        },
        {
            "code": "confidence-snapshot-difference",
            "description": (
                "MASTER item confidence is preserved separately from drill-down "
                "coding confidence; 4,229 focal records differ."
            ),
        },
    ]
    return report


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            delete=False,
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
        ) as handle:
            handle.write(content)
            temporary = Path(handle.name)
        temporary.replace(path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def _current_source_hashes(source_dir: Path) -> dict[str, str]:
    return {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(source_dir.glob("*.xlsx"), key=lambda value: value.name)
        if path.is_file()
    }


def build(repo_root: Path) -> dict[str, Any]:
    _guard_against_canonical_public_overwrite(repo_root)
    source_dir = repo_root / SOURCE_DIR
    source_hashes_before = _current_source_hashes(source_dir)
    extracted = extract_sources(source_dir)
    historical_dataset = normalize_sources(extracted)

    # The historical v1.0 normalized release is validated before any episode
    # semantics are changed. Reconciliation then operates on a deep copy.
    base_qa = validate_dataset(historical_dataset, repo_root=repo_root)
    reconciliation_products = build_reconciliation_products(historical_dataset)
    dataset = reconciliation_products["reconciledDataset"]
    reconciliation_errors = validate_reconciliation_dataset(
        historical_dataset,
        dataset,
        reconciliation_products["privatePayloads"],
        reconciliation_products["publicAggregate"],
    )
    if reconciliation_errors:
        raise ValidationError(
            "Corpus reconciliation validation failed.",
            {"errors": reconciliation_errors},
        )
    qa_report = _enrich_qa_report(
        base_qa,
        dataset,
        extracted,
        reconciliation_products["publicAggregate"],
    )
    qa_report["publicExportChecks"] = {
        "status": "pending",
        "errors": [],
        "positiveAllowlist": True,
    }
    qa_report["deterministicBuild"] = {
        "status": "pending",
        "method": "repeat in-memory serialization plus release-gate rebuild",
    }

    frozen_summary_path = repo_root / FROZEN_EPISODE_SUMMARIES_PATH
    if not frozen_summary_path.is_file():
        raise ValidationError(
            "Frozen episode summary product is missing.",
            {
                "errors": [
                    "Build and review the governed transcript manifest with "
                    "scripts/build_transcript_summaries.py, then use its QA-gated "
                    "publish workflow to freeze episode_summaries.json first."
                ]
            },
        )
    frozen_episode_summaries = json.loads(
        frozen_summary_path.read_text(encoding="utf-8")
    )

    preliminary_public = build_public_payloads(
        dataset,
        qa_report,
        reconciliation_products["publicAggregate"],
        frozen_episode_summaries,
    )
    public_errors = validate_public_payloads(preliminary_public)
    qa_report["publicExportChecks"] = {
        "status": "pass" if not public_errors else "fail",
        "errors": list(public_errors),
        "positiveAllowlist": True,
    }
    if public_errors:
        qa_report["errors"] = list(qa_report.get("errors", ())) + list(public_errors)
        raise ValidationError(
            "Public publication-boundary validation failed.", report=qa_report
        )

    qa_report["deterministicBuild"] = {
        "status": "pass",
        "method": "repeat in-memory serialization plus release-gate rebuild",
    }
    public_payloads = build_public_payloads(
        dataset,
        qa_report,
        reconciliation_products["publicAggregate"],
        frozen_episode_summaries,
    )
    internal_payloads = build_internal_payloads(dataset, qa_report)
    reconciliation_payloads = reconciliation_products["privatePayloads"]
    public_files = serialize_payloads(public_payloads)
    internal_files = serialize_payloads(internal_payloads)
    reconciliation_files = serialize_payloads(reconciliation_payloads)

    repeated_products = build_reconciliation_products(historical_dataset)
    repeated_public = serialize_payloads(
        build_public_payloads(
            repeated_products["reconciledDataset"],
            qa_report,
            repeated_products["publicAggregate"],
            frozen_episode_summaries,
        )
    )
    repeated_internal = serialize_payloads(
        build_internal_payloads(repeated_products["reconciledDataset"], qa_report)
    )
    repeated_reconciliation = serialize_payloads(
        repeated_products["privatePayloads"]
    )
    deterministic = (
        public_files == repeated_public
        and internal_files == repeated_internal
        and reconciliation_files == repeated_reconciliation
    )
    if not deterministic:
        raise ValidationError(
            "Repeated in-memory serialization was not deterministic.", report=qa_report
        )

    public_hashes = generated_hashes(public_files)
    report = render_ingestion_report(
        dataset,
        extracted,
        qa_report,
        public_hashes,
        deterministic,
    )

    source_hashes_after = _current_source_hashes(source_dir)
    if source_hashes_before != source_hashes_after:
        raise ValidationError(
            "A governed source workbook changed during the build.",
            {"errors": ["Source workbook hashes changed during reconciliation."]},
        )

    public_dir = repo_root / PUBLIC_DIR
    unexpected_public_files = sorted(
        path.name
        for path in public_dir.glob("*.json")
        if path.name not in public_files
    )
    if unexpected_public_files:
        raise ValidationError(
            "Unexpected stale public JSON files would survive this build.",
            {
                "errors": [
                    "Remove or govern these files before publication: "
                    + ", ".join(unexpected_public_files)
                ]
            },
        )

    # No generated output is touched until extraction, normalization, structural
    # validation, publication validation, and deterministic serialization pass.
    write_serialized_files(public_dir, public_files)
    write_serialized_files(repo_root / PRIVATE_DIR, internal_files)
    write_serialized_files(
        repo_root / RECONCILIATION_DIR, reconciliation_files
    )
    _atomic_write_text(repo_root / REPORT_PATH, report)

    return {
        "dataset": dataset,
        "qaReport": qa_report,
        "publicHashes": public_hashes,
        "internalHashes": generated_hashes(internal_files),
        "reconciliationHashes": generated_hashes(reconciliation_files),
        "corpusReconciliation": reconciliation_products["publicAggregate"],
    }


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    try:
        result = build(repo_root)
    except (SourceValidationError, ValidationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        report = getattr(exc, "report", None)
        if report:
            errors = list(report.get("errors", ()))
            for error in errors[:25]:
                print(f"  - {error}", file=sys.stderr)
            if len(errors) > 25:
                print(
                    f"  ... {len(errors) - 25} additional errors omitted from console output.",
                    file=sys.stderr,
                )
        return 1
    except (OSError, ValueError) as exc:
        print(f"ERROR: Cognitive Security build failed: {exc}", file=sys.stderr)
        return 1

    counts = result["qaReport"]["normalizedEntityCounts"]
    print("Cognitive Security Map Schema v1.1 build succeeded.")
    print(f"  Source workbooks: {counts.get('artifacts', 0)}")
    print(f"  Extracted items: {counts.get('items', 0)}")
    print(f"  Canonical public feed episodes: {counts.get('episodes', 0)}")
    print(
        "  Historical source identities: "
        f"{counts.get('episode_source_identities', 0)}"
    )
    reconciliation_counts = result["corpusReconciliation"]["counts"]
    print(
        "  Reconciled sensitivity items: "
        f"{reconciliation_counts.get('reconciledSensitivityItems', 0)}"
    )
    print(f"  Clusters: {counts.get('clusters', 0)}")
    print(f"  Meta-clusters: {counts.get('meta_clusters', 0)}")
    print(f"  Themes: {counts.get('themes', 0)}")
    print(f"  Tensions: {counts.get('tensions', 0)}")
    print(f"  Meta-narratives: {counts.get('meta_narratives', 0)}")
    print(f"  Scenarios: {counts.get('scenarios', 0)}")
    print(f"  Public files: {len(result['publicHashes'])}")
    print("  Deterministic serialization: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
