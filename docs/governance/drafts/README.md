# Proposed machine-readable drafts

These JSON Schemas are design-review artifacts, not production contracts:

- `relationship-v1.schema.json` describes the proposed normalized relationship
  record, including entity- and relationship-targeted claims;
- `causal-pathway-v1.schema.json` describes a governed mediation/mechanistic
  pathway assembled from governed causal edge IDs;
- `intervention-v1.schema.json` describes Intervention identity and package
  composition; and
- `intervention-effect-v1.schema.json` describes one bounded
  intervention-to-target effect assertion.

They intentionally do not validate or replace current `data/*.json` files.
Candidate-record relaxation, final controlled vocabularies, canonical file
locations, migration rules, and production validation require explicit
governance approval.
