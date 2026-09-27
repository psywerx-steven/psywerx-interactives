# Network State representation contract

**READ-ONLY ARCHITECTURE DECISION TEST — NO PRODUCTION SCIENCE, SCHEMA, LIFECYCLE OR ACTIVATION CHANGE**

1. **HappeningType / Occurrence** identifies an asserted or observed operation; it does not prove a state consequence.
2. **ScenarioOperationReference** may link that identity to a delta as a modeled consequence assumption, with no automatic execution or empirical consequence claim.
3. **ScenarioStateDelta** stipulates an ordered, typed modification to one exact scenario state.
4. **RelationalState revision** is the resulting immutable modeled configuration with parent lineage.
5. **RDS computation profile / derivation** recalculates a metric from an exact state/boundary/window.
6. **CrossLevelExposureMapping** may later describe how exact network context reaches a lower-level target.
7. **Relationship / EffectAssertion** remains the governed empirical causal claim.

An exact state reference requires state ID, revision, content hash, scenario ID, boundary ID/revision, window, node set, tie type/layer, tie set, missingness/assumptions and provenance. A future cross-level binding must reference these explicitly; a metric value cannot substitute for state identity.

Supported changes are `STIPULATED_CONFIGURATION_CHANGE` or analytic selection. Observation construction is `CONSTRUCTED_STATE_FROM_OBSERVATION`. `EMPIRICALLY_ESTIMATED_TRANSITION` and continuous-time dynamics are not represented and remain blocked.
