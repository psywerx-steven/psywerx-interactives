# Entity and RDS review

Audit: `AUD-SOC-F07-AE-V1-20260906-001`. Frozen baseline: `f0be9c24288bd128231e0d1243b34c03ad055906`. Candidate audit preserved; human governance checkpoint recorded. Seven identities are governed INACTIVE; six identity-provenance sources registered. No activation. See [decision](SOC_F07_GOVERNANCE_DECISION_001.md).

All canonical fields, including aliases, crosswalks, evidence notes and missing values, are frozen in the baseline and fully captured in [structured review](../../../../data/candidates/actions-events-v1/SOC-F07/entity-rds-review.json). Canonical narrative is not newly endorsed science.

## RDS-0005 — Distance-Based Closeness Centrality

An actor-position score based on the shortest-path distances from a specified actor to other actors in a specified network, using a named standard, harmonic, or other governed closeness formulation.


|Item | Audit finding |
|--- | --- |
| Class / scale | RELATIONAL_DERIVED_STATE / Named standard, harmonic, or other governed closeness formulation. |
| Construct / statistic | Distance-based ego closeness |
| Aliases / crosswalks | ['Closeness'] / [] |
| Alias caution | SEARCH_ONLY/RELATED_SEARCH aliases are retrieval aids, not scientific equivalence; network connectedness/closeness/prestige require exact construct disambiguation. |
| Derivation / risk set | Path-distance matrix, focal actor, unreachable-node convention and normalization externally specified. |
| Real antecedents | Node loss, missing ties and routing assumptions alter paths; no universally best centrality. |
| Outgoing causal IDs | [] |
| Blocked/missing fields | ['mechanism', 'modifiability', 'volatility', 'timeScaleOfChange', 'onsetCausalLag', 'persistenceRecovery', 'measurementAssessmentMethods', 'observability', 'evidenceStrength', 'evidenceNotes', 'keySources'] |
| Shared inputs | Same network representation may feed multiple RDS; no independent simultaneous propagation |
| Targetability | FORBIDDEN_DIRECT_RDS_EFFECT |
| Governance question | Resolve named blocked operational metadata only in a separate authorized decision; no substitute entity |

Boundary sensitivity: Specify node set, tie relation/threshold, direction, weights, multiplex layers, boundary, window, missing ties/nodes, isolate inclusion, sampling, denominator and metric variant. Changing any of these can change a statistic without the claimed real-world mechanism. Snapshot versus longitudinal use must be specified; missing operational metadata is not filled.

## RDS-0006 — Network Centralization

The degree to which a specified node-centrality distribution is concentrated in one or a small number of actors relative to an explicitly stated benchmark or maximum for that network size and centrality measure.


|Item | Audit finding |
|--- | --- |
| Class / scale | RELATIONAL_DERIVED_STATE / Named network-centralization statistic with node-centrality measure and benchmark stated. |
| Construct / statistic | Network-level centralization |
| Aliases / crosswalks | [] / [] |
| Alias caution | SEARCH_ONLY/RELATED_SEARCH aliases are retrieval aids, not scientific equivalence; network connectedness/closeness/prestige require exact construct disambiguation. |
| Derivation / risk set | Distribution of one selected node centrality and benchmark/maximum; selection remains external and incomplete. |
| Real antecedents | Degree-based case can derive from degree distribution, not a single actor value; other centralizations differ. |
| Outgoing causal IDs | [] |
| Blocked/missing fields | ['mechanism', 'modifiability', 'volatility', 'timeScaleOfChange', 'onsetCausalLag', 'persistenceRecovery', 'measurementAssessmentMethods', 'observability', 'evidenceStrength', 'evidenceNotes', 'keySources'] |
| Shared inputs | Same network representation may feed multiple RDS; no independent simultaneous propagation |
| Targetability | FORBIDDEN_DIRECT_RDS_EFFECT |
| Governance question | Resolve named blocked operational metadata only in a separate authorized decision; no substitute entity |

Boundary sensitivity: Specify node set, tie relation/threshold, direction, weights, multiplex layers, boundary, window, missing ties/nodes, isolate inclusion, sampling, denominator and metric variant. Changing any of these can change a statistic without the claimed real-world mechanism. Snapshot versus longitudinal use must be specified; missing operational metadata is not filled.

## RDS-0007 — Network Component Fragmentation

The degree to which a specified network is divided into disconnected components or mutually unreachable actor pairs under an explicit component or fragmentation measure.


|Item | Audit finding |
|--- | --- |
| Class / scale | RELATIONAL_DERIVED_STATE / Number of components, giant-component share, isolate prevalence, unreachable-pair proportion, or a named fragmentation index. |
| Construct / statistic | Component fragmentation |
| Aliases / crosswalks | ['Network connectedness'] / [] |
| Alias caution | SEARCH_ONLY/RELATED_SEARCH aliases are retrieval aids, not scientific equivalence; network connectedness/closeness/prestige require exact construct disambiguation. |
| Derivation / risk set | Connected-component structure and selected metric: component count/giant share/isolate share/unreachable pairs are not identical. |
| Real antecedents | Boundary expansion, node removal or bridges change components; no direct RDS manipulation. |
| Outgoing causal IDs | [] |
| Blocked/missing fields | ['mechanism', 'modifiability', 'volatility', 'timeScaleOfChange', 'onsetCausalLag', 'persistenceRecovery', 'measurementAssessmentMethods', 'observability', 'evidenceStrength', 'evidenceNotes', 'keySources'] |
| Shared inputs | Same network representation may feed multiple RDS; no independent simultaneous propagation |
| Targetability | FORBIDDEN_DIRECT_RDS_EFFECT |
| Governance question | Resolve named blocked operational metadata only in a separate authorized decision; no substitute entity |

Boundary sensitivity: Specify node set, tie relation/threshold, direction, weights, multiplex layers, boundary, window, missing ties/nodes, isolate inclusion, sampling, denominator and metric variant. Changing any of these can change a statistic without the claimed real-world mechanism. Snapshot versus longitudinal use must be specified; missing operational metadata is not filled.

## SOC-049 — Degree Centrality

The number or normalized proportion of direct ties incident on an actor in a specified social network.


|Item | Audit finding |
|--- | --- |
| Class / scale | RELATIONAL_DERIVED_STATE / Raw in-degree or out-degree; normalized degree proportion; weighted degree |
| Construct / statistic | Ego degree; raw or normalized incidence |
| Aliases / crosswalks | ['direct connectivity', 'Network degree', 'number of adjacent ties'] / ['CW-0022'] |
| Alias caution | SEARCH_ONLY/RELATED_SEARCH aliases are retrieval aids, not scientific equivalence; network connectedness/closeness/prestige require exact construct disambiguation. |
| Derivation / risk set | Incident adjacency row/column; n-1 or specified opportunity denominator; loops, directedness and weights matter. |
| Real antecedents | Tie allocation/addition/deletion and node sampling alter inputs; no complete network-state Driver. |
| Outgoing causal IDs | [] |
| Blocked/missing fields | [] |
| Shared inputs | Same network representation may feed multiple RDS; no independent simultaneous propagation |
| Targetability | FORBIDDEN_DIRECT_RDS_EFFECT |
| Governance question | Choose operational network boundary and estimator per application; no context-free scalar assumption |

Boundary sensitivity: Specify node set, tie relation/threshold, direction, weights, multiplex layers, boundary, window, missing ties/nodes, isolate inclusion, sampling, denominator and metric variant. Changing any of these can change a statistic without the claimed real-world mechanism. Snapshot versus longitudinal use must be specified; missing operational metadata is not filled.

## SOC-050 — Betweenness Centrality

The proportion of relevant shortest paths between other actors that pass through a specified actor in a defined network.


|Item | Audit finding |
|--- | --- |
| Class / scale | RELATIONAL_DERIVED_STATE / Normalized betweenness score from 0 to 1; weighted or directed variant |
| Construct / statistic | Ego shortest-path betweenness |
| Aliases / crosswalks | ['Brokerage centrality', 'intermediary position', 'shortest-path brokerage'] / ['CW-0023'] |
| Alias caution | SEARCH_ONLY/RELATED_SEARCH aliases are retrieval aids, not scientific equivalence; network connectedness/closeness/prestige require exact construct disambiguation. |
| Derivation / risk set | All relevant shortest paths and geodesic multiplicity; disconnected paths, weights and normalization change meaning. |
| Real antecedents | Rewiring or node loss changes paths; brokerage behavior is not betweenness. |
| Outgoing causal IDs | [] |
| Blocked/missing fields | [] |
| Shared inputs | Same network representation may feed multiple RDS; no independent simultaneous propagation |
| Targetability | FORBIDDEN_DIRECT_RDS_EFFECT |
| Governance question | Choose operational network boundary and estimator per application; no context-free scalar assumption |

Boundary sensitivity: Specify node set, tie relation/threshold, direction, weights, multiplex layers, boundary, window, missing ties/nodes, isolate inclusion, sampling, denominator and metric variant. Changing any of these can change a statistic without the claimed real-world mechanism. Snapshot versus longitudinal use must be specified; missing operational metadata is not filled.

## SOC-051 — Eigenvector Centrality

An actor's centrality as a function of being connected to other actors who are themselves well connected in the specified network.


|Item | Audit finding |
|--- | --- |
| Class / scale | RELATIONAL_DERIVED_STATE / Normalized eigenvector score; related prestige-centrality measure |
| Construct / statistic | Eigenvector-based ego position |
| Aliases / crosswalks | ['central-neighbor connectivity', 'influence centrality', 'Prestige centrality'] / ['CW-0024'] |
| Alias caution | SEARCH_ONLY/RELATED_SEARCH aliases are retrieval aids, not scientific equivalence; network connectedness/closeness/prestige require exact construct disambiguation. |
| Derivation / risk set | Whole adjacency and chosen eigenvector/normalization; disconnected components and directed/weighted conventions matter. |
| Real antecedents | Rewiring can redistribute scores without independently manipulating social influence. |
| Outgoing causal IDs | [] |
| Blocked/missing fields | [] |
| Shared inputs | Same network representation may feed multiple RDS; no independent simultaneous propagation |
| Targetability | FORBIDDEN_DIRECT_RDS_EFFECT |
| Governance question | Choose operational network boundary and estimator per application; no context-free scalar assumption |

Boundary sensitivity: Specify node set, tie relation/threshold, direction, weights, multiplex layers, boundary, window, missing ties/nodes, isolate inclusion, sampling, denominator and metric variant. Changing any of these can change a statistic without the claimed real-world mechanism. Snapshot versus longitudinal use must be specified; missing operational metadata is not filled.

## SOC-052 — Network Density

The proportion of all possible ties among actors in a defined social network that are present.


|Item | Audit finding |
|--- | --- |
| Class / scale | RELATIONAL_DERIVED_STATE / Observed ties divided by possible ties, with direction and loops specified |
| Construct / statistic | Whole-network density |
| Aliases / crosswalks | ['edge saturation', 'network connectedness', 'Tie density'] / ['CW-0025'] |
| Alias caution | SEARCH_ONLY/RELATED_SEARCH aliases are retrieval aids, not scientific equivalence; network connectedness/closeness/prestige require exact construct disambiguation. |
| Derivation / risk set | Observed ties over possible ties; n, directedness, loops, multiplex collapse and boundary determine denominator. |
| Real antecedents | Node admission/removal and contact restrictions can change numerator AND denominator. |
| Outgoing causal IDs | ['REL-SOC-031'] |
| Blocked/missing fields | [] |
| Shared inputs | Same network representation may feed multiple RDS; no independent simultaneous propagation |
| Targetability | FORBIDDEN_DIRECT_RDS_EFFECT |
| Governance question | Choose operational network boundary and estimator per application; no context-free scalar assumption |

Boundary sensitivity: Specify node set, tie relation/threshold, direction, weights, multiplex layers, boundary, window, missing ties/nodes, isolate inclusion, sampling, denominator and metric variant. Changing any of these can change a statistic without the claimed real-world mechanism. Snapshot versus longitudinal use must be specified; missing operational metadata is not filled.

## SOC-053 — Local Clustering

The proportion of possible ties among an actor's network neighbors that are present.


|Item | Audit finding |
|--- | --- |
| Class / scale | RELATIONAL_DERIVED_STATE / Local clustering coefficient from 0 to 1; weighted or directed variant |
| Construct / statistic | Ego neighborhood clustering |
| Aliases / crosswalks | ['Clustering coefficient', 'neighborhood closure', 'triadic closure'] / ['CW-0026'] |
| Alias caution | SEARCH_ONLY aliases do not establish equivalence. The triadic closure search alias on Local Clustering must not collapse SOC-053 into the distinct conditional-rate Driver SOC-102. |
| Derivation / risk set | Triangles among selected neighbors over eligible pairs; degree<2 convention unresolved at analysis time. |
| Real antecedents | Closing a tie changes triangle inputs; conditional closure rate is not a static clustering coefficient. |
| Outgoing causal IDs | ['REL-SOC-035'] |
| Blocked/missing fields | [] |
| Shared inputs | Same network representation may feed multiple RDS; no independent simultaneous propagation |
| Targetability | FORBIDDEN_DIRECT_RDS_EFFECT |
| Governance question | Choose operational network boundary and estimator per application; no context-free scalar assumption |

Boundary sensitivity: Specify node set, tie relation/threshold, direction, weights, multiplex layers, boundary, window, missing ties/nodes, isolate inclusion, sampling, denominator and metric variant. Changing any of these can change a statistic without the claimed real-world mechanism. Snapshot versus longitudinal use must be specified; missing operational metadata is not filled.

## SOC-054 — Network Assortativity

The degree to which social ties disproportionately connect actors who are similar on a specified attribute relative to a defined baseline.


|Item | Audit finding |
|--- | --- |
| Class / scale | RELATIONAL_DERIVED_STATE / Assortativity coefficient; observed-minus-expected same-category mixing |
| Construct / statistic | Attribute-specific mixing |
| Aliases / crosswalks | ['attribute assortativity', 'Homophilous mixing', 'like-with-like connectivity'] / ['CW-0027'] |
| Alias caution | SEARCH_ONLY/RELATED_SEARCH aliases are retrieval aids, not scientific equivalence; network connectedness/closeness/prestige require exact construct disambiguation. |
| Derivation / risk set | Mixing matrix and expected baseline; categorical/degree/scalar attribute choice changes construct. |
| Real antecedents | Assignment, selection and changing attributes affect matrix; preference cannot be inferred from mixing. |
| Outgoing causal IDs | ['REL-SOC-032'] |
| Blocked/missing fields | [] |
| Shared inputs | Same network representation may feed multiple RDS; no independent simultaneous propagation |
| Targetability | FORBIDDEN_DIRECT_RDS_EFFECT |
| Governance question | Choose operational network boundary and estimator per application; no context-free scalar assumption |

Boundary sensitivity: Specify node set, tie relation/threshold, direction, weights, multiplex layers, boundary, window, missing ties/nodes, isolate inclusion, sampling, denominator and metric variant. Changing any of these can change a statistic without the claimed real-world mechanism. Snapshot versus longitudinal use must be specified; missing operational metadata is not filled.

## SOC-055 — Structural Constraint

The degree to which an actor's network contacts are mutually connected or concentrated such that brokerage options are constrained.


|Item | Audit finding |
|--- | --- |
| Class / scale | RELATIONAL_DERIVED_STATE / Burt constraint score from low to high; contact redundancy index |
| Construct / statistic | Actor structural constraint |
| Aliases / crosswalks | ['contact redundancy', 'lack of structural holes', 'Network constraint'] / ['CW-0028'] |
| Alias caution | SEARCH_ONLY/RELATED_SEARCH aliases are retrieval aids, not scientific equivalence; network connectedness/closeness/prestige require exact construct disambiguation. |
| Derivation / risk set | Actor contacts and contact-to-contact weights; concentration and redundancy normalization require named formula. |
| Real antecedents | Brokerage opportunities may change when contacts change; behavior and path-based betweenness are distinct. |
| Outgoing causal IDs | ['REL-SOC-033'] |
| Blocked/missing fields | [] |
| Shared inputs | Same network representation may feed multiple RDS; no independent simultaneous propagation |
| Targetability | FORBIDDEN_DIRECT_RDS_EFFECT |
| Governance question | Choose operational network boundary and estimator per application; no context-free scalar assumption |

Boundary sensitivity: Specify node set, tie relation/threshold, direction, weights, multiplex layers, boundary, window, missing ties/nodes, isolate inclusion, sampling, denominator and metric variant. Changing any of these can change a statistic without the claimed real-world mechanism. Snapshot versus longitudinal use must be specified; missing operational metadata is not filled.

## SOC-056 — Cross-Cluster Tie Prevalence

The proportion of observed social ties that connect actors assigned to different network communities or social clusters.


|Item | Audit finding |
|--- | --- |
| Class / scale | RELATIONAL_DERIVED_STATE / Cross-community ties divided by all ties; bridge count normalized by opportunities |
| Construct / statistic | Tie-level cross-community share |
| Aliases / crosswalks | ['boundary-spanning connections', 'Bridging-tie prevalence', 'intercommunity ties'] / ['CW-0029'] |
| Alias caution | SEARCH_ONLY/RELATED_SEARCH aliases are retrieval aids, not scientific equivalence; network connectedness/closeness/prestige require exact construct disambiguation. |
| Derivation / risk set | Cross-community edges over observed eligible ties; community detection/assignment and scale essential. |
| Real antecedents | A partition change alone changes score without changed ties; member exposure is a separate denominator. |
| Outgoing causal IDs | ['REL-SOC-034'] |
| Blocked/missing fields | [] |
| Shared inputs | Same network representation may feed multiple RDS; no independent simultaneous propagation |
| Targetability | FORBIDDEN_DIRECT_RDS_EFFECT |
| Governance question | Choose operational network boundary and estimator per application; no context-free scalar assumption |

Boundary sensitivity: Specify node set, tie relation/threshold, direction, weights, multiplex layers, boundary, window, missing ties/nodes, isolate inclusion, sampling, denominator and metric variant. Changing any of these can change a statistic without the claimed real-world mechanism. Snapshot versus longitudinal use must be specified; missing operational metadata is not filled.

## SOC-057 — Network Segregation

The degree to which ties are concentrated within rather than between specified social groups beyond what group sizes and opportunities would predict.


|Item | Audit finding |
|--- | --- |
| Class / scale | RELATIONAL_DERIVED_STATE / Observed-to-expected within-group mixing; segregation index; low–high separation |
| Construct / statistic | Group mixing relative to opportunity |
| Aliases / crosswalks | ['group mixing deficit', 'relational segregation', 'Social network separation'] / ['CW-0030'] |
| Alias caution | SEARCH_ONLY/RELATED_SEARCH aliases are retrieval aids, not scientific equivalence; network connectedness/closeness/prestige require exact construct disambiguation. |
| Derivation / risk set | Group assignment and observed mixing with size/opportunity baseline; not any algorithmic community partition. |
| Real antecedents | Institutional assignment and contact configuration may matter; denominator/group changes can be mechanical. |
| Outgoing causal IDs | [] |
| Blocked/missing fields | [] |
| Shared inputs | Same network representation may feed multiple RDS; no independent simultaneous propagation |
| Targetability | FORBIDDEN_DIRECT_RDS_EFFECT |
| Governance question | Choose operational network boundary and estimator per application; no context-free scalar assumption |

Boundary sensitivity: Specify node set, tie relation/threshold, direction, weights, multiplex layers, boundary, window, missing ties/nodes, isolate inclusion, sampling, denominator and metric variant. Changing any of these can change a statistic without the claimed real-world mechanism. Snapshot versus longitudinal use must be specified; missing operational metadata is not filled.

## SOC-102 — Triadic Closure Rate

The rate or conditional probability that an open triad closes through formation of a specified tie between two actors who share one or more common neighbors during a specified interval.


|Item | Audit finding |
|--- | --- |
| Class / scale | DRIVER / Closed open triads divided by open triads at risk; event hazard; or model coefficient with its specification retained. |
| Construct / statistic | Conditional open-triad tie formation, not static triangle/clustering score or all-tie rate |
| Aliases / crosswalks | [] / [] |
| Alias caution | SEARCH_ONLY/RELATED_SEARCH aliases are retrieval aids, not scientific equivalence; network connectedness/closeness/prestige require exact construct disambiguation. |
| Derivation / risk set | Canonical Driver classification preserved. Operational rate denominator is eligible open triads; do not reclassify because measured by a ratio. |
| Real antecedents | Mutual-neighbor cues and contact opportunities may change restricted formation; actual rate effect unresolved |
| Outgoing causal IDs | [] |
| Blocked/missing fields | ['mechanism', 'modifiability', 'volatility', 'timeScaleOfChange', 'onsetCausalLag', 'persistenceRecovery', 'measurementAssessmentMethods', 'observability', 'evidenceStrength', 'evidenceNotes', 'keySources'] |
| Shared inputs | Open-triad risk set shares graph inputs; closure events must not also propagate as a second snapshot triangle effect |
| Targetability | DRIVER_TARGET_VALID; blocked metadata and exact risk set constrain evidence |
| Governance question | Resolve named blocked operational metadata only in a separate authorized decision; no substitute entity |

Boundary sensitivity: Specify node set, tie relation/threshold, direction, weights, multiplex layers, boundary, window, missing ties/nodes, isolate inclusion, sampling, denominator and metric variant. Changing any of these can change a statistic without the claimed real-world mechanism. Snapshot versus longitudinal use must be specified; missing operational metadata is not filled.
