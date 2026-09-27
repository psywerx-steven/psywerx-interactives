# Network State architecture decision 001

**Decision ID:** `GOV-NETWORK-STATE-ARCHITECTURE-001-2026-09-26`

**Decision packet:** `DP-PSG-003`

**Root issue:** `ROOT-NETWORK-STATE-TRANSITION-001`

**Work package:** `WP-PSG-003`

**Decision date:** 2026-09-26

**Outcome:** `APPROVED_BOUNDED_A_PLUS_C_DIRECTION`

## Human-approved direction

The human governor approves the bounded A+C architecture direction established by the Stage C decision test:

- retain the existing immutable typed `ScenarioStateDelta`, `ScenarioOperationReference`, state receipt and `RelationalState` lineage as the sole bounded representation for supported stipulated node, tie, membership, boundary, opportunity and access changes;
- use exact governed RDS computation profiles or preserved legacy derivations only for deterministic metric recalculation;
- keep unsupported or empirically estimated transitions blocked;
- do not create a separate `NetworkStateTransition` class unless a future governed requirement demonstrates a distinct scientific concept.

## Authorized scope

This decision authorizes the architecture direction and optional non-production implementation prototyping, including isolated contract/schema experiments, validator prototypes, synthetic state-transition tests, and read-only migration or consumer-impact planning.

## Explicit boundary

This decision does **not** authorize production Network State schema or state migration, empirical causal claims, Relationships, EffectAssertions, HappeningTypes, cross-level execution, RDS causal-source eligibility, lifecycle change, activation or production state mutation.

## Materialization outcome

No production object is materialized or changed. `WP-PSG-003` Stage D is complete only for the bounded architecture direction. Production implementation, migration/revalidation, cross-level execution, aggregate causal-source adjudication and scientific re-adjudication remain separate governed stages.

`HYP-SOC-F07-H12`, `HYP-SOC-F07-H20` and `ASTRA-SOC-LAYER-003` retain their current production governance state. `DER-V1-SOC-F07-001` remains governed, inactive and recalculation-only.
