# Actions & Events: a bounded architecture proposal

**PROPOSAL / NON_PRODUCTION — all architecture decisions PENDING.**
This package extends the discussion of governed Relationship + Intervention V1;
it does not change that architecture. Baseline scientific state is main at
`2636dd9a8b7bad1da3d7dfa21db5fe877f4de4e1`. There was no later tracked work at
assignment entry, and no equivalent generalized proposal was found.

## Recommended design

Use **Actions & Events** as the practitioner-facing name. Define three objects:
`HappeningType`, `Occurrence`, and `EffectAssertion`. Keep a normalized
`EvidenceAssessment` linked to the precise assertion or occurrence it assesses.
An Intervention remains a deliberate-action profile with its existing identity,
package semantics and separately governed effects. Exposure and process are
overlapping descriptive tags, not new mutually exclusive catalogs.

| Object | Meaning | Does not establish |
|---|---|---|
| HappeningType | Reusable description of an action, event, exposure or process | That it happened, is controllable, or has any particular effect |
| Occurrence | An observed, planned or hypothetical episode with participants, timing and boundary | That its alleged consequences were caused by it |
| EffectAssertion | One contextual proposition about one exact Driver or causal relationship | Every downstream consequence or a universal effect size |
| EvidenceAssessment | Source findings and synthesis for that exact proposition or occurrence | Canonical approval, execution permission, or action feasibility |

Reusable type versus individual episode borrows the class/individual distinction
from [OWL 2](https://www.w3.org/TR/owl2-primer/) and the procedure/actuation/result
separation from [SOSA/SSN](https://www.w3.org/TR/vocab-ssn/). These are design
analogies; PSYWERX is not adopting OWL reasoning or sensor-oriented cardinalities.
The focused review and access limitations are in
[ARCHITECTURE_RESEARCH.md](ARCHITECTURE_RESEARCH.md) and [SOURCES.json](SOURCES.json).

```text
HappeningType <- type reference - Occurrence (observed/planned/hypothetical)
      |                              |
      +-- EffectAssertion -----------+ optional occurrence reference
                 |
                 +--> exact Driver OR exact causal Relationship
                 |
                 +--> EvidenceAssessment: source findings -> synthesis

Occurrence evidence and effect evidence are separate claims.
```

A reusable effect does not require a fabricated occurrence. Conversely, an
observed event may have no supported effects yet. A report about an outage can
support an occurrence; a separate design/contrast and causal argument must
support any claim that the outage changed a Driver.

## Identity, agency, origin and scope

The proposed identity contract uses independent dimensions:

| Dimension | Location / proposed semantics |
|---|---|
| Kind | Type `kindTags`: ACTION, EVENT, EXPOSURE, PROCESS; one or more |
| Origin Layers | Type/episode origin tags from the eight Layers; multiple allowed, never copied from targets |
| Action subset | Explicit deliberate Intervention profile; current ATOMIC/PACKAGE identity retained |
| Actor/source system | Episode participant(s); do not invent a human actor for a natural process |
| Intentionality | Relative to actor, purpose and consequence; intended action can have unintended effects |
| Controllability | Actor-specific ability to initiate, prevent, time, tune, buffer or respond, with constraints/provenance |
| Pattern | Discrete, repeated, continuous, gradual, cumulative, cyclic; multiple descriptors when useful |
| Timing | Episode start/end or interval/unknowns; causal onset/lag separately on effect evidence |
| Dose/intensity | Exposure-specific quantity, unit and protocol or explicit unassessed state; no universal intensity scale |
| Reach/distribution | Recipient/system, exposure access and subgroup distribution; not evidence confidence |
| Internal/external | Relative to an explicitly declared system boundary; may be mixed or unknown |
| Affected Layer | Resolved from exact target IDs, separate from origin tags |

The eight origin dimensions are Biological, Psychological, Social, Cultural,
Physical/Environmental, Institutional/Structural, Informational and Technological.
Experimental codes map explicitly to existing Layer names; no entity receives
new Layer membership. A deliberately caused external event can still be
confounded. External-to-actor is not a statistical independence assumption.
Explicit causal assumptions are required for causal interpretation; an incomplete
catalog also cannot treat absent edges as zero influence.
[Pearl 2009](https://ftp.cs.ucla.edu/pub/stat_ser/r350.pdf)

Exposure descriptions can identify recipient, stressor/input, route and medium,
following the compositional idea in [ECTO](https://github.com/EnvironmentOntology/environmental-exposure-ontology).
The proposed model does not import ECTO classes wholesale or assume that an
organism-centered exposure ontology fully covers institutions. Time profiles
distinguish interval, duration and order, following
[OWL-Time 2017](https://www.w3.org/TR/2017/REC-owl-time-20171019/); precedence
does not become causation.

## Coverage of overlapping origin domains

All examples below are hypothetical structural illustrations, not new scientific
claims. A search domain is neither an exclusive kind nor a governed Layer.

| Domain | Example to represent | Candidate origin tags / possible target Layers |
|---|---|---|
| A Deliberate interventions | Scheduling policy | Institutional/Structural origin; Biological target |
| B Routine/unintended activity | Repeated routine behavior with unintended resource use | Psychological/Social origins; Physical/Environmental target |
| C External shocks | Environmental disruption or leadership loss | Physical/Environmental or Social origin; resources/access across Layers |
| D Environmental exposure | Sustained heat, noise, crowding or pollution | Physical/Environmental origin; Biological/Psychological targets |
| E Institutional change | Rule, sanction, restructuring or formal-authority change | Institutional/Structural and Cultural origins; Social/Technological targets |
| F Technological change | Outage, configuration change or automation | Technological origin; Informational/Institutional targets |
| G Social/network process | Formation/dissolution of real ties, migration or protest | Social/Cultural origins; Social/Institutional targets |
| H Informational exposure | Disclosure, repeated message, rumor or information availability | Informational origin; Psychological/Social targets |
| I Physiological process | Gradual development, illness, injury or sleep loss | Biological origin; Biological/Psychological targets |

Example origins can be multi-tagged: a scheduling policy may be a deliberate
ACTION and an ongoing PROCESS; its enactment is an EVENT; affected participants
may undergo repeated EXPOSURE. None of these tags supplies an effect.

## Effects: property changed versus manner of change

Use eleven property dimensions with constrained change descriptors. Avoid a
flat list of every property-direction combination. A claim refers to one
property and a defined measure/reference; multiple supported effects receive
separate IDs with shared exposure and evidence dependencies where applicable.

| Property | Manner / required interpretation | Structural illustration |
|---|---|---|
| LEVEL | Increase/decrease relative to target scale and contrast | Scheduling changes amount of fictional Driver S |
| VARIABILITY | Increase/decrease fluctuation; variance, stability or predictability must name a statistic | Repeated exposure changes variation of fictional Driver V |
| RATE | Faster/slower change per declared time basis | Gradual process changes rate of a fictional state |
| THRESHOLD | Raise/lower trigger point on a specified scale | Constraint changes threshold for an exact edge operating |
| TIMING | Earlier/later onset; longer/shorter lag, duration or recovery with named component | Outage delays a fictional response |
| PERSISTENCE | Accumulation, carryover, decay, reversibility and recovery of an effect, distinct from continued exposure | Repeated input lengthens fictional carryover |
| RELATIONSHIP_STRENGTH | Amplify/attenuate/buffer/suppress exact relationship sensitivity | Action attenuates an edge under a stated condition |
| RELATIONSHIP_DIRECTION | Reverse under specified state/scope, not globally | State-dependent edge modification |
| ENABLEMENT | Make a mechanism/opportunity possible or prevent operation; exact target required | Rule disables a particular mechanism |
| FUNCTIONAL_SHAPE | Linear, threshold, saturation, U/inverted-U, cyclic, other non-monotonic or unknown | Cyclic input with state-dependent change, no universal sign |
| STRUCTURE | Real resources, opportunities, constraints, access, ties or configuration resolve to Drivers/edges | Real network tie change modifies a scoped causal relationship |

The checklist additionally covers reach/distribution, subgroup differences,
synergy/antagonism, intended versus observed direction, unintended consequences
and beneficial/harmful/mixed/null outcomes. Valence is relative to a stakeholder
and criterion. It is distinct from positive/negative sign. Interaction claims
need joint evidence; a pair of independently supported effects is not enough.

Use NOT_INVESTIGATED, NOT_APPLICABLE, INSUFFICIENT_EVIDENCE,
SUPPORTED_EFFECT and SUPPORTED_NULL as investigation outcomes. An unknown result
is not zero. A supported null needs an explicit contrast, measure, precision and
scope; nonsignificance alone does not establish absence.
[ASA statement](https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf)

## Driver grounding, moderation and double counting

The same two direct target kinds apply to every happening: DRIVER and
RELATIONSHIP. No generic CONTEXT_CONDITION or ALTER_CONTEXT exception is
implemented. Context remains scope, conditions, prerequisites, exposure profile
or an identified governed Driver/moderator. A proposed unmapped real-world
configuration remains research metadata pending ontology governance.

Three distinct routes are possible:

1. An event changes Driver M. The EffectAssertion targets M.
2. An event modifies an exact causal edge A→B. The assertion names that edge,
   what changes, conditions/timing and mechanistic Driver IDs.
3. An event changes moderator Driver M, and M changes A→B's effect. The first
   claim targets M; the moderation assertion independently identifies A→B.

Routes 2 and 3 can describe the same contribution. Require an explicit
contribution/overlap group and a later execution plan choosing one representation
or a justified reconciliation. Do not add their effects by default. If an event
is already represented by a measured Driver exposure trajectory, the event
occurrence supplies provenance for that input, not an independent second causal
input. Episode/type/Driver identity must not collapse into one object.

Distinguish effect modification across strata from an effect of manipulating
the moderator; these answer different causal questions.
[VanderWeele 2009 abstract](https://pubmed.ncbi.nlm.nih.gov/19806059/)
The source review is abstract-level and supplies this distinction only, not an
estimator or proof of any PSYWERX moderation claim. A modification hypothesis
remains a hypothesis; graph reachability never establishes mediation.

RDS remain outcomes, MOEs, measurements or recalculated results. An environmental
shock cannot directly update a sleep ratio, fit or network aggregate independently
of governed inputs merely because it is called an event. Retain derivation
version, inputs, windows, denominator/overlap checks and single-contribution
propagation. If a non-intervention event appears to affect an RDS, identify the
Driver/configuration route or record an unresolved outcome claim. Do not infer
new input entities or execute B01–B05.

## Evidence, inference and governance

Preserve eight independent dimensions:

| Dimension | Proposed location and rule |
|---|---|
| Claim semantics | Effect/relationship claim: causal, association, moderation, temporal, derivational, compositional, realization, semantic or pathway; existing seven-family contract remains authoritative |
| Evidence bases | Multiple source finding design tags: experimental; quasi/natural experimental; longitudinal; cross-sectional; qualitative/historical/case; synthesis; theoretical/mechanistic; definitional calculation; simulation/model; expert judgment; untested hypothesis |
| Production method | Extracted, synthesized, model/pathway inferred, or hypothesized; AI extraction is an actor/method, not empirical evidence |
| Disposition | SUPPORTS, MIXED, CONTRADICTED, INSUFFICIENT, NOT_ASSESSED |
| Confidence | Qualitative reasoned assessment for the precise claim; no numeric score invented |
| Clarity/completeness | Target, direction, mechanism, population, context, timing, measurement and boundaries each assessed; nonempty boilerplate does not prove adequacy |
| Provenance | Source/passages, reviewed access depth, extraction/synthesis method, dataset overlap, agent roles, record revision and human decision |
| Governance/use | Existing lifecycle/activation/block states; separately assessed quantitative-model and actor-action eligibility |

EvidenceAssessment contains stable source finding IDs and a synthesis referencing
them. Supportive, contrary, null and mixed results survive the synthesis. Record
overlapping datasets and review/study overlap; do not count papers as independent
replications automatically. Occurrence findings target the occurrence; efficacy
findings target the effect. An occurrence's truth or confidence never transfers
to its effects. A high-confidence association stays noncausal; low confidence
does not create a new relationship type.

This structure borrows qualified attribution/activity/revision from
[PROV-O](https://www.w3.org/TR/prov-o/) and proposition-specific evidence lines
from [SEPIO](https://sepio-framework.github.io/sepio-linkml/EvidenceLine/).
Provenance influence is not causal influence. SEPIO's optional numeric scores
are not imported.

All real governance remains D11–D12. Approval is neither certainty nor automatic
model eligibility. The experimental dry run uses fictional authorization only
and always reports production eligibility false. An eligible action additionally
needs an eligible effect, actor control/authority, context fit and risks/prerequisites
reviewed. Disasters can inform preparedness but cannot be offered as actions the
practitioner may implement. No ranking algorithm is proposed for this milestone.

## Compatibility with V1 and BIO-F01

Recommend an additive reference bridge before any separately authorized
migration. Preserve every Intervention ID and revision, identitySourceIds,
category, ATOMIC/PACKAGE distinction, component order/content, effect target,
intendedDirection, evidence links and exact lifecycle provenance. New metadata
stays unassessed when the old record does not support it. Do not infer deliberate
control by a particular actor merely from Intervention membership.

| Existing contract | Future mapping recommendation | Current assignment |
|---|---|---|
| Intervention | Intervention profile on reusable type with existing ID reference; no duplicate identity | Read only |
| InterventionEffect | Generalized EffectAssertion reference; preserve old mode/direction verbatim until explicit mapping approval | Read only |
| EvidenceAssessment | Retain original revision; add source-level findings only through governed evidence review | Read only |
| V3 Relationship + V1 projection | One proposition with two contract views | Count once |
| CBT-I package | Keep non-exhaustive component semantics and package-specific evidence | No component inference |
| V1 status | Existing status retained; new draft objects do not inherit scientific authority | No transition |

BIO-F01 currently has six active native Relationships (four causal, one
association, one derivation), five active Interventions, five active effects,
eleven active EvidenceAssessments and four inactive governed Intervention
identities. The light/melatonin assessments remain MIXED. The existing scenario
service uses the entity/V3 compatibility path and does not consume native V1
records; this experiment changes no consumers.

Historical schema/architecture documents still contain launch-time unpopulated
or inactive statements. The later BIO-F01 activation decision and actual records
establish current status. Those historical documents are not edited here.

## Relationship-first work and inventory interpretation

[RESEARCH_PROMPTS.md](RESEARCH_PROMPTS.md) defines linked Pass A relationship
review and Pass B effect search. Start each Family by reviewing current records;
target effects after local definitions, incident dispositions, RDS inputs and
scope are understood. Direct effect research does not require a complete global
graph. Human-action search considers modifiability; natural events/processes also
cover low-modifiability Drivers. Findings move in both directions between passes
without creating scientific records automatically.

The all-Family queue in [reports/auditQueue.csv](reports/auditQueue.csv) uses a
transparent provisional score: 5×RDS causal sources + 2×RDS count + 4 for no
cross-Family links + 2 for no cross-Layer links + isolated entities + 3×blocked
entities + capped-at-10 legacy incomplete incident edges. This schedules review
effort, not scientific importance. RDS-rich and large Families can rank highly;
human priorities/evidence access may justify another order. BIO-F01's row is
follow-up of an existing pilot, not authorization to resolve its revisions.
All 105 rows remain PENDING. Non-BIO-F01 rows report no audit status established
by this inventory, not a claim that no historical audit exists anywhere.

## Prototype boundary and limitations

The experiment includes machine-readable draft schemas, synthetic fixtures,
semantic checks, an immutable eligibility dry run and a read-only inventory.
Use the commands in [PLAN.md](PLAN.md). `prototype.py inventory` requires a
Family ID and an explicit output directory beneath this experiment; resolved
path checks reject canonical destinations and symlink escapes. It emits original
Family records, separate graph coverage and an empty research template. It does
not search the literature, propose scientific edges or mutate canonical stores.

Draft schema expressiveness is a prototype result, not a production-readiness
claim. The implementation is deliberately JSON/Python using existing dependencies;
no ontology import, external service, stream ingestion, model fitting, optimization
or public interface is added. Source findings remain nested within assessments;
a reusable independent finding catalog is deferred. The prototype inherits origin
Layers from the type; an episode-specific override is a proposed later extension.
Timing, dose and duration accept qualitative specification; unit-aware numeric
interval arithmetic is deferred. The supported-null fixture uses a conservative
equivalence-within-margin demonstration, not a proposed claim that this is the
only scientifically valid route to a bounded null conclusion. Context text still requires
human scientific review. Structural overlap detection cannot prove that every
real causal contribution has been identified.

The prototype inherits origin Layers from the reusable type; an episode-specific
origin override is a proposed extension requiring its own provenance, not a field
implemented here. Its occurrence profiles accept qualitative timing/dose/duration
and explicit missing values. Standardized units and interval arithmetic remain
later contract work. Empirical source findings can be inputs to a MODEL_INFERENCE;
their existence never relabels the resulting inference as an observation.

The independent maintainer review checks schema/prose correspondence and all
failure cases in the requirement table. Known gaps must be stated, not repaired
by weakening RDS, causal, evidence, package or activation safeguards. Pending
choices and minimum future implementation are in
[GOVERNANCE_DECISIONS.md](GOVERNANCE_DECISIONS.md).
