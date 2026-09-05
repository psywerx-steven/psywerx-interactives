# Governed-design machine-readable drafts

These JSON Schemas preserve the design-stage materialization reviewed in PR
#11. They are retained as governance history and are not production contracts:

- `relationship-v1.schema.json` describes the governed-design normalized
  relationship record, including entity- and relationship-targeted claims;
- `causal-pathway-v1.schema.json` describes a governed mediation/mechanistic
  pathway assembled from governed causal edge IDs;
- `intervention-v1.schema.json` describes Intervention identity and package
  composition; and
- `intervention-effect-v1.schema.json` describes one bounded
  intervention-to-target effect assertion.

The production contracts now live in
[`schemas/relationship-intervention/v1/`](../../../schemas/relationship-intervention/v1/).
Scientific population, Family audits, native V1 activation, application
behavior changes, and deployment remain separately unauthorized.
