# INF-F03 activation-readiness audit 001

## Audit authority and boundary

- Audit ID: `AUD-INF-F03-ACTIVATION-V1-20260906-001`
- Scientific pilot: `AUD-INF-F03-AE-V1-20260906-001`
- Governance decision reviewed: `GOV-INF-F03-001-2026-09-06`
- PR: `#18`
- Audited head: `246688fb03b525d223ab1bdd540471ae865a4aae`
- Frozen scientific baseline: `164d938bcd4bbd7e8c48c8128cacd6e64ff0287a`
- Audit date: `2026-09-06`
- Status: independent activation-readiness recommendation; **not an activation decision**

This audit changes no lifecycle or activation state. It reconstructs readiness
from the governed Relationship/Intervention and Actions/Events contracts, the
human decision, current records, candidate lineage, source findings, evidence,
and Driver/RDS safeguards. Green validation is necessary but is not scientific
authorization.

## Decision table

| ID | Type | Current status | Evidence | Dependencies | Scientific readiness | Practitioner readiness | Recommendation | Reason |
|---|---|---|---|---|---|---|---|---|
| `EVA-V1-INF-F03-REL-001` | EvidenceAssessment | `GOVERNED / INACTIVE` | `MIXED / MODERATE / MODERATE`; `SRC-551`, `SRC-552` | Registered sources and two governed source findings | Ready as the exact bounded synthesis | Not applicable | `ACTIVATE_RECOMMENDED` | Source trustworthiness is a constituent measure of `PSY-113`; numeric small/null and verbal adverse findings remain explicit. |
| `REL-V1-INF-F03-001` | Relationship | `GOVERNED / INACTIVE` | `EVA-V1-INF-F03-REL-001` | Evidence first; activation must set V1 executability and add exact human transition provenance | Ready after its evidence is active | Not applicable | `ACTIVATE_RECOMMENDED` | Both endpoints are Drivers; randomized format manipulations support a bounded context-dependent effect with no universal sign. |
| `EVA-AE-V1-INF-F03-001` | EvidenceAssessment | `GOVERNED / INACTIVE` | `MIXED / MODERATE / MODERATE`; `SRC-550` | Feature-scope enforcement correction; then supports EA-001 | Not ready while its target assertion is blocked | Not applicable | `BLOCKED_PENDING_CORRECTION` | Evidence is appropriately bounded, but activating it now would prepare an assertion whose core feature scope is not structurally enforced. |
| `EA-V1-INF-F03-001` | EffectAssertion | `GOVERNED / INACTIVE` | `EVA-AE-V1-INF-F03-001` | Active evidence and active `HT-V1-INF-F03-001`; feature-scope enforcement correction | Not mechanically safe for active consumption | Fails closed | `BLOCKED_PENDING_CORRECTION` | `LEVEL / DECREASE` is stored against multidimensional `INF-077`; named feature scope exists only in free text and a generic consumer can read it as whole-construct reduction. |
| `HT-V1-INF-F03-001` | HappeningType | `GOVERNED / INACTIVE` | Identity source `SRC-550`; effect evidence is separate | Must activate atomically with corrected EA-001 after its evidence is active | Blocked by its only effect | Fails actor, feasibility, legal, ethical, prerequisite, and applicability assessments | `BLOCKED_PENDING_CORRECTION` | An active deliberate Intervention-subset identity must have its own active effect. |
| `EVA-AE-V1-INF-F03-002` | EvidenceAssessment | `GOVERNED / INACTIVE` | `SUPPORTS / MODERATE / MODERATE`; two mixed source findings | `SRC-551` and `SRC-552` | Ready for the exact disclosure-target synthesis | Not applicable | `ACTIVATE_RECOMMENDED` | Findings support the disclosure manipulation while keeping downstream trust results separate and mixed/null. |
| `EA-V1-INF-F03-002` | EffectAssertion | `GOVERNED / INACTIVE` | `EVA-AE-V1-INF-F03-002` | Active evidence and active `HT-V1-INF-F03-002` | Ready as part of an atomic type/effect activation bundle | Fails closed pending actor-specific and implementation assessments | `ACTIVATE_RECOMMENDED` | Exact Driver target; `LEVEL / INCREASE` concerns justified disclosure amount/explicitness, not certainty, correctness, trust, or calibration. |
| `HT-V1-INF-F03-002` | HappeningType | `GOVERNED / INACTIVE` | Identity sources `SRC-551`, `SRC-552`; effect evidence separate | Must activate atomically with EA-002 after evidence is active | Ready as part of the EA-002 bundle | Fails actor, feasibility, legal, ethical, prerequisite, and applicability assessments | `ACTIVATE_RECOMMENDED` | The validator requires every active deliberate Intervention-subset identity to have its own active effect. |
| `HT-V1-INF-F03-004` | HappeningType | `GOVERNED / INACTIVE` | No governed identity source or effect | None structurally; no scientific-use dependency established | Identity is valid but not ready for active use | Not actionable: non-deliberate exposure and control is unknown | `KEEP_INACTIVE` | Its INF-F03 effect remains research-needed. Standalone activation would add no supported effect knowledge. |
| `HT-V1-INF-F03-005` | HappeningType | `GOVERNED / INACTIVE` | `SRC-550` is identity context only; no governed effect | Requires its own active eligible effect | Not activatable under the deliberate-identity rule | Fails closed | `KEEP_INACTIVE` | Automatic simplification efficacy/fidelity remains research-needed. |
| `HT-V1-INF-F03-006` | HappeningType | `GOVERNED / INACTIVE` | No governed identity source or effect | Requires its own active eligible effect | Not activatable under the deliberate-identity rule | Fails closed | `KEEP_INACTIVE` | The instruction-specific effect remains research-needed. |
| `HT-V1-INF-F03-007` | HappeningType | `GOVERNED / INACTIVE` | No governed identity source or effect | None structurally; no scientific-use dependency established | Identity is valid but not ready for active use | Not actionable: non-deliberate biological exposure and control is unknown | `KEEP_INACTIVE` | Its proposed INF-F03 effect remains research-needed; activation would not establish that effect. |

No record requires a new human scientific decision at this checkpoint. EA-001
requires an architecture/schema enforcement correction and exact revised-record
authorization if its record hash changes.

## A. Recommend ACTIVATE

The recommended subset is exactly:

1. `EVA-V1-INF-F03-REL-001`
2. `REL-V1-INF-F03-001`
3. `EVA-AE-V1-INF-F03-002`
4. `HT-V1-INF-F03-002`
5. `EA-V1-INF-F03-002`

This is a recommendation only. A new authorized human activation decision and
exact activation hashes/provenance are required. If activated, the Relationship
baseline would become 457 active total and 436 active causal; Actions/Events
records do not add graph edges.

## B. Recommend KEEP INACTIVE

- `HT-V1-INF-F03-004`: non-deliberate babble exposure; no governed effect or
  identity evidence assessment. Structural activation is possible, but there is
  no supported scientific-use reason to do it.
- `HT-V1-INF-F03-005`: deliberate automatic rewrite identity; its own effect is
  research-needed, so the active-identity validator correctly fails closed.
- `HT-V1-INF-F03-006`: deliberate explicit-timing/referent identity; its own
  effect is research-needed and it has no governed identity source.
- `HT-V1-INF-F03-007`: non-deliberate sleep-loss exposure; no governed effect or
  identity evidence assessment. It remains non-actionable.

## C. Blocked pending mechanical correction

`EA-V1-INF-F03-001`, `HT-V1-INF-F03-001`, and
`EVA-AE-V1-INF-F03-001` form one blocked bundle. The scientific prose is bounded,
but the production EffectAssertion contract stores only:

- target `INF-077`;
- property `LEVEL`;
- change `DECREASE`; and
- the named manipulated feature dimensions in the string-valued
  `scope.measurement` field.

No schema field or validator constrains `DECREASE` to
`LEXICAL_LOW_FREQUENCY` and/or `SYNTACTIC_CENTER_EMBEDDED_CLAUSE`. A generic
consumer could therefore interpret the record as a decrease in the whole
multidimensional Driver, contrary to the authorized semantics. Before activation:

1. add a governed, machine-enforced target-dimension representation or equivalent
   validator-enforced normalized structure;
2. reject whole-construct interpretation when only dimensions are supported;
3. preserve the existing fidelity/legal-obligation, audience-readability,
   comprehension, completeness, and contradiction exclusions; and
4. issue an exact activation authorization for the resulting record hashes.

This is an architecture enforcement correction, not permission to broaden or
revise the scientific claim.

## D. Requires new human scientific decision

None identified. A materially different target, whole-construct claim, source
synthesis, or effect direction would require a new scientific decision.

## Relationship audit

`REL-V1-INF-F03-001` is `INF-015` Claim Uncertainty Disclosure to `PSY-113`
Perceived Source Credibility. Both are Drivers. The source Family, `INF-F03`, is
the deterministic owner and `PSY-F13` is the named consulted endpoint Family.
The governed workflow does not make documented target-Family consultation a
mechanical activation prerequisite for an ordinary cross-Layer causal edge;
ownership does not grant unilateral scientific authority, and the exact human
governance decision supplies that authority. The absent consultation artifact is
a future `PSY-F13` review trigger, not an activation blocker under current rules.

The evidence measures trust/trustworthiness of the source, which aligns with a
core `PSY-113` dimension. It does not establish expertise, benevolence, objective
accuracy, or confidence calibration. Randomized message-format experiments
support causal identification at the reported exposure/assessment scale. The
record uses `CONTEXT_DEPENDENT` polarity and
`CONTEXT_DEPENDENT_NON_MONOTONIC` functional form; neither a universal positive
nor negative sign is encoded. No legacy or V1 proposition duplicates the same
endpoints.

Normal activation materialization must change
`compatibility.v1Executability` from `NOT_EXECUTABLE` to `EXECUTABLE`, remove the
`activationNotAuthorized` incomplete marker, retain
`quantitativeExecutionNotAuthorized`, and add exact human activation provenance.
Those are activation-state mechanics, not corrections to the scientific claim.

## EffectAssertion audits

EA-001 targets the Driver `INF-077`, not the readability RDS `INF-014`. Its prose
correctly requires preservation of intended propositions, limits change to named
features, and excludes automatic comprehension, readability, completeness,
contradiction, and fidelity conclusions. `SRC-550` supports the feature distinction
and processing relevance in English legal text, but does not guarantee a
content-preserving rewrite. That guarantee remains an implementation prerequisite.
The string-only enforcement gap prevents activation.

EA-002 targets Driver `INF-015`. `LEVEL / INCREASE` refers only to the amount and
explicitness of justified quantified uncertainty in the same specified numerical
claim. The record prohibits invented intervals, false precision, an accuracy
guarantee, automatic trust benefit, and automatic confidence-calibration benefit.
Its exact target claim is activation-ready.

## Evidence and source audit

Canonical metadata reconciles with PubMed for all three sources:

- `SRC-550`: Martínez, Mollica, and Gibson (2022), *Cognition*, DOI
  `10.1016/j.cognition.2022.105070`, PMID `35257980`.
- `SRC-551`: van der Bles et al. (2020), *PNAS*, DOI
  `10.1073/pnas.1913678117`, PMID `32205438`.
- `SRC-552`: Kerr et al. (2023), *Royal Society Open Science*, DOI
  `10.1098/rsos.230604`, PMID `38026007`.

All source IDs resolve and no identifier duplicate exists. Access depth is
accurately distinguished: selected full text for `SRC-550` and `SRC-551`, abstract
for `SRC-552`. The three Actions/Events findings are enumerated by ID in their
syntheses. The two Relationship findings are linked to the exact assessment by the
governed source-finding sidecar; both source IDs and mixed/null dispositions are
represented in the RI synthesis. The two uncertainty papers remain separate
publication-level programs; experiments within each paper are not counted as
independent replications. No quantitative estimate, causal weight, or model
inference was added.

The Relationship assessment remains `MIXED / MODERATE / MODERATE`. EA-001 remains
`MIXED / MODERATE / MODERATE`. EA-002 is `SUPPORTS / MODERATE / MODERATE` for
the disclosure manipulation only; its source findings remain `MIXED` because
downstream source-trust results include small/null and adverse format-dependent
effects.

Source findings are nested in governed Actions/Events assessments or linked by
the governed Relationship source-finding sidecar. They do not have independent
activation states and follow the supported EvidenceAssessment.

## Exact dependency order

The production contracts create this activation dependency graph:

```text
SRC-551 + SRC-552 (already registered)
        |
        +--> EVA-V1-INF-F03-REL-001
        |          |
        |          +--> REL-V1-INF-F03-001
        |
        +--> EVA-AE-V1-INF-F03-002
                   |
                   +--> { HT-V1-INF-F03-002 <--> EA-V1-INF-F03-002 }
                              atomic activation bundle
```

Evidence must be active before or in the same transaction as its assertion. The
Relationship may then activate after its evidence. For deliberate Actions/Events,
an active Effect requires an active type and an active type requires its own active
Effect, so the type/effect pair must be activated atomically after its evidence.
There are no cycles outside that validator-defined atomic pair, no dangling
references, and no ownership or lineage collision.

The blocked EA-001 bundle has the same order after the scope correction:
`EVA-AE-V1-INF-F03-001` followed by atomic
`{HT-V1-INF-F03-001, EA-V1-INF-F03-001}`.

## Scientific, model, and practitioner eligibility

This audit addresses scientific activation only. Model eligibility remains false
because no quantitative execution contract or weight is authorized.

Even the scientifically activatable quantified-bounds action remains
practitioner-ineligible until the exact actor/revision, population/context,
actor-specific controllability, prerequisites, feasibility, legal constraints,
ethical/risk constraints, and applicability each have an assessed-pass result with
provenance. The same applies to the blocked surface-revision action. Babble and
sleep loss are non-deliberate exposures and cannot become recommended actions.

## Exclusions and RDS safety

The following remain non-governed/non-active: `REL-CAND-INF-F03-002/003/004`,
`HT-CAND-INF-F03-003`, `EA-CAND-INF-F03-003/004/005/006/007`, existing review
proposals for `REL-INF-003/006/008/041/046/048`, existing research-needed
`REL-INF-007/009`, and hypotheses H04/H07/H08/H09/H12/H13/H16/H17. H20 remains
blocked. H01/H02/H03/H05/H06/H10/H11/H14/H15/H18/H19 remain rejected and were
not regenerated.

`INF-010`, `INF-011`, `INF-014`, and `RDS-0001` retain their derivation logic and
remain indirect recalculated states. The recommended activation subset has no RDS
endpoint or direct RDS target, creates no RDS exogeneity, and introduces no
constituent/aggregate or numerator double propagation.

## Audit conclusion

- `ACTIVATE_RECOMMENDED`: 5 root records.
- `KEEP_INACTIVE`: 4 root records.
- `BLOCKED_PENDING_CORRECTION`: 3 root records.
- `NEEDS_NEW_HUMAN_SCIENTIFIC_DECISION`: 0.
- Status changes performed by this audit: 0.
- Production counts remain 770 Drivers, 41 RDS, 811 entities, 456 active
  Relationships, and 435 active causal Relationships.
