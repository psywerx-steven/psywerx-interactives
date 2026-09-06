# Actions & Events: architecture decisions for human review

Status: PROPOSAL / NON_PRODUCTION. Every decision below is **PENDING**.
The synthetic prototype demonstrates structural feasibility only. It changes
no governed architecture, scientific record, activation rule or consumer.

## Decision table

| ID | Governance decision | Recommended option | Compatibility risk | Decision |
|---|---|---|---|---|
| AE01 | Umbrella and object boundaries | “Actions & Events” for people; HappeningType, Occurrence, EffectAssertion as technical names | Low if additive; terminology review required | PENDING |
| AE02 | Identity classification | Overlapping ACTION/EVENT/EXPOSURE/PROCESS tags; separate deliberate Intervention subset | Moderate if mapped as a mutually exclusive taxonomy | PENDING |
| AE03 | Origin, agency and boundary | Multiple origin Layers; target Layers derived from exact targets; actor-relative intention/control/boundary | Low; new metadata not inferred in migration | PENDING |
| AE04 | Direct targets and RDS | Retain DRIVER/RELATIONSHIP only for every effect, including non-intervention events | Low; preserves current safeguards | PENDING |
| AE05 | Full effect vocabulary | Eleven orthogonal properties plus constrained change descriptors and investigation outcomes | Moderate; new properties need production review | PENDING |
| AE06 | Evidence and inference | One assertion EvidenceAssessment with structured sourceFindings and separate synthesis | Moderate; additive normalization must preserve original evidence | PENDING |
| AE07 | Occurrence evidence | Evidence of occurrence separate from evidence of contextual consequences | Low; no occurrence required for reusable effect knowledge | PENDING |
| AE08 | Overlap and moderation | Exact edge targeting, mechanistic Driver linkage and explicit shared-contribution groups | Moderate; execution policy remains separate | PENDING |
| AE09 | Compatibility and packages | ID-stable additive references to current Interventions/effects; no migration in this proposal | Low with read-only links; high if IDs are reminted | PENDING |
| AE10 | Governance and use | Preserve D11/D12; separately calculate scientific/model/action eligibility | Low only if current activation rules remain intact | PENDING |
| AE11 | Relationship-first production workflow | Linked Family Pass A/Pass B with local readiness, shared ownership and deduplication | Low; queue is scheduling evidence only | PENDING |
| AE12 | Next implementation/pilot scope | Approve contract review first, then synthetic structural pilot and bounded compatibility implementation | Low; science/population separately authorized | PENDING |

## Exact recommendations and alternatives

### AE01 — Three scientific object boundaries

Recommend a reusable `HappeningType` for what may happen or be done, an
`Occurrence` for an observed/planned/hypothetical episode, and an
`EffectAssertion` for one scoped effect on one target. “Actions & Events” is
the preferred practitioner label; “Happening” is a technical umbrella that can
include continuous processes. It is not proposed as a new Driver class.
Evidence/provenance is normalized independently of type identity.

Alternative: expand Intervention to include every event. This minimizes new
names but makes disasters appear actionable and conflates agency with occurrence.
Alternative: separate Action, Event, Exposure and Process catalogs. This gives
familiar labels but duplicates overlapping identities and effect contracts.
The recommended common object with tags preserves distinctions with fewer roots.
Risk if wrong: evidence that an event happened is mistaken for proof of its
effects, or a variable such as temperature duplicates an exposure episode.

Proposed rule: a type describes an action/happening/exposure pattern, an
occurrence describes its realization and observation status, and an effect
assertion contains the target-specific claim. Neither identity nor occurrence
implies causality or efficacy. Approval: **PENDING**.

### AE02–AE03 — Overlapping tags and actor-relative metadata

Recommend `kindTags` from ACTION, EVENT, EXPOSURE and PROCESS, permitting
multiple values. Keep domain search tags A–I distinct from Layers: deliberate
interventions; routine/unintended activity; external shocks; environmental
exposure; institutional change; technological change; social/network process;
informational exposure; biological/physiological process. They support retrieval,
not mutually exclusive ontology membership. The prototype vocabulary is
provisional and not a replacement for existing Intervention categories.

Origin Layers may include any of the eight governed Layers and multiple values.
Affected Layers resolve independently from exact Driver/relationship targets.
Actor/source system, intentionality, controllability by a specified actor,
discrete/repeated/continuous/gradual/cumulative/cyclic pattern, timing, dose,
duration and reach are separate fields. Unknown control remains unknown; an
actor-specific control judgment needs context, prerequisites and provenance.
Internal/external/mixed status requires a declared system boundary.

Alternative: one combined category such as “external environmental shock.”
Compact labels lose the fact that one actor intentionally causes another's
external event. Alternative: unconstrained text only. Flexible but difficult
to search/validate. Recommend controlled small dimensions plus qualified text.
Proposed rule: external never entails random assignment, no confounding, or
causal exogeneity. Approval for both AE02 and AE03: **PENDING**.

### AE04 — Targets and RDS safety apply to every event class

Recommend retaining only DRIVER and RELATIONSHIP exact targets. A relationship
target resolves to one governed causal relationship and needs a canonical
mechanistic Driver linkage before activation. RDS references are outcomes,
MOEs, measurements or recalculated states, never directly manipulated effect
targets, whether the cause is deliberate or natural. Missing ontology grounding
stays research metadata or blocked pending a separate ontology decision.

Alternative: allow RDS direct targets for natural events. It looks convenient
for disaster burden or composite outcomes but makes an event label a loophole
for formula causality and independent aggregate updates. Alternative: create
generic context targets. It captures broad narrative but reverses governed D08/
D09 constraints and cannot reliably prevent duplicate propagation. Reject both
for minimum scope. No new target type is implemented as an exception.

Proposed rule: context changes resolve to named Drivers, governed moderation,
scope/prerequisites or relationship conditions; no CONTEXT_CONDITION target
and no ALTER_CONTEXT effect mode. Approval: **PENDING**.

### AE05 — Property of change and manner of change

Recommend EffectAssertion `property` values LEVEL, VARIABILITY, RATE, THRESHOLD, TIMING,
PERSISTENCE, RELATIONSHIP_STRENGTH, RELATIONSHIP_DIRECTION, ENABLEMENT,
FUNCTIONAL_SHAPE and STRUCTURE. A separate property-constrained change descriptor
captures increase/decrease, earlier/later, amplification/attenuation, enabling/
disabling, reversal or specified state-dependent shape. Population, measure,
contrast, time basis and uncertainty qualify the claim. Existing production V1
effect modes retain their current meanings until a separately approved adapter.

The full search checklist also asks about reach/distribution, subgroup effects,
interaction/synergy/antagonism, intended versus observed direction and unintended
beneficial/harmful/mixed/null outcomes. Valence requires a stakeholder/criterion;
it is not synonymous with positive/negative causal sign. Investigation state
distinguishes NOT_INVESTIGATED, NOT_APPLICABLE, INSUFFICIENT_EVIDENCE,
SUPPORTED_EFFECT and SUPPORTED_NULL in both the search log and the draft
assertion's `knowledgeStatus`. Unknown must not become numeric zero;
nonsignificance alone cannot establish supported null.

Alternative: one large flat enum (“increase-lag”, “decrease-strength”, etc.).
Simple to read initially but grows combinatorially and confuses property with
direction. Alternative: free text only. Scientifically expressive but poorly
checkable. Recommend the factored representation with explicit unknowns.
Functional shape permits cyclic/non-monotonic effects without universal sign.
Structural change concerns real-world opportunities/resources/ties, not edits
to ontology records. Approval: **PENDING**.

### AE06–AE07 — Evidence, inference and occurrence records

Recommend an assertion-linked `EvidenceAssessment` with `sourceFindings` and
`synthesis`. Each source finding retains source/passage or result locator,
actual access depth, population/design, comparator/measurement, timing,
support/null/contrary finding, uncertainty, limitations and dataset overlap.
Synthesis links those findings and records overall disposition and confidence
rationale. No numeric confidence or graph weight is generated.

Keep claim semantics, multiple evidence bases, production method, disposition,
confidence, clarity/completeness, provenance and governance/use independent.
Evidence bases include experimental, quasi/natural experimental, longitudinal,
cross-sectional, qualitative/historical/case, synthesis, theoretical/mechanistic,
definitional calculation, model/simulation, expert judgment and hypothesis.
Production method distinguishes extraction, synthesis, model/pathway inference
and proposed hypothesis. Completeness checks cover target, direction, mechanism,
population, context, timing, measurement and boundaries. A complete string is
not proof of scientifically adequate specification.

An OBSERVED occurrence needs occurrence-specific provenance. Its effects need
independent contextual evidence; a planned/hypothetical occurrence remains such.
Reusable effects need not cite one particular occurrence to exist.

Alternative: separate top-level EvidenceFinding and EvidenceSynthesis catalogs
now. Better reuse at large scale, but more identity/lifecycle coordination than
this prototype needs. Preserve stable finding IDs and defer root extraction.
Alternative: blanket event confidence. Easy display, scientifically misleading.
Alternative: only narrative evidence. Low implementation cost but obscures the
BIO-F01 mixed/null findings that motivated the present separation.

Proposed rule: preserve source findings before synthesis; association confidence
never changes semantics, model inference never becomes empirical observation,
graph reachability never demonstrates mediation, and occurrence evidence never
proves all consequences. Approval for AE06 and AE07: **PENDING**.

### AE08 — Effects, moderators and shared contributions

Recommend three expressible routes: event changes Driver; event modifies exact
causal edge; event changes moderator Driver which modifies an edge. The latter
two may be alternative encodings of one mechanism. Require shared-contribution
identity and non-additive/reconciliation semantics when they overlap. A documented
modification needs exact edge/revision, modified aspect, mechanism/Driver linkage,
conditions/timing and source-specific evidence. A hypothesis remains a hypothesis.

Alternative: encode every route as ordinary causal edges. Easy graph tooling,
but changes scientific meaning of moderation. Alternative: force all changes
through a fully specified mechanistic pathway. Strong discipline but blocks
valid direct contextual claims when intermediates remain unresolved. Recommend
bounded direct claims plus explicit overlap safeguards and honest incomplete
mechanisms. An execution package must choose/reconcile overlapping contributions;
the experimental catalog does not compute their sum. Approval: **PENDING**.

### AE09 — Existing V1 and BIO-F01 compatibility

Recommend an additive read-only bridge referencing existing Intervention IDs,
Effect IDs, EvidenceAssessment IDs, versions, sources and exact status snapshots.
Do not remint BIO-F01 identity IDs, infer missing timing/control metadata, change
governance provenance or copy an active status to a new proposed object. Existing
Intervention atomic/package meaning remains intact; CBT-I's modeled components
remain non-exhaustive. Package effects need independent evidence and are never
the sum of component effects. The four governed inactive BIO-F01 identities
remain inactive until separate authorized effects/activation decisions exist.

Alternative: migrate immediately into a generalized catalog. Offers one API but
would exceed scope and risk identity/evidence/status loss. Alternative: permanent
parallel independent catalogs. Avoids migration initially but encourages duplicate
action identities and inconsistent effects. Prefer reference bridge first,
then a separately governed lossless mapping/equivalence test before migration.
Existing legacy V3 and V1 projections remain one proposition. Approval: **PENDING**.

### AE10 — Authority, scientific use and practitioner control

Retain current lifecycle/activation/block fields and exact D12 transitions.
Automation may propose, research, compare, validate and prepare non-governed
records. It may materialize an exact already-authorized decision, never infer
authority from good evidence, schema validity or a simulated eligibility result.

Recommend separate eligibility outputs: scientific use, quantitative modeling,
and practitioner action use. A scientifically active effect need not supply a
numeric estimand/model, transfer to the present context, or be controllable by
the practitioner. An Intervention identity requires its own eligible effect
under existing activation rules; inactive components need not become active
merely because an active package references them. A disaster cannot become a
recommended action. The prototype reports only a dry run and changes no state.

Alternative: treat approval as all-purpose execution permission. Simpler but
confuses certainty, manipulability, ethical/feasibility constraints and model
assumptions. Alternative: invent a second lifecycle. Adds governance ambiguity.
Retain one lifecycle and separate use predicates. Approval: **PENDING**.

### AE11 — Relationship-first research and ownership

Recommend linked Pass A (review existing Family relationships then gaps) and
Pass B (reviewed Driver/edge-centered Actions/Events search). Readiness is local:
membership/definitions understood, incident records dispositioned, RDS inputs
traced, target edges sufficiently scoped, gaps/deferrals explicit. No requirement
for a complete ontology-wide graph precedes direct-effect research. Downstream
consequences remain separately evidenced or labeled inferences.

Keep governed Family ownership rules and add a shared cross-Family identity
steward for reusable types. Deduplicate exact scoped propositions and V3/V1
projections, use shared issue IDs, and consult endpoint/moderator Families.
Pass A evidence goes to a Pass B inbox; Pass B relationship gaps return to Pass A.
Human-action searches consider modifiability. Natural exposures/processes also
cover Drivers humans cannot easily manipulate.

Alternative: finish all 105 Families' relationship work before any effects.
Orderly but unnecessarily blocks evidence relevant to reviewed sections.
Alternative: start from a global action taxonomy. Fast catalog growth but weak
target grounding. Recommend linked local passes and queue coverage priorities,
not quotas. Queue ranks guide review effort without asserting missing science.
Approval: **PENDING**.

### AE12 — Minimum practical implementation and next pilot

Minimum after explicit architecture approval: versioned draft-to-production
contract review; isolated source-finding/synthesis support; read-only inventory
and candidate-template generation; typed candidate storage with no production
input path; exact target/RDS/overlap validators; actor-specific eligibility dry
run; ID-stable compatibility bridge and regression tests. No occurrence catalog
population is needed to begin direct-effect research.

Defer reusable root EvidenceFinding catalogs, occurrence streaming, automated
event detection, universal control scores, probabilistic world models, numerical
weights, network-edit execution, automated recommendations/optimization, full
external ontology import and ontology-wide migration. They require requirements
and governance beyond the bounded architecture.

The next proposed pilot is a **synthetic structural pilot**, using the existing
BIO-F01 read-only snapshot plus fictional policy, shock, outage, disclosure,
network, gradual-process and moderator cases. It exercises contracts and
compatibility across all eight Layers without a new scientific Family audit.
After that review, separately authorize one Family research scope selected from
the computed queue; queue rank alone does not authorize selection or execution.

Implementation order after approval:

1. Resolve AE01–AE04 object/target/control boundaries and AE09 ID compatibility.
2. Resolve AE05–AE08 effect/evidence/overlap contracts and migration-null policy.
3. Review AE10 authority/use predicates against existing validators without
   changing activation rules; validate synthetic structural pilot.
4. Approve separately scoped production infrastructure implementation and
   lossless adapter tests; preserve existing consumer behavior.
5. Approve AE11 operational workflow and a bounded research scope under AE12.
6. Govern exact scientific records and activation only in later human decisions;
   algorithms, practitioner exposure and deployment remain separate approvals.

Approval: **PENDING**. No decision here authorizes any of these future steps.

## Dependency map and concrete review request

```text
AE01 object boundaries -> AE02/03 identity/agency -> AE09 compatibility
AE04 targets + AE05 properties -> AE08 contribution/moderation rules
AE06 evidence + AE07 occurrence -> AE10 governance/use eligibility
AE08 + AE09 + AE10 -> reviewed production-contract implementation scope
AE11 local readiness/ownership -> AE12 later bounded pilot authorization
```

Review the twelve PENDING rows by APPROVE / MODIFY / REJECT with exact replacement
semantics where modified. The present assignment establishes evidence and an
isolated prototype for that review; it does not seek approval of new scientific
claims. See [RESEARCH_PROMPTS.md](RESEARCH_PROMPTS.md) for executable future
research specifications and [ARCHITECTURE_PROPOSAL.md](ARCHITECTURE_PROPOSAL.md)
for the researched design and synthetic stress cases.
