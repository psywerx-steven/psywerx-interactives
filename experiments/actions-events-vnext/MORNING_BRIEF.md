# Morning brief: Actions & Events

**Proposal only. All twelve architecture decisions are PENDING.**

## 1. Proposed design

Keep **Actions & Events** as the public working name. Separate a reusable
`HappeningType`, a particular `Occurrence`, and a contextual `EffectAssertion`.
An Intervention remains an identifiable deliberate-action subset with its
existing IDs and package semantics. An event can be observed without its
effects being established; a disaster never becomes an available practitioner
action simply because it has effects.

Effects still target exact Drivers or causal Relationships. Events do not gain
an RDS-targeting exception. Source findings preserve supportive, mixed, null and
contrary results before a separate synthesis. Evidence basis, causal semantics,
model inference, confidence, completeness, governance and actor control remain
different questions.

## 2. What was built

The isolated package contains a researched proposal, twelve decision rows, five
copy-ready research prompts, nine architecture sources, five modular draft
schemas, a synthetic semantic prototype, and a read-only Family inventory tool.
The examples cover every origin Layer and eleven effect properties: level,
variability, rate, threshold, timing, persistence, strength, direction,
enablement, shape and structure. The dry run cannot activate production records.

The inventory exports all 105 Families and 811 entities, separate semantic
matrices, candidate/legacy/native status counts, RDS flags and a complete audit
queue. A supplied Family ID produces its original baseline and an empty research
template. Resolved output paths are confined to this experiment. Existing
regeneration tests run in an isolated copy; actual results are recorded in
[TEST_RESULTS.json](TEST_RESULTS.json).

Local validation passed: **49 prototype tests, 96 existing Python tests and
21 scenario-service tests**, including the exact 811-entity catalog sweep.
Schema/meta-validation, local links, Python/JavaScript checks and deterministic
regeneration passed. All 234 protected files stayed byte-identical. The saved
[synthetic dry run](reports/synthetic-dry-run.json) changed zero statuses.

## 3. What the inventory shows

The actual starting main matches the last known baseline:
`2636dd9a8b7bad1da3d7dfa21db5fe877f4de4e1`.

| Layer | Families | Drivers | RDS | Causally isolated entities |
|---|---:|---:|---:|---:|
| Biological | 14 | 72 | 5 | 48 |
| Psychological | 14 | 134 | 1 | 52 |
| Social | 12 | 83 | 23 | 34 |
| Cultural | 13 | 90 | 1 | 28 |
| Physical/Environmental | 13 | 109 | 0 | 48 |
| Institutional/Structural | 13 | 112 | 4 | 49 |
| Informational | 13 | 71 | 7 | 22 |
| Technological | 13 | 99 | 0 | 16 |
| **Total** | **105** | **770** | **41** | **297** |

There are 450 legacy active Relationships plus 6 native V1 records: 456 total,
435 causal. The 450 V1 projections add no propositions. Causal coverage is 200
within-Family, 146 same-Layer cross-Family and 89 cross-Layer edges. Eleven Families
have no causal connection to another Family; four have no causal incident edge.
Thirty-seven have no cross-Layer causal link. These are coverage observations,
not evidence that missing edges should be invented.

All five active InterventionEffects target Biological Drivers. BIO-F01 retains
six active native Relationships, five active Intervention identities, five active
effects, eleven active EvidenceAssessments and four inactive governed identities.
Eighteen RDS have outgoing causal claims needing the existing safeguards; all 450
legacy projections remain incomplete/legacy-only. B01–B05 remain unresolved.

The provisional queue places SOC-F07, existing BIO-F01 follow-up and INF-F03 first,
primarily because of RDS complexity and incomplete legacy coverage. It is a
transparent scheduling rubric, not scientific adjudication or audit authorization.

## 4. Decisions for you

Review AE01–AE12 in [GOVERNANCE_DECISIONS.md](GOVERNANCE_DECISIONS.md). The central
choices are the three-object model, overlapping kind/origin tags, universal
Driver/RDS safeguards, factored effect vocabulary, source-finding normalization,
duplicate-contribution control, ID-stable compatibility and separate actor-action
eligibility. Approve, modify or reject exact semantics; no recommendation here
is treated as authorization.

## 5. What can run next

The read-only inventory and synthetic checks already run within this assignment.
After architecture review, separately authorize a bounded production-contract
implementation and compatibility bridge, then a synthetic integration pilot.
A later scientific Family scope can use the two linked research passes: review
existing Relationships first, then search Actions/Events against locally reviewed
Drivers/edges. The entire ontology need not be complete first.

## 6. What remains uncertain

Schemas cannot verify scientific truth, missing mechanisms or all shared causal
contributions. Actor feasibility still needs explicit scope/constraints. Detailed
numeric models, episode ingestion, network editing and recommendation ranking are
deferred. Source access levels are stated: some standards were read by section,
and the effect-modification paper was reviewed at abstract/metadata level.

No production records, contracts, consumers or governance decisions changed.
Protected raw-byte comparisons cover 234 pre-existing tracked files. Remote pushes
are permitted only after inspecting triggers: Pages publishes main, so this work
must remain an unmerged proposal branch. Final commit/PR and actual validation
status are recorded in PROGRESS.md and the handoff report.
