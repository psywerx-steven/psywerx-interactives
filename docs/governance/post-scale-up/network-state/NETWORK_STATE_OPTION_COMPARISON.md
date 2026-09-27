# Network State option comparison

**READ-ONLY ARCHITECTURE DECISION TEST — NO PRODUCTION SCIENCE, SCHEMA, LIFECYCLE OR ACTIVATION CHANGE**

| Criterion | A — current typed delta | B — new transition object | C — leave unsupported blocked | A+C |
|---|---|---|---|---|
| Scientific fidelity | Strong for stipulated operations | Adds no current scientific distinction | Safe but incomplete description | Strongest bounded separation |
| Determinism/replay | Existing hashes, receipts and replay | Would duplicate them | Preserved | Preserved |
| A&E separation | Explicit optional non-effect reference | Risks quasi-causal interpretation | Safe | Explicit and safe |
| RDS separation | Existing calculation receipts are noncausal | Duplicate linkage surface | Safe | Exact recalculation only |
| Cross-level compatibility | Supplies exact state reference | No added exposure semantics | Leaves dependencies blocked | Exact state input; exposure remains WP-PSG-002 |
| Migration | None | New schema/registry/consumers | None | None for current cases |
| Rollback | Historical immutable branches | New object migration required | Current behavior | Current behavior |

Recommendation: `BOUNDED_A_PLUS_C_USE_EXISTING_TYPED_SCENARIO_STATE_DELTA_AND_BLOCK_UNSUPPORTED_TRANSITIONS`. Option B is rejected for current scope because it duplicates delta + receipt + parent state + operation reference. C remains the fail-closed rule for unsupported transitions.
