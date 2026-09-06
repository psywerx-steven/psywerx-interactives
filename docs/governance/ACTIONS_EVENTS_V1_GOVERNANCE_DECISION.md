# Actions & Events V1 architecture decision

Decision ID: `GOV-ACTIONS-EVENTS-V1-2026-09-06`

Effective date: 2026-09-06

Actor class: **authorized human governor**
Authorization: the explicit human instruction authorizing AE01–AE12 and bounded
end-to-end implementation, supplied for PR #15 at
`3331273fcfd72121fe831904c282b87c372eaf55`. Scientific baseline:
`2636dd9a8b7bad1da3d7dfa21db5fe877f4de4e1`.

This governance decision authorizes architecture semantics and bounded
implementation only. It does not approve or activate new scientific
Actions/Events effects or Relationships. Existing D01–D14, D11/D12 lifecycle
rules, BIO-F01 decisions, and v0.3 unresolved items retain their authority.

## Exact outcomes

| ID | Outcome | Governed semantics |
|---|---|---|
| AE01 | APPROVE | Actions & Events umbrella; HappeningType, Occurrence, EffectAssertion; Intervention remains a deliberate subset |
| AE02 | APPROVE | Overlapping ACTION/EVENT/EXPOSURE/PROCESS tags, independent retrieval domains |
| AE03 | APPROVE | Independent origin/target Layers, actor, intention, actor-relative control, pattern, timing/dose/duration/reach and declared-system externality |
| AE04 | APPROVE | DRIVER/RELATIONSHIP exact targets only; universal RDS safeguards; no generic context target |
| AE05 | MODIFY/APPROVE-AS-MODIFIED | Eleven factored effect properties and constrained descriptors below; reach/distribution/subgroups are qualifiers |
| AE06 | APPROVE | Assertion-level sourceFindings before synthesis; independent semantics, basis, production, disposition, confidence, clarity, provenance and use |
| AE07 | APPROVE | OBSERVED/PLANNED/HYPOTHETICAL occurrence; occurrence evidence never establishes effects; reusable effects need no episode |
| AE08 | APPROVE | Driver change, exact-edge modification and moderator route; explicit shared contribution, no automatic sums |
| AE09 | APPROVE | Lossless same-identity read bridge; preserve original IDs, evidence, status, package and lineage; no wholesale migration |
| AE10 | MODIFY/APPROVE-AS-MODIFIED | Separate scientific/model/practitioner-use outputs, with explicit control, prerequisites, feasibility, legal, ethical/risk and applicability checks |
| AE11 | APPROVE | Linked locally ready Family relationship Pass A and Actions/Events Pass B; stable cross-Family ownership/deduplication |
| AE12 | APPROVE | Govern/merge architecture, implement additive contracts/bridge/runner/candidates, synthetic eight-Layer validation, readiness report, then stop |

## Identity, scope and origin

A HappeningType describes a reusable happening/action/exposure/process, not a
Driver variable or an efficacy claim. An Occurrence describes one realization;
an EffectAssertion describes one contextual claim with an exact target. Identity
and occurrence alone never imply causality or efficacy. Kind tags may overlap.

Retrieval domains include deliberate intervention, routine/unintended activity,
external shock, environmental exposure, institutional/structural change,
technological change, social/network process, informational exposure and
biological/physiological process. They are not new Layers. All eight existing
Layers may be origin tags, separately from resolved target Layers. An external
event may be deliberate for another actor; external never implies random,
unconfounded, naturally exogenous or unintended. Discrete, repeated, continuous,
gradual, cumulative and cyclic patterns are supported.

## AE05 exact effect profile

| Property | Governed change descriptors |
|---|---|
| LEVEL | INCREASE, DECREASE; STATE_DEPENDENT when no universal direction exists |
| VARIABILITY | INCREASE, DECREASE, STABILIZE, DESTABILIZE |
| RATE | ACCELERATE, DECELERATE |
| THRESHOLD | RAISE, LOWER |
| TIMING | EARLIER, LATER, SHORTER_LAG, LONGER_LAG |
| PERSISTENCE | PROLONG, SHORTEN, ACCUMULATE, DECAY, ALTER_RECOVERY, ALTER_REVERSIBILITY |
| RELATIONSHIP_STRENGTH | AMPLIFY, ATTENUATE, BUFFER, SUPPRESS |
| RELATIONSHIP_DIRECTION | REVERSE, STATE_DEPENDENT |
| ENABLEMENT | ENABLE, DISABLE |
| FUNCTIONAL_SHAPE | LINEAR, THRESHOLD, SATURATING, U_SHAPED, INVERTED_U, CYCLIC, NON_MONOTONIC, OTHER_SPECIFIED |
| STRUCTURE | Scoped reconfiguration/increase/decrease/enable/disable of opportunities, constraints, resources, access, network ties or configuration |

STATE_DEPENDENT is a qualified non-universal change descriptor, never an inferred
sign. UNKNOWN and NO_DETECTED_CHANGE are non-result/bounded-null representations,
not weights. OTHER_SPECIFIED requires an explanation. Structural change concerns
the real world, not edits to the ontology. Reach/distribution, subgroup effects,
interaction/synergy/antagonism, intention versus observation and unintended
effects qualify the assertion. Beneficial/harmful/mixed/null evaluations require
a stakeholder and criterion.

Investigation states: NOT_INVESTIGATED, NOT_APPLICABLE, INSUFFICIENT_EVIDENCE,
SUPPORTED_EFFECT, SUPPORTED_NULL. Unknown is not zero; nonsignificance alone
cannot establish supported null. No quantitative precision is invented.

## Evidence and mechanism controls

Source findings retain source IDs, passages/result locators, access depth,
population, design, exposure, comparator, outcome/measurement, timing, result,
available estimate/uncertainty, limitations and shared study/dataset information.
Synthesis separately retains evidence disposition/strength, confidence, rationale,
conflicts and generalization limits. Evidence bases may be experimental,
quasi/natural experimental, longitudinal/cross-sectional observational,
qualitative, historical/case, synthesis, theoretical/mechanistic,
definitional/calculational, model inference, expert judgment or hypothesis.
Production distinguishes extraction, synthesis, model/pathway inference and
hypothesis. AI inference is never empirical observation, and evidence grades
never become graph weights. Source findings cannot silently disappear in synthesis.

All events retain Driver/Relationship-only direct targets. RDS can be measured,
reported or recalculated outcomes, never independently manipulated through an
event label. Preserve derivations, shared-input/denominator and double-counting
controls. CONTEXT_CONDITION and ALTER_CONTEXT remain prohibited.

An edge-target effect identifies one governed causal relationship and a
mechanistic Driver route before active use, retaining the existing D09 linkage
requirement. A moderator change and an edge modification can describe one
contribution: link them, independently evidence their assertions, never sum them
automatically or flatten moderation into an ordinary causal edge. Incomplete
mechanisms remain explicit; graph reachability does not establish mediation.

## Compatibility and use

Existing Intervention, InterventionEffect and EvidenceAssessment IDs, revisions,
scientific fields, statuses and provenance remain unchanged. A bridge view may
expose existing status only when explicitly declaring SAME_IDENTITY, adding zero
scientific propositions. Unsupported normalized fields remain null/incomplete.
Atomic/package and non-exhaustive component semantics remain intact; neither
package nor component effects are inferred. V3 and V1 projections count once.

Scientific-use, quantitative-model and practitioner-action eligibility are
derived views, not another lifecycle. D11/D12 human authority remains mandatory.
Practitioner use requires deliberate actionable identity, an eligible governed
active effect, actor-specific control, prerequisites, feasibility, legal and
ethical/risk constraints, and population/context applicability. An uncontrolled
disaster is never an available action merely because its effect is known.
Quantitative algorithms, ranking and optimization are not authorized.

## Workflow and bounded execution authorization

Pass A inventories membership/RDS and reviews existing internal, same-Layer
cross-Family and cross-Layer relationships before gap research. Pass B searches
all nine retrieval domains and eleven properties against locally reviewed
Drivers/edges; it need not await all 105 Families. Membership/definitions,
incident dispositions, RDS inputs, relevant scope and recorded gaps/deferrals
establish local readiness. Both passes exchange evidence/questions without
creating knowledge automatically. Ownership and identity deduplication remain
stable across Families; queue priority is scheduling only.

PR #15 and bounded infrastructure PRs may merge after local validation, CI and
independent diff review. Existing Pages automation may run after these authorized
merges; no manual deployment or deployment-setting change is authorized. The
implementation must finish with a scale-up readiness report and a Family #2
recommendation, not research. No B01–B05 revision, blocked v0.3 item, reclassification,
new scientific governance/activation, occurrence stream, new modeling algorithm,
recommendation/optimization or ontology-wide population is approved.

The prior proposal's PENDING approval fields are superseded by this exact record.
Prototype scientific fixtures remain SYNTHETIC / NON_PRODUCTION, NOT_ELIGIBLE.
