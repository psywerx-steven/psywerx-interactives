# BIO-F01 completeness report

Completeness metrics are review flags. They do not prove that a missing edge,
intervention, or metadata value exists.

## Graph structure

### Governed active causal degree

| BIO-F01 entity | In-degree | Out-degree | Total | Flag |
| --- | ---: | ---: | ---: | --- |
| `BIO-001` Sleep Duration | 1 | 2 | 3 | Connected; receives the sole internal RDS causal edge |
| `BIO-002` Sleep Continuity | 2 | 1 | 3 | Connected across Biological and Environmental Families |
| `BIO-003` Circadian Timing Alignment | 0 | 1 | 1 | RDS outgoing-source review required |
| `BIO-004` Endogenous Circadian Phase | 0 | 0 | 0 | Isolated in causal graph; derivational dependency is missing |
| `BIO-005` Sleep Inertia Severity | 0 | 0 | 0 | Isolated; two internal causal candidates nominated |
| `BIO-006` Chronotype–Schedule Fit | 0 | 0 | 0 | Acceptable RDS outcome-only state at baseline |
| `BIO-073` Chronotype | 0 | 0 | 0 | Causally isolated; association candidate only |
| `BIO-074` Physiological Sleep Need | 0 | 0 | 0 | Causally isolated; derivational input only |
| `RDS-0002` Sleep Architecture Composition | 0 | 0 | 0 | External-series-derived state; no causal claim nominated |
| `RDS-0003` Sleep Sufficiency | 0 | 0 | 0 | Outcome/derived state only |
| `RDS-0004` Cumulative Sleep Deficit | 0 | 0 | 0 | Outcome/derived state only |

There is one internal, three same-Layer cross-Family, and two cross-Layer
governed causal incident records. The Family is not isolated, but causal
coverage is concentrated on duration and continuity. No BIO-F01 member is a
suspicious high-degree hub: the maximum Family-member degree is three. The
external target `BIO-026` Cognitive Fatigue is the Biological Layer’s current
highest-degree node (degree eight) and receives both duration and continuity
edges; its broad endpoint semantics deserve review.

No exact duplicate or same-scope polarity contradiction was found among the 11
incident baseline records or nine candidates. Two plausible intermediary
chains were flagged, but neither became a CausalPathway because pathway-specific
mediation evidence was absent.

## RDS integrity

| Check | Result |
| --- | --- |
| RDS with an explicit derivation specification | 5/5 |
| RDS constituent/entity IDs resolvable | 5/5 |
| Required external parameter types declared where applicable | 4 parameter occurrences across 4 RDS |
| Missing machine-readable derivational dependency | 1: `BIO-003 DERIVED_FROM BIO-004` |
| Governed causal RDS source claims | 1: `REL-BIO-001` |
| RDS source claims receiving an audit disposition | 1/1 |
| Direct RDS InterventionEffect targets | 0 |
| Candidate causal edges with any RDS endpoint | 0 |

`REL-BIO-001` is the only exogenous-root/double-propagation risk. It remains
governed V3 content, but its V1 execution must stay incomplete until derivation
version, calculation scope, temporal/mechanistic independence, and aggregate
reconciliation are human-reviewed. `RDS-0003` and `RDS-0004` share duration and
need inputs; no candidate propagates both an RDS and its constituents.

## Intervention coverage

| Metric | Result |
| --- | --- |
| BIO-F01 Drivers searched | 6/6 |
| Drivers with effect candidates | 4/6 |
| Drivers with documented no adequately supported direct intervention | 2: Chronotype and Physiological Sleep Need |
| Intervention identities | 10 |
| InterventionEffect candidates | 9 |
| Governed delivery modalities represented | 4 |
| Governed identity categories represented | 5 |
| Identities with no direct effect record | 2: CBT-I components `004` and `005`; intentionally not inferred from package evidence |
| Effects lacking exact Driver target | 0 |
| Effects lacking required mechanistic Driver linkage | 0; no relationship-targeted effect exists |
| Direct RDS target violations | 0 |
| Distinct RDS used only as outcomes/recalculated states | 4 |

Sleep Duration has three modalities/contexts, Sleep Continuity two,
Endogenous Circadian Phase two, and Sleep Inertia Severity two. This is useful
coverage diversity, not proof of exhaustiveness. Chronotype and Physiological
Sleep Need remain valid negative search results.

## Evidence quality

| Metric | Result |
| --- | --- |
| Candidate assertions with normalized EvidenceAssessment | 18/18 Relationship/Moderation and Effect assertions |
| EvidenceAssessments resolving current canonical source IDs | 7/18 |
| EvidenceAssessments using supplemental pilot references pending source registration | 11/18 |
| Evidence rationale coverage | 18/18 |
| Population/context coverage | 18/18 at scoped summary level; detailed study populations are in the research log |
| Conflicting/null evidence explicitly represented | 6/18 materially mixed/insufficient assessments; limitations and uncertainty present in all 18 |
| Confidence | 2 high, 10 moderate, 6 low |
| Evidence disposition | 13 supports, 2 mixed, 3 insufficient |

The source-registration gap is administrative/scientific-governance work, not
permission to copy supplemental citations into the governed source register.
Candidate effect estimates remain null because incomparable protocols should
not be collapsed to graph weights.

## Lifecycle and governance

Across 46 candidate records:

| State | Count |
| --- | ---: |
| `CANDIDATE` | 0 |
| `RESEARCH_NEEDED` | 13 |
| `REVIEW_READY` | 33 |
| `NEEDS_GOVERNANCE_INPUT` | 0 |
| New `GOVERNED` | 0 |
| New `ACTIVE` | 0 |

All 46 have `activationStatus: NOT_ELIGIBLE` and automated transition
provenance. The candidate workspace is `productionGraphEligible: false`; V1
validation confirms it contributes no production causal traversal.

## Open flags for human review

- Five existing causal records have revision-candidate dispositions, chiefly
  for source fit, endpoint semantics, or RDS safeguards.
- One missing derivational record is review-ready.
- Two causal candidates rely on supplemental sources not yet in the governed
  register; all supplemental-source effects likewise require source governance
  before activation.
- The phase moderation record and continuity→persistent-pain record remain
  research-needed.
- No CausalPathway met D05 evidence requirements.
- Candidate coverage does not establish graph completeness, especially for
  external schedule/light mechanisms and clinical etiologies.
