# RDS causal-source consumer impact

- **Relationship validation — SOURCE_GATE_AWARE:** Keep D10; require exact advisory mode/decision record without changing current validity.
- **Graph assembly / FCM — CENTRAL_FAIL_CLOSED_GATE:** Require governed source authorization plus contribution resolution before inclusion.
- **Simulation — EXECUTION_AND_PROFILE_AWARE:** Require exact profile/binding, source authorization, temporal context and no double count.
- **Scenario service — DISPLAY_ONLY_UNTIL_GOVERNED:** May show advisory status; must not infer execution.
- **RDS computation — NO_CAUSAL_BEHAVIOR_CHANGE:** Computability remains separate from causal-source eligibility.
- **Contribution resolver — SOURCE_MODE_AWARE:** Select one for alternate abstractions; require independent status for additive routes.
- **Cross-level exposure resolver — MAPPING_AWARE:** Require exact mapping/binding for contextual cross-level routes.
- **Network State runtime — STATE_REFERENCE_AWARE:** Keep state transition/recalculation noncausal; expose exact state identity to a separately governed claim.

No consumer integration is authorized. Minimal future architecture is a versioned eligibility decision record plus existing profile, contribution, exposure, and state references; no RDS schema field is required to govern the reusable contract. The production boolean remains the final execution firewall.
