# Network State V1 — optional scenario substrate

Governed by [NS01–NS12](NETWORK_STATE_V1_GOVERNANCE_DECISION.md). Additive, opt-in, no automatic migration. Existing Driver-only scenarios and application consumers are unchanged. The implementation is representational/deterministic tooling, not a network-science simulation or a recommendation system.

## Separate objects, separate meanings

| Object | Meaning | Does not establish |
| --- | --- | --- |
| Ontology Driver | General causal/process construct | Exact actor/tie configuration |
| RelationalState | Immutable, modeled configuration in one scenario | True or fully observed real network; new ontology entity |
| NetworkObservation | Reported/observed/inferred nodes and ties, sampling and missingness | Ground truth or permission to overwrite state |
| Social tie | Scenario-local relation between nodes | PSYWERX scientific Relationship |
| ScenarioStateDelta | Typed, stipulated operation on one exact state revision/hash | Empirical causality, real-world success, permission or efficacy |
| Occurrence | Particular realization; may separately reference an operation | Evidence of downstream consequences |
| EffectAssertion | Scoped scientific claim targeting a Driver or exact Relationship | Scenario mutation; direct RDS/state targeting |
| Collection derivation binding | Versioned calculational dependency on complete aligned inputs | Ordinary binary causal Relationship |
| RDS calculation receipt | Result/refusal under an explicit specification | Independent causal contribution or quantitative modeling eligibility |

AE04 remains **DRIVER / RELATIONSHIP**. No new scientific StateChangeAssertion, ontology Layer, NetworkState Driver or target class. D10/D12 and all existing IDs/lifecycles remain unchanged.

## Contracts and API

[Eight modular contracts](../../schemas/relational-state/v1/relational-state-v1.schema.json) are generated from [relational_state_contracts.py](../../scripts/relational_state_contracts.py). Runtime [relational_state_v1.py](../../scripts/relational_state_v1.py) validates schema plus cross-field semantics. JSON Schema alone is not the complete scientific gate.

`validate_state`, `validate_observation`, `construct_from_observation`, `apply_delta`, `replay`, `validate_binding`, `calculate` and `validate_operation_reference` are opt-in Python APIs. No existing consumer imports them automatically. `python scripts/relational_state_v1.py --validate-repository` validates the separate derivation catalog and exact human authority.

State records contain scenario-local nodes, memberships, active/inactive node membership status (not scientific activation), stable social-tie IDs, tie type/layer/direction, explicit weight meaning/unit or unknown, validity, opportunity/access sets, analytic boundary/window, provenance, construction assumptions, privacy metadata, revisions/parent/hash. Unknown absence is not a nonexistent tie. Nodes outside the analytic boundary remain represented; changing the boundary does not create/delete real ties.

Observations have their own sampling, node/tie missingness, observed/inferred distinction, method, limitations and hash. Explicit construction starts from an empty state template and records selected observation IDs/hashes and assumptions. It never silently overwrites state. Conflicting observations can produce different plausible modeled states. Observation references can be stored independently; callers must supply the observation lookup to verify external reference resolution. No latent-state estimator or ingestion service exists.

Nine operations are implemented: ADD_NODE, DEACTIVATE_NODE, ADD_TIE, REMOVE_TIE, UPDATE_TIE_WEIGHT, CHANGE_MEMBERSHIP, CHANGE_BOUNDARY, CHANGE_CONTACT_OPPORTUNITY, CHANGE_ACCESS. They require exact precondition revision/hash and scenario. Copy-on-write validation commits the entire result or returns no mutation. Node departure explicitly removes incident represented ties/opportunities in the receipt; identifiers are not silently recycled. Arbitrary JSON mutation is forbidden. Boundary selection is an isolated analytic operation, never a claimed tie-formation event.

V1 does not implicitly advance clocks: delta effective time must equal the state's declared start. Snapshots and persistent-through-window intervals are distinct; temporal evolution/prediction is deferred. Replay reconstructs the exact receipt and resulting hash. Rollback means retaining/selecting the immutable parent, not guessing an inverse real-world operation. Historical states must be retained by the caller.

An optional operation-reference sidecar links exact delta hash and existing HT/Occurrence identity without modifying AE contracts. It confers no automatic operation generation/execution. A seating assignment changes modeled membership/opportunity, not friendship; removing a modeled tie does not prove reduced trust.

## Collection derivations and unsupported calculations

Reusable scientific binding knowledge is distinct from a concrete calculation request. The binding specifies RDS/input definition hashes, all-node collection completeness, exact alignment, variant, normalization, external inputs/maximum and calculational reference. The request binds these to a state/hash, expected member set, boundary/window, metric specification, complete scores and benchmark. A receipt records result or an explicit unsupported/incomplete/not-authorized outcome.

The approved [DER-V1-SOC-F07-001](../../data/relational-state-v1/catalog.json) supports only complete raw degree scores for a simple, loopless, binary, undirected network, n≥3, with same-size star benchmark. It is GOVERNED/INACTIVE. One ego, missing/extra members, inconsistent degree scores, mismatched state/boundary/window, absent maximum and other centrality variants fail. Canonical RDS records and blocked operational metadata are not repaired.

Five exact variants are demonstrated synthetically: raw degree; simple density; local clustering with explicitly specified zero for degree below two; unreachable-pair component fragmentation; Freeman degree-based centralization. Selecting a variant requires its full specification. Directed/weighted/multiplex-collapsed or under-specified variants return `UNSUPPORTED_OR_INCOMPLETE`; a supplied weight is never silently binarized. Fragmentation demonstration does not claim every canonical fragmentation definition is executable.

Calculation execution currently supports **SYNTHETIC_VALIDATION only**. `SCIENTIFIC_USE` returns `NOT_AUTHORIZED`: the one scientific binding is inactive, and no production quantitative execution registration was authorized. This is an explicit degraded interface, not a claim of canonical numerical-model readiness. State operations themselves are deterministic scenario bookkeeping and do not use scientific ACTIVE status as permission.

Shared-contribution identity and `RECALCULATION_ONLY_NO_CAUSAL_SUM` prevent counting recomputation as an independent causal route. Requests permit only STATE_RECALCULATION; receipts set causal contribution and model/practitioner eligibility false. Graph reachability never generates mediation/pathway evidence.

## Source verification

The existing PubMed verification object is preserved exactly as one branch of an additive source-schema union. The new [verification contract](../../schemas/source-verification/v1/verification-v1.schema.json) records authoritative DOI registry plus publisher alignment, exact fields, durable locator, date, access depth, conflicts/status and hash-bound verification provenance. No fabricated PMID or arbitrary website authority is accepted.

Registry identities are allowlisted Crossref/DataCite; publisher metadata must be corroborated by registry publisher links. A checked-in, reviewed field-level attestation supports deterministic offline revalidation. This is not a cryptographic proof that the external authority is honest or a freshness monitor; a human must inspect provenance when registering a source. Unknown/unverified/conflicting metadata fails closed. DOI/PMID/title duplicate checks remain in the native register. Historical sources require no bulk migration. `SRC-509` / `SRC235` component overlap remains explicit.

SRC-559 is the narrowly reverified Sun/Taylor 2020 journal work; its 2019 preprint is the same work, not replication. Access was ABSTRACT_METADATA, not full-text efficacy review. Only identity provenance was registered. No source reviewed solely for research-needed/rejected science was added.

## Privacy and limits

Topology itself can identify people even without names. Contracts support pseudonymous scenario-local IDs, separate external identity reference, minimization, handling/retention and export constraints; fixtures permit no identity mapping. These fields do not implement an authorization service, deletion engine, identity resolution or real-person ingestion. Production hosting/storage/access-control review is mandatory before real network data use.

No diffusion, evolution, probabilistic tie formation, optimization, ranking, numeric causal weighting, automatic recommendation or live monitoring is implemented. No SOC activation or Family #4 research is authorized.

## Validation

Run explicit repository CI suites plus `test_relational_state_v1.py`, `test_source_verification_v1.py` and `test_soc_f07_completion.py`. Regenerate the twelve [synthetic examples](../../reports/relational-state-v1/synthetic-validation.json) using `python scripts/relational_state_fixtures.py --output reports/relational-state-v1`; writes outside that safe report root are rejected. Test coverage includes all 41 RDS direct-target refusals, atomicity/replay, observation uncertainty, five calculations, complete collections, source truthfulness, exact inactive materialization and protected science.
