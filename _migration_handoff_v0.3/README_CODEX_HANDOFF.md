# PSYWERX Codex Migration Handoff v0.2

## Recommended Codex mode
**Sol — High reasoning.** Escalate semantic conflicts or governance exceptions to Pro. Do not merge/deploy on the first run.

## Baseline
- 793 Drivers
- 105 Families
- 439 governed relationships

## Preview target
- **770 Drivers**
- **41 Relational & Derived States**
- **811 total canonical entities**

## Required canonical outputs
`drivers.json`, `relational-derived-states.json`, `entities.json`, `families.json`, `relationships.json`, `aliases.json`, `crosswalks.json`, `migration-manifest.json`.

## Operating rules
1. Inspect repository/source-of-truth first.
2. Create a preview branch from current `main`.
3. Record baseline commit and hashes.
4. Preserve all existing IDs through rename/retype.
5. Allocate new IDs deterministically.
6. Never manually edit generated JSON when the pipeline should generate it.
7. Flag unresolved science/governance as `BLOCKED_NEEDS_GOVERNANCE_INPUT`.
8. Generate and validate preview only.
9. Stop before merge/deploy.

See `migration_manifest_seed.json`, `MIGRATION_DECISIONS_SUMMARY.md`, `VALIDATION_CHECKLIST.md`, and `GOVERNANCE_SOURCE_INDEX.md`.

## v0.2 update
Adds the Secondary Driver↔RDS Boundary Audit and revises the preview count to **770 Drivers + 41 RDS = 811 entities**. See `SECONDARY_BOUNDARY_AUDIT_ADDENDUM.md`.


## RDS positive-control guardrail
Read `RDS_POSITIVE_CONTROL_CALIBRATION.md` before implementing any additional automatic Driver→RDS reclassification. Formula/ratio/index keywords are review flags only, not retype rules.
