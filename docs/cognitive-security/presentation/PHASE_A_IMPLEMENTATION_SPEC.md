# Phase A presentation and discovery specification

This tracked checklist governs the presentation-only refinement of the Cognitive
Security Explorer. It does not change the canonical corpus, ontology, evidence
allocations, support measures, transcript-grounded summaries, or relationship
semantics.

## Protected baseline

- Preserve 242 public releases and 241 analytical content units.
- Preserve 12,933 selected items: 9,822 focal and 3,111 contextual.
- Preserve 7 categories, 50 families, 127 clusters, 11 peer themes, 20
  tensions, 5 narratives, 64 findings/open questions, and 6 scenarios.
- Preserve Episode 83's two catalog releases, one analytical weight, and
  non-weighted shared-content inheritance.
- Preserve tension Pole A/B provenance and cluster-only
  `direct-coded-support`; all public connections remain noncausal.
- Keep internal entity keys, identifiers, bookmarked routes, the 18-file core
  package, Driver Explorer, shared site configuration, and private analysis
  unchanged.

## Presentation checklist

- [x] Install all 11 supplied PNG/WebP icon pairs and a public-safe registry.
- [x] Use a reusable icon component on entry tiles, overview nodes, and
  restrained headings with real text labels and explicit image dimensions.
- [x] Remove duplicate titles/opening prose and make detail routes prose-first.
- [x] Use public labels Category, Subcategory, and Topic without changing
  internal category/family/cluster keys.
- [x] Move support metrics and formal role details into one optional
  Analytical details disclosure per applicable page.
- [x] Keep substantive limitations, neutral tension framing, and the full SC-04
  safeguard accessible without repeated boilerplate.
- [x] Implement a real clickable, keyboard-usable overview that distinguishes
  episodes, hierarchy, cross-cutting interpretations, synthesis/exploration,
  findings/questions, and utilities without implying causality.
- [x] Implement embedded Category -> Subcategory -> Topic browsing with
  independent disclosure and navigation controls, descendant search reveal,
  stable routes, and restored expansion state.
- [x] Default Themes and Tensions to readable prose cards; retain their matrices
  as optional comparison views.
- [x] Make episode cards native links and add range, query, oldest/newest, jump,
  trailer/nonnumbered, browse-context, previous/next, and return-state behavior.
- [x] Omit redundant episode-card labels, keep one prominent publisher action,
  and use practitioner-facing discovery copy in the default reading flow.
- [x] Add a frozen, validated metadata overlay with nullable publication date,
  guests, and verified official publisher URL; require title compatibility for
  numbered candidates, audit governed exceptions, and never guess missing values.
- [x] Add a separate deterministic discovery overlay for calibrated main topics,
  topic indexes, explained similar episodes, and a lazy optional comparison
  matrix. Discovery links never become analytical evidence edges.
- [x] Keep full provenance accessible while foregrounding qualified topics and
  allocated tension evidence in ordinary episode reading.
- [x] Validate zero/sparse/tie/shared-content/number-gap/unknown-metadata cases.
- [x] Test routes, native links, history, keyboard, touch, reduced motion,
  forced colors, zoom, responsive overflow, assets, errors, privacy, secrets,
  deterministic regeneration, and core-package preservation.
- [x] Measure core/discovery/icon bytes and initial/lazy request behavior.
- [x] Keep the completed changes isolated to the presentation feature branch
  and prepare one unmerged pull request against `main`.

## Discovery policy

The initial calibration candidates are `primaryItemCount >= 2` and within-
episode weighted share thresholds 0.03, 0.05, 0.075, and 0.10, using
`governedWeightedCount = 2 * primaryItemCount + secondaryItemCount`. The final
threshold is selected after a documented review of at least 12 varied releases.
Up to six qualifying topics appear initially; all qualifying topics remain
available and feed similarity.

Similarity is a deterministic weighted Jaccard over unique analytical content
units. Qualified topic weights receive the documented inverse-document-frequency
adjustment and within-unit normalization. Recommendations exclude self and
shared-content duplicates, require at least two shared qualifying topics for
"Similar overall," show at most one preferred release per candidate content
unit, and explain overlap with actual shared topics. Empty profiles remain
unavailable. Topic-specific discovery is labelled separately.

## Publication boundary

Supplemental public artifacts use exact allowlists and public identifiers only.
They contain no item identifiers or text, transcripts, local paths, source
filenames, private mappings, credentials, prompts, review notes, or new
analytical claims. Metadata acquisition is a separate cached process; ordinary
builds and page loads are offline and deterministic.
