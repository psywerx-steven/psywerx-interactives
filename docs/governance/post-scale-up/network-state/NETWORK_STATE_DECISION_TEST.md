# Network State transition decision test

**READ-ONLY ARCHITECTURE DECISION TEST — NO PRODUCTION SCIENCE, SCHEMA, LIFECYCLE OR ACTIVATION CHANGE**

`WP-PSG-003` / `DP-PSG-003` tested production Network State V1 at baseline `18be50222d75fea3f27ecfd27aed3eee05409ecd` with fictional `SYN-*` states. The test changed no production state or scientific record.

## Finding

The existing `ScenarioStateDelta` is already the bounded state-transition record for supported modeled operations. It contains an immutable identity, exact before-state reference, ordered typed operations, effective time, provenance, scenario alignment, and deterministic receipt pointing to the resulting `RelationalState`. `ScenarioOperationReference` optionally links a scientific operation identity while stating `REFERENCES_STIPULATED_OPERATION_NOT_EFFECT`.

The advisory recommendation is **A+C**: use the existing typed delta for supported stipulated changes and keep unsupported/empirically estimated transitions blocked. A second `NetworkStateTransition` class would duplicate current semantics.

## H12 — rewiring

The synthetic delta `SYN-DELTA-WP003-REWIRE` removes one tie and adds another. The state hash changes, parent lineage is retained, and node degree changes from `{"SYN-NODE-A": 2, "SYN-NODE-B": 2, "SYN-NODE-C": 3, "SYN-NODE-D": 1}` to `{"SYN-NODE-A": 2, "SYN-NODE-B": 1, "SYN-NODE-C": 3, "SYN-NODE-D": 2}`. The receipt preserves `causalContribution=false`, `empiricalEvidenceProduced=false`, and `ontologyRelationshipsEdited=0`. H12 is architecturally representable as state change plus recalculation; an empirical causal Driver→RDS claim is unnecessary and unsupported.

## H20 — node deactivation

`DEACTIVATE_NODE` removes the inactive node from the analytic boundary and retires its incident ties. Fragmentation changes from `0.0` to `0.6666666666666667`. This is deterministic recalculation from a stipulated state, not an EffectAssertion.

## Controls

- `CHANGE_BOUNDARY` is `ANALYTIC_BOUNDARY_ONLY`; it changes selection and metrics without claiming physical tie change.
- `CHANGE_MEMBERSHIP` changes group membership without creating/removing ties.
- contact opportunity and access changes do not create realized ties or exposure.
- an intensity-weight update makes binary-only metric calculation fail closed.
- observation-derived construction preserves observation reference, selection, missingness, assumptions, boundary and window.
- replay is exact and two branches retain the same parent without becoming observed futures.
- stale state, cross-scenario application and retired tie-ID reuse are rejected.

## Scientific firewalls

No Relationship, EffectAssertion, causal contribution, empirical evidence, ontology edit, RDS causal authorization, graph edge, lifecycle state or activation follows from a delta or recalculation.
