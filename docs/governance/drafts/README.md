# Governed-design machine-readable drafts

These JSON Schemas materialize the governed architecture for validation and
later implementation planning; they are not production contracts:

- `relationship-v1.schema.json` describes the governed-design normalized
  relationship record, including entity- and relationship-targeted claims;
- `causal-pathway-v1.schema.json` describes a governed mediation/mechanistic
  pathway assembled from governed causal edge IDs;
- `intervention-v1.schema.json` describes Intervention identity and package
  composition; and
- `intervention-effect-v1.schema.json` describes one bounded
  intervention-to-target effect assertion.

They intentionally do not validate or replace current `data/*.json` files.
Production locations, data generation, migration execution, population, and
activation remain separately unauthorized.
