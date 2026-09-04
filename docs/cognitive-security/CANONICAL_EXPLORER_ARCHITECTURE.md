# Canonical Cognitive Security Explorer architecture

## Purpose and interpretation

The PSYWERX Cognitive Security Practitioner Discourse Map is a dependency-free
static application at `/cognitive-security/`. It presents the approved
canonical synthesis of one practitioner podcast corpus. It is not a definitive
taxonomy, representative survey, scientific evidence review, consensus
measure, causal model, prevalence estimate, or forecast. It remains separate
from the PSYWERX Driver Ontology.

The governing interpretation appears wherever support is presented:

> Corpus support reflects recurrence and breadth within this practitioner
> discourse corpus. It does not indicate scientific validity, consensus,
> importance, prevalence, or real-world effect size.

No public feature turns the multidimensional support profile into a composite
score.

## Governed corpus and hierarchy

The public corpus contains 242 public-feed releases representing 241 unique
analytical recording/content units. Shared episode-83 content is counted once
analytically. The second public release remains available through a
`shared-content-inheritance` relationship that contributes no analytical
weight. The corrected canonical corpus contains 12,933 analytical items; item
records and text remain private.

The public hierarchy is:

```text
7 focal categories
  -> 50 canonical within-category families
    -> 127 stable clusters
      -> 242 public episode releases (241 analytical content units)
```

Cross-category synthesis consists of 11 flat themes, 20 canonical tensions,
five canonical narratives, 64 category findings, and six scenarios. Themes
have one public level. Findings comprise 50 family findings, seven integrative
category findings, and seven visually distinct open questions.

## Explorer views

The Explorer provides these primary modes:

1. **Overview** gives first-time visitors a short Start Here explanation and
   direct entry points to every major mode.
2. **Categories** presents Category -> Family -> Cluster navigation and embeds
   family findings, integrative findings, and open questions in each category.
3. **Themes** presents all 11 themes at one level and includes the accessible
   Category x Theme heatmap.
4. **Tensions** presents a filterable 20-row matrix with neutral, equally
   weighted poles.
5. **Narratives** exposes each narrative's integrative theme, tension, family,
   and category structure without using saturated corpus reach as its headline.
6. **Scenarios** presents six conditional plausibility exercises, never
   predictions. Scenario relationships are semantic and noncausal.
7. **Evidence Paths** traverses one relationship slice at a time from an entry
   entity toward families, clusters, and public releases, or in the useful
   reverse direction.
8. **Episodes** exposes the 242-release catalog and reviewed transcript-grounded
   summaries.
9. **Search** indexes only allowlisted canonical public records.
10. **Methodology** explains corpus governance, synthesis roles, support,
    provenance, privacy, and limitations.

## Public data contract

The browser fetches only files listed by
`data/cognitive-security/manifest.json`. Core entity files are loaded at
startup. Relationship and episode-provenance indexes are loaded only when a
detail or Evidence Paths interaction needs them.

The canonical package contains:

- `manifest.json`
- `categories.json`
- `families.json`
- `clusters.json`
- `cluster_summaries.json`
- `themes.json`
- `tensions.json`
- `narratives.json`
- `category_findings.json`
- `scenarios.json`
- `episodes.json`
- `episode_summaries.json`
- `heatmap.json`
- `relationship_semantics.json`
- `relationships.json`
- `provenance.json`
- `coverage.json`
- `qa_report.json`

The manifest is the closed inventory. A canonical build fails if an obsolete
JSON artifact remains in the public directory or if any expected file is
missing. Browser code never requests `analysis/`, `source-data/`, transcripts,
workbooks, or local paths.

## Public entity types and routes

| Entity type | Public collection | Stable ID field | Detail route |
| --- | --- | --- | --- |
| `category` | `categories.json` | `categoryId` | `?view=category&id=...` |
| `family` | `families.json` | `familyId` | `?view=family&id=...` |
| `cluster` | `clusters.json` | `clusterId` | `?view=cluster&id=...` |
| `theme` | `themes.json` | `themeId` | `?view=theme&id=...` |
| `tension` | `tensions.json` | `tensionId` | `?view=tension&id=...` |
| `narrative` | `narratives.json` | `narrativeId` | `?view=narrative&id=...` |
| `finding` | `category_findings.json` | `findingId` | `?view=finding&id=...` |
| `scenario` | `scenarios.json` | `scenarioId` | `?view=scenario&id=...` |
| `episode` | `episodes.json` | `episodeId` | `?view=episode&id=...` |

Top-level state also uses query parameters so deep links and refresh work on
GitHub Pages. Search uses `q`, `type`, `category`, `family`, and `cluster`.
Tension filters use type, category, theme, scenario, and support-breadth
parameters. Heatmap cell links preserve both category and theme context.

Navigation uses `pushState`; canonical normalization and safe compatibility
resolution use `replaceState`; `popstate` restores Back/Forward state. Copy
Link copies the normalized canonical URL.

Legacy higher-order records are never loaded or shown. An old link with one
governed successor may resolve silently to that canonical entity through a
privacy-safe compatibility resolver. A split, ambiguous, or unknown old link
opens the relevant canonical browse context with the unobtrusive message
"This link points to content that has been reorganized." No public migration
table or historical identifier is rendered.

## Two-layer support display

Every higher-order entity exposes support without a single score.

**Primary corpus support** may include direct item allocation, primary family
and cluster breadth, directly allocated tension evidence, primary category
breadth, direct content-unit breadth, and concentration. A value is omitted or
described as not independently coded when the governed source does not support
it.

**Broader traceable reach** is subordinate and progressively disclosed. It may
include secondary-family relationships, conceptual framing, future extension,
derived semantic relationships, and total reachable content units/releases.
The inherited episode-83 release can appear in release coverage but never
increases analytical counts.

The application does not use importance, consensus, evidence-quality, or
prevalence scores. Wide derived reach is not used as a narrative or scenario
headline.

## Category x Theme heatmap

The heatmap is a native table with all 11 themes and seven focal categories.
Every cell includes visible numeric text; color is supplemental. Each cell
reports the theme, category, primary family count, primary cluster count,
primary analytical content-unit breadth, and the interpretation caveat.

The deterministic normalized primary-support breadth stored in
`heatmap.json` is the arithmetic mean of three within-category shares, on a
zero-to-one scale:

```text
mean(
  primary families in cell / all families in category,
  primary clusters in cell / all clusters in category,
  primary content units in cell / content units supporting category
)
```

The Explorer multiplies that stored fraction by 100 only for percentage
display.

Only governed primary-theme support enters the numerator. Secondary support,
conceptual framing, future extension, and shared-content inheritance do not.
The measure normalizes category size and never substitutes raw item volume.
Activating a cell opens the relevant filtered support context.

The table has a caption, row and column headers, keyboard-reachable cell links,
a non-color value legend, and a labeled horizontal-scroll region for narrow
screens.

## Canonical tension matrix

The tension matrix groups all 20 tensions by governed analytical type and can
filter by type, category, theme, scenario, and direct support breadth. Both
poles use neutral presentation. Pole allocation describes direct evidence
lineage, not endorsement or a preferred answer. Detail pages retain definition,
assumptions, conditions favoring each pole, complementarity/false-dichotomy
caveat, supporting families and clusters, related themes and narratives,
scenario activation, support layers, and limitations.

## Evidence-path explorer

The Evidence Paths view reveals one adjacency slice at a time. It can enter
from any supported canonical entity and traverse useful directions along:

```text
Episode <-> Cluster <-> Family <-> Theme/Tension <-> Narrative <-> Scenario
```

Each connection exposes its governed semantic role, including
`direct-coded-support`, `primary-family-membership`,
`secondary-family-relationship`, `primary-theme-support`,
`secondary-theme-support`, `conceptual-framing`, `future-extension`,
`activated-tension`, `contextual-connection`, and
`shared-content-inheritance`. The interface uses no causal arrows. All scenario
relationships retain `causalClaim: false`.

## Search contract

The in-browser search index is constructed only from positive allowlists. It
indexes canonical family and cluster descriptions; theme and tension
definitions; tension poles; narratives; findings and open questions;
scenarios; and transcript-grounded episode summaries, key topics, and
why-it-matters text. It does not index private aliases, historical entities,
transcript text, evidence excerpts, item records, or migration lineage.

## Scenario governance

Scenarios are conditional plausibility exercises. Each detail exposes triggers,
pathways, branch points, indicators, counter-signposts, mitigating conditions,
related themes/tensions/families/scenarios, tension-pole dynamics, implications,
response options, research questions, limitations, and uncertainty.

SC-04, The Datafied Identity Bargain, carries a prominent public safeguard
notice: operational application or policy design requires additional review of
legal authorities, privacy, civil liberties, ethics, consent, and
affected-community perspectives. Its response options are analytical options,
not validated recommendations.

## Publication and privacy boundary

Canonical public data is rebuilt from fresh dictionaries using exact recursive
field allowlists. The projection excludes raw item IDs and text, transcript
text and paths, local paths, filenames, workbook metadata and hashes, source
identities, evidence excerpts, adjudication IDs and rationales, migration
tables, review queues and notes, prompts, models, credentials, and secrets.

The public provenance boundary ends at episode releases. Public summaries and
analytical relationships remain separate products:

```text
canonical transcript -> reviewed public episode summary

structured qualitative analysis -> canonical analytical relationships
```

No relationship is inferred from summary prose. Historical provenance remains
privately reproducible outside the public package.

## Accessibility and responsive behavior

- Semantic landmarks, headings, lists, tables, forms, buttons, and links retain
  native keyboard behavior.
- Focus is visible; loading, error, empty, and result states use restrained live
  regions.
- Heatmap values and relationship roles are available without color.
- Wide tables scroll inside labeled regions rather than causing page-level
  horizontal overflow.
- Layouts work at desktop, approximately 500 px, and approximately 390 px.
- Reduced-motion and forced-colors preferences are respected.
- Progressive disclosure does not hide required context or create focus traps.

## Performance and failure behavior

The application has no runtime framework, database, backend, or third-party
script. Core entity JSON loads in parallel and is cached. The former multi-
megabyte eager episode relationship artifact is not part of startup; compact
canonical relationships and release provenance load only when requested.

All fetched payloads are validated before the application becomes interactive.
A required-file failure produces a retryable error. An invalid entity link
produces a local recovery view and never fabricates a record.
