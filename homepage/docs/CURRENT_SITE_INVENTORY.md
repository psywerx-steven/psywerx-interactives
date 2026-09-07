# Current `psywerx.io` public-site inventory

Observed 2026-09-07 before replacement. This is a read-only audit of the Super/Vercel site and public DNS; no Super, DNS, or repository settings were changed.

## Hosting and navigation

- `https://psywerx.io/` returns HTTP 200 from Vercel/Super. `https://www.psywerx.io/` returns a permanent redirect to the apex.
- The visible homepage navigation exposes the root plus **Drivers Taxonomy Explorer** (`https://drivers.psywerx.io`) and **Cognitive Crucible Explorer** (`https://drivers.psywerx.io/cognitive-security/`).
- The homepage embeds LinkedIn's company-follow control for company ID `143309904`. The approved launch design preserves this function as a direct, accessible link to `https://www.linkedin.com/company/psywerx` without loading LinkedIn JavaScript.
- Super reports site search, membership, and feeds as disabled. No user-facing Super navigation links to the 98 secondary sitemap pages were found on the homepage.

## Useful homepage copy preserved

The current site identifies PSYWERX as a nonprofit initiative that makes behavioral and social science more accessible, connected, and useful, with particular relevance to national security and the information environment. It explains that behavior emerges from interacting psychological, social, cultural, environmental, biological, informational, and technological conditions, and that the developing knowledge base connects theories, frameworks, mechanisms, and practical application.

The launch homepage preserves these useful ideas in its hero, six platform areas, connected-knowledge overview, and About section. It does not preserve the temporary "actively being developed" launch notice or the generic title "Welcome To Our Site."

## Newsletter

The public homepage contains a MailerLite inline subscription form:

- action: `https://assets.mailerlite.com/jsonp/2519483/forms/195936376173102135/subscribe`
- method: `POST`
- email field: `fields[email]`
- required hidden values: `ml-submit=1` and `anticsrf=true`
- current behavior: opens the MailerLite result in a new tab

The launch candidate reuses these public, credential-free form details in a restrained inline footer form. It does not copy the large third-party embed stylesheet/script and does not introduce a popup.

## Metadata and branding

- Current title, Open Graph site name, and social title: `Welcome To Our Site`.
- Current description: nonprofit behavioral/social-science initiative; national-security and information-environment focus; theories, models, frameworks, methods, and emerging technologies.
- Current robots behavior: `index, follow`; `/api` and `/_next` are disallowed in `robots.txt` while `/_next/static` is allowed.
- Current social image and cover use the supplied wide PSYWERX banner hosted by Super's image CDN. The launch candidate uses the repository copy of that same supplied banner.
- Super reports no configured favicon, and no favicon link was present in the fetched root HTML. The launch candidate supplies the approved local PSYWERX favicon.

## Public sitemap snapshot

The current sitemap exposes 99 URLs (the root plus 98 secondary pages). Preserve this list until the owner decides which secondary content is archived, migrated, redirected, or intentionally retired. The launch PR does not fabricate replacements for these pages.

```text
/
/agent-based-models
/aiml
/behavior-change-frameworks
/behavior-drivers
/behavior-interventions
/behavior-theories
/biases-heuristics
/biologicalphysiological-drivers
/books-articles
/case-based-comparative-methods
/causal-predictive-methods
/certificates-degrees
/china
/cognitive-psychological
/cognitive-warfare
/communication-theories
/consciousness-theories
/consumer-behavior
/content-analysis
/content-analysis/aiml
/content-discourse-analysis
/courses
/cultural-drivers
/cultural-framework-national
/cultural-framework-organizational
/data-collection
/data-collection-methods
/deception-theories
/decision-making-theories
/determinism-free-will
/deterrence-theory
/digital-twins
/disinformation-theory
/ecological-systems-theories
/environmental-drivers
/evolutionary-theories
/experimental-methods
/frameworks
/frameworks-taxonomies
/future-scenarios
/game-theory
/health-safety-environmental
/humanitarian-ngo
/individuals
/intervention-types
/introduction
/iran
/knowledge-truth
/learning-theories
/lesson-learned
/live-exercises
/logic-reasoning
/methods
/metrics-indicators
/military-defense
/modeling-simulation
/motivation-theories
/network-models
/north-korea
/nudge-theory
/observational-behavioral-tracking
/osint
/p
/pages
/pages/introduction
/pages/learning-theories
/personality-theories
/persuasion-theories
/philosophy-of-science
/planning-frameworks
/political-governance
/propaganda-theory
/psychological-drivers
/quasi-experimental-methods
/radicalization-theories
/reflexive-control-theory
/reporting
/resources-toolkits
/russia
/segmentation-methods
/social-cultural
/social-group-theories
/social-media-analysis
/sociological-drivers
/statistical-models
/structural-environmental
/survey-analysis
/survey-based-methods
/systems-based-models
/systems-complexity-theories
/taxonomies
/technology-forecasts
/terrorist-groups
/test
/three-warfare-doctrine
/vulnerability-susceptibility
/wargaming-ttxs
/will-to-fight
```

## URLs that must not disappear without an explicit decision

The two live explorer destinations and their deep links are mandatory migrations. The 98 secondary Super URLs may contain useful knowledge-base content even though the current homepage does not link to them. Before ending Super service, export or snapshot the underlying Notion/Super content and approve a per-URL disposition. High-signal families include behavior drivers/theories/interventions, frameworks/methods/modeling, cognitive warfare and influence topics, courses/exercises, countries/cases, and resources/reporting. `/test`, `/p`, `/pages`, and duplicate `/pages/...` paths appear administrative or legacy but still require owner confirmation before retirement.
