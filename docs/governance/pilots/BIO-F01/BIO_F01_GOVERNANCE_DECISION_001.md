# BIO-F01 Governance Decision 001

> This record governs scientific content and its initial inactive
> materialization. The later, bounded activation-state decision is recorded in
> [BIO_F01_ACTIVATION_DECISION_001.md](BIO_F01_ACTIVATION_DECISION_001.md).

**Decision ID:** `GOV-BIO-F01-001-2026-09-05`

**Audit ID:** `AUD-BIO-F01-RI-V1-20260905-001`

**Frozen scientific baseline:** `5001611852107f2b95b8f722c71224dc7a538d47`

**Pilot PR:** [#14](https://github.com/psywerx-steven/psywerx-interactives/pull/14)

**Pilot head before this decision:** `0cb77c4722b0d4c474f307d8ae527b8fa6f652cf`

**Governance actor class:** `authorized human governor`

**Effective governance date:** 2026-09-05

**Source authorization:** The explicit user instruction directing the first
human-governance materialization checkpoint for BIO-F01.

## Authority and limit

This decision authorizes only the exact scientific dispositions and
governed-inactive materializations recorded below and in the linked
[decision package](BIO_F01_GOVERNANCE_DECISION_PACKAGE.md). It does not
authorize activation, deployment, another Family audit, an ontology
classification change, or implementation of an existing-edge revision.

Every approved new scientific object enters V1 as:

- `lifecycleStatus: GOVERNED`
- `activationStatus: INACTIVE`

The records are therefore excluded from default causal traversal, graph
metrics, scenario execution, and intervention recommendation.

## Existing Relationship dispositions

- `REL-BIO-002` is retained scientifically unchanged and V1-incomplete.
- `REL-RDS-0016` through `REL-RDS-0020` are retained unchanged as noncausal
  derivational dependencies.
- `REL-BIO-001`, `REL-BIO-003`, `REL-BIO-009`, `REL-BIO-021`, and
  `REL-ENV-040` remain unchanged; only exact non-governed revision proposals
  `REL-REV-BIO-F01-B01` through `REL-REV-BIO-F01-B05` are authorized.

## Canonical Relationship materialization

| Candidate | Canonical V1 ID | Decision | Activation |
| --- | --- | --- | --- |
| `REL-CAND-BIO-F01-001` | `REL-V1-BIO-F01-001` | Approved bounded Sleep Duration → Sleep Inertia Severity causal claim | `INACTIVE` |
| `REL-CAND-BIO-F01-002` | `REL-V1-BIO-F01-002` | Modified and approved with cyclic/state-dependent phase semantics and no universal sign | `INACTIVE` |
| `REL-CAND-BIO-F01-003` | `REL-V1-BIO-F01-003` | Approved bounded Caffeine Effect Level → Sleep Duration causal claim | `INACTIVE` |
| `REL-CAND-BIO-F01-004` | `REL-V1-BIO-F01-004` | Conditional approval satisfied after source and proposition-distinction checks | `INACTIVE` |
| `REL-CAND-BIO-F01-006` | `REL-V1-BIO-F01-005` | Approved symmetric noncausal association with instrument qualification | `INACTIVE` |
| `REL-CAND-BIO-F01-009` | `REL-V1-BIO-F01-006` | Approved noncausal derivational dependency; external timing remains required | `INACTIVE` |

`REL-CAND-BIO-F01-005`, `REL-CAND-BIO-F01-007`, and
`REL-CAND-BIO-F01-008` remain `RESEARCH_NEEDED` and non-governed. No
Moderation or CausalPathway is governed.

## Canonical Intervention materialization

The following identities are approved and materialized `GOVERNED + INACTIVE`:

`INT-V1-BIO-F01-001`, `002`, `003`, `004`, `005`, `006`, `007`, `008`, and
`010`, with candidate lineage preserving the same suffix.

`INT-V1-BIO-F01-006` is a package whose current component list names included
known/core components, not an exhaustive definition of CBT-I. No component
effect is inferred and no package effect is inferred from components.

The generic acoustic candidate `INT-CAND-BIO-F01-009` is not governed. It is
retained as an unresolved umbrella, and receiver-level candidate
`INT-CAND-BIO-F01-011` is created with explicit lineage. Source- and
transmission/path-control identities were not created because the reviewed
intervention evidence did not establish those reusable identity boundaries.

## Canonical InterventionEffect materialization

| Candidate | Canonical V1 ID | Decision | Activation |
| --- | --- | --- | --- |
| `IE-CAND-BIO-F01-001` | `IE-V1-BIO-F01-001` | Approved with extension heterogeneity and insomnia boundaries | `INACTIVE` |
| `IE-CAND-BIO-F01-003` | `IE-V1-BIO-F01-003` | Approved only for supported adolescent education contexts | `INACTIVE` |
| `IE-CAND-BIO-F01-004` | `IE-V1-BIO-F01-004` | Modified and approved with subjective/objective measurement divergence | `INACTIVE` |
| `IE-CAND-BIO-F01-005` | `IE-V1-BIO-F01-005` | Approved with phase-response and safety boundaries | `INACTIVE` |
| `IE-CAND-BIO-F01-006` | `IE-V1-BIO-F01-006` | Approved with timing, formulation, interaction, and phase-shift boundaries | `INACTIVE` |

`IE-CAND-BIO-F01-002`, `007`, `008`, and `009` remain non-governed and
`RESEARCH_NEEDED`.

## Evidence and sources

Eleven exact EvidenceAssessment revisions supporting the six Relationships
and five InterventionEffects are governed inactive. Their IDs and lineage are
listed in `data/relationship-intervention-v1/materialization-manifest.json`.
All scientific source references resolve to either the governed v0.3 register
or the verified native V1 source register.

Twenty of the 25 supplemental audit references were needed for an approved
object or an authorized revision proposal and were verified using PubMed/NCBI
metadata before registration as `SRC-530` through `SRC-549`. No duplicate,
rejected, or unverifiable selected source was found. The other five audit
references remain unregistered because they support only research-needed,
background, or non-created pathway questions. See
[`BIO_F01_SOURCE_REGISTRATION_MANIFEST.json`](BIO_F01_SOURCE_REGISTRATION_MANIFEST.json).

## Rejection decisions

`BIOF01-D-H01` through `BIOF01-D-H05` are approved rejections: formula-induced
causal claims, the invalid cross-construct transition, and the duplicate
alignment-to-duration edge must not be regenerated as active candidates
without new evidence and a new governance decision.

## Activation decision

Activation was explicitly not authorized. The existing production-active
baseline remains 450 Relationships, including 431 causal Relationships.
