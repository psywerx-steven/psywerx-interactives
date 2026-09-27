# DP-PSG-003 — Network State architecture decision packet

**HUMAN ARCHITECTURE GOVERNANCE REQUIRED**

## Current problem

State operations, deterministic metric changes and empirical causal effects must remain separate. Current tests show the production V1 delta already supplies the bounded transition representation.

## Recommendation

Choose bounded **A+C**. Use current typed `ScenarioStateDelta`; use `ScenarioOperationReference` only for non-effect scientific-operation identity; recalculate through exact derivation/profile semantics; leave unsupported transitions blocked. Reject B for current scope as duplicate architecture.

## Cross-level handoff

| Relationship | Proposition | Metric/state finding | Exact Network State input | Later work |
|---|---|---|---|---|
| `REL-SOC-017` | `SOC-024` → `SOC-026` | Network-derived RDS is a potential-provider-pool summary, not actual support exposure. | stateId/revision/contentHash, boundaryId/revision, window, active node set, tie definition, exact SOC-024 profile/binding | WP-PSG-002, WP-PSG-005 |
| `REL-SOC-035` | `SOC-053` → `SOC-061` | Local clustering describes neighbor connectivity; actual reinforcing exposures are separate. | stateId/revision/contentHash, boundaryId/revision, window, ego node, neighbor tie definition, exact SOC-053 profile/binding | WP-PSG-002, WP-PSG-005 |
| `REL-TEC-050` | `TEC-029` → `SOC-057` | A technological affordance does not itself establish a changed network or segregation metric. | stateId/revision/contentHash, boundaryId/revision, window, group labels, tie/opportunity definition, exact SOC-057 profile/binding, transition or observation reference | WP-PSG-001, WP-PSG-002, WP-PSG-005 |

## Safeguards

- modeled delta is not an occurrence or empirical effect;
- metric change is not a Relationship, EffectAssertion or causal contribution;
- direct RDS EffectAssertions remain prohibited;
- RDS causal-source eligibility remains false pending WP-PSG-005;
- alternate state-delta/metric/causal representations go to WP-PSG-004;
- historical states remain immutable and rollback means selecting/replaying a branch.

## Exact bounded approval statement

Approve the bounded WP-PSG-003 A+C architecture direction tested in DP-PSG-003: retain the existing immutable typed ScenarioStateDelta, ScenarioOperationReference, state receipt and RelationalState lineage as the sole bounded representation for supported stipulated node, tie, membership, boundary, opportunity and access changes; use exact governed RDS computation profiles or preserved legacy derivations only for deterministic recalculation; and keep unsupported or empirically estimated transitions blocked. Do not create a separate NetworkStateTransition class unless a future governed requirement demonstrates a distinct scientific concept. This authorizes architecture direction and optional non-production prototyping only; it does not authorize production Network State schema or state migration, empirical causal claims, Relationships, EffectAssertions, HappeningTypes, cross-level execution, RDS causal-source eligibility, lifecycle change, activation, or production state mutation.
