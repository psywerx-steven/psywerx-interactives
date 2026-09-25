# RDS computation profile schema specification

Profiles are typed and immutable at `profileId + profileVersion`. Universal fields anchor exact RDS identity/version/hash, input roles, output meaning, provenance, prototype governance and the causal firewall. Derivation profiles require an exact calculation and entailment. Measurement profiles require instrument/procedure and scoring semantics without claiming ontology entailment. Estimation profiles require model semantics, version, diagnostics and estimator-appropriate uncertainty.

Input roles are `CONSTITUENT`, `MEASUREMENT_INPUT`, `PARAMETER`, `NORMALIZER`, `BOUNDARY_INPUT`, `REFERENCE_VALUE`, `EXTERNAL_CONTEXT` and `DATA_SOURCE`. Context-only changes belong in bindings. Changes to method, normalization, metric variant, constituents, aggregation, missingness, unit, instrument/model or output semantics require a new profile identity; compatible corrections require a new profile version. Presentation-only changes are metadata.
