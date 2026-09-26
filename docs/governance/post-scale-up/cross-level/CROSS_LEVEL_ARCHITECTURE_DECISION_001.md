# Cross-level exposure architecture decision 001

**Decision ID:** `GOV-CROSS-LEVEL-EXPOSURE-001-2026-09-26`

**Decision packet:** `DP-PSG-002`

**Root issue:** `ROOT-CROSS-LEVEL-EXPOSURE-001`

**Work package:** `WP-PSG-002`

**Decision date:** 2026-09-26

**Outcome:** `APPROVED_BOUNDED_A_PLUS_B_PLUS_C_DIRECTION`

## Human-approved direction

The human governor approves the bounded A+B+C architecture direction established by the Stage C decision test:

- use an immutable, versioned `CrossLevelExposureMapping` as a separate noncausal scientific routing and eligibility contract;
- require each governed cross-level Relationship to reference an exact mapping ID and version with claim-specific qualifiers;
- reference existing Driver or HappeningType intermediates only when they are scientifically substantive parts of the pathway;
- explicitly distinguish source state, implementation or transmission, eligibility or membership, actual exposure, optional perceived exposure, temporal ordering and target response;
- mapping existence conveys no causal evidence, lifecycle status, weight, propagation or execution authority.

## Authorized scope

This decision authorizes the architecture direction and non-production implementation prototyping, including isolated schema and validator prototypes, test-only mapping and eligibility experiments, and read-only migration and consumer-impact planning.

## Explicit boundary

This decision does **not** authorize Relationship reclassification or mutation, cross-level execution or activation, new Drivers, new HappeningTypes, Network State changes, RDS causal-source eligibility, production migration, ontology mutation, source registration, lifecycle change or activation.

## Materialization outcome

No production object is materialized or changed. `WP-PSG-002` Stage D is complete only for the bounded architecture direction. Production implementation, migration, Relationship re-adjudication, execution eligibility and activation remain separate governed stages.
