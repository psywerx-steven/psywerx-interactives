# Contribution production implementation decision 001

**Decision ID:** `GOV-CONTRIBUTION-IMPLEMENTATION-001-2026-09-27`

**Decision packet:** `DP-PSG-004-IMPLEMENTATION`

**Architecture decision:** `GOV-CONTRIBUTION-IDENTITY-001-2026-09-27`

**Work package:** `WP-PSG-004`

**Decision date:** 2026-09-27

**Outcome:** `APPROVED_BOUNDED_PHASE_0_AND_SEPARATELY_GATED_REPETITION_SHADOW_PHASE_1`

## Authorized Phase 0

Install immutable exact-version ContributionGroup, ContributionResolutionRequest, and ContributionResolutionReceipt schemas; an empty registry; fail-closed validators; read-only native-control adapters; a central resolution service; and deterministic receipt/fingerprint contracts. Phase 0 contains zero groups, record migrations, Relationship or EffectAssertion changes, graph or simulation behavior changes, lifecycle or activation changes, and RDS causal-source changes.

## Separately gated Phase 1

Only after Phase 0 validation and merge, materialize `CONTRIB-PSY-LAYER-REPETITION-001@1.0.0` in `SHADOW_VALIDATION_ONLY` mode. It externally binds exact unchanged versions and hashes of `REL-V1-PSY-LAYER-001` and `EA-V1-PSY-LAYER-001`, requires explicit selection, and counts the contribution once.

## Explicit boundary

No aggregate RDS group or independence adjudication is authorized. Production scientific records, native contribution controls, graph and simulation behavior, magnitude, polarity, lifecycle, activation, and causal-source eligibility remain unchanged. `BLK-PSY-003` history is preserved; this implementation concerns planning alias `BLK-PSY-003::CONTRIBUTION-REPETITION`. WP-PSG-005 is not started.

## Current implementation state

PHASE_1_REPETITION_COMPLETE_SHADOW_ONLY. Phase 0 passed protected-state, Linux, and Windows gates before merge. Phase 1 then materialized only the authorized repetition ContributionGroup in shadow validation mode. Source records, aggregate cases, graph, simulation, lifecycle, activation, and causal-source eligibility remain unchanged.
