# Informational Layer Relationship review

**ADVISORY — HUMAN DECISION REQUIRED. No production Relationship is changed.**

The frozen Layer has 64 unique active incident Relationships: 58 causal and six noncausal. Every record has exactly one review in `relationship-review-registry.json`; V3/native projections are not counted twice. The current audit dispositions are 11 `RETAIN_AS_IS`, seven `RETAIN_V1_INCOMPLETE`, 12 `REVISION_CANDIDATE`, 18 `RETYPE_CANDIDATE`, and 16 `RESEARCH_NEEDED`. Twenty-six records point to prior INF-F03 or Psychological human decisions and are acknowledgements, not new votes. A review-only proposal is not an implemented replacement.

The most common retype issue is a causal edge that actually describes a component, calculation input, temporal dependency, or content overlap. Examples include `REL-INF-004/005` (rate/length to window-relative volume), `REL-INF-008` (required uncertainty field to completeness), `REL-INF-017` (spacing versus frequency), and `REL-INF-033/034` (guidance components). These sixteen newly undecided retype questions remain individual scientific votes because each proposed semantic relation has different inputs and boundaries.

`REL-INF-006` remains the pilot's approved revision-review-only disposition with a blocked implementation dependency on `HYP-INF-F03-H20`. `REL-INF-007/009` remain research-needed as the pilot directed. Psychological-reviewed cross-Layer edges retain their earlier review lineage; no Psychological science is reopened. The exact per-edge rationale, external ownership and V1-incomplete fields are in the structured registry.
