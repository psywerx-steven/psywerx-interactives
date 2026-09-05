# Governed Driver-to-RDS Migration v0.3

The authoritative specification is `_migration_handoff_v0.3/`. The migration is
implemented by `scripts/build_migration_preview_v0_3.py` and intentionally
refuses to run unless the seed contains the exact approved 34-ID retype set and
the target counts are 770 Drivers, 41 relational/derived states, and 811 total
entities.

Run the ordinary source builds first, ending with the Relationship v2 baseline,
then run:

```powershell
py scripts\build_migration_preview_v0_3.py
py -m unittest discover -s tests -p "test_migration_v0_3.py"
```

The generator writes the canonical partition, union, generic relationships,
typed aliases, crosswalks, and a hash-bearing migration manifest atomically.
Open questions are emitted in `data/migration-manifest.json` with
`BLOCKED_NEEDS_GOVERNANCE_INPUT`; the generator does not adjudicate them.
