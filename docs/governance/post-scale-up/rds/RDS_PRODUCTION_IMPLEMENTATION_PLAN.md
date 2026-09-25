# RDS production implementation plan

This is a design preview, not authorization.

1. **Phase 0:** add production schemas, empty registries, exact validators, eligibility service and causal firewall; migrate zero RDS.
2. **Phase 1:** add only the RDS-0006 compatibility wrapper and binding; preserve `DER-V1-SOC-F07-001`; run numeric/provenance shadow equivalence; do not feed active simulation.
3. **Later batches:** require separate scientific governance. The remaining 40 RDS stay unchanged.

Rollback removes profile-aware integration and empty/new registries while leaving every RDS identity and legacy derivation untouched. Shadow failure returns to legacy-only behavior. WP-PSG-005 receives exact profile/binding/input-role/constituent/output semantics with causal eligibility still false.
