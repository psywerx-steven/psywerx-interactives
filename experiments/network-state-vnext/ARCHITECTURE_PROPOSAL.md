# Relational state: a bounded architecture review

EXPERIMENTAL / NON_PRODUCTION. Every new architecture decision is **PENDING**. This is not a production contract, new ontology entity, simulation or scientific finding.

## Recommendation

Prefer a hybrid: keep Drivers as scientific causal/process constructs; represent a particular configuration in an optional **RelationalState** scenario substrate; keep **NetworkObservation** distinct; calculate RDS through explicit, versioned derivation bindings. Represent deterministic scenario edits as **ScenarioStateDelta**, not as scientific EffectAssertions. Do not add a third AE04 target at this stage.

This recommendation is narrower than “Actions & Events can change networks.” An assigned group can be changed exactly in a fictional scenario; whether that assignment causes later friendship needs independent scientific evidence. State bookkeeping cannot supply that evidence. The hybrid therefore does **not** make current blocked real network effects representable as approved scientific assertions. Those remain blocked until an appropriate existing Driver/Relationship target or separately governed extension exists.

## Evidence of the representation gap

SOC-F07 has one Driver, SOC-102 Conditional Triadic Closure Rate, and twelve RDS. SOC-102 describes a conditional process/risk set, not the node roster, adjacency, membership or multiplex configuration. Neighboring tie-formation/dissolution rates cannot uniquely reconstruct these either. Many configurations share the same rates or degree sequence. The four currently blocked entities remain untouched.

The approved centralization concept exposes a second gap: the binary RI V1 record cannot enforce “all node degree values in this exact network plus benchmark inputs.” A scalar endpoint and a sentence about a collection are not a validated collection binding. The production schema rejects a typed collection field; it accepts scalar wording with no benchmark. Hence no new derivational record was materialized. This result does not refute degree-based centralization mathematically.

Read-only basis: [SOC-F07 entity/RDS review](../../docs/governance/pilots/SOC-F07/SOC_F07_ENTITY_RDS_REVIEW.md), [network findings](../../docs/governance/pilots/SOC-F07/SOC_F07_SPECIAL_NETWORK_FINDINGS.md), [governed RI decisions](../../docs/governance/RELATIONSHIP_INTERVENTION_V1_GOVERNANCE_DECISION.md), [AE01–AE12](../../docs/governance/ACTIONS_EVENTS_V1_GOVERNANCE_DECISION.md). D10/D12 and AE04 remain binding.

## Objects that must remain distinct

| Object | Meaning | Not equivalent to |
| --- | --- | --- |
| Ontology entity | General scientific construct | One actor, one scenario or an adjacency table |
| Driver | Causal/process variable under current classification | Arbitrarily manipulable network statistic |
| RelationalState | Versioned representation of a scenario’s configuration, conditional on assumptions | Guaranteed real network or a causal Driver |
| NetworkObservation | Measured/reported/inferred network data with provenance | Complete latent state |
| Social tie | Real or modeled relation between actors under a specified definition | A PSYWERX scientific Relationship |
| PSYWERX Relationship | Scoped scientific proposition between ontology entities | Friendship, communication link or matrix entry |
| RDS | Derived value under a metric/measurement specification | Independent configurable primitive or universally comparable score |
| HappeningType | Reusable action/event/exposure/process identity | Efficacy or practitioner permission |
| Occurrence | Particular observed, planned or hypothetical realization | Proof of downstream consequences |
| ScenarioStateDelta | Proposed deterministic configuration operation and receipt | Empirical causal EffectAssertion |
| EffectAssertion | Evidence-backed scoped Driver/Relationship effect under AE V1 | An instruction to edit arbitrary state |

The proposed information flow is:

```text
observations + explicit assumptions -> versioned scenario representation
                                         |
hypothetical scenario operation -> new revision -> scoped RDS recomputation

scientific effect knowledge -> separate governed claim/evidence/use checks
                              (no automatic connection to numerical execution)
```

## Competing options

| Option | Advantages | Costs and scientific risks | Compatibility / migration |
| --- | --- | --- | --- |
| A. Driver-only, exact topology external | Smallest surface; existing AE04/D10 unchanged; adequate for bounded qualitative process claims | Rates do not identify configurations. Cannot reproduce RDS without external state; scalar surrogates may create false agency. Network-changing actions remain target-gapped. | No migration. Keep as a supported degraded mode, explicitly non-reconstructive. |
| B. New ontology entity/type/target | First-class reference for relational configuration; potentially explicit scientific structure-change claims | A configuration is not automatically a scalar construct. New target changes AE04; D10, evidence, identity, causal ownership, latent-state and activation rules need redesign. Can create a hidden RDS manipulation route. | High complexity; new contracts/adapters, no automatic Driver conversion or reminting. Not implemented. |
| C. Hybrid scenario substrate | Separates reusable science from particular state; supports reproducible calculations and exact modeled operations; preserves existing targets | Two identity/provenance systems, boundary choices, incomplete observations and adapter burden. Does not solve every scientific targeting gap; scenario-operation authorization is not efficacy governance. | Additive opt-in adapters; unchanged existing consumers and IDs. Medium initial cost, high if real data/uncertainty/execution is later added. |

Challenge to C: if PSYWERX intends only a qualitative knowledge catalog, carrying node-level state may be needless complexity and privacy exposure. A remains preferable there. If future applications require scientifically governed effects on entire configurations, C alone is insufficient; a separate review must decide whether B’s target or a scientific StateChangeAssertion is justified. Do not disguise that unresolved claim inside a scenario delta. This prototype establishes representational feasibility, not product need or scientific target sufficiency.

## Minimum proposed substrate

Use stable scenario-local node IDs, stable tie IDs, separately defined groups/membership and opportunity/risk sets. Define tie type, directedness, positive weight meaning/unit, multiplex layer and validity interval. Declare node boundary and selection rule, excluded/unknown frame treatment, time/window, sampling and provenance. Keep active node membership separate from inclusion in an analytic boundary. Removing a node from a modeled population is not excluding it from analysis.

Prototype state revisions have a parent hash, integer version, content hash and applied-delta IDs. Node/tie order is canonicalized; operation order remains meaningful. Hashes prove consistency, not empirical truth, scientific approval, user permissions or cryptographic identity. Cross-scenario person matching is not attempted.

Observation records need node/tie missingness, sampling, inference method, observation timing and access provenance. A surveyed tie, an algorithmically inferred tie and a stipulated synthetic tie must not receive the same evidence label. Competing observations can disagree without overwriting an asserted latent truth. The minimal prototype embeds synthetic observation metadata; the recommended future design separates observation artifacts with explicit links and multiple observations. It does not implement latent-state estimation or uncertainty propagation.

Snapshots describe a declared instant. Intervals need aggregation semantics (e.g., ties persisting throughout, contact union or time-weighted exposure); these are not interchangeable. Repeated observations are versions with observation provenance, not proof of tie formation. Event-driven logs could later represent entry/exit, creation/dissolution, weight or access changes, but timing/order and estimation algorithms need independent governance. The prototype supports declared snapshots and persistent-through-window selection only; it does not evolve a network over time.

## RDS derivation interface: actual SOC-F07 test cases

Proposed binding: `RDS definition/version + subject unit + state revision/hash + observation/assumption provenance + boundary/window + metric specification + named external inputs -> derived value with limitations`.

The following is an interface-needs analysis, **not** production formulas or filled metadata. Each variant and unresolved field still requires appropriate governance.

| Current RDS | State/input dependency | Specification that cannot be implicit |
| --- | --- | --- |
| SOC-049 Degree Centrality | Incident ties for each included actor; aligned full node roster for collections | In/out/total, binary/weighted, loops, normalization and denominator |
| SOC-050 Betweenness Centrality | Paths across the declared graph | Directed paths, weight-as-distance interpretation, shortest-path ties, disconnected pairs, normalization |
| SOC-051 Eigenvector Centrality | Adjacency/operator and selected nodes/layers | Left/right convention, weight meaning, disconnected/nonunique solution, normalization |
| SOC-052 Network Density | Included node set and eligible ties/opportunity set | Directedness, loops, eligible dyad denominator, excluded actors |
| SOC-053 Local Clustering | Ego neighbors and neighbor-to-neighbor ties | Directed/weighted variant; degree below two convention; not SOC-102 closure rate |
| SOC-054 Network Assortativity | Endpoint attributes and mixing matrix | Attribute categories, degree versus attribute variant, opportunities and baseline |
| SOC-055 Structural Constraint | Ego investment/tie proportions and indirect connections | Weight definition, normalization, ego boundary, directedness; not generic brokerage |
| SOC-056 Cross-Cluster Tie Prevalence | Ties plus specified cluster partition | Partition source/version, cross-cluster criterion, eligible tie denominator |
| SOC-057 Network Segregation | Group membership, mixing and opportunity/baseline distribution | Group definitions, denominator and comparison baseline; not assortativity identity |
| RDS-0005 Distance-Based Closeness | Paths from each actor in declared network | Reachability, disconnected handling, directedness, distance transformation, scale |
| RDS-0006 Network Centralization | Complete aligned actor metric collection plus network definition/benchmark | Metric-specific centralization; degree is not betweenness/eigenvector/closeness; maximum and node set |
| RDS-0007 Network Component Fragmentation | Components from declared ties/node set | Weak/strong components, isolate inclusion, component-count versus pair-disconnection variant |

For a complete simple undirected loopless degree fixture, the sum of deviations from maximum degree is divided by the same-size star benchmark `(n−1)(n−2)`. This is only one explicitly selected centralization variant; other centralities have different extrema. The igraph maintainer documentation explicitly distinguishes node score vectors, theoretical maxima and metric-specific functions. [igraph centralization](https://igraph.org/c/html/latest/igraph-Structural.html#igraph_centralization)

No automatic causal propagation is attached to recomputation. A calculation receipt should identify the shared input/contribution group. If later quantitative execution uses an independently governed RDS-source causal claim, it must reconcile the state/constituent route; it cannot add both contributions blindly. This phase neither rejects all RDS-source causality nor implements it.

## Actions & Events interface alternatives

| Interface | Assessment |
| --- | --- |
| A. Occurrence embeds structural delta | Compact, but can confuse observed event evidence with supposed consequences; schema coupling grows. Prefer a reference to a separately versioned operation. |
| B. Scientific StateChangeAssertion | Potentially useful for evidence-backed changes to whole configurations, but a new scientific target/claim contract needs authority, identification, scope and overlap rules. Defer. |
| C. Add RELATIONAL_STATE to EffectAssertion | Directly changes AE04. A strong future case is required; do not implement or imply this now. |
| D. Driver-mediated only | Correct where an exact governed process Driver exists. Cannot reconstruct adjacency from rates or substitute SOC-102 for arbitrary ties. |
| E. Hybrid | Keep scientific Driver/Relationship effects; attach deterministic scenario operations separately. Recommend this minimal next design, with unresolved scientific target gaps explicit. |

Adding/removing/rewiring a **modeled** tie updates a representation. Assigning groups updates membership. Seats create contact opportunity, not friendship. Access restriction disables an opportunity, not necessarily an existing tie. Storm-related loss of contact opportunities could be represented by a stipulated or observed delta with provenance; the storm’s occurrence does not prove all tie, trust or behavior effects. A real communication-affordance change and its experienced use are also distinct.

The prototype includes receipts and atomic prior-version/hash checks, rejecting partial invalid transactions. RFC 6902 offers a useful model of ordered operations and failed-operation handling, but untyped JSON Patch alone cannot enforce tie/opportunity/scientific distinctions. We borrow the transaction discipline, not unrestricted production patch access. [RFC 6902](https://www.rfc-editor.org/rfc/rfc6902.html#section-5)

## Evidence and provenance

W3C PROV’s entities, activities, revisions and collections are useful bookkeeping concepts. PROV derivation is broader than PSYWERX scientific derivation/causation, and membership is not automatically influence. A provenance path is not proof of mediation. Borrow explicit inputs, outputs and responsibility; do not import a taxonomy or infer scientific authority from a valid provenance graph. [PROV-DM](https://www.w3.org/TR/prov-dm/#component2)

Keep occurrence evidence, observation evidence, calculation receipts and scientific effect assessments separate. The prototype produces no sourceFinding, EvidenceAssessment, production Occurrence or scientific Relationship. Null observed findings stay findings; missing data is not zero, and a deterministic metric difference is not a causal estimate. Existing candidate supportive/mixed/null/insufficient findings remain unchanged.

## Privacy and execution boundaries

Real node-level graphs can identify people or organizations through topology even when names are replaced. Future work needs locally pseudonymous identifiers; separately access-controlled identity mapping; collection purpose/consent or other appropriate authority; minimization of sensitive attributes; small-group aggregation/export review; provenance and retention/deletion policies. Pseudonymization is not anonymity. No personal data, identity service, permissions system or privacy implementation was built here.

Future connectors could read a governed scenario snapshot or call an approved metric adapter. That is not authorization for diffusion, stochastic tie formation, causal numerical execution, network optimization, rankings, recommendations or live ingestion. The experimental CLI only generates synthetic examples within this directory. Existing scenario-service/FCM/Explorer remain untouched.

## Compatibility, limitations and scale-up

No existing Driver/RDS/Relationship/Intervention/HT/EA/EVA ID or status changes; no production target vocabulary changes. Future adapters must reference exact existing RDS definitions and mark unsupported variants, not remint or silently complete them. The twelve target gaps describe one broad missing configuration representation, not twelve new Drivers.

Advisory status: **NOT_READY_PENDING_NETWORK_STATE_DECISION**. Generic audits, candidate isolation, source findings and partial activation separation have worked across three pilots. But exact configuration/collection binding, target sufficiency and observation semantics remain ungoverned. Additional gates also remain: non-PubMed canonical source verification, blocked metadata, legacy RDS causal review, duplicate source components and cross-Family workload/consultation discipline. NS approval alone would not clear all of these.

The next authorized step should be human NS01–NS12 review and a separately bounded source-contract decision. After approval, implement opt-in state/observation/derivation adapters with synthetic and compatibility tests before any real network-data or scale-up pilot. No Family #4 or 105-Family population is started or authorized.

See [decision package](GOVERNANCE_DECISIONS.md), [synthetic examples](SYNTHETIC_EXAMPLES.md), [requirements coverage](REQUIREMENTS_COVERAGE.md) and [proposal-only sources](sources.json).
