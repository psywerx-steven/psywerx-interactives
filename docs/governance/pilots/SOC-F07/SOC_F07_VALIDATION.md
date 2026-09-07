# Validation and skeptical review

Audit: `AUD-SOC-F07-AE-V1-20260906-001`.
Baseline: `f0be9c24288bd128231e0d1243b34c03ad055906`.
Research package checkpoint: `a6b3eb2`.

## Actual local results

| Check | Result |
| --- | --- |
| SOC-F07 pilot suite | 35 passed; includes schema, sourceFinding, lifecycle, ownership, RDS, exclusion, exact membership, hash and deterministic-render checks |
| Repository-defined Python regressions | 249 run, successful; 2 existing Windows symlink-related skips |
| Scenario service | 21 passed |
| RI V1 repository validation | Passed; 457 active / 436 causal |
| AE V1 repository validation | Passed; no status changes |
| Eight-Layer synthetic structural regression | Passed; 46 synthetic records; zero real status changes; no network simulation executed |
| Governed v0.3 baseline regeneration | Passed; no scientific data diff |
| Protected pre-existing files | 133/133 unchanged against start, LF-normalized SHA-256; includes data, sources, schemas, BIO-F01, INF-F03, migration handoff and scenario service |
| Python compilation | `python -m compileall -q scripts tests` passed |
| JavaScript parsing | Every Git-tracked `.js`, `.mjs`, `.cjs` passed `node --check` |
| Markdown/local links | SOC-F07 suite passed |
| Whitespace | `git diff --check` passed |
| Linux/Windows CI | Added SOC-F07 suite to both existing validation jobs; final-head results recorded in PR and execution closeout |

Canonical Python patterns run explicitly: `test_migration_v0_3.py`,
`test_relationship_intervention_v1.py`, `test_bio_f01_pilot.py`,
`test_bio_f01_governance_001.py`, `test_bio_f01_activation_001.py`,
`test_actions_events_v1.py`, `test_audit_family.py`, `test_inf_f03_pilot.py`,
`test_inf_f03_governance_001.py`, `test_inf_f03_activation_audit_001.py`,
`test_inf_f03_activation_001.py`. No noncanonical catch-all discovery was run.

## Independent second-pass skeptical self-review

This is an automated second-pass review, not a claimed independent human review.

- **Causal yield challenged:** the clustering/cooperation hypothesis remains a
  question, not a formal causal candidate. No association was promoted to causality.
- **Exact target challenged:** common-neighbor, group-introduction and disaster
  evidence does not yet adequately establish the exact SOC-102 risk set. All three
  effects are RESEARCH_NEEDED, with `change: UNKNOWN`, not established INCREASE.
- **RDS causal claims challenged:** four same-time metric pairs require retype
  review; SOC-053 to SOC-061 has a plausible mechanism but incomplete alignment.
  No existing authority was changed or grandfathered as executable V1 science.
- **Source alignment challenged:** SRC-509 is a composite reference whose linked
  PMID duplicates SRC-235. SRC-497 was inspected at metadata depth only. Neither
  is treated as a new independent direct finding. Reviews and primary studies
  are not counted as independent replications.
- **Contrary evidence challenged:** source-level mixed findings and three null
  contrasts remain structured. No null of a different outcome is labeled a null
  SOC-102 effect. No unsupported numerical estimate or equivalence claim appears.
- **Network semantics challenged:** no real interpersonal tie is a PSYWERX
  Relationship; no event directly targets an RDS; no topology manipulation is
  smuggled into STRUCTURE by renaming a statistic.
- **Derivation challenged:** the single dependency is only the degree-based
  centralization case using a whole distribution and external benchmark. It
  neither determines all centralization variants nor supplies missing RDS fields.
- **Temporal/identification challenged:** reflection, selection, homophily,
  interference, endogenous ties, boundaries and missingness remain explicit.
  SAOM/theory/sensitivity-model evidence is not called a randomized causal result.
- **Production boundaries challenged:** no scientific activation, source
  registration, recommendation, diffusion/network execution or prior-pilot repair.

## Requirement coverage

| User sections | Deliverable / evidence | Test or review |
| --- | --- | --- |
| 0–3, 41 | Frozen generic-runner baseline, EXECUTION, manifest, protected-science.json | Exact main/membership/counts; protected hash and deterministic tests |
| 4–7, 12–14, 19, 20, 29 | Entity/RDS review, 12 antecedent ledgers, blocked fields, special findings | 12 forbidden target mutations; all 4 blocked entities and 11 fields each preserved |
| 8–10 | Ten existing dispositions, six unimplemented review proposals, seven assertion audits | Five RDS causal sources and four EXCEPTIONAL gates explicitly checked |
| 11, 21–24 | 29 hypotheses, source registry, source findings before synthesis | No causal/pathway/moderation fabrication; design and null-preservation checks |
| 15–18, 25–27, 30–31 | Eight identities, three research-needed Driver effects, target gaps, 72 origin/domain cells and 88 property/target cells | Origin/target, shared-contribution, unknown-not-zero, RDS/STRUCTURE and social-tie counterexamples |
| 28 | Ownership/shared-issue fields and existing/native/projection duplicate checks | Owner and no duplicate derivational proposition tests; no consultation claimed completed |
| 32–35 | Hypothesis ledger, workspace, candidate source queue, governance decision package | Rejections protected, human fields PENDING, no source registration or governance transition |
| 36–39 | Special network findings, cross-pilot comparison, this skeptical review | Explicit ontology target-gap finding; no substitute Driver or scale-up permission |
| 40 | 35 SOC-F07 tests plus required existing suites and CI additions | Local results above; final-head Linux/Windows jobs required |
| 42–44 | Candidate-only PR and EXECUTION closeout | Open/unmerged, branch/remote equality, clean tree, exact stop boundary |

## Remote-action safety

The only checked-in workflow is governance validation: PRs to main, pushes to
main, and explicit dispatch; read-only content permission and no deployment job.
The GitHub Pages API reports legacy Pages builds from **main `/`**. This pilot
pushes a separate branch and opens an unmerged PR. It does not update main,
dispatch deployment or alter Pages settings. Only two SOC-F07 validation steps
were added to existing Linux/Windows jobs; trigger and permission rules unchanged.

## Restart / reproduction

```text
python scripts/build_soc_f07_pilot.py
python -m unittest discover -s tests -p test_soc_f07_pilot.py
python scripts/relationship_intervention_v1.py --validate-repository
python scripts/actions_events_v1.py --validate-repository
git diff --check
```

The renderer is deterministic and confined to the SOC-F07 candidate/document
directories. Its test captures all outputs and compares them without writing.
The frozen baseline must not be regenerated with a later HEAD. No test result
constitutes human scientific approval.
