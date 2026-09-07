# Network State decisions for human review

NS01–NS12 are now governed by [GOV-NETWORK-STATE-V1-2026-09-07](../../docs/governance/NETWORK_STATE_V1_GOVERNANCE_DECISION.md), actor class `authorized human governor`. NS06 and NS09 are MODIFY/APPROVE-AS-MODIFIED; all others APPROVE. The exact governed clarification controls over historical recommendation text. Implementation is authorized separately from scientific activation. Machine-readable outcomes are in [decisions.json](decisions.json). The original prototype remains isolated NON_PRODUCTION.

| ID | Recommended answer | Main alternative / tradeoff | Human decision |
| --- | --- | --- | --- |
| NS01 | Explicit optional relational base state for exact recalculation | Driver-only is simpler but non-reconstructive | APPROVE |
| NS02 | Scenario substrate, not ontology Driver/type | Ontology-level type broadens scientific target/governance burden | APPROVE |
| NS03 | RelationalState; separate NetworkObservation and ScenarioStateDelta | NetworkConfiguration is more graph-specific; names must not imply truth | APPROVE |
| NS04 | Node/tie IDs, membership, typed/layered/directed/weighted ties, boundary, time, risk sets | Bare adjacency loses identity, scope and observation meaning | APPROVE |
| NS05 | Observation artifacts separate from latent state assumptions | One “true graph” is simpler but conceals missingness/inference | APPROVE |
| NS06 | Deterministic collection/multi-input bindings, not causal Relationships; complete members and external inputs enforced | Scalar edges/free text are insufficient for all-node completeness | MODIFY/APPROVE-AS-MODIFIED |
| NS07 | Occurrence may reference a deterministic scenario operation | Embedded deltas couple occurrence evidence to supposed effects | APPROVE |
| NS08 | Preserve AE04 DRIVER/RELATIONSHIP vocabulary | A state target requires new scientific governance; not introduced here | APPROVE |
| NS09 | ScenarioStateDelta only proves modeled transformation, not real-world success, causality or permission; scientific StateChangeAssertion deferred | New scientific claims need a later decision | MODIFY/APPROVE-AS-MODIFIED |
| NS10 | Immutable versions, hash preconditions and receipts; unchanged D12 | Scientific ACTIVE is not a mutable scenario permission flag | APPROVE |
| NS11 | Local pseudonyms, separate identity mapping, minimization/retention/export gates | Real graph data creates substantial re-identification risk | APPROVE |
| NS12 | Additive opt-in compatibility, no automatic migration or scale-up | Immediate population multiplies unresolved representations and governance debt | APPROVE |

## Exact approval scope to consider

The exact human decision record supersedes historical proposal questions, not every possible extension in the prose. NS06 authorizes typed collection/metric bindings, **not** filling SOC-F07 blocked definitions. The already-approved derivational concept may conditionally materialize under the appropriate new binding object, never a forced binary causal edge. NS07/NS09 authorize scenario operations, not empirical effect claims. NS08 preserves AE04. NS12 authorizes bounded additive implementation, not scientific activation or scale-up.

## Backward compatibility and migration

All recommended options are additive and opt-in. Preserve existing IDs, active/inactive states and original scientific evidence. No production migration is performed. Driver-only scenarios must remain valid; state-aware adapters should refuse unsupported RDS variants. No record may be made executable merely because a configuration can be serialized.

Complexity is low for preserving AE04/naming, medium for typed state/delta/versioning, and high for collection derivation, real observation reconciliation, privacy and integration. The alternative new ontology type is the most disruptive: it requires target semantics, D10-like safeguards, scientific lifecycle ownership and new deduplication rules. It is not a shortcut to activating network effects.

## Separate unresolved scientific/maintenance decisions

- REL-CAND-SOC-F07-001: approved concept, BLOCKED_PENDING_REPRESENTATION. A future adequate contract must precede materialization.
- HT-CAND-SOC-F07-008: approved identity, verified bibliography, but native source verification cannot truthfully express non-PubMed verification. No source contract change is authorized here.
- Four RDS retype proposals, two revisions, REL-TEC-050, three exact SOC-102 effects, H12/H20 and twelve target gaps remain unresolved as specified by human governance.
- INF-F03 EA-001/H20, BIO-F01 B01–B05 and blocked v0.3 metadata are outside scope.

Historical proposal advisory was NOT_READY_PENDING_NETWORK_STATE_DECISION. The architecture decision is now made; implementation and its final three-pilot assessment must determine readiness anew. This is not authorization to populate any further Family.
