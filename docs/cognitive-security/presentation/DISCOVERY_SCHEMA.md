# Cognitive Security presentation and discovery overlay

The Phase A overlay adds bibliographic metadata and deterministic browsing aids
without changing the 18-file Cognitive Security analytical package. It does not
create evidence relationships, revise support, or change any entity assignment.

## Public files

The exact supplemental allowlist is declared by
`data/cognitive-security-discovery/discovery_manifest.json`:

- `episode_metadata.json` contains one record for each public release with only
  `episodeId`, nullable `publishedAt`, nullable `guests`, and nullable
  `officialEpisodeUrl`.
- `episode_discovery.json` contains qualified main-topic IDs and explained
  overall-neighbor results for every public release.
- `topic_episode_index.json` supports topic-specific episode browsing.
- `similarity_data.json` contains normalized sparse topic vectors and document
  frequencies. It is loaded only when a reader opens the comparison tool.
- `presentation_copy.json` contains the small public entry-point copy overlay.

The manifest records each file's byte length and SHA-256 digest. Public records
may contain only existing public episode/topic identifiers and the fields above.
They contain no transcript text, item identifiers, local paths, source
filenames, private mappings, review notes, prompts, or credentials.

## Frozen publisher metadata

The metadata projection was matched to the Information Professionals
Association's official Cognitive Crucible archive. A unique episode number is
a strong candidate key, but its catalog and publisher titles must also be
compatible. Compatibility is recorded in the private audit and is limited to
exact normalized titles, safe title prefixes, or structured guest/topic
agreement that permits punctuation and shortened-name differences. Three known
spelling/transcription discrepancies are governed by an explicit
episode-number and official-post-ID exception allowlist with a recorded reason.
A materially conflicting numbered title remains unresolved. A unique exact
normalized-title match may be used when a catalog record has no usable episode
number. Publication dates are publisher post dates, not recording dates. Guest
lines are taken only from the official title's text before an explicit “on”
delimiter. Ordinary builds never request the web.

The frozen projection has 242 records: 237 verified official URLs and publisher
dates, 229 verified guest lines, and 5 deliberately null source matches. Missing
values remain unavailable rather than being inferred. Private source-field and
unresolved-match audit details remain in the ignored analysis workspace.

## Main-topic policy

For an episode-topic aggregate, the existing saved weight is verified as:

`weighted count = 2 × primary item count + secondary item count`

A topic qualifies for default discovery only when it has at least two primary
items and at least 5% of the episode's total saved weighted topic count. Topics
are ranked by weighted prominence with stable ID tie-breaking. Up to six appear
initially; all qualified topics remain available and feed similarity. This rule
creates 699 qualified topic assignments across 241 unique content units; 225 of
242 release pages have at least one qualifying topic.

The 5% choice was compared with 3%, 7.5%, and 10% across 16 varied releases.
Three percent commonly exposed 6–10 topics; 7.5% left 120 content units with no
qualifying topic; 10% left 200 empty. Five percent kept a focused median of
three topics while preserving honest sparse states. This is a calibrated
presentation rule, not a scientifically validated cutoff.

## Similar-overall policy

Similarity uses the 241 unique content units. Qualified topic weights receive:

`idf(topic) = 1 + ln((N + 1) / (df(topic) + 1))`

Each content-unit vector is normalized to sum to one. Similarity is weighted
Jaccard: the sum of per-topic minima divided by the sum of per-topic maxima.
Results require at least two shared qualified topics and a score of at least
0.15, then show at most six neighbors with the top shared topic names. The 0.15
floor removes roughly the weakest tenth of otherwise eligible overlaps without
changing the set of content units that have at least one qualifying neighbor.
It was checked against boolean Jaccard and an IDF-only baseline.

Empty vectors have unavailable similarity. Self matches and every catalog
release representing the same content unit are excluded. The Episode 83
re-release inherits its original content profile but can never recommend the
original recording or add analytical weight. Similarity describes topic overlap
for navigation; it does not imply agreement, importance, truth, or causation.

## Reproduction

`scripts/build_cognitive_security_discovery.py` rebuilds and validates the
overlay offline from the public core package and frozen metadata file. The
separate `scripts/freeze_cognitive_security_episode_metadata.py` projects an
explicitly acquired official cache; it is not part of the ordinary build.
