# RDS contract decision test

**Test:** `WP-PSG-001-STAGE-C-20260924-001`

**Decision packet:** `DP-PSG-001`

**Root issue:** `ROOT-RDS-DEFINITION-DERIVATION-001`
**Status:** advisory Stage C design validation; no human architecture decision taken

## Scope and gate separation

This test evaluates when an RDS is exactly defined and executable. It does not decide whether the RDS may act as an independent causal source. A governed computation profile passes Gate 1 only. Gate 2 remains `WP-PSG-005`; it requires separate scientific governance.

## Real-record test set

| RDS | Layer | Classification | Test role | Portable governed profile |
| --- | --- | --- | --- | --- |
| RDS-0006 | Social | DETERMINISTIC_METRIC, CONTEXT_SPECIFIC_PROFILE | POSITIVE_CONTROL_EXACT_GOVERNED_CALCULATION | yes |
| BIO-003 | Biological | COMPOSITE_SCORE, CONTEXT_SPECIFIC_PROFILE | BIOLOGICAL_ALIGNMENT_COMPOSITE | no |
| CUL-088 | Cultural | DISTANCE_METRIC, CONTEXT_SPECIFIC_PROFILE, NARRATIVE_OR_UNDERDEFINED | MULTI_VARIANT_DISTANCE_COUNTEREXAMPLE | no |
| INS-039 | Institutional / Structural | RATIO, AGGREGATE_STATISTIC, NARRATIVE_OR_UNDERDEFINED | INSTITUTIONAL_RATIO_AGGREGATE | no |
| INS-103 | Institutional / Structural | RATIO, AGGREGATE_STATISTIC, NARRATIVE_OR_UNDERDEFINED | INSTITUTIONAL_RATIO_AGGREGATE | no |
| INF-010 | Informational | RATIO, RULE_BASED_DERIVATION, CONTEXT_SPECIFIC_PROFILE | INFORMATIONAL_REQUIREMENT_SET_RATIO | no |
| PSY-078 | Psychological | DETERMINISTIC_INDEX, RULE_BASED_DERIVATION, CONTEXT_SPECIFIC_PROFILE | PSYCHOLOGICAL_DIFFERENCE_RULE | no |

`BLK-PSY-001` does not identify `PSY-078` as its affected record. The prototype therefore uses `PSY-078` only as a real difference-rule exemplar and retains the feature/dimension blocker as a separate boundary counterexample.

## Experimental result

The prototype ran 19 cases: 5 positive/safe-positive cases and 14 rejection cases. All expected outcomes were observed. A four-node star produced degree centralization `1.0` only when the exact `DER-V1-SOC-F07-001` profile and binding were requested.

Option A works for one exact deterministic calculation but fails as a universal contract. Option B expresses exact versions and context bindings but is unsafe without an explicit zero-profile state. Option C preserves underdefined constructs safely but supplies no execution architecture. The bounded B+C hybrid passed all exemplars: named/versioned profiles plus exact bindings for execution, and non-executable-by-default semantics when no eligible governed profile exists.

## Minimum contract

Universal fields are: rdsId, definitionVersion, derivationProfileId, derivationProfileVersion, profileType, inputContract, inputDefinitionVersions, inputDefinitionHashes, minimumInputRequirements, constituentMapping, outputScale, outputInterpretation, scopeLimitations, derivationEntailed, causalSemantics, provenance, governance. Conditional fields are required when their scientific concept applies and must never be populated with guesses: inputEntityIds, requiredExternalInputs, aggregationFunction, calculationReference, referencePopulation, unitOfAnalysis, boundary, timeWindow, metricVariant, normalization, missingnessPolicy, parameterization.

## Causal firewall

Every profile in the prototype carries `causalSourceEligible=false` and `gate=WP-PSG-005_REQUIRED`. `RDS-0006` calculates deterministically while remaining unauthorized as a causal source. `NEG-014` proves that a causal request is rejected even when the derivation request is otherwise complete.

## Recommendation

Adopt **Option B+C as the architecture direction**, subject to human governance and later implementation design. Use an umbrella RDS computation-profile registry with distinct `DERIVATION_PROFILE`, `MEASUREMENT_PROFILE`, and `ESTIMATION_PROFILE` types. Require exact profile and binding versions. Keep an RDS non-executable when no eligible governed profile/binding exists. Preserve `DER-V1-SOC-F07-001` by additive wrapping and lineage rather than rewriting it.

This recommendation does not govern the architecture, migrate records, authorize execution, or authorize causal-source use.

## Exact governance statement prepared for the human

> Approve the bounded Option B+C architecture direction for later implementation design: preserve each RDS construct separately from named, immutable-version computation profiles and explicit versioned application bindings; permit zero, one, or multiple governed profiles; make zero eligible profile/binding mean non-executable; require exact profile and binding selection with no silent latest/default behavior; preserve typed derivation, measurement, and estimation semantics; wrap `DER-V1-SOC-F07-001` additively without changing its ID or lineage; and keep all RDS causal-source eligibility false unless separately governed through WP-PSG-005. This decision authorizes architecture design only, not production implementation, migration, causal-source use, lifecycle change, or activation.
