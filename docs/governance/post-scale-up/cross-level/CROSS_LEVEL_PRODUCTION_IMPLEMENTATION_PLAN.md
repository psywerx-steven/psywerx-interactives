# Cross-level production implementation plan

Phase 0 installs schemas, empty registries, validators and shadow eligibility/provenance with zero migrations or behavior changes. Separately gated Phase 1 uses `REL-INS-040` only in shadow validation. Other 37 remain unchanged. Rollback removes registry/shadow integration and returns to legacy-only behavior without rewriting Relationships.
