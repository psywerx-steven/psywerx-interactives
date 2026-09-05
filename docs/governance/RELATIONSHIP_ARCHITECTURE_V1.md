# PSYWERX Relationship Architecture V1

**Status:** Governed architecture; production implementation not authorized

**Decision record:**
[`GOV-REL-INT-V1-2026-09-05`](RELATIONSHIP_INTERVENTION_V1_GOVERNANCE_DECISION.md)

**Relationship Schema v3 status:** Current production contract; unchanged

**Scope:** Relationship semantics, evidence, RDS participation, and future
schema direction

## 1. Current governed state

Relationship Schema v3 is a generic proposition envelope over canonical
entities. It separates active, deprecated, and candidate buckets; resolves
endpoints against `data/entities.json`; makes Driver/RDS endpoint types
explicit; and excludes noncausal relationships from the legacy executable
causal view. The v0.3 migration tests protect the identity and content of the
431 fully specified active causal relationships.

The current active corpus contains:

| Property | Current value |
| --- | ---: |
| Active relationship records | 450 |
| Active causal relationships | 431 |
| Active noncausal relationships | 19 |
| Driver -> Driver causal | 394 |
| Driver -> RDS causal | 18 |
| RDS -> Driver causal | 15 |
| RDS -> RDS causal | 4 |
| Cross-Layer causal | 88 |
| Cross-level causal | 83 |

Current causal predicates are `CAUSES` (405), `ENABLES` (16), and
`CONSTRAINS` (10). Current noncausal records use derivational, compositional,
realization, and semantic-mapping families.

Relationship Schema v2 and the legacy browser utility also recognize
`MODERATES`, but none of the 431 active causal records currently uses it. V1
therefore proposes edge-targeted moderation for future records without
rewriting legacy content.

Current active noncausal semantics are eight `DERIVED_FROM`, one
`CONSTITUENT_OF`, two `REALIZES`, and eight semantic mappings: two
`RELATED_METRIC`, two `INVERSE_UNDER_ALIGNED_SCOPE`, two `NARROWER_THAN`, one
`EQUIVALENT_UNDER_CONDITIONS`, and one `OVERLAPS_WITH`. These are already
governed distinctions and should not be collapsed into causal edges.

### Current V3 field inventory

Every active record currently carries this common shape:

| Concern | Current fields |
| --- | --- |
| Identity/endpoints | `id`, `subjectEntityId`, `subjectEntityName`, `subjectEntityType`, `objectEntityId`, `objectRelationshipId`, `objectEntityName`, `objectEntityType` |
| Proposition type | `predicate`, `relationFamily`, `polarity`, `directness` |
| Explanation/scope | `mechanism`, `conditionsModerators`, `moderatorEntityIds`, `generalizabilityContext`, `notesCaveats` |
| Form/level | `functionalForm`, `functionalFormNotes`, `subjectLevel`, `objectLevel`, `levelTransitionMechanism` |
| Time/exposure | `lagProfile`, `lagLowerBound`, `lagUpperBound`, `lagUnit`, `lagNarrative`, `exposurePattern`, `effectPersistence` |
| Evidence/governance | `evidenceStrength`, `confidence`, `governanceClass`, `governanceStatus`, `supportingEvidenceIds` |
| Linkage/provenance | `reciprocalProcessId`, `source`, `legacyRelationship` |

Candidate records may additionally carry `reviewStatus`. The envelope has
`schemaVersion`, `relationships`, `deprecatedRelationships`, and
`relationshipCandidates`. The proposed architecture preserves these concerns
even where it recommends clearer names or normalized subrecords.

### What V3 handles well

- One permanent ID per proposition and explicit lifecycle buckets.
- Generic entity endpoints with explicit Driver/RDS typing.
- A clean causal/noncausal boundary for traversal and simulation.
- Retention of legacy V2 detail and provenance without changing the 431
  governed propositions.
- Directed causal edges, reciprocal-process linkage, level transitions, lag
  bands, evidence IDs, confidence, and contextual qualification.
- Mechanical exclusion of deprecated and blocked candidates.

These capabilities should be preserved. The V1 proposal does not rename,
retype, or rewrite existing records to make them conform.

### Observed limitations in the seed corpus and documentation

This assessment is a corpus profile, not a relationship audit.

- Every causal record has all expected keys, evidence IDs, a mechanism,
  conditions, lag narrative, and review classifications. Structural population
  is therefore highly consistent.
- Several fields provide little current discrimination: all 431 functional
  forms are `UNSPECIFIED`; all 431 exposure patterns are `NOT_SPECIFIED`; none
  has numeric lag bounds, effect persistence, or a linked moderator entity.
- V3 has no governed effect-size/relationship-strength object. That absence is
  preferable to treating evidence strength or confidence as a causal weight.
- Generalizability is populated but uses only five distinct texts; mechanism
  and conditions contain recurring Layer-level templates. A populated string
  must not be treated as proof of edge-specific knowledge.
- `evidenceStrength` and `confidence` are separate, which is correct, but V3
  lacks a dedicated evidence rationale and a structured way to preserve
  conflicting findings.
- `governanceClass` (core/context-dependent) and `governanceStatus`
  (active/proposed/deprecated) are useful but do not express a complete review
  lifecycle.
- The V3 document names some relation families differently from the generated
  artifact. The artifact currently contains `DERIVATIONAL`, `COMPOSITIONAL`,
  `REALIZATION`, and `SEMANTIC_MAPPING`; documentation also mentions
  `SEMANTIC` and `CONSTRAINT`. This vocabulary drift should be resolved by a
  governance decision, not by rewriting data incidentally.
- The migration manifest calls v0.3 a non-authoritative preview even though CI
  protects its exact Driver/RDS partition and 431 causal propositions. This
  proposal does not silently change that authority designation.
- `objectRelationshipId` anticipates edge-to-edge claims, but current records
  and validators still require an entity object. Moderation therefore has no
  complete executable representation.
- `MEDIATED_PATH` is currently attached to governed path segments. For future
  work, mediation needs an explicit pathway container so a segment is not
  mistaken for an indirect source-to-outcome shortcut.
- Names are useful compatibility snapshots, but IDs—not duplicated names—must
  remain authoritative endpoints.

## 2. Governed meanings of “related”

The smallest defensible vocabulary is preferred. Conceptual distinctions do
not automatically require separate top-level relation families.

| Meaning | V1 representation | First-class? | Causal graph treatment |
| --- | --- | --- | --- |
| Causal influence | `CAUSAL` record with `CAUSES`, `ENABLES`, or `CONSTRAINS` | Yes | Eligible only when governed active and executable fields are satisfied |
| Derivation | `DERIVATIONAL` / `DERIVED_FROM`; the RDS is subject and each input is object, preserving current V3 convention | Yes | Dependency graph only; never a causal edge |
| Aggregation | A `DERIVED_FROM` dependency plus the RDS `derivationType` and derivation specification | No separate family | Calculation only; avoid duplicating aggregate and constituent effects |
| Constituent / part-of | `COMPOSITIONAL` / `CONSTITUENT_OF` when membership itself is governed and useful | Yes | Excluded |
| Realization | `REALIZATION` / `REALIZES` for a lower-level configuration or process that instantiates a higher-level state | Yes | Excluded unless a separate causal claim is independently supported |
| Measurement / indicator | An Operationalization record linked to the entity; use `MEASURES` or `INDICATES` only when both endpoints are canonical objects and the distinction is needed | Usually another catalog | Excluded |
| Placement / classification | Existing `primaryFamilyId`, `relatedFamilyIds`, Layer, subtype, and crosswalk fields | No | Excluded; do not duplicate taxonomy as graph edges |
| Temporal transition | `EMPIRICAL_NONCAUSAL` / `PRECEDES` or qualified-state `TRANSITIONS_TO` with explicit states and time basis | Yes, when scientifically material | Excluded unless a distinct causal edge is governed |
| Association | `EMPIRICAL_NONCAUSAL` / `ASSOCIATED_WITH`, canonical endpoint order, and `symmetry: SYMMETRIC` | Yes, when evidence is useful but noncausal | Excluded and visually labeled noncausal |
| Moderation | Normalized n-ary `MODERATION` / `MODERATES` assertion targeting one causal relationship ID | Yes | Modifies a governed edge; is not an ordinary entity-to-entity edge |
| Mediation / mechanistic pathway | A pathway record that orders two or more governed causal edge IDs and identifies mediator entity IDs | Yes as a pathway, not an edge type | Traverse constituent causal edges; never add an unqualified shortcut |

### Governed vocabulary decisions

The seven V1 top-level families are `CAUSAL`, `EMPIRICAL_NONCAUSAL`,
`MODERATION`, `DERIVATIONAL`, `COMPOSITIONAL`, `REALIZATION`, and `SEMANTIC`.
`predicate` is the single relationship subtype; V1 does not add
`relationshipSubtype`.

1. `CONSTRAINS` remains a causal predicate; `CONSTRAINT` should not also be a
   top-level family for the same claim.
2. Aggregation is a subtype of derivation, not a new relation family.
3. Placement remains authoritative entity metadata, not redundant graph data.
4. Measurement normally belongs to the existing Operationalization domain.
   The 2,335 private workbook operationalization rows are candidate measures,
   not interventions and not proof of causal effects.
5. Association and temporal transition are first-class
   `EMPIRICAL_NONCAUSAL` records because otherwise analysts are pressured to
   overstate them as causal. `TRANSITIONS_TO` always relates qualified states;
   a bare entity-to-entity transition is invalid, and the two entity IDs may
   be identical when their governed state definitions differ.
6. Moderation targets an edge. Mediation groups edges. Treating either as an
   ordinary A-to-B causal predicate loses the proposition being qualified.
7. Semantic mappings such as narrower-than, overlap, equivalent-under-
   conditions, and related-metric remain noncausal compatibility constructs.

## 3. Causal relationship contract

The classifications below apply to a relationship at the point it is proposed
for `GOVERNED + ACTIVE`. Candidate records may be incomplete if missing fields
are explicit and route the record to research or governance review.

| Field or concept | Classification | Rule |
| --- | --- | --- |
| Relationship ID | REQUIRED | Permanent and globally unique across lifecycle states |
| Source entity ID and type | REQUIRED | Exact canonical entity; source state change is the antecedent |
| Target entity ID and type | REQUIRED | Exact canonical entity; target state change is the consequent |
| Direction | REQUIRED | Encoded once by source/object order; no bidirectional arrow |
| Causal predicate | REQUIRED | `CAUSES`, `ENABLES`, or `CONSTRAINS`; moderation is reified |
| Polarity/sign | REQUIRED | Positive, negative, non-monotonic, or context-dependent; unsigned is not sufficient for an executable active edge |
| Mechanism | REQUIRED | Edge-specific process connecting source change to target change; not merely co-occurrence or a restatement |
| Causal claim role | REQUIRED | `MODELED_LOCAL_LINK`, `TOTAL_EFFECT`, or `UNRESOLVED_SHORTCUT`; distinct from an evidence estimand, mechanistic directness, and computed graph adjacency |
| Boundary/context conditions | REQUIRED | Conditions under which the causal interpretation is asserted |
| Population/unit/context specificity | REQUIRED | Analytic unit, population/system, setting, and scope or an explicit justified general scope |
| Evidence strength | REQUIRED | Quality/consistency of the evidence body for this proposition, not effect magnitude |
| Confidence | REQUIRED | Curatorial confidence in this encoded proposition and its transferability |
| Evidence rationale | REQUIRED | Concise explanation connecting cited evidence to direction, mechanism, scope, and limitations |
| Supporting sources | REQUIRED | One or more resolvable evidence records for governed active causal claims |
| Lifecycle, activation, and block status | REQUIRED | Only explicit human governance may assign `GOVERNED` or change `ACTIVE`/`INACTIVE`; research workflow remains `NOT_ELIGIBLE` |
| Governance class | REQUIRED | Preserve `CORE` versus `CONTEXT_DEPENDENT`; neither substitutes for lifecycle status |
| Version/review provenance | REQUIRED | Schema version, record revision, reviewed date, reviewer/decision record, and supersession link where applicable |
| Record creation/source provenance | REQUIRED | Workbook row, decision record, or other origin of the structured record, distinct from scientific supporting sources |
| Causal lag profile | RECOMMENDED | Use bands when supported; never invent numeric precision |
| Effect persistence/recovery | RECOMMENDED | Edge-level persistence, distinct from entity persistence |
| Moderator linkage | RECOMMENDED | Governed moderation uses a separate normalized assertion; inline V3 moderator IDs are migration provenance or candidate linkage only |
| Narrative moderators | RECOMMENDED | Preserve unmodeled moderators without pretending they are canonical entities |
| Conflicting evidence | RECOMMENDED | Structured citations and a disposition (`MIXED`, `CONTRADICTED`, or unresolved) |
| Uncertainty | RECOMMENDED | Directional, magnitude, timing, measurement, and transfer uncertainty as applicable |
| Level-transition mechanism | REQUIRED | Populate when levels differ; use explicit not-applicable only when the levels are the same |
| Relationship strength/effect size | OPTIONAL | Only with measure, scale, population, model, interval, and uncertainty; never map evidence grade to a weight |
| Functional form | OPTIONAL | Populate only when evidence supports a defined monotonic, threshold, saturating, U-shaped, or other form |
| Numeric lag bounds/unit | OPTIONAL | All-or-none and source-supported |
| Exposure pattern | OPTIONAL | Use only where pulse/sustained/cumulative/repeated exposure is part of the claim |
| Reciprocal process ID | OPTIONAL | Links two separately governed, time-indexed opposite-direction edges |
| Pathway IDs | OPTIONAL | Links an edge to one or more governed mediation/mechanism pathways |
| Duplicated endpoint names | OPTIONAL | Derived compatibility/display snapshots only; IDs govern identity |
| Scenario-specific effect weight | NOT APPROPRIATE | Belongs in a scenario/model package, not the universal relationship record |
| Intervention mechanism | NOT APPROPRIATE | Belongs on the intervention-effect record; do not confuse it with Driver-to-Driver mechanism |
| Outcome recommendation | NOT APPROPRIATE | A causal edge is a scientific proposition, not prescriptive advice |

### Strength, evidence, confidence, and uncertainty

These are four different concepts:

- **relationship strength** is an estimated effect under a specified design and
  scale;
- **evidence strength** rates the supporting body of evidence;
- **confidence** rates the reviewer's confidence that the encoded claim is
  correct and transferable at the stated scope; and
- **uncertainty** records what remains unknown or variable.

FCM-like weights may be created in a governed model package from an eligible
subset of relationships. They are not canonical universal relationship
strengths and must retain transformation provenance.

## 4. Moderation and mediation

### Moderation

A moderation assertion has:

- `relationFamily: MODERATION` and `predicate: MODERATES`;
- exactly one `moderatedRelationshipId` resolving to a governed causal edge;
- one or more `moderatorSpecifications`, each naming a canonical entity and
  governed state/range and scale interpretation;
- `combinationRule: INDIVIDUAL` for a single moderator or `JOINT` only for an
  evidence-supported multi-moderator interaction;
- `moderationDirection`: `AMPLIFIES`, `ATTENUATES`, `REVERSES`,
  `NON_MONOTONIC`, or `CONTEXT_DEPENDENT`; and
- its own mechanism, conditions, evidence, confidence, lifecycle, and
  provenance.

It must not be flattened to “moderator causes target.” An unmodeled condition
can remain narrative until it becomes a governed entity.

### Mediation

A causal pathway is a separately identified ordered sequence of governed
causal edges. It records mediator entity IDs, temporal order, scope, evidence
for the mediated interpretation, and whether the mediation is `PARTIAL`,
`FULL`, or `UNDETERMINED`. Every segment keeps its own evidence and fields. A total-effect
source-to-outcome record may coexist only when it represents an independently
estimated claim and is explicitly marked as total/indirect, preventing double
counting with its segments.

For new records, `MEDIATED_PATH` should not label a segment merely because the
segment participates in a longer path. Existing values remain unchanged until
a governed relationship audit considers them.

## 5. RDS participation rules

An RDS is calculated or inferred from constituents. It can be observed and can
summarize a causally relevant state, but it must not silently become an
independent exogenous Driver.

| Endpoint pattern | Presumption | Permitted causal use |
| --- | --- | --- |
| Driver -> Driver | Ordinary case | Allowed when the causal contract is satisfied |
| Driver -> RDS | Conditional | Allowed only when the Driver changes a constituent/configuration or a distinct process changes the derived value; derivation dependencies remain explicit and the RDS is not also independently updated |
| RDS -> Driver | Heightened review | Allowed when the realized relational/derived state is temporally prior and its effect is not definitional or reducible to separately modeled constituent effects |
| RDS -> RDS | Exceptional | Allowed only for temporally separated, non-tautological state transformation; otherwise use derivation, composition, semantic mapping, or association |

All executable uses must follow these rules:

1. An RDS is calculated from governed constituents or initialized from a
   measured value with derivation/scope provenance; it is never an unexplained
   root cause.
2. An intervention does not directly manipulate an RDS. It changes one or more
   constituent Drivers or a governed causal relationship, after which
   the RDS is recalculated.
3. A model must choose either constituent propagation into an RDS or an
   independently estimated aggregate effect for the same causal contribution,
   unless an explicit reconciliation rule prevents double counting.
4. A derivational/semantic dependency is never traversed as causal influence.
5. A causal RDS source must identify the derivation version, aligned scope and
   time window, and the distinct downstream mechanism.
6. A causal RDS target must identify which constituent or configuration is
   changed and when recalculation occurs.
7. `modifiability` inherited by an RDS describes practical change via
   constituents; it does not grant direct manipulability.

The 37 current active causal relationships involving at least one RDS are
preserved. These rules govern their later review; they do not adjudicate them
now.

## 6. Proposed changes relative to Relationship Schema v3

V1 governs an additive, versioned successor design for later implementation:

1. Reconcile documented and implemented relation-family names, using current
   artifact terms as compatibility anchors.
2. Add the explicit `EMPIRICAL_NONCAUSAL` family for Association and qualified-
   state Temporal records.
3. Use family-specific endpoint shapes, including n-ary edge-targeted
   Moderation assertions.
4. Reify moderation and add a causal-pathway container for mediation.
5. Add evidence rationale, conflicting-evidence disposition, uncertainty, and
   complete decision/revision provenance.
6. Define candidate versus governed requirements so incomplete candidates are
   honest while active claims remain reviewable.
7. Treat effect size, functional form, numeric lag, persistence, and exposure
   pattern as evidence-dependent rather than forcing placeholder values.
8. Tighten RDS executable rules and add anti-double-counting validation.
9. Preserve the V3 active/deprecated/candidate separation and the 431-edge
   legacy compatibility view until an approved migration replaces it.

No architecture rule in this document changes current governed relationship
content. Production V1 implementation remains separately unauthorized.

## 7. Internal critique and resulting simplifications

The draft was tested against complexity, reliability, RDS leakage,
practitioner comprehension, defensibility, machine use, provenance, conflict,
versioning, and scale.

- Aggregation was not made a top-level relationship family; it is derivation
  metadata.
- Placement was kept out of the relationship graph.
- Measurement remains primarily in Operationalizations rather than creating a
  second measurement graph.
- Mediation is a pathway, not another edge predicate.
- Fields that the current corpus cannot reliably support—numeric strength,
  functional form, numeric lag, persistence, and exposure—are optional or
  recommended, never fabricated requirements.
- Association and temporal transition are retained as explicit noncausal
  records because they reduce pressure to overclaim causality.
- RDS-to-causal participation is permitted only with derivation grounding and
  anti-double-counting controls.
- The normalized model adds records but avoids embedding large nested graphs;
  IDs and controlled fields remain indexable at thousands-of-record scale.

The result is more expressive than V3 where the current schema has genuine
gaps, while preserving its strongest identity, provenance, lifecycle, and
compatibility decisions.
