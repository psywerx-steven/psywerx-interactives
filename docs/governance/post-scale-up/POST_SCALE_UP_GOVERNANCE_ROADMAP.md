# Post-Scale-Up governance roadmap

This roadmap converts the 44-row historical backlog into decision-ready work packages. Stages A and B are complete here; skeptical architecture review is complete for the six highest-consequence packets. DP-PSG-001-IMPLEMENTATION is human-approved. Current bounded production state is `PHASE_0_COMPLETE_EMPTY_REGISTRIES`; causal-source use remains prohibited and all other RDS remain unchanged.

| Order | Work package | Root issue | Band | Dependencies | Original rows |
|---:|---|---|---|---|---:|
| 1 | `WP-PSG-001` Shared RDS definition and derivation contract | `ROOT-RDS-DEFINITION-DERIVATION-001` | BAND_1_FOUNDATION | None | 5 |
| 2 | `WP-PSG-002` Cross-level exposure and group-to-person causal semantics | `ROOT-CROSS-LEVEL-EXPOSURE-001` | BAND_1_FOUNDATION | None | 2 |
| 3 | `WP-PSG-003` Network State, ScenarioStateDelta and metric recalculation boundary | `ROOT-NETWORK-STATE-TRANSITION-001` | BAND_1_FOUNDATION | None | 3 |
| 4 | `WP-PSG-004` Contribution identity and double-count control | `ROOT-CONTRIBUTION-IDENTITY-001` | BAND_2_CONTROL | ROOT-RDS-DEFINITION-DERIVATION-001, ROOT-NETWORK-STATE-TRANSITION-001 | 1 |
| 5 | `WP-PSG-005` Aggregate RDS causal-source independence | `ROOT-RDS-CAUSAL-SOURCE-001` | BAND_3_ADJUDICATION | ROOT-RDS-DEFINITION-DERIVATION-001, ROOT-CROSS-LEVEL-EXPOSURE-001, ROOT-CONTRIBUTION-IDENTITY-001 | 5 |
| 6 | `WP-PSG-006` Active empirical effect versus mechanism-knowledge contract | `ROOT-ACTIVE-EFFECT-MECHANISM-001` | BAND_2_CONTROL | None | 4 |
| 7 | `WP-PSG-007` Construct identity, feature and blocked-metadata governance | `ROOT-CONSTRUCT-ONTOLOGY-001` | BAND_1_FOUNDATION | None | 4 |
| 8 | `WP-PSG-008` Truthful multi-route source registration contract | `ROOT-SOURCE-GOVERNANCE-001` | BAND_1_FOUNDATION | None | 2 |
| 9 | `WP-PSG-009` Production Relationship semantic-debt program | `ROOT-RELATIONSHIP-SEMANTIC-DEBT-001` | BAND_4_MIGRATION_PLANNING | ROOT-CROSS-LEVEL-EXPOSURE-001, ROOT-NETWORK-STATE-TRANSITION-001, ROOT-CONTRIBUTION-IDENTITY-001, ROOT-RDS-CAUSAL-SOURCE-001, ROOT-CONSTRUCT-ONTOLOGY-001 | 8 |
| 10 | `WP-PSG-010` Targeted evidence and inactive-knowledge program | `ROOT-TARGETED-EVIDENCE-001` | BAND_5_TARGETED_RESEARCH | ROOT-RDS-CAUSAL-SOURCE-001, ROOT-ACTIVE-EFFECT-MECHANISM-001, ROOT-CONSTRUCT-ONTOLOGY-001, ROOT-SOURCE-GOVERNANCE-001, ROOT-RELATIONSHIP-SEMANTIC-DEBT-001 | 10 |

## Sequence finding

The tentative sequence is retained with one clarification: construct/ontology and source-governance design can run in parallel with the foundation band, but Relationship migration and targeted evidence must wait for the applicable prerequisite decisions. Aggregate causal-source adjudication follows RDS definition, cross-level exposure and contribution-control decisions.

## Highest leverage

`WP-PSG-001` comes first. It spans six Layers, directly normalizes five definition blockers, and supplies the input/constituent contract required before five aggregate causal-source rows can be judged. A well-defined RDS is not thereby authorized as a cause.

DP-PSG-001 selects only the bounded B+C architecture direction. No production validator, source, RDS, Relationship or lifecycle state changes, and no causal-source use is authorized.
