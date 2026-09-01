# Cognitive Security Map Schema v1.1 Ingestion Report

## Release conclusion

Schema v1.1 passed its governed ingestion, reconciliation, sensitivity, and publication-boundary gate.

This release preserves the historical analytical dataset while adding a canonical public-feed episode model and a separate reconciled sensitivity dataset.

## Source package inventory

| Opaque artifact ID | Canonical role | Integrity verified |
|---|---|---|
| `ART-cluster-summaries` | canonical-cluster-synthesis | yes |
| `ART-codebook` | canonical-cluster-codebook | yes |
| `ART-cross-cutting-themes` | canonical-cross-cutting-themes | yes |
| `ART-drill-down` | canonical-item-cluster-assignments | yes |
| `ART-final-synthesis` | canonical-narratives-findings-and-scenarios | yes |
| `ART-master-extractions` | canonical-items-and-episode-provenance | yes |
| `ART-meta-clusters` | canonical-meta-clusters-and-mappings | yes |
| `ART-tensions` | canonical-tensions-and-debates | yes |

Exact source-workbook filenames, integrity hashes, and row-level provenance remain in the ignored private normalized release. Public products identify sources only by opaque artifact ID and publish safe aggregate QA.

## Aggregate source inventory

| Opaque artifact ID | Worksheets | Aggregate rows |
|---|---:|---:|
| `ART-cluster-summaries` | 5 | 2570 |
| `ART-codebook` | 1 | 128 |
| `ART-cross-cutting-themes` | 10 | 2169 |
| `ART-drill-down` | 8 | 12044 |
| `ART-final-synthesis` | 14 | 902 |
| `ART-master-extractions` | 18 | 43785 |
| `ART-meta-clusters` | 6 | 451 |
| `ART-tensions` | 11 | 1600 |

## Expected versus actual baseline

Expected values are validation baselines, not targets that the importer forces the source to match.

| Metric | Expected | Actual | Result |
|---|---:|---:|---|
| Extracted items | 14,397 | 14,397 | PASS |
| Focal items | 10,940 | 10,940 | PASS |
| Contextual items | 3,457 | 3,457 | PASS |
| Canonical public feed episodes | 242 | 242 | PASS |
| Historical transcript/source identities | 269 | 269 | PASS |
| Reconciled sensitivity items | 12,978 | 12,978 | PASS |
| Reconciled sensitivity focal items | 9,855 | 9,855 | PASS |
| Reconciled sensitivity contextual items | 3,123 | 3,123 | PASS |
| Intermediate clusters | 127 | 127 | PASS |
| Primary focal-item assignments | 10,940 | 10,940 | PASS |
| Substantive secondary assignments | 10,524 | 10,524 | PASS |
| Secondary NONE rows | 416 | 416 | PASS |
| Review-required assignments | 514 | 514 | PASS |
| Ambiguity-flagged assignments | 158 | 158 | PASS |
| Meta-clusters | 36 | 36 | PASS |
| Cluster-to-meta mappings | 124 | 124 | PASS |
| Cross-cutting themes | 11 | 11 | PASS |
| Theme-to-meta mappings | 89 | 89 | PASS |
| Theme-to-cluster evidence rows | 302 | 302 | PASS |
| Tensions/debates | 30 | 30 | PASS |
| Meta-narratives in current source | 7 | 7 | PASS |
| Future scenarios | 6 | 6 | PASS |

## Corpus reconciliation

The historical extraction contains 269 transcript/source identities. Forensic review supports 27 confirmed alias groups and 242 distinct public feed releases. The 242 count is a publication-unit count, not a unique-recording count: the episode 83 re-release is retained as a separate feed release while its content reuse remains privately flagged.

The original 14,397 extracted items remain unchanged. The separate reconciled sensitivity dataset selects one canonical source identity per confirmed feed-release episode and contains 12,978 items (9,855 focal and 3,123 contextual). It is not a corrected replacement for the historical analytical release.

The 27 confirmed groups are the legacy/modern episode-number pairs 2-27 plus the Brown Bag precursor to edited public episode 186. No likely, ambiguous, or unresolved mapping remains under the governed public-feed-release definition.

## Normalized entity counts

| Collection | Records |
|---|---:|
| `artifacts` | 8 |
| `categories` | 10 |
| `category_findings` | 42 |
| `category_summaries` | 7 |
| `cluster_meta_mappings` | 124 |
| `cluster_summaries` | 127 |
| `clusters` | 127 |
| `episode_reconciliation_flags` | 2 |
| `episode_source_identities` | 269 |
| `episode_source_mappings` | 269 |
| `episodes` | 242 |
| `evidence_links` | 12,606 |
| `item_cluster_assignments` | 10,940 |
| `item_tags` | 52,458 |
| `items` | 14,397 |
| `meta_clusters` | 36 |
| `meta_narratives` | 7 |
| `review_flags` | 860 |
| `scenario_actions` | 30 |
| `scenario_indicators` | 36 |
| `scenario_pathways` | 42 |
| `scenarios` | 6 |
| `tension_mappings` | 300 |
| `tensions` | 30 |
| `theme_cluster_evidence` | 302 |
| `theme_meta_mappings` | 89 |
| `themes` | 11 |

## Governance discrepancies retained

### Unmapped intermediate clusters

The following clusters are preserved without invented meta-cluster assignments:

- `CRB-10` — Forecasting, Complexity & Uncertainty
- `FTP-13` — Societal Transformation, Identity, & Social Cohesion
- `KCFT-20` — Strategic Culture & Ideological Competition

### Meta-clusters with no source membership rows

The following governed meta-clusters are retained without invented cluster membership:

- `CRB-M05` — Strategic asymmetry and contested operating conditions

### Meta-narrative count

The canonical worksheet contains seven records (`N01`–`N07`). Earlier project documentation described eight. The build preserves seven, creates no replacement record, and reports the discrepancy for human adjudication.

### Canonical tension source

Opaque artifact `ART-final-synthesis` contains a blank copied source-tension table. The 30 governed tension records come from `ART-tensions`.

### Unresolved theme-to-cluster evidence

Three source-authored placeholder rows for `XTHEME-007`, `XTHEME-008`, and `XTHEME-010` contain no category or cluster ID. They remain in the 302-record evidence collection with null references, portable provenance, explicit unresolved markers, and private review flags. No cluster was invented.

### Additional source observations

- Meta-cluster `CRB-M05` exists but has no rows in the cluster-to-meta mapping table.
- Category-specific worksheets omit canonical MASTER item IDs `14368`–`14373`; the build uses `MASTER` and retains all six.
- Drill-down and current MASTER confidence values differ for 4,229 focal items. Item confidence remains canonical from MASTER, while coding confidence is preserved separately on assignments.
- All 865 Batch Candidate rows have blank `batch_id` but populated `source_batch_id`; explicit candidate/source identifiers are retained through tension lineage where referenced.

## Validation

- Structural errors: 0
- Warnings/review findings: 8
- Deterministic in-memory serialization: PASS
- Public files generated: 18

Warnings and review findings:

- explicit_unresolved_reference: theme_cluster_evidence.cluster_id is unresolved in the source and was preserved without invention. ({"collection": "theme_cluster_evidence", "field": "cluster_id", "governance_known": false, "row": 34, "status": "explicitly-unresolved-source-reference"})
- explicit_unresolved_reference: theme_cluster_evidence.cluster_id is unresolved in the source and was preserved without invention. ({"collection": "theme_cluster_evidence", "field": "cluster_id", "governance_known": false, "row": 154, "status": "explicitly-unresolved-source-reference"})
- explicit_unresolved_reference: theme_cluster_evidence.cluster_id is unresolved in the source and was preserved without invention. ({"collection": "theme_cluster_evidence", "field": "cluster_id", "governance_known": false, "row": 183, "status": "explicitly-unresolved-source-reference"})
- known_unmapped_cluster: Intermediate cluster has no meta-cluster assignment. ({"cluster_id": "CRB-10", "cluster_name": "Forecasting, Complexity & Uncertainty", "governance_known": true})
- known_unmapped_cluster: Intermediate cluster has no meta-cluster assignment. ({"cluster_id": "FTP-13", "cluster_name": "Societal Transformation, Identity, & Social Cohesion", "governance_known": true})
- known_unmapped_cluster: Intermediate cluster has no meta-cluster assignment. ({"cluster_id": "KCFT-20", "cluster_name": "Strategic Culture & Ideological Competition", "governance_known": true})
- known_empty_meta_cluster: Meta-cluster has no source cluster-mapping rows; membership was not invented. ({"entity_type": "meta_cluster", "governance_known": true, "governance_note": "Strategic synthesis lens without source cluster-mapping rows", "meta_cluster_id": "CRB-M05", "meta_cluster_name": "Strategic asymmetry and contested operating conditions"})
- known_meta_narrative_count_mismatch: Source contains seven meta-narratives (N01-N07); prior project documentation expected eight. ({"actual": 7, "expected": 8})

## Generated public-file hashes

| File | SHA-256 |
|---|---|
| `categories.json` | `b4abc976ad5d4674e5f5f176ce7e7a107225fff3540d30e65b76c7af4a732220` |
| `category_findings.json` | `f36ba877492faf91a76af198a9b9b1c6b5805cc8fde7b47e15baeba1f8a02e31` |
| `cluster_summaries.json` | `a4ecc3640c647f3f7bfb48cbcd48f738dcb5aeed39b7be54a6ac634ff7414dc3` |
| `clusters.json` | `8267f35b49000502477f3bad4f172caef726c456a5ff3e0abbece8b22f812095` |
| `corpus_reconciliation.json` | `b183c0dc2cbee7974f6576835e466159f2105a3e23a5e5c754b29678562ec5cc` |
| `coverage.json` | `3303e346d16ac4cfeee65bce2f221f75bdbb06d9e6d26847307ab206cbe8543e` |
| `episode_relationships.json` | `6c6542a276dfae5a5566408ebce3c80631047a14cd7f393e357e3a3e8fc97487` |
| `episode_summaries.json` | `b157e9539bed0aa37ceea2db0952c8b52e887928e4c3419077e1e9f23ec39583` |
| `episodes.json` | `7483f14da002c0f561bcb4913681f8dcde0d5cfa0630c0ab6995a99c598b4da1` |
| `manifest.json` | `7005f4d56d83a8f69c576a5e00b686f87a7a94dc5c6ce86e55c2a23cf73356ab` |
| `meta_clusters.json` | `49b668c65fbc7706be5455d2ce46696e66dc1be299d3f475ce441ecdf2ad81f9` |
| `meta_narratives.json` | `d93f8ea23d78cf892bb3031a17aa2caf6ad38d87dea42df648a56d5bb20e3be4` |
| `qa_report.json` | `248883d1c049b7e0ad6a226d0b1ddb50410dd4e0128a71ed93582c2b4ede7c11` |
| `relationships.json` | `5cc83e56457d274139511d2efa83079fc00aea48d2d7ab62cb882c5fef350714` |
| `review_summary.json` | `a36853f154200f8e91efbaf460f2b9490c24d171aa6650df1d0547c1d93cfa26` |
| `scenarios.json` | `f2996cdbed109d617b0acb58b84e41e37cf0b0b73be6fd371d32ecc20f3931d6` |
| `tensions.json` | `0de9d67bc58c46fbb09b6728efef2a1c9760f8227464bb061446a84f1b724447` |
| `themes.json` | `bbd5539e57c6e9b9f16e398b13a7c40e4bfa6b321a51adec783cd6f349a6bb5c` |

## Public/private boundary

Public export uses positive field allowlists. It includes governed high-level entities, semantic mappings, aggregate coverage, opaque source artifact IDs, and safe aggregate QA. It excludes source-workbook filenames and fingerprints, item text, evidence quotations, detailed rationales, internal notes, detailed review queues, hidden source metadata, and all workbook content blobs.

The complete normalized QA layer—including item records, evidence excerpts, rationales, ambiguity details, and review flags—is written only to ignored `analysis/cognitive-security/normalized/`.

## Methodology cautions

- This is a practitioner-discourse map, not a definitive taxonomy.
- Counts indicate corpus discourse salience, not objective importance, prevalence, scientific support, or consensus.
- Extracted items are interpretive units, not independent statistical observations.
- Primary assignment represents dominant analytic meaning.
- Secondary assignment represents substantive conceptual adjacency.
- Primary-secondary co-occurrence is semantic, not causal.
- Discourse clusters are not automatically PSYWERX behavioral Drivers.
- A meta-cluster is a within-category family.
- A cross-cutting theme connects patterns across categories.
- A tension is an unresolved tradeoff, disagreement, or competing assumption.
- A meta-narrative is a high-level interpretive storyline.
- Scenarios are plausibility exercises, not forecasts.
- Model coding confidence is not scientific evidence strength.
- Frequency is not consensus.
- Higher-order synthesis remains traceable to lower-level source IDs where the source supports the relationship.

## Recommended human adjudications

1. Decide whether and where to map `CRB-10`, `FTP-13`, and `KCFT-20` within the meta-cluster layer.
2. Reconcile the prior eight-narrative expectation with the seven canonical source records.
3. Establish an explicit evidence and quotation publication allowlist before any evidence-browser release.
4. Review speaker attribution and episode-link publication rules before Phase 3 evidence browsing.

## Known limitations

The reconciliation audit does not regenerate higher-order synthesis, infer causal relationships, or publish private evidence. Support sensitivity describes traceable coverage after alias-source exclusion; it is not a validity judgment.
