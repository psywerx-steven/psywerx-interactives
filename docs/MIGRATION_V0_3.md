# Governed Driver-to-RDS Migration v0.3

**Specification authority:** `GOVERNED_MIGRATION_SPECIFICATION`

**Generated baseline authority:** `GOVERNED_MIGRATION_BASELINE`

**Governance decision:**
[Migration Baseline Adoption V0.3](governance/MIGRATION_BASELINE_ADOPTION_V0_3.md)

**Adopted history:** frozen baseline
`580d59c451765e9f4d65b517f538a495fa93bda5`; migration PR #9 head
`ad727cafbb3d970e269848662612c6f638c14cd1`; merge/effective baseline commit
`6cf34a029a9dc6e099628e86dfb9f42b53bd8d13`

The authoritative specification is `_migration_handoff_v0.3/`. The migration is
implemented by `scripts/build_migration_preview_v0_3.py` and intentionally
refuses to run unless the seed contains the exact approved 34-ID retype set and
the target counts are 770 Drivers, 41 relational/derived states, and 811 total
entities.

The generator's historical filename is retained for compatibility; its output
manifest is the adopted governed baseline, not a preview. Authority metadata is
generated from the protected seed and validated by tests.
The manifest's `previewCounts` key is likewise retained as a legacy compatibility
name; it reports governed baseline counts and does not indicate preview authority.

From any clean checkout containing baseline commit
`580d59c451765e9f4d65b517f538a495fa93bda5`, run:

```powershell
py scripts\build_migration_preview_v0_3.py
py -m unittest discover -s tests -p "test_migration_v0_3.py"
```

The generator reads the frozen baseline artifacts from Git rather than private
ignored workbooks. It writes the canonical partition, union, generic relationships,
typed aliases, crosswalks, and a hash-bearing migration manifest atomically.
Open questions are emitted in `data/migration-manifest.json` with
`BLOCKED_NEEDS_GOVERNANCE_INPUT`; the generator does not adjudicate them.
The seven adopted `openGovernanceItems` remain deferred and baseline adoption
does not change record-level scientific governance.
