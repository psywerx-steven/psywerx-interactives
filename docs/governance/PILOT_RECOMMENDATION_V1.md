# PSYWERX Relationship + Intervention Pilot Recommendation V1

**Status:** Recommendation only; pilot not started

**Baseline:** Current Relationship Schema v3 active graph at 2026-09-05

## Counting rule

“Current relationship count” below means unique governed active **causal**
relationships incident to at least one primary member of the Family. Internal
edges count once; outgoing and incoming cross-Family edges are also shown. This
matches the relationships that a Family audit must inspect without counting
noncausal dependencies as causal connectivity. Active noncausal incident
records are reported separately.

## Recommended set

| Family | Layer | Drivers | RDS | Current causal relationships | Active noncausal incident |
| --- | --- | ---: | ---: | --- | ---: |
| `BIO-F01` Sleep & Circadian Regulation | Biological | 6 | 5 | 6 (1 internal, 3 outgoing, 2 incoming) | 5 |
| `PSY-F03` Normative & Relational Perceptions | Psychological | 12 | 0 | 21 (3 internal, 8 outgoing, 10 incoming) | 0 |
| `INF-F03` Clarity, Complexity & Completeness | Informational | 4 | 4 | 9 (4 internal, 2 outgoing, 3 incoming) | 5 |

Together these Families contain 22 Drivers and 9 RDS and touch 36 current
unique current causal edges (there are no causal edges between the three
selected Families in the baseline, so their incident counts do not overlap).
They are small enough for a controlled pilot while spanning biological state,
psychological appraisal, and designed information.

## 1. BIO-F01 — Sleep & Circadian Regulation

**Why it is a good pilot:** Sleep and circadian science has mature measurement
and intervention traditions, multiple time scales, biological constraints,
and strong relevance to performance and behavior. The Family combines highly
modifiable Drivers (Sleep Duration, Sleep Continuity, Sleep Inertia Severity),
moderately modifiable timing constructs, two newly admitted Drivers with
incomplete peripheral metadata, and five RDS.

**Architectural challenges exposed:**

- strict separation of Sleep Duration from Sleep Sufficiency and Cumulative
  Sleep Deficit;
- RDS recalculation from duration/need and serial observations;
- interventions described by desired RDS outcomes that must resolve to Driver
  or schedule/environmental targets;
- acute versus chronic dose, lag, persistence, recovery, and stabilization;
- clinical/biological risks and population boundary conditions; and
- cross-Layer connections to environmental light/schedules and psychological
  cognitive load without aggregate/constituent double counting.

## 2. PSY-F03 — Normative & Relational Perceptions

**Why it is a good pilot:** This is a dense, entirely Driver-based Family with
strong cross-Layer coupling to observed Social conditions and Institutional
conditions. Its 21 incident causal relationships test whether the workflow can
distinguish perceived norms, actual prevalence, fairness, legitimacy, trust,
support, belonging, exclusion, and status without collapsing neighboring
constructs. It also has broad intervention relevance across communication,
social design, procedural change, services, and policy.

**Architectural challenges exposed:**

- perception versus objective condition and measurement versus intervention;
- reciprocal and mediated mechanisms across Psychological, Social,
  Institutional, and Biological Layers;
- risk of high-degree constructs becoming generic explanatory hubs;
- multi-target interventions that affect fairness, legitimacy, trust, and
  norms differently;
- heterogeneous populations, prior beliefs, reference groups, and cultural
  moderators; and
- ethical risk in persuasive or norm-based interventions.

## 3. INF-F03 — Clarity, Complexity & Completeness

**Why it is a good pilot:** This compact Family has equal numbers of Drivers
and RDS, high intervention relevance, and both causal and noncausal incident
records. Message Ambiguity, Message Conceptual Complexity, Claim Uncertainty
Disclosure, and Message Surface-Linguistic Complexity are potentially
configurable Drivers, while readability, contradiction, completeness, and
cohesion require derivation/scope discipline.

**Architectural challenges exposed:**

- causal influence versus derivation, constituent, semantic inverse, and
  realization claims in the same neighborhood;
- audience-relative RDS and matched message/audience/time-window scope;
- direct message editing versus technological realization and delivery;
- intervention-to-Driver mechanism distinct from message-to-psychological
  causal mechanism;
- multi-objective tradeoffs among simplicity, completeness, ambiguity, and
  uncertainty disclosure; and
- measurement validity across languages, audiences, channels, and tasks.

## Why this set is preferable for the first pilot

The set deliberately includes one Family with many RDS and mature biological
timing concerns, one dense psychological Family with no RDS, and one
information-design Family where causal and noncausal semantics are easily
confused. It therefore tests the architecture's hardest boundaries without
selecting the largest or most isolated Families.

The pilot should begin only after governance approves the relationship
vocabulary, Intervention/Effect model, lifecycle, audit ownership rules, and
RDS targeting guardrails. It must use a frozen commit and produce candidates,
review packets, and metrics—not silent canonical changes.
