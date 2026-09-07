# Reconciled seed status

The six handcrafted homepage-preview records were reconciled into `data/research-stream/research_items.jsonl` on 2026-09-07. They are ordinary canonical research records, not a separate feed or candidate system.

All six have `streamDecision: "pending"`, `decisionDate: null`, and `publishedAt: null`. Therefore none appears in `public_feed.json` or the homepage stream until the owner runs an explicit review command.

The prior source review remains useful context:

| Source | Current database status | Review note |
|---|---|---|
| Party cues and policy information | Pending | DOI and publisher metadata were verified; suitable for owner review. |
| Crowd digital twins | Pending | DOI and publication metadata were verified; inspect the primary abstract/full text before publishing the substantive summary. |
| German anti-sabotage proposal | Pending, source unverified | Reuters blocked the automated audit; verify in an authorized browser before publishing. |
| AI content labeling | Pending | DOI, publisher abstract, and experimental framing were verified; suitable for owner review. |
| Adaptive fuzzy cognitive maps | Pending | DOI and publisher abstract were verified; suitable for owner review. |
| Communicating social perspective taking | Pending | DOI, publisher abstract, and study design were verified; suitable for owner review. |

`sourceVerified` records whether the cited source was checked. It does not approve the item for publication or certify that the source's conclusions are correct.
