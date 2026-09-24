# Cross-level and Network architecture options

**DESIGN ALTERNATIVES ONLY — NO ARCHITECTURE OR NETWORK STATE CHANGE**

## Cross-level exposure

`ASTRA-SOC-LAYER-002` and `ASTRA-INS-LAYER-003` share one root question: how a group, institution or network state becomes an exposure experienced by a person. The required chain distinguishes aggregate context, membership, eligibility, implementation, contact, actual exposure, perceived exposure and response.

- Option A: explicit typed `CrossLevelExposureMapping`.
- Option B: existing Driver/HappeningType bridge records for each transition.
- Option C: mandatory exposure-path metadata on cross-level Relationships.

## Network State

`DER-V1-SOC-F07-001` stays governed/inactive and recalculation-only. H12/H20 remain blocked. Network State owns node/tie/membership/boundary observations; Actions & Events own empirical operations; ScenarioStateDelta owns modeled state changes; derivations own deterministic metric recalculation; EffectAssertions require empirical causal evidence.

- Option A: typed ScenarioStateDelta operations within Network State V1.
- Option B: a separate governed NetworkStateTransition record.
- Option C: retain current architecture and leave unsupported operations blocked.

## Contribution identity

Relationship/EffectAssertion duplication, Driver/RDS constituent duplication, and recalculation/causal-edge duplication share a concern but are not assumed identical. `WP-PSG-004` tests whether contribution groups can safely span these classes, whether consumer mutual exclusion is sufficient, or whether class-specific controls must remain separate.
