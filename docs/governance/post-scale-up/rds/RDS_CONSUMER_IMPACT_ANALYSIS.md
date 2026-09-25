# RDS consumer impact analysis

| Consumer | Classification | Backward-compatible path |
|---|---|---|
| `scripts/relational_state_v1.py` | USES_LEGACY_DERIVATION | Keep legacy path; shadow adapter invokes prototype-equivalent profile engine only after Phase 1 authorization. |
| `scripts/relational_state_fixtures.py` | USES_LEGACY_DERIVATION | Reuse fixtures for byte/numeric shadow comparison. |
| `scripts/social_layer_v2_package.py` | USES_RDS_AS_ENTITY_ONLY | No execution migration required. |
| `scripts/next_layer_readiness.py` | USES_RDS_AS_ENTITY_ONLY | No execution migration required. |
| `scripts/rds_contract_decision_test.py` | NO_RDS_EXECUTION_DEPENDENCY | Historical decision-test retained. |
| `scripts/actions_events_v1.py` | NO_RDS_EXECUTION_DEPENDENCY | Rule remains unchanged. |
| `future RDS computation service` | WOULD_REQUIRE_PROFILE_AWARENESS | Require exact rds/profile/version/binding/version; never infer latest/default. |
| `data/relationships.json` | USES_RDS_AS_ENTITY_ONLY | No mutation in Phase 0 or Phase 1. |

The legacy derivation remains the only exact governed executable calculation. No current consumer must migrate in Phase 0. Phase 1 can shadow RDS-0006 beside the legacy evaluator without feeding active simulation.
