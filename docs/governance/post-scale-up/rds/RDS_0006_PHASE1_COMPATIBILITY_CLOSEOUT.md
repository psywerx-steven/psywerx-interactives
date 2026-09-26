# RDS-0006 Phase 1 compatibility closeout

**Phase:** `WP-PSG-001-PHASE-1-RDS-0006-20260925-001`  
**Authorization:** `GOV-RDS-IMPLEMENTATION-001-2026-09-25`  
**Phase 0 merge:** `5891518de3603cc69e10638f44ba8db5862cf5df`

Phase 0 passed the Linux and Windows governance gates before this separately gated Phase 1 began. Phase 1 adds one immutable `DERIVATION_PROFILE`, `RDS-PROFILE-V1-SOC-F07-001`, and one versioned compatibility binding, `RDS-BIND-V1-SOC-F07-001`, for `RDS-0006` only.

The wrapper is additive. `DER-V1-SOC-F07-001` remains unchanged and retains its ID, definition binding, metric variant, calculation reference, lineage, contribution identity, `RECALCULATION_ONLY_NO_CAUSAL_SUM` policy, and governed/inactive lifecycle state. Shadow execution requires the exact profile and binding versions, exact RDS and input definition hashes, a complete legacy-aligned degree collection, and exact request context. It compares the new calculation with the unchanged legacy evaluator and fails closed on numeric or provenance divergence.

The profile is `SHADOW_ONLY`. Its receipts always state `feedsActiveSimulation=false` and `causalSourceAuthorized=false`; the profile itself states `causalSourceEligible=false` and `WP-PSG-005_REQUIRED`. No simulation consumer imports the wrapper. Rollback removes the profile/binding integration and restores legacy-only behavior without rewriting the legacy derivation or any RDS identity.

The other 40 RDS remain without production computation profiles or bindings. No science, ontology, lifecycle, Network State, Actions & Events, source, Relationship, or activation record changed.
