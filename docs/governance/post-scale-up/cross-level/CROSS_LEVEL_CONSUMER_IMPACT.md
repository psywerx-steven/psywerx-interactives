# Cross-level consumer impact

| Consumer | Classification | Future bounded change |
|---|---|---|
| `scripts/relationship_intervention_v1.py` | VALIDATION_AWARE_AND_MIGRATION_REQUIRED | Validate exact mapping/version references for cross-level Relationships; preserve lifecycle separation. |
| `scripts/build_relationships.py` | MIGRATION_REQUIRED | Emit optional exact mapping references only after production governance. |
| `scripts/actions_events_v1.py` | VALIDATION_AWARE | Resolve referenced HappeningTypes when a mapping names a real discrete operation; no universal HT requirement. |
| `scripts/relational_state_v1.py` | VALIDATION_AWARE | Validate exact Network State reference for network-dependent mappings; do not infer exposure from metrics. |
| `scripts/rds_computation_v1.py` | NO_CURRENT_EXECUTION_IMPACT | Later provide exact profile/binding and mapping reference to WP-PSG-005; causal eligibility remains false. |
| `scenario-service/src/openai-service.js` | DISPLAY_ONLY | May display bounded route context later; must not infer execution or causality. |
| `repository FCM/model construction` | UNKNOWN_REQUIRES_REVIEW | No active cross-level propagation consumer was located; external consumers must fail closed until mapping-aware. |

No current consumer is modified. Future execution-aware consumers must fail closed on absent, incomplete or wrong-version mappings and must keep scientific governance and lifecycle separate from routing eligibility.
