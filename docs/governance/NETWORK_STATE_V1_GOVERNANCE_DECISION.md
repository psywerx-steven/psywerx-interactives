# Network State V1 architecture governance decision

Decision ID: `GOV-NETWORK-STATE-V1-2026-09-07`

Effective date: 2026-09-07. Actor class: `authorized human governor`.

Authorization basis: the explicit human Network State architecture, SOC-F07 completion and bounded implementation instruction, following proposal head `ec76bb90da5c704b0d471f2a85e570fe5c43a0c4` in [PR #19](https://github.com/psywerx-steven/psywerx-interactives/pull/19). Starting main: `f0be9c24288bd128231e0d1243b34c03ad055906`.

Prior authority: [D01–D14](RELATIONSHIP_INTERVENTION_V1_GOVERNANCE_DECISION.md), [AE01–AE12](ACTIONS_EVENTS_V1_GOVERNANCE_DECISION.md), and [SOC-F07 scientific decision](pilots/SOC-F07/SOC_F07_GOVERNANCE_DECISION_001.md). Architecture approval does not revise their scientific content.

## Exact decisions

| ID | Human outcome | Governed semantics |
| --- | --- | --- |
| NS01 | APPROVE | OPTIONAL explicit relational base state when exact configuration is needed; Driver-only scenarios remain supported. |
| NS02 | APPROVE | Scenario-state object, not Driver, RDS, Layer, PSYWERX Relationship or automatic scientific causal target. |
| NS03 | APPROVE | RelationalState, NetworkObservation and ScenarioStateDelta with the distinct meanings below. |
| NS04 | APPROVE | Typed node/tie/membership/opportunity/boundary/time/provenance/version/hash contract; applicable fields only; unknown remains unknown. |
| NS05 | APPROVE | Separate observed/reported/inferred network data from modeled state assumptions. No observed-network-equals-truth rule or latent-state estimator. |
| NS06 | MODIFY/APPROVE-AS-MODIFIED | Versioned COLLECTION/MULTI-INPUT deterministic derivation bindings; complete aligned node set and required external parameters machine-readable; not ordinary causal Relationships. |
| NS07 | APPROVE | Optional Occurrence reference to a separate deterministic operation; occurrence evidence does not establish consequences. |
| NS08 | APPROVE | AE04 remains DRIVER/RELATIONSHIP only. No RDS/RELATIONAL_STATE/NETWORK_STATE/SCENARIO_STATE target or context loophole. |
| NS09 | MODIFY/APPROVE-AS-MODIFIED | ScenarioStateDelta is a separate deterministic modeled operation only. Scientific StateChangeAssertion is deferred. |
| NS10 | APPROVE | Immutable revisions, parent hashes, delta preconditions, atomic outcomes and deterministic receipts; no scientific lifecycle as scenario mutation permission. D12 unchanged. |
| NS11 | APPROVE | Privacy/re-identification boundaries, pseudonyms and separately held identity mapping; no real-person identity service or ingestion. |
| NS12 | APPROVE | ADDITIVE, OPT-IN, BACKWARD COMPATIBLE; no automatic migration/reminting; unsupported RDS variants fail explicitly; no scale-up authorization. |

## State and observation contracts

RelationalState is a versioned scenario representation of modeled relational configuration. NetworkObservation is observed/reported/inferred relational data with provenance and missingness. ScenarioStateDelta transforms one modeled revision into another under an explicitly declared deterministic operation. A social tie is not a scientific proposition connecting ontology entities.

The minimum state contract supports, where applicable: scenario-local stable node IDs and membership/status; stable tie IDs, type, source/target, directedness, weights with meaning/unit, distinct multiplex layers/types, validity time/window, group membership, contact/opportunity sets, node/network boundary, included/excluded population rules, observation/assumption provenance, revision and content hash. Genuinely inapplicable fields need not contain invented values. Absent ties are not automatically known non-ties.

NetworkObservation separately records method, timing, sampling frame, boundary, missing nodes/ties, inferred/observed distinction, source/provenance and uncertainty/limitations. Multiple observations may disagree. Mapping into state requires explicit construction assumptions; an observation does not overwrite state automatically. No latent-state estimation or live/real-person ingestion is authorized.

## Collection derivation clarification

Bindings are deterministic/calculational dependencies, not causal Relationships. They identify the target RDS/version, input entity/metric/version, collection subject, completeness rule, expected node set, state version/hash, boundary/window, metric variant, normalization and explicit benchmark/max/reference/external inputs, transformation reference, contribution identity, limitations and receipt.

The approved centralization concept requires the COMPLETE aligned distribution of SOC-049 degree values for every node in the specified network, plus the exact metric-specific normalization/benchmark. One ego is insufficient. Degree scores must not be used for betweenness/eigenvector/closeness centralization. Missing benchmark or mismatched state/boundary versions must fail. No collection dependency solely in prose; existing binary Relationship semantics remain unchanged.

An adapter executes only an exact supported and adequately specified calculation. Unsupported/incomplete canonical variants return explicit refusal, not an invented formula or repaired ontology field. Synthetic examples may demonstrate degree, density, local clustering, fragmentation and degree centralization without approving other variants. Recalculation and causal propagation must not double count a contribution.

## Operation versus effect clarification

An Occurrence may reference a separate ScenarioStateDelta. A seating-assignment occurrence, stipulated modeled seat/contact-opportunity changes, and an empirical claim that proximity changes friendship formation are three distinct objects. Only the last is a scientific EffectAssertion requiring scientific evidence/governance.

A valid delta means only that the declared modeled operation transforms state A into state B. It is not evidence that the real world will change accordingly, an intervention will succeed, behavior will change, causality exists, or action is ethically/legal/practically permitted. No automatic delta from a HappeningType name. A scenario planner must stipulate the operation. Whole-configuration scientific claims require a later architecture decision; scientific StateChangeAssertion remains deferred.

Typed operations cover node/tie addition/removal/deactivation, weight, membership, boundary, contact opportunity and access changes. Preconditions bind state revision/hash; success is atomic and returns a deterministic receipt and new immutable revision/hash. No unrestricted arbitrary JSON mutation. Boundary exclusion is not real node disappearance; contact opportunity is not friendship. Scientific ACTIVE/INACTIVE is not a state-operation permission flag.

## Privacy and compatibility

Topology itself can identify people. Future real-network work needs scenario-local pseudonyms, separate identity mapping, minimization, access control, retention/deletion, sensitive-attribute and provenance handling, aggregation/export controls. This implementation uses fictional SYN-* data only; no personal identity service or real-network ingestion.

Existing state-unaware scenarios remain valid; no automatic migration, reminted ID, new Layer or Driver/RDS reclassification. AE04 and D10/D12 remain unchanged. No scientific target extension, numerical causal weighting, diffusion/evolution simulation, ranking/recommendation/optimization or unrelated governance work.

## Additional bounded implementation authority

Generalize source-verification provenance truthfully and additively. Preserve every existing PubMed record. Appropriate authoritative publisher/registry/DOI routes must identify method, authority, durable identifiers/locators, exact verified fields, date, access depth, conflicts, status/confidence and evidence. Arbitrary web pages, fabricated PubMed IDs and unverifiable records must fail closed. No automatic historical source migration.

The previously approved SOC-F07 concept `REL-CAND-SOC-F07-001` may materialize under an appropriate new derivation-binding identity only if the typed collection gate is met, with candidate lineage and DEFINITIONAL/CALCULATIONAL basis. It need not become a binary Relationship. `HT-CAND-SOC-F07-008` may materialize only after authoritative source reverification/deduplication through the new truthful route. These are conditional completions of prior scientific approval, not new scientific conclusions. Both must remain GOVERNED + INACTIVE. No EffectAssertion or activation is authorized.

PR #19 may merge after exact pre-implementation scope, protected-science, local validation and Linux/Windows CI gates pass. Subsequent implementation must use `implementation/network-state-v1`; its bounded PR may merge after independent diff review and all gates pass. Existing Pages automation may run after authorized merges; no manual deployment or configuration change.

After merged implementation, conduct only read-only three-pilot readiness review. Distinguish beginning a controlled Family program from scientific completeness/automatic population. No Family #4, 105-Family population, SOC activation, old-edge rewrite, blocked-field invention, BIO B01–B05, INF EA-001/H20 or v0.3 resolution is authorized.
