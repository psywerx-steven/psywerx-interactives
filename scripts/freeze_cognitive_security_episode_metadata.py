"""Freeze cached official publisher records into a public metadata overlay."""

from __future__ import annotations

import argparse
from pathlib import Path

from cognitive_security.discovery import freeze_episode_metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--core-dir", type=Path, default=Path("data/cognitive-security"))
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument(
        "--public-output",
        type=Path,
        default=Path("data/cognitive-security-discovery/episode_metadata.json"),
    )
    parser.add_argument("--private-audit-output", type=Path, required=True)
    parser.add_argument("--retrieved-at", required=True)
    args = parser.parse_args()
    audit = freeze_episode_metadata(
        core_dir=args.core_dir,
        cache_dir=args.cache_dir,
        public_output=args.public_output,
        private_audit_output=args.private_audit_output,
        retrieved_at=args.retrieved_at,
    )
    print(
        "Frozen episode metadata: "
        f"{audit['matchedReleaseCount']} matched, "
        f"{audit['unmatchedReleaseCount']} unresolved."
    )


if __name__ == "__main__":
    main()
