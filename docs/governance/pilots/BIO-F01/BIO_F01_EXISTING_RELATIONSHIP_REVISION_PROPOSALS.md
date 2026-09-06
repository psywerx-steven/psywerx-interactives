# BIO-F01 existing-Relationship revision proposals

**Authority:** `GOV-BIO-F01-001-2026-09-05`

**Status:** Non-governed revision-review proposals only

**Activation:** `NOT_ELIGIBLE`

Nothing in this document mutates, supersedes, or deactivates the five current
V3 records. Each proposal isolates the exact later decision a human governor
would need to make.

## `REL-REV-BIO-F01-B01` — review of `REL-BIO-001`

### Current governed record

`BIO-003` Circadian Timing Alignment (RDS) `CAUSES` `BIO-001` Sleep Duration,
positive, with active V3 authority. Its mechanism presently says misalignment
and restriction co-occur. Sources are `SRC006`, `SRC007`, and `SRC008`.

### Exact proposed V1 alternatives

1. **RDS-source completion:** retain `BIO-003 → BIO-001` only if later review
   confirms a time-indexed alignment state, derivation version/window,
   temporal and mechanistic independence from the target duration, controlled
   constituent overlap, and a duplicate-propagation rule. External schedule
   requirements must be measured with provenance; the RDS cannot be exogenous.
2. **Driver/environment mechanism:** preserve the current V3 record until a
   later decision identifies exact Driver endpoint(s) for schedule, phase, or
   light exposure. Any changed source endpoint is a different scientific
   proposition and requires a new Relationship ID and explicit reconciliation
   with `REL-BIO-001`.

### Proposed field/evidence changes

- Replace co-occurrence language with an actual causal mechanism or leave V1
  incomplete.
- Add `HEIGHTENED_CAUSAL` RDS safeguards only when supported; do not infer
  calculation window, independence, or propagation control.
- Add `SRC-547` as schedule-context evidence for later adjudication, retaining
  its low/very-low-certainty and roster-dependence limitations.
- Bound population/context by schedule system, light exposure, chronotype,
  sleep opportunity, and measurement window.

### Identity and unresolved decision

The ID can remain stable only under alternative 1 with unchanged endpoints and
proposition identity. Alternative 2 requires new ID(s) and a later
supersession/reconciliation decision. This checkpoint selects neither.

## `REL-REV-BIO-F01-B02` — review of `REL-BIO-003`

### Current governed record

`BIO-002` Sleep Continuity `CAUSES` `BIO-026` Cognitive Fatigue, negative,
active V3. Current sources `SRC005` and `SRC006` do not isolate the exact
continuity-to-fatigue proposition.

### Exact proposed V1 proposition

Within protocols that fragment sleep while accounting for total sleep time,
reduced Sleep Continuity may increase next-day subjective sleepiness/fatigue
and impair some cognitive tasks; effects are outcome- and task-dependent and
must not be encoded as uniform performance impairment.

### Proposed field/evidence changes

- Retain endpoints and negative direction only if `BIO-026` is interpreted as
  fatigue rather than a generic performance score.
- Add continuity-specific `SRC-534`; retain the finding that sleepiness changed
  while selected performance measures did not.
- Tighten mechanism to fragmentation/restorative interruption rather than time
  in bed alone.
- Bound etiology, total sleep time, task, assessment time, adaptation, age, and
  clinical sleep disorder.
- Leave numeric lag, persistence, and functional form null unless later
  evidence supports them.

### Identity and unresolved decision

The ID may remain stable if the endpoint meaning remains Cognitive Fatigue and
only mechanism/evidence/scope are revised. Substitution of a vigilance or
performance endpoint would require a new ID. Later human adjudication is
required.

## `REL-REV-BIO-F01-B03` — review of `REL-BIO-009`

### Current governed record

`BIO-028` Persistent Pain Burden `CONSTRAINS` `BIO-002` Sleep Continuity,
negative, active V3. Its mechanism mentions reciprocity, but the record stores
only pain → continuity. Current sources `SRC033` and `SRC034` concern
pain/cognition rather than sleep continuity.

### Exact proposed V1 proposition

In people with chronic musculoskeletal or other specifically characterized
persistent pain conditions, greater pain burden may reduce Sleep Continuity
through nocturnal discomfort, arousal, movement, and related processes, with
condition, medication, insomnia, mood, and measurement boundaries.

### Proposed field/evidence changes

- Retain the stored direction only; remove reciprocal wording from this edge.
- Add direction-specific syntheses `SRC-532` and `SRC-533`, preserving their
  observational design, broad sleep-problem measures, heterogeneity, and
  residual-confounding limitations.
- State pain condition, medication, sleep-disorder, psychiatric comorbidity,
  population, and time-window boundaries.
- Do not infer `BIO-002 → BIO-028`; any reverse edge requires independent
  evidence and a new decision.

### Identity and unresolved decision

The same ID may remain if endpoints, direction, and predicate remain unchanged.
The exact evidence sufficiency for a causal rather than associative claim
remains a later human decision; no reverse ID is proposed.

## `REL-REV-BIO-F01-B04` — review of `REL-BIO-021`

### Current governed record

`BIO-001` Sleep Duration `CAUSES` `PSY-057` Cognitive Load, negative, active
V3, supported by broad construct sources `SRC-494` and `SRC-499`.

### Exact alternatives for construct adjudication

1. **Experienced/perceived load:** adequate sleep changes perceived effort or
   experienced cognitive burden under a specified task.
2. **Working-memory/resource availability:** sleep loss reduces available
   cognitive resources; this is not necessarily a change in task-imposed load.
3. **Performance under load:** sleep duration changes accuracy, reaction time,
   or stability while task load is held or manipulated.

### Proposed field/evidence changes

- Do not reuse one mechanism across all three alternatives.
- Require task, load manipulation, measurement type, prior sleep dose,
  circadian phase, stimulant use, and population boundaries.
- Obtain alternative-specific evidence; current construct sources do not
  adjudicate the causal proposition.
- Keep polarity unresolved if the selected endpoint scale makes “higher”
  ambiguous.

### Identity and unresolved decision

No exact V1 replacement proposition is selected. Retaining `PSY-057` with a
clarified experienced-load meaning might preserve the ID; changing to a
resource or performance endpoint requires a new ID. This governance-sensitive
construct choice remains non-governed and `NOT_ELIGIBLE`.

## `REL-REV-BIO-F01-B05` — review of `REL-ENV-040`

### Current governed record

`ENV-039` Ambient Noise Level `CAUSES` `BIO-002` Sleep Continuity, negative,
active V3, with generic source `SRC-508` and an unspecified exposure pattern.

### Exact proposed V1 proposition

Higher average nighttime environmental-noise exposure can reduce Sleep
Continuity in the exposed population, with source type, indoor/outdoor metric,
measurement period, event distribution, background level, setting, and
individual sensitivity explicitly bounded.

### Proposed field/evidence changes

- Keep `ENV-039` reserved for an average-level exposure claim.
- Add direct sleep-noise syntheses `SRC-530` and `SRC-531`, distinguishing
  average `Lnight`-type evidence from event-maximum awakening evidence.
- Tighten the cross-level exposure mechanism from physical setting to person.
- Do not fold `ENV-041` Noise Intermittency into this endpoint. The separately
  governed-inactive `REL-V1-BIO-F01-004` represents event/intermittency
  semantics and must be reconciled before activation to avoid duplicate
  propagation.
- Leave universal dose response, lag, persistence, and generalization across
  all noise sources unsupported.

### Identity and unresolved decision

The ID may remain stable if the claim stays average ambient level → continuity.
Changing the source to `ENV-041` would be a different proposition and would
duplicate the newly materialized inactive record. No current record is changed
at this checkpoint.
