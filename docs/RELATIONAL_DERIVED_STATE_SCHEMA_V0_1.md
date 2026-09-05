# Relational / Derived State Schema v0.1

`data/relational-derived-states.json` contains canonical entities whose values
are calculated from other entities, ties, configurations, or observations.
They are not independent causal inputs. `data/entities.json` is the canonical
union of Drivers and relational/derived states (RDS).

## Identity and classification

Every RDS has a globally unique permanent `id`, `entityType` equal to
`RELATIONAL_DERIVED_STATE`, an `entitySubtype`, a canonical `name`,
`definition`, `primaryFamilyId`, `layer`, and zero or more related
families/associated layers. Retyped records preserve their pre-migration IDs.

## Derivation metadata

Every RDS must provide:

- `constituentSpecifications`: the governed inputs or observations;
- `derivationType`: the closed derivation category;
- `derivationLogic`: the calculation or classification rule;
- `scopeRequirements`: the population, network, document, time, or system scope;
- `recalculationBehavior`: when the state must be recomputed.

Subtype-specific metadata is mandatory where applicable. Network metrics
declare their boundary, tie type, direction/weighting, time window, and formula.
Ratios declare numerator and denominator. Temporal-pattern states declare an
observation window and update rule. Difference and composite states declare
their reference/sign or component/weight conventions.

## Incomplete peripheral metadata

The governed v0.3 preview admits 18 new entities with approved identities,
definitions, boundaries, and derivations. Where the specification does not
supply mechanism, temporal, observability, evidence-strength, or source-register
content, the value remains null or empty and the record lists the field in
`blockedFields`. Such records use `metadataStatus` =
`PARTIAL_GOVERNED_PREVIEW`; missing values must not be inferred.

## Mechanical invariants

The migration generator and `tests/test_migration_v0_3.py` require 770 Drivers,
41 RDS, and 811 total entities; a disjoint Driver/RDS ID partition; the exact
approved 34 legacy IDs as retypes; and reconciled per-Family counts.
