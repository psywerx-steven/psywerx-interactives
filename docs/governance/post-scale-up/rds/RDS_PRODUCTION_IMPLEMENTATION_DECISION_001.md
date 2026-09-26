# RDS production implementation decision 001

**Decision ID:** `GOV-RDS-IMPLEMENTATION-001-2026-09-25`

**Decision packet:** `DP-PSG-001-IMPLEMENTATION`

**Architecture decision:** `GOV-RDS-CONTRACT-001-2026-09-25`

## Human authorization

The human governor approves bounded production Phase 0 and the separately gated RDS-0006 Phase 1 exactly as specified. Phase 0 installs governed computation-profile schemas, exact validators, empty registries and the causal firewall with zero migrations. Phase 1 may begin only after Phase 0 validation passes and may add only the RDS-0006 compatibility wrapper preserving `DER-V1-SOC-F07-001`, with shadow numeric/provenance equivalence, rollback to legacy-only behavior, no active simulation feed and `causalSourceEligible=false`.

## Explicit exclusions

All other 40 RDS and all other production science, ontology, lifecycle, Network State, Actions & Events, sources and activation remain unchanged and unauthorized. This decision does not authorize WP-PSG-005 causal-source use.

## Materialization sequence

Phase 0 and Phase 1 are separate validation gates and commits. Phase 1 cannot proceed unless the empty-registry architecture passes its focused tests, protected-science checks and repository regressions.
