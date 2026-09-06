"""Run proposal checks and applicable production regressions in a temporary clone."""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote

import prototype as p


def run():
    results = []

    def command(name, args, cwd):
        completed = subprocess.run(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = completed.stdout.decode("utf-8", errors="replace")
        result = {"name": name, "command": args, "passed": completed.returncode == 0,
                  "exitCode": completed.returncode, "output": output}
        # Temporary path is not an enduring provenance ID.
        result["command"] = [str(a).replace(str(cwd), "<isolated-checkout>") for a in args]
        results.append(result)
        print(f"{name}: {'PASS' if result['passed'] else 'FAIL'}", flush=True)
        return result["passed"]

    before = p.protected_hashes()
    command("Prototype suites", [sys.executable, "-m", "unittest", "discover", "-s", str(p.HERE), "-p", "test_*.py"], p.ROOT)
    scratch = p.HERE / "_scratch"
    scratch.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="regression-", dir=scratch) as directory:
        checkout = Path(directory) / "checkout"
        if not command("Isolated local clone", ["git", "clone", "--no-hardlinks", "--quiet", str(p.ROOT), str(checkout)], p.ROOT):
            raise RuntimeError("Cannot create regression copy")
        command("Checkout frozen scientific baseline", ["git", "checkout", "--quiet", p.BASELINE], checkout)
        scientific = [name for name in p.git("ls-files").splitlines() if name.startswith("data/")]
        hashes = {name: hashlib.sha256((checkout / name).read_bytes()).hexdigest() for name in scientific}
        for module in ("test_migration_v0_3.py", "test_relationship_intervention_v1.py", "test_bio_f01_pilot.py", "test_bio_f01_governance_001.py", "test_bio_f01_activation_001.py"):
            command(module, [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", module], checkout)
        command("Production schema/meta/reference validation", [sys.executable, "scripts/relationship_intervention_v1.py", "--validate-repository"], checkout)
        command("Deterministic migration regeneration", [sys.executable, "scripts/build_migration_preview_v0_3.py"], checkout)
        command("Deterministic BIO materialization", [sys.executable, "scripts/materialize_bio_f01_governance_001.py"], checkout)
        changed = [name for name in scientific if hashlib.sha256((checkout / name).read_bytes()).hexdigest() != hashes[name]]
        results.append({"name": "Isolated scientific raw-byte regeneration", "passed": not changed,
                        "filesCompared": len(scientific), "changed": changed})
        command("Isolated tracked worktree remains unchanged", ["git", "diff", "--exit-code"], checkout)
        npm = shutil.which("npm.cmd") or shutil.which("npm")
        if not npm:
            results.append({"name": "Scenario dependencies", "passed": False, "reason": "npm unavailable"})
        elif command("Isolated scenario dependencies", [npm, "install", "--ignore-scripts", "--no-audit", "--no-fund", "--no-package-lock"], checkout / "scenario-service"):
            command("Scenario contract and 811-entity sweep", [npm, "test"], checkout / "scenario-service")
        command("Python compilation", [sys.executable, "-m", "compileall", "-q", "scripts", "tests"], checkout)
        js_files = subprocess.check_output(["git", "ls-files", "--", "*.js", "*.mjs", "*.cjs"], cwd=checkout).decode().splitlines()
        failures = []
        for name in js_files:
            completed = subprocess.run(["node", "--check", name], cwd=checkout, capture_output=True)
            if completed.returncode:
                failures.append(name)
        results.append({"name": "JavaScript parsing", "passed": not failures, "filesChecked": len(js_files), "failures": failures})
    broken = []
    docs = list(p.HERE.glob("*.md"))
    for doc in docs:
        for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", doc.read_text(encoding="utf-8")):
            link = unquote(link.strip("<>").split("#", 1)[0])
            # This runner writes its own report after validation, including on a first run.
            generated_report = (doc.parent / link).resolve() == (p.HERE / "TEST_RESULTS.json").resolve()
            if link and not generated_report and not re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", link) and not (doc.parent / link).exists():
                broken.append(f"{doc.name}: {link}")
    results.append({"name": "Proposal Markdown local links", "passed": not broken, "filesChecked": len(docs), "broken": broken})
    command("Git diff check", ["git", "diff", "--check"], p.ROOT)
    comparison = p.verify_protected()
    results.append({"name": "Protected original repository", **comparison,
                    "sameAsBeforeValidation": before == p.protected_hashes()})
    payload = {"status": "EXPERIMENTAL_NON_PRODUCTION", "results": results,
               "allPassed": all(r["passed"] for r in results),
               "regressionBaseline": p.BASELINE,
               "note": "Existing regeneration tests ran in a temporary local clone. No production tests or dependencies modified."}
    p.write_json(p.HERE, "TEST_RESULTS.json", payload)
    return 0 if payload["allPassed"] else 1


if __name__ == "__main__":
    raise SystemExit(run())
