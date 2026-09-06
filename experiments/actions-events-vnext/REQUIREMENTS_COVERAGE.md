# Requirement coverage and maintainer review

All design conclusions are PENDING. Tests demonstrate isolated representation
and mechanical controls; they do not validate the truth of scientific claims.

| User requirement | Deliverable / example | Test or review evidence |
|---|---|---|
| 1 Repository, actual HEAD, instructions, existing work and isolation | PLAN.md, PROGRESS.md, PROTECTED_BASELINE.json; baseline equals2636dd9 | `test_protected_hash_comparison_passes`; final diff restricted to experiment; remote gate below |
| 2 Durable milestones and resumability | PLAN.md / PROGRESS.md | Progress checkpoints and validation commands; exact next action recorded |
| 3 Every Layer/Family/entity and independent graph/count views | reports/inventory.json; layers/families/entities/matrices/auditQueue.csv; BIO-F01_baseline.json | `test_partition_and_family_reconciliation`, `test_graphs_and_matrices_remain_separate`, `test_projections_are_not_counted_as_science`; independent count recomputation |
| 3 Candidates, inactive, projections, RDS flags and coverage | Inventory summary/buckets; RDS specifications/shared inputs; incomplete projection fields | Candidate copies distinguished from canonical; `test_bio_f01_current_compatibility`; no scientific disposition inferred |
| 4 Focused primary architecture sources | SOURCES.json / ARCHITECTURE_RESEARCH.md | Nine primary sources; access depth, section and limitation review; no production registration |
| 5 All A–I overlapping domains, eight origins, target separation, agency/pattern/control | Architecture origin table; shared prompt checklist; synthetic origins | `test_eleven_properties_and_eight_layers`, `test_externality_not_exogeneity`; actor-action dry run |
| 6 Type versus occurrence versus effect; Intervention subset and stable identity | HappeningType/Occurrence/EffectAssertion contracts; compatibility table | Duplicate identity/episode tests; occurrence evidence cannot support effect automatically; no actual migration |
| 7 Driver effects, exact-edge modification, moderator route and RDS | Effect contract/overlap group; synthetic Moderator change | RDS/context-target rejection, edge/mechanistic-link tests, mediator reconciliation and separate pathway rejection |
| 8 Every effect class plus distribution/interactions/intended/unintended/valence | Eleven property table; synthetic fixture; effect schema scope/interaction/consequences | Every property tested, property/change constraints, cyclic sign, unknown/null and interaction validation; no real network editing |
| 9 Independent semantics/evidence basis/production/disposition/confidence/clarity/provenance/governance | Evidence sourceFindings/synthesis; model input role; separate occurrence evidence | Evidence graph-weight/number rejection, contrary evidence inclusion, source references, source versus model distinction, readiness tests |
| 10 Linked Pass A/B, local readiness, ownership and all-Family queue | RESEARCH_PROMPTS.md; GOVERNANCE_DECISIONS AE11; auditQueue.csv | `test_every_family_has_unadjudicated_queue_entry`; all105 rows PENDING; no scientific queue execution |
| 11 Working schemas/validation/inventory/determinism/dry run | prototype.py / model.py / schemas / synthetic.json | Output path and unknown Family rejection; byte-identical repeat report; pure dry-run tests; BIO original field equality |
| 12 Hypothetical policy, shock, outage, disclosure, network, gradual physiology, moderator | Eleven named synthetic examples | Semantic fixture tests; reviewed examples are fictional and have no real citations |
| 12 Failure cases: duplicate representations, unsupported occurrence attribution, causal inflation, missing context, RDS, doublecount, cyclic sign, unknown zero, contrary evidence, no effect, package inference | test_model.py | Named failure regression tests; independent counterexamples described below |
| 13 Five copy-ready prompts and decisive decision package | RESEARCH_PROMPTS.md / GOVERNANCE_DECISIONS.md | Each has inputs, outputs, automation boundary, completion and no-findings/deferrals; twelve decisions PENDING |
| 14 Skeptical review, existing regressions in isolated copy, protected hashes | TEST_RESULTS.json / validate.py / protected-comparison.json | Production migration/materializer tests confined to temporary clone; no existing tests modified |
| 15 Morning brief, commit, safe remote boundary and stop | MORNING_BRIEF.md / PROGRESS.md; final git report | No merge/deployment/activation/scientific Family work; draft PR only if refreshed trigger inspection passes |

## Independent critique and resulting changes

Two bounded read-only reviewers examined code, prose and counts. Numerical
reconciliation independently confirmed 456 active/435 causal, 297 isolated entities,
and BIO-F01 ten incident/three internal causal edges. No source-design citation
mismatch was identified; selected-section and abstract-only limits are retained.

Inventory review prompted resolved output-file containment for every writer,
actual invocation-commit provenance, separation of 20 candidate identity/assertion
copies from 11 linked evidence copies, native GOVERNED+ACTIVE filtering, actual
projection-incomplete flags and detection of untracked files outside the
experiment. Queue statuses no longer imply an undocumented audit never occurred.

Semantic review used adversarial synthetic modifications rather than trusting
happy-path tests. Required checks cover actor control before action eligibility,
nonempty relevant evidence, null-only versus positive support, unknown supported
changes, readiness of type/evidence dependencies, and model inferences that use
experimental source inputs without being mislabeled observations. See the actual
test results for pass/fail status; these findings are not hidden by schema text.

Final local acceptance: 49 prototype tests and 96 existing Python regressions
passed, as did 21 scenario-service tests (including 811 entities), schema/meta
validation, 19 JavaScript parses, Python compilation, local links and deterministic
regeneration. All 45 regenerated scientific files and 234 original protected
files were unchanged. The saved synthetic dry run reports zero status changes.
An independent recheck confirmed the semantic fixes; no governance approval is
implied. Current production CI does not run the experimental suite; local results
and any later CI results must be reported separately.

## Deliberate limits

- Closed-world schema validation cannot verify external scientific truth or
  completeness. Source content alignment remains independent human review.
- The dry run is a fictional eligibility check. It does not change D11/D12,
  authorize scientific use, rank actions, fit a model or execute a causal graph.
- Model-derived pathways remain outside the prototype Effect contract; governed
  CausalPathway structure would still be required. No reachability shortcut.
- Reconciliation demonstrates one primary contribution; a numerical
  multi-contribution reconciliation algorithm is deferred.
- The queue favors RDS-rich/large Families and legacy review burden; it is a
  transparent scheduling proposal with human override, not a priority fact.
- Broad automated scientific population, production schemas and consumers are
  absent. No synthetic content is inserted into the real candidate workspace.

## Remote action inspection

Read-only GitHub API inspection on 2026-09-06 found:

- Governance CI: `pull_request` against main, `push` on main, and manual dispatch;
  jobs contain validation/regeneration in the CI checkout, no deploy or publishing
  steps, no downstream workflow calls, and token permission `contents: read`.
- Dynamic Pages: legacy Pages build source is `main` at `/`. Branch push and
  draft PR do not update that source; merging main would trigger publication.
- Repository webhooks: zero. No workflow_run/repository_dispatch trigger is in
  the checked workflow.

The final remote gate rechecked main SHA, identical remote workflow content,
main-only Pages source and an exact empty hook response before pushing this
feature branch. This passed without workflow/settings changes. Only a draft PR
is permitted; merging would cross the publication boundary.
