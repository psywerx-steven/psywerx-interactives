# Cognitive Security Map Build and Provenance

This document defines how the eight private workbooks become the governed
internal normalized dataset and conservative static JSON package for the
PSYWERX Cognitive Security Practitioner Discourse Map.

The workbooks are successive stages of one analytic lineage, not eight
independent datasets:

```text
episodes
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

`normalize_sources(extracted)` returns the entity collections defined in
`COGNITIVE_SECURITY_SCHEMA_V1.md`. It fails on missing source IDs or duplicate
canonical IDs. It preserves explicit unresolved records where the workbook
itself marks a missing link rather than inventing a target.

## Extraction and normalization decisions

1. Each workbook is hashed with SHA-256 before semantic extraction. Hashes are
   reported in the manifest and QA outputs; workbook bytes are not published.
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
8. Episode IDs are deterministic from `source_file`; podcast and episode title
   are a fallback only when that file key is absent. A source-file collision
   with inconsistent metadata is an error.
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

| Metric | Actual source-derived count |
| --- | ---: |
| Workbooks | 8 |
| Episodes/source files | 269 |
| Items | 14,397 |
| Focal items and assignment rows | 10,940 |
| Contextual items | 3,457 |
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
alter source truth to force a target count.

## Known source anomalies and governance state

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
pipeline does not manufacture membership.

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
cover required files, hashes, sheet/header contracts, unique IDs, category and
episode reconciliation, one primary assignment per focal item, controlled
secondary `NONE`, foreign keys, review/ambiguity retention, unmapped clusters,
theme/tension/synthesis references, and the seven-narrative discrepancy.

Generated content is serialized in memory and staged before existing valid
output is replaced. Any source, normalization, validation, or public-boundary
error aborts the write. Reproducible JSON uses UTF-8, sorted keys, fixed
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
positive field allowlists. It contains governed high-level entities, episode
labels, aggregate coverage/review/QA information, and semantic relationships.
It excludes:

- workbook files and workbook data blobs;
- full transcripts and full item corpus;
- unrestricted quotations or evidence-excerpt dumps;
- primary/secondary coding rationales;
- model, coder, prompt, and detailed run metadata;
- internal human notes and detailed review queues; and
- absolute paths or private source locations.

Adding a field to the internal schema never publishes it automatically. A
human-approved public allowlist change is required.

## Methodology cautions

1. This is a practitioner-discourse map, not a definitive taxonomy.
2. Counts indicate corpus discourse salience, not importance or consensus.
3. Extracted items are interpretive units, not independent observations.
4. Primary assignment records dominant analytic meaning.
5. Secondary assignment records substantive conceptual adjacency.
6. Primary/secondary co-occurrence is semantic, not causal.
7. A discourse cluster is not automatically a behavioral Driver.
8. A meta-cluster is a within-category family.
9. A cross-cutting theme connects patterns across categories.
10. A tension retains an unresolved tradeoff or competing assumption.
11. A meta-narrative is a high-level interpretive storyline.
12. A scenario is a plausibility exercise, not a forecast.
13. Model coding confidence is not scientific evidence strength.
14. Frequency is not consensus.
15. Higher-order synthesis must remain traceable to lower-level source IDs
    where the workbook lineage supplies them.
