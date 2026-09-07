# Morning Brief → research database → public stream

## Active architecture

Every item in the daily Morning Brief is retained in the canonical, Git-friendly database at:

```text
data/research-stream/research_items.jsonl
```

Database inclusion is not a publishing decision. Every new source begins with `streamDecision: "pending"`; an owner later chooses `publish`, `hold`, or `reject`. Held and rejected items remain in the database for retrieval, deduplication, source tracking, trend analysis, content development, and future clustering or embedding work.

The frontend never reads the canonical notes. It receives only the allowlisted public projection in `data/research-stream/public_feed.json` and, when needed, small files under `data/research-stream/public_feed_pages/`.

## Morning Brief handoff

The Morning Brief normally contains about 8–12 high-quality items, without category quotas. It does not require research to be represented as a Driver, mechanism, pathway, intervention chain, or causal model; those connections may be mentioned only when they genuinely help.

The final fenced JSON object in each exported brief uses `schemaVersion: "psywerx-research-items-v1"`, `briefType: "daily"`, and the four approved category IDs. Every item contains exactly four substantive plain-language sections—`questionAndWhy`, `whatTheyDid`, `whatTheyFound`, and `whatItMeans`—plus the website-ready `streamTitle`, approximately 60–120 word `streamSummary`, attribution, and authoritative source.

The formal interchange schema is `homepage/schemas/psywerx-research-items-v1.schema.json`. The standard-library validator additionally enforces matching top-level/item provenance, unique source numbers, canonical dates, safe credential-free HTTPS URLs, unique categories containing the primary category, and `streamDecision: "pending"`.

Ingest raw JSON or a full Markdown/text export:

```powershell
py homepage/tools/ingest_research_items.py --input path/to/morning-brief.md --dry-run
py homepage/tools/ingest_research_items.py --input path/to/morning-brief.md
```

The operation is transactional: malformed handoffs do not partially modify the database. Its JSON report gives counts and details for `added`, `updated`, `unchanged`, `conflicts`, and `rejected`.

## Canonical record

Each JSONL line is one validated object with this intentionally small field set:

```text
itemId, sourceKey, firstSeenBriefDate, latestSeenBriefDate,
sourcePublishedAt, primaryCategory, categories,
questionAndWhy, whatTheyDid, whatTheyFound, whatItMeans,
streamTitle, streamSummary, attribution, sourceUrl, sourceVerified,
streamDecision, decisionDate, publishedAt, reviewRequired
```

`reviewRequired` is a controlled boolean used only when a previously decided source returns with materially changed content. No Drive URL/ID, local path, credential, account identifier, or private hidden note is allowed into the public projection.

## Source identity and repeat handling

`sourceKey` is the identity key. Bare DOI, `doi:` DOI, and `https://doi.org/` variants normalize to lower-case `doi:10...`. Non-DOI identities normalize as credential-free HTTPS URLs: host and scheme are normalized, fragments and common tracking parameters are removed, query parameters are sorted, and non-root trailing slashes are removed.

One stable `itemId` is derived from the normalized source key. A later brief cannot create a second record merely because its date changed.

- Exact same source and content: update `firstSeenBriefDate`/`latestSeenBriefDate` if necessary; otherwise report unchanged.
- Pending source with newer wording: retain the item ID and first-seen date, apply the newer normalized content, advance latest-seen date, and keep the decision pending.
- Older repeat of a pending source: it may extend first-seen provenance but cannot overwrite newer content.
- `sourceVerified` is monotonic for pending updates: a later false value cannot erase a prior true value.
- Missing publication dates do not erase a known publication date.
- A publish/hold/reject source with materially changed content: preserve its content and human decision, update seen-date provenance, set `reviewRequired: true`, report a conflict, and exit with status 2. The archived Morning Brief remains the source for adjudicating the incoming revision.

The ingestion tool never changes any decision to publish.

## Evening review

Apply exactly one explicit owner decision:

```powershell
py homepage/tools/review_research_item.py ITEM_ID publish --date YYYY-MM-DD
py homepage/tools/review_research_item.py ITEM_ID hold --date YYYY-MM-DD
py homepage/tools/review_research_item.py ITEM_ID reject --date YYYY-MM-DD
```

If `--date` is omitted, the local current date is used. Publish sets `decisionDate` and `publishedAt`; hold or reject sets `decisionDate` and leaves `publishedAt` null. Nothing is deleted. The command also regenerates the public projection.

## Public projection and homepage build

Regenerate the allowlisted stream directly when needed:

```powershell
py homepage/tools/build_research_stream.py
```

The homepage builder runs the same projection before rendering. Only publish records are eligible, ordered by `publishedAt` and then stable ID, newest first. Public items contain exactly:

- `itemId`
- `streamTitle`
- `streamSummary`
- `attribution`
- `sourceUrl`
- `categories`
- `publishedAt`

The first 24 records are embedded in the static homepage. Additional 24-record JSON pages are fetched only when a visitor chooses **Load older selections**. The four filters use OR semantics across the records loaded so far. This keeps the first page bounded as the canonical database grows to thousands of records without requiring a backend.

## Future automation contract

```text
Scheduled Morning Brief
    ↓
Google Drive archive
    ↓
psywerx-research-items-v1 block
    ↓
deterministic ingestion
    ↓
research_items.jsonl
    ↓
all new items pending
    ↓
evening owner review
    ↓
publish / hold / reject
    ↓
generate public_feed.json
    ↓
content-only website update
```

A future connector may fetch the archived brief and create an ingestion PR. It must run outside public GitHub Actions with narrowly scoped access, discard the source document after extracting the final block, and commit only the canonical JSONL/public projection changes. It must never change `pending` to `publish`, store Drive URLs or IDs, place credentials in Git, or make GitHub Actions scrape private Drive. Publication remains a separate owner-triggered content PR or commit after evening review.
