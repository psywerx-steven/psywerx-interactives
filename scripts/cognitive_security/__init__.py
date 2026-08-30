"""PSYWERX Cognitive Security Map source-ingestion primitives.

The package deliberately separates workbook extraction from semantic
normalization.  Callers can inspect the lossless extracted tables before
building the governed normalized entity collections.
"""

from .extract import extract_sources
from .normalize import normalize_sources
from .sources import SourceValidationError


def build_normalized_dataset(source_dir):
    """Extract and normalize the eight-workbook source package."""

    return normalize_sources(extract_sources(source_dir))


__all__ = (
    "SourceValidationError",
    "build_normalized_dataset",
    "extract_sources",
    "normalize_sources",
)
