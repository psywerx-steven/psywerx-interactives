# PSYWERX Intervention Architecture V1

**Status:** Governed architecture; production implementation not authorized

**Decision record:**
[`GOV-REL-INT-V1-2026-09-05`](RELATIONSHIP_INTERVENTION_V1_GOVERNANCE_DECISION.md)

**Production catalog:** Does not yet exist

**Organizing principle:** Start with the Driver

## 1. Recommendation

Intervention should be a first-class PSYWERX catalog object. It is not a
Driver, RDS, relationship subtype, measurement Operationalization, or scenario
response.

The canonical unit is a recognizable method, action, environmental change,
communication, policy, technology, incentive, constraint, service, or
practice. Its context-specific claim of changing a Driver or causal pathway is
stored separately as an **Intervention Effect**. An **Intervention Package** is
an Intervention whose components are other Intervention IDs.

This normalized design is necessary because:

- the same intervention can affect several Drivers with different directions,
  evidence, populations, doses, and risks;
- the same Driver can be addressed by many modalities;
- intrinsic identity should not be duplicated in every target assertion;
- an intervention package must not be mistaken for a single indivisible
  method; and
- evidence that a method changes Driver A is not automatically evidence that
  it changes Driver B or produces a downstream outcome.

External taxonomies may be crosswalked later. Their codes remain mappings, not
the organizing spine. A PSYWERX Intervention enters the catalog because it has
a clear Driver-centered use, not because a generic technique list contains it.

## 2. Separation from existing Operationalizations

The eight source workbooks contain 2,335 Operationalization rows describing
indicators, measures, tasks, scales, observations, sensors, archives, and
elicitation methods. They are explicitly candidate ways to observe a Driver,
not claims of interchangeability and not interventions.

The Scenario Operationalization v1 service likewise produces transient ways to
define, derive, observe, compare, classify, or investigate one Entity. It does
not recommend an action or create canonical knowledge.

| Object | Governing question |
| --- | --- |
| Operationalization | How can this entity be defined, measured, inferred, or observed? |
| Intervention | What deliberate method or change can be implemented? |
| Intervention Effect | Under what conditions is that intervention expected to modify this exact Driver or relationship, in what way, and with what evidence? |
| Causal relationship | If this source entity changes, how does the target entity change? |

An item can play more than one real-world role—for example, a feedback display
can measure and intervene—but it requires separate records and evidence for
each role.

## 3. Normalized object model

### 3.1 Intervention

The catalog object supplies stable identity and reusable description.

```text
Intervention
  id, canonicalName, aliases, kind, category, description
  package flag and component IDs when applicable
  general implementation notes and identity sources
  governance and revision provenance
```

Governed high-level categories are deliberately broad:

- `COMMUNICATION_OR_INFORMATION`
- `TRAINING_OR_SKILL`
- `ENVIRONMENTAL_OR_CHOICE_ARCHITECTURE`
- `POLICY_RULE_OR_STANDARD`
- `INCENTIVE_OR_RESOURCE`
- `CONSTRAINT_OR_ENFORCEMENT`
- `TECHNOLOGY_OR_CONFIGURATION`
- `SERVICE_OR_SUPPORT`
- `BIOLOGICAL_OR_CLINICAL`
- `OTHER_SPECIFIED`, with a required nonempty specification

Category supports discovery, not scientific inference. Delivery modality and
channel belong on effect profiles when they change implementation or evidence.
`interventionKind` separately distinguishes `ATOMIC` from `PACKAGE`, so a
package does not lose its substantive category.

### 3.2 Intervention Effect

One effect record makes one bounded claim about one primary target. A
multi-target intervention therefore has multiple effect records so direction,
mechanism, evidence, timing, and risk are not conflated.

```text
Intervention Effect
  interventionId
  targetKind + exactly one primary target
  effectMode and intendedDirection
  intervention-to-target mechanism
  implementer, audience, delivery, context, scale, exposure
  evidence, confidence, uncertainty, risk, review provenance
```

The target kinds are:

- `DRIVER`: increase, decrease, stabilize, or disrupt one exact Driver; and
- `RELATIONSHIP`: modify one exact governed causal relationship.

V1 has no generic context target. Context, scope, boundary conditions,
prerequisites, implementation conditions, moderators, population/system,
setting/jurisdiction, and scenario applicability remain effect fields. If a
context feature is manipulated causally, it must resolve to a governed Driver
or relationship mechanism/moderator, or remain research metadata pending
ontology governance.

A relationship-targeted record must identify at least one canonical Driver in
`mechanisticDriverIds` before it can become `GOVERNED + ACTIVE`. A governed
moderator Driver may satisfy that requirement. If no legitimate Driver can be
identified, the record remains `RESEARCH_NEEDED` or blocked and is not
executable.

### 3.3 Intervention Package

A package is a catalog Intervention with `interventionKind: PACKAGE` and two or
more ordered or unordered `componentInterventionIds`. Package-level
effects require their own evidence; they are not calculated by adding component
effects. Component dose, sequencing, actor, and interaction notes belong in a
package specification. Cycles and self-membership are prohibited.

## 4. Targeting rules

| Target | V1 decision | Rule |
| --- | --- | --- |
| Driver | Yes; primary case | Exact canonical Driver ID and bounded effect record required |
| RDS | No direct target in V1 | May be a desired/reported outcome or MOE; intervention effects must map to constituent Driver(s) or governed causal relationship(s) and then recalculate the RDS |
| Relationship/edge | Yes, conditionally | Use `MODIFY_RELATIONSHIP` for an exact governed causal edge; require mechanism, evidence, and at least one canonical mechanistic Driver before active governance |
| Moderator | Yes, through its representation | Target the moderator when it is a Driver, or target the moderated relationship and name a governed moderator Driver in `mechanisticDriverIds`; do not target an unlabeled slot |
| Context/boundary condition | No generic target in V1 | Keep as scoped effect metadata unless it resolves to a governed Driver or relationship mechanism/moderator |
| Multiple Drivers | Yes | One effect record per Driver; optional shared study/package linkage preserves common evidence |

RDS can appear in `outcomeEntityIds` or `measureOfEffect` when it is recalculated
from its constituents. Calling an RDS “highly modifiable” does not make it
directly manipulable. If practitioners describe an intervention by an RDS
outcome (“reduce sleep deficit”), the interface should resolve the actual
constituent targets (for example, Sleep Duration or schedule-related Drivers)
before creating an executable recommendation.

## 5. Effect semantics

| Intended meaning | Representation |
| --- | --- |
| Intervention increases Driver | `targetKind: DRIVER`, `effectMode: CHANGE_LEVEL`, `intendedDirection: INCREASE` |
| Intervention decreases Driver | `targetKind: DRIVER`, `effectMode: CHANGE_LEVEL`, `intendedDirection: DECREASE` |
| Intervention stabilizes Driver | `targetKind: DRIVER`, `effectMode: STABILIZE`, with target range/baseline in conditions |
| Intervention disrupts Driver | `targetKind: DRIVER`, `effectMode: DISRUPT`, with the process being interrupted stated explicitly |
| Intervention buffers a causal influence | `targetKind: RELATIONSHIP`, `effectMode: MODIFY_RELATIONSHIP`, `intendedDirection: ATTENUATE`, exact target relationship ID, and mechanistic Driver linkage |
| Intervention amplifies a pathway | One or more relationship-targeted `MODIFY_RELATIONSHIP` effects with `intendedDirection: AMPLIFY`; never a package-wide weight without edge-level claims |
| Intervention suppresses a pathway | One or more relationship-targeted `MODIFY_RELATIONSHIP` effects with `intendedDirection: SUPPRESS` |
| Intervention changes a moderator | Driver-targeted effect when the moderator is a Driver, or relationship-targeted effect with the moderator Driver in `mechanisticDriverIds` |
| Intervention changes environment/context | Driver-targeted effect if the feature is a governed Driver; otherwise research metadata pending ontology governance |
| Multi-target intervention | Multiple effect records linked to one Intervention |
| Package containing methods | Package Intervention plus component IDs and separately supported package effects |

`ATTENUATE` and `SUPPRESS` are not synonyms. Attenuation reduces sensitivity or
strength; suppression reduces or interrupts transmission of the specified relationship.
`STABILIZE` must name a range or reference and cannot mean “improve.”

## 6. Field classification

Classification applies to governed active records. A candidate may omit fields
only when its missing-data and research status are explicit. “Context-
dependent” means required when the real intervention/evidence makes the field
material; it must not be filled with boilerplate.

| Requested field | Classification | Canonical location and rationale |
| --- | --- | --- |
| Intervention ID | REQUIRED | Intervention; permanent identity |
| Canonical name | REQUIRED | Intervention; recognizable method/action, not a desired outcome |
| Aliases | RECOMMENDED | Intervention; search and external terminology |
| Intervention kind | REQUIRED | Intervention; `ATOMIC` or `PACKAGE`, separate from substantive category |
| Intervention category/type | REQUIRED | Intervention; one broad discovery category |
| Description | REQUIRED | Intervention; defines what is implemented and its boundaries |
| Target Driver(s) | REQUIRED | Effect; one primary Driver per Driver-targeted record; every governed intervention needs at least one Driver-centered effect or mechanistic Driver linkage |
| Target relationship(s) | CONTEXT-DEPENDENT | Effect; exact governed causal edge, `MODIFY_RELATIONSHIP`, and nonempty canonical `mechanisticDriverIds` required before active governance |
| Intended direction of change | REQUIRED | Effect; direction relative to canonical target scale |
| Mechanism of action | REQUIRED | Effect; explains intervention -> target, not Driver -> Driver |
| Actor / implementer | RECOMMENDED | Effect; feasibility and authority depend on who acts |
| Target actor/population/audience | REQUIRED | Effect; establishes whom/what the evidence applies to |
| Delivery modality | RECOMMENDED | Effect; material implementation form |
| Intervention channel | CONTEXT-DEPENDENT | Effect; required when channel affects reach, fidelity, or effect |
| Context | REQUIRED | Effect; setting, system, jurisdiction, or bounded use context |
| Scale | REQUIRED | Effect; analytic/implementation scale such as person, group, organization, or jurisdiction |
| Dose/intensity | CONTEXT-DEPENDENT | Effect; required when a meaningful dose exists or evidence is dose-specific |
| Frequency | CONTEXT-DEPENDENT | Effect; required for repeated delivery |
| Duration | CONTEXT-DEPENDENT | Effect; required for sustained delivery |
| Onset / time to effect | RECOMMENDED | Effect; bands permitted when exact timing is unsupported |
| Persistence | RECOMMENDED | Effect; distinguish lasting effect from continued delivery |
| Reversibility | CONTEXT-DEPENDENT | Effect; required when rollback, lock-in, or irreversibility is material |
| Modifiability requirements | RECOMMENDED | Effect; identifies controllable prerequisites and target constraints |
| Prerequisites | CONTEXT-DEPENDENT | Effect; required when implementation/effect depends on them |
| Moderators | RECOMMENDED | Effect; structured Driver IDs plus narrative conditions |
| Boundary conditions | REQUIRED | Effect; prevents universal interpretation |
| Expected downstream effects | EXCLUDE from canonical Intervention/Effect | Derive from governed graph or store in a versioned scenario/model assessment; do not freeze inferred consequences as intrinsic truth |
| Unintended effects | RECOMMENDED | Effect; evidence-backed collateral changes, preferably as separate effect records when a canonical target exists |
| Risks | REQUIRED | Effect; concise risk/harms assessment, including “no material risk identified in reviewed evidence” only when justified |
| Ethical/legal constraints | CONTEXT-DEPENDENT | Effect; required when rights, consent, equity, safety, law, or authority is implicated |
| Implementation feasibility | CONTEXT-DEPENDENT | Effect/scenario assessment; depends on resources, actor, setting, and scale |
| Measurement / MOE | RECOMMENDED | Effect; exact measure/Operationalization linkage, baseline, target, and window when available |
| Evidence strength | REQUIRED | Effect; body of evidence for this target/context claim |
| Evidence notes/rationale | REQUIRED | Effect; explains support, limits, and transfer |
| Confidence | REQUIRED | Effect; curatorial confidence in encoding/applicability |
| Sources | REQUIRED | Effect for efficacy/safety claims; Intervention may also cite identity/definition sources |
| Crosswalks to external taxonomies | OPTIONAL | Separate crosswalk record; never determines canonical identity |
| Evidence-conflict disposition | RECOMMENDED | Effect; preserves mixed or contradictory findings |
| Uncertainty | RECOMMENDED | Effect; magnitude, direction, timing, transfer, implementation, or measurement uncertainty |
| Governance/revision provenance | REQUIRED | Both objects; lifecycle status, revision, dates, and explicit decision record |

### Minimum governed Intervention

An Intervention cannot become `GOVERNED + ACTIVE` without identity, name, kind,
category, description, governance/revision provenance, and at least one
`GOVERNED + ACTIVE` Intervention Effect connected to an exact Driver or to an exact
relationship with a mechanistic Driver linkage.

### Minimum governed Intervention Effect

An active relationship-targeted effect additionally requires one or more
canonical mechanistic Driver IDs. Every active effect requires identity,
Intervention ID, target kind and exact target, intended mode/direction,
mechanism of action, target population,
context, scale, boundary conditions, evidence strength and rationale,
confidence, source IDs, risk assessment, and governance/revision provenance.

## 7. Causal-graph and scenario use

An intervention is an exogenous action node only inside a versioned analysis or
scenario package. The canonical catalog supplies eligible effect assertions;
the package chooses context, baseline, dose, timing, and model transformation.

```text
Intervention --effect assertion--> Driver A
Driver A --governed causal edge--> Driver B
Driver B --governed causal/dependency structure--> RDS C
RDS C --measure/outcome interpretation--> bounded outcome assessment
```

Nonlinear, multi-target, feedback, delayed, and pathway-modifying interventions
are represented by multiple explicit effects and governed graph structure, not
by forcing a single chain. Recommendation ranking must keep efficacy, evidence,
feasibility, risk, ethics, and uncertainty separate; no universal score is part
of the canonical intervention object.

## 8. Internal critique and resulting simplifications

- Intervention is first-class because forcing it into relationships or
  Operationalizations would collapse identity, action, measurement, and
  evidence.
- Intervention Effect is separate because context-specific claims cannot be
  reliable intrinsic properties of the method.
- Multi-target claims are split into one primary target per effect instead of a
  large nested target array.
- RDS direct targeting is prohibited in V1, preventing derived outcomes from
  becoming manipulable roots.
- Expected downstream effects are excluded from canonical intervention data;
  the governed graph calculates or narrates them in bounded analyses.
- Dose, frequency, duration, reversibility, feasibility, channel, and legal
  constraints are context-dependent rather than mandatory boilerplate.
- The categories are broad and small. External behavior-change or method
  taxonomies remain optional crosswalks.
- Mechanism of action is explicitly intervention -> target; causal relationship
  mechanism remains source Driver/RDS -> target Driver/RDS.

This model remains Driver-centered, usable by practitioners, defensible by
researchers, and normalized for thousands of effect records without optimizing
for any one modeling technique.
