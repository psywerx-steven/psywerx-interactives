# Network State migration classification

**READ-ONLY ARCHITECTURE DECISION TEST — NO PRODUCTION SCIENCE, SCHEMA, LIFECYCLE OR ACTIVATION CHANGE**

| Category | Count |
|---|---:|
| ALREADY_REPRESENTABLE_BY_CURRENT_NETWORK_STATE | 2 |
| REPRESENTABLE_WITH_DOCUMENTED_CONTRACT_ONLY | 1 |
| REPRESENTABLE_WITH_MINOR_ADDITIVE_METADATA | 0 |
| NEEDS_NEW_TYPED_OPERATION | 0 |
| NEEDS_NEW_ARCHITECTURE_OBJECT | 0 |
| BLOCKED_BY_SCIENCE_NOT_ARCHITECTURE | 1 |
| BLOCKED_BY_WP_PSG_004 | 0 |
| BLOCKED_BY_WP_PSG_005 | 2 |

H12 and H20 are already representable, while the root architecture question needs only a documented contract. REL-SOC-017 and REL-SOC-035 remain blocked on later aggregate-source governance; REL-TEC-050 lacks science establishing a state transition and an exact segregation computation. No production migration is proposed.
