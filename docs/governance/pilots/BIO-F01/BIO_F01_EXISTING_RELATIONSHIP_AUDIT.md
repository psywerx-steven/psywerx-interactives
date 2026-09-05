# BIO-F01 existing relationship audit

**Audit ID:** `AUD-BIO-F01-RI-V1-20260905-001`

**Scope:** Every active Relationship V3 record incident to a BIO-F01 member
**Rule:** Audit dispositions are recommendations only; no governed proposition
was edited, retyped, superseded, or deactivated.

## Disposition summary

| Disposition | Count |
| --- | ---: |
| Retain as-is | 5 |
| Retain but V1 incomplete | 1 |
| Revision candidate | 5 |
| Retype candidate | 0 |
| Split candidate | 0 |
| Merge/duplicate candidate | 0 |
| Deprecation candidate | 0 |
| Research needed as sole disposition | 0 |
| Blocked | 0 |

“Retain as-is” applies only to scientific proposition identity and V3 content;
those records still need a future V1-native representation if V1 execution is
desired. “Revision candidate” never modifies the governed record.

## Causal records

All six causal records are directed V3 propositions with
`DIRECT_AT_STATED_RESOLUTION`. Their V1 projection has no
`causalClaimRole`; `legacyDirectness` is preserved but cannot control V1
execution. Numeric lag, persistence, normalized evidence rationale, and
conflict records are absent throughout.

| ID and proposition | Audit findings | Disposition |
| --- | --- | --- |
| `REL-BIO-001`: `BIO-003` Circadian Timing Alignment **CAUSES** `BIO-001` Sleep Duration, positive | Endpoint types are RDS→Driver, so V1 requires `HEIGHTENED_CAUSAL`. The mechanism text says misalignment and restriction “co-occur” and asks users to isolate effects; that is not a clean causal mechanism. `BIO-003` is calculated from phase plus external timing requirements, making exogenous execution and duplicate schedule/phase propagation material risks. Temporal order is plausible but not quantified. Sources concern shift work/misalignment, where schedule, light, and sleep opportunity remain bundled. | **Revision candidate.** Preserve V3 authority. A later governed revision must either complete RDS independence/reconciliation safeguards or replace the proposition with more exact Driver/schedule mechanisms; do not mechanically retype it. |
| `REL-BIO-002`: `BIO-001` Sleep Duration **CAUSES** `BIO-026` Cognitive Fatigue, negative | Driver→Driver and direction/polarity are coherent at person level. Sleep-restriction meta-analyses and experiments support fatigue, vigilance, and performance impairment, with task, dose, phase, stimulant use, and individual vulnerability as boundaries. The endpoint is broader than any one task. V1 fields remain incomplete and the current mechanism conflates fatigue with performance instability, but no proposition-identity change is presently justified. | **Retain but V1 incomplete.** Candidate completion should add evidence-specific estimands, boundary conditions, exposure pattern, lag, persistence, and conflict notes without changing the governed edge. |
| `REL-BIO-003`: `BIO-002` Sleep Continuity **CAUSES** `BIO-026` Cognitive Fatigue, negative | Driver→Driver is structurally legitimate. Controlled fragmentation studies support subsequent sleepiness and some performance impairment, but findings vary by test and one experiment found sleepiness without selected performance deficits. Current `SRC005`/`SRC006` are not proposition-specific: cognitive decline and shift-work reviews do not isolate continuity→fatigue. | **Revision candidate.** Retain the edge pending human review; propose a source/evidence-rationale revision and tighter outcome language, not automatic replacement. |
| `REL-BIO-009`: `BIO-028` Persistent Pain Burden **CONSTRAINS** `BIO-002` Sleep Continuity, negative | Driver→Driver and reciprocal physiology are plausible. Prospective meta-analyses support bidirectional broad sleep-problem/pain associations, but current `SRC033`/`SRC034` concern pain–executive/attention effects rather than sleep continuity. Pain condition, medication, insomnia, and measurement are crucial. | **Revision candidate.** Scientific proposition may be retained, but its current evidence packet does not directly support it; add direction-specific pain→continuity evidence before V1 completion. |
| `REL-BIO-021`: `BIO-001` Sleep Duration **CAUSES** `PSY-057` Cognitive Load, negative | Driver→Driver, cross-Layer. Sleep loss can impair working memory and interact with task load, but cognitive load is task demand/resource burden, not a generic synonym for impaired cognition. Current NIMH RDoC sources are broad construct references rather than evidence for this proposition. Direction and endpoint identity need sharper definition; sleep loss may reduce capacity while task load remains unchanged. | **Revision candidate.** Human review should decide whether the proposition concerns perceived/experienced load, working-memory availability, or performance under load. No retyping or endpoint substitution is authorized here. |
| `REL-ENV-040`: `ENV-039` Ambient Noise Level **CAUSES** `BIO-002` Sleep Continuity, negative | Cross-Layer Driver→Driver with an exposure mechanism. Systematic reviews find dose-related awakenings from nighttime transportation-noise events, but average level and event intermittency are distinct exposure dimensions. Current `SRC-508` is an IPCC health chapter, not the most direct sleep-noise evidence. The generic level-transition text should be replaced with explicit acoustic exposure in any V1 revision. | **Revision candidate.** Preserve V3 edge; propose direct sleep-noise evidence, event/average exposure separation, and context-specific lag/response semantics. |

### Causal completeness matrix

| Field | `REL-BIO-001` | `REL-BIO-002` | `REL-BIO-003` | `REL-BIO-009` | `REL-BIO-021` | `REL-ENV-040` |
| --- | --- | --- | --- | --- | --- | --- |
| Endpoint/type correct | Structurally yes; RDS risk | Yes | Yes | Yes | Endpoint meaning needs review | Yes |
| Direction/polarity defensible | Conditional | Yes | Yes | Plausible | Ambiguous construct interpretation | Yes |
| Mechanism adequate for V1 | No | Partial | Partial | Partial | No | Partial |
| Population/context explicit | Generic only | Generic only | Generic only | Generic only | Generic only | Generic only |
| Temporal order | Narrative | Narrative | Narrative | Narrative | Narrative | Narrative |
| Numeric lag/persistence | Missing | Missing | Missing | Missing | Missing | Missing |
| Normalized moderation | Missing | Missing | Missing | Missing | Missing | Missing |
| Contrary/null evidence | Missing | Missing | Missing | Missing | Missing | Missing |
| RDS safeguard required | Yes; incomplete | No | No | No | No | No |
| V1 complete / executable | No / legacy-only | No / legacy-only | No / legacy-only | No / legacy-only | No / legacy-only | No / legacy-only |

## Derivational records

These are noncausal dependencies and must never enter causal traversal.

| ID | Proposition | Derivation check | Disposition |
| --- | --- | --- | --- |
| `REL-RDS-0016` | `BIO-006` Chronotype–Schedule Fit **DERIVED_FROM** `BIO-073` Chronotype | Matches one required entity input; required schedule remains an external parameter. | **Retain as-is** |
| `REL-RDS-0017` | `RDS-0003` Sleep Sufficiency **DERIVED_FROM** `BIO-001` Sleep Duration | Matches numerator/input; interval and units must align. | **Retain as-is** |
| `REL-RDS-0018` | `RDS-0003` Sleep Sufficiency **DERIVED_FROM** `BIO-074` Physiological Sleep Need | Matches reference input; shared-denominator warnings must accompany analysis. | **Retain as-is** |
| `REL-RDS-0019` | `RDS-0004` Cumulative Sleep Deficit **DERIVED_FROM** `BIO-001` Sleep Duration | Matches serial obtained-sleep input; accumulation/recovery rule is separately required. | **Retain as-is** |
| `REL-RDS-0020` | `RDS-0004` Cumulative Sleep Deficit **DERIVED_FROM** `BIO-074` Physiological Sleep Need | Matches reference requirement; outcome criterion and uncertainty must align across intervals. | **Retain as-is** |

The baseline lacks the corresponding derivational dependency
`BIO-003 DERIVED_FROM BIO-004`, even though the governed RDS definition names
`BIO-004` as required. That gap is a new noncausal candidate, not a repair made
to the existing corpus.

## Duplicate, contradiction, and double-count review

- No exact duplicate among the 11 incident records was found.
- No same-scope polarity contradiction was found.
- `REL-BIO-001` is the principal aggregate/constituent propagation risk: the
  RDS combines endogenous phase with external timing, so downstream use must
  not also add phase and schedule contributions without reconciliation.
- `RDS-0003` and `RDS-0004` share `BIO-001` and `BIO-074`; simultaneous causal
  propagation through either RDS and its components would double count.
- `REL-BIO-009` describes a bidirectional mechanism in notes but stores only
  pain→continuity. A reverse candidate requires independent evidence and is
  assessed separately; narrative reciprocity is not a second edge.
