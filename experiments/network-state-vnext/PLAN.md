# SOC-F07 governance and bounded network-state review

Status: milestones 1–4 complete; milestone 5 local and checkpoint CI validation passed, with final-head confirmation tracked in PR #19. Architecture content is EXPERIMENTAL / NON_PRODUCTION; every new architecture decision remains PENDING.

Starting branch: `pilot/soc-f07-actions-events-v1`; head: `339c2e80206b0b304cdb262e7c5fec6dc0bc27ab`; main: `f0be9c24288bd128231e0d1243b34c03ad055906`.

## Milestones and acceptance gates

1. Reconcile human decisions, production contracts, candidate lineage and source identities. Preserve all existing science; do not bypass collection-level derivation or source-registration constraints.
2. Record exact human decisions and selectively materialize only representable, source-verified approved identities/propositions as GOVERNED + INACTIVE. Commit a durable checkpoint.
3. Compare Driver-only, ontology-type and scenario-substrate options. Draft NS01–NS12, all PENDING, with compatibility, observation, time, privacy and execution boundaries.
4. Build a synthetic-only, deterministic state/delta prototype and metric demonstrations. Reject prohibited targets, causal interpretations and unsafe output paths.
5. Independently review scope; run explicit repository suites, protected-record comparison and deterministic regeneration. Commit/push and update PR #19; inspect Linux/Windows CI. Never merge or activate.

## Validation commands

- `python -m unittest discover -s tests -p test_soc_f07_governance_001.py`
- `python -m unittest discover -s tests -p test_network_state_vnext.py`
- Explicit repository test patterns from `.github/workflows/governance-ci.yml` (not unrelated catch-all discovery).
- `python scripts/relationship_intervention_v1.py --validate-repository`
- `python scripts/actions_events_v1.py --validate-repository`
- `python scripts/build_soc_f07_pilot.py` and checkpoint/prototype deterministic regeneration with comparison.
- Python compilation; tracked JavaScript parsing; Markdown/local links; `git diff --check`.
- Compare every pre-existing protected scientific record, permitting only the exact authorized additive sources/identities.

## Stop boundaries

No production schema/target changes; no existing edge revisions; no blocked field repair; no activation; no merge; no new Family; no simulation/recommendation/deployment. Representation failures remain explicit, not approximated. Architecture recommendations are not human decisions.
