# BIO-F01 governance decision package

**Audit ID:** `AUD-BIO-F01-RI-V1-20260905-001`

**Decision authority:** Authorized human governor
**Current status:** Candidate review only; every decision is `PENDING`

An `APPROVE` entry would authorize a later deterministic governance
materialization only to the exact proposition/revision specified by the
decision. It would not, by itself, authorize deployment or another Family
audit. CI success validates structure, not scientific truth.

## A. Existing relationships proposed to remain scientifically unchanged

| Decision ID | Relationship | Recommendation | Reason | Governance decision |
| --- | --- | --- | --- | --- |
| `BIOF01-D-A01` | `REL-BIO-002` | Retain current proposition; keep V1 incomplete pending field-level completion | Duration→Cognitive Fatigue is defensible, but numeric lag, persistence, boundaries, normalized evidence, and conflicts are incomplete. | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-A02` | `REL-RDS-0016` | Retain as-is | Correct noncausal dependency from Chronotype–Schedule Fit to Chronotype. | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-A03` | `REL-RDS-0017` | Retain as-is | Correct Sleep Sufficiency duration input. | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-A04` | `REL-RDS-0018` | Retain as-is | Correct Sleep Sufficiency need/reference input. | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-A05` | `REL-RDS-0019` | Retain as-is | Correct serial-duration input for Cumulative Sleep Deficit. | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-A06` | `REL-RDS-0020` | Retain as-is | Correct need/reference input for Cumulative Sleep Deficit. | `PENDING — APPROVE / MODIFY / REJECT` |

## B. Existing relationships needing revision review

Approval here should authorize preparation of an exact revision proposal, not
silent mutation of the current record.

| Decision ID | Relationship | Recommended review | Primary risk | Governance decision |
| --- | --- | --- | --- | --- |
| `BIOF01-D-B01` | `REL-BIO-001` | Require heightened RDS safeguards and clarify whether the causal source should remain the alignment RDS or be represented by exact constituent/environmental mechanisms. | Exogenous RDS and aggregate/constituent double counting. | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-B02` | `REL-BIO-003` | Replace/augment evidence with continuity-specific fragmentation evidence and tighten Cognitive Fatigue outcome language. | Current sources do not isolate the proposition; null task effects exist. | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-B03` | `REL-BIO-009` | Add direction-specific pain→continuity evidence and boundaries. | Current sources concern pain/cognition, not sleep continuity. | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-B04` | `REL-BIO-021` | Adjudicate whether endpoint is experienced load, working-memory availability, or performance under load before any V1 revision. | Cognitive load may be conflated with capacity/performance. | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-B05` | `REL-ENV-040` | Add direct sleep-noise sources and distinguish average ambient level from event intermittency. | Generic source and exposure semantics. | `PENDING — APPROVE / MODIFY / REJECT` |

No existing edge is proposed for automatic retype, split, merge, or
deprecation in this pilot.

## C. New causal candidates

| Decision ID | Candidate | Recommendation | Key boundary | Governance decision |
| --- | --- | --- | --- | --- |
| `BIOF01-D-C01` | `REL-CAND-BIO-F01-001` Sleep Duration→Sleep Inertia Severity | Review for future V1 governance | Prior restriction, sleep stage, phase, task, and assessment window | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-C02` | `REL-CAND-BIO-F01-002` Endogenous Circadian Phase→Sleep Inertia Severity | Review with context-dependent/cyclic polarity | Phase at awakening; no universal high/low direction | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-C03` | `REL-CAND-BIO-F01-003` Caffeine Effect Level→Sleep Duration | Review for future governance | Dose, timing, metabolism, tolerance, formulation | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-C04` | `REL-CAND-BIO-F01-004` Noise Intermittency→Sleep Continuity | Review after supplemental-source registration | Transportation-noise evidence may not generalize to all sounds | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-C05` | `REL-CAND-BIO-F01-005` Sleep Continuity→Persistent Pain Burden | Keep `RESEARCH_NEEDED` | Broad observational sleep problems do not isolate continuity causality | `PENDING — APPROVE / MODIFY / REJECT` |

## D. New noncausal candidates

| Decision ID | Candidate | Recommendation | Safeguard | Governance decision |
| --- | --- | --- | --- | --- |
| `BIOF01-D-D01` | `REL-CAND-BIO-F01-006` Endogenous Circadian Phase `ASSOCIATED_WITH` Chronotype | Review as association only | Never substitute chronotype for phase without instrument/protocol qualification | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-D02` | `REL-CAND-BIO-F01-007` Sleep Duration `ASSOCIATED_WITH` Sleep Continuity | Keep `RESEARCH_NEEDED` | Shared epochs and denominators can manufacture association | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-D03` | `REL-CAND-BIO-F01-009` Circadian Timing Alignment `DERIVED_FROM` Endogenous Circadian Phase | Review as missing derivational dependency | External timing parameter remains required | `PENDING — APPROVE / MODIFY / REJECT` |

No temporal-transition candidate is recommended. Do not infer a temporal
record from prior-sleep ordering or causal lag.

## E. Moderation and pathway candidates

| Decision ID | Candidate | Recommendation | Reason | Governance decision |
| --- | --- | --- | --- | --- |
| `BIOF01-D-E01` | `REL-CAND-BIO-F01-008` Endogenous Circadian Phase moderates `REL-BIO-002` | Keep `RESEARCH_NEEDED` | Experimental moderation outcome is vigilance performance, not yet aligned to Cognitive Fatigue. | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-E02` | Noise→Continuity→Cognitive Fatigue pathway hypothesis | Do not create a pathway yet | No aligned pathway-specific mediation evidence. | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-E03` | Pain→Continuity→Cognitive Fatigue pathway hypothesis | Do not create a pathway yet | Graph reachability and separate segment evidence do not establish mediation. | `PENDING — APPROVE / MODIFY / REJECT` |

## F. Intervention identities

| Decision ID | Candidate IDs | Recommendation | Governance decision |
| --- | --- | --- | --- |
| `BIOF01-D-F01` | `INT-CAND-BIO-F01-001`–`003` | Review the three distinct duration/schedule intervention identities. | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-F02` | `INT-CAND-BIO-F01-004`, `005` | Review CBT-I component identities; approval must not infer component effects. | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-F03` | `INT-CAND-BIO-F01-006` | Review CBT-I as a package containing at least components `004` and `005`; package effect requires separate approval. | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-F04` | `INT-CAND-BIO-F01-007`, `008` | Review timed light and timed melatonin as reusable phase-manipulation identities. | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-F05` | `INT-CAND-BIO-F01-009` | Review acoustic attenuation identity and whether source/path/receiver variants remain one identity. | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-F06` | `INT-CAND-BIO-F01-010` | Review pre-awakening caffeine as distinct from ordinary caffeine consumption. | `PENDING — APPROVE / MODIFY / REJECT` |

## G. InterventionEffect candidates

| Decision ID | Effects | Recommendation | Governance decision |
| --- | --- | --- | --- |
| `BIOF01-D-G01` | `IE-CAND-BIO-F01-001` behavioral sleep extension→Sleep Duration | Review with heterogeneity and insomnia boundary. | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-G02` | `IE-CAND-BIO-F01-002` protected scheduling→Sleep Duration | Keep `RESEARCH_NEEDED`; roster-specific certainty is low. | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-G03` | `IE-CAND-BIO-F01-003` delayed school start→Sleep Duration | Review for adolescent education context only. | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-G04` | `IE-CAND-BIO-F01-004` CBT-I package→Sleep Continuity | Review with subjective/objective measurement conflict and transient-sleepiness risk. | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-G05` | `IE-CAND-BIO-F01-005` timed light→Endogenous Circadian Phase | Review only with phase-response timing and safety constraints. | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-G06` | `IE-CAND-BIO-F01-006` timed melatonin→Endogenous Circadian Phase | Review with population, timing, formulation, quality, and interaction constraints. | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-G07` | `IE-CAND-BIO-F01-007` acoustic attenuation→Sleep Continuity | Review for stated noise-exposed contexts; preserve alarm-audibility risk. | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-G08` | `IE-CAND-BIO-F01-008` pre-awakening caffeine→Sleep Inertia Severity | Keep `RESEARCH_NEEDED`; evidence is small and formulation-specific. | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-G09` | `IE-CAND-BIO-F01-009` post-awakening light→Sleep Inertia Severity | Keep `RESEARCH_NEEDED`; objective-performance evidence is insufficient. | `PENDING — APPROVE / MODIFY / REJECT` |

All nine target Drivers. No RDS or generic context object is a direct target.

## H. Rejected/not-supported hypotheses

| Decision ID | Hypothesis | Recommendation | Governance decision |
| --- | --- | --- | --- |
| `BIOF01-D-H01` | Sleep Duration causally changes Sleep Sufficiency | Reject causal representation; retain derivation only. | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-H02` | Sleep Duration causally changes Cumulative Sleep Deficit | Reject causal representation; retain serial derivation only. | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-H03` | Physiological Sleep Need causally changes either sleep RDS | Reject causal representation; preserve denominator/input dependencies. | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-H04` | Low Sleep Duration `TRANSITIONS_TO` high Sleep Inertia | Reject transition record; constructs do not transform into one another. | `PENDING — APPROVE / MODIFY / REJECT` |
| `BIOF01-D-H05` | Add another Circadian Timing Alignment→Sleep Duration edge | Reject duplicate; handle through the existing-edge revision process. | `PENDING — APPROVE / MODIFY / REJECT` |

## I. Research-needed and governance-blocked summary

Thirteen machine records remain `RESEARCH_NEEDED`: three Relationships, six
EvidenceAssessments, one Intervention identity, and three InterventionEffects.
Additional pathway and ontology-alignment questions are documented in the
research queue. No record is marked `NEEDS_GOVERNANCE_INPUT`; none of the open
questions prevented a conservative non-governed disposition.

Supplemental pilot sources must not be silently appended to the governed
source register. Source registration, if desired, is a later explicit
governance/materialization step.
