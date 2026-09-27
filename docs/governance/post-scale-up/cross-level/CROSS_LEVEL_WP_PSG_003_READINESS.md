# WP-PSG-003 entry readiness from cross-level Phase 1

WP-PSG-003 remains unstarted. The bounded next decision test must address the Network State, `ScenarioStateDelta`, and metric-recalculation boundary for exactly these handoff records:

- `REL-SOC-017`: requires an exact network-state identity and boundary before a network condition can be separated from metric recalculation and person exposure.
- `REL-SOC-035`: requires exact node/tie membership and boundary semantics plus a governed transition representation; a metric value alone is insufficient.
- `REL-TEC-050`: requires an exact technology-mediated network state, observation boundary, and transition route before exposure semantics can be evaluated.

Entry criteria are: preserve `DER-V1-SOC-F07-001`, H12, and H20; distinguish empirical action/event from stipulated state delta; distinguish node/tie state from derived metric recalculation; prevent metric-to-exposure inference; and keep all causal evidence, Relationship, Network State, lifecycle, and activation decisions unchanged during the decision test.

Recommended next work is a read-only Stage C architecture decision test with real counterexamples for adjacency change, membership change, boundary change, deterministic recalculation, and empirically identified exposure. No WP-PSG-003 implementation is authorized here.
