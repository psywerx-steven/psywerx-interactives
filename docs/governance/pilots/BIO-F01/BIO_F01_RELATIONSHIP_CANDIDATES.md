# BIO-F01 relationship candidates

> Governance checkpoint 001 materialized approved propositions under new
> canonical `REL-V1-*` IDs while retaining these candidate copies for lineage.
> The authoritative mappings and inactive status are recorded in
> `data/relationship-intervention-v1/materialization-manifest.json`.
> Candidates `005`, `007`, and `008` remain non-governed.

All records are non-governed, `NOT_ELIGIBLE`, and excluded from production
causal traversal. “Review ready” means the AI-prepared packet is ready for
human adjudication; it does not mean accepted science.

## Triage result

Twenty plausible propositions were explicitly triaged. Nine became
machine-readable Relationship candidates: five causal, two association, one
moderation, and one derivational. No temporal-transition or CausalPathway
candidate met the V1 threshold. Five hypotheses were rejected as category
errors or duplicates, and nine surviving questions remain research-needed
(three represented by Relationship records and six retained only in the
research queue). Research-needed is a lifecycle/queue status and overlaps
three of the nine retained records.

## New causal candidates

| Candidate | Proposition and review gate | Evidence rationale | Lifecycle | Recommendation |
| --- | --- | --- | --- | --- |
| `REL-CAND-BIO-F01-001` | More `BIO-001` Sleep Duration reduces `BIO-005` Sleep Inertia Severity; `STANDARD_CAUSAL` | The governed sleep-inertia review and controlled chronic-restriction study indicate that restricted prior sleep magnifies post-awakening impairment, especially during biological night. This is bounded, not a universal linear function. | `REVIEW_READY` | Review the causal proposition with explicit prior-sleep, phase, stage, task, and assessment-window scope. |
| `REL-CAND-BIO-F01-002` | `BIO-004` Endogenous Circadian Phase affects `BIO-005` Sleep Inertia Severity; `STANDARD_CAUSAL`, context-dependent polarity | Laboratory and review evidence indicate greater impairment near biological night/trough; phase is cyclic, so no universal positive/negative interpretation is valid. | `REVIEW_READY` | Approve only with cyclic/state-qualified interpretation; do not encode clock time as phase. |
| `REL-CAND-BIO-F01-003` | `BIO-061` Caffeine Effect Level constrains `BIO-001` Sleep Duration; `STANDARD_CAUSAL` | Controlled evidence summarized in `SRC086` supports sleep disruption from sufficiently late caffeine exposure while emphasizing timing, dose, metabolism, tolerance, and formulation. | `REVIEW_READY` | Review as a cross-Family exposure edge; do not infer that all caffeine exposure shortens all sleep. |
| `REL-CAND-BIO-F01-004` | `ENV-041` Noise Intermittency constrains `BIO-002` Sleep Continuity; `STANDARD_CAUSAL` | Systematic reviews find discrete nighttime transportation-noise events increase cortical awakenings. Intermittency is separable from `ENV-039` average level and may explain event-triggered fragmentation. | `REVIEW_READY` | Review alongside, not as a duplicate of, `REL-ENV-040`; require direct-source registration before activation. |
| `REL-CAND-BIO-F01-005` | More `BIO-002` Sleep Continuity reduces `BIO-028` Persistent Pain Burden; `STANDARD_CAUSAL` | Prospective meta-analyses support sleep-problem→pain direction, but exposures are broader than canonical continuity and residual confounding remains. | `RESEARCH_NEEDED` | Seek continuity-specific intervention or intensive-longitudinal evidence; do not activate from association alone. |

None has an RDS endpoint, so no candidate attempts to evade heightened RDS
review. Numeric lag, persistence, and functional form remain null rather than
being inferred from heterogeneous studies.

## Noncausal candidates

| Candidate | Semantics | Safeguards | Lifecycle | Recommendation |
| --- | --- | --- | --- | --- |
| `REL-CAND-BIO-F01-006` | Symmetric `ASSOCIATED_WITH`: `BIO-004` Endogenous Circadian Phase and `BIO-073` Chronotype | Canonically ordered endpoints; explicitly noncausal. Chronotype measures and DLMO correlate, but preference, observed sleep timing, phase, age, and schedule must not be collapsed. | `REVIEW_READY` | Review as an association only. Do not use it in causal traversal or treat chronotype as a phase measurement without protocol qualification. |
| `REL-CAND-BIO-F01-007` | Symmetric `ASSOCIATED_WITH`: `BIO-001` Sleep Duration and `BIO-002` Sleep Continuity | Flags shared scored epochs and sleep-efficiency/time-in-bed denominators. No generic strength is stored. | `RESEARCH_NEEDED` | Retain only if non-overlapping operationalizations and a scoped association estimate can be supplied. |
| `REL-CAND-BIO-F01-009` | `DERIVED_FROM`: `BIO-003` Circadian Timing Alignment from `BIO-004` Endogenous Circadian Phase | Restores the machine-readable dependency already explicit in the governed derivation specification; noncausal and non-executable. | `REVIEW_READY` | Review as a missing derivational record. External timing requirements remain mandatory and are not invented as an ontology entity. |

No `PRECEDES` record was retained. Prior sleep necessarily occurs before a
post-awakening assessment, but a separate precedence edge would add little
beyond the bounded causal/evidence timing and could be misread as a generic
construct sequence. No `TRANSITIONS_TO` record was retained: a statement such
as “low sleep duration transitions to high sleep inertia” wrongly suggests
that one construct becomes another and fails the qualified-state semantics.

## Moderation candidate

`REL-CAND-BIO-F01-008` proposes that `BIO-004` Endogenous Circadian Phase
moderates governed edge `REL-BIO-002` (Sleep Duration→Cognitive Fatigue).
Forced-desynchrony experiments show a sleep-dose × circadian-phase interaction
for vigilance performance, but vigilance is not automatically the same as the
governed Cognitive Fatigue endpoint. The candidate therefore remains
`RESEARCH_NEEDED`. It creates no `BIO-004→BIO-001` or
`BIO-004→BIO-026` edge and makes no joint-moderation claim.

## Pathway investigation

No CausalPathway candidate was created. Two graph-reachable chains were
examined:

- `ENV-039 → BIO-002 → BIO-026` using `REL-ENV-040` and `REL-BIO-003`; and
- `BIO-028 → BIO-002 → BIO-026` using `REL-BIO-009` and `REL-BIO-003`.

The sources reviewed do not provide pathway-specific mediation evidence with
aligned exposure, mediator, outcome, population, and timing. Graph
contiguity is insufficient under D05. Both remain research questions; neither
adds an edge or weight.

## Rejected / not-modeled hypotheses

| Hypothesis | Triage outcome | Reason |
| --- | --- | --- |
| Sleep Duration causes Sleep Sufficiency | Rejected as causal | `RDS-0003` is calculated from duration and need; causal representation would restate the formula. |
| Sleep Duration causes Cumulative Sleep Deficit | Rejected as causal | Serial duration is a constituent of `RDS-0004`; the dependency already exists as `REL-RDS-0019`. |
| Physiological Sleep Need causes Sleep Sufficiency or Cumulative Sleep Deficit | Rejected as causal | Shared denominator/reference input; use `REL-RDS-0018`/`0020`. |
| Low Sleep Duration `TRANSITIONS_TO` high Sleep Inertia Severity | Rejected temporal transition | Different ontology constructs do not literally transform into each other; the scientific claim is causal and is represented once as candidate `001`. |
| Circadian Timing Alignment→Sleep Duration as a second new edge | Rejected duplicate | A governed V3 proposition already exists as `REL-BIO-001`; proposed improvements belong in a revision decision, not a duplicate candidate. |

## Research queue not promoted to records

- Does Sleep Duration causally affect Sleep Continuity independently of shared
  episode scoring and time-in-bed constraints?
- Is the pain→continuity→fatigue chain supported by a formal longitudinal or
  interventional mediation analysis at aligned scope?
- Is the noise→continuity→fatigue chain supported by pathway-specific evidence
  rather than separate segment studies?
- Does Chronotype moderate a particular governed sleep/cognition edge after
  controlling endogenous phase and schedule fit?
- Should light spectral composition (`ENV-044`) have a distinct causal edge to
  `BIO-004`, or is intensity/timing information indispensable and currently
  missing from the Driver endpoint?
- Which ontology Driver best represents mandatory work/school timing so the
  schedule component of alignment RDS can participate without inventing a
  generic context object?
