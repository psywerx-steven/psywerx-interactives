# RDS contract architecture decision 001

**Decision ID:** `GOV-RDS-CONTRACT-001-2026-09-25`

**Decision packet:** `DP-PSG-001`

**Work package:** `WP-PSG-001`

**Decision date:** 2026-09-25

**Outcome:** `APPROVED_BOUNDED_OPTION_B_PLUS_C_DIRECTION`

## Human-approved direction

The human governor approves the bounded Option B+C RDS architecture direction established by the Stage C decision test:

- typed, named, immutable-version computation profiles;
- explicit versioned application bindings;
- valid RDS constructs remain non-executable when no eligible governed profile and complete binding exist;
- exact profile and binding versions are mandatory, with no silent default, first, or latest resolution;
- existing governed derivation IDs and lineage are preserved additively;
- definition/derivation eligibility remains separate from causal-source eligibility;
- any causal-source use requires separate `WP-PSG-005` governance and defaults to ineligible.

## Authorized scope

This decision authorizes architecture design and non-production implementation prototyping: schema experiments, validator prototypes, test-only profile/binding execution, and migration dry-run planning.

## Explicit boundary

This decision does **not** authorize production RDS migration, production RDS or validator mutation, causal-source use, Relationship or EffectAssertion mutation, lifecycle change, activation, or source registration. Production implementation remains `NOT_AUTHORIZED_NOT_STARTED`.

## Materialization outcome

No production record is materialized or changed. The current safe state of every RDS and dependent blocker remains intact. Stage D is complete only for the bounded architecture direction; later production implementation, migration/revalidation, and scientific re-adjudication remain separate stages.
