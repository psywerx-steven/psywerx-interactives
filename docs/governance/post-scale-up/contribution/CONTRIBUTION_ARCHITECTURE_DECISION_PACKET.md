# DP-PSG-004 — contribution identity and double-count control

> **READ-ONLY / NON-PRODUCTION PRE-GOVERNANCE DECISION TEST**

Baseline: `24a406468180a35af5beb74df427053cc1536090`. No production mutation or governance decision is made.

## Recommended architecture

Adopt the bounded A+B+C direction: immutable exact-version external ContributionGroups only for explicitly adjudicated cross-class identity; preserve class-native controls; require centralized fail-closed resolution for future causal consumers. Keep unresolved constituent/aggregate routes blocked.

Rejected: A without enforcement, B as distributed lineage-only logic, and C as a permanent fragmented architecture. No production migration is proposed in this decision.

## Known unresolved science

`INS-039`, `INS-103`, the ten Social RDS sources, total-effect/local-link reconciliation, and any aggregate independence remain unadjudicated. WP-PSG-005 receives structured inputs only and is not started.

## Exact bounded approval statement

Approve the bounded WP-PSG-004 A+B+C architecture direction tested in DP-PSG-004: use immutable, exact-version ContributionGroups only for explicitly adjudicated cross-class contribution identity; retain existing class-specific contribution and recalculation controls; and require one centralized fail-closed resolution gate before any future graph, simulation, summation, or effect-attribution consumer. Group membership must bind exact record IDs, versions and hashes and align causal exposure/change, target change, contrast, unit of analysis, time scope and pathway scope. Require explicit representation selection for mutually exclusive representations, preserve derivation/state/exposure/evidence records as noncausal, and keep constituent/aggregate overlap blocked pending WP-PSG-005. This authorizes architecture direction and optional non-production prototyping only; it does not authorize production ContributionGroups, record migration, Relationship or EffectAssertion mutation, RDS causal-source use, graph behavior change, lifecycle change, activation, effect magnitude, polarity, or WP-PSG-005 adjudication.
