# Topic Guides implementation and validation

Date: 2026-09-14

## Delivered scope

The first 15 curated topic guides, a searchable directory, an Explorer navigation entry, inline canonical citations and tags, explicit reverse guide links on admitted Explorer entities, static share URLs, and Open Graph metadata. One shared builder generates the directory and all guide pages.

- 15 guide pages, plus the directory.
- 63 featured-episode placements representing 62 unique episodes.
- 236 selected source-card placements from current canonical content.
- All 63 episode-card placements are quote-free and retain their cited listening notes.
- Quote collections, identifiers, rendering code, styling, and omission counters are removed. There is no separate Voices section and no Continue Exploring section.
- 65 canonical clusters have no displayed guide membership. This is valid and is not a coverage defect. These are the first guides, not an exhaustive partition.

## Source and method controls

The guide builder requires `deduplicated-canonical-resynthesis` and `canonical-resynthesis`, preserving the deduplicated evidence base and improved reviewed family assignments. It rejects initial-pass/noncanonical inputs. No original extraction workbook, transcript corpus, model call, embedding similarity, or network retrieval enters the ordinary guide build.

All 127 canonical ID/name pairs and primary-family assignments are checked against the source lock. Each selected source reference also carries the expected canonical name and a source-field digest. This catches a valid-but-wrong ID, stale prose, and accidental reuse of earlier erroneous chat mappings. Names displayed on pages are resolved from the canonical registry, not retyped as new taxonomy labels. The underlying registry itself was not wrong and has not been rewritten.

Topic-first, evidence-first editorial curation is separate from canonical clustering. Featured episodes and admitted source passages are explicit selections; the old whole-episode similarity calculation and its topic-prominence/shared-topic thresholds are not used as admission gates. Broad crosswalk topics only identify candidate sources, not automatic membership. Theme/family reach does not propagate guide tags to every reachable episode. Source-topic membership, public-guide inclusion, and canonical analytical relationships remain distinct.

All existing analytical/discovery JSON files are byte-for-byte unchanged. Counts, weights, canonical classifications, and existing similar-overall results are unchanged. Public provenance still ends at episode releases. The guides publish no transcript quotations, raw items, private source paths, or verification notes.

## Integration details

Each guide is a real static `cognitive-security/topic/<slug>/index.html` with canonical sharing metadata. The ordinary Explorer's query-string routes are retained. A small additive `view=finding` route renders already-published canonical findings that guide cards need to cite; it does not alter their content or the legacy category-finding compatibility behavior.

Optional guide tags fail independently of the core Explorer. The reverse index is generated only from explicit selections. The page contents remain usable without JavaScript; JavaScript adds directory search and copy-link convenience.

## Original implementation validation (before quote removal)

GitHub Actions run: https://github.com/psywerx-steven/psywerx-interactives/actions/runs/34871892109

Implementation commit: `efa6214ce9b43ebfc30b38b58f2f95a9a672335e`

- Deterministic build followed by `--check`: passed.
- 34 new guide unit/contract tests: passed.
- 49 existing Explorer/discovery/site-navigation regression tests: passed.
- Combined unit/regression run: 83 tests, no skips, passed in 1.552 seconds on the runner.
- Real-browser acceptance: 14 tests, no skips, passed in 24.883 seconds on standard GitHub-hosted Chrome.
- Browser coverage includes all 15 pages at 1360 px and 390 px, directory filtering, source/finding deep links, reverse tags, back/forward, optional-overlay failure, copying canonical URLs, keyboard/skip navigation, JavaScript-disabled content, unmapped entities, main-navigation entry, stale-tag prevention, and asset loads.
- Protected analytical/discovery directories: no diff.
- Local/runner generated guide content and authoring-file parity: confirmed.

Local Chromium could render in-memory HTML for visual/component review but blocked HTTP navigation with `ERR_BLOCKED_BY_ADMINISTRATOR`. Those local attempts are not counted as passing navigation tests. Full HTTP browser validation was performed on the standard GitHub Actions runner instead.

The temporary checksum-verified source-transport workflow and its five transport chunks were removed after materialization. The retained validation workflow uses read-only repository permissions and does not modify branches or deploy.

## Publication limitations

This implementation is prepared for review, not merged or deployed by this task. The static Open Graph tags are validated; a live LinkedIn unfurl/Post Inspector result has not been checked. Topic relevance and listening takeaways are editorial judgments, not scientifically validated rankings or claims of guest consensus.

## Citation-only revision

On 2026-09-14 the user approved the design, requested removal of the quotations,
and authorized continuation. The quote feature is removed completely, not hidden.
Source selection, all 127 ID/name locks, reviewed primary-family assignments,
source citations, featured listening takeaways, and core/discovery data are unchanged.
The original four quote tests are replaced with quote-absence, forbidden-field,
asset-removal, and citation-preservation tests. Desktop/mobile acceptance now
asserts zero quotation blocks on all 15 guides. The schema for changed guide
records is 1.1; the unchanged directory/reverse-index formats remain 1.0.

The existing run above documents the original implementation. The final PR's
checks and subsequent deployment record establish validation/publication of this
revision; the original run is not presented as a test of later changes.
