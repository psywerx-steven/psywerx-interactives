# WP-PSG-003 decision-test harness

This isolated harness executes fictional `SYN-*` fixtures through the existing production Network State V1 runtime. It writes only governance planning artifacts under `docs/governance/post-scale-up/network-state/` and `data/governance/post-scale-up/network-state/`. It does not define a production schema, mutate a scientific catalog, or integrate a consumer.

Run `python prototypes/network-state-transition-v1/build_decision_test.py` from the repository root.
