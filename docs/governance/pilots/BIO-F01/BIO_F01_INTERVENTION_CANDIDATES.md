# BIO-F01 intervention candidates

> Governance checkpoint 001 materialized approved identities/effects under
> canonical `INT-V1-*` and `IE-V1-*` IDs. These candidate copies remain for
> lineage only. The generic acoustic umbrella and receiver-level replacement
> candidate remain non-governed.

The search began with each BIO-F01 Driver and its mechanism. External method
taxonomies were not used as the organizing hierarchy. Every identity and
effect below is non-governed and `NOT_ELIGIBLE`.

## Driver-by-Driver search coverage

| Driver | Baseline modifiability | Search result |
| --- | --- | --- |
| `BIO-001` Sleep Duration | High | Supported candidates across behavioral sleep extension, protected scheduling, and delayed school-start policy. CBT-I was not treated as a generic duration intervention because objective duration effects conflict by measure and may initially decrease. |
| `BIO-002` Sleep Continuity | High | Supported candidates for CBT-I in chronic insomnia and nighttime acoustic attenuation in noise-exposed settings. Etiology-specific treatments such as PAP were reviewed but not generalized to all continuity problems. |
| `BIO-004` Endogenous Circadian Phase | Moderate | Timed bright light and timed melatonin retained. Direction is context-dependent because the phase-response curve and administration timing determine advance versus delay. |
| `BIO-005` Sleep Inertia Severity | High | Pre-awakening caffeine and post-awakening light retained as research-needed effects. Reviews do not support a universal reactive countermeasure; safety-critical delay after awakening remains a risk-control practice rather than a Driver-changing effect. |
| `BIO-073` Chronotype | Metadata incomplete | Search found no adequately supported, ethically unambiguous direct manipulation of the relatively stable phenotype distinct from changing phase, schedule, or fit. No InterventionEffect created. |
| `BIO-074` Physiological Sleep Need | Metadata incomplete | Search found no defensible direct intervention to reduce biological need as defined. Stimulants can mask sleepiness without reducing need; sleep extension meets need but does not target need itself. No InterventionEffect created. |

The two “none found” results are valid coverage outcomes, not missing-data
fillers. Their ontology metadata remains unchanged.

## Deduplicated Intervention identities

| ID | Identity | Kind / category | Lifecycle | Identity boundary |
| --- | --- | --- | --- | --- |
| `INT-CAND-BIO-F01-001` | Behavioral sleep-extension protocol | Atomic / Training or skill | `REVIEW_READY` | Planned opportunity expansion plus adherence support; context and achieved duration belong in effects. |
| `INT-CAND-BIO-F01-002` | Protected sleep-opportunity scheduling | Atomic / Policy, rule, or standard | `RESEARCH_NEEDED` | Organizational protection of sleep opportunity; roster implementations remain effect context. |
| `INT-CAND-BIO-F01-003` | Delayed school start-time policy | Atomic / Policy, rule, or standard | `REVIEW_READY` | Materially distinct education policy, not another generic sleep-extension identity. |
| `INT-CAND-BIO-F01-004` | Stimulus-control therapy for insomnia | Atomic / Training or skill | `REVIEW_READY` | CBT-I component; no component effect is inferred from package evidence. |
| `INT-CAND-BIO-F01-005` | Sleep-restriction therapy for insomnia | Atomic / Training or skill | `REVIEW_READY` | CBT-I component; clinically different from behavioral sleep extension. |
| `INT-CAND-BIO-F01-006` | Cognitive behavioral therapy for insomnia package | Package / Service or support | `REVIEW_READY` | Composes `004` and `005`; package effect has its own evidence. The component list is minimum V1 identity, not a claim that CBT-I has only two possible components. |
| `INT-CAND-BIO-F01-007` | Timed bright-light exposure | Atomic / Biological or clinical | `REVIEW_READY` | One reusable action identity supports separate phase and sleep-inertia effects. Timing/intensity/spectrum/duration stay effect-specific. |
| `INT-CAND-BIO-F01-008` | Timed exogenous melatonin administration | Atomic / Biological or clinical | `REVIEW_READY` | Dose, formulation, timing, population, and target remain effect context. |
| `INT-CAND-BIO-F01-009` | Nighttime acoustic attenuation | Atomic / Environmental or choice architecture | `RESEARCH_NEEDED` | Unresolved umbrella spanning source, transmission/path, and receiver mechanisms; not governed. |
| `INT-CAND-BIO-F01-010` | Pre-awakening timed caffeine delivery | Atomic / Biological or clinical | `REVIEW_READY` | Distinct from ordinary post-awakening caffeine because delayed release/timing is part of the action. |
| `INT-CAND-BIO-F01-011` | Nighttime personal acoustic protection | Atomic / Environmental or choice architecture | `RESEARCH_NEEDED` | Receiver-level candidate split from `009`; evidence and alarm-safety boundaries remain under review. |

## InterventionEffect candidates

| Effect | Exact Driver target | Mode / direction | Population and context | Evidence / uncertainty | Lifecycle |
| --- | --- | --- | --- | --- | --- |
| `IE-CAND-BIO-F01-001` | `BIO-001` | Change level / increase | Habitually short-sleeping adolescents or adults where opportunity can expand | Behavioral extension meta-analysis supports longer sleep with very high heterogeneity and incomplete intervention reporting. | `REVIEW_READY` |
| `IE-CAND-BIO-F01-002` | `BIO-001` | Change level / increase | Shift/duty systems able to protect rest | Roster-specific evidence is low/very-low certainty; compression elsewhere may erase benefit. | `RESEARCH_NEEDED` |
| `IE-CAND-BIO-F01-003` | `BIO-001` | Change level / increase | Middle/high-school students after a delayed mandatory start | Reviews show longer sleep, largely in natural experiments; transport and activity schedules are boundaries. | `REVIEW_READY` |
| `IE-CAND-BIO-F01-004` | `BIO-002` | Change level / increase | Adults with chronic insomnia receiving clinician-led or validated digital CBT-I | Strong subjective-continuity evidence; objective PSG/actigraphy changes are smaller or inconsistent. Initial time-in-bed restriction can increase sleepiness. | `REVIEW_READY` |
| `IE-CAND-BIO-F01-005` | `BIO-004` | Change level / context-dependent | People requiring a defined phase shift under a timed-light protocol | Experimental phase resetting is established; desired direction depends on phase-response timing. | `REVIEW_READY` |
| `IE-CAND-BIO-F01-006` | `BIO-004` | Change level / context-dependent | Delayed or otherwise mistimed phase under timed dosing | Meta-analysis/RCT evidence supports selected populations; phase-shifting and sleep-promoting effects must be separated. | `REVIEW_READY` |
| `IE-CAND-BIO-F01-007` | `BIO-002` | Change level / increase | Noise-exposed sleepers; receiver-level personal protection only | Evidence is ICU-heavy; identity, tolerance, alarm audibility, and subjective/objective differences remain unresolved. It does not apply to source/path controls. | `RESEARCH_NEEDED` |
| `IE-CAND-BIO-F01-008` | `BIO-005` | Change level / decrease | Sleep-restricted healthy adults with a planned awakening | One small crossover trial and a review; formulation-specific with subsequent-sleep and adverse-effect risks. | `RESEARCH_NEEDED` |
| `IE-CAND-BIO-F01-009` | `BIO-005` | Change level / decrease | Adults exposed to bright light just after awakening | Subjective alertness may improve, but objective performance benefit is not convincing. | `RESEARCH_NEEDED` |

No relationship-targeted effect was retained, so no candidate invokes the
`mechanisticDriverIds` requirement. The search considered buffering or
amplifying sleep-loss pathways, but no exact governed causal edge had evidence
sufficiently specific for a relationship-targeted effect.

## RDS outcome mappings

No RDS is a direct target. RDS references are downstream/recalculated outcomes:

- sleep-extension and protected-opportunity effects may recalculate
  `RDS-0003` Sleep Sufficiency and `RDS-0004` Cumulative Sleep Deficit using
  `BIO-001` and the governed need/window rules;
- delayed school start may additionally recalculate `BIO-006`
  Chronotype–Schedule Fit because the required schedule changes;
- timed light and timed melatonin may recalculate `BIO-003` Circadian Timing
  Alignment only after `BIO-004` and the external timing requirements are
  measured; and
- no effect claims a direct change to `RDS-0002` Sleep Architecture
  Composition.

There are nine RDS outcome references across five effects, covering four
distinct RDS. These are not additional causal edges or automatic favorable
outcomes.

## Modality and category coverage

The nine effects use four governed delivery modalities: human-delivered,
digital/automated, organizational/policy process, and physical environment.
The ten identities span training/skill, policy/rule, service/support,
biological/clinical, and environmental/choice-architecture categories. No
quota was used, and no unsupported category was populated for balance.

## Risk and implementation cautions

- Light and melatonin can shift phase in the wrong direction when mistimed.
- Melatonin product quality, formulation, interactions, and age/comorbidity
  restrict generalization.
- Sleep-restriction therapy is not sleep deprivation as an unsupervised
  general intervention; transient sleepiness is a safety concern.
- Caffeine may improve awakening performance while worsening subsequent sleep.
- Acoustic attenuation must preserve safety-critical alarm audibility.
- School/work schedule policies have distributional, transportation,
  caregiving, staffing, and legal implications not captured by an effect-size
  summary.
