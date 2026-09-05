# PSYWERX Relationship + Intervention Governance V1

**Status:** Proposed governance model; approval required

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
| `GOVERNED_ACTIVE` | Authorized governance decision approved this exact revision and scope | Yes, subject to type-specific executable rules |
| `GOVERNED_INACTIVE` | Governed record is retained but deliberately excluded from default execution | No |
| `BLOCKED_NEEDS_GOVERNANCE_INPUT` | A specific policy/ontology decision is necessary before review can proceed | No |
| `REJECTED` | Reviewed proposition was not accepted; rationale retained | No |
| `DEPRECATED` | Previously governed revision has been retired or superseded | No |

`REVIEW_READY` is intentionally not called “reviewed.” Review is not complete
until a disposition is recorded.

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
provenance, and remain outside active canonical collections.

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

### AI MAY NOT GOVERN

AI may not:

- set `GOVERNED_ACTIVE` or create the equivalent by moving a record into an
  active bucket;
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
mechanism, directness, boundary conditions, evidence strength, and confidence.

Before `GOVERNED_ACTIVE`, an authorized reviewer must explicitly decide:

1. causal versus noncausal interpretation;
2. Driver/RDS endpoint legitimacy and double-counting risk;
3. proposition identity and compatibility/migration behavior;
4. evidence and conflict disposition;
5. applicable scope and executable eligibility; and
6. whether the exact revision is approved.

### Intervention gate

An Intervention and each Effect are governed separately. The Intervention
identity may be approved as `GOVERNED_INACTIVE` while every effect remains
research-needed; it cannot become `GOVERNED_ACTIVE` without an active effect.
An Effect can move to `REVIEW_READY` only when it has an exact primary target,
Driver-centered mechanism/linkage, bounded population/context/scale, direction
or pathway mode, evidence rationale and sources, risk assessment,
uncertainty/conflict disposition, and required provenance.

Before `GOVERNED_ACTIVE`, an authorized reviewer must explicitly decide:

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
| Active governed legacy relationship | `GOVERNED_ACTIVE`, preserving exact proposition and prior provenance |
| `PROPOSED` candidate | `CANDIDATE` or `RESEARCH_NEEDED` after explicit migration review |
| `BLOCKED_NEEDS_GOVERNANCE_INPUT` | Same status |
| Deprecated relationship | `DEPRECATED` |

The 431 current causal records are not re-reviewed by adopting this
architecture. Their field upgrades happen only through the later systematic
Family workflow and explicit decisions.

## 7. Publication and CI controls

Future implementation should enforce:

1. candidate and active collections are physically or logically separated;
2. only a signed/identified governance decision can change a record to
   `GOVERNED_ACTIVE`;
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

## 9. Decisions reserved for explicit approval

The following cannot be implemented from this proposal alone:

- adoption of the relationship-family/predicate vocabulary;
- permission to add association and temporal-transition records;
- the edge-target representation for moderation and the pathway representation
  for mediation;
- changes to current `directness` semantics;
- the canonical Intervention, Effect, Package, and crosswalk datasets;
- intervention category/effect-mode vocabularies;
- the no-direct-RDS-target rule and executable RDS validation;
- lifecycle/evidence-disposition names and authorized approval roles;
- migration of any V3 record or workbook Operationalization;
- resolution of the current `NON_AUTHORITATIVE_MIGRATION_PREVIEW` authority
  label relative to the CI-protected v0.3 artifacts;
- thresholds used as governance gates rather than review flags; and
- any change to application behavior, scenario contracts, source workbooks, or
  current governed ontology content.
