"""Deterministic, source-preserving normalization helpers."""

from __future__ import annotations

import ast
import hashlib
import re
import unicodedata
from datetime import date, datetime, time
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


_WHITESPACE = re.compile(r"\s+")
_NATURAL_PART = re.compile(r"(\d+)")
_DICT_ID = re.compile(
    r"[\"'](?P<key>[A-Za-z_][A-Za-z0-9_]*)[\"']\s*:\s*"
    r"[\"'](?P<value>[^\"']+)[\"']"
)


def normalize_text(value: Any) -> str | None:
    """Collapse source whitespace and represent empty cells as ``None``."""

    if value is None:
        return None
    result = _WHITESPACE.sub(" ", str(value)).strip()
    return result or None


def normalize_cell(value: Any) -> Any:
    """Normalize a cell without coercing meaningful numeric/boolean types."""

    if value is None:
        return None
    if isinstance(value, str):
        return normalize_text(value)
    if isinstance(value, datetime):
        return value.isoformat(timespec="seconds")
    if isinstance(value, (date, time)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    return value


def identifier(value: Any) -> str | None:
    """Return a stable textual representation for a source-authored ID."""

    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return str(int(value)) if value.is_integer() else format(value, ".15g")
    return normalize_text(value)


def normalized_key(value: Any) -> str:
    """Case-insensitive comparison key; never use as displayed source text."""

    text = unicodedata.normalize("NFKC", normalize_text(value) or "").casefold()
    return re.sub(r"[^\w]+", " ", text, flags=re.UNICODE).strip()


def deterministic_id(prefix: str, *parts: Any, length: int = 16) -> str:
    """Create a stable ID from normalized semantic identity, never time/row."""

    if not prefix or not re.fullmatch(r"[A-Za-z][A-Za-z0-9-]*", prefix):
        raise ValueError("A URL-safe deterministic-ID prefix is required.")
    # Case and whitespace are non-semantic for generated identity, but retain
    # punctuation so distinct source labels cannot collapse to the same ID.
    identity = "\x1f".join(
        unicodedata.normalize("NFKC", normalize_text(part) or "").casefold()
        for part in parts
    )
    if not identity.replace("\x1f", ""):
        raise ValueError("At least one non-empty identity component is required.")
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:length].upper()
    return f"{prefix.upper()}-{digest}"


def file_sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def natural_key(value: Any) -> tuple[Any, ...]:
    """Deterministic human-friendly key for mixed alpha/numeric identifiers."""

    return tuple(
        int(part) if part.isdigit() else part.casefold()
        for part in _NATURAL_PART.split(str(value or ""))
    )


def stable_unique(values: Iterable[Any]) -> list[Any]:
    result: list[Any] = []
    seen: set[Any] = set()
    for value in values:
        marker = value if isinstance(value, (str, int, float, bool, type(None))) else repr(value)
        if marker in seen:
            continue
        seen.add(marker)
        result.append(value)
    return result


def split_values(
    value: Any,
    delimiters: Sequence[str] = (";",),
    *,
    drop_missing_tokens: bool = False,
) -> list[str]:
    """Split a source list while preserving first-seen order and wording."""

    text = normalize_text(value)
    if text is None:
        return []
    pattern = "|".join(re.escape(delimiter) for delimiter in delimiters)
    parts = [normalize_text(part) for part in re.split(pattern, text)]
    values = [part for part in parts if part is not None]
    if drop_missing_tokens:
        values = [
            part
            for part in values
            if normalized_key(part) not in {"none", "nan", "n a", "not applicable"}
        ]
    return stable_unique(values)


def literal_list(value: Any, *, fallback_delimiters: Sequence[str] = (";",)) -> list[str]:
    """Read a serialized Python list used by final_synthesis, conservatively."""

    text = normalize_text(value)
    if text is None:
        return []
    if text[:1] in {"[", "("} and text[-1:] in {"]",
        ")",
    }:
        try:
            parsed = ast.literal_eval(text)
        except (SyntaxError, ValueError):
            parsed = None
        if isinstance(parsed, (list, tuple)):
            return stable_unique(
                item for raw in parsed if (item := normalize_text(raw)) is not None
            )
    return split_values(text, fallback_delimiters)


def embedded_reference_ids(value: Any, key: str) -> list[str]:
    """Extract explicit IDs from serialized ``{'key': 'ID'}`` references."""

    text = normalize_text(value)
    if text is None:
        return []
    wanted = key.casefold()
    return stable_unique(
        identifier(match.group("value"))
        for match in _DICT_ID.finditer(text)
        if match.group("key").casefold() == wanted
        and identifier(match.group("value")) is not None
    )


def prefixed_reference_ids(value: Any, pattern: str) -> list[str]:
    """Extract explicit prefixed IDs without guessing from descriptive prose."""

    text = normalize_text(value)
    if text is None:
        return []
    return stable_unique(re.findall(pattern, text, flags=re.IGNORECASE))


def as_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in {0, 1}:
        return bool(value)
    key = normalized_key(value)
    if key in {"true", "yes", "y", "1"}:
        return True
    if key in {"false", "no", "n", "0"}:
        return False
    return None


def as_int(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    text = normalize_text(value)
    return int(text) if text and re.fullmatch(r"[+-]?\d+", text) else None


def as_number(value: Any) -> int | float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value
    text = normalize_text(value)
    if text is None:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    return int(number) if number.is_integer() else number


def source_ref(row: Mapping[str, Any]) -> dict[str, Any]:
    """Copy the portable workbook provenance attached during extraction."""

    source = row.get("_source")
    if not isinstance(source, Mapping):
        raise ValueError("Extracted row is missing _source provenance.")
    return {
        "artifactId": source["artifactId"],
        "fileName": source["fileName"],
        "sheet": source["sheet"],
        "rowNumber": source["rowNumber"],
    }


def sort_records(records: Iterable[dict[str, Any]], *keys: str) -> list[dict[str, Any]]:
    return sorted(
        records,
        key=lambda record: tuple(natural_key(record.get(key)) for key in keys),
    )
