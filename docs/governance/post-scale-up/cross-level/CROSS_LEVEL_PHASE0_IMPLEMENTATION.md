# Cross-level exposure Phase 0 implementation

**Authorization:** `GOV-CROSS-LEVEL-IMPLEMENTATION-001-2026-09-26`  
**Scope:** empty production architecture; zero Relationship migrations

Phase 0 installs immutable exact-version `CrossLevelExposureMapping` and `CrossLevelExposureBinding` schemas, empty registries, fail-closed validators, and a shadow-only eligibility/provenance service. Mapping objects remain noncausal, nonevidentiary, nonpropagating, nonlifecycle, and nonactivating.

The subsystem is additive. Existing Relationship validation, build output, graph construction, simulation, Actions & Events, Network State, RDS causal eligibility, ontology, sources, lifecycle, and activation behavior are unchanged. Relationships without a binding continue under legacy behavior.

Phase 0 registry baseline: **0 mappings / 0 bindings / 0 migrations**.
