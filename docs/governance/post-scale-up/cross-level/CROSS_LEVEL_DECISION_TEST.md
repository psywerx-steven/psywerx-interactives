# WP-PSG-002 cross-level exposure decision test

This read-only Stage C test reconciles `ASTRA-SOC-LAYER-002` (20 rows) and `ASTRA-INS-LAYER-003` (21 rows). Three rows overlap, producing 38 distinct current records. No disposition or production record changes.

15 real/synthetic cases test implemented and unimplemented policy, eligibility without receipt, partial coverage, discrete assignment, institutional-to-person perception, institution-to-group allocation, ambient group context, network-state dependency, objective exposure without perception, ecological association, temporal reversal and a same-level control. All expected fail-closed states were reproduced.

The test supports a bounded A+B+C hybrid: a separate immutable typed mapping is the reusable contract; each cross-level Relationship carries only its exact mapping ID/version plus claim qualifiers; existing Drivers/HappeningTypes are referenced only when they are scientifically real intermediates. The mapping is routing/eligibility metadata, never a causal node or evidence.

Migration rehearsal: `{"CONSTRUCT_ONTOLOGY_DEPENDENCY": 0, "EXISTING_BRIDGE_SUFFICIENT": 5, "MAPPING_LIKELY_REQUIRED": 13, "METADATA_ONLY_MAY_SUFFICE": 2, "NETWORK_STATE_DEPENDENCY": 3, "NO_CROSS_LEVEL_PROBLEM_AFTER_REVIEW": 13, "RESEARCH_NEEDED_BEFORE_MAPPING": 2}`. The 38-row queue is not 38 production migrations: 13 rows have no cross-level problem after review and several others first depend on Network State or research.
