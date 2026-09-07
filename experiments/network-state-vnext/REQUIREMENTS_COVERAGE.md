# Requirements coverage and review map

Scope: latest SOC-F07 governance + bounded Network State instruction, sections 1–38. Prototype material is EXPERIMENTAL / NON_PRODUCTION; NS decisions remain PENDING. Validation outcomes are recorded in [progress](PROGRESS.md) and the [checkpoint validation report](../../docs/governance/pilots/SOC-F07/SOC_F07_GOVERNANCE_VALIDATION.md), not presumed from this table.

Abbreviations: **G** = [checkpoint tests](../../tests/test_soc_f07_governance_001.py); **N** = [prototype tests](../../tests/test_network_state_vnext.py); **P** = [pilot tests](../../tests/test_soc_f07_pilot.py). [Human decisions](../../docs/governance/pilots/SOC-F07/SOC_F07_GOVERNANCE_DECISION_001.md); [lineage manifest](../../data/actions-events-v1/SOC-F07-materialization-manifest.json).

| Requirement | Deliverable / concrete case | Test or review |
| --- | --- | --- |
| 1 Authorization | Seven inactive identities; explicit conditional non-materialization | G exact subset, inactive/hash authority, protected records |
| 2 Durable decisions | Human record + machine decisions + updated package | G exact outcomes and actor class |
| 3 Retain semantic edges | Three retained bounded propositions | G exact old relationships; P noncausal safeguards |
| 4 Retype review only | REL-SOC-031–034 proposals unchanged scientifically | G review-only + P snapshot hashes |
| 5 Revision review only | REL-INS-047 / REL-SOC-035 | G review-only and protected science |
| 6 REL-TEC-050 | Human RESEARCH_NEEDED disposition | G retained/current disposition |
| 7 Conditional derivation | Concept approved; BLOCKED_PENDING_REPRESENTATION | G typed-field rejection and scalar-text counterexample; N all-node benchmark tests |
| 8 Eight identity decisions | All eight approved; seven materialized; HT-008 source-contract block | G exact identity set and source gate |
| 9 Effects remain RN | Three candidate UNKNOWN effects | G candidate/evidence equality |
| 10 Non-creation | No new causal/moderation/pathway/other records | G catalog/reference equality; P no inference |
| 11 Rejections | Exact 15 hypotheses | G rejected ledger equality and regeneration protection |
| 12 Research-needed | Exact eleven hypotheses | G exact research set |
| 13 Blocks/gaps | H12/H20 + twelve unresolved gaps | G block statuses; P canonical missing fields |
| 14 Selective registration | Six sources, two canonical IDs reused; twelve supplemental unregistered | G exact source delta/dedup; registration manifest |
| 15 Governed evidence | Zero EVA/findings; identity provenance is not efficacy | G assessment/sourceFinding equality |
| 16 Active boundary | 770 / 41 / 811 / 457 / 436 | G counts; production validators; scenario regressions |
| 17 Underlying state question | Proposal: configuration is not a process rate | N membership/access/seating cases; architecture review |
| 18 Options A/B/C | Comparative table and challenge to hybrid | Prose review of costs, target and migration tradeoffs |
| 19 Distinctions | Eleven-object table | N social tie, delta/EffectAssertion and direct-target failures |
| 20 Observation vs real | Separate observation artifacts recommended; synthetic metadata implemented | N truth and missingness failures |
| 21 Time/dynamics | Snapshot/interval/validity; no evolution engine | N static/interval/expired-tie tests |
| 22 Twelve RDS interface | Actual RDS mapping table; explicit variant/input needs | N five arithmetic examples; G production definitions unchanged |
| 23 AE interfaces | Five alternatives; operations for ties/nodes/access/groups/seats | N nine demonstrations + rewire |
| 24 Mutation vs science | State receipts without evidence/claims | N consequences/empirical/middleware rejection |
| 25 Execution boundary | Deterministic fixture recomputation only | N forbidden-use guard; no service imports/modifications |
| 26 Privacy/identity | Pseudonymous IDs, external mapping, retention/export considerations | N SYN-only fixtures; design review, not a privacy system |
| 27 Isolated prototype | State/delta schemas, fixture, nine generated cases | N deterministic artifacts and path tests |
| 28 Failure cases | All twelve requested failure categories | N direct RDS, tie namespace, truth, boundary, causality, collection, missingness, evidence, mediation, time, duplicate propagation |
| 29 NS01–NS12 | PENDING decision table + structured decisions | N exact NS set/status; backward-compatibility review |
| 30 Challenge hybrid | Driver-only valid for qualitative catalog; hybrid not enough for whole-state effect claims | Proposal alternatives / remaining target gap |
| 31 Scale-up | NOT_READY_PENDING_NETWORK_STATE_DECISION + additional gates | Cross-pilot handoff; no scale-up action |
| 32 Governance tests | G exact approved scope and gates | Explicit 19-test suite plus P |
| 33 Prototype tests | N determinism/identity/delta/observation/metrics/isolation | Explicit N suite; directed/multiplex refusals |
| 34 Validation | Required repository patterns, schema, service, parsing, CI | Checkpoint validation report; actual CI on PR #19 |
| 35 Protected science | All old records preserved; only two additive envelopes differ | G exact additions; P 133-file comparison; BIO/INF regressions |
| 36 PR19 | Existing branch, no merge or activation PR | Remote final-head/check/status review |
| 37 Deliverables | This directory + SOC-F07 governance/source/handoff records | N/P local links and deterministic products |
| 38 Final report | Handoff and user closeout with actual counts/CI/Git | Final diff/scope review; no unearned completion claim |

## Skeptical review conclusions

The design intentionally fails closed on a single-ego derivation and on treating a social tie as an ontology Relationship. A byte-valid JSON object is not sufficient scientific semantics. A production source contract can also exclude a valid discipline-specific source: HT-008 was not smuggled through empty identitySourceIds or a false PubMed label.

The hybrid option preserves target safeguards but does not solve scientific whole-configuration targeting. Synthetic arithmetic demonstrates a proposed interface only; the actual RDS definitions and blocked fields remain untouched. Existing research findings do not become governed merely because a reusable identity was approved. No scale-up decision is inferred from three pilots.
