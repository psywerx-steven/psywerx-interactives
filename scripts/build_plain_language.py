"""Publish the approved PSYWERX plain-language Driver content.

The governed editorial source remains in the private ``analysis`` layer. This
exporter validates it against canonical ``data/drivers.json`` and writes only
the approved public fields to ``data/plain_language.json``. Canonical ontology
data and private editorial metadata never enter the public output.
"""

from __future__ import annotations

import csv
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"
CONTENT_VERSION = "1.0"
STANDARD_VERSION = "1.0"

EXPECTED_SOURCE_COLUMNS = (
    "driverId",
    "canonicalName",
    "layer",
    "family",
    "canonicalDefinition",
    "plainLanguageLabel",
    "plainLanguageExplanation",
    "analyticQuestion",
    "whatThisDoesNotMean",
    "meaningPreservationRisk",
    "releaseStatus",
    "finalQaFindings",
    "revisionFromPreviousCandidate",
    "reviewPriority",
    "humanDecision",
    "humanNotes",
    "plainnessQaStatus",
    "plainnessQaFindings",
)

CANONICAL_SNAPSHOT_FIELDS = {
    "canonicalName": "name",
    "layer": "layer",
    "family": "family",
    "canonicalDefinition": "definition",
}

PUBLIC_FIELDS = (
    "plainLanguageLabel",
    "plainLanguageExplanation",
    "analyticQuestion",
    "whatThisDoesNotMean",
)
PUBLIC_RECORD_KEYS = ("driverId",) + PUBLIC_FIELDS

APPROVED_RELEASE_STATUSES = {
    "CALIBRATED_APPROVED",
    "EDITORIAL_RELEASE_CANDIDATE",
    "EDITORIAL_REVISED_CANDIDATE",
}
PROTECTED_RELEASE_STATUSES = {
    "BLOCKED_ON_ONTOLOGY_REVIEW",
    "SUBJECT_MATTER_REVIEW_REQUIRED",
}
EXPECTED_COUNTS = {
    "source": 762,
    "approved": 737,
    "blocked": 22,
    "sme": 3,
}

WINDOWS_PATH = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]")


class ReleaseValidationError(Exception):
    """Raised when publication validation fails."""


def load_canonical_drivers(path: Path) -> list[dict[str, Any]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReleaseValidationError(
            f"Could not read canonical Driver data from {path.name}: {exc}"
        ) from exc
    if not isinstance(value, list):
        raise ReleaseValidationError("Canonical Driver data must be a JSON array.")
    return value


def load_release_rows(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = tuple(reader.fieldnames or ())
            if headers != EXPECTED_SOURCE_COLUMNS:
                raise ReleaseValidationError(
                    "Approved release-source headers do not match the governed "
                    f"contract. Expected {list(EXPECTED_SOURCE_COLUMNS)}; "
                    f"discovered {list(headers)}."
                )
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise ReleaseValidationError(
            f"Could not read approved release source {path.name}: {exc}"
        ) from exc
    incomplete_rows = any(
        None in row or any(value is None for value in row.values())
        for row in rows
    )
    if incomplete_rows:
        raise ReleaseValidationError(
            "Approved release source contains a row with missing or unexpected columns."
        )
    return rows


def require_text(value: Any, field: str, driver_id: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ReleaseValidationError(
            f"{driver_id}: approved field {field!r} must be a non-empty string."
        )
    return value


def validate_no_private_paths(value: Any, location: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            validate_no_private_paths(child, f"{location}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            validate_no_private_paths(child, f"{location}[{index}]")
    elif isinstance(value, str):
        lowered = value.casefold()
        if (
            WINDOWS_PATH.search(value)
            or "\\\\" in value
            or "file://" in lowered
            or "analysis/" in lowered
            or "analysis\\" in lowered
            or "source-data/" in lowered
            or "source-data\\" in lowered
        ):
            raise ReleaseValidationError(
                f"Private or local path detected in public output at {location}."
            )
        if "\ufffd" in value:
            raise ReleaseValidationError(
                f"Unicode replacement character detected in public output at {location}."
            )


def build_public_payload(
    canonical_drivers: list[dict[str, Any]],
    release_rows: list[dict[str, str]],
) -> tuple[dict[str, Any], dict[str, int]]:
    errors: list[str] = []
    canonical_by_id: dict[str, dict[str, Any]] = {}
    for index, driver in enumerate(canonical_drivers, start=1):
        driver_id = driver.get("id") if isinstance(driver, dict) else None
        if not isinstance(driver_id, str) or not driver_id:
            errors.append(f"Canonical Driver row {index} has no valid ID.")
            continue
        if driver_id in canonical_by_id:
            errors.append(f"Canonical Driver ID {driver_id!r} is duplicated.")
        canonical_by_id[driver_id] = driver

    release_by_id: dict[str, dict[str, str]] = {}
    status_counts = {"approved": 0, "blocked": 0, "sme": 0}
    for index, row in enumerate(release_rows, start=2):
        driver_id = row.get("driverId", "")
        if not driver_id:
            errors.append(f"Approved release-source row {index} has no Driver ID.")
            continue
        if driver_id in release_by_id:
            errors.append(
                f"Approved release-source Driver ID {driver_id!r} is duplicated."
            )
        release_by_id[driver_id] = row

        canonical = canonical_by_id.get(driver_id)
        if canonical is None:
            errors.append(f"{driver_id}: no matching canonical Driver exists.")
            continue
        for source_field, canonical_field in CANONICAL_SNAPSHOT_FIELDS.items():
            if row[source_field] != canonical.get(canonical_field):
                errors.append(
                    f"{driver_id}: {source_field} does not exactly match canonical "
                    f"{canonical_field}."
                )

        status = row["releaseStatus"]
        decision = row["humanDecision"]
        if status in APPROVED_RELEASE_STATUSES:
            status_counts["approved"] += 1
            if decision != "APPROVED":
                errors.append(
                    f"{driver_id}: publication-eligible content lacks an APPROVED "
                    "human decision."
                )
            for field in PUBLIC_FIELDS[:3]:
                if not row[field].strip():
                    errors.append(f"{driver_id}: approved field {field!r} is empty.")
        elif status == "BLOCKED_ON_ONTOLOGY_REVIEW":
            status_counts["blocked"] += 1
            if decision:
                errors.append(
                    f"{driver_id}: ontology-blocked content must remain unapproved."
                )
        elif status == "SUBJECT_MATTER_REVIEW_REQUIRED":
            status_counts["sme"] += 1
            if decision:
                errors.append(
                    f"{driver_id}: SME-review content must remain unapproved."
                )
        else:
            errors.append(f"{driver_id}: unsupported release status {status!r}.")

    canonical_ids = set(canonical_by_id)
    release_ids = set(release_by_id)
    missing = sorted(canonical_ids - release_ids)
    unexpected = sorted(release_ids - canonical_ids)
    if missing:
        errors.append(f"Release source is missing canonical IDs: {missing}.")
    if unexpected:
        errors.append(f"Release source contains unknown IDs: {unexpected}.")
    if len(canonical_drivers) != EXPECTED_COUNTS["source"]:
        errors.append(
            f"Expected {EXPECTED_COUNTS['source']} canonical Drivers; "
            f"found {len(canonical_drivers)}."
        )
    if len(release_rows) != EXPECTED_COUNTS["source"]:
        errors.append(
            f"Expected {EXPECTED_COUNTS['source']} release-source rows; "
            f"found {len(release_rows)}."
        )
    for key in ("approved", "blocked", "sme"):
        if status_counts[key] != EXPECTED_COUNTS[key]:
            errors.append(
                f"Expected {EXPECTED_COUNTS[key]} {key} records; "
                f"found {status_counts[key]}."
            )

    if errors:
        raise ReleaseValidationError("\n".join(errors))

    public_records: list[dict[str, Any]] = []
    for canonical in canonical_drivers:
        row = release_by_id[canonical["id"]]
        if row["releaseStatus"] in PROTECTED_RELEASE_STATUSES:
            continue
        boundary = row["whatThisDoesNotMean"]
        public_record = {
            "driverId": canonical["id"],
            "plainLanguageLabel": require_text(
                row["plainLanguageLabel"], "plainLanguageLabel", canonical["id"]
            ),
            "plainLanguageExplanation": require_text(
                row["plainLanguageExplanation"],
                "plainLanguageExplanation",
                canonical["id"],
            ),
            "analyticQuestion": require_text(
                row["analyticQuestion"], "analyticQuestion", canonical["id"]
            ),
            "whatThisDoesNotMean": boundary if boundary.strip() else None,
        }
        if tuple(public_record) != PUBLIC_RECORD_KEYS:
            raise ReleaseValidationError(
                f"{canonical['id']}: public record key order is not canonical."
            )
        public_records.append(public_record)

    if len(public_records) != EXPECTED_COUNTS["approved"]:
        raise ReleaseValidationError(
            f"Expected {EXPECTED_COUNTS['approved']} public records; "
            f"built {len(public_records)}."
        )

    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "contentVersion": CONTENT_VERSION,
        "standardVersion": STANDARD_VERSION,
        "drivers": public_records,
    }
    validate_no_private_paths(payload, "plain-language release")
    return payload, status_counts


def write_atomically(payload: dict[str, Any], output: Path) -> None:
    content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=output.parent,
            prefix=f".{output.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(content)
            temporary = Path(handle.name)
        os.replace(temporary, output)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    source = (
        root
        / "analysis"
        / "plain_language_release_candidate_v2"
        / "plain_language_release_candidate_v2.csv"
    )
    canonical_path = root / "data" / "drivers.json"
    output = root / "data" / "plain_language.json"

    try:
        canonical_drivers = load_canonical_drivers(canonical_path)
        release_rows = load_release_rows(source)
        payload, counts = build_public_payload(canonical_drivers, release_rows)
        write_atomically(payload, output)
    except ReleaseValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        print(f"Did not modify {output}.", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"ERROR: Could not replace {output}: {exc}", file=sys.stderr)
        print(f"Did not modify {output}.", file=sys.stderr)
        return 1

    print("Plain-language release statistics")
    print(f"  Source Drivers: {len(release_rows)}")
    print(f"  Approved public records: {counts['approved']}")
    print(f"  Ontology-blocked records withheld: {counts['blocked']}")
    print(f"  SME-review records withheld: {counts['sme']}")
    print(f"  Content version: {CONTENT_VERSION}")
    print(f"Wrote validated data to {output}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
