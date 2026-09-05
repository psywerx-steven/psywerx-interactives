# PSYWERX Relationship + Intervention Infrastructure V1

**Status:** Production-capable infrastructure; scientifically unpopulated
beyond lossless access to preserved Relationship V3 content

**Implementation record:**
[Relationship + Intervention V1 Implementation](governance/RELATIONSHIP_INTERVENTION_V1_IMPLEMENTATION_RECORD.md)

**Governed design:** D01–D14 in the
[Relationship + Intervention V1 Governance Decision](governance/RELATIONSHIP_INTERVENTION_V1_GOVERNANCE_DECISION.md)

## 1. Production components

The canonical schemas are in
[`schemas/relationship-intervention/v1/`](../schemas/relationship-intervention/v1/).
Shared EvidenceAssessment and governance contracts are referenced by the
scientific-object schemas rather than copied into each object. JSON Schema
enforces shape and bounded vocabularies; the Python semantic validator enforces
catalog identity, reference integrity, graph rules, package cycles, RDS gates,
and authorized state transitions.

No native V1 scientific data catalog exists yet. The empty candidate workspace
is not a production graph input.

## 2. Relationship V1

`relationFamily` and its permitted `predicate` values are:

| Family | Predicates | Causal traversal |
| --- | --- | --- |
| `CAUSAL` | `CAUSES`, `ENABLES`, `CONSTRAINS` | Only `GOVERNED + ACTIVE`, complete, executable V1 records |
| `EMPIRICAL_NONCAUSAL` | `ASSOCIATED_WITH`, `PRECEDES`, `TRANSITIONS_TO` | Never |
| `MODERATION` | `MODERATES` | Never as an ordinary edge |
| `DERIVATIONAL` | `DERIVED_FROM` | Never |
| `COMPOSITIONAL` | `CONSTITUENT_OF`, `MEMBER_OF` | Never |
| `REALIZATION` | `REALIZES` | Never |
| `SEMANTIC` | `NARROWER_THAN`, `BROADER_THAN`, `OVERLAPS_WITH`, `EQUIVALENT_UNDER_CONDITIONS`, `INVERSE_UNDER_ALIGNED_SCOPE`, `RELATED_METRIC` | Never |

`predicate` is the only subtype field. Mechanism, functional form, evidence,
and pathway participation remain separate.

Associations are symmetric and stored once with lexically ordered endpoint IDs.
They may coexist with a separate causal assertion but never inherit its causal
semantics or weight. `PRECEDES` and `TRANSITIONS_TO` are directed but
noncausal. A transition requires explicit source and target state definitions,
observation unit, time origin, horizon/risk set, population/system, and context;
a bare entity transformation is invalid.

Moderation is an n-ary Relationship record targeting exactly one governed
causal edge. `INDIVIDUAL` names exactly one moderator; `JOINT` names at least
two and represents an evidence-supported joint claim. Moderators require
state/range and scale interpretation. Validation never generates causal edges
from a moderation assertion.

For causal records, `causalClaimRole` is one of `MODELED_LOCAL_LINK`,
`TOTAL_EFFECT`, or `UNRESOLVED_SHORTCUT`. `legacyDirectness` is compatibility
provenance only. It cannot control V1 traversal. Graph adjacency is computed;
evidence estimand and mechanistic directness remain inside EvidenceAssessment.

## 3. Driver/RDS safeguards

The validator computes the mandatory review gate from exact endpoint types:

- Driver → Driver: `STANDARD_CAUSAL`;
- Driver → RDS: `HEIGHTENED_CAUSAL`;
- RDS → Driver: `HEIGHTENED_CAUSAL`; and
- RDS → RDS: `EXCEPTIONAL_CAUSAL`.

Before a native RDS-involving causal record may be active, its safeguard record
must resolve derivation version/inputs, calculation window, temporal and
mechanistic independence, constituent overlap, shared denominators,
definitional entailment, duplicate propagation, and exogenous use. Preserved V3
records are not rejected when those V1 fields are absent; they remain explicitly
legacy-only and V1-incomplete.

## 4. EvidenceAssessment V1

EvidenceAssessment is a normalized object linked to exactly one assertion. It
holds source IDs, rationale, evidence strength, scientific confidence, evidence
disposition, population/context, study-design characterization, optional
quantitative estimate, uncertainty, conflicting/null evidence, limitations,
review provenance, and governance state.

Quantitative estimates are optional. Evidence strength and confidence are not
graph weights. An active assessment requires sources, rationale, and assessed
strength/confidence/disposition.

## 5. CausalPathway V1

A CausalPathway is a separate governed assertion over two or more ordered,
contiguous governed causal Relationship IDs. It records start/end entities,
intermediate roles, aligned scope, temporal-order rationale, pathway-specific
evidence, and partial/full/undetermined mediation classification.

`contributesCausalEdge` is fixed to `false`. Graph reachability cannot create a
pathway. If a governed total-effect edge has the same start/end entities, the
pathway must name it under an explicit `RECONCILED` duplicate-counting rule;
otherwise validation fails.

## 6. Intervention and InterventionEffect V1

Intervention is reusable action identity. Its `interventionKind` is `ATOMIC` or
`PACKAGE`. Packages contain at least two unique Intervention IDs; the validator
rejects missing components, self-membership, and composition cycles.

InterventionEffect is one contextual scientific assertion about one exact
target. Direct target kinds are only `DRIVER` and `RELATIONSHIP`:

- Driver targets must resolve to canonical Drivers; RDS targets are rejected.
- Relationship targets must resolve to governed causal Relationships, use
  `MODIFY_RELATIONSHIP`, and include a canonical mechanistic Driver before
  activation.

RDS IDs may appear as outcomes or measures but not as direct targets. Component
effects never imply a package effect; an active package requires its own active,
independently evidenced effect.

Controlled categories, effect modes, intended directions, delivery modalities,
scale, population scope, context scope, evidence strength, and confidence match
D08. `OTHER_SPECIFIED` requires explanatory text. External technique taxonomies
are optional future crosswalks, not PSYWERX's canonical hierarchy.

## 7. Governance enforcement

Lifecycle, activation, block, scientific confidence, evidence disposition, and
decision outcome are independent fields. Only `GOVERNED + ACTIVE` can enter
default V1 production scientific use.

Automation and researchers may move records only through the governed
non-eligible research transitions. Transitions to `GOVERNED`, `REJECTED`,
`ACTIVE`, `INACTIVE`, or `DEPRECATED`, and substantive governed revisions,
require an authorized human decision record. Automation may mechanically apply
an exact named decision but cannot broaden it. Deprecated records cannot be
reactivated.

## 8. V3 compatibility adapter

Run:

```powershell
py scripts/relationship_intervention_v1.py --validate-repository
```

The adapter projects all 450 active V3 records in memory with stable IDs, exact
endpoints, predicate, polarity, mechanism, evidence/source IDs, source record,
and hash. `SEMANTIC_MAPPING` is the governed D01 alias for V1 `SEMANTIC`; the
legacy value remains recorded. `directness` is copied only to
`legacyDirectness`.

The adapter does not infer causalClaimRole, evidence rationale, functional form,
numeric lag, persistence, moderation, or pathways. Each current projection is
therefore `INCOMPLETE` and `LEGACY_ONLY`, with named blocked fields, while its
existing V3 authority remains `PRESERVED_V3_GOVERNED_ACTIVE`. The exact V3
record is embedded in-memory with a content hash and round-trips byte-for-data
equivalently. Existing V3 consumers continue reading unchanged
`data/relationships.json`.

## 9. Candidate workspace and future Family audits

The workspace at
[`data/candidates/relationship-intervention-v1/`](../data/candidates/relationship-intervention-v1/)
is physically separate, declares `productionGraphEligible: false`, and is empty.
Every future record there must use `CANDIDATE`, `RESEARCH_NEEDED`, or
`REVIEW_READY` with `activationStatus: NOT_ELIGIBLE`. The validator rejects any
governed, active, rejected, or deprecated record in that directory and proves
candidate causal records cannot enter traversal.

A separately authorized Family audit may later write research candidates to
this workspace and submit exact records for human governance. This
infrastructure does not start that process and does not claim that the current
relationship graph is complete.
