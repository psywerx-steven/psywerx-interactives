# RDS profile identity rules

## Architecture vocabulary

- **RDS construct identity:** the scientific concept and its definition version.
- **Computation profile:** a named, versioned method. Use `DERIVATION_PROFILE` for deterministic calculations, `MEASUREMENT_PROFILE` for observed-score construction, and `ESTIMATION_PROFILE` for latent/model-estimated states.
- **Application binding:** the concrete population, boundary, window, instrument/data source, and compatible input versions used in an application.

## New identity versus version versus binding

| Change | Required action |
| --- | --- |
| Same method, different population, cohort, jurisdiction, network instance, node set, data source, or observation window | New or revised **binding**; profile unchanged |
| Correction that preserves the scientific method and output meaning | New **profile version**; old version remains reproducible |
| Different normalization, metric variant, aggregation rule, constituent set, missingness policy, unit of analysis, or latent measurement model | New **profile identity** unless a governed compatibility rule proves it is only parameterization |
| Degree versus weighted degree; deterministic score versus latent estimator | New **profile identity** and correct profile type |
| Change to the scientific construct or output interpretation | New **RDS identity/version** through ontology governance, not a profile workaround |
| Presentation-only label change with unchanged definition hash and semantics | Metadata update; no new profile or RDS |

## Proliferation controls

Profiles require a material computation difference, canonical registry search, explicit supersession/compatibility statement, immutable version, and human governance. Bindings carry contextual variation that does not change method semantics. Consumers must supply exact IDs and versions; no default, first, or latest profile is allowed.

## Version propagation

A changed Driver/input definition invalidates compatibility unless the binding cites a governed compatibility assertion. Normalization, formula, estimator, or time-window-rule changes create a new profile version or identity. Source changes update provenance only when the method is unchanged. Historical requests retain their cited profile, binding, input versions, and hashes.

## Constituent roles

Every input is typed as `CONSTITUENTS`, `MEASUREMENT_INPUTS`, `PARAMETERS`, `NORMALIZERS`, `BOUNDARY_INPUTS`, `REFERENCE_VALUES`, or `EXTERNAL_CONTEXT`. Required input does not imply causal constituent. This prepares later double-count review without deciding it.
