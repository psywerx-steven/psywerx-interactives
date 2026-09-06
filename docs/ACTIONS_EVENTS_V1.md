# Actions & Events V1: production-compatible infrastructure

Authority: [AE01–AE12](governance/ACTIONS_EVENTS_V1_GOVERNANCE_DECISION.md),
GOV-ACTIONS-EVENTS-V1-2026-09-06. Architecture/tooling only; native scientific stores
are empty. BIO-F01 remains existing scientific knowledge, not newly governed here.
The [original proposal](../experiments/actions-events-vnext/ARCHITECTURE_PROPOSAL.md)
documents the researched design rationale; this document describes implemented contracts.

## Object boundaries

| Contract | Meaning | Not implied |
|---|---|---|
| HappeningType | Reusable action/event/exposure/process identity; overlapping kind/domain tags | Target-specific efficacy; a Driver subclass |
| Occurrence | Particular OBSERVED, PLANNED or HYPOTHETICAL realization with time/system boundary | Causation from occurrence evidence |
| EffectAssertion | One scoped proposition about one Driver or exact governed causal Relationship | Universal effects, downstream graph completeness |
| EvidenceAssessment + sourceFindings | Assertion-specific source results before synthesis | Independent replications from overlapping datasets |
| Compatibility view | SAME_IDENTITY view of an existing RI record, exact original embedded | A second assertion or new authority |
| Use eligibility | Calculated scientific/model/practitioner checks | A lifecycle, recommendation, rank or executable model |

Contracts are [versioned JSON Schema 2020-12](../schemas/actions-events/v1/catalog-v1.schema.json).
Common scope/control/profile/provenance definitions and existing RI governance
are referenced, not replaced. Native catalog and candidate envelope reference
modular object contracts. No existing production schema or consumer was changed.

A HappeningType may have multiple origin Layers, independently of exact target
Layers derived from Driver membership or edge endpoints. Nine overlapping domain
tags provide search recall without creating new ontology Layers. Deliberate
Interventions remain an explicit subset. Identity-defining schedules/doses belong
in the type only if they define the reusable action; effect-specific values remain
in the effect. Packages need two unique acyclic components and explicit EXHAUSTIVE
or NON_EXHAUSTIVE enumeration; package and component evidence never transfer.

Occurrence externality is relative to a required named system boundary. It never
means random/unconfounded/exogenous. OBSERVED requires occurrence-specific
supporting findings. An occurrence is optional for reusable effect knowledge.
No event-stream ingestion or observation extractor is implemented.

## Effect-property contract

The eleven properties and property-constrained descriptors are machine-readable
in [vocabulary.json](../schemas/actions-events/v1/vocabulary.json): LEVEL,
VARIABILITY, RATE, THRESHOLD, TIMING, PERSISTENCE, RELATIONSHIP_STRENGTH,
RELATIONSHIP_DIRECTION, ENABLEMENT, FUNCTIONAL_SHAPE and STRUCTURE.
Property and change are independent fields with compatibility constraints.
Distribution/reach, subgroup heterogeneity, interaction/synergy/antagonism,
intended/observed change and stakeholder-qualified valence are qualifiers.
Real-world structural changes never edit ontology edges.

Knowledge status distinguishes NOT_INVESTIGATED, NOT_APPLICABLE,
INSUFFICIENT_EVIDENCE, SUPPORTED_EFFECT and SUPPORTED_NULL. Unknown change is
UNKNOWN, not zero. Bounded null requires an explicit precision/interpretation
rationale, not nonsignificance alone. Cyclic/non-monotonic effects cannot carry a
universal observed increase/decrease. OTHER_SPECIFIED requires explanatory text.

DRIVER targets resolve only to canonical Drivers, never RDS, including for natural
events. RDS may be outcomes/measurements/recalculated states. Formula-entailed
causation is rejected. Event/Driver representations require duplicate-propagation
control. No CONTEXT_CONDITION or ALTER_CONTEXT exception exists.

RELATIONSHIP targets resolve to an exact governed causal edge. Active use requires
a mechanistic Driver linkage, active edge and bounded mechanism/scope/evidence.
Mechanism may be PARTIAL: a fully reconstructed pathway is not required. Moderator
Driver effects and edge modifications use shared contribution groups, one PRIMARY
route and explicit non-additive reconciliation. Moderator segments retain separate
assertion evidence. No automatic edge/pathway generation or route summation occurs.

## Evidence before synthesis

Each sourceFinding has a stable finding ID, canonical source ID, actual access
depth, passage/result locator, scope/design/bases, exposure/comparator/measurement,
timing, disposition, uncertainty, limitations and dataset/overlap references.
Numeric estimates are optional; scientific confidence is reasoned, not numeric.
Source findings can be supporting, mixed, null, contrary or insufficient.

Synthesis must list every finding and explicitly disposition every mixed/null/
contrary finding. A supportive overall synthesis with contrary results requires
an explicit rationale rather than erasing those results. Automated validation
checks structure/linkage, not whether a paper scientifically justifies a claimed
causal identification; independent source-alignment review remains mandatory.

Claim semantics, multiple evidence bases, extraction/synthesis/model/hypothesis
production method, disposition, confidence, clarity, provenance and governance/use
remain distinct. Model inputs are labeled MODEL_INPUT, never direct observations.
An occurrence or association finding cannot establish causal effect knowledge.
Dataset identifiers expose dependence; they do not automatically compute an
independence correction or evidence score.

Source registration triage only compares normalized DOI/PMID (exact identifier
match) and title/year (review flag). It writes nothing, does not fetch papers,
and does not automatically merge/register bibliographic records.

## D12, isolation and use boundaries

Native records retain the existing RI lifecycle/activation/block vocabulary and
transition validator. A continuous transition chain and exact independent human
decision path + ID/revision/content hash are required for governed records.
Architecture approval cannot supply scientific approval. The ledger is auditable
provenance, not a cryptographic identity/permission service; repository human review
and access controls still establish that an authorization is authentic.

Candidate stores permit only non-governed research states and NOT_ELIGIBLE.
Pass A embeds existing RI schemas/semantic validation; Pass B uses AE contracts.
Question dispositions are research-log labels, not a second scientific lifecycle.
Rejected-hypothesis logs preserve prior decisions; records may not silently govern.
Readiness booleans record a review attestation, not an automatic scientific verdict.

Scientific eligibility requires governed-active assertions and dependencies.
Quantitative model eligibility currently always returns false because no numerical
execution contract is authorized. Practitioner-action checks additionally require
a deliberate identity, independent active effect, exact actor/revision/scope,
control capability and explicit prerequisite, feasibility, legal, ethical/risk and
applicability assessments with rationale/provenance. Unknown fails closed.
Contradicted or insufficient overall effect evidence also blocks practitioner
eligibility even when a record remains scientifically active for inspection.
An external disaster remains non-actionable. These predicates do not select,
rank, optimize or recommend anything, and no existing UI/scenario consumer calls
them. A caller's applicability assessment still needs genuine human/scientific
review; a boolean cannot demonstrate clinical or legal suitability.

Synthetic fixtures require SYN- IDs and SYNTHETIC / NON_PRODUCTION labels and a
separate synthetic context. Even fictional active simulations return all real
use-eligibility flags false. No production importer or activation writer exists.

## ID-stable compatibility, not migration

The bridge exposes 25 read views (9 Interventions, 5 Effects, 11 EvidenceAssessments),
keeping exact IDs, revisions, full originals, hashes, governance, activation,
lineage, package descriptions and mixed evidence. Views are validated against
the current source record; stale/modified views fail. Exact restoration and
deduplication are tested. Unsupported origin/control/sourceFinding/observed-change
fields stay empty/unassessed and are named in incompleteFields. No source-level
finding is invented by parsing legacy narrative. Only unambiguous CHANGE_LEVEL
mapping is normalized; other legacy modes remain verbatim with null new fields.
Views are a distinct compatibility contract, not falsely complete native objects.

BIO-F01 has 5 active Interventions, 4 inactive identities, 5 active Effects and
11 active EvidenceAssessments. Timed-light/melatonin MIXED evidence, cyclic phase
direction and non-exhaustive CBT-I composition survive unchanged. The 450 V3
relationship projections contribute zero additional propositions.

## Commands and output safety

```text
python scripts/actions_events_v1.py --validate-repository
python scripts/actions_events_v1.py --compatibility-summary
python scripts/actions_events_synthetic.py
python scripts/audit_family.py --family BIO-F01 --output reports/actions-events-v1/current
python -m unittest discover -s tests -p test_actions_events_v1.py
python -m unittest discover -s tests -p test_audit_family.py
python scripts/validate_actions_events_v1.py
```

The Family runner is mechanical, deterministic at a frozen commit, and writes only
to the explicitly supplied child of reports/actions-events-v1 or
experiments/actions-events-vnext. Canonical/root/prefix/symlink escapes are rejected.
It outputs all-Layer coverage, distinct semantic matrices, the exact requested
Family baseline/aliases/crosswalks/RDS/incident records, an empty two-pass workspace
and scientific integrity hashes. No edge search or candidate creation occurs.

Coverage flags are recorded coverage, not missing science. Queue score is transparent:
see scoreComponents per Family. Directed ownership follows source Family; symmetric
ownership uses lexically first Family; edge modifications follow edge owner.
Other endpoint/moderator Families are consulted. A shared issue is not duplicate
scientific content. Future use follows the [five research prompts](governance/ACTIONS_EVENTS_RESEARCH_PROMPTS_V1.md).

## Limits and deferred work

No native AE science, normalized BIO source findings, new activation, Family #2
audit, real occurrence ingestion, quantitative weights, recommendation/model
algorithm or app integration is included. Cross-Family identity and evidence
deduplication still need real-pilot validation. Mechanical checks cannot settle
construct alignment, causal identification, transferability or evidence sufficiency.
The production-capable contracts are not a claim of scientific graph completeness.
