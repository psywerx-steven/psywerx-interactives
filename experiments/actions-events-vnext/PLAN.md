# Actions & Events proposal execution plan

Status: experimental proposal; every architecture decision PENDING.

1. Freeze repository and protected-file hashes; inspect governed contracts and prior work. Accept when actual HEAD, remote, baseline difference and applicable instructions are recorded.
2. Compute read-only coverage for every Layer/Family/entity and separate semantic graphs. Accept when V3/native/candidate counts reconcile without projection duplication and every Family has a queue row.
3. Review primary architecture sources. Accept when proposal-only source register identifies access level and design claims with limitations.
4. Define identity/occurrence/effect/evidence model, two-pass workflow, decisions and five reusable prompts. Accept when every requested origin/effect class and safeguard is covered.
5. Build isolated Python prototype, draft JSON Schemas and synthetic tests. Accept when Family inventory writes only under an explicit experimental output path, reports are deterministic, and dry runs never activate real records.
6. Independently critique, validate protected hashes and run existing regressions in an isolated copy. Accept when requirements coverage and actual results are recorded.
7. Commit proposal. Inspect remote workflow and Pages triggers before any push/draft PR; otherwise retain local commit. Never merge or deploy.

Validation commands (from repository root):

```powershell
python experiments/actions-events-vnext/prototype.py inventory --family BIO-F01 --output experiments/actions-events-vnext/reports
python experiments/actions-events-vnext/prototype.py synthetic-demo --output experiments/actions-events-vnext/reports
python -m unittest discover -s experiments/actions-events-vnext -p 'test_*.py'
python experiments/actions-events-vnext/validate.py
python experiments/actions-events-vnext/prototype.py verify-protected
git diff --check
```

Existing regression commands run only in the isolated copy: five migration/V1/BIO-F01 unittest modules, scenario-service `npm test`, Python compilation and JavaScript parsing.
