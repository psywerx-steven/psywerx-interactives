# Synthetic structural demonstrations

**SYNTHETIC / NON_PRODUCTION / NOT A SCIENTIFIC MODEL.** Architecture approval remains PENDING. Every node, tie, group, opportunity, state and operation uses a fictional `SYN-*` ID. No real citations are attached as evidence for these invented examples.

Run from repository root:

```powershell
python experiments/network-state-vnext/prototype.py --output experiments/network-state-vnext/generated
python -m unittest discover -s tests -p test_network_state_vnext.py
```

[Generated examples](generated/synthetic-examples.json) include the full input, each delta, each resulting state, hashes, receipts and metrics. [State schema](generated/state.schema.json) and [delta schema](generated/delta.schema.json) are draft experimental contracts, not production schemas.

## Starting configuration

The fictional catalog contains A–E. The analytic boundary initially includes A–D. Friendship ties AB, AC, BC, CD and DE exist in the authored representation; DE is outside the initial analytic boundary. An A–D platform-access opportunity exists, but no A–D friendship does. All group membership starts in fictional group 1.

The selected simple undirected binary friendship graph has 4 nodes / 4 edges, degrees `(2,2,3,1)`, density `2/3`, local clustering `(1,1,1/3,0)`, degree centralization `2/3`, and disconnected-pair fragmentation `0`. These are arithmetic properties of the fixture, not population estimates or evidence of causal effects.

## Nine independent changes from the same starting revision

| Case | Deterministic operation | Selected nodes / edges | Density | Degree centralization | What is NOT inferred |
| --- | --- | --- | --- | --- | --- |
| Add tie | Add modeled AD friendship | 4 / 5 | 5/6 | 1/3 | Trust, adoption or an empirical tie-formation effect |
| Remove tie | Remove modeled AB | 4 / 3 | 1/2 | 1 | Behavioral change or a causal effect of a metric |
| Node enters | Add fictional F as isolated, included node | 5 / 4 | 2/5 | 7/12 | Automatic friendship or social isolation as a psychological construct |
| Node leaves | Retire C; explicitly remove AC, BC, CD and record receipt | 3 / 1 | 1/3 | 1/2 | A deletion from the real world or arbitrary loss of history |
| Membership changes | Move A to modeled group 2 | 4 / 4 | 2/3 | 2/3 | Friendship, attribute homophily or causal segregation change |
| Boundary expands | Include already-known E; DE becomes visible to calculation | 5 / 5 | 1/2 | 5/12 | Actual tie creation; this is analytic selection only |
| Tie weight changes | AB weight 1 → 2 | 4 / 4 | 2/3 | 2/3 | Changed binary degree or a numerical causal weight |
| Platform access disabled | Disable A–D contact opportunity | 4 / 4 | 2/3 | 2/3 | Deletion of an existing friendship |
| Seats assigned | Add A–D seating contact opportunity | 4 / 4 | 2/3 | 2/3 | Creation of A–D friendship |

Fragmentation is explicitly the fraction of unreachable unordered pairs, not an unspecified “fragmentation score.” It becomes `2/5` on isolated node entry and `2/3` on C’s exit; other listed cases remain connected. Low-degree local clustering uses a declared zero convention. Singleton density/centralization normalization returns not-applicable/null, not invented precision.

## Safeguards and negative tests

- Typed social ties cannot serialize as PSYWERX Relationships. Production AE validators reject Degree/Density RDS targets and synthetic state/tie targets.
- Observations cannot claim perfect real state. Missingness provenance is required; incomplete-frame metrics remain conditional on the representation.
- Boundary changes are classified separately, cannot be bundled as tie mutation, and preserve all actual modeled ties.
- Node IDs cannot be recycled; duplicate tie IDs and duplicate dyads are rejected. Node exit retains a tombstone and records removed ties.
- Prior version/hash checks and copy-on-apply keep failed multi-operation updates atomic. Replaying on a changed revision fails.
- Complete all-node degree keys and an exact matching external benchmark are required. One actor cannot stand in for the distribution.
- State receipts establish no scientific consequences or empirical evidence. Reachability is not mediation; metric recomputation cannot be added as causal propagation.
- Static snapshots do not silently become dynamic intervals. Directed and multiplex data can be represented, but directed metrics and multiplex collapse are refused unless a future specification supports them.
- Output is confined to an explicit child of this experiment, including resolved-file path checks. Production data, schemas and service paths are rejected.

## What this proves and does not prove

It proves that these distinctions and deterministic operations can coexist in a small typed representation, while AE04/D10 remain unchanged. It does not prove that a modeled operation happens in reality, that a network is fully observed, that any intervention works, or that the current scientific ontology has an adequate target for every structural effect.

No live network ingestion, probabilistic model, uncertainty propagation, topology optimization, recommendation, causal pathway execution or production adapter is implemented. Weighted/directed metric variants, time-respecting paths, recurrent parallel tie episodes, signed weights, hyperedges and multi-observation reconciliation remain unimplemented. The prototype’s scalar centralization helper is an interface check over a supplied collection, not an independent network estimator; reported collections are generated from validated fixture adjacency.
