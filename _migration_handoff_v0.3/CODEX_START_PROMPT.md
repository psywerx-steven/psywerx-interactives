# Codex Start Prompt

Continue the PSYWERX Driver Ontology migration from the current repository state. This is an IMPLEMENTATION/PREVIEW task, not a new ontology-research task.

Read all files in this handoff bundle first, especially `SECONDARY_BOUNDARY_AUDIT_ADDENDUM.md`, then inspect the repository source-of-truth, build scripts, schemas, IDs, validation, and tests.

Use a new migration-preview branch. Do not merge or deploy. Preserve existing IDs; allocate new IDs deterministically; do not manually edit generated JSON; do not invent missing scientific definitions. Flag unresolved items as `BLOCKED_NEEDS_GOVERNANCE_INPUT`.

Target: **770 Drivers + 41 RDS = 811 canonical entities**.

Deliver: repository assessment, baseline commit/hashes, deterministic new-ID table, final machine-readable migration manifest, preview artifacts, before/after counts, relationship migration counts, alias/crosswalk summary, validation results, two clean-build hashes, unresolved questions, and exact diff/commit plan. Stop before commit/merge/deployment for approval.


## Positive-control requirement
Do not automatically retype any additional Driver based only on words such as ratio, relative, index, score, aggregate, average, proportion, distribution, or capacity. Apply the five-part anti-overreach test in `RDS_POSITIVE_CONTROL_CALIBRATION.md`; otherwise flag `BLOCKED_NEEDS_GOVERNANCE_INPUT`.
