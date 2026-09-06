"""Validate committed AE infrastructure in an isolated clone, never regenerate the user's data."""
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import unquote

import audit_family as af


def local_links(root):
    docs = [root / "docs/ACTIONS_EVENTS_V1.md", *root.glob("docs/governance/ACTIONS_EVENTS*.md"),
            root / "data/actions-events-v1/README.md", root / "data/candidates/actions-events-v1/README.md",
            root / "experiments/actions-events-vnext/MORNING_BRIEF.md",
            root / "experiments/actions-events-vnext/OVERNIGHT_EXECUTION.md",
            root / "reports/actions-events-v1/IMPLEMENTATION_REVIEW.md"]
    broken = []
    for doc in docs:
        for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", doc.read_text(encoding="utf-8")):
            link = unquote(link.strip("<>").split("#", 1)[0])
            if link and not re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", link) and not (doc.parent / link).exists():
                broken.append(f"{doc.relative_to(root)}: {link}")
    return {"name": "Markdown local-file links", "passed": not broken, "filesChecked": len(docs), "broken": broken}


def run():
    started = time.perf_counter()
    results = []
    original = af.scientific_integrity()
    head = af.git("rev-parse", "HEAD")

    def command(name, args, cwd):
        tick = time.perf_counter()
        proc = subprocess.run([str(a) for a in args], cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = proc.stdout.decode("utf-8", errors="replace")
        results.append({"name": name, "command": [str(a).replace(str(cwd), "<checkout>") for a in args],
                        "passed": proc.returncode == 0, "exitCode": proc.returncode,
                        "seconds": round(time.perf_counter() - tick, 3), "output": output})
        print(f"{name}: {'PASS' if proc.returncode == 0 else 'FAIL'}", flush=True)
        return proc.returncode == 0

    scratch = af.output_dir(af.ROOT / "reports/actions-events-v1/_scratch")
    with tempfile.TemporaryDirectory(prefix="validation-", dir=scratch) as directory:
        checkout = Path(directory) / "checkout"
        if not command("Isolated committed implementation clone", ["git", "clone", "--no-hardlinks", "--quiet", str(af.ROOT), str(checkout)], af.ROOT):
            raise RuntimeError("Cannot create isolated regression checkout")
        if not command("Freeze tested commit", ["git", "checkout", "--quiet", head], checkout):
            raise RuntimeError("Cannot freeze tested commit")
        scientific = af.git("ls-tree", "-r", "--name-only", af.BASELINE, "--", "data").splitlines()
        hashes = {n: hashlib.sha256((checkout/n).read_bytes()).hexdigest() for n in scientific}
        for module in ("test_actions_events_v1.py", "test_audit_family.py", "test_migration_v0_3.py",
                       "test_relationship_intervention_v1.py", "test_bio_f01_pilot.py",
                       "test_bio_f01_governance_001.py", "test_bio_f01_activation_001.py"):
            command(module, [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", module], checkout)
        command("Production AE/RI schemas, references, lifecycle and bridge", [sys.executable, "scripts/actions_events_v1.py", "--validate-repository"], checkout)
        command("Eight-Layer synthetic structural pilot", [sys.executable, "scripts/actions_events_synthetic.py"], checkout)
        command("Deterministic migration regeneration", [sys.executable, "scripts/build_migration_preview_v0_3.py"], checkout)
        command("Deterministic BIO materialization", [sys.executable, "scripts/materialize_bio_f01_governance_001.py"], checkout)
        changed = [n for n in scientific if hashlib.sha256((checkout/n).read_bytes()).hexdigest() != hashes[n]]
        results.append({"name": "Isolated scientific byte identity after regeneration", "passed": not changed, "filesCompared": len(hashes), "changed": changed})
        command("No tracked mutation from regeneration/tests", ["git", "diff", "--exit-code"], checkout)
        npm = shutil.which("npm.cmd") or shutil.which("npm")
        if npm and command("Isolated scenario dependencies", [npm, "install", "--ignore-scripts", "--no-audit", "--no-fund", "--no-package-lock"], checkout/"scenario-service"):
            command("Scenario contracts and exact 811-entity sweep", [npm, "test"], checkout/"scenario-service")
        elif not npm:
            results.append({"name": "Scenario dependency tool", "passed": False, "reason": "npm not available"})
        command("Python compilation", [sys.executable, "-m", "compileall", "-q", "scripts", "tests"], checkout)
        scripts = subprocess.check_output(["git", "ls-files", "--", "*.js", "*.mjs", "*.cjs"], cwd=checkout).decode().splitlines()
        failed = [n for n in scripts if subprocess.run(["node", "--check", n], cwd=checkout, capture_output=True).returncode]
        results.append({"name": "JavaScript parsing", "passed": not failed, "filesChecked": len(scripts), "failed": failed})
        results.append(local_links(checkout))
    current = af.scientific_integrity()
    results.append({"name": "Protected original scientific data", "passed": current["passed"] and original["rawCurrentSha256"] == current["rawCurrentSha256"],
                    "comparison": current, "rawBeforeEqualsAfter": original["rawCurrentSha256"] == current["rawCurrentSha256"]})
    command("Git diff check", ["git", "diff", "--check"], af.ROOT)
    result = {"testedCommit": head, "baseline": af.BASELINE, "allPassed": all(r["passed"] for r in results),
              "seconds": round(time.perf_counter()-started, 3), "results": results,
              "notes": ["Existing regeneration tests ran only in an isolated clone.",
                        "This report measures local results; it makes no CI or scientific approval claim."]}
    af.write_json(af.output_dir(af.ROOT/"reports/actions-events-v1/validation"), "LOCAL_VALIDATION.json", result)
    return 0 if result["allPassed"] else 1


if __name__ == "__main__":
    raise SystemExit(run())
