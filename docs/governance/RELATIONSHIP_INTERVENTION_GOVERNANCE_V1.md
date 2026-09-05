# PSYWERX Relationship + Intervention Governance V1

**Status:** Governed architecture; production implementation not authorized

**Decision record:**
[`GOV-REL-INT-V1-2026-09-05`](RELATIONSHIP_INTERVENTION_V1_GOVERNANCE_DECISION.md)

**Current protection:** Driver/RDS v0.3 data and the 431 governed causal
relationships remain protected and unchanged

## 1. Core rule

No model output, generated file, research note, candidate record, pull request,
or passing CI check is a governance decision. A record becomes canonical only
through an explicit PSYWERX governance approval captured in immutable decision
provenance.

CI proves conformance and determinism. It cannot prove scientific validity,
ethical acceptability, or governance approval.

## 2. Separate lifecycle from evidence disposition

Terms such as “supported,” “disputed,” and “reviewed” mix different questions.
V1 separates workflow state from the state of the evidence.

### Lifecycle status

| Status | Meaning | Canonical/executable? |
| --- | --- | --- |
| `CANDIDATE` | Proposition or intervention/effect has been captured but not researched | No |
| `RESEARCH_NEEDED` | Required evidence, scope, mechanism, or field work is incomplete | No |
| `REVIEW_READY` | Required structure and source packet are complete for a human decision | No |
| `GOVERNED` | Authorized human governance approved this exact revision and scope | Only when `activationStatus: ACTIVE` and type-specific executable rules pass |
| `REJECTED` | Reviewed proposition was not accepted; rationale retained | No |
| `DEPRECATED` | Previously governed revision has been retired or superseded | No |

`REVIEW_READY` is intentionally not called “reviewed.” Review is not complete
until a disposition is recorded.

### Activation status

| Status | Meaning |
| --- | --- |
| `NOT_ELIGIBLE` | Non-governed research record; cannot enter production scientific use |
| `ACTIVE` | Governed record is eligible for default production scientific use subject to type-specific rules |
| `INACTIVE` | Governed or deprecated record is deliberately excluded from default production use |

`CANDIDATE`, `RESEARCH_NEEDED`, `REVIEW_READY`, and `REJECTED` require
`NOT_ELIGIBLE`. `DEPRECATED` requires `INACTIVE`. Only `GOVERNED + ACTIVE` is
eligible for default production scientific use.

### Block status

`blockStatus` is `NONE` or `NEEDS_GOVERNANCE_INPUT`. A block is an orthogonal
condition, not a lifecycle stage, and never grants canonical authority.

### Evidence disposition

| Disposition | Meaning |
| --- | --- |
| `NOT_ASSESSED` | No completed evidence appraisal |
| `SUPPORTS` | Reviewed evidence supports the bounded claim |
| `MIXED` | Material heterogeneity or conflict remains |
| `CONTRADICTED` | Stronger or more applicable evidence weighs against the claim |
| `INSUFFICIENT` | Evidence cannot justify the proposed claim at the stated scope |

Evidence disposition does not activate a record. A `MIXED` claim can be
governed for a narrow context; a `SUPPORTS` claim remains noncanonical until
approved.

## 3. Required decision provenance

Every governed revision requires:

- permanent record ID and integer revision;
- lifecycle status and evidence disposition;
- schema version;
- proposer and proposal date;
- research/review packet ID or URI;
- authorized decision record ID or URI;
- approver identity or governed role;
- decision date and effective version;
- concise decision rationale;
- source IDs and conflict disposition;
- prior revision/supersedes links; and
- next review date or review trigger when appropriate.

Changing endpoint identity, target kind, predicate/effect mode, or causal
polarity changes proposition identity: mint a new ID and crosswalk/deprecate the
old record. Correcting metadata or adding evidence without changing the claim
increments the revision. History is append-only.

## 4. Authority boundary

### AI MAY PROPOSE

- candidate relationships, relationship types, intervention identities,
  intervention effects, aliases, external crosswalks, and possible gaps;
- candidate rejection reasons such as association-only evidence, derivation,
  tautology, double counting, or unresolved scope; and
- candidate pilot priorities and completeness flags.

All AI proposals start as `CANDIDATE` or `RESEARCH_NEEDED`, carry generation
provenance, remain `NOT_ELIGIBLE`, and stay outside active canonical
collections.

### AI MAY RESEARCH

- locate and summarize sources;
- extract study design, population, context, direction, effect estimates,
  uncertainty, moderators, timing, implementation, harms, and limitations;
- compare conflicting evidence and draft an evidence disposition; and
- identify where evidence supports association but not causation.

AI-produced research must preserve citations and clearly distinguish source
claims from synthesis or inference.

### AI MAY STRUCTURE

- validate IDs and schemas;
- normalize approved controlled terms without changing substantive meaning;
- assemble review packets;
- compute graph/completeness metrics;
- identify duplicates and contradictions for review;
- draft records with missing fields explicitly marked; and
- implement an already recorded governance decision exactly.

AI/automation may autonomously manage the non-governed workflow transitions
`none → CANDIDATE`, `CANDIDATE ↔ RESEARCH_NEEDED`,
`RESEARCH_NEEDED → REVIEW_READY`, and `REVIEW_READY → RESEARCH_NEEDED` when
rationale, actor class, timestamp, object/revision, and provenance are recorded
and `activationStatus` remains `NOT_ELIGIBLE`.

Every lifecycle or activation transition records actor class, rationale,
timestamp, object ID/revision, and provenance, plus a governance-decision
reference where required. Automation may mechanically materialize an already
authorized exact human decision only when that decision specifies the exact
object, revision, content, or deterministic transformation; automation may not
broaden or reinterpret it.

### AI MAY NOT GOVERN

AI may not:

- move a record from `REVIEW_READY` to `GOVERNED` or `REJECTED`;
- set or change `ACTIVE`/`INACTIVE`, deprecate governed content, resolve a block
  by changing canonical meaning, or approve a substantive governed revision;
- decide that association, temporal order, derivation, or realization proves
  causality;
- reclassify a Driver/RDS, resolve a boundary dispute, or relax a protected
  invariant;
- invent mechanism, effect direction, magnitude, timing, persistence,
  population applicability, risk, or evidence;
- silently resolve conflicting evidence;
- approve an intervention for operational use or imply safety/legality; or
- treat a passing automated check as substantive approval.

## 5. Review gates

### Relationship gate

A relationship can move to `REVIEW_READY` only when its proposition identity,
relation family, endpoint typing, scope, evidence rationale, sources,
uncertainty/conflict disposition, and required type-specific fields are
complete. Causal relationships additionally require direction, polarity,
mechanism, causal claim role, boundary conditions, evidence strength, and
confidence.

Before `GOVERNED + ACTIVE`, an authorized human governor must explicitly decide:

1. causal versus noncausal interpretation;
2. Driver/RDS endpoint legitimacy and double-counting risk;
3. proposition identity and compatibility/migration behavior;
4. evidence and conflict disposition;
5. applicable scope and executable eligibility; and
6. whether the exact revision is approved.

### Intervention gate

An Intervention and each Effect are governed separately. The Intervention
identity may be approved as `GOVERNED + INACTIVE` while every effect remains
research-needed; it cannot become `GOVERNED + ACTIVE` without an active effect.
An Effect can move to `REVIEW_READY` only when it has an exact primary target,
Driver-centered mechanism/linkage, bounded population/context/scale, direction
or pathway mode, evidence rationale and sources, risk assessment,
uncertainty/conflict disposition, and required provenance.

Before `GOVERNED + ACTIVE`, an authorized human governor must explicitly decide:

1. whether the object is an intervention rather than a measure or outcome;
2. whether its exact Driver or relationship target is correct;
3. whether RDS is only an outcome/indicator and constituents are explicit;
4. whether effect, harms, ethics, and transfer claims match the evidence;
5. whether package/component claims are separate; and
6. whether the exact revision and scope are approved.

## 6. Compatibility with current V3 states

No automatic migration is authorized. A future approved migration may map:

| Current V3 | Proposed lifecycle starting point |
| --- | --- |
| Active governed legacy relationship | `GOVERNED + ACTIVE`, preserving exact proposition and prior provenance |
| `PROPOSED` candidate | `CANDIDATE` or `RESEARCH_NEEDED` after explicit migration review |
| Blocked candidate | Existing lifecycle plus `blockStatus: NEEDS_GOVERNANCE_INPUT` and `activationStatus: NOT_ELIGIBLE` |
| Deprecated relationship | `DEPRECATED + INACTIVE` |

The 431 current causal records are not re-reviewed by adopting this
architecture. Their field upgrades happen only through the later systematic
Family workflow and explicit decisions.

## 7. Publication and CI controls

Future implementation should enforce:

1. candidate and active collections are physically or logically separated;
2. only an identified authorized human governance decision can change a record
   to `GOVERNED` or change its `ACTIVE`/`INACTIVE` status;
3. pull requests show candidate-to-active transitions explicitly;
4. schema checks reject AI-generation provenance as approval provenance;
5. references, IDs, revisions, crosswalks, and supersession chains resolve;
6. active causal traversal excludes all noncausal and nonactive records;
7. RDS executable checks reject unexplained exogenous roots and duplicate
   constituent/aggregate propagation;
8. intervention checks reject active effects with no clear Driver target or
   mechanistic Driver linkage;
9. generated artifacts rebuild deterministically on Linux and Windows; and
10. source workbooks, migration handoff records, and governed artifacts cannot
    change as an incidental side effect of a documentation or candidate PR.

## 8. Conflict, dispute, and urgent safety handling

New conflicting evidence creates a new evidence review; it does not silently
overwrite prior rationale. Governance may narrow, inactivate, supersede, or
deprecate the record. If a governed intervention effect presents a credible
safety, rights, or legal risk, an authorized maintainer may follow the
repository's emergency inactivation process, but the decision and rationale
must still be recorded and later reviewed.

## 9. Governed decisions and remaining implementation gate

D01–D14 are governed by the linked decision record. That approval does not
authorize production schemas or datasets, migration of V3 records or workbook
Operationalizations, Family audits, scientific population, modeling/application
changes, or deployment. The migration-preview authority label is handled only
through the separately authorized baseline-adoption action. Production V1
implementation remains a separate governance action.
