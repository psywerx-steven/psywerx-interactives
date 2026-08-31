# Cognitive Security corpus reconciliation

## Decision summary

The historical extraction dataset contains 269 transcript/source identities,
not 269 independent public releases. A deterministic forensic reconciliation
supports **242 canonical public-feed episode releases** without changing the
source workbooks or forcing the result arithmetically.

The reconciliation found:

| Disposition | Source identities | Canonical episodes |
| --- | ---: | ---: |
| One-to-one unique identities | 215 | 215 |
| Confirmed modern/legacy alias members | 52 | 26 |
| Confirmed episode-186 precursor/recording alias members | 2 | 1 |
| Likely, ambiguous, or unresolved identities | 0 | — |
| **Total** | **269** | **242** |

Twenty-six confirmed pairs are the modern and legacy file-naming variants for
episodes 2 through 27. The twenty-seventh links the `IPA Brown Bag Vygotsky
Inner Speech with Rod Korba` source recording to public episode 186. In every
group, the public-feed identity is the canonical representative for
sensitivity analysis. All original source identities and items remain
preserved.

The unit being counted is a distinct public-feed episode release. `#000
Trailer` is therefore retained as episode 000. The episode 83 re-release is
also retained as a distinct feed release even though private transcript review
shows content reuse. A stricter unique-recording/content count would be 241;
this alternate unit is a documented limitation, not the public corpus metric.

## Scope and evidence available

The audit used the eight immutable canonical XLSX artifacts, the repository's
normalized data, workbook provenance, and locally available project
documentation, extraction-method materials, and transcript/source artifacts.
Transcript comparison was performed privately where it materially clarified
identity, including the episode-186 precursor and the episode-83 re-release.
Transcript text, detailed comparison evidence, and hashes are not published.

The accessible source-material inventory also documents two raw source names,
episodes `#109` and `#127`, for which corresponding normalized transcript
artifacts were not present, and a name change for episode `#73` between raw and
normalized conventions. These are source-lineage limitations, not reasons to
invent or delete episode records. The build relies on the canonical workbook
provenance it can actually inspect.

Raw transcripts, source-file inventories outside the governed public
allowlist, normalized comparison strings, detailed pair evidence, transcript
hashes, and source-level item records remain private. The existing public
provenance contract uses opaque `ART-*` identifiers, canonical roles, and safe
aggregate QA only; it does not expose source-workbook filenames, exact source
hashes, worksheet names, workbook content, or local paths. No API key, token,
or credential is part of the reconciliation data or public package.

## What was reconciled

Schema v1.0 used one deterministic `episodeId` per `source_file`. That was an
accurate source-identity key but an inaccurate label for a public-feed release.
Schema v1.1 keeps that historical ID as `sourceIdentityId` and adds a separate
canonical episode model:

```text
canonical episode
  -> one or more source identities
       -> extracted items
```

This preserves three truths at once:

1. the workbooks analyzed 269 historical source identities;
2. the best-supported public-feed corpus contains 242 episode releases; and
3. the original 14,397-item analysis must remain reproducible.

## Forensic method

Each source identity was compared using only deterministic, auditable signals:

- governed leading episode-number patterns in the source title and filename;
- normalized titles after removal of the episode-number convention;
- normalized source basenames;
- meaningful title-token overlap;
- modern versus legacy filename conventions;
- numbering continuity; and
- source-level item and focal/contextual counts for impact analysis.

Fuzzy matching alone never confirms an alias. A numbered pair is confirmed
only when a single legacy identity and a single modern identity share an
episode number in the governed 2–27 range and their normalized title tokens
corroborate the same episode. Exact title equality is sufficient corroboration
but is not required when the number and distinctive title/guest tokens agree.
The one non-numbered confirmation required stronger evidence: the source
transcript explicitly describes the recording as material to be edited into
the podcast, and private content comparison strongly matches public episode
186.

Potential states are:

- `unique` — retained one-to-one;
- `confirmed-alias` — definitive enough for the governed sensitivity
  selection;
- `likely-alias` — strong candidate, kept separate pending review;
- `ambiguous` — competing or conflicting evidence;
- `unresolved` — insufficient evidence; and
- `excluded-non-episode` — a governed source identity that is not an episode.

An unexpected pair cardinality, insufficient title corroboration, or
conflicting number evidence creates a private review-queue record. None occurs
in the current reconciled release.

## Why the count is 242

The result is supported by identity evidence rather than by subtracting until
a target is reached:

- 26 legacy `The Cognitive Crucible Episode NNN ...` identities are confirmed
  aliases of their modern `#N ...` public-feed identities for episodes 2–27;
- the `IPA Brown Bag Vygotsky Inner Speech with Rod Korba` source is confirmed
  as a precursor/recording alias of public episode 186; and
- the other 215 source identities each represent a distinct public-feed
  release under the declared unit, including episode 000 and the episode 83
  re-release.

Thus the 269 historical identities contain 27 alias identities beyond the 242
canonical public-feed releases. Re-release wording alone is not enough to
collapse a record. The content-equivalent episode 83 release stays distinct
because the governed unit is the public feed release; counting unique
recordings/content instead would yield 241.

## Sensitivity dataset and counts

The **reconciled sensitivity dataset** selects one source identity per
confirmed canonical episode. It excludes one alias member from every confirmed
group while retaining the trailer and the separately published episode 83
re-release. It does not merge similar items or replace the historical item
table.

| Measure | Original analytic release | Reconciled sensitivity dataset | Change |
| --- | ---: | ---: | ---: |
| Source identities represented | 269 | 242 | -27 |
| Extracted items | 14,397 | 12,978 | -1,419 |
| Focal items | 10,940 | 9,855 | -1,085 |
| Contextual items | 3,457 | 3,123 | -334 |

The excluded 1,419 items comprise 1,376 items from the 26 duplicate legacy
identities and 43 items from the episode-186 precursor identity. Their removal
from the sensitivity view does not imply that the extracted item records are
textually or semantically identical; the exclusion unit is the confirmed
source/release identity.

Across the 27 alias groups, the selected canonical identities contain 1,409
items and the excluded alias identities contain 1,419. The structured-record
comparison found zero exact normalized item-record matches and zero heuristic
near matches at the conservative 0.80 within-category token-set Jaccard
threshold. This indicates that alternate source runs produced materially
different extraction records even when the source identities refer to the same
release. It does not contradict the transcript-level alias decision and is
precisely why no item-level semantic deduplication is attempted.

All ten categories remain represented. Their aggregate sensitivity is:

| Extraction category | Original items | Sensitivity items | Change |
| --- | ---: | ---: | ---: |
| Key Concepts / Frameworks / Theories | 1,885 | 1,695 | -190 (-10.08%) |
| Technologies / Tools / Platforms | 1,243 | 1,115 | -128 (-10.30%) |
| Organizations / Actors / Communities | 1,892 | 1,703 | -189 (-9.99%) |
| Key Events / Historical Examples | 1,304 | 1,162 | -142 (-10.89%) |
| Future Trends / Predictions | 939 | 856 | -83 (-8.84%) |
| Challenges / Risks / Barriers | 1,871 | 1,689 | -182 (-9.73%) |
| Opportunities / Recommended Actions | 1,806 | 1,635 | -171 (-9.47%) |
| Memorable Insights / Quotes | 1,615 | 1,467 | -148 (-9.16%) |
| Strategic Landscape / Times | 969 | 876 | -93 (-9.60%) |
| Guest Background / Experience | 873 | 780 | -93 (-10.65%) |

The pipeline compares original and sensitivity counts by extraction category,
cluster assignment, and traceable higher-order support. Cluster comparisons
include primary count, secondary count, governed weighted count where present,
absolute and percentage change, and unique episode coverage. Full results are
private because they link back to source identities and the item-level
analysis.

The largest governed weighted-count changes (`2 × primary + secondary`) are:

| Cluster | Weighted change | Percent change |
| --- | ---: | ---: |
| `OPP-04` | -119 | -10.37% |
| `KCFT-06` | -103 | -14.23% |
| `KE-03` | -96 | -14.26% |
| `ORG-ACT-02` | -90 | -11.90% |
| `ORG-ACT-04` | -86 | -11.07% |

These are sensitivity diagnostics, not rankings of substantive instability.
A larger count change can reflect where confirmed alias sources contributed
many coded items; interpretation also depends on episode coverage, category
breadth, and the content of the remaining support.

## Support-sensitivity interpretation

The audit does not regenerate the 36 meta-clusters, 11 cross-cutting themes,
30 tensions, seven source meta-narratives, or six scenarios. Those are frozen
historical syntheses. It asks a narrower question: how does their traceable
support change when confirmed duplicate identities are excluded?

Sensitivity labels are conservative and describe support retention only. For
the traceable item/episode/category support measured by the pipeline:

- **stable** — no category loss, no more than 5% canonical-episode loss, and no
  more than 10% item loss;
- **mildly sensitive** — more than 5% episode loss or more than 10% item loss,
  without a category loss or a stronger condition below;
- **moderately sensitive** — more than 10% episode loss, one category lost, or
  support that originally spanned more than two episodes concentrates in two
  or fewer;
- **highly sensitive** — no retained support, more than 25% episode loss, at
  least 75% item loss, or two or more categories lost; and
- **cannot assess from available provenance** — no sufficiently direct
  item-level lineage is available. This applies by design to entity types such
  as meta-narratives, category findings, and scenarios when only indirect
  source support is present.

These labels do not establish whether an entity is true, scientifically valid,
important, or representative. Preferred interpretation is that an entity
"remains broadly supported within the reconciled sensitivity dataset" where
the traceable metrics warrant that statement—not that it "remains valid."

Across the 132 higher-order entities, the support-sensitivity results are:

| Entity type | Stable | Mildly sensitive | Moderately sensitive | Highly sensitive | Cannot assess |
| --- | ---: | ---: | ---: | ---: | ---: |
| Meta-clusters | 26 | 1 | 4 | 5 | 0 |
| Cross-cutting themes | 2 | 1 | 8 | 0 | 0 |
| Tensions | 16 | 0 | 6 | 8 | 0 |
| Meta-narratives | 0 | 0 | 0 | 0 | 7 |
| Category findings | 0 | 0 | 0 | 0 | 42 |
| Scenarios | 0 | 0 | 0 | 0 | 6 |
| **Total** | **44** | **2** | **18** | **13** | **55** |

Tension `TD-024` loses all 12 directly traceable supporting items and `TD-026`
loses all 14 under canonical-source selection. Several other tensions lose
category breadth. These are material provenance signals and trigger the
reanalysis recommendation below, but they are not proof that either tension is
false or analytically invalid. The 55 `cannot assess` results reflect
insufficiently direct item-level lineage for the applicable higher-order entity
types, not a finding of no support.

## Governed recommendation

The sensitivity findings support **full-pipeline reanalysis recommended** as a
future, separately governed project. Thirteen higher-order entities are highly
sensitive under the conservative thresholds, including two tensions that lose
all directly traceable item support, and other tensions lose category breadth.
Those results are substantial enough that count-only remediation cannot answer
whether the same cluster and synthesis structure would emerge from one source
identity per public-feed release.

This release still makes the corrections that are established now:

- public corpus and coverage language uses 242 canonical episode releases;
- 269 remains the historical transcript/source-identity count;
- original-versus-sensitivity denominators are labeled separately; and
- all private reconciliation and support diagnostics remain reproducible.

This work package **does not** rerun extraction, coding, cluster formation, or
higher-order synthesis. The existing synthesis remains a frozen historical
output and is not silently replaced. Losing traceable support under this test
does not prove an entity invalid; it demonstrates that the historical support
base is sensitive enough to warrant a full future rerun and human comparison
of the resulting structures.

## Outputs and publication boundary

Private reconciliation and sensitivity records are generated beneath
`analysis/cognitive-security/corpus-reconciliation/`. They include the full
source mapping, alias groups, review queue, item sensitivity, cluster
sensitivity, higher-order support sensitivity, and overall report. The
directory remains ignored and is not a public API.

The public package exposes only canonical episode records and
`data/cognitive-security/corpus_reconciliation.json`, an aggregate account of
the decision, counts, rules, limitations, and governed reanalysis
recommendation. The public reconciliation aggregate does not contain transcript
details, source filenames, pair-level identity evidence, workbook hashes, item
IDs, quotations, or private local paths. The separate governed manifest and QA
products publish opaque artifact IDs, canonical roles, integrity-verification
status, and aggregate dimensions. Exact names, hashes, and provenance remain
in the ignored private normalized release for reproducibility.

## Reproducibility and change control

The eight XLSX artifacts are immutable historical sources. Reconciliation is
built in memory after v1.0 normalization and validated before any generated
file is replaced. The build preserves all source hashes, explicit IDs,
assignments, and synthesis records; produces deterministic UTF-8 JSON; and
must be byte-identical on a second run with unchanged inputs.

Future mapping changes require either a documented rule-version change or a
durable human decision. Likely or ambiguous records must never be silently
promoted merely to preserve the count of 242.
