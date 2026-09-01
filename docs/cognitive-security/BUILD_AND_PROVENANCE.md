# Cognitive Security Map Build and Provenance

This document defines how the eight private workbooks become the governed
internal normalized dataset and conservative static JSON package for the
PSYWERX Cognitive Security Practitioner Discourse Map.

This release uses the governed historical v1.1 package described below. A
separate v2 analytical effort is underway, but unfinished v2 outputs are not
source inputs, comparison authorities, or fallback material for this build.

The workbooks are successive stages of one analytic lineage, not eight
independent datasets. Schema v1.1 adds a reconciliation layer between the
historical source identities and canonical public-feed episode releases:

```text
canonical episodes
  -> transcript/source identities
    -> extracted items
  -> intermediate clusters and item assignments
  -> cluster synthesis
  -> within-category meta-clusters
  -> cross-cutting themes and tensions
  -> meta-narratives, category findings, and scenarios
```

The Cognitive Security Map remains separate from the PSYWERX Driver Ontology.
No discourse cluster, theme, tension, narrative, or scenario is imported as a
behavioral Driver.

## Source package and authority

All source files live under the ignored local directory
`source-data/ipa-podcast/`. The build requires these exact basenames:

| Artifact ID | Workbook and canonical worksheets | Authority |
| --- | --- | --- |
| `ART-codebook` | `codebook.xlsx` / `Sheet1` | Canonical 127 cluster IDs, names, categories, definitions, inclusion/exclusion criteria, near-neighbor distinctions, and examples. |
| `ART-master-extractions` | `master_extractions.xlsx` / `MASTER`; `MASTER (only coded cats)` | Canonical 14,397 items and episode/source information. The coded sheet supplies the authoritative 10,940 focal-ID subset only. |
| `ART-drill-down` | `drill_down.xlsx` / `Drill Down` | Canonical primary/secondary assignments, rationales, coding confidence, ambiguity, and review fields for focal items. |
| `ART-cluster-summaries` | `drill_up_cluster_summaries.xlsx` / `Cluster Summaries`, `Theme Details`, `Representative Items` | Canonical cluster synthesis, recurring subthemes, counts, significance, implications, and representative-item evidence. |
| `ART-meta-clusters` | `drill_up_meta_clusters.xlsx` / `Candidate Meta-Clusters`, `Cluster-to-Meta Mapping`, `Meta-Cluster Evidence`, `Review Queue` | Canonical within-category meta-clusters, mappings, evidence, and review queue. |
| `ART-cross-cutting-themes` | `cross_cutting_themes.xlsx` / `Cross-Cutting Themes`, mapping/evidence/representative/review sheets | Canonical cross-category themes and their source-authored support. |
| `ART-tensions` | `tensions_debates_rebuilt.xlsx` / `Tensions Debates`, `Tension Evidence`, `Tension Mapping`, `Review Queue` | Canonical final tensions, poles, assumptions, evidence, confidence, and mappings. |
| `ART-final-synthesis` | `final_synthesis.xlsx` / narrative, category, scenario, pathway, indicator, action, and review sheets | Canonical seven meta-narratives, category summaries/findings, and six scenarios. |

Copied `Codebook Used`, `Source Meta-Clusters`, `Source Cluster Summaries`,
`Source Cross Themes`, representative-item prose, and final-synthesis previews
are not independent entities. Canonical precedence always follows the table
above.

## Source-reading API

The reusable ingestion boundary is:

```python
from cognitive_security import extract_sources, normalize_sources

extracted = extract_sources("source-data/ipa-podcast")
dataset = normalize_sources(extracted)
```

`extract_sources(source_dir)` returns:

- `artifacts`: basename-only source manifest with SHA-256 and byte size;
- `tables`: canonical worksheet rows with normalized cells and `_source`
  provenance; and
- `sheetInventory`: every sheet's dimensions, discovered header row, headers,
  and canonical-table designation.

It raises `SourceValidationError` after collecting clear diagnostics when a
required workbook, worksheet, unique header row, required header, or canonical
data table is missing. All current canonical table headers are centralized in
`scripts/cognitive_security/sources.py`.

`normalize_sources(extracted)` first recreates the historical entity
collections defined in `COGNITIVE_SECURITY_SCHEMA_V1.md`. The reconciliation
stage then applies the governed source-identity rules and produces the
Schema v1.1 collections defined in
`COGNITIVE_SECURITY_SCHEMA_V1_1.md`. It fails on missing source IDs, duplicate
canonical IDs, unmapped identities, or a collapse that does not meet the
confirmation rule. It preserves explicit unresolved records where the source
marks a missing link rather than inventing a target.

## Extraction and normalization decisions

1. Each workbook is hashed with SHA-256 before semantic extraction. Exact
   hashes and filenames are retained in the ignored private normalized
   manifest and QA outputs. The public manifest exposes only opaque artifact
   IDs and canonical roles; public QA exposes verification status and aggregate
   worksheet/row counts without workbook names, worksheet names, or hashes.
2. Workbooks open read-only with cached formula results. Canonical sources do
   not rely on formula/working sheets.
3. Source strings are trimmed and internal whitespace is collapsed. Empty
   cells become `null`; numbers and booleans retain their types.
4. The header detector scans the first 25 rows, requires one row containing
   every governed header, and rejects duplicate headers. All current canonical
   tables use row 1.
5. Fully empty data rows are skipped. This is important because
   `MASTER (only coded cats)` retains blank row positions from the complete
   master sheet.
6. Canonical item identity is `MASTER.ID`. The focal subset and every copied
   representative/evidence row join back to that ID. Copied text never creates
   a second item.
7. Focal categories are those governed by the Codebook and present in the
   coded master subset. The three additional master categories are contextual.
8. Historical source-identity IDs are deterministic from `source_file`;
   podcast and episode title are a fallback only when that file key is absent.
   A source-file collision with inconsistent metadata is an error. Schema v1.1
   preserves that ID as `sourceIdentityId` and links it to a separate canonical
   `episodeId`.
9. Explicit cluster, meta-cluster, theme, tension, narrative, finding, and
   scenario IDs are preserved. Generated IDs use stable semantic fields, not
   row number, random state, or time.
10. Source `NONE` secondary assignments become `secondaryClusterId: null` and
    retain `secondaryIsNone: true`. Blank and substantive secondary states are
    not silently merged.
11. Source review-required and ambiguity flags remain on assignment records
    and also create durable normalized review flags once per source row.
12. Serialized list fields are parsed conservatively. Final-synthesis Python
    list/dict representations are read with safe literal parsing. Explicit
    embedded IDs are extracted only from named ID fields or known canonical ID
    sets.
13. Legacy item-ID list cells contain a small number of malformed quote/comma
    fragments such as `732','1852` and trailing commas. Because canonical item
    IDs are numeric, the parser extracts numeric tokens in source order and
    validates every resulting ID against `MASTER`; it does not infer prose or
    invent an item.
14. Higher-order debate labels are not treated as canonical tension IDs merely
    because wording is similar. Theme/tension IDs are derived only from the
    explicit canonical `Tension Mapping` sheet. Unresolved narrative/scenario
    labels remain narrative text.
15. Source identities are reconciled after historical normalization. Only a
    single modern/legacy pair with the same governed episode number and
    corroborating title tokens is automatically confirmed. Fuzzy similarity,
    re-release wording, or the desired corpus count is not sufficient.
16. Every item retains its historical `sourceIdentityId`. Its `episodeId`
    resolves to the canonical public-feed episode. Episode `#000 Trailer`
    remains public-feed episode 000; no current source identity is dropped as a
    non-episode.
17. The reconciled sensitivity dataset selects the modern source identity in
    each confirmed pair. It never merges or rewrites item text and never
    overwrites the historical item collection.
18. Public episode products apply the canonical selection again at their input
    boundary. An item contributes only when its `sourceIdentityId` equals the
    episode's `canonicalSourceIdentityId`; an `episodeId` remapping by itself is
    insufficient. This prevents an excluded alias member from entering episode
    summary inputs or episode relationship aggregates.

## Portable provenance

Every normalized record points to an artifact ID, workbook basename,
worksheet, and one-based source row. Semantic evidence and review records can
merge repeated support while retaining an ordered `sources` array.

The build intentionally does not ingest Run Summary path cells. Current Run
Summary sheets contain private Windows paths, input/output workbook paths, and
candidate-file locations. These are neither semantic data nor safe public
provenance. The normalized and public datasets contain no absolute local path.

Source-authored `runId`, `promptVersion`, `model`, `coder`, and
`codedTimestamp` fields remain available only where they support private QA.
They do not determine generated IDs and are excluded from public allowlists.

## Current source reconciliation

The original analytic release and reconciled corpus interpretation are both
governed facts. They must not be collapsed into one unlabeled count.

| Corpus metric | Original analytic release | Reconciled interpretation |
| --- | ---: | ---: |
| Workbooks | 8 | 8 |
| Transcript/source identities | 269 | 269 preserved; 242 selected |
| Canonical public-feed episode releases | Not separately modeled | 242 |
| Confirmed alias groups | Not separately modeled | 27 |
| Excluded non-episode identities | Not separately modeled | 0 |
| Items | 14,397 | 12,978 sensitivity items |
| Focal items and assignment rows | 10,940 | 9,855 sensitivity items |
| Contextual items | 3,457 | 3,123 sensitivity items |

The 242 releases comprise 215 one-to-one identities and 27 confirmed alias
groups. Twenty-six pairs cover episodes 2 through 27; each includes one modern
`#N ...` identity and one legacy `The Cognitive Crucible Episode NNN ...`
identity. A twenty-seventh group links a precursor/source recording to public
episode 186. Episode `#000 Trailer` is retained as episode 000. The episode 83
re-release remains a distinct public-feed release despite documented content
reuse, so a stricter unique-recording/content unit would yield 241. No likely,
ambiguous, or unresolved mapping is collapsed in the current build. Detailed
rules and evidence boundaries are in
[Corpus reconciliation](./CORPUS_RECONCILIATION.md).

The following historical synthesis counts remain unchanged:

| Analytic entity | Historical count |
| --- | ---: |
| Substantive secondary assignments | 10,524 |
| Explicit secondary `NONE` rows | 416 |
| Review-required assignment rows | 514 |
| Ambiguity-flagged assignment rows | 158 |
| Intermediate clusters | 127 |
| Cluster summaries | 127 |
| Meta-clusters | 36 |
| Cluster-to-meta mappings | 124 |
| Cross-cutting themes | 11 |
| Theme-to-meta mappings | 89 |
| Theme-to-cluster evidence rows | 302 |
| Tensions | 30 |
| Meta-narratives | 7 |
| Category findings | 42 |
| Scenarios | 6 |

These are comparisons used by QA. The pipeline reports deviations and does not
alter source truth to force a target count. The sensitivity layer measures
support change; it does not regenerate or independently validate any
higher-order entity.

The support audit classifies 44 of 132 higher-order entities as stable, two as
mildly sensitive, 18 as moderately sensitive, 13 as highly sensitive, and 55
as unassessable from available item-level provenance. Among the highly
sensitive records, `TD-024` loses all 12 directly traceable supporting items
and `TD-026` loses all 14 after canonical-source selection. Several other
tensions lose category breadth. These conditions trigger the governed
`full-pipeline-reanalysis-recommended` result; they do not establish that the
historical entities are invalid.

## Episode products and freeze boundary

Episode summaries and episode relationships are public companion products;
they do not regenerate the historical extraction, coding, clusters, or
higher-order synthesis.

`scripts/build_transcript_summaries.py` is the separate summary authoring
workflow. It joins the ignored transcript corpus to the governed v1.1
reconciliation, selects one canonical readable transcript for each of the 242
public releases, records complete sequential chunk coverage, and keeps the
manifest, transcript paths and hashes, source identities, alias decisions,
authoring checkpoints, comparisons, and QA beneath the ignored
`analysis/cognitive-security/transcript-summaries-v1/` directory. The public
summary record contains only the canonical episode ID, number and title,
reviewed summary prose, three to six transcript-derived key topics, a
why-it-matters statement, the frozen summary-method token, and safe transcript
and summary word counts. Transcript text, item IDs and text, source identities,
evidence excerpts, authoring prompts, raw responses, and credentials remain
private.

Summary authoring is review-gated and occurs before an ordinary website build.
First run deterministic corpus QA against the reviewed private candidate (not
the currently published file):

```powershell
py scripts\build_transcript_summaries.py qa `
  --summaries <reviewed-summary-json>
```

Review and adjudicate every resulting review-level flag, complete the deep
transcript-grounding sample, and then publish that same reviewed candidate
with:

```powershell
py scripts\build_transcript_summaries.py publish `
  --summaries-from <reviewed-summary-json> `
  --qa-report <automatic-qa-json> `
  --adjudication-report <review-flag-dispositions-json> `
  --deep-qa-report <deep-transcript-qa-json>
```

The resulting `data/cognitive-security/episode_summaries.json` is then a frozen
input to `scripts/build_cognitive_security.py`. The ordinary build requires
complete coverage, validates the frozen file, carries it into the deterministic
public package, and makes no API calls. Missing or invalid frozen summaries stop
publication instead of triggering implicit generation.

The transcript publisher permits an ignored private candidate before QA. A
write to the public frozen path is atomic and additionally requires an
automatic QA report whose payload hash matches the candidate, complete
adjudication of every review-level flag, and a payload-matched deep grounding
review of at least 24 releases with no unresolved major issue. The legacy
structured-item episode-product command rejects summary publication so it
cannot bypass these transcript gates or rewrite relationships as a side effect.

Public episode summaries are transcript-grounded syntheses generated from the
canonical episode transcripts. The analytical relationships shown elsewhere
in the map are derived from the separately governed structured coding pipeline.
The transcript summary and analytical map relationship are separate products;
summary authoring does not change categories, clusters, themes, tensions,
narratives, scenarios, or either relationship graph.

`episode_relationships.json` is rebuilt deterministically from the same
canonical-source-only inputs:

- Category relationships directly aggregate retained items by category and
  focal/contextual scope.
- Cluster relationships directly aggregate actual primary and secondary codes,
  retaining the governed `2 × primary + secondary` weighted count.
- Meta-cluster relationships are derived through governed cluster membership.
- Theme relationships distinguish direct representative-item lineage from
  connections derived through governed cluster or meta-cluster paths.
- Tension relationships require direct retained-item evidence in at least one
  tension pole. Broader theme/meta-cluster closure is intentionally omitted
  because it would be analytically non-discriminating; direct lineage never
  means endorsement of either pole.

The episode graph is stored separately so its source selection and support
semantics remain explicit. The historical `relationships.json` stays
byte-equivalent to the governed historical release and is neither appended to
nor rewritten by episode-product generation.

## Known source anomalies and governance state

### Transcript/source lineage limits

Locally available historical materials identify raw source names for episodes
`#109` and `#127` without corresponding normalized transcript artifacts and
record a filename/title change for episode `#73` between raw and normalized
conventions. The canonical workbooks nevertheless contain the analytic records
and portable workbook provenance used by this build. The pipeline reports the
lineage gap; it does not reconstruct missing transcript files, substitute a
different source, or alter an episode identity to conceal the condition.

Private transcript comparison supports the episode-186 precursor/source alias
and documents content reuse in the episode-83 re-release. The latter remains a
distinct episode because the governed corpus unit is a public-feed release.
Transcript text, comparison details, and hashes are not public.

### Unmapped intermediate clusters

The source mapping has no meta-cluster assignment for:

- `CRB-10` — Forecasting, Complexity & Uncertainty
- `FTP-13` — Societal Transformation, Identity, & Social Cohesion
- `KCFT-20` — Strategic Culture & Ideological Competition

All three clusters remain in the dataset with review flags. No mapping is
invented.

`CRB-M05` is a source meta-cluster candidate with no cluster-mapping rows. Its
source rationale describes it as a cross-cutting synthesis lens rather than a
separate problem family. The record and empty membership are preserved; the
pipeline does not manufacture membership. Validation emits the explicit
governance warning `known_empty_meta_cluster` and carries the record into the
machine-readable unresolved-mapping review state.

### Explicit theme/cluster placeholders

Three `Theme-to-Cluster Evidence` rows, for `XTHEME-007`, `XTHEME-008`, and
`XTHEME-010`, contain no category or cluster ID and state that no matching
cluster-summary row was found. They remain among the 302 records with
`clusterId: null`, `unresolvedReference: true`, source provenance, and review
flags. Validation permits only these explicitly marked unresolved records.

### Seven source narratives, not eight

`final_synthesis.xlsx` contains seven records, `N01` through `N07`. Earlier
project documentation expected eight. The seven source IDs are preserved,
the mismatch is reported, and no `N08` is generated.

### Blank copied tension sheet

`final_synthesis.xlsx / Source Tensions` is blank. This does not mean the
corpus has no tensions. `tensions_debates_rebuilt.xlsx` is the authoritative
source and contains 30 final tensions.

### Duplicate/copy drift deliberately avoided

- The current `MASTER` has 14,397 unique IDs. Category-specific copy sheets
  omit six items and therefore are not canonical.
- `MASTER (only coded cats)` and `Drill Down` contain the same 10,940 focal
  IDs. Their copied extraction `confidence` fields differ from current MASTER
  for 4,229 IDs. Item confidence therefore comes from MASTER, while assignment
  coding confidence comes from Drill Down.
- Codebook copies agree with the canonical 127 IDs, but only
  `codebook.xlsx / Sheet1` creates cluster entities.

## Validation and failure safety

The orchestrator runs normalized integrity checks before publication. Checks
cover required files, hashes, sheet/header contracts, unique IDs, complete
source-identity-to-episode reconciliation, one primary assignment per focal
item, controlled
secondary `NONE`, category-summary completeness, polymorphic foreign keys,
review/ambiguity retention, unmapped clusters, public relationship endpoints,
theme/tension/synthesis references, and the seven-narrative discrepancy.
Public-product checks additionally require one frozen summary per canonical
episode, safe and internally consistent summary counts, valid episode
relationship endpoints and semantics, and direct item lineage for every
published episode-tension connection.

Generated content is serialized in memory and staged before existing valid
output is replaced. Any source, normalization, reconciliation, sensitivity,
validation, or public-boundary error aborts the write. Reproducible JSON uses UTF-8, sorted keys, fixed
indentation, trailing newlines, deterministic record order, and no generated
timestamp. Two builds from unchanged sources must be byte-identical.

Repository-root commands:

```powershell
py scripts\build_cognitive_security.py
py -m unittest discover -s tests/cognitive_security -p "test_*.py"
```

## Public/private publication boundary

The ignored private release candidate under
`analysis/cognitive-security/normalized/` retains canonical items, evidence
excerpts, speakers, full assignments, coding rationales, model/coder fields,
human notes, detailed review flags, and complete provenance.

The static public package under `data/cognitive-security/` is created only from
positive field allowlists. It contains governed high-level entities, canonical
public-feed episode labels, reviewed episode synthesis prose, public-safe
episode relationship aggregates, aggregate coverage/review/QA information,
`corpus_reconciliation.json`, and semantic relationships.
It excludes:

- workbook files and workbook data blobs;
- source-workbook filenames, exact source hashes, and worksheet names;
- full transcripts and full item corpus;
- unrestricted quotations or evidence-excerpt dumps;
- primary/secondary coding rationales;
- model, coder, prompt, and detailed run metadata;
- internal human notes and detailed review queues; and
- absolute paths or private source locations.

The public `manifest.json` represents each source artifact with exactly
`artifactId` and `canonicalRole`. Public `qa_report.json` uses the same opaque
IDs with `worksheetCount`, `aggregateRowCount`, and `integrityVerified`; the
exact filename-to-hash and worksheet inventory remains private.

The public reconciliation aggregate contains counts, method versions,
automatic rules, interpretation, limitations, and the governed reanalysis
recommendation only. It excludes source filenames, alias-pair detail,
normalized comparison values, transcript details, workbook hashes, item IDs,
and the private sensitivity tables.

Adding a field to the internal schema never publishes it automatically. A
human-approved public allowlist change is required.

## Research design and analytic workflow

### 1. Research purpose

This project is a field-mapping exercise. It asks what concepts, practices,
risks, opportunities, disagreements, and future possibilities recur in a
practitioner-facing podcast corpus. The public companion product now summarizes
each canonical release for navigation, but an episode is not the analytic unit
used to construct the map. The project is not a definitive taxonomy,
representative survey, causal model, competency framework, or scientific
evidence review.

### 2. Corpus and reconciliation

The governed corpus unit is a distinct public-feed episode release. The
historical workflow produced records for 269 transcript/source identities.
Forensic reconciliation maps those identities to 242 public-feed releases:
215 one-to-one identities and 27 confirmed alias groups. The alias groups
comprise the 26 legacy/modern pairs for episodes 2–27 and one precursor/source
recording for episode 186.

Episode `#000 Trailer` counts as release 000. Episode 83 is a separately
published re-release and is retained even though private comparison documents
content reuse; a unique-recording/content definition would yield 241. This
unit decision is disclosed so 242 is not mistaken for a count of independent
recordings or unique transcript content.

### 3. Transcript processing

The historical transcript files were processed through a structured
Python/API workflow that turned source material into consistently shaped
extraction records. The current repository starts from the eight canonical
XLSX outputs of that workflow; it does not rerun the historical model calls.
The importer validates the workbook lineage and preserves source-authored IDs
and portable row provenance. Private transcript material, prompts, detailed
extraction traces, and credentials are not published.

### 4. Unit of analysis

The analytic unit is an **extracted item**: a bounded, interpretive statement
about one concept, actor, event, risk, opportunity, prediction, or other
governed category. It is not an episode, paragraph, speaker, quotation, or
statistically independent observation. One episode can yield many items, and
items from the same episode may be related.

### 5. Ten extraction categories

Every item belongs to one of ten source-authored categories:

1. Key Concepts / Frameworks / Theories
2. Technologies / Tools / Platforms
3. Organizations / Actors / Communities
4. Key Events / Historical Examples
5. Future Trends / Predictions
6. Challenges / Risks / Barriers
7. Opportunities / Recommended Actions
8. Memorable Insights / Quotes
9. Strategic Landscape / Times
10. Guest Background / Experience

The categories are extraction lenses, not claims that the underlying subject
matter falls into mutually exclusive natural kinds.

### 6. Seven focal and three contextual categories

The first seven categories proceeded into the formal deep-coding and cluster
pipeline because they directly captured the concepts, actors, examples,
forecasts, problems, and actions needed for the field map. The remaining three
provided interpretive context—memorable language, strategic setting, and guest
background—but were not assigned to the 127 intermediate clusters. Their
3,457 historical items remain in the corpus and are not treated as failed or
missing coding.

### 7. Inductive codebook development

Intermediate cluster codes were developed separately within each focal
category. The source methodology records approximately three rounds of about
100 randomly sampled items per category:

- **Round 1 — discovery:** identify candidate codes and recurring distinctions;
- **Round 2 — refinement:** merge, split, rename, and clarify candidate-code
  boundaries; and
- **Round 3 — saturation-style stability check:** test whether another sample
  materially changes the working code structure.

This is a practical stability procedure, not formal proof of qualitative
saturation. The resulting codebook fixed cluster IDs, names, definitions,
inclusion and exclusion criteria, near-neighbor distinctions, and anchor
examples before full-corpus assignment.

### 8. Primary and secondary coding

Every focal item received exactly one primary cluster. The primary code records
the item's dominant analytic meaning. A secondary code was optional and marks
substantive conceptual adjacency that would be analytically useful to retain;
it is not merely a lower-confidence or second-best guess. An explicit `NONE`
means that no secondary assignment was made. Primary/secondary co-occurrence
is a semantic relationship, not evidence that one concept causes another.

### 9. Cluster synthesis and weighting

All items associated with an intermediate cluster informed its synthesis.
Source methodology documents a 2:1 primary-to-secondary weighting: a primary
assignment contributes two weighted units and a secondary assignment one. The
governed comparison formula is therefore `2 × primary + secondary` where that
measure is used. Weighting prioritizes dominant meaning during synthesis;
it does not make items independent, establish effect size, or convert a
frequency into evidence strength.

Cluster summaries capture recurring subthemes, strategic significance,
operational implications, edge cases, and representative source IDs. The 127
clusters were inductively developed analytic groupings, not pre-existing
scientific constructs.

### 10. Within-category meta-clusters

The 36 meta-clusters were built within categories before cross-category
synthesis. This preserves each extraction category's analytic meaning and
prevents superficially similar language from being merged across different
questions too early. A meta-cluster is a within-category family of clusters,
not an additional observation or behavioral Driver.

### 11. Cross-cutting themes

The 11 cross-cutting themes integrate patterns that recur across categories.
They differ from meta-clusters: a meta-cluster organizes related material
inside one category, while a theme expresses a supported cross-category
pattern. Theme links are semantic and source-governed; they are not causal
edges or proof of consensus.

### 12. Tensions and debates

The 30 tensions/debates were developed as a separate analytic product rather
than as negative themes. Their purpose is to retain competing assumptions,
tradeoffs, disagreements, and unresolved choices that a smoother synthesis
might erase. The two poles describe the source debate and do not imply equal
empirical support or endorse either side.

### 13. Meta-narratives and category findings

Meta-narratives are higher-order interpretive storylines that connect themes,
tensions, meta-clusters, and categories. They carry more interpretive distance
from the extracted items than clusters do and therefore require especially
cautious reading. The canonical final-synthesis workbook contains seven source
meta-narratives (`N01`–`N07`), despite an earlier expectation of eight; no
eighth record is invented. Category findings preserve additional synthesis
within the seven focal categories.

### 14. Scenarios

The six scenarios are structured plausibility exercises. They explore how
identified forces, tensions, and uncertainties might combine and identify
possible pathways, indicators, and actions. They are not predictions,
probability estimates, or statements that an outcome will occur.

### 15. Human role

Human judgment governed the research purpose, extraction ontology, selection
of focal categories, inductive codebook development, merge/split decisions,
code boundaries, ambiguity and review handling, reconciliation unit and rules,
interpretation, publication boundary, and final claims. Automation does not
remove researcher responsibility for those decisions.

### 16. AI role

AI served as a research assistant and scaling mechanism for structured
extraction, coding assistance, and synthesis support. It did not independently
define the research purpose or turn outputs into validated scientific facts.
Model outputs remain vulnerable to prompt sensitivity, model dependence,
semantic smoothing, overgeneralization, and hidden bias. Coding confidence is
workflow metadata, not scientific evidence strength.

Episode summary authoring is also a separate grounded synthesis task whose
authoritative input is each release's selected canonical transcript. Structured
analytical records may be consulted only after a transcript-first draft for QA
and identity checking; they do not determine summary content. The reviewed
output is frozen before the ordinary build, which performs no model or API
call. A summary-method token documents how the public prose was produced
without publishing prompts, raw responses, credentials, transcript text or
paths, or other private source material.

### 17. Traceability and reconciliation sensitivity

Where the workbook lineage supports it, the evidence chain is:

```text
public-feed episode
  -> historical source identity
    -> extracted item
      -> primary / optional secondary cluster assignment
        -> cluster synthesis
          -> within-category meta-cluster
            -> cross-cutting or higher-order synthesis
```

Explicit IDs and workbook-row provenance preserve this chain privately.
Public files expose only an allowlisted subset and aggregate coverage. The
reconciled sensitivity dataset removes one confirmed alias identity per group
and recalculates traceable support metrics without overwriting the historical
analysis. Support retention does not validate an entity; it shows only how
available within-corpus support changes under the declared source selection.

The public episode graph makes the final steps explicit without exposing the
items: category and cluster support is direct aggregation, meta-cluster and
some theme support is derived through governed mappings, and direct theme or
tension labels require representative-item or pole-evidence lineage. Derived
paths describe analytical traceability, not causal influence. Tension links are
direct-only because broad closure would not provide useful episode-level
discrimination.

### 18. Limitations

- A single practitioner-facing podcast corpus is not representative of the
  entire cognitive-security field or its affected populations.
- Discourse salience is not objective importance, prevalence, quality, or
  policy priority.
- Frequency is not consensus; repeated or duplicated discourse can increase a
  count without increasing agreement.
- Extracted items are interpretive and are not independent statistical
  observations.
- Results depend on the extraction ontology, codebook, prompts, models,
  sampling choices, and human interpretive decisions; another defensible
  design could yield different structures.
- AI-assisted processing is susceptible to prompt sensitivity, model
  dependence, semantic smoothing, overgeneralization, omissions, and hidden
  bias.
- Speaker labels, punctuation, and quotation boundaries inherit the source
  transcript's attribution limits; extracted wording should not be treated as
  a publication-ready verified quotation without separate review.
- Coding confidence records workflow certainty, not source credibility or
  scientific evidence strength.
- Primary/secondary co-occurrence and other semantic mappings do not establish
  causation, direction, or effect size.
- Interpretive distance increases at higher levels: meta-clusters, themes,
  tensions, meta-narratives, and scenarios are progressively farther from the
  source item and require correspondingly greater caution.
- The public-feed release unit retains content reuse such as the episode 83
  re-release. A unique-recording/content unit would produce a different count.
- Two raw source names (`#109`, `#127`) lack corresponding normalized
  transcript artifacts in the locally reviewed lineage, and episode `#73` was
  renamed between raw and normalized conventions.
- Some higher-order provenance is indirect or incomplete. `cannot assess from
  available provenance` is a valid sensitivity result and must not be replaced
  with an inferred link.
- The support-sensitivity audit does not regenerate the historical synthesis
  and cannot establish that a theme or other entity is scientifically valid.

The governed recommendation is **full-pipeline reanalysis recommended**. Use
the reconciled episode and coverage metrics now, preserve the original
synthesis as a historical output, and disclose its support sensitivity. This
release does not regenerate extraction, coding, clusters, or synthesis; that
future rerun should occur only through a separately governed project. Loss of
traceable support in this audit is a reason to rerun and compare, not proof
that an existing entity is invalid.

The underway v2 effort may eventually provide a separately governed basis for
comparison or replacement. Until that work is complete and approved, no v2
artifact contributes to this release, its episode summaries, or its episode
relationships.
