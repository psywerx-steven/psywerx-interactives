# BIO-F01 baseline

**Audit ID:** `AUD-BIO-F01-RI-V1-20260905-001`

**Family:** `BIO-F01 — Sleep & Circadian Regulation`

**Layer:** Biological

**Frozen commit:** `5001611852107f2b95b8f722c71224dc7a538d47`
**Status:** Frozen audit input; no classification or canonical scientific content changed

## Frozen contracts and registers

| Item | Frozen value |
| --- | --- |
| Driver contract | Driver Schema v1.1 |
| RDS contract | Relational/Derived State Schema v0.1 |
| Relationship contract | Relationship V1 `1.0.0`; V3 remains the current scientific corpus |
| Intervention contract | Intervention V1 `1.0.0` |
| Source register | v1.0; 529 records; SHA-256 `f1aae4135ac049e223ae65a66a24a6dfc2c28e911add59ce11df34e9c0af3615` |
| Entity dataset | SHA-256 `74f88110911280bc6d508da56af824b63db4c11d741223b694aa7ac18734cf99` |
| Relationship dataset | SHA-256 `759f90446ff5f6e27d496e3e3603bb44045f7f0abf4770e4c012c5e4d974ba51` |

The Family definition is “Variables governing sleep amount, continuity,
circadian timing, and sleep–wake transitions.” Its governed exclusion places
external schedules and light conditions outside the Family, even though they
may causally affect Family members.

## Membership inventory

Mechanical extraction found 11 primary members: 6 Drivers and 5 RDS.

| ID | Type | Canonical name | Definition | Mechanism / current metadata | Indicators | Governed source references |
| --- | --- | --- | --- | --- | --- | --- |
| `BIO-001` | Driver | Sleep Duration | Amount of sleep obtained over a defined interval relative to physiological sleep need. | Homeostatic sleep pressure and altered neural function affect vigilance, working memory, executive control, and response stability. | Sleep/wake history, actigraphy, polysomnography, diary, PVT, subjective sleepiness/fatigue | `SRC001`–`SRC004` |
| `BIO-002` | Driver | Sleep Continuity | Degree to which a sleep period is maintained without awakenings, fragmentation, or loss of restorative architecture. | Fragmentation alters restorative processes and can reduce daytime alertness, memory, and performance. | Polysomnography, actigraphy, wake after sleep onset, sleep efficiency, apnea indices | `SRC005`, `SRC006` |
| `BIO-004` | Driver | Endogenous Circadian Phase | Current position within the endogenous circadian cycle organizing time-of-day variation in physiological readiness. | Circadian oscillations alter arousal and cognitive efficiency. | DLMO when available; clock time, chronotype, and sleep history are contextual proxies, not interchangeable measures | `SRC009`, `SRC011` |
| `BIO-005` | Driver | Sleep Inertia Severity | Magnitude of transient cognitive and motor impairment following awakening. | Incomplete restoration of alertness networks after waking. | Time since awakening, performance tests, subjective alertness | `SRC010` |
| `BIO-073` | Driver | Chronotype | Relatively stable earlier-versus-later timing phenotype or preference shaped by circadian, homeostatic, developmental, genetic, and environmental influences. | Metadata fields are blocked/incomplete in the governed migration baseline. | None governed | None |
| `BIO-074` | Driver | Physiological Sleep Need | Individual amount and composition of sleep biologically required over a specified interval for defined outcomes under stated conditions. | Metadata fields are blocked/incomplete; need is not one universally measurable number. | None governed | None |
| `BIO-003` | RDS | Circadian Timing Alignment | Alignment between internal circadian phase and the timing of sleep, work, meals, light exposure, and required behavior. | Derived by comparing `BIO-004` with explicit external timing requirements. | DLMO, core temperature, work schedule, actigraphy | `SRC006`–`SRC008` |
| `BIO-006` | RDS | Chronotype–Schedule Fit | Fit between preferred biological timing and externally required schedules. | Derived by comparing `BIO-073` with an explicit required schedule. | Morningness-eveningness scales, midsleep timing, social-jetlag metrics | `SRC009`, `SRC011` |
| `RDS-0002` | RDS | Sleep Architecture Composition | Composition and organization of stages and cycles in a specified sleep episode. | Derived from a time-indexed sleep-stage classification sequence. | None governed | None |
| `RDS-0003` | RDS | Sleep Sufficiency | Degree to which obtained sleep meets estimated physiological need for a specified interval and outcome criterion. | Ratio/extension using `BIO-001` and `BIO-074`. | None governed | None |
| `RDS-0004` | RDS | Cumulative Sleep Deficit | Accumulated sleep shortfall over specified intervals under explicit accumulation and recovery rules. | Temporal-pattern derivation using serial `BIO-001`, `BIO-074`, and an accumulation/recovery rule. | None governed | None |

`BIO-073`, `BIO-074`, `RDS-0002`, `RDS-0003`, and `RDS-0004` retain
partial governed migration metadata and named blocked fields. This pilot does
not fill those fields or treat missing metadata as evidence of absence.

## Alias and crosswalk inventory

There are 28 typed alias records incident to BIO-F01 members. They are search
or deprecated-term aids, not equivalence assertions. The most consequential
clusters are:

- `BIO-001`: acute total sleep deprivation, all-nighter, chronic sleep
  restriction, extended wakefulness, repeated partial sleep restriction,
  sleep debt, sleep loss, and deprecated “Sleep Quantity”;
- `BIO-002`: disrupted sleep, poor sleep quality, sleep continuity, and sleep
  fragmentation / poor sleep continuity;
- `BIO-003`: deprecated “Circadian Alignment,” circadian misalignment,
  biological-night work, jet lag, and shift work;
- `BIO-004`: adverse circadian phase / time-of-day vulnerability, deprecated
  “Circadian Phase,” circadian phase, and time-of-day effect;
- `BIO-005`: awakening impairment, post-waking grogginess, and sleep inertia;
- `BIO-006`: chronotype mismatch, deprecated “Chronotype–Schedule Alignment,”
  chronotype–schedule mismatch / social jetlag, and social jetlag; and
- `RDS-0004`: sleep debt, shared with `BIO-001` as a related-search alias with
  an explicit warning that debt is not necessarily conserved or linear.

Four governed crosswalks apply: `CW-0001` (`BIO-003`, Driver→RDS), `CW-0002`
(`BIO-006`, Driver→RDS), `CW-0035` (`BIO-001`, rename), and `CW-0036`
(`BIO-004`, rename). No crosswalk is changed by the pilot.

## RDS derivation trace

The derivation version for this audit is RDS Schema v0.1 at the frozen commit.
No entity record carries a more granular derivation-version identifier, so the
commit hash is the immutable specification reference.

| RDS | Required inputs | Derivation and window | Shared-input / causal-participation review | Exogenous-risk disposition |
| --- | --- | --- | --- | --- |
| `BIO-003` | `BIO-004` plus `EXTERNAL_TIMING_REQUIREMENTS` | Alignment convention over a declared interval; phase measure, external requirements, and update rule required | One outgoing causal V3 edge, `REL-BIO-001`, to `BIO-001`; the derivational edge from `BIO-004` is absent | High review priority: `REL-BIO-001` can mistakenly execute the calculated fit as an independent root |
| `BIO-006` | `BIO-073` plus `REQUIRED_SCHEDULE` | Fit rule; instrument, schedule, reference period, time zone, and convention required | One derivational edge, `REL-RDS-0016`; no causal edge | No current exogenous causal use |
| `RDS-0002` | External `SLEEP_STAGE_TIME_SERIES` | Stage proportions, sequence, transitions, and cycles within an explicitly bounded sleep episode | No relationship records | No current exogenous causal use; external input provenance is mandatory at analysis time |
| `RDS-0003` | `BIO-001`, `BIO-074` | Ratio or stated multidimensional extension over an aligned interval and outcome criterion | Two correct derivational records; shares both inputs with `RDS-0004` | No current causal use; do not propagate it alongside its inputs without reconciliation |
| `RDS-0004` | Serial `BIO-001`, `BIO-074`, `ACCUMULATION_RECOVERY_RULE` | Temporal accumulation with explicit recovery, decay, oversleep-credit, missing-interval, and uncertainty rules | Two correct derivational records; shares both entity inputs with `RDS-0003` | No current causal use; must never be initialized as independent sleep debt |

## Incident relationship baseline

There are 11 active incident records: six causal and five derivational. Of the
causal records, one is internal, three are same-Layer cross-Family, and two are
cross-Layer. All five derivational records are internal.

| Scope | Relationship IDs |
| --- | --- |
| Internal causal | `REL-BIO-001` |
| Internal derivational | `REL-RDS-0016`–`REL-RDS-0020` |
| Same-Layer outgoing | `REL-BIO-002`, `REL-BIO-003` to `BIO-F05` |
| Same-Layer incoming | `REL-BIO-009` from `BIO-F05` |
| Cross-Layer outgoing | `REL-BIO-021` to Psychological `PSY-F06` |
| Cross-Layer incoming | `REL-ENV-040` from Physical/Environmental `ENV-F06` |

All 450 active V3 records, including these 11, project conservatively as V1
`INCOMPLETE` / `LEGACY_ONLY`; that compatibility status does not revoke their
existing V3 authority. Candidate records in the pilot are physically excluded
from causal traversal.
