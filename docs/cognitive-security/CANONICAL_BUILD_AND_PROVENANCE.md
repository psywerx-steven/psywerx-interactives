# Canonical Cognitive Security build and provenance

## Scope

This is the active build contract for the canonical public Cognitive Security
Practitioner Discourse Map. The public site is a static projection of an
approved private analytical package. Private canonical analysis remains the
reproducible source of truth; its draft JSON is never copied directly into the
public directory.

The corpus contains:

- 242 canonical public-feed releases;
- 241 unique analytical recording/content units;
- 269 historical source identities preserved privately;
- 12,933 corrected canonical analytical items: 9,822 focal and 3,111
  contextual;
- 127 retained clusters organized into 50 canonical families;
- 11 flat themes, 20 tensions, five narratives, 64 findings, and six
  scenarios.

Corpus support reflects recurrence and breadth within this practitioner
discourse corpus. It does not indicate scientific validity, consensus,
importance, prevalence, or real-world effect size.

## Source authority

The public projector reads three governed inputs:

1. the approved private canonical re-synthesis checkpoint;
2. the private normalized Cognitive Security release used to reconstruct
   safe aggregate support and release provenance;
3. the frozen, reviewed public episode summaries.

The projector treats the private locations as read-only. It writes generated
analysis only beneath the canonical worktree and public artifacts only beneath
`data/cognitive-security/`. It does not read unfinished parallel reanalysis
work as a fallback and does not modify source workbooks, transcripts, or other
worktrees.

## Approval gate

The private analytical records deliberately retain draft/review status. Public
promotion is a separate explicit action. The projector requires the approved
analytical checkpoint identity and verifies the governed method, counts, and
invariants before constructing fresh public records. A mismatch fails before
any public file is replaced.

Public records use canonical status only in the public projection. This does
not rewrite or erase private analytical review history.

## Canonical selection and episode-83 inheritance

Historical aliases and duplicated content do not contribute duplicate
analytical weight. Selection retains one representation for each of 241
analytical content units and 12,933 items.

Both public episode-83 releases remain in the catalog. The original content
representation carries the governed support relationships. The second release
has one `shared-content-inheritance` relationship, with
`contributesAnalyticalWeight: false`, and receives no copied direct cluster or
tension evidence edges. It may be shown as inherited public release coverage,
but it cannot increment item, cluster, content-unit, pole, or other analytical
support counts.

## Projection boundary

The projector builds every public record from an explicit positive allowlist
and recursively validates exact nested shapes and JSON types. It excludes:

- raw item IDs and item text;
- transcript text, paths, and hashes;
- local paths, source filenames, workbook names, worksheet data, and source
  fingerprints;
- historical source-identity ledgers;
- evidence excerpts and private quotations;
- historical-to-canonical migration tables and identifiers;
- private adjudication IDs, decisions, rationales, allocation tables, review
  queues, flags, and notes;
- prompts, model metadata, credentials, secrets, and machine-local metadata.

Episode IDs, cluster IDs, canonical entity IDs, reviewed summary prose, safe
aggregate counts, and governed semantic roles are public only because they are
needed for navigation and interpretation.

## Public artifacts

`manifest.json` is the sole file inventory. The public package contains core
entities, a documented 77-cell heatmap, a compact semantic relationship graph,
and lazy release provenance. Obsolete higher-order records and the former
large eager episode relationship file are not retained.

The projection is atomic: it builds and validates all payloads in memory,
serializes them deterministically, verifies unchanged-input byte identity, and
only then replaces the public package. A validation failure leaves the prior
valid package intact. Files not in the canonical manifest are rejected and
removed only as part of the validated cutover.

The legacy `build_cognitive_security.py` pipeline remains available for private
historical reconstruction, but it must fail closed rather than overwrite a
canonical public manifest. Canonical publication is performed only through
`build_canonical_public.py`.

## Support model

Support is multidimensional and has no composite score.

The public `primarySupport` layer contains only governed direct or primary
measures that exist for the entity: directly allocated items, primary families
and clusters, direct content-unit breadth, primary category breadth, pole
allocation, and concentration.

The subordinate `broaderTraceableReach` layer may contain secondary support,
conceptual framing, future extension, derived semantic reach, total reachable
content units, and inherited public-release coverage. Broad reach is useful
for provenance but is not a headline measure for saturated themes, narratives,
or scenarios.

## Relationship construction

The semantic graph is rebuilt from governed canonical identifiers. Each record
has resolvable public endpoints, a closed semantic role, and an explicit
`causalClaim` Boolean. Current scenario relationships always use
`causalClaim: false`.

Public paths can move among episodes, clusters, families, themes, tensions,
narratives, findings, and scenarios. They stop at public releases. Relationship
direction organizes traversal; it does not imply causal direction. No edge is
created from lexical similarity or from episode-summary prose.

## Heatmap normalization

The Category x Theme heatmap contains 77 cells. It uses normalized primary
support breadth, not raw item count. For each theme/category cell, the stored
zero-to-one value is:

```text
mean(
  primary-family share within category,
  primary-cluster share within category,
  primary-content-unit share within category
)
```

The browser converts the stored fraction to a percentage for display.

The three denominators are respectively all families, all clusters, and all
supporting analytical content units in that category. Only the governed
primary-theme-support role enters the numerator. Secondary support,
conceptual framing, future extension, and inherited releases are excluded.
Values are deterministically rounded and accompanied by their component
counts, so they are auditable and usable without color.

## Scenario safeguards

Scenarios are conditional plausibility exercises, not predictions. Their
relationships are noncausal. SC-04, The Datafied Identity Bargain, carries a
prominent public notice requiring additional review of legal authorities,
privacy, civil liberties, ethics, consent, and affected-community perspectives
before operational application or policy design. Its response options are not
validated recommendations.

## Episode summaries and analytical relationships

The site preserves two separate products:

```text
canonical transcript -> reviewed public episode summary

structured qualitative analysis -> canonical analytical map relationships
```

The frozen 242-record summary set was generated from privately governed
canonical transcripts and review-gated separately. The canonical public build
validates and reuses it; the build does not call an API or generate new summary
prose. Analytical relationships come from the corrected structured analysis,
not from summary language.

## Validation and QA

Canonical publication requires:

- exact corpus and entity counts;
- one nonempty primary family for every cluster;
- one public theme level;
- complete endpoint resolution and closed semantic roles;
- noncausal scenario edges;
- zero inherited analytical weight;
- exact recursive public schemas and privacy/secret scans;
- 77 correctly normalized heatmap cells;
- zero unresolved redundancy and no orphan or self-supported entity;
- byte-identical repeated builds from unchanged inputs;
- static Explorer tests and browser checks at desktop, approximately 500 px,
  and approximately 390 px.

The standard Python suite is:

```powershell
py -m unittest discover -s tests/cognitive_security -p "test_*.py"
```

Use `py scripts/build_canonical_public.py --help` for the current explicit
input and approval arguments. The build command is intentionally not given
implicit machine-specific source paths.

## Limitations

- One practitioner podcast corpus is not representative of the full field or
  affected populations.
- Extracted analytical items are interpretive units, not statistically
  independent observations.
- Results depend on corpus scope, extraction, codebook, prompts, models,
  mapping decisions, and human synthesis.
- AI assistance can introduce omissions, prompt sensitivity, semantic
  smoothing, overgeneralization, and hidden bias.
- Coding confidence and review status are workflow signals, not scientific
  evidence strength.
- Semantic co-occurrence and relationship paths do not establish causation,
  direction, effect size, endorsement, or policy validity.
- Higher-order entities are progressively farther from source material and
  should be interpreted with their published boundaries and limitations.
- Scenarios are structured plausibility exercises, not probabilities,
  forecasts, or validated recommendations.
