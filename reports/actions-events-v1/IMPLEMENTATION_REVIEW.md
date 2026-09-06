# Implementation review and requirements coverage

Scope: architecture/tooling authorized by GOV-ACTIONS-EVENTS-V1-2026-09-06.
This is a maintainer-style independent second-pass review of the diff, not an
independent human scientific adjudication. No new scientific research occurred.

## Second-pass findings and resolutions

- Checked the complete changed-file list: existing scientific data/source registers,
  RI schemas/validators, application/scenario consumers, source workbooks, migration
  handoff and deployment settings are untouched. CI only gains validation steps.
- Replaced duplicate shared schema definitions with common scope/control/profile/
  provenance references. Existing RI D12 governance remains authoritative.
- Tightened subgroup reference resolution and Pass A use of existing RI semantic
  validators. Candidate revisions cannot reuse and overwrite canonical edge IDs.
- Found and closed an allowlisted-root symlink redirection case during final
  review. The report root itself must resolve to its actual permitted path;
  an added Linux-capable regression proves it cannot redirect into data.
- Added recorded-control override rejection, governed-inactive eligibility,
  component/package evidence isolation, observed-occurrence evidence success/failure,
  shared-dataset synthesis notes and complete-prompt coverage tests.
- SourceFinding disposition is preserved before synthesis; every contrary/null/mixed
  finding must have a synthesis rationale. Machines do not decide scientific support
  from bibliography alone. Citation alignment is explicitly a human review gate.
- Twenty-five compatibility views restore byte-equivalent JSON content with stable
  IDs/revisions/authority; no newly normalized empirical findings or actor control.
- Fixture IDs, source identities, decisions and populations are fictional SYN values.
  Fictional ACTIVE simulations are copies, with real eligibility always false.
- New native scientific catalogs and candidate workspace are empty.
- No numeric engine, consumer integration, source registration, occurrence ingestion,
  ranking, recommendation selection, scientific status writer or deployment code.
- Local validation runner regenerates existing artifacts only in a temporary clone.
  Scientific hashes are checked against frozen git content (checkout EOL distinguished)
  and raw bytes before/after validation. All 45 original data files are protected.
- Remaining limits: text-based scientific rationale cannot be verified semantically by
  JSON validation; shared contribution IDs and source identifiers still require
  research/review judgment; no identity-authentication service is claimed by provenance
  hashes; legacy sourceFindings remain unnormalized rather than guessed.

## Requirement-to-deliverable/test mapping

Paths below are repository-relative. Each row refers to an executable test,
schema constraint or explicitly manual review, not an inferred scientific result.

| User milestone | Implemented deliverable | Demonstration / gate |
|---|---|---|
| 0 scope/stop | Empty catalog, unchanged old files; this diff review | scientific_integrity, no consumers/deployment changes |
| 1 durable execution | experiments/actions-events-vnext/OVERNIGHT_EXECUTION.md | Per-milestone commit/PR/test log |
| 2 AE01–12 | docs/governance/ACTIONS_EVENTS_V1_GOVERNANCE_DECISION.md | Exact outcome and clarification review |
| 3 proposal merge | PR #15 governance commits and merge f573074 | 51 experimental + 96 Python + 21 scenario; Linux/Windows green |
| 4 separate branch | implementation/actions-events-v1 | git ancestry/scope review |
| 5 modular contracts | schemas/actions-events/v1 (11 schemas + vocabulary) | SchemaSet meta-validation; empty catalogs validate |
| 6 reusable identity | happening-type contract | test_all_origins_and_domains; package/identity tests |
| 7 occurrence | occurrence contract | observed proof success/failure; no effect evidence transfer |
| 8 effects | effect-assertion and vocabulary | Every property/descriptor, exact target/Layer, RDS, cyclic, null tests |
| 9 evidence | source-finding + evidence-assessment | Contrary preservation; shared dataset notes; no invented numeric estimates |
| 10 compatibility | SAME_IDENTITY read bridge | 25 exact round trips; legacy/projection dedup; BIO state/MIXED tests |
| 11 generic runner | scripts/audit_family.py | 14 runner tests, deterministic exports, unsafe-path rejection |
| 12 research workspace | candidate-workspace + empty passA/passB | No authority/activation allowed; RI Pass A semantics |
| 13 automated checks | scripts/actions_events_v1.py | ActionsEventsTests and CompatibilityTests |
| 14 eight-Layer synthetic pilot | scripts/actions_events_synthetic.py | 11 types, 11 episodes, 12 effects, 12 evidence; all eight origins/eleven properties |
| 15 separate eligibility | use_eligibility | Scientific/model/action separation; exact actor constraints fail closed |
| 16 reusable prompts | docs/governance/ACTIONS_EVENTS_RESEARCH_PROMPTS_V1.md | Five independently complete blocks; checklist coverage test |
| 17 whole ontology | reports/actions-events-v1/current | 105 Families/811 entities; semantic matrices; transparent queue |
| 18 full validation | scripts/validate_actions_events_v1.py; governance CI | Isolated tests/regeneration; schemas, source refs, scenario811, hashes, parse, links |
| 19 implementation PR | Separate implementation PR | Exact-head review and both blocking CI checks before merge |
| 20 post-merge readiness | Separate final readiness record after merge | Rerun synthetic/inventory against merged contracts |
| 21 Family #2 | Final readiness comparison PSY-F03/INF-F03/SOC-F07 | Mechanical workload only; no audit or sources searched |
| 22 scale-up safety | Final readiness gate table | Two different real governed pilots required; third recommended |
| 23 morning brief | experiments/actions-events-vnext/MORNING_BRIEF.md | Final merged state, CI, protected hashes, next authorization |
| 24 stop | No real Family #2 workspace population | Final empty native/candidate catalogs and unchanged old data |

## Validation evidence

See [LOCAL_VALIDATION.json](validation/LOCAL_VALIDATION.json) for exact tested SHA,
commands, output, timing and raw-byte comparisons. CI is recorded separately by
run ID; local success is not called CI success. Windows may lack symlink privilege;
the equivalent test runs without that skip on Linux. The old experimental
protected-file test was designed for a proposal-only allowlist and was completed
before PR #15 merge; it is not weakened to allow production implementation.
The production integrity test now protects the exact original scientific baseline.

Generated reports are read-only snapshots, not authoritative copies of scientific
records. Re-running at a new commit changes provenance, not the recorded science.
