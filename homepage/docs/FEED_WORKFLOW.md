# Daily / weekly reports → homepage research rail

## What is implemented now

A local, deterministic editorial build. The frontend reads a small generated JavaScript data object; it does not call Google Drive, an LLM, or a private service. There are no browser-side API keys or credentials.

`content/feed.json` is the input. Updating it and rebuilding updates the feed. Automating extraction from future reports is a later integration, not something the preview has silently activated.

## Routine workflow

1. Read the new daily or weekly report in full.
2. Select public-appropriate items rather than dumping the whole report.
3. Deduplicate sources against existing feed entries. A recurring source should usually update or extend an existing note, rather than create duplicate cards.
4. Write a title, a short summary, and a short detail note grounded in the report. Preserve its actual uncertainty and outcome distinctions.
5. Attach one or more of the four approved categories. Category assignments are editorial navigation labels, not research findings.
6. Retain the report selection date separately from the source's publication date.
7. Verify the linked original source and clear the public text for release.
8. Mark only reviewed entries `approved`, set `primarySourceChecked: true`, and supply `reviewedAt`.
9. Build in release mode, run tests, and submit the content update in an unmerged PR.

## Record shape

```json
{
  "id": "stable-public-slug",
  "title": "Grounded editorial headline",
  "summary": "A short source-supported explanation.",
  "detail": "Context, practical relevance, and any substantive limitation.",
  "categories": ["behavioral-science", "application-analysis"],
  "publisher": "Actual publisher",
  "sourceUrl": "https://verified-original-source.example/article",
  "sourceType": "Research",
  "briefDate": "2026-09-06",
  "briefType": "daily",
  "sourcePublishedAt": null,
  "status": "draft",
  "primarySourceChecked": false,
  "order": 0
}
```

The URL above is a schema example, not a site item. Approved entries additionally require a `reviewedAt` ISO date. Do not place account names, local paths, private Drive URLs, private report IDs, raw transcripts, internal review notes, or API keys into public fields.

## Publication rules

- Drafts are visible only in preview builds and explicitly identified at feed level.
- Release builds include approved entries only; archived entries are not shown.
- Do not convert the preview's draft statuses to approval automatically.
- `primarySourceChecked` means the cited source was checked, not that the study's conclusions were proven.
- Do not infer a new scientific result from the homepage's cross-topic navigation.
- The public output is allowlisted: ID, title, summary, detail, categories, publisher, source URL/type, brief date/type, and source publication date.
- The two report types are daily and weekly. The four topic filters are independent of report cadence.

## Automation boundary

A future connector/Codex job can draft records from the user's reports and run this builder. That job should not silently publish, bypass review, or change the homepage layout. Prefer a reviewed content-only PR. Scheduling, account credentials, source synchronization, and webhook setup are not implemented by this package.
