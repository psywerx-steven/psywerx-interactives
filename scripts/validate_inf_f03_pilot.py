"""Run the committed pilot and existing regeneration regressions in isolation."""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import audit_family as af
import build_inf_f03_pilot as pilot


def run():
    before = pilot.protected()
    head = af.git("rev-parse", "HEAD")
    results = []

    def command(name, args, cwd):
        proc = subprocess.run(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        results.append({"name": name, "passed": proc.returncode == 0,
                        "output": proc.stdout.decode("utf-8", errors="replace")})
        print(name + (": PASS" if proc.returncode == 0 else ": FAIL"), flush=True)
        return proc.returncode == 0

    # Keep nested legacy-validation clone paths below Windows path limits.
    with tempfile.TemporaryDirectory(prefix="inf-f03-") as directory:
        clone = Path(directory) / "checkout"
        subprocess.run(["git", "clone", "--quiet", "--no-hardlinks", str(af.ROOT), str(clone)], check=True)
        subprocess.run(["git", "checkout", "--quiet", head], cwd=clone, check=True)
        command("Existing regressions and isolated deterministic baseline regeneration",
                [sys.executable, "scripts/validate_actions_events_v1.py"], clone)
        existing = json.loads((clone / "reports/actions-events-v1/validation/LOCAL_VALIDATION.json").read_text(encoding="utf-8"))
        results.append({"name": "Existing report belongs to tested pilot commit",
                        "passed": existing.get("testedCommit") == head})
        command("INF-F03 candidate schemas, evidence, lifecycle, RDS, deduplication, links, isolation and determinism",
                [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_inf_f03_pilot.py"], clone)
        # Actual on-disk generation as well as the test's in-memory comparison.
        command("Deterministic pilot regeneration", [sys.executable, "scripts/build_inf_f03_pilot.py"], clone)
        command("Pilot generated documents and candidates unchanged",
                ["git", "diff", "--exit-code", "--", "data/candidates/actions-events-v1/INF-F03", "docs/governance/pilots/INF-F03"], clone)
        command("Diff whitespace", ["git", "diff", "--check"], clone)
    after = pilot.protected()
    results.append({"name": "Original checkout protected bytes unchanged",
                    "passed": before == after and pilot.protected_checkpoint_ok(after),
                    "filesCompared": len(after)})
    report = {"auditId": pilot.AUDIT, "testedCommit": head, "baseline": pilot.R["baseline"],
              "allPassed": all(r["passed"] for r in results) and existing["allPassed"],
              "results": results, "existingValidation": existing,
              "protectedComparisonSha256": hashlib.sha256(pilot.encode(after).encode()).hexdigest(),
              "protectedBefore": before, "protectedAfter": after,
              "notes": ["The exact authorized governance checkpoint is materialized; activation remains withheld.",
                        "Only the three selectively approved sources are canonically registered.",
                        "Regeneration ran only in disposable isolated clones.", "CI is reported separately from these local results."]}
    pilot.emit(pilot.DOCS / "INF_F03_LOCAL_VALIDATION.json", report)
    return 0 if report["allPassed"] else 1


if __name__ == "__main__":
    raise SystemExit(run())
