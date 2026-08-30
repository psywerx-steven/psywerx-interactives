# Cognitive Security Map Phase 1 Ingestion Report

## Release conclusion

Phase 1 passed its governed ingestion and publication-boundary gate.

This release builds the data foundation only. It does not add a public user interface.

## Source package manifest

| Artifact | Canonical role | SHA-256 |
|---|---|---|
| codebook.xlsx | canonical-cluster-codebook | `a578d408c6bbaa42b0cde5738418b86f73fa51bf75646e4462a452f12d09af1e` |
| cross_cutting_themes.xlsx | canonical-cross-cutting-themes | `cd9540c3b2b780088d64a9b463cea3773e946cad33d42641f69aafc190f2cc17` |
| drill_down.xlsx | canonical-item-cluster-assignments | `e85a038144e2ffc3ed65061490bb25e006c6205e3a88be07edd08cf706eff8df` |
| drill_up_cluster_summaries.xlsx | canonical-cluster-synthesis | `6e806e87a1f50f7ca57367865ee0148abdbde24c15b3669b96352ca1e0c5a737` |
| drill_up_meta_clusters.xlsx | canonical-meta-clusters-and-mappings | `a7b436c18f5d1a40ef664da87c5b5e9f92f145cfd76972a9947a538e9c7f0afa` |
| final_synthesis.xlsx | canonical-narratives-findings-and-scenarios | `9e1a39755fe5397f4395c1019203db80ebe0123e25fea70a4e88001eec8f4ff2` |
| master_extractions.xlsx | canonical-items-and-episode-provenance | `974aa0b8b83371681b3a921d6f2bface2befa680db1f0b68954a6c48487f4d0f` |
| tensions_debates_rebuilt.xlsx | canonical-tensions-and-debates | `60b3ce533852fda1e47afee687e7e9b5f5838c2691006e28c3477b25dea65394` |

All source files are local, ignored XLSX artifacts. Public JSON contains filenames and integrity hashes, never local paths or workbook binaries.

## Workbook and worksheet inventory

| Workbook | Worksheet | Rows | Columns |
|---|---|---:|---:|
| codebook.xlsx | Sheet1 | 128 | 8 |
| cross_cutting_themes.xlsx | Computed Cooccurrence | 1331 | 5 |
| cross_cutting_themes.xlsx | Cooccurrence Evidence | 133 | 7 |
| cross_cutting_themes.xlsx | Cross-Cutting Themes | 12 | 22 |
| cross_cutting_themes.xlsx | Representative Items | 111 | 13 |
| cross_cutting_themes.xlsx | Review Queue | 8 | 7 |
| cross_cutting_themes.xlsx | Run Summary | 16 | 2 |
| cross_cutting_themes.xlsx | Source Cluster Summaries | 128 | 11 |
| cross_cutting_themes.xlsx | Source Meta-Clusters | 37 | 19 |
| cross_cutting_themes.xlsx | Theme-to-Cluster Evidence | 303 | 9 |
| cross_cutting_themes.xlsx | Theme-to-Meta Mapping | 90 | 10 |
| drill_down.xlsx | Codebook Used | 128 | 8 |
| drill_down.xlsx | Drill Down | 10941 | 34 |
| drill_down.xlsx | Primary Frequencies | 128 | 4 |
| drill_down.xlsx | Primary-Secondary Matrix | 128 | 128 |
| drill_down.xlsx | Rep Items | 63 | 18 |
| drill_down.xlsx | Review Queue | 515 | 34 |
| drill_down.xlsx | Run Summary | 13 | 2 |
| drill_down.xlsx | Secondary Frequencies | 128 | 4 |
| drill_up_cluster_summaries.xlsx | Cluster Summaries | 128 | 15 |
| drill_up_cluster_summaries.xlsx | Codebook Used | 128 | 11 |
| drill_up_cluster_summaries.xlsx | Representative Items | 1362 | 12 |
| drill_up_cluster_summaries.xlsx | Run Summary | 2 | 12 |
| drill_up_cluster_summaries.xlsx | Theme Details | 950 | 10 |
| drill_up_meta_clusters.xlsx | Candidate Meta-Clusters | 37 | 16 |
| drill_up_meta_clusters.xlsx | Category Inputs | 8 | 7 |
| drill_up_meta_clusters.xlsx | Cluster-to-Meta Mapping | 125 | 10 |
| drill_up_meta_clusters.xlsx | Meta-Cluster Evidence | 221 | 6 |
| drill_up_meta_clusters.xlsx | Review Queue | 52 | 8 |
| drill_up_meta_clusters.xlsx | Run Summary | 8 | 9 |
| final_synthesis.xlsx | Category Findings | 43 | 12 |
| final_synthesis.xlsx | Category Summaries | 8 | 3 |
| final_synthesis.xlsx | Corpus Meta-Narratives | 8 | 14 |
| final_synthesis.xlsx | Future Scenarios | 7 | 16 |
| final_synthesis.xlsx | Review Queue | 32 | 4 |
| final_synthesis.xlsx | Run Summary | 13 | 2 |
| final_synthesis.xlsx | Scenario Actions | 31 | 2 |
| final_synthesis.xlsx | Scenario Indicators | 37 | 2 |
| final_synthesis.xlsx | Scenario Pathways | 43 | 3 |
| final_synthesis.xlsx | Source Cluster Summaries | 128 | 15 |
| final_synthesis.xlsx | Source Cross Themes | 12 | 22 |
| final_synthesis.xlsx | Source Drill Down Preview | 502 | 34 |
| final_synthesis.xlsx | Source Meta-Clusters | 37 | 16 |
| final_synthesis.xlsx | Source Tensions | 1 | 1 |
| master_extractions.xlsx | Analysis | 15 | 2 |
| master_extractions.xlsx | Challenges, Risks, Barriers | 1872 | 17 |
| master_extractions.xlsx | Codebook | 128 | 11 |
| master_extractions.xlsx | Concepts, Frameworks, Theories | 1886 | 17 |
| master_extractions.xlsx | Future Trends & Predictions | 940 | 17 |
| master_extractions.xlsx | Guest Background | 874 | 17 |
| master_extractions.xlsx | Key Events & Historical Example | 1305 | 17 |
| master_extractions.xlsx | MASTER | 14398 | 17 |
| master_extractions.xlsx | MASTER (only coded cats) | 14398 | 17 |
| master_extractions.xlsx | Memorable Quotes & Insights | 1616 | 17 |
| master_extractions.xlsx | Opportunities & Recs | 1807 | 17 |
| master_extractions.xlsx | Organizations & Actors | 1887 | 17 |
| master_extractions.xlsx | Sheet1 | 63 | 2 |
| master_extractions.xlsx | Strategic Landscape | 970 | 17 |
| master_extractions.xlsx | Tags (final) | 128 | 8 |
| master_extractions.xlsx | Tags (working) | 153 | 7 |
| master_extractions.xlsx | Tech, Tools, & Platforms | 1244 | 17 |
| master_extractions.xlsx | Working | 101 | 26 |
| tensions_debates_rebuilt.xlsx | Batch Candidates | 866 | 20 |
| tensions_debates_rebuilt.xlsx | Category Distribution | 8 | 2 |
| tensions_debates_rebuilt.xlsx | Cluster Distribution | 128 | 4 |
| tensions_debates_rebuilt.xlsx | Review Queue | 29 | 11 |
| tensions_debates_rebuilt.xlsx | Run Summary | 16 | 2 |
| tensions_debates_rebuilt.xlsx | Source Cluster Summaries | 128 | 15 |
| tensions_debates_rebuilt.xlsx | Source Cross Themes | 12 | 22 |
| tensions_debates_rebuilt.xlsx | Source Meta-Clusters | 37 | 16 |
| tensions_debates_rebuilt.xlsx | Tension Evidence | 44 | 16 |
| tensions_debates_rebuilt.xlsx | Tension Mapping | 301 | 8 |
| tensions_debates_rebuilt.xlsx | Tensions Debates | 31 | 25 |

## Expected versus actual baseline

Expected values are validation baselines, not targets that the importer forces the source to match.

| Metric | Expected | Actual | Result |
|---|---:|---:|---|
| Extracted items | 14,397 | 14,397 | PASS |
| Focal items | 10,940 | 10,940 | PASS |
| Contextual items | 3,457 | 3,457 | PASS |
| Distinct episodes/source files | 269 | 269 | PASS |
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
| `episodes` | 269 |
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

### Meta-narrative count

The canonical worksheet contains seven records (`N01`–`N07`). Earlier project documentation described eight. The build preserves seven, creates no replacement record, and reports the discrepancy for human adjudication.

### Canonical tension source

`final_synthesis.xlsx` contains a blank copied `Source Tensions` worksheet. The 30 governed tension records come from `tensions_debates_rebuilt.xlsx`.

### Unresolved theme-to-cluster evidence

Three source-authored placeholder rows for `XTHEME-007`, `XTHEME-008`, and `XTHEME-010` contain no category or cluster ID. They remain in the 302-record evidence collection with null references, portable provenance, explicit unresolved markers, and private review flags. No cluster was invented.

### Additional source observations

- Meta-cluster `CRB-M05` exists but has no rows in the cluster-to-meta mapping table.
- Category-specific worksheets omit canonical MASTER item IDs `14368`–`14373`; the build uses `MASTER` and retains all six.
- Drill-down and current MASTER confidence values differ for 4,229 focal items. Item confidence remains canonical from MASTER, while coding confidence is preserved separately on assignments.
- All 865 Batch Candidate rows have blank `batch_id` but populated `source_batch_id`; explicit candidate/source identifiers are retained through tension lineage where referenced.

## Validation

- Structural errors: 0
- Warnings/review findings: 7
- Deterministic in-memory serialization: PASS
- Public files generated: 15

Warnings and review findings:

- explicit_unresolved_reference: theme_cluster_evidence.cluster_id is unresolved in the source and was preserved without invention. ({"collection": "theme_cluster_evidence", "field": "cluster_id", "governance_known": false, "row": 34, "status": "explicitly-unresolved-source-reference"})
- explicit_unresolved_reference: theme_cluster_evidence.cluster_id is unresolved in the source and was preserved without invention. ({"collection": "theme_cluster_evidence", "field": "cluster_id", "governance_known": false, "row": 154, "status": "explicitly-unresolved-source-reference"})
- explicit_unresolved_reference: theme_cluster_evidence.cluster_id is unresolved in the source and was preserved without invention. ({"collection": "theme_cluster_evidence", "field": "cluster_id", "governance_known": false, "row": 183, "status": "explicitly-unresolved-source-reference"})
- known_unmapped_cluster: Intermediate cluster has no meta-cluster assignment. ({"cluster_id": "CRB-10", "cluster_name": "Forecasting, Complexity & Uncertainty", "governance_known": true})
- known_unmapped_cluster: Intermediate cluster has no meta-cluster assignment. ({"cluster_id": "FTP-13", "cluster_name": "Societal Transformation, Identity, & Social Cohesion", "governance_known": true})
- known_unmapped_cluster: Intermediate cluster has no meta-cluster assignment. ({"cluster_id": "KCFT-20", "cluster_name": "Strategic Culture & Ideological Competition", "governance_known": true})
- known_meta_narrative_count_mismatch: Source contains seven meta-narratives (N01-N07); prior project documentation expected eight. ({"actual": 7, "expected": 8})

## Generated public-file hashes

| File | SHA-256 |
|---|---|
| `categories.json` | `b4abc976ad5d4674e5f5f176ce7e7a107225fff3540d30e65b76c7af4a732220` |
| `category_findings.json` | `f36ba877492faf91a76af198a9b9b1c6b5805cc8fde7b47e15baeba1f8a02e31` |
| `cluster_summaries.json` | `a4ecc3640c647f3f7bfb48cbcd48f738dcb5aeed39b7be54a6ac634ff7414dc3` |
| `clusters.json` | `8267f35b49000502477f3bad4f172caef726c456a5ff3e0abbece8b22f812095` |
| `coverage.json` | `127238b85efd14ffd45bf708f38a143b455c25e9233800725c65b0112dd09dac` |
| `episodes.json` | `47139afb4c8f306c7eb5ea6f9af07e9ae9f9eb355ea75ce6e8cbdadb77f80ba3` |
| `manifest.json` | `65fcc230cf2bf6a9fc8fe8d677731337a635cd58d2747dc54e3ab038aa3282db` |
| `meta_clusters.json` | `49b668c65fbc7706be5455d2ce46696e66dc1be299d3f475ce441ecdf2ad81f9` |
| `meta_narratives.json` | `d93f8ea23d78cf892bb3031a17aa2caf6ad38d87dea42df648a56d5bb20e3be4` |
| `qa_report.json` | `89b168f88b6634dd2239a0e67b82855f3f5d2a345a7421ae5d62650fdf9f0e9f` |
| `relationships.json` | `d8d58595c4517061d3ea70d0cb8c926ea8ae9e51a2f5516b9502d2abaa3c7c83` |
| `review_summary.json` | `c3cad6f0951696bf979d137e798ae9086484168b7250933f5c47e694e24c7c4c` |
| `scenarios.json` | `f2996cdbed109d617b0acb58b84e41e37cf0b0b73be6fd371d32ecc20f3931d6` |
| `tensions.json` | `0de9d67bc58c46fbb09b6728efef2a1c9760f8227464bb061446a84f1b724447` |
| `themes.json` | `bbd5539e57c6e9b9f16e398b13a7c40e4bfa6b321a51adec783cd6f349a6bb5c` |

## Public/private boundary

Public export uses positive field allowlists. It includes governed high-level entities, semantic mappings, aggregate coverage, source integrity hashes, and aggregate QA. It excludes item text, evidence quotations, detailed rationales, internal notes, detailed review queues, hidden source metadata, and all workbook content blobs.

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

Phase 1 does not adjudicate source review queues, infer causal relationships, publish evidence excerpts, or implement the explorer interface. Those are intentionally deferred to governed follow-on phases.
