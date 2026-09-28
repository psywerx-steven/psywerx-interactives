# RDS causal-source option comparison

| Criterion | A: independent contrast | B: contextual exposure | C: prohibit | C default + bounded A/B |
|---|---|---|---|---|
| Scientific fidelity | Strong for exact same-level contrasts | Strong for real higher-level contexts | Rejects all higher-level causal use | Strongest when every exception passes exact gates |
| Causal interpretability | Requires intervention policy and mechanism | Requires context, mechanism, and actual exposure | Simple noncausal interpretation | Explicitly separates independent, contextual, alternate, and derivational modes |
| Constituent double-count prevention | Incomplete alone | Incomplete alone | Prevents by prohibition | Requires WP-PSG-004 independent or select-one resolution |
| Contextual-causality support | Limited | Core strength | None | B-like exception only |
| Network-metric support | Only with exact topology intervention | Only with state and exposure binding | Descriptive/recalculation only | Requires WP-PSG-003 state, transformation, boundary, and window |
| Ratio/composite handling | Good if versions are bound | Possible for contextual ratios | Always derivational | Multiple versions fail closed unless explicitly resolved |
| Cross-level safety | Does not supply exposure semantics | Depends on WP-PSG-002 | Safe by prohibition | Exact mapping and actual exposure required |
| Temporal clarity | Must be specified | Context and response windows required | No causal ordering needed | Mandatory source-before-target gate |
| Execution clarity | Profile still separate | Profile still separate | Computation only | Science, Relationship evidence, execution, and governance remain separate |
| Migration burden | Medium | High | Low | Low default; case-specific exception records only |
| Consumer clarity | Ambiguous without modes | Ambiguous without modes | Simple | Rich advisory mode plus unchanged boolean authority firewall |
| False-positive risk | Medium | High if ecological inference leaks | Lowest | Low through default prohibition and fail-closed gates |
| False-negative risk | High if manipulability is literal | Lower for contexts | Highest | Bounded by exception pathways |
| Rollback safety | Case record removal | Case record/mapping removal | Highest | High because no production behavior changes in this decision test |

“Manipulable” should mean a well-defined causal contrast or intervention policy, not necessarily a literal single treatment. Alternate abstraction is a separate non-additive mode: aggregate or constituents, never both.
