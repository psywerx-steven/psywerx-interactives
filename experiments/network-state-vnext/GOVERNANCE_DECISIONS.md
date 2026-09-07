# Network State decisions for human review

All **NS01–NS12 remain PENDING**. Recommendations are not authorization. Machine-readable questions/recommendations are in [decisions.json](decisions.json); the full comparison is in [the proposal](ARCHITECTURE_PROPOSAL.md).

| ID | Recommended answer | Main alternative / tradeoff | Human decision |
| --- | --- | --- | --- |
| NS01 | Explicit optional relational base state for exact recalculation | Driver-only is simpler but non-reconstructive | PENDING |
| NS02 | Scenario substrate, not ontology Driver/type | Ontology-level type broadens scientific target/governance burden | PENDING |
| NS03 | RelationalState; separate NetworkObservation and ScenarioStateDelta | NetworkConfiguration is more graph-specific; names must not imply truth | PENDING |
| NS04 | Node/tie IDs, membership, typed/layered/directed/weighted ties, boundary, time, risk sets | Bare adjacency loses identity, scope and observation meaning | PENDING |
| NS05 | Observation artifacts separate from latent state assumptions | One “true graph” is simpler but conceals missingness/inference | PENDING |
| NS06 | Versioned collection/multi-input RDS bindings | Scalar edges/free text are insufficient for all-node completeness | PENDING |
| NS07 | Occurrence may reference a deterministic scenario operation | Embedded deltas couple occurrence evidence to supposed effects | PENDING |
| NS08 | Preserve AE04 DRIVER/RELATIONSHIP vocabulary | A state target requires new scientific governance; not introduced here | PENDING |
| NS09 | Separate ScenarioStateDelta; defer scientific StateChangeAssertion | A new scientific assertion might address whole-configuration claims but needs evidence/target design | PENDING |
| NS10 | Immutable versions, hash preconditions and receipts; unchanged D12 | Scientific ACTIVE is not a mutable scenario permission flag | PENDING |
| NS11 | Local pseudonyms, separate identity mapping, minimization/retention/export gates | Real graph data creates substantial re-identification risk | PENDING |
| NS12 | Additive opt-in compatibility, no automatic migration or scale-up | Immediate population multiplies unresolved representations and governance debt | PENDING |

## Exact approval scope to consider

The question for each row is the corresponding `question` in decisions.json, not approval of every possible extension in the prose. NS06 approval would authorize design of typed collection/metric bindings, **not** fill SOC-F07 blocked definitions or govern the currently blocked derivational Relationship. NS07/NS09 would concern scenario operations, not automatic empirical effect claims. NS08 recommends leaving AE04 unchanged. NS12 would require a separate implementation plan and later scientific gates.

## Backward compatibility and migration

All recommended options are additive and opt-in. Preserve existing IDs, active/inactive states and original scientific evidence. No production migration is performed. Driver-only scenarios must remain valid; state-aware adapters should refuse unsupported RDS variants. No record may be made executable merely because a configuration can be serialized.

Complexity is low for preserving AE04/naming, medium for typed state/delta/versioning, and high for collection derivation, real observation reconciliation, privacy and integration. The alternative new ontology type is the most disruptive: it requires target semantics, D10-like safeguards, scientific lifecycle ownership and new deduplication rules. It is not a shortcut to activating network effects.

## Separate unresolved scientific/maintenance decisions

- REL-CAND-SOC-F07-001: approved concept, BLOCKED_PENDING_REPRESENTATION. A future adequate contract must precede materialization.
- HT-CAND-SOC-F07-008: approved identity, verified bibliography, but native source verification cannot truthfully express non-PubMed verification. No source contract change is authorized here.
- Four RDS retype proposals, two revisions, REL-TEC-050, three exact SOC-102 effects, H12/H20 and twelve target gaps remain unresolved as specified by human governance.
- INF-F03 EA-001/H20, BIO-F01 B01–B05 and blocked v0.3 metadata are outside scope.

Recommended scale-up advisory: **NOT_READY_PENDING_NETWORK_STATE_DECISION**, with the other gates above retained. This is not an authorization to populate all Families.
