# PSYWERX Family Audit Workflow V1

**Status:** Governed workflow design; execution and systematic population not
authorized

**Decision record:**
[`GOV-REL-INT-V1-2026-09-05`](RELATIONSHIP_INTERVENTION_V1_GOVERNANCE_DECISION.md)

**Unit of work:** One Family at one frozen audit version

## 1. Why Family is the unit

Family provides a bounded semantic neighborhood that practitioners can review
without losing Layer and cross-Layer context. It is small enough for a complete
inventory, but it cannot own only internal edges: most causal meaning crosses
Family boundaries.

To avoid duplicated work, the default owner is:

- causal, temporal, realization, and constituent records: the source/subject
  entity's primary Family;
- derivation records: the RDS subject's primary Family;
- symmetric association/semantic records: the lexically lower Family ID, with
  both Families listed as reviewers;
- intervention effects: the primary target Driver's Family; and
- relationship-targeted intervention effects: the source entity's Family for
  the target relationship, with the target Family consulted when different.

Ownership schedules work; it does not grant unilateral governance authority.

## 2. Entry criteria

A Family audit may start only when:

1. the ontology commit, schema versions, source-register version, and audit
   version are frozen;
2. Family ID/name/Layer and current member IDs are exported without changing
   classifications;
3. Driver/RDS counts reconcile with `data/entities.json` and Family totals;
4. all current incident relationship IDs and lifecycle states are inventoried;
5. RDS derivation specifications and blocked fields are available;
6. source access and citation rules are defined;
7. reviewer roles, governance authority, and conflict-of-interest rules are
   assigned;
8. audit scope and exclusions are recorded, including whether external
   unmodeled outcomes may be nominated only as candidates; and
9. the tooling guarantees that candidates cannot enter active canonical data.

A Family with a membership or Driver/RDS dispute may still be researched, but
the audit stays blocked from completion until governance supplies or defers a
decision explicitly. This workflow itself never reclassifies an entity.

## 3. Refined sequence

### Stage A — Freeze and understand the Family

1. Verify the Family boundary, membership, entity IDs, Driver/RDS partition,
   definitions, related Families/Layers, aliases, crosswalks, and known blocked
   fields. Record discrepancies; do not repair them opportunistically.
2. Inventory every owned and incident relationship across active, candidate,
   deprecated, and rejected states. Record baseline counts by relation family,
   endpoint type, internal/same-Layer/cross-Layer, evidence grade, and
   lifecycle.
3. For every RDS, trace constituent specifications, derivation logic, scope,
   recalculation, uncertainty propagation, and current causal participation.
   Flag any use as an exogenous root.

### Stage B — Review current relationships before finding gaps

4. Review existing within-Family records first: proposition identity, causal
   versus derivational/semantic meaning, direction, polarity, mechanism,
   directness, lag, context, evidence, conflicts, and double counting.
5. Review outgoing and incoming same-Layer cross-Family records using the
   ownership rule and consult the other Family.
6. Review outgoing and incoming cross-Layer records, including level-transition
   mechanisms and population/system alignment.
7. Give every current record an audit disposition: retain as-is, revision
   candidate, retype candidate, split candidate, merge/duplicate candidate,
   deprecation candidate, research-needed, or blocked. These are proposals,
   not changes.

### Stage C — Identify and research relationship gaps

8. Generate plausible missing relationships from theory, evidence, entity
   mechanisms, upstream/downstream narratives, intervention pathways, and
   observed graph gaps. Narrative mentions remain retrieval prompts only.
9. Triage each candidate before deep research:
   causal influence, derivation/aggregation, constituent, realization,
   measurement, placement, temporal transition, association, moderation, or
   mediated pathway. Reject category errors and tautologies early.
10. Research surviving candidates. Extract design, population, unit, context,
    temporal order, intervention/exposure contrast, confounding controls,
    mechanism, direction, magnitude when supportable, lag, persistence,
    moderators, boundary conditions, uncertainty, conflicts, and provenance.
11. Assemble review-ready records. Preserve negative and mixed findings; do not
    upgrade association or temporal order to causality.
12. Submit relationship decisions to explicit governance. Implement only the
    recorded decisions, minting new IDs when proposition identity changes.

### Stage D — Build Driver-centered intervention candidates

13. Prioritize actual Drivers by modifiability, decision relevance, evidence
    need, downstream reach, and risk. Do not rank RDS as direct targets.
14. For each Driver, ask the canonical question: what methods, techniques,
    actions, environmental changes, communications, policies, technologies,
    incentives, constraints, services, or packages could increase, decrease,
    stabilize, disrupt, buffer, amplify, suppress, or otherwise modify this
    Driver or one of its causal pathways?
15. Search broadly by Driver construct and mechanism first. Use external method
    taxonomies as later recall aids and crosswalks, never as the starting spine.
16. Distinguish intervention from exposure, measurement, implementation
    prerequisite, desired outcome, and causal mediator. Deduplicate identities
    while retaining materially different delivery variants as effect profiles.
17. Create one Intervention Effect candidate per primary Driver or exact
    relationship target. For multi-target methods, link separate effect records
    through the same Intervention/study/package IDs.
18. Extract implementer, target population, delivery, context, scale, dose and
    timing when meaningful, mechanism of action, prerequisites, moderators,
    boundaries, MOE, evidence, conflicts, uncertainty, unintended effects,
    risks, ethics/legal constraints, and feasibility.
19. If an RDS is named as an outcome, map the intervention to constituent
    Drivers/relationships/context and specify recalculation. If this cannot be
    done, retain a research-needed outcome claim, not an executable target.
20. Submit Intervention and Effect decisions to explicit governance. Approval
    of identity does not approve every effect.

### Stage E — Consequence analysis and closeout

21. Trace downstream consequences only through governed active causal edges.
    Mark every result as an inference, carry context/uncertainty, prevent
    constituent/RDS double counting, and do not write inferred consequences
    into the canonical Intervention object.
22. Run automated completeness and integrity checks, then human scientific,
    ontology, practitioner, ethics/risk, and governance review.
23. Resolve, reject, or explicitly defer every flag. Record blocked items with
    owner, reason, and next action.
24. Publish the Family audit manifest, decision records, before/after counts,
    source packet, validation results, and immutable audited commit. Mark the
    Family complete for that audit version only.

This order improves the proposed sequence by classifying existing semantics
before gap generation, governing relationships before using them for
intervention consequence analysis, and separating automated flags from human
decisions.

## 4. Exit criteria

A Family is complete for an audit version only when:

- every baseline member has a reviewed identity/type/boundary disposition and
  no classification was changed without a separate governance decision;
- every owned current relationship has a recorded audit disposition;
- every incident cross-Family relationship has been checked or has a named
  owner and explicit deferral;
- every RDS has a verified derivation trace and no unexplained executable root
  treatment;
- all nominated relationship candidates have a lifecycle status, evidence
  packet or research-needed reason, and no candidate is `GOVERNED + ACTIVE`;
- every in-scope modifiable Driver was searched for interventions, even when
  the defensible result is “none found”;
- every intervention effect has an exact Driver target or permitted exact edge
  plus mechanistic Driver linkage;
- risks, conflicts, uncertainty, and source provenance are recorded at the
  right level;
- automated metrics ran and every flag has a resolution or explicit deferral;
- required human reviews and governance decisions are linked;
- deterministic builds and application/schema regression tests pass; and
- a completion manifest records audited commit, scope, exclusions, counts,
  open items, approvers, and next review trigger.

“Complete” means systematically reviewed against the stated scope and version.
It never means causally exhaustive or permanently final.

## 5. Completeness and integrity metrics

Metrics are review triggers unless explicitly marked as hard errors. They do
not prove that a missing edge or intervention exists.

### Graph coverage

| Metric | Definition | Default interpretation |
| --- | --- | --- |
| Zero causal in-degree | Eligible entity has no incoming governed active causal edge | Review flag; acceptable for true roots or bounded gaps |
| Zero causal out-degree | Eligible entity has no outgoing governed active causal edge | Review flag; acceptable for outcomes or measurement-only constructs |
| Suspicious high degree | Total causal degree above Layer `Q3 + 3*IQR` or top 1%, whichever flags fewer | Review for umbrella concepts, duplication, or generic edges |
| Isolated Family | No governed active causal edge connects a member to another Family | Review flag, never automatic edge creation |
| Weak cross-Layer connectivity | Family has no cross-Layer causal incident edge, or reviewed theory/evidence expects a Layer transition absent from the graph | Review flag; no quota-based invention |
| Missing causal intermediate | Indirect/total claim or mechanism names a mediator but no governed pathway/segment represents it | Review flag |
| Duplicate exact edge | Same source, target, predicate, scope, and overlapping effective revision | Hard error |
| Semantic duplicate | Different IDs encode materially identical propositions | Review/merge flag |
| Contradictory relationship | Same source/target and overlapping scope have incompatible polarity/direction without conflict linkage | Review flag; preserve conflicting evidence |
| Unresolved reciprocal pair | Reciprocal process has fewer/more than two opposite directed edges | Hard error when reciprocal ID is assigned |
| Placeholder saturation | Required scientific field is repeated boilerplate or unspecified above a reported threshold | Quality flag; a nonempty string is not completeness |

### RDS controls

| Metric | Definition | Default interpretation |
| --- | --- | --- |
| RDS root-cause violation | Executable model initializes an RDS as exogenous without measurement/derivation provenance | Hard error |
| Missing RDS dependency | RDS constituent specification lacks a resolvable entity/external parameter or matching derivation record where required | Hard error or blocked item according to schema stage |
| Aggregate/constituent double count | Same contribution propagates through constituent edges and an aggregate shortcut with no reconciliation rule | Hard error for executable package |
| RDS direct intervention target | Active Effect has an RDS primary target | Hard error in Intervention V1 |
| RDS causal-source review rate | RDS with outgoing causal edge lacking aligned derivation version, scope, and downstream mechanism | Review flag; target 100% disposition |

### Intervention coverage and balance

| Metric | Definition | Default interpretation |
| --- | --- | --- |
| Modifiable Driver with no intervention search | In-scope Driver has no search log | Hard audit-completeness error |
| Highly modifiable Driver with no supported intervention | High-modifiability Driver has no governed effect | Research/prioritization flag, not proof of omission |
| Intervention with no Driver target | Intervention has no active Driver effect and no active edge effect with mechanistic Driver | Hard error for governed active catalog |
| Driver with one modality | Driver's active effects cover only one intervention category/modality | Diversity flag when at least two plausible modalities were searched |
| Layer concentration | Share of active Driver effects by target Layer and category | Report distribution; flag dominance only against a predeclared audit threshold |
| Psychological/Social overconcentration | Psychological + Social target effects divided by all Driver-targeted effects, reported with ontology and search denominators | Review for search bias; no universal cap |
| Multi-target evidence leakage | One source/context claim copied to several Driver effects without target-specific rationale | Review or hard error if fields are identical and unsupported |
| Package inference error | Package effect exists only as sum of component effects without package evidence | Review/hard error for active package effect |

### Evidence and governance

- percentage of active records with resolvable sources, edge/effect-specific
  rationale, explicit scope, conflict disposition, uncertainty, reviewer, and
  decision record;
- age since evidence review and count of triggered re-reviews;
- candidate-to-governed transitions lacking an authorized decision (hard
  error; target zero);
- proportion of candidates rejected/retyped as association, derivation,
  measurement, realization, or placement, reported to detect causal inflation;
  and
- source diversity by study design, population, geography, discipline, and
  publication type, interpreted qualitatively rather than as a quota.

## 6. Family audit manifest

Each completed audit should emit a small machine-readable manifest containing:

- audit ID/version and Family ID;
- baseline and final commit SHAs;
- schema/source-register versions;
- member, relationship, candidate, decision, intervention, and effect counts;
- relationship counts split internal/outgoing/incoming, same-/cross-Layer, and
  causal/noncausal;
- search protocol and date range;
- validation commands/results;
- linked decision records and reviewers;
- all explicit deferrals/blockers; and
- completion status and next review trigger.

The manifest describes process completeness. It must not label the ontology
scientifically exhaustive.
