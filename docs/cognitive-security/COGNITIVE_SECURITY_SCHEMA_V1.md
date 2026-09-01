# PSYWERX Cognitive Security Map Schema v1.0

**Status:** Governed Phase 1 normalized-data contract
**Product:** PSYWERX Cognitive Security Practitioner Discourse Map
**Scope:** Source ingestion, normalized internal data, provenance, validation,
and conservative public export. This schema does not define a Driver Ontology
extension and does not define the future Explorer UI.

The product maps practitioner discourse in the supplied podcast corpus. Its
clusters, themes, tensions, narratives, and scenarios are interpretive
structures. They are not behavioral Drivers, causal claims, prevalence
estimates, scientific evidence-strength judgments, or consensus measures.

## Serialization conventions

- Collection names are the exact snake-case top-level names documented below.
- Record fields are camelCase.
- Explicit source IDs are trimmed and otherwise preserved. They are never
  replaced by generated IDs.
- An absent scalar is `null`; an absent list is `[]`.
- Source whitespace is collapsed and empty cells become `null` during
  extraction. Meaningful case, punctuation, and wording are retained.
- Generated IDs use `PREFIX-` plus the first 16 uppercase hexadecimal
  characters of SHA-256 over the normalized semantic identity. Unicode is
  NFKC-normalized, whitespace is collapsed, and case is folded; punctuation is
  retained to avoid collapsing punctuation-distinct labels. Row numbers,
  random UUIDs, and wall-clock time are never identity inputs.
- Lists preserve first-seen source order unless the field is explicitly an ID
  set. Entity collections are deterministically sorted by stable ID.
- Source-authored run IDs and coding timestamps may exist in the private
  normalized layer. They are provenance values, not build timestamps.

### Provenance object

Most records carry one `source` object:

```json
{
  "artifactId": "ART-master-extractions",
  "fileName": "master_extractions.xlsx",
  "sheet": "MASTER",
  "rowNumber": 2
}
```

Merged evidence and review records carry `sources`, an ordered array of the
same objects. Only workbook basenames are retained. Absolute paths, desktop
locations, and Run Summary path cells are excluded.

## Collection registry

| Collection | Primary key | Principal foreign keys | Current records | Publication class |
| --- | --- | --- | ---: | --- |
| `artifacts` | `artifactId` | None | 8 | Internal manifest; public release exposes opaque IDs and canonical roles only |
| `episodes` | `episodeId` | Provenance to artifact | 269 | Public subset |
| `items` | `itemId` | `episodeId`, `categoryId` | 14,397 | Private/internal |
| `item_tags` | `itemTagId` | `itemId` | 52,458 | Private/internal |
| `categories` | `categoryId` | None | 10 | Public subset |
| `clusters` | `clusterId` | `categoryId` | 127 | Public subset |
| `item_cluster_assignments` | `assignmentId` | `itemId`, `primaryClusterId`, `secondaryClusterId` | 10,940 | Private/internal |
| `cluster_summaries` | `clusterSummaryId` | `clusterId`, `categoryId` | 127 | Public subset |
| `meta_clusters` | `metaClusterId` | `categoryId`, included cluster/item IDs | 36 | Public subset |
| `cluster_meta_mappings` | `clusterMetaMappingId` | `clusterId`, `metaClusterId` | 124 | Public semantic relationship |
| `themes` | `themeId` | category, meta-cluster, cluster, tension, and item ID lists | 11 | Public subset |
| `theme_meta_mappings` | `themeMetaMappingId` | `themeId`, `metaClusterId`, `categoryId` | 89 | Public semantic relationship |
| `theme_cluster_evidence` | `themeClusterEvidenceId` | `themeId`, nullable `clusterId`, `categoryId` | 302 | Public semantic relationship |
| `tensions` | `tensionId` | category, cluster, and item ID lists | 30 | Public subset |
| `tension_mappings` | `tensionMappingId` | `tensionId`, polymorphic `mappedId` | 300 | Public semantic relationship |
| `meta_narratives` | `narrativeId` | theme, tension, meta-cluster, and category ID lists | 7 | Public subset |
| `category_summaries` | `categorySummaryId` | `categoryId` | 7 | Internal normalized synthesis |
| `category_findings` | `findingId` | `categoryId`, meta-cluster and cluster ID lists | 42 | Public subset |
| `scenarios` | `scenarioId` | category, theme, and tension ID lists | 6 | Public subset |
| `scenario_pathways` | `pathwayId` | `scenarioId` | 42 | Nested into public scenarios |
| `scenario_indicators` | `indicatorId` | `scenarioId` | 36 | Nested into public scenarios |
| `scenario_actions` | `actionId` | `scenarioId` | 30 | Nested into public scenarios |
| `evidence_links` | `evidenceLinkId` | polymorphic source and target IDs | 12,606 | Private/internal |
| `review_flags` | `reviewFlagId` | polymorphic `entityId` | 860 | Private; public aggregates only |

Counts describe the current source package and are validation comparisons, not
hard-coded coercion targets.

## Exact normalized record shapes

Notation: `?` means nullable, `[]` means an array, and `source`/`sources` use
the provenance shape above.

### Source, corpus, and taxonomy

`artifacts`

- `artifactId: string` — stable package identifier.
- `fileName: string`, `sha256: string`, `byteSize: integer`.
- `sheets: object[]` — each has `name`, `rowCount`, `columnCount`, nullable
  `headerRow`, `headers`, and nullable `canonicalTable`.

`episodes`

- `episodeId: string` — deterministic from `sourceFile`, falling back to
  podcast plus title only if the source file is absent.
- `podcast: string?`, `episodeTitle: string?`, `sourceFile: string?`.
- `itemCount`, `focalItemCount`, `contextualItemCount: integer`.
- `source: provenance`.

`items`

- `itemId: string` — explicit `MASTER.ID`, canonical and globally unique.
- `episodeId: string`, `categoryId: string`, `categoryName: string`.
- `scope: "focal" | "contextual"`.
- `item`, `summary`, `strategicSignificance`, `operationalImplications`,
  `evidenceExcerpt`, `speaker`, `confidence`, `timeHorizon: string?`.
- `episodeRelevanceScore`, `noveltyScore`, `actionabilityScore: number?`.
- `source: provenance`.

`item_tags`

- `itemTagId: string` — deterministic from item ID and source tag.
- `itemId: string`, `tag: string`, `normalizedTag: string`.
- `source: provenance`.

`categories`

- `categoryId: string` — deterministic from category name.
- `name: string`, `scope: "focal" | "contextual"`.
- `itemCount`, `clusterCount: integer`.
- `source: provenance`.

`clusters`

- `clusterId: string` — explicit Codebook `ID`.
- `categoryId: string`, `categoryName: string`, `name: string`.
- `definition`, `inclusionCriteria`, `exclusionCriteria`,
  `nearNeighborDistinctions: string?`.
- `anchorExamples: string[]`.
- `source: provenance`.

### Coding and cluster synthesis

`item_cluster_assignments`

- `assignmentId: string` — deterministic from item, primary cluster, and
  nullable secondary cluster.
- `itemId`, `categoryId`, `primaryClusterId: string`.
- `primaryClusterName`, `primaryRationale: string?`.
- `secondaryClusterId`, `secondaryClusterName`,
  `secondaryRationale: string?`; source `NONE` becomes `null`.
- `secondaryIsNone: boolean` — preserves the explicit source sentinel.
- `confidence: string?` — drill-down coding confidence, distinct from the
  canonical item's extraction confidence.
- `ambiguityFlag: boolean`, `ambiguityType: string?`,
  `alternativeClusterIds: string[]`, `alternativeClusterNames: string[]`.
- `reviewRequired: boolean`, `reviewReason: string?`.
- `coder`, `model`, `promptVersion`, `codebookVersion`,
  `codedTimestamp: string?`.
- `source: provenance`.

`cluster_summaries`

- `clusterSummaryId: string`, `clusterId: string`, `categoryId: string`,
  `clusterName: string`.
- `primaryCount`, `secondaryCount: integer`; `weightedCount: number`.
- `summary`, `strategicSignificance`, `operationalImplications`,
  `primarySecondaryDistinction`, `edgeCasesOrAmbiguities: string?`.
- `representativeItemIds: string[]`,
  `candidateMetaClusterAffinities: string[]`, `reviewQuestions: string[]`.
- `summaryConfidence: string?`, `keyThemes: string[]`.
- `recurringThemes: object[]`; each object contains `clusterThemeId`,
  `themeNumber`, `name`, `description`, `evidenceItemIds`,
  support-count estimates, `importance`, and `source`.
- `source: provenance`.

### Meta-clusters and cross-cutting themes

`meta_clusters`

- `metaClusterId: string` — explicit source ID.
- `categoryId`, `categoryName`, `name`, `definition: string`.
- `includedClusterIds`, `includedClusterNames`,
  `representativeItemIds: string[]`.
- `rationale`, `nearNeighborDistinctions`, `categorySynthesis: string?`.
- `salience`, `reviewPriority`, `reviewStatus`, `humanNotes`,
  `runId`, `promptVersion: string?`.
- `source: provenance`.

`cluster_meta_mappings`

- `clusterMetaMappingId: string`, `clusterId: string`,
  `metaClusterId: string`, `categoryId: string`.
- `mappingType`, `mappingRationale`, `reviewStatus`, `humanNotes`,
  `runId: string?`.
- `source: provenance`.

`themes`

- `themeId: string` — explicit source ID; `name`, `definition: string`.
- `categoryNames`, `categoryIds: string[]`; `categoryCount: integer`.
- `linkedMetaClusterIds`, `linkedMetaClusterNames`, `linkedClusterIds`,
  `linkedClusterNames: string[]`.
- `crossCategoryLogic`, `cooccurrenceEvidence`, `strategicSignificance`,
  `operationalImplications`, `boundaryConditions: string?`.
- `relatedTensionNames: string[]` preserves source debate labels;
  `relatedTensionIds: string[]` is derived from either an exact
  whitespace-normalized, case-insensitive match to a canonical tension name or
  an explicit `cross_cutting_theme` tension mapping. Similar wording is never
  treated as a match.
- `representativeItemIds: string[]`, `evidenceStrength`, `reviewPriority`,
  `reviewNotes`, `humanReviewStatus`, `humanThemeName`, `humanNotes: string?`,
  `reviewRequired: boolean`.
- `source: provenance`.

`theme_meta_mappings`

- `themeMetaMappingId`, `themeId`, `metaClusterId`, `categoryId: string`.
- `mappingBasis`, `humanReviewStatus`, `humanNotes: string?`.
- `source: provenance`.

`theme_cluster_evidence`

- `themeClusterEvidenceId`, `themeId: string`.
- `clusterId`, `categoryId: string?`.
- `unresolvedReference: boolean`; `true` only for an explicit source
  placeholder with no cluster ID.
- `clusterSummary`, `strategicSignificance`, `operationalImplications`,
  `evidenceNote: string?`.
- `source: provenance`.

### Tensions and higher synthesis

`tensions`

- `tensionId: string` — explicit source ID; `name`, `description: string`.
- `poleALabel`, `poleBLabel`, `poleAAssumption`, `poleBAssumption: string`.
- `tensionLevel: string`.
- `categoryNames`, `categoryIds`, `clusterNames`, `clusterIds: string[]`;
  `categoryCount`, `clusterCount: integer`.
- `supportingItemIdsPoleA`, `supportingItemIdsPoleB`,
  `sourceCandidateIds`, `keyTerms: string[]`; `candidateCount: integer`.
- `evidenceStrength`, `confidence`, `reviewPriority`, `evidenceRationale`,
  `selectionMethod`, `humanReviewStatus`, `humanNotes: string?`,
  `reviewRequired: boolean`.
- `source: provenance`.

`tension_mappings`

- `tensionMappingId`, `tensionId: string`.
- `mappedEntityType: "cross_cutting_theme" | "meta_cluster"`.
- `mappedId`, `mappedName: string`, `mappingStrength: number?`.
- `mappingBasis`, `reviewStatus`, `humanNotes: string?`.
- `source: provenance`.

`meta_narratives`

- `narrativeId: string` — explicit source ID; `name`, `shortVersion`,
  `coreClaim: string`.
- `supportingThemeIds`, `supportingTensionIds`,
  `supportingMetaClusterIds`, `categoryNames`, `categoryIds: string[]`.
- `supportingTensionNames: string[]` preserves unresolved source labels.
- `representativeEvidence`, `strategicSignificance`, `caveats: string?`.
- `operationalImplications: string[]`, `confidence: string`,
  `reviewRequired: boolean`.
- `source: provenance`.

`category_summaries`

- `categorySummaryId: string`, `categoryId: string`,
  `categoryName: string`, `summary: string`, `soWhat: string`.
- `source: provenance`.

`category_findings`

- `findingId: string` — explicit source ID; `categoryId`, `categoryName`,
  `name`, `coreFinding: string`.
- `supportingMetaClusterIds`, `supportingClusterIds: string[]`.
- `strategicSignificance: string`, `operationalImplications`,
  `unresolvedQuestions`, `caveats: string[]`.
- `confidence: string`, `reviewRequired: boolean`.
- `source: provenance`.

`scenarios`

- `scenarioId: string` — explicit source ID; `name`, `timeframe`,
  `scenarioType`, `coreScenario: string`.
- `drivingForces`, `categoryNames`, `categoryIds`, `themeIds`,
  `tensionNames`, `tensionIds`, `strategicImplications`,
  `operationalImplications`, `researchQuestions`, `assumptions`,
  `alternativeOutcomes: string[]`.
- `uncertaintyLevel: string`, `reviewRequired: boolean`.
- `source: provenance`.

`scenario_pathways`

- `pathwayId: string`, `scenarioId: string`, `stepNumber: integer`,
  `pathwayStep: string`, `source: provenance`.

`scenario_indicators`

- `indicatorId: string`, `scenarioId: string`, `ordinal: integer`,
  `indicator: string`, `source: provenance`.

`scenario_actions`

- `actionId: string`, `scenarioId: string`, `ordinal: integer`,
  `policyOrPracticeAction: string`, `source: provenance`.

### Evidence and review governance

`evidence_links`

- `evidenceLinkId: string` — deterministic semantic-link ID.
- `sourceEntityType`, `sourceEntityId`, `targetEntityType`,
  `targetEntityId`, `evidenceRole: string`.
- `rank: integer?`, `notes: string[]`, `targetResolved: boolean`.
- `sources: provenance[]`.

`review_flags`

- `reviewFlagId: string`, `entityType`, `entityId`, `flagType: string`.
- `reason`, `status`, `priority`, `details: string?`.
- `sources: provenance[]`.

Current `flagType` values are `ambiguity`, `reviewRequired`,
`sourceReviewQueue`, `unmappedMetaCluster`, and
`unresolvedClusterReference`. Current evidence roles include
`representativeItem`, `representative`, `primary`, `secondary`,
`clusterThemeEvidence`, `cooccurrenceExample`, `poleAEvidence`, and
`poleBEvidence`.

## Controlled and source-preserved values

The pipeline normalizes booleans but does not rewrite substantive analytical
vocabularies.

- `scope`: `focal`, `contextual`.
- Assignment `confidence`: `high`, `medium` in the drill-down source.
- `mappingType`: currently `primary`.
- `mappedEntityType`: `cross_cutting_theme`, `meta_cluster`.
- Theme and meta-cluster review status: currently `candidate`.
- `tensionLevel`: `within_cluster`, `between_clusters`, `cross_category`,
  `corpus_level_candidate`.
- `scenarioType`: `adaptation`, `baseline`, `disruption`, `escalation`,
  `failure`.
- `uncertaintyLevel`: currently `medium`, `high`.

Item extraction `confidence` is not a clean controlled vocabulary: the source
contains numbers, capitalization variants, and labels such as `moderate` and
`medium-high`. It is preserved as source text and must not be used as a public
facet without later governance.

Public `relationships.json` uses this closed relationship vocabulary and
canonical endpoint types:

| `relationshipType` | `sourceType` | `targetType` |
|---|---|---|
| `cluster-belongs-to-category` | `cluster` | `category` |
| `meta-cluster-belongs-to-category` | `metaCluster` | `category` |
| `cluster-belongs-to-meta-cluster` | `cluster` | `metaCluster` |
| `theme-connects-meta-cluster` | `theme` | `metaCluster` |
| `theme-supported-by-cluster` | `theme` | `cluster` |
| `tension-maps-to-cross-cutting-theme` | `tension` | `theme` |
| `tension-maps-to-meta-cluster` | `tension` | `metaCluster` |

Relationship IDs are unique and every source and target ID must resolve to the
corresponding public entity collection. Every public relationship has
`interpretation: "semantic"`; causal interpretation values are invalid.

## Foreign-key and unresolved-reference rules

- All focal items have one assignment row and exactly one primary cluster.
- `secondaryClusterId` is either a canonical cluster ID or `null`; the 416
  explicit source `NONE` values are not converted into a fabricated cluster.
- Contextual items do not require cluster assignments.
- Every focal category has exactly one `category_summaries` record with a
  stable `categorySummaryId`, a valid `categoryId`, `summary`, and `soWhat`.
- Tension mappings are polymorphic but closed: `cross_cutting_theme` targets
  `themes`, while `meta_cluster` targets `meta_clusters`; other mapping types
  are validation errors.
- Evidence and representative-item references resolve to canonical `MASTER`
  item IDs; copied item prose never creates another item entity.
- Three source theme/cluster evidence placeholders have no cluster ID. They are
  retained with `clusterId: null`, `unresolvedReference: true`, provenance, and
  review flags. No other null required foreign key is permitted.
- Three clusters currently lack a meta-cluster mapping: `CRB-10`, `FTP-13`,
  and `KCFT-20`. They remain valid clusters with explicit review flags.
- Narrative and scenario tension text is retained as names. An ID is populated
  only when the source or an exact authoritative mapping supports it; the
  importer does not guess an ontology link from similar wording.

## Public/private boundary

The complete normalized dataset is private under
`analysis/cognitive-security/normalized/`. Public files are generated from
positive field allowlists under `data/cognitive-security/`.

Public output may contain governed category, cluster, synthesis, episode, and
high-level semantic-relationship fields. It must not contain full item
records, evidence excerpts, copied quotes, speakers, assignment rationales,
model/coder metadata, internal human notes, detailed review queues, raw source
paths, or workbook blobs. Review and unresolved state is exposed publicly only
as aggregate QA/coverage information unless a later human publication review
expands the allowlist.

## Interpretation requirements

- Counts measure corpus discourse salience, not objective importance,
  frequency in the world, consensus, or scientific support.
- Items are interpretive extraction units, not independent observations.
- Primary and secondary coding encode dominant meaning and substantive
  conceptual adjacency; co-occurrence is semantic, not causal.
- A meta-cluster is a within-category family. A cross-cutting theme connects
  patterns across categories. A tension preserves competing assumptions. A
  meta-narrative is a high-level interpretive storyline.
- Scenarios are plausibility exercises, not forecasts.
- Model coding confidence is not scientific evidence strength.
- Every higher-order claim should remain traceable to source IDs where the
  workbook lineage supplies them.
