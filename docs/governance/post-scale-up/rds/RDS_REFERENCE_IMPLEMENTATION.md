# RDS computation-profile reference implementation

**Decision:** `GOV-RDS-CONTRACT-001-2026-09-25`
**Scope:** non-production Stage E prototype and Stage F dry run only

The isolated implementation in `prototypes/rds-computation-v1/` separates RDS construct, typed immutable computation profile, versioned application binding, execution request/provenance and causal authorization. It supports `DERIVATION_PROFILE`, `MEASUREMENT_PROFILE` and `ESTIMATION_PROFILE` without collapsing their semantics. Every prototype object is `PROTOTYPE_ONLY`; no production registry imports this package.

RDS-0006 is the only exact positive control. Its additive wrapper references `DER-V1-SOC-F07-001`, retains the governed definition hash and recalculation-only semantics, and produces `1.0` for the four-node star. The deterministic fingerprint is `ca3ad01c4ad8c9f69ae9c361f58568ac36470dbba1c8961c60f2089bafa622e5`. Causal authorization remains false.

Stage E is complete in the authorized non-production scope. Stage F is complete only as a dry run; production migration is not started or authorized.
