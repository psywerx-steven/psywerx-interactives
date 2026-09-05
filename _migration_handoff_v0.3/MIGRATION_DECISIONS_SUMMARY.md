# Migration Decisions Summary

## Retypes
- `INF-010` → **Decision-Relevant Information Completeness**
- `INF-011` → **Information-Set Contradiction**
- `INF-014` → **Message–Audience Readability**
- `INS-024` → **Administrative Compliance Burden**
- `BIO-003` → **Circadian Timing Alignment**
- `BIO-006` → **Chronotype–Schedule Fit**
- `SOC-049` → **retain adjudicated name**
- `SOC-050` → **retain adjudicated name**
- `SOC-051` → **retain adjudicated name**
- `SOC-052` → **retain adjudicated name**
- `SOC-053` → **retain adjudicated name**
- `SOC-054` → **retain adjudicated name**
- `SOC-055` → **retain adjudicated name**
- `SOC-056` → **retain adjudicated name**
- `SOC-057` → **retain adjudicated name**
- `INF-053` → **Message–Audience Language Accessibility**
- `INF-068` → **Material Selective-Omission Degree**
- `SOC-024` → **Active Personal Network Size**
- `SOC-090` → **Member-Level Cross-Group Friendship Prevalence**
- `INF-004` → **Information-Item Prominence**
- `INS-113` → **Policy/Rule Implementation Fidelity**
- `SOC-022` → **Tie Survival Probability**

## New Drivers
- **Message Surface-Linguistic Complexity** — Informational / INF-F03
- **Chronotype** — Biological / BIO-F01
- **Physiological Sleep Need** — Biological / BIO-F01
- **Presented Choice-Set Size** — Technological / TEC-F02
- **Interface Option Grouping Configuration** — Technological / TEC-F02
- **System-Gated Interaction Delay** — Technological / TEC-F03
- **Administrative Scheduling Flexibility** — Institutional / Structural / INS-F03
- **Administrative Recovery Opportunity** — Institutional / Structural / INS-F03
- **Social Tie Formation Rate** — Social / SOC-F03
- **Triadic Closure Rate** — Social / SOC-F07
- **Tie Dissolution Rate** — Social / SOC-F03

## New RDS
- **Message Cohesion** — RELATIONAL_DERIVED_STATE
- **Sleep Architecture Composition** — TEMPORAL_PATTERN_STATE
- **Sleep Sufficiency** — RELATIONAL_DERIVED_STATE
- **Cumulative Sleep Deficit** — TEMPORAL_PATTERN_STATE
- **Distance-Based Closeness Centrality** — DERIVED_STRUCTURAL_STATE
- **Network Centralization** — DERIVED_STRUCTURAL_STATE
- **Network Component Fragmentation** — DERIVED_STRUCTURAL_STATE

## Major renames
- `TEC-018` → **Interface Task Complexity**
- `BIO-001` → **Sleep Duration**
- `BIO-004` → **Endogenous Circadian Phase**
- `INF-013` → **Message Conceptual Complexity**
- `INF-015` → **Claim Uncertainty Disclosure**
- `INF-033` → **Methodological & Applicability Limitation Disclosure**
- `INS-028` → **Institutional Default Rule**
- `TEC-013` → **Interface Default-State Configuration**

## Relationship rules
- Preserve relationship IDs only if proposition identity remains continuous.
- If target/source meaning or polarity changes materially, deprecate old relationship and mint a new ID with crosswalk.
- Noncausal derivation/composition/semantic mappings are excluded from causal simulation.
- SOC-022 stability edges must migrate to Tie Dissolution Rate with new IDs where target/polarity changes.

## Secondary high-confidence Driver→RDS retypes
- `SOC-018` → **Tie Age / Relationship Duration**
- `SOC-035` → **Reciprocity Balance**
- `SOC-041` → **Status Hierarchy Steepness**
- `SOC-046` → **Resource Control Asymmetry**
- `SOC-047` → **Dependence Asymmetry**
- `SOC-074` → **Goal Alignment**
- `SOC-076` → **Mutual Expectation Alignment**
- `SOC-096` → **Intergroup Status Inequality**
- `CUL-088` → **Generational Cultural Distance**
- `PSY-078` → **Perceived Goal–State Discrepancy**
- `INS-039` → **Caseload Pressure**
- `INS-103` → **Staffing Adequacy**

## Secondary boundary decisions
- `SOC-036 Repeated Interaction Probability` remains a Social Driver; it may be directly configured as an interaction-horizon condition and is distinct from survival of an existing tie.
- Add `OVERLAPS_WITH` between SOC-036 and Tie Survival Probability only when the operational tie definition is recurring interaction.
- `INS-102 Fiscal Capacity` remains in a lower-priority boundary queue; relational wording alone does not justify RDS retyping when a construct may represent a latent institutional capability.
- Revised preview target: **770 Drivers + 41 RDS = 811 total canonical entities**.
