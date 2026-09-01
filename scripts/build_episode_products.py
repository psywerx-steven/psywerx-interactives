"""Build legacy private episode pilots and standalone relationships.

This authoring command is intentionally separate from the ordinary website
build.  It may read the ignored normalized historical release and writes its
full source packages only beneath ``analysis/``. Transcript-summary publication
has moved to ``build_transcript_summaries.py`` and is blocked here so the
transcript manifest and grounding-QA release gate cannot be bypassed.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from cognitive_security.episode_products import (
    build_private_source_packages,
    build_summary_authoring_inputs,
    episode_relationship_payload,
    select_representative_pilot,
    validate_frozen_summaries,
)
from cognitive_security.export import serialize_payloads, write_serialized_files


REQUIRED_PRIVATE_COLLECTIONS = (
    "episodes",
    "episode_source_mappings",
    "items",
    "item_tags",
    "categories",
    "clusters",
    "item_cluster_assignments",
    "cluster_meta_mappings",
    "meta_clusters",
    "themes",
    "theme_cluster_evidence",
    "theme_meta_mappings",
    "tensions",
    "tension_mappings",
)


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_dataset(normalized_dir: Path) -> dict[str, Any]:
    missing = [
        f"{collection}.json"
        for collection in REQUIRED_PRIVATE_COLLECTIONS
        if not (normalized_dir / f"{collection}.json").is_file()
    ]
    if missing:
        raise FileNotFoundError(
            f"Normalized directory {normalized_dir} is missing: {', '.join(missing)}"
        )
    return {
        collection: _load_json(normalized_dir / f"{collection}.json")
        for collection in REQUIRED_PRIVATE_COLLECTIONS
    }


def _relationship_counts(records: list[dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(row["relationshipType"] for row in records).items()))


def build(args: argparse.Namespace) -> dict[str, Any]:
    if args.summaries_from:
        raise ValueError(
            "Transcript-summary publication is not supported by this legacy "
            "structured-item command. Use scripts/build_transcript_summaries.py "
            "and its manifest, QA, and publish workflow."
        )
    dataset = _load_dataset(args.normalized_dir)
    packages = build_private_source_packages(dataset)
    authoring_inputs = build_summary_authoring_inputs(packages)
    pilot = select_representative_pilot(packages)

    reviewed_summaries: list[dict[str, Any]] | None = None
    if args.summaries_from:
        supplied_rows = [
            row
            for path in args.summaries_from
            for row in _load_json(path)
        ]
        reviewed_summaries = validate_frozen_summaries(
            supplied_rows, dataset["episodes"]
        )

    provenance: dict[str, Any] = {
        "status": (
            "frozen-reviewed-grounded-synthesis"
            if reviewed_summaries is not None
            else "private-authoring-pilot"
        ),
        "apiModelDiscovery": "unavailable-in-execution-environment",
        "apiPilotEpisodes": 0,
        "apiSummaryGenerationEpisodes": 0,
        "additionalApiCostUsd": 0,
        "rejectedPilotMethod": "deterministic-grounded-extractive-synthesis-v1",
        "rejectedPilotReason": (
            "The private extractive pilot did not meet the synthesis and "
            "source-paraphrase quality gate and was not published."
        ),
        "pilotEpisodeCount": len(pilot),
        "sourcePackageCount": len(packages),
        "ordinaryWebsiteBuildCallsApi": False,
        "publicSummariesAreFrozen": reviewed_summaries is not None,
    }
    if reviewed_summaries is not None:
        provenance["acceptedGenerationMethods"] = sorted(
            {row["summaryMethod"] for row in reviewed_summaries}
        )
        provenance["acceptedSummaryCount"] = len(reviewed_summaries)

    write_serialized_files(
        args.private_dir,
        serialize_payloads(
            {
                "episode_source_packages.json": packages,
                "summary_authoring_inputs.json": authoring_inputs,
                "summary_pilot.json": pilot,
                "summary_generation_provenance.json": provenance,
            }
        ),
    )

    if args.pilot_only:
        return {
            "packages": len(packages),
            "pilot": len(pilot),
            "summaries": 0,
            "relationships": 0,
            "relationshipCounts": {},
        }

    if reviewed_summaries is None:
        raise ValueError(
            "This legacy command only prepares private structured-item pilots. "
            "Use --pilot-only here, and use scripts/build_transcript_summaries.py "
            "for transcript-summary publication."
        )
    summaries = reviewed_summaries
    relationships = episode_relationship_payload(dataset)

    write_serialized_files(
        args.public_dir,
        serialize_payloads(
            {
                "episode_summaries.json": summaries,
                "episode_relationships.json": relationships,
            }
        ),
    )
    return {
        "packages": len(packages),
        "pilot": len(pilot),
        "summaries": len(summaries),
        "relationships": len(relationships),
        "relationshipCounts": _relationship_counts(relationships),
        "summaryWords": {
            "minimum": min(len(row["summary"].split()) for row in summaries),
            "maximum": max(len(row["summary"].split()) for row in summaries),
        },
    }


def _parser() -> argparse.ArgumentParser:
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(
        description="Build grounded Cognitive Security episode products."
    )
    parser.add_argument(
        "--normalized-dir",
        type=Path,
        default=repo_root / "analysis" / "cognitive-security" / "normalized",
        help="Ignored normalized v1.1 historical release directory.",
    )
    parser.add_argument(
        "--private-dir",
        type=Path,
        default=repo_root / "analysis" / "cognitive-security" / "eod-explorer",
        help="Ignored private source-package and QA directory.",
    )
    parser.add_argument(
        "--public-dir",
        type=Path,
        default=repo_root / "data" / "cognitive-security",
        help="Public data directory.",
    )
    parser.add_argument(
        "--summaries-from",
        type=Path,
        nargs="+",
        help=(
            "Retired compatibility option. Transcript-summary publication is "
            "QA-gated by scripts/build_transcript_summaries.py and is rejected here."
        ),
    )
    parser.add_argument(
        "--pilot-only",
        action="store_true",
        help="Write only ignored source packages and the representative pilot.",
    )
    return parser


def main() -> int:
    args = _parser().parse_args()
    result = build(args)
    print("Grounded episode authoring build succeeded.")
    print(f"  Private source packages: {result['packages']}")
    print(f"  Representative pilot episodes: {result['pilot']}")
    if not args.pilot_only:
        print(f"  Frozen public summaries: {result['summaries']}")
        print(f"  Public episode relationships: {result['relationships']}")
        for relationship_type, count in result["relationshipCounts"].items():
            print(f"    {relationship_type}: {count}")
        print(
            "  Summary word range: "
            f"{result['summaryWords']['minimum']}-{result['summaryWords']['maximum']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
