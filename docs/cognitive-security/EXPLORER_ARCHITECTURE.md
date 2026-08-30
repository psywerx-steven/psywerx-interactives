# Cognitive Security Explorer architecture

## Status and purpose

This document defines the Phase 2 public information architecture and browser
contract for the **PSYWERX Cognitive Security Practitioner Discourse Map**. The
Explorer is a dependency-free static application at
`/cognitive-security/`, backed only by the governed public files in
`data/cognitive-security/`.

The Map presents recurring concepts and higher-order syntheses found through a
human-guided, AI-assisted qualitative analysis of practitioner discourse. It is
not a definitive taxonomy, a representative survey, a consensus measure, a
causal model, a validated competency framework, or a scientific evidence
ranking. It is also separate from the PSYWERX Driver Ontology: discourse
clusters are not behavioral Drivers, and no cross-product identity or causal
mapping is implied.

The governing data contract is documented in
[Cognitive Security Schema v1.0](./COGNITIVE_SECURITY_SCHEMA_V1.md). Source
selection, transformation, and publication boundaries are documented in
[Build and Provenance](./BUILD_AND_PROVENANCE.md), with current build results in
the [Ingestion Report](./INGESTION_REPORT.md).

## Information architecture

The Explorer has eight primary modes:

1. **Overview** introduces the product, corpus coverage, analytical hierarchy,
   cautions, and major entry points.
2. **Browse** supports the focal hierarchy Category -> Meta-cluster ->
   Intermediate cluster while retaining governed exceptions.
3. **Cross-Cutting Themes** presents the eleven themes that connect concepts
   across categories.
4. **Tensions & Debates** presents all thirty tensions through a neutral
   two-pole structure.
5. **Meta-Narratives** presents the seven records in the canonical source.
6. **Future Scenarios** presents six plausible scenarios, each explicitly
   labeled as a scenario rather than a prediction.
7. **Search** searches the public package, not transcripts or the private item
   corpus.
8. **Methodology** explains the corpus, analytical process, human and
   AI-assisted roles, traceability, and interpretive limits.

The seven focal categories are the main Browse entry points. The three
contextual extraction categories remain visible in corpus scope and
methodology, but the interface must not make them appear to have missing
cluster data.

The principal within-category hierarchy is:

```text
Episode / extracted material
  -> Category
    -> Meta-cluster
      -> Intermediate cluster
```

Cross-cutting themes, tensions, meta-narratives, category findings, and
scenarios are higher-order synthesis layers. They connect to the hierarchy
where governed IDs support the connection; they do not form one strict tree.

## Public data contract

The Explorer may fetch only files named by
`data/cognitive-security/manifest.json`. The current package comprises:

- `categories.json`
- `clusters.json`
- `cluster_summaries.json`
- `meta_clusters.json`
- `themes.json`
- `tensions.json`
- `meta_narratives.json`
- `category_findings.json`
- `scenarios.json`
- `episodes.json`
- `relationships.json`
- `coverage.json`
- `review_summary.json`
- `qa_report.json`
- `manifest.json`

Browser URLs must be relative to the application and repository so the same
assets work on localhost and beneath the GitHub Pages repository path. Browser
code must never request `analysis/`, `source-data/`, an XLSX workbook, or any
other ignored/private artifact.

Loaded datasets are cached in memory. Lookup maps and sets are created once for
IDs and common relationships; the search index is also created once after
loading. Rendering and filter operations should use those indexes rather than
repeated full-dataset scans.

## Canonical public entity types

These names are the closed public entity-type vocabulary used by URL state,
cross-navigation, and relationship endpoints:

| Entity type | Public collection | Stable ID field |
|---|---|---|
| `category` | `categories.json` | `categoryId` |
| `cluster` | `clusters.json` | `clusterId` |
| `metaCluster` | `meta_clusters.json` | `metaClusterId` |
| `theme` | `themes.json` | `themeId` |
| `tension` | `tensions.json` | `tensionId` |
| `metaNarrative` | `meta_narratives.json` | `narrativeId` |
| `categoryFinding` | `category_findings.json` | `findingId` |
| `scenario` | `scenarios.json` | `scenarioId` |
| `episode` | `episodes.json` | `episodeId` |

Source-native labels such as `cross_cutting_theme` and `meta_cluster` remain
valid inside the normalized private data model, but they are not public
relationship endpoint types.

## URL and deep-link contract

The app uses query parameters instead of path routing so direct links and page
reloads work on static GitHub Pages.

The base route is:

```text
/cognitive-security/
```

Top-level view state uses `view`:

```text
?view=overview
?view=browse
?view=themes
?view=tensions
?view=narratives
?view=scenarios
?view=search
?view=methodology
```

A selected entity uses a detail-specific `view` route and its stable `id`.
There is no separate `entity` query parameter:

```text
?view=category&id=CAT-...
?view=meta-cluster&id=CRB-M01
?view=cluster&id=CRB-01
?view=theme&id=XTHEME-001
?view=tension&id=TD-001
?view=meta-narrative&id=N01
?view=category-finding&id=CRB-F01
?view=scenario&id=S01
```

An episode may use the auxiliary detail route `?view=episode&id=EPI-...` when
episode detail navigation is exposed.

Search uses this parameter contract:

```text
?view=search&q=&type=&category=&meta=&cluster=
```

Search and filter state uses `q`, `type`, `category`, `meta`, and `cluster`.
Selections within one facet use OR semantics; different facets combine with
AND semantics.

All parameter values are URL-encoded. Selecting a new view or entity adds a
history entry; initialization and normalization of equivalent state may
replace the current entry. The app listens for `popstate`, so Back and Forward
restore the prior mode, filters, and selected entity without reloading data.

On reload, valid state is restored after public data and indexes are ready. An
unknown view falls back to Overview. A known detail route with an unknown ID
shows a non-destructive not-found state in the requested view, offers a way
back to that view's index, and does not throw or fabricate a record. Optional
or unsupported parameters are ignored safely.

## Semantic relationship rules

Relationships provide cross-navigation and describe source-supported semantic
connections. They do not represent causation, direction of influence, effect
size, endorsement, consensus, or scientific evidence.

The public relationship vocabulary is:

| `relationshipType` | `sourceType` | `targetType` |
|---|---|---|
| `cluster-belongs-to-category` | `cluster` | `category` |
| `meta-cluster-belongs-to-category` | `metaCluster` | `category` |
| `cluster-belongs-to-meta-cluster` | `cluster` | `metaCluster` |
| `theme-connects-meta-cluster` | `theme` | `metaCluster` |
| `theme-supported-by-cluster` | `theme` | `cluster` |
| `tension-maps-to-cross-cutting-theme` | `tension` | `theme` |
| `tension-maps-to-meta-cluster` | `tension` | `metaCluster` |

Public language should use **semantic relationship**, **connected to**,
**mapped to**, and **supported by**. It must not substitute **causes**,
**drives**, or **effect**. Counts are labeled **Corpus coverage** or discourse
salience, never importance, consensus, prevalence, or scientific support.
Likewise, source synthesis confidence and within-corpus evidence labels must
not be presented as scientific evidence strength.

## Governed unresolved records

The interface treats known source conditions as governed information, not as
data to repair in the browser:

- `CRB-M05` is a valid meta-cluster with no source-authored cluster mappings.
  It remains visible with an unobtrusive unresolved-source-mapping note. It is
  not rendered as an ordinary empty family, and the Explorer invents no
  members.
- `CRB-10`, `FTP-13`, and `KCFT-20` are valid intermediate clusters without a
  meta-cluster assignment. Each remains discoverable on its Category page
  under **Unmapped clusters retained for review**.
- Three source theme/cluster evidence placeholders have no canonical cluster
  ID. They remain in QA and methodology information only and never generate a
  fake cluster link.
- Empty narrative or scenario tension-ID arrays remain empty. Similar wording
  is not used to infer a link.
- The canonical source contains seven meta-narratives although earlier project
  documentation referenced eight. The Explorer displays seven and explains
  the discrepancy briefly in Methodology.
- Missing optional scalars and empty lists produce an honest omitted or empty
  state. They do not produce blank controls, broken links, or invented text.

The QA package is the authoritative source for governed unresolved-state
labels. UI code should not duplicate ontology decisions or use absence alone
to determine whether a record is unresolved.

## Evidence and publication boundary

Phase 2 does not publish or load the private item corpus, transcripts,
quotations, evidence excerpts, speakers, assignment rationales, internal
notes, or detailed review queues. Episode titles and aggregate corpus counts
are public because they support navigation and coverage context without
exposing item-level material.

Where evidence access would otherwise be expected, Methodology may state:

> Source-linked item and quotation browsing is being held for a separate
> publication and attribution review.

The Explorer must not show disabled evidence controls or imply that private
evidence is available. Expanding this boundary requires a separate governed
publication decision and data contract.

## Accessibility expectations

- Use semantic landmarks, headings, lists, buttons, and form labels.
- Maintain complete keyboard access and clearly visible focus indicators.
- Dialogs or drawers use an accessible name, appropriate dialog semantics,
  Escape-to-close, contained focus while open, and focus restoration to the
  invoking control.
- Announce loading, error, empty, and result-count changes without creating
  noisy live regions.
- Expose selected and expanded state with native semantics or appropriate
  `aria-*` attributes.
- Preserve sufficient color contrast and never encode entity type, evidence
  status, or selection by color alone.
- Respect `prefers-reduced-motion` and avoid motion required for comprehension.
- Keep long-form text readable and prevent horizontal page overflow at mobile
  widths. Wide structures must reflow, scroll within a labeled region, or use
  a stacked alternative.
- Progressive disclosure should present an understandable overview before
  opening dense detail.

## Performance and failure behavior

- Use no framework, runtime database, or unnecessary third-party script.
- Fetch public JSON in sensible parallel groups and cache it for the session.
- Build ID, hierarchy, relationship, filter, and search indexes once.
- Batch DOM updates and avoid repeated full-list scans during rendering.
- Keep filters and search responsive at the current corpus size; debounce only
  where it materially reduces redundant work.
- Display an intentional loading state while the initial package is fetched.
- A failed required request produces a useful retryable error without leaving
  partially interactive controls.
- Missing optional fields and governed unresolved records degrade locally and
  do not prevent the rest of the Explorer from loading.

## Current Phase 2 scope

The Phase 2 MVP covers the eight primary modes, responsive Category ->
Meta-cluster -> Cluster browsing, substantial entity details, public-package
search, focused facets, semantic cross-links, corpus coverage, stable query
deep links, and a public Methodology experience.

It intentionally does not include transcript search, item-level evidence,
quotation browsing, a force-directed or causal graph, AI-generated content, a
runtime backend, or integration with the PSYWERX Driver Ontology.
