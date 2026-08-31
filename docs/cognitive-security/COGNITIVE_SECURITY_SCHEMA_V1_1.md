# PSYWERX Cognitive Security Map Schema v1.1

**Status:** Governed corpus-reconciliation contract

**Product:** PSYWERX Cognitive Security Practitioner Discourse Map

**Supersedes for new builds:** Schema v1.0

**Preserves:** The complete Schema v1.0 historical analytic release

Schema v1.1 separates a canonical public-feed episode release from the transcript or
source-file identity used by the historical extraction workflow. The change
corrects the corpus model and public coverage language; it does not alter any
source workbook, item, assignment, cluster, or higher-order synthesis record.

[Schema v1.0](./COGNITIVE_SECURITY_SCHEMA_V1.md) remains the historical
contract for the original release, in which `episodes` represented 269
source-file identities. All v1.0 entity definitions not explicitly changed
below remain in force.

The Map is an interpretive account of practitioner discourse. Its counts do
not measure objective importance, prevalence, consensus, or scientific
evidence strength.

## Why the schema changed

The historical extraction dataset contains 269 distinct transcript/source
identities. Forensic reconciliation established that these identities comprise
242 canonical public-feed episode releases:

- 215 source identities map one-to-one to a public-feed release;
- 52 identities form 26 confirmed modern/legacy alias pairs for episodes 2
  through 27; and
- two identities form one confirmed precursor/recording alias group for public
  episode 186.

The original 14,397 extracted items remain intact. A separately labeled
reconciled sensitivity dataset retains one governed source identity per
canonical episode and contains 12,978 items. It is not a replacement or silent
rewrite of the original analytic dataset.

## Identity model

```text
canonical episode
  1 -> many source identities
          1 -> many extracted items
```

The three identities have different meanings:

- `episodeId` identifies a canonical public-feed episode release.
- `sourceIdentityId` identifies the historical transcript/source-file record
  from which an item was extracted.
- `itemId` remains the explicit, permanent `MASTER.ID` from the historical
  workbook.

Items retain both links. This preserves backwards traceability while allowing
public episode coverage to count public-feed releases rather than input files.
An item from a governed excluded source would retain its `sourceIdentityId` and
have `episodeId: null`; there is no such excluded identity in the current
release.

## Serialization and provenance

Schema v1.0 serialization rules continue to apply: absent scalars are `null`,
absent lists are `[]`, source IDs are preserved, generated IDs are
deterministic, records are sorted by stable ID, and JSON is UTF-8 with no
generated timestamp.

Private provenance uses workbook basenames, worksheet names, and one-based row
numbers. Absolute paths are prohibited. Workbook hashes may be used in private
build and QA artifacts, but are not part of the public reconciliation
contract. Transcript text, transcript hashes, source filenames, normalized
titles, item text, evidence excerpts, and detailed matching evidence remain
private.

## Collection registry changes

| Collection | Primary key | Principal foreign keys | Records | Publication class |
| --- | --- | --- | ---: | --- |
| `episodes` | `episodeId` | `canonicalSourceIdentityId` | 242 | Public allowlisted subset |
| `episode_summaries` | `episodeId` | Canonical public episode | 242 | Public reviewed/frozen product |
| `episode_relationships` | `relationshipId` | Canonical public episode and public analytical entity | 21,855 | Public standalone derived product |
| `episode_source_identities` | `sourceIdentityId` | Source provenance | 269 | Private/internal |
| `episode_source_mappings` | `episodeSourceMappingId` | `sourceIdentityId`, nullable `canonicalEpisodeId` | 269 | Private/internal; public aggregates only |
| `episode_reconciliation_flags` | `episodeReconciliationFlagId` | Source-identity and candidate-episode IDs | Source-derived | Private/internal; public aggregates only |
| `items` | `itemId` | nullable `episodeId`, `sourceIdentityId`, `categoryId` | 14,397 | Private/internal |

The remaining v1.0 collections and counts are unchanged. In particular, v1.1
does not regenerate the 127 clusters, 36 meta-clusters, 11 themes, 30
tensions, seven source meta-narratives, 42 category findings, or six
scenarios.

## Exact v1.1 record shapes

### `episodes`

- `episodeId: string` — stable canonical public-feed episode ID. The selected canonical
  source identity's existing deterministic ID is retained.
- `podcast: string?`, `episodeTitle: string?`.
- `parsedEpisodeNumber: integer?`.
- `canonicalSourceIdentityId: string` — private normalized record only.
- `sourceIdentityIds: string[]`, `sourceIdentityCount: integer` — private
  normalized record; the public record exposes only the count.
- `originalItemCount`, `originalFocalItemCount`,
  `originalContextualItemCount: integer` — historical items across all mapped
  source identities.
- `reconciledSensitivityItemCount`,
  `reconciledSensitivityFocalItemCount`,
  `reconciledSensitivityContextualItemCount: integer` — items retained from
  the selected canonical source identity.
- `reconciliationStatus: "unique" | "confirmed-alias"` for the current
  confirmed corpus.
- `source: provenance` — private normalized record only.

The public episode allowlist is intentionally smaller: `episodeId`, `podcast`,
`episodeTitle`, `parsedEpisodeNumber`, `sourceIdentityCount`,
`originalItemCount`, and `reconciledSensitivityItemCount`. It contains no
source filename, alias-member ID, transcript detail, or row-level provenance.

### `episode_summaries` public product

`episode_summaries.json` contains exactly one record for each public episode:

- `episodeId: string` — canonical public-feed release ID.
- `summary: string` — reviewed 100–180-word grounded synthesis.
- `keyTopics: string[]` — three to six concise grounded topics.
- `whyItMatters: string` — concise interpretive relevance statement grounded
  in the same selected inputs.
- `sourceItemCount`, `focalItemCount`, `contextualItemCount: integer` — safe
  aggregate counts from the retained canonical source; the focal and contextual
  counts sum to the source-item count.
- `generationMethod: string` — frozen authoring-method label.

The product is authored from an ignored source package and reviewed before it
is frozen. An ordinary website build treats this JSON as an input, validates
complete episode coverage and its allowlist, and does not regenerate prose or
call an API.

### `episode_relationships` public product

`episode_relationships.json` is separate from the historical
`relationships.json`. Every record has these common fields:

- `relationshipId: string` — stable ID derived from relationship type, episode,
  and target.
- `relationshipType: string` — one value from the closed vocabulary below.
- `sourceType: "episode"`, `sourceId: string` — canonical public episode.
- `targetType: "category" | "cluster" | "metaCluster" | "theme" |
  "tension"`, `targetId: string` — existing public entity.
- `relationshipSemantics: string` — explicit direct, derived, or aggregation
  interpretation.

| `relationshipType` | `relationshipSemantics` | Required support fields |
| --- | --- | --- |
| `episode-participates-in-category` | `direct-item-aggregation` | `itemCount`, `focalItemCount`, `contextualItemCount` |
| `episode-coded-to-cluster` | `direct-coded-relationship` | `primaryCount`, `secondaryCount`, `weightedCount` |
| `episode-derived-to-meta-cluster` | `derived-through-cluster-membership` | coding counts plus `supportingClusterIds` |
| `episode-derived-to-theme` | `derived-analytical-connection` | coding counts, supporting cluster/meta-cluster IDs, and `derivationPaths` |
| `episode-has-theme-lineage` | `direct-item-lineage` | derived support fields plus public-safe `itemCount` |
| `episode-has-tension-lineage` | `direct-item-lineage` | `itemCount`, `poleASupportCount`, `poleBSupportCount`, and `interpretiveCaveat` |

Cluster, meta-cluster, and theme weighted counts use the existing
`2 × primary + secondary` rule. Direct theme lineage requires a retained item
listed in governed theme representative evidence. Direct tension lineage
requires a retained item listed in governed pole evidence. Tension connections
are not derived through broader theme or meta-cluster closure; the public
product intentionally omits those non-discriminating links. Item and pole
counts describe traceable lineage and never imply endorsement, consensus, or
causation.

### `episode_source_identities`

- `sourceIdentityId: string` — the historical v1.0 `episodeId`, preserved
  exactly.
- `podcast`, `sourceEpisodeTitle`, `sourceFile: string?`.
- `parsedEpisodeNumber: integer?`.
- `identityKind: string` — governed filename/title convention such as
  `modern-numbered`, `legacy-numbered`, `leading-numbered`, `re-release`,
  `trailer`, or `unnumbered`.
- `numberEvidenceConflict: boolean`.
- `normalizedTitle`, `normalizedSourceFilename: string` — deterministic
  comparison aids, not public labels.
- `originalItemCount`, `focalItemCount`, `contextualItemCount: integer`.
- `source: provenance`.

### `episode_source_mappings`

- `episodeSourceMappingId: string` — deterministic from source identity.
- `sourceIdentityId: string`.
- `candidateCanonicalEpisodeId`, `canonicalEpisodeId: string?`.
- `aliasGroupId: string?`.
- `mappingStatus: "unique" | "confirmed-alias" | "likely-alias" |
  "ambiguous" | "unresolved" | "excluded-non-episode"`.
- `mappingRole: "canonical" | "alias" | "candidate" | "excluded"`.
- `mappingBasis: string[]`, `confidence: string`.
- `collapseEligible: boolean` — true only for a confirmed alias member that
  may be excluded from the reconciled sensitivity dataset.
- `decisionSource: string` — identifies the governed rule or future human
  decision layer.
- `source: provenance`.

`likely-alias`, `ambiguous`, and `unresolved` mappings remain distinct. They
cannot be collapsed automatically or used to force a target episode count.

### `episode_reconciliation_flags`

- `episodeReconciliationFlagId: string`.
- `flagType: string`.
- `sourceIdentityIds: string[]`.
- `candidateEpisodeNumber: integer?`.
- `status: string`, `reason: string`.
- `evidence: object` — structured diagnostic evidence; never transcript text.
- `sources: provenance[]`.

Pending flags form the private reconciliation review queue. Informational and
resolved flags preserve decisions such as retaining a content-equivalent
re-release as a distinct public-feed release.

### `items` changes

All v1.0 item fields remain. Two corpus links now have explicit semantics:

- `sourceIdentityId: string` — the historical source identity from which the
  item was extracted.
- `episodeId: string?` — the reconciled public-feed episode. It is null only
  when the source has a governed non-episode disposition.

Item IDs, text, category, scope, evidence, scoring, and provenance are not
rewritten by reconciliation.

## Reconciliation decision rules

The governed automatic rules are deliberately narrow. A legacy and a modern
source identity are confirmed aliases only when they:

1. encode the same governed episode number in the established leading-name
   convention; and
2. have corroborating normalized title tokens above the documented threshold.

The modern `#N ...` identity is selected for the sensitivity dataset. One
additional source, the `IPA Brown Bag Vygotsky Inner Speech with Rod Korba`
recording, is confirmed as a precursor/source alias for public episode 186
because the locally available transcript explicitly identifies the intended
podcast edit and the content comparison strongly corroborates it. Exact or
fuzzy title similarity by itself, re-release wording, and arithmetic pressure
to reach 242 are not sufficient. Conflicting number evidence or an unexpected
pair cardinality creates a review flag and preserves separate candidates.

Private transcript comparison may inform a mapping, but transcript text,
transcript-level evidence, and hashes are not part of the public data contract.
Episode 83 is a public-feed re-release with content reuse; it remains a distinct
canonical release under the declared unit of analysis. A stricter unique-
recording/content unit would yield 241, which is a documented limitation rather
than an undisclosed alternate count.

## Reconciled sensitivity dataset

The sensitivity dataset is a derived, private analytical view. It:

- retains one canonical source identity for each confirmed episode;
- excludes one alias member from each of the 27 confirmed groups;
- retains episode `#000 Trailer` as public-feed episode 000;
- retains the episode 83 re-release as a distinct public-feed release while
  preserving a private content-reuse flag;
- retains 12,978 items: 9,855 focal and 3,123 contextual; and
- never semantically deduplicates or rewrites item records.

The historical release remains 14,397 items: 10,940 focal and 3,457
contextual. Reports must label the two bases explicitly as **original analytic
release** and **reconciled sensitivity dataset**.

Support-sensitivity metrics test how traceable support counts change under the
selection rule. They do not independently validate a cluster, theme, tension,
narrative, or scenario, and they do not convert frequency into consensus.

The episode products apply a stricter canonical-source selection at their
input boundary: an item is retained only when its historical
`sourceIdentityId` equals the episode's `canonicalSourceIdentityId`. A remapped
`episodeId` alone is not sufficient. This prevents excluded alias-source items
from contributing to summary inputs or episode relationship counts.

## Public reconciliation aggregate

`data/cognitive-security/corpus_reconciliation.json` is the only dedicated
public reconciliation file. It provides:

- schema and reconciliation-rule versions;
- aggregate counts for canonical episodes, historical source identities,
  confirmed alias groups and members, excluded identities, unresolved states,
  and original versus sensitivity item totals;
- neutral interpretation and limitation text; and
- the governed automatic-rule summary needed to understand the count; and
- `reanalysisRecommendation: "full-pipeline-reanalysis-recommended"` for the
  current sensitivity result.

It must not expose source filenames, alias-pair details, workbook hashes,
transcript hashes or text, normalized matching strings, item IDs, detailed
review evidence, local paths, or private analysis filenames.

The browser-loaded `manifest.json` identifies each governed source with only
an opaque `artifactId` and `canonicalRole`. Public `qa_report.json` uses the
same IDs and exposes only `worksheetCount`, `aggregateRowCount`, and
`integrityVerified` for source QA. Exact source filenames, hashes, worksheet
names, and row-level provenance remain in the ignored private normalized
release.

The exact top-level fields are `schemaVersion`, `methodVersion`, `status`,
`counts`, `interpretation`, `automaticRules`, `limitations`, and
`reanalysisRecommendation`. `counts` contains only non-negative integers under
these keys:

- `canonicalEpisodes`, `originalSourceIdentities`,
  `confirmedAliasGroups`, `sourceIdentitiesInConfirmedAliasGroups`,
  `excludedConfirmedAliasSourceIdentities`, and
  `excludedNonEpisodeSourceIdentities`;
- `likelyAliasSourceIdentities`, `ambiguousSourceIdentities`,
  `unresolvedSourceIdentities`, and `pendingDecisionRecords`; and
- `originalItems`, `reconciledSensitivityItems`, `originalFocalItems`,
  `reconciledSensitivityFocalItems`, `originalContextualItems`, and
  `reconciledSensitivityContextualItems`.

`status` is `complete` only when the private review queue is empty; otherwise
it is `human-review-required` and the uncertain identities remain uncollapsed.

## Validation requirements

A v1.1 build fails before publication unless all of the following hold:

- every historical source identity has exactly one mapping;
- every item resolves to its historical `sourceIdentityId`;
- every episode item resolves to one canonical episode;
- every collapsed member is a high-confidence `confirmed-alias` with
  `collapseEligible: true`;
- likely, ambiguous, and unresolved candidates remain uncollapsed;
- canonical episode IDs are unique;
- the 27 governed alias groups have one canonical and one alias member each;
- the episode-zero trailer remains represented as episode 000;
- original counts remain 14,397 / 10,940 / 3,457;
- sensitivity counts are 12,978 / 9,855 / 3,123;
- frozen summaries cover all 242 canonical episodes exactly once and retain
  valid public-safe source counts;
- every episode relationship starts at a canonical episode, resolves to an
  existing public entity, and declares the correct direct or derived semantics;
- episode tension links have direct retained-item lineage and are never
  inferred through broad analytical closure;
- the historical public `relationships.json` is byte-equivalent to the
  governed historical release;
- no public file exposes a private field or absolute local path; and
- two builds from unchanged inputs produce byte-identical JSON.

## Interpretation and migration rule

Schema v1.1 is a corpus-model correction and sensitivity layer, not a
retroactive edit to the analysis. Canonical episode and coverage metrics use
the reconciled model, while the historical higher-order synthesis remains
frozen and is accompanied by support-sensitivity findings. Because 13
higher-order entities are highly sensitive—including two tensions that lose
all directly traceable item support—the governed result is **full-pipeline
reanalysis recommended**. That future rerun is outside this migration and
requires a separately governed project. Sensitivity does not prove that an
existing entity is invalid.

An unfinished v2 analytical effort is not part of the v1.1 authority chain and
is not used to create these episode products. Any future migration to a v2
source package requires its own governed release and validation decision.
