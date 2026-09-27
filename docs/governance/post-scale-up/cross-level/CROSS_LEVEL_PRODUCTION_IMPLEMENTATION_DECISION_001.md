# Cross-level production implementation decision 001

**Decision ID:** `GOV-CROSS-LEVEL-IMPLEMENTATION-001-2026-09-26`

**Decision packet:** `DP-PSG-002-IMPLEMENTATION`

**Architecture decision:** `GOV-CROSS-LEVEL-EXPOSURE-001-2026-09-26`

**Work package:** `WP-PSG-002`

**Decision date:** 2026-09-26

**Outcome:** `APPROVED_BOUNDED_PHASE_0_AND_SEPARATELY_GATED_REL_INS_040_SHADOW_PHASE_1`

## Authorized Phase 0

Install immutable exact-version `CrossLevelExposureMapping` and `CrossLevelExposureBinding` schemas, empty registries, fail-closed validators, provenance and fingerprint contracts, and a shadow eligibility service. Phase 0 must migrate zero Relationships and change neither graph construction nor simulation behavior.

## Separately gated Phase 1

Only after Phase 0 validation passes, materialize the mapping and binding for `REL-INS-040` alone in validation/shadow mode. Preserve the production Relationship unchanged. The mapping and binding confer no causal evidence, execution, lifecycle status, weight, propagation, graph inclusion, simulation behavior, or activation authority.

## Explicit boundary

The other 37 Relationships, all Relationship classifications, Drivers, HappeningTypes, Network State, RDS causal-source eligibility, ontology, sources, lifecycle states and activation remain unchanged and unauthorized.

## Current implementation state

`PHASE_1_REL_INS_040_COMPLETE_SHADOW_ONLY`. Phase 0 installed the additive architecture and passed protected-state, Linux, and Windows gates. Phase 1 then materialized only the authorized REL-INS-040 mapping/binding in validation/shadow mode. The production Relationship, graph, simulation, lifecycle, activation, and causal authority remain unchanged.
