# Relationship Schema v3

`data/relationships.json` uses a generic directed relationship model whose
endpoints resolve against `data/entities.json`.

## Envelope

The v3 envelope contains:

- `relationships`: governed active relationships;
- `deprecatedRelationships`: retained provenance excluded from the active graph;
- `relationshipCandidates`: proposed or blocked relationships excluded from the
  active graph.

Every relationship ID is unique across all three buckets. Every entity endpoint
must resolve to exactly one canonical Driver or RDS.

## Generic triple

The core statement is `subjectEntityId` + `predicate` + `objectEntityId`.
`subjectEntityType` and `objectEntityType` make the Driver/RDS distinction
explicit. `objectRelationshipId` is reserved for governed relationships whose
object is another relationship.

`relationFamily` distinguishes `CAUSAL`, `SEMANTIC`, `DERIVATIONAL`,
`REALIZATION`, and `CONSTRAINT` propositions. Noncausal relationships must not
carry causal polarity, lag, exposure, or persistence fields.

## Governance and compatibility

`governanceStatus` controls graph inclusion. Only `ACTIVE` records belong to the
active relationship graph. Blocked candidates additionally use
`reviewStatus: BLOCKED_NEEDS_GOVERNANCE_INPUT` and must not be activated without
a governance decision.

Migrated Relationship v2 causal records retain a `legacyRelationship` marker.
The optional causal browser normalizes only these fully specified active causal
records. New semantic/derivational relationships, deprecated records, blocked
candidates, and causal propositions lacking the legacy executable field set are
excluded from that compatibility view.
