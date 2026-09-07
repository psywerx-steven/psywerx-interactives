# SOC-F07 governance and isolated prototype validation

Checkpoint status: local validation passed; final-head Linux/Windows CI pending.

- Production RI and AE validators pass after selective materialization: 770 Drivers, 41 RDS, 811 entities, 457 active Relationships / 436 causal.
- SOC-F07 checkpoint suite: 19 tests passed locally.
- Network State suite: 43 tests pass, including all nine cases, complete collection/benchmark validation, UTC interval boundaries, atomicity, output isolation and forbidden interpretations.
- Protected comparison permits only exact seven identity records, their authorization and six source records in two additive envelopes; every pre-existing record is compared for equality. No general file whitelist.
- Candidate scientific workspace and source findings remain exactly equal to pre-checkpoint head. Human audit/decision/queue metadata changes are separate.
- Required Python suites: migration 19; RI V1 38; BIO pilot 13/governance 15/activation 11; AE V1 65; audit-family 14 (two Windows symlink-privilege skips); INF pilot 29/governance 17/activation audit 14/activation 14; SOC pilot 36/governance 19; Network State 43. Total 347 tests, two platform-specific skips, no remaining failures.
- Scenario-service: 21 tests pass. Existing eight-Layer synthetic pilot validates 46 synthetic records; no real status changes.
- Determinism: migration regeneration, SOC renderer, source/identity materialization and generated Network State artifacts pass. The INF deterministic materializer also preserves SOC additions.
- Python compilation passes for scripts/tests/isolated prototype; all 19 tracked JavaScript files parse. SOC/prototype Markdown local links and `git diff --check` pass. Production RI/AE schema/meta-validation and source/reference/governance checks pass.

## Failures found and corrected during validation

Historical BIO/INF tests assumed a fixed global source/catalog size. They failed on the authorized additive SOC identities/sources. Tests now freeze the BIO source set and the exact INF record/authorization set, preserving every historical record and the entire catalog validation. No scientific assertion, production validator or governance gate was weakened. Prototype development also corrected an interval-end convention and added non-graphical degree-vector rejection; neither changes production contracts.

## Independent scope review

The candidate scientific workspace and all candidate source findings match the pre-checkpoint head exactly. Source aliases are normalized only in new canonical identity provenance. The source manifest explicitly distinguishes bibliography verification from the unsupported non-PubMed registration path. The derivation remains blocked despite valid free-text schema payloads: semantic collection enforcement is absent. No field-completion, retyping, new Driver, AE04 target, inference weight or consumer change was introduced.

CI changes add the two bounded suites to existing Linux and Windows jobs and compile the isolated Python prototype. Workflow triggers, permissions and deployment behavior are unchanged. GitHub Pages remains legacy publication from main `/`; this unmerged branch does not change its source. Final-head CI results are to be recorded after push.

No activation, merge, production architecture change or deployment action is performed. Final results will replace this in-progress section before closeout.
