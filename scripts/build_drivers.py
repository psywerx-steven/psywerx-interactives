"""Build public Driver Explorer JSON from local PSYWERX XLSX workbooks.

Explicit Driver IDs are preserved after whitespace cleanup. When absent, the
stable fallback is a slug of canonical layer plus driver name; it never depends
on a workbook, sheet, or row position.
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


# Central mapping to extend as future layer workbook headers become known.
HEADER_ALIASES: dict[str, set[str]] = {
    "id": {"id", "driver id", "driver identifier", "unique id"},
    "name": {"name", "driver", "driver name", "driver title", "canonical driver"},
    "layer": {"layer", "driver layer", "taxonomy layer", "domain"},
    "familyCode": {"family code"},
    "category": {"category", "driver category", "family"},
    "subcategory": {"subcategory", "sub category", "driver subcategory"},
    "taxonomyStatus": {"taxonomy status"},
    "driverRole": {"driver role"},
    "typicalTimeScale": {"typical time scale", "time scale", "timescale"},
    "definition": {"definition", "driver definition", "description"},
    "mechanism": {"mechanism", "mechanisms", "causal mechanism", "mechanism pathway"},
    "behavioralConsequences": {"primary behavioral consequences", "behavioral consequences"},
    "behaviorChangeRelevance": {"behavior change relevance"},
    "contextsBoundaryConditions": {
        "typical contexts boundary conditions", "contexts boundary conditions", "boundary conditions"
    },
    "modifiability": {"modifiability"},
    "measurementIndicators": {"measurement indicators", "measurement", "indicators"},
    "evidenceGrade": {"evidence grade"},
    "evidenceIds": {"key evidence ids", "evidence ids", "evidence id"},
    "evidenceUrls": {"representative source urls", "source urls", "evidence urls"},
    "caveats": {"important caveats misuse risk", "caveats", "misuse risk"},
    "crossLayerInteractions": {"cross layer interactions"},
    "aliases": {
        "aliases", "alias", "alternate names", "alternative names", "related constructs aliases"
    },
    "relatedDrivers": {"related drivers", "related driver", "relateddrivers"},
    "examples": {"examples", "example"},
}

CANONICAL_LAYERS = (
    "Biological", "Psychological", "Social", "Cultural",
    "Physical / Environmental", "Institutional / Structural",
    "Informational", "Technological",
)
LAYER_ALIASES = {
    "biological": "Biological",
    "psychological": "Psychological",
    "social": "Social",
    "cultural": "Cultural",
    "physical": "Physical / Environmental",
    "environmental": "Physical / Environmental",
    "physical environmental": "Physical / Environmental",
    "institutional": "Institutional / Structural",
    "structural": "Institutional / Structural",
    "institutional structural": "Institutional / Structural",
    "informational": "Informational",
    "information": "Informational",
    "technological": "Technological",
    "technology": "Technological",
}
OUTPUT_FIELDS = (
    "id", "name", "layer", "familyCode", "category", "subcategory",
    "taxonomyStatus", "driverRole", "typicalTimeScale", "definition",
    "mechanism", "behavioralConsequences", "behaviorChangeRelevance",
    "contextsBoundaryConditions", "modifiability", "measurementIndicators",
    "evidence", "caveats", "crossLayerInteractions", "aliases",
    "relatedDrivers", "examples", "source",
)
KNOWN_SUPPORT_SHEETS = {
    "summary", "families", "evidence library", "cautions boundaries", "taxonomy guide"
}
DRIVER_SIGNALS = {"id", "name", "category", "definition", "mechanism", "taxonomyStatus"}
HEADER_SCAN_ROWS = 25


@dataclass
class Summary:
    files: int = 0
    sheets: int = 0
    sheets_ignored: int = 0
    rows_processed: int = 0
    rows_skipped: int = 0
    ignored: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def clean(value: Any) -> str:
    return "" if value is None else re.sub(r"\s+", " ", str(value)).strip()


def key(value: Any) -> str:
    text = unicodedata.normalize("NFKC", clean(value)).casefold()
    return re.sub(r"[^\w]+", " ", text, flags=re.UNICODE).strip()


def normalize_layer(value: Any) -> str | None:
    return LAYER_ALIASES.get(key(value))


def alias_lookup() -> dict[str, str]:
    result: dict[str, str] = {}
    for field_name, aliases in HEADER_ALIASES.items():
        for alias in aliases:
            normalized = key(alias)
            if normalized in result and result[normalized] != field_name:
                raise ValueError(f"Header alias {alias!r} maps to multiple fields.")
            result[normalized] = field_name
    return result


def map_headers(values: tuple[Any, ...]) -> tuple[dict[str, int], list[str]]:
    lookup = alias_lookup()
    mapping: dict[str, int] = {}
    discovered: list[str] = []
    for index, value in enumerate(values):
        heading = clean(value)
        if not heading:
            continue
        discovered.append(heading)
        normalized = key(heading)
        field_name = lookup.get(normalized)
        if field_name is None and normalized.endswith(" mechanism pathway"):
            prefix = normalized.removesuffix(" mechanism pathway")
            if normalize_layer(prefix):
                field_name = "mechanism"
        if field_name and field_name not in mapping:
            mapping[field_name] = index
    return mapping, discovered


def find_header_row(sheet: Any) -> tuple[int, dict[str, int], list[str]] | None:
    best = None
    best_score = -1
    for number, row in enumerate(
        sheet.iter_rows(min_row=1, max_row=HEADER_SCAN_ROWS, values_only=True), start=1
    ):
        mapping, discovered = map_headers(row)
        if discovered and len(mapping) > best_score:
            best = (number, mapping, discovered)
            best_score = len(mapping)
        if "name" in mapping and len(mapping) >= 2:
            return number, mapping, discovered
    return best


def mentioned_layers(value: Any) -> set[str]:
    normalized = f" {key(value)} "
    matches: set[str] = set()
    for compound in ("physical environmental", "institutional structural"):
        if f" {compound} " in normalized:
            matches.add(LAYER_ALIASES[compound])
            normalized = normalized.replace(f" {compound} ", " ")
    for alias, canonical in LAYER_ALIASES.items():
        if " " not in alias and f" {alias} " in normalized:
            matches.add(canonical)
    return matches


def infer_layer(
    workbook_path: Path, sheet: Any, workbook_title: Any, title_text: list[str], summary: Summary
) -> str | None:
    sources = {
        "workbook filename": mentioned_layers(workbook_path.stem),
        "worksheet name": mentioned_layers(sheet.title),
        "workbook/title text": mentioned_layers(" ".join([clean(workbook_title), *title_text])),
    }
    location = f"{workbook_path.name} / {sheet.title}"
    for source_name, matches in sources.items():
        if len(matches) > 1:
            summary.errors.append(
                f"{location}: {source_name} identifies conflicting layers: {', '.join(sorted(matches))}"
            )
            return None
    inferred = {next(iter(matches)) for matches in sources.values() if matches}
    if len(inferred) > 1:
        details = ", ".join(
            f"{name}={next(iter(matches))}" for name, matches in sources.items() if matches
        )
        summary.errors.append(f"{location}: conflicting layer inference sources ({details}).")
        return None
    return next(iter(inferred)) if inferred else None


def split_list(value: Any) -> list[str]:
    if value is None or not str(value).strip():
        return []
    # Commas are deliberately not split because they are often part of citations or URLs.
    return [item for item in (clean(part) for part in re.split(r"[\r\n;|]+", str(value))) if item]


def slug(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_value.casefold()).strip("-") or "driver"


def get_cell(row: tuple[Any, ...], mapping: dict[str, int], field_name: str) -> Any:
    index = mapping.get(field_name)
    return row[index] if index is not None and index < len(row) else None


def row_layer(
    row: tuple[Any, ...], mapping: dict[str, int], inferred: str | None,
    location: str, summary: Summary
) -> str | None:
    raw = clean(get_cell(row, mapping, "layer"))
    if raw:
        explicit = normalize_layer(raw)
        if explicit is None:
            summary.errors.append(f"{location}: unrecognized explicit layer {raw!r}.")
            return None
        if inferred and explicit != inferred:
            summary.errors.append(
                f"{location}: explicit layer {explicit!r} conflicts with inferred layer {inferred!r}."
            )
            return None
        return explicit
    if inferred is None:
        summary.errors.append(f"{location}: layer is absent and could not be inferred.")
    return inferred


def make_record(
    row: tuple[Any, ...], mapping: dict[str, int], inferred: str | None,
    workbook_path: Path, sheet_name: str, row_number: int, summary: Summary
) -> dict[str, Any] | None:
    if not any(clean(value) for value in row):
        summary.rows_skipped += 1
        return None
    location = f"{workbook_path.name} / {sheet_name} / row {row_number}"
    name = clean(get_cell(row, mapping, "name"))
    if not name:
        summary.errors.append(f"{location}: missing required driver name.")
        summary.rows_skipped += 1
        return None
    layer = row_layer(row, mapping, inferred, location, summary)
    if layer is None:
        summary.rows_skipped += 1
        return None
    explicit_id = clean(get_cell(row, mapping, "id"))
    record = {
        "id": explicit_id or slug(f"{layer}-{name}"),
        "name": name,
        "layer": layer,
        "familyCode": clean(get_cell(row, mapping, "familyCode")),
        "category": clean(get_cell(row, mapping, "category")),
        "subcategory": clean(get_cell(row, mapping, "subcategory")),
        "taxonomyStatus": clean(get_cell(row, mapping, "taxonomyStatus")),
        "driverRole": clean(get_cell(row, mapping, "driverRole")),
        "typicalTimeScale": clean(get_cell(row, mapping, "typicalTimeScale")),
        "definition": clean(get_cell(row, mapping, "definition")),
        "mechanism": clean(get_cell(row, mapping, "mechanism")),
        "behavioralConsequences": clean(get_cell(row, mapping, "behavioralConsequences")),
        "behaviorChangeRelevance": clean(get_cell(row, mapping, "behaviorChangeRelevance")),
        "contextsBoundaryConditions": clean(get_cell(row, mapping, "contextsBoundaryConditions")),
        "modifiability": clean(get_cell(row, mapping, "modifiability")),
        "measurementIndicators": clean(get_cell(row, mapping, "measurementIndicators")),
        "evidence": {
            "grade": clean(get_cell(row, mapping, "evidenceGrade")),
            "ids": split_list(get_cell(row, mapping, "evidenceIds")),
            "urls": split_list(get_cell(row, mapping, "evidenceUrls")),
        },
        "caveats": clean(get_cell(row, mapping, "caveats")),
        "crossLayerInteractions": clean(get_cell(row, mapping, "crossLayerInteractions")),
        "aliases": split_list(get_cell(row, mapping, "aliases")),
        "relatedDrivers": split_list(get_cell(row, mapping, "relatedDrivers")),
        "examples": split_list(get_cell(row, mapping, "examples")),
        "source": {"workbook": workbook_path.name, "sheet": sheet_name},
    }
    summary.rows_processed += 1
    return record


def report_duplicates(records: list[dict[str, Any]], summary: Summary) -> None:
    names: dict[str, list[dict[str, Any]]] = defaultdict(list)
    layer_names: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    ids: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        normalized_name = key(record["name"])
        names[normalized_name].append(record)
        layer_names[(record["layer"], normalized_name)].append(record)
        ids[record["id"]].append(record)
    for normalized_name, matches in sorted(names.items()):
        if len(matches) > 1:
            summary.warnings.append(
                f"Potential duplicate normalized name {normalized_name!r}: "
                + ", ".join(item["id"] for item in matches)
            )
    for (layer, normalized_name), matches in sorted(layer_names.items()):
        if len(matches) > 1:
            summary.warnings.append(
                f"Potential duplicate name in {layer} ({normalized_name!r}): "
                + ", ".join(item["id"] for item in matches)
            )
    for driver_id, matches in sorted(ids.items()):
        if len(matches) > 1:
            summary.errors.append(f"Duplicate Driver ID {driver_id!r} ({len(matches)} records).")


def read_workbooks(source_dir: Path, summary: Summary) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    files = sorted(
        path for path in source_dir.rglob("*")
        if path.is_file() and path.suffix.casefold() == ".xlsx" and not path.name.startswith("~$")
    )
    summary.files = len(files)
    if not files:
        summary.errors.append(f"No XLSX files found in {source_dir}.")
        return records
    for path in files:
        try:
            workbook = load_workbook(path, read_only=True, data_only=True)
        except Exception as exc:
            summary.errors.append(f"{path.name}: could not open workbook: {exc}")
            continue
        try:
            for sheet in workbook.worksheets:
                location = f"{path.name} / {sheet.title}"
                if key(sheet.title) in KNOWN_SUPPORT_SHEETS:
                    summary.sheets_ignored += 1
                    summary.ignored.append(f"{location}: known supporting sheet")
                    continue
                header = find_header_row(sheet)
                if header is None:
                    summary.sheets_ignored += 1
                    summary.ignored.append(f"{location}: empty sheet")
                    continue
                header_row, mapping, discovered = header
                if "name" not in mapping:
                    message = (
                        f"{location}: missing mapped field name. "
                        f"Discovered headers: {discovered or ['(none)']}"
                    )
                    looks_like_drivers = (
                        "driver" in key(sheet.title).split()
                        or len(DRIVER_SIGNALS.intersection(mapping)) >= 3
                    )
                    if looks_like_drivers:
                        summary.warnings.append(message)
                    else:
                        summary.sheets_ignored += 1
                        summary.ignored.append(f"{location}: non-driver sheet")
                    continue
                title_text = [
                    clean(value)
                    for row in sheet.iter_rows(
                        min_row=1, max_row=max(1, header_row - 1), values_only=True
                    )
                    for value in row if clean(value)
                ]
                inferred = infer_layer(
                    path, sheet, workbook.properties.title, title_text, summary
                )
                summary.sheets += 1
                for row_number, row in enumerate(
                    sheet.iter_rows(min_row=header_row + 1, values_only=True),
                    start=header_row + 1,
                ):
                    record = make_record(
                        row, mapping, inferred, path, sheet.title, row_number, summary
                    )
                    if record is not None:
                        records.append(record)
        except Exception as exc:
            summary.errors.append(f"{path.name}: error while reading workbook: {exc}")
        finally:
            workbook.close()
    if summary.sheets == 0:
        summary.errors.append("No recognizable driver taxonomy worksheet was found.")
    return records


def validate(records: list[dict[str, Any]], summary: Summary) -> None:
    if not records:
        summary.errors.append("No valid driver records were produced.")
        return
    for record in records:
        missing = [field_name for field_name in OUTPUT_FIELDS if field_name not in record]
        if missing:
            summary.errors.append(f"Record {record.get('id')!r} lacks: {', '.join(missing)}")
        if not clean(record.get("id")):
            summary.errors.append("A driver has an empty ID.")
        if not clean(record.get("name")):
            summary.errors.append(f"Driver {record.get('id')!r} has an empty name.")
        if record.get("layer") not in CANONICAL_LAYERS:
            summary.errors.append(f"Driver {record.get('id')!r} has a non-canonical layer.")
        evidence = record.get("evidence")
        if (
            not isinstance(evidence, dict)
            or set(evidence) != {"grade", "ids", "urls"}
            or not isinstance(evidence.get("ids"), list)
            or not isinstance(evidence.get("urls"), list)
        ):
            summary.errors.append(f"Driver {record.get('id')!r} has invalid evidence.")
        for field_name in ("aliases", "relatedDrivers", "examples"):
            if not isinstance(record.get(field_name), list):
                summary.errors.append(
                    f"Driver {record.get('id')!r} has non-list field {field_name!r}."
                )
        source = record.get("source")
        if not isinstance(source, dict) or set(source) != {"workbook", "sheet"}:
            summary.errors.append(f"Driver {record.get('id')!r} has invalid source provenance.")
    report_duplicates(records, summary)


def write_atomically(records: list[dict[str, Any]], output: Path) -> None:
    content = json.dumps(records, ensure_ascii=False, indent=2) + "\n"
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", newline="\n", dir=output.parent,
            prefix=f".{output.name}.", suffix=".tmp", delete=False
        ) as handle:
            handle.write(content)
            temporary = Path(handle.name)
        temporary.replace(output)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def print_summary(summary: Summary, output: Path, wrote: bool) -> None:
    print(
        f"Import summary: files={summary.files}, sheets={summary.sheets}, "
        f"supporting_sheets_ignored={summary.sheets_ignored}, "
        f"rows_processed={summary.rows_processed}, rows_skipped={summary.rows_skipped}, "
        f"warnings={len(summary.warnings)}, errors={len(summary.errors)}"
    )
    for message in summary.ignored:
        print(f"IGNORED: {message}")
    for message in summary.warnings:
        print(f"WARNING: {message}")
    for message in summary.errors:
        print(f"ERROR: {message}", file=sys.stderr)
    print(
        f"Wrote {summary.rows_processed} drivers to {output}."
        if wrote else f"Did not modify {output}.",
        file=sys.stdout if wrote else sys.stderr,
    )


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    output = root / "data" / "drivers.json"
    summary = Summary()
    records = read_workbooks(root / "source-data", summary)
    validate(records, summary)
    records.sort(
        key=lambda item: (
            CANONICAL_LAYERS.index(item["layer"]), key(item["name"]), item["id"]
        )
    )
    wrote = False
    if not summary.errors:
        try:
            write_atomically(records, output)
            wrote = True
        except OSError as exc:
            summary.errors.append(f"Could not replace {output}: {exc}")
    print_summary(summary, output, wrote)
    return 0 if wrote else 1


if __name__ == "__main__":
    raise SystemExit(main())
