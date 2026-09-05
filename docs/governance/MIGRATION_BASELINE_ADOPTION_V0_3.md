# PSYWERX Migration Baseline Adoption V0.3

**Decision ID:** `MIGRATION_BASELINE_ADOPTION_V0_3-2026-09-05`

**Decision date / effective date:** 2026-09-05

**Authority:** Authorized human governor

**Source authorization:** The explicit human governance instruction authorizing
the separate v0.3 migration-baseline adoption after PR #11, supplied on
2026-09-05

**Status:** Governed migration specification and generated baseline

## Exact adopted baseline

This decision adopts the following exact, reproducible migration history:

| Element | Governed value |
| --- | --- |
| Frozen pre-migration baseline commit | `580d59c451765e9f4d65b517f538a495fa93bda5` |
| Governed migration pull request | `#9` |
| Final migration branch/head used by PR #9 | `ad727cafbb3d970e269848662612c6f638c14cd1` |
| Merge commit placing v0.3 on `main` | `6cf34a029a9dc6e099628e86dfb9f42b53bd8d13` |
| Effective baseline commit | `6cf34a029a9dc6e099628e86dfb9f42b53bd8d13` |
| Pre-adoption manifest SHA-256 | `7def0e756b2e8049ad909c9837e0f72ac3be4a9eac66489f418472deee7430f1` |
| Pre-adoption generator SHA-256 | `cfacc17d0a5eaaa4a25c1314e901cd80d64374bf75f84d92de4291d0643749b1` |
| Pre-adoption seed SHA-256 | `0608bc1f1e855f312ed39310193dc5722a84c203cf7b5a6b462a1a31e559253a` |

The hashes above and below were obtained mechanically from the
`migration-manifest.json` present on `main` before this authority-only change.
The seed and generator hashes necessarily change when authority metadata and
tests are materialized; the generated scientific artifact hashes must not.

### Frozen pre-migration artifact hashes

| Artifact | SHA-256 |
| --- | --- |
| `codebook.json` | `4dd0ffe790b2b08180777d7ef0ca681eda1e7f72ce1d8e7fc8304a8aad131508` |
| `drivers.json` | `55fcd27e7a45218721dbe02efda518f77ed4d53c54031f5b8aeea3c0433b3c8f` |
| `families.json` | `ac81d446dc664497104a6ef3e23f0768eaf3aa632dab57c970edaab7df7dfc7c` |
| `plain_language.json` | `7d042a2dd3dd2994eec50b9cc97e9200265177194e40030223888bdcaebd8743` |
| `relationships.json` | `27c6ebcfdeb481d2577e823792204dc74d05e1b894d397aa5417fb99ebc431db` |
| `sources.json` | `f1aae4135ac049e223ae65a66a24a6dfc2c28e911add59ce11df34e9c0af3615` |

### Pre-adoption governed migration-input hashes

| Artifact | SHA-256 |
| --- | --- |
| `_migration_handoff_v0.3/CODEX_START_PROMPT.md` | `d2acc643c805e00e66174f60cff6b632ee7842a53c18c6bed289bafa83a38563` |
| `_migration_handoff_v0.3/GOVERNANCE_SOURCE_INDEX.md` | `b4b05f07daae9b02391c15426496c5e483d63fd7cfdf5f679a17c523315771c5` |
| `_migration_handoff_v0.3/MIGRATION_DECISIONS_SUMMARY.md` | `8c7c3622bd387189b872f67aeb21a30db1bc2e2d65d2aabffea5cf5e7188bc8d` |
| `_migration_handoff_v0.3/RDS_POSITIVE_CONTROL_CALIBRATION.md` | `883ca0d0fac0dff866a8246741b0d93391b246cf7a812a95771e4998ee148454` |
| `_migration_handoff_v0.3/README_CODEX_HANDOFF.md` | `bf8427460cbf75b842711dc7887bce42c6c617354b76bf5da50b04b06d262d16` |
| `_migration_handoff_v0.3/SECONDARY_BOUNDARY_AUDIT_ADDENDUM.md` | `b1f87266394d316efa3a51b5112c688334265dc73eb87e65071d976a6a3f3fff` |
| `_migration_handoff_v0.3/VALIDATION_CHECKLIST.md` | `4e08d998d63e8feae9ed444955e6f9ecbb209c52b74bbf9b4d609e8781674592` |
| `_migration_handoff_v0.3/migration_manifest_seed.json` | `0608bc1f1e855f312ed39310193dc5722a84c203cf7b5a6b462a1a31e559253a` |

### Adopted generated scientific artifact hashes

| Artifact | SHA-256 |
| --- | --- |
| `aliases.json` | `e14f9ba67d51d4f0a18cc05ad029da08f7d206dda1c636fbbd866b16ed1b7fb9` |
| `crosswalks.json` | `8583159cbdd9bc00cc912e367a53515511709ef7796119ecfa10d0145f1ad7c5` |
| `drivers.json` | `017a79d1f33230e788fe82175d74714f28e7e0af18878fa718c971a0e101534b` |
| `entities.json` | `74f88110911280bc6d508da56af824b63db4c11d741223b694aa7ac18734cf99` |
| `families.json` | `8fc4b3f08de1b27850fb460d528c3d95a6d9ea858bb1e55ca687722af80d7f9d` |
| `relational-derived-states.json` | `126ee66cfed4833603376bec5e0eb4da39f37eec8605480c82ebada70641d333` |
| `relationships.json` | `759f90446ff5f6e27d496e3e3603bb44045f7f0abf4770e4c012c5e4d974ba51` |

## Authority granted

The exact v0.3 handoff specification is adopted as:

`GOVERNED_MIGRATION_SPECIFICATION`

The generated deterministic v0.3 Driver/RDS baseline is adopted as:

`GOVERNED_MIGRATION_BASELINE`

This adoption governs:

- the approved 34 existing Driver IDs retyped to RDS;
- the resulting partition of 770 Drivers, 41 RDS, and 811 canonical entities;
- the deterministic generated artifacts representing those decisions; and
- use of that partition as the starting ontology/entity baseline for later,
  separately governed V1 work.

This baseline adoption does not:

- upgrade, re-review, or alter a scientific Relationship;
- invent missing scientific metadata;
- approve a candidate Relationship;
- convert every scientific record to `GOVERNED + ACTIVE`;
- resolve any deferred ontology or migration item;
- authorize V1 relationship/intervention population, Family auditing,
  application behavior changes, or deployment.

Record-level scientific governance remains separate under D11–D12 of the
[Relationship + Intervention Architecture V1 decision](RELATIONSHIP_INTERVENTION_V1_GOVERNANCE_DECISION.md).

## Open governance items retained

The adoption explicitly retains these items without adjudication:

1. `INS-102`
2. `REL-SOC-028`
3. `REL-TEC-049`
4. `REL-MIG-CAND-0001`
5. `REL-MIG-CAND-0002`
6. `REL-MIG-CAND-0003`
7. `NEW-ENTITIES-V0.3`

They remain represented by `openGovernanceItems` and their existing detailed
`blockedItems` records in the generated manifest. Baseline adoption cannot
remove, reorder, reinterpret, or resolve them.

## Materialization rule

The authority metadata is generated from the protected seed rather than
manually edited into `data/migration-manifest.json`. The generated manifest
must contain:

- `status: GOVERNED_MIGRATION_BASELINE`;
- `specificationStatus: GOVERNED_MIGRATION_SPECIFICATION`;
- `authorityDecisionRecord: docs/governance/MIGRATION_BASELINE_ADOPTION_V0_3.md`;
- `effectiveCommit: 6cf34a029a9dc6e099628e86dfb9f42b53bd8d13`;
- `effectiveDate: 2026-09-05`; and
- the seven exact `openGovernanceItems` above.

The historical script filename and historical `previewCounts` compatibility
field may remain. They do not weaken the governed authority fields. Generated
scientific artifacts must remain byte-identical to their adopted hashes.

## Future gate

This decision adopts the v0.3 migration baseline only. Relationship +
Intervention Architecture V1 production implementation and population remain
unauthorized.
