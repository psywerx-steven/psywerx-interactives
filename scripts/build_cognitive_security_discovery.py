"""Build the frozen Cognitive Security presentation/discovery overlay."""

from __future__ import annotations

import argparse
from pathlib import Path

from cognitive_security.discovery import build_discovery_package


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--core-dir", type=Path, default=Path("data/cognitive-security"))
    parser.add_argument(
        "--output-dir", type=Path, default=Path("data/cognitive-security-discovery")
    )
    parser.add_argument("--calibration-output", type=Path)
    args = parser.parse_args()
    manifest = build_discovery_package(
        core_dir=args.core_dir,
        output_dir=args.output_dir,
        calibration_output=args.calibration_output,
    )
    counts = manifest["counts"]
    print(
        "Built Cognitive Security discovery overlay: "
        f"{counts['discoveryRecordCount']} releases, "
        f"{counts['contentUnitCount']} content units, "
        f"{counts['qualifiedTopicAssignmentCount']} qualified topic assignments."
    )


if __name__ == "__main__":
    main()
