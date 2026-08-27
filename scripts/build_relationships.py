"""Build data/relationships.json from canonical Relationships worksheets."""

from __future__ import annotations

import json
import os
import re
import tempfile
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


SCHEMA_VERSION = "1.0"
WORKBOOK_COUNT = 8
RELATIONSHIP_SHEET = "Relationships"
HEADER_ROW = 4
FIRST_DATA_ROW = 5
CANONICAL_LAYERS = (
    "Biological",
    "Psychological",
    "Social",
    "Cultural",
    "Physical / Environmental",
    "Institutional / Structural",
    "Informational",
    "Technological",
)
FILENAME_LAYER_PATTERNS = (
    (r"(?:^|_)layer_1_biological(?:_|$)", "Biological"),
    (r"(?:^|_)layer_2_psychological(?:_|$)", "Psychological"),
    (r"(?:^|_)layer_3_social(?:_|$)", "Social"),
    (r"(?:^|_)layer_4_cultural(?:_|$)", "Cultural"),
    (
        r"(?:^|_)layer_5_physical_environmental(?:_|$)",
        "Physical / Environmental",
    ),
    (
        r"(?:^|_)layer_6_institutional_structural(?:_|$)",
        "Institutional / Structural",
    ),
    (r"(?:^|_)layer_7_informational(?:_|$)", "Informational"),
    (r"(?:^|_)layer_8_technological(?:_|$)", "Technological"),
)
HEADERS = (
    "Relationship ID",
    "Source Driver ID",
    "Source Driver",
    "Target Driver ID",
    "Target Driver",
    "Relationship Type",
    "Expected Direction",
    "Functional Form",
    "Moderators / Conditions",
    "Time Lag",
    "Evidence Strength",
    "Evidence Notes",
    "Evidence IDs",
)
OUTPUT_KEYS = (
    "id",
    "sourceDriverId",
    "sourceDriverName",
    "targetDriverId",
    "targetDriverName",
    "relationshipType",
    "expectedDirection",
    "functionalForm",
    "moderatorsConditions",
    "timeLag",
    "evidenceStrength",
    "evidenceNotes",
    "evidenceIds",
    "source",
)
HEADER_TO_KEY = dict(zip(HEADERS, OUTPUT_KEYS[:-1]))
CONTROLLED_CODEBOOK_TERMS = {
    "expectedDirection": (
        "CB-REL-EXPECTED-DIRECTION",
        "Expected Direction",
    ),
    "evidenceStrength": (
        "CB-REL-EVIDENCE-STRENGTH",
        "Evidence Strength",
    ),
}
LOCAL_PATH_PATTERN = re.compile(
    r"(?:[A-Za-z]:[\\/]|/Users/|/home/|\\\\[^\\]+\\[^\\]+)",
    flags=re.IGNORECASE,
)


@dataclass
class Summary:
    workbooks: int = 0
    relationship_sheets: int = 0
    relationships: int = 0
    unique_relationship_ids: int = 0
    unique_directed_pairs: int = 0
    same_layer: int = 0
    cross_layer: int = 0
    duplicate_ids: int = 0
    duplicate_pairs: int = 0
    duplicate_records: int = 0
    self_relationships: int = 0
    unresolved_driver_ids: int = 0
    driver_name_mismatches: int = 0
    codebook_violations: int = 0
    by_layer: dict[str, int] = field(default_factory=dict)
    by_direction: dict[str, int] = field(default_factory=dict)
    by_evidence_strength: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def source_text(value: Any) -> str:
    """Trim cell boundaries while preserving internal source wording."""
    return "" if value is None else str(value).strip()


def explicit_id(value: Any) -> str:
    """Preserve an explicit identity exactly; validation handles whitespace."""
    return "" if value is None else str(value)


def normalized_text(value: Any) -> str:
    return unicodedata.normalize("NFKC", source_text(value)).casefold()


def filename_layer(path: Path) -> str | None:
    filename = path.stem.casefold()
    matches = {
        layer
        for pattern, layer in FILENAME_LAYER_PATTERNS
        if re.search(pattern, filename)
    }
    return next(iter(matches)) if len(matches) == 1 else None


def header_values(sheet: Any) -> tuple[str, ...]:
    values = [source_text(cell.value) for cell in sheet[HEADER_ROW]]
    while values and not values[-1]:
        values.pop()
    return tuple(values)


def row_has_content(row: tuple[Any, ...]) -> bool:
    return any(source_text(value) for value in row)


def split_evidence_ids(value: Any) -> list[str]:
    if value is None or not str(value).strip():
        return []
    return [source_text(part) for part in str(value).split(";")]


def load_drivers(path: Path, summary: Summary) -> dict[str, dict[str, str]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        summary.errors.append(f"Could not load {path.name}: {exc}")
        return {}
    if not isinstance(payload, list):
        summary.errors.append(f"{path.name}: expected a top-level JSON array.")
        return {}

    drivers: dict[str, dict[str, str]] = {}
    for index, record in enumerate(payload):
        location = f"{path.name} / record {index}"
        if not isinstance(record, dict):
            summary.errors.append(f"{location}: expected an object.")
            continue
        values: dict[str, str] = {}
        for key in ("id", "name", "layer"):
            value = record.get(key)
            if not isinstance(value, str) or not value:
                summary.errors.append(
                    f"{location}: {key!r} must be a non-empty string."
                )
            else:
                values[key] = value
        driver_id = values.get("id")
        if not driver_id:
            continue
        if driver_id in drivers:
            summary.errors.append(
                f"{path.name}: duplicate canonical Driver ID {driver_id!r}."
            )
            continue
        if values.get("layer") not in CANONICAL_LAYERS:
            summary.errors.append(
                f"{location}: invalid canonical Driver layer {values.get('layer')!r}."
            )
        drivers[driver_id] = values
    return drivers


def load_controlled_values(
    path: Path, summary: Summary
) -> dict[str, set[str]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        summary.errors.append(f"Could not load {path.name}: {exc}")
        return {}
    entries = payload.get("entries") if isinstance(payload, dict) else None
    if not isinstance(entries, list):
        summary.errors.append(f"{path.name}: expected an entries array.")
        return {}

    by_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        if isinstance(entry, dict) and isinstance(entry.get("id"), str):
            by_id[entry["id"]].append(entry)

    controlled: dict[str, set[str]] = {}
    for output_key, (term_id, expected_field) in CONTROLLED_CODEBOOK_TERMS.items():
        matches = by_id.get(term_id, [])
        if len(matches) != 1:
            summary.errors.append(
                f"{path.name}: expected exactly one Codebook term {term_id!r}; "
                f"found {len(matches)}."
            )
            continue
        entry = matches[0]
        if entry.get("sheet") != RELATIONSHIP_SHEET:
            summary.errors.append(
                f"{path.name}: {term_id!r} has sheet {entry.get('sheet')!r}; "
                f"expected {RELATIONSHIP_SHEET!r}."
            )
        if entry.get("field") != expected_field:
            summary.errors.append(
                f"{path.name}: {term_id!r} has field {entry.get('field')!r}; "
                f"expected {expected_field!r}."
            )
        if entry.get("required") is not True:
            summary.errors.append(f"{path.name}: {term_id!r} must be required.")
        allowed = entry.get("allowedValues")
        if (
            not isinstance(allowed, list)
            or not allowed
            or any(not isinstance(value, str) or not value for value in allowed)
        ):
            summary.errors.append(
                f"{path.name}: {term_id!r} lacks a valid allowedValues list."
            )
            continue
        if len(allowed) != len(set(allowed)):
            summary.errors.append(
                f"{path.name}: {term_id!r} repeats an allowed value."
            )
        controlled[output_key] = set(allowed)
    return controlled


def build_record(
    row: tuple[Any, ...],
    path: Path,
    row_number: int,
    summary: Summary,
) -> dict[str, Any]:
    location = f"{path.name} / {RELATIONSHIP_SHEET} / row {row_number}"
    values = {
        header: row[index] if index < len(row) else None
        for index, header in enumerate(HEADERS)
    }
    record: dict[str, Any] = {}
    for header in HEADERS:
        key = HEADER_TO_KEY[header]
        value = values[header]
        if key in ("id", "sourceDriverId", "targetDriverId"):
            parsed: Any = explicit_id(value)
            if parsed and parsed != parsed.strip():
                summary.errors.append(
                    f"{location}: {header!r} has leading or trailing whitespace; "
                    "explicit IDs are never normalized."
                )
        elif key == "evidenceIds":
            parsed = split_evidence_ids(value)
        else:
            parsed = source_text(value)
        record[key] = parsed

    for header in HEADERS:
        key = HEADER_TO_KEY[header]
        value = record[key]
        if (isinstance(value, str) and not value) or (
            isinstance(value, list) and not value
        ):
            summary.errors.append(
                f"{location}: required field {header!r} is empty."
            )
    evidence_ids = record["evidenceIds"]
    if any(not item for item in evidence_ids):
        summary.errors.append(
            f"{location}: Evidence IDs contains an empty semicolon-delimited item."
        )
    if len(evidence_ids) != len(set(evidence_ids)):
        summary.errors.append(f"{location}: Evidence IDs contains a duplicate item.")

    record["source"] = {
        "workbook": path.name,
        "sheet": RELATIONSHIP_SHEET,
        "row": row_number,
    }
    return record


def read_workbooks(source_dir: Path, summary: Summary) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    paths = sorted(
        path
        for path in source_dir.rglob("*")
        if path.is_file()
        and path.suffix.casefold() == ".xlsx"
        and not path.name.startswith("~$")
    )
    summary.workbooks = len(paths)
    if len(paths) != WORKBOOK_COUNT:
        summary.errors.append(
            f"Expected {WORKBOOK_COUNT} XLSX workbooks; found {len(paths)}."
        )

    workbook_layers: dict[str, list[str]] = defaultdict(list)
    for path in paths:
        layer = filename_layer(path)
        if layer is None:
            summary.errors.append(
                f"{path.name}: filename does not identify exactly one canonical layer."
            )
        else:
            workbook_layers[layer].append(path.name)
        try:
            workbook = load_workbook(path, read_only=True, data_only=True)
        except Exception as exc:
            summary.errors.append(f"{path.name}: could not open workbook: {exc}")
            continue
        try:
            matching_sheets = [
                sheet
                for sheet in workbook.worksheets
                if sheet.title == RELATIONSHIP_SHEET
            ]
            if len(matching_sheets) != 1:
                summary.errors.append(
                    f"{path.name}: expected exactly one {RELATIONSHIP_SHEET!r} "
                    f"worksheet; found {len(matching_sheets)}."
                )
                continue
            sheet = matching_sheets[0]
            summary.relationship_sheets += 1
            actual_headers = header_values(sheet)
            if actual_headers != HEADERS:
                summary.errors.append(
                    f"{path.name} / {sheet.title}: expected exact headers "
                    f"{HEADERS}; found {actual_headers}."
                )
                continue
            for row_number, row in enumerate(
                sheet.iter_rows(min_row=FIRST_DATA_ROW, values_only=True),
                start=FIRST_DATA_ROW,
            ):
                if not row_has_content(row):
                    continue
                if any(source_text(value) for value in row[len(HEADERS) :]):
                    summary.errors.append(
                        f"{path.name} / {sheet.title} / row {row_number}: "
                        "unexpected data appears beyond the 13 canonical columns."
                    )
                records.append(build_record(row, path, row_number, summary))
        except Exception as exc:
            summary.errors.append(
                f"{path.name}: error while reading Relationships worksheet: {exc}"
            )
        finally:
            workbook.close()

    for layer in CANONICAL_LAYERS:
        matches = workbook_layers.get(layer, [])
        if len(matches) != 1:
            summary.errors.append(
                f"Canonical source layer {layer!r} must have exactly one workbook; "
                f"found {len(matches)}."
            )
    return records


def record_signature(record: dict[str, Any]) -> tuple[Any, ...]:
    return (
        record["sourceDriverId"],
        record["sourceDriverName"],
        record["targetDriverId"],
        record["targetDriverName"],
        record["relationshipType"],
        record["expectedDirection"],
        record["functionalForm"],
        record["moderatorsConditions"],
        record["timeLag"],
        record["evidenceStrength"],
        record["evidenceNotes"],
        tuple(record["evidenceIds"]),
    )


def validate_records(
    records: list[dict[str, Any]],
    drivers: dict[str, dict[str, str]],
    controlled: dict[str, set[str]],
    summary: Summary,
) -> None:
    if not records:
        summary.errors.append("No Relationship records were produced.")
        return
    ids: dict[str, list[dict[str, Any]]] = defaultdict(list)
    pairs: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    signatures: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    layer_counts: Counter[str] = Counter()
    direction_counts: Counter[str] = Counter()
    evidence_counts: Counter[str] = Counter()

    for record in records:
        if tuple(record) != OUTPUT_KEYS:
            summary.errors.append(
                f"Relationship {record.get('id')!r} has a non-canonical key structure."
            )
        relationship_id = record["id"]
        if relationship_id:
            ids[relationship_id].append(record)
        pair = (record["sourceDriverId"], record["targetDriverId"])
        pairs[pair].append(record)
        signatures[record_signature(record)].append(record)

        if pair[0] and pair[0] == pair[1]:
            summary.self_relationships += 1
            summary.errors.append(
                f"Relationship {relationship_id!r} is a prohibited self-relationship."
            )

        resolved: dict[str, dict[str, str]] = {}
        for role, id_key, name_key in (
            ("source", "sourceDriverId", "sourceDriverName"),
            ("target", "targetDriverId", "targetDriverName"),
        ):
            driver = drivers.get(record[id_key])
            if driver is None:
                summary.unresolved_driver_ids += 1
                summary.errors.append(
                    f"Relationship {relationship_id!r}: {role} Driver ID "
                    f"{record[id_key]!r} does not resolve exactly in drivers.json."
                )
                continue
            resolved[role] = driver
            if record[name_key] != driver["name"]:
                summary.driver_name_mismatches += 1
                summary.errors.append(
                    f"Relationship {relationship_id!r}: {role} Driver name "
                    f"{record[name_key]!r} does not exactly match canonical name "
                    f"{driver['name']!r} for {record[id_key]!r}."
                )

        source_layer = resolved.get("source", {}).get("layer")
        target_layer = resolved.get("target", {}).get("layer")
        if source_layer and target_layer:
            if source_layer == target_layer:
                summary.same_layer += 1
            else:
                summary.cross_layer += 1

        workbook_layer = filename_layer(Path(record["source"]["workbook"]))
        if workbook_layer:
            layer_counts[workbook_layer] += 1
        direction_counts[record["expectedDirection"]] += 1
        evidence_counts[record["evidenceStrength"]] += 1

        for key in ("expectedDirection", "evidenceStrength"):
            allowed = controlled.get(key)
            if allowed is not None and record[key] not in allowed:
                summary.codebook_violations += 1
                summary.errors.append(
                    f"Relationship {relationship_id!r}: {key} value "
                    f"{record[key]!r} is not defined by the canonical Codebook."
                )

    for relationship_id, matches in sorted(ids.items()):
        if len(matches) > 1:
            summary.duplicate_ids += 1
            summary.errors.append(
                f"Duplicate Relationship ID {relationship_id!r} "
                f"({len(matches)} records)."
            )
    for pair, matches in sorted(pairs.items()):
        if len(matches) > 1:
            summary.duplicate_pairs += 1
            summary.errors.append(
                f"Duplicate directed Driver pair {pair!r} ({len(matches)} records)."
            )
    for signature, matches in signatures.items():
        if len(matches) > 1:
            summary.duplicate_records += 1
            relationship_ids = sorted(record["id"] for record in matches)
            summary.errors.append(
                "Duplicate Relationship record content under IDs: "
                + ", ".join(repr(value) for value in relationship_ids)
            )

    summary.relationships = len(records)
    summary.unique_relationship_ids = len(ids)
    summary.unique_directed_pairs = len(pairs)
    summary.by_layer = {
        layer: layer_counts[layer] for layer in CANONICAL_LAYERS
    }
    summary.by_direction = dict(sorted(direction_counts.items()))
    summary.by_evidence_strength = dict(sorted(evidence_counts.items()))


def relationship_sort_key(record: dict[str, Any]) -> tuple[int, str, str, str]:
    layer = filename_layer(Path(record["source"]["workbook"]))
    layer_index = (
        CANONICAL_LAYERS.index(layer)
        if layer in CANONICAL_LAYERS
        else len(CANONICAL_LAYERS)
    )
    return (
        layer_index,
        normalized_text(record["id"]),
        record["sourceDriverId"],
        record["targetDriverId"],
    )


def contains_local_path(value: Any) -> bool:
    if isinstance(value, str):
        return bool(LOCAL_PATH_PATTERN.search(value))
    if isinstance(value, list):
        return any(contains_local_path(item) for item in value)
    if isinstance(value, dict):
        return any(contains_local_path(item) for item in value.values())
    return False


def write_atomically(payload: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=output.parent,
            prefix=f".{output.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_name = temporary.name
            json.dump(payload, temporary, ensure_ascii=False, indent=2)
            temporary.write("\n")
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_name, output)
    except Exception:
        if temporary_name:
            Path(temporary_name).unlink(missing_ok=True)
        raise


def relationship_type_diagnostics(
    records: list[dict[str, Any]],
) -> tuple[dict[str, tuple[int, list[str]]], list[list[str]], list[list[str]]]:
    inventory: dict[str, Counter[str]] = defaultdict(Counter)
    for record in records:
        layer = filename_layer(Path(record["source"]["workbook"])) or "Unknown"
        inventory[record["relationshipType"]][layer] += 1

    rendered = {
        value: (sum(counts.values()), sorted(counts, key=layer_order))
        for value, counts in sorted(inventory.items())
    }
    case_groups: dict[str, list[str]] = defaultdict(list)
    for value in inventory:
        case_groups[normalized_text(value)].append(value)
    capitalization_variants = [
        sorted(values) for values in case_groups.values() if len(values) > 1
    ]

    lexical_groups: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for value in inventory:
        tokens = re.findall(r"[a-z0-9]+", normalized_text(value))
        tokens = ["influence" if token == "influences" else token for token in tokens]
        reduced = tuple(
            sorted(token for token in tokens if token not in {"influence", "relationship"})
        )
        if reduced:
            lexical_groups[reduced].append(value)
    lexical_variants = [
        sorted(values)
        for values in lexical_groups.values()
        if len(values) > 1
    ]
    if "Influence" in inventory and "Influences" in inventory:
        lexical_variants.append(["Influence", "Influences"])
    lexical_variants.sort()
    return rendered, capitalization_variants, lexical_variants


def layer_order(layer: str) -> int:
    return (
        CANONICAL_LAYERS.index(layer)
        if layer in CANONICAL_LAYERS
        else len(CANONICAL_LAYERS)
    )


def graph_diagnostics(
    records: list[dict[str, Any]], drivers: dict[str, dict[str, str]]
) -> dict[str, Any]:
    outgoing: Counter[str] = Counter()
    incoming: Counter[str] = Counter()
    for record in records:
        outgoing[record["sourceDriverId"]] += 1
        incoming[record["targetDriverId"]] += 1
    all_ids = set(drivers)
    with_outgoing = set(outgoing)
    with_incoming = set(incoming)
    connected = with_outgoing | with_incoming

    def leaders(counts: Counter[str]) -> list[tuple[str, str, int]]:
        ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:10]
        return [
            (driver_id, drivers.get(driver_id, {}).get("name", "<unresolved>"), count)
            for driver_id, count in ranked
        ]

    return {
        "uniqueSources": len(with_outgoing),
        "uniqueTargets": len(with_incoming),
        "uniqueDriversReferenced": len(connected),
        "zeroDegreeDrivers": len(all_ids - connected),
        "onlyIncoming": len(with_incoming - with_outgoing),
        "onlyOutgoing": len(with_outgoing - with_incoming),
        "bothIncomingAndOutgoing": len(with_incoming & with_outgoing),
        "highestOutgoing": leaders(outgoing),
        "highestIncoming": leaders(incoming),
    }


def print_summary(
    summary: Summary,
    records: list[dict[str, Any]],
    drivers: dict[str, dict[str, str]],
    output: Path,
    wrote: bool,
) -> None:
    print("PSYWERX Relationship import summary")
    print(f"Workbooks: {summary.workbooks}")
    print(f"Relationships worksheets: {summary.relationship_sheets}")
    print(f"Relationships: {summary.relationships}")
    print(f"Unique Relationship IDs: {summary.unique_relationship_ids}")
    print(f"Unique directed pairs: {summary.unique_directed_pairs}")
    print("Relationships by source Layer workbook:")
    for layer in CANONICAL_LAYERS:
        print(f"  {layer}: {summary.by_layer.get(layer, 0)}")
    print("Expected Direction counts:")
    for value, count in summary.by_direction.items():
        print(f"  {value}: {count}")
    print("Evidence Strength counts:")
    for value, count in summary.by_evidence_strength.items():
        print(f"  {value}: {count}")
    print(f"Same-layer relationships: {summary.same_layer}")
    print(f"Cross-layer relationships: {summary.cross_layer}")
    print(f"Duplicate Relationship IDs: {summary.duplicate_ids}")
    print(f"Duplicate directed pairs: {summary.duplicate_pairs}")
    print(f"Duplicate Relationship records: {summary.duplicate_records}")
    print(f"Self-relationships: {summary.self_relationships}")
    print(f"Unresolved Driver IDs: {summary.unresolved_driver_ids}")
    print(f"Driver name mismatches: {summary.driver_name_mismatches}")
    print(f"Codebook violations: {summary.codebook_violations}")

    inventory, capitalization_variants, lexical_variants = (
        relationship_type_diagnostics(records)
    )
    print(f"Relationship Type exact values: {len(inventory)}")
    for value, (count, layers) in inventory.items():
        print(f"  {value}: {count} [{'; '.join(layers)}]")
    print("Relationship Type capitalization-only variants:")
    if capitalization_variants:
        for group in capitalization_variants:
            print(f"  {' | '.join(group)}")
    else:
        print("  None")
    print("Relationship Type obvious lexical variants (diagnostic only):")
    if lexical_variants:
        for group in lexical_variants:
            print(f"  {' | '.join(group)}")
    else:
        print("  None")

    graph = graph_diagnostics(records, drivers)
    print("Graph diagnostics:")
    for label, key in (
        ("Unique source Drivers", "uniqueSources"),
        ("Unique target Drivers", "uniqueTargets"),
        ("Unique Drivers referenced by any edge", "uniqueDriversReferenced"),
        ("Zero-degree Drivers", "zeroDegreeDrivers"),
        ("Drivers with only incoming edges", "onlyIncoming"),
        ("Drivers with only outgoing edges", "onlyOutgoing"),
        ("Drivers with both incoming and outgoing edges", "bothIncomingAndOutgoing"),
    ):
        print(f"  {label}: {graph[key]}")
    print("Highest outgoing degree (top 10):")
    for driver_id, name, count in graph["highestOutgoing"]:
        print(f"  {driver_id} | {name}: {count}")
    print("Highest incoming degree (top 10):")
    for driver_id, name, count in graph["highestIncoming"]:
        print(f"  {driver_id} | {name}: {count}")

    print(f"Warnings: {len(summary.warnings)}")
    for warning in summary.warnings:
        print(f"WARNING: {warning}")
    print(f"Errors: {len(summary.errors)}")
    for error in summary.errors:
        print(f"ERROR: {error}")
    if wrote:
        print(f"Wrote {output}")
    else:
        print(f"Did not modify {output}")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    source_dir = root / "source-data"
    output = root / "data" / "relationships.json"
    summary = Summary()

    drivers = load_drivers(root / "data" / "drivers.json", summary)
    controlled = load_controlled_values(root / "data" / "codebook.json", summary)
    records = read_workbooks(source_dir, summary)
    validate_records(records, drivers, controlled, summary)
    records.sort(key=relationship_sort_key)
    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "relationships": records,
    }
    if contains_local_path(payload):
        summary.errors.append("Generated Relationship payload contains a local path.")

    wrote = False
    if not summary.errors:
        try:
            write_atomically(payload, output)
            wrote = True
        except OSError as exc:
            summary.errors.append(f"Could not replace {output}: {exc}")
    print_summary(summary, records, drivers, output, wrote)
    return 0 if wrote else 1


if __name__ == "__main__":
    raise SystemExit(main())
