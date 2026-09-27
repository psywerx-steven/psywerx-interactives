# Cross-level exposure Phase 0 validation

The production-focused suite validates empty registries, four schemas, exact immutable versions, source/target/level/hash attachment, partial-coverage and actual-exposure gates, perception semantics, Network State fail-closed behavior, the RDS causal firewall, and deterministic fingerprints.

Protected hashes cover the production Driver, entity/RDS, Relationship, source, Actions & Events, Network State, RDS-computation, Relationship-build, graph-adjacent, and scenario-service inputs. Phase 0 changes none of them. Empty registries introduce no validation requirement for legacy Relationships and feed neither graph construction nor simulation.

Phase 1 is gated on green Linux and Windows CI plus these protected-state checks.
