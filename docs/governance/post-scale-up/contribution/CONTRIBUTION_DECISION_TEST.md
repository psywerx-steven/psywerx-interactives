# WP-PSG-004 contribution identity decision test

> **READ-ONLY / NON-PRODUCTION PRE-GOVERNANCE DECISION TEST**

Baseline: `24a406468180a35af5beb74df427053cc1536090`. No production mutation or governance decision is made.

## Finding

The tests support a bounded A+B+C design. An immutable external `ContributionGroup` supplies explicit cross-class identity, existing class-native fields remain authoritative within their subsystems, and a central resolver enforces count-once, select-one, derivation-only, and blocked-pending-independence policies. Groups are created only after explicit scientific identity adjudication; shared sources, targets, interventions, mechanisms, or graph paths never infer membership.

The numeric control rejected naive `0.2 + 0.2 = 0.4` for the Relationship/EA duplicate and returned one `0.2`; adding an independent `0.1` returned `0.3`. State delta plus metric recalculation returned zero causal contribution. An unresolved constituent/aggregate pair failed closed.

## Positive control

`REL-V1-PSY-LAYER-001` and `EA-V1-PSY-LAYER-001` represent `CONTRIB-PSY-LAYER-REPETITION-001`. They remain distinct record classes and inactive. Exact external membership can bind the Relationship without editing it, while the EA's native contribution metadata remains intact.

## Aggregate and state cases

`INS-039`/`REL-INS-017` and `INS-103`/`REL-INS-036` have unresolved constituent overlap and remain `BLOCKED_PENDING_CAUSAL_INDEPENDENCE`. The ten Social RDS sources under `ASTRA-SOC-LAYER-001` remain unknown until exact routes exist. H12/H20 and `DER-V1-SOC-F07-001` are `NONCAUSAL_STATE_DERIVATION`; recalculation never becomes an empirical contribution.

## Safeguards

- Exact immutable group version and member record ID/version/hash.
- No first/latest/active/best automatic selection.
- No group inference from evidence, target, intervention, mechanism, source, or graph reachability.
- Contribution group has no causal authority, evidence, weight, polarity, activation, propagation, or scientific lifecycle.
- Total-effect/local-link and interaction semantics require explicit scientific relations.
- External consumers must accept a centrally resolved set or fail closed.

## Recommendation

`BOUNDED_A_PLUS_B_PLUS_C_EXPLICIT_CROSS_CLASS_GROUPS_NATIVE_CONTROLS_CENTRAL_FAIL_CLOSED_ENFORCEMENT`. Advisory only; human architecture governance remains required.
