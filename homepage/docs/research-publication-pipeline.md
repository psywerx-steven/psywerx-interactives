# PSYWERX research publication pipeline v2

Rebuilt 2026-10-21. Repository: `psywerx-steven/psywerx-interactives`. Authoritative data branch: `research-data`.

## Ownership and publication path

`Morning Brief producer → validated inbox JSON → repository-owned reconciliation → canonical ingestion, manifests, receipts and projections → live data verification`

The producer constructs one complete payload first, writes and reads back its GitHub inbox, then saves the full human-readable brief and exactly one fenced handoff JSON object to the Drive archive. Drive archival is secondary: an archive failure must not block a valid GitHub handoff. If the GitHub write fails, the producer still attempts a complete archive so independent recovery can publish it.

The existing `homepage/tools/research_stream.py` remains the canonical ingestion and identity implementation. `homepage/tools/research_pipeline.py` adds strict input gates, reconciliation, receipts and publication checks; it does not introduce a second canonical database.

Assistants may create or repair only `data/research-stream/inbox/YYYY-MM-DD.json` during ordinary publication. Only repository Actions generate the canonical database, archive shards, brief manifests, ingestion receipts, public feed/pages and explorer projection. Do not manually patch those outputs, the generated homepage, or the website to make a health check pass. Preserve editorial hold/reject decisions.

## Operating schedule and deadline

All human-facing times use `America/Chicago`, including daylight saving time.

| Stage | Schedule | Responsibility |
|---|---|---|
| PSYWERX Morning Brief | 07:30 daily | Research, complete payload, GitHub write/readback, complete Drive archive |
| PSYWERX Publish Recovery | 08:15, 09:15, 10:15, 11:15, 12:15 daily | Recover missed handoffs independently; verify full propagation |
| Research feed ingest | Inbox/code/workflow pushes; hourly at minute 23; manual dispatch | Reconcile available handoffs, build and verify generated data |
| Missing-today deadline | 08:45 | Do not call today's publication late before this time |

The GitHub schedule must be installed in `.github/workflows/research-feed-ingest.yml` on the default branch `main`, as well as `research-data`. Every execution checks out and writes only `research-data`. Copy the workflow through a normal protected-branch pull request; never merge the whole data branch into main to activate the schedule. Scheduled service execution can be delayed; a configured time is not a guarantee of exact service start.

Before the deadline, missing today's inbox is not itself a late-publication incident. If today's inbox already exists, verify it immediately. After the deadline, failures identify the exact checkpoint and latest date actually verified. Routine unchanged alerts are limited to the 09:15 and 12:15 recovery runs; 10:15 and 11:15 report only a new critical failure. Healthy runs finish silently. Do not disable either task because one run failed. Task push/email notification delivery is controlled separately by the user's notification settings.

## Source archive and safe recovery

Native Google Doc name: exactly `YYYY-MM-DD — PSYWERX Morning Brief`.

Archive folder: Content → Daily Briefs, ID `10lr3r2ro1IFoeKOwY7BjDO9cG1auAP0q`.

Search the designated folder first, then the exact title across accessible Drive to recover a misplaced archive. Read the actual document and metadata. A title, search hit or nonzero file size is not proof of completeness. Confirm the full prose and exactly one valid fenced handoff block. Identical duplicate payloads can be treated as one; conflicting versions are a failure, not permission to pick arbitrarily or delete documents.

For a misplaced valid archive, move the same document ID into the configured folder using metadata-confirmed parent changes and read back its final parent. Do not create a replacement duplicate. Moving an archive must not block a valid inbox write.

Recovery may publish today's valid archived handoff and missing handoffs from the preceding two days, restricted to dates on or after the 2026-10-21 cutover. Never relabel an old brief as today's. Never reconstruct absent JSON from prose, fabricate verification, or publish an empty placeholder. Never overwrite a valid complete inbox with a partial or conflicting archive. On an update, use the freshly read GitHub blob SHA; reread on conflicts. An identical complete inbox is a successful no-op, not a reason to manufacture another push.

## Handoff contract

Path: `data/research-stream/inbox/YYYY-MM-DD.json`; plain formatted JSON only.

The object has exactly `schemaVersion`, `briefDate`, `briefType`, `items`. Require `schemaVersion: psywerx-research-items-v1`, the correct date, `briefType: daily`, and a nonempty items array.

Each item has exactly:

```text
sourceItemNumber primaryCategory categories questionAndWhy whatTheyDid
whatTheyFound whatItMeans streamTitle streamSummary attribution sourceUrl
sourcePublishedAt sourceKey sourceVerified briefDate briefType streamDecision
```

Categories are `behavioral-science`, `technology-modeling`, `operations-strategy`, `application-analysis`. For handoffs dated on or after 2026-10-21, every item must have `sourceVerified: true`, `streamDecision: publish`, and matching daily provenance. Require unique positive item numbers, unique normalized source identities, valid public HTTPS source URLs, complete substantive fields, valid publication dates or null, no duplicate JSON keys and no non-finite numbers. The filename must match `briefDate`. Archived pre-cutover compatibility is retained by the existing validator; compressed envelopes are not accepted for new handoffs.

The wrapper calls the existing canonical validator so normalized DOI/URL identity and exact-field rules are shared with ingestion. The assistant should execute it when available, and must not claim execution from a visual inspection alone.

## Restartable repository reconciliation

The workflow runs 20 guard/integration tests, then reconciles a temporary staged copy of the data. It validates each inbox independently, sorts valid handoffs chronologically and ingests handoffs whose complete receipt/outputs are missing or changed. A malformed file is reported but does not prevent unrelated valid handoffs from being processed. Downstream editorial hold/reject overrides are preserved and reported, not republished.

It rebuilds public projections once, verifies every valid handoff, and promotes only fully checked generated files. Commits are restricted to these paths under `data/research-stream/`: `research_items.jsonl`, `archive`, `briefs`, `public_feed.json`, `public_feed_pages`, `explorer.json`, `receipts`. Inbox and website changes are forbidden in the generated-data commit.

The workflow serializes ingestion runs. On a concurrent remote update it fetches the new branch state and regenerates, with up to four push attempts. It does not force-push or rebase stale projections. Its hard reset is confined to the disposable runner checkout.

## Evidence of completion

For date D, require all of:

1. A valid `inbox/D.json`, read back after publication.
2. `briefs/D.json` with the complete expected item IDs and count.
3. `receipts/D.json` matching the normalized handoff hash and all expected/published/blocked IDs.
4. The explorer's D brief membership and all expected public items, matching canonical content.
5. The same complete published items at the live public explorer data endpoint.

Receipt schema: `psywerx-ingestion-receipt-v1`. Fields: `schemaVersion`, `briefDate`, `handoffSha256`, `itemIds`, `publishedItemIds`, `blockedItemIds`. The SHA-256 is over the canonical validator's normalized handoff encoded as sorted-key compact UTF-8 JSON. Receipts are deterministic so a replay can be a no-op.

Repeated sources retain their original `dateAdded`; verify dated manifest membership and `latestSeenBriefDate` rather than requiring all records to be newly added. A current `generatedAt`, one fresh item or a successful workflow predating the handoff is not sufficient.

Live data endpoint:

```text
https://raw.githubusercontent.com/psywerx-steven/psywerx-interactives/research-data/data/research-stream/explorer.json
```

The checker bypasses cache where possible and retries this read four times. It compares the complete expected item content, not only the latest date. This verifies the live data endpoint; it does not by itself certify browser rendering or every unrelated website feature.

## Failure reports and operational commands

Artifacts named `research-publication-checks-RUN_ID-ATTEMPT` retain `reconcile.json` and `publication-health.json` for 14 days. Reports also appear in the workflow summary. A workflow remains failed if reconciliation reported a rejected input/conflict or any publication checkpoint failed, even when unrelated valid content was successfully processed.

Health reports include the requested `briefDate`, latest inbox/manifest/explorer/live dates, `ok`, and either `publishedItems` or `failedCheckpoint` plus `error`. Distinguish absent source, invalid JSON, write/readback failure, manifest, explorer propagation, receipt, live endpoint, and editorial override. A permission, authentication or network error is not evidence that a file is absent.

From a repository checkout:

```bash
python homepage/tools/research_pipeline.py validate --input data/research-stream/inbox/2026-10-21.json --date 2026-10-21
python -m unittest discover -s homepage/tests -p test_research_pipeline.py -v
python homepage/tools/research_pipeline.py check --date 2026-10-21 --live
```

To recover ingested outputs, run the existing Research feed ingest workflow through GitHub Actions manual dispatch or its scheduled reconciler. Do not manually patch generated files or rewrite an identical inbox merely to trigger a push. Ordinary assistant tasks do not run `reconcile` against production data directly; that write path belongs to the workflow.

## Rebuild verification and remaining gap

On 2026-10-21, workflow run `39604494744` passed all 20 tests (including six canonical integration tests), reconciled 43 available handoffs with no errors, and verified all 10 October 21 items at the live explorer data endpoint. The recovered October 21 archive was moved into the intended Daily Briefs folder.

The October 20 archive inspected during recovery contained only two prose summaries and no handoff JSON. No full October 20 payload was fabricated, and that historical publication gap remains unresolved. Today's successful check must not be represented as recovery of that missing day.
