# Contribution reference implementation

> GOVERNED DIRECTION / NON-PRODUCTION PROTOTYPE / DRY RUN ONLY

The isolated prototype supplies a JSON Schema, exact-version immutable registry, validator, centralized `resolve_contribution_set` function, and deterministic receipts. It validates exact IDs/revisions/hashes, native EA agreement, identity dimensions, explicit select-one behavior, noncausal roles, unresolved aggregate blocking, collisions, and deterministic fingerprints. Production modules do not import it.

The architecture is sparse: only explicitly adjudicated cross-class identity receives a group. Independent native records remain outside the registry.
