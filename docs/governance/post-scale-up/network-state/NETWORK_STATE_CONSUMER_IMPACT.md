# Network State consumer impact

**READ-ONLY ARCHITECTURE DECISION TEST — NO PRODUCTION SCIENCE, SCHEMA, LIFECYCLE OR ACTIVATION CHANGE**

| Consumer | Impact | Finding |
|---|---|---|
| `scripts/relational_state_v1.py` | NO_CHANGE | Current typed state, receipt, replay, observation and metric runtime is sufficient for tested cases. |
| `scripts/rds_computation_v1.py` | CALCULATION_PROFILE_AWARE_FUTURE | Future unified execution may bind exact state references to governed RDS profiles; legacy DER-V1 compatibility remains. |
| `scripts/cross_level_exposure_v1.py` | STATE_REFERENCE_AWARE_FUTURE | Network-dependent mappings must fail closed until exact state, boundary, window and profile references exist. |
| `scripts/relationship_intervention_v1.py` | NO_CHANGE | State deltas do not edit or approve ontology Relationships. |
| `scripts/actions_events_v1.py` | NO_CHANGE | ScenarioOperationReference can link identity without asserting an empirical consequence; direct RDS effects remain prohibited. |
| `scenario-service/src/openai-service.js` | NO_CURRENT_NETWORK_STATE_CONSUMER_FOUND | Repository search found no RelationalState or ScenarioStateDelta ingestion path. |
| `repository FCM/model construction` | NO_INTERNAL_ACTIVE_NETWORK_STATE_CONSUMER_FOUND | No production graph builder consumes state deltas or calculation receipts as causal edges. |

No current internal FCM, model-construction or scenario-service path was found that consumes a state delta or metric receipt as a causal edge. Future consumers must preserve exact state/profile references and fail closed; this decision test changes no behavior.
