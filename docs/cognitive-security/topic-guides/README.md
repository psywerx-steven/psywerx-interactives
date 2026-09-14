# Topic Guides v1 — canonical curation, not another clustering pass

## Scope

The first 15 guides are selected editorial starting points. Existing records may
belong to zero, one, or several guides. There is no total-coverage target,
"missing home" error, catch-all category, or forced assignment.

The directory is `/cognitive-security/topic/`; each guide has a real static
`/cognitive-security/topic/<slug>/index.html`. Existing query-string Explorer
routes remain valid. The directory is linked as **Topic Guides** in the Explorer.

## Source authority and the corrected ID/name pairings

The baseline is main commit `eb6a1f3bd7da8d7908ccb0c2e7471b1e2cc7a66d`.
The source method must be `deduplicated-canonical-resynthesis` and content must
be `canonical-resynthesis`. This is the later, deduplicated analysis with
127 clusters, 50 reviewed primary families, 11 themes, 20 tensions, five
narratives, 64 findings, and six scenarios. The 242 public releases represent
241 analytical content units and 12,933 retained items. Raw items remain private.

The builder does **not** use the initial `master_extractions.xlsx` workbook,
retired clusters or synthesis products, summary embeddings, keyword co-occurrence,
the old discovery prominence gates, or a new whole-episode similarity ranking.
It does not redo clustering, change analytical weights, or infer relationships
from summary text.

`content/cognitive-security-guides/source_lock.json` freezes the current names
of **all 127 cluster IDs**, all 127 primary family assignments, the method and
counts, and hashes of every existing core/discovery JSON source. The builder
resolves displayed names from those canonical records. Authoring references
carry an expected canonical name and a field-specific fingerprint: a valid but
wrong ID/name pair fails rather than silently displaying incorrect information.

The previous chat table, not the canonical taxonomy, contained the shifted IDs.
The corrections now locked and regression-tested are:

| ID | Canonical name |
| --- | --- |
| KCFT-21 | Information Environment & Ecosystem Models |
| KCFT-22 | Targeting, Segmentation & Audience Analysis |
| KCFT-23 | Campaign Integration & Cross-Domain Synchronization |
| KCFT-24 | Innovation, Experimentation & Foresight |
| KCFT-25 | Organizational Learning & Talent Development |
| KCFT-26 | Platform, Algorithmic & Information Ecosystem Concepts |
| KCFT-27 | Campaigning & Persistent Competition Concepts |
| KCFT-28 | Human-Centered Security & Human Terrain Concepts |
| KCFT-29 | Cross-Domain & Integrated Competition Frameworks |
| KCFT-30 | Learning, Education & Cognitive Development Frameworks |
| OPP-05 | Campaigning, Targeting & Influence Operations |
| OPP-11 | Workforce, Talent & Human Capital |

The builder must never automatically refresh this lock to make a failure go away.
A later canonical source update requires checking its semantic changes, reviewing
the affected guide references/listening takeaways, and deliberately updating the
lock and fingerprints. This prevents a stale page from claiming fresh provenance.

## Two distinct kinds of curation

1. **Source-topic crosswalk:** core/supporting topics are places to look. They
   do not automatically admit every record or descendant to a guide.
2. **Explicit content admission:** each source card selects an existing public
   entity and exact source field, recurring-pattern heading, or bounded excerpt.
   The interpretation and relevance note are visible; canonical text is not
   rewritten into a new finding. Themes and narratives remain higher-order
   synthesis. Tensions retain both poles and their false-dichotomy caveat.

Featured episodes have two reviewed, source-cited editorial listening takeaways.
Their selection is independent of the similarity feature. A tag on a featured
card uses a positive existing **primary** episode-to-cluster coding relationship
and an already admitted guide topic. There is no two-item, 5%-prominence,
two-shared-topic, or score gate. Assessment retains Masick and Burgos; Cyber
retains Littell and Carley.

The reverse index is built only from explicit source-card/featured-episode
inclusion. It does not propagate through all related themes, families, or source
candidates. Its semantic label is
`explicit-curated-inclusion-not-analytical-support`. Unmapped entities show no
badge. Failure to fetch this optional index does not disable the Explorer.

## Public quotation boundary

The existing analytical package excludes raw excerpts and item records. This
feature introduces a small, separate allowlisted quote projection—not permission
to publish the transcript corpus or raw extraction records.

The release includes 15 brief, context-checked transcript excerpts, placed in
16 episode-card locations across the 15 guides. These were checked against
archived episode transcripts and their surrounding speaker turns; they have not
been independently checked against audio. The display says **Transcript excerpt**
and does not invent timestamps. The correct episode, speaker, text, publisher
URL, and verification basis are bound together in an excerpt-approval digest.
The digest is a change-detection guard, not cryptographic proof of human review.

Cards without an approved excerpt simply retain their cited listening takeaways.
`BUILD_REPORT.json` lists the 47 omitted quote placements. This is not a claim
that those episodes lack quotable material; no excerpt has been approved for
these cards in this build. No quotation was synthesized from an AI summary.

The private transcript locator, full text, raw file hashes, surrounding-turn
review notes, and historical item IDs are deliberately not part of this repository
change or the public guide package. Public episode links are resolved from the
existing verified publisher metadata, not guessed from guest names.

## Files and build

Authoring inputs live in `content/cognitive-security-guides/`; generated public
references live separately in `data/cognitive-security-guides/`. The existing
closed analytical/discovery packages remain byte-for-byte unchanged.

```sh
python scripts/build_topic_guides.py
python scripts/build_topic_guides.py --check
python -m unittest tests.cognitive_security.test_topic_guides -v
```

The standard-library compiler validates all inputs before writing. It generates
one shared-template directory and 15 guide pages, public ID references, an explicit
reverse index, the narrow quote projection, a manifest, and a build report.
Static HTML necessarily materializes the selected canonical prose for browsing
and sharing; that prose is not duplicated into manually maintained guide records.
The `--check` mode detects stale or unexpected outputs without changing them.

The page order is orientation, Start Here, corpus findings, concepts/frameworks,
challenges, practitioner approaches, tools/methods, tensions, and corpus
connections. A genuinely empty section is omitted rather than filled with weak
adjacency. Deterrence has no separately selected tools section in this build.
There is no Continue Exploring section and no separate Voices/Quotes section.
Each quote appears inside its episode card. Source titles, citations, and tags
are links to actual Explorer records or verified publisher episode pages.

A small additive `?view=finding&id=...` renderer exposes the already published
canonical findings that the previous app did not give their own detail view.
Legacy `category-finding` compatibility handling is unchanged. No finding text or
support is modified.

## Browser acceptance and sharing

The guide HTML is readable without JavaScript. Small enhancement scripts provide
copy-link fallback, directory filtering, and optional reverse guide tags in the
existing Explorer. No new runtime dependency, framework, database, or service is
required.

```sh
# Set to an already-installed Chrome/Edge/Chromium executable.
PSYWERX_BROWSER_EXECUTABLE=/usr/bin/chromium \
  python -m unittest tests.cognitive_security.test_topic_guides_browser -v
```

Browser tests cover all 15 guides at desktop and 390px, direct loading, canonical
source targets (including all selected findings), directory filtering, keyboard
navigation, no-JavaScript reading, copy-link, reverse tags, Back/Forward,
nonfatal overlay failure, unmapped records, and assets.

Every guide emits its own title, description, canonical URL, and Open Graph
metadata in the initial HTML. The preview image is the existing PSYWERX brand
asset; no per-guide illustration is claimed. Checking the generated tags/assets
is not the same as checking a deployed LinkedIn unfurl. This branch does not
merge, deploy, schedule posts, or publish to LinkedIn.
