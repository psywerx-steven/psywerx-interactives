# Governed native Relationship + Intervention V1 stores

These files contain native V1 scientific records that have received an
explicit human governance decision. They are separate from the governed v0.3
Relationship V3 and workbook-derived source baselines.

At BIO-F01 partial activation checkpoint 001, six Relationships, five
Intervention identities, five InterventionEffects, and eleven
EvidenceAssessments are `GOVERNED + ACTIVE`. Four governed Intervention
identities remain `GOVERNED + INACTIVE` because they do not have their own
governed active effect. Only the four active causal Relationships enter the V1
causal traversal helper; the active association and derivational dependency do
not. The existing scenario service and public application do not consume these
native V1 stores.

INF-F03 governance checkpoint 001 adds one bounded causal Relationship and its
EvidenceAssessment. Partial activation decision 001 makes both `GOVERNED + ACTIVE`.
The Relationship has context-dependent, non-monotonic polarity semantics, enters
scientific causal traversal without a numeric weight, and remains ineligible for
quantitative execution. Its source-level findings are normalized in
`relationship-source-findings.json` and governed through the exact parent
assessment and decision record.

- `source-register.json` contains verified native V1 source records.
- `relationships.json` contains governed native V1 Relationships.
- `evidence-assessments.json` contains their normalized evidence and the
  evidence for governed InterventionEffects.
- `interventions.json` contains reusable Intervention identities.
- `intervention-effects.json` contains bounded Driver-targeted assertions.
- `causal-pathways.json` is empty because no pathway was governed.
- `materialization-manifest.json` links every canonical object to its pilot
  candidate, scientific governance decision, and activation decision.
- `relationship-source-findings.json` preserves source-level findings for the
  INF-F03 Relationship without altering the RI V1 schema.

Candidate copies remain physically separated under
`data/candidates/relationship-intervention-v1/`. A candidate is not a second
authoritative proposition; its canonical lineage is resolved through the
materialization manifest.
