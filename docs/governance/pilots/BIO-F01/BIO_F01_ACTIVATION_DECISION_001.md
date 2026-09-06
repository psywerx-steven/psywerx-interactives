# BIO-F01 Activation Decision 001

## Decision identity

| Field | Value |
|---|---|
| Activation decision ID | `GOV-BIO-F01-ACTIVATION-001-2026-09-05` |
| Audit ID | `AUD-BIO-F01-RI-V1-20260905-001` |
| Prior scientific governance decision | `GOV-BIO-F01-001-2026-09-05` |
| Prior decision record | `BIO_F01_GOVERNANCE_DECISION_001.md` |
| Pull request | `#14` |
| Pre-activation head | `f3a933d09f98c08fa8c31374ed17658a660943aa` |
| Frozen scientific baseline | `5001611852107f2b95b8f722c71224dc7a538d47` |
| Governance actor class | `authorized human governor` |
| Effective date | `2026-09-05` |
| Authorization basis | The explicit human instruction authorizing the bounded BIO-F01 partial activation and the three evidence-fidelity corrections recorded below. |

## Decision

The records listed in the exact activation set below are authorized to move from
`GOVERNED + INACTIVE` to `GOVERNED + ACTIVE` after all validation gates pass.
No other record is authorized for activation. Scientific activation makes a
record eligible for production scientific use; it does not authorize a new
modeling, simulation, ranking, recommendation, Explorer, or deployment path.

## Exact activated records

### Relationships

- `REL-V1-BIO-F01-001`
- `REL-V1-BIO-F01-002`
- `REL-V1-BIO-F01-003`
- `REL-V1-BIO-F01-004`
- `REL-V1-BIO-F01-005`
- `REL-V1-BIO-F01-006`

The first four are causal. `REL-V1-BIO-F01-005` is a symmetric association and
`REL-V1-BIO-F01-006` is a derivational dependency; neither is eligible for
causal traversal.

### Intervention identities

- `INT-V1-BIO-F01-001`
- `INT-V1-BIO-F01-003`
- `INT-V1-BIO-F01-006`
- `INT-V1-BIO-F01-007`
- `INT-V1-BIO-F01-008`

### InterventionEffects

- `IE-V1-BIO-F01-001`
- `IE-V1-BIO-F01-003`
- `IE-V1-BIO-F01-004`
- `IE-V1-BIO-F01-005`
- `IE-V1-BIO-F01-006`

### EvidenceAssessments

- `EVA-V1-BIO-F01-REL-001`
- `EVA-V1-BIO-F01-REL-002`
- `EVA-V1-BIO-F01-REL-003`
- `EVA-V1-BIO-F01-REL-004`
- `EVA-V1-BIO-F01-REL-006`
- `EVA-V1-BIO-F01-REL-009`
- `EVA-V1-BIO-F01-IE-001`
- `EVA-V1-BIO-F01-IE-003`
- `EVA-V1-BIO-F01-IE-004`
- `EVA-V1-BIO-F01-IE-005`
- `EVA-V1-BIO-F01-IE-006`

## Authorized evidence-fidelity corrections

Only these scientific-record corrections accompany activation:

1. In `EVA-V1-BIO-F01-REL-001`, the stale narrative source alias
   `BIOF01-EXT-007` is replaced with its canonical source ID `SRC-536`.
   Structured source IDs and all scientific semantics remain unchanged.
2. `EVA-V1-BIO-F01-IE-005` changes from `SUPPORTS` to `MIXED`. `SRC-539`
   remains supportive of controlled phase resetting, while `SRC-541` is
   represented as mixed/null clinical evidence. Timing-dependent advance or
   delay, heterogeneity, and limited persistence/generalization are retained.
3. `EVA-V1-BIO-F01-IE-006` changes from `SUPPORTS` to `MIXED`. `SRC-540`
   remains supportive of appropriately timed phase advancement, while
   `SRC-549` is recorded as a null between-group DLMO result with possible
   sleep-promoting rather than measurable phase-shifting benefit.

Evidence strength and confidence remain `MODERATE` for the two corrected mixed
assessments. No quantitative estimate, graph weight, source substitution, or
broader proposition is authorized.

## Intentionally inactive and excluded records

These governed Intervention identities remain `GOVERNED + INACTIVE` because
they lack their own governed active effect:

- `INT-V1-BIO-F01-002`
- `INT-V1-BIO-F01-004`
- `INT-V1-BIO-F01-005`
- `INT-V1-BIO-F01-010`

The following remain non-governed and non-active:

- Relationships: `REL-CAND-BIO-F01-005`, `REL-CAND-BIO-F01-007`, and
  `REL-CAND-BIO-F01-008`.
- InterventionEffects: `IE-CAND-BIO-F01-002`, `IE-CAND-BIO-F01-007`,
  `IE-CAND-BIO-F01-008`, and `IE-CAND-BIO-F01-009`.
- Acoustic identities: `INT-CAND-BIO-F01-009` and
  `INT-CAND-BIO-F01-011`.
- Existing-edge revision proposals B01 through B05.
- Moderation assertions and CausalPathways: none.
- Rejected hypotheses H01 through H05 remain rejected and protected from
  silent regeneration.

## Validation gates and graph effect

Activation is effective only with successful schema, evidence, source,
lineage, lifecycle, RDS, traversal, intervention-eligibility, regression, and
determinism validation. The mechanically expected active Relationship state is
456 total and 435 causal: the 450/431 V3 baseline plus four active V1 causal
Relationships and two active V1 noncausal Relationships.

For BIO-F01, the expected causal graph change is:

| Metric | Before | After |
|---|---:|---:|
| Incident causal edges | 6 | 10 |
| Internal causal edges | 1 | 3 |
| Same-Layer cross-Family causal edges | 3 | 4 |
| Cross-Layer causal edges | 2 | 3 |
| Causally isolated BIO-F01 entities | 8 | 6 |

Activation must introduce no causal cycle, reciprocal pair, duplicate
proposition, RDS exogenous root, or aggregate/constituent double counting. The
association and derivational records contribute no causal graph degree.

## Unresolved items retained

- Existing-edge revision proposals for `REL-BIO-001`, `REL-BIO-003`,
  `REL-BIO-009`, `REL-BIO-021`, and `REL-ENV-040` remain non-governed.
  `REL-BIO-001` remains flagged for heightened RDS/exogeneity review.
- The research-needed Relationships, InterventionEffects, and acoustic
  identities listed above remain unresolved.
- The governed v0.3 open items remain unresolved: `INS-102`, `REL-SOC-028`,
  `REL-TEC-049`, `REL-MIG-CAND-0001`, `REL-MIG-CAND-0002`,
  `REL-MIG-CAND-0003`, and `NEW-ENTITIES-V0.3`.
- No BIO-F01 Moderation assertion or CausalPathway has been governed.

## Future review triggers

Review is required before any substantive revision, deactivation, addition of
BIO-F01 science, resolution of the listed open items, Family-scale
extrapolation, or connection to a modeling or recommendation algorithm.
Material new evidence that changes phase-response interpretation,
subjective/objective sleep-continuity divergence, source validity, or RDS
independence also triggers review.

No second Family audit, deployment, or application-behavior change is approved
by this decision.
